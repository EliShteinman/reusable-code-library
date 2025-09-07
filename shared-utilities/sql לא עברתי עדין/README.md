# SQL Utils - ערכת כלים מקצועית ל-SQL

ערכת כלים מלאה עם הפרדה מושלמת בין clients ו-repository, תמיכה ב-MySQL ו-PostgreSQL.

## 📁 מבנה הקבצים - CLEAN ARCHITECTURE

```
shared-utilities/sql/
├── __init__.py                      # יבואים ופונקציות מהירות
├── mysql_sync_client.py             # MySQL connection client (CONNECTION ONLY)
├── postgresql_sync_client.py        # PostgreSQL connection client (CONNECTION ONLY)  
├── sql_repository.py                # Repository אחד (CRUD ONLY - עובד עם שני הclients)
├── examples.py                      # דוגמאות מקיפות למבחן
└── README.md                        # המדריך הזה
```

## 🚀 התקנה מהירה

```bash
# MySQL
pip install mysql-connector-python

# PostgreSQL  
pip install psycopg2-binary

# Pandas integration
pip install pandas
```

## 🎯 העקרונות החדשים - FIXED ARCHITECTURE

### ✅ **ההפרדה המושלמת:**
- **Connection Clients:** רק חיבור ופעולות RAW SQL (`execute_*`)
- **SQL Repository:** רק לוגיקה עסקית (`create`, `search`, `join`, `aggregate`)
- **Repository אחד:** עובד עם MySQL ו-PostgreSQL!
- **אין עוד runtime detection מכוער!**

### ❌ **מה תיקנו:**
- ❌ אין יותר 3 repositories שונים
- ❌ אין יותר קובץ ענק של 450+ שורות
- ❌ אין יותר בלגן של CRUD ב-client

---

## 📊 מה זה SQL? - למבחן

### **SQL vs NoSQL:**
| SQL Database | → | NoSQL Database |
|-------------|---|----------------|
| Table       | → | Collection/Document |
| Row         | → | Document/Record |
| Column      | → | Field/Property |
| Schema      | → | Schema-less |
| ACID        | → | BASE |
| JOIN        | → | Embed/Reference |
| Normalization | → | Denormalization |

### **מושגי יסוד למבחן:**
- **Primary Key** - מפתח ייחודי של הטבלה
- **Foreign Key** - מפתח המקשר בין טבלאות
- **Index** - לשיפור ביצועי חיפוש
- **Transaction** - קבוצת פעולות שמתבצעות יחד או בכלל לא
- **ACID** - Atomicity, Consistency, Isolation, Durability
- **JOIN** - חיבור בין טבלאות (INNER, LEFT, RIGHT, FULL)
- **Aggregation** - פונקציות צבירה (COUNT, SUM, AVG, MIN, MAX)
- **Normalization** - תקינון הנתונים למניעת כפילויות

---

## 🔧 שימוש בסיסי - MySQL

### 1. הקמה מהירה
```python
from shared_utilities.sql import MySQLSyncClient, SQLRepository

# יצירת client (CONNECTION ONLY) ו-repository (CRUD ONLY)
client = MySQLSyncClient("localhost", "user", "password", "test_db")
repo = SQLRepository(client, "users")

# יצירת טבלה
create_table = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INT,
    city VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
"""
client.execute_query(create_table, fetch=False)
```

### 2. CRUD בסיסי
```python
# CREATE - יצירת record
user_id = repo.create({
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "city": "Tel Aviv"
})
print(f"Created user: {user_id}")

# READ - קריאת record
user = repo.get_by_id(user_id)
print(f"User: {user['name']} - {user['email']}")

# UPDATE - עדכון record  
updated = repo.update(user_id, {
    "age": 31,
    "city": "Jerusalem"
})
print(f"Updated: {updated} rows affected")

# DELETE - מחיקת record
deleted = repo.delete(user_id)
print(f"Deleted: {deleted} rows affected")
```

### 3. חיפוש מתקדם - Query Building System
```python
# חיפוש מדויק (exact match)
tel_aviv_users = repo.search(
    filters={"city": "Tel Aviv", "age": 30},
    limit=10
)
print(f"Found {tel_aviv_users['total_count']} users")

# חיפוש טווח (range filters)
adults = repo.search(
    filters={"age": {"gte": 18, "lte": 65}},
    limit=15,
    order_by="age",
    order_dir="ASC"
)

# חיפוש ברשימה (IN filters)
cities_users = repo.search(
    filters={"city": ["Tel Aviv", "Jerusalem", "Haifa"]},
    limit=20
)

# חיפוש LIKE patterns
gmail_users = repo.search(
    filters={"email": "%@gmail.com"},
    limit=10
)

# חיפוש משולב - כל הפילטרים ביחד
filtered_results = repo.search(
    filters={
        "city": ["Tel Aviv", "Jerusalem"],  # IN filter
        "age": {"gte": 25, "lte": 40},      # Range filter
        "email": "%@company.com"            # LIKE filter
    },
    order_by="age",
    order_dir="DESC",
    limit=10,
    offset=0
)
```

### 4. Bulk Operations - עיבוד מסיבי
```python
# Bulk create - יצירה מסיבית (הכי יעיל!)
users = [
    {"name": "Alice", "age": 25, "city": "Tel Aviv", "email": "alice@example.com"},
    {"name": "Bob", "age": 30, "city": "Jerusalem", "email": "bob@example.com"},
    {"name": "Carol", "age": 35, "city": "Haifa", "email": "carol@example.com"}
]
result = repo.bulk_create(users)
print(f"Created: {result['success_count']}/{len(users)} users")

# Bulk update - עדכון מסיבי
updates = [
    {"filters": {"city": "Tel Aviv"}, "data": {"city": "Tel Aviv-Yafo"}},
    {"filters": {"age": {"lt": 25}}, "data": {"status": "young"}}
]
result = repo.bulk_update(updates)
print(f"Updated: {result['success_count']} operations")

# Bulk delete - מחיקה מסיבית
filters_to_delete = [
    {"status": "inactive"},
    {"age": {"lt": 18}}
]
result = repo.bulk_delete(filters_to_delete)
print(f"Deleted: {result['success_count']} operations")
```

---

## 🐘 שימוש עם PostgreSQL

### הגדרת PostgreSQL
```python
from shared_utilities.sql import PostgreSQLSyncClient, SQLRepository

# יצירת PostgreSQL client ו-repository
client = PostgreSQLSyncClient("localhost", "user", "password", "test_db")
repo = SQLRepository(client, "products")

# יצירת טבלה עם PostgreSQL features
create_table = """
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    tags TEXT[],  -- PostgreSQL array
    data JSONB,   -- PostgreSQL JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
client.execute_query(create_table, fetch=False)

# PostgreSQL שימוש זהה לחלוטין!
product_id = repo.create({
    "product_name": "Gaming Laptop",
    "description": "High-performance laptop",
    "price": 4999.99
})

# חיפוש זהה
products = repo.search(
    filters={"price": {"gte": 1000}},
    limit=10
)
```

---

## 🔗 JOIN Operations - חיבורים בין טבלאות

### JOIN בסיסי
```python
# INNER JOIN - רק records שיש להם התאמה
users_with_orders = users_repo.inner_join(
    "orders",
    "users.id = orders.user_id",
    limit=10
)

# LEFT JOIN - כל המשתמשים, גם אלה בלי הזמנות
all_users = users_repo.left_join(
    "orders", 
    "users.id = orders.user_id",
    limit=20
)

# JOIN עם פילטרים
tel_aviv_orders = users_repo.inner_join(
    "orders",
    "users.id = orders.user_id",
    filters={"users.city": "Tel Aviv", "orders.status": "completed"},
    limit=10
)
```

### JOIN מורכב למבחן
```python
# סטטיסטיקות משתמשים עם הזמנות
user_stats = client.execute_query("""
SELECT 
    u.name,
    u.city,
    COUNT(o.id) as order_count,
    COALESCE(SUM(o.amount), 0) as total_spent,
    COALESCE(AVG(o.amount), 0) as avg_order_value
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name, u.city
ORDER BY total_spent DESC
""")

for stat in user_stats:
    name = stat['name']
    city = stat['city']
    orders = stat['order_count']
    total = stat['total_spent']
    avg = stat['avg_order_value']
    print(f"{name} ({city}): {orders} orders, ${total:.2f} total, ${avg:.2f} avg")
```

---

## 📊 Aggregations - ניתוחים וסטטיסטיקות

### אגרגציות נפוצות למבחן
```python
# 1. GROUP BY עם COUNT (כמו בMongoDB)
dept_stats = repo.aggregate(
    "department, COUNT(*) as employee_count, AVG(salary) as avg_salary",
    group_by="department"
)

for result in dept_stats:
    dept = result['department']
    count = result['employee_count']
    avg_salary = result['avg_salary']
    print(f"{dept}: {count} employees, avg salary: {avg_salary:.2f}")

# 2. סטטיסטיקות בסיסיות (min, max, avg, sum)
stats = repo.aggregate(
    "MIN(salary) as min_salary, MAX(salary) as max_salary, AVG(salary) as avg_salary, SUM(salary) as total_salary"
)
print(f"Salary stats: min={stats[0]['min_salary']}, max={stats[0]['max_salary']}")

# 3. פונקציות נוחות
total_salary = repo.sum("salary")  # SUM
avg_age = repo.avg("age")          # AVG
salary_range = repo.min_max("salary")  # MIN & MAX
dept_counts = repo.group_by_count("department")  # GROUP BY + COUNT

# 4. HAVING clause
high_salary_depts = repo.aggregate(
    "department, AVG(salary) as avg_salary, COUNT(*) as employee_count",
    group_by="department",
    having="AVG(salary) > 15000"
)

# 5. ספירה פשוטה
total_count = repo.count()
active_count = repo.count({"active": True})
tel_aviv_count = repo.count({"city": "Tel Aviv"})
```

---

## 🐼 אינטגרציה עם Pandas

### DataFrame ↔ SQL
```python
import pandas as pd

# 1. יצירת נתונים ב-DataFrame
df = pd.DataFrame({
    'user_id': ['U001', 'U002', 'U003'],
    'name': ['Alice', 'Bob', 'Carol'],
    'age': [25, 30, 35],
    'city': ['Tel Aviv', 'Jerusalem', 'Haifa'],
    'salary': [15000, 18000, 20000]
})

# 2. העלאה מ-DataFrame ל-SQL
result = repo.bulk_create_from_dataframe(df, id_column='user_id')
print(f"Uploaded: {result['success_count']} records")

# 3. הורדה מ-SQL ל-DataFrame
search_df = repo.to_dataframe(
    filters={"city": "Tel Aviv", "salary": {"gte": 15000}},
    limit=100
)

# 4. ניתוח עם pandas
if not search_df.empty:
    avg_salary = search_df['salary'].mean()
    city_counts = search_df['city'].value_counts()
    age_groups = search_df.groupby('city')['age'].mean()
    
    print(f"Average salary: {avg_salary:.2f}")
    print("City distribution:")
    print(city_counts)
    print("Average age by city:")
    print(age_groups)

# 5. DataFrame analysis
analysis = repo.from_dataframe_analysis(search_df)
print(f"DataFrame analysis: {analysis['total_rows']} rows, {len(analysis['columns'])} columns")
```

---

## 💾 Transactions - עקביות נתונים

### Transaction בסיסי
```python
# Transaction מוצלח
try:
    with repo.transaction() as conn:
        cursor = conn.cursor()
        
        # העברת כסף בין חשבונות
        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE account_id = %s",
            (500.00, "ACC001")
        )
        
        cursor.execute(
            "UPDATE accounts SET balance = balance + %s WHERE account_id = %s", 
            (500.00, "ACC002")
        )
        
        # Transaction יתבצע אוטומטית
        print("✅ Transfer completed")
        
except Exception as e:
    print(f"❌ Transaction failed and rolled back: {e}")
```

### Transaction עם rollback
```python
try:
    with repo.transaction() as conn:
        cursor = conn.cursor()
        
        # ניסיון להעביר יותר כסף מהזמין
        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE account_id = %s AND balance >= %s",
            (10000.00, "ACC001", 10000.00)
        )
        
        if cursor.rowcount == 0:
            raise ValueError("Insufficient funds")
            
        # אם הגענו לכאן - הכסף מספיק
        cursor.execute(
            "UPDATE accounts SET balance = balance + %s WHERE account_id = %s",
            (10000.00, "ACC002")
        )
        
except Exception as e:
    print(f"✅ Transaction rolled back: {e}")
```

---

## 🎯 דפוסים נפוצים למבחן

### 1. חיפוש מורכב עם JOIN
```python
# שאלת מבחן: "מצא משתמשים מתל אביב עם הזמנות מעל 1000₪"
results = users_repo.inner_join(
    "orders",
    "users.id = orders.user_id",
    filters={
        "users.city": "Tel Aviv",
        "orders.amount": {"gte": 1000},
        "orders.status": "completed"
    },
    limit=20
)
```

### 2. ניתוח נתונים עם GROUP BY
```python
# שאלת מבחן: "חשב סך הכנסות לפי חודש ומצא החודש הטוב ביותר"
monthly_revenue = repo.aggregate(
    "YEAR(order_date) as year, MONTH(order_date) as month, SUM(amount) as total_revenue, COUNT(*) as order_count",
    group_by="YEAR(order_date), MONTH(order_date)",
    filters={"status": "completed"}
)

# מיון לפי הכנסות (Python)
sorted_months = sorted(monthly_revenue, key=lambda x: x['total_revenue'], reverse=True)
best_month = sorted_months[0]
print(f"Best month: {best_month['year']}-{best_month['month']:02d} with ${best_month['total_revenue']:,.2f}")
```

### 3. Bulk Operations עם validation
```python
# שאלת מבחן: "העלה 1000 עובדים מקובץ CSV עם validation"
import pandas as pd

# קריאת CSV
df = pd.read_csv("employees.csv")

# ניקוי נתונים
df = df.dropna()
df['salary'] = pd.to_numeric(df['salary'], errors='coerce')
df = df[df['salary'] > 0]  # ווידוא שכר חיובי

# validation נוסף
valid_cities = ['Tel Aviv', 'Jerusalem', 'Haifa', 'Beer Sheva']
df = df[df['city'].isin(valid_cities)]

# העלאה מסיבית
result = repo.bulk_create_from_dataframe(df, id_column='employee_id')
print(f"Success: {result['success_count']}, Errors: {result['error_count']}")
```

### 4. Complex JOIN עם aggregation
```python
# שאלת מבחן: "דו"ח מכירות מלא עם לקוחות ומוצרים"
sales_report = client.execute_query("""
SELECT 
    c.name as customer_name,
    c.city,
    p.product_name,
    p.category,
    SUM(oi.quantity) as total_quantity,
    SUM(oi.price * oi.quantity) as total_revenue,
    COUNT(DISTINCT o.id) as order_count
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN order_items oi ON o.id = oi.order_id  
JOIN products p ON oi.product_id = p.id
WHERE o.order_date >= %s
GROUP BY c.id, c.name, c.city, p.id, p.product_name, p.category
HAVING SUM(oi.price * oi.quantity) > %s
ORDER BY total_revenue DESC
""", (datetime.now().date() - timedelta(days=90), 1000))

for report in sales_report:
    customer = report['customer_name']
    city = report['city']
    product = report['product_name']
    revenue = report['total_revenue']
    orders = report['order_count']
    print(f"{customer} ({city}) - {product}: {orders} orders, ${revenue:,.2f}")
```

---

## ⚡ פונקציות מהירות למבחן

### Setup מהיר
```python
# MySQL
from shared_utilities.sql import setup_mysql
client, repo = setup_mysql("localhost", "user", "password", "test_db", "users")

# PostgreSQL
from shared_utilities.sql import setup_postgresql
client, repo = setup_postgresql("localhost", "user", "password", "test_db", "users")
```

### פקודות חיוניות
```python
# יצירה מהירה
user_id = repo.create({"name": "Test", "age": 25, "city": "Tel Aviv"})

# חיפוש מהיר
results = repo.search(filters={"city": "Tel Aviv"}, limit=5)

# ספירה מהירה  
count = repo.count(filters={"active": True})

# אגרגציה מהירה
stats = repo.aggregate("AVG(age) as avg_age, COUNT(*) as total")

# JOIN מהיר
joined = repo.inner_join("orders", "users.id = orders.user_id", limit=10)

# DataFrame מהיר
df = repo.to_dataframe(limit=100)

# Transaction מהיר
with repo.transaction() as conn:
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET active = TRUE WHERE city = %s", ("Tel Aviv",))
```

---

## 🚨 שגיאות נפוצות ופתרונות

### 1. בעיות חיבור
```python
# MySQL לא רץ
# פתרון: systemctl start mysql
# או: brew services start mysql

# PostgreSQL לא רץ  
# פתרון: systemctl start postgresql
# או: brew services start postgresql
```

### 2. טבלה לא קיימת
```python
# יצירת טבלה אם לא קיימת
create_table = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,  -- PostgreSQL
    -- או --
    id INT AUTO_INCREMENT PRIMARY KEY,  -- MySQL
    name VARCHAR(100) NOT NULL
)
"""
client.execute_query(create_table, fetch=False)
```

### 3. Foreign Key constraints
```python
# יצירת טבלאות בסדר הנכון
create_users = "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100))"
create_orders = """
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
"""
```

### 4. שגיאות JOIN
```python
# בדיקת נתונים לפני JOIN
users_count = users_repo.count()
orders_count = orders_repo.count()
print(f"Users: {users_count}, Orders: {orders_count}")

# JOIN עם COALESCE למניעת NULL
safe_join = client.execute_query("""
SELECT u.name, COALESCE(COUNT(o.id), 0) as order_count
FROM users u LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name
""")
```

---

## 📝 טיפים למבחן

### מה חשוב לדעת:
1. **SQL Operators:** `=`, `!=`, `>`, `>=`, `<`, `<=`, `IN`, `LIKE`, `BETWEEN`, `IS NULL`
2. **JOIN Types:** `INNER`, `LEFT`, `RIGHT`, `FULL OUTER`
3. **Aggregation Functions:** `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `GROUP BY`, `HAVING`
4. **Transactions:** `BEGIN`, `COMMIT`, `ROLLBACK`, `ACID`
5. **Indexes:** `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `INDEX`

### דפוסי קוד שחוזרים במבחנים:
```python
# 1. יצירת repository
client = MySQLSyncClient("localhost", "user", "password", "db_name")
repo = SQLRepository(client, "table_name")

# 2. חיפוש משולב
results = repo.search(
    filters={"field": "value", "age": {"gte": 18}},
    limit=10
)

# 3. אגרגציה בסיסית
stats = repo.aggregate(
    "field, COUNT(*) as count, AVG(value) as average",
    group_by="field"
)

# 4. JOIN עם פילטרים
joined = repo.inner_join(
    "other_table",
    "table.id = other_table.foreign_id",
    filters={"field": "value"}
)

# 5. DataFrame integration
df = repo.to_dataframe()
repo.bulk_create_from_dataframe(df)

# 6. Transaction
with repo.transaction() as conn:
    cursor = conn.cursor()
    cursor.execute("UPDATE ...", params)
```

**בהצלחה במבחן! 🎯**

---

## 🔧 Troubleshooting מהיר

| בעיה | פתרון |
|------|--------|
| Connection refused | `systemctl start mysql/postgresql` |
| Table doesn't exist | `CREATE TABLE IF NOT EXISTS ...` |
| Foreign key error | יצירת parent table קודם |
| JOIN returns empty | בדוק שיש נתונים בשתי הטבלאות |
| Transaction failed | בדוק ACID constraints |

**זה הכל! SQL מוכן למבחן! 🚀**