# configuration-templates/data-science/text_data_cleaner.py
import pandas as pd
import string
import re
from typing import List, Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class TextDataCleaner:
    """
    Comprehensive text data cleaning class for NLP preprocessing.
    Handles common text cleaning operations with flexibility and validation.
    """

    def __init__(self):
        """Initialize the text cleaner with default configurations."""
        self.cleaning_stats = {}

    def clean_pipeline(self, data: pd.DataFrame, text_columns: List[str],
                       classification_columns: List[str] = None,
                       remove_unclassified: bool = True) -> pd.DataFrame:
        """
        Complete text cleaning pipeline.

        Args:
            data: Input DataFrame
            text_columns: List of text columns to clean
            classification_columns: Columns to check for missing values
            remove_unclassified: Whether to remove rows with missing classifications

        Returns:
            pd.DataFrame: Cleaned data
        """
        logger.info("Starting text cleaning pipeline")

        cleaned_data = data.copy()

        # Remove unclassified entries
        if remove_unclassified and classification_columns:
            cleaned_data = self.remove_unclassified(
                cleaned_data, classification_columns
            )

        # Clean text columns
        for col in text_columns:
            if col not in cleaned_data.columns:
                logger.warning(f"Column '{col}' not found in data")
                continue

            logger.info(f"Cleaning text column: {col}")

            # Apply cleaning steps
            cleaned_data[col] = self._clean_text_column(cleaned_data[col])

        # Log cleaning statistics
        self._log_cleaning_stats(data, cleaned_data)

        return cleaned_data

    def remove_unclassified(self, data: pd.DataFrame,
                            columns_to_check: List[str]) -> pd.DataFrame:
        """
        Remove rows with missing values in specified columns.

        Args:
            data: Input DataFrame
            columns_to_check: Columns to check for missing values

        Returns:
            pd.DataFrame: Data without unclassified entries
        """
        initial_count = len(data)
        cleaned_data = data.dropna(subset=columns_to_check)
        removed_count = initial_count - len(cleaned_data)

        logger.info(f"Removed {removed_count:,} unclassified entries")

        self.cleaning_stats['unclassified_removed'] = removed_count

        return cleaned_data

    def remove_punctuation(self, data: pd.DataFrame,
                           columns: List[str]) -> pd.DataFrame:
        """
        Remove punctuation from specified text columns.

        Args:
            data: Input DataFrame
            columns: List of columns to process

        Returns:
            pd.DataFrame: Data with punctuation removed
        """
        cleaned_data = data.copy()

        for col in columns:
            if col not in cleaned_data.columns:
                continue

            logger.info(f"Removing punctuation from column: {col}")

            # Create translation table to remove punctuation
            translator = str.maketrans('', '', string.punctuation)
            cleaned_data[col] = cleaned_data[col].astype(str).apply(
                lambda x: x.translate(translator)
            )

        return cleaned_data

    def convert_to_lowercase(self, data: pd.DataFrame,
                             columns: List[str]) -> pd.DataFrame:
        """
        Convert text in specified columns to lowercase.

        Args:
            data: Input DataFrame
            columns: List of columns to convert

        Returns:
            pd.DataFrame: Data with lowercase text
        """
        cleaned_data = data.copy()

        for col in columns:
            if col not in cleaned_data.columns:
                continue

            logger.info(f"Converting to lowercase: {col}")
            cleaned_data[col] = cleaned_data[col].astype(str).str.lower()

        return cleaned_data

    def remove_extra_whitespace(self, data: pd.DataFrame,
                                columns: List[str]) -> pd.DataFrame:
        """
        Remove extra whitespace from text columns.

        Args:
            data: Input DataFrame
            columns: List of columns to process

        Returns:
            pd.DataFrame: Data with normalized whitespace
        """
        cleaned_data = data.copy()

        for col in columns:
            if col not in cleaned_data.columns:
                continue

            logger.info(f"Removing extra whitespace from: {col}")

            # Remove extra whitespace and strip
            cleaned_data[col] = cleaned_data[col].astype(str).apply(
                lambda x: re.sub(r'\s+', ' ', x).strip()
            )

        return cleaned_data

    def remove_urls(self, data: pd.DataFrame,
                    columns: List[str]) -> pd.DataFrame:
        """
        Remove URLs from text columns.

        Args:
            data: Input DataFrame
            columns: List of columns to process

        Returns:
            pd.DataFrame: Data with URLs removed
        """
        cleaned_data = data.copy()
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

        for col in columns:
            if col not in cleaned_data.columns:
                continue

            logger.info(f"Removing URLs from: {col}")
            cleaned_data[col] = cleaned_data[col].astype(str).apply(
                lambda x: re.sub(url_pattern, '', x)
            )

        return cleaned_data

    def remove_mentions_hashtags(self, data: pd.DataFrame,
                                 columns: List[str]) -> pd.DataFrame:
        """
        Remove @mentions and #hashtags from text columns.

        Args:
            data: Input DataFrame
            columns: List of columns to process

        Returns:
            pd.DataFrame: Data with mentions and hashtags removed
        """
        cleaned_data = data.copy()

        for col in columns:
            if col not in cleaned_data.columns:
                continue

            logger.info(f"Removing mentions/hashtags from: {col}")

            # Remove @mentions and #hashtags
            cleaned_data[col] = cleaned_data[col].astype(str).apply(
                lambda x: re.sub(r'[@#]\w+', '', x)
            )

        return cleaned_data

    def keep_only_columns(self, data: pd.DataFrame,
                          columns_to_keep: List[str]) -> pd.DataFrame:
        """
        Keep only specified columns in the DataFrame.

        Args:
            data: Input DataFrame
            columns_to_keep: List of columns to retain

        Returns:
            pd.DataFrame: Data with only specified columns
        """
        # Check which columns exist
        existing_columns = [col for col in columns_to_keep if col in data.columns]
        missing_columns = [col for col in columns_to_keep if col not in data.columns]

        if missing_columns:
            logger.warning(f"Columns not found: {missing_columns}")

        logger.info(f"Keeping columns: {existing_columns}")

        return data[existing_columns].copy()

    def _clean_text_column(self, series: pd.Series) -> pd.Series:
        """
        Apply comprehensive text cleaning to a pandas Series.

        Args:
            series: Text data series

        Returns:
            pd.Series: Cleaned text series
        """
        # Convert to string and handle NaN values
        cleaned_series = series.astype(str)

        # Remove URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        cleaned_series = cleaned_series.apply(lambda x: re.sub(url_pattern, '', x))

        # Remove @mentions and #hashtags (optional - comment out if needed)
        # cleaned_series = cleaned_series.apply(lambda x: re.sub(r'[@#]\w+', '', x))

        # Remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        cleaned_series = cleaned_series.apply(lambda x: x.translate(translator))

        # Convert to lowercase
        cleaned_series = cleaned_series.str.lower()

        # Remove extra whitespace
        cleaned_series = cleaned_series.apply(lambda x: re.sub(r'\s+', ' ', x).strip())

        return cleaned_series

    def _log_cleaning_stats(self, original_data: pd.DataFrame,
                            cleaned_data: pd.DataFrame) -> None:
        """
        Log statistics about the cleaning process.

        Args:
            original_data: Original DataFrame
            cleaned_data: Cleaned DataFrame
        """
        original_rows = len(original_data)
        cleaned_rows = len(cleaned_data)
        rows_removed = original_rows - cleaned_rows

        logger.info(f"Cleaning complete:")
        logger.info(f"  Original rows: {original_rows:,}")
        logger.info(f"  Final rows: {cleaned_rows:,}")
        logger.info(f"  Rows removed: {rows_removed:,}")

        # Update cleaning stats
        self.cleaning_stats.update({
            'original_rows': original_rows,
            'cleaned_rows': cleaned_rows,
            'rows_removed': rows_removed
        })

    def get_cleaning_stats(self) -> Dict[str, Any]:
        """
        Get statistics from the last cleaning operation.

        Returns:
            Dict: Cleaning statistics
        """
        return self.cleaning_stats.copy()