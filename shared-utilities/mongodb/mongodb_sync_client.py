# ============================================================================
# shared-utilities/mongodb/mongodb_sync_client.py - CONNECTIONS ONLY
# ============================================================================
import logging
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class MongoDBSyncClient:
    """
    SYNC MongoDB client - CONNECTIONS ONLY
    No CRUD operations - only raw pymongo operations
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
            logger.info("Successfully connected to MongoDB (sync)")
            self._setup_indexes()
            return True
        except PyMongoError as e:
            logger.error(f"MongoDB connection failed: {e}")
            return False

    def _setup_indexes(self):
        """Setup common indexes."""
        try:
            # We'll setup indexes per collection in repository
            logger.info("MongoDB sync client ready for index setup")
        except PyMongoError as e:
            logger.warning(f"Failed to create indexes: {e}")

    def get_collection(self, collection_name: str):
        """Get collection object."""
        if self.db is None:
            raise RuntimeError("Database connection not available")
        return self.db[collection_name]

    # RAW PYMONGO OPERATIONS ONLY
    def execute_find(self, collection_name: str, query: dict = None, limit: int = 0, sort: List[tuple] = None):
        """Execute find operation."""
        collection = self.get_collection(collection_name)
        cursor = collection.find(query or {})
        if sort:
            cursor = cursor.sort(sort)
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

    def execute_insert_many(self, collection_name: str, documents: List[dict]):
        """Execute insert_many operation."""
        collection = self.get_collection(collection_name)
        return collection.insert_many(documents, ordered=False)

    def execute_update_one(self, collection_name: str, filter_query: dict, update_data: dict):
        """Execute update_one operation."""
        collection = self.get_collection(collection_name)
        return collection.update_one(filter_query, {"$set": update_data})

    def execute_delete_one(self, collection_name: str, query: dict):
        """Execute delete_one operation."""
        collection = self.get_collection(collection_name)
        return collection.delete_one(query)

    def execute_count_documents(self, collection_name: str, query: dict = None):
        """Execute count_documents operation."""
        collection = self.get_collection(collection_name)
        return collection.count_documents(query or {})

    def execute_aggregate(self, collection_name: str, pipeline: List[dict]):
        """Execute aggregation pipeline."""
        collection = self.get_collection(collection_name)
        return list(collection.aggregate(pipeline))

    def create_index(self, collection_name: str, index_spec, **kwargs):
        """Create index on collection."""
        collection = self.get_collection(collection_name)
        return collection.create_index(index_spec, **kwargs)

    def close(self):
        """Close connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB sync connection closed")




