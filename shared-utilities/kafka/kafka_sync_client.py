# shared-utilities/kafka/kafka_sync_client.py
import json
import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from kafka import KafkaConsumer as SyncKafkaConsumer
from kafka import KafkaProducer as SyncKafkaProducer
from kafka.consumer.fetcher import ConsumerRecord

logger = logging.getLogger(__name__)


class KafkaSyncProducer:
    """
    Synchronous Kafka producer with JSON serialization.
    Thread-safe for multiple producers.
    """

    def __init__(self, bootstrap_servers: str, **kwargs):
        producer_config = {
            'bootstrap_servers': bootstrap_servers,
            'value_serializer': self._json_serializer,
            'key_serializer': lambda x: x.encode('utf-8') if x else None,
            'acks': 'all',
            'retries': 3,
            'max_in_flight_requests_per_connection': 1,
            **kwargs
        }

        self.producer = SyncKafkaProducer(**producer_config)
        self._lock = threading.Lock()

    def _json_serializer(self, obj: Any) -> bytes:
        """Serialize object to JSON bytes."""
        return json.dumps(obj, ensure_ascii=False, default=str).encode('utf-8')

    def send_message(self, topic: str, value: Any, key: Optional[str] = None) -> bool:
        """Send message synchronously."""
        try:
            with self._lock:
                future = self.producer.send(topic, value=value, key=key)
                record_metadata = future.get(timeout=10)

            logger.debug(f"Message sent to {topic}:{record_metadata.partition} at offset {record_metadata.offset}")
            return True

        except Exception as e:
            logger.error(f"Failed to send message to {topic}: {e}")
            return False

    def send_batch(self, topic: str, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        """Send multiple messages in batch."""
        success_count = 0
        error_count = 0

        for msg in messages:
            value = msg.get('value')
            key = msg.get('key')

            if self.send_message(topic, value, key):
                success_count += 1
            else:
                error_count += 1

        return {'success_count': success_count, 'error_count': error_count}

    def flush(self, timeout: Optional[float] = None):
        """Flush all buffered messages."""
        self.producer.flush(timeout=timeout)

    def close(self):
        """Close producer and release resources."""
        try:
            self.producer.flush()
            self.producer.close()
        except Exception as e:
            logger.error(f"Error closing producer: {e}")


class KafkaSyncConsumer:
    """
    Synchronous Kafka consumer with manual polling and commit control.
    Enhanced with your requested features: manual polling, manual commit.
    """

    def __init__(self,
                 topics: List[str],
                 bootstrap_servers: str,
                 group_id: str,
                 auto_commit: bool = True,
                 auto_poll: bool = True,
                 **kwargs):
        self.topics = topics
        self.group_id = group_id
        self.auto_commit = auto_commit
        self.auto_poll = auto_poll

        consumer_config = {
            'bootstrap_servers': bootstrap_servers,
            'group_id': group_id,
            'auto_offset_reset': 'earliest',
            'enable_auto_commit': auto_commit,
            'value_deserializer': self._json_deserializer,
            'key_deserializer': lambda x: x.decode('utf-8') if x else None,
            'session_timeout_ms': 30000,
            'heartbeat_interval_ms': 3000,
            **kwargs
        }

        self.consumer = SyncKafkaConsumer(*topics, **consumer_config)
        self._stop_polling = False
        self._lock = threading.Lock()

        # Track messages for manual commit
        self._pending_commits: Dict[Tuple[str, int], int] = {}

        logger.info(f"Kafka consumer initialized for topics {topics}, group: {group_id}")
        logger.info(f"Auto-commit: {auto_commit}, Auto-poll: {auto_poll}")

    def _json_deserializer(self, data: bytes) -> Any:
        """Deserialize JSON bytes to object."""
        if data is None:
            return None
        try:
            return json.loads(data.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to deserialize JSON: {e}")
            return None

    def poll_messages(self, timeout_ms: int = 1000, max_records: int = 500) -> List[ConsumerRecord]:
        """
        MANUAL POLLING: Poll for messages manually (single batch).
        This is what you requested - only poll when explicitly called.
        """
        try:
            message_batch = self.consumer.poll(
                timeout_ms=timeout_ms,
                max_records=max_records
            )

            messages = []
            for topic_partition, records in message_batch.items():
                for record in records:
                    messages.append(record)

                    # Track for manual commit if needed
                    if not self.auto_commit:
                        tp_key = (topic_partition.topic, topic_partition.partition)
                        self._pending_commits[tp_key] = max(
                            self._pending_commits.get(tp_key, -1),
                            record.offset
                        )

            logger.debug(f"Polled {len(messages)} messages")
            return messages

        except Exception as e:
            logger.error(f"Error polling messages: {e}")
            return []

    def consume_continuously(self, message_handler, max_empty_polls: int = 10):
        """
        Continuous polling mode with message handler.
        Only use this if auto_poll=True.
        """
        if not self.auto_poll:
            logger.warning("Auto-poll is disabled, but using continuous mode")

        empty_poll_count = 0

        while not self._stop_polling and empty_poll_count < max_empty_polls:
            messages = self.poll_messages()

            if not messages:
                empty_poll_count += 1
                time.sleep(0.1)
                continue

            empty_poll_count = 0

            for message in messages:
                try:
                    success = message_handler(message)
                    if not success:
                        logger.warning(f"Handler failed for message at offset {message.offset}")

                    # Auto-commit individual message if manual commit mode
                    if not self.auto_commit and success:
                        self.commit_message(message)

                except Exception as e:
                    logger.error(f"Error processing message: {e}")

    def commit_message(self, message: ConsumerRecord) -> bool:
        """
        MANUAL COMMIT: Manually commit a specific message offset.
        This is what you requested - commit only when you approve.
        """
        if self.auto_commit:
            logger.warning("Auto-commit is enabled, manual commit not needed")
            return True

        try:
            from kafka import TopicPartition

            tp = TopicPartition(message.topic, message.partition)
            # Commit offset + 1 (next message to be consumed)
            self.consumer.commit({tp: message.offset + 1})

            # Remove from pending commits
            tp_key = (message.topic, message.partition)
            if tp_key in self._pending_commits:
                if self._pending_commits[tp_key] <= message.offset:
                    del self._pending_commits[tp_key]

            logger.debug(f"Committed offset {message.offset + 1} for {message.topic}:{message.partition}")
            return True

        except Exception as e:
            logger.error(f"Failed to commit message: {e}")
            return False

    def commit_all_pending(self) -> bool:
        """Commit all pending message offsets."""
        if self.auto_commit or not self._pending_commits:
            return True

        try:
            from kafka import TopicPartition

            commit_map = {}
            for (topic, partition), offset in self._pending_commits.items():
                tp = TopicPartition(topic, partition)
                commit_map[tp] = offset + 1

            self.consumer.commit(commit_map)
            self._pending_commits.clear()

            logger.info(f"Committed {len(commit_map)} pending offsets")
            return True

        except Exception as e:
            logger.error(f"Failed to commit pending offsets: {e}")
            return False

    def get_pending_commits_count(self) -> int:
        """Get number of pending commits."""
        return len(self._pending_commits)

    def seek_to_beginning(self, topic: Optional[str] = None):
        """Seek to beginning of partitions."""
        if topic:
            partitions = [tp for tp in self.consumer.assignment() if tp.topic == topic]
        else:
            partitions = self.consumer.assignment()

        self.consumer.seek_to_beginning(*partitions)
        logger.info(f"Seeked to beginning for {len(partitions)} partitions")

    def seek_to_end(self, topic: Optional[str] = None):
        """Seek to end of partitions."""
        if topic:
            partitions = [tp for tp in self.consumer.assignment() if tp.topic == topic]
        else:
            partitions = self.consumer.assignment()

        self.consumer.seek_to_end(*partitions)
        logger.info(f"Seeked to end for {len(partitions)} partitions")

    def get_current_offsets(self) -> Dict[str, Dict[int, int]]:
        """Get current offset position for all assigned partitions."""
        offsets = {}
        for tp in self.consumer.assignment():
            topic = tp.topic
            partition = tp.partition
            current_offset = self.consumer.position(tp)

            if topic not in offsets:
                offsets[topic] = {}
            offsets[topic][partition] = current_offset

        return offsets

    def stop_polling(self):
        """Stop continuous polling."""
        self._stop_polling = True

    def close(self):
        """Close consumer and release resources."""
        try:
            self.stop_polling()

            # Commit pending offsets before closing
            if not self.auto_commit:
                self.commit_all_pending()

            self.consumer.close()
            logger.info("Kafka consumer closed successfully")

        except Exception as e:
            logger.error(f"Error closing consumer: {e}")








