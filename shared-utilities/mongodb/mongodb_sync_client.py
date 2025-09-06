# shared-utilities/mongodb/mongodb_sync_client.py
import logging
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class MongoDBSyncClient:
    """
    MongoDB connection client - ONLY handles connections and raw operations.
    CRUD operations are in MongoDBRepository.
    """

    def __init__(self, mongo_uri: str, db_name: str):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        """Create connection to MongoDB."""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")  # Test connection
            self.db = self.client[self.db_name]
            logger.info("Successfully connected to MongoDB")
            return True
        except PyMongoError as e:
            logger.error(f"MongoDB connection failed: {e}")
            return False

    def get_collection(self, collection_name: str):
        """Get collection object."""
        if self.db is None:
            raise RuntimeError("Database connection not available")
        return self.db[collection_name]

    def execute_find(self, collection_name: str, query: dict = None, limit: int = 0):
        """Execute find operation."""
        collection = self.get_collection(collection_name)
        cursor = collection.find(query or {})
        if limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)

    def execute_find_one(self, collection_name: str, query: dict):
        """Execute find_one operation."""
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def execute_insert_one(self, collection_name: str, document: dict):
        """Execute insert_one operation."""
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)

    def execute_update_one(self, collection_name: str, filter_query: dict, update_data: dict):
        """Execute update_one operation."""
        collection = self.get_collection(collection_name)
        return collection.update_one(filter_query, {"$set": update_data})

    def execute_delete_one(self, collection_name: str, query: dict):
        """Execute delete_one operation."""
        collection = self.get_collection(collection_name)
        return collection.delete_one(query)

    def close(self):
        """Close connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
