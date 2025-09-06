# shared-utilities/sql/postgresql_repository.py
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class PostgreSQLRepository:
    """
    PostgreSQL CRUD repository - ONLY handles CRUD operations.
    Requires PostgreSQLSyncClient for connections.
    """

    def __init__(self, client, table_name: str):
        self.client = client
        self.table_name = table_name

    def create(self, data: Dict[str, Any], returning: str = "id") -> Any:
        """Create new record with RETURNING clause."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING {returning}"
        result = self.client.execute_returning(query, tuple(data.values()))
        return result[returning] if result else None

    def get_by_id(self, id_value: Any, id_column: str = "id") -> Optional[Dict[str, Any]]:
        """Get record by ID."""
        query = f"SELECT * FROM {self.table_name} WHERE {id_column} = %s"
        results = self.client.execute_query(query, (id_value,))
        return results[0] if results else None

    def get_all(self, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all records with optional pagination."""
        query = f"SELECT * FROM {self.table_name}"
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        return self.client.execute_query(query)

    def update(self, id_value: Any, data: Dict[str, Any], id_column: str = "id") -> int:
        """Update record by ID and return affected rows."""
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {id_column} = %s"
        params = list(data.values()) + [id_value]
        return self.client.execute_query(query, params, fetch=False)

    def delete(self, id_value: Any, id_column: str = "id") -> int:
        """Delete record by ID and return affected rows."""
        query = f"DELETE FROM {self.table_name} WHERE {id_column} = %s"
        return self.client.execute_query(query, (id_value,), fetch=False)

    def search(self, filters: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Search records with filters."""
        where_clause = ' AND '.join([f"{k} = %s" for k in filters.keys()])
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause} LIMIT {limit}"
        return self.client.execute_query(query, tuple(filters.values()))

    def count(self, filters: Dict[str, Any] = None) -> int:
        """Count records with optional filters."""
        query = f"SELECT COUNT(*) as count FROM {self.table_name}"
        params = ()

        if filters:
            where_clause = ' AND '.join([f"{k} = %s" for k in filters.keys()])
            query += f" WHERE {where_clause}"
            params = tuple(filters.values())

        result = self.client.execute_query(query, params)
        return result[0]['count'] if result else 0