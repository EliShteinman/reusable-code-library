# ============================================================================
# shared-utilities/data_science/sentiment_implementations.py - MULTIPLE LIBRARIES
# ============================================================================
"""
Multiple sentiment analysis implementations
Future-proof for any exam scenario
"""

import logging
from typing import Dict, List, Any, Optional
from .text_processing_base import SentimentAnalyzerBase, ProcessorFactory

logger = logging.getLogger(__name__)


# ============================================================================
# VADER Implementation (NLTK)
# ============================================================================

class VADERSentimentAnalyzer(SentimentAnalyzerBase):
    """
    VADER sentiment analyzer (NLTK-based)
    Best for social media text, informal language
    """

    def __init__(self, nltk_data_path: Optional[str] = None):
        self.analyzer = None
        self.available = False
        self._setup_vader(nltk_data_path)

    def _setup_vader(self, nltk_data_path: Optional[str] = None):
        """Setup VADER with fallback handling."""
        try:
            import nltk
            from nltk.sentiment.vader import SentimentIntensityAnalyzer

            if nltk_data_path:
                nltk_dir = nltk_data_path
            else:
                import os
                nltk_dir = "/tmp/nltk_data"

            try:
                os.makedirs(nltk_dir, exist_ok=True)
                if nltk_dir not in nltk.data.path:
                    nltk.data.path.append(nltk_dir)

                # Check if VADER lexicon exists
                try:
                    nltk.data.find('sentiment/vader_lexicon.zip')
                except LookupError:
                    nltk.download("vader_lexicon", download_dir=nltk_dir, quiet=True)

                self.analyzer = SentimentIntensityAnalyzer()
                self.available = True
                logger.info("VADER sentiment analyzer initialized successfully")

            except Exception as e:
                logger.warning(f"VADER setup failed: {e}")
                self.available = False

        except ImportError:
            logger.warning("NLTK not available, VADER sentiment analyzer disabled")
            self.available = False

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using VADER."""
        if not self.available or not self.analyzer:
            return self._fallback_analysis(text)

        if not text or not isinstance(text, str):
            return self._empty_result()

        try:
            scores = self.analyzer.polarity_scores(text)
            compound = scores['compound']

            # Determine label
            if compound >= 0.05:
                label = 'positive'
            elif compound <= -0.05:
                label = 'negative'
            else:
                label = 'neutral'

            return {
                'compound': compound,
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'label': label,
                'confidence': abs(compound),
                'analyzer': 'vader'
            }

        except Exception as e:
            logger.error(f"VADER analysis failed: {e}")
            return self._fallback_analysis(text)

    def get_supported_languages(self) -> List[str]:
        """VADER primarily supports English."""
        return ['en', 'english']

    def _fallback_analysis(self, text: str) -> Dict[str, Any]:
        """Simple fallback when VADER is not available."""
        return FallbackSentimentAnalyzer().analyze_sentiment(text)

    def _empty_result(self) -> Dict[str, Any]:
        """Return neutral result for empty text."""
        return {
            'compound': 0.0,
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 1.0,
            'label': 'neutral',
            'confidence': 0.0,
            'analyzer': 'vader'
        }


# ============================================================================
# TextBlob Implementation
# ============================================================================

class TextBlobSentimentAnalyzer(SentimentAnalyzerBase):
    """
    TextBlob sentiment analyzer
    Good for formal text, general purpose
    """

    def __init__(self):
        self.available = False
        self._setup_textblob()

    def _setup_textblob(self):
        """Setup TextBlob with fallback handling."""
        try:
            from textblob import TextBlob
            self.TextBlob = TextBlob
            self.available = True
            logger.info("TextBlob sentiment analyzer initialized successfully")
        except ImportError:
            logger.warning("TextBlob not available, sentiment analyzer disabled")
            self.available = False

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using TextBlob."""
        if not self.available:
            return self._fallback_analysis(text)

        if not text or not isinstance(text, str):
            return self._empty_result()

        try:
            blob = self.TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1

            # Convert to VADER-like format
            positive = max(0, polarity)
            negative = max(0, -polarity)
            neutral = 1 - abs(polarity)

            # Determine label
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'

            return {
                'compound': polarity,
                'positive': positive,
                'negative': negative,
                'neutral': neutral,
                'label': label,
                'confidence': abs(polarity),
                'subjectivity': subjectivity,
                'analyzer': 'textblob'
            }

        except Exception as e:
            logger.error(f"TextBlob analysis failed: {e}")
            return self._fallback_analysis(text)

    def get_supported_languages(self) -> List[str]:
        """TextBlob supports multiple languages but works best with English."""
        return ['en', 'english', 'es', 'fr', 'de', 'it', 'pt', 'ru']

    def _fallback_analysis(self, text: str) -> Dict[str, Any]:
        """Simple fallback when TextBlob is not available."""
        return FallbackSentimentAnalyzer().analyze_sentiment(text)

    def _empty_result(self) -> Dict[str, Any]:
        """Return neutral result for empty text."""
        return {
            'compound': 0.0,
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 1.0,
            'label': 'neutral',
            'confidence': 0.0,
            'subjectivity': 0.0,
            'analyzer': 'textblob'
        }


# ============================================================================
# spaCy Implementation
# ============================================================================

class SpacySentimentAnalyzer(SentimentAnalyzerBase):
    """
    spaCy-based sentiment analyzer
    Requires spaCy with sentiment model
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        self.model_name = model_name
        self.nlp = None
        self.available = False
        self._setup_spacy()

    def _setup_spacy(self):
        """Setup spaCy with fallback handling."""
        try:
            import spacy
            self.nlp = spacy.load(self.model_name)

            # Check if sentiment component is available
            if 'textcat' in self.nlp.pipe_names or 'sentiment' in self.nlp.pipe_names:
                self.available = True
                logger.info(f"spaCy sentiment analyzer initialized with {self.model_name}")
            else:
                logger.warning("spaCy model doesn't have sentiment component")
                self.available = False

        except (ImportError, OSError) as e:
            logger.warning(f"spaCy not available or model not found: {e}")
            self.available = False

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using spaCy."""
        if not self.available or not self.nlp:
            return self._fallback_analysis(text)

        if not text or not isinstance(text, str):
            return self._empty_result()

        try:
            doc = self.nlp(text)

            # Extract sentiment scores (depends on model)
            if hasattr(doc, 'sentiment'):
                polarity = doc.sentiment
            elif doc.cats:  # Text classification categories
                # Assume positive/negative categories
                positive_score = doc.cats.get('POSITIVE', 0)
                negative_score = doc.cats.get('NEGATIVE', 0)
                polarity = positive_score - negative_score
            else:
                # Fallback to simple rule-based
                return self._rule_based_analysis(text)

            # Convert to standard format
            positive = max(0, polarity)
            negative = max(0, -polarity)
            neutral = 1 - abs(polarity)

            # Determine label
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'

            return {
                'compound': polarity,
                'positive': positive,
                'negative': negative,
                'neutral': neutral,
                'label': label,
                'confidence': abs(polarity),
                'analyzer': 'spacy'
            }

        except Exception as e:
            logger.error(f"spaCy analysis failed: {e}")
            return self._fallback_analysis(text)

    def get_supported_languages(self) -> List[str]:
        """spaCy supports multiple languages based on loaded model."""
        model_languages = {
            'en_core_web_sm': ['en', 'english'],
            'de_core_news_sm': ['de', 'german'],
            'fr_core_news_sm': ['fr', 'french'],
            'es_core_news_sm': ['es', 'spanish'],
            'it_core_news_sm': ['it', 'italian'],
            'pt_core_news_sm': ['pt', 'portuguese']
        }
        return model_languages.get(self.model_name, ['en'])

    def _rule_based_analysis(self, text: str) -> Dict[str, Any]:
        """Simple rule-based sentiment when spaCy sentiment is not available."""
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome', 'love', 'like',
                          'happy', 'joy'}
        negative_words = {'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'sad', 'angry', 'disappointed',
                          'disgusting'}

        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        if positive_count > negative_count:
            polarity = 0.5
            label = 'positive'
        elif negative_count > positive_count:
            polarity = -0.5
            label = 'negative'
        else:
            polarity = 0.0
            label = 'neutral'

        return {
            'compound': polarity,
            'positive': max(0, polarity),
            'negative': max(0, -polarity),
            'neutral': 1 - abs(polarity),
            'label': label,
            'confidence': abs(polarity),
            'analyzer': 'spacy_rules'
        }

    def _fallback_analysis(self, text: str) -> Dict[str, Any]:
        """Simple fallback when spaCy is not available."""
        return FallbackSentimentAnalyzer().analyze_sentiment(text)

    def _empty_result(self) -> Dict[str, Any]:
        """Return neutral result for empty text."""
        return {
            'compound': 0.0,
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 1.0,
            'label': 'neutral',
            'confidence': 0.0,
            'analyzer': 'spacy'
        }


# ============================================================================
# Custom/Fallback Implementation
# ============================================================================

class FallbackSentimentAnalyzer(SentimentAnalyzerBase):
    """
    Simple rule-based sentiment analyzer
    Always available as fallback when other libraries fail
    """

    def __init__(self):
        """Initialize with predefined word lists."""
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome',
            'love', 'like', 'happy', 'joy', 'pleased', 'satisfied', 'perfect', 'best',
            'brilliant', 'outstanding', 'superb', 'marvelous', 'terrific', 'fabulous'
        }

        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'sad', 'angry',
            'disappointed', 'disgusting', 'pathetic', 'useless', 'worst', 'ridiculous',
            'annoying', 'frustrating', 'boring', 'stupid', 'ugly', 'disgusted'
        }

        self.intensifiers = {
            'very': 1.5, 'really': 1.3, 'extremely': 1.8, 'incredibly': 1.6,
            'absolutely': 1.7, 'totally': 1.4, 'completely': 1.5, 'quite': 1.2
        }

        self.negators = {'not', 'no', 'never', 'neither', 'nor', 'none', 'nobody', 'nothing'}

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using rule-based approach."""
        if not text or not isinstance(text, str):
            return self._empty_result()

        words = text.lower().split()
        sentiment_score = 0.0
        total_words = len(words)

        for i, word in enumerate(words):
            # Check for sentiment words
            word_score = 0.0
            if word in self.positive_words:
                word_score = 1.0
            elif word in self.negative_words:
                word_score = -1.0

            if word_score != 0.0:
                # Check for intensifiers before the word
                if i > 0 and words[i - 1] in self.intensifiers:
                    word_score *= self.intensifiers[words[i - 1]]

                # Check for negators before the word
                negated = False
                for j in range(max(0, i - 3), i):  # Check 3 words before
                    if words[j] in self.negators:
                        negated = True
                        break

                if negated:
                    word_score *= -1

                sentiment_score += word_score

        # Normalize score
        if total_words > 0:
            compound = max(-1.0, min(1.0, sentiment_score / total_words * 2))
        else:
            compound = 0.0

        # Convert to standard format
        positive = max(0, compound)
        negative = max(0, -compound)
        neutral = 1 - abs(compound)

        # Determine label
        if compound > 0.1:
            label = 'positive'
        elif compound < -0.1:
            label = 'negative'
        else:
            label = 'neutral'

        return {
            'compound': compound,
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'label': label,
            'confidence': abs(compound),
            'analyzer': 'hebrew'
        }

    def get_supported_languages(self) -> List[str]:
        """Hebrew analyzer supports Hebrew."""
        return ['he', 'hebrew', 'iw']

    def _empty_result(self) -> Dict[str, Any]:
        """Return neutral result for empty text."""
        return {
            'compound': 0.0,
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 1.0,
            'label': 'neutral',
            'confidence': 0.0,
            'analyzer': 'hebrew'
        }


# ============================================================================
# Auto-Register All Implementations
# ============================================================================

def register_sentiment_analyzers():
    """Register all sentiment analyzer implementations."""
    ProcessorFactory.register_sentiment_analyzer("vader", VADERSentimentAnalyzer)
    ProcessorFactory.register_sentiment_analyzer("textblob", TextBlobSentimentAnalyzer)
    ProcessorFactory.register_sentiment_analyzer("spacy", SpacySentimentAnalyzer)
    ProcessorFactory.register_sentiment_analyzer("fallback", FallbackSentimentAnalyzer)
    ProcessorFactory.register_sentiment_analyzer("hebrew", HebrewSentimentAnalyzer)
    logger.info("All sentiment analyzers registered")


# Auto-register when module is imported
register_sentiment_analyzers()


# ============================================================================
# Smart Sentiment Analyzer (Auto-Detection)
# ============================================================================

class SmartSentimentAnalyzer(SentimentAnalyzerBase):
    """
    Smart sentiment analyzer that automatically chooses the best available implementation
    and can detect language for appropriate analyzer selection
    """

    def __init__(self, preferred_order: List[str] = None):
        """
        Initialize smart analyzer.

        Args:
            preferred_order: List of analyzer names in order of preference
        """
        self.preferred_order = preferred_order or ["vader", "textblob", "spacy", "hebrew", "fallback"]
        self.available_analyzers = {}
        self.language_specific = {
            'he': 'hebrew',
            'hebrew': 'hebrew',
            'iw': 'hebrew'
        }
        self._setup_analyzers()

    def _setup_analyzers(self):
        """Setup available analyzers."""
        for analyzer_name in self.preferred_order:
            try:
                analyzer = ProcessorFactory.create_sentiment_analyzer(analyzer_name)
                # Test if analyzer is actually working
                test_result = analyzer.analyze_sentiment("test")
                if test_result and 'analyzer' in test_result:
                    self.available_analyzers[analyzer_name] = analyzer
                    logger.info(f"Smart analyzer: {analyzer_name} is available")
            except Exception as e:
                logger.debug(f"Smart analyzer: {analyzer_name} not available: {e}")

        if not self.available_analyzers:
            # Ensure fallback is always available
            self.available_analyzers['fallback'] = FallbackSentimentAnalyzer()
            logger.warning("Only fallback sentiment analyzer available")

    def analyze_sentiment(self, text: str, language: str = None) -> Dict[str, Any]:
        """
        Analyze sentiment with automatic analyzer selection.

        Args:
            text: Input text
            language: Optional language hint

        Returns:
            Sentiment analysis result with analyzer used
        """
        if not text or not isinstance(text, str):
            return self._empty_result()

        # Detect language if not provided
        if not language:
            language = self._simple_language_detection(text)

        # Choose analyzer based on language
        chosen_analyzer = self._choose_analyzer(language)

        try:
            result = chosen_analyzer.analyze_sentiment(text)
            result['auto_language'] = language
            result['chosen_analyzer'] = result.get('analyzer', 'unknown')
            return result
        except Exception as e:
            logger.error(f"Smart analyzer failed: {e}")
            # Fallback to any available analyzer
            for analyzer in self.available_analyzers.values():
                try:
                    result = analyzer.analyze_sentiment(text)
                    result['auto_language'] = language
                    result['chosen_analyzer'] = result.get('analyzer', 'fallback')
                    return result
                except:
                    continue

            return self._empty_result()

    def _choose_analyzer(self, language: str) -> SentimentAnalyzerBase:
        """Choose best analyzer for given language."""
        # Check language-specific analyzers first
        if language in self.language_specific:
            specific_analyzer = self.language_specific[language]
            if specific_analyzer in self.available_analyzers:
                return self.available_analyzers[specific_analyzer]

        # Use preferred order for general analyzers
        for analyzer_name in self.preferred_order:
            if analyzer_name in self.available_analyzers:
                analyzer = self.available_analyzers[analyzer_name]
                if language in analyzer.get_supported_languages():
                    return analyzer

        # Fallback to any available analyzer
        if self.available_analyzers:
            return list(self.available_analyzers.values())[0]

        # Ultimate fallback
        return FallbackSentimentAnalyzer()

    def _simple_language_detection(self, text: str) -> str:
        """Simple language detection based on character patterns."""
        if not text:
            return 'en'

        # Hebrew detection (basic)
        hebrew_chars = sum(1 for char in text if '\u0590' <= char <= '\u05FF')
        total_chars = len([char for char in text if char.isalpha()])

        if total_chars > 0 and hebrew_chars / total_chars > 0.3:
            return 'he'

        # Default to English
        return 'en'

    def get_supported_languages(self) -> List[str]:
        """Get all supported languages from available analyzers."""
        languages = set()
        for analyzer in self.available_analyzers.values():
            languages.update(analyzer.get_supported_languages())
        return list(languages)

    def get_available_analyzers(self) -> List[str]:
        """Get list of available analyzer names."""
        return list(self.available_analyzers.keys())

    def _empty_result(self) -> Dict[str, Any]:
        """Return neutral result for empty text."""
        return {
            'compound': 0.0,
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 1.0,
            'label': 'neutral',
            'confidence': 0.0,
            'analyzer': 'smart',
            'auto_language': 'unknown',
            'chosen_analyzer': 'none'
        }


# Register smart analyzer
ProcessorFactory.register_sentiment_analyzer("smart", SmartSentimentAnalyzer)
ProcessorFactory.register_sentiment_analyzer("auto", SmartSentimentAnalyzer)


# ============================================================================
# Ensemble Sentiment Analyzer
# ============================================================================

class EnsembleSentimentAnalyzer(SentimentAnalyzerBase):
    """
    Ensemble sentiment analyzer that combines multiple analyzers
    for more robust results
    """

    def __init__(self, analyzers: List[str] = None, voting: str = "average"):
        """
        Initialize ensemble analyzer.

        Args:
            analyzers: List of analyzer names to combine
            voting: Voting method ('average', 'majority', 'weighted')
        """
        self.analyzer_names = analyzers or ["vader", "textblob", "fallback"]
        self.voting = voting
        self.analyzers = {}
        self.weights = {
            "vader": 1.0,
            "textblob": 1.0,
            "spacy": 1.0,
            "hebrew": 1.0,
            "fallback": 0.5  # Lower weight for fallback
        }
        self._setup_analyzers()

    def _setup_analyzers(self):
        """Setup ensemble analyzers."""
        for analyzer_name in self.analyzer_names:
            try:
                analyzer = ProcessorFactory.create_sentiment_analyzer(analyzer_name)
                # Test analyzer
                test_result = analyzer.analyze_sentiment("test")
                if test_result and 'analyzer' in test_result:
                    self.analyzers[analyzer_name] = analyzer
                    logger.info(f"Ensemble: {analyzer_name} added")
            except Exception as e:
                logger.debug(f"Ensemble: {analyzer_name} not available: {e}")

        if not self.analyzers:
            self.analyzers['fallback'] = FallbackSentimentAnalyzer()

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using ensemble method."""
        if not text or not isinstance(text, str):
            return self._empty_result()

        results = []
        for name, analyzer in self.analyzers.items():
            try:
                result = analyzer.analyze_sentiment(text)
                result['source_analyzer'] = name
                results.append(result)
            except Exception as e:
                logger.warning(f"Ensemble analyzer {name} failed: {e}")

        if not results:
            return self._empty_result()

        # Combine results based on voting method
        if self.voting == "average":
            return self._average_voting(results)
        elif self.voting == "majority":
            return self._majority_voting(results)
        elif self.voting == "weighted":
            return self._weighted_voting(results)
        else:
            return self._average_voting(results)

    def _average_voting(self, results: List[Dict]) -> Dict[str, Any]:
        """Combine results using simple averaging."""
        compounds = [r['compound'] for r in results]
        positives = [r['positive'] for r in results]
        negatives = [r['negative'] for r in results]
        neutrals = [r['neutral'] for r in results]
        confidences = [r['confidence'] for r in results]

        avg_compound = sum(compounds) / len(compounds)
        avg_positive = sum(positives) / len(positives)
        avg_negative = sum(negatives) / len(negatives)
        avg_neutral = sum(neutrals) / len(neutrals)
        avg_confidence = sum(confidences) / len(confidences)

        # Determine label
        if avg_compound > 0.1:
            label = 'positive'
        elif avg_compound < -0.1:
            label = 'negative'
        else:
            label = 'neutral'

        return {
            'compound': avg_compound,
            'positive': avg_positive,
            'negative': avg_negative,
            'neutral': avg_neutral,
            'label': label,
            'confidence': avg_confidence,
            'analyzer': 'ensemble_average',
            'component_results': results
        }

    def _majority_voting(self, results: List[Dict]) -> Dict[str, Any]:
        """Combine results using majority voting for labels."""
        labels = [r['label'] for r in results]

        # Count votes
        label_counts = {}
        for label in labels:
            label_counts[label] = label_counts.get(label, 0) + 1

        # Find majority
        majority_label = max(label_counts, key=label_counts.get)

        # Average scores from analyzers that voted for majority
        majority_results = [r for r in results if r['label'] == majority_label]

        if majority_results:
            avg_compound = sum(r['compound'] for r in majority_results) / len(majority_results)
            avg_positive = sum(r['positive'] for r in majority_results) / len(majority_results)
            avg_negative = sum(r['negative'] for r in majority_results) / len(majority_results)
            avg_neutral = sum(r['neutral'] for r in majority_results) / len(majority_results)
            avg_confidence = sum(r['confidence'] for r in majority_results) / len(majority_results)
        else:
            # Fallback to overall average
            return self._average_voting(results)

        return {
            'compound': avg_compound,
            'positive': avg_positive,
            'negative': avg_negative,
            'neutral': avg_neutral,
            'label': majority_label,
            'confidence': avg_confidence,
            'analyzer': 'ensemble_majority',
            'votes': label_counts,
            'component_results': results
        }

    def _weighted_voting(self, results: List[Dict]) -> Dict[str, Any]:
        """Combine results using weighted averaging."""
        total_weight = 0
        weighted_compound = 0
        weighted_positive = 0
        weighted_negative = 0
        weighted_neutral = 0
        weighted_confidence = 0

        for result in results:
            analyzer_name = result.get('source_analyzer', 'fallback')
            weight = self.weights.get(analyzer_name, 1.0)

            weighted_compound += result['compound'] * weight
            weighted_positive += result['positive'] * weight
            weighted_negative += result['negative'] * weight
            weighted_neutral += result['neutral'] * weight
            weighted_confidence += result['confidence'] * weight
            total_weight += weight

        if total_weight > 0:
            avg_compound = weighted_compound / total_weight
            avg_positive = weighted_positive / total_weight
            avg_negative = weighted_negative / total_weight
            avg_neutral = weighted_neutral / total_weight
            avg_confidence = weighted_confidence / total_weight
        else:
            return self._average_voting(results)

        # Determine label
        if avg_compound > 0.1:
            label = 'positive'
        elif avg_compound < -0.1:
            label = 'negative'
        else:
            label = 'neutral'

        return {
            'compound': avg_compound,
            'positive': avg_positive,
            'negative': avg_negative,
            'neutral': avg_neutral,
            'label': label,
            'confidence': avg_confidence,
            'analyzer': 'ensemble_weighted',
            'total_weight': total_weight,
            'component_results': results
        }

    def get_supported_languages(self) -> List[str]:
        """Get all supported languages from component analyzers."""
        languages = set()
        for analyzer in self.analyzers.values():
            languages.update(analyzer.get_supported_languages())
        return list(languages)

    def _empty_result(self) -> Dict[str, Any]:
        """Return neutral result for empty text."""
        return {
            'compound': 0.0,
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 1.0,
            'label': 'neutral',
            'confidence': 0.0,
            'analyzer': 'ensemble',
            'component_results': []
        }


# Register ensemble analyzer
ProcessorFactory.register_sentiment_analyzer("ensemble", EnsembleSentimentAnalyzer)


# ============================================================================
# Convenience Functions
# ============================================================================

def get_best_available_sentiment_analyzer() -> SentimentAnalyzerBase:
    """Get the best available sentiment analyzer."""
    return SmartSentimentAnalyzer()


def analyze_sentiment_with_fallback(text: str, preferred_analyzer: str = "vader") -> Dict[str, Any]:
    """
    Analyze sentiment with automatic fallback to available analyzers.

    Args:
        text: Input text
        preferred_analyzer: Preferred analyzer name

    Returns:
        Sentiment analysis result
    """
    try:
        analyzer = ProcessorFactory.create_sentiment_analyzer(preferred_analyzer)
        return analyzer.analyze_sentiment(text)
    except Exception:
        # Fallback to smart analyzer
        smart_analyzer = SmartSentimentAnalyzer()
        return smart_analyzer.analyze_sentiment(text)


def get_available_sentiment_analyzers() -> List[str]:
    """Get list of available sentiment analyzer names."""
    available = ProcessorFactory.list_available()
    return available.get('sentiment_analyzers', [])

    'confidence': abs(compound),
    'analyzer': 'fallback'

}

def get_supported_languages(self) -> List[str]:
    """Fallback analyzer supports basic English."""
    return ['en', 'english']


def _empty_result(self) -> Dict[str, Any]:
    """Return neutral result for empty text."""
    return {
        'compound': 0.0,
        'positive': 0.0,
        'negative': 0.0,
        'neutral': 1.0,
        'label': 'neutral',
        'confidence': 0.0,
        'analyzer': 'fallback'
    }


# ============================================================================
# Hebrew Sentiment Analyzer (Custom)
# ============================================================================

class HebrewSentimentAnalyzer(SentimentAnalyzerBase):
    """
    Hebrew sentiment analyzer
    Custom implementation for Hebrew text
    """

    def __init__(self):
        """Initialize with Hebrew word lists."""
        self.positive_words = {
            'טוב', 'מעולה', 'נהדר', 'יפה', 'נפלא', 'מדהים', 'איכותי', 'מושלם',
            'משובח', 'יוצא מן הכלל', 'מצוין', 'אהבתי', 'שמח', 'מרוצה', 'מומלץ'
        }

        self.negative_words = {
            'רע', 'גרוע', 'נורא', 'איום', 'מבאס', 'מעצבן', 'מאכזב', 'זבל',
            'לא טוב', 'בעיה', 'קשה', 'מסריח', 'מגעיל', 'שנאתי', 'עצוב'
        }

        self.negators = {'לא', 'אין', 'בלי', 'ללא', 'בלתי', 'אל'}

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze Hebrew text sentiment."""
        if not text or not isinstance(text, str):
            return self._empty_result()

        words = text.split()
        sentiment_score = 0.0
        total_words = len(words)

        for i, word in enumerate(words):
            word_score = 0.0
            if word in self.positive_words:
                word_score = 1.0
            elif word in self.negative_words:
                word_score = -1.0

            if word_score != 0.0:
                # Check for negators
                negated = False
                for j in range(max(0, i - 2), i):
                    if words[j] in self.negators:
                        negated = True
                        break

                if negated:
                    word_score *= -1

                sentiment_score += word_score

        # Normalize score
        if total_words > 0:
            compound = max(-1.0, min(1.0, sentiment_score / total_words * 2))
        else:
            compound = 0.0

        # Convert to standard format
        positive = max(0, compound)
        negative = max(0, -compound)
        neutral = 1 - abs(compound)

        # Determine label
        if compound > 0.1:
            label = 'positive'
        elif compound < -0.1:
            label = 'negative'
        else:
            label = 'neutral'

        return {
            'compound': compound,
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'label': label,