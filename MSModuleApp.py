from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from typing import List, Dict
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
    # Custom exception handler for 400 Bad Request
@app.exception_handler(HTTPException)
async def handle_bad_request(request, exc):
    print(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


#-================================================================================

from confluent_kafka import Producer
import json
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException
import json
from confluent_kafka import Producer


# Connect to MongoDB
client = MongoClient("mongodb://root:example@localhost:27017/")
db = client["elearningDB"]
collection = db["modules"]

# Kafka configuration
kafka_bootstrap_servers = "localhost:9092"
kafka_topic = "elearning_topic"

# Kafka producer configuration
kafka_conf = {
    "bootstrap.servers": "localhost:9092",  # Kafka broker address
    "client.id": "user-profile-producer",  # Unique ID for the Kafka producer
}
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
    admin_client = AdminClient({"bootstrap.servers": kafka_bootstrap_servers})
    topic_metadata = admin_client.list_topics(timeout=5)
    if topic not in topic_metadata.topics:
        new_topic = NewTopic(topic, num_partitions=1, replication_factor=1)
        admin_client.create_topics([new_topic], request_timeout=15)
        admin_client.close()


class Module(BaseModel):
    module_id: str
    title: str
    description: str
    content: Dict = None
    parent_module_id: str = None
    sub_modules: List[str] = []


@app.post("/module/")
def create_module(module: Module):
    module_dict = module.dict()

    if not module.parent_module_id:
        result = collection.insert_one(module_dict)
        module.module_id = str(result.inserted_id)
    else:
        parent_module = collection.find_one({"module_id": module.parent_module_id})
        if parent_module:
            result = collection.insert_one(module_dict)
            module.module_id = str(result.inserted_id)
            parent_module["sub_modules"].append(module.module_id)
            collection.update_one({"module_id": module.parent_module_id}, {"$set": parent_module})
        else:
            raise HTTPException(status_code=404, detail="Parent module not found")

    # Publish message to Kafka topic
    publish_to_kafka("module_created", module.module_id)

    return module


@app.get("/module/{module_id}")
def get_module(module_id: str):
    module = collection.find_one({"module_id": module_id})
    if module:
        # Publish message to Kafka topic
        publish_to_kafka("module_retrieved", module_id)

        return Module(**module)

    raise HTTPException(status_code=404, detail="Module not found")


@app.get("/module")
def get_all_modules():
    modules = collection.find()
    module_list = [Module(**module) for module in modules]

    # Publish message to Kafka topic for each module
    for module in module_list:
        publish_to_kafka("module_retrieved", module.module_id)

    return module_list


@app.put("/module/{module_id}")
def update_module(module_id: str, module: Module):
    module_dict = module.dict()
    result = collection.update_one({"module_id": module_id}, {"$set": module_dict})
    if result.modified_count > 0:
        # Publish message to Kafka topic
        publish_to_kafka("module_updated", module_id)

        return module

    raise HTTPException(status_code=404, detail="Module not found")


@app.delete("/module/{module_id}")
def delete_module(module_id: str):
    result = collection.delete_one({"module_id": module_id})
    if result.deleted_count > 0:
        # Publish message to Kafka topic
        publish_to_kafka("module_deleted", module_id)

        return {"message": "Module deleted"}

    raise HTTPException(status_code=404, detail="Module not found")
