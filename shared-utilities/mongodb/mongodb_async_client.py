
# ============================================================================
# shared-utilities/mongodb/mongodb_async_client.py - ASYNC CONNECTIONS ONLY
# ============================================================================
import asyncio
import logging
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class MongoDBAsyncClient:
    """
    ASYNC MongoDB client - CONNECTIONS ONLY
    No CRUD operations - only raw motor operations
    """

    def __init__(self, mongo_uri: str, db_name: str):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.connected = False

    async def connect(self):
        """Create async connection to MongoDB."""
        try:
            self.client = AsyncMongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            await self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            self.connected = True
            logger.info("Successfully connected to MongoDB (async)")
            await self._setup_indexes()
            return True
        except PyMongoError as e:
            logger.error(f"MongoDB async connection failed: {e}")
            return False

    async def _setup_indexes(self):
        """Setup common indexes."""
        try:
            logger.info("MongoDB async client ready for index setup")
        except PyMongoError as e:
            logger.warning(f"Failed to create indexes: {e}")

    def get_collection(self, collection_name: str):
        """Get collection object."""
        if self.db is None:
            raise RuntimeError("Database connection not available")
        return self.db[collection_name]

    # RAW ASYNC MOTOR OPERATIONS ONLY
    async def execute_find(self, collection_name: str, query: dict = None, limit: int = 0, sort: List[tuple] = None):
        """Execute find operation."""
        collection = self.get_collection(collection_name)
        cursor = collection.find(query or {})
        if sort:
            cursor = cursor.sort(sort)
        if limit > 0:
            cursor = cursor.limit(limit)
        return await cursor.to_list(length=limit if limit > 0 else None)

    async def execute_find_one(self, collection_name: str, query: dict):
        """Execute find_one operation."""
        collection = self.get_collection(collection_name)
        return await collection.find_one(query)

    async def execute_insert_one(self, collection_name: str, document: dict):
        """Execute insert_one operation."""
        collection = self.get_collection(collection_name)
        return await collection.insert_one(document)

    async def execute_insert_many(self, collection_name: str, documents: List[dict]):
        """Execute insert_many operation."""
        collection = self.get_collection(collection_name)
        return await collection.insert_many(documents, ordered=False)

    async def execute_update_one(self, collection_name: str, filter_query: dict, update_data: dict):
        """Execute update_one operation."""
        collection = self.get_collection(collection_name)
        return await collection.update_one(filter_query, {"$set": update_data})

    async def execute_delete_one(self, collection_name: str, query: dict):
        """Execute delete_one operation."""
        collection = self.get_collection(collection_name)
        return await collection.delete_one(query)

    async def execute_count_documents(self, collection_name: str, query: dict = None):
        """Execute count_documents operation."""
        collection = self.get_collection(collection_name)
        return await collection.count_documents(query or {})

    async def close(self):
        """Close async connection."""
        if self.client and self.connected:
            self.client.close()
            self.connected = False
            logger.info("MongoDB async connection closed")