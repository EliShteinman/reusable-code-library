# ============================================================================
# shared-utilities/elasticsearch/__init__.py - FIXED VERSION
# ============================================================================
"""
Elasticsearch utilities - CLEAN ARCHITECTURE
Connection clients handle ONLY connections
Repositories handle ONLY CRUD operations - SEPARATED by sync/async
"""

from .elasticsearch_sync_client import ElasticsearchSyncClient
from .elasticsearch_async_client import ElasticsearchAsyncClient
from .elasticsearch_sync_repository import ElasticsearchSyncRepository
from .elasticsearch_async_repository import ElasticsearchAsyncRepository

__all__ = [
    'ElasticsearchSyncClient',      # Sync connections only
    'ElasticsearchAsyncClient',     # Async connections only
    'ElasticsearchSyncRepository',  # Sync CRUD operations only
    'ElasticsearchAsyncRepository'  # Async CRUD operations only
]


# Quick setup functions
def setup_elasticsearch_sync(es_url: str, index_name: str):
    """Quick setup: sync client + sync repository."""
    client = ElasticsearchSyncClient(es_url)
    repository = ElasticsearchSyncRepository(client, index_name)
    return client, repository


async def setup_elasticsearch_async(es_url: str, index_name: str):
    """Quick setup: async client + async repository."""
    client = ElasticsearchAsyncClient(es_url)
    await client.connect()
    repository = ElasticsearchAsyncRepository(client, index_name)
    return client, repository