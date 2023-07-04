import json
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import os 

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException
# Kafka producer configuration

# Kafka producer configuration
kafka_conf = {
    "bootstrap.servers":  os.getenv('KAFKA_BOOTSTRAP_SERVERS'),  # Kafka broker address
    "client.id": "user-profile-producer",  # Unique ID for the Kafka producer
}
print(kafka_conf)
# Create the Kafka producer
kafka_producer = Producer(kafka_conf)

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

