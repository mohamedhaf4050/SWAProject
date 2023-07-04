




# Connect to MongoDB
import os
from pymongo import MongoClient


client = MongoClient(f"mongodb://root:example@{os.getenv('MONGO_HOST')}/")
db = client["elearningDB"]
collection = db["modules"]