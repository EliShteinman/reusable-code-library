# fastapi-templates/database-integration/mongodb-dal.py
import logging
from typing import Any, Dict, List, Optional
from pymongo import AsyncMongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, PyMongoError

logger = logging.getLogger(__name__)


class MongoDBDataLoader:
    """
    Advanced MongoDB Data Access Layer with async support.
    Template based on the exam solution patterns.
    """

    def __init__(self, mongo_uri: str, db_name: str, collection_name: str):
        """
        Initialize DataLoader with connection parameters.
        Connection happens separately in connect() method.
        """
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name
        # Initialize connections to None - graceful failure pattern
        self.client: Optional[AsyncMongoClient] = None
        self.db: Optional[Database] = None
        self.collection: Optional[Collection] = None

    async def connect(self):
        """
        Creates async connection to MongoDB with proper error handling.
        """
        try:
            self.client = AsyncMongoClient(
                self.mongo_uri, serverSelectionTimeoutMS=5000
            )
            # Ping to verify connection actually works
            await self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info("Successfully connected to MongoDB")
            await self._setup_indexes()
        except PyMongoError as e:
            logger.error(f"DATABASE CONNECTION FAILED: {e}")
            # Don't crash - set to None for graceful degradation
            self.client = None
            self.db = None
            self.collection = None

    async def _setup_indexes(self):
        """
        Creates indexes for better performance and uniqueness.
        Customize based on your data model.
        """
        if self.collection is not None:
            try:
                # Example: Create unique index on ID field
                await self.collection.create_index("ID", unique=True)
                logger.info("Database indexes ensured")
            except PyMongoError as e:
                logger.error(f"Failed to create indexes: {e}")

    def disconnect(self):
        """Closes the connection to the database."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def get_all_data(self) -> List[Dict[str, Any]]:
        """
        Retrieves all documents from collection.
        """
        if self.collection is None:
            raise RuntimeError("Database connection is not available")

        try:
            logger.info("Attempting to retrieve all documents")
            items: List[Dict[str, Any]] = []
            # Async iteration over cursor
            async for item in self.collection.find({}):
                # Convert ObjectId to string for JSON serialization
                item["_id"] = str(item["_id"])
                items.append(item)
            logger.info(f"Retrieved {len(items)} documents from database")
            return items
        except PyMongoError as e:
            logger.error(f"Error retrieving all data: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    async def get_item_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single document by ID.
        """
        if self.collection is None:
            raise RuntimeError("Database connection is not available")

        try:
            logger.info(f"Attempting to retrieve item with ID {item_id}")
            item = await self.collection.find_one({"ID": item_id})
            if item:
                item["_id"] = str(item["_id"])
                logger.info(f"Retrieved item with ID {item_id}")
            else:
                logger.info(f"No item found with ID {item_id}")
            return item
        except PyMongoError as e:
            logger.error(f"Error retrieving item with ID {item_id}: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    async def create_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new document with duplicate handling.
        """
        if self.collection is None:
            raise RuntimeError("Database connection is not available")

        try:
            item_id = item_data.get("ID", "unknown")
            logger.info(f"Attempting to create item with ID {item_id}")

            insert_result = await self.collection.insert_one(item_data)
            created_item = await self.collection.find_one(
                {"_id": insert_result.inserted_id}
            )
            if created_item:
                created_item["_id"] = str(created_item["_id"])
                logger.info(f"Successfully created item with ID {item_id}")
            return created_item
        except DuplicateKeyError:
            logger.warning(f"Attempt to create duplicate item with ID {item_id}")
            raise ValueError(f"Item with ID {item_id} already exists")
        except PyMongoError as e:
            logger.error(f"Error creating item with ID {item_id}: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    async def update_item(
            self, item_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Updates an existing document with partial update support.
        """
        if self.collection is None:
            raise RuntimeError("Database connection is not available")

        try:
            logger.info(f"Attempting to update item with ID {item_id}")

            if not update_data:
                logger.info(f"No fields to update for item ID {item_id}")
                return await self.get_item_by_id(item_id)

            result = await self.collection.find_one_and_update(
                {"ID": item_id},
                {"$set": update_data},
                return_document=True,
            )
            if result:
                result["_id"] = str(result["_id"])
                logger.info(f"Successfully updated item with ID {item_id}")
            else:
                logger.info(f"No item found to update with ID {item_id}")
            return result
        except PyMongoError as e:
            logger.error(f"Error updating item with ID {item_id}: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    async def update_item(
            self, item_id: int, item_update: Any  # Any can be a Pydantic model
    ) -> Optional[Dict[str, Any]]:
        """
        Updates an existing document with partial update support using Pydantic models.
        Raises RuntimeError if the database is not connected.
        """
        if self.collection is None:
            raise RuntimeError("Database connection is not available")

        try:
            logger.info(f"Attempting to update item with ID {item_id}")

            # Use model_dump to get only the fields that were actually provided for update
            update_data = item_update.model_dump(exclude_unset=True)

            if not update_data:
                logger.info(f"No fields to update for item ID {item_id}. Returning current item.")
                return await self.get_item_by_id(item_id)

            result = await self.collection.find_one_and_update(
                {"ID": item_id},
                {"$set": update_data},
                return_document=True,  # Return the document AFTER the update
            )

            if result:
                result["_id"] = str(result["_id"])
                logger.info(f"Successfully updated item with ID {item_id}")
            else:
                logger.info(f"No item found to update with ID {item_id}")

            return result

        except PyMongoError as e:
            logger.error(f"Error updating item with ID {item_id}: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    async def execute_custom_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute custom MongoDB query for advanced use cases.
        """
        if self.collection is None:
            raise RuntimeError("Database connection is not available")

        try:
            logger.info("Executing custom query")
            items: List[Dict[str, Any]] = []
            async for item in self.collection.find(query):
                item["_id"] = str(item["_id"])
                items.append(item)
            logger.info(f"Custom query returned {len(items)} items")
            return items
        except PyMongoError as e:
            logger.error(f"Error executing custom query: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics for monitoring.
        """
        if self.db is None:
            raise RuntimeError("Database connection is not available")

        try:
            stats = await self.db.command("collstats", self.collection_name)
            return {
                "collection_name": self.collection_name,
                "document_count": stats.get("count", 0),
                "storage_size": stats.get("storageSize", 0),
                "index_count": stats.get("nindexes", 0)
            }
        except PyMongoError as e:
            logger.error(f"Error getting collection stats: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    async def initialize_sample_data(self, sample_data: List[Dict[str, Any]]) -> bool:
        """
        Initialize collection with sample data if empty.
        """
        if self.collection is None:
            raise RuntimeError("Database connection is not available")

        try:
            # Check if collection already has data
            count = await self.collection.count_documents({})
            if count > 0:
                logger.info(f"Collection already contains {count} documents")
                return False

            # Insert sample data
            logger.info(f"Initializing collection with {len(sample_data)} sample documents")
            await self.collection.insert_many(sample_data)
            logger.info("Sample data initialization completed")
            return True
        except PyMongoError as e:
            logger.error(f"Error initializing sample data: {e}")
            raise RuntimeError(f"Database operation failed: {e}")