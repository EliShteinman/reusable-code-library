# ============================================================================
# shared-utilities/mongodb/examples.py - דוגמאות מקיפות למבחן
# ============================================================================
import asyncio
import pandas as pd
from datetime import datetime, timezone

# Import all MongoDB utilities - FIXED ARCHITECTURE
from . import (
    MongoDBSyncClient, MongoDBAsyncClient,
    MongoDBSyncRepository, MongoDBAsyncRepository,
    setup_mongodb_sync, setup_mongodb_async
)


# ============================================================================
# דוגמה 1: Sync Usage - שימוש סינכרוני עם הפרדה נכונה
# ============================================================================

def example_sync_usage():
    """Example: sync client (CONNECTION ONLY) + sync repository (CRUD ONLY)"""
    print("=== Synchronous MongoDB Example (FIXED ARCHITECTURE) ===")

    # 1. Create SYNC client (CONNECTION ONLY) + SYNC repository (CRUD ONLY)
    client = MongoDBSyncClient("mongodb://localhost:27017", "test_db")
    client.connect()
    repo = MongoDBSyncRepository(client, "users")

    # 2. Create indexes for performance
    repo.create_index("email", unique=True)
    repo.create_text_index(["name", "bio"])
    print("✅ Indexes created")

    # 3. Create single user (Repository handles metadata)
    user_id = repo.create({
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "city": "Tel Aviv",
        "bio": "Software developer passionate about Python and AI",
        "skills": ["python", "mongodb", "fastapi"],
        "active": True,
        "salary": 15000
    })
    print(f"✅ Created user: {user_id}")

    # 4. Bulk create multiple users (Repository handles the logic)
    users = [
        {
            "name": "Alice Cohen",
            "email": "alice@example.com",
            "age": 28,
            "city": "Tel Aviv",
            "bio": "Data scientist with expertise in machine learning",
            "skills": ["python", "pandas", "sklearn"],
            "active": True,
            "salary": 18000
        },
        {
            "name": "Bob Miller",
            "email": "bob@example.com",
            "age": 35,
            "city": "Jerusalem",
            "bio": "Full-stack developer building web applications",
            "skills": ["javascript", "react", "node"],
            "active": False,
            "salary": 12000
        },
        {
            "name": "Carol Davis",
            "email": "carol@example.com",
            "age": 32,
            "city": "Haifa",
            "bio": "DevOps engineer managing cloud infrastructure",
            "skills": ["docker", "kubernetes", "aws"],
            "active": True,
            "salary": 20000
        },
        {
            "name": "David Wilson",
            "email": "david@example.com",
            "age": 26,
            "city": "Tel Aviv",
            "bio": "Mobile developer creating iOS and Android apps",
            "skills": ["swift", "kotlin", "react-native"],
            "active": True,
            "salary": 14000
        }
    ]

    # Repository handles bulk creation with metadata
    bulk_result = repo.bulk_create(users)
    print(f"✅ Bulk created: {bulk_result['success_count']}/{len(users)} users")

    # 5. Search with various filters (Repository handles query building)
    print("\n--- Search Examples (Repository Query Building) ---")

    # Text search (requires text index)
    text_results = repo.search(
        text_search="python developer",
        limit=5
    )
    print(f"Text search 'python developer': {text_results['total_hits']} results")

    # Field filters (exact matches)
    tel_aviv_users = repo.search(
        field_filters={"city": "Tel Aviv", "active": True},
        limit=10
    )
    print(f"Active Tel Aviv users: {tel_aviv_users['total_hits']} users")

    # Range filters
    high_earners = repo.search(
        range_filters={"salary": {"gte": 15000}, "age": {"lte": 35}},
        limit=10
    )
    print(f"High earners under 35: {high_earners['total_hits']} users")

    # Combined complex search
    python_devs = repo.search(
        text_search="python",
        field_filters={"city": "Tel Aviv", "active": True},
        range_filters={"age": {"gte": 25, "lte": 35}},
        in_filters={"skills": ["python"]},
        sort_by=[("salary", -1)],
        limit=10
    )
    print(f"Python devs in Tel Aviv (25-35, active): {python_devs['total_hits']} users")

    # Regex search
    gmail_users = repo.search(
        regex_filters={"email": ".*@gmail\\.com"},
        limit=10
    )
    print(f"Gmail users: {gmail_users['total_hits']} results")

    # Exists filters
    has_bio = repo.search(
        exists_filters=["bio", "skills"],
        limit=10
    )
    print(f"Users with bio and skills: {has_bio['total_hits']} results")

    # 6. Get specific user
    if user_id:
        user = repo.get_by_id(user_id)
        print(f"✅ Retrieved user: {user['name']} - {user['email']}")

    # 7. Update user
    if user_id:
        updated = repo.update(user_id, {
            "age": 31,
            "salary": 16000,
            "skills": ["python", "mongodb", "fastapi", "docker"],
            "last_updated": datetime.now()
        })
        print(f"✅ Updated user: {updated}")

    # 8. Aggregations (Repository handles complex aggregations)
    print("\n--- Aggregations (Repository Business Logic) ---")

    # Average salary by city
    salary_agg = repo.aggregate([
        {"$group": {
            "_id": "$city",
            "avg_salary": {"$avg": "$salary"},
            "min_salary": {"$min": "$salary"},
            "max_salary": {"$max": "$salary"},
            "user_count": {"$sum": 1}
        }},
        {"$sort": {"avg_salary": -1}}
    ])

    if salary_agg:
        print("Salary analysis by city:")
        for result in salary_agg:
            city = result['_id']
            avg_salary = result['avg_salary']
            min_salary = result['min_salary']
            max_salary = result['max_salary']
            count = result['user_count']
            print(f"  {city}: {count} users, avg={avg_salary:.0f}₪, range={min_salary}-{max_salary}₪")

    # Skills distribution
    skills_agg = repo.aggregate([
        {"$unwind": "$skills"},
        {"$group": {
            "_id": "$skills",
            "count": {"$sum": 1},
            "avg_salary": {"$avg": "$salary"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])

    if skills_agg:
        print("\nSkills popularity:")
        for result in skills_agg:
            skill = result['_id']
            count = result['count']
            avg_salary = result['avg_salary']
            print(f"  {skill}: {count} users, avg salary: {avg_salary:.0f}₪")

    # Age distribution
    age_ranges = repo.aggregate([
        {"$bucket": {
            "groupBy": "$age",
            "boundaries": [20, 25, 30, 35, 40],
            "default": "40+",
            "output": {
                "count": {"$sum": 1},
                "avg_salary": {"$avg": "$salary"},
                "cities": {"$addToSet": "$city"}
            }
        }}
    ])

    if age_ranges:
        print("\nAge distribution:")
        for bucket in age_ranges:
            age_range = bucket['_id']
            count = bucket['count']
            avg_salary = bucket['avg_salary']
            cities = bucket['cities']
            print(f"  {age_range}: {count} users, avg salary: {avg_salary:.0f}₪, cities: {cities}")

    # 9. Count operations
    total_count = repo.count()
    active_count = repo.count(field_filters={"active": True})
    tel_aviv_count = repo.count(field_filters={"city": "Tel Aviv"})
    high_earner_count = repo.count(range_filters={"salary": {"gte": 15000}})

    print(f"\n--- Counts ---")
    print(f"Total users: {total_count}")
    print(f"Active users: {active_count}")
    print(f"Tel Aviv users: {tel_aviv_count}")
    print(f"High earners (≥15K): {high_earner_count}")

    # 10. Close connection
    client.close()
    print("✅ Sync example completed")

    return {
        'total_users': total_count,
        'active_users': active_count,
        'tel_aviv_users': tel_aviv_count
    }


# ============================================================================
# דוגמה 2: Async Usage - שימוש אסינכרוני עם הפרדה נכונה
# ============================================================================

async def example_async_usage():
    """Example: async client (CONNECTION ONLY) + async repository (CRUD ONLY)"""
    print("\n=== Asynchronous MongoDB Example (FIXED ARCHITECTURE) ===")

    # 1. Create ASYNC client (CONNECTION ONLY) + ASYNC repository (CRUD ONLY)
    client = MongoDBAsyncClient("mongodb://localhost:27017", "async_test_db")
    await client.connect()  # Client handles connection
    repo = MongoDBAsyncRepository(client, "async_products")

    # 2. Create indexes (Repository handles business logic)
    await repo.create_index("product_id", unique=True)
    await repo.create_text_index(["name", "description"])
    print("✅ Async indexes created")

    # 3. Create async product (Repository handles metadata)
    product_id = await repo.create({
        "product_id": "P001",
        "name": "Gaming Laptop Pro",
        "description": "High-performance laptop for gaming and development",
        "category": "electronics",
        "brand": "TechCorp",
        "price": 4999.99,
        "stock": 15,
        "rating": 4.7,
        "tags": ["gaming", "laptop", "high-performance"],
        "active": True
    })
    print(f"✅ Created async product: {product_id}")

    # 4. Bulk create async products (Repository handles bulk logic)
    products = [
        {
            "product_id": "P002",
            "name": "Wireless Gaming Mouse",
            "description": "Ergonomic wireless mouse with RGB lighting",
            "category": "accessories",
            "brand": "GameGear",
            "price": 199.99,
            "stock": 50,
            "rating": 4.3,
            "tags": ["mouse", "wireless", "gaming"],
            "active": True
        },
        {
            "product_id": "P003",
            "name": "4K Monitor Ultra",
            "description": "27-inch 4K monitor with HDR support",
            "category": "monitors",
            "brand": "DisplayPro",
            "price": 1299.99,
            "stock": 8,
            "rating": 4.8,
            "tags": ["monitor", "4k", "hdr"],
            "active": True
        },
        {
            "product_id": "P004",
            "name": "Mechanical Keyboard RGB",
            "description": "RGB mechanical keyboard with blue switches",
            "category": "accessories",
            "brand": "KeyMaster",
            "price": 299.99,
            "stock": 0,
            "rating": 4.5,
            "tags": ["keyboard", "mechanical", "rgb"],
            "active": False
        },
        {
            "product_id": "P005",
            "name": "Noise-Cancelling Headphones",
            "description": "Premium headphones with active noise cancellation",
            "category": "audio",
            "brand": "SoundWave",
            "price": 799.99,
            "stock": 25,
            "rating": 4.6,
            "tags": ["headphones", "noise-cancelling", "premium"],
            "active": True
        }
    ]

    bulk_result = await repo.bulk_create(products)
    print(f"✅ Async bulk created: {bulk_result['success_count']}/{len(products)} products")

    # 5. Async search operations (Repository handles query building)
    print("\n--- Async Search Examples (Repository Query Building) ---")

    # Text search
    search_results = await repo.search(
        text_search="gaming laptop",
        limit=5
    )
    print(f"Async text search 'gaming laptop': {search_results['total_hits']} results")

    # Active products with stock
    active_products = await repo.search(
        field_filters={"active": True},
        range_filters={"stock": {"gt": 0}},
        sort_by=[("rating", -1)],
        limit=10
    )
    print(f"Active products in stock: {active_products['total_hits']} products")

    # High-value electronics
    electronics = await repo.search(
        field_filters={"category": "electronics", "active": True},
        range_filters={"price": {"gte": 1000}, "rating": {"gte": 4.5}},
        sort_by=[("price", -1)],
        limit=5
    )
    print(f"High-value electronics: {electronics['total_hits']} products")

    # Complex search with multiple conditions
    premium_gaming = await repo.search(
        text_search="gaming",
        field_filters={"active": True},
        range_filters={"price": {"gte": 200}, "rating": {"gte": 4.0}},
        in_filters={"tags": ["gaming"]},
        exists_filters=["rating", "stock"],
        sort_by=[("rating", -1)],
        limit=10
    )
    print(f"Premium gaming products: {premium_gaming['total_hits']} products")

    # Regex search for brands
    tech_brands = await repo.search(
        regex_filters={"brand": ".*Tech.*"},
        limit=5
    )
    print(f"Tech brands: {tech_brands['total_hits']} results")

    # 6. Async aggregations (Repository handles complex analytics)
    print("\n--- Async Aggregations (Repository Analytics Logic) ---")

    # Price statistics by category
    category_stats = await repo.aggregate([
        {"$match": {"active": True}},
        {"$group": {
            "_id": "$category",
            "avg_price": {"$avg": "$price"},
            "min_price": {"$min": "$price"},
            "max_price": {"$max": "$price"},
            "total_stock": {"$sum": "$stock"},
            "product_count": {"$sum": 1},
            "avg_rating": {"$avg": "$rating"}
        }},
        {"$sort": {"avg_price": -1}}
    ])

    if category_stats:
        print("Category analysis:")
        for result in category_stats:
            category = result['_id']
            avg_price = result['avg_price']
            min_price = result['min_price']
            max_price = result['max_price']
            stock = result['total_stock']
            count = result['product_count']
            avg_rating = result['avg_rating']
            print(f"  {category}: {count} products, avg_price={avg_price:.2f}₪, "
                  f"stock={stock}, avg_rating={avg_rating:.1f}")

    # Brand performance
    brand_performance = await repo.aggregate([
        {"$group": {
            "_id": "$brand",
            "product_count": {"$sum": 1},
            "avg_price": {"$avg": "$price"},
            "total_value": {"$sum": {"$multiply": ["$price", "$stock"]}},
            "avg_rating": {"$avg": "$rating"}
        }},
        {"$sort": {"total_value": -1}}
    ])

    if brand_performance:
        print("\nBrand performance:")
        for result in brand_performance:
            brand = result['_id']
            count = result['product_count']
            avg_price = result['avg_price']
            total_value = result['total_value']
            avg_rating = result['avg_rating']
            print(f"  {brand}: {count} products, avg_price={avg_price:.0f}₪, "
                  f"total_value={total_value:.0f}₪, rating={avg_rating:.1f}")

    # Price ranges analysis
    price_ranges = await repo.aggregate([
        {"$bucket": {
            "groupBy": "$price",
            "boundaries": [0, 200, 500, 1000, 5000],
            "default": "Expensive",
            "output": {
                "count": {"$sum": 1},
                "avg_rating": {"$avg": "$rating"},
                "categories": {"$addToSet": "$category"}
            }
        }}
    ])

    if price_ranges:
        print("\nPrice range analysis:")
        for bucket in price_ranges:
            price_range = bucket['_id']
            count = bucket['count']
            avg_rating = bucket['avg_rating']
            categories = bucket['categories']
            print(f"  {price_range}₪: {count} products, avg_rating={avg_rating:.1f}, "
                  f"categories={categories}")

    # 7. Async count operations
    total_count = await repo.count()
    active_count = await repo.count(field_filters={"active": True})
    in_stock_count = await repo.count(range_filters={"stock": {"gt": 0}})
    high_rated_count = await repo.count(range_filters={"rating": {"gte": 4.5}})

    print(f"\n--- Async Counts ---")
    print(f"Total products: {total_count}")
    print(f"Active products: {active_count}")
    print(f"In stock: {in_stock_count}")
    print(f"High rated (≥4.5): {high_rated_count}")

    # 8. Async update and bulk operations
    if product_id:
        # Update single product
        updated = await repo.update(product_id, {
            "price": 4799.99,
            "stock": 12,
            "tags": ["gaming", "laptop", "high-performance", "discounted"],
            "last_updated": datetime.now()
        })
        print(f"✅ Async updated product: {updated}")

    # Bulk update example
    updates = [
        {"filter": {"category": "accessories"}, "update": {"discount": 0.1}},
        {"filter": {"stock": 0}, "update": {"active": False}}
    ]
    bulk_update_result = await repo.bulk_update(updates)
    print(f"✅ Bulk updated: {bulk_update_result['success_count']} products")

    # 9. Close async connection (Client handles cleanup)
    await client.close()
    print("✅ Async example completed")

    return {
        'total_products': total_count,
        'active_products': active_count,
        'async_operations': True
    }


# ============================================================================
# דוגמה 3: DataFrame Integration - אינטגרציה מתקדמת עם Pandas
# ============================================================================

def example_dataframe_integration():
    """Example: Advanced DataFrame integration patterns"""
    print("\n=== DataFrame Integration Example (Repository Data Logic) ===")

    # Quick setup using helper function
    client, repo = setup_mongodb_sync("mongodb://localhost:27017", "pandas_db", "sales_data")

    # Create comprehensive sample DataFrame
    import numpy as np
    np.random.seed(42)  # For reproducible results

    # Generate realistic sales data
    products = ["Laptop", "Mouse", "Keyboard", "Monitor", "Webcam", "Speakers", "Tablet", "Phone"]
    categories = ["electronics"] * len(products)
    brands = ["TechCorp", "GameGear", "DisplayPro", "VidTech", "SoundWave", "AudioMax", "TabletCo", "PhonePro"]
    regions = ["North", "South", "East", "West", "Central"]
    customers = ["Enterprise", "SMB", "Consumer", "Education"]

    sales_data = []
    for i in range(100):  # Generate 100 sales records
        product_idx = i % len(products)
        base_price = [2000, 150, 300, 1200, 250, 400, 1500, 2500][product_idx]
        quantity = np.random.randint(1, 10)
        discount = np.random.choice([0, 0.05, 0.1, 0.15], p=[0.5, 0.2, 0.2, 0.1])
        final_price = base_price * (1 - discount)
        revenue = final_price * quantity

        sales_data.append({
            'sale_id': f'S{i+1:04d}',
            'product_name': products[product_idx],
            'category': categories[product_idx],
            'brand': brands[product_idx],
            'base_price': base_price,
            'discount': discount,
            'final_price': final_price,
            'quantity': quantity,
            'revenue': revenue,
            'sale_date': pd.Timestamp('2024-01-01') + pd.Timedelta(days=np.random.randint(0, 365)),
            'customer_type': np.random.choice(customers),
            'region': np.random.choice(regions),
            'sales_rep': f"Rep_{np.random.randint(1, 20):02d}"
        })

    df = pd.DataFrame(sales_data)
    print(f"Created comprehensive DataFrame with {len(df)} sales records")
    print("\nDataFrame sample:")
    print(df.head(3))
    print(f"\nDataFrame info:")
    print(f"Columns: {list(df.columns)}")
    print(f"Total revenue: ${df['revenue'].sum():,.2f}")

    # Bulk create from DataFrame (Repository handles the business logic)
    result = repo.bulk_create_from_dataframe(df, id_column='sale_id')
    print(f"✅ Bulk created from DataFrame: {result['success_count']}/{len(df)} records")

    # Advanced search and convert back to DataFrame
    print(f"\n--- Advanced DataFrame Analysis ---")

    # High-value sales
    high_value_df = repo.to_dataframe(
        range_filters={"revenue": {"gte": 5000}},
        sort_by=[("revenue", -1)],
        limit=50
    )
    print(f"High-value sales: {len(high_value_df)} records")

    # Electronics sales analysis
    electronics_df = repo.to_dataframe(
        field_filters={"category": "electronics"},
        limit=100
    )
    print(f"Electronics sales: {len(electronics_df)} records")

    # Regional performance analysis
    if not electronics_df.empty:
        print(f"\n--- Pandas Analysis on MongoDB Data ---")

        # Revenue by region
        if 'region' in electronics_df.columns and 'revenue' in electronics_df.columns:
            regional_revenue = electronics_df.groupby('region')['revenue'].agg(['sum', 'mean', 'count'])
            print("\nRegional performance:")
            print(regional_revenue)

        # Top performing sales reps
        if 'sales_rep' in electronics_df.columns:
            rep_performance = electronics_df.groupby('sales_rep').agg({
                'revenue': ['sum', 'mean'],
                'quantity': 'sum'
            }).round(2)
            print("\nSales rep performance (top 5):")
            print(rep_performance.head())

        # Customer type analysis
        if 'customer_type' in electronics_df.columns:
            customer_analysis = electronics_df.groupby('customer_type').agg({
                'revenue': ['sum', 'mean', 'count'],
                'discount': 'mean'
            }).round(2)
            print("\nCustomer type analysis:")
            print(customer_analysis)

    # MongoDB aggregations for comparison
    print(f"\n--- MongoDB Aggregations vs Pandas ---")

    # Monthly sales trends using MongoDB
    monthly_sales = repo.aggregate([
        {"$group": {
            "_id": {
                "year": {"$year": "$sale_date"},
                "month": {"$month": "$sale_date"}
            },
            "total_revenue": {"$sum": "$revenue"},
            "total_quantity": {"$sum": "$quantity"},
            "avg_transaction": {"$avg": "$revenue"},
            "sales_count": {"$sum": 1}
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ])

    if monthly_sales:
        print("Monthly sales trends (MongoDB aggregation):")
        for result in monthly_sales[:6]:  # Show first 6 months
            year_month = f"{result['_id']['year']}-{result['_id']['month']:02d}"
            revenue = result['total_revenue']
            count = result['sales_count']
            avg_transaction = result['avg_transaction']
            print(f"  {year_month}: {count} sales, ${revenue:,.2f} revenue, ${avg_transaction:.2f} avg")

    # Product performance analysis
    product_performance = repo.aggregate([
        {"$group": {
            "_id": "$product_name",
            "total_revenue": {"$sum": "$revenue"},
            "total_quantity": {"$sum": "$quantity"},
            "avg_price": {"$avg": "$final_price"},
            "sales_count": {"$sum": 1}
        }},
        {"$sort": {"total_revenue": -1}},
        {"$limit": 5}
    ])

    if product_performance:
        print("\nTop performing products (MongoDB):")
        for result in product_performance:
            product = result['_id']
            revenue = result['total_revenue']
            quantity = result['total_quantity']
            count = result['sales_count']
            print(f"  {product}: {count} sales, {quantity} units, ${revenue:,.2f} revenue")

    client.close()
    return len(electronics_df)


# ============================================================================
# דוגמה 4: Advanced Query Patterns - דפוסי חיפוש מתקדמים למבחן
# ============================================================================

def example_advanced_queries():
    """Example: Advanced search patterns for exam preparation"""
    print("\n=== Advanced Query Patterns for Exam (Repository Query Building) ===")

    # Quick setup
    client, repo = setup_mongodb_sync("mongodb://localhost:27017", "exam_db", "students")

    # Create comprehensive test data for advanced queries
    test_data = [
        {
            "student_id": "S001",
            "name": "Alice Johnson",
            "email": "alice@university.edu",
            "age": 20,
            "major": "Computer Science",
            "year": 2,
            "gpa": 3.8,
            "courses": ["Data Structures", "Algorithms", "Database Systems"],
            "skills": ["python", "java", "sql"],
            "city": "Tel Aviv",
            "scholarship": True,
            "graduation_year": 2026
        },
        {
            "student_id": "S002",
            "name": "Bob Smith",
            "email": "bob@university.edu",
            "age": 22,
            "major": "Mathematics",
            "year": 4,
            "gpa": 3.9,
            "courses": ["Calculus", "Linear Algebra", "Statistics"],
            "skills": ["python", "r", "matlab"],
            "city": "Jerusalem",
            "scholarship": False,
            "graduation_year": 2024
        },
        {
            "student_id": "S003",
            "name": "Carol Davis",
            "email": "carol@university.edu",
            "age": 19,
            "major": "Computer Science",
            "year": 1,
            "gpa": 3.7,
            "courses": ["Programming Basics", "Math for CS"],
            "skills": ["python", "javascript"],
            "city": "Haifa",
            "scholarship": True,
            "graduation_year": 2027
        },
        {
            "student_id": "S004",
            "name": "David Wilson",
            "email": "david@university.edu",
            "age": 21,
            "major": "Physics",
            "year": 3,
            "gpa": 3.6,
            "courses": ["Quantum Mechanics", "Thermodynamics"],
            "skills": ["python", "matlab", "mathematica"],
            "city": "Tel Aviv",
            "scholarship": False,
            "graduation_year": 2025
        },
        {
            "student_id": "S005",
            "name": "Eve Brown",
            "email": "eve@university.edu",
            "age": 23,
            "major": "Computer Science",
            "year": 4,
            "gpa": 4.0,
            "courses": ["Machine Learning", "AI", "Data Mining"],
            "skills": ["python", "tensorflow", "pytorch"],
            "city": "Tel Aviv",
            "scholarship": True,
            "graduation_year": 2024
        }
    ]

    # Bulk create test data
    bulk_result = repo.bulk_create(test_data)
    print(f"✅ Created {bulk_result['success_count']} test records for advanced queries")

    print("\n--- Advanced Query Examples (Repository Query Building System) ---")

    # 1. Complex boolean query with multiple conditions
    complex_results = repo.search(
        field_filters={"major": "Computer Science", "scholarship": True},
        range_filters={"gpa": {"gte": 3.7}, "year": {"gte": 2}},
        exists_filters=["courses", "skills"],
        sort_by=[("gpa", -1)],
        limit=10
    )
    print(f"1. Complex query (CS majors with scholarship, GPA≥3.7, year≥2): {complex_results['total_hits']} results")

    # 2. Text search with field filters
    text_results = repo.search(
        text_search="alice computer",  # Requires text index
        field_filters={"city": "Tel Aviv"},
        limit=5
    )
    print(f"2. Text search for 'alice computer' in Tel Aviv: {text_results['total_hits']} results")

    # 3. In filters for multiple values
    multi_skill_results = repo.search(
        in_filters={"skills": ["python", "java"], "major": ["Computer Science", "Mathematics"]},
        limit=10
    )
    print(f"3. Students with python/java skills in CS/Math: {multi_skill_results['total_hits']} results")

    # 4. Range queries with multiple fields
    senior_students = repo.search(
        range_filters={
            "age": {"gte": 21, "lte": 25},
            "year": {"gte": 3},
            "gpa": {"gte": 3.5}
        },
        limit=10
    )
    print(f"4. Senior students (age 21-25, year≥3, GPA≥3.5): {senior_students['total_hits']} results")

    # 5. Regex patterns for email domains
    university_emails = repo.search(
        regex_filters={"email": ".*@university\\.edu"},
        limit=10
    )
    print(f"5. University email addresses: {university_emails['total_hits']} results")

    # 6. Combined filters with sorting
    top_students = repo.search(
        field_filters={"scholarship": True},
        range_filters={"gpa": {"gte": 3.8}},
        in_filters={"city": ["Tel Aviv", "Jerusalem"]},
        sort_by=[("gpa", -1), ("age", 1)],
        limit=5
    )
    print(f"6. Top scholarship students in major cities: {top_students['total_hits']} results")

    # 7. Advanced aggregations for academic analytics
    print("\n--- Advanced Aggregation Examples (Repository Analytics Logic) ---")

    # GPA statistics by major
    major_stats = repo.aggregate([
        {"$group": {
            "_id": "$major",
            "avg_gpa": {"$avg": "$gpa"},
            "min_gpa": {"$min": "$gpa"},
            "max_gpa": {"$max": "$gpa"},
            "student_count": {"$sum": 1},
            "scholarship_count": {"$sum": {"$cond": ["$scholarship", 1, 0]}}
        }},
        {"$sort": {"avg_gpa": -1}}
    ])

    if major_stats:
        print("Academic performance by major:")
        for result in major_stats:
            major = result['_id']
            avg_gpa = result['avg_gpa']
            min_gpa = result['min_gpa']
            max_gpa = result['max_gpa']
            count = result['student_count']
            scholarships = result['scholarship_count']
            print(f"  {major}: {count} students, avg_gpa={avg_gpa:.2f}, "
                  f"range={min_gpa}-{max_gpa}, scholarships={scholarships}")

    # Skills analysis
    skills_analysis = repo.aggregate([
        {"$unwind": "$skills"},
        {"$group": {
            "_id": "$skills",
            "student_count": {"$sum": 1},
            "avg_gpa": {"$avg": "$gpa"},
            "majors": {"$addToSet": "$major"}
        }},
        {"$sort": {"student_count": -1}}
    ])

    if skills_analysis:
        print("\nSkills analysis:")
        for result in skills_analysis:
            skill = result['_id']
            count = result['student_count']
            avg_gpa = result['avg_gpa']
            majors = result['majors']
            print(f"  {skill}: {count} students, avg_gpa={avg_gpa:.2f}, majors={majors}")

    # City and year distribution
    city_year_analysis = repo.aggregate([
        {"$group": {
            "_id": {"city": "$city", "year": "$year"},
            "count": {"$sum": 1},
            "avg_gpa": {"$avg": "$gpa"}
        }},
        {"$sort": {"_id.city": 1, "_id.year": 1}}
    ])

    if city_year_analysis:
        print("\nCity and year distribution:")
        for result in city_year_analysis:
            city = result['_id']['city']
            year = result['_id']['year']
            count = result['count']
            avg_gpa = result['avg_gpa']
            print(f"  {city} Year {year}: {count} students, avg_gpa={avg_gpa:.2f}")

    # 8. Count operations with different filters
    total_students = repo.count()
    cs_students = repo.count(field_filters={"major": "Computer Science"})
    scholarship_students = repo.count(field_filters={"scholarship": True})
    high_gpa_students = repo.count(range_filters={"gpa": {"gte": 3.8}})
    tel_aviv_students = repo.count(field_filters={"city": "Tel Aviv"})

    print(f"\n--- Student Counts by Category ---")
    print(f"Total students: {total_students}")
    print(f"CS students: {cs_students}")
    print(f"Scholarship recipients: {scholarship_students}")
    print(f"High GPA (≥3.8): {high_gpa_students}")
    print(f"Tel Aviv students: {tel_aviv_students}")

    client.close()
    print("✅ Advanced queries example completed")

    return total_students


# ============================================================================
# Main execution function
# ============================================================================

if __name__ == "__main__":
    print("🚀 MongoDB Examples - COMPLETELY FIXED ARCHITECTURE")
    print("\nClean separation:")
    print("  - Clients: CONNECTION ONLY (execute_* methods)")
    print("  - Repositories: CRUD ONLY (create, search, aggregate methods)")
    print()
    print("Choose example to run:")
    print("1. Sync usage (Client + Repository separation)")
    print("2. Async usage (Client + Repository separation)")
    print("3. DataFrame integration")
    print("4. Advanced queries")
    print("5. All examples")

    choice = input("\nEnter choice (1-5): ").strip()

    try:
        if choice == "1":
            example_sync_usage()
        elif choice == "2":
            asyncio.run(example_async_usage())
        elif choice == "3":
            example_dataframe_integration()
        elif choice == "4":
            example_advanced_queries()
        elif choice == "5":
            # Run all examples
            print("Running ALL examples with FIXED ARCHITECTURE...\n")

            sync_result = example_sync_usage()
            async_result = asyncio.run(example_async_usage())
            df_result = example_dataframe_integration()
            query_result = example_advanced_queries()

            print(f"\n🎉 ALL EXAMPLES COMPLETED WITH CLEAN ARCHITECTURE!")
            print(f"✅ Sync users: {sync_result['total_users']}")
            print(f"✅ Async products: {async_result['total_products']}")
            print(f"✅ DataFrame records: {df_result}")
            print(f"✅ Advanced query students: {query_result}")
            print(f"✅ Architecture: CLEAN SEPARATION between Clients and Repositories")
        else:
            print("Invalid choice")

    except Exception as e:
        print(f"❌ Example failed: {e}")
        print("Make sure MongoDB is running on localhost:27017")

    print(f"\n✅ MongoDB examples completed!")
    print(f"🏗️  Architecture: CONNECTION clients + CRUD repositories")
    print(f"🎯  Ready for exam with clean patterns!")