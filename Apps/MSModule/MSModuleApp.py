from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from .cirriclumModel import Module
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import os 


app = FastAPI(docs_url=None, redoc_url=None)
print(os.getenv('KAFKA_BOOTSTRAP_SERVERS'))
print(os.getenv('MONGO_HOST'))
app.mount("/static", StaticFiles(directory="Apps/Util/static"), name="static")

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
import os
from ..Util.kafka import publish_to_kafka, create_topic, kafka_conf, kafka_producer





@app.post("/module/")
def create_module(module: Module):
    module_dict = module.dict()
  # Check if module ID already exists
    existing_module = collection.find_one({"module_id": module.module_id})
    if existing_module:
        raise HTTPException(status_code=409, detail="Module ID already exists")

    def create():
            result = collection.insert_one(module_dict)
            # module.db_id = str(result.inserted_id)
            module.module_id = module.module_id  

    if not module.parent_module_id:
        create()
    else:
        parent_module = collection.find_one({"module_id": module.parent_module_id})
        if parent_module:
            create()
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
      # Check if module ID already exists
    existing_module = collection.find_one({"module_id": module.module_id})
    if existing_module:
        raise HTTPException(status_code=409, detail="Module ID already exists")

    module_dict = module.dict()
    result = collection.update_one({"module_id": module_id}, {"$set": module_dict})
    if result.modified_count > 0:
        # Publish message to Kafka topic
        publish_to_kafka("module_updated", module_id)

        return module

    raise HTTPException(status_code=404, detail="Module not found")


@app.delete("/module/{module_id}")
def delete_module(module_id: str):
    module = collection.find_one({"module_id": module_id})
    if module:
        # Recursively delete child modules
        delete_child_modules(module_id)
        
        # Delete the parent module
        result = collection.delete_one({"module_id": module_id})
        if result.deleted_count > 0:
            # Publish message to Kafka topic
            publish_to_kafka("module_deleted", module_id)

            return {"message": "Module deleted"}

    raise HTTPException(status_code=404, detail="Module not found")


def delete_child_modules(module_id: str):
    # Find and delete child modules recursively
    child_modules = collection.find({"parent_module_id": module_id})
    for child_module in child_modules:
        delete_child_modules(child_module["module_id"])
        collection.delete_one({"module_id": child_module["module_id"]})