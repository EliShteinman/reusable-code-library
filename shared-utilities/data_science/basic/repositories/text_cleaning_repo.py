# ============================================================================
# shared-utilities/data_science/basic/repositories/text_cleaning_repo.py
# ============================================================================
"""
Text Cleaning Repository - CRUD Operations for Text Cleaning
Handles Create, Read, Update, Delete operations for text cleaning workflows
"""

import re
import string
import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import pandas as pd

from ..clients.text_processor_client import TextProcessorClient

logger = logging.getLogger(__name__)


class TextCleaningRepository:
    """
    Repository for managing text cleaning operations
    Provides CRUD interface for text cleaning workflows
    """

    def __init__(self,
                 client: Optional[TextProcessorClient] = None,
                 auto_save_operations: bool = False):
        """
        Initialize text cleaning repository.

        Args:
            client: Text processor client for operations
            auto_save_operations: Whether to automatically save operation history
        """
        self.client = client or TextProcessorClient()
        self.auto_save_operations = auto_save_operations

        # Operation history storage
        self._operation_history = []
        self._cleaning_configs = {}
        self._cleaning_stats = {}

        logger.info("TextCleaningRepository initialized")

    # ========================================================================
    # CREATE Operations
    # ========================================================================

    def create_cleaning_config(self,
                               config_name: str,
                               config: Dict[str, Any]) -> str:
        """
        Create a new text cleaning configuration.

        Args:
            config_name: Name for the configuration
            config: Cleaning configuration parameters

        Returns:
            Configuration ID
        """
        config_id = f"{config_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Validate configuration
        valid_options = {
            'remove_urls', 'remove_emails', 'remove_mentions', 'remove_hashtags',
            'remove_punctuation', 'to_lowercase', 'remove_extra_whitespace',
            'remove_numbers', 'remove_special_chars', 'custom_replacements',
            'language', 'preserve_patterns'
        }

        # Filter valid options
        validated_config = {k: v for k, v in config.items() if k in valid_options}

        # Add metadata
        config_record = {
            'config_id': config_id,
            'config_name': config_name,
            'config': validated_config,
            'created_at': datetime.now(),
            'usage_count': 0
        }

        self._cleaning_configs[config_id] = config_record

        if self.auto_save_operations:
            self._save_operation('create_config', config_record)

        logger.info(f"Created cleaning configuration: {config_name} (ID: {config_id})")
        return config_id

    def create_cleaning_operation(self,
                                  data: pd.DataFrame,
                                  text_columns: List[str],
                                  config_id: Optional[str] = None,
                                  config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create and execute a text cleaning operation.

        Args:
            data: DataFrame with text data
            text_columns: List of columns to clean
            config_id: ID of existing configuration to use
            config: Direct configuration (if config_id not provided)

        Returns:
            Operation result with cleaned data and metadata
        """
        operation_id = f"clean_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Get configuration
        if config_id:
            if config_id not in self._cleaning_configs:
                raise ValueError(f"Configuration not found: {config_id}")
            cleaning_config = self._cleaning_configs[config_id]['config']
            self._cleaning_configs[config_id]['usage_count'] += 1
        elif config:
            cleaning_config = config
        else:
            # Default configuration
            cleaning_config = {
                'remove_urls': True,
                'remove_emails': True,
                'remove_punctuation': True,
                'to_lowercase': True,
                'remove_extra_whitespace': True
            }

        # Execute cleaning
        start_time = datetime.now()

        try:
            with self.client.create_session() as session:
                cleaned_data = data.copy()

                for col in text_columns:
                    if col not in cleaned_data.columns:
                        logger.warning(f"Column '{col}' not found in DataFrame")
                        continue

                    logger.info(f"Cleaning column: {col}")

                    # Apply cleaning to each text
                    cleaned_data[col] = cleaned_data[col].astype(str).apply(
                        lambda x: session.clean_text(x, **cleaning_config)
                    )

                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                # Calculate statistics
                original_stats = self._calculate_text_stats(data, text_columns)
                cleaned_stats = self._calculate_text_stats(cleaned_data, text_columns)

                operation_result = {
                    'operation_id': operation_id,
                    'config_used': cleaning_config,
                    'config_id': config_id,
                    'columns_processed': text_columns,
                    'original_rows': len(data),
                    'processed_rows': len(cleaned_data),
                    'duration_seconds': duration,
                    'original_stats': original_stats,
                    'cleaned_stats': cleaned_stats,
                    'cleaning_impact': self._calculate_cleaning_impact(original_stats, cleaned_stats),
                    'timestamp': start_time,
                    'cleaned_data': cleaned_data
                }

                # Store operation
                self._operation_history.append(operation_result)
                self._cleaning_stats[operation_id] = operation_result

                if self.auto_save_operations:
                    self._save_operation('clean_text', operation_result)

                logger.info(f"Cleaning operation completed: {operation_id} ({duration:.2f}s)")
                return operation_result

        except Exception as e:
            logger.error(f"Cleaning operation failed: {e}")
            raise

    # ========================================================================
    # READ Operations
    # ========================================================================

    def read_cleaning_config(self, config_id: str) -> Dict[str, Any]:
        """
        Read a cleaning configuration by ID.

        Args:
            config_id: Configuration ID

        Returns:
            Configuration details
        """
        if config_id not in self._cleaning_configs:
            raise ValueError(f"Configuration not found: {config_id}")

        return self._cleaning_configs[config_id].copy()

    def read_all_configs(self) -> List[Dict[str, Any]]:
        """
        Read all cleaning configurations.

        Returns:
            List of all configurations
        """
        return list(self._cleaning_configs.values())

    def read_operation_history(self,
                               limit: Optional[int] = None,
                               config_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Read operation history.

        Args:
            limit: Maximum number of operations to return
            config_id: Filter by configuration ID

        Returns:
            List of operation records
        """
        history = self._operation_history.copy()

        # Filter by config_id if provided
        if config_id:
            history = [op for op in history if op.get('config_id') == config_id]

        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x['timestamp'], reverse=True)

        # Apply limit
        if limit:
            history = history[:limit]

        return history

    def read_cleaning_stats(self, operation_id: str) -> Dict[str, Any]:
        """
        Read cleaning statistics for specific operation.

        Args:
            operation_id: Operation ID

        Returns:
            Operation statistics
        """
        if operation_id not in self._cleaning_stats:
            raise ValueError(f"Operation not found: {operation_id}")

        return self._cleaning_stats[operation_id].copy()

    def read_summary_stats(self) -> Dict[str, Any]:
        """
        Read summary statistics for all operations.

        Returns:
            Summary statistics
        """
        if not self._operation_history:
            return {'total_operations': 0}

        total_operations = len(self._operation_history)
        total_rows_processed = sum(op['processed_rows'] for op in self._operation_history)
        total_duration = sum(op['duration_seconds'] for op in self._operation_history)

        config_usage = {}
        for op in self._operation_history:
            config_id = op.get('config_id', 'direct_config')
            config_usage[config_id] = config_usage.get(config_id, 0) + 1

        return {
            'total_operations': total_operations,
            'total_rows_processed': total_rows_processed,
            'total_duration_seconds': total_duration,
            'average_duration_per_operation': total_duration / total_operations,
            'average_rows_per_operation': total_rows_processed / total_operations,
            'config_usage_frequency': config_usage,
            'most_used_config': max(config_usage.items(), key=lambda x: x[1])[0] if config_usage else None
        }

    # ========================================================================
    # UPDATE Operations
    # ========================================================================

    def update_cleaning_config(self,
                               config_id: str,
                               updated_config: Dict[str, Any]) -> bool:
        """
        Update an existing cleaning configuration.

        Args:
            config_id: Configuration ID to update
            updated_config: New configuration parameters

        Returns:
            Success status
        """
        if config_id not in self._cleaning_configs:
            raise ValueError(f"Configuration not found: {config_id}")

        try:
            # Preserve original metadata
            original_record = self._cleaning_configs[config_id]

            # Update configuration
            original_record['config'].update(updated_config)
            original_record['updated_at'] = datetime.now()

            if self.auto_save_operations:
                self._save_operation('update_config', {
                    'config_id': config_id,
                    'updated_fields': updated_config,
                    'timestamp': datetime.now()
                })

            logger.info(f"Updated cleaning configuration: {config_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update configuration {config_id}: {e}")
            return False

    def update_operation_metadata(self,
                                  operation_id: str,
                                  metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for an operation.

        Args:
            operation_id: Operation ID
            metadata: Metadata to update

        Returns:
            Success status
        """
        if operation_id not in self._cleaning_stats:
            raise ValueError(f"Operation not found: {operation_id}")

        try:
            self._cleaning_stats[operation_id].update(metadata)

            # Also update in history
            for op in self._operation_history:
                if op['operation_id'] == operation_id:
                    op.update(metadata)
                    break

            logger.info(f"Updated operation metadata: {operation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update operation {operation_id}: {e}")
            return False

    # ========================================================================
    # DELETE Operations
    # ========================================================================

    def delete_cleaning_config(self, config_id: str) -> bool:
        """
        Delete a cleaning configuration.

        Args:
            config_id: Configuration ID to delete

        Returns:
            Success status
        """
        if config_id not in self._cleaning_configs:
            raise ValueError(f"Configuration not found: {config_id}")

        try:
            # Check if configuration is in use
            in_use = any(op.get('config_id') == config_id for op in self._operation_history)

            if in_use:
                logger.warning(f"Configuration {config_id} is referenced in operation history")
                # Mark as deleted instead of removing
                self._cleaning_configs[config_id]['deleted'] = True
                self._cleaning_configs[config_id]['deleted_at'] = datetime.now()
            else:
                del self._cleaning_configs[config_id]

            if self.auto_save_operations:
                self._save_operation('delete_config', {
                    'config_id': config_id,
                    'timestamp': datetime.now()
                })

            logger.info(f"Deleted cleaning configuration: {config_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete configuration {config_id}: {e}")
            return False

    def delete_operation_history(self,
                                 operation_ids: Optional[List[str]] = None,
                                 older_than_days: Optional[int] = None) -> int:
        """
        Delete operation history records.

        Args:
            operation_ids: Specific operation IDs to delete
            older_than_days: Delete operations older than N days

        Returns:
            Number of operations deleted
        """
        deleted_count = 0

        try:
            if operation_ids:
                # Delete specific operations
                self._operation_history = [
                    op for op in self._operation_history
                    if op['operation_id'] not in operation_ids
                ]

                for op_id in operation_ids:
                    if op_id in self._cleaning_stats:
                        del self._cleaning_stats[op_id]
                        deleted_count += 1

            elif older_than_days:
                # Delete old operations
                from datetime import timedelta
                cutoff_date = datetime.now() - timedelta(days=older_than_days)

                operations_to_keep = []
                for op in self._operation_history:
                    if op['timestamp'] >= cutoff_date:
                        operations_to_keep.append(op)
                    else:
                        if op['operation_id'] in self._cleaning_stats:
                            del self._cleaning_stats[op['operation_id']]
                        deleted_count += 1

                self._operation_history = operations_to_keep

            if self.auto_save_operations and deleted_count > 0:
                self._save_operation('delete_history', {
                    'deleted_count': deleted_count,
                    'timestamp': datetime.now()
                })

            logger.info(f"Deleted {deleted_count} operation records")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete operation history: {e}")
            return 0

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _calculate_text_stats(self,
                              data: pd.DataFrame,
                              text_columns: List[str]) -> Dict[str, Any]:
        """Calculate text statistics for DataFrame."""
        stats = {}

        for col in text_columns:
            if col not in data.columns:
                continue

            texts = data[col].astype(str)

            # Calculate statistics
            char_lengths = texts.str.len()
            word_counts = texts.str.split().str.len()

            stats[col] = {
                'total_texts': len(texts),
                'average_char_length': char_lengths.mean(),
                'average_word_count': word_counts.mean(),
                'max_char_length': char_lengths.max(),
                'max_word_count': word_counts.max(),
                'empty_texts': (texts == '').sum(),
                'unique_texts': texts.nunique()
            }

        return stats

    def _calculate_cleaning_impact(self,
                                   original_stats: Dict[str, Any],
                                   cleaned_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the impact of cleaning operations."""
        impact = {}

        for col in original_stats:
            if col in cleaned_stats:
                orig = original_stats[col]
                clean = cleaned_stats[col]

                impact[col] = {
                    'char_length_reduction': orig['average_char_length'] - clean['average_char_length'],
                    'char_length_reduction_pct': (
                        (orig['average_char_length'] - clean['average_char_length']) /
                        orig['average_char_length'] * 100
                        if orig['average_char_length'] > 0 else 0
                    ),
                    'word_count_reduction': orig['average_word_count'] - clean['average_word_count'],
                    'empty_texts_created': clean['empty_texts'] - orig['empty_texts'],
                    'unique_texts_lost': orig['unique_texts'] - clean['unique_texts']
                }

        return impact

    def _save_operation(self, operation_type: str, operation_data: Dict[str, Any]):
        """Save operation to persistent storage (placeholder)."""
        # This would save to database or file in real implementation
        logger.debug(f"Saved operation: {operation_type}")

    def clear_all_data(self):
        """Clear all repository data."""
        self._operation_history.clear()
        self._cleaning_configs.clear()
        self._cleaning_stats.clear()
        logger.info("All text cleaning repository data cleared")

    def get_repository_status(self) -> Dict[str, Any]:
        """Get current repository status."""
        return {
            'total_configs': len(self._cleaning_configs),
            'total_operations': len(self._operation_history),
            'client_connected': self.client._connection_active,
            'auto_save_enabled': self.auto_save_operations,
            'supported_languages': self.client.get_supported_languages()
        }