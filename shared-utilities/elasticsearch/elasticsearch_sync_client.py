# shared-utilities/elasticsearch/elasticsearch_sync_client.py
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan

logger = logging.getLogger(__name__)


class ElasticsearchSyncClient:
    """
    SYNC Elasticsearch client - CONNECTIONS ONLY
    No CRUD operations - only raw elasticsearch operations
    """

    def __init__(self, es_url: str, **kwargs):
        self.es_url = es_url
        self.es = Elasticsearch(es_url, **kwargs)

        # Test connection
        try:
            info = self.es.info()
            logger.info(f"Connected to Elasticsearch {info['version']['number']}")
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise

    # RAW ELASTICSEARCH OPERATIONS ONLY
    def execute_index(self, index: str, doc: Dict[str, Any], doc_id: str = None):
        """Execute index operation."""
        if doc_id:
            return self.es.index(index=index, id=doc_id, body=doc)
        else:
            return self.es.index(index=index, body=doc)

    def execute_get(self, index: str, doc_id: str):
        """Execute get operation."""
        try:
            return self.es.get(index=index, id=doc_id)
        except Exception as e:
            logger.error(f"Document not found: {e}")
            return None

    def execute_update(self, index: str, doc_id: str, updates: Dict[str, Any]):
        """Execute update operation."""
        return self.es.update(index=index, id=doc_id, body={"doc": updates})

    def execute_delete(self, index: str, doc_id: str):
        """Execute delete operation."""
        return self.es.delete(index=index, id=doc_id)

    def execute_search(self, index: str, query: Dict[str, Any]):
        """Execute search operation."""
        return self.es.search(index=index, body=query)

    def execute_count(self, index: str, query: Dict[str, Any]):
        """Execute count operation."""
        return self.es.count(index=index, body=query)

    def execute_bulk(self, actions: List[Dict[str, Any]]):
        """Execute bulk operations."""
        return bulk(self.es, actions)

    def execute_scroll(self, index: str, query: Dict[str, Any], scroll_size: int = 1000):
        """Execute scroll for large datasets."""
        return scan(self.es, query=query, index=index, size=scroll_size)

    # INDEX MANAGEMENT
    def create_index(self, index: str, mapping: Dict[str, Any] = None):
        """Create index with mapping."""
        try:
            self.es.indices.delete(index=index, ignore=[404])
            body = {"mappings": mapping} if mapping else None
            self.es.indices.create(index=index, body=body)
            logger.info(f"Created index: {index}")
            return True
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False

    def refresh_index(self, index: str):
        """Refresh index."""
        return self.es.indices.refresh(index=index)

    def close(self):
        """Close connection."""
        try:
            self.es.close()
            logger.info("Elasticsearch connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
