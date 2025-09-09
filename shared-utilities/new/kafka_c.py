producer.send(
    'transcription_topic',
    key=file_hash,
    value=transcription,
    headers=[
        ('file_type', b'audio'),
        ('source_service', b'whisper'),
        ('processing_time', str(time.time()).encode())
    ]
)