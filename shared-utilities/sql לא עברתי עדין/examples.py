# ============================================================================
# shared-utilities/sql/examples.py - דוגמאות SQL מקיפות למבחן
# ============================================================================
import pandas as pd
from datetime import datetime, timedelta
import random

# Import SQL utilities - FIXED ARCHITECTURE
from . import (
    MySQLSyncClient, PostgreSQLSyncClient, SQLRepository,
    setup_mysql, setup_postgresql
)


# ============================================================================
# דוגמה 1: MySQL Usage - שימוש עם MySQL
# ============================================================================

def example_mysql_usage():
    """Example: MySQL client (CONNECTION ONLY) + SQL repository (CRUD ONLY)"""
    print("=== MySQL SQL Example (FIXED ARCHITECTURE) ===")

    # 1. Create MySQL client (CONNECTION ONLY) + SQL repository (CRUD ONLY)
    client = MySQLSyncClient("localhost", "user", "password", "test_db")
    repo = SQLRepository(client, "employees")

    try:
        # 2. Create table for testing
        create_table_query = """
                             CREATE TABLE IF NOT EXISTS employees \
                             ( \
                                 id \
                                 INT \
                                 AUTO_INCREMENT \
                                 PRIMARY \
                                 KEY, \
                                 name \
                                 VARCHAR \
                             ( \
                                 100 \
                             ) NOT NULL,
                                 email VARCHAR \
                             ( \
                                 100 \
                             ) UNIQUE NOT NULL,
                                 department VARCHAR \
                             ( \
                                 50 \
                             ),
                                 salary DECIMAL \
                             ( \
                                 10, \
                                 2 \
                             ),
                                 age INT,
                                 hire_date DATE,
                                 active BOOLEAN DEFAULT TRUE,
                                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                                 ) \
                             """
        client.execute_query(create_table_query, fetch=False)
        print("✅ MySQL table created")

        # 3. Create single employee (Repository handles metadata)
        employee_id = repo.create({
            "name": "John Doe",
            "email": "john@company.com",
            "department": "Engineering",
            "salary": 15000.00,
            "age": 30,
            "hire_date": datetime.now().date(),
            "active": True
        })
        print(f"✅ Created employee: {employee_id}")

        # 4. Bulk create employees (Repository handles bulk logic)
        employees = [
            {
                "name": "Alice Cohen",
                "email": "alice@company.com",
                "department": "Engineering",
                "salary": 18000.00,
                "age": 28,
                "hire_date": datetime.now().date(),
                "active": True
            },
            {
                "name": "Bob Miller",
                "email": "bob@company.com",
                "department": "Marketing",
                "salary": 12000.00,
                "age": 35,
                "hire_date": datetime.now().date(),
                "active": False
            },
            {
                "name": "Carol Davis",
                "email": "carol@company.com",
                "department": "HR",
                "salary": 14000.00,
                "age": 32,
                "hire_date": datetime.now().date(),
                "active": True
            },
            {
                "name": "David Wilson",
                "email": "david@company.com",
                "department": "Engineering",
                "salary": 16000.00,
                "age": 26,
                "hire_date": datetime.now().date(),
                "active": True
            }
        ]

        bulk_result = repo.bulk_create(employees)
        print(f"✅ Bulk created: {bulk_result['success_count']}/{len(employees)} employees")

        # 5. Search with filters (Repository handles query building)
        print("\n--- Search Examples (Repository Query Building) ---")

        # Exact filters
        engineering_employees = repo.search(
            filters={"department": "Engineering", "active": True},
            limit=10
        )
        print(f"Engineering employees: {engineering_employees['total_count']} employees")

        # Range filters
        high_earners = repo.search(
            filters={"salary": {"gte": 15000}, "age": {"lte": 35}},
            limit=10,
            order_by="salary",
            order_dir="DESC"
        )
        print(f"High earners under 35: {high_earners['total_count']} employees")

        # IN filters
        tech_and_hr = repo.search(
            filters={"department": ["Engineering", "HR"]},
            limit=10
        )
        print(f"Tech and HR employees: {tech_and_hr['total_count']} employees")

        # LIKE patterns
        gmail_users = repo.search(
            filters={"email": "%@company.com"},
            limit=10
        )
        print(f"Company email users: {gmail_users['total_count']} employees")

        # 6. Get specific employee
        if employee_id:
            employee = repo.get_by_id(employee_id)
            print(f"✅ Retrieved employee: {employee['name']} - {employee['email']}")

        # 7. Update employee
        if employee_id:
            updated = repo.update(employee_id, {
                "salary": 16000.00,
                "department": "Senior Engineering"
            })
            print(f"✅ Updated employee: {updated} rows affected")

        # 8. Aggregations (Repository handles business analytics)
        print("\n--- Aggregations (Repository Analytics Logic) ---")

        # Average salary by department
        dept_stats = repo.aggregate(
            "department, AVG(salary) as avg_salary, COUNT(*) as employee_count",
            group_by="department"
        )

        print("Department salary analysis:")
        for result in dept_stats:
            dept = result['department']
            avg_salary = result['avg_salary']
            count = result['employee_count']
            print(f"  {dept}: {count} employees, avg salary: {avg_salary:.2f}₪")

        # Salary statistics
        salary_stats = repo.aggregate(
            "MIN(salary) as min_salary, MAX(salary) as max_salary, AVG(salary) as avg_salary, SUM(salary) as total_salary"
        )

        if salary_stats:
            stats = salary_stats[0]
            print(f"\nSalary statistics:")
            print(f"  Range: {stats['min_salary']:.2f}₪ - {stats['max_salary']:.2f}₪")
            print(f"  Average: {stats['avg_salary']:.2f}₪")
            print(f"  Total: {stats['total_salary']:.2f}₪")

        # Age distribution
        age_groups = repo.group_by_count("CASE WHEN age < 30 THEN 'Young' WHEN age < 40 THEN 'Mid' ELSE 'Senior' END")
        print("\nAge distribution:")
        for group in age_groups:
            print(f"  {group['department']}: {group['count']} employees")

        # 9. Count operations
        total_count = repo.count()
        active_count = repo.count({"active": True})
        engineering_count = repo.count({"department": "Engineering"})

        print(f"\n--- Counts ---")
        print(f"Total employees: {total_count}")
        print(f"Active employees: {active_count}")
        print(f"Engineering employees: {engineering_count}")

        # 10. Advanced operations
        print("\n--- Advanced Operations ---")

        # Check if record exists
        exists = repo.exists({"email": "john@company.com"})
        print(f"John exists: {exists}")

        # Get min/max salary
        salary_range = repo.min_max("salary")
        print(f"Salary range: {salary_range['min']:.2f}₪ - {salary_range['max']:.2f}₪")

        # Average age
        avg_age = repo.avg("age")
        print(f"Average age: {avg_age:.1f} years")

        # Total salary
        total_salary = repo.sum("salary")
        print(f"Total salary budget: {total_salary:.2f}₪")

        print("✅ MySQL example completed")

        return {
            'total_employees': total_count,
            'active_employees': active_count,
            'database': 'mysql'
        }

    except Exception as e:
        print(f"❌ MySQL example failed: {e}")
        return {'total_employees': 0, 'active_employees': 0, 'database': 'mysql'}

    finally:
        client.close()


# ============================================================================
# דוגמה 2: PostgreSQL Usage - שימוש עם PostgreSQL
# ============================================================================

def example_postgresql_usage():
    """Example: PostgreSQL client (CONNECTION ONLY) + SQL repository (CRUD ONLY)"""
    print("\n=== PostgreSQL SQL Example (FIXED ARCHITECTURE) ===")

    # 1. Create PostgreSQL client (CONNECTION ONLY) + SQL repository (CRUD ONLY)
    client = PostgreSQLSyncClient("localhost", "user", "password", "test_db")
    repo = SQLRepository(client, "products")

    try:
        # 2. Create table for testing
        create_table_query = """
                             CREATE TABLE IF NOT EXISTS products \
                             ( \
                                 id \
                                 SERIAL \
                                 PRIMARY \
                                 KEY, \
                                 product_name \
                                 VARCHAR \
                             ( \
                                 100 \
                             ) NOT NULL,
                                 description TEXT,
                                 category VARCHAR \
                             ( \
                                 50 \
                             ),
                                 price DECIMAL \
                             ( \
                                 10, \
                                 2 \
                             ),
                                 stock_quantity INT DEFAULT 0,
                                 supplier_id INT,
                                 is_active BOOLEAN DEFAULT TRUE,
                                 rating DECIMAL \
                             ( \
                                 3, \
                                 2 \
                             ) DEFAULT 0.0,
                                 tags TEXT[],
                                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                 ) \
                             """
        client.execute_query(create_table_query, fetch=False)
        print("✅ PostgreSQL table created")

        # 3. Create single product (Repository handles metadata)
        product_id = repo.create({
            "product_name": "Gaming Laptop Pro",
            "description": "High-performance laptop for gaming and development",
            "category": "Electronics",
            "price": 4999.99,
            "stock_quantity": 15,
            "supplier_id": 1,
            "is_active": True,
            "rating": 4.7
        })
        print(f"✅ Created product: {product_id}")

        # 4. Bulk create products (Repository handles bulk logic)
        products = [
            {
                "product_name": "Wireless Gaming Mouse",
                "description": "Ergonomic wireless mouse with RGB lighting",
                "category": "Accessories",
                "price": 199.99,
                "stock_quantity": 50,
                "supplier_id": 2,
                "is_active": True,
                "rating": 4.3
            },
            {
                "product_name": "4K Monitor Ultra",
                "description": "27-inch 4K monitor with HDR support",
                "category": "Monitors",
                "price": 1299.99,
                "stock_quantity": 8,
                "supplier_id": 1,
                "is_active": True,
                "rating": 4.8
            },
            {
                "product_name": "Mechanical Keyboard RGB",
                "description": "RGB mechanical keyboard with blue switches",
                "category": "Accessories",
                "price": 299.99,
                "stock_quantity": 0,
                "supplier_id": 3,
                "is_active": False,
                "rating": 4.5
            },
            {
                "product_name": "Noise-Cancelling Headphones",
                "description": "Premium headphones with active noise cancellation",
                "category": "Audio",
                "price": 799.99,
                "stock_quantity": 25,
                "supplier_id": 2,
                "is_active": True,
                "rating": 4.6
            }
        ]

        bulk_result = repo.bulk_create(products)
        print(f"✅ Bulk created: {bulk_result['success_count']}/{len(products)} products")

        # 5. Search operations (Repository handles query building)
        print("\n--- PostgreSQL Search Examples ---")

        # Active products with stock
        active_products = repo.search(
            filters={"is_active": True, "stock_quantity": {"gt": 0}},
            order_by="rating",
            order_dir="DESC",
            limit=10
        )
        print(f"Active products in stock: {active_products['total_count']} products")

        # High-value electronics
        electronics = repo.search(
            filters={
                "category": "Electronics",
                "price": {"gte": 1000},
                "rating": {"gte": 4.5}
            },
            order_by="price",
            order_dir="DESC",
            limit=5
        )
        print(f"High-value electronics: {electronics['total_count']} products")

        # Multiple categories
        accessories_and_audio = repo.search(
            filters={"category": ["Accessories", "Audio"]},
            limit=10
        )
        print(f"Accessories and Audio: {accessories_and_audio['total_count']} products")

        # 6. PostgreSQL-specific aggregations
        print("\n--- PostgreSQL Aggregations ---")

        # Price statistics by category
        category_stats = repo.aggregate(
            "category, AVG(price) as avg_price, MIN(price) as min_price, MAX(price) as max_price, SUM(stock_quantity) as total_stock, COUNT(*) as product_count",
            group_by="category",
            filters={"is_active": True}
        )

        print("Category analysis:")
        for result in category_stats:
            category = result['category']
            avg_price = result['avg_price']
            min_price = result['min_price']
            max_price = result['max_price']
            stock = result['total_stock']
            count = result['product_count']
            print(f"  {category}: {count} products, avg_price={avg_price:.2f}₪, stock={stock}")

        # Supplier performance
        supplier_stats = repo.aggregate(
            "supplier_id, COUNT(*) as product_count, AVG(price) as avg_price, SUM(stock_quantity * price) as total_value, AVG(rating) as avg_rating",
            group_by="supplier_id"
        )

        print("\nSupplier performance:")
        for result in supplier_stats:
            supplier = result['supplier_id']
            count = result['product_count']
            avg_price = result['avg_price']
            total_value = result['total_value']
            avg_rating = result['avg_rating']
            print(
                f"  Supplier {supplier}: {count} products, avg_price={avg_price:.0f}₪, total_value={total_value:.0f}₪, rating={avg_rating:.1f}")

        # 7. Update and bulk operations
        if product_id:
            # Update single product
            updated = repo.update(product_id, {
                "price": 4799.99,
                "stock_quantity": 12,
                "rating": 4.8
            })
            print(f"✅ Updated product: {updated} rows affected")

        # Bulk update example
        updates = [
            {"filters": {"category": "Accessories"}, "data": {"stock_quantity": 100}},
            {"filters": {"stock_quantity": 0}, "data": {"is_active": False}}
        ]
        bulk_update_result = repo.bulk_update(updates)
        print(f"✅ Bulk updated: {bulk_update_result['success_count']} operations")

        # 8. Count operations
        total_count = repo.count()
        active_count = repo.count({"is_active": True})
        in_stock_count = repo.count({"stock_quantity": {"gt": 0}})

        print(f"\n--- PostgreSQL Counts ---")
        print(f"Total products: {total_count}")
        print(f"Active products: {active_count}")
        print(f"In stock: {in_stock_count}")

        print("✅ PostgreSQL example completed")

        return {
            'total_products': total_count,
            'active_products': active_count,
            'database': 'postgresql'
        }

    except Exception as e:
        print(f"❌ PostgreSQL example failed: {e}")
        return {'total_products': 0, 'active_products': 0, 'database': 'postgresql'}


# ============================================================================
# דוגמה 3: DataFrame Integration - אינטגרציה מתקדמת עם Pandas
# ============================================================================

def example_dataframe_integration():
    """Example: Advanced DataFrame integration with SQL"""
    print("\n=== DataFrame Integration Example (Repository Data Logic) ===")

    # Quick setup using helper function
    client, repo = setup_mysql("localhost", "user", "password", "pandas_db", "sales_data")

    try:
        # Create table for sales data
        create_table_query = """
                             CREATE TABLE IF NOT EXISTS sales_data \
                             ( \
                                 id \
                                 INT \
                                 AUTO_INCREMENT \
                                 PRIMARY \
                                 KEY, \
                                 sale_id \
                                 VARCHAR \
                             ( \
                                 20 \
                             ) UNIQUE NOT NULL,
                                 product_name VARCHAR \
                             ( \
                                 100 \
                             ),
                                 category VARCHAR \
                             ( \
                                 50 \
                             ),
                                 brand VARCHAR \
                             ( \
                                 50 \
                             ),
                                 base_price DECIMAL \
                             ( \
                                 10, \
                                 2 \
                             ),
                                 discount DECIMAL \
                             ( \
                                 5, \
                                 2 \
                             ) DEFAULT 0.0,
                                 final_price DECIMAL \
                             ( \
                                 10, \
                                 2 \
                             ),
                                 quantity INT,
                                 revenue DECIMAL \
                             ( \
                                 12, \
                                 2 \
                             ),
                                 sale_date DATE,
                                 customer_type VARCHAR \
                             ( \
                                 50 \
                             ),
                                 region VARCHAR \
                             ( \
                                 50 \
                             ),
                                 sales_rep VARCHAR \
                             ( \
                                 50 \
                             ),
                                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                                 ) \
                             """
        client.execute_query(create_table_query, fetch=False)

        # Generate realistic sales data
        products = ["Laptop", "Mouse", "Keyboard", "Monitor", "Webcam", "Speakers", "Tablet", "Phone"]
        categories = ["Electronics"] * len(products)
        brands = ["TechCorp", "GameGear", "DisplayPro", "VidTech", "SoundWave", "AudioMax", "TabletCo", "PhonePro"]
        regions = ["North", "South", "East", "West", "Central"]
        customers = ["Enterprise", "SMB", "Consumer", "Education"]

        sales_data = []
        for i in range(100):  # Generate 100 sales records
            product_idx = i % len(products)
            base_price = [2000, 150, 300, 1200, 250, 400, 1500, 2500][product_idx]
            quantity = random.randint(1, 10)
            discount = random.choice([0, 0.05, 0.1, 0.15])
            final_price = base_price * (1 - discount)
            revenue = final_price * quantity

            sales_data.append({
                'sale_id': f'S{i + 1:04d}',
                'product_name': products[product_idx],
                'category': categories[product_idx],
                'brand': brands[product_idx],
                'base_price': base_price,
                'discount': discount,
                'final_price': final_price,
                'quantity': quantity,
                'revenue': revenue,
                'sale_date': (datetime.now() - timedelta(days=random.randint(0, 365))).date(),
                'customer_type': random.choice(customers),
                'region': random.choice(regions),
                'sales_rep': f"Rep_{random.randint(1, 20):02d}"
            })

        df = pd.DataFrame(sales_data)
        print(f"Created comprehensive DataFrame with {len(df)} sales records")

        # Bulk create from DataFrame (Repository handles the business logic)
        result = repo.bulk_create_from_dataframe(df, id_column='sale_id')
        print(f"✅ Bulk created from DataFrame: {result['success_count']}/{len(df)} records")

        # Advanced search and convert back to DataFrame
        print(f"\n--- Advanced DataFrame Analysis ---")

        # High-value sales
        high_value_df = repo.to_dataframe(
            filters={"revenue": {"gte": 5000}},
            limit=50
        )
        print(f"High-value sales: {len(high_value_df)} records")

        # Electronics sales analysis
        electronics_df = repo.to_dataframe(
            filters={"category": "Electronics"},
            limit=100
        )
        print(f"Electronics sales: {len(electronics_df)} records")

        # DataFrame analysis with Pandas
        if not electronics_df.empty:
            print(f"\n--- Pandas Analysis on SQL Data ---")

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

        # SQL aggregations for comparison
        print(f"\n--- SQL Aggregations vs Pandas ---")

        # Monthly sales trends using SQL
        monthly_sales = repo.aggregate(
            "YEAR(sale_date) as year, MONTH(sale_date) as month, SUM(revenue) as total_revenue, COUNT(*) as sales_count, AVG(revenue) as avg_transaction",
            group_by="YEAR(sale_date), MONTH(sale_date)",
            filters={"sale_date": {"gte": datetime.now().date() - timedelta(days=180)}}
        )

        print("Monthly sales trends (SQL aggregation):")
        for result in monthly_sales[:6]:  # Show first 6 months
            year_month = f"{result['year']}-{result['month']:02d}"
            revenue = result['total_revenue']
            count = result['sales_count']
            avg_transaction = result['avg_transaction']
            print(f"  {year_month}: {count} sales, ${revenue:,.2f} revenue, ${avg_transaction:.2f} avg")

        # Product performance analysis
        product_performance = repo.aggregate(
            "product_name, SUM(revenue) as total_revenue, SUM(quantity) as total_quantity, AVG(final_price) as avg_price, COUNT(*) as sales_count",
            group_by="product_name",
            filters={"sale_date": {"gte": datetime.now().date() - timedelta(days=90)}}
        )

        print("\nTop performing products (SQL):")
        # Sort by revenue (SQL doesn't have ORDER BY in this aggregate call)
        sorted_products = sorted(product_performance, key=lambda x: x['total_revenue'], reverse=True)
        for result in sorted_products[:5]:
            product = result['product_name']
            revenue = result['total_revenue']
            quantity = result['total_quantity']
            count = result['sales_count']
            print(f"  {product}: {count} sales, {quantity} units, ${revenue:,.2f} revenue")

        # DataFrame analysis comparison
        df_analysis = repo.from_dataframe_analysis(electronics_df)
        print(f"\nDataFrame analysis:")
        print(f"  Columns: {len(df_analysis['columns'])}")
        print(f"  Numeric columns: {len(df_analysis['summary_stats'])}")
        print(f"  Null values detected: {sum(df_analysis['null_counts'].values())}")

        return len(electronics_df)

    except Exception as e:
        print(f"❌ DataFrame integration failed: {e}")
        return 0

    finally:
        client.close()


# ============================================================================
# דוגמה 4: JOIN Operations - פעולות JOIN מתקדמות
# ============================================================================

def example_join_operations():
    """Example: Advanced JOIN operations for exam preparation"""
    print("\n=== JOIN Operations Example (Repository JOIN Logic) ===")

    # Quick setup
    client, users_repo = setup_postgresql("localhost", "user", "password", "join_db", "users")
    orders_repo = SQLRepository(client, "orders")

    try:
        # Create tables for JOIN operations
        create_users_table = """
                             CREATE TABLE IF NOT EXISTS users \
                             ( \
                                 id \
                                 SERIAL \
                                 PRIMARY \
                                 KEY, \
                                 name \
                                 VARCHAR \
                             ( \
                                 100 \
                             ) NOT NULL,
                                 email VARCHAR \
                             ( \
                                 100 \
                             ) UNIQUE NOT NULL,
                                 city VARCHAR \
                             ( \
                                 50 \
                             ),
                                 age INT,
                                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                 ) \
                             """

        create_orders_table = """
                              CREATE TABLE IF NOT EXISTS orders \
                              ( \
                                  id \
                                  SERIAL \
                                  PRIMARY \
                                  KEY, \
                                  user_id \
                                  INT \
                                  REFERENCES \
                                  users \
                              ( \
                                  id \
                              ),
                                  product_name VARCHAR \
                              ( \
                                  100 \
                              ),
                                  amount DECIMAL \
                              ( \
                                  10, \
                                  2 \
                              ),
                                  order_date DATE,
                                  status VARCHAR \
                              ( \
                                  20 \
                              ) DEFAULT 'pending',
                                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                  ) \
                              """

        client.execute_query(create_users_table, fetch=False)
        client.execute_query(create_orders_table, fetch=False)
        print("✅ Tables created for JOIN operations")

        # Create test data
        test_users = [
            {"name": "Alice Johnson", "email": "alice@example.com", "city": "Tel Aviv", "age": 25},
            {"name": "Bob Smith", "email": "bob@example.com", "city": "Jerusalem", "age": 30},
            {"name": "Carol Davis", "email": "carol@example.com", "city": "Haifa", "age": 35},
            {"name": "David Wilson", "email": "david@example.com", "city": "Tel Aviv", "age": 28}
        ]

        # Create users and store IDs
        user_ids = []
        for user_data in test_users:
            user_id = users_repo.create(user_data)
            user_ids.append(user_id)
        print(f"✅ Created {len(user_ids)} users")

        # Create orders for users
        test_orders = [
            {"user_id": user_ids[0], "product_name": "Laptop", "amount": 2000.00, "order_date": datetime.now().date(),
             "status": "completed"},
            {"user_id": user_ids[0], "product_name": "Mouse", "amount": 50.00, "order_date": datetime.now().date(),
             "status": "pending"},
            {"user_id": user_ids[1], "product_name": "Monitor", "amount": 800.00, "order_date": datetime.now().date(),
             "status": "completed"},
            {"user_id": user_ids[2], "product_name": "Keyboard", "amount": 150.00, "order_date": datetime.now().date(),
             "status": "shipped"},
            {"user_id": user_ids[3], "product_name": "Webcam", "amount": 200.00, "order_date": datetime.now().date(),
             "status": "pending"}
        ]

        orders_repo.bulk_create(test_orders)
        print(f"✅ Created {len(test_orders)} orders")

        # JOIN operations (Repository handles JOIN logic)
        print("\n--- JOIN Examples (Repository JOIN System) ---")

        # 1. INNER JOIN - users with orders
        users_with_orders = users_repo.inner_join(
            "orders",
            "users.id = orders.user_id",
            limit=10
        )
        print(f"1. INNER JOIN - Users with orders: {len(users_with_orders)} results")

        # 2. LEFT JOIN - all users, including those without orders
        all_users_orders = users_repo.left_join(
            "orders",
            "users.id = orders.user_id",
            limit=20
        )
        print(f"2. LEFT JOIN - All users with/without orders: {len(all_users_orders)} results")

        # 3. JOIN with filters
        tel_aviv_orders = users_repo.inner_join(
            "orders",
            "users.id = orders.user_id",
            filters={"users.city": "Tel Aviv", "orders.status": "completed"},
            limit=10
        )
        print(f"3. JOIN with filters - Tel Aviv completed orders: {len(tel_aviv_orders)} results")

        # 4. Complex JOIN aggregation
        user_order_stats = client.execute_query("""
                                                SELECT u.name,
                                                       u.city,
                                                       COUNT(o.id)                as order_count,
                                                       COALESCE(SUM(o.amount), 0) as total_spent,
                                                       COALESCE(AVG(o.amount), 0) as avg_order_value
                                                FROM users u
                                                         LEFT JOIN orders o ON u.id = o.user_id
                                                GROUP BY u.id, u.name, u.city
                                                ORDER BY total_spent DESC
                                                """)

        print("\n4. User order statistics (Complex JOIN + GROUP BY):")
        for stat in user_order_stats:
            name = stat['name']
            city = stat['city']
            order_count = stat['order_count']
            total_spent = stat['total_spent']
            avg_order = stat['avg_order_value']
            print(f"  {name} ({city}): {order_count} orders, ${total_spent:.2f} total, ${avg_order:.2f} avg")

        # 5. Multiple table analysis
        print("\n--- Multi-table Analysis ---")

        # Orders by city
        city_orders = client.execute_query("""
                                           SELECT u.city,
                                                  COUNT(o.id)   as order_count,
                                                  SUM(o.amount) as total_revenue,
                                                  AVG(u.age)    as avg_customer_age
                                           FROM users u
                                                    JOIN orders o ON u.id = o.user_id
                                           GROUP BY u.city
                                           ORDER BY total_revenue DESC
                                           """)

        print("Orders by city:")
        for result in city_orders:
            city = result['city']
            count = result['order_count']
            revenue = result['total_revenue']
            avg_age = result['avg_customer_age']
            print(f"  {city}: {count} orders, ${revenue:.2f} revenue, {avg_age:.1f} avg age")

        # Order status distribution
        status_dist = orders_repo.group_by_count("status")
        print("\nOrder status distribution:")
        for status in status_dist:
            print(f"  {status['status']}: {status['count']} orders")

        print("✅ JOIN operations example completed")

        return len(user_order_stats)

    except Exception as e:
        print(f"❌ JOIN operations failed: {e}")
        return 0


# ============================================================================
# דוגמה 5: Transaction Operations - פעולות טרנזקציות
# ============================================================================

def example_transaction_operations():
    """Example: Transaction handling for data consistency"""
    print("\n=== Transaction Operations Example ===")

    client, repo = setup_mysql("localhost", "user", "password", "transaction_db", "accounts")

    try:
        # Create accounts table for transaction testing
        create_table_query = """
                             CREATE TABLE IF NOT EXISTS accounts \
                             ( \
                                 id \
                                 INT \
                                 AUTO_INCREMENT \
                                 PRIMARY \
                                 KEY, \
                                 account_number \
                                 VARCHAR \
                             ( \
                                 20 \
                             ) UNIQUE NOT NULL,
                                 account_holder VARCHAR \
                             ( \
                                 100 \
                             ) NOT NULL,
                                 balance DECIMAL \
                             ( \
                                 12, \
                                 2 \
                             ) DEFAULT 0.00,
                                 account_type VARCHAR \
                             ( \
                                 20 \
                             ),
                                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                                 ) \
                             """
        client.execute_query(create_table_query, fetch=False)

        # Create test accounts
        accounts = [
            {"account_number": "ACC001", "account_holder": "Alice Johnson", "balance": 5000.00,
             "account_type": "checking"},
            {"account_number": "ACC002", "account_holder": "Bob Smith", "balance": 3000.00, "account_type": "savings"},
            {"account_number": "ACC003", "account_holder": "Carol Davis", "balance": 1000.00,
             "account_type": "checking"}
        ]

        repo.bulk_create(accounts)
        print("✅ Created test accounts for transactions")

        # 1. Successful transaction example
        print("\n--- Transaction Examples ---")

        try:
            with repo.transaction() as conn:
                cursor = conn.cursor()

                # Transfer $500 from Alice to Bob
                # Debit Alice's account
                cursor.execute(
                    "UPDATE accounts SET balance = balance - %s WHERE account_number = %s",
                    (500.00, "ACC001")
                )

                # Credit Bob's account
                cursor.execute(
                    "UPDATE accounts SET balance = balance + %s WHERE account_number = %s",
                    (500.00, "ACC002")
                )

                # Transaction will be committed automatically
                print("✅ Transfer transaction completed successfully")

        except Exception as e:
            print(f"❌ Transaction failed: {e}")

        # 2. Transaction rollback example
        try:
            with repo.transaction() as conn:
                cursor = conn.cursor()

                # Try to transfer more money than available
                cursor.execute(
                    "UPDATE accounts SET balance = balance - %s WHERE account_number = %s AND balance >= %s",
                    (10000.00, "ACC003", 10000.00)  # Carol doesn't have this much
                )

                # Check if update affected any rows
                if cursor.rowcount == 0:
                    raise ValueError("Insufficient funds")

                cursor.execute(
                    "UPDATE accounts SET balance = balance + %s WHERE account_number = %s",
                    (10000.00, "ACC001")
                )

        except Exception as e:
            print(f"✅ Transaction correctly rolled back: {e}")

        # 3. Show final account balances
        final_balances = repo.get_all()
        print("\nFinal account balances:")
        for account in final_balances:
            print(f"  {account['account_number']} ({account['account_holder']}): ${account['balance']:.2f}")

        # 4. Bulk operations with transaction safety
        print("\n--- Bulk Operations with Transactions ---")

        # Bulk update with transaction
        interest_updates = [
            {"filters": {"account_type": "savings"}, "data": {"balance": 3150.00}},  # 5% interest
            {"filters": {"account_type": "checking", "balance": {"gte": 4000}}, "data": {"balance": 4600.00}}  # Bonus
        ]

        bulk_result = repo.bulk_update(interest_updates)
        print(f"✅ Bulk interest updates: {bulk_result['success_count']} successful")

        print("✅ Transaction operations example completed")
        return len(final_balances)

    except Exception as e:
        print(f"❌ Transaction operations failed: {e}")
        return 0

    finally:
        client.close()


# ============================================================================
# Main execution function
# ============================================================================

if __name__ == "__main__":
    print("🚀 SQL Examples - COMPLETELY FIXED ARCHITECTURE")
    print("\nClean separation:")
    print("  - Clients: CONNECTION ONLY (execute_* methods)")
    print("  - Repository: CRUD ONLY (create, search, join, aggregate methods)")
    print()
    print("Choose example to run:")
    print("1. MySQL usage (Client + Repository separation)")
    print("2. PostgreSQL usage (Client + Repository separation)")
    print("3. DataFrame integration")
    print("4. JOIN operations")
    print("5. Transaction operations")
    print("6. All examples")

    choice = input("\nEnter choice (1-6): ").strip()

    try:
        if choice == "1":
            example_mysql_usage()
        elif choice == "2":
            example_postgresql_usage()
        elif choice == "3":
            example_dataframe_integration()
        elif choice == "4":
            example_join_operations()
        elif choice == "5":
            example_transaction_operations()
        elif choice == "6":
            # Run all examples
            print("Running ALL SQL examples with FIXED ARCHITECTURE...\n")

            mysql_result = example_mysql_usage()
            postgresql_result = example_postgresql_usage()
            df_result = example_dataframe_integration()
            join_result = example_join_operations()
            transaction_result = example_transaction_operations()

            print(f"\n🎉 ALL SQL EXAMPLES COMPLETED WITH CLEAN ARCHITECTURE!")
            print(f"✅ MySQL employees: {mysql_result.get('total_employees', 0)}")
            print(f"✅ PostgreSQL products: {postgresql_result.get('total_products', 0)}")
            print(f"✅ DataFrame records: {df_result}")
            print(f"✅ JOIN operations: {join_result}")
            print(f"✅ Transaction accounts: {transaction_result}")
            print(f"✅ Architecture: CLEAN SEPARATION between Clients and Repository")
        else:
            print("Invalid choice")

    except Exception as e:
        print(f"❌ Example failed: {e}")
        print("Make sure MySQL/PostgreSQL are running with proper credentials")

    print(f"\n✅ SQL examples completed!")
    print(f"🏗️  Architecture: CONNECTION clients + CRUD repository")
    print(f"🎯  Ready for SQL exam with clean patterns!")