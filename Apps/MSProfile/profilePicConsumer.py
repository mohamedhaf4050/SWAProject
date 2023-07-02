import os
from confluent_kafka import Consumer
import json 
from pymongo import MongoClient, UpdateOne

# Kafka consumer configuration
kafka_conf = {
    "bootstrap.servers":  os.getenv('KAFKA_BOOTSTRAP_SERVERS'),  # Kafka broker address
    "group.id": "user-profile-consumer",  # Unique ID for the Kafka consumer group
    "auto.offset.reset": "earliest",  # Start consuming from the beginning of the topic
}

client = MongoClient("mongodb://root:example@localhost:27017/")
db = client["userProfileDB"]
user_profile_collection = db["user_profiles"]


# Create the Kafka consumer
kafka_consumer = Consumer(kafka_conf)
topic = "profile_picture"
def consume_from_kafka():
    kafka_consumer.subscribe([topic])
    
    while True:
        try:
            message = kafka_consumer.poll(1.0)

            if message is None:
                continue

            if message.error():
                print(f"Error consuming message: {message.error()}")
                continue

            # Process the consumed message
            value = message.value().decode("utf-8")
            data = json.loads(value)
            print(data)
            
            # Update the database accordingly
            user_id = data.get("user_id")
            profile_picture_url = data.get("profile_picture_url")

            if user_id and profile_picture_url:
                update_operation = UpdateOne(
                    {"userId": user_id},
                    {"$set": {"profilePictureUrl": profile_picture_url}}
                )
                user_profile_collection.bulk_write([update_operation])
            
            # Commit the offset to mark the message as consumed
            kafka_consumer.commit(message)

        except KeyboardInterrupt:
            break

    kafka_consumer.close()

consume_from_kafka()
