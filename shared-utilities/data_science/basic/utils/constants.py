# ============================================================================
# shared-utilities/data_science/utils/constants.py
# ============================================================================
"""
Constants - Shared constants and default values
Common constants used across data science components
"""

from typing import Dict, List, Set, Any

# ============================================================================
# FILE FORMAT CONSTANTS
# ============================================================================

SUPPORTED_FILE_FORMATS = [
    '.csv', '.tsv', '.json', '.jsonl', '.xlsx', '.xls',
    '.parquet', '.txt', '.html', '.xml'
]

FILE_FORMAT_DESCRIPTIONS = {
    '.csv': 'Comma-separated values',
    '.tsv': 'Tab-separated values',
    '.json': 'JavaScript Object Notation',
    '.jsonl': 'JSON Lines (newline-delimited JSON)',
    '.xlsx': 'Excel spreadsheet (modern)',
    '.xls': 'Excel spreadsheet (legacy)',
    '.parquet': 'Apache Parquet columnar format',
    '.txt': 'Plain text file',
    '.html': 'HTML table data',
    '.xml': 'XML structured data'
}

DEFAULT_ENCODING_BY_FORMAT = {
    '.csv': 'utf-8',
    '.tsv': 'utf-8',
    '.json': 'utf-8',
    '.jsonl': 'utf-8',
    '.txt': 'utf-8',
    '.html': 'utf-8',
    '.xml': 'utf-8',
    '.xlsx': None,  # Binary format
    '.xls': None,   # Binary format
    '.parquet': None  # Binary format
}

# ============================================================================
# TEXT PROCESSING CONSTANTS
# ============================================================================

DEFAULT_CLEANING_OPTIONS = {
    'remove_urls': True,
    'remove_emails': True,
    'remove_mentions': False,
    'remove_hashtags': False,
    'remove_punctuation': True,
    'to_lowercase': True,
    'remove_extra_whitespace': True,
    'remove_numbers': False,
    'remove_special_chars': False,
    'custom_replacements': None
}

AGGRESSIVE_CLEANING_OPTIONS = {
    'remove_urls': True,
    'remove_emails': True,
    'remove_mentions': True,
    'remove_hashtags': True,
    'remove_punctuation': True,
    'to_lowercase': True,
    'remove_extra_whitespace': True,
    'remove_numbers': True,
    'remove_special_chars': True,
    'custom_replacements': None
}

MINIMAL_CLEANING_OPTIONS = {
    'remove_urls': False,
    'remove_emails': False,
    'remove_mentions': False,
    'remove_hashtags': False,
    'remove_punctuation': False,
    'to_lowercase': True,
    'remove_extra_whitespace': True,
    'remove_numbers': False,
    'remove_special_chars': False,
    'custom_replacements': None
}

# ============================================================================
# SENTIMENT ANALYSIS CONSTANTS
# ============================================================================

SENTIMENT_THRESHOLDS = {
    'conservative': {
        'positive_threshold': 0.2,
        'negative_threshold': -0.2
    },
    'standard': {
        'positive_threshold': 0.05,
        'negative_threshold': -0.05
    },
    'sensitive': {
        'positive_threshold': 0.01,
        'negative_threshold': -0.01
    }
}

SENTIMENT_LABELS = ['positive', 'negative', 'neutral']

SENTIMENT_ANALYZERS = [
    'vader', 'textblob', 'spacy', 'fallback', 'hebrew',
    'smart', 'ensemble', 'basic', 'auto'
]

# ============================================================================
# LANGUAGE CONSTANTS
# ============================================================================

LANGUAGE_CODES = {
    'english': ['en', 'eng', 'english'],
    'hebrew': ['he', 'heb', 'hebrew', 'iw'],
    'spanish': ['es', 'spa', 'spanish'],
    'french': ['fr', 'fra', 'french'],
    'german': ['de', 'deu', 'german'],
    'italian': ['it', 'ita', 'italian'],
    'portuguese': ['pt', 'por', 'portuguese'],
    'russian': ['ru', 'rus', 'russian'],
    'chinese': ['zh', 'chi', 'chinese'],
    'japanese': ['ja', 'jpn', 'japanese'],
    'korean': ['ko', 'kor', 'korean'],
    'arabic': ['ar', 'ara', 'arabic']
}

# Reverse mapping for quick lookup
LANGUAGE_CODE_LOOKUP = {}
for lang, codes in LANGUAGE_CODES.items():
    for code in codes:
        LANGUAGE_CODE_LOOKUP[code.lower()] = lang

SUPPORTED_LANGUAGES = list(LANGUAGE_CODES.keys())

# Language-specific settings
LANGUAGE_SETTINGS = {
    'english': {
        'default_stemmer': 'porter',
        'stopwords_available': True,
        'right_to_left': False,
        'complex_morphology': False
    },
    'hebrew': {
        'default_stemmer': 'hebrew_custom',
        'stopwords_available': True,
        'right_to_left': True,
        'complex_morphology': True,
        'prefix_stripping': True,
        'suffix_stripping': True
    },
    'arabic': {
        'default_stemmer': 'arabic_custom',
        'stopwords_available': True,
        'right_to_left': True,
        'complex_morphology': True
    }
}

# ============================================================================
# NLP PROCESSING CONSTANTS
# ============================================================================

NLP_PROCESSORS = [
    'nltk', 'spacy', 'hebrew', 'basic', 'smart', 'auto'
]

STEMMING_ALGORITHMS = {
    'english': ['porter', 'snowball', 'lancaster'],
    'hebrew': ['hebrew_custom'],
    'basic': ['suffix_removal']
}

# Common English stopwords (basic set)
BASIC_ENGLISH_STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'will', 'with', 'i', 'you', 'we', 'they', 'this',
    'but', 'not', 'or', 'have', 'had', 'what', 'when', 'where', 'who',
    'would', 'could', 'should', 'can', 'may', 'might', 'must', 'shall',
    'do', 'did', 'does', 'done', 'go', 'went', 'gone', 'get', 'got',
    'make', 'made', 'see', 'saw', 'seen', 'come', 'came', 'take', 'took'
}

# Common Hebrew stopwords (basic set)
BASIC_HEBREW_STOPWORDS = {
    'של', 'את', 'על', 'אל', 'זה', 'זו', 'זאת', 'אני', 'אתה', 'אתם', 'אתן',
    'היא', 'הוא', 'הם', 'הן', 'אנחנו', 'אנו', 'יש', 'אין', 'היה', 'היתה',
    'היו', 'הייתי', 'הייתה', 'היינו', 'הייתם', 'גם', 'כל', 'כמו', 'או',
    'אבל', 'רק', 'עוד', 'פה', 'שם', 'כאן', 'שלא', 'לא', 'עם', 'לפני',
    'אחרי', 'בתוך', 'מתוך', 'אצל', 'ליד', 'מול', 'תחת', 'מעל', 'בין'
}

STOPWORDS_BY_LANGUAGE = {
    'english': BASIC_ENGLISH_STOPWORDS,
    'hebrew': BASIC_HEBREW_STOPWORDS
}

# ============================================================================
# EXTERNAL LIBRARY CONSTANTS
# ============================================================================

EXTERNAL_LIBRARIES = {
    'required': ['pandas', 'numpy'],
    'optional_basic': ['openpyxl'],  # For Excel support
    'optional_advanced': ['nltk', 'textblob', 'spacy'],
    'optional_specialized': ['scikit-learn', 'matplotlib', 'seaborn']
}

LIBRARY_IMPORT_NAMES = {
    'pandas': 'pd',
    'numpy': 'np',
    'matplotlib.pyplot': 'plt',
    'seaborn': 'sns',
    'scikit-learn': 'sklearn'
}

# Library-specific settings
NLTK_REQUIRED_DATA = [
    'punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger',
    'vader_lexicon', 'omw-1.4'
]

SPACY_MODELS = {
    'english': 'en_core_web_sm',
    'german': 'de_core_news_sm',
    'french': 'fr_core_news_sm',
    'spanish': 'es_core_news_sm',
    'italian': 'it_core_news_sm',
    'portuguese': 'pt_core_news_sm',
    'chinese': 'zh_core_web_sm'
}

# ============================================================================
# PERFORMANCE CONSTANTS
# ============================================================================

DEFAULT_PERFORMANCE_SETTINGS = {
    'chunk_size': 1000,
    'max_workers': 4,
    'connection_timeout': 30,
    'max_cache_size': 1000,
    'batch_size': 100,
    'max_retries': 3
}

MEMORY_LIMITS = {
    'small_dataset': 1000,      # rows
    'medium_dataset': 10000,    # rows
    'large_dataset': 100000,    # rows
    'max_memory_mb': 1024       # MB
}

# ============================================================================
# VALIDATION CONSTANTS
# ============================================================================

VALID_PIPELINE_TYPES = [
    'basic', 'advanced_sync', 'advanced_async', 'auto'
]

VALID_OUTPUT_FORMATS = [
    'dict', 'dataframe', 'json', 'csv', 'excel'
]

VALID_LOG_LEVELS = [
    'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
]

# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_MESSAGES = {
    'file_not_found': "Data file not found: {path}",
    'unsupported_format': "Unsupported file format: {format}. Supported: {supported}",
    'column_not_found': "Column '{column}' not found in data. Available: {available}",
    'empty_data': "No data available for processing",
    'invalid_config': "Invalid configuration: {issues}",
    'library_missing': "Required library '{library}' not installed. Install with: pip install {library}",
    'connection_failed': "Failed to connect to data source: {error}",
    'processing_failed': "Processing failed: {error}",
    'invalid_language': "Unsupported language: {language}. Supported: {supported}",
    'threshold_invalid': "Invalid threshold values: positive must be greater than negative"
}

# ============================================================================
# REGULAR EXPRESSIONS
# ============================================================================

REGEX_PATTERNS = {
    'url': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'mention': r'@\w+',
    'hashtag': r'#\w+',
    'hebrew_chars': r'[\u0590-\u05FF]+',
    'arabic_chars': r'[\u0600-\u06FF]+',
    'chinese_chars': r'[\u4e00-\u9fff]+',
    'whitespace': r'\s+',
    'punctuation': r'[^\w\s]',
    'numbers': r'\d+',
    'word_boundaries': r'\b\w+\b'
}

# ============================================================================
# DEFAULT TEXT PATTERNS
# ============================================================================

COMMON_TEXT_PATTERNS = {
    'social_media': {
        'remove_mentions': True,
        'remove_hashtags': True,
        'remove_urls': True,
        'casual_language': True
    },
    'formal_text': {
        'preserve_punctuation': True,
        'preserve_capitalization': True,
        'remove_urls': True,
        'remove_emails': True
    },
    'academic': {
        'preserve_numbers': True,
        'preserve_special_terms': True,
        'careful_cleaning': True
    },
    'web_content': {
        'remove_html': True,
        'remove_urls': True,
        'remove_emails': True,
        'normalize_whitespace': True
    }
}

# ============================================================================
# FEATURE EXTRACTION CONSTANTS
# ============================================================================

DEFAULT_FEATURE_TYPES = [
    'tokens', 'clean_text', 'word_count', 'character_count',
    'sentence_count', 'vocabulary_richness', 'average_word_length'
]

ADVANCED_FEATURE_TYPES = [
    'stems', 'lemmas', 'pos_tags', 'named_entities', 'ngrams',
    'sentiment', 'emotion', 'readability', 'complexity'
]

NLP_FEATURE_TYPES = [
    'tokenization', 'stemming', 'lemmatization', 'pos_tagging',
    'ner', 'dependency_parsing', 'chunking'
]

# ============================================================================
# EXAM AND TESTING CONSTANTS
# ============================================================================

EXAM_SCENARIOS = {
    'basic_pipeline': {
        'required_components': ['DataLoaderClient', 'TextCleaningRepository', 'SentimentAnalysisRepository'],
        'test_data': "This is an amazing product! I love it so much.",
        'expected_features': ['sentiment_score', 'sentiment_label', 'cleaned_text']
    },
    'stemming_lemmatization': {
        'test_text': "The running dogs are quickly eating delicious foods",
        'expected_stems': ['run', 'dog', 'quick', 'eat', 'delici', 'food'],
        'expected_lemmas': ['running', 'dog', 'quickly', 'eat', 'delicious', 'food']
    },
    'hebrew_processing': {
        'test_text': "המוצר הזה מעולה ומומלץ בחום",
        'language': 'hebrew',
        'expected_features': ['hebrew_tokens', 'hebrew_stems', 'hebrew_sentiment']
    },
    'multi_analyzer': {
        'test_analyzers': ['vader', 'textblob', 'fallback'],
        'comparison_required': True,
        'ensemble_available': True
    }
}

# Quick reference for common exam requirements
EXAM_REQUIREMENTS = {
    'file_loading': SUPPORTED_FILE_FORMATS,
    'text_cleaning': list(DEFAULT_CLEANING_OPTIONS.keys()),
    'sentiment_analysis': SENTIMENT_ANALYZERS,
    'nlp_processing': NLP_PROCESSORS,
    'language_support': SUPPORTED_LANGUAGES,
    'pipeline_types': VALID_PIPELINE_TYPES
}