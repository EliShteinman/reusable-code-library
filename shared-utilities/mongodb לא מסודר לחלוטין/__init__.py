# ============================================================================
# shared-utilities/mongodb/__init__.py - FIXED VERSION
# ============================================================================
"""
MongoDB utilities - CLEAN ARCHITECTURE
Connection clients handle ONLY connections
Repositories handle ONLY CRUD operations - SEPARATED by sync/async
"""

from .mongodb_sync_client import MongoDBSyncClient
from .mongodb_async_client import MongoDBAsyncClient
from .mongodb_sync_repository import MongoDBSyncRepository
from .mongodb_async_repository import MongoDBAsyncRepository

# Keep existing singleton for backward compatibility
from .mongo_client import SingletonMongoClient

__all__ = [
    'MongoDBSyncClient',      # Sync connections only
    'MongoDBAsyncClient',     # Async connections only
    'MongoDBSyncRepository',  # Sync CRUD operations only
    'MongoDBAsyncRepository', # Async CRUD operations only
    'SingletonMongoClient'    # Existing (unchanged)
]


# Quick setup functions
def setup_mongodb_sync(mongo_uri: str, db_name: str, collection_name: str):
    """Quick setup: sync client + sync repository."""
    client = MongoDBSyncClient(mongo_uri, db_name)
    client.connect()
    repository = MongoDBSyncRepository(client, collection_name)
    return client, repository


async def setup_mongodb_async(mongo_uri: str, db_name: str, collection_name: str):
    """Quick setup: async client + async repository."""
    client = MongoDBAsyncClient(mongo_uri, db_name)
    await client.connect()
    repository = MongoDBAsyncRepository(client, collection_name)
    return client, repository