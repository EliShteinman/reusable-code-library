# ============================================================================
# shared-utilities/data_science/__init__.py - FIXED VERSION
# ============================================================================
"""
Data Science utilities - COMPLETE ARCHITECTURE
Basic + Generic implementations with proper imports
"""

import logging

logger = logging.getLogger(__name__)

# Import basic components (always work)
from .data_loader import UniversalDataLoader
from .text_cleaner import TextCleaner
from .text_analyzer import TextAnalyzer
from .sentiment_analyzer import SentimentAnalyzer

# Import generic architecture (advanced features)
from .text_processing_base import (
    SentimentAnalyzerBase,
    TextProcessorBase,
    ProcessorFactory,
    ProcessingConfig
)

# Import all implementations
from .sentiment_implementations import (
    VADERSentimentAnalyzer,
    TextBlobSentimentAnalyzer,
    SpacySentimentAnalyzer,
    FallbackSentimentAnalyzer,
    HebrewSentimentAnalyzer,
    SmartSentimentAnalyzer,
    EnsembleSentimentAnalyzer,
    get_best_available_sentiment_analyzer,
    analyze_sentiment_with_fallback,
    get_available_sentiment_analyzers
)

from .text_processing_implementations import (
    NLTKTextProcessor,
    SpaCyTextProcessor,
    HebrewTextProcessor,
    BasicTextProcessor,
    SmartTextProcessor,
    get_best_available_text_processor,
    extract_text_features,
    get_available_text_processors
)

__all__ = [
    # Basic components (always available)
    'UniversalDataLoader',
    'TextCleaner',
    'TextAnalyzer',
    'SentimentAnalyzer',

    # Generic base classes
    'SentimentAnalyzerBase',
    'TextProcessorBase',
    'ProcessorFactory',
    'ProcessingConfig',

    # Sentiment implementations
    'VADERSentimentAnalyzer',
    'TextBlobSentimentAnalyzer',
    'SpacySentimentAnalyzer',
    'FallbackSentimentAnalyzer',
    'HebrewSentimentAnalyzer',
    'SmartSentimentAnalyzer',
    'EnsembleSentimentAnalyzer',

    # Text processing implementations
    'NLTKTextProcessor',
    'SpaCyTextProcessor',
    'HebrewTextProcessor',
    'BasicTextProcessor',
    'SmartTextProcessor',

    # Convenience functions
    'get_best_available_sentiment_analyzer',
    'analyze_sentiment_with_fallback',
    'get_available_sentiment_analyzers',
    'get_best_available_text_processor',
    'extract_text_features',
    'get_available_text_processors',

    # Pipeline functions
    'quick_text_analysis_pipeline',
    'sentiment_analysis_pipeline',
    'text_cleaning_pipeline',
    'create_exam_safe_pipeline'
]


# ============================================================================
# SIMPLE PIPELINE FUNCTIONS (Fixed)
# ============================================================================

def quick_text_analysis_pipeline(file_path: str,
                                 text_column: str,
                                 category_column: str = None):
    """
    Complete text analysis pipeline - EXAM SAFE VERSION.

    Args:
        file_path: Path to data file
        text_column: Name of text column
        category_column: Optional category column for grouping

    Returns:
        Dict with cleaned data, analysis report, and info
    """
    try:
        # 1. Load data
        loader = UniversalDataLoader()
        df = loader.load_data(file_path)

        # 2. Clean text
        cleaner = TextCleaner()
        df_clean = cleaner.clean_dataframe(df, [text_column])
        df_clean = cleaner.remove_empty_texts(df_clean, [text_column])

        # 3. Analyze sentiment - try advanced first, fallback to basic
        try:
            sentiment_analyzer = SmartSentimentAnalyzer()
            logger.info("Using SmartSentimentAnalyzer")
        except:
            sentiment_analyzer = SentimentAnalyzer()
            logger.info("Using basic SentimentAnalyzer")

        df_analyzed = sentiment_analyzer.analyze_dataframe(df_clean, text_column)

        # 4. Text analysis
        analyzer = TextAnalyzer()
        report = analyzer.generate_summary_report(df_analyzed, text_column, category_column)

        return {
            'cleaned_data': df_analyzed,
            'analysis_report': report,
            'processing_info': {
                'original_rows': len(df),
                'final_rows': len(df_analyzed),
                'analyzer_used': type(sentiment_analyzer).__name__
            }
        }

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


def sentiment_analysis_pipeline(df,
                                text_column: str,
                                analyzer: str = "auto"):
    """
    Flexible sentiment analysis pipeline.

    Args:
        df: DataFrame with text data
        text_column: Name of text column
        analyzer: Sentiment analyzer to use ("auto", "vader", "textblob", etc.)

    Returns:
        DataFrame with sentiment analysis results
    """
    try:
        if analyzer == "auto":
            # Try smart analyzer first
            try:
                sentiment_analyzer = SmartSentimentAnalyzer()
                logger.info("Using SmartSentimentAnalyzer")
            except:
                sentiment_analyzer = SentimentAnalyzer()
                logger.info("Using basic SentimentAnalyzer")
        else:
            # Try specific analyzer
            try:
                sentiment_analyzer = ProcessorFactory.create_sentiment_analyzer(analyzer)
                logger.info(f"Using {analyzer} analyzer")
            except:
                sentiment_analyzer = SentimentAnalyzer()
                logger.warning(f"{analyzer} not available, using basic analyzer")

        return sentiment_analyzer.analyze_dataframe(df, text_column)

    except Exception as e:
        logger.error(f"Sentiment pipeline failed: {e}")
        # Ultimate fallback
        basic_analyzer = SentimentAnalyzer()
        return basic_analyzer.analyze_dataframe(df, text_column)


def text_cleaning_pipeline(df,
                           text_columns: list,
                           **cleaning_options):
    """
    Flexible text cleaning pipeline.

    Args:
        df: DataFrame with text data
        text_columns: List of column names to clean
        **cleaning_options: Options for text cleaning

    Returns:
        DataFrame with cleaned text columns
    """
    try:
        # Try smart processor first
        try:
            processor = SmartTextProcessor()
            logger.info("Using SmartTextProcessor")

            df_clean = df.copy()
            for col in text_columns:
                if col in df_clean.columns:
                    df_clean[col] = df_clean[col].astype(str).apply(
                        lambda x: processor.clean_text(x, **cleaning_options)
                    )
            return df_clean

        except:
            # Fallback to basic cleaner
            cleaner = TextCleaner()
            logger.info("Using basic TextCleaner")
            return cleaner.clean_dataframe(df, text_columns, **cleaning_options)

    except Exception as e:
        logger.error(f"Cleaning pipeline failed: {e}")
        raise


def create_exam_safe_pipeline(preferred_sentiment: str = None):
    """
    Create an exam-safe configuration that works even if libraries are missing.

    Args:
        preferred_sentiment: Preferred sentiment analyzer

    Returns:
        Configuration that guarantees to work
    """
    try:
        # Test what's available
        available_sentiment = get_available_sentiment_analyzers()

        # Choose best available options
        sentiment_choice = "fallback"  # Always available
        if preferred_sentiment and preferred_sentiment in available_sentiment:
            sentiment_choice = preferred_sentiment
        elif "vader" in available_sentiment:
            sentiment_choice = "vader"
        elif "textblob" in available_sentiment:
            sentiment_choice = "textblob"

        config = ProcessingConfig(
            sentiment_analyzer=sentiment_choice,
            text_processor="auto",
            fallback_enabled=True,
            exam_safe=True
        )

        logger.info(f"Exam-safe pipeline: sentiment={sentiment_choice}")
        return config

    except Exception as e:
        logger.warning(f"Error creating exam-safe pipeline: {e}")
        # Ultimate fallback - just return basic config
        return ProcessingConfig.exam_safe_config() if hasattr(ProcessingConfig, 'exam_safe_config') else None


# ============================================================================
# EXAM HELPER FUNCTIONS
# ============================================================================

def quick_sentiment_check(text: str, analyzer: str = "auto"):
    """
    Quick sentiment check for single text - perfect for exam demos.

    Args:
        text: Text to analyze
        analyzer: Analyzer to use

    Returns:
        Sentiment result
    """
    try:
        if analyzer == "auto":
            sentiment_analyzer = get_best_available_sentiment_analyzer()
        else:
            sentiment_analyzer = ProcessorFactory.create_sentiment_analyzer(analyzer)

        return sentiment_analyzer.analyze_sentiment(text)

    except Exception as e:
        logger.warning(f"Quick check failed: {e}, using basic analyzer")
        basic_analyzer = SentimentAnalyzer()
        return {
            'compound': basic_analyzer.get_sentiment_score(text),
            'label': basic_analyzer.get_sentiment_label(text),
            'analyzer': 'basic_fallback'
        }


def extract_all_features(text: str, language: str = "auto"):
    """
    Extract all possible features from text - great for exam demonstrations.

    Args:
        text: Input text
        language: Text language

    Returns:
        Dictionary with all features
    """
    try:
        features = {}

        # Try smart processor
        processor = get_best_available_text_processor()

        # Basic features
        features['tokens'] = processor.tokenize(text)
        features['stems'] = processor.extract_stems(text)
        features['lemmas'] = processor.extract_lemmas(text)
        features['roots'] = processor.extract_roots(text)

        # Sentiment
        sentiment_analyzer = get_best_available_sentiment_analyzer()
        features['sentiment'] = sentiment_analyzer.analyze_sentiment(text)

        return features

    except Exception as e:
        logger.error(f"Feature extraction failed: {e}")
        # Basic fallback
        return {
            'tokens': text.split(),
            'error': str(e)
        }


# Log initialization
logger.info("Data Science utilities initialized successfully")
logger.info(f"Available sentiment analyzers: {get_available_sentiment_analyzers()}")
logger.info(f"Available text processors: {get_available_text_processors()}")