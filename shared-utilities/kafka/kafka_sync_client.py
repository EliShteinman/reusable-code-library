# ============================================================================
# shared-utilities/kafka/kafka_sync_client.py - CONNECTIONS ONLY
# ============================================================================
import json
import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from kafka import KafkaConsumer as SyncKafkaConsumer
from kafka import KafkaProducer as SyncKafkaProducer
from kafka.consumer.fetcher import ConsumerRecord

logger = logging.getLogger(__name__)


class KafkaSyncProducer:
    """
    SYNC Kafka producer - CONNECTIONS ONLY
    No high-level patterns - only raw kafka operations
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

    # RAW KAFKA PRODUCER OPERATIONS ONLY
    def send_raw(self, topic: str, value: Any, key: Optional[str] = None) -> bool:
        """Send raw message - core operation."""
        try:
            with self._lock:
                future = self.producer.send(topic, value=value, key=key)
                record_metadata = future.get(timeout=10)  # Wait for confirmation

            logger.debug(f"Message sent to {topic}:{record_metadata.partition} at offset {record_metadata.offset}")
            return True

        except Exception as e:
            logger.error(f"Failed to send message to {topic}: {e}")
            return False

    def send_batch_raw(self, topic: str, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        """Send multiple raw messages."""
        success_count = 0
        error_count = 0

        for msg in messages:
            value = msg.get('value')
            key = msg.get('key')

            if self.send_raw(topic, value, key):
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
    SYNC Kafka consumer - CONNECTIONS ONLY
    No high-level patterns - only raw kafka operations
    """

    def __init__(self,
                 topics: List[str],
                 bootstrap_servers: str,
                 group_id: str,
                 auto_commit: bool = True,
                 **kwargs):
        self.topics = topics
        self.group_id = group_id

    async def start(self):
        if not self._started:
            await self._consumer.start()
            self._started = True

    async def stop(self):
        if self._started:
            await self._consumer.stop()
            self._started = False

    # RAW ASYNC KAFKA CONSUMER OPERATIONS ONLY
    async def poll_raw(self, timeout_ms: int = 1000, max_records: int = 500) -> List[Dict[str, Any]]:
        """Poll for raw messages - core async operation."""
        if not self._started:
            raise RuntimeError("Kafka consumer is not started")

        try:
            messages = []
            end_time = asyncio.get_event_loop().time() + (timeout_ms / 1000)

            while len(messages) < max_records and asyncio.get_event_loop().time() < end_time:
                try:
                    msg = await asyncio.wait_for(
                        self._consumer.__anext__(),
                        timeout=min(1.0, end_time - asyncio.get_event_loop().time())
                    )
                    messages.append({
                        'topic': msg.topic,
                        'partition': msg.partition,
                        'offset': msg.offset,
                        'key': msg.key,
                        'value': msg.value,
                        'timestamp': msg.timestamp,
                        '_raw_msg': msg  # For manual commit
                    })
                except asyncio.TimeoutError:
                    break

            logger.debug(f"Polled {len(messages)} messages")
            return messages

        except Exception as e:
            logger.error(f"Error polling messages: {e}")
            return []

    async def commit_raw(self, message: Dict[str, Any]) -> bool:
        """Manual commit for raw message."""
        if self.auto_commit:
            logger.warning("Auto-commit is enabled, manual commit not needed")
            return True

        try:
            raw_msg = message.get('_raw_msg')
            if raw_msg:
                await self._consumer.commit({
                    raw_msg.partition: raw_msg.offset + 1
                })
                logger.debug(f"Committed offset {raw_msg.offset + 1}")
                return True
            else:
                logger.error("No raw message data for commit")
                return False

        except Exception as e:
            logger.error(f"Failed to commit message: {e}")
            return False

    async def seek_to_beginning(self):
        """Seek to beginning of all partitions."""
        self._consumer.seek_to_beginning()

    async def seek_to_end(self):
        """Seek to end of all partitions."""
        self._consumer.seek_to_end()


