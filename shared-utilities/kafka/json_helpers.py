# ============================================================================
# shared-utilities/kafka/json_helpers.py - 3 JSON HELPER FUNCTIONS
# ============================================================================
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def serialize_json(data: Any) -> str:
    """
    המרת Python object ל-JSON string
    עם תמיכה ב-datetime ואובייקטים מורכבים

    Args:
        data: הנתונים להמרה

    Returns:
        JSON string

    Raises:
        ValueError: אם ההמרה נכשלה
    """

    def json_serializer(obj):
        """סיריאלייזר מותאם אישית"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)

    try:
        return json.dumps(data, default=json_serializer, ensure_ascii=False, indent=None)
    except Exception as e:
        logger.error(f"Failed to serialize JSON: {e}")
        raise ValueError(f"JSON serialization failed: {e}")


def deserialize_json(json_str: str) -> Any:
    """
    המרת JSON string ל-Python object
    עם טיפול בשגיאות

    Args:
        json_str: מחרוזת JSON

    Returns:
        Python object

    Raises:
        ValueError: אם ההמרה נכשלה
    """
    if not json_str or not isinstance(json_str, str):
        raise ValueError("Invalid JSON string provided")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to deserialize JSON: {e}")
        raise ValueError(f"Invalid JSON format: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in JSON deserialization: {e}")
        raise ValueError(f"JSON deserialization failed: {e}")


def create_kafka_message(topic: str, data: Any, key: Optional[str] = None) -> Dict[str, Any]:
    """
    יצירת הודעת Kafka סטנדרטית עם metadata

    Args:
        topic: שם ה-topic
        data: הנתונים עצמם
        key: מפתח אופציונלי

    Returns:
        Dictionary עם מבנה הודעת Kafka סטנדרטית
    """
    timestamp = datetime.now()

    return {
        'topic': topic,
        'key': key,
        'data': data,
        'timestamp': timestamp.isoformat(),
        'message_id': f"{topic}_{timestamp.timestamp()}",
        'created_at': timestamp.isoformat(),
        'version': '1.0'
    }