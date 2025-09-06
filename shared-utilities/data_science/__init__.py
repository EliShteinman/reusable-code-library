# shared-utilities/data_science/__init__.py
"""
Data Science utilities for text analysis and data processing.
"""

from .data_loader import UniversalDataLoader
from .text_cleaner import TextCleaner
from .text_analyzer import TextAnalyzer
from .sentiment_analyzer import SentimentAnalyzer

__all__ = [
    'UniversalDataLoader',
    'TextCleaner',
    'TextAnalyzer',
    'SentimentAnalyzer'
]


# Usage Examples:

def quick_text_analysis_pipeline(file_path: str, text_column: str, category_column: str = None):
    """
    Quick pipeline for comprehensive text analysis.

    Example:
        results = quick_text_analysis_pipeline("data.csv", "text", "category")
    """
    # Load data
    loader = UniversalDataLoader()
    df = loader.load_data(file_path)

    # Clean text
    cleaner = TextCleaner()
    df_clean = cleaner.clean_dataframe(df, [text_column])
    df_clean = cleaner.remove_empty_texts(df_clean, [text_column])

    # Analyze sentiment
    sentiment_analyzer = SentimentAnalyzer()
    df_analyzed = sentiment_analyzer.analyze_dataframe(df_clean, text_column)

    # Text analysis
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
    """
    Quick sentiment analysis pipeline.
    """
    analyzer = SentimentAnalyzer()
    return analyzer.analyze_dataframe(df, text_column, add_detailed=True)