# shared-utilities/mongodb/mongo_client.py
import logging
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError
from typing import Optional

logger = logging.getLogger(__name__)


class SingletonMongoClient:
    """
    A thread-safe, singleton wrapper for the AsyncMongoClient.
    Ensures only one instance of the client is created per process.

    Usage:
    # First initialization (e.g., on application startup)
    client = SingletonMongoClient(uri="mongodb://...", db_name="my_db")
    await client.connect_and_verify()

    # Subsequent calls anywhere in the app
    client = SingletonMongoClient() # No arguments needed
    collection = client.get_collection("my_collection")
    """
    _instance: Optional[AsyncMongoClient] = None
    _connection_info: Optional[dict] = None

    def __new__(cls, uri: str = None, db_name: str = None, *args, **kwargs):
        if cls._instance is None:
            if uri is None or db_name is None:
                raise ValueError("URI and db_name must be provided on first initialization")
            logger.info("Creating new SingletonMongoClient instance.")

            # Create the actual client instance
            instance = AsyncMongoClient(uri, *args, **kwargs)
            cls._instance = instance

            # Store connection info for later use
            cls._connection_info = {"uri": uri, "db_name": db_name}

        return cls._instance

    def __init__(self, *args, **kwargs):
        # The __init__ of the actual client is handled by AsyncMongoClient's constructor.
        # This method is here to prevent re-initialization.
        pass

    @classmethod
    def get_instance(cls) -> AsyncMongoClient:
        """Get the existing singleton instance."""
        if cls._instance is None:
            raise RuntimeError("MongoClient has not been initialized. Call SingletonMongoClient(uri, db_name) first.")
        return cls._instance

    @classmethod
    async def connect_and_verify(cls):
        """Verifies the connection to the database by sending a ping command."""
        instance = cls.get_instance()
        try:
            await instance.admin.command("ping")
            logger.info("MongoDB connection verified successfully.")
        except PyMongoError as e:
            logger.error(f"MongoDB connection verification failed: {e}")
            raise

    @classmethod
    def get_collection(cls, collection_name: str, db_name: str = None):
        """Gets a collection from the database."""
        instance = cls.get_instance()
        target_db_name = db_name or cls._connection_info["db_name"]
        if not target_db_name:
            raise ValueError("Database name must be provided either at init or in this call.")
        return instance[target_db_name][collection_name]

    @classmethod
    def is_connected(cls) -> bool:
        """Checks if the singleton instance has been initialized."""
        return cls._instance is not None

    @classmethod
    def close(cls):
        """Closes the connection."""
        if cls._instance:
            cls._instance.close()
            cls._instance = None
            logger.info("MongoDB singleton connection closed.")