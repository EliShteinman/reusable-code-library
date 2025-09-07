# ============================================================================
# shared-utilities/kafka/examples.py - דוגמאות שימוש מלאות ומתוקנות
# ============================================================================
import asyncio
import time
from datetime import datetime

# Import all our Kafka utilities
from . import (
    KafkaProducerSync, KafkaConsumerSync,
    KafkaProducerAsync, KafkaConsumerAsync,
    serialize_json, deserialize_json, create_kafka_message
)


# ============================================================================
# דוגמה 1: שימוש סינכרוני בסיסי
# ============================================================================

def sync_example():
    """דוגמה לשימוש בלקוח הסינכרוני"""
    print("=== Synchronous Kafka Example ===")

    TOPIC = "sync_test_topic"

    # 1. Producer סינכרוני
    producer = KafkaProducerSync()

    # שליחת הודעות
    test_messages = [
        {"user_id": 1, "action": "login", "timestamp": datetime.now()},
        {"user_id": 2, "action": "purchase", "amount": 99.99},
        {"user_id": 3, "action": "logout"}
    ]

    print("Sending messages synchronously...")
    for msg in test_messages:
        success = producer.send_message(TOPIC, msg, key=f"user_{msg['user_id']}")
        print(f"  Sent {msg['action']}: {'✅' if success else '❌'}")

    producer.close()
    print("Producer closed\n")

    # 2. Consumer סינכרוני
    def handle_message(message_data):
        """פונקציה לטיפול בהודעות"""
        try:
            value = message_data['value']
            data = value['data']
            print(f"  📨 Received: {data['action']} from user {data['user_id']}")
            return True
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    consumer = KafkaConsumerSync([TOPIC], group_id="sync_example_group")

    # האזנה להודעות (מוגבל ל-3 הודעות)
    print("Listening for messages...")
    processed = consumer.listen_forever(handle_message, max_messages=3)
    print(f"Processed {processed} messages synchronously")

    consumer.close()
    print("Sync example completed\n")


# ============================================================================
# דוגמה 2: שימוש אסינכרוני
# ============================================================================

async def async_example():
    """דוגמה לשימוש בלקוח האסינכרוני"""
    print("=== Asynchronous Kafka Example ===")

    TOPIC = "async_test_topic"

    # 1. Producer אסינכרוני
    producer = KafkaProducerAsync()
    await producer.start()

    # שליחת הודעות במקביל
    async_messages = [
        {"session_id": "sess_001", "event": "page_view", "page": "/home"},
        {"session_id": "sess_002", "event": "click", "element": "buy_button"},
        {"session_id": "sess_003", "event": "form_submit", "form": "contact"}
    ]

    print("Sending messages asynchronously...")
    sent_count = await producer.send_batch(TOPIC, async_messages)
    print(f"  Sent {sent_count}/{len(async_messages)} messages")

    await producer.stop()
    print("Async producer stopped\n")

    # 2. Consumer אסינכרוני
    async def handle_async_message(message_data):
        """פונקציה אסינכרונית לטיפול בהודעות"""
        try:
            value = message_data['value']
            data = value['data']
            print(f"  📨 Async received: {data['event']} from {data['session_id']}")

            # סימולציה של עיבוד אסינכרוני
            await asyncio.sleep(0.1)
            return True
        except Exception as e:
            print(f"  ❌ Async error: {e}")
            return False

    consumer = KafkaConsumerAsync([TOPIC], group_id="async_example_group")
    await consumer.start()

    # האזנה אסינכרונית
    print("Listening for messages asynchronously...")
    processed = await consumer.listen_forever(handle_async_message, max_messages=3)
    print(f"Processed {processed} messages asynchronously")

    await consumer.stop()
    print("Async example completed\n")


# ============================================================================
# דוגמה 3: get_new_messages - קריאת עדכונים
# ============================================================================

def get_new_messages_example():
    """דוגמה לשימוש ב-get_new_messages"""
    print("=== Get New Messages Example ===")

    TOPIC = "updates_topic"

    # שליחת כמה הודעות קודם
    producer = KafkaProducerSync()

    updates = [
        {"type": "status_update", "user": "alice", "status": "online"},
        {"type": "notification", "user": "bob", "message": "new message"},
        {"type": "status_update", "user": "charlie", "status": "away"}
    ]

    print("Sending update messages...")
    for update in updates:
        producer.send_message(TOPIC, update)
    producer.close()

    # עכשיו נקרא את העדכונים
    consumer = KafkaConsumerSync([TOPIC], group_id="updates_group")

    print("\nFirst check - getting all available messages:")
    messages = consumer.get_new_messages(timeout_seconds=3)
    print(f"  Found {len(messages)} messages")
    for msg in messages:
        data = msg['value']['data']
        print(f"    - {data['type']}: {data.get('user', 'unknown')}")

    print("\nSecond check - should be empty (no new messages):")
    messages = consumer.get_new_messages(timeout_seconds=2)
    print(f"  Found {len(messages)} new messages")

    # שליחת הודעה נוספת
    producer = KafkaProducerSync()
    producer.send_message(TOPIC, {"type": "new_update", "user": "david", "status": "busy"})
    producer.close()

    print("\nThird check - after sending new message:")
    messages = consumer.get_new_messages(timeout_seconds=3)
    print(f"  Found {len(messages)} new messages")
    for msg in messages:
        data = msg['value']['data']
        print(f"    - NEW: {data['type']}: {data.get('user', 'unknown')}")

    consumer.close()
    print("Get new messages example completed\n")


# ============================================================================
# דוגמה 4: JSON Helpers
# ============================================================================

def json_helpers_example():
    """דוגמה לשימוש בפונקציות העזר ל-JSON"""
    print("=== JSON Helpers Example ===")

    # נתונים מורכבים
    complex_data = {
        "user_id": 12345,
        "timestamp": datetime.now(),
        "metadata": {
            "device": "mobile",
            "app_version": "2.1.0"
        },
        "actions": [
            {"type": "click", "element": "button"},
            {"type": "scroll", "position": 150}
        ]
    }

    print("1. serialize_json - המרה ל-JSON:")
    json_string = serialize_json(complex_data)
    print(f"   JSON length: {len(json_string)} characters")
    print(f"   Contains timestamp: {'timestamp' in json_string}")

    print("\n2. deserialize_json - המרה חזרה:")
    restored_data = deserialize_json(json_string)
    print(f"   User ID: {restored_data['user_id']}")
    print(f"   Actions count: {len(restored_data['actions'])}")
    print(f"   Device: {restored_data['metadata']['device']}")

    print("\n3. create_kafka_message - יצירת הודעה מובנית:")
    kafka_msg = create_kafka_message("user_actions", complex_data, key="user_12345")
    print(f"   Topic: {kafka_msg['topic']}")
    print(f"   Key: {kafka_msg['key']}")
    print(f"   Message ID: {kafka_msg['message_id']}")
    print(f"   Version: {kafka_msg['version']}")
    print(f"   Has original data: {'data' in kafka_msg}")

    print("JSON helpers example completed\n")


# ============================================================================
# דוגמה 5: consume() Method - הדוגמאות החסרות! ⭐
# ============================================================================

def consume_example():
    """דוגמה לשימוש בmethod consume() - FIXED!"""
    print("=== Consume Method Example (Sync) ===")

    TOPIC = "consume_test_topic"

    # שליחת הודעות לבדיקה
    producer = KafkaProducerSync()
    test_messages = [
        {"item": "laptop", "price": 1200},
        {"item": "mouse", "price": 25},
        {"item": "keyboard", "price": 80}
    ]

    print("Sending test messages...")
    for msg in test_messages:
        producer.send_message(TOPIC, msg)
    producer.close()

    # שימוש ב-consume()
    consumer = KafkaConsumerSync([TOPIC], group_id="consume_example_group")

    print("Using consume() method:")
    count = 0
    try:
        for message in consumer.consume():
            if message:
                data = message['value']['data']
                print(f"  📦 Item: {data['item']}, Price: ${data['price']}")
                count += 1

                # עצירה אחרי 3 הודעות
                if count >= 3:
                    break
    except KeyboardInterrupt:
        print("  Stopped by user")

    consumer.close()
    print(f"Consumed {count} messages using consume() method\n")


async def async_consume_example():
    """דוגמה לשימוש באסינכרוני consume() - FIXED!"""
    print("=== Async Consume Method Example ===")

    TOPIC = "async_consume_test_topic"

    # שליחת הודעות
    producer = KafkaProducerAsync()
    await producer.start()

    test_messages = [
        {"event": "user_login", "user_id": 101},
        {"event": "page_view", "page": "/dashboard"},
        {"event": "user_logout", "user_id": 101}
    ]

    print("Sending test messages async...")
    await producer.send_batch(TOPIC, test_messages)
    await producer.stop()

    # שימוש באסינכרוני consume()
    consumer = KafkaConsumerAsync([TOPIC], group_id="async_consume_group")
    await consumer.start()

    print("Using async consume() method:")
    count = 0
    try:
        async for message in consumer.consume():
            if message:
                data = message['value']['data']
                print(f"  🔄 Event: {data['event']}")
                count += 1

                # עצירה אחרי 3 הודעות
                if count >= 3:
                    break
    except Exception as e:
        print(f"  Error: {e}")

    await consumer.stop()
    print(f"Async consumed {count} messages\n")


# ============================================================================
# דוגמה 6: Error Handling
# ============================================================================

async def error_handling_example():
    """דוגמה לטיפול בשגיאות"""
    print("=== Error Handling Example ===")

    # נסיון להתחבר לשרת שלא קיים
    try:
        producer = KafkaProducerAsync(bootstrap_servers="nonexistent:9092")
        await producer.start()
        await producer.send_message("test", {"data": "test"})
    except Exception as e:
        print(f"  ❌ Expected connection error: {type(e).__name__}")

    # JSON שגוי
    try:
        bad_json = '{"incomplete": json data'
        deserialize_json(bad_json)
    except ValueError as e:
        print(f"  ❌ Expected JSON error: {e}")

    # הודעה ריקה
    try:
        result = serialize_json(None)
        print(f"  ✅ Handling None: '{result}'")
    except Exception as e:
        print(f"  ❌ Unexpected error with None: {e}")

    print("Error handling example completed\n")


# ============================================================================
# הרצת כל הדוגמאות
# ============================================================================

def run_sync_examples():
    """הרצת הדוגמאות הסינכרוניות"""
    print("🚀 Running Synchronous Kafka Examples\n")

    try:
        json_helpers_example()
        sync_example()
        consume_example()  # ⭐ דוגמה שתוקנה!
        get_new_messages_example()
        print("✅ All sync examples completed!")

    except Exception as e:
        print(f"❌ Error in sync examples: {e}")
        print("Make sure Kafka is running on localhost:9092")


async def run_async_examples():
    """הרצת הדוגמאות האסינכרוניות"""
    print("🚀 Running Asynchronous Kafka Examples\n")

    try:
        await async_example()
        await async_consume_example()  # ⭐ דוגמה שתוקנה!
        await error_handling_example()
        print("✅ All async examples completed!")

    except Exception as e:
        print(f"❌ Error in async examples: {e}")
        print("Make sure Kafka is running on localhost:9092")


if __name__ == "__main__":
    print("Kafka Utils Examples\n")
    print("Choose example to run:")
    print("1. Sync examples")
    print("2. Async examples")
    print("3. All examples")

    choice = input("\nEnter choice (1/2/3): ").strip()

    if choice == "1":
        run_sync_examples()
    elif choice == "2":
        asyncio.run(run_async_examples())
    elif choice == "3":
        run_sync_examples()
        print("\n" + "=" * 50 + "\n")
        asyncio.run(run_async_examples())
    else:
        print("Invalid choice")