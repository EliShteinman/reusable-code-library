# ============================================================================
# shared-utilities/data_science/basic/__init__.py
# ============================================================================
"""
Basic Components - Dependency-free data science operations
Simple, reliable components that work without external libraries
"""

# Import clients
from .clients import (
    DataLoaderClient,
    TextProcessorClient
)

# Import repositories
from .repositories import (
    TextCleaningRepository,
    TextAnalysisRepository,
    SentimentAnalysisRepository
)

__all__ = [
    # Clients (connection management)
    'DataLoaderClient',
    'TextProcessorClient',

    # Repositories (CRUD operations)
    'TextCleaningRepository',
    'TextAnalysisRepository',
    'SentimentAnalysisRepository'
]