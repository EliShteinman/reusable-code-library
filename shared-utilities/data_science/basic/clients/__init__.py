# ============================================================================
# shared-utilities/data_science/basic/clients/__init__.py
# ============================================================================
"""
Basic Clients - Connection Management
Simple, dependency-free clients for basic data science operations
"""

from .data_loader_client import DataLoaderClient
from .text_processor_client import TextProcessorClient

__all__ = [
    'DataLoaderClient',
    'TextProcessorClient'
]