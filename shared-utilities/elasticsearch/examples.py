# Brand distribution
brand_agg = repo.aggregate({
    "top_brands": {
        "terms": {"field": "brand", "size": 5},
        "aggs": {
            "avg_rating": {"avg": {"field": "rating"}},
            "total_products": {"value_count": {"field": "name"}}
        }
    }
})

if 'top_brands' in brand_agg:
    print("\nTop brands:")
    for bucket in brand_agg['top_brands']['buckets']:
        brand = bucket['key']
        count = bucket['doc_count']
        avg_rating = bucket['avg_rating']['value']
        print(f"  {brand}: {count} products, avg rating: {avg_rating:.2f}")

# Price range distribution
price_ranges = repo.aggregate({
    "price_ranges": {
        "range": {
            "field": "price",
            "ranges": [
                {"to": 50, "key": "under_50"},
                {"from": 50, "to": 100, "key": "50_to_100"},
                {"from": 100, "to": 300, "key": "100_to_300"},
                {"from": 300, "key": "over_300"}
            ]
        }
    }
})

if 'price_ranges' in price_ranges:
    print("\nPrice distribution:")
    for bucket in price_ranges['price_ranges']['buckets']:
        range_key = bucket['key']
        count = bucket['doc_count']
        print(f"  {range_key}: {count} products")

# 9. Scroll search for large datasets (Repository handles pagination)
print(f"\n--- Scroll Search (Repository Handles Large Data) ---")
all_products = []
for product in repo.scroll_search(scroll_size=3):  # Small batch for demo
    all_products.append(product)
    if len(all_products) >= 6:  # Limit for demo
        break
print(f"Scrolled through {len(all_products)} products")

# 10. DataFrame integration (Repository handles conversion)
df = repo.to_dataframe(
    term_filters={"category": "electronics"},
    limit=10
)
print(f"\n--- DataFrame Integration (Repository Logic) ---")
print(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
if not df.empty:
    print("Columns:", list(df.columns))
    if 'price' in df.columns:
        print(f"Price range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")
        print(f"Average price: ${df['price'].mean():.2f}")

# 11. Count documents
total_count = repo.count()
electronics_count = repo.count(term_filters={"category": "electronics"})
in_stock_count = repo.count(term_filters={"in_stock": True})
print(f"\nDocument counts:")
print(f"Total products: {total_count}")
print(f"Electronics: {electronics_count}")
print(f"In stock: {in_stock_count}")

# 12. Bulk operations
print(f"\n--- Bulk Operations ---")

# Bulk update
updates = [
    {"_id": product_id, "doc": {"price": 1099.99, "tags": ["gaming", "laptop", "sale"]}},
]
update_result = repo.bulk_update(updates)
print(f"Bulk updated: {update_result['success_count']} products")

# 13. Close connection (Client handles connection cleanup)
client.close()
print("✅ Sync example completed")

return {
    'total_products': total_count,
    'electronics_count': electronics_count,
    'dataframe_rows': len(df)
}


# ============================================================================
# דוגמה 2: Async Usage - שימוש אסינכרוני עם הפרדה נכונה
# ============================================================================

async def example_async_usage():
    """Example: async client (CONNECTION ONLY) + async repository (CRUD ONLY)"""
    print("\n=== Asynchronous Elasticsearch Example (FIXED ARCHITECTURE) ===")

    # 1. Create ASYNC client (CONNECTION ONLY) + ASYNC repository (CRUD ONLY)
    client = ElasticsearchAsyncClient("http://localhost:9200")
    await client.connect()  # Client handles connection
    repo = ElasticsearchAsyncRepository(client, "async_articles")

    # 2. Initialize index (Repository handles business logic)
    mapping = {
        "properties": {
            "title": {"type": "text", "analyzer": "standard"},
            "content": {"type": "text"},
            "author": {"type": "keyword"},
            "publish_date": {"type": "date"},
            "views": {"type": "integer"},
            "likes": {"type": "integer"},
            "tags": {"type": "keyword"},
            "category": {"type": "keyword"},
            "featured": {"type": "boolean"},
            "reading_time": {"type": "integer"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"}
        }
    }

    await repo.initialize_index(mapping)
    print("✅ Async index initialized")

    # 3. Create async documents (Repository handles metadata)
    article_id = await repo.create({
        "title": "Introduction to Elasticsearch",
        "content": "Elasticsearch is a powerful search and analytics engine built on Apache Lucene...",
        "author": "tech_writer",
        "publish_date": datetime.now(timezone.utc),
        "views": 1250,
        "likes": 89,
        "tags": ["elasticsearch", "search", "tutorial", "beginner"],
        "category": "technology",
        "featured": True,
        "reading_time": 8
    })
    print(f"✅ Created async article: {article_id}")

    # 4. Bulk create async (Repository handles bulk logic)
    articles = [
        {
            "title": "Advanced Search Queries",
            "content": "Learn advanced search techniques and query DSL for complex searches...",
            "author": "search_expert",
            "publish_date": datetime.now(timezone.utc),
            "views": 890,
            "likes": 67,
            "tags": ["elasticsearch", "query", "advanced", "dsl"],
            "category": "technology",
            "featured": False,
            "reading_time": 12
        },
        {
            "title": "Scaling Elasticsearch Clusters",
            "content": "Best practices for scaling elasticsearch clusters in production environments...",
            "author": "devops_guru",
            "publish_date": datetime.now(timezone.utc),
            "views": 2100,
            "likes": 156,
            "tags": ["elasticsearch", "scaling", "devops", "production"],
            "category": "devops",
            "featured": True,
            "reading_time": 15
        },
        {
            "title": "Data Visualization with Kibana",
            "content": "Create stunning visualizations and dashboards with Kibana...",
            "author": "data_analyst",
            "publish_date": datetime.now(timezone.utc),
            "views": 675,
            "likes": 42,
            "tags": ["kibana", "visualization", "dashboard", "analytics"],
            "category": "analytics",
            "featured": False,
            "reading_time": 10
        },
        {
            "title": "Machine Learning with Elasticsearch",
            "content": "Explore machine learning capabilities in Elasticsearch for anomaly detection...",
            "author": "ml_engineer",
            "publish_date": datetime.now(timezone.utc),
            "views": 1500,
            "likes": 120,
            "tags": ["elasticsearch", "machine-learning", "anomaly-detection", "ml"],
            "category": "ai",
            "featured": True,
            "reading_time": 18
        }
    ]

    bulk_result = await repo.bulk_create(articles)
    print(f"✅ Async bulk created: {bulk_result['success_count']}/{len(articles)} articles")

    # 5. Async search operations (Repository handles query building)
    print("\n--- Async Search Examples (Repository Query Building) ---")

    # Text search
    search_results = await repo.search(
        text_search="elasticsearch",
        limit=5
    )
    print(f"Async text search: {search_results['total_hits']} results")

    # Featured articles with high views
    featured_articles = await repo.search(
        term_filters={"featured": True},
        range_filters={"views": {"gte": 1000}},
        sort_by=[{"views": {"order": "desc"}}],
        limit=10
    )
    print(f"Featured high-traffic articles: {featured_articles['total_hits']} results")

    # Popular articles by category
    tech_articles = await repo.search(
        term_filters={"category": "technology"},
        range_filters={"likes": {"gte": 50}},
        sort_by=[{"likes": {"order": "desc"}}],
        limit=5
    )
    print(f"Popular tech articles: {tech_articles['total_hits']} results")

    # Complex search with multiple conditions
    long_featured_articles = await repo.search(
        term_filters={"featured": True},
        range_filters={"reading_time": {"gte": 10}, "views": {"gte": 500}},
        exists_filters=["tags"],
        sort_by=[{"views": {"order": "desc"}}],
        limit=10
    )
    print(f"Long featured articles (>10min, >500 views): {long_featured_articles['total_hits']} results")

    # Wildcard search for titles
    tutorial_articles = await repo.search(
        wildcard_filters={"title": "*tutorial*"},
        limit=5
    )
    print(f"Tutorial articles: {tutorial_articles['total_hits']} results")

    # 6. Async aggregations (Repository handles complex analytics)
    print("\n--- Async Aggregations (Repository Analytics) ---")

    # Views and likes statistics by author
    author_stats = await repo.aggregate({
        "authors": {
            "terms": {"field": "author", "size": 10},
            "aggs": {
                "total_views": {"sum": {"field": "views"}},
                "avg_views": {"avg": {"field": "views"}},
                "total_likes": {"sum": {"field": "likes"}},
                "avg_likes": {"avg": {"field": "likes"}},
                "article_count": {"value_count": {"field": "title"}},
                "avg_reading_time": {"avg": {"field": "reading_time"}}
            }
        }
    })

    if 'authors' in author_stats:
        print("Author performance statistics:")
        for bucket in author_stats['authors']['buckets']:
            author = bucket['key']
            total_views = bucket['total_views']['value']
            avg_views = bucket['avg_views']['value']
            total_likes = bucket['total_likes']['value']
            avg_likes = bucket['avg_likes']['value']
            count = bucket['doc_count']
            avg_reading_time = bucket['avg_reading_time']['value']
            print(
                f"  {author}: {count} articles, {total_views} total views ({avg_views:.0f} avg), {total_likes} total likes ({avg_likes:.0f} avg), {avg_reading_time:.1f}min avg reading")

    # Category analysis
    category_analysis = await repo.aggregate({
        "categories": {
            "terms": {"field": "category", "size": 10},
            "aggs": {
                "avg_views": {"avg": {"field": "views"}},
                "avg_engagement": {
                    "bucket_script": {
                        "buckets_path": {
                            "views": "avg_views",
                            "likes": "avg_likes"
                        },
                        "script": "params.likes / params.views * 100"
                    }
                },
                "avg_likes": {"avg": {"field": "likes"}},
                "featured_count": {
                    "filter": {"term": {"featured": True}}
                }
            }
        }
    })

    if 'categories' in category_analysis:
        print("\nCategory performance:")
        for bucket in category_analysis['categories']['buckets']:
            category = bucket['key']
            count = bucket['doc_count']
            avg_views = bucket['avg_views']['value']
            avg_likes = bucket['avg_likes']['value']
            featured_count = bucket['featured_count']['doc_count']
            print(
                f"  {category}: {count} articles, {avg_views:.0f} avg views, {avg_likes:.0f} avg likes, {featured_count} featured")

    # Tag popularity
    tag_popularity = await repo.aggregate({
        "popular_tags": {
            "terms": {"field": "tags", "size": 10},
            "aggs": {
                "avg_views": {"avg": {"field": "views"}},
                "avg_likes": {"avg": {"field": "likes"}}
            }
        }
    })

    if 'popular_tags' in tag_popularity:
        print("\nPopular tags:")
        for bucket in tag_popularity['popular_tags']['buckets']:
            tag = bucket['key']
            count = bucket['doc_count']
            avg_views = bucket['avg_views']['value']
            avg_likes = bucket['avg_likes']['value']
            print(f"  #{tag}: {count} articles, {avg_views:.0f} avg views, {avg_likes:.0f} avg likes")

    # 7. Async scroll search (Repository handles large data processing)
    print(f"\n--- Async Scroll Search (Repository Large Data) ---")
    all_articles = []
    async for article in repo.scroll_search(scroll_size=2):
        all_articles.append(article)
        if len(all_articles) >= 4:  # Limit for demo
            break
    print(f"Async scrolled through {len(all_articles)} articles")

    # 8. Async DataFrame conversion (Repository handles data transformation)
    df = await repo.to_dataframe(
        range_filters={"views": {"gte": 500}},
        limit=10
    )
    print(f"\n--- Async DataFrame Integration ---")
    print(f"Created async DataFrame with {len(df)} rows")
    if not df.empty:
        print("Columns:", list(df.columns))
        if 'views' in df.columns and 'likes' in df.columns:
            print(f"Views range: {df['views'].min()} - {df['views'].max()}")
            print(f"Average engagement: {(df['likes'] / df['views'] * 100).mean():.2f}%")

    # 9. Async update and delete operations
    if article_id:
        # Update
        updated = await repo.update(article_id, {
            "views": 1500,
            "likes": 105,
            "featured": True,
            "tags": ["elasticsearch", "search", "tutorial", "beginner", "updated"]
        })
        print(f"✅ Async updated article: {updated}")

    # 10. Async count operations
    total_count = await repo.count()
    featured_count = await repo.count(term_filters={"featured": True})
    high_traffic_count = await repo.count(range_filters={"views": {"gte": 1000}})
    print(f"\nAsync counts:")
    print(f"Total articles: {total_count}")
    print(f"Featured articles: {featured_count}")
    print(f"High traffic (>1000 views): {high_traffic_count}")

    # 11. Close async connection (Client handles cleanup)
    await client.close()
    print("✅ Async example completed")

    return {
        'total_articles': total_count,
        'featured_count': featured_count,
        'async_dataframe_rows': len(df)
    }


# ============================================================================
# דוגמה 3: DataFrame Integration - אינטגרציה מתקדמת עם Pandas
# ============================================================================

def example_dataframe_integration():
    """Example: Advanced DataFrame integration patterns"""
    print("\n=== DataFrame Integration Example (Repository Data Logic) ===")

    # Quick setup using helper function
    client, repo = setup_elasticsearch_sync("http://localhost:9200", "sales_data")

    # Initialize index for sales data analysis
    mapping = {
        "properties": {
            "product_id": {"type": "keyword"},
            "product_name": {"type": "text"},
            "category": {"type": "keyword"},
            "subcategory": {"type": "keyword"},
            "brand": {"type": "keyword"},
            "price": {"type": "float"},
            "cost": {"type": "float"},
            "quantity": {"type": "integer"},
            "revenue": {"type": "float"},
            "profit": {"type": "float"},
            "sale_date": {"type": "date"},
            "customer_id": {"type": "keyword"},
            "customer_segment": {"type": "keyword"},
            "region": {"type": "keyword"},
            "sales_rep": {"type": "keyword"},
            "discount_applied": {"type": "boolean"},
            "discount_amount": {"type": "float"}
        }
    }
    repo.initialize_index(mapping)

    # Create comprehensive sample DataFrame
    import numpy as np
    np.random.seed(42)  # For reproducible results

    # Generate realistic sales data
    products = ["Gaming Mouse", "Mechanical Keyboard", "4K Monitor", "Webcam", "Speakers", "Headphones", "Tablet",
                "Smartphone"]
    categories = ["electronics", "electronics", "electronics", "electronics", "electronics", "electronics",
                  "electronics", "electronics"]
    subcategories = ["gaming", "gaming", "display", "video", "audio", "audio", "mobile", "mobile"]
    brands = ["TechCorp", "GameGear", "DisplayPro", "VidTech", "SoundWave", "AudioMax", "TabletCo", "PhonePro"]
    regions = ["North", "South", "East", "West", "Central"]
    customer_segments = ["Enterprise", "SMB", "Consumer", "Education"]
    sales_reps = ["Alice Johnson", "Bob Smith", "Carol White", "David Brown", "Eva Green"]

    sales_data = []
    for i in range(50):  # Generate 50 sales records
        product_idx = i % len(products)
        base_price = [49.99, 89.99, 299.99, 79.99, 129.99, 159.99, 399.99, 699.99][product_idx]
        cost = base_price * 0.6  # 60% of price
        quantity = np.random.randint(1, 5)
        discount_applied = np.random.choice([True, False], p=[0.3, 0.7])
        discount_amount = base_price * 0.1 if discount_applied else 0
        final_price = base_price - discount_amount
        revenue = final_price * quantity
        profit = (final_price - cost) * quantity

        sales_data.append({
            'product_id': f'P{product_idx + 1:03d}',
            'product_name': products[product_idx],
            'category': categories[product_idx],
            'subcategory': subcategories[product_idx],
            'brand': brands[product_idx],
            'price': base_price,
            'cost': cost,
            'quantity': quantity,
            'revenue': revenue,
            'profit': profit,
            'sale_date': pd.Timestamp('2024-01-01') + pd.Timedelta(days=np.random.randint(0, 90)),
            'customer_id': f'C{np.random.randint(1, 20):03d}',
            'customer_segment': np.random.choice(customer_segments),
            'region': np.random.choice(regions),
            'sales_rep': np.random.choice(sales_reps),
            'discount_applied': discount_applied,
            'discount_amount': discount_amount
        })

    df = pd.DataFrame(sales_data)
    print(f"Created comprehensive DataFrame with {len(df)} sales records")
    print("\nDataFrame sample:")
    print(df.head(3))
    print(f"\nDataFrame info:")
    print(f"Columns: {list(df.columns)}")
    print(f"Total revenue: ${df['revenue'].sum():,.2f}")
    print(f"Total profit: ${df['profit'].sum():,.2f}")

    # Bulk create from DataFrame (Repository handles the business logic)
    result = repo.bulk_create_from_dataframe(df, id_column='product_id')
    print(f"✅ Bulk created from DataFrame: {result['success_count']}/{len(df)} records")

    # Advanced search and convert back to DataFrame
    print(f"\n--- Advanced DataFrame Analysis ---")

    # High-value electronics sales
    electronics_df = repo.to_dataframe(
        term_filters={"category": "electronics"},
        range_filters={"revenue": {"gte": 200}},
        sort_by=[{"revenue": {"order": "desc"}}],
        limit=50
    )
    print(f"High-value electronics sales: {len(electronics_df)} records")

    # Gaming products analysis
    gaming_df = repo.to_dataframe(
        term_filters={"subcategory": "gaming"},
        limit=50
    )
    print(f"Gaming products sales: {len(gaming_df)} records")

    # Regional performance analysis
    if not electronics_df.empty:
        print(f"\n--- Pandas Analysis on Elasticsearch Data ---")

        # Revenue by region
        if 'region' in electronics_df.columns and 'revenue' in electronics_df.columns:
            regional_revenue = electronics_df.groupby('region')['revenue'].agg(['sum', 'mean', 'count'])
            print("\nRegional performance:")
            print(regional_revenue)

        # Top performing sales reps
        if 'sales_rep' in electronics_df.columns:
            rep_performance = electronics_df.groupby('sales_rep').agg({
                'revenue': ['sum', 'mean'],
                'profit': 'sum',
                'quantity': 'sum'
            }).round(2)
            print("\nSales rep performance:")
            print(rep_performance.head())

        # Customer segment analysis
        if 'customer_segment' in electronics_df.columns:
            segment_analysis = electronics_df.groupby('customer_segment').agg({
                'revenue': ['sum', 'mean', 'count'],
                'discount_applied': lambda x: (x == True).sum()
            }).round(2)
            print("\nCustomer segment analysis:")
            print(segment_analysis)

    # Time-based analysis using Elasticsearch aggregations
    print(f"\n--- Time-based Analysis (Repository Aggregations) ---")

    # Monthly sales trends
    monthly_sales = repo.aggregate({
        "sales_by_month": {
            "date_histogram": {
                "field": "sale_date",
                "calendar_interval": "month"
            },
            "aggs": {
                "total_revenue": {"sum": {"field": "revenue"}},
                "total_profit": {"sum": {"field": "profit"}},
                "avg_transaction": {"avg": {"field": "revenue"}},
                "transaction_count": {"value_count": {"field": "product_id"}}
            }
        }
    })

    if 'sales_by_month' in monthly_sales:
        print("Monthly sales trends:")
        for bucket in monthly_sales['sales_by_month']['buckets']:
            month = bucket['key_as_string']
            revenue = bucket['total_revenue']['value']
            profit = bucket['total_profit']['value']
            count = bucket['transaction_count']['value']
            avg_transaction = bucket['avg_transaction']['value']
            print(
                f"  {month}: {count} sales, ${revenue:,.2f} revenue, ${profit:,.2f} profit, ${avg_transaction:.2f} avg")

    # Product performance analysis
    product_performance = repo.aggregate({
        "top_products": {
            "terms": {"field": "product_name", "size": 5},
            "aggs": {
                "total_revenue": {"sum": {"field": "revenue"}},
                "total_quantity": {"sum": {"field": "quantity"}},
                "avg_price": {"avg": {"field": "price"}},
                "profit_margin": {
                    "bucket_script": {
                        "buckets_path": {
                            "revenue": "total_revenue",
                            "cost": "total_cost"
                        },
                        "script": "params.revenue > 0 ? ((params.revenue - params.cost) / params.revenue) * 100 : 0"
                    }
                },
                "total_cost": {"sum": {"field": "cost"}}
            }
        }
    })

    if 'top_products' in product_performance:
        print("\nTop performing products:")
        for bucket in product_performance['top_products']['buckets']:
            product = bucket['key']
            revenue = bucket['total_revenue']['value']
            quantity = bucket['total_quantity']['value']
            count = bucket['doc_count']
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
    client, repo = setup_elasticsearch_sync("http://localhost:9200", "exam_prep")

    # Initialize index for complex query examples
    mapping = {
        "properties": {
            "title": {"type": "text", "analyzer": "standard"},
            "description": {"type": "text"},
            "content": {"type": "text"},
            "status": {"type": "keyword"},
            "priority": {"type": "keyword"},
            "score": {"type": "float"},
            "tags": {"type": "keyword"},
            "created_by": {"type": "keyword"},
            "assigned_to": {"type": "keyword"},
            "created_date": {"type": "date"},
            "due_date": {"type": "date"},
            "completed_date": {"type": "date"},
            "completed": {"type": "boolean"},
            "difficulty": {"type": "keyword"},
            "estimated_hours": {"type": "float"},
            "actual_hours": {"type": "float"},
            "project": {"type": "keyword"},
            "department": {"type": "keyword"}
        }
    }
    repo.initialize_index(mapping)

    # Comprehensive test data for advanced queries
    test_data = [
        {
            "title": "Implement user authentication system",
            "description": "Add OAuth2 and JWT authentication to the application",
            "content": "The authentication system should support multiple providers including Google, GitHub, and email/password login",
            "status": "in_progress",
            "priority": "high",
            "score": 85.5,
            "tags": ["authentication", "security", "oauth", "jwt"],
            "created_by": "product_manager",
            "assigned_to": "developer1",
            "created_date": "2024-01-01T10:00:00Z",
            "due_date": "2024-01-15T18:00:00Z",
            "completed": False,
            "difficulty": "complex",
            "estimated_hours": 40.0,
            "actual_hours": 32.5,
            "project": "user_management",
            "department": "engineering"
        },
        {
            "title": "Database optimization and indexing",
            "description": "Optimize slow queries and add proper database indexes",
            "content": "Focus on the user search queries and product catalog performance issues",
            "status": "completed",
            "priority": "medium",
            "score": 92.0,
            "tags": ["database", "performance", "optimization", "sql"],
            "created_by": "tech_lead",
            "assigned_to": "developer2",
            "created_date": "2024-01-02T09:00:00Z",
            "due_date": "2024-01-10T17:00:00Z",
            "completed_date": "2024-01-09T16:30:00Z",
            "completed": True,
            "difficulty": "medium",
            "estimated_hours": 16.0,
            "actual_hours": 14.5,
            "project": "performance",
            "department": "engineering"
        },
        {
            "title": "Frontend UI/UX improvements",
            "description": "Redesign user interface for better user experience",
            "content": "Update the dashboard layout and improve mobile responsiveness",
            "status": "pending",
            "priority": "low",
            "score": 78.3,
            "tags": ["frontend", "ui", "ux", "design", "mobile"],
            "created_by": "ux_designer",
            "assigned_to": "designer1",
            "created_date": "2024-01-03T14:00:00Z",
            "due_date": "2024-01-20T16:00:00Z",
            "completed": False,
            "difficulty": "simple",
            "estimated_hours": 24.0,
            "actual_hours": 0.0,
            "project": "user_experience",
            "department": "design"
        },
        {
            "title": "API documentation update",
            "description": "Update API documentation with new endpoints",
            "content": "Document all REST API endpoints and add examples for developers",
            "status": "completed",
            "priority": "medium",
            "score": 88.7,
            "tags": ["documentation", "api", "rest", "developers"],
            "created_by": "tech_writer",
            "assigned_to": "developer3",
            "created_date": "2024-01-04T11:00:00Z",
            "due_date": "2024-01-12T15:00:00Z",
            "completed_date": "2024-01-11T14:20:00Z",
            "completed": True,
            "difficulty": "simple",
            "estimated_hours": 8.0,
            "actual_hours": 6.5,
            "project": "documentation",
            "department": "engineering"
        },
        {
            "title": "Security audit and vulnerability assessment",
            "description": "Conduct comprehensive security audit",
            "content": "Review authentication, authorization, data encryption, and identify potential vulnerabilities",
            "status": "in_progress",
            "priority": "high",
            "score": 95.2,
            "tags": ["security", "audit", "vulnerability", "encryption"],
            "created_by": "security_lead",
            "assigned_to": "security_expert",
            "created_date": "2024-01-05T08:00:00Z",
            "due_date": "2024-01-25T17:00:00Z",
            "completed": False,
            "difficulty": "complex",
            "estimated_hours": 60.0,
            "actual_hours": 45.0,
            "project": "security",
            "department": "security"
        }
    ]

    # Bulk create test data
    bulk_result = repo.bulk_create(test_data)
    print(f"✅ Created {bulk_result['success_count']} test records for advanced queries")

    print("\n--- Advanced Query Examples (Repository Query Building System) ---")

    # 1. Complex boolean query with multiple conditions
    complex_results = repo.search(
        text_search="authentication security",
        term_filters={"status": "in_progress", "priority": "high"},
        range_filters={"score": {"gte": 80}, "estimated_hours": {"gte": 30}},
        exists_filters=["due_date", "assigned_to"],
        sort_by=[{"score": {"order": "desc"}}],
        limit=10
    )
    print(
        f"1. Complex boolean query (high-priority, in-progress, high-score security tasks): {complex_results['total_hits']} results")

    # 2. Fuzzy search for typos
    fuzzy_results = repo.search(
        fuzzy_search={"title": "autentication"},  # Misspelled "authentication"
        limit=5
    )
    print(f"2. Fuzzy search for misspelled 'autentication': {fuzzy_results['total_hits']} results")

    # 3. Wildcard search patterns
    wildcard_results = repo.search(
        wildcard_filters={"description": "*optim*", "title": "*API*"},
        limit=5
    )
    print(f"3. Wildcard search for '*optim*' and '*API*': {wildcard_results['total_hits']} results")

    # 4. Date range queries
    date_range_results = repo.search(
        range_filters={
            "created_date": {
                "gte": "2024-01-01T00:00:00Z",
                "lte": "2024-01-03T23:59:59Z"
            },
            "due_date": {
                "gte": "2024-01-10T00:00:00Z"
            }
        },
        limit=10
    )
    print(f"4. Date range query (created Jan 1-3, due after Jan 10): {date_range_results['total_hits']} results")

    # 5. Multiple term filters with existence checks
    multi_term_results = repo.search(
        term_filters={
            "completed": False,
            "priority": "high",
            "department": "engineering"
        },
        exists_filters=["assigned_to", "estimated_hours"],
        limit=10
    )
    print(
        f"5. Multiple terms (incomplete + high priority + engineering + assigned): {multi_term_results['total_hits']} results")

    # 6. Text search across multiple fields
    multi_field_results = repo.search(
        text_search="database performance",
        term_filters={"status": "completed"},
        sort_by=[{"score": {"order": "desc"}}],
        limit=5
    )
    print(
        f"6. Multi-field text search for 'database performance' in completed tasks: {multi_field_results['total_hits']} results")

    # 7. Advanced aggregations for project analytics
    print("\n--- Advanced Aggregation Examples (Repository Analytics Logic) ---")

    # Project performance analysis
    project_analytics = repo.aggregate({
        "project_performance": {
            "terms": {"field": "project", "size": 10},
            "aggs": {
                "avg_score": {"avg": {"field": "score"}},
                "completion_rate": {
                    "bucket_script": {
                        "buckets_path": {
                            "completed": "completed_tasks",
                            "total": "_count"
                        },
                        "script": "params.completed / params.total * 100"
                    }
                },
                "completed_tasks": {
                    "filter": {"term": {"completed": True}}
                },
                "avg_hours_variance": {
                    "bucket_script": {
                        "buckets_path": {
                            "estimated": "avg_estimated",
                            "actual": "avg_actual"
                        },
                        "script": "Math.abs(params.actual - params.estimated) / params.estimated * 100"
                    }
                },
                "avg_estimated": {"avg": {"field": "estimated_hours"}},
                "avg_actual": {"avg": {"field": "actual_hours"}},
                "high_priority_count": {
                    "filter": {"term": {"priority": "high"}}
                }
            }
        }
    })

    if 'project_performance' in project_analytics:
        print("Project performance analysis:")
        for bucket in project_analytics['project_performance']['buckets']:
            project = bucket['key']
            count = bucket['doc_count']
            avg_score = bucket['avg_score']['value']
            completed = bucket['completed_tasks']['doc_count']
            high_priority = bucket['high_priority_count']['doc_count']
            avg_estimated = bucket['avg_estimated']['value']
            avg_actual = bucket['avg_actual']['value']
            print(
                f"  {project}: {count} tasks, {completed} completed, avg score: {avg_score:.1f}, {high_priority} high priority")
            print(f"    Hours: {avg_estimated:.1f} estimated vs {avg_actual:.1f} actual")

    # Status and priority breakdown
    status_priority_breakdown = repo.aggregate({
        "status_breakdown": {
            "terms": {"field": "status", "size": 10},
            "aggs": {
                "priority_distribution": {
                    "terms": {"field": "priority", "size": 5}
                },
                "avg_score": {"avg": {"field": "score"}},
                "difficulty_breakdown": {
                    "terms": {"field": "difficulty", "size": 5}
                }
            }
        }
    })

    if 'status_breakdown' in status_priority_breakdown:
        print("\nStatus and priority breakdown:")
        for bucket in status_priority_breakdown['status_breakdown']['buckets']:
            status = bucket['key']
            count = bucket['doc_count']
            avg_score = bucket['avg_score']['value']
            print(f"  {status}: {count} tasks, avg score: {avg_score:.1f}")

            for priority_bucket in bucket['priority_distribution']['buckets']:
                priority = priority_bucket['key']
                priority_count = priority_bucket['doc_count']
                print(f"    - {priority}: {priority_count} tasks")

    # Department workload analysis
    department_workload = repo.aggregate({
        "department_workload": {
            "terms": {"field": "department", "size": 10},
            "aggs": {
                "total_estimated_hours": {"sum": {"field": "estimated_hours"}},
                "total_actual_hours": {"sum": {"field": "actual_hours"}},
                "avg_task_complexity": {"avg": {"field": "score"}},
                "overdue_tasks": {
                    "filter": {
                        "bool": {
                            "must": [
                                {"term": {"completed": False}},
                                {"range": {"due_date": {"lt": "now"}}}
                            ]
                        }
                    }
                },
                "task_status_breakdown": {
                    "terms": {"field": "status", "size": 5}
                }
            }
        }
    })

    if 'department_workload' in department_workload:
        print("\nDepartment workload analysis:")
        for bucket in department_workload['department_workload']['buckets']:
            department = bucket['key']
            count = bucket['doc_count']
            estimated_hours = bucket['total_estimated_hours']['value']
            actual_hours = bucket['total_actual_hours']['value']
            avg_complexity = bucket['avg_task_complexity']['value']
            overdue = bucket['overdue_tasks']['doc_count']
            print(
                f"  {department}: {count} tasks, {estimated_hours:.1f}h estimated, {actual_hours:.1f}h actual, {overdue} overdue")
            print(f"    Avg complexity: {avg_complexity:.1f}")

    # 8. Time-based aggregations
    print("\n--- Time-based Analysis ---")

    # Tasks created over time
    creation_timeline = repo.aggregate({
        "creation_timeline": {
            "date_histogram": {
                "field": "created_date",
                "calendar_interval": "day"
            },
            "aggs": {
                "avg_score": {"avg": {"field": "score"}},
                "priority_breakdown": {
                    "terms": {"field": "priority", "size": 3}
                }
            }
        }
    })

    if 'creation_timeline' in creation_timeline:
        print("Task creation timeline:")
        for bucket in creation_timeline['creation_timeline']['buckets']:
            date = bucket['key_as_string']
            count = bucket['doc_count']
            avg_score = bucket['avg_score']['value']
            print(f"  {date}: {count} tasks created, avg score: {avg_score:.1f}")

    # 9. Performance metrics analysis
    performance_metrics = repo.aggregate({
        "performance_stats": {
            "stats": {"field": "score"}
        },
        "hours_accuracy": {
            "bucket_script": {
                "buckets_path": {
                    "estimated": "total_estimated",
                    "actual": "total_actual"
                },
                "script": "params.actual > 0 ? (Math.abs(params.actual - params.estimated) / params.estimated) * 100 : 0"
            }
        },
        "total_estimated": {"sum": {"field": "estimated_hours"}},
        "total_actual": {"sum": {"field": "actual_hours"}},
        "completion_stats": {
            "terms": {"field": "completed", "size": 2}
        }
    })

    if 'performance_stats' in performance_metrics:
        stats = performance_metrics['performance_stats']
        print(f"\nOverall performance statistics:")
        print(f"  Score range: {stats['min']:.1f} - {stats['max']:.1f}")
        print(f"  Average score: {stats['avg']:.1f}")
        print(f"  Total tasks: {stats['count']}")

    # 10. Scroll through all tasks for detailed analysis
    print(f"\n--- Detailed Task Analysis (Scroll Processing) ---")

    high_score_tasks = []
    overdue_tasks = []

    for task in repo.scroll_search(scroll_size=10):
        if task.get('score', 0) > 90:
            high_score_tasks.append(task)

        # Check if overdue (simplified check)
        if not task.get('completed', False) and 'due_date' in task:
            # In real scenario, would parse dates properly
            overdue_tasks.append(task)

    print(f"High-scoring tasks (>90): {len(high_score_tasks)}")
    print(f"Potentially overdue tasks: {len(overdue_tasks)}")

    # 11. Count operations with different filters
    total_tasks = repo.count()
    completed_tasks = repo.count(term_filters={"completed": True})
    high_priority_tasks = repo.count(term_filters={"priority": "high"})
    engineering_tasks = repo.count(term_filters={"department": "engineering"})
    complex_tasks = repo.count(term_filters={"difficulty": "complex"})

    print(f"\n--- Task Counts by Category ---")
    print(f"Total tasks: {total_tasks}")
    print(f"Completed tasks: {completed_tasks} ({completed_tasks / total_tasks * 100:.1f}%)")
    print(f"High priority tasks: {high_priority_tasks}")
    print(f"Engineering tasks: {engineering_tasks}")
    print(f"Complex tasks: {complex_tasks}")

    client.close()
    print("✅ Advanced queries example completed")

    return total_tasks


# ============================================================================
# דוגמה 5: Error Handling & Performance - טיפול בשגיאות וביצועים
# ============================================================================

def example_error_handling():
    """Example: Error handling and performance patterns"""
    print("\n=== Error Handling & Performance Example (Clean Architecture) ===")

    # Test connection errors
    try:
        # Try to connect to non-existent server
        client = ElasticsearchSyncClient("http://nonexistent:9200")
    except Exception as e:
        print(f"❌ Expected connection error: {type(e).__name__}")

    # Use real connection
    try:
        client = ElasticsearchSyncClient("http://localhost:9200")
        repo = ElasticsearchSyncRepository(client, "error_test")
        print("✅ Successfully connected to Elasticsearch")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # Test error scenarios
    print("\n--- Error Handling Tests ---")

    # 1. Get non-existent document
    missing_doc = repo.get_by_id("non_existent_id")
    print(f"1. Get missing document returns None: {missing_doc is None}")

    # 2. Search in non-existent index
    try:
        search_results = repo.search(text_search="test", limit=5)
        print(f"2. Search in non-existent index: {search_results['total_hits']} results (graceful handling)")
    except Exception as e:
        print(f"2. Search error handled: {type(e).__name__}")

    # 3. Initialize index and test with valid data
    mapping = {
        "properties": {
            "name": {"type": "text"},
            "price": {"type": "float"},
            "category": {"type": "keyword"},
            "valid": {"type": "boolean"}
        }
    }
    repo.initialize_index(mapping)
    print("✅ Index initialized for error testing")

    # 4. Bulk operations with mixed success/failure scenarios
    mixed_documents = [
        {"name": "Valid Product 1", "price": 10.99, "category": "electronics", "valid": True},
        {"name": "Valid Product 2", "price": 25.50, "category": "books", "valid": True},
        {"name": "Valid Product 3", "price": 15.75, "category": "electronics", "valid": True}
    ]

    bulk_result = repo.bulk_create(mixed_documents)
    print(f"3. Bulk create mixed data: {bulk_result['success_count']} success, {bulk_result['error_count']} errors")

    # 5. Performance demonstrations
    print("\n--- Performance Best Practices ---")

    # Generate larger dataset for performance testing
    large_dataset = []
    for i in range(200):
        large_dataset.append({
            "item": f"product_{i:04d}",
            "name": f"Product Name {i}",
            "value": i * 10.5,
            "category": f"category_{i % 5}",
            "subcategory": f"subcat_{i % 10}",
            "active": i % 3 == 0,
            "priority": ["low", "medium", "high"][i % 3],
            "metadata": {
                "created_by": f"user_{i % 20}",
                "tags": [f"tag_{j}" for j in range(i % 4 + 1)]
            }
        })

    # Performance test: Bulk vs individual operations
    import time

    # Bulk insert (recommended)
    start_time = time.time()
    bulk_result = repo.bulk_create(large_dataset)
    bulk_time = time.time() - start_time
    print(f"4a. Bulk insert {len(large_dataset)} docs: {bulk_time:.3f}s ({bulk_result['success_count']} successful)")

    # Refresh for search performance
    repo.refresh_index()

    # Performance test: Scroll vs pagination for large results
    start_time = time.time()
    scroll_count = 0
    for doc in repo.scroll_search(scroll_size=50):
        scroll_count += 1
        if scroll_count >= 150:  # Limit for demo
            break
    scroll_time = time.time() - start_time
    print(f"4b. Scroll through {scroll_count} docs: {scroll_time:.3f}s")

    # Performance test: Targeted search vs broad search
    start_time = time.time()
    targeted_results = repo.search(
        term_filters={"category": "category_1", "active": True},
        range_filters={"value": {"gte": 50, "lte": 150}},
        limit=20
    )
    targeted_time = time.time() - start_time
    print(f"4c. Targeted search: {targeted_time:.3f}s for {targeted_results['total_hits']} results")

    # Performance test: Aggregation performance
    start_time = time.time()
    agg_results = repo.aggregate({
        "category_stats": {
            "terms": {"field": "category", "size": 10},
            "aggs": {
                "avg_value": {"avg": {"field": "value"}},
                "max_value": {"max": {"field": "value"}},
                "active_count": {"filter": {"term": {"active": True}}}
            }
        }
    })
    agg_time = time.time() - start_time
    print(f"4d. Complex aggregation: {agg_time:.3f}s")

    # 6. Memory-efficient processing with scroll
    print("\n--- Memory-Efficient Processing ---")

    def process_large_dataset_efficiently():
        """Demonstrate memory-efficient processing"""
        total_value = 0
        processed_count = 0
        category_counts = {}

        # Process in batches to avoid memory issues
        for document in repo.scroll_search(
                term_filters={"active": True},
                scroll_size=25  # Small batches
        ):
            # Process each document
            total_value += document.get('value', 0)
            processed_count += 1

            category = document.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1

            # Progress reporting
            if processed_count % 50 == 0:
                print(f"    Processed {processed_count} documents...")

        return {
            'total_value': total_value,
            'processed_count': processed_count,
            'category_distribution': category_counts
        }

    efficient_results = process_large_dataset_efficiently()
    print(f"Efficiently processed {efficient_results['processed_count']} documents")
    print(f"Total value: {efficient_results['total_value']:,.2f}")
    print(f"Categories found: {len(efficient_results['category_distribution'])}")

    # 7. Error recovery patterns
    print("\n--- Error Recovery Patterns ---")

    # Retry pattern for transient failures
    def retry_operation(operation, max_retries=3):
        """Retry pattern for transient failures"""
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"    Operation failed after {max_retries} attempts: {e}")
                    raise
                print(f"    Attempt {attempt + 1} failed, retrying...")
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff

    # Test retry pattern
    def flaky_search():
        return repo.search(text_search="test", limit=5)

    try:
        results = retry_operation(flaky_search)
        print(f"5. Retry pattern successful: {results['total_hits']} results")
    except Exception as e:
        print(f"5. Retry pattern failed: {e}")

    # 8. Resource cleanup and monitoring
    print("\n--- Resource Management ---")

    # Check index health
    if repo.index_exists():
        total_docs = repo.count()
        print(f"Index health: {total_docs} documents indexed")

        # Sample some documents to verify data integrity
        sample_results = repo.search(limit=3)
        print(f"Sample verification: {len(sample_results['documents'])} sample documents retrieved")

        for doc in sample_results['documents'][:2]:
            print(f"  Sample: {doc.get('name', 'N/A')} - {doc.get('category', 'N/A')}")

    # Performance summary
    print(f"\n--- Performance Summary ---")
    print(f"✅ Bulk operations: {bulk_time:.3f}s for {len(large_dataset)} documents")
    print(f"✅ Scroll processing: {scroll_time:.3f}s for {scroll_count} documents")
    print(f"✅ Targeted search: {targeted_time:.3f}s")
    print(f"✅ Aggregations: {agg_time:.3f}s")

    # Cleanup
    client.close()
    print("✅ Error handling and performance example completed")


# ============================================================================
# דוגמה 6: Quick Exam Patterns - דפוסים מהירים למבחן
# ============================================================================

def quick_exam_patterns():
    """Quick patterns for exam preparation"""
    print("\n=== QUICK EXAM PATTERNS (Clean Architecture) ===")

    # Setup pattern (Repository + Client separation)
    print("1. Setup Pattern (Fixed Architecture):")
    print("   # Sync")
    print("   from shared_utilities.elasticsearch import ElasticsearchSyncClient, ElasticsearchSyncRepository")
    print("   client = ElasticsearchSyncClient('http://localhost:9200')  # CONNECTION ONLY")
    print("   repo = ElasticsearchSyncRepository(client, 'index_name')   # CRUD ONLY")
    print()
    print("   # Async")
    print("   from shared_utilities.elasticsearch import ElasticsearchAsyncClient, ElasticsearchAsyncRepository")
    print("   client = ElasticsearchAsyncClient('http://localhost:9200')")
    print("   await client.connect()")
    print("   repo = ElasticsearchAsyncRepository(client, 'index_name')")

    # CRUD patterns
    print("\n2. CRUD Operations (Repository Logic):")
    print("   CREATE: doc_id = repo.create({'field': 'value'})")
    print("   READ:   doc = repo.get_by_id(doc_id)")
    print("   UPDATE: success = repo.update(doc_id, {'field': 'new_value'})")
    print("   DELETE: success = repo.delete(doc_id)")

    # Search patterns
    print("\n3. Search Patterns (Repository Query Building):")
    print("   TEXT:     repo.search(text_search='gaming laptop')")
    print("   EXACT:    repo.search(term_filters={'category': 'electronics'})")
    print("   RANGE:    repo.search(range_filters={'price': {'gte': 100, 'lte': 500}})")
    print("   WILDCARD: repo.search(wildcard_filters={'name': '*wireless*'})")
    print("   FUZZY:    repo.search(fuzzy_search={'name': 'lapto'})")
    print("   COMBO:    repo.search(text_search='gaming', term_filters={'in_stock': True})")

    # Bulk patterns
    print("\n4. Bulk Operations (Repository Batch Logic):")
    print("   CREATE: repo.bulk_create([{'name': 'Item1'}, {'name': 'Item2'}])")
    print("   UPDATE: repo.bulk_update([{'_id': 'id1', 'doc': {'field': 'new'}}])")
    print("   DELETE: repo.bulk_delete(['id1', 'id2', 'id3'])")

    # Aggregation patterns
    print("\n5. Common Aggregations (Repository Analytics):")
    print("   AVG:    repo.aggregate({'avg_price': {'avg': {'field': 'price'}}})")
    print("   GROUP:  repo.aggregate({'categories': {'terms': {'field': 'category'}}})")
    print("   RANGE:  repo.aggregate({'price_ranges': {'range': {'field': 'price', 'ranges': [...]}}})")
    print("   STATS:  repo.aggregate({'price_stats': {'stats': {'field': 'price'}}})")

    # DataFrame patterns
    print("\n6. DataFrame Integration (Repository Data Logic):")
    print("   TO_DF:   df = repo.to_dataframe(limit=100)")
    print("   FROM_DF: repo.bulk_create_from_dataframe(df, id_column='id')")

    # Performance patterns
    print("\n7. Performance Patterns:")
    print("   SCROLL:  for doc in repo.scroll_search(scroll_size=1000): process(doc)")
    print("   COUNT:   count = repo.count(term_filters={'status': 'active'})")
    print("   BULK:    # Always prefer bulk operations over individual ones")
    print("   REFRESH: repo.refresh_index()  # Make recent changes searchable")

    # Mapping patterns
    print("\n8. Common Mapping Patterns:")
    print("   TEXT:    {'field': {'type': 'text'}}      # For full-text search")
    print("   KEYWORD: {'field': {'type': 'keyword'}}   # For exact filtering")
    print("   DATE:    {'field': {'type': 'date'}}      # For date operations")
    print("   FLOAT:   {'field': {'type': 'float'}}     # For numeric operations")
    print("   BOOL:    {'field': {'type': 'boolean'}}   # For true/false")

    # Error handling patterns
    print("\n9. Error Handling:")
    print("   CHECK:   if repo.index_exists(): ...")
    print("   SAFE:    doc = repo.get_by_id(id) or {}")
    print("   BULK:    result = repo.bulk_create(docs)")
    print("           if result['error_count'] > 0: handle_errors()")

    print("\n✅ Quick exam patterns ready - Clean Architecture implemented!")


# ============================================================================
# Main execution function
# ============================================================================

if __name__ == "__main__":
    print("🔍 Elasticsearch Examples - COMPLETELY FIXED ARCHITECTURE")
    print("\nClean separation:")
    print("  - Clients: CONNECTION ONLY (execute_* methods)")
    print("  - Repositories: CRUD ONLY (create, search, aggregate methods)")
    print()
    print("Choose example to run:")
    print("1. Sync usage (Client + Repository separation)")
    print("2. Async usage (Client + Repository separation)")
    print("3. DataFrame integration")
    print("4. Advanced queries")
    print("5. Error handling & performance")
    print("6. Quick exam patterns")
    print("7. All examples")

    choice = input("\nEnter choice (1-7): ").strip()

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
            example_error_handling()
        elif choice == "6":
            quick_exam_patterns()
        elif choice == "7":
            # Run all examples
            print("Running ALL examples with FIXED ARCHITECTURE...\n")

            sync_result = example_sync_usage()
            async_result = asyncio.run(example_async_usage())
            df_result = example_dataframe_integration()
            query_result = example_advanced_queries()
            example_error_handling()
            quick_exam_patterns()

            print(f"\n🎉 ALL EXAMPLES COMPLETED WITH CLEAN ARCHITECTURE!")
            print(f"✅ Sync products: {sync_result['total_products']}")
            print(f"✅ Async articles: {async_result['total_articles']}")
            print(f"✅ DataFrame records: {df_result}")
            print(f"✅ Advanced query tasks: {query_result}")
            print(f"✅ Architecture: CLEAN SEPARATION between Clients and Repositories")
        else:
            print("Invalid choice")

    except Exception as e:
        print(f"❌ Example failed: {e}")
        print("Make sure Elasticsearch is running on localhost:9200")

    print(f"\n✅ Elasticsearch examples completed!")
    print(f"🏗️  Architecture: CONNECTION clients + CRUD repositories")
    print(
        f"🎯  Ready for exam with clean patterns!")  # ============================================================================
# shared-utilities/elasticsearch/EXAMPLES.py - COMPLETELY FIXED
# ============================================================================

import asyncio
import pandas as pd
from datetime import datetime, timezone

# Import the FIXED elasticsearch utilities
from . import (
    ElasticsearchSyncClient, ElasticsearchAsyncClient,
    ElasticsearchSyncRepository, ElasticsearchAsyncRepository,
    setup_elasticsearch_sync, setup_elasticsearch_async
)


# ============================================================================
# דוגמה 1: Sync Usage - שימוש סינכרוני עם הפרדה נכונה
# ============================================================================

def example_sync_usage():
    """Example: sync client (CONNECTION ONLY) + sync repository (CRUD ONLY)"""
    print("=== Synchronous Elasticsearch Example (FIXED ARCHITECTURE) ===")

    # 1. Create SYNC client (CONNECTION ONLY) + SYNC repository (CRUD ONLY)
    client = ElasticsearchSyncClient("http://localhost:9200")
    repo = ElasticsearchSyncRepository(client, "products")

    # 2. Initialize index with mapping
    mapping = {
        "properties": {
            "name": {"type": "text", "analyzer": "standard"},
            "description": {"type": "text"},
            "price": {"type": "float"},
            "category": {"type": "keyword"},  # For exact filtering
            "brand": {"type": "keyword"},
            "tags": {"type": "keyword"},  # Array of keywords
            "in_stock": {"type": "boolean"},
            "rating": {"type": "float"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"}
        }
    }

    settings = {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "standard": {
                    "type": "standard"
                }
            }
        }
    }

    # Repository handles the business logic
    repo.initialize_index(mapping, settings)
    print("✅ Index initialized with mapping")

    # 3. Create single document (Repository handles metadata)
    product_id = repo.create({
        "name": "Gaming Laptop Pro",
        "description": "High-performance laptop for gaming and productivity with RTX 4080",
        "price": 1299.99,
        "category": "electronics",
        "brand": "TechCorp",
        "tags": ["gaming", "laptop", "high-performance", "rtx"],
        "in_stock": True,
        "rating": 4.7
    })
    print(f"✅ Created product: {product_id}")

    # 4. Bulk create multiple products (Repository handles the logic)
    products = [
        {
            "name": "Wireless Gaming Mouse",
            "description": "Ergonomic wireless mouse with precision tracking and RGB lighting",
            "price": 49.99,
            "category": "electronics",
            "brand": "GameGear",
            "tags": ["mouse", "wireless", "gaming", "rgb"],
            "in_stock": True,
            "rating": 4.3
        },
        {
            "name": "Mechanical Keyboard RGB",
            "description": "RGB mechanical keyboard with blue switches and customizable lighting",
            "price": 129.99,
            "category": "electronics",
            "brand": "KeyMaster",
            "tags": ["keyboard", "mechanical", "rgb", "blue-switches"],
            "in_stock": False,
            "rating": 4.6
        },
        {
            "name": "4K Ultra Monitor",
            "description": "27-inch 4K UHD monitor with HDR support and 144Hz refresh rate",
            "price": 399.99,
            "category": "electronics",
            "brand": "DisplayPro",
            "tags": ["monitor", "4k", "hdr", "144hz"],
            "in_stock": True,
            "rating": 4.8
        },
        {
            "name": "Python Programming Guide",
            "description": "Complete guide to Python programming with practical examples",
            "price": 39.99,
            "category": "books",
            "brand": "TechBooks",
            "tags": ["programming", "python", "education", "guide"],
            "in_stock": True,
            "rating": 4.5
        },
        {
            "name": "Wireless Headphones",
            "description": "Noise-cancelling wireless headphones with 30-hour battery life",
            "price": 199.99,
            "category": "electronics",
            "brand": "SoundWave",
            "tags": ["headphones", "wireless", "noise-cancelling"],
            "in_stock": True,
            "rating": 4.4
        }
    ]

    # Repository handles bulk creation with metadata
    bulk_result = repo.bulk_create(products)
    print(f"✅ Bulk created: {bulk_result['success_count']}/{len(products)} products")

    # 5. Search with various filters (Repository handles query building)
    print("\n--- Search Examples (Repository Query Building) ---")

    # Text search
    text_results = repo.search(
        text_search="gaming laptop",
        limit=5
    )
    print(f"Text search 'gaming laptop': {text_results['total_hits']} results")

    # Term filters (exact matches)
    electronics = repo.search(
        term_filters={"category": "electronics", "in_stock": True},
        limit=10
    )
    print(f"In-stock electronics: {electronics['total_hits']} products")

    # Range filters
    expensive_products = repo.search(
        range_filters={"price": {"gte": 100, "lte": 500}},
        limit=10
    )
    print(f"Price $100-500: {expensive_products['total_hits']} products")

    # Combined complex search
    gaming_deals = repo.search(
        text_search="gaming",
        term_filters={"category": "electronics", "in_stock": True},
        range_filters={"price": {"lte": 200}, "rating": {"gte": 4.0}},
        sort_by=[{"price": {"order": "asc"}}],
        limit=10
    )
    print(f"Gaming deals (in-stock, <$200, rating>=4.0): {gaming_deals['total_hits']} products")

    # Wildcard search
    wireless_products = repo.search(
        wildcard_filters={"name": "*wireless*"},
        limit=10
    )
    print(f"Products with 'wireless': {wireless_products['total_hits']} results")

    # Fuzzy search
    fuzzy_results = repo.search(
        fuzzy_search={"name": "lapto"},  # Will find "laptop"
        limit=5
    )
    print(f"Fuzzy search for 'lapto': {fuzzy_results['total_hits']} results")

    # Exists filters
    has_rating = repo.search(
        exists_filters=["rating", "tags"],
        limit=10
    )
    print(f"Products with rating and tags: {has_rating['total_hits']} results")

    # 6. Get specific document
    if product_id:
        product = repo.get_by_id(product_id)
        print(f"✅ Retrieved product: {product['name']} - ${product['price']}")

    # 7. Update document
    if product_id:
        updated = repo.update(product_id, {
            "price": 1199.99,
            "tags": ["gaming", "laptop", "high-performance", "rtx", "discounted"],
            "in_stock": True
        })
        print(f"✅ Updated product: {updated}")

    # 8. Aggregations (Repository handles complex aggregations)
    print("\n--- Aggregations (Repository Business Logic) ---")

    # Average price by category
    price_agg = repo.aggregate({
        "avg_price_by_category": {
            "terms": {"field": "category", "size": 10},
            "aggs": {
                "avg_price": {"avg": {"field": "price"}},
                "min_price": {"min": {"field": "price"}},
                "max_price": {"max": {"field": "price"}},
                "product_count": {"value_count": {"field": "name"}}
            }
        }
    })

    if 'avg_price_by_category' in price_agg:
        print("Price analysis by category:")
        for bucket in price_agg['avg_price_by_category']['buckets']:
            category = bucket['key']
            avg_price = bucket['avg_price']['value']
            min_price = bucket['min_price']['value']
            max_price = bucket['max_price']['value']
            count = bucket['doc_count']
            print(f"  {category}: {count} products, avg=${avg_price:.2f}, range=${min_price:.2f}-${max_price:.2f}")

    # Brand distribution