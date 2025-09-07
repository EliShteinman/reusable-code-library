# ============================================================================
# shared-utilities/data_science/__init__.py - FUTURE-PROOF GENERIC ARCHITECTURE
# ============================================================================
"""
Data Science utilities - GENERIC ARCHITECTURE
Future-proof design for any exam scenario with multiple library support
"""

# Import original components (backward compatibility)
from .data_loader import UniversalDataLoader
from .text_cleaner import TextCleaner
from .text_analyzer import TextAnalyzer
from .sentiment_analyzer import SentimentAnalyzer

# Import new generic architecture
from .text_processing_base import (
    SentimentAnalyzerBase,
    TextProcessorBase,
    ProcessorFactory,
    ProcessingConfig
)

# Import multiple implementations
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
    # Original components (backward compatibility)
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

    # Quick pipeline functions (updated)
    'quick_text_analysis_pipeline',
    'sentiment_analysis_pipeline',
    'text_cleaning_pipeline',
    'create_exam_safe_pipeline'
]


# ============================================================================
# Updated Pipeline Functions - Exam Safe
# ============================================================================

def quick_text_analysis_pipeline(file_path: str = None,
                                 data=None,
                                 text_column: str = None,
                                 category_column: str = None,
                                 sentiment_analyzer: str = "auto",
                                 text_processor: str = "auto",
                                 config: ProcessingConfig = None):
    """
    Complete text analysis pipeline with flexible library support.

    Args:
        file_path: Path to data file (optional if data provided)
        data: Pre-loaded data (DataFrame or list of dicts)
        text_column: Name of text column
        category_column: Optional category column for grouping
        sentiment_analyzer: Analyzer to use ("auto", "vader", "textblob", etc.)
        text_processor: Processor to use ("auto", "nltk", "spacy", etc.)
        config: Processing configuration

    Returns:
        Dict with cleaned data, analysis report, and info
    """
    try:
        # Use configuration if provided
        if config:
            sentiment_analyzer = config.sentiment_analyzer
            text_processor = config.text_processor

        # 1. Load data if needed
        if data is None:
            if file_path is None:
                raise ValueError("Either file_path or data must be provided")
            loader = UniversalDataLoader()
            df = loader.load_data(file_path)
        else:
            import pandas as pd
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data.copy()

        # Auto-detect text column if not specified
        if text_column is None:
            text_columns = [col for col in df.columns if df[col].dtype == 'object']
            if text_columns:
                text_column = text_columns[0]
            else:
                raise ValueError("No text column found or specified")

        # 2. Clean text using smart processor
        processor = ProcessorFactory.create_text_processor(text_processor)

        # Clean the text column
        df_clean = df.copy()
        df_clean[text_column] = df_clean[text_column].astype(str).apply(
            lambda x: processor.clean_text(x,
                                           remove_urls=True,
                                           remove_punctuation=True,
                                           to_lowercase=True)
        )

        # Remove empty texts
        df_clean = df_clean[df_clean[text_column].str.strip() != '']

        # 3. Analyze sentiment using flexible analyzer
        sentiment_analyzer_obj = ProcessorFactory.create_sentiment_analyzer(sentiment_analyzer)

        sentiment_results = []
        for text in df_clean[text_column]:
            result = sentiment_analyzer_obj.analyze_sentiment(text)
            sentiment_results.append(result)

        # Add sentiment columns
        df_analyzed = df_clean.copy()
        df_analyzed['sentiment_score'] = [r['compound'] for r in sentiment_results]
        df_analyzed['sentiment_label'] = [r['label'] for r in sentiment_results]
        df_analyzed['sentiment_confidence'] = [r['confidence'] for r in sentiment_results]

        # 4. Text analysis using analyzer
        analyzer = TextAnalyzer()
        report = analyzer.generate_summary_report(df_analyzed, text_column, category_column)

        # 5. Add processing info
        processing_info = {
            'sentiment_analyzer_used': sentiment_results[0].get('analyzer', 'unknown') if sentiment_results else 'none',
            'text_processor_used': text_processor,
            'original_rows': len(df),
            'cleaned_rows': len(df_clean),
            'final_rows': len(df_analyzed),
            'available_analyzers': get_available_sentiment_analyzers(),
            'available_processors': get_available_text_processors()
        }

        return {
            'cleaned_data': df_analyzed,
            'analysis_report': report,
            'processing_info': processing_info,
            'sentiment_results': sentiment_results
        }

    except Exception as e:
        # Fallback to basic processing
        logger.warning(f"Advanced pipeline failed: {e}, falling back to basic processing")
        return _fallback_pipeline(file_path, data, text_column, category_column)


def sentiment_analysis_pipeline(df,
                                text_column: str,
                                analyzer: str = "auto",
                                add_detailed: bool = True,
                                language: str = None):
    """
    Flexible sentiment analysis pipeline.

    Args:
        df: DataFrame with text data
        text_column: Name of text column
        analyzer: Sentiment analyzer to use
        add_detailed: Whether to add detailed scores
        language: Text language hint

    Returns:
        DataFrame with sentiment analysis results
    """
    try:
        # Create analyzer based on preference
        if analyzer == "auto":
            sentiment_analyzer = SmartSentimentAnalyzer()
        else:
            sentiment_analyzer = ProcessorFactory.create_sentiment_analyzer(analyzer)

        df_result = df.copy()

        # Analyze sentiment for each text
        sentiment_results = []
        for text in df_result[text_column]:
            if language:
                result = sentiment_analyzer.analyze_sentiment(str(text), language=language)
            else:
                result = sentiment_analyzer.analyze_sentiment(str(text))
            sentiment_results.append(result)

        # Add basic sentiment columns
        df_result['sentiment_score'] = [r['compound'] for r in sentiment_results]
        df_result['sentiment_label'] = [r['label'] for r in sentiment_results]
        df_result['sentiment_confidence'] = [r['confidence'] for r in sentiment_results]

        # Add detailed scores if requested
        if add_detailed:
            df_result['sentiment_positive'] = [r['positive'] for r in sentiment_results]
            df_result['sentiment_negative'] = [r['negative'] for r in sentiment_results]
            df_result['sentiment_neutral'] = [r['neutral'] for r in sentiment_results]
            df_result['analyzer_used'] = [r.get('analyzer', 'unknown') for r in sentiment_results]

        return df_result

    except Exception as e:
        logger.error(f"Sentiment analysis pipeline failed: {e}")
        # Fallback to original implementation
        original_analyzer = SentimentAnalyzer()
        return original_analyzer.analyze_dataframe(df, text_column, add_detailed)


def text_cleaning_pipeline(df,
                           text_columns: list,
                           processor: str = "auto",
                           language: str = None,
                           **cleaning_options):
    """
    Flexible text cleaning pipeline.

    Args:
        df: DataFrame with text data
        text_columns: List of column names to clean
        processor: Text processor to use
        language: Text language
        **cleaning_options: Options for text cleaning

    Returns:
        DataFrame with cleaned text columns
    """
    try:
        # Create processor
        if processor == "auto":
            text_processor = SmartTextProcessor()
        else:
            text_processor = ProcessorFactory.create_text_processor(processor)

        df_clean = df.copy()

        # Clean each text column
        for col in text_columns:
            if col in df_clean.columns:
                # Add language to cleaning options if specified
                if language:
                    cleaning_options['language'] = language

                df_clean[col] = df_clean[col].astype(str).apply(
                    lambda x: text_processor.clean_text(x, **cleaning_options)
                )

        # Remove empty texts if requested
        if cleaning_options.get('remove_empty', True):
            mask = True
            for col in text_columns:
                if col in df_clean.columns:
                    mask = mask & (df_clean[col].str.strip() != '')
            df_clean = df_clean[mask]

        return df_clean

    except Exception as e:
        logger.error(f"Text cleaning pipeline failed: {e}")
        # Fallback to original implementation
        cleaner = TextCleaner()
        return cleaner.clean_dataframe(df, text_columns, **cleaning_options)


def create_exam_safe_pipeline(preferred_sentiment: str = None,
                              preferred_processor: str = None):
    """
    Create an exam-safe pipeline that works even if libraries are missing.

    Args:
        preferred_sentiment: Preferred sentiment analyzer
        preferred_processor: Preferred text processor

    Returns:
        Configuration that guarantees to work
    """
    try:
        # Test what's available
        available_sentiment = get_available_sentiment_analyzers()
        available_processors = get_available_text_processors()

        # Choose best available options
        sentiment_choice = "fallback"  # Always available
        if preferred_sentiment and preferred_sentiment in available_sentiment:
            sentiment_choice = preferred_sentiment
        elif "vader" in available_sentiment:
            sentiment_choice = "vader"
        elif "textblob" in available_sentiment:
            sentiment_choice = "textblob"

        processor_choice = "basic"  # Always available
        if preferred_processor and preferred_processor in available_processors:
            processor_choice = preferred_processor
        elif "nltk" in available_processors:
            processor_choice = "nltk"
        elif "spacy" in available_processors:
            processor_choice = "spacy"

        config = ProcessingConfig(
            sentiment_analyzer=sentiment_choice,
            text_processor=processor_choice,
            fallback_enabled=True,
            exam_safe=True
        )

        logger.info(f"Exam-safe pipeline: sentiment={sentiment_choice}, processor={processor_choice}")
        return config

    except Exception as e:
        logger.warning(f"Error creating exam-safe pipeline: {e}")
        # Ultimate fallback
        return ProcessingConfig.exam_safe_config()


def _fallback_pipeline(file_path=None, data=None, text_column=None, category_column=None):
    """Fallback pipeline using original components."""
    try:
        # Load data
        if data is None:
            loader = UniversalDataLoader()
            df = loader.load_data(file_path)
        else:
            import pandas as pd
            df = pd.DataFrame(data) if isinstance(data, list) else data.copy()

        # Auto-detect text column
        if text_column is None:
            text_columns = [col for col in df.columns if df[col].dtype == 'object']
            text_column = text_columns[0] if text_columns else df.columns[0]

        # Clean text
        cleaner = TextCleaner()
        df_clean = cleaner.clean_dataframe(df, [text_column])
        df_clean = cleaner.remove_empty_texts(df_clean, [text_column])

        # Analyze sentiment
        sentiment_analyzer = SentimentAnalyzer()
        df_analyzed = sentiment_analyzer.analyze_dataframe(df_clean, text_column)

        # Generate report
        analyzer = TextAnalyzer()
        report = analyzer.generate_summary_report(df_analyzed, text_column, category_column)

        return {
            'cleaned_data': df_analyzed,
            'analysis_report': report,
            'processing_info': {
                'sentiment_analyzer_used': 'fallback',
                'text_processor_used': 'basic',
                'original_rows': len(df),
                'final_rows': len(df_analyzed),
                'fallback_mode': True
            }
        }

    except Exception as e:
        logger.error(f"Even fallback pipeline failed: {e}")
        return {
            'error': str(e),
            'processing_info': {'failed': True}
        }


# ============================================================================
# Advanced Feature Extraction Functions
# ============================================================================

def extract_comprehensive_features(text: str,
                                   language: str = "auto",
                                   include_sentiment: bool = True,
                                   include_stems: bool = True,
                                   include_lemmas: bool = True,
                                   include_roots: bool = True) -> Dict[str, Any]:
    """
    Extract comprehensive text features using best available tools.

    Args:
        text: Input text
        language: Text language ("auto" for detection)
        include_sentiment: Whether to include sentiment analysis
        include_stems: Whether to include stems
        include_lemmas: Whether to include lemmas
        include_roots: Whether to include roots

    Returns:
        Dictionary with all extracted features
    """
    try:
        features = {}

        # Language detection if needed
        if language == "auto":
            # Simple language detection
            if re.search(r'[\u0590-\u05FF]', text):
                language = "hebrew"
            else:
                language = "english"

        features['detected_language'] = language

        # Get best processors
        text_processor = SmartTextProcessor()

        # Basic text features
        features['char_count'] = len(text)
        features['word_count'] = len(text.split())
        features['sentence_count'] = len(re.split(r'[.!?]+', text))

        # Tokenization
        tokens = text_processor.tokenize(text)
        features['tokens'] = tokens
        features['token_count'] = len(tokens)

        # Remove stopwords
        clean_tokens = text_processor.remove_stopwords(tokens, language)
        features['clean_tokens'] = clean_tokens
        features['clean_token_count'] = len(clean_tokens)

        # Stemming, Lemmatization, Root extraction
        if include_stems:
            features['stems'] = text_processor.extract_stems(text)
            features['unique_stems'] = list(set(features['stems']))

        if include_lemmas:
            features['lemmas'] = text_processor.extract_lemmas(text)
            features['unique_lemmas'] = list(set(features['lemmas']))

        if include_roots:
            features['roots'] = text_processor.extract_roots(text)
            features['unique_roots'] = list(set(features['roots']))

        # Sentiment analysis
        if include_sentiment:
            sentiment_analyzer = SmartSentimentAnalyzer()
            sentiment = sentiment_analyzer.analyze_sentiment(text, language)
            features['sentiment'] = sentiment

        # Additional linguistic features
        features['avg_word_length'] = sum(len(word) for word in tokens) / len(tokens) if tokens else 0
        features['punctuation_count'] = sum(1 for char in text if char in string.punctuation)
        features['uppercase_count'] = sum(1 for char in text if char.isupper())
        features['digit_count'] = sum(1 for char in text if char.isdigit())

        return features

    except Exception as e:
        logger.error(f"Feature extraction failed: {e}")
        return {'error': str(e), 'text_length': len(text) if text else 0}


def analyze_text_with_multiple_tools(text: str,
                                     sentiment_analyzers: List[str] = None,
                                     text_processors: List[str] = None) -> Dict[str, Any]:
    """
    Analyze text with multiple tools for comparison and robustness.

    Args:
        text: Input text
        sentiment_analyzers: List of sentiment analyzers to use
        text_processors: List of text processors to use

    Returns:
        Dictionary with results from all tools
    """
    results = {
        'input_text': text,
        'sentiment_analysis': {},
        'text_processing': {},
        'consensus': {}
    }

    # Default analyzers if not specified
    if sentiment_analyzers is None:
        sentiment_analyzers = ["vader", "textblob", "fallback"]

    if text_processors is None:
        text_processors = ["nltk", "spacy", "basic"]

    # Sentiment analysis with multiple tools
    sentiment_results = []
    for analyzer_name in sentiment_analyzers:
        try:
            analyzer = ProcessorFactory.create_sentiment_analyzer(analyzer_name)
            result = analyzer.analyze_sentiment(text)
            results['sentiment_analysis'][analyzer_name] = result
            sentiment_results.append(result)
        except Exception as e:
            results['sentiment_analysis'][analyzer_name] = {'error': str(e)}

    # Text processing with multiple tools
    for processor_name in text_processors:
        try:
            processor = ProcessorFactory.create_text_processor(processor_name)
            result = {
                'tokens': processor.tokenize(text),
                'stems': processor.extract_stems(text),
                'lemmas': processor.extract_lemmas(text),
                'roots': processor.extract_roots(text)
            }
            results['text_processing'][processor_name] = result
        except Exception as e:
            results['text_processing'][processor_name] = {'error': str(e)}

    # Calculate consensus
    if sentiment_results:
        # Average sentiment scores
        compounds = [r['compound'] for r in sentiment_results if 'compound' in r]
        if compounds:
            results['consensus']['avg_sentiment'] = sum(compounds) / len(compounds)

        # Majority vote on labels
        labels = [r['label'] for r in sentiment_results if 'label' in r]
        if labels:
            from collections import Counter
            label_counts = Counter(labels)
            results['consensus']['majority_label'] = label_counts.most_common(1)[0][0]

    return results


# ============================================================================
# Exam Scenario Handlers
# ============================================================================

def handle_unknown_library_scenario(required_library: str, task: str, text: str):
    """
    Handle scenarios where exam asks for specific library that might not be available.

    Args:
        required_library: Library name mentioned in exam (e.g., "textblob", "spacy")
        task: Task to perform (e.g., "sentiment", "stemming", "lemmatization")
        text: Input text

    Returns:
        Result using best available alternative
    """
    logger.info(f"Exam scenario: {required_library} requested for {task}")

    try:
        # Try to use the requested library first
        if task == "sentiment":
            if required_library.lower() in get_available_sentiment_analyzers():
                analyzer = ProcessorFactory.create_sentiment_analyzer(required_library.lower())
                return analyzer.analyze_sentiment(text)
            else:
                # Fallback with notification
                logger.warning(f"{required_library} not available for sentiment, using fallback")
                analyzer = ProcessorFactory.create_sentiment_analyzer("auto")
                result = analyzer.analyze_sentiment(text)
                result['requested_library'] = required_library
                result['actual_library'] = result.get('analyzer', 'fallback')
                return result

        elif task in ["stemming", "lemmatization", "tokenization"]:
            if required_library.lower() in get_available_text_processors():
                processor = ProcessorFactory.create_text_processor(required_library.lower())
            else:
                logger.warning(f"{required_library} not available for {task}, using fallback")
                processor = ProcessorFactory.create_text_processor("auto")

            if task == "stemming":
                return processor.extract_stems(text)
            elif task == "lemmatization":
                return processor.extract_lemmas(text)
            elif task == "tokenization":
                return processor.tokenize(text)

        else:
            raise ValueError(f"Unknown task: {task}")

    except Exception as e:
        logger.error(f"Failed to handle exam scenario: {e}")
        # Ultimate fallback
        if task == "sentiment":
            return FallbackSentimentAnalyzer().analyze_sentiment(text)
        else:
            processor = BasicTextProcessor()
            if task == "stemming":
                return processor.extract_stems(text)
            elif task == "lemmatization":
                return processor.extract_lemmas(text)
            elif task == "tokenization":
                return processor.tokenize(text)


def exam_mode_analysis(text: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform analysis based on exam requirements with automatic fallbacks.

    Args:
        text: Input text
        requirements: Dict specifying exam requirements
                     e.g., {'sentiment': 'vader', 'stemming': 'nltk', 'language': 'hebrew'}

    Returns:
        Analysis results meeting requirements or best available alternatives
    """
    results = {
        'requirements': requirements,
        'results': {},
        'alternatives_used': {},
        'available_tools': {
            'sentiment_analyzers': get_available_sentiment_analyzers(),
            'text_processors': get_available_text_processors()
        }
    }

    # Handle sentiment analysis requirement
    if 'sentiment' in requirements:
        required_analyzer = requirements['sentiment']
        try:
            result = handle_unknown_library_scenario(required_analyzer, "sentiment", text)
            results['results']['sentiment'] = result
            if result.get('actual_library') != required_analyzer:
                results['alternatives_used']['sentiment'] = result.get('actual_library')
        except Exception as e:
            results['results']['sentiment'] = {'error': str(e)}

    # Handle stemming requirement
    if 'stemming' in requirements:
        required_processor = requirements['stemming']
        try:
            stems = handle_unknown_library_scenario(required_processor, "stemming", text)
            results['results']['stems'] = stems
        except Exception as e:
            results['results']['stems'] = {'error': str(e)}

    # Handle lemmatization requirement
    if 'lemmatization' in requirements:
        required_processor = requirements['lemmatization']
        try:
            lemmas = handle_unknown_library_scenario(required_processor, "lemmatization", text)
            results['results']['lemmas'] = lemmas
        except Exception as e:
            results['results']['lemmas'] = {'error': str(e)}

    # Handle language-specific requirements
    if 'language' in requirements:
        language = requirements['language']
        try:
            # Use language-appropriate tools
            if language.lower() in ['hebrew', 'he']:
                processor = ProcessorFactory.create_text_processor("hebrew")
                analyzer = ProcessorFactory.create_sentiment_analyzer("hebrew")
            else:
                processor = ProcessorFactory.create_text_processor("auto")
                analyzer = ProcessorFactory.create_sentiment_analyzer("auto")

            results['results']['language_specific'] = {
                'tokens': processor.tokenize(text),
                'roots': processor.extract_roots(text),
                'sentiment': analyzer.analyze_sentiment(text)
            }
        except Exception as e:
            results['results']['language_specific'] = {'error': str(e)}

    return results


# Log initialization
import logging

logger = logging.getLogger(__name__)
logger.info("Data Science utilities with generic architecture initialized")
logger.info(f"Available sentiment analyzers: {get_available_sentiment_analyzers()}")
logger.info(f"Available text processors: {get_available_text_processors()}")