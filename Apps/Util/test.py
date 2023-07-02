import os
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from userProfileModel import UserProfile


app = FastAPI(docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )




#-================================================================================


# Connect to the MongoDB server
client = MongoClient(f"mongodb://root:example@{os.getenv('MONGO_HOST')}/")
db = client["userProfileDB"]
user_profile_collection = db["user_profiles"]

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException

# Kafka producer configuration
kafka_conf = {
    "bootstrap.servers": os.getenv('KAFKA_BOOTSTRAP_SERVERS'),  # Kafka broker address
    "client.id": "module-producer",  # Unique ID for the Kafka producer
}

# Create the Kafka producer
kafka_producer = Producer(kafka_conf)


import json

def publish_to_kafka(topic: str, message: dict):
    try:
        value = json.dumps(message).encode("utf-8")
        kafka_producer.produce(topic, value=value)
        kafka_producer.flush()
    except KafkaException as e:
        if e.args[0].code() == KafkaException.UNKNOWN_TOPIC_OR_PART:
            create_topic(topic)
            kafka_producer.produce(topic, value=value)
            kafka_producer.flush()
        else:
            raise e


def create_topic(topic: str):
    admin_client = AdminClient({"bootstrap.servers": kafka_broker})
    topic_metadata = admin_client.list_topics(timeout=5)
    if topic not in topic_metadata.topics:
        new_topic = NewTopic(topic, num_partitions=1, replication_factor=1)
        admin_client.create_topics([new_topic], request_timeout=15)
        admin_client.close()



@app.post("/api/profiles", status_code=201)
def create_user_profile(user_profile: UserProfile):
    # Check if the user ID already exists
    if user_profile_collection.find_one({"userId": user_profile.userId}):
        raise HTTPException(status_code=400, detail="User ID already exists")

    # Insert the user profile into the collection
    user_profile_dict = user_profile.dict()
    user_profile_collection.insert_one(user_profile_dict)

    # Publish a message to the "user-profile-created" topic
    topic = "user-profile-created"
    message = {
        "userId": user_profile.userId,
        # ... other relevant data ...
    }
    publish_to_kafka(topic, message)

    return {"userId": user_profile.userId}


@app.get("/api/profiles/{userId}")
def get_user_profile(user_id: str):
    user_profile = user_profile_collection.find_one({"userId": user_id})
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert ObjectId to string representation
    user_profile["_id"] = str(user_profile["_id"])

    # Publish a message to the "user-profile-accessed" topic
    topic = "user-profile-accessed"
    message = {
        "userId": user_id,
        # ... other relevant data ...
    }
    publish_to_kafka(topic, message)

    return user_profile


@app.put("/api/profiles/{userId}")
def update_user_profile(user_id: str, user_profile: UserProfile):
    existing_profile = user_profile_collection.find_one({"userId": user_id})
    if not existing_profile:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the fields in the existing profile
    user_profile_dict = user_profile.dict()
    user_profile_collection.update_one({"userId": user_id}, {"$set": user_profile_dict})

    # Publish a message to the "user-profile-updated" topic
    topic = "user-profile-updated"
    message = {
        "userId": user_id,
        # ... other relevant data ...
    }
    publish_to_kafka(topic, message)

    return user_profile


@app.delete("/api/profiles/{userId}")
def delete_user_profile(user_id: str):
    result = user_profile_collection.delete_one({"userId": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # Publish a message to the "user-profile-deleted" topic
    topic = "user-profile-deleted"
    message = {
        "userId": user_id,
        # ... other relevant data ...
    }
    publish_to_kafka(topic, message)

    return {"message": "User profile deleted"}


@app.get("/api/profiles")
def get_all_user_profiles():
    user_profiles = list(user_profile_collection.find())
    # Convert ObjectId to string representation
    for profile in user_profiles:
        profile["_id"] = str(profile["_id"])

    # Publish a message to the "all-user-profiles-accessed" topic
    topic = "all-user-profiles-accessed"
    message = {
        # ... other relevant data ...
    }
    publish_to_kafka(topic, message)

    return user_profiles
