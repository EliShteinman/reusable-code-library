# ============================================================================
# shared-utilities/kafka/__init__.py - CLEAN IMPORTS
# ============================================================================
"""
Kafka Utils - ערכת כלים פשוטה לעבודה עם Apache Kafka

מבנה:
- לקוחות סינכרוניים ואסינכרוניים
- 3 פונקציות עזר ל-JSON
- 2 מתודות עיקריות לכל Consumer: listen_forever, get_new_messages
"""

# Synchronous clients
from .sync_client import KafkaProducerSync, KafkaConsumerSync

# Asynchronous clients
from .async_client import KafkaProducerAsync, KafkaConsumerAsync

# JSON helpers
from .json_helpers import serialize_json, deserialize_json, create_kafka_message

__all__ = [
    # Synchronous
    'KafkaProducerSync',
    'KafkaConsumerSync',

    # Asynchronous
    'KafkaProducerAsync',
    'KafkaConsumerAsync',

    # JSON helpers
    'serialize_json',
    'deserialize_json',
    'create_kafka_message'
]

# גרסה
__version__ = "1.0.0"

# הגדרות ברירת מחדל
DEFAULT_BOOTSTRAP_SERVERS = "localhost:9092"
DEFAULT_GROUP_ID = "default_group"