# examples/kafka-microservice-template/config.py
import os

# Kafka connection settings
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Service-specific topics
KAFKA_INPUT_TOPIC = os.getenv("KAFKA_INPUT_TOPIC", "input_topic")
KAFKA_OUTPUT_TOPIC = os.getenv("KAFKA_OUTPUT_TOPIC", "output_topic")
KAFKA_ERROR_TOPIC = os.getenv("KAFKA_ERROR_TOPIC", "error_topic")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "my-service-group")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()