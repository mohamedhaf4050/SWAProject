import os
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer
import json

# Kafka configuration
bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
topic = 'profile_picture'
num_partitions = 1
replication_factor = 1

# Create Kafka admin client
admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})

# Create Kafka producer
producer = Producer({'bootstrap.servers': bootstrap_servers})

def delivery_report(err, msg):
    """Delivery callback function to check if the message was successfully produced."""
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def create_topic():
    """Create Kafka topic if it doesn't exist."""
    topic_metadata = admin_client.list_topics(timeout=5)
    if topic_metadata.topics.get(topic) is None:
        new_topic = NewTopic(topic, num_partitions=num_partitions, replication_factor=replication_factor)
        admin_client.create_topics([new_topic])
        print(f'Topic "{topic}" created successfully')

def produce_user_data(user_id, profile_picture_url):
    """Produce user data to Kafka topic."""
    data = {'user_id': user_id, 'profile_picture_url': profile_picture_url}
    producer.produce(topic, json.dumps(data), callback=delivery_report)

    # Wait for the message to be delivered or raise an exception
    producer.flush()

# Create topic if it doesn't exist
create_topic()

# Example usage
user_id = '444'
profile_picture_url = 'https://example.com/profile_picture.jpg'

produce_user_data(user_id, profile_picture_url)
