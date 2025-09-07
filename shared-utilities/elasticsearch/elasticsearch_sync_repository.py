# ============================================================================
# shared-utilities/elasticsearch/elasticsearch_sync_repository.py - CRUD ONLY
# ============================================================================
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class ElasticsearchSyncRepository:
    """
    Elasticsearch SYNC CRUD repository - OPERATIONS ONLY
    Works ONLY with ElasticsearchSyncClient
    """

    def __init__(self, client, index_name: str):
        """
        Initialize sync repository.

        Args:
            client: ElasticsearchSyncClient instance
            index_name: Elasticsearch index name
        """
        self.client = client
        self.index_name = index_name

    def _add_metadata(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Add created_at and updated_at to document."""
        doc_with_meta = doc.copy()
        now = datetime.now(timezone.utc)
        doc_with_meta['created_at'] = now
        doc_with_meta['updated_at'] = now
        return doc_with_meta

    def _build_query(self, **filters) -> Dict[str, Any]:
        """
        Build Elasticsearch query from filters.

        Args:
            text_search: Full text search query
            term_filters: Exact term matches {"field": "value"}
            range_filters: Range queries {"field": {"gte": 10, "lte": 100}}
            fuzzy_search: Fuzzy text search {"field": "value"}
            wildcard_filters: Wildcard searches {"field": "val*"}
            exists_filters: Field existence checks ["field1", "field2"]
            sort_by: Sort specification [{"field": {"order": "desc"}}]

        Returns:
            Elasticsearch query dict
        """
        must_clauses = []
        filter_clauses = []
        should_clauses = []

        # Text search (match query)
        if 'text_search' in filters and filters['text_search']:
            must_clauses.append({
                "multi_match": {
                    "query": filters['text_search'],
                    "fields": ["_all", "*"],
                    "type": "best_fields"
                }
            })

        # Term filters (exact matches)
        if 'term_filters' in filters:
            for field, value in filters['term_filters'].items():
                filter_clauses.append({"term": {field: value}})

        # Range filters
        if 'range_filters' in filters:
            for field, range_config in filters['range_filters'].items():
                filter_clauses.append({"range": {field: range_config}})

        # Fuzzy search
        if 'fuzzy_search' in filters:
            for field, value in filters['fuzzy_search'].items():
                should_clauses.append({
                    "fuzzy": {field: {"value": value, "fuzziness": "AUTO"}}
                })

        # Wildcard filters
        if 'wildcard_filters' in filters:
            for field, pattern in filters['wildcard_filters'].items():
                filter_clauses.append({"wildcard": {field: pattern}})

        # Exists filters
        if 'exists_filters' in filters:
            for field in filters['exists_filters']:
                filter_clauses.append({"exists": {"field": field}})

        # Build final query
        query = {"bool": {}}

        if must_clauses:
            query["bool"]["must"] = must_clauses
        else:
            query["bool"]["must"] = [{"match_all": {}}]

        if filter_clauses:
            query["bool"]["filter"] = filter_clauses

        if should_clauses:
            query["bool"]["should"] = should_clauses
            query["bool"]["minimum_should_match"] = 1

        return query

    # BASIC CRUD OPERATIONS
    def create(self, document: Dict[str, Any], doc_id: str = None) -> Optional[str]:
        """Create document in Elasticsearch."""
        try:
            doc_with_meta = self._add_metadata(document)
            result = self.client.execute_index(self.index_name, doc_with_meta, doc_id)
            logger.info(f"Document created in {self.index_name}: {result['_id']}")
            return result['_id']
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            return None

    def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        try:
            result = self.client.execute_get(self.index_name, doc_id)
            if result:
                doc = result['_source']
                doc['_id'] = result['_id']
                doc['_score'] = result.get('_score')
                return doc
            return None
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None

    def update(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        """Update document by ID."""
        try:
            updates_with_meta = updates.copy()
            updates_with_meta['updated_at'] = datetime.now(timezone.utc)

            result = self.client.execute_update(self.index_name, doc_id, updates_with_meta)
            logger.info(f"Document updated in {self.index_name}: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            return False

    def delete(self, doc_id: str) -> bool:
        """Delete document by ID."""
        try:
            result = self.client.execute_delete(self.index_name, doc_id)
            logger.info(f"Document deleted from {self.index_name}: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False

    # SEARCH OPERATIONS
    def search(self, limit: int = 10, offset: int = 0, **filters) -> Dict[str, Any]:
        """
        Search documents with various filters.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            **filters: Search filters (see _build_query)

        Returns:
            Dict with total_hits, documents, and metadata
        """
        try:
            query = self._build_query(**filters)

            # Add sorting
            sort_spec = filters.get('sort_by', [{"created_at": {"order": "desc"}}])

            search_body = {
                "query": query,
                "from": offset,
                "size": limit,
                "sort": sort_spec
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
                'max_score': result['hits']['max_score'],
                'documents': documents,
                'took': result['took'],
                'timed_out': result['timed_out']
            }

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {'total_hits': 0, 'documents': [], 'error': str(e)}

    def count(self, **filters) -> int:
        """Count documents matching filters."""
        try:
            query = self._build_query(**filters)
            count_body = {"query": query}
            result = self.client.execute_count(self.index_name, count_body)
            return result['count']
        except Exception as e:
            logger.error(f"Count failed: {e}")
            return 0

    def scroll_search(self, scroll_size: int = 1000, **filters):
        """
        Scroll through large result sets.

        Args:
            scroll_size: Number of documents per batch
            **filters: Search filters

        Yields:
            Individual documents
        """
        try:
            query = self._build_query(**filters)
            search_body = {"query": query}

            for doc in self.client.execute_scan(self.index_name, search_body, scroll_size):
                # Add metadata
                doc['_source']['_id'] = doc['_id']
                doc['_source']['_score'] = doc['_score']
                yield doc['_source']

        except Exception as e:
            logger.error(f"Scroll search failed: {e}")

    # BULK OPERATIONS
    def bulk_create(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk create multiple documents."""
        try:
            actions = []
            for doc in documents:
                doc_with_meta = self._add_metadata(doc)
                actions.append({
                    '_index': self.index_name,
                    '_source': doc_with_meta
                })

            result = self.client.execute_bulk(actions)

            # Refresh index to make documents searchable
            self.client.refresh_index(self.index_name)

            logger.info(f"Bulk created {result['success']} documents in {self.index_name}")
            return {
                'success_count': result['success'],
                'error_count': result['failed']
            }

        except Exception as e:
            logger.error(f"Bulk create failed: {e}")
            return {'success_count': 0, 'error_count': len(documents)}

    def bulk_update(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk update multiple documents.

        Args:
            updates: List of {"_id": "doc_id", "doc": {"field": "value"}}
        """
        try:
            actions = []
            for update in updates:
                doc_id = update['_id']
                update_data = update['doc'].copy()
                update_data['updated_at'] = datetime.now(timezone.utc)

                actions.append({
                    '_op_type': 'update',
                    '_index': self.index_name,
                    '_id': doc_id,
                    'doc': update_data
                })

            result = self.client.execute_bulk(actions)
            logger.info(f"Bulk updated {result['success']} documents in {self.index_name}")
            return {
                'success_count': result['success'],
                'error_count': result['failed']
            }

        except Exception as e:
            logger.error(f"Bulk update failed: {e}")
            return {'success_count': 0, 'error_count': len(updates)}

    def bulk_delete(self, doc_ids: List[str]) -> Dict[str, Any]:
        """Bulk delete multiple documents by IDs."""
        try:
            actions = []
            for doc_id in doc_ids:
                actions.append({
                    '_op_type': 'delete',
                    '_index': self.index_name,
                    '_id': doc_id
                })

            result = self.client.execute_bulk(actions)
            logger.info(f"Bulk deleted {result['success']} documents from {self.index_name}")
            return {
                'success_count': result['success'],
                'error_count': result['failed']
            }

        except Exception as e:
            logger.error(f"Bulk delete failed: {e}")
            return {'success_count': 0, 'error_count': len(doc_ids)}

    # AGGREGATIONS
    def aggregate(self, aggregations: Dict[str, Any], **filters) -> Dict[str, Any]:
        """
        Perform aggregations on the index.

        Args:
            aggregations: Elasticsearch aggregation query
            **filters: Filters to apply before aggregation

        Returns:
            Aggregation results
        """
        try:
            query = self._build_query(**filters)
            agg_body = {
                "query": query,
                "aggs": aggregations
            }

            result = self.client.execute_search(self.index_name, agg_body)
            return result['aggregations']

        except Exception as e:
            logger.error(f"Aggregation failed: {e}")
            return {}

    # PANDAS INTEGRATION
    def to_dataframe(self, **filters) -> pd.DataFrame:
        """Convert search results to pandas DataFrame."""
        try:
            # Get all results using scroll
            documents = list(self.scroll_search(**filters))

            if not documents:
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(documents)
            logger.info(f"Created DataFrame with {len(df)} rows from {self.index_name}")
            return df

        except Exception as e:
            logger.error(f"Failed to create DataFrame: {e}")
            return pd.DataFrame()

    def bulk_create_from_dataframe(self, df: pd.DataFrame, id_column: str = None) -> Dict[str, Any]:
        """
        Bulk create documents from pandas DataFrame.

        Args:
            df: pandas DataFrame
            id_column: Column to use as document ID (optional)

        Returns:
            Result dict with success/error counts
        """
        try:
            documents = df.to_dict('records')

            # If ID column specified, extract IDs
            if id_column and id_column in df.columns:
                actions = []
                for i, doc in enumerate(documents):
                    doc_id = str(doc.pop(id_column))  # Remove ID from document
                    doc_with_meta = self._add_metadata(doc)
                    actions.append({
                        '_index': self.index_name,
                        '_id': doc_id,
                        '_source': doc_with_meta
                    })

                result = self.client.execute_bulk(actions)
                self.client.refresh_index(self.index_name)

                return {
                    'success_count': result['success'],
                    'error_count': result['failed']
                }
            else:
                # No ID column, use regular bulk create
                return self.bulk_create(documents)

        except Exception as e:
            logger.error(f"Failed to create from DataFrame: {e}")
            return {'success_count': 0, 'error_count': len(df)}

    # INDEX MANAGEMENT
    def initialize_index(self, mapping: Dict[str, Any] = None, settings: Dict[str, Any] = None):
        """Initialize index with mapping and settings."""
        return self.client.create_index(self.index_name, mapping, settings)

    def delete_index(self):
        """Delete the entire index."""
        return self.client.delete_index(self.index_name)

    def refresh_index(self):
        """Refresh index to make recent changes searchable."""
        return self.client.refresh_index(self.index_name)

    def index_exists(self) -> bool:
        """Check if index exists."""
        return self.client.index_exists(self.index_name)