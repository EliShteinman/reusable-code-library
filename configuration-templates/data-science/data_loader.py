# configuration-templates/data-science/data_loader.py
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Optional, Union

logger = logging.getLogger(__name__)


class DataHandler:
    """
    Universal data loader class supporting multiple file formats.
    Handles CSV, JSON, Excel files with proper error handling and encoding support.
    """

    SUPPORTED_FORMATS = ['csv', 'json', 'xlsx', 'xls', 'parquet']

    def __init__(self, data_path: Union[str, Path], encoding: str = "utf-8", **kwargs):
        """
        Initialize the data loader with path and configuration.

        Args:
            data_path: Path to the data file
            encoding: File encoding (default: utf-8)
            **kwargs: Additional parameters passed to pandas read functions

        Raises:
            ValueError: If data path is empty or file format not supported
            FileNotFoundError: If file doesn't exist
        """
        if not data_path:
            raise ValueError("Data path cannot be empty.")

        self.data_path = Path(data_path)
        self.encoding = encoding
        self.load_kwargs = kwargs

        # Validate file exists
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")

        # Determine file type and loader method
        self.file_type = self._get_file_type()
        self.load_method = self._get_load_method()

        logger.info(f"DataHandler initialized for {self.file_type} file: {self.data_path}")

    def load_data(self) -> pd.DataFrame:
        """
        Load data using the appropriate method based on file type.

        Returns:
            pd.DataFrame: Loaded data

        Raises:
            FileNotFoundError: If file doesn't exist
            pd.errors.EmptyDataError: If file is empty
            Exception: For other loading errors
        """
        try:
            logger.info(f"Loading data from: {self.data_path}")
            data = self.load_method()

            # Validate loaded data
            if data.empty:
                logger.warning("Loaded data is empty")
            else:
                logger.info(f"Successfully loaded {len(data):,} rows, {len(data.columns)} columns")

            return data

        except FileNotFoundError:
            logger.error(f"File not found: {self.data_path}")
            raise
        except pd.errors.EmptyDataError:
            logger.error(f"File is empty: {self.data_path}")
            raise
        except pd.errors.ParserError as e:
            logger.error(f"Error parsing file {self.data_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading {self.data_path}: {e}")
            raise

    def get_data_info(self) -> Dict[str, Union[int, str, list]]:
        """
        Get basic information about the data file.

        Returns:
            Dict with file info: size, type, columns (if loaded)
        """
        info = {
            'file_path': str(self.data_path),
            'file_type': self.file_type,
            'file_size_mb': round(self.data_path.stat().st_size / (1024 * 1024), 2),
            'encoding': self.encoding
        }

        try:
            # Try to get column info without loading full data
            if self.file_type == 'csv':
                sample_data = pd.read_csv(self.data_path, nrows=1, encoding=self.encoding)
                info['columns'] = sample_data.columns.tolist()
                info['column_count'] = len(sample_data.columns)
        except Exception as e:
            logger.warning(f"Could not retrieve column info: {e}")

        return info

    def _get_file_type(self) -> str:
        """
        Determine file type from extension.

        Returns:
            str: File type (csv, json, xlsx, etc.)

        Raises:
            ValueError: If file type not supported
        """
        suffix = self.data_path.suffix.lower().lstrip('.')

        if suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file format: {suffix}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        return suffix

    def _get_load_method(self):
        """
        Get the appropriate pandas loading method for the file type.

        Returns:
            Callable: Pandas reading function
        """
        method_map = {
            'csv': self._load_csv,
            'json': self._load_json,
            'xlsx': self._load_excel,
            'xls': self._load_excel,
            'parquet': self._load_parquet
        }
        return method_map[self.file_type]

    def _load_csv(self) -> pd.DataFrame:
        """Load CSV file with proper encoding and error handling."""
        default_params = {
            'encoding': self.encoding,
            'low_memory': False,  # Avoid mixed type warnings
        }
        # Merge with user-provided parameters
        params = {**default_params, **self.load_kwargs}
        return pd.read_csv(self.data_path, **params)

    def _load_json(self) -> pd.DataFrame:
        """Load JSON file."""
        default_params = {
            'encoding': self.encoding,
            'lines': True  # Assume JSON Lines format by default
        }
        params = {**default_params, **self.load_kwargs}
        return pd.read_json(self.data_path, **params)

    def _load_excel(self) -> pd.DataFrame:
        """Load Excel file (.xlsx, .xls)."""
        default_params = {
            'engine': 'openpyxl' if self.file_type == 'xlsx' else 'xlrd'
        }
        params = {**default_params, **self.load_kwargs}
        return pd.read_excel(self.data_path, **params)

    def _load_parquet(self) -> pd.DataFrame:
        """Load Parquet file."""
        return pd.read_parquet(self.data_path, **self.load_kwargs)

    @staticmethod
    def save_data(data: pd.DataFrame, file_path: Union[str, Path],
                  file_type: str = 'csv', **kwargs) -> None:
        """
        Save DataFrame to file with specified format.

        Args:
            data: DataFrame to save
            file_path: Output file path
            file_type: Output format (csv, json, xlsx, parquet)
            **kwargs: Additional parameters for pandas save functions
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        save_methods = {
            'csv': lambda: data.to_csv(file_path, index=False, **kwargs),
            'json': lambda: data.to_json(file_path, orient='records', **kwargs),
            'xlsx': lambda: data.to_excel(file_path, index=False, **kwargs),
            'parquet': lambda: data.to_parquet(file_path, **kwargs)
        }

        if file_type not in save_methods:
            raise ValueError(f"Unsupported save format: {file_type}")

        save_methods[file_type]()
        logger.info(f"Data saved to {file_path} ({file_type} format)")