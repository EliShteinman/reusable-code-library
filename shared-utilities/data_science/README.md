# Data Science Utilities - ערכת כלים מתקדמת לניתוח נתונים

ערכת כלים מקצועית עם **ארכיטקטורה כפולה**: יישום בסיסי שתמיד עובד + יישום גנרי מתקדם עם תמיכה בספריות מרובות.

## 🚀 התקנה מהירה

```bash
pip install pandas numpy nltk
pip install textblob spacy openpyxl  # אופציונלי למאפיינים מתקדמים
```

## 📖 שימוש בסיסי (לתחילת מבחן)

```python
from shared_utilities.data_science import *

# טעינת נתונים
loader = UniversalDataLoader()
df = loader.load_data("data.csv")

# ניקוי טקסט
cleaner = TextCleaner()
df_clean = cleaner.clean_dataframe(df, ['text_column'])

# ניתוח רגשות
sentiment_analyzer = SentimentAnalyzer()
df_with_sentiment = sentiment_analyzer.analyze_dataframe(df_clean, 'text_column')

# ניתוח טקסט
analyzer = TextAnalyzer()
report = analyzer.generate_summary_report(df_with_sentiment, 'text_column')
```

## ⚡ שימוש מתקדם (לציונים גבוהים)

### 🔧 Factory Pattern למבחנים

```python
# יצירת analyzer ספציפי לפי דרישת המבחן
sentiment_analyzer = ProcessorFactory.create_sentiment_analyzer("textblob")
text_processor = ProcessorFactory.create_text_processor("spacy")

# אם הספרייה לא זמינה - fallback אוטומטי
smart_analyzer = SmartSentimentAnalyzer()  # בוחר הטוב ביותר
```

### 🌟 מולטי-ספריות (עמידות במבחן)

```python
# בדיקה מה זמין
available_analyzers = get_available_sentiment_analyzers()
print(f"Sentiment analyzers: {available_analyzers}")

# שימוש ב-ensemble לדיוק גבוה
ensemble = EnsembleSentimentAnalyzer(['vader', 'textblob', 'fallback'])
result = ensemble.analyze_sentiment("Amazing product!")
```

### 🇮🇱 תמיכה בעברית

```python
# עיבוד טקסט עברי מתקדם
hebrew_processor = HebrewTextProcessor()
roots = hebrew_processor.extract_roots("המוצר הזה מעולה ומומלץ")
stems = hebrew_processor.extract_stems("אני אוהב את הטכנולוגיה החדשה")

# ניתוח רגשות עברי
hebrew_sentiment = HebrewSentimentAnalyzer()
result = hebrew_sentiment.analyze_sentiment("זה מוצר מדהים!")
```

### 🎯 NLP מתקדם (Stemming & Lemmatization)

```python
# NLTK מתקדם
nltk_processor = NLTKTextProcessor()
stems = nltk_processor.extract_stems("running dogs are eating quickly")
lemmas = nltk_processor.extract_lemmas("running dogs are eating quickly")

# spaCy מתקדם
spacy_processor = SpaCyTextProcessor()
lemmas = spacy_processor.extract_lemmas("The running dogs are eating")
```

## 🧪 פונקציות מהירות למבחן

### Pipeline מלא

```python
# ניתוח מלא בשורה אחת
results = quick_text_analysis_pipeline(
    file_path="reviews.csv",
    text_column="review_text",
    category_column="product_type"
)

print(f"Processed {results['processing_info']['final_rows']} texts")
print(f"Sentiment distribution: {results['analysis_report']['common_words']}")
```

### בדיקת רגשות מהירה

```python
# בדיקה מהירה לטקסט בודד
result = quick_sentiment_check("I love this product!", analyzer="vader")
print(f"Sentiment: {result['label']} (score: {result['compound']})")

# עם fallback אוטומטי אם VADER לא זמין
result = quick_sentiment_check("Great experience!", analyzer="auto")
```

### חילוץ מאפיינים מלא

```python
# כל המאפיינים בפעולה אחת
features = extract_all_features("The running dogs are eating delicious food")
print(f"Tokens: {features['tokens']}")
print(f"Stems: {features['stems']}")
print(f"Lemmas: {features['lemmas']}")
print(f"Sentiment: {features['sentiment']}")
```

## 🎓 תרחישי מבחן נפוצים

### תרחיש 1: "השתמש ב-TextBlob"
```python
# המבחן דורש TextBlob ספציפי
try:
    analyzer = ProcessorFactory.create_sentiment_analyzer("textblob")
    result = analyzer.analyze_sentiment(text)
except:
    # Fallback אוטומטי
    analyzer = SmartSentimentAnalyzer()
    result = analyzer.analyze_sentiment(text)
```

### תרחיש 2: "בצע stemming ו-lemmatization"
```python
# עם NLTK
processor = NLTKTextProcessor()
stems = processor.extract_stems(text)
lemmas = processor.extract_lemmas(text)

# עם spaCy (אם זמין)
spacy_processor = SpaCyTextProcessor()
lemmas = spacy_processor.extract_lemmas(text)
```

### תרחיש 3: "ניתוח טקסט בעברית"
```python
# מיוחד לעברית
hebrew_processor = HebrewTextProcessor()
tokens = hebrew_processor.tokenize("טקסט בעברית")
roots = hebrew_processor.extract_roots("המילים האלה")
sentiment = HebrewSentimentAnalyzer().analyze_sentiment("מוצר מעולה!")
```

### תרחיש 4: Pipeline בטוח למבחן
```python
# יצירת pipeline שתמיד יעבוד
config = create_exam_safe_pipeline(preferred_sentiment="vader")
pipeline_result = quick_text_analysis_pipeline(
    file_path="data.csv",
    text_column="text"
)
```

## 📁 מבנה הספרייה

```
shared-utilities/data_science/
├── __init__.py                          # Import כל הפונקציות
│
├── data_loader.py                       # טעינת קבצים (CSV, JSON, Excel)
├── text_cleaner.py                      # ניקוי טקסט בסיסי
├── text_analyzer.py                     # ניתוח טקסט סטטיסטי
├── sentiment_analyzer.py                # ניתוח רגשות בסיסי
│
├── text_processing_base.py              # ABC Classes + Factory
├── sentiment_implementations.py         # כל ה-sentiment analyzers
├── text_processing_implementations.py   # Stemming, Lemmatization, Hebrew
│
├── examples.py                          # דוגמאות בסיסיות
├── examples_advanced.py                 # דוגמאות מתקדמות
└── README.md                           # המדריך הזה
```

## 🔧 Troubleshooting למבחן

### בעיה: NLTK לא נמצא
```python
# הספרייה תעבור אוטומטית ל-fallback
# או התקן: pip install nltk
```

### בעיה: spaCy לא נמצא
```python
# pip install spacy
# python -m spacy download en_core_web_sm
```

### בעיה: קובץ לא נטען
```python
# בדוק פורמטים נתמכים
loader = UniversalDataLoader()
info = loader.get_file_info("file.csv")
print(info)
```

## 🎯 טיפים למבחן

### 1. **תמיד התחל בסיסי:**
```python
from shared_utilities.data_science import UniversalDataLoader, TextCleaner, SentimentAnalyzer
```

### 2. **אם המבחן דורש ספרייה ספציפית:**
```python
analyzer = ProcessorFactory.create_sentiment_analyzer("textblob")  # או vader, spacy
```

### 3. **אם לא בטוח מה זמין:**
```python
smart_analyzer = SmartSentimentAnalyzer()  # יבחר הטוב ביותר
```

### 4. **לעבודה עם עברית:**
```python
hebrew_processor = HebrewTextProcessor()
hebrew_sentiment = HebrewSentimentAnalyzer()
```

### 5. **לבדיקות מהירות:**
```python
result = quick_sentiment_check("text to analyze")
features = extract_all_features("text for complete analysis")
```

## 🏆 יתרונות למבחן

- ✅ **עמידות**: עובד עם כל ספרייה או בלעדיה
- ✅ **גמישות**: תומך ב-VADER, TextBlob, spaCy, Hebrew
- ✅ **פשטות**: פונקציות one-liner למבחן מהיר
- ✅ **מתקדם**: Stemming, Lemmatization, Ensemble
- ✅ **עברית**: תמיכה מלאה בעיבוד עברית
- ✅ **Factory Pattern**: ארכיטקטורה מקצועית
- ✅ **Fallbacks**: תמיד יש פתרון גיבוי

**בהצלחה במבחן! 🎯**