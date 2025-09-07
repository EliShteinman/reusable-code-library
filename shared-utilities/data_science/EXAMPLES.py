
# ============================================================================
# USAGE EXAMPLES - CLEAN SEPARATION
# ============================================================================

def example_complete_pipeline():
    """Example: Complete text analysis pipeline"""

    # Sample data
    import pandas as pd

    sample_data = pd.DataFrame({
        'text': [
            "This is a great product! I love it so much.",
            "Terrible quality, would not recommend to anyone.",
            "Average product, nothing special but does the job.",
            "AMAZING!!! Best purchase ever made! 5 stars!",
            "Poor customer service, product arrived damaged.",
            "Good value for money, satisfied with purchase.",
            "Not worth the price, quality is questionable.",
            "Excellent quality and fast shipping, very happy!",
            "Okay product but could be better for the price.",
            "Outstanding! Exceeded all my expectations!"
        ],
        'category': ['electronics', 'electronics', 'books', 'electronics', 'clothing',
                     'books', 'clothing', 'electronics', 'books', 'electronics'],
        'rating': [5, 1, 3, 5, 2, 4, 2, 5, 3, 5]
    })

    print("=== Complete Text Analysis Pipeline ===")

    # 1. Load data (simulation)
    loader = UniversalDataLoader()
    # df = loader.load_data("reviews.csv")  # In real scenario
    df = sample_data

    # 2. Clean text
    cleaner = TextCleaner()
    df_clean = cleaner.clean_dataframe(df, ['text'],
                                       remove_punctuation=True,
                                       to_lowercase=True,
                                       remove_extra_whitespace=True)

    # 3. Remove short/empty texts
    df_clean = cleaner.remove_empty_texts(df_clean, ['text'])
    df_clean = cleaner.filter_by_length(df_clean, 'text', min_length=5, by_chars=False)

    print(f"Data cleaning: {len(df)} → {len(df_clean)} texts")

    # 4. Analyze sentiment
    sentiment_analyzer = SentimentAnalyzer()
    df_analyzed = sentiment_analyzer.analyze_dataframe(df_clean, 'text', add_detailed=True)

    # 5. Text analysis
    analyzer = TextAnalyzer()

    # Basic analysis
    distribution = analyzer.analyze_text_distribution(df_analyzed, 'text', 'category')
    print(f"Distribution by category: {distribution['by_category']}")

    # Length analysis
    lengths = analyzer.analyze_text_lengths(df_analyzed, 'text', 'category')
    print(f"Average text length: {lengths['average_word_count']} words")

    # Common words
    common_words = analyzer.find_common_words(df_analyzed, 'text', top_n=10)
    print(f"Top 5 words: {[w['word'] for w in common_words[:5]]}")

    # Keyword analysis
    keywords = ['good', 'great', 'terrible', 'amazing', 'poor']
    keyword_results = analyzer.keyword_analysis(df_analyzed, 'text', keywords)

    for keyword, stats in keyword_results['keyword_stats'].items():
        print(f"'{keyword}': {stats['count']} occurrences ({stats['percentage']}%)")

    # 6. Generate comprehensive report
    full_report = analyzer.generate_summary_report(df_analyzed, 'text', 'category', keywords)

    return df_analyzed, full_report


def example_sentiment_analysis():
    """Example: Sentiment analysis"""

    import pandas as pd

    # Sample data
    reviews = pd.DataFrame({
        'review_text': [
            "I absolutely love this product! Best purchase ever!",
            "Terrible quality, waste of money.",
            "It's okay, nothing special.",
            "Great value for the price, very satisfied.",
            "Poor customer service, disappointed."
        ],
        'product': ['laptop', 'phone', 'tablet', 'laptop', 'phone']
    })

    print("=== Sentiment Analysis Example ===")

    # Initialize sentiment analyzer
    sentiment_analyzer = SentimentAnalyzer()

    # Analyze sentiment
    df_with_sentiment = sentiment_analyzer.analyze_dataframe(
        reviews, 'review_text', add_detailed=True
    )

    # Display results
    for idx, row in df_with_sentiment.iterrows():
        print(f"Review: {row['review_text'][:50]}...")
        print(f"Sentiment: {row['sentiment_label']} (score: {row['sentiment_score']:.3f})")
        print(f"Detailed: pos={row['sentiment_positive']:.2f}, neg={row['sentiment_negative']:.2f}")
        print("---")

    # Get sentiment statistics
    scores = df_with_sentiment['sentiment_score'].tolist()
    stats = sentiment_analyzer.get_sentiment_statistics(scores)

    print(f"Sentiment Statistics:")
    print(f"Positive: {stats['positive_count']} ({stats['positive_percentage']}%)")
    print(f"Negative: {stats['negative_count']} ({stats['negative_percentage']}%)")
    print(f"Neutral: {stats['neutral_count']} ({stats['neutral_percentage']}%)")
    print(f"Average score: {stats['average_score']}")

    return df_with_sentiment


def example_text_cleaning():
    """Example: Advanced text cleaning"""

    import pandas as pd

    # Messy sample data
    messy_data = pd.DataFrame({
        'text': [
            "Check out this AMAZING deal!!! http://example.com #sale @mention",
            "Contact us at: support@company.com for more info!!!",
            "   LOTS   OF   WHITESPACE   AND   CAPS   ",
            "Mixed 123 numbers and @symbols #hashtags",
            "",  # Empty text
            "Normal text without issues.",
            "!!!!!Special characters everywhere!!!!!"
        ]
    })

    print("=== Text Cleaning Example ===")

    cleaner = TextCleaner()

    # Show original
    print("Original texts:")
    for i, text in enumerate(messy_data['text']):
        print(f"{i}: '{text}'")

    # Clean with different options
    df_cleaned = cleaner.clean_dataframe(
        messy_data,
        ['text'],
        remove_urls=True,
        remove_emails=True,
        remove_mentions=True,
        remove_hashtags=True,
        remove_punctuation=True,
        to_lowercase=True,
        remove_extra_whitespace=True,
        remove_numbers=True
    )

    # Remove empty texts
    df_cleaned = cleaner.remove_empty_texts(df_cleaned, ['text'])

    print("\nCleaned texts:")
    for i, text in enumerate(df_cleaned['text']):
        print(f"{i}: '{text}'")

    # Show cleaning stats
    stats = cleaner.get_cleaning_stats()
    print(f"\nCleaning stats: {stats}")

    return df_cleaned


if __name__ == "__main__":
    print("Running Data Science utilities examples...\n")

    # Complete pipeline
    analyzed_data, report = example_complete_pipeline()

    print("\n" + "=" * 50 + "\n")

    # Sentiment analysis
    sentiment_results = example_sentiment_analysis()

    print("\n" + "=" * 50 + "\n")

    # Text cleaning
    cleaned_data = example_text_cleaning()

    print("\nAll Data Science examples completed successfully!")