# shared-utilities/elasticsearch/elasticsearch_async_client.py
import logging
from elasticsearch import Elasticsearch
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ElasticsearchSyncClient:
    """
    Elasticsearch connection client - ONLY handles connections and raw operations.
    CRUD operations are in ElasticsearchRepository.
    """

    def __init__(self, es_url: str):
        self.es_url = es_url
        self.client = None
        self.connect()

    def connect(self):
        """Create connection to Elasticsearch."""
        try:
            self.client = Elasticsearch(self.es_url)
            info = self.client.info()
            logger.info(f"Connected to Elasticsearch {info['version']['number']}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            return False

    def execute_index(self, index: str, doc: Dict[str, Any], doc_id: str = None):
        """Execute index operation."""
        if doc_id:
            return self.client.index(index=index, id=doc_id, body=doc)
        else:
            return self.client.index(index=index, body=doc)

    def execute_get(self, index: str, doc_id: str):
        """Execute get operation."""
        try:
            return self.client.get(index=index, id=doc_id)
        except Exception as e:
            logger.error(f"Document not found: {e}")
            return None

    def execute_update(self, index: str, doc_id: str, updates: Dict[str, Any]):
        """Execute update operation."""
        return self.client.update(index=index, id=doc_id, body={"doc": updates})

    def execute_delete(self, index: str, doc_id: str):
        """Execute delete operation."""
        return self.client.delete(index=index, id=doc_id)

    def execute_search(self, index: str, query: Dict[str, Any]):
        """Execute search operation."""
        return self.client.search(index=index, body=query)

    def create_index(self, index: str, mapping: Dict[str, Any] = None):
        """Create index with mapping."""
        try:
            self.client.indices.delete(index=index, ignore=[404])
            body = {"mappings": mapping} if mapping else None
            self.client.indices.create(index=index, body=body)
            logger.info(f"Created index: {index}")
            return True
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False

    def refresh_index(self, index: str):
        """Refresh index."""
        return self.client.indices.refresh(index=index)

    def close(self):
        """Close connection."""
        try:
            self.client.close()
            logger.info("Elasticsearch connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
