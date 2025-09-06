# shared-utilities/data_science/text_analyzer.py
import logging
from collections import Counter
from typing import Any, Dict, List, Optional, Set

import pandas as pd

logger = logging.getLogger(__name__)


class TextAnalyzer:
    """
    Comprehensive text analysis utility.
    Based on your generic_text_analysis.py patterns.
    """

    def __init__(self, min_word_length: int = 2):
        self.min_word_length = min_word_length

    def analyze_text_distribution(self,
                                  df: pd.DataFrame,
                                  text_column: str,
                                  category_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze text distribution by categories.
        """
        results = {
            'total_texts': len(df),
            'text_column': text_column
        }

        if category_column and category_column in df.columns:
            # Count by category
            category_counts = df[category_column].value_counts()
            results['by_category'] = category_counts.to_dict()

            # Calculate percentages
            total = len(df)
            results['category_percentages'] = {
                cat: round(count / total * 100, 2)
                for cat, count in category_counts.items()
            }

        return results

    def analyze_text_lengths(self,
                             df: pd.DataFrame,
                             text_column: str,
                             category_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze text lengths (characters and words).
        """
        # Add length columns
        df_analysis = df.copy()
        df_analysis['_char_length'] = df_analysis[text_column].astype(str).str.len()
        df_analysis['_word_count'] = df_analysis[text_column].astype(str).str.split().str.len()

        results = {
            'average_char_length': round(df_analysis['_char_length'].mean(), 2),
            'average_word_count': round(df_analysis['_word_count'].mean(), 2),
            'median_char_length': df_analysis['_char_length'].median(),
            'median_word_count': df_analysis['_word_count'].median(),
            'max_char_length': df_analysis['_char_length'].max(),
            'max_word_count': df_analysis['_word_count'].max(),
            'min_char_length': df_analysis['_char_length'].min(),
            'min_word_count': df_analysis['_word_count'].min()
        }

        if category_column and category_column in df_analysis.columns:
            category_stats = {}
            for category in df_analysis[category_column].dropna().unique():
                cat_data = df_analysis[df_analysis[category_column] == category]
                category_stats[str(category)] = {
                    'avg_char_length': round(cat_data['_char_length'].mean(), 2),
                    'avg_word_count': round(cat_data['_word_count'].mean(), 2),
                    'count': len(cat_data)
                }
            results['by_category'] = category_stats

        return results

    def find_common_words(self,
                          df: pd.DataFrame,
                          text_column: str,
                          top_n: int = 20,
                          exclude_words: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
        """
        Find most common words across all texts.
        """
        # Combine all text
        all_text = ' '.join(df[text_column].dropna().astype(str)).lower()

        # Remove punctuation and split
        import string
        translator = str.maketrans('', '', string.punctuation)
        clean_text = all_text.translate(translator)
        words = clean_text.split()

        # Filter words
        filtered_words = [
            word for word in words
            if len(word) >= self.min_word_length
               and word.isalpha()
               and (exclude_words is None or word not in exclude_words)
        ]

        # Count and return top N
        word_counts = Counter(filtered_words)

        return [
            {'word': word, 'count': count, 'frequency': round(count / len(filtered_words), 4)}
            for word, count in word_counts.most_common(top_n)
        ]

    def find_common_words_by_category(self,
                                      df: pd.DataFrame,
                                      text_column: str,
                                      category_column: str,
                                      top_n: int = 10,
                                      exclude_words: Optional[Set[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find common words for each category.
        """
        results = {}

        for category in df[category_column].dropna().unique():
            category_df = df[df[category_column] == category]
            category_words = self.find_common_words(
                category_df, text_column, top_n, exclude_words
            )
            results[str(category)] = category_words

        return results

    def find_longest_texts(self,
                           df: pd.DataFrame,
                           text_column: str,
                           top_n: int = 5,
                           by_words: bool = True,
                           category_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Find longest texts by word count or character count.
        """
        df_analysis = df.copy()

        if by_words:
            df_analysis['_length'] = df_analysis[text_column].astype(str).str.split().str.len()
            length_type = 'word_count'
        else:
            df_analysis['_length'] = df_analysis[text_column].astype(str).str.len()
            length_type = 'char_count'

        results = {'length_type': length_type}

        if category_column and category_column in df_analysis.columns:
            # Longest by category
            for category in df_analysis[category_column].dropna().unique():
                cat_data = df_analysis[df_analysis[category_column] == category]
                longest_texts = cat_data.nlargest(top_n, '_length')

                results[str(category)] = [
                    {
                        'text': text[:200] + '...' if len(text) > 200 else text,
                        'length': length,
                        'full_text': text
                    }
                    for text, length in zip(
                        longest_texts[text_column].tolist(),
                        longest_texts['_length'].tolist()
                    )
                ]
        else:
            # Overall longest
            longest_texts = df_analysis.nlargest(top_n, '_length')
            results['overall'] = [
                {
                    'text': text[:200] + '...' if len(text) > 200 else text,
                    'length': length,
                    'full_text': text
                }
                for text, length in zip(
                    longest_texts[text_column].tolist(),
                    longest_texts['_length'].tolist()
                )
            ]

        return results

    def analyze_text_patterns(self,
                              df: pd.DataFrame,
                              text_column: str) -> Dict[str, Any]:
        """
        Analyze various text patterns.
        """
        texts = df[text_column].dropna().astype(str)

        # Count various patterns
        results = {
            'total_texts': len(texts),
            'texts_with_urls': sum(1 for text in texts if 'http' in text.lower()),
            'texts_with_emails': sum(1 for text in texts if '@' in text and '.' in text),
            'texts_with_mentions': sum(1 for text in texts if '@' in text),
            'texts_with_hashtags': sum(1 for text in texts if '#' in text),
            'texts_with_numbers': sum(1 for text in texts if any(char.isdigit() for char in text)),
            'texts_all_caps': sum(1 for text in texts if text.isupper() and len(text) > 5)
        }

        # Calculate percentages
        total = len(texts)
        for key, value in results.items():
            if key != 'total_texts':
                results[f'{key}_percentage'] = round(value / total * 100, 2)

        return results

    def keyword_analysis(self,
                         df: pd.DataFrame,
                         text_column: str,
                         keywords: List[str],
                         case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Analyze presence of specific keywords.
        """
        results = {'keywords_analyzed': keywords}
        keyword_stats = {}

        for keyword in keywords:
            if case_sensitive:
                mask = df[text_column].astype(str).str.contains(keyword, na=False)
            else:
                mask = df[text_column].astype(str).str.lower().str.contains(keyword.lower(), na=False)

            count = mask.sum()
            percentage = round(count / len(df) * 100, 2)

            keyword_stats[keyword] = {
                'count': int(count),
                'percentage': percentage,
                'texts_with_keyword': df[mask][text_column].tolist()[:5]  # First 5 examples
            }

        results['keyword_stats'] = keyword_stats
        return results

    def generate_summary_report(self,
                                df: pd.DataFrame,
                                text_column: str,
                                category_column: Optional[str] = None,
                                keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive text analysis report.
        """
        report = {
            'dataset_info': {
                'total_texts': len(df),
                'text_column': text_column,
                'category_column': category_column
            }
        }

        # Basic distribution
        report['distribution'] = self.analyze_text_distribution(df, text_column, category_column)

        # Length analysis
        report['length_analysis'] = self.analyze_text_lengths(df, text_column, category_column)

        # Common words
        report['common_words'] = self.find_common_words(df, text_column, top_n=15)

        if category_column:
            report['common_words_by_category'] = self.find_common_words_by_category(
                df, text_column, category_column, top_n=10
            )

        # Longest texts
        report['longest_texts'] = self.find_longest_texts(df, text_column, top_n=3, category_column=category_column)

        # Pattern analysis
        report['text_patterns'] = self.analyze_text_patterns(df, text_column)

        # Keyword analysis if provided
        if keywords:
            report['keyword_analysis'] = self.keyword_analysis(df, text_column, keywords)

        return report