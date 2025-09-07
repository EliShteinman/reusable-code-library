
# ============================================================================
# shared-utilities/sql/mysql_sync_client.py - CONNECTIONS ONLY
# ============================================================================
import mysql.connector
from mysql.connector import pooling
import logging
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)


class MySQLSyncClient:
    """
    MySQL connection client - CONNECTIONS ONLY
    No CRUD operations - only raw mysql operations
    """

    def __init__(self, host: str, user: str, password: str, database: str, pool_size: int = 5):
        self.config = {
            'host': host, 'user': user, 'password': password, 'database': database,
            'autocommit': False, 'charset': 'utf8mb4'
        }
        self.pool_config = {'pool_name': 'mysql_pool', 'pool_size': pool_size, **self.config}

        try:
            self.pool = pooling.MySQLConnectionPool(**self.pool_config)
            logger.info(f"MySQL pool created with {pool_size} connections")
        except Exception as e:
            logger.error(f"Failed to create MySQL pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Get connection from pool with automatic cleanup."""
        conn = None
        try:
            conn = self.pool.get_connection()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if conn:
                conn.close()

    # RAW MYSQL OPERATIONS ONLY
    def execute_query(self, query: str, params=None, fetch=True):
        """Execute raw query - returns results for SELECT, rowcount for others."""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())

            if fetch and query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount

    def execute_insert(self, query: str, params=None) -> int:
        """Execute raw INSERT and return last inserted ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid

    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute query with multiple parameter sets."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount

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

    def close(self):
        """Connection pool cleanup."""
        logger.info("MySQL connection pool closed")