# ============================================================================
# shared-utilities/data_science/basic/clients/data_loader_client.py
# ============================================================================
"""
Data Loader Client - Connection Management for File Loading
Handles connection to various file formats and data sources
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

import pandas as pd

logger = logging.getLogger(__name__)


class DataLoaderClient:
    """
    Client for managing connections to data sources
    Handles file format detection and loading strategies
    """

    def __init__(self,
                 default_encoding: str = "utf-8",
                 cache_enabled: bool = False,
                 connection_timeout: int = 30):
        """
        Initialize data loader client.

        Args:
            default_encoding: Default text encoding
            cache_enabled: Whether to cache loaded data
            connection_timeout: Timeout for network operations
        """
        self.default_encoding = default_encoding
        self.cache_enabled = cache_enabled
        self.connection_timeout = connection_timeout
        self._connection_cache = {}
        self._data_cache = {}

        # Supported file formats and their handlers
        self.supported_formats = {
            '.csv': self._connect_csv,
            '.tsv': self._connect_tsv,
            '.json': self._connect_json,
            '.jsonl': self._connect_jsonlines,
            '.xlsx': self._connect_excel,
            '.xls': self._connect_excel,
            '.parquet': self._connect_parquet,
            '.txt': self._connect_text,
            '.html': self._connect_html,
            '.xml': self._connect_xml
        }

        logger.info(f"DataLoaderClient initialized with {len(self.supported_formats)} supported formats")

    def connect(self, path: str, **connection_options) -> 'DataConnection':
        """
        Establish connection to data source.

        Args:
            path: Path to data file or connection string
            **connection_options: Format-specific connection options

        Returns:
            DataConnection object for performing operations
        """
        path_obj = Path(path)

        if not path_obj.exists():
            raise FileNotFoundError(f"Data source not found: {path}")

        file_extension = path_obj.suffix.lower()
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported format: {file_extension}")

        # Check cache
        cache_key = f"{path}:{hash(str(connection_options))}"
        if self.cache_enabled and cache_key in self._connection_cache:
            logger.info(f"Using cached connection for {path}")
            return self._connection_cache[cache_key]

        # Create new connection
        logger.info(f"Creating new connection to {file_extension} file: {path}")
        connection_handler = self.supported_formats[file_extension]

        connection = DataConnection(
            path=path,
            format=file_extension,
            handler=connection_handler,
            encoding=self.default_encoding,
            client=self,
            **connection_options
        )

        # Cache connection if enabled
        if self.cache_enabled:
            self._connection_cache[cache_key] = connection

        return connection

    def test_connection(self, path: str) -> Dict[str, Any]:
        """
        Test connection to data source without loading data.

        Args:
            path: Path to test

        Returns:
            Connection test results
        """
        try:
            path_obj = Path(path)

            if not path_obj.exists():
                return {
                    'success': False,
                    'error': 'File not found',
                    'path': path
                }

            file_extension = path_obj.suffix.lower()

            result = {
                'success': True,
                'path': path,
                'format': file_extension,
                'supported': file_extension in self.supported_formats,
                'size_bytes': path_obj.stat().st_size,
                'size_mb': round(path_obj.stat().st_size / (1024 * 1024), 2)
            }

            # Try to read first few rows for additional info
            if result['supported']:
                try:
                    connection = self.connect(path)
                    sample_data = connection.peek(rows=5)
                    result.update({
                        'sample_rows': len(sample_data),
                        'columns': list(sample_data.columns) if hasattr(sample_data, 'columns') else [],
                        'preview_available': True
                    })
                except Exception as e:
                    result.update({
                        'preview_available': False,
                        'preview_error': str(e)
                    })

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'path': path
            }

    def list_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return list(self.supported_formats.keys())

    def clear_cache(self):
        """Clear connection and data cache."""
        self._connection_cache.clear()
        self._data_cache.clear()
        logger.info("Connection cache cleared")

    # ========================================================================
    # Format-specific connection handlers
    # ========================================================================

    def _connect_csv(self, path: str, **options) -> Dict[str, Any]:
        """CSV connection handler."""
        defaults = {'encoding': self.default_encoding, 'low_memory': False}
        defaults.update(options)
        return {'loader': pd.read_csv, 'options': defaults}

    def _connect_tsv(self, path: str, **options) -> Dict[str, Any]:
        """TSV connection handler."""
        defaults = {'encoding': self.default_encoding, 'sep': '\t', 'low_memory': False}
        defaults.update(options)
        return {'loader': pd.read_csv, 'options': defaults}

    def _connect_json(self, path: str, **options) -> Dict[str, Any]:
        """JSON connection handler."""
        defaults = {'encoding': self.default_encoding}
        defaults.update(options)

        def json_loader(file_path, **opts):
            with open(file_path, 'r', encoding=opts.get('encoding', 'utf-8')) as f:
                data = json.load(f)

            if isinstance(data, list):
                return pd.json_normalize(data)
            elif isinstance(data, dict):
                return pd.json_normalize([data])
            else:
                return pd.DataFrame([data])

        return {'loader': json_loader, 'options': defaults}

    def _connect_jsonlines(self, path: str, **options) -> Dict[str, Any]:
        """JSON Lines connection handler."""
        defaults = {'encoding': self.default_encoding, 'lines': True}
        defaults.update(options)
        return {'loader': pd.read_json, 'options': defaults}

    def _connect_excel(self, path: str, **options) -> Dict[str, Any]:
        """Excel connection handler."""
        defaults = {'engine': 'openpyxl'}
        defaults.update(options)
        return {'loader': pd.read_excel, 'options': defaults}

    def _connect_parquet(self, path: str, **options) -> Dict[str, Any]:
        """Parquet connection handler."""
        return {'loader': pd.read_parquet, 'options': options}

    def _connect_text(self, path: str, **options) -> Dict[str, Any]:
        """Text file connection handler."""
        defaults = {'column_name': 'text'}
        defaults.update(options)

        def text_loader(file_path, **opts):
            col_name = opts.get('column_name', 'text')
            encoding = opts.get('encoding', self.default_encoding)

            with open(file_path, 'r', encoding=encoding) as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]

            return pd.DataFrame(lines, columns=[col_name])

        return {'loader': text_loader, 'options': defaults}

    def _connect_html(self, path: str, **options) -> Dict[str, Any]:
        """HTML connection handler."""
        defaults = {'encoding': self.default_encoding}
        defaults.update(options)

        def html_loader(file_path, **opts):
            tables = pd.read_html(file_path, **opts)
            return tables[0] if tables else pd.DataFrame()

        return {'loader': html_loader, 'options': defaults}

    def _connect_xml(self, path: str, **options) -> Dict[str, Any]:
        """XML connection handler."""
        defaults = {'encoding': self.default_encoding}
        defaults.update(options)
        return {'loader': pd.read_xml, 'options': defaults}


class DataConnection:
    """
    Represents an active connection to a data source
    Provides methods for data operations without re-establishing connection
    """

    def __init__(self,
                 path: str,
                 format: str,
                 handler: callable,
                 encoding: str,
                 client: DataLoaderClient,
                 **options):
        """
        Initialize data connection.

        Args:
            path: Path to data source
            format: File format
            handler: Connection handler function
            encoding: Text encoding
            client: Parent client
            **options: Connection options
        """
        self.path = path
        self.format = format
        self.handler = handler
        self.encoding = encoding
        self.client = client
        self.options = options
        self._connection_config = None
        self._is_connected = False

        # Establish connection
        self._connect()

    def _connect(self):
        """Establish the actual connection."""
        try:
            self._connection_config = self.handler(self.path, **self.options)
            self._is_connected = True
            logger.info(f"Connection established to {self.format} file: {self.path}")
        except Exception as e:
            logger.error(f"Failed to establish connection: {e}")
            raise

    def load_data(self, **load_options) -> pd.DataFrame:
        """
        Load data using established connection.

        Args:
            **load_options: Additional loading options

        Returns:
            Loaded DataFrame
        """
        if not self._is_connected:
            raise RuntimeError("Connection not established")

        try:
            # Merge connection options with load options
            merged_options = {**self._connection_config['options'], **load_options}

            # Load data using configured loader
            loader = self._connection_config['loader']
            df = loader(self.path, **merged_options)

            logger.info(f"Loaded {len(df):,} rows, {len(df.columns)} columns from {self.path}")
            return df

        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise

    def peek(self, rows: int = 5) -> pd.DataFrame:
        """
        Load a small sample of data for preview.

        Args:
            rows: Number of rows to preview

        Returns:
            Sample DataFrame
        """
        try:
            # For CSV/TSV, use nrows parameter
            if self.format in ['.csv', '.tsv']:
                return self.load_data(nrows=rows)

            # For other formats, load all and take first N rows
            df = self.load_data()
            return df.head(rows)

        except Exception as e:
            logger.warning(f"Failed to peek data: {e}")
            return pd.DataFrame()

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the data source.

        Returns:
            Data source information
        """
        try:
            sample = self.peek(100)  # Larger sample for better info

            return {
                'path': self.path,
                'format': self.format,
                'encoding': self.encoding,
                'sample_rows': len(sample),
                'columns': list(sample.columns) if hasattr(sample, 'columns') else [],
                'column_count': len(sample.columns) if hasattr(sample, 'columns') else 0,
                'dtypes': sample.dtypes.to_dict() if hasattr(sample, 'dtypes') else {},
                'connection_options': self.options,
                'is_connected': self._is_connected
            }

        except Exception as e:
            return {
                'path': self.path,
                'format': self.format,
                'error': str(e),
                'is_connected': self._is_connected
            }

    def close(self):
        """Close the connection."""
        self._is_connected = False
        logger.info(f"Connection closed: {self.path}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()