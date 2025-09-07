
# ============================================================================
# USAGE EXAMPLES - CLEAN SEPARATION
# ============================================================================

def example_sync_usage():
    """Example: sync client + repository"""

    # 1. Create CONNECTION client
    client = ElasticsearchSyncClient("http://localhost:9200")

    # 2. Create CRUD repository
    repo = ElasticsearchRepository(client, "products")

    # 3. Initialize index
    repo.initialize_index({
        "properties": {
            "name": {"type": "text"},
            "price": {"type": "float"},
            "category": {"type": "keyword"}
        }
    })

    # 4. Use repository for CRUD
    doc_id = repo.create({"name": "Laptop", "price": 999.99, "category": "electronics"})
    product = repo.get_by_id(doc_id)

    # 5. Search
    results = repo.search(
        term_filters={"category": "electronics"},
        range_filters={"price": {"gte": 500}},
        limit=10
    )

    # 6. Bulk operations
    products = [
        {"name": f"Product {i}", "price": i * 10, "category": "test"}
        for i in range(100)
    ]
    bulk_result = repo.bulk_create(products)

    # 7. Close connection
    client.close()

    return results


async def example_async_usage():
    """Example: async client + repository"""

    # 1. Create async CONNECTION client
    client = ElasticsearchAsyncClient("http://localhost:9200")
    await client.connect()

    # 2. Create CRUD repository
    repo = ElasticsearchRepository(client, "async_products")

    # 3. Use async CRUD
    doc_id = await repo.create_async({"name": "Async Product", "price": 199.99})
    product = await repo.get_by_id_async(doc_id)

    # 4. Async search
    results = await repo.search_async(
        term_filters={"category": "electronics"},
        limit=5
    )

    # 5. Close connection
    await client.close()

    return results


if __name__ == "__main__":
    # Test sync
    sync_results = example_sync_usage()
    print(f"Sync results: {len(sync_results['documents'])} documents")

    # Test async
    import asyncio

    async_results = asyncio.run(example_async_usage())
    print(f"Async results: {len(async_results['documents'])} documents")