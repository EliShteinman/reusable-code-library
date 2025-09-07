
# ============================================================================
# USAGE EXAMPLES - CLEAN SEPARATION
# ============================================================================

def example_sync_usage():
    """Example: sync client + repository"""

    # 1. Create CONNECTION client
    client = MongoDBSyncClient("mongodb://localhost:27017", "test_db")
    client.connect()

    # 2. Create CRUD repository
    repo = MongoDBRepository(client, "users")

    # 3. Use repository for CRUD
    user_id = repo.create({
        "ID": 123,
        "name": "John Doe",
        "email": "john@test.com",
        "age": 30
    })

    user = repo.get_by_id(user_id)
    print(f"Created user: {user}")

    # 4. Search with filters
    results = repo.search(
        field_filters={"age": {"$gte": 25}},
        limit=10
    )

    # 5. Range search
    adults = repo.search(
        range_filters={"age": {"gte": 18, "lte": 65}},
        limit=20
    )

    # 6. Bulk operations
    users_data = [
        {"ID": i, "name": f"User {i}", "age": 20 + i}
        for i in range(100, 110)
    ]
    bulk_result = repo.bulk_create(users_data)
    print(f"Bulk created: {bulk_result['success_count']} users")

    # 7. Pandas integration
    import pandas as pd
    df = pd.DataFrame([
        {"ID": i, "name": f"DF User {i}", "age": 25 + i}
        for i in range(200, 205)
    ])
    df_result = repo.bulk_create_from_dataframe(df)

    # 8. Close connection
    client.close()

    return results


async def example_async_usage():
    """Example: async client + repository"""

    # 1. Create async CONNECTION client
    client = MongoDBAsyncClient("mongodb://localhost:27017", "test_async_db")
    await client.connect()

    # 2. Create CRUD repository
    repo = MongoDBRepository(client, "async_users")

    # 3. Use async CRUD
    user_id = await repo.create_async({
        "ID": 456,
        "name": "Async User",
        "email": "async@test.com"
    })

    user = await repo.get_by_id_async(user_id)
    print(f"Created async user: {user}")

    # 4. Async search
    results = await repo.search_async(
        field_filters={"name": {"$regex": "Async"}},
        limit=5
    )

    # 5. Async bulk operations
    async_users = [
        {"ID": i, "name": f"Async User {i}"}
        for i in range(500, 510)
    ]
    bulk_result = await repo.bulk_create_async(async_users)

    # 6. Close connection
    await client.close()

    return results


def example_repository_patterns():
    """Example: Advanced repository patterns"""

    client, repo = setup_mongodb_sync(
        "mongodb://localhost:27017",
        "exam_db",
        "products"
    )

    # Search by specific field
    electronics = repo.search(
        field_filters={"category": "electronics"},
        limit=20
    )

    # Range search for prices
    expensive_products = repo.search(
        range_filters={"price": {"gte": 1000, "lte": 5000}},
        limit=10
    )

    # Text search (requires text index)
    # repo.client.create_index("products", [("name", "text"), ("description", "text")])
    search_results = repo.search(
        text_search="laptop gaming",
        limit=15
    )

    # Multiple filters
    filtered_results = repo.search(
        field_filters={"category": "electronics", "brand": "Apple"},
        range_filters={"price": {"gte": 500}},
        in_filters={"color": ["black", "white", "silver"]},
        limit=25
    )

    client.close()
    return filtered_results


if __name__ == "__main__":
    # Test sync
    sync_results = example_sync_usage()
    print(f"Sync results: {len(sync_results['documents'])} documents")

    # Test async
    import asyncio

    async_results = asyncio.run(example_async_usage())
    print(f"Async results: {len(async_results['documents'])} documents")

    # Test patterns
    pattern_results = example_repository_patterns()
    print(f"Pattern results: {len(pattern_results['documents'])} documents")