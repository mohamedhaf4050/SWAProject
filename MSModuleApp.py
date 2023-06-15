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
#-================================================================================

from confluent_kafka import Producer
import json

# Connect to MongoDB
client = MongoClient("mongodb://root:example@localhost:27017/")
db = client["elearningDB"]
collection = db["modules"]

# Kafka configuration
kafka_bootstrap_servers = "localhost:9092"
kafka_topic = "elearning_topic"
kafka_producer = Producer({"bootstrap.servers": kafka_bootstrap_servers})


class Module(BaseModel):
    module_id: str
    title: str
    description: str
    content: Dict = None
    parent_module_id: str = None
    sub_modules: List[str] = []




def publish_to_kafka(event: str, module_id: str):
    kafka_message = {"event": event, "module_id": module_id}
    kafka_producer.produce(kafka_topic, value=json.dumps(kafka_message).encode("utf-8"))
    kafka_producer.flush()


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