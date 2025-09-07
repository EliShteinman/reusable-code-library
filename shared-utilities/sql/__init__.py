# ============================================================================
# shared-utilities/sql/__init__.py - FIXED VERSION
# ============================================================================
"""
SQL utilities - CLEAN ARCHITECTURE
Connection clients handle ONLY connections and raw SQL operations
Repository handles ONLY CRUD operations - WORKS WITH BOTH MySQL & PostgreSQL
"""

from .mysql_sync_client import MySQLSyncClient
from .postgresql_sync_client import PostgreSQLSyncClient
from .sql_repository import SQLRepository

__all__ = [
    'MySQLSyncClient',      # MySQL connections only
    'PostgreSQLSyncClient', # PostgreSQL connections only
    'SQLRepository'         # CRUD operations only (works with both clients)
]


# Quick setup functions
def setup_mysql(host: str, user: str, password: str, database: str, table_name: str):
    """Quick setup: MySQL client + SQL repository."""
    client = MySQLSyncClient(host, user, password, database)
    repository = SQLRepository(client, table_name)
    return client, repository


def setup_postgresql(host: str, user: str, password: str, database: str, table_name: str, port: int = 5432):
    """Quick setup: PostgreSQL client + SQL repository."""
    client = PostgreSQLSyncClient(host, user, password, database, port)
    repository = SQLRepository(client, table_name)
    return client, repository