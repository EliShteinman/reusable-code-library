# shared-utilities/mongodb/__init__.py
"""
MongoDB utilities for document database operations.
"""

from .mongodb_sync_client import MongoDBSyncClient
from .mongodb_async_client import MongoDBAsyncClient
from .mongodb_repository import MongoDBRepository

# Keep existing singleton for backward compatibility
from .mongo_client import SingletonMongoClient

__all__ = [
    'MongoDBSyncClient',
    'MongoDBAsyncClient',
    'MongoDBRepository',
    'SingletonMongoClient'  # Existing
]


# Quick factory functions
def create_sync_client(mongo_uri: str, db_name: str, collection_name: str = None) -> MongoDBSyncClient:
    """Create sync MongoDB client."""
    return MongoDBSyncClient(mongo_uri, db_name, collection_name)


def create_async_client(mongo_uri: str, db_name: str, collection_name: str = None) -> MongoDBAsyncClient:
    """Create async MongoDB client."""
    return MongoDBAsyncClient(mongo_uri, db_name, collection_name)


def create_repository(client: Union[MongoDBSyncClient, MongoDBAsyncClient],
                      collection_name: str) -> MongoDBRepository:
    """Create MongoDB repository."""
    return MongoDBRepository(client, collection_name)


# Usage examples
def setup_mongodb_sync(mongo_uri: str, db_name: str, collection_name: str):
    """Quick setup for sync MongoDB with repository."""
    client = create_sync_client(mongo_uri, db_name, collection_name)
    repo = create_repository(client, collection_name)

    return client, repo


async def setup_mongodb_async(mongo_uri: str, db_name: str, collection_name: str):
    """Quick setup for async MongoDB with repository."""
    client = create_async_client(mongo_uri, db_name, collection_name)
    await client.connect()
    repo = create_repository(client, collection_name)

    return client, repo


# Example usage patterns
def example_usage():
    """
    Example usage of MongoDB utilities.
    """

    # Sync example
    client, repo = setup_mongodb_sync(
        "mongodb://localhost:27017",
        "my_database",
        "my_collection"
    )

    # Create document
    doc_id = repo.create({
        "ID": 123,
        "name": "Test Document",
        "tags": ["test", "example"]
    })

    # Search documents
    results = repo.search(limit=10)

    # Search by field
    tagged_docs = repo.search_by_field("tags", "test")

    # Range search
    recent_docs = repo.search_range(
        "created_at",
        gte=datetime(2024, 1, 1)
    )

    # Bulk create
    documents = [
        {"ID": i, "name": f"Doc {i}"}
        for i in range(100, 200)
    ]
    bulk_result = repo.bulk_create(documents)

    # Group by field
    groups = repo.group_by("tags")

    client.close()

    return results, bulk_result


async def example_async_usage():
    """
    Example async usage of MongoDB utilities.
    """

    # Async example
    client, repo = await setup_mongodb_async(
        "mongodb://localhost:27017",
        "my_async_database",
        "my_async_collection"
    )

    # Create document
    doc_id = await repo.create({
        "ID": 456,
        "name": "Async Test Document",
        "content": "This is async test content"
    })

    # Search documents
    results = await repo.search(limit=10)

    # Get all documents with filter
    all_docs = await repo.get_all(
        field_filters={"name": {"$regex": "Test"}}
    )

    await client.close()

    return results