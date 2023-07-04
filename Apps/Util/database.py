

from dotenv import load_dotenv
load_dotenv()

from confluent_kafka.admin import AdminClient, NewTopic

# Connect to MongoDB
import os
from pymongo import MongoClient


client = MongoClient(f"mongodb://root:example@{os.getenv('MONGO_HOST')}/")
db = client["elearningDB"]
collection = db["modules"]
user_profile_collection = db["user_profiles"]



def reset_kafka_topic_and_database(topic):
    # Delete Kafka topic
    admin_client = AdminClient({'bootstrap.servers':  os.getenv('KAFKA_BOOTSTRAP_SERVERS')})
    topic_metadata = admin_client.list_topics(timeout=10)

    if topic in topic_metadata.topics:
        admin_client.delete_topics([topic], operation_timeout=10)
        admin_client.create_topics([NewTopic(topic, num_partitions=1, replication_factor=1)])
    else:
        admin_client.create_topics([NewTopic(topic, num_partitions=1, replication_factor=1)])

    # Delete data from MongoDB
    collection.delete_many({})
    user_profile_collection.delete_many({})
