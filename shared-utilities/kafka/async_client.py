# ============================================================================
# shared-utilities/kafka/async_client.py - ASYNCHRONOUS KAFKA CLIENT
# ============================================================================
import asyncio
import logging
from typing import Any, List, Optional, Callable, Dict
from datetime import datetime

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError

from .json_helpers import serialize_json, deserialize_json, create_kafka_message

logger = logging.getLogger(__name__)


class KafkaProducerAsync:
    """
    Kafka Producer אסינכרוני
    לשליחת הודעות ב-async/await
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092", **config):
        """
        יצירת Producer אסינכרוני

        Args:
            bootstrap_servers: כתובת שרתי Kafka
            **config: הגדרות נוספות
        """
        self.bootstrap_servers = bootstrap_servers

        default_config = {
            'bootstrap_servers': bootstrap_servers,
            'value_serializer': lambda x: serialize_json(x).encode('utf-8'),
            'key_serializer': lambda x: x.encode('utf-8') if x else None,
            'acks': 'all',
            'retries': 3
        }
        default_config.update(config)

        self.producer = AIOKafkaProducer(**default_config)
        self.is_started = False
        logger.info("Async Kafka Producer created")

    async def start(self):
        """התחלת ה-Producer"""
        if not self.is_started:
            try:
                await self.producer.start()
                self.is_started = True
                logger.info("Async Kafka Producer started")
            except Exception as e:
                logger.error(f"Failed to start Async Producer: {e}")
                raise

    async def stop(self):
        """עצירת ה-Producer"""
        if self.is_started:
            try:
                await self.producer.stop()
                self.is_started = False
                logger.info("Async Kafka Producer stopped")
            except Exception as e:
                logger.error(f"Error stopping Async Producer: {e}")

    async def send_message(self, topic: str, message: Any, key: Optional[str] = None) -> bool:
        """
        שליחת הודעה יחידה (אסינכרונית)

        Args:
            topic: שם ה-topic
            message: ההודעה לשליחה
            key: מפתח אופציונלי

        Returns:
            True אם ההודעה נשלחה בהצלחה
        """
        if not self.is_started:
            logger.error("Producer is not started. Call start() first.")
            return False

        try:
            # יצירת הודעה מובנית
            kafka_message = create_kafka_message(topic, message, key)

            # שליחה אסינכרונית
            await self.producer.send_and_wait(topic, value=kafka_message, key=key)

            logger.info(f"Message sent to '{topic}': {kafka_message['message_id']}")
            return True

        except Exception as e:
            logger.error(f"Failed to send message to '{topic}': {e}")
            return False

    async def send_batch(self, topic: str, messages: List[Any], keys: Optional[List[str]] = None) -> int:
        """
        שליחת מספר הודעות (אסינכרונית)

        Args:
            topic: שם ה-topic
            messages: רשימת הודעות
            keys: רשימת מפתחות (אופציונלי)

        Returns:
            מספר ההודעות שנשלחו בהצלחה
        """
        if not self.is_started:
            logger.error("Producer is not started. Call start() first.")
            return 0

        successful_sends = 0

        # שליחה מקבילה
        tasks = []
        for i, message in enumerate(messages):
            key = keys[i] if keys and i < len(keys) else None
            task = self.send_message(topic, message, key)
            tasks.append(task)

        # המתנה לכל השליחות
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # ספירת הצלחות
        for result in results:
            if result is True:
                successful_sends += 1

        logger.info(f"Async batch send: {successful_sends}/{len(messages)} messages sent to '{topic}'")
        return successful_sends


class KafkaConsumerAsync:
    """
    Kafka Consumer אסינכרוני
    עם 2 מתודות עיקריות: האזנה תמידית וקריאת עדכונים
    """

    def __init__(self,
                 topics: List[str],
                 bootstrap_servers: str = "localhost:9092",
                 group_id: str = "default_group",
                 **config):
        """
        יצירת Consumer אסינכרוני

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
            'bootstrap_servers': bootstrap_servers,
            'group_id': group_id,
            'value_deserializer': lambda x: deserialize_json(x.decode('utf-8')),
            'key_deserializer': lambda x: x.decode('utf-8') if x else None,
            'auto_offset_reset': 'latest'
        }
        default_config.update(config)

        self.consumer = AIOKafkaConsumer(*topics, **default_config)
        self.is_started = False
        logger.info(f"Async Kafka Consumer created for topics: {topics}")

    async def start(self):
        """התחלת ה-Consumer"""
        if not self.is_started:
            try:
                await self.consumer.start()
                self.is_started = True
                self.last_check_time = datetime.now()
                logger.info("Async Kafka Consumer started")
            except Exception as e:
                logger.error(f"Failed to start Async Consumer: {e}")
                raise

    async def stop(self):
        """עצירת ה-Consumer"""
        if self.is_started:
            try:
                await self.consumer.stop()
                self.is_started = False
                logger.info("Async Kafka Consumer stopped")
            except Exception as e:
                logger.error(f"Error stopping Async Consumer: {e}")

    async def listen_forever(self,
                             message_handler: Callable[[Dict], bool],
                             max_messages: Optional[int] = None) -> int:
        """
        האזנה תמידית להודעות עם callback function (אסינכרונית)

        Args:
            message_handler: פונקציה אסינכרונית לטיפול בהודעות
            max_messages: מספר מקסימלי של הודעות (None = אינסופי)

        Returns:
            מספר ההודעות שעובדו בהצלחה
        """
        if not self.is_started:
            logger.error("Consumer is not started. Call start() first.")
            return 0

        processed_count = 0
        logger.info("Starting async continuous listening...")

        try:
            async for message in self.consumer:
                try:
                    # עיבוד ההודעה
                    message_data = {
                        'topic': message.topic,
                        'partition': message.partition,
                        'offset': message.offset,
                        'key': message.key,
                        'value': message.value,
                        'timestamp': message.timestamp,
                        'received_at': datetime.now().isoformat()
                    }

                    # קריאה אסינכרונית ל-handler
                    if asyncio.iscoroutinefunction(message_handler):
                        success = await message_handler(message_data)
                    else:
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

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error in async listen_forever: {e}")

        logger.info(f"Processed {processed_count} messages")
        return processed_count

    async def get_new_messages(self, timeout_seconds: int = 5) -> List[Dict]:
        """
        קריאת כל ההודעות החדשות שהתחדשו מאז הפעם הקודמת (אסינכרונית)

        Args:
            timeout_seconds: זמן המתנה מקסימלי

        Returns:
            רשימת הודעות חדשות
        """
        if not self.is_started:
            logger.error("Consumer is not started. Call start() first.")
            return []

        new_messages = []
        logger.info("Checking for new messages (async)...")

        try:
            # בדיקת הודעות עם timeout
            end_time = asyncio.get_event_loop().time() + timeout_seconds

            while asyncio.get_event_loop().time() < end_time:
                try:
                    # המתנה להודעה עם timeout קצר
                    message = await asyncio.wait_for(
                        self.consumer.__anext__(),
                        timeout=1.0
                    )

                    message_data = {
                        'topic': message.topic,
                        'partition': message.partition,
                        'offset': message.offset,
                        'key': message.key,
                        'value': message.value,
                        'timestamp': message.timestamp,
                        'received_at': datetime.now().isoformat()
                    }
                    new_messages.append(message_data)

                except asyncio.TimeoutError:
                    # אין הודעות חדשות, נמשיך לבדוק
                    continue
                except StopAsyncIteration:
                    # אין יותר הודעות
                    break

            # עדכון זמן הבדיקה הקודמת
            self.last_check_time = datetime.now()

        except Exception as e:
            logger.error(f"Error getting new messages (async): {e}")

    async def consume(self):
        """
        צריכת הודעות (אסינכרונית) - generator שמחזיר הודעה אחת בכל פעם
        לשימוש עם: async for message in consumer.consume():

        Yields:
            Dictionary עם topic, key, value
        """
        if not self.is_started:
            logger.error("Consumer is not started. Call start() first.")
            return

        try:
            async for message in self.consumer:
                yield {
                    'topic': message.topic,
                    'partition': message.partition,
                    'offset': message.offset,
                    'key': message.key,
                    'value': message.value,
                    'timestamp': message.timestamp,
                    'received_at': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error in async consume: {e}")
            return