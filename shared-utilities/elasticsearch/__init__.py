# shared-utilities/elasticsearch/__init__.py
"""
Elasticsearch utilities - CLEAN ARCHITECTURE
Connection clients handle ONLY connections
Repositories handle ONLY CRUD operations
"""

from .elasticsearch_sync_client import ElasticsearchSyncClient
from .elasticsearch_async_client import ElasticsearchAsyncClient
from .elasticsearch_repository import ElasticsearchRepository

__all__ = [
    'ElasticsearchSyncClient',  # Sync connections only
    'ElasticsearchAsyncClient',  # Async connections only
    'ElasticsearchRepository'  # CRUD operations only
]


# Quick setup functions
def setup_elasticsearch_sync(es_url: str, index_name: str):
    """Quick setup: client + repository."""
    client = ElasticsearchSyncClient(es_url)
    repo = ElasticsearchRepository(client, index_name)
    return client, repo


async def setup_elasticsearch_async(es_url: str, index_name: str):
    """Quick setup: async client + repository."""
    client = ElasticsearchAsyncClient(es_url)
    await client.connect()
    repo = ElasticsearchRepository(client, index_name)
    return client, repo