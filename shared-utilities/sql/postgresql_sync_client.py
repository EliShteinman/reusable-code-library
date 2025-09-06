# shared-utilities/sql/postgresql_sync_client.py
import psycopg2
import psycopg2.extras
import logging
from contextlib import contextmanager
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class PostgreSQLSyncClient:
    """
    PostgreSQL connection client - ONLY handles connections.
    CRUD operations are in PostgreSQLRepository.
    """

    def __init__(self, host: str, user: str, password: str, database: str, port: int = 5432):
        self.dsn = f"host={host} port={port} user={user} password={password} dbname={database}"

        # Test connection
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version()")
                    logger.info(f"Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Get connection with automatic cleanup."""
        conn = None
        try:
            conn = psycopg2.connect(self.dsn)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params=None, fetch=True):
        """Execute query with dict results."""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query, params or ())

            if fetch and query.strip().upper().startswith('SELECT'):
                return [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                return cursor.rowcount

    def execute_returning(self, query: str, params=None):
        """Execute INSERT/UPDATE with RETURNING clause."""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query, params or ())
            conn.commit()
            result = cursor.fetchone()
            return dict(result) if result else None