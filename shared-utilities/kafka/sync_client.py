# ============================================================================
# shared-utilities/kafka/sync_client.py - OPTIMIZED VERSION
# ============================================================================
import logging
import time
from typing import Any, List, Optional, Callable, Dict
from datetime import datetime, timedelta

from kafka import KafkaProducer as SyncKafkaProducer
from kafka import KafkaConsumer as SyncKafkaConsumer
from kafka.errors import KafkaError

from .json_helpers import serialize_json, deserialize_json, create_kafka_message

logger = logging.getLogger(__name__)


def _handle_kafka_error(operation: str, topic: str, error: Exception) -> None:
    """פונקציה משותפת לטיפול בשגיאות Kafka"""
    logger.error(f"Failed to {operation} for topic '{topic}': {error}")


class KafkaProducerSync:
    """
    Kafka Producer סינכרוני
    פשוט וישיר לשימוש
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092", **config):
        """
        יצירת Producer סינכרוני

        Args:
            bootstrap_servers: כתובת שרתי Kafka
            **config: הגדרות נוספות
        """
        self.bootstrap_servers = bootstrap_servers

        default_config = {
            'bootstrap_servers': [bootstrap_servers],
            'value_serializer': lambda x: serialize_json(x).encode('utf-8'),
            'key_serializer': lambda x: x.encode('utf-8') if x else None,
            'acks': 'all',  # המתן לאישור מכל השרתים
            'retries': 3,  # ניסיונות חוזרים
            'max_in_flight_requests_per_connection': 1  # סדר הודעות
        }
        default_config.update(config)

        try:
            self.producer = SyncKafkaProducer(**default_config)
            logger.info("Sync Kafka Producer created successfully")
        except Exception as e:
            _handle_kafka_error("create producer", "N/A", e)
            raise

    def send_message(self, topic: str, message: Any, key: Optional[str] = None, timeout: int = 10) -> bool:
        """
        שליחת הודעה יחידה

        Args:
            topic: שם ה-topic
            message: ההודעה לשליחה
            key: מפתח אופציונלי
            timeout: זמן המתנה לאישור (שניות)

        Returns:
            True אם ההודעה נשלחה בהצלחה
        """
        try:
            # יצירת הודעה מובנית
            kafka_message = create_kafka_message(topic, message, key)

            # שליחה
            future = self.producer.send(topic, value=kafka_message, key=key)
            result = future.get(timeout=timeout)

            logger.info(f"Message sent to '{topic}': {kafka_message['message_id']}")
            return True

        except Exception as e:
            _handle_kafka_error("send message", topic, e)
            return False

    def send_batch(self, topic: str, messages: List[Any], keys: Optional[List[str]] = None) -> int:
        """
        שליחת מספר הודעות

        Args:
            topic: שם ה-topic
            messages: רשימת הודעות
            keys: רשימת מפתחות (אופציונלי)

        Returns:
            מספר ההודעות שנשלחו בהצלחה
        """
        successful_sends = 0

        for i, message in enumerate(messages):
            key = keys[i] if keys and i < len(keys) else None
            success = self.send_message(topic, message, key)
            if success:
                successful_sends += 1

        logger.info(f"Batch send: {successful_sends}/{len(messages)} messages sent to '{topic}'")
        return successful_sends

    def close(self):
        """סגירת ה-Producer"""
        try:
            self.producer.close()
            logger.info("Kafka Producer closed")
        except Exception as e:
            logger.error(f"Error closing Producer: {e}")


class KafkaConsumerSync:
    """
    Kafka Consumer סינכרוני
    עם 3 מתודות עיקריות: האזנה תמידית, קריאת עדכונים, וconsume generator
    """

    def __init__(self,
                 topics: List[str],
                 bootstrap_servers: str = "localhost:9092",
                 group_id: str = "default_group",
                 **config):
        """
        יצירת Consumer סינכרוני

        Args:
            topics: רשימת topics לעקוב אחריהם
            bootstrap_servers: כתובת שרתי Kafka
            group_id: מזהה קבוצת הconsumers
            **config: הגדרות נוספות
        """
        self.topics = topics
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.last_check_time = None

        default_config = {
            'bootstrap_servers': [bootstrap_servers],
            'group_id': group_id,
            'value_deserializer': lambda x: deserialize_json(x.decode('utf-8')),
            'key_deserializer': lambda x: x.decode('utf-8') if x else None,
            'auto_offset_reset': 'latest',  # התחל מההודעות החדשות
            'enable_auto_commit': True,
            'consumer_timeout_ms': 1000  # timeout לget_new_messages
        }
        default_config.update(config)

        try:
            self.consumer = SyncKafkaConsumer(*topics, **default_config)
            self.last_check_time = datetime.now()
            logger.info(f"Sync Kafka Consumer created for topics: {topics}")
        except Exception as e:
            _handle_kafka_error("create consumer", str(topics), e)
            raise

    def _create_message_data(self, message) -> Dict:
        """יצירת dictionary של נתוני הודעה - פונקציה משותפת"""
        return {
            'topic': message.topic,
            'partition': message.partition,
            'offset': message.offset,
            'key': message.key,
            'value': message.value,
            'timestamp': message.timestamp,
            'received_at': datetime.now().isoformat()
        }

    def listen_forever(self, message_handler: Callable[[Dict], bool], max_messages: Optional[int] = None) -> int:
        """
        האזנה תמידית להודעות עם callback function

        Args:
            message_handler: פונקציה לטיפול בהודעות (message_dict) -> bool
            max_messages: מספר מקסימלי של הודעות (None = אינסופי)

        Returns:
            מספר ההודעות שעובדו בהצלחה
        """
        processed_count = 0
        logger.info("Starting continuous listening...")

        try:
            for message in self.consumer:
                try:
                    # שימוש בפונקציה המשותפת
                    message_data = self._create_message_data(message)
                    success = message_handler(message_data)

                    if success:
                        processed_count += 1
                        logger.debug(f"Processed message from '{message.topic}'")
                    else:
                        logger.warning(f"Failed to process message from '{message.topic}'")

                    # בדיקת מגבלת הודעות
                    if max_messages and processed_count >= max_messages:
                        logger.info(f"Reached max messages limit: {max_messages}")
                        break

                except KeyboardInterrupt:
                    logger.info("Stopping listener (Ctrl+C)")
                    break
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

        except Exception as e:
            _handle_kafka_error("listen forever", str(self.topics), e)

        logger.info(f"Processed {processed_count} messages")
        return processed_count

    def get_new_messages(self, timeout_seconds: int = 5) -> List[Dict]:
        """
        קריאת כל ההודעות החדשות שהתחדשו מאז הפעם הקודמת

        Args:
            timeout_seconds: זמן המתנה מקסימלי לבדיקת הודעות

        Returns:
            רשימת הודעות חדשות
        """
        new_messages = []
        start_time = time.time()

        logger.info("Checking for new messages...")

        try:
            # בדיקת הודעות עד הtimeout
            while (time.time() - start_time) < timeout_seconds:
                message_batch = self.consumer.poll(timeout_ms=1000)

                if not message_batch:
                    break

                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        # שימוש בפונקציה המשותפת
                        message_data = self._create_message_data(message)
                        new_messages.append(message_data)

            # עדכון זמן הבדיקה הקודמת
            self.last_check_time = datetime.now()

        except Exception as e:
            _handle_kafka_error("get new messages", str(self.topics), e)

        logger.info(f"Retrieved {len(new_messages)} new messages")
        return new_messages

    def consume(self):
        """
        צריכת הודעות - generator שמחזיר הודעה אחת בכל קריאה
        לשימוש עם for loop: for message in consumer.consume():

        Yields:
            Dictionary עם topic, key, value או None אם אין הודעה
        """
        try:
            for message in self.consumer:
                # שימוש בפונקציה המשותפת
                yield self._create_message_data(message)

        except Exception as e:
            _handle_kafka_error("consume", str(self.topics), e)
            return

    def close(self):
        """סגירת ה-Consumer"""
        try:
            self.consumer.close()
            logger.info("Kafka Consumer closed")
        except Exception as e:
            logger.error(f"Error closing Consumer: {e}")