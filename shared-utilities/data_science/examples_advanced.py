# ============================================================================
# shared-utilities/data_science/examples_advanced.py - EXAM FOCUSED
# ============================================================================
"""
דוגמאות מתקדמות מתמקדות בתרחישי מבחן נפוצים
כל דוגמה מתאימה לשאלה אפשרית במבחן
"""

import pandas as pd
from datetime import datetime
import logging

# Import everything we might need
from . import *

logger = logging.getLogger(__name__)


# ============================================================================
# דוגמה 1: המבחן דורש ספרייה ספציפית
# ============================================================================

def exam_scenario_specific_library():
    """
    תרחיש מבחן: "השתמש ב-TextBlob לניתוח רגשות"
    מה לעשות כשהמבחן דורש ספרייה ספציפית
    """
    print("=== תרחיש מבחן: ספרייה ספציפית ===")

    exam_text = "I absolutely love this new smartphone! The camera quality is amazing."

    # 1. ניסיון להשתמש בספרייה המבוקשת
    print("1. המבחן דורש: TextBlob")

    try:
        # נסה TextBlob ספציפי
        analyzer = ProcessorFactory.create_sentiment_analyzer("textblob")
        result = analyzer.analyze_sentiment(exam_text)
        print(f"   ✅ TextBlob זמין: {result['label']} ({result['compound']:.3f})")
        analyzer_used = "textblob"

    except Exception as e:
        print(f"   ❌ TextBlob לא זמין: {e}")

        # 2. Fallback לזמין
        print("2. עובר ל-fallback אוטומטי:")
        analyzer = SmartSentimentAnalyzer()
        result = analyzer.analyze_sentiment(exam_text)
        analyzer_used = result.get('analyzer', 'unknown')
        print(f"   ✅ השתמש ב-{analyzer_used}: {result['label']} ({result['compound']:.3f})")

    # 3. הצג מה זמין במערכת
    available = get_available_sentiment_analyzers()
    print(f"3. ספריות זמינות במערכת: {available}")

    return result, analyzer_used


# ============================================================================
# דוגמה 2: Stemming ו-Lemmatization (נושא פופולרי במבחנים)
# ============================================================================

def exam_scenario_stemming_lemmatization():
    """
    תרחיש מבחן: "בצע stemming ו-lemmatization לטקסט"
    הדגמת יכולות NLP מתקדמות
    """
    print("\n=== תרחיש מבחן: Stemming & Lemmatization ===")

    exam_text = "The running dogs are quickly eating delicious foods"
    print(f"טקסט לניתוח: '{exam_text}'")

    # 1. ניסיון עם NLTK
    print("\n1. עם NLTK:")
    try:
        nltk_processor = NLTKTextProcessor()

        tokens = nltk_processor.tokenize(exam_text)
        stems = nltk_processor.extract_stems(exam_text)
        lemmas = nltk_processor.extract_lemmas(exam_text)

        print(f"   Tokens: {tokens}")
        print(f"   Stems: {stems}")
        print(f"   Lemmas: {lemmas}")

    except Exception as e:
        print(f"   ❌ NLTK לא זמין: {e}")

    # 2. ניסיון עם spaCy
    print("\n2. עם spaCy:")
    try:
        spacy_processor = SpaCyTextProcessor()

        tokens = spacy_processor.tokenize(exam_text)
        lemmas = spacy_processor.extract_lemmas(exam_text)
        roots = spacy_processor.extract_roots(exam_text)

        print(f"   Tokens: {tokens}")
        print(f"   Lemmas: {lemmas}")
        print(f"   Roots: {roots}")

    except Exception as e:
        print(f"   ❌ spaCy לא זמין: {e}")

    # 3. Fallback בסיסי (תמיד עובד)
    print("\n3. Fallback בסיסי:")
    basic_processor = BasicTextProcessor()

    tokens = basic_processor.tokenize(exam_text)
    stems = basic_processor.extract_stems(exam_text)
    lemmas = basic_processor.extract_lemmas(exam_text)

    print(f"   Tokens: {tokens}")
    print(f"   Stems: {stems}")
    print(f"   Lemmas: {lemmas}")


# ============================================================================
# דוגמה 3: עיבוד עברית (חשוב לישראל)
# ============================================================================

def exam_scenario_hebrew_processing():
    """
    תרחיש מבחן: "נתח טקסט בעברית"
    הדגמת יכולות עיבוד עברית מתקדמות
    """
    print("\n=== תרחיש מבחן: עיבוד עברית ===")

    hebrew_texts = [
        "המוצר הזה מעולה ומומלץ בחום",
        "השירות היה רע ומאכזב מאוד",
        "אני מאוד מרוצה מהקנייה החדשה",
        "הטכנולוגיה החדשה מדהימה"
    ]

    hebrew_processor = HebrewTextProcessor()
    hebrew_sentiment = HebrewSentimentAnalyzer()

    print("ניתוח טקסטים בעברית:")
    for i, text in enumerate(hebrew_texts, 1):
        print(f"\n{i}. '{text}'")

        # טוקניזציה
        tokens = hebrew_processor.tokenize(text)
        print(f"   טוקנים: {tokens}")

        # חילוץ stems ו-roots
        stems = hebrew_processor.extract_stems(text)
        roots = hebrew_processor.extract_roots(text)
        print(f"   Stems: {stems}")
        print(f"   Roots: {roots}")

        # ניתוח רגשות
        sentiment = hebrew_sentiment.analyze_sentiment(text)
        print(f"   רגש: {sentiment['label']} (ציון: {sentiment['compound']:.3f})")


# ============================================================================
# דוגמה 4: השוואת מודלים (אמין למבחן)
# ============================================================================

def exam_scenario_model_comparison():
    """
    תרחיש מבחן: "השווה בין מודלים שונים"
    הדגמת Ensemble ו-Multi-model
    """
    print("\n=== תרחיש מבחן: השוואת מודלים ===")

    test_sentences = [
        "This product is absolutely amazing!",
        "Terrible quality, very disappointed.",
        "It's okay, nothing special.",
        "Outstanding service and fast delivery!"
    ]

    print("השוואת analyzers על טקסטים שונים:")

    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n{i}. '{sentence}'")

        # בדיקה עם analyzers שונים
        analyzers_to_test = ["vader", "textblob", "fallback", "smart"]

        results = {}
        for analyzer_name in analyzers_to_test:
            try:
                if analyzer_name == "smart":
                    analyzer = SmartSentimentAnalyzer()
                else:
                    analyzer = ProcessorFactory.create_sentiment_analyzer(analyzer_name)

                result = analyzer.analyze_sentiment(sentence)
                results[analyzer_name] = result

                print(f"   {analyzer_name:8}: {result['label']:8} ({result['compound']:+.3f})")

            except Exception as e:
                print(f"   {analyzer_name:8}: ❌ לא זמין")
                results[analyzer_name] = None

        # Ensemble (אם יש כמה analyzers זמינים)
        try:
            available_analyzers = [name for name, result in results.items() if result is not None]
            if len(available_analyzers) >= 2:
                ensemble = EnsembleSentimentAnalyzer(available_analyzers[:3])
                ensemble_result = ensemble.analyze_sentiment(sentence)
                print(f"   ensemble : {ensemble_result['label']:8} ({ensemble_result['compound']:+.3f}) [ממוצע]")
        except:
            print("   ensemble : ❌ לא זמין")


# ============================================================================
# דוגמה 5: Pipeline מלא למבחן
# ============================================================================

def exam_scenario_complete_pipeline():
    """
    תרחיש מבחן: "בצע ניתוח טקסט מלא"
    Pipeline שלם מטעינת קובץ עד תוצאות
    """
    print("\n=== תרחיש מבחן: Pipeline מלא ===")

    # יצירת נתוני דוגמה למבחן
    sample_data = pd.DataFrame({
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
        'product_category': ['laptop', 'electronics', 'phone', 'service', 'electronics',
                             'laptop', 'shipping', 'electronics', 'electronics', 'electronics'],
        'rating': [5, 1, 3, 5, 2, 4, 1, 4, 5, 3]
    })

    print(f"1. נתוני דוגמה: {len(sample_data)} ביקורות")

    # Pipeline בסיסי
    print("\n2. Pipeline בסיסי:")
    try:
        results = quick_text_analysis_pipeline(
            data=sample_data,  # אם יש data במקום file_path
            text_column="review_text",
            category_column="product_category"
        )

        processing_info = results.get('processing_info', {})
        print(f"   ✅ Pipeline הושלם בהצלחה")
        print(f"   מעבד רגשות: {processing_info.get('analyzer_used', 'unknown')}")
        print(f"   טקסטים מעובדים: {processing_info.get('final_rows', 0)}")

        # הצג תוצאות
        if 'cleaned_data' in results:
            df_result = results['cleaned_data']
            sentiment_dist = df_result['sentiment_label'].value_counts()
            print(f"   התפלגות רגשות: {sentiment_dist.to_dict()}")

    except Exception as e:
        print(f"   ❌ Pipeline בסיסי נכשל: {e}")

    # Pipeline מתקדם עם הגדרות
    print("\n3. Pipeline מתקדם:")
    try:
        # יצירת הגדרות בטוחות למבחן
        config = create_exam_safe_pipeline(preferred_sentiment="vader")
        print(f"   הגדרות בטוחות: {config.to_dict() if config else 'basic fallback'}")

        # ניתוח ידני עם smart analyzers
        smart_analyzer = SmartSentimentAnalyzer()
        smart_processor = SmartTextProcessor()

        print(f"   Smart analyzer זמין: {smart_analyzer.get_available_analyzers()}")
        print(f"   Smart processor זמין: {smart_processor.get_supported_languages()}")

    except Exception as e:
        print(f"   ❌ Pipeline מתקדם נכשל: {e}")


# ============================================================================
# דוגמה 6: בעיות נפוצות ופתרונות למבחן
# ============================================================================

def exam_scenario_troubleshooting():
    """
    תרחיש מבחן: "פתרון בעיות נפוצות"
    איך להתמודד עם בעיות שיכולות לקרות במבחן
    """
    print("\n=== תרחיש מבחן: פתרון בעיות ===")

    # בעיה 1: קובץ לא נמצא
    print("1. טיפול בקובץ שלא נמצא:")
    try:
        loader = UniversalDataLoader()
        df = loader.load_data("nonexistent_file.csv")
    except FileNotFoundError:
        print("   ✅ זוהה קובץ שלא נמצא - הטיפול תקין")
        # פתרון: יצירת נתוני דוגמה
        df = pd.DataFrame({
            'text': ['sample text for demo'],
            'category': ['demo']
        })
        print("   ✅ נוצרו נתוני דוגמה במקום")

    # בעיה 2: עמודה שלא קיימת
    print("\n2. טיפול בעמודה שלא קיימת:")
    if 'nonexistent_column' not in df.columns:
        print("   ✅ זוהה עמודה שלא קיימת")
        print(f"   עמודות זמינות: {list(df.columns)}")
        text_column = df.columns[0]  # השתמש בעמודה הראשונה
        print(f"   ✅ השתמש בעמודה: {text_column}")

    # בעיה 3: ספרייה חסרה
    print("\n3. טיפול בספרייה חסרה:")
    try:
        # נסה ספרייה שלא קיימת
        analyzer = ProcessorFactory.create_sentiment_analyzer("nonexistent_analyzer")
    except (ValueError, Exception) as e:
        print(f"   ✅ זוהה ספרייה חסרה: {type(e).__name__}")
        # פתרון: fallback
        analyzer = FallbackSentimentAnalyzer()
        print("   ✅ עבר ל-fallback analyzer")

        # בדיקה שהוא עובד
        result = analyzer.analyze_sentiment("test text")
        print(f"   ✅ Fallback עובד: {result['label']}")

    # בעיה 4: טקסט ריק
    print("\n4. טיפול בטקסט ריק:")
    empty_texts = ["", None, "   ", "###"]
    cleaner = TextCleaner()

    for i, empty_text in enumerate(empty_texts):
        cleaned = cleaner.clean_text(str(empty_text) if empty_text else "")
        print(f"   טקסט {i + 1}: '{empty_text}' → '{cleaned}'")

    print("   ✅ טיפול בטקסטים ריקים תקין")


# ============================================================================
# דוגמה 7: תכונות מתקדמות למבחן מקצועי
# ============================================================================

def exam_scenario_advanced_features():
    """
    תרחיש מבחן: "השתמש בתכונות מתקדמות"
    הדגמת יכולות מתקדמות לציון גבוה
    """
    print("\n=== תרחיש מבחן: תכונות מתקדמות ===")

    # 1. חילוץ תכונות מלא
    print("1. חילוץ תכונות מלא:")
    sample_text = "The innovative technology is revolutionizing industries"

    features = extract_all_features(sample_text)
    for feature_name, feature_value in features.items():
        if isinstance(feature_value, list):
            print(f"   {feature_name}: {feature_value[:5]}...")  # הצג 5 ראשונים
        elif isinstance(feature_value, dict):
            print(f"   {feature_name}: {feature_value.get('label', 'N/A')} ({feature_value.get('compound', 0):.3f})")
        else:
            print(f"   {feature_name}: {feature_value}")

    # 2. ניתוח בזמן אמת
    print("\n2. ניתוח מהיר לטקסטים שונים:")
    quick_tests = [
        "Excellent product quality!",
        "Disappointing experience overall.",
        "Average performance, nothing special."
    ]

    for text in quick_tests:
        result = quick_sentiment_check(text, analyzer="auto")
        print(f"   '{text[:30]}...' → {result['label']} ({result.get('compound', 0):+.3f})")

    # 3. סטטיסטיקות מתקדמות
    print("\n3. סטטיסטיקות מתקדמות:")
    sample_df = pd.DataFrame({
        'text': [
            "Amazing product with great features!",
            "Poor quality, not recommended at all.",
            "Good value for the price point.",
            "Outstanding customer service experience!",
            "Average product, meets basic needs."
        ],
        'category': ['electronics', 'electronics', 'electronics', 'service', 'electronics']
    })

    # ניתוח מהיר
    analyzer = SentimentAnalyzer()
    df_analyzed = analyzer.analyze_dataframe(sample_df, 'text')

    # חישוב סטטיסטיקות
    scores = df_analyzed['sentiment_score'].tolist()
    stats = analyzer.get_sentiment_statistics(scores)

    print(f"   ממוצע רגשות: {stats['average_score']}")
    print(
        f"   התפלגות: חיובי {stats['positive_percentage']}%, שלילי {stats['negative_percentage']}%, ניטרלי {stats['neutral_percentage']}%")


# ============================================================================
# פונקציה ראשית להרצת כל הדוגמאות
# ============================================================================

def run_all_exam_scenarios():
    """הרץ את כל תרחישי המבחן בבת אחת"""
    print("🚀 תרחישי מבחן - Data Science")
    print("=" * 50)

    try:
        # הצג מה זמין במערכת
        print("מצב המערכת:")
        print(f"  Sentiment analyzers: {get_available_sentiment_analyzers()}")
        print(f"  Text processors: {get_available_text_processors()}")
        print()

        # הרץ את כל התרחישים
        exam_scenario_specific_library()
        exam_scenario_stemming_lemmatization()
        exam_scenario_hebrew_processing()
        exam_scenario_model_comparison()
        exam_scenario_complete_pipeline()
        exam_scenario_troubleshooting()
        exam_scenario_advanced_features()

        print("\n" + "=" * 50)
        print("🎉 כל תרחישי המבחן הושלמו בהצלחה!")
        print("\nעיקרי הלקחים למבחן:")
        print("  ✅ תמיד יש fallback לכל ספרייה")
        print("  ✅ הקוד עמיד בפני שגיאות")
        print("  ✅ תמיכה מלאה בעברית")
        print("  ✅ מגוון רחב של analyzers")
        print("  ✅ Pipeline מלא עובד תמיד")

    except Exception as e:
        print(f"❌ שגיאה בהרצת תרחישי המבחן: {e}")
        logger.error(f"Exam scenarios failed: {e}", exc_info=True)


# ============================================================================
# פונקציות עזר מהירות למבחן
# ============================================================================

def quick_exam_demo(text: str = "This is an amazing product!"):
    """
    הדגמה מהירה לכל היכולות - מושלם למבחן

    Args:
        text: טקסט לניתוח
    """
    print(f"🎯 הדגמה מהירה: '{text}'")
    print("-" * 40)

    # Sentiment
    result = quick_sentiment_check(text)
    print(f"רגש: {result['label']} (ציון: {result.get('compound', 0):+.3f})")

    # Features
    features = extract_all_features(text)
    print(f"טוקנים: {features.get('tokens', [])}")
    print(f"Stems: {features.get('stems', [])}")

    # Available tools
    print(f"כלים זמינים: {get_available_sentiment_analyzers()}")


if __name__ == "__main__":
    # הרץ הדגמה מהירה
    quick_exam_demo()

    print("\n" + "=" * 60)

    # הרץ את כל התרחישים
    run_all_exam_scenarios()