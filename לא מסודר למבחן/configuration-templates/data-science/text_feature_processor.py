# configuration-templates/data-science/text_feature_processor.py
import logging
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from collections import Counter
from typing import List, Set, Dict

logger = logging.getLogger(__name__)


class TextFeatureProcessor:
    """A class for text processing and feature engineering from a text column."""

    def __init__(self):
        logger.info("Initializing TextFeatureProcessor.")
        try:
            # Best practice: Ensure NLTK data is available.
            # In production, this should ideally be part of the Docker image build process.
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download("vader_lexicon", quiet=True)

        self.sid = SentimentIntensityAnalyzer()
        logger.info("VADER lexicon loaded successfully.")

    def find_rarest_word(self, text: str) -> str:
        """Finds the first rarest word in a given text."""
        if not isinstance(text, str) or not text.strip():
            return ""
        words = text.split()
        if not words:
            return ""

        counts = Counter(words)
        min_freq = min(counts.values())

        for word in words:
            if counts[word] == min_freq:
                return word
        return ""

    def get_sentiment(self, text: str, thresholds: Dict[str, float] = None) -> str:
        """Determines sentiment (positive/negative/neutral) of a text."""
        if thresholds is None:
            thresholds = {'positive': 0.5, 'negative': -0.5}

        if not isinstance(text, str) or not text.strip():
            return "neutral"

        try:
            score = self.sid.polarity_scores(text)
            compound = score['compound']

            if compound >= thresholds['positive']:
                return "positive"
            elif compound <= thresholds['negative']:
                return "negative"
            else:
                return "neutral"
        except Exception as e:
            logger.warning(f"Sentiment analysis failed for text: '{text[:50]}...'. Error: {e}")
            return "neutral"

    def find_first_keyword(self, text: str, keyword_set: Set[str]) -> str:
        """Finds the first keyword from a given set within a text."""
        if not isinstance(text, str) or not text.strip() or not keyword_set:
            return ""

        text_lower = text.lower()

        for keyword in keyword_set:
            if keyword.lower() in text_lower:
                return keyword
        return ""

    def apply_all_features(self, df: pd.DataFrame, text_column: str, keyword_set: Set[str] = None) -> pd.DataFrame:
        """Applies all processing functions to a DataFrame and adds them as new columns."""
        if text_column not in df.columns:
            raise ValueError(f"Text column '{text_column}' not found in DataFrame.")

        df['rarest_word'] = df[text_column].apply(self.find_rarest_word)
        df['sentiment'] = df[text_column].apply(self.get_sentiment)
        if keyword_set:
            df['keywords_detected'] = df[text_column].apply(lambda x: self.find_first_keyword(x, keyword_set))

        return df