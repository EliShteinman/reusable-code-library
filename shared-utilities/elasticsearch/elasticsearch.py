# shared-utilities/elasticsearch/elasticsearch_sync_client.py
# RESTORED: The perfect Elasticsearch client with all features

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan

logger = logging.getLogger(__name__)


class ElasticsearchSyncClient:
    """
    Synchronous Elasticsearch client with full CRUD operations and query builder.
    RESTORED: All the advanced features that were working perfectly!
    """

    def __init__(self, es_url: str, index_name: Optional[str] = None, **kwargs):
        self.es_url = es_url
        self.index_name = index_name
        self.es = Elasticsearch(es_url, **kwargs)

        # Test connection
        try:
            info = self.es.info()
            logger.info(f"Connected to Elasticsearch {info['version']['number']}")
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise

    def _build_query(self,
                     query_text: Optional[str] = None,
                     search_terms: Optional[List[str]] = None,
                     term_filters: Optional[Dict[str, Any]] = None,
                     exists_filters: Optional[List[str]] = None,
                     not_exists_filters: Optional[List[str]] = None,
                     terms_filters: Optional[Dict[str, List[str]]] = None,
                     range_filters: Optional[Dict[str, Dict[str, Any]]] = None,
                     script_filters: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        RESTORED: Universal query builder supporting all filter types.
        This was the crown jewel of the Elasticsearch implementation!
        """
        must_clauses: List[Dict[str, Any]] = []
        filter_clauses: List[Dict[str, Any]] = []
        must_not_clauses: List[Dict[str, Any]] = []

        # Text search
        if query_text:
            must_clauses.append({"match": {"text": query_text}})
        elif search_terms:
            must_clauses.append({"terms": {"text": search_terms}})
        else:
            must_clauses.append({"match_all": {}})

        # Term filters (exact matches)
        if term_filters:
            for field, value in term_filters.items():
                filter_clauses.append({"term": {field: value}})

        # Exists filters
        if exists_filters:
            for field in exists_filters:
                filter_clauses.append({"exists": {"field": field}})

        # Not exists filters
        if not_exists_filters:
            for field in not_exists_filters:
                must_not_clauses.append({"exists": {"field": field}})

        # Terms filters (multiple values)
        if terms_filters:
            for field, values in terms_filters.items():
                filter_clauses.append({"terms": {field: values}})

        # Range filters
        if range_filters:
            for field, range_config in range_filters.items():
                filter_clauses.append({"range": {field: range_config}})

        # Script filters
        if script_filters:
            for script_source in script_filters:
                filter_clauses.append({"script": {"script": {"source": script_source}}})

        return {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses,
                "must_not": must_not_clauses,
            }
        }

    # Index Management
    def create_index(self,
                     index_name: Optional[str] = None,
                     mapping: Optional[Dict[str, Any]] = None,
                     settings: Optional[Dict[str, Any]] = None) -> bool:
        """Create index with mapping and settings."""
        index = index_name or self.index_name
        if not index:
            raise ValueError("Index name must be provided")

        try:
            body = {}
            if mapping:
                body['mappings'] = mapping
            if settings:
                body['settings'] = settings

            self.es.indices.create(index=index, body=body if body else None)
            logger.info(f"Created index: {index}")
            return True
        except Exception as e:
            logger.error(f"Failed to create index {index}: {e}")
            return False

    def delete_index(self, index_name: Optional[str] = None) -> bool:
        """Delete index."""
        index = index_name or self.index_name
        try:
            self.es.indices.delete(index=index, ignore=[404])
            logger.info(f"Deleted index: {index}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete index {index}: {e}")
            return False

    def refresh_index(self, index_name: Optional[str] = None) -> bool:
        """Refresh index."""
        index = index_name or self.index_name
        try:
            self.es.indices.refresh(index=index)
            return True
        except Exception as e:
            logger.error(f"Failed to refresh index {index}: {e}")
            return False

    # Document CRUD Operations
    def create_document(self,
                        doc: Dict[str, Any],
                        doc_id: Optional[str] = None,
                        index_name: Optional[str] = None) -> Optional[str]:
        """Create document."""
        index = index_name or self.index_name
        if not index:
            raise ValueError("Index name must be provided")

        try:
            doc_with_meta = doc.copy()
            doc_with_meta['created_at'] = datetime.now(timezone.utc)
            doc_with_meta['updated_at'] = datetime.now(timezone.utc)

            if doc_id:
                result = self.es.create(index=index, id=doc_id, body=doc_with_meta)
            else:
                result = self.es.index(index=index, body=doc_with_meta)

            return result['_id']
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            return None

    def get_document(self, doc_id: str, index_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        index = index_name or self.index_name
        try:
            result = self.es.get(index=index, id=doc_id)
            doc = result['_source']
            doc['id'] = result['_id']
            return doc
        except Exception as e:
            if "not_found" not in str(e).lower():
                logger.error(f"Failed to get document {doc_id}: {e}")
            return None

    def update_document(self,
                        doc_id: str,
                        doc_update: Dict[str, Any],
                        index_name: Optional[str] = None) -> bool:
        """Update document."""
        index = index_name or self.index_name
        try:
            update_with_meta = doc_update.copy()
            update_with_meta['updated_at'] = datetime.now(timezone.utc)

            self.es.update(index=index, id=doc_id, body={'doc': update_with_meta})
            return True
        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            return False

    def delete_document(self, doc_id: str, index_name: Optional[str] = None) -> bool:
        """Delete document."""
        index = index_name or self.index_name
        try:
            self.es.delete(index=index, id=doc_id)
            return True
        except Exception as e:
            if "not_found" not in str(e).lower():
                logger.error(f"Failed to delete document {doc_id}: {e}")
            return False

    # Search Operations - RESTORED!
    def search_documents(self,
                         limit: int = 10,
                         offset: int = 0,
                         index_name: Optional[str] = None,
                         **kwargs) -> Dict[str, Any]:
        """RESTORED: Search documents with advanced query builder."""
        index = index_name or self.index_name

        query = self._build_query(**kwargs)
        search_body = {
            "query": query,
            "from": offset,
            "size": limit,
            "sort": [{"created_at": {"order": "desc"}}]
        }

        try:
            result = self.es.search(index=index, body=search_body)

            documents = []
            for hit in result['hits']['hits']:
                doc = hit['_source']
                doc['id'] = hit['_id']
                doc['score'] = hit['_score']
                documents.append(doc)

            return {
                'total_hits': result['hits']['total']['value'],
                'max_score': result['hits']['max_score'],
                'took_ms': result['took'],
                'documents': documents
            }
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {'total_hits': 0, 'documents': []}

    def count_documents(self, index_name: Optional[str] = None, **kwargs) -> int:
        """Count documents matching query."""
        index = index_name or self.index_name
        query = self._build_query(**kwargs)

        try:
            result = self.es.count(index=index, body={'query': query})
            return result.get('count', 0)
        except Exception as e:
            logger.error(f"Count failed: {e}")
            return 0

    # Bulk Operations - RESTORED!
    def bulk_index_documents(self,
                             documents: List[Dict[str, Any]],
                             index_name: Optional[str] = None,
                             doc_id_field: Optional[str] = None) -> Dict[str, Any]:
        """RESTORED: Bulk index documents - this was working perfectly!"""
        index = index_name or self.index_name

        try:
            now = datetime.now(timezone.utc)
            actions = []

            for doc in documents:
                doc_with_meta = doc.copy()
                doc_with_meta['created_at'] = now
                doc_with_meta['updated_at'] = now

                action = {'_index': index, '_source': doc_with_meta}
                if doc_id_field and doc_id_field in doc:
                    action['_id'] = doc[doc_id_field]

                actions.append(action)

            success, failed = bulk(self.es, actions, stats_only=True)
            self.refresh_index(index)

            return {'success_count': success, 'error_count': failed}
        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
            return {'success_count': 0, 'error_count': len(documents)}

    # Scan Operations - RESTORED!
    def scroll_search(self, index_name: Optional[str] = None, scroll_size: int = 1000, **kwargs):
        """RESTORED: Generator for scrolling through large result sets - this was amazing!"""
        index = index_name or self.index_name
        query = self._build_query(**kwargs)

        try:
            for hit in scan(self.es, query=query, index=index, size=scroll_size):
                doc = hit['_source']
                doc['id'] = hit['_id']
                yield doc
        except Exception as e:
            logger.error(f"Scroll search failed: {e}")

    # Advanced Search Methods - RESTORED!
    def simple_search(self, query_text: str, fields: List[str] = None,
                      index_name: Optional[str] = None, size: int = 10) -> List[Dict[str, Any]]:
        """RESTORED: Simple multi-match search."""
        index = index_name or self.index_name
        search_fields = fields or ["_all"]

        body = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": search_fields
                }
            },
            "size": size
        }

        try:
            result = self.es.search(index=index, body=body)
            documents = []
            for hit in result['hits']['hits']:
                doc = hit['_source']
                doc['id'] = hit['_id']
                doc['score'] = hit['_score']
                documents.append(doc)
            return documents
        except Exception as e:
            logger.error(f"Simple search failed: {e}")
            return []

    def aggregation_search(self, aggregations: Dict[str, Any],
                           index_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """RESTORED: Aggregation search."""
        index = index_name or self.index_name
        query = self._build_query(**kwargs)

        body = {
            "query": query,
            "aggs": aggregations,
            "size": 0  # Don't return documents, just aggregations
        }

        try:
            result = self.es.search(index=index, body=body)
            return result.get('aggregations', {})
        except Exception as e:
            logger.error(f"Aggregation search failed: {e}")
            return {}

    def close(self):
        """Close client connection."""
        try:
            self.es.close()
        except Exception as e:
            logger.error(f"Error closing client: {e}")


# ============================================================================
# shared-utilities/elasticsearch/elasticsearch_repository.py
# RESTORED: Repository with all the perfect functionality
# ============================================================================

import logging
from typing import Any, Dict, List, Optional, Union
import pandas as pd

logger = logging.getLogger(__name__)


class ElasticsearchRepository:
    """
    RESTORED: High-level repository pattern for Elasticsearch operations.
    All the perfect functionality is back!
    """

    def __init__(self, client: ElasticsearchSyncClient, index_name: str):
        self.client = client
        self.index_name = index_name

    # High-level CRUD operations
    def create(self, document: Dict[str, Any], doc_id: Optional[str] = None):
        """Create a document."""
        return self.client.create_document(document, doc_id, self.index_name)

    def get_by_id(self, doc_id: str):
        """Get document by ID."""
        return self.client.get_document(doc_id, self.index_name)

    def update(self, doc_id: str, updates: Dict[str, Any]):
        """Update document."""
        return self.client.update_document(doc_id, updates, self.index_name)

    def delete(self, doc_id: str):
        """Delete document."""
        return self.client.delete_document(doc_id, self.index_name)

    # Search operations with simplified interface
    def search(self,
               limit: int = 10,
               offset: int = 0,
               **filters):
        """Search documents with filters."""
        return self.client.search_documents(
            limit=limit,
            offset=offset,
            index_name=self.index_name,
            **filters
        )

    def search_by_field(self, field: str, value: Any, limit: int = 10):
        """Search by exact field value."""
        return self.search(
            term_filters={field: value},
            limit=limit
        )

    def search_by_text(self, text: str, fields: List[str] = None, limit: int = 10):
        """Simple text search."""
        return self.client.simple_search(text, fields, self.index_name, limit)

    def search_in_field(self, field: str, values: List[Any], limit: int = 10):
        """Search where field value is in list."""
        return self.search(
            terms_filters={field: values},
            limit=limit
        )

    def search_range(self, field: str, gte=None, lte=None, gt=None, lt=None, limit: int = 10):
        """Range search."""
        range_filter = {}
        if gte is not None:
            range_filter['gte'] = gte
        if lte is not None:
            range_filter['lte'] = lte
        if gt is not None:
            range_filter['gt'] = gt
        if lt is not None:
            range_filter['lt'] = lt

        return self.search(
            range_filters={field: range_filter},
            limit=limit
        )

    def count(self, **filters):
        """Count documents matching filters."""
        return self.client.count_documents(
            index_name=self.index_name,
            **filters
        )

    # Bulk operations - RESTORED!
    def bulk_create(self, documents: List[Dict[str, Any]], id_field: str = None):
        """Bulk create documents."""
        return self.client.bulk_index_documents(documents, self.index_name, id_field)

    def bulk_create_from_dataframe(self, df: pd.DataFrame, id_field: str = None):
        """Bulk create from DataFrame."""
        documents = df.to_dict('records')
        return self.bulk_create(documents, id_field)

    # Scan operations - RESTORED!
    def scan_all(self, **filters):
        """Scan through all documents matching filters."""
        return self.client.scroll_search(self.index_name, **filters)

    # Index management
    def initialize_index(self, mapping: Dict[str, Any] = None, settings: Dict[str, Any] = None):
        """Initialize index with mapping."""
        # Delete existing
        self.client.delete_index(self.index_name)
        # Create new
        return self.client.create_index(self.index_name, mapping, settings)

    def refresh(self):
        """Refresh index."""
        return self.client.refresh_index(self.index_name)

    # Advanced operations - RESTORED!
    def aggregate(self, aggregations: Dict[str, Any], **filters):
        """Run aggregations."""
        return self.client.aggregation_search(aggregations, self.index_name, **filters)


# ============================================================================
# USAGE EXAMPLES - All the perfect functionality restored!
# ============================================================================

def elasticsearch_perfect_usage_example():
    """Example showing all the restored perfect functionality."""
    from shared_utilities.elasticsearch import ElasticsearchSyncClient, ElasticsearchRepository

    # Setup
    client = ElasticsearchSyncClient("http://localhost:9200", "products")
    repo = ElasticsearchRepository(client, "products")

    # Initialize index with mapping
    repo.initialize_index({
        "properties": {
            "name": {"type": "text"},
            "description": {"type": "text"},
            "price": {"type": "float"},
            "category": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "created_at": {"type": "date"}
        }
    })

    # CRUD operations
    doc_id = repo.create({
        "name": "Gaming Laptop",
        "description": "High-performance laptop for gaming",
        "price": 1299.99,
        "category": "electronics",
        "tags": ["gaming", "laptop", "high-performance"]
    })

    # Advanced search - RESTORED!
    results = repo.search(
        term_filters={"category": "electronics"},
        range_filters={"price": {"gte": 1000, "lte": 2000}},
        exists_filters=["tags"],
        limit=10
    )

    # Bulk operations - RESTORED!
    products = [
        {"name": f"Product {i}", "price": i * 10, "category": "test"}
        for i in range(1000)
    ]
    bulk_result = repo.bulk_create(products)
    print(f"Bulk indexed: {bulk_result['success_count']} products")

    # Scan through large datasets - RESTORED!
    print("Scanning through all electronics:")
    for product in repo.scan_all(term_filters={"category": "electronics"}):
        print(f"Found: {product['name']}")
        break  # Just show first one

    # Aggregations - RESTORED!
    agg_results = repo.aggregate({
        "avg_price": {"avg": {"field": "price"}},
        "categories": {"terms": {"field": "category"}}
    })

    client.close()


if __name__ == "__main__":
    elasticsearch_perfect_usage_example()