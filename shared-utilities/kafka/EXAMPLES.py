

# ============================================================================
# USAGE EXAMPLES - CLEAN SEPARATION
# ============================================================================
import time
import datetime


def example_sync_manual_control():
    """Example: Manual polling and manual commit (sync)."""

    # 1. Create CONNECTION clients
    producer = create_sync_producer("localhost:9092")
    consumer = create_sync_consumer(
        topics=["test-topic"],
        bootstrap_servers="localhost:9092",
        group_id="manual-group",
        auto_commit=False  # Manual commit
    )

    # 2. Create REPOSITORY for high-level patterns
    repo = create_repository(producer, consumer)

    # 3. Send some test messages
    for i in range(10):
        repo.send_message("test-topic", {"id": i, "data": f"message {i}"})

    # 4. MANUAL POLLING - only when you want
    print("Polling for messages...")
    messages = repo.poll_messages(timeout_ms=5000, max_records=5)

    for msg in messages:
        print(f"Processing message: {msg.value}")

        # Your processing logic here
        success = process_message(msg.value)

        # MANUAL COMMIT - only if processing succeeded
        if success:
            if repo.commit(msg):
                print(f"✅ Committed message offset {msg.offset}")
            else:
                print(f"❌ Failed to commit message offset {msg.offset}")
        else:
            print(f"⚠️ Skipping commit for failed message {msg.offset}")

    # 5. Check pending commits
    if hasattr(consumer, 'get_pending_commits_count'):
        pending = consumer.get_pending_commits_count()
        print(f"Pending commits: {pending}")

    # 6. Cleanup
    producer.close()
    consumer.close()


def example_sync_auto_processing():
    """Example: Automatic message processing (sync)."""

    producer, consumer, repo = setup_kafka_sync(
        bootstrap_servers="localhost:9092",
        consumer_topics=["auto-topic"],
        group_id="auto-group"
    )

    # Send some events
    for i in range(5):
        repo.send_event(
            topic="auto-topic",
            event_type="user_action",
            data={"user_id": i, "action": "login"},
            key=f"user_{i}"
        )

    # Process messages with handler
    def message_handler(message_value):
        print(f"Auto processing: {message_value}")
        return True  # Success

    # Process batch
    repo.process_messages(message_handler, timeout_ms=3000)

    # Or continuous processing
    # repo.consume_continuously(message_handler, max_empty_polls=5)

    producer.close()
    consumer.close()


async def example_async_manual_control():
    """Example: Manual polling and manual commit (async)."""

    # 1. Create async CONNECTION clients
    producer = await create_async_producer("localhost:9092")
    consumer = await create_async_consumer(
        topics=["async-topic"],
        bootstrap_servers="localhost:9092",
        group_id="async-manual-group",
        auto_commit=False  # Manual commit
    )

    # 2. Create REPOSITORY
    repo = create_repository(producer, consumer)

    # 3. Send async messages
    await repo.send_message_async("async-topic", {"type": "test", "data": "async message"})

    # 4. MANUAL POLLING (async)
    messages = await repo.poll_messages_async(timeout_ms=5000, max_records=10)

    for msg in messages:
        print(f"Processing async message: {msg['value']}")

        # Process message
        success = await process_async_message(msg['value'])

        # MANUAL COMMIT (async)
        if success:
            if await repo.commit_async(msg):
                print(f"✅ Committed async message offset {msg['offset']}")
        else:
            print(f"⚠️ Skipping commit for failed async message")

    # 5. Cleanup
    await producer.stop()
    await consumer.stop()


async def example_async_auto_processing():
    """Example: Automatic async message processing."""

    producer, consumer, repo = await setup_kafka_async(
        bootstrap_servers="localhost:9092",
        consumer_topics=["async-auto-topic"],
        group_id="async-auto-group"
    )

    # Send batch of events
    events = [
        {"event_type": "order_created", "order_id": i}
        for i in range(1000, 1010)
    ]
    await repo.send_batch_async("async-auto-topic", events)

    # Process with async handler
    async def async_message_handler(message_value):
        print(f"Async auto processing: {message_value}")
        await asyncio.sleep(0.1)  # Simulate async work
        return True

    await repo.process_messages_async(async_message_handler, timeout_ms=5000)

    await producer.stop()
    await consumer.stop()


def example_event_patterns():
    """Example: Event-driven patterns."""

    producer, consumer, repo = setup_kafka_sync(
        "localhost:9092",
        consumer_topics=["events"],
        group_id="event-processors"
    )

    # Send different event types
    repo.send_event("events", "user_registered", {
        "user_id": 123,
        "email": "user@test.com",
        "signup_source": "web"
    })

    repo.send_event("events", "order_placed", {
        "order_id": 456,
        "user_id": 123,
        "total": 99.99,
        "items": ["laptop", "mouse"]
    })

    repo.send_event("events", "payment_processed", {
        "payment_id": 789,
        "order_id": 456,
        "amount": 99.99,
        "method": "credit_card"
    })

    # Process events by type
    def event_handler(event_data):
        event_type = event_data.get('event_type')
        data = event_data.get('data', {})

        if event_type == "user_registered":
            print(f"New user registered: {data['user_id']}")
        elif event_type == "order_placed":
            print(f"Order placed: {data['order_id']} for ${data['total']}")
        elif event_type == "payment_processed":
            print(f"Payment processed: {data['payment_id']}")

        return True

    repo.process_messages(event_handler, timeout_ms=5000)

    producer.close()
    consumer.close()


# Helper functions for examples
def process_message(message_value):
    """Dummy message processing function."""
    print(f"Processing: {message_value}")
    # Simulate processing that might fail
    return True  # Assume success


async def process_async_message(message_value):
    """Dummy async message processing function."""
    print(f"Async processing: {message_value}")
    await asyncio.sleep(0.1)  # Simulate async work
    return True  # Assume success


if __name__ == "__main__":
    from typing import List
    import asyncio

    print("=== Sync Manual Control ===")
    example_sync_manual_control()

    print("\n=== Sync Auto Processing ===")
    example_sync_auto_processing()

    print("\n=== Event Patterns ===")
    example_event_patterns()

    print("\n=== Async Manual Control ===")
    asyncio.run(example_async_manual_control())

    print("\n=== Async Auto Processing ===")
    asyncio.run(example_async_auto_processing())
    id
    self.auto_commit = auto_commit

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
    logger.info(f"Auto-commit: {auto_commit}")


def _json_deserializer(self, data: bytes) -> Any:
    """Deserialize JSON bytes to object."""
    if data is None:
        return None
    try:
        return json.loads(data.decode('utf-8'))
    except json.JSONDecodeError as e:
        logger.error(f"Failed to deserialize JSON: {e}")
        return None


# RAW KAFKA CONSUMER OPERATIONS ONLY
def poll_raw(self, timeout_ms: int = 1000, max_records: int = 500) -> List[ConsumerRecord]:
    """Poll for raw messages - core operation."""
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


def commit_raw(self, message: ConsumerRecord) -> bool:
    """Manually commit raw message offset."""
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


def get_pending_commits_count(self) -> int:
    """Get number of pending commits."""
    return len(self._pending_commits)


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

