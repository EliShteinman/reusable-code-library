


# ============================================================================
# shared-utilities/kafka/kafka_async_client.py - ASYNC CONNECTIONS ONLY
# ============================================================================
import asyncio
import datetime
import json
import logging
from typing import Any, AsyncIterator, Dict, List, Optional, Sequence

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

logger = logging.getLogger(__name__)


def _json_default_handler(obj):
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _default_json_serializer(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, default=_json_default_handler).encode("utf-8")


def _kafka_json_deserializer(data: bytes):
    return json.loads(data.decode("utf-8")) if data else None


class KafkaAsyncProducer:
    """
    ASYNC Kafka producer - CONNECTIONS ONLY
    No high-level patterns - only raw kafka operations
    """

    def __init__(self, bootstrap_servers: str, acks=1, **kwargs):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=_default_json_serializer,
            acks=acks,
            **kwargs
        )
        self._started = False

    async def start(self):
        if not self._started:
            await self._producer.start()
            self._started = True

    async def stop(self):
        if self._started:
            await self._producer.stop()
            self._started = False

    # RAW ASYNC KAFKA PRODUCER OPERATIONS ONLY
    async def send_raw(self, topic: str, obj: Any, key: str = None) -> bool:
        """Send raw message - core async operation."""
        if not self._started:
            raise RuntimeError("Kafka producer is not started")

        try:
            await self._producer.send_and_wait(topic, value=obj, key=key)
            logger.debug(f"Message sent to {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {topic}: {e}")
            return False

    async def send_batch_raw(self, topic: str, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        """Send multiple raw messages."""
        success_count = 0
        error_count = 0

        for msg in messages:
            if isinstance(msg, dict):
                value = msg.get('value')
                key = msg.get('key')
            else:
                value = msg
                key = None

            if await self.send_raw(topic, value, key):
                success_count += 1
            else:
                error_count += 1

        return {'success_count': success_count, 'error_count': error_count}


class KafkaAsyncConsumer:
    """
    ASYNC Kafka consumer - CONNECTIONS ONLY
    No high-level patterns - only raw kafka operations
    """

    def __init__(self,
                 topics: Sequence[str],
                 bootstrap_servers: str,
                 group_id: str,
                 auto_commit: bool = True,
                 **kwargs):
        self._consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=auto_commit,
            value_deserializer=_kafka_json_deserializer,
            **kwargs
        )
        self._started = False
        self.auto_commit = auto_commit
        self.topics = topics
        self.group_id = group_