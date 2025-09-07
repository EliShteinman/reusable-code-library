# shared-utilities/elasticsearch/elasticsearch_repository.py
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import pandas as pd

logger = logging.getLogger(__name__)


class ElasticsearchRepository:
    """
    Elasticsearch CRUD repository - OPERATIONS ONLY
    Works with both sync and async clients
    """

    def __init__(self, client: Union[ElasticsearchSyncClient, 'ElasticsearchAsyncClient'], index_name: str):
        self.client = client
        self.index_name = index_name
        self.is_async = hasattr(client, 'connected')  # Detect async client

    def _add_metadata(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Add created_at and updated_at to document."""
        doc_with_meta = doc.copy()
        now = datetime.now(timezone.utc)
        doc_with_meta['created_at'] = now
        doc_with_meta['updated_at'] = now
        return doc_with_meta

    def _build_query(self, **filters) -> Dict[str, Any]:
        """Build Elasticsearch query from filters."""
        must_clauses = []
        filter_clauses = []

        # Text search
        if 'query_text' in filters:
            must_clauses.append({"match": {"_all": filters['query_text']}})
        else:
            must_clauses.append({"match_all": {}})

        # Term filters (exact matches)
        if 'term_filters' in filters:
            for field, value in filters['term_filters'].items():
                filter_clauses.append({"term": {field: value}})

        # Range filters
        if 'range_filters' in filters:
            for field, range_config in filters['range_filters'].items():
                filter_clauses.append({"range": {field: range_config}})

        return {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses
            }
        }

    # SYNC CRUD OPERATIONS
    def create(self, document: Dict[str, Any], doc_id: str = None) -> Optional[str]:
        """Create document (sync)."""
        if self.is_async:
            raise RuntimeError("Use create_async for async client")

        doc_with_meta = self._add_metadata(document)
        result = self.client.execute_index(self.index_name, doc_with_meta, doc_id)
        return result['_id'] if result else None

    def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID (sync)."""
        if self.is_async:
            raise RuntimeError("Use get_by_id_async for async client")

        result = self.client.execute_get(self.index_name, doc_id)
        if result:
            doc = result['_source']
            doc['_id'] = result['_id']
            return doc
        return None

    def search(self, limit: int = 10, offset: int = 0, **filters) -> Dict[str, Any]:
        """Search documents (sync)."""
        if self.is_async:
            raise RuntimeError("Use search_async for async client")

        query = self._build_query(**filters)
        search_body = {
            "query": query,
            "from": offset,
            "size": limit,
            "sort": [{"created_at": {"order": "desc"}}]
        }

        result = self.client.execute_search(self.index_name, search_body)

        documents = []
        for hit in result['hits']['hits']:
            doc = hit['_source']
            doc['_id'] = hit['_id']
            doc['_score'] = hit['_score']
            documents.append(doc)

        return {
            'total_hits': result['hits']['total']['value'],
            'documents': documents
        }

    def bulk_create(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk create documents (sync)."""
        if self.is_async:
            raise RuntimeError("Use bulk_create_async for async client")

        actions = []
        for doc in documents:
            doc_with_meta = self._add_metadata(doc)
            actions.append({
                '_index': self.index_name,
                '_source': doc_with_meta
            })

        success, failed = self.client.execute_bulk(actions)
        self.client.refresh_index(self.index_name)

        return {'success_count': success, 'error_count': failed}

    # ASYNC CRUD OPERATIONS
    async def create_async(self, document: Dict[str, Any], doc_id: str = None) -> Optional[str]:
        """Create document (async)."""
        if not self.is_async:
            raise RuntimeError("Use create for sync client")

        doc_with_meta = self._add_metadata(document)
        result = await self.client.execute_index(self.index_name, doc_with_meta, doc_id)
        return result['_id'] if result else None

    async def get_by_id_async(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID (async)."""
        if not self.is_async:
            raise RuntimeError("Use get_by_id for sync client")

        result = await self.client.execute_get(self.index_name, doc_id)
        if result:
            doc = result['_source']
            doc['_id'] = result['_id']
            return doc
        return None

    async def search_async(self, limit: int = 10, offset: int = 0, **filters) -> Dict[str, Any]:
        """Search documents (async)."""
        if not self.is_async:
            raise RuntimeError("Use search for sync client")

        query = self._build_query(**filters)
        search_body = {
            "query": query,
            "from": offset,
            "size": limit,
            "sort": [{"created_at": {"order": "desc"}}]
        }

        result = await self.client.execute_search(self.index_name, search_body)

        documents = []
        for hit in result['hits']['hits']:
            doc = hit['_source']
            doc['_id'] = hit['_id']
            doc['_score'] = hit['_score']
            documents.append(doc)

        return {
            'total_hits': result['hits']['total']['value'],
            'documents': documents
        }

    # INDEX MANAGEMENT
    def initialize_index(self, mapping: Dict[str, Any] = None):
        """Initialize index with mapping."""
        return self.client.create_index(self.index_name, mapping)
