# shared-utilities/kafka/kafka_client.py
import asyncio
import datetime
import json
import logging
from typing import Any, AsyncIterator, Tuple, Sequence

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

logger = logging.getLogger(__name__)


# --- Private helper functions for serialization ---
def _json_default_handler(obj):
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _default_json_serializer(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, default=_json_default_handler).encode("utf-8")


def _kafka_json_deserializer(data: bytes):
    return json.loads(data.decode("utf-8")) if data else None


# --- Public Classes ---
class KafkaProducer:
    """A simple, ready-to-use Kafka producer wrapper."""

    def __init__(self, bootstrap_servers: str, acks=1):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=_default_json_serializer,
            acks=acks,
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

    async def send_json(self, topic: str, obj: Any):
        if not self._started:
            raise RuntimeError("Kafka producer is not started")
        return await self._producer.send_and_wait(topic, value=obj)


class KafkaConsumer:
    """A simple, ready-to-use Kafka consumer wrapper that yields messages."""

    def __init__(self, topics: Sequence[str], bootstrap_servers: str, group_id: str):
        self._consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            value_deserializer=_kafka_json_deserializer,
        )
        self._started = False

    async def start(self):
        if not self._started:
            await self._consumer.start()
            self._started = True

    async def stop(self):
        if self._started:
            await self._consumer.stop()
            self._started = False

    async def consume(self) -> AsyncIterator[Tuple[str, Any]]:
        """Consume messages as an async iterator."""
        if not self._started:
            raise RuntimeError("Kafka consumer is not started")

        async for msg in self._consumer:
            yield msg.topic, msg.value