# shared-utilities/mongodb/mongodb_async_client.py
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from pymongo import AsyncMongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

logger = logging.getLogger(__name__)


class MongoDBAsyncClient:
    """
    Async MongoDB client with full CRUD operations and query builder.
    Async version of the sync client with same interface.
    """

    def __init__(self, mongo_uri: str, db_name: str, collection_name: str = None):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name

        # Initialize connections
        self.client: Optional[AsyncMongoClient] = None
        self.db = None
        self.collection = None

    async def connect(self):
        """Create connection to MongoDB."""
        try:
            self.client = AsyncMongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            await self.client.admin.command("ping")

            self.db = self.client[self.db_name]
            if self.collection_name:
                self.collection = self.db[self.collection_name]

            logger.info("Successfully connected to MongoDB (async)")
            await self._setup_indexes()

        except PyMongoError as e:
            logger.error(f"MongoDB async connection failed: {e}")
            self.client = None
            self.db = None
            self.collection = None
            raise

    async def _setup_indexes(self):
        """Create indexes for better performance."""
        if self.collection is not None:
            try:
                # Create unique index on ID field if it exists
                await self.collection.create_index("ID", unique=True, sparse=True)
                # Create index on created_at
                await self.collection.create_index("created_at")
                logger.info("Database indexes ensured (async)")
            except PyMongoError as e:
                logger.warning(f"Failed to create indexes: {e}")

    def _build_query(self, **kwargs) -> Dict[str, Any]:
        """Same query builder as sync version."""
        query = {}

        # Direct query filters
        query_filters = kwargs.get('query_filters')
        if query_filters:
            query.update(query_filters)

        # Text search
        text_search = kwargs.get('text_search')
        if text_search:
            query["$text"] = {"$search": text_search}

        # Field filters
        field_filters = kwargs.get('field_filters')
        if field_filters:
            query.update(field_filters)

        # Exists filters
        exists_filters = kwargs.get('exists_filters')
        if exists_filters:
            for field in exists_filters:
                query[field] = {"$exists": True}

        # Not exists filters
        not_exists_filters = kwargs.get('not_exists_filters')
        if not_exists_filters:
            for field in not_exists_filters:
                query[field] = {"$exists": False}

        # In filters
        in_filters = kwargs.get('in_filters')
        if in_filters:
            for field, values in in_filters.items():
                query[field] = {"$in": values}

        # Range filters
        range_filters = kwargs.get('range_filters')
        if range_filters:
            for field, range_config in range_filters.items():
                range_query = {}
                if "gte" in range_config:
                    range_query["$gte"] = range_config["gte"]
                if "lte" in range_config:
                    range_query["$lte"] = range_config["lte"]
                if "gt" in range_config:
                    range_query["$gt"] = range_config["gt"]
                if "lt" in range_config:
                    range_query["$lt"] = range_config["lt"]
                if range_query:
                    query[field] = range_query

        # Regex filters
        regex_filters = kwargs.get('regex_filters')
        if regex_filters:
            for field, pattern in regex_filters.items():
                query[field] = {"$regex": pattern, "$options": "i"}

        return query

    def get_collection(self, collection_name: str = None):
        """Get collection object."""
        if self.db is None:
            raise RuntimeError("Database connection is not available")

        if collection_name:
            return self.db[collection_name]
        elif self.collection:
            return self.collection
        else:
            raise ValueError("No collection specified")

    # Document CRUD Operations (all async versions)
    async def create_document(self,
                              doc: Dict[str, Any],
                              collection_name: str = None) -> Optional[str]:
        """Create a single document."""
        collection = self.get_collection(collection_name)

        try:
            doc_with_meta = doc.copy()
            doc_with_meta['created_at'] = datetime.now(timezone.utc)
            doc_with_meta['updated_at'] = datetime.now(timezone.utc)

            result = await collection.insert_one(doc_with_meta)
            logger.debug(f"Created document with _id: {result.inserted_id}")
            return str(result.inserted_id)

        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error: {e}")
            raise ValueError(f"Document with duplicate key already exists")
        except PyMongoError as e:
            logger.error(f"Error creating document: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    async def get_document(self,
                           doc_filter: Dict[str, Any],
                           collection_name: str = None) -> Optional[Dict[str, Any]]:
        """Get single document by filter."""
        collection = self.get_collection(collection_name)

        try:
            doc = await collection.find_one(doc_filter)
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc

        except PyMongoError as e:
            logger.error(f"Error retrieving document: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    async def get_document_by_id(self,
                                 doc_id: Union[str, int],
                                 id_field: str = "_id",
                                 collection_name: str = None) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        if id_field == "_id":
            from bson import ObjectId
            try:
                filter_query = {"_id": ObjectId(doc_id)}
            except:
                filter_query = {"_id": doc_id}
        else:
            filter_query = {id_field: doc_id}

        return await self.get_document(filter_query, collection_name)

    async def update_document(self,
                              doc_filter: Dict[str, Any],
                              update_data: Dict[str, Any],
                              collection_name: str = None,
                              upsert: bool = False) -> bool:
        """Update document(s) matching filter."""
        collection = self.get_collection(collection_name)

        try:
            update_with_meta = update_data.copy()
            update_with_meta['updated_at'] = datetime.now(timezone.utc)

            result = await collection.update_one(
                doc_filter,
                {"$set": update_with_meta},
                upsert=upsert
            )

            if result.matched_count > 0:
                logger.debug(f"Updated {result.modified_count} documents")
                return True
            else:
                logger.debug("No documents matched the filter")
                return False

        except PyMongoError as e:
            logger.error(f"Error updating document: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    async def update_document_by_id(self,
                                    doc_id: Union[str, int],
                                    update_data: Dict[str, Any],
                                    id_field: str = "_id",
                                    collection_name: str = None) -> bool:
        """Update document by ID."""
        if id_field == "_id":
            from bson import ObjectId
            try:
                filter_query = {"_id": ObjectId(doc_id)}
            except:
                filter_query = {"_id": doc_id}
        else:
            filter_query = {id_field: doc_id}

        return await self.update_document(filter_query, update_data, collection_name)

    async def delete_document(self,
                              doc_filter: Dict[str, Any],
                              collection_name: str = None) -> bool:
        """Delete document(s) matching filter."""
        collection = self.get_collection(collection_name)

        try:
            result = await collection.delete_one(doc_filter)
            if result.deleted_count > 0:
                logger.debug(f"Deleted {result.deleted_count} documents")
                return True
            else:
                logger.debug("No documents matched the filter")
                return False

        except PyMongoError as e:
            logger.error(f"Error deleting document: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    async def delete_document_by_id(self,
                                    doc_id: Union[str, int],
                                    id_field: str = "_id",
                                    collection_name: str = None) -> bool:
        """Delete document by ID."""
        if id_field == "_id":
            from bson import ObjectId
            try:
                filter_query = {"_id": ObjectId(doc_id)}
            except:
                filter_query = {"_id": doc_id}
        else:
            filter_query = {id_field: doc_id}

        return await self.delete_document(filter_query, collection_name)

    # Search Operations
    async def search_documents(self,
                               limit: int = 10,
                               skip: int = 0,
                               sort_by: Optional[List[tuple]] = None,
                               collection_name: str = None,
                               **kwargs) -> Dict[str, Any]:
        """Search documents with query builder."""
        collection = self.get_collection(collection_name)

        try:
            query = self._build_query(**kwargs)

            if sort_by is None:
                sort_by = [("created_at", -1)]

            cursor = collection.find(query).skip(skip).limit(limit).sort(sort_by)
            documents = []

            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                documents.append(doc)

            total_count = await collection.count_documents(query)

            return {
                'total_hits': total_count,
                'returned_count': len(documents),
                'limit': limit,
                'skip': skip,
                'documents': documents
            }

        except PyMongoError as e:
            logger.error(f"Search failed: {e}")
            return {'total_hits': 0, 'documents': []}

    async def count_documents(self, collection_name: str = None, **kwargs) -> int:
        """Count documents matching query."""
        collection = self.get_collection(collection_name)

        try:
            query = self._build_query(**kwargs)
            return await collection.count_documents(query)
        except PyMongoError as e:
            logger.error(f"Count failed: {e}")
            return 0

    async def get_all_documents(self,
                                collection_name: str = None,
                                limit: int = None,
                                **kwargs) -> List[Dict[str, Any]]:
        """Get all documents matching query."""
        collection = self.get_collection(collection_name)

        try:
            query = self._build_query(**kwargs)
            cursor = collection.find(query)

            if limit:
                cursor = cursor.limit(limit)

            documents = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                documents.append(doc)

            logger.info(f"Retrieved {len(documents)} documents")
            return documents

        except PyMongoError as e:
            logger.error(f"Error retrieving documents: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    # Bulk Operations
    async def bulk_create_documents(self,
                                    documents: List[Dict[str, Any]],
                                    collection_name: str = None) -> Dict[str, Any]:
        """Bulk insert documents."""
        collection = self.get_collection(collection_name)

        try:
            now = datetime.now(timezone.utc)

            docs_with_meta = []
            for doc in documents:
                doc_with_meta = doc.copy()
                doc_with_meta['created_at'] = now
                doc_with_meta['updated_at'] = now
                docs_with_meta.append(doc_with_meta)

            result = await collection.insert_many(docs_with_meta, ordered=False)

            logger.info(f"Bulk inserted {len(result.inserted_ids)} documents")
            return {
                'success_count': len(result.inserted_ids),
                'error_count': 0,
                'inserted_ids': [str(id) for id in result.inserted_ids]
            }

        except PyMongoError as e:
            logger.error(f"Bulk insert failed: {e}")
            return {'success_count': 0, 'error_count': len(documents)}

    async def close(self):
        """Close connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB async connection closed")