
# ============================================================================
# shared-utilities/mongodb/mongodb_repository.py - CRUD ONLY
# ============================================================================
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
import pandas as pd

logger = logging.getLogger(__name__)


class MongoDBRepository:
    """
    MongoDB CRUD repository - OPERATIONS ONLY
    Works with both sync and async clients
    """

    def __init__(self, client: Union[MongoDBSyncClient, MongoDBAsyncClient], collection_name: str):
        self.client = client
        self.collection_name = collection_name
        self.is_async = hasattr(client, 'connected')  # Detect async client

    def _add_metadata(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Add created_at and updated_at to document."""
        doc_with_meta = doc.copy()
        now = datetime.now(timezone.utc)
        doc_with_meta['created_at'] = now
        doc_with_meta['updated_at'] = now
        return doc_with_meta

    def _build_query(self, **filters) -> Dict[str, Any]:
        """Build MongoDB query from filters."""
        query = {}

        # Direct field filters
        if 'field_filters' in filters:
            query.update(filters['field_filters'])

        # Text search
        if 'text_search' in filters:
            query["$text"] = {"$search": filters['text_search']}

        # Range filters
        if 'range_filters' in filters:
            for field, range_config in filters['range_filters'].items():
                range_query = {}
                if "gte" in range_config:
                    range_query["$gte"] = range_config["gte"]
                if "lte" in range_config:
                    range_query["$lte"] = range_config["lte"]
                if range_query:
                    query[field] = range_query

        # In filters
        if 'in_filters' in filters:
            for field, values in filters['in_filters'].items():
                query[field] = {"$in": values}

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
        """Create document (sync)."""
        if self.is_async:
            raise RuntimeError("Use create_async for async client")

        self._ensure_indexes()
        doc_with_meta = self._add_metadata(document)
        result = self.client.execute_insert_one(self.collection_name, doc_with_meta)
        return str(result.inserted_id)

    def get_by_id(self, doc_id: str, id_field: str = "_id") -> Optional[Dict[str, Any]]:
        """Get document by ID (sync)."""
        if self.is_async:
            raise RuntimeError("Use get_by_id_async for async client")

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
        """Get all documents (sync)."""
        if self.is_async:
            raise RuntimeError("Use get_all_async for async client")

        query = self._build_query(**filters)
        sort_by = sort_by or [("created_at", -1)]

        docs = self.client.execute_find(self.collection_name, query, limit, sort_by)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    def update(self, doc_id: str, updates: Dict[str, Any], id_field: str = "_id") -> bool:
        """Update document (sync)."""
        if self.is_async:
            raise RuntimeError("Use update_async for async client")

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
        """Delete document (sync)."""
        if self.is_async:
            raise RuntimeError("Use delete_async for async client")

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

    def search(self, limit: int = 10, skip: int = 0, **filters) -> Dict[str, Any]:
        """Search documents (sync)."""
        if self.is_async:
            raise RuntimeError("Use search_async for async client")

        query = self._build_query(**filters)
        sort_by = [("created_at", -1)]

        # Get documents with limit
        docs = self.client.execute_find(
            self.collection_name,
            query,
            limit + skip,  # Get more to handle skip
            sort_by
        )[skip:skip + limit]  # Manual skip

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
        """Count documents (sync)."""
        if self.is_async:
            raise RuntimeError("Use count_async for async client")

        query = self._build_query(**filters)
        return self.client.execute_count_documents(self.collection_name, query)

    def bulk_create(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk create documents (sync)."""
        if self.is_async:
            raise RuntimeError("Use bulk_create_async for async client")

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

    # ASYNC CRUD OPERATIONS
    async def create_async(self, document: Dict[str, Any]) -> str:
        """Create document (async)."""
        if not self.is_async:
            raise RuntimeError("Use create for sync client")

        doc_with_meta = self._add_metadata(document)
        result = await self.client.execute_insert_one(self.collection_name, doc_with_meta)
        return str(result.inserted_id)

    async def get_by_id_async(self, doc_id: str, id_field: str = "_id") -> Optional[Dict[str, Any]]:
        """Get document by ID (async)."""
        if not self.is_async:
            raise RuntimeError("Use get_by_id for sync client")

        if id_field == "_id":
            from bson import ObjectId
            try:
                query = {"_id": ObjectId(doc_id)}
            except:
                query = {"_id": doc_id}
        else:
            query = {id_field: doc_id}

        doc = await self.client.execute_find_one(self.collection_name, query)
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def get_all_async(self, limit: int = 0, sort_by: List[tuple] = None, **filters) -> List[Dict[str, Any]]:
        """Get all documents (async)."""
        if not self.is_async:
            raise RuntimeError("Use get_all for sync client")

        query = self._build_query(**filters)
        sort_by = sort_by or [("created_at", -1)]

        docs = await self.client.execute_find(self.collection_name, query, limit, sort_by)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    async def search_async(self, limit: int = 10, skip: int = 0, **filters) -> Dict[str, Any]:
        """Search documents (async)."""
        if not self.is_async:
            raise RuntimeError("Use search for sync client")

        query = self._build_query(**filters)
        sort_by = [("created_at", -1)]

        # Get documents with manual skip
        all_docs = await self.client.execute_find(
            self.collection_name,
            query,
            limit + skip,
            sort_by
        )
        docs = all_docs[skip:skip + limit]

        for doc in docs:
            doc["_id"] = str(doc["_id"])

        # Get total count
        total_count = await self.client.execute_count_documents(self.collection_name, query)

        return {
            'total_hits': total_count,
            'returned_count': len(docs),
            'limit': limit,
            'skip': skip,
            'documents': docs
        }

    async def bulk_create_async(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk create documents (async)."""
        if not self.is_async:
            raise RuntimeError("Use bulk_create for sync client")

        docs_with_meta = []
        for doc in documents:
            docs_with_meta.append(self._add_metadata(doc))

        try:
            result = await self.client.execute_insert_many(self.collection_name, docs_with_meta)
            return {
                'success_count': len(result.inserted_ids),
                'error_count': 0,
                'inserted_ids': [str(id) for id in result.inserted_ids]
            }
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            return {'success_count': 0, 'error_count': len(documents)}

    # PANDAS INTEGRATION
    def bulk_create_from_dataframe(self, df: pd.DataFrame, id_field: str = None) -> Dict[str, Any]:
        """Bulk create from DataFrame (sync)."""
        if self.is_async:
            raise RuntimeError("Use bulk_create_from_dataframe_async for async client")

        documents = df.to_dict('records')
        return self.bulk_create(documents)

    async def bulk_create_from_dataframe_async(self, df: pd.DataFrame, id_field: str = None) -> Dict[str, Any]:
        """Bulk create from DataFrame (async)."""
        if not self.is_async:
            raise RuntimeError("Use bulk_create_from_dataframe for sync client")

        documents = df.to_dict('records')
        return await self.bulk_create_async(documents)
