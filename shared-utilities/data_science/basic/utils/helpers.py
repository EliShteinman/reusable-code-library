# ============================================================================
# shared-utilities/data_science/utils/helpers.py
# ============================================================================
"""
Helper Functions - Utility functions and pipeline builders
Common functionality shared across basic and advanced components
"""

import logging
from typing import Dict, Any, List, Optional, Union
import pandas as pd

logger = logging.getLogger(__name__)


# ============================================================================
# PIPELINE BUILDERS
# ============================================================================

def create_basic_pipeline(data_source: str = None,
                          text_column: str = None,
                          **pipeline_options) -> Dict[str, Any]:
    """
    Create a basic data science pipeline using only basic components.

    Args:
        data_source: Path to data file or DataFrame
        text_column: Name of text column to process
        **pipeline_options: Pipeline configuration options

    Returns:
        Pipeline configuration and components
    """
    from ..basic.clients import DataLoaderClient, TextProcessorClient
    from ..basic.repositories import (
        TextCleaningRepository,
        TextAnalysisRepository,
        SentimentAnalysisRepository
    )

    # Initialize basic components
    data_client = DataLoaderClient()
    text_client = TextProcessorClient()

    # Initialize repositories
    cleaning_repo = TextCleaningRepository(client=text_client)
    analysis_repo = TextAnalysisRepository()
    sentiment_repo = SentimentAnalysisRepository()

    pipeline_config = {
        'type': 'basic',
        'components': {
            'data_client': data_client,
            'text_client': text_client,
            'cleaning_repo': cleaning_repo,
            'analysis_repo': analysis_repo,
            'sentiment_repo': sentiment_repo
        },
        'data_source': data_source,
        'text_column': text_column,
        'options': pipeline_options,
        'capabilities': [
            'file_loading', 'basic_text_cleaning', 'text_analysis',
            'basic_sentiment_analysis', 'statistics'
        ]
    }

    logger.info("Basic pipeline created successfully")
    return pipeline_config


def create_advanced_pipeline(data_source: str = None,
                             text_column: str = None,
                             mode: str = 'sync',
                             **pipeline_options) -> Dict[str, Any]:
    """
    Create an advanced data science pipeline with multi-library support.

    Args:
        data_source: Path to data file or DataFrame
        text_column: Name of text column to process
        mode: 'sync' or 'async' for operation mode
        **pipeline_options: Pipeline configuration options

    Returns:
        Pipeline configuration and components
    """
    try:
        # Import advanced components based on mode
        if mode == 'sync':
            from ..advanced.clients.sync import SentimentClient, NLPClient
            from ..advanced.repositories.sync import (
                AdvancedSentimentRepository, NLPRepository, HebrewRepository
            )
            client_suffix = 'sync'
        elif mode == 'async':
            from ..advanced.clients.async_ import AsyncSentimentClient, AsyncNLPClient
            from ..advanced.repositories.async_ import (
                AsyncSentimentRepository, AsyncNLPRepository, AsyncHebrewRepository
            )
            client_suffix = 'async'
        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'sync' or 'async'")

        # Also include basic components
        from ..basic.clients import DataLoaderClient

        # Initialize components
        data_client = DataLoaderClient()

        if mode == 'sync':
            sentiment_client = SentimentClient()
            nlp_client = NLPClient()

            sentiment_repo = AdvancedSentimentRepository(client=sentiment_client)
            nlp_repo = NLPRepository(client=nlp_client)
            hebrew_repo = HebrewRepository()
        else:
            sentiment_client = AsyncSentimentClient()
            nlp_client = AsyncNLPClient()

            sentiment_repo = AsyncSentimentRepository(client=sentiment_client)
            nlp_repo = AsyncNLPRepository(client=nlp_client)
            hebrew_repo = AsyncHebrewRepository()

        pipeline_config = {
            'type': 'advanced',
            'mode': mode,
            'components': {
                'data_client': data_client,
                'sentiment_client': sentiment_client,
                'nlp_client': nlp_client,
                'sentiment_repo': sentiment_repo,
                'nlp_repo': nlp_repo,
                'hebrew_repo': hebrew_repo
            },
            'data_source': data_source,
            'text_column': text_column,
            'options': pipeline_options,
            'capabilities': [
                'file_loading', 'multi_library_sentiment', 'stemming',
                'lemmatization', 'hebrew_processing', 'ensemble_analysis',
                f'{mode}_operations'
            ]
        }

        logger.info(f"Advanced {mode} pipeline created successfully")
        return pipeline_config

    except ImportError as e:
        logger.warning(f"Advanced components not available: {e}")
        logger.info("Falling back to basic pipeline")
        return create_basic_pipeline(data_source, text_column, **pipeline_options)


# ============================================================================
# SYSTEM CAPABILITIES
# ============================================================================

def get_system_capabilities() -> Dict[str, Any]:
    """
    Get comprehensive system capabilities and component availability.

    Returns:
        System capabilities information
    """
    capabilities = {
        'basic_components': True,  # Always available
        'advanced_sync': False,
        'advanced_async': False,
        'factory_pattern': False,
        'external_libraries': {}
    }

    # Test basic components
    try:
        from ..basic.clients import DataLoaderClient, TextProcessorClient
        from ..basic.repositories import (
            TextCleaningRepository, TextAnalysisRepository, SentimentAnalysisRepository
        )
        capabilities['basic_components'] = True
    except ImportError:
        capabilities['basic_components'] = False

    # Test advanced sync components
    try:
        from ..advanced.clients.sync import SentimentClient, NLPClient
        from ..advanced.repositories.sync import AdvancedSentimentRepository
        capabilities['advanced_sync'] = True
    except ImportError:
        pass

    # Test advanced async components
    try:
        from ..advanced.clients.async_ import AsyncSentimentClient
        capabilities['advanced_async'] = True
    except ImportError:
        pass

    # Test factory pattern
    try:
        from ..advanced.base import ProcessorFactory
        capabilities['factory_pattern'] = True
    except ImportError:
        pass

    # Test external libraries
    external_libs = ['nltk', 'textblob', 'spacy', 'pandas', 'numpy']
    for lib in external_libs:
        try:
            __import__(lib)
            capabilities['external_libraries'][lib] = True
        except ImportError:
            capabilities['external_libraries'][lib] = False

    # Add summary
    capabilities['summary'] = {
        'total_external_libs': len(capabilities['external_libraries']),
        'available_external_libs': sum(capabilities['external_libraries'].values()),
        'component_levels': []
    }

    if capabilities['basic_components']:
        capabilities['summary']['component_levels'].append('basic')
    if capabilities['advanced_sync']:
        capabilities['summary']['component_levels'].append('advanced_sync')
    if capabilities['advanced_async']:
        capabilities['summary']['component_levels'].append('advanced_async')

    return capabilities


# ============================================================================
# QUICK ANALYSIS FUNCTIONS
# ============================================================================

def quick_sentiment_check(text: str,
                          method: str = 'auto') -> Dict[str, Any]:
    """
    Quick sentiment analysis for single text with automatic fallback.

    Args:
        text: Text to analyze
        method: 'auto', 'basic', 'advanced', or specific analyzer name

    Returns:
        Sentiment analysis result
    """
    try:
        if method == 'auto':
            # Try advanced first, fallback to basic
            try:
                from ..advanced.clients.sync import SentimentClient
                client = SentimentClient()
                return client.analyze_single(text)
            except ImportError:
                method = 'basic'

        if method == 'basic':
            from ..basic.repositories import SentimentAnalysisRepository
            repo = SentimentAnalysisRepository()
            return repo.create_sentiment_analysis(
                data=pd.DataFrame([{'text': text}]),
                text_column='text'
            )['results'][0]

        elif method == 'advanced':
            from ..advanced.clients.sync import SentimentClient
            client = SentimentClient()
            return client.analyze_single(text)

        else:
            # Try specific analyzer through factory
            try:
                from ..advanced.base import ProcessorFactory
                analyzer = ProcessorFactory.create_sentiment_analyzer(method)
                return analyzer.analyze_sentiment(text)
            except:
                # Final fallback to basic
                return quick_sentiment_check(text, 'basic')

    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return {
            'compound': 0.0,
            'label': 'neutral',
            'confidence': 0.0,
            'error': str(e),
            'analyzer': 'error_fallback'
        }


def extract_all_features(text: str,
                         language: str = 'auto',
                         include_sentiment: bool = True,
                         include_nlp: bool = True) -> Dict[str, Any]:
    """
    Extract all available features from text using best available tools.

    Args:
        text: Text to analyze
        language: Language for processing ('auto' for detection)
        include_sentiment: Whether to include sentiment analysis
        include_nlp: Whether to include NLP features (stemming, lemmatization)

    Returns:
        Dictionary with all extracted features
    """
    features = {
        'input_text': text,
        'language': language,
        'timestamp': pd.Timestamp.now(),
        'features': {}
    }

    try:
        # Basic text processing
        from ..basic.clients import TextProcessorClient
        basic_client = TextProcessorClient()

        with basic_client.create_session(language if language != 'auto' else 'english') as session:
            # Basic features
            features['features']['tokens'] = session.tokenize(text)
            features['features']['clean_text'] = session.clean_text(text)
            features['features']['word_count'] = len(features['features']['tokens'])
            features['features']['text_stats'] = session.get_text_stats(text)

            if include_nlp:
                features['features']['stems'] = session.extract_stems(text)
                features['features']['tokens_no_stopwords'] = session.remove_stopwords(
                    features['features']['tokens']
                )

        # Advanced NLP features (if available)
        if include_nlp:
            try:
                from ..advanced.clients.sync import NLPClient
                nlp_client = NLPClient()

                with nlp_client.create_session() as nlp_session:
                    nlp_features = nlp_session.extract_all_features(text)
                    features['features'].update(nlp_features)

            except ImportError:
                logger.debug("Advanced NLP features not available")

        # Sentiment analysis
        if include_sentiment:
            sentiment_result = quick_sentiment_check(text)
            features['features']['sentiment'] = sentiment_result

        # Hebrew-specific features (if detected)
        if language in ['he', 'hebrew'] or (language == 'auto' and _is_hebrew_text(text)):
            try:
                from ..advanced.repositories.sync import HebrewRepository
                hebrew_repo = HebrewRepository()

                hebrew_features = hebrew_repo.create_hebrew_analysis(
                    data=pd.DataFrame([{'text': text}]),
                    text_column='text'
                )
                features['features']['hebrew'] = hebrew_features['results'][0]
                features['language'] = 'hebrew'

            except ImportError:
                logger.debug("Hebrew processing features not available")

        # Feature summary
        features['summary'] = {
            'total_features': len(features['features']),
            'feature_types': list(features['features'].keys()),
            'processing_successful': True
        }

    except Exception as e:
        logger.error(f"Feature extraction failed: {e}")
        features['summary'] = {
            'total_features': 0,
            'error': str(e),
            'processing_successful': False
        }

    return features


# ============================================================================
# PIPELINE EXECUTION FUNCTIONS
# ============================================================================

def execute_complete_pipeline(data_source: Union[str, pd.DataFrame],
                              text_column: str,
                              pipeline_type: str = 'auto',
                              category_column: str = None,
                              **options) -> Dict[str, Any]:
    """
    Execute a complete data science pipeline from data loading to analysis.

    Args:
        data_source: Path to data file or DataFrame
        text_column: Name of text column
        pipeline_type: 'basic', 'advanced_sync', 'advanced_async', or 'auto'
        category_column: Optional category column for grouping
        **options: Pipeline execution options

    Returns:
        Complete pipeline results
    """
    start_time = pd.Timestamp.now()

    try:
        # Determine pipeline type
        if pipeline_type == 'auto':
            capabilities = get_system_capabilities()
            if capabilities['advanced_sync']:
                pipeline_type = 'advanced_sync'
            elif capabilities['advanced_async']:
                pipeline_type = 'advanced_async'
            else:
                pipeline_type = 'basic'

        # Create pipeline
        if pipeline_type == 'basic':
            pipeline = create_basic_pipeline(
                data_source=data_source if isinstance(data_source, str) else None,
                text_column=text_column,
                **options
            )
        elif pipeline_type.startswith('advanced'):
            mode = 'async' if 'async' in pipeline_type else 'sync'
            pipeline = create_advanced_pipeline(
                data_source=data_source if isinstance(data_source, str) else None,
                text_column=text_column,
                mode=mode,
                **options
            )
        else:
            raise ValueError(f"Invalid pipeline type: {pipeline_type}")

        # Load data
        if isinstance(data_source, pd.DataFrame):
            df = data_source
        else:
            data_client = pipeline['components']['data_client']
            with data_client.connect(data_source) as conn:
                df = conn.load_data()

        # Execute pipeline steps
        results = {
            'pipeline_info': {
                'type': pipeline['type'],
                'mode': pipeline.get('mode', 'sync'),
                'capabilities': pipeline['capabilities'],
                'start_time': start_time,
                'data_source': data_source if isinstance(data_source, str) else 'DataFrame',
                'text_column': text_column,
                'category_column': category_column
            },
            'data_info': {
                'original_rows': len(df),
                'columns': list(df.columns),
                'text_column_exists': text_column in df.columns
            }
        }

        if text_column not in df.columns:
            raise ValueError(f"Text column '{text_column}' not found in data")

        # Text cleaning
        if pipeline['type'] == 'basic':
            cleaning_repo = pipeline['components']['cleaning_repo']
            cleaning_result = cleaning_repo.create_cleaning_operation(
                data=df,
                text_columns=[text_column]
            )
            cleaned_df = cleaning_result['cleaned_data']
            results['cleaning'] = cleaning_result
        else:
            # Advanced cleaning would go here
            cleaned_df = df.copy()
            results['cleaning'] = {'message': 'Advanced cleaning not implemented in this example'}

        # Sentiment analysis
        if pipeline['type'] == 'basic':
            sentiment_repo = pipeline['components']['sentiment_repo']
            sentiment_result = sentiment_repo.create_sentiment_analysis(
                data=cleaned_df,
                text_column=text_column
            )
            analyzed_df = sentiment_result['analyzed_data']
            results['sentiment'] = sentiment_result
        else:
            # Advanced sentiment would go here
            analyzed_df = cleaned_df.copy()
            results['sentiment'] = {'message': 'Advanced sentiment not implemented in this example'}

        # Text analysis
        if pipeline['type'] == 'basic':
            analysis_repo = pipeline['components']['analysis_repo']
            analysis_result = analysis_repo.create_text_analysis(
                data=analyzed_df,
                text_column=text_column,
                category_column=category_column
            )
            results['analysis'] = analysis_result

        # Final results
        end_time = pd.Timestamp.now()
        duration = (end_time - start_time).total_seconds()

        results['summary'] = {
            'total_duration_seconds': duration,
            'final_rows': len(analyzed_df),
            'processing_successful': True,
            'pipeline_type_used': pipeline['type'],
            'end_time': end_time
        }

        results['final_data'] = analyzed_df

        logger.info(f"Complete pipeline executed successfully in {duration:.2f}s")
        return results

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        return {
            'summary': {
                'processing_successful': False,
                'error': str(e),
                'pipeline_type_attempted': pipeline_type
            }
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _is_hebrew_text(text: str) -> bool:
    """Simple Hebrew text detection."""
    if not text:
        return False

    hebrew_chars = sum(1 for char in text if '\u0590' <= char <= '\u05FF')
    total_chars = len([char for char in text if char.isalpha()])

    return total_chars > 0 and hebrew_chars / total_chars > 0.3


def validate_data_science_setup() -> Dict[str, Any]:
    """
    Validate the entire data science setup and return status report.

    Returns:
        Comprehensive validation report
    """
    validation = {
        'timestamp': pd.Timestamp.now(),
        'overall_status': 'unknown',
        'components': {},
        'recommendations': []
    }

    try:
        # Test basic components
        basic_test = _test_basic_components()
        validation['components']['basic'] = basic_test

        # Test advanced components
        advanced_test = _test_advanced_components()
        validation['components']['advanced'] = advanced_test

        # Test external libraries
        lib_test = _test_external_libraries()
        validation['components']['external_libraries'] = lib_test

        # Determine overall status
        if basic_test['status'] == 'working':
            if advanced_test['status'] == 'working':
                validation['overall_status'] = 'excellent'
            elif lib_test['nltk'] or lib_test['textblob']:
                validation['overall_status'] = 'good'
            else:
                validation['overall_status'] = 'basic'
        else:
            validation['overall_status'] = 'error'

        # Generate recommendations
        validation['recommendations'] = _generate_recommendations(validation['components'])

    except Exception as e:
        validation['overall_status'] = 'error'
        validation['error'] = str(e)

    return validation


def _test_basic_components() -> Dict[str, Any]:
    """Test basic components functionality."""
    try:
        from ..basic.clients import DataLoaderClient, TextProcessorClient
        from ..basic.repositories import TextCleaningRepository

        # Test data loader
        data_client = DataLoaderClient()

        # Test text processor
        text_client = TextProcessorClient()
        test_result = text_client.test_connection()

        # Test repository
        cleaning_repo = TextCleaningRepository(client=text_client)

        return {
            'status': 'working',
            'data_client': True,
            'text_client': True,
            'text_client_details': test_result,
            'repositories': True
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def _test_advanced_components() -> Dict[str, Any]:
    """Test advanced components functionality."""
    result = {
        'status': 'not_available',
        'sync': False,
        'async': False,
        'factory': False
    }

    try:
        from ..advanced.clients.sync import SentimentClient
        result['sync'] = True
    except ImportError:
        pass

    try:
        from ..advanced.clients.async_ import AsyncSentimentClient
        result['async'] = True
    except ImportError:
        pass

    try:
        from ..advanced.base import ProcessorFactory
        result['factory'] = True
    except ImportError:
        pass

    if any([result['sync'], result['async'], result['factory']]):
        result['status'] = 'partial'
        if all([result['sync'], result['async'], result['factory']]):
            result['status'] = 'working'

    return result


def _test_external_libraries() -> Dict[str, bool]:
    """Test external library availability."""
    libraries = ['nltk', 'textblob', 'spacy', 'pandas', 'numpy']
    results = {}

    for lib in libraries:
        try:
            __import__(lib)
            results[lib] = True
        except ImportError:
            results[lib] = False

    return results


def _generate_recommendations(components: Dict[str, Any]) -> List[str]:
    """Generate setup recommendations based on component status."""
    recommendations = []

    # Basic components
    if components['basic']['status'] != 'working':
        recommendations.append("Fix basic components - these are required for all functionality")

    # External libraries
    ext_libs = components['external_libraries']
    if not ext_libs['nltk']:
        recommendations.append("Install NLTK for advanced text processing: pip install nltk")
    if not ext_libs['textblob']:
        recommendations.append("Install TextBlob for sentiment analysis: pip install textblob")
    if not ext_libs['spacy']:
        recommendations.append("Install spaCy for advanced NLP: pip install spacy")

    # Advanced components
    if components['advanced']['status'] == 'not_available':
        recommendations.append("Advanced components require external libraries to be installed")
    elif components['advanced']['status'] == 'partial':
        recommendations.append("Some advanced components are missing - check library installations")

    if not recommendations:
        recommendations.append("All components working perfectly! You have full functionality available.")

    return recommendations