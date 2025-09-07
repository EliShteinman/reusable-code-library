# shared-utilities/elasticsearch/elasticsearch_async_client.py
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

    async def connect(self):
        """Create async connection."""
        try:
            # Import here to avoid issues if elasticsearch-async not installed
            from elasticsearch import AsyncElasticsearch
            self.es = AsyncElasticsearch(self.es_url)

            # Test connection
            info = await self.es.info()
            logger.info(f"Connected to Elasticsearch {info['version']['number']} (async)")
            self.connected = True

        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch (async): {e}")
            raise

    # RAW ASYNC ELASTICSEARCH OPERATIONS
    async def execute_index(self, index: str, doc: Dict[str, Any], doc_id: str = None):
        """Execute index operation."""
        if not self.connected:
            raise RuntimeError("Client not connected")

        if doc_id:
            return await self.es.index(index=index, id=doc_id, body=doc)
        else:
            return await self.es.index(index=index, body=doc)

    async def execute_get(self, index: str, doc_id: str):
        """Execute get operation."""
        try:
            return await self.es.get(index=index, id=doc_id)
        except Exception as e:
            logger.error(f"Document not found: {e}")
            return None

    async def execute_search(self, index: str, query: Dict[str, Any]):
        """Execute search operation."""
        return await self.es.search(index=index, body=query)

    async def close(self):
        """Close async connection."""
        if self.es and self.connected:
            await self.es.close()
            self.connected = False
            logger.info("Elasticsearch async connection closed")