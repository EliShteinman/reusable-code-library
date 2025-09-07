# Data Science Utilities - ערכת כלים לניתוח נתונים

ערכת כלים מקצועית וקלה לשימוש לניתוח טקסט ונתונים, מיועדת למבחנים ופרויקטים אקדמיים.

## 📋 תוכן העניינים

1. [התקנה ודרישות](#התקנה-ודרישות)
2. [מבנה הספרייה](#מבנה-הספרייה)
3. [שימוש בסיסי](#שימוש-בסיסי)
4. [מדריכים מפורטים](#מדריכים-מפורטים)
5. [דוגמאות קוד](#דוגמאות-קוד)
6. [טיפים למבחן](#טיפים-למבחן)

## 🚀 התקנה ודרישות

### דרישות מערכת
```bash
pip install pandas numpy nltk
```

### ספריות אופציונליות (מומלץ)
```bash
pip install openpyxl  # עבור קבצי Excel
pip install pyarrow   # עבור קבצי Parquet
pip install lxml      # עבור קבצי XML/HTML
```

### הגדרה ראשונית
```python
# יבוא כל הכלים
from shared_utilities.data_science import (
    UniversalDataLoader,
    TextCleaner, 
    TextAnalyzer,
    SentimentAnalyzer
)
```

## 📁 מבנה הספרייה

```
shared-utilities/data_science/
├── __init__.py              # יבואים ופונקציות מהירות
├── data_loader.py           # טעינת קבצים מכל הפורמטים
├── text_cleaner.py          # ניקוי טקסט מתקדם
├── text_analyzer.py         # ניתוח טקסט סטטיסטי
├── sentiment_analyzer.py    # ניתוח רגשות
└── EXAMPLES.py             # דוגמאות שימוש מלאות
```

---

## 🔧 שימוש בסיסי

### 1. טעינת נתונים (UniversalDataLoader)

```python
# יצירת אובייקט לטעינת נתונים
loader = UniversalDataLoader()

# טעינת קבצים שונים
df_csv = loader.load_data("data.csv")
df_excel = loader.load_data("data.xlsx") 
df_json = loader.load_data("data.json")
df_parquet = loader.load_data("data.parquet")

# מידע על הקובץ
info = loader.get_file_info("data.csv")
print(info)
```

**פורמטים נתמכים:**
- CSV, TSV
- Excel (xlsx, xls)
- JSON, JSON Lines
- Parquet
- TXT, HTML, XML

### 2. ניקוי טקסט (TextCleaner)

```python
# יצירת אובייקט לניקוי טקסט
cleaner = TextCleaner()

# ניקוי בסיסי
clean_text = cleaner.clean_text(
    "Check this AMAZING deal!!! http://example.com @user #sale",
    remove_urls=True,
    remove_mentions=True,
    remove_hashtags=True,
    to_lowercase=True
)
# תוצאה: "check this amazing deal"

# ניקוי DataFrame
df_clean = cleaner.clean_dataframe(
    df, 
    ['text_column'],
    remove_punctuation=True,
    remove_extra_whitespace=True
)

# הסרת טקסטים ריקים וקצרים
df_clean = cleaner.remove_empty_texts(df_clean, ['text_column'])
df_clean = cleaner.filter_by_length(df_clean, 'text_column', min_length=3, by_chars=False)
```

### 3. ניתוח רגשות (SentimentAnalyzer)

```python
# יצירת אובייקט לניתוח רגשות
sentiment_analyzer = SentimentAnalyzer()

# ניתוח טקסט יחיד
score = sentiment_analyzer.get_sentiment_score("I love this product!")
label = sentiment_analyzer.get_sentiment_label("I love this product!")
detailed = sentiment_analyzer.get_detailed_scores("I love this product!")

print(f"Score: {score}, Label: {label}")
# Score: 0.6369, Label: positive

# ניתוח DataFrame
df_with_sentiment = sentiment_analyzer.analyze_dataframe(
    df, 
    'text_column',
    add_detailed=True
)

# סטטיסטיקות רגשות
scores = df_with_sentiment['sentiment_score'].tolist()
stats = sentiment_analyzer.get_sentiment_statistics(scores)
print(stats)
```

### 4. ניתוח טקסט (TextAnalyzer)

```python
# יצירת אובייקט לניתוח טקסט
analyzer = TextAnalyzer()

# התפלגות טקסטים לפי קטגוריות
distribution = analyzer.analyze_text_distribution(df, 'text_column', 'category_column')

# ניתוח אורכי טקסטים
lengths = analyzer.analyze_text_lengths(df, 'text_column')
print(f"Average words: {lengths['average_word_count']}")

# מילים נפוצות
common_words = analyzer.find_common_words(df, 'text_column', top_n=10)
for word_info in common_words[:5]:
    print(f"{word_info['word']}: {word_info['count']} times")

# חיפוש מילות מפתח
keywords = ['good', 'bad', 'excellent']
keyword_results = analyzer.keyword_analysis(df, 'text_column', keywords)

# דוח מקיף
report = analyzer.generate_summary_report(df, 'text_column', 'category_column', keywords)
```

---

## 📚 מדריכים מפורטים

### Pipeline מלא לניתוח טקסט

```python
def complete_text_analysis_pipeline(file_path, text_col, category_col=None):
    """Pipeline מלא לניתוח טקסט"""
    
    # 1. טעינת נתונים
    loader = UniversalDataLoader()
    df = loader.load_data(file_path)
    print(f"Loaded: {len(df)} rows")
    
    # 2. ניקוי טקסט
    cleaner = TextCleaner()
    df_clean = cleaner.clean_dataframe(
        df, [text_col],
        remove_urls=True,
        remove_punctuation=True,
        to_lowercase=True,
        remove_extra_whitespace=True
    )
    
    # הסרת טקסטים ריקים וקצרים
    df_clean = cleaner.remove_empty_texts(df_clean, [text_col])
    df_clean = cleaner.filter_by_length(df_clean, text_col, min_length=3, by_chars=False)
    print(f"After cleaning: {len(df_clean)} rows")
    
    # 3. ניתוח רגשות
    sentiment_analyzer = SentimentAnalyzer()
    df_analyzed = sentiment_analyzer.analyze_dataframe(df_clean, text_col, add_detailed=True)
    
    # 4. ניתוח טקסט
    analyzer = TextAnalyzer()
    
    # דוח מקיף
    keywords = ['good', 'great', 'bad', 'terrible', 'excellent']
    report = analyzer.generate_summary_report(df_analyzed, text_col, category_col, keywords)
    
    return df_analyzed, report

# שימוש
df_result, analysis_report = complete_text_analysis_pipeline(
    "reviews.csv", 
    "review_text", 
    "product_category"
)
```

### ניתוח השוואתי בין קטגוריות

```python
def compare_categories_sentiment(df, text_col, category_col):
    """השוואת רגשות בין קטגוריות"""
    
    sentiment_analyzer = SentimentAnalyzer()
    df_with_sentiment = sentiment_analyzer.analyze_dataframe(df, text_col)
    
    # סטטיסטיקות לפי קטגוריה
    category_stats = {}
    for category in df[category_col].unique():
        category_data = df_with_sentiment[df_with_sentiment[category_col] == category]
        scores = category_data['sentiment_score'].tolist()
        stats = sentiment_analyzer.get_sentiment_statistics(scores)
        category_stats[category] = stats
    
    return category_stats

# שימוש
stats_by_category = compare_categories_sentiment(df, 'review_text', 'product_type')
for category, stats in stats_by_category.items():
    print(f"{category}: Avg sentiment = {stats['average_score']}")
```

---

## 💡 דוגמאות קוד מעשיות

### דוגמה 1: ניתוח ביקורות מוצרים

```python
import pandas as pd
from shared_utilities.data_science import *

# יצירת נתוני דוגמה
reviews_data = pd.DataFrame({
    'review_text': [
        "This product is absolutely amazing! Best purchase ever!",
        "Terrible quality, broke after one day. Very disappointed.",
        "Good value for money, does what it promises.",
        "Outstanding customer service and fast delivery!",
        "Average product, nothing special but works fine."
    ],
    'product_category': ['electronics', 'electronics', 'books', 'electronics', 'books'],
    'rating': [5, 1, 4, 5, 3]
})

# Pipeline מלא
def analyze_product_reviews(df):
    # 1. ניקוי
    cleaner = TextCleaner()
    df_clean = cleaner.clean_dataframe(
        df, ['review_text'],
        remove_punctuation=True,
        to_lowercase=True
    )
    
    # 2. ניתוח רגשות
    sentiment_analyzer = SentimentAnalyzer()
    df_sentiment = sentiment_analyzer.analyze_dataframe(
        df_clean, 'review_text', add_detailed=True
    )
    
    # 3. ניתוח טקסט
    analyzer = TextAnalyzer()
    
    # מילים נפוצות
    common_words = analyzer.find_common_words(df_sentiment, 'review_text', top_n=10)
    
    # ניתוח לפי קטגוריה
    category_analysis = analyzer.analyze_text_distribution(
        df_sentiment, 'review_text', 'product_category'
    )
    
    # חיפוש מילות מפתח
    keywords = ['amazing', 'terrible', 'good', 'bad', 'excellent']
    keyword_analysis = analyzer.keyword_analysis(df_sentiment, 'review_text', keywords)
    
    return {
        'data': df_sentiment,
        'common_words': common_words,
        'category_distribution': category_analysis,
        'keywords': keyword_analysis
    }

# ביצוע הניתוח
results = analyze_product_reviews(reviews_data)

# הצגת תוצאות
print("=== ניתוח ביקורות מוצרים ===")
print(f"סה\"כ ביקורות: {len(results['data'])}")
print(f"התפלגות לפי קטגוריה: {results['category_distribution']['by_category']}")

print("\nמילים נפוצות:")
for word in results['common_words'][:5]:
    print(f"  {word['word']}: {word['count']} פעמים ({word['percentage']}%)")

print("\nמילות מפתח:")
for keyword, stats in results['keywords']['keyword_stats'].items():
    print(f"  '{keyword}': {stats['count']} פעמים")
```

### דוגמה 2: ניתוח סנטימנט מתקדם

```python
def advanced_sentiment_analysis(df, text_col):
    """ניתוח סנטימנט מתקדם עם תובנות"""
    
    sentiment_analyzer = SentimentAnalyzer()
    df_analyzed = sentiment_analyzer.analyze_dataframe(df, text_col, add_detailed=True)
    
    # סטטיסטיקות כלליות
    scores = df_analyzed['sentiment_score'].tolist()
    stats = sentiment_analyzer.get_sentiment_statistics(scores)
    
    # חלוקה לקבוצות סנטימנט
    positive_texts = df_analyzed[df_analyzed['sentiment_label'] == 'positive']
    negative_texts = df_analyzed[df_analyzed['sentiment_label'] == 'negative']
    neutral_texts = df_analyzed[df_analyzed['sentiment_label'] == 'neutral']
    
    # מציאת הטקסטים הקיצוניים
    most_positive = df_analyzed.loc[df_analyzed['sentiment_score'].idxmax()]
    most_negative = df_analyzed.loc[df_analyzed['sentiment_score'].idxmin()]
    
    return {
        'statistics': stats,
        'most_positive_text': most_positive[text_col],
        'most_positive_score': most_positive['sentiment_score'],
        'most_negative_text': most_negative[text_col],
        'most_negative_score': most_negative['sentiment_score'],
        'positive_count': len(positive_texts),
        'negative_count': len(negative_texts),
        'neutral_count': len(neutral_texts)
    }

# שימוש
sentiment_insights = advanced_sentiment_analysis(reviews_data, 'review_text')
print(f"הטקסט החיובי ביותר: {sentiment_insights['most_positive_text']}")
print(f"ציון: {sentiment_insights['most_positive_score']:.3f}")
```

### דוגמה 3: עיבוד מהיר עם Pipeline Functions

```python
# שימוש בפונקציות המהירות מ-__init__.py
from shared_utilities.data_science import (
    quick_text_analysis_pipeline,
    sentiment_analysis_pipeline,
    text_cleaning_pipeline
)

# Pipeline מהיר מקובץ
results = quick_text_analysis_pipeline(
    file_path="reviews.csv",
    text_column="review_text", 
    category_column="category"
)

print(f"נתונים מקוריים: {results['data_info']['original_rows']}")
print(f"נתונים מנוקים: {results['data_info']['final_rows']}")

# ניקוי מהיר
df_clean = text_cleaning_pipeline(
    df, 
    ['text_column'],
    remove_punctuation=True,
    to_lowercase=True,
    remove_urls=True
)

# ניתוח רגשות מהיר
df_sentiment = sentiment_analysis_pipeline(df_clean, 'text_column')
```

---

## 🎯 טיפים למבחן

### נושאים חשובים שכדאי לדעת:

#### 1. **פנדס (Pandas) - נושאים למבחן**
```python
# טעינת נתונים
df = pd.read_csv("file.csv")
df = pd.read_excel("file.xlsx")

# בדיקת נתונים
df.info()          # מידע על העמודות
df.describe()      # סטטיסטיקות בסיסיות
df.head()          # 5 שורות ראשונות
df.shape           # מימדי הנתונים

# עיבוד נתונים
df.dropna()        # הסרת ערכים חסרים
df.fillna(0)       # מילוי ערכים חסרים
df.drop_duplicates()  # הסרת כפילויות

# סינון וקיבוץ
df[df['column'] > 5]  # סינון
df.groupby('category').mean()  # קיבוץ וחישוב ממוצע
df.value_counts()     # ספירת ערכים
```

#### 2. **Text Processing - עקרונות חשובים**
```python
# ניקוי טקסט בסיסי
text = text.lower()                    # הורדת אותיות
text = re.sub(r'[^\w\s]', '', text)   # הסרת סימני פיסוק
text = ' '.join(text.split())         # ניקוי רווחים

# טכניקות נפוצות במבחנים
df['word_count'] = df['text'].str.split().str.len()    # ספירת מילים
df['char_count'] = df['text'].str.len()                # ספירת תווים
df['contains_keyword'] = df['text'].str.contains('word')  # חיפוש מילה
```

#### 3. **Sentiment Analysis - מה חשוב לדעת**
```python
# VADER Sentiment - הערכים החשובים
# compound: -1 (שלילי מאוד) עד 1 (חיובי מאוד)
# pos, neu, neg: אחוזים שסכומם 1

# סיווג בסיסי
if compound >= 0.05:
    sentiment = "positive"
elif compound <= -0.05:
    sentiment = "negative" 
else:
    sentiment = "neutral"
```

#### 4. **File Formats - מה יכול להיות במבחן**
```python
# CSV - הנפוץ ביותר
df = pd.read_csv("file.csv", encoding='utf-8')

# JSON - למבנים מורכבים
df = pd.read_json("file.json")

# Excel - עם sheets
df = pd.read_excel("file.xlsx", sheet_name="Sheet1")

# Parquet - לקבצים גדולים
df = pd.read_parquet("file.parquet")
```

### דוגמאות לשאלות אפשריות במבחן:

**שאלה 1: ניקוי וניתוח טקסט**
```python
# נתון DataFrame עם עמודת 'reviews'
# נקה את הטקסט והסר ביקורות קצרות מ-5 מילים

cleaner = TextCleaner()
df_clean = cleaner.clean_dataframe(
    df, ['reviews'],
    remove_punctuation=True,
    to_lowercase=True
)
df_filtered = cleaner.filter_by_length(df_clean, 'reviews', min_length=5, by_chars=False)
```

**שאלה 2: חישוב סטטיסטיקות טקסט**
```python
# חשב אורך ממוצע של ביקורות לפי קטגוריה

analyzer = TextAnalyzer()
length_stats = analyzer.analyze_text_lengths(df, 'reviews', 'category')
print(length_stats['by_category'])
```

**שאלה 3: ניתוח רגשות**
```python
# נתח רגשות ומצא את אחוז הביקורות החיוביות

sentiment_analyzer = SentimentAnalyzer()
df_sentiment = sentiment_analyzer.analyze_dataframe(df, 'reviews')
scores = df_sentiment['sentiment_score'].tolist()
stats = sentiment_analyzer.get_sentiment_statistics(scores)
print(f"Positive percentage: {stats['positive_percentage']}%")
```

---

## ⚠️ פתרון בעיות נפוצות

### בעיה: NLTK לא נמצא
```python
# אם NLTK לא זמין, המערכת תעבור למצב fallback
# הקוד ימשיך לעבוד עם sentiment analysis פשוט יותר
```

### בעיה: קובץ לא נטען
```python
# בדוק את הנתיב והפורמט
loader = UniversalDataLoader()
try:
    df = loader.load_data("file.csv")
except FileNotFoundError:
    print("הקובץ לא נמצא - בדוק את הנתיב")
except ValueError as e:
    print(f"פורמט קובץ לא נתמך: {e}")
```

### בעיה: עמודה לא קיימת
```python
# תמיד בדוק שהעמודה קיימת
if 'text_column' in df.columns:
    # ביצע את הפעולה
    pass
else:
    print("העמודה לא קיימת")
    print("עמודות זמינות:", df.columns.tolist())
```

---

## 📝 סיכום לקראת המבחן

### צ'קליסט מוכנות למבחן:

- [ ] **טעינת נתונים**: יודע לטעון CSV, JSON, Excel
- [ ] **ניקוי טקסט**: הסרת פיסוק, lowercase, ניקוי רווחים
- [ ] **ניתוח רגשות**: VADER scores, סיווג positive/negative/neutral
- [ ] **סטטיסטיקות טקסט**: ספירת מילים, מילים נפוצות, אורכי טקסט
- [ ] **עיבוד DataFrame**: סינון, קיבוץ, value_counts
- [ ] **Pipeline מלא**: יודע לשלב את כל השלבים

### פקודות מהירות למבחן:
```python
# טעינה מהירה
from shared_utilities.data_science import *

# ניתוח מלא במעט שורות
loader = UniversalDataLoader()
df = loader.load_data("file.csv")

cleaner = TextCleaner()
df = cleaner.clean_dataframe(df, ['text'], remove_punctuation=True, to_lowercase=True)

sentiment = SentimentAnalyzer()
df = sentiment.analyze_dataframe(df, 'text', add_detailed=True)

analyzer = TextAnalyzer()
report = analyzer.generate_summary_report(df, 'text')
```

**בהצלחה במבחן! 🎯**