import pytest
from fastapi.testclient import TestClient
from ..MSProfile import MSProfileApp
from confluent_kafka import Consumer, KafkaError, Producer
import json
import threading


def test_create_user_profile(client, kafka_consumer):
    # Make the request
    response = client.post("/api/profiles", json={"userId": "5456"})
    assert response.status_code == 201

    # Consume the Kafka message
    message = kafka_consumer.poll(5.0)  # Wait for 5 seconds for the message

    # Verify the Kafka message
    assert message is not None
    assert not message.error()
    value = message.value()
    kafka_message = json.loads(value.decode('utf-8'))

    assert kafka_message['userId'] == '5456'
    # Assert other relevant data in the Kafka message

    # Continue with additional assertions or checks on the Kafka message if needed
