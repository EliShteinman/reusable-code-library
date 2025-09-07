# ============================================================================
# shared-utilities/mongodb/mongodb_sync_repository.py - SYNC CRUD ONLY
# ============================================================================
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo import MongoClient
import pandas as pd

logger = logging.getLogger(__name__)


class MongoDBSyncRepository:
    """
    MongoDB SYNC CRUD repository - OPERATIONS ONLY
    Works ONLY with MongoDBSyncClient
    """

    def __init__(self, client: MongoClient, collection_name: str):
        """
        Initialize sync repository.

        Args:
            client: MongoDBSyncClient instance
            collection_name: MongoDB collection name
        """
        self.client = client
        self.collection_name = collection_name

    def _add_metadata(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Add created_at and updated_at to document."""
        doc_with_meta = doc.copy()
        now = datetime.now(timezone.utc)
        doc_with_meta['created_at'] = now
        doc_with_meta['updated_at'] = now
        return doc_with_meta

    def _build_query(self, **filters) -> Dict[str, Any]:
        """
        Build MongoDB query from filters.

        Args:
            field_filters: Direct field matches {"field": "value"}
            range_filters: Range queries {"field": {"gte": 10, "lte": 100}}
            text_search: Full text search query
            in_filters: Value in list {"field": ["val1", "val2"]}
            regex_filters: Regex patterns {"field": "pattern"}
            exists_filters: Field existence checks ["field1", "field2"]

        Returns:
            MongoDB query dict
        """
        query = {}

        # Direct field filters
        if 'field_filters' in filters:
            query.update(filters['field_filters'])

        # Range filters
        if 'range_filters' in filters:
            for field, range_config in filters['range_filters'].items():
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

        # Text search (requires text index)
        if 'text_search' in filters and filters['text_search']:
            query["$text"] = {"$search": filters['text_search']}

        # In filters
        if 'in_filters' in filters:
            for field, values in filters['in_filters'].items():
                query[field] = {"$in": values}

        # Regex filters
        if 'regex_filters' in filters:
            for field, pattern in filters['regex_filters'].items():
                query[field] = {"$regex": pattern, "$options": "i"}

        # Exists filters
        if 'exists_filters' in filters:
            for field in filters['exists_filters']:
                query[field] = {"$exists": True}

        return query

    def _ensure_indexes(self):
        """Ensure collection has proper indexes."""
        try:
            # Create unique index on ID field if it exists
            self.client.create_index(self.collection_name, "ID", unique=True, sparse=True)
            # Create index on created_at
            self.client.create_index(self.collection_name, "created_at")
        except Exception as e:
            logger.debug(f"Index creation info: {e}")

    # SYNC CRUD OPERATIONS
    def create(self, document: Dict[str, Any]) -> str:
        """Create document in MongoDB."""
        self._ensure_indexes()
        doc_with_meta = self._add_metadata(document)
        result = self.client.execute_insert_one(self.collection_name, doc_with_meta)
        logger.info(f"Document created in {self.collection_name}: {result.inserted_id}")
        return str(result.inserted_id)

    def get_by_id(self, doc_id: str, id_field: str = "_id") -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        if id_field == "_id":
            from bson import ObjectId
            try:
                query = {"_id": ObjectId(doc_id)}
            except:
                query = {"_id": doc_id}
        else:
            query = {id_field: doc_id}

        doc = self.client.execute_find_one(self.collection_name, query)
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def get_all(self, limit: int = 0, sort_by: List[tuple] = None, **filters) -> List[Dict[str, Any]]:
        """Get all documents with optional filters."""
        query = self._build_query(**filters)
        sort_by = sort_by or [("created_at", -1)]

        docs = self.client.execute_find(self.collection_name, query, limit, sort_by)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    def update(self, doc_id: str, updates: Dict[str, Any], id_field: str = "_id") -> bool:
        """Update document by ID."""
        if id_field == "_id":
            from bson import ObjectId
            try:
                query = {"_id": ObjectId(doc_id)}
            except:
                query = {"_id": doc_id}
        else:
            query = {id_field: doc_id}

        updates_with_meta = updates.copy()
        updates_with_meta['updated_at'] = datetime.now(timezone.utc)

        result = self.client.execute_update_one(self.collection_name, query, updates_with_meta)
        return result.modified_count > 0

    def delete(self, doc_id: str, id_field: str = "_id") -> bool:
        """Delete document by ID."""
        if id_field == "_id":
            from bson import ObjectId
            try:
                query = {"_id": ObjectId(doc_id)}
            except:
                query = {"_id": doc_id}
        else:
            query = {id_field: doc_id}

        result = self.client.execute_delete_one(self.collection_name, query)
        return result.deleted_count > 0

    def search(self, limit: int = 10, skip: int = 0, sort_by: List[tuple] = None, **filters) -> Dict[str, Any]:
        """
        Search documents with various filters.

        Args:
            limit: Maximum number of results
            skip: Number of results to skip
            sort_by: Sort specification [(field, direction)]
            **filters: Search filters (see _build_query)

        Returns:
            Dict with total_hits, documents, and metadata
        """
        query = self._build_query(**filters)
        sort_by = sort_by or [("created_at", -1)]

        # Get documents with limit
        all_docs = self.client.execute_find(
            self.collection_name,
            query,
            limit + skip,
            sort_by
        )
        docs = all_docs[skip:skip + limit] if skip > 0 else all_docs[:limit]

        for doc in docs:
            doc["_id"] = str(doc["_id"])

        # Get total count
        total_count = self.client.execute_count_documents(self.collection_name, query)

        return {
            'total_hits': total_count,
            'returned_count': len(docs),
            'limit': limit,
            'skip': skip,
            'documents': docs
        }

    def count(self, **filters) -> int:
        """Count documents matching filters."""
        query = self._build_query(**filters)
        return self.client.execute_count_documents(self.collection_name, query)

    def bulk_create(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk create multiple documents."""
        docs_with_meta = []
        for doc in documents:
            docs_with_meta.append(self._add_metadata(doc))

        try:
            result = self.client.execute_insert_many(self.collection_name, docs_with_meta)
            return {
                'success_count': len(result.inserted_ids),
                'error_count': 0,
                'inserted_ids': [str(id) for id in result.inserted_ids]
            }
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            return {'success_count': 0, 'error_count': len(documents)}

    def bulk_update(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk update multiple documents.

        Args:
            updates: List of {"filter": {...}, "update": {...}}
        """
        success_count = 0
        error_count = 0

        for update_doc in updates:
            try:
                filter_query = update_doc['filter']
                update_data = update_doc['update'].copy()
                update_data['updated_at'] = datetime.now(timezone.utc)

                result = self.client.execute_update_one(self.collection_name, filter_query, update_data)
                if result.modified_count > 0:
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                logger.error(f"Bulk update item failed: {e}")
                error_count += 1

        return {'success_count': success_count, 'error_count': error_count}

    def bulk_delete(self, filters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk delete documents by filters."""
        success_count = 0
        error_count = 0

        for filter_query in filters:
            try:
                result = self.client.execute_delete_one(self.collection_name, filter_query)
                if result.deleted_count > 0:
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                logger.error(f"Bulk delete item failed: {e}")
                error_count += 1

        return {'success_count': success_count, 'error_count': error_count}

    # AGGREGATIONS
    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform aggregation on the collection.

        Args:
            pipeline: MongoDB aggregation pipeline

        Returns:
            Aggregation results
        """
        try:
            results = self.client.execute_aggregate(self.collection_name, pipeline)
            # Convert ObjectIds to strings
            for result in results:
                if '_id' in result and result['_id']:
                    result['_id'] = str(result['_id'])
            return results
        except Exception as e:
            logger.error(f"Aggregation failed: {e}")
            return []

    # PANDAS INTEGRATION
    def to_dataframe(self, **filters) -> pd.DataFrame:
        """Convert search results to pandas DataFrame."""
        try:
            # Get all results
            documents = self.get_all(**filters)

            if not documents:
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(documents)
            logger.info(f"Created DataFrame with {len(df)} rows from {self.collection_name}")
            return df

        except Exception as e:
            logger.error(f"Failed to create DataFrame: {e}")
            return pd.DataFrame()

    def bulk_create_from_dataframe(self, df: pd.DataFrame, id_column: str = None) -> Dict[str, Any]:
        """
        Bulk create documents from pandas DataFrame.

        Args:
            df: pandas DataFrame
            id_column: Column to use as document ID (optional)

        Returns:
            Result dict with success/error counts
        """
        try:
            documents = df.to_dict('records')

            # Handle ID column
            if id_column and id_column in df.columns:
                for doc in documents:
                    if id_column in doc:
                        doc['ID'] = doc.pop(id_column)

            return self.bulk_create(documents)

        except Exception as e:
            logger.error(f"Failed to create from DataFrame: {e}")
            return {'success_count': 0, 'error_count': len(df)}

    # INDEX MANAGEMENT
    def create_text_index(self, fields: List[str]):
        """Create text index for full-text search."""
        try:
            index_spec = [(field, "text") for field in fields]
            self.client.create_index(self.collection_name, index_spec)
            logger.info(f"Text index created on {fields}")
        except Exception as e:
            logger.warning(f"Failed to create text index: {e}")

    def create_index(self, field: str, unique: bool = False):
        """Create index on field."""
        try:
            self.client.create_index(self.collection_name, field, unique=unique)
            logger.info(f"Index created on {field}")
        except Exception as e:
            logger.warning(f"Failed to create index on {field}: {e}")

    def drop_collection(self):
        """Drop the entire collection."""
        try:
            collection = self.client.get_collection(self.collection_name)
            collection.drop()
            logger.info(f"Collection {self.collection_name} dropped")
        except Exception as e:
            logger.error(f"Failed to drop collection: {e}")