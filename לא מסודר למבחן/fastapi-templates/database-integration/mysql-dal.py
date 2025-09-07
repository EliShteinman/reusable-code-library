# fastapi-templates/database-integration/mysql-dal.py
import mysql.connector
from mysql.connector import pooling, Error
from typing import List, Dict, Any, Union, Optional


class MySQLDataLoader:
    """
    Data Access Layer (DAL) for MySQL.
    Template with connection pool for enhanced performance and reliability.
    """

    def __init__(self, host: str, user: str, password: str, database: str, pool_size: int = 5):
        """
        Initializes the DataLoader with database configuration for the pool.
        """
        self.db_config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
        }
        self.pool_size = pool_size
        self.pool = None

    def connect(self) -> None:
        """
        Creates a MySQL connection pool.
        """
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="app_pool",
                pool_size=self.pool_size,
                **self.db_config,
            )
            print("Successfully created MySQL connection pool")
        except Error as e:
            print(f"Error while creating connection pool: {e}")
            self.pool = None

    def close(self) -> None:
        """
        Connection pool management is handled by its lifecycle.
        No explicit close action is needed for the pool itself.
        """
        print("Connection pool lifecycle is managed automatically.")

    def get_all_data(self, table_name: str = "data") -> Union[List[Dict], Dict[str, str]]:
        """
        Fetches all records from the specified table using a connection from the pool.
        """
        if not self.pool:
            return {"error": "Connection pool is not available."}

        connection = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {table_name}")
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error reading data from MySQL table: {e}")
            return {"error": str(e)}
        finally:
            if connection and connection.is_connected():
                connection.close()

    def get_item_by_id(self, item_id: int, table_name: str = "data") -> Optional[Dict]:
        """
        Fetches a single record by its ID.
        """
        if not self.pool:
            return {"error": "Connection pool is not available."}

        query = f"SELECT * FROM {table_name} WHERE ID = %s"
        connection = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (item_id,))
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error fetching item by ID: {e}")
            return {"error": str(e)}
        finally:
            if connection and connection.is_connected():
                connection.close()

    def create_item(self, data: Dict[str, Any], table_name: str = "data") -> Union[Dict, Dict[str, str]]:
        """
        Creates a new record and returns it with the new ID.
        Template - adapt fields based on your table structure.
        """
        if not self.pool:
            return {"error": "Connection pool is not available."}

        # Example for table with first_name, last_name
        # Adapt this query based on your table structure
        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        connection = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, tuple(data.values()))
            connection.commit()
            new_id = cursor.lastrowid
            return {"ID": new_id, **data}
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error creating item: {e}")
            return {"error": str(e)}
        finally:
            if connection and connection.is_connected():
                connection.close()

    def update_item(self, item_id: int, data: Dict[str, Any], table_name: str = "data") -> Optional[
        Union[Dict, Dict[str, str]]]:
        """
        Updates an existing record.
        Template - adapt based on your table structure.
        """
        if not self.pool:
            return {"error": "Connection pool is not available."}

        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE ID = %s"

        connection = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            values = list(data.values()) + [item_id]
            cursor.execute(query, values)
            connection.commit()
            if cursor.rowcount == 0:
                return None  # No record found to update
            return {"ID": item_id, **data}
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error updating item: {e}")
            return {"error": str(e)}
        finally:
            if connection and connection.is_connected():
                connection.close()

    def delete_item(self, item_id: int, table_name: str = "data") -> Optional[Union[Dict, Dict[str, str]]]:
        """
        Deletes an existing record.
        """
        if not self.pool:
            return {"error": "Connection pool is not available."}

        query = f"DELETE FROM {table_name} WHERE ID = %s"
        connection = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, (item_id,))
            connection.commit()
            if cursor.rowcount == 0:
                return None  # No record found to delete
            return {"message": "Item deleted successfully"}
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error deleting item: {e}")
            return {"error": str(e)}
        finally:
            if connection and connection.is_connected():
                connection.close()

    def execute_custom_query(self, query: str, params: tuple = None) -> Union[List[Dict], Dict[str, str]]:
        """
        Execute custom SQL query. Use with caution.
        """
        if not self.pool:
            return {"error": "Connection pool is not available."}

        connection = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                return {"message": f"Query executed successfully. Affected rows: {cursor.rowcount}"}
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error executing custom query: {e}")
            return {"error": str(e)}
        finally:
            if connection and connection.is_connected():
                connection.close()