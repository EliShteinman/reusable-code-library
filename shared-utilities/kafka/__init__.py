# ============================================================================
# shared-utilities/kafka/__init__.py - FIXED VERSION
# ============================================================================
"""
Kafka utilities - CLEAN ARCHITECTURE
Connection clients handle ONLY connections and raw kafka operations
Repositories handle ONLY high-level messaging patterns
"""

from .kafka_sync_client import KafkaSyncProducer, KafkaSyncConsumer
from .kafka_async_client import KafkaAsyncProducer, KafkaAsyncConsumer
from .kafka_repository import KafkaRepository

__all__ = [
    'KafkaSyncProducer',  # Sync producer connections only
    'KafkaSyncConsumer',  # Sync consumer connections only
    'KafkaAsyncProducer',  # Async producer connections only
    'KafkaAsyncConsumer',  # Async consumer connections only
    'KafkaRepository'  # High-level messaging patterns only
]


# Quick factory functions
def create_sync_producer(bootstrap_servers: str, **kwargs) -> KafkaSyncProducer:
    """Create sync producer."""
    return KafkaSyncProducer(bootstrap_servers, **kwargs)


def create_sync_consumer(topics: List[str],
                         bootstrap_servers: str,
                         group_id: str,
                         auto_commit: bool = True,
                         **kwargs) -> KafkaSyncConsumer:
    """Create sync consumer."""
    return KafkaSyncConsumer(
        topics=topics,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_commit=auto_commit,
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


def create_repository(producer, consumer=None) -> KafkaRepository:
    """Create Kafka repository."""
    return KafkaRepository(producer, consumer)


# Quick setup functions
def setup_kafka_sync(bootstrap_servers: str,
                     producer_topics: List[str] = None,
                     consumer_topics: List[str] = None,
                     group_id: str = None):
    """Quick setup: sync producer + consumer + repository."""
    producer = create_sync_producer(bootstrap_servers)

    consumer = None
    if consumer_topics and group_id:
        consumer = create_sync_consumer(consumer_topics, bootstrap_servers, group_id)

    repo = create_repository(producer, consumer)
    return producer, consumer, repo


async def setup_kafka_async(bootstrap_servers: str,
                            producer_topics: List[str] = None,
                            consumer_topics: List[str] = None,
                            group_id: str = None):
    """Quick setup: async producer + consumer + repository."""
    producer = await create_async_producer(bootstrap_servers)

    consumer = None
    if consumer_topics and group_id:
        consumer = await create_async_consumer(consumer_topics, bootstrap_servers, group_id)

    repo = create_repository(producer, consumer)
    return producer, consumer, repo



