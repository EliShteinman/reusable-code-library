# ============================================================================
# shared-utilities/mongodb/__init__.py - FIXED VERSION
# ============================================================================
"""
MongoDB utilities - CLEAN ARCHITECTURE
Connection clients handle ONLY connections
Repositories handle ONLY CRUD operations
"""

from .mongodb_sync_client import MongoDBSyncClient
from .mongodb_async_client import MongoDBAsyncClient
from .mongodb_repository import MongoDBRepository

# Keep existing singleton for backward compatibility
from .mongo_client import SingletonMongoClient

__all__ = [
    'MongoDBSyncClient',  # Sync connections only
    'MongoDBAsyncClient',  # Async connections only
    'MongoDBRepository',  # CRUD operations only
    'SingletonMongoClient'  # Existing (unchanged)
]


# Quick setup functions
def setup_mongodb_sync(mongo_uri: str, db_name: str, collection_name: str):
    """Quick setup: sync client + repository."""
    client = MongoDBSyncClient(mongo_uri, db_name)
    client.connect()
    repo = MongoDBRepository(client, collection_name)
    return client, repo


async def setup_mongodb_async(mongo_uri: str, db_name: str, collection_name: str):
    """Quick setup: async client + repository."""
    client = MongoDBAsyncClient(mongo_uri, db_name)
    await client.connect()
    repo = MongoDBRepository(client, collection_name)
    return client, repo