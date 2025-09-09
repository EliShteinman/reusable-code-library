from kafka import KafkaProducer, KafkaConsumer
import json

# שליחה
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    key_serializer=lambda x: x.encode('utf-8'),
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# שליחת תוצאת התמלול
transcription = whisper_service.whisper_transcribe(file_path, file_hash)

producer.send(
    'transcription_topic',
    key=transcription['file_hash'],  # ה-hash כ-key
    value=transcription
)

# קריאה
consumer = KafkaConsumer(
    'transcription_topic',
    bootstrap_servers=['localhost:9092'],
    key_deserializer=lambda x: x.decode('utf-8'),
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for message in consumer:
    file_hash = message.key  # ה-hash
    transcription = message.value  # כל הנתונים
    print(f"עיבוד קובץ: {file_hash}")