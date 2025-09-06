import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ElasticsearchRepository:
    """
    Elasticsearch CRUD repository - ONLY handles CRUD operations.
    Requires ElasticsearchSyncClient for connections.
    """

    def __init__(self, client, index_name: str):
        self.client = client
        self.index_name = index_name

    def create(self, document: Dict[str, Any], doc_id: str = None) -> str:
        """Create new document and return ID."""
        doc_with_meta = document.copy()
        doc_with_meta['created_at'] = datetime.now()

        result = self.client.execute_index(self.index_name, doc_with_meta, doc_id)
        return result['_id']

    def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        result = self.client.execute_get(self.index_name, doc_id)
        if result:
            doc = result['_source']
            doc['_id'] = result['_id']
            return doc
        return None

    def update(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        """Update document by ID."""
        try:
            updates_with_meta = updates.copy()
            updates_with_meta['updated_at'] = datetime.now()

            self.client.execute_update(self.index_name, doc_id, updates_with_meta)
            return True
        except Exception as e:
            logger.error(f"Update failed: {e}")
            return False

    def delete(self, doc_id: str) -> bool:
        """Delete document by ID."""
        try:
            self.client.execute_delete(self.index_name, doc_id)
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False

    def search_simple(self, query_text: str, fields: List[str] = None, size: int = 10) -> List[Dict[str, Any]]:
        """Simple text search."""
        search_fields = fields or ["_all"]
        query = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": search_fields
                }
            },
            "size": size
        }

        response = self.client.execute_search(self.index_name, query)
        results = []

        for hit in response['hits']['hits']:
            doc = hit['_source']
            doc['_id'] = hit['_id']
            doc['_score'] = hit['_score']
            results.append(doc)

        return results

    def search_by_field(self, field: str, value: Any, size: int = 10) -> List[Dict[str, Any]]:
        """Search by exact field value."""
        query = {
            "query": {
                "term": {field: value}
            },
            "size": size
        }

        response = self.client.execute_search(self.index_name, query)
        return [hit['_source'] for hit in response['hits']['hits']]

    def create_index_with_mapping(self, mapping: Dict[str, Any] = None):
        """Create index with mapping."""
        return self.client.create_index(self.index_name, mapping)