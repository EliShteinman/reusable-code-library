# ============================================================================
# shared-utilities/data_science/text_processing_base.py - GENERIC ARCHITECTURE
# ============================================================================
"""
Abstract base classes for generic text processing
Future-proof design for any sentiment/stemming library
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzerBase(ABC):
    """
    Abstract base class for sentiment analysis
    Supports any sentiment library (VADER, TextBlob, spaCy, Custom)
    """

    @abstractmethod
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.

        Args:
            text: Input text

        Returns:
            Dict with standardized format:
            {
                'compound': float,  # -1 to 1
                'positive': float,  # 0 to 1
                'negative': float,  # 0 to 1
                'neutral': float,   # 0 to 1
                'label': str,       # 'positive', 'negative', 'neutral'
                'confidence': float # 0 to 1
            }
        """
        pass

    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Return list of supported language codes."""
        pass

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple texts."""
        return [self.analyze_sentiment(text) for text in texts]

    def is_language_supported(self, language: str) -> bool:
        """Check if language is supported."""
        return language.lower() in [lang.lower() for lang in self.get_supported_languages()]


class TextProcessorBase(ABC):
    """
    Abstract base class for text processing
    Supports any text processing library (NLTK, spaCy, Custom)
    """

    @abstractmethod
    def clean_text(self, text: str, **options) -> str:
        """Clean and normalize text."""
        pass

    @abstractmethod
    def tokenize(self, text: str) -> List[str]:
        """Split text into tokens."""
        pass

    @abstractmethod
    def extract_stems(self, text: str) -> List[str]:
        """Extract word stems."""
        pass

    @abstractmethod
    def extract_lemmas(self, text: str) -> List[str]:
        """Extract word lemmas (base forms)."""
        pass

    @abstractmethod
    def extract_roots(self, text: str) -> List[str]:
        """Extract word roots."""
        pass

    @abstractmethod
    def remove_stopwords(self, tokens: List[str], language: str = 'english') -> List[str]:
        """Remove stopwords from token list."""
        pass

    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Return list of supported language codes."""
        pass


class LanguageDetectorBase(ABC):
    """
    Abstract base class for language detection
    """

    @abstractmethod
    def detect_language(self, text: str) -> str:
        """
        Detect language of text.

        Returns:
            Language code (e.g., 'en', 'he', 'ar')
        """
        pass

    @abstractmethod
    def detect_with_confidence(self, text: str) -> Dict[str, Any]:
        """
        Detect language with confidence score.

        Returns:
            {
                'language': str,
                'confidence': float,
                'alternatives': List[Dict]
            }
        """
        pass


class TextCleanerBase(ABC):
    """
    Abstract base class for text cleaning strategies
    """

    @abstractmethod
    def clean_basic(self, text: str) -> str:
        """Basic cleaning (whitespace, punctuation)."""
        pass

    @abstractmethod
    def clean_advanced(self, text: str) -> str:
        """Advanced cleaning (URLs, emails, special chars)."""
        pass

    @abstractmethod
    def clean_social_media(self, text: str) -> str:
        """Social media specific cleaning (mentions, hashtags)."""
        pass

    @abstractmethod
    def normalize_text(self, text: str) -> str:
        """Normalize text (case, encoding, etc.)."""
        pass


class FeatureExtractorBase(ABC):
    """
    Abstract base class for feature extraction
    """

    @abstractmethod
    def extract_keywords(self, text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Extract keywords from text."""
        pass

    @abstractmethod
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities."""
        pass

    @abstractmethod
    def extract_pos_tags(self, text: str) -> List[Dict[str, str]]:
        """Extract part-of-speech tags."""
        pass

    @abstractmethod
    def extract_ngrams(self, text: str, n: int = 2) -> List[str]:
        """Extract n-grams."""
        pass


# ============================================================================
# Factory Interface
# ============================================================================

class ProcessorFactory:
    """
    Factory for creating text processors
    Enables easy switching between implementations
    """

    _sentiment_analyzers = {}
    _text_processors = {}
    _language_detectors = {}
    _text_cleaners = {}
    _feature_extractors = {}

    @classmethod
    def register_sentiment_analyzer(cls, name: str, analyzer_class):
        """Register a sentiment analyzer implementation."""
        cls._sentiment_analyzers[name] = analyzer_class
        logger.info(f"Registered sentiment analyzer: {name}")

    @classmethod
    def register_text_processor(cls, name: str, processor_class):
        """Register a text processor implementation."""
        cls._text_processors[name] = processor_class
        logger.info(f"Registered text processor: {name}")

    @classmethod
    def register_language_detector(cls, name: str, detector_class):
        """Register a language detector implementation."""
        cls._language_detectors[name] = detector_class
        logger.info(f"Registered language detector: {name}")

    @classmethod
    def register_text_cleaner(cls, name: str, cleaner_class):
        """Register a text cleaner implementation."""
        cls._text_cleaners[name] = cleaner_class
        logger.info(f"Registered text cleaner: {name}")

    @classmethod
    def register_feature_extractor(cls, name: str, extractor_class):
        """Register a feature extractor implementation."""
        cls._feature_extractors[name] = extractor_class
        logger.info(f"Registered feature extractor: {name}")

    @classmethod
    def create_sentiment_analyzer(cls, name: str, **kwargs) -> SentimentAnalyzerBase:
        """Create sentiment analyzer instance."""
        if name not in cls._sentiment_analyzers:
            available = list(cls._sentiment_analyzers.keys())
            raise ValueError(f"Unknown sentiment analyzer: {name}. Available: {available}")

        analyzer_class = cls._sentiment_analyzers[name]
        return analyzer_class(**kwargs)

    @classmethod
    def create_text_processor(cls, name: str, **kwargs) -> TextProcessorBase:
        """Create text processor instance."""
        if name not in cls._text_processors:
            available = list(cls._text_processors.keys())
            raise ValueError(f"Unknown text processor: {name}. Available: {available}")

        processor_class = cls._text_processors[name]
        return processor_class(**kwargs)

    @classmethod
    def create_language_detector(cls, name: str, **kwargs) -> LanguageDetectorBase:
        """Create language detector instance."""
        if name not in cls._language_detectors:
            available = list(cls._language_detectors.keys())
            raise ValueError(f"Unknown language detector: {name}. Available: {available}")

        detector_class = cls._language_detectors[name]
        return detector_class(**kwargs)

    @classmethod
    def create_text_cleaner(cls, name: str, **kwargs) -> TextCleanerBase:
        """Create text cleaner instance."""
        if name not in cls._text_cleaners:
            available = list(cls._text_cleaners.keys())
            raise ValueError(f"Unknown text cleaner: {name}. Available: {available}")

        cleaner_class = cls._text_cleaners[name]
        return cleaner_class(**kwargs)

    @classmethod
    def create_feature_extractor(cls, name: str, **kwargs) -> FeatureExtractorBase:
        """Create feature extractor instance."""
        if name not in cls._feature_extractors:
            available = list(cls._feature_extractors.keys())
            raise ValueError(f"Unknown feature extractor: {name}. Available: {available}")

        extractor_class = cls._feature_extractors[name]
        return extractor_class(**kwargs)

    @classmethod
    def list_available(cls) -> Dict[str, List[str]]:
        """List all available implementations."""
        return {
            'sentiment_analyzers': list(cls._sentiment_analyzers.keys()),
            'text_processors': list(cls._text_processors.keys()),
            'language_detectors': list(cls._language_detectors.keys()),
            'text_cleaners': list(cls._text_cleaners.keys()),
            'feature_extractors': list(cls._feature_extractors.keys())
        }


# ============================================================================
# Configuration System
# ============================================================================

class ProcessingConfig:
    """
    Configuration for text processing pipeline
    Allows easy switching of implementations
    """

    def __init__(self,
                 sentiment_analyzer: str = "vader",
                 text_processor: str = "nltk",
                 language_detector: str = "auto",
                 text_cleaner: str = "advanced",
                 feature_extractor: str = "nltk",
                 **kwargs):
        """
        Initialize processing configuration.

        Args:
            sentiment_analyzer: Name of sentiment analyzer to use
            text_processor: Name of text processor to use
            language_detector: Name of language detector to use
            text_cleaner: Name of text cleaner to use
            feature_extractor: Name of feature extractor to use
            **kwargs: Additional configuration options
        """
        self.sentiment_analyzer = sentiment_analyzer
        self.text_processor = text_processor
        self.language_detector = language_detector
        self.text_cleaner = text_cleaner
        self.feature_extractor = feature_extractor
        self.options = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'sentiment_analyzer': self.sentiment_analyzer,
            'text_processor': self.text_processor,
            'language_detector': self.language_detector,
            'text_cleaner': self.text_cleaner,
            'feature_extractor': self.feature_extractor,
            **self.options
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ProcessingConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)

    @classmethod
    def exam_safe_config(cls) -> 'ProcessingConfig':
        """
        Configuration that works even if specific libraries are missing.
        Uses fallback implementations.
        """
        return cls(
            sentiment_analyzer="fallback",
            text_processor="basic",
            language_detector="simple",
            text_cleaner="basic",
            feature_extractor="basic"
        )