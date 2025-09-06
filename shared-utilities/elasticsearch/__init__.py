# shared-utilities/elasticsearch/__init__.py
"""
Elasticsearch utilities for search and indexing operations.
"""
from typing import Any, Dict, Union

from .elasticsearch_sync_client import ElasticsearchSyncClient
from .elasticsearch_async_client import ElasticsearchAsyncClient
from .elasticsearch_repository import ElasticsearchRepository

__all__ = [
    'ElasticsearchSyncClient',
    'ElasticsearchAsyncClient',
    'ElasticsearchRepository'
]


# Quick factory functions
def create_sync_client(es_url: str, index_name: str = None) -> ElasticsearchSyncClient:
    """Create sync Elasticsearch client."""
    return ElasticsearchSyncClient(es_url, index_name)


def create_async_client(es_url: str, index_name: str = None) -> ElasticsearchAsyncClient:
    """Create an async Elasticsearch client."""
    return ElasticsearchAsyncClient(es_url, index_name)


def create_repository(client: Union[ElasticsearchSyncClient, ElasticsearchAsyncClient],
                      index_name: str) -> ElasticsearchRepository:
    """Create an Elasticsearch repository."""
    return ElasticsearchRepository(client, index_name)


# Usage examples
def setup_elasticsearch_sync(es_url: str, index_name: str, mapping: Dict[str, Any] = None):
    """Quick setup for sync Elasticsearch with a repository."""
    client = create_sync_client(es_url, index_name)
    repo = create_repository(client, index_name)

    if mapping:
        repo.initialize_index(mapping)

    return client, repo


async def setup_elasticsearch_async(es_url: str, index_name: str, mapping: Dict[str, Any] = None):
    """Quick setup for async Elasticsearch with repository."""
    client = create_async_client(es_url, index_name)
    repo = create_repository(client, index_name)

    if mapping:
        await repo.initialize_index(mapping)

    return client, repo


# Example usage patterns
def example_usage():
    """
    Example usage of Elasticsearch utilities.
    """

    # Sync example
    client, repo = setup_elasticsearch_sync(
        "http://localhost:9200",
        "my_index",
        {
            "properties": {
                "title": {"type": "text"},
                "content": {"type": "text"},
                "tags": {"type": "keyword"},
                "created_at": {"type": "date"}
            }
        }
    )

    # Create document
    doc_id = repo.create({
        "title": "Test Document",
        "content": "This is test content",
        "tags": ["test", "example"]
    })

    # Search documents
    results = repo.search("test", limit=10)

    # Search by field
    tagged_docs = repo.search_by_field("tags", "test")

    # Bulk create from list
    documents = [
        {"title": f"Doc {i}", "content": f"Content {i}"}
        for i in range(100)
    ]
    bulk_result = repo.bulk_create(documents)

    client.close()

    return results, bulk_result


async def example_async_usage():
    """
    Example async usage of Elasticsearch utilities.
    """

    # Async example
    client, repo = await setup_elasticsearch_async(
        "http://localhost:9200",
        "my_async_index"
    )

    # Create a document
    doc_id = await repo.create({
        "title": "Async Test Document",
        "content": "This is async test content"
    })

    # Search documents
    results = await repo.search("async", limit=10)

    # Stream large result sets
    async for doc in client.scroll_search(query_text="test"):
        print(f"Processing doc: {doc['id']}")
        # Process document
        break  # Just show first one in example

    await client.close()

    return results