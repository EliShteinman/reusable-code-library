# shared-utilities/elasticsearch/elasticsearch_repository.py
import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd

logger = logging.getLogger(__name__)


class ElasticsearchRepository:
    """
    High-level repository pattern for Elasticsearch operations.
    Works with both sync and async clients.
    """

    def __init__(self, client: Union['ElasticsearchSyncClient', 'ElasticsearchAsyncClient'], index_name: str):
        self.client = client
        self.index_name = index_name
        self.is_async = hasattr(client, '__aenter__') or 'async' in str(type(client)).lower()

    def _handle_async(self, method, *args, **kwargs):
        """Helper to handle both sync and async calls."""
        if self.is_async:
            return method(*args, **kwargs)
        else:
            return method(*args, **kwargs)

    # High-level CRUD operations
    def create(self, document: Dict[str, Any], doc_id: Optional[str] = None):
        """Create a document."""
        return self._handle_async(
            self.client.create_document,
            document,
            doc_id,
            self.index_name
        )

    def get_by_id(self, doc_id: str):
        """Get document by ID."""
        return self._handle_async(
            self.client.get_document,
            doc_id,
            self.index_name
        )

    def update(self, doc_id: str, updates: Dict[str, Any]):
        """Update document."""
        return self._handle_async(
            self.client.update_document,
            doc_id,
            updates,
            self.index_name
        )

    def delete(self, doc_id: str):
        """Delete document."""
        return self._handle_async(
            self.client.delete_document,
            doc_id,
            self.index_name
        )

    # Search operations
    def search(self,
               query: str = None,
               limit: int = 10,
               offset: int = 0,
               **filters):
        """Simple search interface."""
        search_params = {'limit': limit, 'offset': offset, 'index_name': self.index_name}

        if query:
            search_params['query_text'] = query

        search_params.update(filters)

        return self._handle_async(
            self.client.search_documents,
            **search_params
        )

    def search_by_field(self, field: str, value: Any, limit: int = 10):
        """Search by exact field value."""
        return self.search(
            term_filters={field: value},
            limit=limit
        )

    def search_by_terms(self, field: str, values: List[Any], limit: int = 10):
        """Search by multiple field values."""
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
        return self._handle_async(
            self.client.count_documents,
            index_name=self.index_name,
            **filters
        )

    # Bulk operations
    def bulk_create(self, documents: List[Dict[str, Any]], id_field: str = None):
        """Bulk create documents."""
        return self._handle_async(
            self.client.bulk_index_documents,
            documents,
            self.index_name,
            id_field
        )

    def bulk_create_from_dataframe(self, df: pd.DataFrame, id_field: str = None):
        """Bulk create from DataFrame."""
        documents = df.to_dict('records')
        return self.bulk_create(documents, id_field)

    # Index management
    def initialize_index(self, mapping: Dict[str, Any] = None, settings: Dict[str, Any] = None):
        """Initialize index with mapping."""
        # Delete existing
        self._handle_async(self.client.delete_index, self.index_name)

        # Create new
        return self._handle_async(
            self.client.create_index,
            self.index_name,
            mapping,
            settings
        )

    def refresh(self):
        """Refresh index."""
        return self._handle_async(self.client.refresh_index, self.index_name)