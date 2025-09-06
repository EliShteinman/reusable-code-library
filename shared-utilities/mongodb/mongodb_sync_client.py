# shared-utilities/mongodb/mongodb_sync_client.py
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, PyMongoError

logger = logging.getLogger(__name__)


class MongoDBSyncClient:
    """
    Synchronous MongoDB client with full CRUD operations and query builder.
    Enhanced version with universal query building like your Elasticsearch pattern.
    """

    def __init__(self, mongo_uri: str, db_name: str, collection_name: str = None):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name

        # Initialize connections
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.collection: Optional[Collection] = None

        self.connect()

    def connect(self):
        """Create connection to MongoDB."""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command("ping")

            self.db = self.client[self.db_name]
            if self.collection_name:
                self.collection = self.db[self.collection_name]

            logger.info("Successfully connected to MongoDB")
            self._setup_indexes()

        except PyMongoError as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.client = None
            self.db = None
            self.collection = None
            raise

    def _setup_indexes(self):
        """Create indexes for better performance."""
        if self.collection is not None:
            try:
                # Create unique index on ID field if it exists
                self.collection.create_index("ID", unique=True, sparse=True)
                # Create index on created_at
                self.collection.create_index("created_at")
                logger.info("Database indexes ensured")
            except PyMongoError as e:
                logger.warning(f"Failed to create indexes: {e}")

    def _build_query(self,
                     query_filters: Optional[Dict[str, Any]] = None,
                     text_search: Optional[str] = None,
                     field_filters: Optional[Dict[str, Any]] = None,
                     exists_filters: Optional[List[str]] = None,
                     not_exists_filters: Optional[List[str]] = None,
                     in_filters: Optional[Dict[str, List[Any]]] = None,
                     range_filters: Optional[Dict[str, Dict[str, Any]]] = None,
                     regex_filters: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Universal MongoDB query builder.
        Similar pattern to your Elasticsearch query builder.
        """
        query = {}

        # Direct query filters (for custom MongoDB queries)
        if query_filters:
            query.update(query_filters)

        # Text search (MongoDB text index required)
        if text_search:
            query["$text"] = {"$search": text_search}

        # Field filters (exact matches)
        if field_filters:
            query.update(field_filters)

        # Exists filters
        if exists_filters:
            for field in exists_filters:
                query[field] = {"$exists": True}

        # Not exists filters
        if not_exists_filters:
            for field in not_exists_filters:
                query[field] = {"$exists": False}

        # In filters (field value in list)
        if in_filters:
            for field, values in in_filters.items():
                query[field] = {"$in": values}

        # Range filters
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
        if regex_filters:
            for field, pattern in regex_filters.items():
                query[field] = {"$regex": pattern, "$options": "i"}

        return query

    def get_collection(self, collection_name: str = None) -> Collection:
        """Get collection object."""
        if self.db is None:
            raise RuntimeError("Database connection is not available")

        if collection_name:
            return self.db[collection_name]
        elif self.collection:
            return self.collection
        else:
            raise ValueError("No collection specified")

    # Document CRUD Operations
    def create_document(self,
                        doc: Dict[str, Any],
                        collection_name: str = None) -> Optional[str]:
        """Create a single document."""
        collection = self.get_collection(collection_name)

        try:
            # Add timestamps
            doc_with_meta = doc.copy()
            doc_with_meta['created_at'] = datetime.now(timezone.utc)
            doc_with_meta['updated_at'] = datetime.now(timezone.utc)

            result = collection.insert_one(doc_with_meta)
            logger.debug(f"Created document with _id: {result.inserted_id}")
            return str(result.inserted_id)

        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error: {e}")
            raise ValueError(f"Document with duplicate key already exists")
        except PyMongoError as e:
            logger.error(f"Error creating document: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    def get_document(self,
                     doc_filter: Dict[str, Any],
                     collection_name: str = None) -> Optional[Dict[str, Any]]:
        """Get single document by filter."""
        collection = self.get_collection(collection_name)

        try:
            doc = collection.find_one(doc_filter)
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc

        except PyMongoError as e:
            logger.error(f"Error retrieving document: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    def get_document_by_id(self,
                           doc_id: Union[str, int],
                           id_field: str = "_id",
                           collection_name: str = None) -> Optional[Dict[str, Any]]:
        """Get document by ID (supports both ObjectId and custom ID fields)."""
        if id_field == "_id":
            from bson import ObjectId
            try:
                filter_query = {"_id": ObjectId(doc_id)}
            except:
                # If not valid ObjectId, search as string
                filter_query = {"_id": doc_id}
        else:
            filter_query = {id_field: doc_id}

        return self.get_document(filter_query, collection_name)

    def update_document(self,
                        doc_filter: Dict[str, Any],
                        update_data: Dict[str, Any],
                        collection_name: str = None,
                        upsert: bool = False) -> bool:
        """Update document(s) matching filter."""
        collection = self.get_collection(collection_name)

        try:
            # Add timestamp
            update_with_meta = update_data.copy()
            update_with_meta['updated_at'] = datetime.now(timezone.utc)

            result = collection.update_one(
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

    def update_document_by_id(self,
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

        return self.update_document(filter_query, update_data, collection_name)

    def delete_document(self,
                        doc_filter: Dict[str, Any],
                        collection_name: str = None) -> bool:
        """Delete document(s) matching filter."""
        collection = self.get_collection(collection_name)

        try:
            result = collection.delete_one(doc_filter)
            if result.deleted_count > 0:
                logger.debug(f"Deleted {result.deleted_count} documents")
                return True
            else:
                logger.debug("No documents matched the filter")
                return False

        except PyMongoError as e:
            logger.error(f"Error deleting document: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    def delete_document_by_id(self,
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

        return self.delete_document(filter_query, collection_name)

    # Search Operations
    def search_documents(self,
                         limit: int = 10,
                         skip: int = 0,
                         sort_by: Optional[List[tuple]] = None,
                         collection_name: str = None,
                         **kwargs) -> Dict[str, Any]:
        """Search documents with query builder."""
        collection = self.get_collection(collection_name)

        try:
            query = self._build_query(**kwargs)

            # Default sort
            if sort_by is None:
                sort_by = [("created_at", -1)]  # Newest first

            # Execute query with pagination
            cursor = collection.find(query).skip(skip).limit(limit).sort(sort_by)
            documents = []

            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                documents.append(doc)

            # Get total count
            total_count = collection.count_documents(query)

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

    def count_documents(self, collection_name: str = None, **kwargs) -> int:
        """Count documents matching query."""
        collection = self.get_collection(collection_name)

        try:
            query = self._build_query(**kwargs)
            return collection.count_documents(query)
        except PyMongoError as e:
            logger.error(f"Count failed: {e}")
            return 0

    def get_all_documents(self,
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
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                documents.append(doc)

            logger.info(f"Retrieved {len(documents)} documents")
            return documents

        except PyMongoError as e:
            logger.error(f"Error retrieving documents: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    # Bulk Operations
    def bulk_create_documents(self,
                              documents: List[Dict[str, Any]],
                              collection_name: str = None) -> Dict[str, Any]:
        """Bulk insert documents."""
        collection = self.get_collection(collection_name)

        try:
            now = datetime.now(timezone.utc)

            # Add timestamps to all documents
            docs_with_meta = []
            for doc in documents:
                doc_with_meta = doc.copy()
                doc_with_meta['created_at'] = now
                doc_with_meta['updated_at'] = now
                docs_with_meta.append(doc_with_meta)

            result = collection.insert_many(docs_with_meta, ordered=False)

            logger.info(f"Bulk inserted {len(result.inserted_ids)} documents")
            return {
                'success_count': len(result.inserted_ids),
                'error_count': 0,
                'inserted_ids': [str(id) for id in result.inserted_ids]
            }

        except PyMongoError as e:
            logger.error(f"Bulk insert failed: {e}")
            return {'success_count': 0, 'error_count': len(documents)}

    def bulk_update_documents(self,
                              updates: List[Dict[str, Any]],
                              collection_name: str = None) -> Dict[str, Any]:
        """
        Bulk update documents.
        updates should be list of {'filter': {}, 'update': {}} dicts.
        """
        collection = self.get_collection(collection_name)

        try:
            from pymongo import UpdateOne

            operations = []
            for update_op in updates:
                doc_filter = update_op['filter']
                update_data = update_op['update'].copy()
                update_data['updated_at'] = datetime.now(timezone.utc)

                operations.append(
                    UpdateOne(doc_filter, {"$set": update_data})
                )

            result = collection.bulk_write(operations, ordered=False)

            return {
                'matched_count': result.matched_count,
                'modified_count': result.modified_count,
                'upserted_count': result.upserted_count
            }

        except PyMongoError as e:
            logger.error(f"Bulk update failed: {e}")
            return {'matched_count': 0, 'modified_count': 0}

    # Aggregation Operations
    def aggregate(self,
                  pipeline: List[Dict[str, Any]],
                  collection_name: str = None) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline."""
        collection = self.get_collection(collection_name)

        try:
            cursor = collection.aggregate(pipeline)
            results = []

            for doc in cursor:
                if '_id' in doc and isinstance(doc['_id'], dict):
                    # Handle grouped results
                    continue
                elif '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                results.append(doc)

            return results

        except PyMongoError as e:
            logger.error(f"Aggregation failed: {e}")
            return []

    def group_by_field(self,
                       field: str,
                       collection_name: str = None) -> List[Dict[str, Any]]:
        """Group documents by field value."""
        pipeline = [
            {"$group": {
                "_id": f"${field}",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]

        results = self.aggregate(pipeline, collection_name)

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'field_value': result['_id'],
                'count': result['count']
            })

        return formatted_results

    # Index Management
    def create_index(self,
                     index_spec: Union[str, List[tuple]],
                     collection_name: str = None,
                     **kwargs):
        """Create index on collection."""
        collection = self.get_collection(collection_name)

        try:
            result = collection.create_index(index_spec, **kwargs)
            logger.info(f"Created index: {result}")
            return result
        except PyMongoError as e:
            logger.error(f"Failed to create index: {e}")
            return None

    def drop_index(self,
                   index_name: str,
                   collection_name: str = None):
        """Drop index from collection."""
        collection = self.get_collection(collection_name)

        try:
            collection.drop_index(index_name)
            logger.info(f"Dropped index: {index_name}")
            return True
        except PyMongoError as e:
            logger.error(f"Failed to drop index: {e}")
            return False

    def list_indexes(self, collection_name: str = None) -> List[Dict[str, Any]]:
        """List all indexes on collection."""
        collection = self.get_collection(collection_name)

        try:
            return list(collection.list_indexes())
        except PyMongoError as e:
            logger.error(f"Failed to list indexes: {e}")
            return []

    # Database Management
    def drop_collection(self, collection_name: str = None):
        """Drop collection."""
        if self.db is None:
            raise RuntimeError("Database connection is not available")

        coll_name = collection_name or self.collection_name
        if not coll_name:
            raise ValueError("Collection name must be provided")

        try:
            self.db.drop_collection(coll_name)
            logger.info(f"Dropped collection: {coll_name}")
        except PyMongoError as e:
            logger.error(f"Failed to drop collection: {e}")

    def get_collection_stats(self, collection_name: str = None) -> Dict[str, Any]:
        """Get collection statistics."""
        if self.db is None:
            raise RuntimeError("Database connection is not available")

        coll_name = collection_name or self.collection_name
        if not coll_name:
            raise ValueError("Collection name must be provided")

        try:
            stats = self.db.command("collstats", coll_name)
            return {
                "collection_name": coll_name,
                "document_count": stats.get("count", 0),
                "storage_size": stats.get("storageSize", 0),
                "index_count": stats.get("nindexes", 0),
                "total_index_size": stats.get("totalIndexSize", 0)
            }
        except PyMongoError as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}

    def close(self):
        """Close connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")







