# ============================================================================
# shared-utilities/data_science/basic/clients/text_processor_client.py
# ============================================================================
"""
Text Processor Client - Basic Text Processing Connection Management
Handles connection to text processing resources and basic NLP operations
"""

import re
import string
import logging
from typing import List, Dict, Any, Optional, Set
from collections import Counter

logger = logging.getLogger(__name__)


class TextProcessorClient:
    """
    Client for managing basic text processing connections
    Provides dependency-free text processing capabilities
    """

    def __init__(self,
                 default_language: str = "english",
                 cache_results: bool = True,
                 max_cache_size: int = 1000):
        """
        Initialize text processor client.

        Args:
            default_language: Default language for processing
            cache_results: Whether to cache processing results
            max_cache_size: Maximum number of cached results
        """
        self.default_language = default_language
        self.cache_results = cache_results
        self.max_cache_size = max_cache_size
        self._processing_cache = {}
        self._connection_active = False

        # Basic language resources
        self._setup_language_resources()

        # Establish connection to processing resources
        self._connect()

    def _setup_language_resources(self):
        """Setup basic language processing resources."""
        # Basic stopwords for multiple languages
        self.stopwords = {
            'english': {
                'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
                'to', 'was', 'will', 'with', 'i', 'you', 'we', 'they', 'this',
                'but', 'not', 'or', 'have', 'had', 'what', 'when', 'where', 'who',
                'would', 'could', 'should', 'can', 'may', 'might', 'must', 'shall'
            },
            'hebrew': {
                'של', 'את', 'על', 'אל', 'זה', 'זו', 'זאת', 'אני', 'אתה', 'אתם', 'אתן',
                'היא', 'הוא', 'הם', 'הן', 'אנחנו', 'אנו', 'יש', 'אין', 'היה', 'היתה',
                'היו', 'הייתי', 'הייתה', 'היינו', 'הייתם', 'גם', 'כל', 'כמו', 'או',
                'אבל', 'רק', 'עוד', 'פה', 'שם', 'כאן', 'שלא', 'לא', 'עם', 'לפני',
                'אחרי', 'בתוך', 'מתוך', 'אצל', 'ליד', 'מול', 'תחת', 'מעל', 'בין'
            }
        }

        # Basic word patterns for stemming
        self.english_suffixes = {
            'ing': 3, 'ed': 2, 'er': 2, 'est': 3, 'ly': 2, 'tion': 4, 'sion': 4,
            'ness': 4, 'ment': 4, 'able': 4, 'ible': 4, 'ful': 3, 'less': 4
        }

        # Hebrew prefixes and suffixes
        self.hebrew_prefixes = {'ו', 'ב', 'ל', 'מ', 'ה', 'כ', 'ש'}
        self.hebrew_suffixes = {'ים', 'ות', 'יה', 'ון', 'ית', 'י', 'ה', 'ת', 'ך', 'נו', 'כם', 'הן'}

    def _connect(self):
        """Establish connection to text processing resources."""
        try:
            # Test basic processing capabilities
            test_text = "This is a test sentence for connection validation."
            tokens = self._basic_tokenize(test_text)

            if tokens:
                self._connection_active = True
                logger.info(f"TextProcessorClient connected successfully for {self.default_language}")
            else:
                raise RuntimeError("Basic tokenization failed")

        except Exception as e:
            logger.error(f"Failed to establish text processing connection: {e}")
            raise

    def create_session(self, language: str = None, **session_options) -> 'TextProcessingSession':
        """
        Create a text processing session.

        Args:
            language: Language for this session
            **session_options: Session-specific options

        Returns:
            TextProcessingSession object
        """
        if not self._connection_active:
            raise RuntimeError("Text processor not connected")

        session_language = language or self.default_language

        session = TextProcessingSession(
            client=self,
            language=session_language,
            **session_options
        )

        logger.info(f"Created text processing session for {session_language}")
        return session

    def test_connection(self) -> Dict[str, Any]:
        """
        Test text processing connection.

        Returns:
            Connection test results
        """
        try:
            test_cases = [
                "English test sentence with multiple words.",
                "טקסט בדיקה בעברית עם מילים שונות.",
                "Test with numbers 123 and symbols @#$!"
            ]

            results = []
            for test_text in test_cases:
                try:
                    tokens = self._basic_tokenize(test_text)
                    clean_text = self._basic_clean(test_text)

                    results.append({
                        'input': test_text,
                        'tokens': len(tokens),
                        'cleaned_length': len(clean_text),
                        'success': True
                    })
                except Exception as e:
                    results.append({
                        'input': test_text,
                        'error': str(e),
                        'success': False
                    })

            return {
                'connection_active': self._connection_active,
                'default_language': self.default_language,
                'supported_languages': list(self.stopwords.keys()),
                'test_results': results,
                'cache_size': len(self._processing_cache),
                'capabilities': [
                    'tokenization', 'cleaning', 'stopword_removal',
                    'basic_stemming', 'word_counting', 'pattern_matching'
                ]
            }

        except Exception as e:
            return {
                'connection_active': False,
                'error': str(e)
            }

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self.stopwords.keys())

    def clear_cache(self):
        """Clear processing cache."""
        self._processing_cache.clear()
        logger.info("Text processing cache cleared")

    def close(self):
        """Close text processing connection."""
        self._connection_active = False
        self.clear_cache()
        logger.info("Text processor connection closed")

    # ========================================================================
    # Basic Text Processing Methods (Internal)
    # ========================================================================

    def _basic_tokenize(self, text: str) -> List[str]:
        """Basic tokenization without external dependencies."""
        if not text or not isinstance(text, str):
            return []

        # Check cache
        cache_key = f"tokenize:{hash(text)}"
        if self.cache_results and cache_key in self._processing_cache:
            return self._processing_cache[cache_key]

        # Simple word tokenization with Unicode support
        tokens = re.findall(r'\b\w+\b', text)

        # Cache result
        if self.cache_results and len(self._processing_cache) < self.max_cache_size:
            self._processing_cache[cache_key] = tokens

        return tokens

    def _basic_clean(self, text: str, **options) -> str:
        """Basic text cleaning without external dependencies."""
        if not text or not isinstance(text, str):
            return ""

        cleaned = text

        # Remove URLs
        if options.get('remove_urls', True):
            cleaned = re.sub(r'http[s]?://[^\s]+', '', cleaned)

        # Remove emails
        if options.get('remove_emails', True):
            cleaned = re.sub(r'\S+@\S+', '', cleaned)

        # Remove mentions and hashtags
        if options.get('remove_mentions', False):
            cleaned = re.sub(r'@\w+', '', cleaned)
        if options.get('remove_hashtags', False):
            cleaned = re.sub(r'#\w+', '', cleaned)

        # Remove punctuation
        if options.get('remove_punctuation', True):
            cleaned = cleaned.translate(str.maketrans('', '', string.punctuation))

        # Convert to lowercase
        if options.get('to_lowercase', True):
            cleaned = cleaned.lower()

        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

    def _basic_stem(self, word: str, language: str = None) -> str:
        """Basic stemming for single word."""
        lang = language or self.default_language

        if lang == 'english':
            return self._english_stem(word)
        elif lang == 'hebrew':
            return self._hebrew_stem(word)
        else:
            return word.lower()

    def _english_stem(self, word: str) -> str:
        """Basic English stemming."""
        word = word.lower()

        for suffix, length in self.english_suffixes.items():
            if word.endswith(suffix) and len(word) > length + 2:
                return word[:-length]

        return word

    def _hebrew_stem(self, word: str) -> str:
        """Basic Hebrew stemming."""
        if len(word) < 3:
            return word

        stem = word

        # Remove prefixes
        for prefix in self.hebrew_prefixes:
            if stem.startswith(prefix) and len(stem) > len(prefix) + 1:
                stem = stem[len(prefix):]
                break

        # Remove suffixes
        for suffix in sorted(self.hebrew_suffixes, key=len, reverse=True):
            if stem.endswith(suffix) and len(stem) > len(suffix) + 1:
                stem = stem[:-len(suffix)]
                break

        return stem


class TextProcessingSession:
    """
    Represents an active text processing session
    Provides methods for text operations using established connection
    """

    def __init__(self,
                 client: TextProcessorClient,
                 language: str,
                 **options):
        """
        Initialize text processing session.

        Args:
            client: Parent text processor client
            language: Language for this session
            **options: Session options
        """
        self.client = client
        self.language = language
        self.options = options
        self._session_active = True

        logger.info(f"Text processing session initialized for {language}")

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using session connection."""
        if not self._session_active:
            raise RuntimeError("Session not active")

        return self.client._basic_tokenize(text)

    def clean_text(self, text: str, **clean_options) -> str:
        """Clean text using session connection."""
        if not self._session_active:
            raise RuntimeError("Session not active")

        # Merge session options with method options
        merged_options = {**self.options, **clean_options}
        return self.client._basic_clean(text, **merged_options)

    def extract_stems(self, text: str) -> List[str]:
        """Extract word stems from text."""
        if not self._session_active:
            raise RuntimeError("Session not active")

        tokens = self.tokenize(text)
        stems = []

        for token in tokens:
            if token.isalpha():  # Only process alphabetic tokens
                stem = self.client._basic_stem(token, self.language)
                stems.append(stem)

        return stems

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from token list."""
        if not self._session_active:
            raise RuntimeError("Session not active")

        stopwords_set = self.client.stopwords.get(self.language, set())
        return [token for token in tokens if token.lower() not in stopwords_set]

    def count_words(self, text: str, remove_stopwords: bool = False) -> Dict[str, int]:
        """Count word frequencies in text."""
        if not self._session_active:
            raise RuntimeError("Session not active")

        tokens = self.tokenize(text.lower())

        if remove_stopwords:
            tokens = self.remove_stopwords(tokens)

        return dict(Counter(tokens))

    def extract_patterns(self, text: str, patterns: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract patterns from text using regex."""
        if not self._session_active:
            raise RuntimeError("Session not active")

        results = {}
        for pattern_name, pattern_regex in patterns.items():
            matches = re.findall(pattern_regex, text)
            results[pattern_name] = matches

        return results

    def get_text_stats(self, text: str) -> Dict[str, Any]:
        """Get comprehensive text statistics."""
        if not self._session_active:
            raise RuntimeError("Session not active")

        tokens = self.tokenize(text)
        unique_tokens = set(tokens)

        return {
            'character_count': len(text),
            'word_count': len(tokens),
            'unique_words': len(unique_tokens),
            'vocabulary_richness': len(unique_tokens) / len(tokens) if tokens else 0,
            'average_word_length': sum(len(token) for token in tokens) / len(tokens) if tokens else 0,
            'sentences': len(re.findall(r'[.!?]+', text)),
            'language': self.language
        }

    def close(self):
        """Close processing session."""
        self._session_active = False
        logger.info(f"Text processing session closed for {self.language}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()