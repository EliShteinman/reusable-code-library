# shared-utilities/sql/__init__.py
"""
SQL utilities with clear separation between connection clients and CRUD repositories.
"""

from .mysql_sync_client import MySQLSyncClient
from .mysql_repository import MySQLRepository
from .postgresql_sync_client import PostgreSQLSyncClient
from .postgresql_repository import PostgreSQLRepository

__all__ = [
    'MySQLSyncClient',
    'MySQLRepository',
    'PostgreSQLSyncClient',
    'PostgreSQLRepository'
]


# Quick setup functions
def setup_mysql(host: str, user: str, password: str, database: str, table_name: str):
    """Quick setup for MySQL client + repository."""
    client = MySQLSyncClient(host, user, password, database)
    repository = MySQLRepository(client, table_name)
    return client, repository


def setup_postgresql(host: str, user: str, password: str, database: str, table_name: str, port: int = 5432):
    """Quick setup for PostgreSQL client + repository."""
    client = PostgreSQLSyncClient(host, user, password, database, port)
    repository = PostgreSQLRepository(client, table_name)
    return client, repository


# Usage examples
def example_mysql_usage():
    """Example of proper separation."""
    # 1. Create connection client
    client = MySQLSyncClient("localhost", "root", "password", "exam_db")

    # 2. Create repository for specific table
    users_repo = MySQLRepository(client, "users")

    # 3. Use repository for CRUD
    user_id = users_repo.create({"name": "John", "email": "john@test.com"})
    user = users_repo.get_by_id(user_id)
    users_repo.update(user_id, {"name": "Jane"})
    users_repo.delete(user_id)

    # 4. Close connection
    client.close()


def example_postgresql_usage():
    """Example of proper separation."""
    # Quick setup
    client, products_repo = setup_postgresql(
        "localhost", "postgres", "password", "exam_db", "products"
    )

    # Use repository
    product_id = products_repo.create({"name": "Laptop", "price": 999.99})
    product = products_repo.get_by_id(product_id)
    products_repo.update(product_id, {"price": 899.99})