# configuration-templates/data-science/generic_text_analysis.py
"""
Generic Text Analysis Framework
Universal solution for text classification and analysis projects.
Not tied to specific domain (Twitter, reviews, etc.)
"""

import pandas as pd
import json
import string
import re
from pathlib import Path
from collections import Counter
from typing import Dict, List, Any, Union, Optional
from abc import ABC, abstractmethod

from data_loader import DataHandler
from text_data_cleaner import TextDataCleaner


class TextAnalysisConfig:
    """
    Configuration class for text analysis projects.
    Allows customization without hardcoded values.
    """

    def __init__(self,
                 text_column: str,
                 classification_column: str,
                 output_dir: str = "results",
                 cleaned_filename: str = "cleaned_data.csv",
                 results_filename: str = "results.json"):
        """
        Initialize configuration.

        Args:
            text_column: Name of the text column to analyze
            classification_column: Name of the classification column
            output_dir: Directory to save results
            cleaned_filename: Name for cleaned data file
            results_filename: Name for results JSON file
        """
        self.text_column = text_column
        self.classification_column = classification_column
        self.output_dir = Path(output_dir)
        self.cleaned_filename = cleaned_filename
        self.results_filename = results_filename

        # Analysis parameters (customizable)
        self.top_common_words = 10
        self.top_longest_texts = 3
        self.min_word_length = 2

        # Category mapping (for display names)
        self.category_names = {}  # Can be customized per project


class BaseTextAnalyzer(ABC):
    """
    Abstract base class for text analysis.
    Defines the interface that all text analyzers should implement.
    """

    def __init__(self, data: pd.DataFrame, config: TextAnalysisConfig):
        self.data = data.copy()
        self.config = config
        self.analysis_results = {}

    @abstractmethod
    def analyze_text_counts(self) -> Dict[str, Any]:
        """Analyze distribution of texts by category."""
        pass

    @abstractmethod
    def analyze_text_lengths(self) -> Dict[str, float]:
        """Analyze average text lengths."""
        pass

    @abstractmethod
    def find_common_words(self) -> List[str]:
        """Find most common words."""
        pass

    @abstractmethod
    def analyze_text_features(self) -> Dict[str, Any]:
        """Analyze domain-specific features."""
        pass


class GenericTextAnalyzer(BaseTextAnalyzer):
    """
    Generic text analyzer that works with any text classification dataset.
    Can be used for sentiment analysis, topic classification, spam detection, etc.
    """

    def run_complete_analysis(self) -> Dict[str, Any]:
        """
        Run comprehensive analysis on the dataset.

        Returns:
            Complete analysis results
        """
        print("🚀 STARTING TEXT ANALYSIS")
        print(f"📊 Dataset: {len(self.data):,} records")
        print(f"📝 Text column: {self.config.text_column}")
        print(f"🏷️ Classification column: {self.config.classification_column}")

        # Run all analysis components
        self.analysis_results = {
            'text_counts': self.analyze_text_counts(),
            'average_lengths': self.analyze_text_lengths(),
            'common_words': self.find_common_words(),
            'longest_texts': self.find_longest_texts(),
            'text_features': self.analyze_text_features()
        }

        print("✅ Analysis completed successfully!")
        return self.analysis_results

    def analyze_text_counts(self) -> Dict[str, Any]:
        """Count texts by classification category."""
        counts = self.data[self.config.classification_column].value_counts()
        unspecified = self.data[self.config.classification_column].isnull().sum()

        result = {}
        for category, count in counts.items():
            # Use custom names if provided
            display_name = self.config.category_names.get(str(category), str(category))
            result[display_name] = int(count)

        result['total'] = int(len(self.data))
        result['unspecified'] = int(unspecified)

        return result

    def analyze_text_lengths(self) -> Dict[str, float]:
        """Calculate average text length by category (in words)."""
        # Add word count column
        self.data['_word_count'] = self.data[self.config.text_column].apply(
            lambda x: len(str(x).split()) if pd.notna(x) else 0
        )

        result = {}

        # Calculate by category
        for category in self.data[self.config.classification_column].dropna().unique():
            category_data = self.data[self.data[self.config.classification_column] == category]
            avg_length = category_data['_word_count'].mean()

            display_name = self.config.category_names.get(str(category), str(category))
            result[display_name] = round(float(avg_length), 2)

        # Overall average
        result['total'] = round(float(self.data['_word_count'].mean()), 2)

        return result

    def find_common_words(self) -> List[str]:
        """Find most common words across all texts."""
        # Combine all text
        all_text = ' '.join(
            self.data[self.config.text_column].dropna().astype(str)
        ).lower()

        # Remove punctuation and split
        translator = str.maketrans('', '', string.punctuation)
        clean_text = all_text.translate(translator)
        words = clean_text.split()

        # Filter words
        filtered_words = [
            word for word in words
            if len(word) >= self.config.min_word_length and word.isalpha()
        ]

        # Count and return top N
        word_counts = Counter(filtered_words)
        return [word for word, count in word_counts.most_common(self.config.top_common_words)]

    def find_longest_texts(self) -> Dict[str, List[str]]:
        """Find longest texts by category."""
        if '_word_count' not in self.data.columns:
            self.data['_word_count'] = self.data[self.config.text_column].apply(
                lambda x: len(str(x).split()) if pd.notna(x) else 0
            )

        result = {}

        for category in self.data[self.config.classification_column].dropna().unique():
            category_data = self.data[self.data[self.config.classification_column] == category].copy()
            longest_texts = category_data.nlargest(
                self.config.top_longest_texts, '_word_count'
            )[self.config.text_column].tolist()

            display_name = self.config.category_names.get(str(category), str(category))
            result[display_name] = longest_texts

        return result

    def analyze_text_features(self) -> Dict[str, Any]:
        """
        Analyze generic text features.
        Override this method for domain-specific features.
        """

        # Count uppercase words (shouting indicator)
        def count_caps_words(text):
            if pd.isna(text):
                return 0
            words = str(text).split()
            return sum(1 for word in words if word.isupper() and len(word) > 1 and word.isalpha())

        self.data['_uppercase_count'] = self.data[self.config.text_column].apply(count_caps_words)

        result = {}

        # Count by category
        for category in self.data[self.config.classification_column].dropna().unique():
            category_data = self.data[self.data[self.config.classification_column] == category]
            total_caps = category_data['_uppercase_count'].sum()

            display_name = self.config.category_names.get(str(category), str(category))
            result[f'{display_name}_uppercase_words'] = int(total_caps)

        # Total
        result['total_uppercase_words'] = int(self.data['_uppercase_count'].sum())

        return result

    def save_results(self, custom_format_func=None) -> None:
        """
        Save analysis results to files.

        Args:
            custom_format_func: Optional function to customize output format
        """
        # Ensure output directory exists
        self.config.output_dir.mkdir(exist_ok=True)

        # Save results JSON
        results_path = self.config.output_dir / self.config.results_filename

        # Apply custom formatting if provided
        if custom_format_func:
            formatted_results = custom_format_func(self.analysis_results)
        else:
            formatted_results = self.analysis_results

        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_results, f, indent=4, ensure_ascii=False)

        print(f"💾 Results saved: {results_path}")

    def print_summary(self) -> None:
        """Print a formatted summary of analysis results."""
        print("\n" + "=" * 60)
        print("TEXT ANALYSIS SUMMARY")
        print("=" * 60)

        # Text counts
        if 'text_counts' in self.analysis_results:
            counts = self.analysis_results['text_counts']
            print(f"\n📊 TEXT DISTRIBUTION:")
            total = counts.get('total', 0)
            for category, count in counts.items():
                if category not in ['total', 'unspecified']:
                    percentage = (count / total * 100) if total > 0 else 0
                    print(f"  • {category}: {count:,} ({percentage:.1f}%)")
            print(f"  📈 Total: {total:,}")

        # Average lengths
        if 'average_lengths' in self.analysis_results:
            lengths = self.analysis_results['average_lengths']
            print(f"\n📝 AVERAGE LENGTH (words):")
            for category, length in lengths.items():
                print(f"  • {category}: {length:.1f}")

        # Common words
        if 'common_words' in self.analysis_results:
            words = self.analysis_results['common_words']
            print(f"\n🔤 TOP COMMON WORDS:")
            print(f"  {', '.join(words)}")

        print("=" * 60)


class TextAnalysisPipeline:
    """
    Complete pipeline for text analysis projects.
    Handles loading, cleaning, analysis, and export.
    """

    def __init__(self, data_path: str, config: TextAnalysisConfig):
        """
        Initialize the analysis pipeline.

        Args:
            data_path: Path to the dataset file
            config: Analysis configuration
        """
        self.data_path = Path(data_path)
        self.config = config

        # Pipeline components
        self.data_loader = None
        self.data_cleaner = None
        self.analyzer = None

        # Data storage
        self.raw_data = None
        self.cleaned_data = None

    def load_data(self) -> pd.DataFrame:
        """Load the dataset."""
        print("📁 Loading data...")
        self.data_loader = DataHandler(str(self.data_path))
        self.raw_data = self.data_loader.load_data()
        print(f"✅ Loaded {len(self.raw_data):,} records")
        return self.raw_data

    def clean_data(self, custom_cleaning_steps: Optional[List] = None) -> pd.DataFrame:
        """
        Clean the dataset.

        Args:
            custom_cleaning_steps: Optional custom cleaning functions

        Returns:
            Cleaned dataset
        """
        print("🧹 Cleaning data...")

        self.data_cleaner = TextDataCleaner()

        # Apply comprehensive cleaning
        self.cleaned_data = self.data_cleaner.comprehensive_text_cleaning(
            data=self.raw_data,
            text_columns=[self.config.text_column],
            classification_columns=[self.config.classification_column],
            remove_unclassified=True
        )

        # Keep only relevant columns
        columns_to_keep = [self.config.text_column, self.config.classification_column]
        self.cleaned_data = self.cleaned_data[columns_to_keep]

        # Apply custom cleaning steps if provided
        if custom_cleaning_steps:
            for cleaning_func in custom_cleaning_steps:
                self.cleaned_data = cleaning_func(self.cleaned_data)

        print(f"✅ Cleaned data: {len(self.cleaned_data):,} records")
        return self.cleaned_data

    def analyze_data(self, analyzer_class=None) -> Dict[str, Any]:
        """
        Analyze the cleaned data.

        Args:
            analyzer_class: Custom analyzer class (defaults to GenericTextAnalyzer)

        Returns:
            Analysis results
        """
        print("📊 Analyzing data...")

        if analyzer_class is None:
            analyzer_class = GenericTextAnalyzer

        self.analyzer = analyzer_class(self.cleaned_data, self.config)
        results = self.analyzer.run_complete_analysis()

        return results

    def save_cleaned_data(self) -> None:
        """Save the cleaned dataset."""
        if self.cleaned_data is None:
            raise ValueError("No cleaned data to save. Run clean_data() first.")

        cleaned_path = self.config.output_dir / self.config.cleaned_filename
        self.config.output_dir.mkdir(exist_ok=True)

        self.cleaned_data.to_csv(cleaned_path, index=False)
        print(f"💾 Cleaned data saved: {cleaned_path}")

    def run_complete_pipeline(self,
                              custom_cleaning_steps=None,
                              analyzer_class=None,
                              results_formatter=None) -> Dict[str, Any]:
        """
        Run the complete analysis pipeline.

        Args:
            custom_cleaning_steps: Custom data cleaning functions
            analyzer_class: Custom analyzer class
            results_formatter: Custom results formatting function

        Returns:
            Analysis results
        """
        try:
            # Run pipeline steps
            self.load_data()
            self.clean_data(custom_cleaning_steps)
            results = self.analyze_data(analyzer_class)

            # Save outputs
            self.save_cleaned_data()
            self.analyzer.save_results(results_formatter)

            # Display summary
            self.analyzer.print_summary()

            print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            return results

        except Exception as e:
            print(f"\n❌ PIPELINE FAILED: {e}")
            raise


# Example usage functions for different domains
def create_twitter_config():
    """Create configuration for Twitter sentiment analysis."""
    config = TextAnalysisConfig(
        text_column="Text",
        classification_column="Biased",
        output_dir="results",
        cleaned_filename="tweets_dataset_cleaned.csv",
        results_filename="results.json"
    )

    # Custom category names
    config.category_names = {
        '0': 'non_antisemitic',
        '1': 'antisemitic'
    }

    return config


def create_review_config():
    """Create configuration for product review analysis."""
    config = TextAnalysisConfig(
        text_column="review_text",
        classification_column="sentiment",
        output_dir="review_analysis",
        cleaned_filename="cleaned_reviews.csv",
        results_filename="review_analysis.json"
    )

    # Custom category names
    config.category_names = {
        '1': 'positive',
        '0': 'negative'
    }

    return config


def create_email_config():
    """Create configuration for email spam detection."""
    config = TextAnalysisConfig(
        text_column="email_body",
        classification_column="is_spam",
        output_dir="spam_analysis",
        cleaned_filename="cleaned_emails.csv",
        results_filename="spam_analysis.json"
    )

    # Custom category names
    config.category_names = {
        '1': 'spam',
        '0': 'not_spam'
    }

    return config


# Main execution example
def main():
    """Example of how to use the generic framework."""
    # Create configuration (customize for your domain)
    config = create_twitter_config()  # or create_review_config(), etc.

    # Create and run pipeline
    pipeline = TextAnalysisPipeline("data/your_dataset.csv", config)

    # Custom formatter for specific output format (optional)
    def twitter_results_formatter(results):
        """Format results for Twitter analysis exam requirements."""
        return {
            'total_tweets': results['text_counts'],
            'average_length': results['average_lengths'],
            'common_words': {'total': results['common_words']},
            'longest_3_tweets': results['longest_texts'],
            'uppercase_words': results['text_features']
        }

    # Run complete analysis
    results = pipeline.run_complete_pipeline(
        results_formatter=twitter_results_formatter
    )

    return results


if __name__ == "__main__":
    main()