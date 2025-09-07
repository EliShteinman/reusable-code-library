# ============================================================================
# shared-utilities/elasticsearch/elasticsearch_async_client.py - CONNECTION ONLY
# ============================================================================
import asyncio
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ElasticsearchAsyncClient:
    """
    ASYNC Elasticsearch client - CONNECTIONS ONLY
    No CRUD operations - only raw elasticsearch operations
    """

    def __init__(self, es_url: str, **kwargs):
        self.es_url = es_url
        self.es = None  # Will be created in connect()
        self.connected = False
        self.config = kwargs

    async def connect(self):
        """Create async connection."""
        try:
            # Import here to avoid issues if elasticsearch-async not installed
            from elasticsearch import AsyncElasticsearch

            default_config = {
                'timeout': 30,
                'max_retries': 3,
                'retry_on_timeout': True
            }
            default_config.update(self.config)

            self.es = AsyncElasticsearch(self.es_url, **default_config)

            # Test connection
            info = await self.es.info()
            logger.info(f"Connected to Elasticsearch {info['version']['number']} (async)")
            self.connected = True

        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch (async): {e}")
            raise

    # RAW ASYNC ELASTICSEARCH OPERATIONS ONLY
    async def execute_index(self, index: str, doc: Dict[str, Any], doc_id: str = None):
        """Execute raw async index operation."""
        if not self.connected:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            if doc_id:
                return await self.es.index(index=index, id=doc_id, body=doc)
            else:
                return await self.es.index(index=index, body=doc)
        except Exception as e:
            logger.error(f"Failed to index document (async): {e}")
            raise

    async def execute_get(self, index: str, doc_id: str):
        """Execute raw async get operation."""
        if not self.connected:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            return await self.es.get(index=index, id=doc_id)
        except Exception as e:
            logger.warning(f"Document not found (async): {e}")
            return None

    async def execute_update(self, index: str, doc_id: str, updates: Dict[str, Any]):
        """Execute raw async update operation."""
        if not self.connected:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            return await self.es.update(index=index, id=doc_id, body={"doc": updates})
        except Exception as e:
            logger.error(f"Failed to update document (async): {e}")
            raise

    async def execute_delete(self, index: str, doc_id: str):
        """Execute raw async delete operation."""
        if not self.connected:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            return await self.es.delete(index=index, id=doc_id)
        except Exception as e:
            logger.error(f"Failed to delete document (async): {e}")
            raise

    async def execute_search(self, index: str, query: Dict[str, Any]):
        """Execute raw async search operation."""
        if not self.connected:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            return await self.es.search(index=index, body=query)
        except Exception as e:
            logger.error(f"Search failed (async): {e}")
            raise

    async def execute_count(self, index: str, query: Dict[str, Any]):
        """Execute raw async count operation."""
        if not self.connected:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            return await self.es.count(index=index, body=query)
        except Exception as e:
            logger.error(f"Count failed (async): {e}")
            raise

    async def execute_bulk(self, actions: List[Dict[str, Any]]):
        """Execute raw async bulk operations."""
        if not self.connected:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            from elasticsearch.helpers import async_bulk
            success, failed = await async_bulk(self.es, actions)
            return {'success': success, 'failed': failed}
        except Exception as e:
            logger.error(f"Bulk operation failed (async): {e}")
            raise

    async def execute_scan(self, index: str, query: Dict[str, Any], scroll_size: int = 1000, scroll_time: str = "5m"):
        """Execute raw async scan for large datasets."""
        if not self.connected:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            from elasticsearch.helpers import async_scan
            async for doc in async_scan(
                    self.es,
                    query=query,
                    index=index,
                    size=scroll_size,
                    scroll=scroll_time
            ):
                yield doc
        except Exception as e:
            logger.error(f"Scan failed (async): {e}")
            raise

    # BASIC ASYNC INDEX MANAGEMENT (connection level)
    async def create_index(self, index: str, mapping: Dict[str, Any] = None, settings: Dict[str, Any] = None):
        """Create index with mapping and settings (async)."""
        if not self.connected:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            # Delete existing index
            if await self.es.indices.exists(index=index):
                await self.es.indices.delete(index=index)
                logger.info(f"Deleted existing index: {index}")

            # Create index body
            body = {}
            if mapping:
                body["mappings"] = mapping
            if settings:
                body["settings"] = settings

            await self.es.indices.create(index=index, body=body if body else None)
            logger.info(f"Created index: {index} (async)")
            return True
        except Exception as e:
            logger.error(f"Failed to create index (async): {e}")
            return False

    async def delete_index(self, index: str):
        """Delete index (async)."""
        if not self.connected:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            await self.es.indices.delete(index=index)
            logger.info(f"Deleted index: {index} (async)")
            return True
        except Exception as e:
            logger.error(f"Failed to delete index (async): {e}")
            return False

    async def index_exists(self, index: str) -> bool:
        """Check if index exists (async)."""
        if not self.connected:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            return await self.es.indices.exists(index=index)
        except Exception as e:
            logger.error(f"Failed to check index existence (async): {e}")
            return False

    async def refresh_index(self, index: str):
        """Refresh index (async)."""
        if not self.connected:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            return await self.es.indices.refresh(index=index)
        except Exception as e:
            logger.error(f"Failed to refresh index (async): {e}")
            raise

    async def close(self):
        """Close async connection."""
        if self.es and self.connected:
            await self.es.close()
            self.connected = False
            logger.info("Elasticsearch async connection closed")