# shared-utilities/elasticsearch/elasticsearch_sync_client.py
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan

logger = logging.getLogger(__name__)


class ElasticsearchSyncClient:
    """
    Synchronous Elasticsearch client with full CRUD operations.
    Enhanced version with query builder like your async version.
    """

    def __init__(self, es_url: str, index_name: Optional[str] = None, **kwargs):
        self.es = Elasticsearch(es_url, **kwargs)
        self.index_name = index_name

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
        Universal query builder supporting all filter types.
        Based on your app/utils/elasticSearch_repository.py pattern.
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

    # Document CRUD
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

    # Search Operations
    def search_documents(self,
                         limit: int = 10,
                         offset: int = 0,
                         index_name: Optional[str] = None,
                         **kwargs) -> Dict[str, Any]:
        """Search documents with query builder."""
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

    # Bulk Operations
    def bulk_index_documents(self,
                             documents: List[Dict[str, Any]],
                             index_name: Optional[str] = None,
                             doc_id_field: Optional[str] = None) -> Dict[str, Any]:
        """Bulk index documents."""
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

    def scroll_search(self, index_name: Optional[str] = None, scroll_size: int = 1000, **kwargs):
        """Generator for scrolling through large result sets."""
        index = index_name or self.index_name
        query = self._build_query(**kwargs)

        try:
            for hit in scan(self.es, query=query, index=index, size=scroll_size):
                doc = hit['_source']
                doc['id'] = hit['_id']
                yield doc
        except Exception as e:
            logger.error(f"Scroll search failed: {e}")

    def close(self):
        """Close client connection."""
        try:
            self.es.close()
        except Exception as e:
            logger.error(f"Error closing client: {e}")







