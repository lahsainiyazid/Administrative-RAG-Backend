import certifi
from pymongo import MongoClient
from app.config import MONGODB_URI

mongo_client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
collection = mongo_client["rag_db"]["chunks"]
