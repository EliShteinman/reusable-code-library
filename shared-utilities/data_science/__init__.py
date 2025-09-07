# ============================================================================
# shared-utilities/data_science/__init__.py - CLEAN ORGANIZED STRUCTURE
# ============================================================================
"""
Data Science Utilities - Organized Architecture

Basic vs Advanced separation with clear Client/Repository pattern
Sync/Async support for advanced features
"""

import logging

logger = logging.getLogger(__name__)

# ============================================================================
# BASIC IMPORTS (Always Available)
# ============================================================================

# Basic clients (connection management)
from .basic.clients import (
    DataLoaderClient,
    TextProcessorClient
)

# Basic repositories (CRUD operations)
from .basic.repositories import (
    TextCleaningRepository,
    TextAnalysisRepository,
    SentimentAnalysisRepository
)

# ============================================================================
# ADVANCED IMPORTS (Library Dependent)
# ============================================================================

try:
    # Advanced sync clients
    from .advanced.clients.sync import (
        SentimentClient,
        NLPClient
    )

    # Advanced sync repositories
    from .advanced.repositories.sync import (
        AdvancedSentimentRepository,
        NLPRepository,
        HebrewRepository
    )

    ADVANCED_SYNC_AVAILABLE = True
    logger.info("Advanced sync components loaded successfully")

except ImportError as e:
    ADVANCED_SYNC_AVAILABLE = False
    logger.warning(f"Advanced sync components not available: {e}")

try:
    # Advanced async clients
    from .advanced.clients.async_ import (
        AsyncSentimentClient,
        AsyncNLPClient
    )

    # Advanced async repositories
    from .advanced.repositories.async_ import (
        AsyncSentimentRepository,
        AsyncNLPRepository,
        AsyncHebrewRepository
    )

    ADVANCED_ASYNC_AVAILABLE = True
    logger.info("Advanced async components loaded successfully")

except ImportError as e:
    ADVANCED_ASYNC_AVAILABLE = False
    logger.warning(f"Advanced async components not available: {e}")

# ============================================================================
# FACTORY AND BASE CLASSES
# ============================================================================

try:
    from .advanced.base import (
        SentimentAnalyzerBase,
        TextProcessorBase,
        ProcessorFactory,
        ProcessingConfig
    )

    FACTORY_AVAILABLE = True

except ImportError as e:
    FACTORY_AVAILABLE = False
    logger.warning(f"Factory pattern not available: {e}")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

from .utils import (
    create_basic_pipeline,
    create_advanced_pipeline,
    get_system_capabilities,
    quick_sentiment_check,
    extract_all_features
)

# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    # Basic components (always available)
    'DataLoaderClient',
    'TextProcessorClient',
    'TextCleaningRepository',
    'TextAnalysisRepository',
    'SentimentAnalysisRepository',

    # Utility functions
    'create_basic_pipeline',
    'create_advanced_pipeline',
    'get_system_capabilities',
    'quick_sentiment_check',
    'extract_all_features',

    # Status flags
    'ADVANCED_SYNC_AVAILABLE',
    'ADVANCED_ASYNC_AVAILABLE',
    'FACTORY_AVAILABLE'
]

# Conditionally add advanced components to public API
if ADVANCED_SYNC_AVAILABLE:
    __all__.extend([
        'SentimentClient',
        'NLPClient',
        'AdvancedSentimentRepository',
        'NLPRepository',
        'HebrewRepository'
    ])

if ADVANCED_ASYNC_AVAILABLE:
    __all__.extend([
        'AsyncSentimentClient',
        'AsyncNLPClient',
        'AsyncSentimentRepository',
        'AsyncNLPRepository',
        'AsyncHebrewRepository'
    ])

if FACTORY_AVAILABLE:
    __all__.extend([
        'SentimentAnalyzerBase',
        'TextProcessorBase',
        'ProcessorFactory',
        'ProcessingConfig'
    ])


# ============================================================================
# INITIALIZATION
# ============================================================================

def get_available_components():
    """Get status of all components."""
    return {
        'basic': True,  # Always available
        'advanced_sync': ADVANCED_SYNC_AVAILABLE,
        'advanced_async': ADVANCED_ASYNC_AVAILABLE,
        'factory_pattern': FACTORY_AVAILABLE,
        'total_components': len(__all__)
    }


# Log initialization status
logger.info("=" * 60)
logger.info("Data Science Utilities - Organized Structure Loaded")
logger.info("=" * 60)

capabilities = get_available_components()
for component, available in capabilities.items():
    if component != 'total_components':
        status = "✅" if available else "❌"
        logger.info(f"{status} {component.replace('_', ' ').title()}")

logger.info(f"📦 Total components available: {capabilities['total_components']}")
logger.info("=" * 60)