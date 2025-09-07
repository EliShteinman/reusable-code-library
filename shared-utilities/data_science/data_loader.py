
# ============================================================================
# shared-utilities/data_science/data_loader.py - FILE LOADING ONLY
# ============================================================================
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

import pandas as pd

logger = logging.getLogger(__name__)


class UniversalDataLoader:
    """
    Universal data loader - FILE LOADING ONLY
    Supports all common file formats with automatic detection
    """

    def __init__(self, data_path: Optional[str] = None, encoding: str = "utf-8"):
        self.data_path = data_path
        self.encoding = encoding

        self.supported_formats = {
            '.csv': self._load_csv,
            '.tsv': self._load_tsv,
            '.json': self._load_json,
            '.jsonl': self._load_jsonlines,
            '.xlsx': self._load_excel,
            '.xls': self._load_excel,
            '.parquet': self._load_parquet,
            '.txt': self._load_text,
            '.html': self._load_html,
            '.xml': self._load_xml
        }

    def load_data(self, path: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """Load data from file with automatic format detection."""
        current_path = path or self.data_path
        if not current_path:
            raise ValueError("No data path provided")

        path_obj = Path(current_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {current_path}")

        file_extension = path_obj.suffix.lower()
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported format: {file_extension}")

        logger.info(f"Loading {file_extension} file: {current_path}")
        loader_func = self.supported_formats[file_extension]

        try:
            df = loader_func(current_path, **kwargs)
            logger.info(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"Failed to load {current_path}: {e}")
            raise

    def _load_csv(self, path: str, **kwargs) -> pd.DataFrame:
        """Load CSV file."""
        defaults = {'encoding': self.encoding, 'low_memory': False}
        defaults.update(kwargs)
        return pd.read_csv(path, **defaults)

    def _load_tsv(self, path: str, **kwargs) -> pd.DataFrame:
        """Load TSV file."""
        defaults = {'encoding': self.encoding, 'sep': '\t', 'low_memory': False}
        defaults.update(kwargs)
        return pd.read_csv(path, **defaults)

    def _load_json(self, path: str, **kwargs) -> pd.DataFrame:
        """Load JSON file."""
        defaults = {'encoding': self.encoding}
        defaults.update(kwargs)

        with open(path, 'r', encoding=defaults['encoding']) as f:
            data = json.load(f)

        if isinstance(data, list):
            return pd.json_normalize(data)
        elif isinstance(data, dict):
            return pd.json_normalize([data])
        else:
            return pd.DataFrame([data])

    def _load_jsonlines(self, path: str, **kwargs) -> pd.DataFrame:
        """Load JSON Lines file."""
        defaults = {'encoding': self.encoding, 'lines': True}
        defaults.update(kwargs)
        return pd.read_json(path, **defaults)

    def _load_excel(self, path: str, **kwargs) -> pd.DataFrame:
        """Load Excel file."""
        defaults = {'engine': 'openpyxl'}
        defaults.update(kwargs)
        return pd.read_excel(path, **defaults)

    def _load_parquet(self, path: str, **kwargs) -> pd.DataFrame:
        """Load Parquet file."""
        return pd.read_parquet(path, **kwargs)

    def _load_text(self, path: str, **kwargs) -> pd.DataFrame:
        """Load text file (one line per row)."""
        col_name = kwargs.get('column_name', 'text')
        with open(path, 'r', encoding=self.encoding) as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        return pd.DataFrame(lines, columns=[col_name])

    def _load_html(self, path: str, **kwargs) -> pd.DataFrame:
        """Load HTML table."""
        defaults = {'encoding': self.encoding}
        defaults.update(kwargs)
        tables = pd.read_html(path, **defaults)
        return tables[0] if tables else pd.DataFrame()

    def _load_xml(self, path: str, **kwargs) -> pd.DataFrame:
        """Load XML file."""
        defaults = {'encoding': self.encoding}
        defaults.update(kwargs)
        return pd.read_xml(path, **defaults)

    def load_lines_as_list(self, path: Optional[str] = None, strip_empty: bool = True) -> List[str]:
        """Load text file as list of strings."""
        current_path = path or self.data_path
        if not current_path:
            raise ValueError("No data path provided")

        with open(current_path, 'r', encoding=self.encoding) as f:
            lines = [line.strip() for line in f.readlines()]

        if strip_empty:
            lines = [line for line in lines if line]

        return lines

    def save_data(self, df: pd.DataFrame, path: str, **kwargs):
        """Save DataFrame to file with format auto-detection."""
        path_obj = Path(path)
        file_extension = path_obj.suffix.lower()

        save_methods = {
            '.csv': lambda: df.to_csv(path, index=False, **kwargs),
            '.json': lambda: df.to_json(path, orient='records', **kwargs),
            '.xlsx': lambda: df.to_excel(path, index=False, **kwargs),
            '.parquet': lambda: df.to_parquet(path, **kwargs),
            '.tsv': lambda: df.to_csv(path, sep='\t', index=False, **kwargs)
        }

        if file_extension not in save_methods:
            raise ValueError(f"Unsupported save format: {file_extension}")

        path_obj.parent.mkdir(parents=True, exist_ok=True)
        save_methods[file_extension]()
        logger.info(f"Data saved to {path}")

    def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get information about a file."""
        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path}")

        info = {
            'filename': path_obj.name,
            'extension': path_obj.suffix.lower(),
            'size_bytes': path_obj.stat().st_size,
            'size_mb': round(path_obj.stat().st_size / (1024 * 1024), 2),
            'supported': path_obj.suffix.lower() in self.supported_formats
        }

        # Try to get preview for supported formats
        if info['supported']:
            try:
                df = self.load_data(path)
                info.update({
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': list(df.columns),
                    'dtypes': df.dtypes.to_dict()
                })
            except Exception as e:
                info['load_error'] = str(e)

        return info