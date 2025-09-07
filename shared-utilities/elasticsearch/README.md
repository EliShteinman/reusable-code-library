# Elasticsearch Utils - ערכת כלים מקצועית ל-Elasticsearch

ערכת כלים מותאמת למבחנים ופרויקטים, עם הפרדה מושלמת בין clients ו-repositories, תמיכה מלאה בסינכרוני ואסינכרוני.

## 📁 מבנה הקבצים - CLEAN ARCHITECTURE

```
shared-utilities/elasticsearch/
├── __init__.py                      # יבואים ופונקציות מהירות
├── elasticsearch_sync_client.py     # לקוח סינכרוני (CONNECTION ONLY)
├── elasticsearch_async_client.py    # לקוח אסינכרוני (CONNECTION ONLY)  
├── elasticsearch_sync_repository.py # repository סינכרוני (CRUD ONLY)
├── elasticsearch_async_repository.py# repository אסינכרוני (CRUD ONLY)
├── examples.py                      # דוגמאות מקיפות
└── README.md                        # המדריך הזה
```

## 🚀 התקנה מהירה

```bash
pip install elasticsearch
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
- ❌ אין יותר בלגן של aggregations בclient

---

## 📊 מה זה Elasticsearch? - למבחן

### **Elasticsearch vs SQL:**
| SQL Database | → | Elasticsearch |
|-------------|---|---------------|
| Database    | → | Index         |
| Table       | → | Index         |
| Row         | → | Document      |
| Column      | → | Field         |
| Schema      | → | Mapping       |
| WHERE       | → | Query DSL     |

### **מושגי יסוד למבחן:**
- **Index** - מכל documents מאותו סוג (כמו table)
- **Document** - רשומה בפורמט JSON עם `_id` ייחודי
- **Mapping** - הגדרת סוג השדות (`text`, `keyword`, `date`, `float`)
- **Query DSL** - שפת חיפוש גמישה של Elasticsearch
- **Aggregations** - ניתוחים וסטטיסטיקות (כמו GROUP BY)
- **Shards** - חלוקה פנימית לביצועים
- **Replicas** - עותקים לזמינות גבוהה

---

## 🔧 שימוש בסיסי - Sync

### 1. הקמה מהירה
```python
from shared_utilities.elasticsearch import ElasticsearchSyncClient, ElasticsearchSyncRepository

# יצירת client (CONNECTION ONLY) ו-repository (CRUD ONLY)
client = ElasticsearchSyncClient("http://localhost:9200")
repo = ElasticsearchSyncRepository(client, "products")

# הקמת index עם mapping
mapping = {
    "properties": {
        "name": {"type": "text", "analyzer": "standard"},
        "price": {"type": "float"},
        "category": {"type": "keyword"},  # לסינון מדויק
        "description": {"type": "text"},  # לחיפוש טקסט
        "in_stock": {"type": "boolean"},
        "created_at": {"type": "date"},
        "tags": {"type": "keyword"}       # מערך של מילות מפתח
    }
}

settings = {
    "number_of_shards": 1,
    "number_of_replicas": 0  # לפיתוח מקומי
}

repo.initialize_index(mapping, settings)
```

### 2. CRUD בסיסי
```python
# CREATE - יצירת document
doc_id = repo.create({
    "name": "Gaming Laptop",
    "price": 1299.99,
    "category": "electronics",
    "description": "High-performance gaming laptop with RTX graphics",
    "in_stock": True,
    "tags": ["gaming", "laptop", "rtx"]
})
print(f"Created document: {doc_id}")

# READ - קריאת document
product = repo.get_by_id(doc_id)
print(f"Product: {product['name']} - ${product['price']}")

# UPDATE - עדכון document  
success = repo.update(doc_id, {
    "price": 1199.99,
    "in_stock": False,
    "tags": ["gaming", "laptop", "rtx", "sale"]
})

# DELETE - מחיקת document
success = repo.delete(doc_id)
```

### 3. חיפוש מתקדם - Query Building System
```python
# חיפוש טקסט חופשי (full-text search)
results = repo.search(
    text_search="gaming laptop",
    limit=10
)
print(f"Found {results['total_hits']} results")

# חיפוש מדויק (exact match) - term filters
electronics = repo.search(
    term_filters={"category": "electronics", "in_stock": True},
    limit=20
)

# חיפוש טווח (range filters)
expensive_products = repo.search(
    range_filters={"price": {"gte": 1000, "lte": 5000}},
    limit=15
)

# חיפוש משולב - כל הפילטרים ביחד
filtered_results = repo.search(
    text_search="laptop",                           # חיפוש טקסט
    term_filters={"category": "electronics", "in_stock": True},  # מדויק
    range_filters={"price": {"lte": 2000}},        # טווח
    sort_by=[{"price": {"order": "asc"}}],         # מיון
    limit=10,
    offset=0
)

# חיפוש wildcard (תווים כלליים)
wireless_products = repo.search(
    wildcard_filters={"name": "*wireless*"},
    limit=10
)

# חיפוש fuzzy (סלחני לשגיאות כתיב)
fuzzy_results = repo.search(
    fuzzy_search={"name": "lapto"},  # יחפש "laptop"
    limit=5
)

# בדיקת קיום שדות
has_tags = repo.search(
    exists_filters=["tags", "description"],
    limit=10
)
```

### 4. Bulk Operations - עיבוד מסיבי
```python
# Bulk create - יצירה מסיבית (הכי יעיל!)
products = [
    {"name": "Wireless Mouse", "price": 29.99, "category": "electronics"},
    {"name": "Mechanical Keyboard", "price": 79.99, "category": "electronics"},
    {"name": "4K Monitor", "price": 299.99, "category": "electronics"},
    {"name": "Python Guide", "price": 39.99, "category": "books"}
]
result = repo.bulk_create(products)
print(f"Created: {result['success_count']}/{len(products)} products")

# Bulk update - עדכון מסיבי
updates = [
    {"_id": "product1", "doc": {"price": 25.99, "in_stock": False}},
    {"_id": "product2", "doc": {"price": 75.99, "tags": ["keyboard", "sale"]}}
]
result = repo.bulk_update(updates)
print(f"Updated: {result['success_count']} products")

# Bulk delete - מחיקה מסיבית
result = repo.bulk_delete(["product1", "product2", "product3"])
print(f"Deleted: {result['success_count']} products")
```

---

## ⚡ שימוש אסינכרוני - Async

### הגדרה אסינכרונית
```python
import asyncio
from shared_utilities.elasticsearch import ElasticsearchAsyncClient, ElasticsearchAsyncRepository

async def async_example():
    # יצירת client ו-repository אסינכרוניים
    client = ElasticsearchAsyncClient("http://localhost:9200")
    await client.connect()  # ⚠️ חשוב!
    repo = ElasticsearchAsyncRepository(client, "async_products")
    
    # כל הפעולות זהות אבל עם await
    doc_id = await repo.create({"name": "Async Product", "price": 99.99})
    product = await repo.get_by_id(doc_id)
    
    results = await repo.search(
        text_search="async",
        term_filters={"price": {"gte": 50}},
        limit=10
    )
    
    bulk_result = await repo.bulk_create([
        {"name": "Product 1", "price": 10.99},
        {"name": "Product 2", "price": 20.99}
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
# 1. ממוצע מחירים לפי קטגוריה (כמו GROUP BY + AVG)
agg_results = repo.aggregate({
    "avg_price_by_category": {
        "terms": {"field": "category"},  # קיבוץ לפי קטגוריה
        "aggs": {
            "avg_price": {"avg": {"field": "price"}}  # ממוצע מחיר
        }
    }
})

for bucket in agg_results['avg_price_by_category']['buckets']:
    category = bucket['key']
    count = bucket['doc_count']
    avg_price = bucket['avg_price']['value']
    print(f"{category}: {count} products, avg price: ${avg_price:.2f}")

# 2. סטטיסטיקות בסיסיות (min, max, avg, sum, count)
stats = repo.aggregate({
    "price_stats": {"stats": {"field": "price"}}
})
print(f"Price stats: min=${stats['price_stats']['min']}, max=${stats['price_stats']['max']}")

# 3. התפלגות טווחי מחירים
price_ranges = repo.aggregate({
    "price_ranges": {
        "range": {
            "field": "price",
            "ranges": [
                {"to": 50, "key": "cheap"},
                {"from": 50, "to": 200, "key": "medium"},
                {"from": 200, "key": "expensive"}
            ]
        }
    }
})

for bucket in price_ranges['price_ranges']['buckets']:
    range_key = bucket['key']
    count = bucket['doc_count']
    print(f"{range_key}: {count} products")

# 4. אגרגציה מותנית (עם פילטרים)
filtered_agg = repo.aggregate(
    {"avg_electronics_price": {"avg": {"field": "price"}}},
    term_filters={"category": "electronics", "in_stock": True}
)

# 5. ספירה פשוטה
electronics_count = repo.count(term_filters={"category": "electronics"})
expensive_count = repo.count(range_filters={"price": {"gte": 500}})
```

---

## 🐼 אינטגרציה עם Pandas

### DataFrame ↔ Elasticsearch
```python
import pandas as pd

# 1. יצירת נתונים ב-DataFrame
df = pd.DataFrame({
    'product_id': ['P001', 'P002', 'P003'],
    'name': ['Gaming Mouse', 'Keyboard', 'Monitor'],
    'price': [49.99, 79.99, 299.99],
    'category': ['electronics', 'electronics', 'electronics'],
    'in_stock': [True, False, True]
})

# 2. העלאה מ-DataFrame ל-Elasticsearch
result = repo.bulk_create_from_dataframe(df, id_column='product_id')
print(f"Uploaded: {result['success_count']} records")

# 3. הורדה מ-Elasticsearch ל-DataFrame
search_df = repo.to_dataframe(
    term_filters={"category": "electronics"},
    range_filters={"price": {"gte": 50}},
    limit=100
)

# 4. ניתוח עם pandas
if not search_df.empty:
    total_revenue = search_df['price'].sum()
    avg_price = search_df['price'].mean()
    category_counts = search_df['category'].value_counts()
    
    print(f"Total value: ${total_revenue:.2f}")
    print(f"Average price: ${avg_price:.2f}")
    print("Category breakdown:")
    print(category_counts)
```

---

## 🔍 Scroll Search - עיבוד נתונים גדולים

### סריקת כמויות גדולות (לא deep pagination!)
```python
# 1. סריקה דרך כל הdocuments
all_products = []
for product in repo.scroll_search(scroll_size=1000):  # בצבי של 1000
    all_products.append(product)
    if len(all_products) >= 10000:  # הגבלה לדוגמה
        break

print(f"Processed {len(all_products)} products")

# 2. סריקה עם פילטרים
expensive_products = []
for product in repo.scroll_search(
    range_filters={"price": {"gte": 500}},
    scroll_size=500
):
    expensive_products.append(product)

# 3. עיבוד streaming (חסכוני בזיכרון)
def process_products_streaming():
    total_value = 0
    count = 0
    
    for product in repo.scroll_search(scroll_size=1000):
        total_value += product.get('price', 0)
        count += 1
        
        if count % 1000 == 0:
            print(f"Processed {count} products, total value: ${total_value:.2f}")
    
    return total_value, count

total, count = process_products_streaming()
```

---

## 🎯 דפוסים נפוצים למבחן

### 1. חיפוש מורכב
```python
# שאלת מבחן טיפוסית: "מצא מוצרי אלקטרוניקה במלאי, במחיר 100-500$, שמכילים 'gaming'"
results = repo.search(
    text_search="gaming",
    term_filters={"category": "electronics", "in_stock": True},
    range_filters={"price": {"gte": 100, "lte": 500}},
    sort_by=[{"price": {"order": "asc"}}],
    limit=20
)
```

### 2. ניתוח נתונים
```python
# שאלת מבחן: "חשב ממוצע מחיר לפי קטגוריה ומצא הקטגוריה היקרה ביותר"
agg_results = repo.aggregate({
    "categories": {
        "terms": {"field": "category"},
        "aggs": {"avg_price": {"avg": {"field": "price"}}}
    }
})

# עיבוד התוצאות
category_prices = {}
for bucket in agg_results['categories']['buckets']:
    category = bucket['key']
    avg_price = bucket['avg_price']['value']
    category_prices[category] = avg_price

most_expensive_category = max(category_prices, key=category_prices.get)
print(f"Most expensive category: {most_expensive_category}")
```

### 3. Bulk Operations
```python
# שאלת מבחן: "העלה 1000 מוצרים מקובץ CSV"
import pandas as pd

# קריאת CSV
df = pd.read_csv("products.csv")

# ניקוי נתונים
df = df.dropna()
df['price'] = pd.to_numeric(df['price'], errors='coerce')

# העלאה מסיבית
result = repo.bulk_create_from_dataframe(df, id_column='product_id')
print(f"Success: {result['success_count']}, Errors: {result['error_count']}")
```

### 4. מעקב אחר שינויים
```python
# עדכון מחירים והוספת timestamp
updates = []
for product_id in product_ids:
    updates.append({
        "_id": product_id,
        "doc": {
            "price": new_price,
            "last_updated": datetime.now(),
            "price_changed": True
        }
    })

result = repo.bulk_update(updates)
```

---

## ⚡ פונקציות מהירות למבחן

### Setup מהיר
```python
# Sync
from shared_utilities.elasticsearch import setup_elasticsearch_sync
client, repo = setup_elasticsearch_sync("http://localhost:9200", "products")

# Async
from shared_utilities.elasticsearch import setup_elasticsearch_async
client, repo = await setup_elasticsearch_async("http://localhost:9200", "products")
```

### פקודות חיוניות
```python
# יצירה מהירה
doc_id = repo.create({"name": "Test", "price": 99.99})

# חיפוש מהיר
results = repo.search(text_search="test", limit=5)

# ספירה מהירה  
count = repo.count(term_filters={"category": "electronics"})

# אגרגציה מהירה
stats = repo.aggregate({"avg_price": {"avg": {"field": "price"}}})

# DataFrame מהיר
df = repo.to_dataframe(limit=100)
```

---

## 🚨 שגיאות נפוצות ופתרונות

### 1. בעיות חיבור
```python
# Elasticsearch לא רץ
# פתרון: docker run -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.17.0
```

### 2. Index לא קיים
```python
# בדיקה אם index קיים
if not repo.index_exists():
    repo.initialize_index(mapping)
```

### 3. Mapping conflicts
```python
# מחיקה ויצירה מחדש
repo.delete_index()
repo.initialize_index(new_mapping)
```

### 4. שגיאות bulk
```python
result = repo.bulk_create(documents)
if result['error_count'] > 0:
    print(f"Had {result['error_count']} errors")
```

---

## 📝 טיפים למבחן

### מה חשוב לדעת:
1. **Query Types:** match (טקסט), term (מדויק), range (טווח), wildcard, fuzzy
2. **Mapping Types:** text (חיפוש), keyword (סינון), date, float, boolean
3. **Aggregations:** terms (קיבוץ), avg/sum/min/max (חישובים), range (טווחים)
4. **Bulk Operations:** תמיד יותר יעיל מפעולות יחידות
5. **Scroll vs Pagination:** scroll לנתונים גדולים, pagination לממשק

### דפוסי קוד שחוזרים במבחנים:
```python
# 1. יצירת index עם mapping
repo.initialize_index(mapping)

# 2. חיפוש משולב
results = repo.search(
    text_search="query",
    term_filters={"field": "value"},
    range_filters={"price": {"gte": 100}}
)

# 3. אגרגציה בסיסית
agg = repo.aggregate({"group": {"terms": {"field": "category"}}})

# 4. DataFrame integration
df = repo.to_dataframe()
repo.bulk_create_from_dataframe(df)
```

**בהצלחה במבחן! 🎯**

---

## 🔧 Troubleshooting מהיר

| בעיה | פתרון |
|------|--------|
| Connection refused | `docker run -p 9200:9200 elasticsearch:7.17.0` |
| Index not found | `repo.initialize_index(mapping)` |
| Mapping conflict | `repo.delete_index()` + create again |
| Slow queries | השתמש ב-term במקום match לסינון |
| Memory issues | השתמש ב-scroll במקום pagination גדול |

**זה הכל! Elasticsearch מוכן למבחן! 🚀**