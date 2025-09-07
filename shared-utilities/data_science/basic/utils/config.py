# ============================================================================
# shared-utilities/data_science/utils/config.py
# ============================================================================
"""
Configuration Management - Settings and configuration classes
Centralized configuration for data science components
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class DataScienceConfig:
    """
    Main configuration class for data science utilities
    """
    # Basic settings
    default_language: str = "english"
    default_encoding: str = "utf-8"
    cache_enabled: bool = True
    auto_save_operations: bool = False

    # Connection settings
    connection_timeout: int = 30
    max_cache_size: int = 1000
    max_retries: int = 3

    # Processing settings
    chunk_size: int = 1000
    parallel_processing: bool = False
    max_workers: int = 4

    # Logging settings
    log_level: str = "INFO"
    log_operations: bool = True
    detailed_logging: bool = False

    # File handling
    supported_formats: List[str] = field(default_factory=lambda: [
        '.csv', '.tsv', '.json', '.jsonl', '.xlsx', '.xls',
        '.parquet', '.txt', '.html', '.xml'
    ])

    # Text processing
    text_cleaning_options: Dict[str, Any] = field(default_factory=lambda: {
        'remove_urls': True,
        'remove_emails': True,
        'remove_punctuation': True,
        'to_lowercase': True,
        'remove_extra_whitespace': True
    })

    # Sentiment analysis
    sentiment_options: Dict[str, Any] = field(default_factory=lambda: {
        'positive_threshold': 0.05,
        'negative_threshold': -0.05,
        'default_analyzer': 'auto'
    })

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'default_language': self.default_language,
            'default_encoding': self.default_encoding,
            'cache_enabled': self.cache_enabled,
            'auto_save_operations': self.auto_save_operations,
            'connection_timeout': self.connection_timeout,
            'max_cache_size': self.max_cache_size,
            'max_retries': self.max_retries,
            'chunk_size': self.chunk_size,
            'parallel_processing': self.parallel_processing,
            'max_workers': self.max_workers,
            'log_level': self.log_level,
            'log_operations': self.log_operations,
            'detailed_logging': self.detailed_logging,
            'supported_formats': self.supported_formats,
            'text_cleaning_options': self.text_cleaning_options,
            'sentiment_options': self.sentiment_options
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DataScienceConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)

    @classmethod
    def from_json(cls, json_path: str) -> 'DataScienceConfig':
        """Load configuration from JSON file."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            return cls.from_dict(config_dict)
        except Exception as e:
            logger.error(f"Failed to load configuration from {json_path}: {e}")
            raise

    def save_to_json(self, json_path: str) -> bool:
        """Save configuration to JSON file."""
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {json_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration to {json_path}: {e}")
            return False

    def update(self, **kwargs) -> 'DataScienceConfig':
        """Update configuration with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logger.warning(f"Unknown configuration option: {key}")
        return self

    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []

        # Validate basic settings
        if self.connection_timeout <= 0:
            issues.append("connection_timeout must be positive")

        if self.max_cache_size <= 0:
            issues.append("max_cache_size must be positive")

        if self.chunk_size <= 0:
            issues.append("chunk_size must be positive")

        if self.max_workers <= 0:
            issues.append("max_workers must be positive")

        # Validate language
        supported_languages = ['english', 'hebrew', 'spanish', 'french', 'german']
        if self.default_language not in supported_languages:
            issues.append(f"default_language must be one of: {supported_languages}")

        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_log_levels:
            issues.append(f"log_level must be one of: {valid_log_levels}")

        # Validate sentiment thresholds
        sentiment_opts = self.sentiment_options
        if 'positive_threshold' in sentiment_opts and 'negative_threshold' in sentiment_opts:
            if sentiment_opts['positive_threshold'] <= sentiment_opts['negative_threshold']:
                issues.append("positive_threshold must be greater than negative_threshold")

        return issues


@dataclass
class PipelineConfig:
    """
    Configuration for data science pipelines
    """
    # Pipeline type
    pipeline_type: str = "auto"  # 'basic', 'advanced_sync', 'advanced_async', 'auto'

    # Data source settings
    data_source: Optional[str] = None
    text_column: Optional[str] = None
    category_column: Optional[str] = None

    # Processing steps
    enable_cleaning: bool = True
    enable_sentiment: bool = True
    enable_analysis: bool = True
    enable_nlp: bool = False

    # Advanced settings
    sentiment_analyzer: str = "auto"  # 'auto', 'vader', 'textblob', 'ensemble'
    nlp_processor: str = "auto"  # 'auto', 'nltk', 'spacy', 'basic'
    language_processor: str = "auto"  # 'auto', 'english', 'hebrew'

    # Output settings
    include_intermediate_results: bool = False
    save_results: bool = False
    output_format: str = "dict"  # 'dict', 'dataframe', 'json'

    # Performance settings
    batch_processing: bool = False
    batch_size: int = 100
    use_multiprocessing: bool = False

    # Custom options
    custom_options: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert pipeline configuration to dictionary."""
        return {
            'pipeline_type': self.pipeline_type,
            'data_source': self.data_source,
            'text_column': self.text_column,
            'category_column': self.category_column,
            'enable_cleaning': self.enable_cleaning,
            'enable_sentiment': self.enable_sentiment,
            'enable_analysis': self.enable_analysis,
            'enable_nlp': self.enable_nlp,
            'sentiment_analyzer': self.sentiment_analyzer,
            'nlp_processor': self.nlp_processor,
            'language_processor': self.language_processor,
            'include_intermediate_results': self.include_intermediate_results,
            'save_results': self.save_results,
            'output_format': self.output_format,
            'batch_processing': self.batch_processing,
            'batch_size': self.batch_size,
            'use_multiprocessing': self.use_multiprocessing,
            'custom_options': self.custom_options
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'PipelineConfig':
        """Create pipeline configuration from dictionary."""
        return cls(**config_dict)

    def validate(self) -> List[str]:
        """Validate pipeline configuration."""
        issues = []

        # Validate pipeline type
        valid_types = ['basic', 'advanced_sync', 'advanced_async', 'auto']
        if self.pipeline_type not in valid_types:
            issues.append(f"pipeline_type must be one of: {valid_types}")

        # Validate required fields for data processing
        if self.data_source and not self.text_column:
            issues.append("text_column is required when data_source is specified")

        # Validate batch settings
        if self.batch_processing and self.batch_size <= 0:
            issues.append("batch_size must be positive when batch_processing is enabled")

        # Validate output format
        valid_formats = ['dict', 'dataframe', 'json']
        if self.output_format not in valid_formats:
            issues.append(f"output_format must be one of: {valid_formats}")

        return issues

    def get_effective_config(self, system_capabilities: Dict[str, Any]) -> 'PipelineConfig':
        """
        Get effective configuration based on system capabilities.

        Args:
            system_capabilities: Available system capabilities

        Returns:
            Effective configuration adjusted for available components
        """
        effective = PipelineConfig(**self.to_dict())

        # Adjust pipeline type based on capabilities
        if effective.pipeline_type == 'auto':
            if system_capabilities.get('advanced_sync', False):
                effective.pipeline_type = 'advanced_sync'
            elif system_capabilities.get('advanced_async', False):
                effective.pipeline_type = 'advanced_async'
            else:
                effective.pipeline_type = 'basic'

        # Adjust analyzers based on available libraries
        if effective.sentiment_analyzer == 'auto':
            ext_libs = system_capabilities.get('external_libraries', {})
            if ext_libs.get('nltk', False):
                effective.sentiment_analyzer = 'vader'
            elif ext_libs.get('textblob', False):
                effective.sentiment_analyzer = 'textblob'
            else:
                effective.sentiment_analyzer = 'basic'

        if effective.nlp_processor == 'auto':
            ext_libs = system_capabilities.get('external_libraries', {})
            if ext_libs.get('spacy', False):
                effective.nlp_processor = 'spacy'
            elif ext_libs.get('nltk', False):
                effective.nlp_processor = 'nltk'
            else:
                effective.nlp_processor = 'basic'

        # Disable features not available in basic mode
        if effective.pipeline_type == 'basic':
            effective.enable_nlp = False
            if effective.sentiment_analyzer not in ['basic', 'simple']:
                effective.sentiment_analyzer = 'basic'

        return effective


# ============================================================================
# Predefined Configurations
# ============================================================================

# Default basic configuration
DEFAULT_BASIC_CONFIG = DataScienceConfig(
    default_language="english",
    cache_enabled=True,
    auto_save_operations=False,
    parallel_processing=False,
    text_cleaning_options={
        'remove_urls': True,
        'remove_emails': True,
        'remove_punctuation': True,
        'to_lowercase': True,
        'remove_extra_whitespace': True
    },
    sentiment_options={
        'positive_threshold': 0.1,
        'negative_threshold': -0.1,
        'default_analyzer': 'basic'
    }
)

# Default advanced configuration
DEFAULT_ADVANCED_CONFIG = DataScienceConfig(
    default_language="english",
    cache_enabled=True,
    auto_save_operations=True,
    parallel_processing=True,
    max_workers=4,
    text_cleaning_options={
        'remove_urls': True,
        'remove_emails': True,
        'remove_mentions': True,
        'remove_hashtags': True,
        'remove_punctuation': True,
        'to_lowercase': True,
        'remove_extra_whitespace': True
    },
    sentiment_options={
        'positive_threshold': 0.05,
        'negative_threshold': -0.05,
        'default_analyzer': 'ensemble'
    }
)