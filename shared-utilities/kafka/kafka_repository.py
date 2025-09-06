# shared-utilities/kafka/kafka_repository.py
import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class KafkaRepository:
    """
    High-level repository pattern for Kafka operations.
    Works with both sync and async clients.
    """

    def __init__(self,
                 producer: Union['KafkaSyncProducer', 'KafkaAsyncProducer'],
                 consumer: Union['KafkaSyncConsumer', 'KafkaAsyncConsumer'] = None):
        self.producer = producer
        self.consumer = consumer
        self.is_async = 'async' in str(type(producer)).lower()

    def _handle_async(self, method, *args, **kwargs):
        """Helper to handle both sync and async calls."""
        return method(*args, **kwargs)

    # Producer operations
    def send(self, topic: str, message: Any, key: str = None):
        """Send single message."""
        if hasattr(self.producer, 'send_message'):
            return self._handle_async(self.producer.send_message, topic, message, key)
        else:
            return self._handle_async(self.producer.send_json, topic, message)

    def send_many(self, topic: str, messages: List[Any]):
        """Send multiple messages."""
        return self._handle_async(self.producer.send_batch, topic, messages)

    # Consumer operations (if consumer provided)
    def poll(self, timeout_ms: int = 1000, max_records: int = 500):
        """Poll for messages."""
        if not self.consumer:
            raise ValueError("No consumer configured")

        if hasattr(self.consumer, 'poll_messages'):
            return self._handle_async(self.consumer.poll_messages, timeout_ms, max_records)
        else:
            return self._handle_async(self.consumer.poll_batch, timeout_ms, max_records)

    def consume_stream(self):
        """Get continuous message stream."""
        if not self.consumer:
            raise ValueError("No consumer configured")

        if hasattr(self.consumer, 'consume_continuously'):
            return self._handle_async(self.consumer.consume_continuously)
        else:
            return self.consumer.consume()

    def commit(self, message):
        """Commit message offset."""
        if not self.consumer:
            raise ValueError("No consumer configured")

        return self._handle_async(self.consumer.commit_message, message)

    def seek_to_beginning(self):
        """Seek to beginning."""
        if not self.consumer:
            raise ValueError("No consumer configured")

        return self._handle_async(self.consumer.seek_to_beginning)

    def seek_to_end(self):
        """Seek to end."""
        if not self.consumer:
            raise ValueError("No consumer configured")

        return self._handle_async(self.consumer.seek_to_end)