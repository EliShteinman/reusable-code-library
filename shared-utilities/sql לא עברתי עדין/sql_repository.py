
# ============================================================================
# shared-utilities/sql/sql_repository.py - CRUD ONLY
# ============================================================================
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from . import MySQLSyncClient, PostgreSQLSyncClient

logger = logging.getLogger(__name__)


class SQLRepository:
    """
    SQL CRUD repository - OPERATIONS ONLY
    Works with both MySQL and PostgreSQL clients
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

    # BASIC CRUD OPERATIONS
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

    # SEARCH AND FILTER OPERATIONS
    def search(self, filters: Dict[str, Any], limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Search records with filters."""
        where_clause = ' AND '.join([f"{k} = %s" for k in filters.keys()])
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause}"