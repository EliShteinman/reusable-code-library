# ============================================================================
# shared-utilities/data_science/examples_advanced.py - FUTURE-PROOF EXAMPLES
# ============================================================================
"""
Advanced examples demonstrating generic architecture
Perfect for handling unknown exam scenarios
"""

import pandas as pd
from datetime import datetime
import logging

# Import the new generic architecture
from . import (
    # Original (for backward compatibility)
    UniversalDataLoader, TextCleaner, TextAnalyzer, SentimentAnalyzer,

    # New generic architecture
    ProcessorFactory, ProcessingConfig,
    SmartSentimentAnalyzer, SmartTextProcessor,
    get_best_available_sentiment_analyzer, get_best_available_text_processor,
    extract_comprehensive_features, analyze_text_with_multiple_tools,
    handle_unknown_library_scenario, exam_mode_analysis,

    # Pipeline functions
    quick_text_analysis_pipeline, sentiment_analysis_pipeline,
    text_cleaning_pipeline, create_exam_safe_pipeline
)

logger = logging.getLogger(__name__)


# ============================================================================
# Example 1: Exam Scenario - Unknown Library Required
# ============================================================================

def example_exam_unknown_library():
    """
    Example: Exam asks for TextBlob but you only have VADER
    Shows how generic architecture handles this gracefully
    """
    print("=== Exam Scenario: Unknown Library Handling ===")

    # Sample exam question: "Use TextBlob to analyze sentiment of this text"
    exam_text = "I absolutely love this new smartphone! The camera quality is amazing and the battery lasts all day."

    # Try TextBlob first, fallback if not available
    print("1. Exam requires 'TextBlob' for sentiment analysis:")

    try:
        # This will try TextBlob, fallback to available alternatives
        result = handle_unknown_library_scenario("textblob", "sentiment", exam_text)

        print(f"   ✅ Analysis completed using: {result.get('analyzer', 'unknown')}")
        print(f"   Sentiment: {result['label']} (score: {result['compound']:.3f})")

        if result.get('actual_library') != 'textblob':
            print(f"   ⚠️  TextBlob not available, used {result.get('actual_library')} instead")

    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Example 2: Exam asks for spaCy lemmatization
    print("\n2. Exam requires 'spaCy' for lemmatization:")

    try:
        lemmas = handle_unknown_library_scenario("spacy", "lemmatization", exam_text)
        print(f"   ✅ Lemmas extracted: {lemmas[:10]}...")  # Show first 10

    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Example 3: Comprehensive exam requirements
    print("\n3. Complex exam requirements:")

    exam_requirements = {
        'sentiment': 'vader',  # Specific sentiment analyzer
        'stemming': 'nltk',  # Specific stemming
        'lemmatization': 'spacy',  # Specific lemmatization
        'language': 'english'  # Language specification
    }

    results = exam_mode_analysis(exam_text, exam_requirements)

    print("   Requirements vs Reality:")
    for requirement, value in exam_requirements.items():
        actual_result = results['results'].get(requirement, {})
        if requirement in results['alternatives_used']:
            print(f"   - {requirement}: requested {value}, used {results['alternatives_used'][requirement]}")
        else:
            print(f"   - {requirement}: ✅ {value} as requested")

    print(f"   Available tools: {results['available_tools']}")

    return results


# ============================================================================
# Example 2: Multi-Library Comparison
# ============================================================================

def example_multi_library_comparison():
    """
    Example: Compare results from multiple sentiment libraries
    Shows robustness and ensemble approaches
    """
    print("\n=== Multi-Library Comparison ===")

    test_texts = [
        "I love this product! It's absolutely fantastic!",
        "This is terrible. Worst purchase ever.",
        "It's okay, nothing special but does the job.",
        "המוצר הזה מעולה! אני מאוד מרוצה מהקנייה.",  # Hebrew positive
        "זה היה רע מאוד, לא מומלץ."  # Hebrew negative
    ]

    print("Comparing sentiment analyzers across multiple texts:")

    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Text: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")

        # Analyze with multiple tools
        comparison = analyze_text_with_multiple_tools(
            text,
            sentiment_analyzers=["vader", "textblob", "hebrew", "fallback"],
            text_processors=["nltk", "spacy", "hebrew", "basic"]
        )

        # Show sentiment comparison
        print("   Sentiment Analysis:")
        for analyzer, result in comparison['sentiment_analysis'].items():
            if 'error' not in result:
                label = result.get('label', 'unknown')
                score = result.get('compound', 0)
                analyzer_name = result.get('analyzer', analyzer)
                print(f"     {analyzer}: {label} ({score:.3f}) [{analyzer_name}]")
            else:
                print(f"     {analyzer}: ❌ {result['error']}")

        # Show consensus
        if 'consensus' in comparison:
            consensus = comparison['consensus']
            avg_sentiment = consensus.get('avg_sentiment', 0)
            majority_label = consensus.get('majority_label', 'unknown')
            print(f"   Consensus: {majority_label} (avg: {avg_sentiment:.3f})")

    return comparison


# ============================================================================
# Example 3: Hebrew Text Processing
# ============================================================================

def example_hebrew_processing():
    """
    Example: Hebrew text processing with roots and stems
    """
    print("\n=== Hebrew Text Processing ===")

    hebrew_texts = [
        "אני אוהב את הטכנולוגיה החדשה הזו",
        "המחשב הזה עובד מצוין ומהיר מאוד",
        "השירות היה רע ולא מקצועי בכלל",
        "מומלץ מאוד לקנות את המוצר הזה"
    ]

    # Get Hebrew processor
    hebrew_processor = ProcessorFactory.create_text_processor("hebrew")
    hebrew_sentiment = ProcessorFactory.create_sentiment_analyzer("hebrew")

    print("Processing Hebrew texts:")

    for i, text in enumerate(hebrew_texts, 1):
        print(f"\n{i}. \"{text}\"")

        # Comprehensive feature extraction
        features = extract_comprehensive_features(
            text,
            language="hebrew",
            include_sentiment=True,
            include_stems=True,
            include_roots=True
        )

        print(f"   Language: {features.get('detected_language', 'unknown')}")
        print(f"   Tokens: {features.get('tokens', [])}")
        print(f"   Stems: {features.get('stems', [])}")
        print(f"   Roots: {features.get('roots', [])}")

        sentiment = features.get('sentiment', {})
        if sentiment:
            print(f"   Sentiment: {sentiment.get('label', 'unknown')} ({sentiment.get('compound', 0):.3f})")

    return features


# ============================================================================
# Example 4: Exam-Safe Pipeline
# ============================================================================

def example_exam_safe_pipeline():
    """
    Example: Create pipeline that works in any exam environment
    """
    print("\n=== Exam-Safe Pipeline ===")

    # Create sample data that might appear in exam
    exam_data = pd.DataFrame({
        'review_text': [
            "This laptop is amazing! Great performance and battery life.",
            "Poor quality product. Broke after one week of use.",
            "Average phone, nothing extraordinary but functional.",
            "Excellent customer service and fast shipping!",
            "Overpriced for what you get. Not recommended.",
            "Perfect for students. Lightweight and reliable.",
            "Terrible experience. Product arrived damaged.",
            "Good value for money. Satisfied with purchase.",
            "Outstanding quality! Exceeded my expectations.",
            "Okay product but could be better for the price."
        ],
        'product_category': ['electronics', 'electronics', 'electronics', 'electronics', 'electronics',
                             'electronics', 'electronics', 'electronics', 'electronics', 'electronics'],
        'rating': [5, 1, 3, 5, 2, 4, 1, 4, 5, 3]
    })

    print("1. Creating exam-safe configuration:")

    # Create configuration that works regardless of available libraries
    config = create_exam_safe_pipeline(
        preferred_sentiment="vader",
        preferred_processor="nltk"
    )

    print(f"   Configuration: {config.to_dict()}")

    print("\n2. Running comprehensive analysis pipeline:")

    # Run analysis with automatic fallbacks
    results = quick_text_analysis_pipeline(
        data=exam_data,
        text_column="review_text",
        category_column="product_category",
        config=config
    )

    processing_info = results.get('processing_info', {})
    print(f"   ✅ Analysis completed successfully!")
    print(f"   Sentiment analyzer used: {processing_info.get('sentiment_analyzer_used', 'unknown')}")
    print(f"   Text processor used: {processing_info.get('text_processor_used', 'unknown')}")
    print(f"   Processed: {processing_info.get('final_rows', 0)} texts")

    # Show sample results
    if 'cleaned_data' in results:
        df_result = results['cleaned_data']
        sentiment_distribution = df_result['sentiment_label'].value_counts()
        print(f"   Sentiment distribution: {sentiment_distribution.to_dict()}")

        avg_sentiment = df_result['sentiment_score'].mean()
        print(f"   Average sentiment score: {avg_sentiment:.3f}")

    print("\n3. Testing with different requirements:")

    # Test different scenarios
    scenarios = [
        {"sentiment_analyzer": "textblob", "text_processor": "spacy"},
        {"sentiment_analyzer": "vader", "text_processor": "nltk"},
        {"sentiment_analyzer": "fallback", "text_processor": "basic"}
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"   Scenario {i}: {scenario}")
        try:
            test_config = ProcessingConfig(**scenario)
            test_result = quick_text_analysis_pipeline(
                data=exam_data.head(3),  # Small sample
                text_column="review_text",
                config=test_config
            )

            test_info = test_result.get('processing_info', {})
            print(f"     ✅ Success with {test_info.get('sentiment_analyzer_used', 'unknown')}")

        except Exception as e:
            print(f"     ❌ Failed: {e}")

    return results


# ============================================================================
# Example 5: Real-World Text Analysis
# ============================================================================

def example_real_world_analysis():
    """
    Example: Real-world text analysis combining everything
    """
    print("\n=== Real-World Text Analysis ===")

    # Simulate loading data (could be from CSV, JSON, etc.)
    loader = UniversalDataLoader()

    # Create realistic social media data
    social_media_data = pd.DataFrame({
        'post_text': [
            "Just bought the new iPhone 15! The camera quality is absolutely stunning 📸 #Apple #iPhone15",
            "Worst customer service ever @BadCompany. Waited 2 hours just to be hung up on 😡",
            "Having a great day at the beach with family 🏖️ #weekend #blessed",
            "This coffee shop has amazing WiFi and the best latte in town ☕ highly recommend!",
            "Traffic is horrible today... been stuck for 45 minutes 🚗 #MondayMorning",
            "Thank you @GoodCompany for the quick resolution to my issue! Great support team 👍",
            "Movie night with friends watching the new Marvel film 🎬 #Marvel #MovieNight",
            "ארוחת בוקר מושלמת במסעדה החדשה בתל אביב! מומלץ בחום 🍳",  # Hebrew
            "Frustrated with my laptop constantly freezing... need a new one ASAP 💻",
            "Beautiful sunset from my balcony tonight 🌅 nature is amazing!"
        ],
        'platform': ['twitter', 'twitter', 'instagram', 'facebook', 'twitter',
                     'twitter', 'instagram', 'facebook', 'twitter', 'instagram'],
        'user_type': ['consumer', 'consumer', 'personal', 'consumer', 'personal',
                      'consumer', 'personal', 'consumer', 'consumer', 'personal'],
        'timestamp': pd.date_range('2024-01-01', periods=10, freq='D'),
        'engagement': [150, 45, 230, 67, 23, 89, 180, 34, 12, 145]
    })

    print("1. Multi-platform social media analysis:")
    print(f"   Analyzing {len(social_media_data)} posts from different platforms")

    # Comprehensive analysis pipeline
    results = quick_text_analysis_pipeline(
        data=social_media_data,
        text_column="post_text",
        category_column="platform",
        sentiment_analyzer="auto",
        text_processor="auto"
    )

    if 'cleaned_data' in results:
        df_analyzed = results['cleaned_data']

        # Platform-wise sentiment analysis
        platform_sentiment = df_analyzed.groupby('platform').agg({
            'sentiment_score': ['mean', 'count'],
            'sentiment_label': lambda x: x.value_counts().to_dict()
        }).round(3)

        print("\n   Platform sentiment analysis:")
        for platform in df_analyzed['platform'].unique():
            platform_data = df_analyzed[df_analyzed['platform'] == platform]
            avg_sentiment = platform_data['sentiment_score'].mean()
            sentiment_dist = platform_data['sentiment_label'].value_counts()
            print(f"     {platform}: avg_sentiment={avg_sentiment:.3f}, distribution={sentiment_dist.to_dict()}")

        # Language detection and processing
        print("\n2. Language-specific processing:")

        for idx, row in df_analyzed.iterrows():
            text = row['post_text']

            # Extract comprehensive features
            features = extract_comprehensive_features(
                text,
                language="auto",
                include_sentiment=True,
                include_stems=True,
                include_roots=True
            )

            detected_lang = features.get('detected_language', 'unknown')
            sentiment = features.get('sentiment', {})

            print(
                f"     Post {idx + 1}: {detected_lang} | {sentiment.get('label', 'unknown')} ({sentiment.get('compound', 0):.2f})")

            # Show linguistic features for interesting posts
            if detected_lang == 'hebrew' or sentiment.get('compound', 0) > 0.5:
                if 'stems' in features and features['stems']:
                    print(f"       Stems: {features['stems'][:5]}...")
                if 'roots' in features and features['roots']:
                    print(f"       Roots: {features['roots'][:5]}...")

    print("\n3. Engagement vs Sentiment correlation:")

    if 'cleaned_data' in results:
        # Analyze correlation between sentiment and engagement
        correlation = df_analyzed['sentiment_score'].corr(df_analyzed['engagement'])
        print(f"   Sentiment-Engagement correlation: {correlation:.3f}")

        # High engagement posts analysis
        high_engagement = df_analyzed[df_analyzed['engagement'] > df_analyzed['engagement'].median()]
        avg_sentiment_high_eng = high_engagement['sentiment_score'].mean()
        print(f"   Average sentiment of high-engagement posts: {avg_sentiment_high_eng:.3f}")

    return results


# ============================================================================
# Example 6: Performance and Fallback Testing
# ============================================================================

def example_performance_testing():
    """
    Example: Test performance and fallback mechanisms
    """
    print("\n=== Performance and Fallback Testing ===")

    import time

    # Test texts of different lengths and languages
    test_cases = [
        ("Short", "Great product!"),
        ("Medium",
         "This smartphone has excellent battery life and camera quality. I'm very satisfied with my purchase and would recommend it to others."),
        ("Long",
         "After using this laptop for three months, I can confidently say it's one of the best investments I've made. The processing speed is remarkable, handling multiple applications simultaneously without any lag. The build quality feels premium with its aluminum finish, and the keyboard is comfortable for long typing sessions. The display is crisp and vibrant, making it perfect for both work and entertainment. Battery life easily lasts a full workday, which is crucial for my mobile lifestyle. Customer support has been responsive and helpful whenever I had questions. Overall, this product exceeds expectations and offers excellent value for money."),
        ("Hebrew",
         "המוצר הזה פשוט מדהים! איכות בנייה מעולה, ביצועים מהירים, ושירות לקוחות אדיב ומקצועי. בהחלט שווה את הכסף."),
        ("Mixed",
         "I love this café! ☕ Great atmosphere and the barista makes amazing latte art. המקום הכי טוב בעיר! #coffee #weekend")
    ]

    print("1. Testing different analyzers on various text types:")

    analyzers_to_test = ["auto", "vader", "textblob", "hebrew", "fallback"]

    for text_type, text in test_cases:
        print(f"\n   {text_type} text: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")

        for analyzer_name in analyzers_to_test:
            try:
                start_time = time.time()

                # Test sentiment analysis
                analyzer = ProcessorFactory.create_sentiment_analyzer(analyzer_name)
                result = analyzer.analyze_sentiment(text)

                end_time = time.time()
                processing_time = (end_time - start_time) * 1000  # Convert to milliseconds

                actual_analyzer = result.get('analyzer', analyzer_name)
                sentiment = result.get('label', 'unknown')
                score = result.get('compound', 0)

                print(
                    f"     {analyzer_name:8} → {actual_analyzer:8} | {sentiment:8} ({score:+.3f}) | {processing_time:5.1f}ms")

            except Exception as e:
                print(f"     {analyzer_name:8} → ❌ Error: {str(e)[:30]}...")

    print("\n2. Testing text processors:")

    processors_to_test = ["auto", "nltk", "spacy", "hebrew", "basic"]
    test_text = "The running dogs are quickly eating delicious food."

    print(f"   Test text: \"{test_text}\"")

    for processor_name in processors_to_test:
        try:
            start_time = time.time()

            processor = ProcessorFactory.create_text_processor(processor_name)

            # Test multiple operations
            tokens = processor.tokenize(test_text)
            stems = processor.extract_stems(test_text)
            lemmas = processor.extract_lemmas(test_text)

            end_time = time.time()
            processing_time = (end_time - start_time) * 1000

            print(
                f"     {processor_name:8} | tokens:{len(tokens):2} stems:{len(stems):2} lemmas:{len(lemmas):2} | {processing_time:5.1f}ms")
            print(f"              | stems: {stems[:5]}...")
            print(f"              | lemmas: {lemmas[:5]}...")

        except Exception as e:
            print(f"     {processor_name:8} → ❌ Error: {str(e)[:40]}...")

    print("\n3. Stress testing with large dataset:")

    # Create larger dataset for stress testing
    large_dataset = []
    base_texts = [
        "I love this product! It's amazing!",
        "This is terrible. Very disappointed.",
        "It's okay, nothing special.",
        "Outstanding quality and service!",
        "Poor quality, not recommended."
    ]

    # Replicate texts to create larger dataset
    for i in range(100):  # 500 texts total
        text = base_texts[i % len(base_texts)]
        large_dataset.append({
            'text': f"{text} (review #{i + 1})",
            'review_id': f"R{i + 1:03d}"
        })

    large_df = pd.DataFrame(large_dataset)

    print(f"   Testing with {len(large_df)} texts...")

    start_time = time.time()

    # Use exam-safe pipeline for reliability
    config = create_exam_safe_pipeline()
    stress_results = quick_text_analysis_pipeline(
        data=large_df,
        text_column="text",
        config=config
    )

    end_time = time.time()
    total_time = end_time - start_time

    if 'processing_info' in stress_results:
        info = stress_results['processing_info']
        processed_count = info.get('final_rows', 0)
        analyzer_used = info.get('sentiment_analyzer_used', 'unknown')

        print(f"   ✅ Processed {processed_count} texts in {total_time:.2f} seconds")
        print(f"   Average: {(total_time / processed_count) * 1000:.1f}ms per text")
        print(f"   Analyzer used: {analyzer_used}")

        if 'cleaned_data' in stress_results:
            sentiment_dist = stress_results['cleaned_data']['sentiment_label'].value_counts()
            print(f"   Results: {sentiment_dist.to_dict()}")

    return stress_results


# ============================================================================
# Main Demo Function
# ============================================================================

def run_all_advanced_examples():
    """Run all advanced examples demonstrating generic architecture."""
    print("🚀 Advanced Data Science Examples - Future-Proof Architecture")
    print("=" * 70)

    try:
        # Check what's available
        from . import get_available_sentiment_analyzers, get_available_text_processors

        print("Available Tools:")
        print(f"  Sentiment Analyzers: {get_available_sentiment_analyzers()}")
        print(f"  Text Processors: {get_available_text_processors()}")
        print()

        # Run examples
        results = {}

        results['unknown_library'] = example_exam_unknown_library()
        results['multi_library'] = example_multi_library_comparison()
        results['hebrew_processing'] = example_hebrew_processing()
        results['exam_safe'] = example_exam_safe_pipeline()
        results['real_world'] = example_real_world_analysis()
        results['performance'] = example_performance_testing()

        print("\n" + "=" * 70)
        print("🎉 All Advanced Examples Completed Successfully!")
        print("\nKey Benefits of Generic Architecture:")
        print("  ✅ Works with any available library (VADER, TextBlob, spaCy, etc.)")
        print("  ✅ Automatic fallbacks when libraries are missing")
        print("  ✅ Hebrew and multilingual support")
        print("  ✅ Exam-safe configurations")
        print("  ✅ Performance optimized with multiple backends")
        print("  ✅ Future-proof for unknown exam scenarios")

        return results

    except Exception as e:
        print(f"❌ Error running examples: {e}")
        logger.error(f"Advanced examples failed: {e}", exc_info=True)
        return {}


# ============================================================================
# Quick Test Function for Exam Scenarios
# ============================================================================

def quick_exam_test(text: str, required_library: str = None, task: str = "sentiment"):
    """
    Quick test function for exam scenarios.

    Args:
        text: Text to analyze
        required_library: Library mentioned in exam (e.g., "textblob")
        task: Task to perform ("sentiment", "stemming", "lemmatization")

    Returns:
        Analysis result with fallback information
    """
    print(f"Quick Exam Test: {task} analysis")
    print(f"Text: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")

    if required_library:
        print(f"Required library: {required_library}")
        result = handle_unknown_library_scenario(required_library, task, text)
    else:
        if task == "sentiment":
            analyzer = get_best_available_sentiment_analyzer()
            result = analyzer.analyze_sentiment(text)
        else:
            processor = get_best_available_text_processor()
            if task == "stemming":
                result = processor.extract_stems(text)
            elif task == "lemmatization":
                result = processor.extract_lemmas(text)
            else:
                result = processor.tokenize(text)

    print(f"Result: {result}")
    return result


if __name__ == "__main__":
    # Run all examples
    run_all_advanced_examples()

    print("\n" + "=" * 50)
    print("Quick Test Examples:")

    # Quick tests
    quick_exam_test("I love this product!", "textblob", "sentiment")
    quick_exam_test("The running dogs are eating.", "nltk", "stemming")
    quick_exam_test("המוצר הזה מעולה ומומלץ!", "hebrew", "sentiment")