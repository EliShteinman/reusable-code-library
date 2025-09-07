# ============================================================================
# shared-utilities/data_science/__init__.py - FIXED VERSION
# ============================================================================
"""
Data Science utilities - CLEAN ARCHITECTURE
Each module has a single, clear responsibility
"""

from .data_loader import UniversalDataLoader
from .text_cleaner import TextCleaner
from .text_analyzer import TextAnalyzer
from .sentiment_analyzer import SentimentAnalyzer

__all__ = [
    'UniversalDataLoader',  # File loading only
    'TextCleaner',  # Text cleaning only
    'TextAnalyzer',  # Text analysis only
    'SentimentAnalyzer'  # Sentiment analysis only
]


# Quick pipeline functions
def quick_text_analysis_pipeline(file_path: str, text_column: str, category_column: str = None):
    """
    Complete text analysis pipeline.

    Args:
        file_path: Path to data file
        text_column: Name of text column
        category_column: Optional category column for grouping

    Returns:
        Dict with cleaned data, analysis report, and info
    """
    # 1. Load data
    loader = UniversalDataLoader()
    df = loader.load_data(file_path)

    # 2. Clean text
    cleaner = TextCleaner()
    df_clean = cleaner.clean_dataframe(df, [text_column])
    df_clean = cleaner.remove_empty_texts(df_clean, [text_column])

    # 3. Analyze sentiment
    sentiment_analyzer = SentimentAnalyzer()
    df_analyzed = sentiment_analyzer.analyze_dataframe(df_clean, text_column)

    # 4. Text analysis
    analyzer = TextAnalyzer()
    report = analyzer.generate_summary_report(df_analyzed, text_column, category_column)

    return {
        'cleaned_data': df_analyzed,
        'analysis_report': report,
        'data_info': {
            'original_rows': len(df),
            'cleaned_rows': len(df_clean),
            'final_rows': len(df_analyzed)
        }
    }


def sentiment_analysis_pipeline(df, text_column: str):
    """Quick sentiment analysis pipeline."""
    analyzer = SentimentAnalyzer()
    return analyzer.analyze_dataframe(df, text_column, add_detailed=True)


def text_cleaning_pipeline(df, text_columns: list, **cleaning_options):
    """Quick text cleaning pipeline."""
    cleaner = TextCleaner()
    df_clean = cleaner.clean_dataframe(df, text_columns, **cleaning_options)
    return cleaner.remove_empty_texts(df_clean, text_columns)







