
# ============================================================================
# shared-utilities/kafka/kafka_repository.py - HIGH-LEVEL PATTERNS ONLY
# ============================================================================
import logging
from typing import Any, Dict, List, Optional, Union, Callable

logger = logging.getLogger(__name__)


class KafkaRepository:
    """
    Kafka repository - HIGH-LEVEL MESSAGING PATTERNS ONLY
    Works with both sync and async clients
    """

    def __init__(self,
                 producer: Union[KafkaSyncProducer, KafkaAsyncProducer],
                 consumer: Union[KafkaSyncConsumer, KafkaAsyncConsumer] = None):
        self.producer = producer
        self.consumer = consumer
        self.is_async = hasattr(producer, '_started')  # Detect async producer

    # HIGH-LEVEL PRODUCER PATTERNS
    def send_message(self, topic: str, message: Any, key: str = None):
        """Send single message (sync)."""
        if self.is_async:
            raise RuntimeError("Use send_message_async for async producer")

        return self.producer.send_raw(topic, message, key)

    def send_batch(self, topic: str, messages: List[Any]):
        """Send multiple messages (sync)."""
        if self.is_async:
            raise RuntimeError("Use send_batch_async for async producer")

        # Convert simple list to message format
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, dict) and ('value' in msg or 'key' in msg):
                formatted_messages.append(msg)
            else:
                formatted_messages.append({'value': msg})

        return self.producer.send_batch_raw(topic, formatted_messages)

    def send_event(self, topic: str, event_type: str, data: Dict[str, Any], key: str = None):
        """Send structured event message (sync)."""
        if self.is_async:
            raise RuntimeError("Use send_event_async for async producer")

        event_message = {
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        return self.producer.send_raw(topic, event_message, key)

    # HIGH-LEVEL CONSUMER PATTERNS  
    def poll_messages(self, timeout_ms: int = 1000, max_records: int = 500):
        """Poll for messages (sync)."""
        if self.is_async:
            raise RuntimeError("Use poll_messages_async for async consumer")

        if not self.consumer:
            raise ValueError("No consumer configured")

        return self.consumer.poll_raw(timeout_ms, max_records)

    def process_messages(self,
                         message_handler: Callable[[Any], bool],
                         timeout_ms: int = 1000,
                         auto_commit: bool = True):
        """Process messages with handler (sync)."""
        if self.is_async:
            raise RuntimeError("Use process_messages_async for async consumer")

        if not self.consumer:
            raise ValueError("No consumer configured")

        messages = self.consumer.poll_raw(timeout_ms)

        for message in messages:
            try:
                success = message_handler(message.value)

                # Manual commit if auto_commit disabled and processing succeeded
                if not auto_commit and success:
                    self.consumer.commit_raw(message)

            except Exception as e:
                logger.error(f"Error processing message: {e}")

    def consume_continuously(self,
                             message_handler: Callable[[Any], bool],
                             max_empty_polls: int = 10,
                             auto_commit: bool = True):
        """Continuous message consumption (sync)."""
        if self.is_async:
            raise RuntimeError("Use consume_continuously_async for async consumer")

        if not self.consumer:
            raise ValueError("No consumer configured")

        empty_poll_count = 0

        while empty_poll_count < max_empty_polls:
            messages = self.consumer.poll_raw(timeout_ms=1000)

            if not messages:
                empty_poll_count += 1
                time.sleep(0.1)
                continue

            empty_poll_count = 0

            for message in messages:
                try:
                    success = message_handler(message.value)

                    if not auto_commit and success:
                        self.consumer.commit_raw(message)

                except Exception as e:
                    logger.error(f"Error processing message: {e}")

    # ASYNC HIGH-LEVEL PATTERNS
    async def send_message_async(self, topic: str, message: Any, key: str = None):
        """Send single message (async)."""
        if not self.is_async:
            raise RuntimeError("Use send_message for sync producer")

        return await self.producer.send_raw(topic, message, key)

    async def send_batch_async(self, topic: str, messages: List[Any]):
        """Send multiple messages (async)."""
        if not self.is_async:
            raise RuntimeError("Use send_batch for sync producer")

        formatted_messages = []
        for msg in messages:
            if isinstance(msg, dict) and ('value' in msg or 'key' in msg):
                formatted_messages.append(msg)
            else:
                formatted_messages.append({'value': msg})

        return await self.producer.send_batch_raw(topic, formatted_messages)

    async def send_event_async(self, topic: str, event_type: str, data: Dict[str, Any], key: str = None):
        """Send structured event message (async)."""
        if not self.is_async:
            raise RuntimeError("Use send_event for sync producer")

        event_message = {
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        return await self.producer.send_raw(topic, event_message, key)

    async def poll_messages_async(self, timeout_ms: int = 1000, max_records: int = 500):
        """Poll for messages (async)."""
        if not self.is_async:
            raise RuntimeError("Use poll_messages for sync consumer")

        if not self.consumer:
            raise ValueError("No consumer configured")

        return await self.consumer.poll_raw(timeout_ms, max_records)

    async def process_messages_async(self,
                                     message_handler: Callable,
                                     timeout_ms: int = 1000,
                                     auto_commit: bool = True):
        """Process messages with async handler."""
        if not self.is_async:
            raise RuntimeError("Use process_messages for sync consumer")

        if not self.consumer:
            raise ValueError("No consumer configured")

        messages = await self.consumer.poll_raw(timeout_ms)

        for message in messages:
            try:
                if asyncio.iscoroutinefunction(message_handler):
                    success = await message_handler(message['value'])
                else:
                    success = message_handler(message['value'])

                if not auto_commit and success:
                    await self.consumer.commit_raw(message)

            except Exception as e:
                logger.error(f"Error processing message: {e}")

    # UTILITY PATTERNS
    def seek_to_beginning(self):
        """Seek consumer to beginning."""
        if not self.consumer:
            raise ValueError("No consumer configured")

        if self.is_async:
            raise RuntimeError("Use seek_to_beginning_async for async consumer")

        self.consumer.seek_to_beginning()

    async def seek_to_beginning_async(self):
        """Seek consumer to beginning (async)."""
        if not self.consumer:
            raise ValueError("No consumer configured")

        if not self.is_async:
            raise RuntimeError("Use seek_to_beginning for sync consumer")

        await self.consumer.seek_to_beginning()

    def commit(self, message):
        """Manual commit (sync)."""
        if not self.consumer:
            raise ValueError("No consumer configured")

        if self.is_async:
            raise RuntimeError("Use commit_async for async consumer")

        return self.consumer.commit_raw(message)

    async def commit_async(self, message):
        """Manual commit (async)."""
        if not self.consumer:
            raise ValueError("No consumer configured")

        if not self.is_async:
            raise RuntimeError("Use commit for sync consumer")

        return await self.consumer.commit_raw(message)
