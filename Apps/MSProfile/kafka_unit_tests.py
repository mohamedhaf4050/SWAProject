import os
from pymongo import MongoClient
import pytest
from dotenv import load_dotenv
load_dotenv()

from fastapi.testclient import TestClient
from confluent_kafka import Consumer, KafkaError, Producer
from ..MSProfile.MSProfileApp import app 
from ..Util.database import reset_kafka_topic_and_database
import json
import threading
from confluent_kafka.admin import AdminClient, NewTopic

topic = 'user-profile-created'  # Adjust the topic based on your use case


@pytest.fixture(scope='module')
def kafka_consumer():

    kafka_conf = {
            "bootstrap.servers": os.getenv('KAFKA_BOOTSTRAP_SERVERS'),  # Kafka broker address
            "group.id": f"{topic}-consumer",  # Consumer group ID
            "auto.offset.reset": "earliest",  # Start consuming from the beginning of the topic
        }
    consumer = Consumer(kafka_conf)

    consumer.subscribe([topic])

    yield consumer

    consumer.close()

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as client:
        yield client


def test_create_user_profile(client, kafka_consumer):
    reset_kafka_topic_and_database(topic)
    # Make the request
    id = 88
    response = client.post(
        "/api/profiles", 
        json={
        "userId": str(id),
        "username": "john_doe",
        "email": "john.doe@example.com",
        "profilePictureUrl": "https://example.com/profile.jpg"
        }
        )
    assert response.status_code == 201

    # Consume the Kafka messages
    while True:
        message = kafka_consumer.poll(5.0)  # Wait for 5 seconds for a message
        if message is None:
            break

        # Verify the Kafka message
        if not message.error():
            value = message.value()
            kafka_message = json.loads(value.decode('utf-8'))

            if kafka_message['userId'] == id:
                # Assert other relevant data in the Kafka message
                assert kafka_message['userId'] == str(id)
                response = client.delete("/api/profiles/"+str(id)+"?user_id="+ str(id))
                print(response)
                break

    else:
        pytest.fail("No matching Kafka message found")

    # Continue with additional assertions or checks on the Kafka message if needed


    # # Consume the Kafka message
    # message = kafka_consumer.poll(5.0)  # Wait for 5 seconds for the message

    # # Verify the Kafka message
    # assert message is not None
    # assert not message.error()
    # value = message.value()
    # kafka_message = json.loads(value.decode('utf-8'))

    # assert kafka_message['userId'] == '333'
    # # Assert other relevant data in the Kafka message

    # # Continue with additional assertions or checks on the Kafka message if needed
