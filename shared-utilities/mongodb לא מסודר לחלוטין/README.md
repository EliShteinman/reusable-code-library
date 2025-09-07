# MongoDB Utils - ערכת כלים מקצועית ל-MongoDB

ערכת כלים מלאה עם הפרדה מושלמת בין clients ו-repositories, תמיכה מלאה בסינכרוני ואסינכרוני.

## 📁 מבנה הקבצים - CLEAN ARCHITECTURE

```
shared-utilities/mongodb/
├── __init__.py                      # יבואים ופונקציות מהירות
├── mongodb_sync_client.py           # לקוח סינכרוני (CONNECTION ONLY)
├── mongodb_async_client.py          # לקוח אסינכרוני (CONNECTION ONLY)  
├── mongodb_sync_repository.py       # repository סינכרוני (CRUD ONLY)
├── mongodb_async_repository.py      # repository אסינכרוני (CRUD ONLY)
├── mongo_client.py                  # singleton (legacy - unchanged)
├── examples.py                      # דוגמאות מקיפות
└── README.md                        # המדריך הזה
```

## 🚀 התקנה מהירה

```bash
pip install pymongo
pip install pandas  # לאינטגרציית DataFrame
```

## 🎯 העקרונות החדשים - FIXED ARCHITECTURE

### ✅ **ההפרדה המושלמת:**
- **Connection Clients:** רק חיבור ופעולות RAW (`execute_*`)
- **CRUD Repositories:** רק לוגיקה עסקית (`create`, `search`, `aggregate`)
- **4 קלאסים נפרדים:** לא עוד בלגן של sync/async באותו מקום!
- **אין עוד runtime detection מכוער!**

### ❌ **מה תיקנו:**
- ❌ אין יותר Repository יחיד עם `if self.is_async`
- ❌ אין יותר `RuntimeError` exceptions
- ❌ אין יותר בלגן של operations בclient

---

## 📊 מה זה MongoDB? - למבחן

### **MongoDB vs SQL:**
| SQL Database | → | MongoDB |
|-------------|---|---------|
| Database    | → | Database |
| Table       | → | Collection |
| Row         | → | Document |
| Column      | → | Field |
| JOIN        | → | Embed/Reference |
| WHERE       | → | Query Filter |

### **מושגי יסוד למבחן:**
- **Database** - מכיל collections (כמו schema)
- **Collection** - מכיל documents (כמו table)
- **Document** - רשומה בפורמט BSON עם `_id` ייחודי
- **Field** - שדה בdocument (כמו column)
- **Index** - לשיפור ביצועי חיפוש
- **Aggregation Pipeline** - עיבוד נתונים מתקדם
- **ObjectId** - מפתח ייחודי אוטומטי של MongoDB

---

## 🔧 שימוש בסיסי - Sync

### 1. הקמה מהירה
```python
from shared_utilities.mongodb import MongoDBSyncClient, MongoDBSyncRepository

# יצירת client (CONNECTION ONLY) ו-repository (CRUD ONLY)
client = MongoDBSyncClient("mongodb://localhost:27017", "test_db")
client.connect()
repo = MongoDBSyncRepository(client, "users")

# יצירת index לביצועים
repo.create_index("email", unique=True)
repo.create_text_index(["name", "description"])  # לחיפוש טקסט
```

### 2. CRUD בסיסי
```python
# CREATE - יצירת document
user_id = repo.create({
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "city": "Tel Aviv",
    "hobbies": ["reading", "coding", "gaming"]
})
print(f"Created user: {user_id}")

# READ - קריאת document
user = repo.get_by_id(user_id)
print(f"User: {user['name']} - {user['email']}")

# UPDATE - עדכון document  
success = repo.update(user_id, {
    "age": 31,
    "city": "Jerusalem",
    "hobbies": ["reading", "coding", "gaming", "traveling"]
})

# DELETE - מחיקת document
success = repo.delete(user_id)
```

### 3. חיפוש מתקדם - Query Building System
```python
# חיפוש טקסט חופשי (צריך text index)
results = repo.search(
    text_search="john developer",
    limit=10
)
print(f"Found {results['total_hits']} results")

# חיפוש מדויק (exact match) - field filters
young_users = repo.search(
    field_filters={"city": "Tel Aviv", "active": True},
    limit=20
)

# חיפוש טווח (range filters)
adults = repo.search(
    range_filters={"age": {"gte": 18, "lte": 65}},
    limit=15
)

# חיפוש משולב - כל הפילטרים ביחד
filtered_results = repo.search(
    text_search="developer",                      # חיפוש טקסט
    field_filters={"city": "Tel Aviv", "active": True},  # מדויק
    range_filters={"age": {"gte": 25, "lte": 40}}, # טווח
    in_filters={"skills": ["python", "javascript"]}, # ערכים ברשימה
    exists_filters=["email", "phone"],             # שדות שקיימים
    sort_by=[("created_at", -1)],                  # מיון
    limit=10,
    skip=0
)

# חיפוש regex (תבניות)
email_patterns = repo.search(
    regex_filters={"email": ".*@gmail\\.com"},
    limit=10
)

# בדיקת קיום שדות
has_phone = repo.search(
    exists_filters=["phone", "address"],
    limit=10
)
```

### 4. Bulk Operations - עיבוד מסיבי
```python
# Bulk create - יצירה מסיבית (הכי יעיל!)
users = [
    {"name": "Alice", "age": 25, "city": "Tel Aviv"},
    {"name": "Bob", "age": 30, "city": "Jerusalem"},
    {"name": "Carol", "age": 35, "city": "Haifa"},
    {"name": "David", "age": 28, "city": "Tel Aviv"}
]
result = repo.bulk_create(users)
print(f"Created: {result['success_count']}/{len(users)} users")

# Bulk update - עדכון מסיבי
updates = [
    {"filter": {"name": "Alice"}, "update": {"age": 26, "active": True}},
    {"filter": {"name": "Bob"}, "update": {"city": "Eilat", "active": False}}
]
result = repo.bulk_update(updates)
print(f"Updated: {result['success_count']} users")

# Bulk delete - מחיקה מסיבית
filters_to_delete = [
    {"name": "Alice"},
    {"age": {"$lt": 25}}
]
result = repo.bulk_delete(filters_to_delete)
print(f"Deleted: {result['success_count']} users")
```

---

## ⚡ שימוש אסינכרוני - Async

### הגדרה אסינכרונית
```python
import asyncio
from shared_utilities.mongodb import MongoDBAsyncClient, MongoDBAsyncRepository

async def async_example():
    # יצירת client ו-repository אסינכרוניים
    client = MongoDBAsyncClient("mongodb://localhost:27017", "async_db")
    await client.connect()  # ⚠️ חשוב!
    repo = MongoDBAsyncRepository(client, "async_users")
    
    # כל הפעולות זהות אבל עם await
    user_id = await repo.create({"name": "Async User", "age": 25})
    user = await repo.get_by_id(user_id)
    
    results = await repo.search(
        field_filters={"age": {"$gte": 20}},
        limit=10
    )
    
    bulk_result = await repo.bulk_create([
        {"name": "User 1", "age": 20},
        {"name": "User 2", "age": 25}
    ])
    
    # ⚠️ חשוב לסגור!
    await client.close()
    
    return results

# הרצה
results = asyncio.run(async_example())
```

---

## 📈 Aggregations - ניתוחים וסטטיסטיקות

### אגרגציות נפוצות למבחן
```python
# 1. ממוצע גיל לפי עיר (כמו GROUP BY + AVG)
agg_results = repo.aggregate([
    {"$group": {
        "_id": "$city",
        "avg_age": {"$avg": "$age"},
        "count": {"$sum": 1}
    }},
    {"$sort": {"avg_age": -1}}
])

for result in agg_results:
    city = result['_id']
    avg_age = result['avg_age']
    count = result['count']
    print(f"{city}: {count} users, avg age: {avg_age:.1f}")

# 2. סטטיסטיקות בסיסיות (min, max, avg, sum, count)
stats = repo.aggregate([
    {"$group": {
        "_id": None,
        "min_age": {"$min": "$age"},
        "max_age": {"$max": "$age"},
        "avg_age": {"$avg": "$age"},
        "total_users": {"$sum": 1}
    }}
])
print(f"Age stats: min={stats[0]['min_age']}, max={stats[0]['max_age']}")

# 3. התפלגות טווחי גילאים
age_ranges = repo.aggregate([
    {"$bucket": {
        "groupBy": "$age",
        "boundaries": [0, 18, 30, 50, 100],
        "default": "Other",
        "output": {
            "count": {"$sum": 1},
            "users": {"$push": "$name"}
        }
    }}
])

for bucket in age_ranges:
    range_id = bucket['_id']
    count = bucket['count']
    print(f"Age range {range_id}: {count} users")

# 4. חיפוש עם אגרגציה מורכבת
user_skills = repo.aggregate([
    {"$match": {"city": "Tel Aviv"}},           # סינון
    {"$unwind": "$skills"},                     # פירוק מערך
    {"$group": {                                # קיבוץ
        "_id": "$skills",
        "count": {"$sum": 1},
        "users": {"$addToSet": "$name"}
    }},
    {"$sort": {"count": -1}},                   # מיון
    {"$limit": 10}                              # הגבלה
])

# 5. ספירה פשוטה
tel_aviv_count = repo.count(field_filters={"city": "Tel Aviv"})
young_count = repo.count(range_filters={"age": {"lte": 30}})
```

---

## 🐼 אינטגרציה עם Pandas

### DataFrame ↔ MongoDB
```python
import pandas as pd

# 1. יצירת נתונים ב-DataFrame
df = pd.DataFrame({
    'user_id': ['U001', 'U002', 'U003'],
    'name': ['Alice', 'Bob', 'Carol'],
    'age': [25, 30, 35],
    'city': ['Tel Aviv', 'Jerusalem', 'Haifa'],
    'active': [True, False, True]
})

# 2. העלאה מ-DataFrame ל-MongoDB
result = repo.bulk_create_from_dataframe(df, id_column='user_id')
print(f"Uploaded: {result['success_count']} records")

# 3. הורדה מ-MongoDB ל-DataFrame
search_df = repo.to_dataframe(
    field_filters={"city": "Tel Aviv"},
    range_filters={"age": {"gte": 25}},
    limit=100
)

# 4. ניתוח עם pandas
if not search_df.empty:
    avg_age = search_df['age'].mean()
    city_counts = search_df['city'].value_counts()
    active_percentage = search_df['active'].mean() * 100
    
    print(f"Average age: {avg_age:.1f}")
    print(f"Active users: {active_percentage:.1f}%")
    print("City distribution:")
    print(city_counts)
```

---

## 🎯 דפוסים נפוצים למבחן

### 1. חיפוש מורכב
```python
# שאלת מבחן טיפוסית: "מצא משתמשים פעילים בתל אביב, בגיל 25-40, עם כישורי פייתון"
results = repo.search(
    field_filters={"city": "Tel Aviv", "active": True},
    range_filters={"age": {"gte": 25, "lte": 40}},
    in_filters={"skills": ["python"]},
    sort_by=[("created_at", -1)],
    limit=20
)
```

### 2. ניתוח נתונים
```python
# שאלת מבחן: "חשב ממוצע גיל לפי עיר ומצא העיר הצעירה ביותר"
agg_results = repo.aggregate([
    {"$group": {
        "_id": "$city",
        "avg_age": {"$avg": "$age"},
        "count": {"$sum": 1}
    }},
    {"$sort": {"avg_age": 1}}  # מיון עולה - הצעירה ביותר ראשונה
])

youngest_city = agg_results[0]
print(f"Youngest city: {youngest_city['_id']} (avg age: {youngest_city['avg_age']:.1f})")
```

### 3. Bulk Operations
```python
# שאלת מבחן: "העלה 1000 משתמשים מקובץ CSV"
import pandas as pd

# קריאת CSV
df = pd.read_csv("users.csv")

# ניקוי נתונים
df = df.dropna()
df['age'] = pd.to_numeric(df['age'], errors='coerce')

# העלאה מסיבית
result = repo.bulk_create_from_dataframe(df, id_column='user_id')
print(f"Success: {result['success_count']}, Errors: {result['error_count']}")
```

### 4. מעקב אחר שינויים
```python
# עדכון סטטוס משתמשים והוספת timestamp
from datetime import datetime

updates = []
for user_id in user_ids:
    updates.append({
        "filter": {"_id": user_id},
        "update": {
            "status": "updated",
            "last_login": datetime.now(),
            "active": True
        }
    })

result = repo.bulk_update(updates)
```

---

## ⚡ פונקציות מהירות למבחן

### Setup מהיר
```python
# Sync
from shared_utilities.mongodb import setup_mongodb_sync
client, repo = setup_mongodb_sync("mongodb://localhost:27017", "test_db", "users")

# Async
from shared_utilities.mongodb import setup_mongodb_async
client, repo = await setup_mongodb_async("mongodb://localhost:27017", "test_db", "users")
```

### פקודות חיוניות
```python
# יצירה מהירה
user_id = repo.create({"name": "Test", "age": 25})

# חיפוש מהיר
results = repo.search(field_filters={"city": "Tel Aviv"}, limit=5)

# ספירה מהירה  
count = repo.count(field_filters={"active": True})

# אגרגציה מהירה
stats = repo.aggregate([{"$group": {"_id": None, "avg_age": {"$avg": "$age"}}}])

# DataFrame מהיר
df = repo.to_dataframe(limit=100)
```

---

## 🚨 שגיאות נפוצות ופתרונות

### 1. בעיות חיבור
```python
# MongoDB לא רץ
# פתרון: mongod --dbpath /data/db
# או: docker run -p 27017:27017 mongo
```

### 2. Index לא קיים
```python
# בדיקה ויצירת index
repo.create_text_index(["name", "description"])
repo.create_index("email", unique=True)
```

### 3. ObjectId vs String
```python
# חיפוש לפי ObjectId
from bson import ObjectId
user = repo.get_by_id(ObjectId("507f1f77bcf86cd799439011"))

# חיפוש לפי שדה אחר
user = repo.get_by_id("john@example.com", id_field="email")
```

### 4. שגיאות aggregation
```python
# תמיד לבדוק תוצאות aggregation
results = repo.aggregate(pipeline)
if not results:
    print("No results from aggregation")
```

---

## 📝 טיפים למבחן

### מה חשוב לדעת:
1. **Query Operators:** `$eq`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$regex`, `$exists`
2. **Aggregation Stages:** `$match`, `$group`, `$sort`, `$limit`, `$project`, `$unwind`
3. **Index Types:** single field, compound, text, unique
4. **Bulk Operations:** תמיד יותר יעיל מפעולות יחידות
5. **ObjectId:** מפתח ייחודי של MongoDB, נוצר אוטומטיש

### דפוסי קוד שחוזרים במבחנים:
```python
# 1. יצירת repository
client = MongoDBSyncClient("mongodb://localhost:27017", "db_name")
client.connect()
repo = MongoDBSyncRepository(client, "collection_name")

# 2. חיפוש משולב
results = repo.search(
    field_filters={"field": "value"},
    range_filters={"age": {"gte": 18}},
    limit=10
)

# 3. אגרגציה בסיסית
agg = repo.aggregate([
    {"$group": {"_id": "$field", "count": {"$sum": 1}}}
])

# 4. DataFrame integration
df = repo.to_dataframe()
repo.bulk_create_from_dataframe(df)
```

**בהצלחה במבחן! 🎯**

---

## 🔧 Troubleshooting מהיר

| בעיה | פתרון |
|------|--------|
| Connection refused | `mongod --dbpath /data/db` |
| Collection not found | MongoDB יוצר אוטומטית |
| Index error | `repo.create_index(field)` |
| ObjectId error | השתמש ב-`str()` או `ObjectId()` |
| Aggregation empty | בדוק pipeline syntax |

**זה הכל! MongoDB מוכן למבחן! 🚀**