# ============================================================================
# shared-utilities/elasticsearch/elasticsearch_sync_client.py - CONNECTION ONLY
# ============================================================================
import logging
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

        default_config = {
            'timeout': 30,
            'max_retries': 3,
            'retry_on_timeout': True
        }
        default_config.update(kwargs)

        self.es = Elasticsearch(es_url, **default_config)

        # Test connection
        try:
            info = self.es.info()
            logger.info(f"Connected to Elasticsearch {info['version']['number']}")
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise

    # RAW ELASTICSEARCH OPERATIONS ONLY
    def execute_index(self, index: str, doc: Dict[str, Any], doc_id: str = None):
        """Execute raw index operation - create/update document."""
        try:
            if doc_id:
                return self.es.index(index=index, id=doc_id, body=doc)
            else:
                return self.es.index(index=index, body=doc)
        except Exception as e:
            logger.error(f"Failed to index document: {e}")
            raise

    def execute_get(self, index: str, doc_id: str):
        """Execute raw get operation - retrieve document by ID."""
        try:
            return self.es.get(index=index, id=doc_id)
        except Exception as e:
            logger.warning(f"Document not found: {e}")
            return None

    def execute_update(self, index: str, doc_id: str, updates: Dict[str, Any]):
        """Execute raw update operation - partial document update."""
        try:
            return self.es.update(index=index, id=doc_id, body={"doc": updates})
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            raise

    def execute_delete(self, index: str, doc_id: str):
        """Execute raw delete operation - remove document."""
        try:
            return self.es.delete(index=index, id=doc_id)
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            raise

    def execute_search(self, index: str, query: Dict[str, Any]):
        """Execute raw search operation - find documents."""
        try:
            return self.es.search(index=index, body=query)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def execute_count(self, index: str, query: Dict[str, Any]):
        """Execute raw count operation - count matching documents."""
        try:
            return self.es.count(index=index, body=query)
        except Exception as e:
            logger.error(f"Count failed: {e}")
            raise

    def execute_bulk(self, actions: List[Dict[str, Any]]):
        """Execute raw bulk operations - batch processing."""
        try:
            success, failed = bulk(self.es, actions)
            return {'success': success, 'failed': failed}
        except Exception as e:
            logger.error(f"Bulk operation failed: {e}")
            raise

    def execute_scan(self, index: str, query: Dict[str, Any], scroll_size: int = 1000, scroll_time: str = "5m"):
        """Execute raw scan for large datasets."""
        try:
            return scan(
                self.es,
                query=query,
                index=index,
                size=scroll_size,
                scroll=scroll_time
            )
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            raise

    # BASIC INDEX MANAGEMENT (connection level)
    def create_index(self, index: str, mapping: Dict[str, Any] = None, settings: Dict[str, Any] = None):
        """Create index with mapping and settings."""
        try:
            # Delete existing index
            if self.es.indices.exists(index=index):
                self.es.indices.delete(index=index)
                logger.info(f"Deleted existing index: {index}")

            # Create index body
            body = {}
            if mapping:
                body["mappings"] = mapping
            if settings:
                body["settings"] = settings

            self.es.indices.create(index=index, body=body if body else None)
            logger.info(f"Created index: {index}")
            return True
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False

    def delete_index(self, index: str):
        """Delete index."""
        try:
            self.es.indices.delete(index=index)
            logger.info(f"Deleted index: {index}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete index: {e}")
            return False

    def index_exists(self, index: str) -> bool:
        """Check if index exists."""
        try:
            return self.es.indices.exists(index=index)
        except Exception as e:
            logger.error(f"Failed to check index existence: {e}")
            return False

    def refresh_index(self, index: str):
        """Refresh index - make recent changes visible for search."""
        try:
            return self.es.indices.refresh(index=index)
        except Exception as e:
            logger.error(f"Failed to refresh index: {e}")
            raise

    def close(self):
        """Close connection."""
        try:
            self.es.close()
            logger.info("Elasticsearch connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")