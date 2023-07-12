

import os
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi import Depends, FastAPI, HTTPException
from pymongo import MongoClient
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException

from Apps.Util.auth import authenticate_user, create_access_token
from ..Util.kafka import publish_to_kafka, create_topic, kafka_conf, kafka_producer
import json
from ..Util.database import collection

def init_app():
    
    
    app= FastAPI(docs_url=None, redoc_url=None)
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




    @app.post("/token")
    def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        username = form_data.username
        password = form_data.password
        if not authenticate_user(username, password):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        access_token = create_access_token(data={"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}

    @app.exception_handler(HTTPException)
    async def handle_bad_request(request, exc):
        print(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    return app