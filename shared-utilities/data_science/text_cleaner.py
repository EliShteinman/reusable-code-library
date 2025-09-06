# shared-utilities/data_science/text_cleaner.py
import re
import string
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

import pandas as pd


class TextCleaner:
    """
    Comprehensive text cleaning utility.
    Based on your app/utils patterns but enhanced.
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
                   remove_numbers: bool = False) -> str:
        """
        Clean individual text with various options.
        """
        if not isinstance(text, str) or not text.strip():
            return ""

        cleaned = text

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

        # Remove punctuation
        if remove_punctuation:
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
        """
        cleaned_df = df.copy()

        for col in text_columns:
            if col not in cleaned_df.columns:
                continue

            logger.info(f"Cleaning column: {col}")
            cleaned_df[col] = cleaned_df[col].astype(str).apply(
                lambda x: self.clean_text(x, **cleaning_options)
            )

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
                         max_length: Optional[int] = None) -> pd.DataFrame:
        """Filter texts by character length."""
        initial_count = len(df)

        # Calculate text lengths
        df['_text_length'] = df[text_column].astype(str).str.len()

        # Apply filters
        mask = df['_text_length'] >= min_length
        if max_length:
            mask &= df['_text_length'] <= max_length

        filtered_df = df[mask].drop(columns=['_text_length'])
        removed_count = initial_count - len(filtered_df)

        logger.info(f"Filtered out {removed_count:,} texts by length")
        return filtered_df

    def filter_by_word_count(self,
                             df: pd.DataFrame,
                             text_column: str,
                             min_words: int = 1,
                             max_words: Optional[int] = None) -> pd.DataFrame:
        """Filter texts by word count."""
        initial_count = len(df)

        # Calculate word counts
        df['_word_count'] = df[text_column].astype(str).str.split().str.len()

        # Apply filters
        mask = df['_word_count'] >= min_words
        if max_words:
            mask &= df['_word_count'] <= max_words

        filtered_df = df[mask].drop(columns=['_word_count'])
        removed_count = initial_count - len(filtered_df)

        logger.info(f"Filtered out {removed_count:,} texts by word count")
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
