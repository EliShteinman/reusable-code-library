# שליחה עם partition מבוסס hash
def send_transcription(transcription):
    message = {
        'file_hash': transcription['file_hash'],
        'data': transcription,
        'timestamp': datetime.now().isoformat()
    }

    producer.send(
        'transcription_topic',
        key=transcription['file_hash'],  # לpartitioning
        value=message
    )


# קריאה
def process_messages():
    for message in consumer:
        file_hash = message.value['file_hash']
        transcription_data = message.value['data']

        # עיבוד...
        save_transcription_to_elasticsearch(transcription_data, es)