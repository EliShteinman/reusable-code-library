# examples/kafka-microservice-template/service.py
import logging
from typing import Dict, Any

# TODO: Import your shared utilities
# from shared_utilities.kafka.kafka_client import KafkaProducer

# Mock producer for template
class KafkaProducer:
    async def send_json(self, topic, msg): pass

logger = logging.getLogger(__name__)

class BusinessLogicService:
    """
    Encapsulates the core business logic of the microservice.
    It receives a Kafka producer to send results.
    """
    def __init__(self, producer: KafkaProducer, output_topic: str, error_topic: str):
        self.producer = producer
        self.output_topic = output_topic
        self.error_topic = error_topic
        logger.info(f"BusinessLogicService initialized. Outputting to '{output_topic}'.")

    async def process_message(self, message: Dict[str, Any]) -> None:
        """
        Processes a single message from Kafka.
        """
        try:
            # TODO: Implement your core business logic here
            # Example: Add a new field to the message
            logger.info(f"Processing message ID: {message.get('id')}")
            processed_message = message.copy()
            processed_message["processing_status"] = "processed"
            processed_message["service_name"] = "my-kafka-service"

            # Send the processed message to the output topic
            await self.producer.send_json(self.output_topic, processed_message)
            logger.info(f"Successfully processed and sent message ID: {message.get('id')}")

        except Exception as e:
            logger.error(f"Failed to process message ID: {message.get('id')}. Error: {e}")
            # Send the original message to an error topic for later analysis
            error_payload = {"original_message": message, "error": str(e)}
            await self.producer.send_json(self.error_topic, error_payload)