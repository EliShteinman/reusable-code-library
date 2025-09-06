# shared-utilities/kafka/kafka_async_client.py (Enhanced version of existing)
import asyncio
import datetime
import json
import logging
from typing import Any, AsyncIterator, Tuple, Sequence

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
    """Enhanced async Kafka producer."""

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

    async def send_message(self, topic: str, obj: Any, key: str = None) -> bool:
        """Send single message with error handling."""
        if not self._started:
            raise RuntimeError("Kafka producer is not started")

        try:
            await self._producer.send_and_wait(topic, value=obj, key=key)
            logger.debug(f"Message sent to {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {topic}: {e}")
            return False

    async def send_batch(self, topic: str, messages: list) -> dict:
        """Send multiple messages."""
        success_count = 0
        error_count = 0

        for msg in messages:
            if isinstance(msg, dict):
                value = msg.get('value')
                key = msg.get('key')
            else:
                value = msg
                key = None

            if await self.send_message(topic, value, key):
                success_count += 1
            else:
                error_count += 1

        return {'success_count': success_count, 'error_count': error_count}


class KafkaAsyncConsumer:
    """Enhanced async Kafka consumer with manual control options."""

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
        self.group_id = group_id

    async def start(self):
        if not self._started:
            await self._consumer.start()
            self._started = True

    async def stop(self):
        if self._started:
            await self._consumer.stop()
            self._started = False

    async def consume_continuously(self) -> AsyncIterator[Tuple[str, Any]]:
        """Continuous message consumption."""
        if not self._started:
            raise RuntimeError("Kafka consumer is not started")

        async for msg in self._consumer:
            yield msg.topic, msg.value

    async def poll_batch(self, timeout_ms: int = 1000, max_records: int = 500) -> list:
        """Manual polling - get batch of messages."""
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

    async def commit_message(self, message: dict) -> bool:
        """Manual commit for specific message."""
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