# examples/kafka-microservice-template/main.py
import asyncio
import logging
import config
from service import BusinessLogicService

# TODO: Import your shared utilities
# from shared_utilities.kafka.kafka_client import KafkaConsumer, KafkaProducer

# Mock Kafka classes for template
class KafkaConsumer:
    def __init__(self, *args, **kwargs): pass
    async def start(self): pass
    async def consume(self):
        for i in range(3):
            yield "input_topic", {"id": i, "data": "sample"}
            await asyncio.sleep(1)

class KafkaProducer:
    def __init__(self, *args, **kwargs): pass
    async def start(self): pass
    async def send_json(self, topic, msg): print(f"Sent to {topic}: {msg}")

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting Kafka Microservice...")

    # 1. Initialize Kafka clients
    consumer = KafkaConsumer(
        topics=[config.KAFKA_INPUT_TOPIC],
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
        group_id=config.KAFKA_GROUP_ID
    )
    producer = KafkaProducer(bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS)

    # 2. Initialize the business logic service
    logic_service = BusinessLogicService(
        producer,
        config.KAFKA_OUTPUT_TOPIC,
        config.KAFKA_ERROR_TOPIC
    )

    try:
        await consumer.start()
        await producer.start()
        logger.info("Kafka clients started.")

        # 3. Start the main consumption loop
        async for topic, message in consumer.consume():
            await logic_service.process_message(message)

    except Exception as e:
        logger.critical(f"A critical error occurred: {e}")
    finally:
        logger.info("Shutting down...")
        # await consumer.stop()
        # await producer.stop()

if __name__ == "__main__":
    asyncio.run(main())