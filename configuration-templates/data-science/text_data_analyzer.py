# configuration-templates/data-science/text_data_analyzer.py
import pandas as pd
import json
from typing import Dict, List, Any, Union, Optional
from collections import Counter
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TextDataAnalyzer:
    """
    Comprehensive text data analysis class for NLP research.
    Provides statistical analysis, word frequency, and classification insights.
    """

    def __init__(self, data: pd.DataFrame, text_column: str,
                 classification_column: str):
        """
        Initialize the analyzer with data and column specifications.

        Args:
            data: Input DataFrame
            text_column: Name of the text column to analyze
            classification_column: Name of the classification column

        Raises:
            ValueError: If data is empty or columns don't exist
        """
        if data.empty:
            raise ValueError("Data cannot be empty.")

        if text_column not in data.columns:
            raise ValueError(f"Text column '{text_column}' not found in data.")

        if classification_column not in data.columns:
            raise ValueError(f"Classification column '{classification_column}' not found in data.")

        self.data = data.copy()
        self.text_column = text_column
        self.classification_column = classification_column

        # Cache for analysis results
        self._analysis_cache = {}

        logger.info(f"TextDataAnalyzer initialized with {len(self.data):,} rows")

    def analyze_tweet_counts(self) -> Dict[str, Union[int, Dict]]:
        """
        Analyze tweet counts by classification category.

        Returns:
            Dict: Tweet counts by category including totals and unclassified
        """
        logger.info("Analyzing tweet counts by category")

        # Get value counts for classification column
        category_counts = self.data[self.classification_column].value_counts()

        # Count unclassified (NaN) entries
        unclassified_count = self.data[self.classification_column].isnull().sum()

        # Convert to the required format
        result = {}

        # Add each category
        for category, count in category_counts.items():
            result[str(category)] = int(count)

        # Add totals and unclassified
        result['total'] = int(len(self.data))
        result['unclassified'] = int(unclassified_count)

        logger.info(f"Found {len(category_counts)} categories, {unclassified_count} unclassified")

        return result

    def analyze_average_length(self) -> Dict[str, float]:
        """
        Analyze average text length by category (in words).

        Returns:
            Dict: Average word counts by category and overall
        """
        logger.info("Analyzing average text length by category")

        # Create word count column
        self.data['word_count'] = self.data[self.text_column].apply(
            lambda x: len(str(x).split()) if pd.notna(x) else 0
        )

        result = {}

        # Calculate average length by category
        for category in self.data[self.classification_column].dropna().unique():
            category_data = self.data[
                self.data[self.classification_column] == category
                ]
            avg_length = category_data['word_count'].mean()
            result[str(category)] = round(float(avg_length), 2)

        # Calculate overall average
        result['total'] = round(float(self.data['word_count'].mean()), 2)

        logger.info(f"Average lengths calculated for {len(result) - 1} categories")

        return result

    def find_common_words(self, top_n: int = 10,
                          min_word_length: int = 2) -> List[str]:
        """
        Find the most common words across all texts.

        Args:
            top_n: Number of top words to return
            min_word_length: Minimum word length to consider

        Returns:
            List: Most common words
        """
        logger.info(f"Finding top {top_n} common words")

        # Combine all text
        all_text = ' '.join(
            self.data[self.text_column].dropna().astype(str)
        ).lower()

        # Split into words and filter
        words = [
            word for word in all_text.split()
            if len(word) >= min_word_length and word.isalpha()
        ]

        # Count word frequency
        word_counts = Counter(words)

        # Get top N words
        top_words = [word for word, count in word_counts.most_common(top_n)]

        logger.info(f"Found {len(word_counts)} unique words, returning top {len(top_words)}")

        return top_words

    def find_longest_tweets(self, top_n: int = 3) -> Dict[str, List[str]]:
        """
        Find the longest tweets by category.

        Args:
            top_n: Number of longest tweets per category

        Returns:
            Dict: Longest tweets by category
        """
        logger.info(f"Finding top {top_n} longest tweets per category")

        # Create word count column if not exists
        if 'word_count' not in self.data.columns:
            self.data['word_count'] = self.data[self.text_column].apply(
                lambda x: len(str(x).split()) if pd.notna(x) else 0
            )

        result = {}

        # Find longest tweets by category
        for category in self.data[self.classification_column].dropna().unique():
            category_data = self.data[
                self.data[self.classification_column] == category
                ].copy()

            # Sort by word count and get top N
            longest_tweets = category_data.nlargest(top_n, 'word_count')[
                self.text_column
            ].tolist()

            result[str(category)] = longest_tweets

        return result

    def count_uppercase_words(self) -> Dict[str, int]:
        """
        Count words in uppercase (all caps) by category.
        Indicates "shouting" or emphasis in text.

        Returns:
            Dict: Uppercase word counts by category
        """
        logger.info("Counting uppercase words by category")

        def count_caps_words(text):
            """Count words that are entirely uppercase."""
            if pd.isna(text):
                return 0

            words = str(text).split()
            caps_count = sum(
                1 for word in words
                if word.isupper() and len(word) > 1 and word.isalpha()
            )
            return caps_count

        # Add uppercase count column
        self.data['uppercase_count'] = self.data[self.text_column].apply(
            count_caps_words
        )

        result = {}

        # Count by category
        for category in self.data[self.classification_column].dropna().unique():
            category_data = self.data[
                self.data[self.classification_column] == category
                ]
            total_caps = category_data['uppercase_count'].sum()
            result[str(category)] = int(total_caps)

        # Total across all categories
        result['total'] = int(self.data['uppercase_count'].sum())

        logger.info(f"Counted uppercase words across {len(result) - 1} categories")

        return result

    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Generate a comprehensive analysis report.

        Returns:
            Dict: Complete analysis results matching the required format
        """
        logger.info("Generating comprehensive analysis report")

        analysis_results = {
            'total_tweets': self.analyze_tweet_counts(),
            'average_length': self.analyze_average_length(),
            'common_words': self.find_common_words(),
            'longest_3_tweets': self.find_longest_tweets(3),
            'uppercase_words': self.count_uppercase_words()
        }

        # Cache results
        self._analysis_cache = analysis_results

        logger.info("Comprehensive analysis completed")

        return analysis_results

    def save_results(self, file_path: Union[str, Path],
                     results: Optional[Dict] = None) -> None:
        """
        Save analysis results to JSON file.

        Args:
            file_path: Path to save the results
            results: Results to save (uses cached results if None)
        """
        if results is None:
            if not self._analysis_cache:
                results = self.generate_comprehensive_analysis()
            else:
                results = self._analysis_cache

        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Save with proper formatting
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        logger.info(f"Analysis results saved to: {file_path}")

    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the loaded data.

        Returns:
            Dict: Data summary statistics
        """
        summary = {
            'total_rows': len(self.data),
            'total_columns': len(self.data.columns),
            'text_column': self.text_column,
            'classification_column': self.classification_column,
            'unique_categories': self.data[self.classification_column].nunique(),
            'missing_text': self.data[self.text_column].isnull().sum(),
            'missing_classifications': self.data[self.classification_column].isnull().sum()
        }

        return summary

    def print_analysis_summary(self, results: Optional[Dict] = None) -> None:
        """
        Print a formatted summary of analysis results.

        Args:
            results: Results to print (generates if None)
        """
        if results is None:
            results = self.generate_comprehensive_analysis()

        print("=" * 60)
        print("TEXT DATA ANALYSIS SUMMARY")
        print("=" * 60)

        # Tweet counts
        tweet_counts = results['total_tweets']
        print(f"\n📊 TWEET COUNTS:")
        for category, count in tweet_counts.items():
            if category not in ['total', 'unclassified']:
                print(f"  Category {category}: {count:,}")
        print(f"  Total: {tweet_counts['total']:,}")
        if tweet_counts['unclassified'] > 0:
            print(f"  Unclassified: {tweet_counts['unclassified']:,}")

        # Average lengths
        avg_lengths = results['average_length']
        print(f"\n📝 AVERAGE LENGTH (words):")
        for category, length in avg_lengths.items():
            if category != 'total':
                print(f"  Category {category}: {length:.1f}")
        print(f"  Overall: {avg_lengths['total']:.1f}")

        # Common words
        common_words = results['common_words']
        print(f"\n🔤 TOP COMMON WORDS:")
        print(f"  {', '.join(common_words[:10])}")

        # Uppercase counts
        uppercase_counts = results['uppercase_words']
        print(f"\n📢 UPPERCASE WORDS (shouting indicators):")
        for category, count in uppercase_counts.items():
            if category != 'total':
                print(f"  Category {category}: {count:,}")
        print(f"  Total: {uppercase_counts['total']:,}")

        print("=" * 60)