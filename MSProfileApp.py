from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from models import UserProfile


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


# Connect to the MongoDB server
client = MongoClient("mongodb://root:example@localhost:27017/")
db = client["userProfileDB"]
user_profile_collection = db["user_profiles"]


@app.post("/api/profiles", status_code=201)
def create_user_profile(user_profile: UserProfile):
    # Check if the user ID already exists
    if user_profile_collection.find_one({"userId": user_profile.userId}):
        raise HTTPException(status_code=400, detail="User ID already exists")

    # Insert the user profile into the collection
    user_profile_dict = user_profile.dict()
    user_profile_collection.insert_one(user_profile_dict)

    return {"userId": user_profile.userId}

@app.get("/api/profiles/{userId}")
def get_user_profile(user_id: str):
    user_profile = user_profile_collection.find_one({"userId": user_id})
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert ObjectId to string representation
    user_profile["_id"] = str(user_profile["_id"])

    return user_profile

@app.put("/api/profiles/{userId}")
def update_user_profile(user_id: str, user_profile: UserProfile):
    existing_profile = user_profile_collection.find_one({"userId": user_id})
    if not existing_profile:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the fields in the existing profile
    user_profile_dict = user_profile.dict()
    user_profile_collection.update_one({"userId": user_id}, {"$set": user_profile_dict})

    return user_profile

@app.delete("/api/profiles/{userId}")
def delete_user_profile(user_id: str):
    result = user_profile_collection.delete_one({"userId": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User profile deleted"}

@app.delete("/api/profiles/{userId}/profile-picture", status_code=204)
def delete_profile_picture(user_id: str):
    result = user_profile_collection.update_one({"userId": user_id}, {"$unset": {"profilePictureUrl": ""}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Profile picture deleted"}


from bson import ObjectId

@app.get("/api/profiles")
def get_all_user_profiles():
    user_profiles = list(user_profile_collection.find())
    # Convert ObjectId to string representation
    for profile in user_profiles:
        profile["_id"] = str(profile["_id"])
    return user_profiles
