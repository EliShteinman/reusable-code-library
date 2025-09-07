# ============================================================================
# shared-utilities/sql/sql_repository.py - CRUD ONLY (FIXED VERSION)
# ============================================================================
import logging
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from .mysql_sync_client import MySQLSyncClient
from .postgresql_sync_client import PostgreSQLSyncClient

logger = logging.getLogger(__name__)


class SQLRepository:
    """
    SQL CRUD repository - OPERATIONS ONLY
    Works with both MySQL and PostgreSQL clients
    Clean separation: Client = CONNECTION, Repository = CRUD
    """

    def __init__(self, client: Union[MySQLSyncClient, PostgreSQLSyncClient], table_name: str):
        self.client = client
        self.table_name = table_name
        self.is_postgresql = isinstance(client, PostgreSQLSyncClient)

    def _add_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add created_at and updated_at timestamps."""
        data_with_meta = data.copy()
        now = datetime.now(timezone.utc)

        # Only add if columns don't exist
        if 'created_at' not in data_with_meta:
            data_with_meta['created_at'] = now
        if 'updated_at' not in data_with_meta:
            data_with_meta['updated_at'] = now

        return data_with_meta

    def _build_where_clause(self, filters: Dict[str, Any]) -> tuple:
        """
        Build WHERE clause from filters.

        Args:
            filters: Dictionary of field-value pairs

        Returns:
            Tuple of (where_clause, params)
        """
        if not filters:
            return "", ()

        conditions = []
        params = []

        for field, value in filters.items():
            if isinstance(value, dict):
                # Range filters: {"age": {"gte": 25, "lte": 65}}
                for op, val in value.items():
                    if op == "gte":
                        conditions.append(f"{field} >= %s")
                        params.append(val)
                    elif op == "lte":
                        conditions.append(f"{field} <= %s")
                        params.append(val)
                    elif op == "gt":
                        conditions.append(f"{field} > %s")
                        params.append(val)
                    elif op == "lt":
                        conditions.append(f"{field} < %s")
                        params.append(val)
                    elif op == "ne":
                        conditions.append(f"{field} != %s")
                        params.append(val)
            elif isinstance(value, list):
                # IN filters: {"city": ["Tel Aviv", "Jerusalem"]}
                placeholders = ','.join(['%s'] * len(value))
                conditions.append(f"{field} IN ({placeholders})")
                params.extend(value)
            elif isinstance(value, str) and '%' in value:
                # LIKE patterns: {"name": "%john%"}
                conditions.append(f"{field} LIKE %s")
                params.append(value)
            else:
                # Exact match
                conditions.append(f"{field} = %s")
                params.append(value)

        where_clause = " AND ".join(conditions)
        return where_clause, tuple(params)

    # ========================================================================
    # BASIC CRUD OPERATIONS
    # ========================================================================

    def create(self, data: Dict[str, Any]) -> Union[int, str]:
        """Create new record and return ID."""
        data_with_meta = self._add_metadata(data)
        columns = ', '.join(data_with_meta.keys())

        if self.is_postgresql:
            # PostgreSQL with RETURNING
            placeholders = ', '.join(['%s'] * len(data_with_meta))
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING id"
            result = self.client.execute_returning(query, tuple(data_with_meta.values()))
            return result['id'] if result else None
        else:
            # MySQL
            placeholders = ', '.join(['%s'] * len(data_with_meta))
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            return self.client.execute_insert(query, tuple(data_with_meta.values()))

    def get_by_id(self, id_value: Any, id_column: str = "id") -> Optional[Dict[str, Any]]:
        """Get record by ID."""
        query = f"SELECT * FROM {self.table_name} WHERE {id_column} = %s"
        results = self.client.execute_query(query, (id_value,))
        return results[0] if results else None

    def get_all(self, limit: int = None, offset: int = 0, order_by: str = "id") -> List[Dict[str, Any]]:
        """Get all records with optional pagination."""
        query = f"SELECT * FROM {self.table_name} ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        return self.client.execute_query(query)

    def update(self, id_value: Any, data: Dict[str, Any], id_column: str = "id") -> int:
        """Update record by ID and return affected rows."""
        # Add updated_at timestamp
        update_data = data.copy()
        update_data['updated_at'] = datetime.now(timezone.utc)

        set_clause = ', '.join([f"{k} = %s" for k in update_data.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {id_column} = %s"
        params = list(update_data.values()) + [id_value]
        return self.client.execute_query(query, params, fetch=False)

    def delete(self, id_value: Any, id_column: str = "id") -> int:
        """Delete record by ID and return affected rows."""
        query = f"DELETE FROM {self.table_name} WHERE {id_column} = %s"
        return self.client.execute_query(query, (id_value,), fetch=False)

    # ========================================================================
    # SEARCH AND FILTER OPERATIONS
    # ========================================================================

    def search(self, filters: Dict[str, Any] = None, limit: int = 10, offset: int = 0,
               order_by: str = "id", order_dir: str = "ASC") -> Dict[str, Any]:
        """
        Search records with filters.

        Args:
            filters: Search filters
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Column to order by
            order_dir: Order direction (ASC/DESC)

        Returns:
            Dict with total_count, documents, and metadata
        """
        where_clause, params = self._build_where_clause(filters or {})

        # Base query
        base_query = f"SELECT * FROM {self.table_name}"
        if where_clause:
            base_query += f" WHERE {where_clause}"

        # Count query
        count_query = f"SELECT COUNT(*) as count FROM {self.table_name}"
        if where_clause:
            count_query += f" WHERE {where_clause}"

        # Get total count
        count_result = self.client.execute_query(count_query, params)
        total_count = count_result[0]['count'] if count_result else 0

        # Get documents with pagination
        query = f"{base_query} ORDER BY {order_by} {order_dir} LIMIT {limit} OFFSET {offset}"
        documents = self.client.execute_query(query, params)

        return {
            'total_count': total_count,
            'returned_count': len(documents),
            'limit': limit,
            'offset': offset,
            'documents': documents
        }

    def count(self, filters: Dict[str, Any] = None) -> int:
        """Count records matching filters."""
        where_clause, params = self._build_where_clause(filters or {})

        query = f"SELECT COUNT(*) as count FROM {self.table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"

        result = self.client.execute_query(query, params)
        return result[0]['count'] if result else 0

    def exists(self, filters: Dict[str, Any]) -> bool:
        """Check if record exists with given filters."""
        return self.count(filters) > 0

    # ========================================================================
    # BULK OPERATIONS
    # ========================================================================

    def bulk_create(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk create multiple documents."""
        if not documents:
            return {'success_count': 0, 'error_count': 0}

        docs_with_meta = []
        for doc in documents:
            docs_with_meta.append(self._add_metadata(doc))

        try:
            # Get columns from first document
            columns = ', '.join(docs_with_meta[0].keys())
            placeholders = ', '.join(['%s'] * len(docs_with_meta[0]))
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"

            # Prepare parameters
            params_list = [tuple(doc.values()) for doc in docs_with_meta]

            # Execute bulk insert
            affected_rows = self.client.execute_many(query, params_list)

            return {
                'success_count': affected_rows,
                'error_count': 0
            }
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            return {'success_count': 0, 'error_count': len(documents)}

    def bulk_update(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk update multiple records.

        Args:
            updates: List of {"filters": {...}, "data": {...}}
        """
        success_count = 0
        error_count = 0

        for update_item in updates:
            try:
                filters = update_item['filters']
                data = update_item['data'].copy()
                data['updated_at'] = datetime.now(timezone.utc)

                where_clause, where_params = self._build_where_clause(filters)
                set_clause = ', '.join([f"{k} = %s" for k in data.keys()])

                query = f"UPDATE {self.table_name} SET {set_clause}"
                params = list(data.values())

                if where_clause:
                    query += f" WHERE {where_clause}"
                    params.extend(where_params)

                affected = self.client.execute_query(query, params, fetch=False)
                if affected > 0:
                    success_count += affected
                else:
                    error_count += 1

            except Exception as e:
                logger.error(f"Bulk update item failed: {e}")
                error_count += 1

        return {'success_count': success_count, 'error_count': error_count}

    def bulk_delete(self, filter_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk delete records by filters."""
        success_count = 0
        error_count = 0

        for filters in filter_list:
            try:
                where_clause, params = self._build_where_clause(filters)

                query = f"DELETE FROM {self.table_name}"
                if where_clause:
                    query += f" WHERE {where_clause}"

                affected = self.client.execute_query(query, params, fetch=False)
                if affected > 0:
                    success_count += affected
                else:
                    error_count += 1

            except Exception as e:
                logger.error(f"Bulk delete item failed: {e}")
                error_count += 1

        return {'success_count': success_count, 'error_count': error_count}

    # ========================================================================
    # JOIN OPERATIONS
    # ========================================================================

    def join(self, join_table: str, join_condition: str, join_type: str = "INNER",
             filters: Dict[str, Any] = None, limit: int = None) -> List[Dict[str, Any]]:
        """
        Perform JOIN operation.

        Args:
            join_table: Table to join with
            join_condition: JOIN condition (e.g., "users.id = orders.user_id")
            join_type: Type of JOIN (INNER, LEFT, RIGHT)
            filters: WHERE conditions
            limit: Result limit

        Returns:
            List of joined records
        """
        query = f"""
        SELECT * FROM {self.table_name} 
        {join_type} JOIN {join_table} ON {join_condition}
        """

        params = ()
        if filters:
            where_clause, params = self._build_where_clause(filters)
            if where_clause:
                query += f" WHERE {where_clause}"

        if limit:
            query += f" LIMIT {limit}"

        return self.client.execute_query(query, params)

    def left_join(self, join_table: str, join_condition: str, **kwargs) -> List[Dict[str, Any]]:
        """LEFT JOIN shortcut."""
        return self.join(join_table, join_condition, "LEFT", **kwargs)

    def inner_join(self, join_table: str, join_condition: str, **kwargs) -> List[Dict[str, Any]]:
        """INNER JOIN shortcut."""
        return self.join(join_table, join_condition, "INNER", **kwargs)

    # ========================================================================
    # AGGREGATION OPERATIONS
    # ========================================================================

    def aggregate(self, select_clause: str, group_by: str = None,
                  having: str = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Perform aggregation queries.

        Args:
            select_clause: SELECT part with aggregation functions
            group_by: GROUP BY clause
            having: HAVING clause
            filters: WHERE conditions

        Returns:
            Aggregation results
        """
        query = f"SELECT {select_clause} FROM {self.table_name}"
        params = ()

        if filters:
            where_clause, params = self._build_where_clause(filters)
            if where_clause:
                query += f" WHERE {where_clause}"

        if group_by:
            query += f" GROUP BY {group_by}"

        if having:
            query += f" HAVING {having}"

        return self.client.execute_query(query, params)

    def sum(self, column: str, filters: Dict[str, Any] = None) -> float:
        """Calculate SUM of column."""
        result = self.aggregate(f"SUM({column}) as total", filters=filters)
        return float(result[0]['total'] or 0) if result else 0

    def avg(self, column: str, filters: Dict[str, Any] = None) -> float:
        """Calculate AVG of column."""
        result = self.aggregate(f"AVG({column}) as average", filters=filters)
        return float(result[0]['average'] or 0) if result else 0

    def min_max(self, column: str, filters: Dict[str, Any] = None) -> Dict[str, float]:
        """Get MIN and MAX of column."""
        result = self.aggregate(f"MIN({column}) as min_val, MAX({column}) as max_val", filters=filters)
        if result:
            return {
                'min': float(result[0]['min_val'] or 0),
                'max': float(result[0]['max_val'] or 0)
            }
        return {'min': 0, 'max': 0}

    def group_by_count(self, group_column: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Group by column and count."""
        return self.aggregate(
            f"{group_column}, COUNT(*) as count",
            group_by=group_column,
            filters=filters
        )

    # ========================================================================
    # PANDAS INTEGRATION
    # ========================================================================

    def to_dataframe(self, filters: Dict[str, Any] = None, limit: int = None) -> pd.DataFrame:
        """Convert query results to pandas DataFrame."""
        try:
            where_clause, params = self._build_where_clause(filters or {})

            query = f"SELECT * FROM {self.table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"
            if limit:
                query += f" LIMIT {limit}"

            results = self.client.execute_query(query, params)

            if not results:
                return pd.DataFrame()

            df = pd.DataFrame(results)
            logger.info(f"Created DataFrame with {len(df)} rows from {self.table_name}")
            return df

        except Exception as e:
            logger.error(f"Failed to create DataFrame: {e}")
            return pd.DataFrame()

    def bulk_create_from_dataframe(self, df: pd.DataFrame, id_column: str = None) -> Dict[str, Any]:
        """
        Bulk create records from pandas DataFrame.

        Args:
            df: pandas DataFrame
            id_column: Column to use as ID (optional)

        Returns:
            Result dict with success/error counts
        """
        try:
            # Convert DataFrame to list of dictionaries
            documents = df.to_dict('records')

            # Handle ID column renaming
            if id_column and id_column in df.columns:
                for doc in documents:
                    if id_column in doc:
                        doc['record_id'] = doc.pop(id_column)

            return self.bulk_create(documents)

        except Exception as e:
            logger.error(f"Failed to create from DataFrame: {e}")
            return {'success_count': 0, 'error_count': len(df)}

    def from_dataframe_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze DataFrame and provide SQL insights.

        Args:
            df: pandas DataFrame

        Returns:
            Analysis results
        """
        analysis = {
            'total_rows': len(df),
            'columns': list(df.columns),
            'column_types': df.dtypes.to_dict(),
            'null_counts': df.isnull().sum().to_dict(),
            'summary_stats': {}
        }

        # Add summary statistics for numeric columns
        numeric_columns = df.select_dtypes(include=['number']).columns
        for col in numeric_columns:
            analysis['summary_stats'][col] = {
                'mean': df[col].mean(),
                'min': df[col].min(),
                'max': df[col].max(),
                'std': df[col].std()
            }

        return analysis

    # ========================================================================
    # TRANSACTION SUPPORT
    # ========================================================================

    def transaction(self):
        """Get transaction context manager from client."""
        return self.client.transaction()

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def get_table_info(self) -> Dict[str, Any]:
        """Get table structure information."""
        try:
            if self.is_postgresql:
                query = """
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_name = %s
                        ORDER BY ordinal_position \
                        """
            else:
                query = """
                DESCRIBE {self.table_name}
                """

            if self.is_postgresql:
                results = self.client.execute_query(query, (self.table_name,))
            else:
                results = self.client.execute_query(query)

            return {
                'table_name': self.table_name,
                'columns': results
            }
        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return {'table_name': self.table_name, 'columns': []}

    def truncate(self):
        """Truncate table (delete all records)."""
        try:
            if self.is_postgresql:
                query = f"TRUNCATE TABLE {self.table_name} RESTART IDENTITY"
            else:
                query = f"TRUNCATE TABLE {self.table_name}"

            self.client.execute_query(query, fetch=False)
            logger.info(f"Table {self.table_name} truncated")
        except Exception as e:
            logger.error(f"Failed to truncate table: {e}")

    def drop_table(self):
        """Drop the table."""
        try:
            query = f"DROP TABLE IF EXISTS {self.table_name}"
            self.client.execute_query(query, fetch=False)
            logger.info(f"Table {self.table_name} dropped")
        except Exception as e:
            logger.error(f"Failed to drop table: {e}")

    def create_index(self, column: str, unique: bool = False):
        """Create index on column."""
        try:
            index_name = f"idx_{self.table_name}_{column}"
            unique_clause = "UNIQUE " if unique else ""
            query = f"CREATE {unique_clause}INDEX {index_name} ON {self.table_name} ({column})"

            self.client.execute_query(query, fetch=False)
            logger.info(f"Index created on {self.table_name}.{column}")
        except Exception as e:
            logger.warning(f"Failed to create index: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get table statistics."""
        try:
            total_count = self.count()

            # Get first and last records
            first_record = self.client.execute_query(
                f"SELECT * FROM {self.table_name} ORDER BY id LIMIT 1"
            )
            last_record = self.client.execute_query(
                f"SELECT * FROM {self.table_name} ORDER BY id DESC LIMIT 1"
            )

            return {
                'total_records': total_count,
                'first_record': first_record[0] if first_record else None,
                'last_record': last_record[0] if last_record else None,
                'table_name': self.table_name
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {'total_records': 0, 'table_name': self.table_name}