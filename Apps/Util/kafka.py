from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException

def init():

    # Kafka producer configuration
    kafka_conf = {
        "bootstrap.servers": "localhost:9092",  # Kafka broker address
        "client.id": "user-profile-producer",  # Unique ID for the Kafka producer
    }

    # Create the Kafka producer
    kafka_producer = Producer(kafka_conf)



def create_topic(topic: str):
    admin_client = AdminClient({"bootstrap.servers": kafka_bootstrap_servers})
    topic_metadata = admin_client.list_topics(timeout=5)
    if topic not in topic_metadata.topics:
        new_topic = NewTopic(topic, num_partitions=1, replication_factor=1)
        admin_client.create_topics([new_topic], request_timeout=15)
        admin_client.close()