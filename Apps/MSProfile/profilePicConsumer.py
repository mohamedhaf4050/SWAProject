import os
from dotenv import load_dotenv
from confluent_kafka import Consumer
import json
from pymongo import MongoClient, UpdateOne

load_dotenv()

# Kafka consumer configuration
kafka_conf = {
    "bootstrap.servers": os.getenv('KAFKA_BOOTSTRAP_SERVERS'),  # Kafka broker address
    "group.id": "user-profile-consumer",  # Unique ID for the Kafka consumer group
    "auto.offset.reset": "earliest",  # Start consuming from the beginning of the topic
}

client = MongoClient(f"mongodb://root:example@{os.getenv('MONGO_HOST')}/")
db = client["elearningDB"]
collection = db["modules"]
user_profile_collection = db["user_profiles"]

# Create the Kafka consumer
kafka_consumer = Consumer(kafka_conf)
topic = "profile_picture"


def consume_from_kafka():
    kafka_consumer.subscribe([topic])

    try:
        while True:
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
                # Check if the user_id exists in the database
                user_exists = user_profile_collection.find_one({"userId": user_id})
                if user_exists:
                    update_operation = UpdateOne(
                        {"userId": user_id},
                        {"$set": {"profilePictureUrl": profile_picture_url}}
                    )
                    user_profile_collection.bulk_write([update_operation])
                    print(f"Profile picture URL updated for user_id: {user_id}")
                else:
                    
                    print(f"User_id {user_id} not found in the database")

            # Commit the offset to mark the message as consumed
            kafka_consumer.commit(message)

    except KeyboardInterrupt:
        pass

    kafka_consumer.close()


consume_from_kafka()
