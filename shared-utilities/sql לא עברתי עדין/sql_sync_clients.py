# shared-utilities/sql/sql_sync_clients.py
import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union

import mysql.connector
import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)


class MySQLSyncClient:
    """
    Synchronous MySQL client with connection pooling and transaction support.
    """

    def __init__(self,
                 host: str,
                 user: str,
                 password: str,
                 database: str,
                 port: int = 3306,
                 pool_size: int = 5,
                 **kwargs):
        """
        Initialize MySQL client with connection pooling.

        Args:
            host: MySQL host
            user: Username
            password: Password
            database: Database name
            port: MySQL port (default 3306)
            pool_size: Connection pool size
            **kwargs: Additional MySQL connector arguments
        """
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port,
            'autocommit': False,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            **kwargs
        }

        self.pool_config = {
            'pool_name': 'mysql_pool',
            'pool_size': pool_size,
            'pool_reset_session': True,
            **self.config
        }

        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(**self.pool_config)
            logger.info(f"MySQL connection pool created with {pool_size} connections")
        except Exception as e:
            logger.error(f"Failed to create MySQL pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Get connection from pool with automatic cleanup."""
        connection = None
        try:
            connection = self.pool.get_connection()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if connection:
                connection.close()

    @contextmanager
    def get_cursor(self, dictionary: bool = True):
        """Get cursor with automatic connection management."""
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=dictionary)
            try:
                yield cursor, connection
            finally:
                cursor.close()

    def execute_query(self,
                      query: str,
                      params: Optional[tuple] = None,
                      fetch: bool = True) -> Union[List[Dict], int]:
        """
        Execute a single query.

        Args:
            query: SQL query
            params: Query parameters
            fetch: Whether to fetch results (SELECT) or return affected rows

        Returns:
            List of dictionaries for SELECT, affected row count for DML
        """
        with self.get_cursor() as (cursor, connection):
            cursor.execute(query, params or ())

            if fetch:
                results = cursor.fetchall()
                return results
            else:
                connection.commit()
                return cursor.rowcount

    def execute_many(self,
                     query: str,
                     params_list: List[tuple]) -> int:
        """
        Execute query with multiple parameter sets.

        Args:
            query: SQL query
            params_list: List of parameter tuples

        Returns:
            Number of affected rows
        """
        with self.get_cursor() as (cursor, connection):
            cursor.executemany(query, params_list)
            connection.commit()
            return cursor.rowcount

    def select_one(self,
                   query: str,
                   params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """
        Execute SELECT query and return first result.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            First row as dictionary or None
        """
        with self.get_cursor() as (cursor, connection):
            cursor.execute(query, params or ())
            return cursor.fetchone()

    def select_all(self,
                   query: str,
                   params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute SELECT query and return all results.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List of rows as dictionaries
        """
        return self.execute_query(query, params, fetch=True)

    def insert(self,
               table: str,
               data: Dict[str, Any]) -> int:
        """
        Insert single record.

        Args:
            table: Table name
            data: Column-value pairs

        Returns:
            Inserted record ID
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        with self.get_cursor() as (cursor, connection):
            cursor.execute(query, tuple(data.values()))
            connection.commit()
            return cursor.lastrowid

    def insert_many(self,
                    table: str,
                    data_list: List[Dict[str, Any]]) -> int:
        """
        Insert multiple records.

        Args:
            table: Table name
            data_list: List of column-value dictionaries

        Returns:
            Number of inserted rows
        """
        if not data_list:
            return 0

        columns = ', '.join(data_list[0].keys())
        placeholders = ', '.join([f":{k}" for k in data_list[0].keys()])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        with self.get_connection() as connection:
            result = connection.execute(text(query), data_list)
            connection.commit()
            return result.rowcount

    def update_dict(self,
                    table: str,
                    data: Dict[str, Any],
                    where_clause: str,
                    where_params: Optional[Dict[str, Any]] = None) -> int:
        """
        Update records using dictionary.

        Args:
            table: Table name
            data: Column-value pairs to update
            where_clause: WHERE clause with named parameters
            where_params: WHERE clause parameters

        Returns:
            Number of affected rows
        """
        set_clause = ', '.join([f"{k} = :{k}" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

        params = data.copy()
        if where_params:
            params.update(where_params)

        return self.execute_statement(query, params)

    def delete_dict(self,
                    table: str,
                    where_clause: str,
                    where_params: Optional[Dict[str, Any]] = None) -> int:
        """
        Delete records using dictionary parameters.

        Args:
            table: Table name
            where_clause: WHERE clause with named parameters
            where_params: WHERE clause parameters

        Returns:
            Number of deleted rows
        """
        query = f"DELETE FROM {table} WHERE {where_clause}"
        return self.execute_statement(query, where_params or {})

    @contextmanager
    def transaction(self):
        """Transaction context manager using SQLAlchemy session."""
        with self.get_session() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get table column information.

        Args:
            table_name: Table name

        Returns:
            List of column information dictionaries
        """
        from sqlalchemy import inspect

        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)

        return [
            {
                'name': col['name'],
                'type': str(col['type']),
                'nullable': col['nullable'],
                'default': col['default'],
                'primary_key': col.get('primary_key', False)
            }
            for col in columns
        ]

    def get_table_names(self) -> List[str]:
        """Get list of all table names in the database."""
        from sqlalchemy import inspect

        inspector = inspect(self.engine)
        return inspector.get_table_names()

    def close(self):
        """Close all connections and dispose engine."""
        try:
            self.engine.dispose()
            logger.info("SQLAlchemy engine disposed")
        except Exception as e:
            logger.error(f"Error disposing SQLAlchemy engine: {e}")


# Utility functions for creating clients
def create_mysql_client(host: str,
                        user: str,
                        password: str,
                        database: str,
                        **kwargs) -> MySQLSyncClient:
    """Create MySQL client with standard settings."""
    return MySQLSyncClient(host, user, password, database, **kwargs)


def create_postgresql_client(host: str,
                             user: str,
                             password: str,
                             database: str,
                             **kwargs) -> PostgreSQLSyncClient:
    """Create PostgreSQL client with standard settings."""
    return PostgreSQLSyncClient(host, user, password, database, **kwargs)


def create_sqlalchemy_client(database_url: str, **kwargs) -> SQLAlchemySyncClient:
    """Create SQLAlchemy client with standard settings."""
    return SQLAlchemySyncClient(database_url, **kwargs)


# Factory function for creating clients based on database type
def create_sql_client(db_type: str, **config) -> Union[MySQLSyncClient, PostgreSQLSyncClient, SQLAlchemySyncClient]:
    """
    Factory function to create appropriate SQL client.

    Args:
        db_type: Database type ('mysql', 'postgresql', 'sqlalchemy')
        **config: Database configuration parameters

    Returns:
        Appropriate SQL client instance
    """
    if db_type.lower() == 'mysql':
        return create_mysql_client(**config)
    elif db_type.lower() in ['postgresql', 'postgres']:
        return create_postgresql_client(**config)
    elif db_type.lower() == 'sqlalchemy':
        return create_sqlalchemy_client(**config)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


# Example usage and testing
if __name__ == "__main__":

    # MySQL example
    def mysql_example():
        client = create_mysql_client(
            host="localhost",
            user="user",
            password="password",
            database="test_db"
        )

        # Create table
        create_table_query = """
                             CREATE TABLE IF NOT EXISTS users \
                             ( \
                                 id \
                                 INT \
                                 AUTO_INCREMENT \
                                 PRIMARY \
                                 KEY, \
                                 name \
                                 VARCHAR \
                             ( \
                                 100 \
                             ) NOT NULL,
                                 email VARCHAR \
                             ( \
                                 100 \
                             ) UNIQUE NOT NULL,
                                 age INT,
                                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                 ) \
                             """
        client.execute_query(create_table_query, fetch=False)

        # Insert single record
        user_id = client.insert('users', {
            'name': 'John Doe',
            'email': 'john@example.com',
            'age': 30
        })
        print(f"Inserted user with ID: {user_id}")

        # Insert multiple records
        users_data = [
            {'name': 'Jane Smith', 'email': 'jane@example.com', 'age': 25},
            {'name': 'Bob Johnson', 'email': 'bob@example.com', 'age': 35}
        ]
        inserted_count = client.insert_many('users', users_data)
        print(f"Inserted {inserted_count} users")

        # Select all users
        all_users = client.select_all("SELECT * FROM users")
        print(f"All users: {all_users}")

        # Update user
        updated_count = client.update(
            'users',
            {'age': 31},
            'id = %s',
            (user_id,)
        )
        print(f"Updated {updated_count} users")

        # Transaction example
        try:
            with client.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET age = age + 1 WHERE id = %s", (user_id,))
                cursor.execute("INSERT INTO users (name, email, age) VALUES (%s, %s, %s)",
                               ('Transaction User', 'transaction@example.com', 40))
                # Transaction will be committed automatically
        except Exception as e:
            print(f"Transaction failed: {e}")

        client.close_pool()


    # PostgreSQL example
    def postgresql_example():
        client = create_postgresql_client(
            host="localhost",
            user="user",
            password="password",
            database="test_db"
        )

        # Create table
        create_table_query = """
                             CREATE TABLE IF NOT EXISTS products \
                             ( \
                                 id \
                                 SERIAL \
                                 PRIMARY \
                                 KEY, \
                                 name \
                                 VARCHAR \
                             ( \
                                 100 \
                             ) NOT NULL,
                                 price DECIMAL \
                             ( \
                                 10, \
                                 2 \
                             ),
                                 category VARCHAR \
                             ( \
                                 50 \
                             ),
                                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                 ) \
                             """
        client.execute_query(create_table_query, fetch=False)

        # Insert with RETURNING
        product_id = client.insert('products', {
            'name': 'Laptop',
            'price': 999.99,
            'category': 'Electronics'
        })
        print(f"Inserted product with ID: {product_id}")

        # Select with parameters
        expensive_products = client.select_all(
            "SELECT * FROM products WHERE price > %s",
            (500,)
        )
        print(f"Expensive products: {expensive_products}")


    # SQLAlchemy example
    def sqlalchemy_example():
        # MySQL URL example: mysql+pymysql://user:password@localhost/test_db
        # PostgreSQL URL example: postgresql://user:password@localhost/test_db
        client = create_sqlalchemy_client(
            "sqlite:///test.db"  # SQLite for simplicity
        )

        # Create table
        create_table_query = """
                             CREATE TABLE IF NOT EXISTS orders \
                             ( \
                                 id \
                                 INTEGER \
                                 PRIMARY \
                                 KEY, \
                                 customer_name \
                                 TEXT \
                                 NOT \
                                 NULL, \
                                 amount \
                                 DECIMAL \
                             ( \
                                 10, \
                                 2 \
                             ),
                                 status TEXT DEFAULT 'pending',
                                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                 ) \
                             """
        client.execute_statement(create_table_query)

        # Insert using dictionary
        client.insert_dict('orders', {
            'customer_name': 'Alice Johnson',
            'amount': 150.75,
            'status': 'completed'
        })

        # Insert multiple records
        orders_data = [
            {'customer_name': 'Bob Smith', 'amount': 75.50, 'status': 'pending'},
            {'customer_name': 'Carol White', 'amount': 200.00, 'status': 'completed'}
        ]
        client.insert_many_dicts('orders', orders_data)

        # Select with named parameters
        pending_orders = client.select_all(
            "SELECT * FROM orders WHERE status = :status",
            {'status': 'pending'}
        )
        print(f"Pending orders: {pending_orders}")

        # Update with named parameters
        updated_count = client.update_dict(
            'orders',
            {'status': 'shipped'},
            'status = :old_status AND amount > :min_amount',
            {'old_status': 'completed', 'min_amount': 100}
        )
        print(f"Updated {updated_count} orders to shipped")

        # Get table information
        table_info = client.get_table_info('orders')
        print(f"Orders table structure: {table_info}")

        client.close()


    # ORM-style helper class for SQLAlchemy
    class BaseRepository:
        """
        Base repository class for common database operations.
        """

        def __init__(self, client: SQLAlchemySyncClient, table_name: str):
            self.client = client
            self.table_name = table_name

        def create(self, data: Dict[str, Any]) -> int:
            """Create new record."""
            return self.client.insert_dict(self.table_name, data)

        def find_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
            """Find record by ID."""
            return self.client.select_one(
                f"SELECT * FROM {self.table_name} WHERE id = :id",
                {'id': record_id}
            )

        def find_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
            """Find all records with pagination."""
            return self.client.select_all(
                f"SELECT * FROM {self.table_name} LIMIT :limit OFFSET :offset",
                {'limit': limit, 'offset': offset}
            )

        def find_by_field(self, field: str, value: Any) -> List[Dict[str, Any]]:
            """Find records by field value."""
            return self.client.select_all(
                f"SELECT * FROM {self.table_name} WHERE {field} = :value",
                {'value': value}
            )

        def update_by_id(self, record_id: int, data: Dict[str, Any]) -> int:
            """Update record by ID."""
            return self.client.update_dict(
                self.table_name,
                data,
                'id = :id',
                {'id': record_id}
            )

        def delete_by_id(self, record_id: int) -> int:
            """Delete record by ID."""
            return self.client.delete_dict(
                self.table_name,
                'id = :id',
                {'id': record_id}
            )

        def count(self, where_clause: str = "", where_params: Optional[Dict[str, Any]] = None) -> int:
            """Count records."""
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"

            result = self.client.select_one(query, where_params or {})
            return result['count'] if result else 0


    # Repository pattern example
    def repository_example():
        client = create_sqlalchemy_client("sqlite:///test.db")

        # Create users repository
        users_repo = BaseRepository(client, 'users')

        # Create user
        user_id = users_repo.create({
            'name': 'Repository User',
            'email': 'repo@example.com',
            'age': 28
        })

        # Find user
        user = users_repo.find_by_id(user_id)
        print(f"Found user: {user}")

        # Update user
        users_repo.update_by_id(user_id, {'age': 29})

        # Count users
        total_users = users_repo.count()
        print(f"Total users: {total_users}")

        client.close()


    # Run examples (comment out database connections you don't have)
    try:
        # mysql_example()
        # postgresql_example()
        sqlalchemy_example()
        repository_example()
        print("All SQL client examples completed successfully!")
    except Exception as e:
        print(f"Example failed: {e}")
        logger.error(f"SQL client example error: {e}", exc_info=True)
        return 0

    columns = ', '.join(data_list[0].keys())
    placeholders = ', '.join(['%s'] * len(data_list[0]))
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

    params_list = [tuple(data.values()) for data in data_list]
    return self.execute_many(query, params_list)


def update(self,
           table: str,
           data: Dict[str, Any],
           where_clause: str,
           where_params: Optional[tuple] = None) -> int:
    """
    Update records.

    Args:
        table: Table name
        data: Column-value pairs to update
        where_clause: WHERE clause
        where_params: WHERE clause parameters

    Returns:
        Number of affected rows
    """
    set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

    params = list(data.values())
    if where_params:
        params.extend(where_params)

    return self.execute_query(query, tuple(params), fetch=False)


def delete(self,
           table: str,
           where_clause: str,
           where_params: Optional[tuple] = None) -> int:
    """
    Delete records.

    Args:
        table: Table name
        where_clause: WHERE clause
        where_params: WHERE clause parameters

    Returns:
        Number of deleted rows
    """
    query = f"DELETE FROM {table} WHERE {where_clause}"
    return self.execute_query(query, where_params, fetch=False)


@contextmanager
def transaction(self):
    """Transaction context manager."""
    with self.get_connection() as connection:
        try:
            connection.start_transaction()
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise


def close_pool(self):
    """Close all connections in pool."""
    try:
        # Note: MySQL connector doesn't have a direct pool close method
        # The pool will be garbage collected
        logger.info("MySQL connection pool closed")
    except Exception as e:
        logger.error(f"Error closing MySQL pool: {e}")


class PostgreSQLSyncClient:
    """
    Synchronous PostgreSQL client with connection pooling.
    """

    def __init__(self,
                 host: str,
                 user: str,
                 password: str,
                 database: str,
                 port: int = 5432,
                 **kwargs):
        """
        Initialize PostgreSQL client.

        Args:
            host: PostgreSQL host
            user: Username
            password: Password
            database: Database name
            port: PostgreSQL port (default 5432)
            **kwargs: Additional psycopg2 arguments
        """
        self.dsn = f"host={host} port={port} user={user} password={password} dbname={database}"
        self.connection_params = kwargs

        # Test connection
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version()")
                    version = cursor.fetchone()[0]
                    logger.info(f"Connected to PostgreSQL: {version}")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Get connection with automatic cleanup."""
        connection = None
        try:
            connection = psycopg2.connect(self.dsn, **self.connection_params)
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if connection:
                connection.close()

    @contextmanager
    def get_cursor(self, cursor_factory=None):
        """Get cursor with automatic connection management."""
        with self.get_connection() as connection:
            cursor_factory = cursor_factory or psycopg2.extras.RealDictCursor
            cursor = connection.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor, connection
            finally:
                cursor.close()

    def execute_query(self,
                      query: str,
                      params: Optional[tuple] = None,
                      fetch: bool = True) -> Union[List[Dict], int]:
        """
        Execute a single query.

        Args:
            query: SQL query
            params: Query parameters
            fetch: Whether to fetch results

        Returns:
            List of dictionaries for SELECT, affected row count for DML
        """
        with self.get_cursor() as (cursor, connection):
            cursor.execute(query, params or ())

            if fetch:
                results = cursor.fetchall()
                # Convert RealDictRow to regular dict
                return [dict(row) for row in results]
            else:
                connection.commit()
                return cursor.rowcount

    def execute_many(self,
                     query: str,
                     params_list: List[tuple]) -> int:
        """Execute query with multiple parameter sets."""
        with self.get_cursor() as (cursor, connection):
            cursor.executemany(query, params_list)
            connection.commit()
            return cursor.rowcount

    def select_one(self,
                   query: str,
                   params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Execute SELECT query and return first result."""
        with self.get_cursor() as (cursor, connection):
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return dict(result) if result else None

    def select_all(self,
                   query: str,
                   params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return all results."""
        return self.execute_query(query, params, fetch=True)

    def insert(self,
               table: str,
               data: Dict[str, Any],
               returning: str = "id") -> Any:
        """
        Insert single record with RETURNING clause.

        Args:
            table: Table name
            data: Column-value pairs
            returning: Column to return (default 'id')

        Returns:
            Value of returned column
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING {returning}"

        with self.get_cursor() as (cursor, connection):
            cursor.execute(query, tuple(data.values()))
            result = cursor.fetchone()
            connection.commit()
            return result[returning] if result else None

    def insert_many(self,
                    table: str,
                    data_list: List[Dict[str, Any]]) -> int:
        """Insert multiple records."""
        if not data_list:
            return 0

        columns = ', '.join(data_list[0].keys())
        placeholders = ', '.join(['%s'] * len(data_list[0]))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        params_list = [tuple(data.values()) for data in data_list]
        return self.execute_many(query, params_list)

    def update(self,
               table: str,
               data: Dict[str, Any],
               where_clause: str,
               where_params: Optional[tuple] = None) -> int:
        """Update records."""
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

        params = list(data.values())
        if where_params:
            params.extend(where_params)

        return self.execute_query(query, tuple(params), fetch=False)

    def delete(self,
               table: str,
               where_clause: str,
               where_params: Optional[tuple] = None) -> int:
        """Delete records."""
        query = f"DELETE FROM {table} WHERE {where_clause}"
        return self.execute_query(query, where_params, fetch=False)

    @contextmanager
    def transaction(self):
        """Transaction context manager."""
        with self.get_connection() as connection:
            try:
                yield connection
                connection.commit()
            except Exception:
                connection.rollback()
                raise


class SQLAlchemySyncClient:
    """
    SQLAlchemy-based client supporting multiple databases.
    """

    def __init__(self,
                 database_url: str,
                 pool_size: int = 5,
                 max_overflow: int = 10,
                 echo: bool = False,
                 **kwargs):
        """
        Initialize SQLAlchemy client.

        Args:
            database_url: Database URL (e.g., 'mysql://user:pass@host/db')
            pool_size: Connection pool size
            max_overflow: Max overflow connections
            echo: Echo SQL statements
            **kwargs: Additional engine arguments
        """
        self.database_url = database_url

        try:
            self.engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_pre_ping=True,
                echo=echo,
                **kwargs
            )

            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("SQLAlchemy engine created successfully")

        except Exception as e:
            logger.error(f"Failed to create SQLAlchemy engine: {e}")
            raise

    @contextmanager
    def get_session(self):
        """Get SQLAlchemy session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def get_connection(self):
        """Get raw connection for direct SQL execution."""
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()

    def execute_query(self,
                      query: str,
                      params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute raw SQL query and return results.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List of row dictionaries
        """
        with self.get_connection() as connection:
            result = connection.execute(text(query), params or {})
            return [dict(row._mapping) for row in result]

    def execute_statement(self,
                          query: str,
                          params: Optional[Dict[str, Any]] = None) -> int:
        """
        Execute DML statement and return affected rows.

        Args:
            query: SQL statement
            params: Statement parameters

        Returns:
            Number of affected rows
        """
        with self.get_connection() as connection:
            result = connection.execute(text(query), params or {})
            connection.commit()
            return result.rowcount

    def select_one(self,
                   query: str,
                   params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Execute SELECT query and return first result."""
        results = self.execute_query(query, params)
        return results[0] if results else None

    def select_all(self,
                   query: str,
                   params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return all results."""
        return self.execute_query(query, params)

    def insert_dict(self,
                    table: str,
                    data: Dict[str, Any]) -> int:
        """
        Insert single record using dictionary.

        Args:
            table: Table name
            data: Column-value pairs

        Returns:
            Number of affected rows
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join([f":{k}" for k in data.keys()])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        return self.execute_statement(query, data)

    def insert_many_dicts(self,
                          table: str,
                          data_list: List[Dict[str, Any]]) -> int:
        """
        Insert multiple records using dictionaries.

        Args:
            table: Table name
            data_list: List of column-value dictionaries

        Returns:
            Number of affected rows
        """
        if not data_list: