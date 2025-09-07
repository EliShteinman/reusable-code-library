# shared-utilities/data_science/sentiment_analyzer.py
import logging
import os
from typing import Dict, List, Optional, Any
import pandas as pd

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Enhanced sentiment analyzer - now with better error handling
    """

    def __init__(self,
                 nltk_path: Optional[str] = None,
                 positive_threshold: float = 0.5,
                 negative_threshold: float = -0.5):
        """
        Initialize sentiment analyzer.

        Args:
            nltk_path: Custom path for NLTK data
            positive_threshold: Threshold for positive sentiment
            negative_threshold: Threshold for negative sentiment
        """
        self.positive_threshold = positive_threshold
        self.negative_threshold = negative_threshold
        self.analyzer = None

        # Try to initialize VADER
        self._setup_sentiment_analyzer(nltk_path)

    def _setup_sentiment_analyzer(self, nltk_path: Optional[str] = None):
        """Setup sentiment analyzer with fallback options."""
        try:
            # Try NLTK VADER first
            import nltk
            from nltk.sentiment.vader import SentimentIntensityAnalyzer

            self._setup_nltk(nltk_path)
            self.analyzer = SentimentIntensityAnalyzer()
            self.analyzer_type = "vader"
            logger.info("VADER sentiment analyzer initialized successfully")

        except ImportError:
            logger.warning("NLTK not available, falling back to simple sentiment analysis")
            self.analyzer_type = "simple"

        except Exception as e:
            logger.error(f"Failed to initialize VADER: {e}, falling back to simple sentiment")
            self.analyzer_type = "simple"

    def _setup_nltk(self, nltk_path: Optional[str] = None):
        """Setup NLTK data directory and download VADER lexicon."""
        import nltk

        if nltk_path:
            nltk_dir = nltk_path
        else:
            nltk_dir = "/tmp/nltk_data"

        try:
            os.makedirs(nltk_dir, exist_ok=True)

            if nltk_dir not in nltk.data.path:
                nltk.data.path.append(nltk_dir)

            # Check if VADER lexicon exists
            try:
                nltk.data.find('sentiment/vader_lexicon.zip')
                logger.info("VADER lexicon already available")
            except LookupError:
                logger.info("Downloading VADER lexicon...")
                nltk.download("vader_lexicon", download_dir=nltk_dir, quiet=True)
                logger.info("VADER lexicon downloaded successfully")

        except Exception as e:
            logger.error(f"Error setting up NLTK: {e}")
            raise

    def _simple_sentiment_score(self, text: str) -> float:
        """Simple rule-based sentiment analysis as fallback."""
        if not text or not isinstance(text, str):
            return 0.0

        text_lower = text.lower()

        # Simple positive/negative word lists
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'awesome', 'fantastic', 'wonderful',
            'love', 'like', 'happy', 'pleased', 'satisfied', 'perfect', 'best', 'brilliant'
        }

        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'angry', 'sad',
            'disappointed', 'poor', 'worst', 'disgusting', 'pathetic', 'useless'
        }

        words = text_lower.split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        # Simple scoring
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0

        score = (positive_count - negative_count) / len(words)
        return max(-1.0, min(1.0, score * 10))  # Scale and clamp

    def get_sentiment_score(self, text: str) -> float:
        """
        Get compound sentiment score (-1 to 1).

        Args:
            text: Text to analyze

        Returns:
            Compound sentiment score
        """
        if not text or not isinstance(text, str):
            return 0.0

        try:
            if self.analyzer_type == "vader" and self.analyzer:
                scores = self.analyzer.polarity_scores(text)
                return scores['compound']
            else:
                return self._simple_sentiment_score(text)
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.0

    def get_detailed_scores(self, text: str) -> Dict[str, float]:
        """
        Get detailed sentiment scores.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with pos, neu, neg, compound scores
        """
        if not text or not isinstance(text, str):
            return {'pos': 0.0, 'neu': 1.0, 'neg': 0.0, 'compound': 0.0}

        try:
            if self.analyzer_type == "vader" and self.analyzer:
                return self.analyzer.polarity_scores(text)
            else:
                # Simple fallback
                compound = self._simple_sentiment_score(text)
                if compound > 0:
                    return {'pos': abs(compound), 'neu': 1 - abs(compound), 'neg': 0.0, 'compound': compound}
                elif compound < 0:
                    return {'pos': 0.0, 'neu': 1 - abs(compound), 'neg': abs(compound), 'compound': compound}
                else:
                    return {'pos': 0.0, 'neu': 1.0, 'neg': 0.0, 'compound': 0.0}
        except Exception as e:
            logger.error(f"Error analyzing detailed sentiment: {e}")
            return {'pos': 0.0, 'neu': 1.0, 'neg': 0.0, 'compound': 0.0}

    def get_sentiment_label(self, text: str) -> str:
        """
        Get sentiment label (positive, negative, neutral).

        Args:
            text: Text to analyze

        Returns:
            Sentiment label
        """
        score = self.get_sentiment_score(text)
        return self.score_to_label(score)

    def score_to_label(self, score: float) -> str:
        """Convert sentiment score to label."""
        if score >= self.positive_threshold:
            return "positive"
        elif score <= self.negative_threshold:
            return "negative"
        else:
            return "neutral"

    def analyze_dataframe(self,
                          df,
                          text_column: str,
                          add_detailed: bool = False) -> pd.DataFrame:
        """
        Analyze sentiment for DataFrame.

        Args:
            df: DataFrame with text data
            text_column: Name of text column
            add_detailed: Whether to add detailed scores

        Returns:
            DataFrame with sentiment columns added
        """
        df_result = df.copy()

        # Add compound score and label
        logger.info(f"Analyzing sentiment for {len(df)} texts using {self.analyzer_type} analyzer...")

        df_result['sentiment_score'] = df_result[text_column].apply(self.get_sentiment_score)
        df_result['sentiment_label'] = df_result['sentiment_score'].apply(self.score_to_label)

        if add_detailed:
            # Add detailed scores
            detailed_scores = df_result[text_column].apply(self.get_detailed_scores)
            df_result['sentiment_positive'] = detailed_scores.apply(lambda x: x['pos'])
            df_result['sentiment_neutral'] = detailed_scores.apply(lambda x: x['neu'])
            df_result['sentiment_negative'] = detailed_scores.apply(lambda x: x['neg'])

        logger.info("Sentiment analysis completed")
        return df_result

    def get_sentiment_statistics(self, scores: List[float]) -> Dict[str, Any]:
        """
        Get statistics for sentiment scores.

        Args:
            scores: List of sentiment scores

        Returns:
            Statistics dictionary
        """
        import numpy as np

        labels = [self.score_to_label(score) for score in scores]
        label_counts = pd.Series(labels).value_counts()

        return {
            'total_texts': len(scores),
            'average_score': round(np.mean(scores), 3),
            'median_score': round(np.median(scores), 3),
            'std_score': round(np.std(scores), 3),
            'min_score': round(min(scores), 3),
            'max_score': round(max(scores), 3),
            'positive_count': label_counts.get('positive', 0),
            'negative_count': label_counts.get('negative', 0),
            'neutral_count': label_counts.get('neutral', 0),
            'positive_percentage': round(label_counts.get('positive', 0) / len(scores) * 100, 2),
            'negative_percentage': round(label_counts.get('negative', 0) / len(scores) * 100, 2),
            'neutral_percentage': round(label_counts.get('neutral', 0) / len(scores) * 100, 2)
        }