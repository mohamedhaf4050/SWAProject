from confluent_kafka import Consumer, KafkaError
import threading

topics =["", "", "", "", "", "", "", "","", "", "", "", "", ""]
def kafka_listener(topic):
    # Kafka consumer configuration
    kafka_conf = {
        "bootstrap.servers": "localhost:9092",  # Kafka broker address
        "group.id": f"{topic}-consumer",  # Consumer group ID
        "auto.offset.reset": "earliest",  # Start consuming from the beginning of the topic
    }

    
    # for topic in   topics:
    #     create_topic(topic)



    # Create the Kafka consumer
    kafka_consumer = Consumer(kafka_conf)
    kafka_consumer.subscribe([topic])

    try:
        while True:
            message = kafka_consumer.poll(1.0)

            if message is None:
                continue

            if message.error():
                if message.error().code() == KafkaError._PARTITION_EOF:
                    # Reached the end of the partition, continue consuming
                    continue
                else:
                    # Handle other Kafka errors
                    print(f"Kafka error: {message.error().str()}")
                    continue

            # Process the consumed message
            value = message.value()
            print(f"Received message from topic '{topic}': {value}")

    except KeyboardInterrupt:
        kafka_consumer.close()


# Start the Kafka listeners for the topics
topics = [
    "user-profile-created",
    "user-profile-accessed",
    "user-profile-updated",
    "user-profile-deleted",
    "all-user-profiles-accessed",
    "module_created",
    "module_retrieved",
    "module_updated",
    "module_deleted"
]

from confluent_kafka.admin import AdminClient, NewTopic
kafka_bootstrap_servers = "localhost:9092"

admin_client = AdminClient({"bootstrap.servers": kafka_bootstrap_servers})

# def create_topic_if_not_exist(topic_name):
#     # Check if the topic already exists
#     topic_metadata = admin_client.list_topics(timeout=5)
#     if topic_name not in topic_metadata.topics:
#         # Topic doesn't exist, create it
#         new_topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
#         admin_client.create_topics([new_topic])

# Create and start a thread for each listener

# for topic in topics:
#     create_topic_if_not_exist(topic)

threads = []
for topic in topics:
    thread = threading.Thread(target=kafka_listener, args=(topic,))
    thread.start()
    threads.append(thread)

# Wait for all threads to complete
for thread in threads:
    thread.join()
