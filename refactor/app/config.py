import os
from dotenv import load_dotenv,find_dotenv 

load_dotenv(find_dotenv())

REDIS_URL = os.getenv("UPSTASH_REDIS_URL")
if not REDIS_URL:
    raise ValueError("UPSTASH_REDIS_URL not found in .env file!")

MONGODB_URI = os.getenv("MONGODB_URI")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
