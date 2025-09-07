# Kafka Utils - ערכת כלים פשוטה ל-Apache Kafka

ערכת כלים מינימליסטית וברורה לעבודה עם Apache Kafka, עם תמיכה בלקוחות סינכרוניים ואסינכרוניים.

## 📁 מבנה הקבצים

```
shared-utilities/kafka/
├── __init__.py           # יבואים ראשיים
├── sync_client.py        # לקוח סינכרוני
├── async_client.py       # לקוח אסינכרוני
├── json_helpers.py       # 3 פונקציות עזר ל-JSON
├── examples.py           # דוגמאות שימוש
├── requirements.txt      # תלויות
└── README.md            # המדריך הזה
```

## 🚀 התקנה מהירה

```bash
pip install kafka-python aiokafka
```

## 🎯 העקרונות שלנו

### ✅ **מה יש:**
- **2 קלאסים לכל סוג:** Producer + Consumer
- **2 מתודות עיקריות לConsumer:** `listen_forever()` + `get_new_messages()`
- **3 פונקציות עזר ל-JSON:** serialize, deserialize, create_message
- **סינכרוני + אסינכרוני:** בחר מה שמתאים לך

### ❌ **מה אין:**
- עשרות מתודות מבלבלות
- הגדרות מורכבות
- קוד מיותר

---

## 📤 Producer - שליחת הודעות

### סינכרוני (פשוט)
```python
from shared_utilities.kafka import KafkaProducerSync

# יצירה ושליחה
producer = KafkaProducerSync()

# הודעה יחידה
success = producer.send_message(
    topic="my_topic",
    message={"user_id": 123, "action": "login"},
    key="user_123"
)

# מספר הודעות
messages = [
    {"user_id": 1, "action": "login"},
    {"user_id": 2, "action": "purchase"}
]
sent_count = producer.send_batch("my_topic", messages)

producer.close()
```

### אסינכרוני (למקביליות)
```python
from shared_utilities.kafka import KafkaProducerAsync

async def send_async():
    producer = KafkaProducerAsync()
    await producer.start()
    
    # שליחה אסינכרונית
    success = await producer.send_message("my_topic", {"data": "test"})
    
    # שליחה מקבילה
    messages = [{"id": 1}, {"id": 2}, {"id": 3}]
    sent_count = await producer.send_batch("my_topic", messages)
    
    await producer.stop()

# הרצה
import asyncio
asyncio.run(send_async())
```

---

## 📥 Consumer - קריאת הודעות

### המתודות שלך:

#### 1. `listen_forever()` - האזנה תמידית
```python
from shared_utilities.kafka import KafkaConsumerSync

def handle_message(message_data):
    """פונקציה שמטפלת בכל הודעה"""
    value = message_data['value']
    data = value['data']
    print(f"Got: {data}")
    return True  # True = עיבוד הצליח

consumer = KafkaConsumerSync(["my_topic"], group_id="my_group")

# האזנה לנצח (או עד max_messages)
processed = consumer.listen_forever(
    handle_message, 
    max_messages=100  # אופציונלי
)

consumer.close()
```

#### 2. `get_new_messages()` - קריאת עדכונים
```python
consumer = KafkaConsumerSync(["my_topic"], group_id="my_group")

# קריאה ראשונה - כל מה שיש
messages = consumer.get_new_messages(timeout_seconds=5)
print(f"Found {len(messages)} messages")

# קריאה שנייה - רק מה שחדש מאז הפעם הקודמת
new_messages = consumer.get_new_messages(timeout_seconds=5)  
print(f"Found {len(new_messages)} NEW messages")

consumer.close()
```

### אסינכרוני
```python
from shared_utilities.kafka import KafkaConsumerAsync

async def listen_async():
    async def handle_async_message(message_data):
        # עיבוד אסינכרוני
        data = message_data['value']['data']
        await some_async_processing(data)
        return True

    consumer = KafkaConsumerAsync(["my_topic"], group_id="async_group")
    await consumer.start()
    
    # האזנה אסינכרונית
    processed = await consumer.listen_forever(handle_async_message)
    
    # או קריאת עדכונים
    messages = await consumer.get_new_messages(timeout_seconds=3)
    
    await consumer.stop()

asyncio.run(listen_async())
```

---

## 🔧 JSON Helpers - הפונקציות שלך

```python
from shared_utilities.kafka import serialize_json, deserialize_json, create_kafka_message
from datetime import datetime

# 1. המרה ל-JSON (עם תמיכה ב-datetime)
data = {"user": "alice", "time": datetime.now()}
json_string = serialize_json(data)

# 2. המרה חזרה
restored_data = deserialize_json(json_string)

# 3. יצירת הודעת Kafka מובנית
kafka_msg = create_kafka_message(
    topic="users", 
    data={"action": "login"}, 
    key="user_123"
)
# תוצאה:
# {
#   "topic": "users",
#   "key": "user_123", 
#   "data": {"action": "login"},
#   "timestamp": "2025-09-07T...",
#   "message_id": "users_1725742800.123",
#   "version": "1.0"
# }
```

---

## 💡 דוגמאות מעשיות

### Pipeline פשוט
```python
# תהליך שמעביר הודעות בין topics
from shared_utilities.kafka import KafkaConsumerSync, KafkaProducerSync

def process_pipeline():
    consumer = KafkaConsumerSync(["input_topic"], group_id="processor")
    producer = KafkaProducerSync()
    
    def process_message(message_data):
        # קבל הודעה
        original_data = message_data['value']['data']
        
        # עבד אותה
        processed_data = {
            "original": original_data,
            "processed_at": datetime.now(),
            "status": "processed"
        }
        
        # שלח הלאה
        success = producer.send_message("output_topic", processed_data)
        return success
    
    # האזנה ועיבוד
    processed_count = consumer.listen_forever(process_message)
    
    consumer.close()
    producer.close()
    
    return processed_count
```

### מערכת התראות
```python
def notification_system():
    consumer = KafkaConsumerSync(["alerts"], group_id="notifications")
    
    def send_alert(message_data):
        alert = message_data['value']['data']
        
        if alert['severity'] == 'high':
            send_email(alert['message'])
        elif alert['severity'] == 'medium':
            send_sms(alert['message'])
        else:
            log_alert(alert['message'])
            
        return True
    
    # מערכת התראות שרצה לנצח
    consumer.listen_forever(send_alert)
```

### בדיקת עדכונים תקופתית
```python
import time

def check_for_updates():
    consumer = KafkaConsumerSync(["user_updates"], group_id="update_checker")
    
    while True:
        # בדוק מה חדש כל 30 שניות
        new_messages = consumer.get_new_messages(timeout_seconds=5)
        
        if new_messages:
            print(f"Processing {len(new_messages)} new updates")
            for msg in new_messages:
                update = msg['value']['data']
                update_user_in_database(update)
        else:
            print("No new updates")
        
        time.sleep(30)  # המתן 30 שניות
```

---

## ⚙️ הגדרות נפוצות

### חיבור לשרת אחר
```python
# במקום localhost
producer = KafkaProducerSync(bootstrap_servers="kafka.mycompany.com:9092")
consumer = KafkaConsumerSync(["topic"], bootstrap_servers="kafka.mycompany.com:9092")
```

### הגדרות Consumer מתקדמות
```python
consumer = KafkaConsumerSync(
    ["my_topic"],
    bootstrap_servers="localhost:9092",
    group_id="my_group",
    auto_offset_reset='earliest',  # התחל מההתחלה
    consumer_timeout_ms=5000       # timeout ל-get_new_messages
)
```

### הגדרות Producer מתקדמות
```python
producer = KafkaProducerSync(
    bootstrap_servers="localhost:9092",
    acks='all',    # המתן לאישור מכל השרתים
    retries=5,     # נסיונות חוזרים
    batch_size=16384  # גודל batch
)
```

---

## 🎯 טיפים למבחן

### מה חשוב לדעת על Kafka:

1. **Topics** - ערוצי הודעות (כמו תורים)
2. **Partitions** - חלוקה פנימית של topic לביצועים
3. **Consumer Groups** - קבוצות consumers שחולקות עבודה
4. **Offsets** - מיקום של consumer בתור

### פקודות מהירות למבחן:
```python
from shared_utilities.kafka import *

# שליחה מהירה
producer = KafkaProducerSync()
producer.send_message("test", {"data": "hello"})
producer.close()

# קריאה מהירה
consumer = KafkaConsumerSync(["test"])
messages = consumer.get_new_messages()
print(f"Got {len(messages)} messages")
consumer.close()

# JSON
data = {"user": 123, "time": datetime.now()}
json_str = serialize_json(data)
restored = deserialize_json(json_str)
```

### שגיאות נפוצות:
- **Kafka לא רץ:** `kafka-server-start.sh config/server.properties`
- **Topic לא קיים:** ייווצר אוטומטית או `kafka-topics.sh --create`
- **Consumer Group עומד:** שנה group_id או reset offsets

---

## 🏃‍♂️ התחלה מהירה

```python
# Copy-paste זה והכל יעבוד:

from shared_utilities.kafka import KafkaProducerSync, KafkaConsumerSync

# שלח הודעה
producer = KafkaProducerSync()
producer.send_message("test_topic", {"message": "Hello Kafka!"})
producer.close()

# קרא הודעה  
def print_message(msg):
    data = msg['value']['data']
    print(f"Received: {data}")
    return True

consumer = KafkaConsumerSync(["test_topic"], group_id="test_group")
consumer.listen_forever(print_message, max_messages=1)
consumer.close()
```

**זה הכל! פשוט, ברור, ועובד.** 🚀

---

## 📝 לסיכום

### יש לך:
- ✅ **KafkaProducerSync/Async** - שליחת הודעות
- ✅ **KafkaConsumerSync/Async** - קריאת הודעות
- ✅ **consume()** - קריאת הודעה יחידה (לfor loops)
- ✅ **listen_forever()** - האזנה תמידית עם callback
- ✅ **get_new_messages()** - קריאת עדכונים
- ✅ **3 JSON helpers** - serialize, deserialize, create_message

### אין לך:
- ❌ עשרות פונקציות מבלבלות
- ❌ הגדרות מורכבות
- ❌ קוד מיותר

**בהצלחה במבחן! 🎯**