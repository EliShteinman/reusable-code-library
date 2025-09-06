# shared-utilities/mongodb/mongodb_repository.py
import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd

logger = logging.getLogger(__name__)


class MongoDBRepository:
    """
    High-level repository pattern for MongoDB operations.
    Works with both sync and async clients, similar to Elasticsearch pattern.
    """

    def __init__(self, client: Union['MongoDBSyncClient', 'MongoDBAsyncClient'], collection_name: str = None):
        self.client = client
        self.collection_name = collection_name
        self.is_async = hasattr(client, '__aenter__') or 'async' in str(type(client)).lower()

    def _handle_async(self, method, *args, **kwargs):
        """Helper to handle both sync and async calls."""
        return method(*args, **kwargs)

    # High-level CRUD operations
    def create(self, document: Dict[str, Any]):
        """Create a document."""
        return self._handle_async(
            self.client.create_document,
            document,
            self.collection_name
        )

    def get_by_id(self, doc_id: Union[str, int], id_field: str = "ID"):
        """Get document by ID."""
        return self._handle_async(
            self.client.get_document_by_id,
            doc_id,
            id_field,
            self.collection_name
        )

    def get_by_filter(self, filter_query: Dict[str, Any]):
        """Get document by custom filter."""
        return self._handle_async(
            self.client.get_document,
            filter_query,
            self.collection_name
        )

    def update_by_id(self, doc_id: Union[str, int], updates: Dict[str, Any], id_field: str = "ID"):
        """Update document by ID."""
        return self._handle_async(
            self.client.update_document_by_id,
            doc_id,
            updates,
            id_field,
            self.collection_name
        )

    def update_by_filter(self, filter_query: Dict[str, Any], updates: Dict[str, Any]):
        """Update document by filter."""
        return self._handle_async(
            self.client.update_document,
            filter_query,
            updates,
            self.collection_name
        )

    def delete_by_id(self, doc_id: Union[str, int], id_field: str = "ID"):
        """Delete document by ID."""
        return self._handle_async(
            self.client.delete_document_by_id,
            doc_id,
            id_field,
            self.collection_name
        )

    def delete_by_filter(self, filter_query: Dict[str, Any]):
        """Delete document by filter."""
        return self._handle_async(
            self.client.delete_document,
            filter_query,
            self.collection_name
        )

    # Search operations with simplified interface
    def search(self,
               limit: int = 10,
               skip: int = 0,
               sort_by: Optional[List[tuple]] = None,
               **filters):
        """Search documents with filters."""
        search_params = {
            'limit': limit,
            'skip': skip,
            'sort_by': sort_by,
            'collection_name': self.collection_name
        }
        search_params.update(filters)

        return self._handle_async(
            self.client.search_documents,
            **search_params
        )

    def search_by_field(self, field: str, value: Any, limit: int = 10):
        """Search by exact field value."""
        return self.search(
            field_filters={field: value},
            limit=limit
        )

    def search_by_text(self, text: str, limit: int = 10):
        """Text search (requires text index)."""
        return self.search(
            text_search=text,
            limit=limit
        )

    def search_in_field(self, field: str, values: List[Any], limit: int = 10):
        """Search where field value is in list."""
        return self.search(
            in_filters={field: values},
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

    def search_regex(self, field: str, pattern: str, limit: int = 10):
        """Regex search."""
        return self.search(
            regex_filters={field: pattern},
            limit=limit
        )

    def count(self, **filters):
        """Count documents matching filters."""
        return self._handle_async(
            self.client.count_documents,
            collection_name=self.collection_name,
            **filters
        )

    def get_all(self, limit: int = None, **filters):
        """Get all documents matching filters."""
        return self._handle_async(
            self.client.get_all_documents,
            collection_name=self.collection_name,
            limit=limit,
            **filters
        )

    # Bulk operations
    def bulk_create(self, documents: List[Dict[str, Any]]):
        """Bulk create documents."""
        return self._handle_async(
            self.client.bulk_create_documents,
            documents,
            self.collection_name
        )

    def bulk_create_from_dataframe(self, df: pd.DataFrame):
        """Bulk create from DataFrame."""
        documents = df.to_dict('records')
        return self.bulk_create(documents)

    # Aggregation operations
    def group_by(self, field: str):
        """Group documents by field value."""
        return self._handle_async(
            self.client.group_by_field,
            field,
            self.collection_name
        )

    def aggregate(self, pipeline: List[Dict[str, Any]]):
        """Execute custom aggregation pipeline."""
        return self._handle_async(
            self.client.aggregate,
            pipeline,
            self.collection_name
        )

    # Collection management
    def drop_collection(self):
        """Drop the collection."""
        return self._handle_async(
            self.client.drop_collection,
            self.collection_name
        )

    def get_stats(self):
        """Get collection statistics."""
        return self._handle_async(
            self.client.get_collection_stats,
            self.collection_name
        )

    def create_index(self, index_spec: Union[str, List[tuple]], **kwargs):
        """Create index on collection."""
        return self._handle_async(
            self.client.create_index,
            index_spec,
            self.collection_name,
            **kwargs
        )
