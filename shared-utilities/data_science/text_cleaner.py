
# ============================================================================
# shared-utilities/data_science/text_cleaner.py - TEXT CLEANING ONLY
# ============================================================================
import re
import string
from typing import List, Optional, Set
import logging

import pandas as pd

logger = logging.getLogger(__name__)


class TextCleaner:
    """
    Text cleaning utility - TEXT CLEANING ONLY
    Comprehensive text preprocessing and cleaning operations
    """

    def __init__(self):
        self.cleaning_stats = {}

    def clean_text(self,
                   text: str,
                   remove_urls: bool = True,
                   remove_emails: bool = True,
                   remove_mentions: bool = False,
                   remove_hashtags: bool = False,
                   remove_punctuation: bool = True,
                   to_lowercase: bool = True,
                   remove_extra_whitespace: bool = True,
                   remove_numbers: bool = False,
                   remove_special_chars: bool = False,
                   custom_replacements: dict = None) -> str:
        """
        Clean individual text with comprehensive options.

        Args:
            text: Input text to clean
            remove_urls: Remove HTTP/HTTPS URLs
            remove_emails: Remove email addresses
            remove_mentions: Remove @mentions
            remove_hashtags: Remove #hashtags
            remove_punctuation: Remove punctuation marks
            to_lowercase: Convert to lowercase
            remove_extra_whitespace: Remove extra spaces and line breaks
            remove_numbers: Remove numeric digits
            remove_special_chars: Remove special characters
            custom_replacements: Dictionary of custom text replacements

        Returns:
            Cleaned text string
        """
        if not isinstance(text, str) or not text.strip():
            return ""

        cleaned = text

        # Custom replacements first
        if custom_replacements:
            for old, new in custom_replacements.items():
                cleaned = cleaned.replace(old, new)

        # Remove URLs
        if remove_urls:
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            cleaned = re.sub(url_pattern, '', cleaned)

        # Remove emails
        if remove_emails:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            cleaned = re.sub(email_pattern, '', cleaned)

        # Remove @mentions
        if remove_mentions:
            cleaned = re.sub(r'@\w+', '', cleaned)

        # Remove #hashtags
        if remove_hashtags:
            cleaned = re.sub(r'#\w+', '', cleaned)

        # Remove numbers
        if remove_numbers:
            cleaned = re.sub(r'\d+', '', cleaned)

        # Remove special characters (but keep letters and spaces)
        if remove_special_chars:
            cleaned = re.sub(r'[^a-zA-Z\s]', '', cleaned)

        # Remove punctuation
        if remove_punctuation and not remove_special_chars:  # Avoid double removal
            translator = str.maketrans('', '', string.punctuation)
            cleaned = cleaned.translate(translator)

        # Convert to lowercase
        if to_lowercase:
            cleaned = cleaned.lower()

        # Remove extra whitespace
        if remove_extra_whitespace:
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

    def clean_dataframe(self,
                        df: pd.DataFrame,
                        text_columns: List[str],
                        **cleaning_options) -> pd.DataFrame:
        """
        Clean text columns in DataFrame.

        Args:
            df: Input DataFrame
            text_columns: List of column names to clean
            **cleaning_options: Options for clean_text method

        Returns:
            DataFrame with cleaned text columns
        """
        cleaned_df = df.copy()

        for col in text_columns:
            if col not in cleaned_df.columns:
                logger.warning(f"Column '{col}' not found in DataFrame")
                continue

            logger.info(f"Cleaning column: {col}")

            # Track cleaning stats
            original_count = len(cleaned_df[col].dropna())

            cleaned_df[col] = cleaned_df[col].astype(str).apply(
                lambda x: self.clean_text(x, **cleaning_options)
            )

            # Update stats
            cleaned_count = len(cleaned_df[col].dropna())
            self.cleaning_stats[col] = {
                'original_count': original_count,
                'cleaned_count': cleaned_count,
                'cleaning_options': cleaning_options
            }

        return cleaned_df

    def remove_duplicates(self,
                          df: pd.DataFrame,
                          text_column: str,
                          keep: str = 'first') -> pd.DataFrame:
        """Remove duplicate texts."""
        initial_count = len(df)
        cleaned_df = df.drop_duplicates(subset=[text_column], keep=keep)
        removed_count = initial_count - len(cleaned_df)

        logger.info(f"Removed {removed_count:,} duplicate texts")
        return cleaned_df

    def filter_by_length(self,
                         df: pd.DataFrame,
                         text_column: str,
                         min_length: int = 1,
                         max_length: Optional[int] = None,
                         by_chars: bool = True) -> pd.DataFrame:
        """
        Filter texts by length.

        Args:
            df: Input DataFrame
            text_column: Text column name
            min_length: Minimum length
            max_length: Maximum length (None for no limit)
            by_chars: If True, filter by character count; if False, by word count

        Returns:
            Filtered DataFrame
        """
        initial_count = len(df)

        if by_chars:
            # Filter by character length
            df['_text_length'] = df[text_column].astype(str).str.len()
        else:
            # Filter by word count
            df['_text_length'] = df[text_column].astype(str).str.split().str.len()

        # Apply filters
        mask = df['_text_length'] >= min_length
        if max_length:
            mask &= df['_text_length'] <= max_length

        filtered_df = df[mask].drop(columns=['_text_length'])
        removed_count = initial_count - len(filtered_df)

        length_type = "characters" if by_chars else "words"
        logger.info(f"Filtered out {removed_count:,} texts by {length_type} length")
        return filtered_df

    def remove_empty_texts(self,
                           df: pd.DataFrame,
                           text_columns: List[str]) -> pd.DataFrame:
        """Remove rows with empty text in any specified column."""
        initial_count = len(df)

        # Remove rows where any text column is empty
        mask = pd.Series([True] * len(df), index=df.index)
        for col in text_columns:
            if col in df.columns:
                mask &= (df[col].astype(str).str.strip() != '') & df[col].notna()

        cleaned_df = df[mask]
        removed_count = initial_count - len(cleaned_df)

        logger.info(f"Removed {removed_count:,} rows with empty text")
        return cleaned_df

    def remove_short_texts(self,
                           df: pd.DataFrame,
                           text_column: str,
                           min_words: int = 3) -> pd.DataFrame:
        """Remove texts with fewer than minimum words."""
        return self.filter_by_length(df, text_column, min_words, by_chars=False)

    def normalize_whitespace(self, df: pd.DataFrame, text_columns: List[str]) -> pd.DataFrame:
        """Normalize whitespace in text columns."""
        df_normalized = df.copy()

        for col in text_columns:
            if col in df_normalized.columns:
                df_normalized[col] = df_normalized[col].astype(str).apply(
                    lambda x: re.sub(r'\s+', ' ', x).strip()
                )

        return df_normalized

    def remove_non_printable(self, df: pd.DataFrame, text_columns: List[str]) -> pd.DataFrame:
        """Remove non-printable characters from text."""
        df_clean = df.copy()

        for col in text_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).apply(
                    lambda x: ''.join(char for char in x if char.isprintable())
                )

        return df_clean

    def get_cleaning_stats(self) -> dict:
        """Get statistics from last cleaning operation."""
        return self.cleaning_stats