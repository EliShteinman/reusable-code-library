# shared-utilities/kafka/__init__.py
"""
Kafka utilities for message streaming and processing.
"""
from typing import List

from .kafka_sync_client import KafkaSyncProducer, KafkaSyncConsumer
from .kafka_async_client import KafkaAsyncProducer, KafkaAsyncConsumer
from .kafka_repository import KafkaRepository

# Keep the existing client for backward compatibility
from .kafka_client import KafkaProducer, KafkaConsumer

__all__ = [
    'KafkaSyncProducer',
    'KafkaSyncConsumer',
    'KafkaAsyncProducer',
    'KafkaAsyncConsumer',
    'KafkaRepository',
    'KafkaProducer',  # Existing async
    'KafkaConsumer'  # Existing async
]


# Factory functions
def create_sync_producer(bootstrap_servers: str, **kwargs) -> KafkaSyncProducer:
    """Create sync producer."""
    return KafkaSyncProducer(bootstrap_servers, **kwargs)


def create_sync_consumer(topics: List[str],
                         bootstrap_servers: str,
                         group_id: str,
                         auto_commit: bool = True,
                         auto_poll: bool = True,
                         **kwargs) -> KafkaSyncConsumer:
    """Create sync consumer with control options."""
    return KafkaSyncConsumer(
        topics=topics,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_commit=auto_commit,
        auto_poll=auto_poll,
        **kwargs
    )


async def create_async_producer(bootstrap_servers: str, **kwargs) -> KafkaAsyncProducer:
    """Create and start async producer."""
    producer = KafkaAsyncProducer(bootstrap_servers, **kwargs)
    await producer.start()
    return producer


async def create_async_consumer(topics: List[str],
                                bootstrap_servers: str,
                                group_id: str,
                                auto_commit: bool = True,
                                **kwargs) -> KafkaAsyncConsumer:
    """Create and start async consumer."""
    consumer = KafkaAsyncConsumer(
        topics=topics,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_commit=auto_commit,
        **kwargs
    )
    await consumer.start()
    return consumer


def create_manual_consumer(topics: List[str],
                           bootstrap_servers: str,
                           group_id: str) -> KafkaSyncConsumer:
    """Create consumer with manual polling and manual commit."""
    return create_sync_consumer(
        topics=topics,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_commit=False,  # Manual commit
        auto_poll=False  # Manual polling
    )


def create_repository(producer, consumer=None) -> KafkaRepository:
    """Create Kafka repository."""
    return KafkaRepository(producer, consumer)


# Usage examples
def example_manual_control():
    """
    Example of manual polling and manual commit - what you requested!
    """

    # Create producer
    producer = create_sync_producer("localhost:9092")

    # Create consumer with MANUAL CONTROL
    consumer = create_manual_consumer(
        topics=["test-topic"],
        bootstrap_servers="localhost:9092",
        group_id="manual-group"
    )

    # Send some messages
    for i in range(10):
        producer.send_message("test-topic", {"id": i, "data": f"message {i}"})

    # MANUAL POLLING - only when you want
    print("Polling for messages...")
    messages = consumer.poll_messages(timeout_ms=5000, max_records=5)

    for msg in messages:
        print(f"Processing message: {msg.value}")

        # Process your message here
        success = process_message(msg.value)  # Your processing logic

        # MANUAL COMMIT - only if processing succeeded
        if success:
            if consumer.commit_message(msg):
                print(f"✅ Committed message offset {msg.offset}")
            else:
                print(f"❌ Failed to commit message offset {msg.offset}")
        else:
            print(f"⚠️ Skipping commit for failed message {msg.offset}")

    # Check pending commits
    pending = consumer.get_pending_commits_count()
    print(f"Pending commits: {pending}")

    # Cleanup
    producer.close()
    consumer.close()


async def example_async_manual_control():
    """
    Example of async manual control.
    """

    # Create async producer
    producer = await create_async_producer("localhost:9092")

    # Create async consumer with manual commit
    consumer = await create_async_consumer(
        topics=["async-topic"],
        bootstrap_servers="localhost:9092",
        group_id="async-manual-group",
        auto_commit=False  # Manual commit
    )

    # Send messages
    await producer.send_message("async-topic", {"type": "test", "data": "async message"})

    # MANUAL POLLING (async)
    messages = await consumer.poll_batch(timeout_ms=5000, max_records=10)

    for msg in messages:
        print(f"Processing async message: {msg['value']}")

        # Process message
        success = await process_async_message(msg['value'])  # Your async processing

        # MANUAL COMMIT (async)
        if success:
            if await consumer.commit_message(msg):
                print(f"✅ Committed async message offset {msg['offset']}")
        else:
            print(f"⚠️ Skipping commit for failed async message")

    # Cleanup
    await producer.stop()
    await consumer.stop()


def example_repository_pattern():
    """
    Example using repository pattern for cleaner code.
    """

    # Setup
    producer = create_sync_producer("localhost:9092")
    consumer = create_manual_consumer(
        topics=["repo-topic"],
        bootstrap_servers="localhost:9092",
        group_id="repo-group"
    )

    # Create repository
    repo = create_repository(producer, consumer)

    # Send messages through repository
    repo.send("repo-topic", {"message": "Hello from repository!"})

    # Poll messages through repository
    messages = repo.poll(timeout_ms=3000)

    for msg in messages:
        print(f"Repository message: {msg.value}")
        # Process and commit
        if process_message(msg.value):
            repo.commit(msg)

    # Cleanup
    producer.close()
    consumer.close()


# Helper functions for examples
def process_message(message_value):
    """Dummy message processing function."""
    # Your message processing logic here
    print(f"Processing: {message_value}")
    return True  # Assume success


async def process_async_message(message_value):
    """Dummy async message processing function."""
    # Your async message processing logic here
    print(f"Async processing: {message_value}")
    await asyncio.sleep(0.1)  # Simulate async work
    return True  # Assume success


if __name__ == "__main__":
    # Test manual control
    example_manual_control()

    # Test repository pattern
    example_repository_pattern()

    # Test async manual control
    import asyncio

    asyncio.run(example_async_manual_control())