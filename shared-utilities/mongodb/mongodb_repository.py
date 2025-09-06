# shared-utilities/mongodb/mongodb_repository.py
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class MongoDBRepository:
    """
    MongoDB CRUD repository - ONLY handles CRUD operations.
    Requires MongoDBSyncClient for connections.
    """

    def __init__(self, client, collection_name: str):
        self.client = client
        self.collection_name = collection_name

    def create(self, document: Dict[str, Any]) -> str:
        """Create new document and return ID."""
        doc_with_meta = document.copy()
        doc_with_meta['created_at'] = datetime.now(timezone.utc)
        doc_with_meta['updated_at'] = datetime.now(timezone.utc)

        result = self.client.execute_insert_one(self.collection_name, doc_with_meta)
        return str(result.inserted_id)

    def get_by_id(self, doc_id: str, id_field: str = "_id"):
        """Get document by ID."""
        from bson import ObjectId

        if id_field == "_id":
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

    def get_all(self, limit: int = 0) -> List[Dict[str, Any]]:
        """Get all documents."""
        docs = self.client.execute_find(self.collection_name, {}, limit)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    def update(self, doc_id: str, updates: Dict[str, Any], id_field: str = "_id") -> bool:
        """Update document by ID."""
        from bson import ObjectId

        if id_field == "_id":
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
        from bson import ObjectId

        if id_field == "_id":
            try:
                query = {"_id": ObjectId(doc_id)}
            except:
                query = {"_id": doc_id}
        else:
            query = {id_field: doc_id}

        result = self.client.execute_delete_one(self.collection_name, query)
        return result.deleted_count > 0

    def search(self, filters: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents with filters."""
        docs = self.client.execute_find(self.collection_name, filters, limit)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
