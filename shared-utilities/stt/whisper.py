import whisper
import logging
from datetime import datetime
from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)


class WhisperService:
    def __init__(self, model_name: str, download_root: str):
        self.model = whisper.load_model(
            name=model_name,
            download_root=download_root
        )

    def whisper_transcribe(self, file_path, file_hash: str):
        """תמלול מלא - מחזיר כל המידע הרלוונטי"""
        result = self.model.transcribe(
            file_path,
            word_timestamps=True
        )

        logger.info(f"Detected language: {result['language']}")
        logger.debug(f"Transcription completed for: {file_hash}")

        return {
            'file_hash': file_hash,
            'full_text': result['text'],
            'language': result['language'],
            'segments': result['segments']
        }


def save_transcription_to_elasticsearch(transcription, es_client, index_name="transcriptions"):
    """
    שומר תמלול ב-Elasticsearch עם עדכון חכם

    Args:
        transcription: התוצאה מ-whisper_transcribe
        es_client: Elasticsearch client
        index_name: שם ה-index
    """

    doc = {
        'file_hash': transcription['file_hash'],
        'full_text': transcription['full_text'],
        'language': transcription['language'],
        'segments': transcription['segments'],
        'transcription_indexed_at': datetime.now()
    }

    try:
        es_client.update(
            index=index_name,
            id=transcription['file_hash'],
            body={
                "doc": doc,
                "doc_as_upsert": True  # יוצר חדש אם לא קיים, מעדכן אם קיים
            }
        )
        logger.info(f"Transcription saved/updated for file: {transcription['file_hash']}")
        return True

    except Exception as e:
        logger.error(f"Failed to save transcription to Elasticsearch: {e}")
        return False


# דוגמה לשימוש:
if __name__ == "__main__":
    # יצירת שירות Whisper
    whisper_service = WhisperService(
        model_name="base",
        download_root=r"C:\models\whisper"
    )

    # יצירת חיבור ל-Elasticsearch
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    # תמלול
    transcription = whisper_service.whisper_transcribe(
        r"C:\podcasts\download (6).wav",
        "jhgyuftydtuyytftrdtr"
    )

    # שמירה ב-Elasticsearch
    success = save_transcription_to_elasticsearch(transcription, es)

    if success:
        print("תמלול נשמר בהצלחה!")
        print(f"טקסט: {transcription['full_text']}")
    else:
        print("שגיאה בשמירה")