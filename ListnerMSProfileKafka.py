from confluent_kafka import Consumer, KafkaError
import threading


def kafka_listener(topic):
    # Kafka consumer configuration
    kafka_conf = {
        "bootstrap.servers": "localhost:9092",  # Kafka broker address
        "group.id": f"{topic}-consumer",  # Consumer group ID
        "auto.offset.reset": "earliest",  # Start consuming from the beginning of the topic
    }

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
    "all-user-profiles-accessed"
]

# Create and start a thread for each listener
threads = []
for topic in topics:
    thread = threading.Thread(target=kafka_listener, args=(topic,))
    thread.start()
    threads.append(thread)

# Wait for all threads to complete
for thread in threads:
    thread.join()
