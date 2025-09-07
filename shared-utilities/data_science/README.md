# Data Science Utilities - Organized Architecture 🚀

ערכת כלים מקצועית עם **ארכיטקטורה מאורגנת**: הפרדה ברורה בין בסיסי למתקדם, Clients נפרדים מ-Repositories, תמיכה מלאה ב-Sync/Async.

## 📁 מבנה מאורגן

```
shared-utilities/data_science/
├── basic/                              # רכיבים בסיסיים (ללא תלותיות)
│   ├── clients/                        # Connection Management
│   │   ├── data_loader_client.py       # טעינת קבצים
│   │   └── text_processor_client.py    # עיבוד טקסט בסיסי
│   └── repositories/                   # CRUD Operations
│       ├── text_cleaning_repo.py       # ניקוי טקסט
│       ├── text_analysis_repo.py       # ניתוח טקסט
│       └── sentiment_analysis_repo.py  # ניתוח רגשות בסיסי
│
├── advanced/                           # רכיבים מתקדמים (ספריות חיצוניות)
│   ├── clients/
│   │   ├── sync/                       # לקוחות סינכרוניים
│   │   │   ├── sentiment_client.py     # VADER, TextBlob, spaCy
│   │   │   └── nlp_client.py          # NLTK, spaCy stemming
│   │   └── async/                      # לקוחות אסינכרוניים
│   │       ├── sentiment_client.py     # Async sentiment
│   │       └── nlp_client.py          # Async NLP
│   │
│   ├── repositories/
│   │   ├── sync/                       # Repositories סינכרוניים
│   │   │   ├── sentiment_repo.py       # Multi-library sentiment
│   │   │   ├── nlp_repo.py            # Stemming/Lemmatization
│   │   │   └── hebrew_repo.py         # עיבוד עברית
│   │   └── async/                      # Repositories אסינכרוניים
│   │       ├── sentiment_repo.py       # Async sentiment ops
│   │       ├── nlp_repo.py            # Async NLP ops
│   │       └── hebrew_repo.py         # Async Hebrew ops
│   │
│   └── base/                          # Abstract Base Classes
│       ├── sentiment_base.py          # SentimentAnalyzerBase
│       ├── text_processor_base.py     # TextProcessorBase
│       └── factory.py                 # ProcessorFactory
│
└── utils/                              # כלי עזר משותפים
    ├── config.py                       # ProcessingConfig
    ├── helpers.py                      # Pipeline functions
    └── constants.py                    # קבועים משותפים
```

## 🎯 יתרונות הארכיטקטורה

### ✅ הפרדה ברורה
- **Basic vs Advanced**: רכיבים בסיסיים ללא תלותיות, מתקדמים עם ספריות
- **Clients vs Repositories**: ניהול חיבורים נפרד מפעולות CRUD
- **Sync vs Async**: תמיכה מלאה בשני מודלים

### ✅ עמידות במבחן
- רכיבים בסיסיים **תמיד עובדים**
- Fallback אוטומטי אם ספריות חסרות
- מבנה אחיד ועקבי

### ✅ הרחבה קלה
- כל רכיב במקום הנכון שלו
- הוספת ספריות חדשות פשוטה
- ארכיטקטורה מודולרית

## 🚀 שימוש מהיר

### Basic Pipeline (תמיד עובד)
```python
from shared_utilities.data_science import (
    DataLoaderClient, TextCleaningRepository, 
    SentimentAnalysisRepository, create_basic_pipeline
)

# יצירת pipeline בסיסי
pipeline = create_basic_pipeline(
    data_source="reviews.csv",
    text_column="review_text"
)

# טעינת נתונים
data_client = pipeline['components']['data_client']
with data_client.connect("reviews.csv") as conn:
    df = conn.load_data()

# ניקוי טקסט
cleaning_repo = pipeline['components']['cleaning_repo']
cleaning_result = cleaning_repo.create_cleaning_operation(
    data=df,
    text_columns=['review_text']
)

# ניתוח רגשות
sentiment_repo = pipeline['components']['sentiment_repo']
sentiment_result = sentiment_repo.create_sentiment_analysis(
    data=cleaning_result['cleaned_data'],
    text_column='review_text'
)

print(f"Processed {len(sentiment_result['analyzed_data'])} reviews")
```

### Advanced Pipeline (אם זמין)
```python
from shared_utilities.data_science import (
    SentimentClient, NLPClient, 
    AdvancedSentimentRepository, create_advanced_pipeline
)

# יצירת pipeline מתקדם
pipeline = create_advanced_pipeline(
    data_source="reviews.csv",
    text_column="review_text",
    mode='sync'  # או 'async'
)

# ניתוח רגשות מתקדם
sentiment_client = pipeline['components']['sentiment_client']
with sentiment_client.create_session() as session:
    # השוואת analyzers
    result_vader = session.analyze_with_analyzer(text, 'vader')
    result_textblob = session.analyze_with_analyzer(text, 'textblob')
    result_ensemble = session.analyze_with_ensemble(['vader', 'textblob'])

# עיבוד NLP מתקדם
nlp_client = pipeline['components']['nlp_client']
with nlp_client.create_session() as session:
    stems = session.extract_stems(text)
    lemmas = session.extract_lemmas(text)
    roots = session.extract_roots(text)
```

### Pipeline אוטומטי (בחירה חכמה)
```python
from shared_utilities.data_science import execute_complete_pipeline

# Pipeline שבוחר אוטומטית את הטוב ביותר הזמין
results = execute_complete_pipeline(
    data_source="reviews.csv",
    text_column="review_text",
    pipeline_type='auto',  # בוחר אוטומטית
    category_column="product_type"
)

print(f"Pipeline type used: {results['pipeline_info']['type']}")
print(f"Processing successful: {results['summary']['processing_successful']}")
```

## 🔧 תכונות מתקדמות

### Factory Pattern
```python
from shared_utilities.data_science.advanced.base import ProcessorFactory

# יצירת analyzers ספציפיים
vader_analyzer = ProcessorFactory.create_sentiment_analyzer("vader")
textblob_analyzer = ProcessorFactory.create_sentiment_analyzer("textblob")

# יצירת processors
nltk_processor = ProcessorFactory.create_text_processor("nltk")
spacy_processor = ProcessorFactory.create_text_processor("spacy")
```

### Async Operations
```python
from shared_utilities.data_science.advanced.clients.async_ import AsyncSentimentClient

async def analyze_large_dataset():
    async_client = AsyncSentimentClient()
    
    async with async_client.create_session() as session:
        tasks = [
            session.analyze_batch_async(batch) 
            for batch in text_batches
        ]
        results = await asyncio.gather(*tasks)
    
    return results
```

### Hebrew Processing
```python
from shared_utilities.data_science.advanced.repositories.sync import HebrewRepository

hebrew_repo = HebrewRepository()

hebrew_result = hebrew_repo.create_hebrew_analysis(
    data=pd.DataFrame([{'text': 'המוצר הזה מעולה ומומלץ בחום'}]),
    text_column='text'
)

print(f"Hebrew sentiment: {hebrew_result['results'][0]['sentiment']}")
print(f"Hebrew stems: {hebrew_result['results'][0]['stems']}")
```

## 🎓 תרחישי מבחן

### תרחיש 1: "השתמש ב-TextBlob"
```python
# אם TextBlob זמין
try:
    analyzer = ProcessorFactory.create_sentiment_analyzer("textblob")
    result = analyzer.analyze_sentiment(text)
except:
    # Fallback אוטומטי
    result = quick_sentiment_check(text, method="auto")
```

### תרחיש 2: "בצע Stemming ו-Lemmatization"
```python
# עם NLTK
from shared_utilities.data_science.advanced.clients.sync import NLPClient

nlp_client = NLPClient()
with nlp_client.create_session() as session:
    stems = session.extract_stems_with_nltk(text)
    lemmas = session.extract_lemmas_with_nltk(text)

# עם spaCy (אם זמין)
spacy_stems = session.extract_stems_with_spacy(text)
spacy_lemmas = session.extract_lemmas_with_spacy(text)
```

### תרחיש 3: "ניתוח טקסט בעברית"
```python
from shared_utilities.data_science.advanced.repositories.sync import HebrewRepository

hebrew_repo = HebrewRepository()
result = hebrew_repo.create_hebrew_analysis(
    data=pd.DataFrame([{'text': 'טקסט בעברית'}]),
    text_column='text'
)
```

## 📊 בדיקת מצב המערכת

```python
from shared_utilities.data_science import get_system_capabilities, validate_data_science_setup

# בדיקת יכולות המערכת
capabilities = get_system_capabilities()
print(f"Basic components: {capabilities['basic_components']}")
print(f"Advanced sync: {capabilities['advanced_sync']}")
print(f"Advanced async: {capabilities['advanced_async']}")
print(f"External libraries: {capabilities['external_libraries']}")

# ולידציה מלאה
validation = validate_data_science_setup()
print(f"Overall status: {validation['overall_status']}")
print(f"Recommendations: {validation['recommendations']}")
```

## 🛠️ התקנה

### בסיסי (תמיד עובד)
```bash
pip install pandas numpy
```

### מתקדם (לתכונות מלאות)
```bash
pip install pandas numpy nltk textblob spacy openpyxl
python -m spacy download en_core_web_sm
```

## 🎯 עיקרי הלקחים למבחן

- ✅ **מבנה מאורגן**: הפרדה ברורה בין רכיבים
- ✅ **Client/Repository Pattern**: ארכיטקטורה מקצועית
- ✅ **Sync/Async Support**: תמיכה בשני מודלים
- ✅ **תמיד עובד**: רכיבים בסיסיים ללא תלותיות
- ✅ **Fallback אוטומטי**: עמידות בפני ספריות חסרות
- ✅ **Factory Pattern**: יצירת objects גמישה
- ✅ **תמיכה בעברית**: עיבוד טקסט עברי מלא

**בהצלחה במבחן! 🎉**