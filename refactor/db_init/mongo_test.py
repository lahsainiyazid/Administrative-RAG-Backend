import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI")

if not mongo_uri:
    raise ValueError("MONGODB_URI not found in .env")

print("Connecting to MongoDB...")

try:
    client = MongoClient(
        mongo_uri,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )

    # 1. Test connection
    client.admin.command("ping")
    print("✅ MongoDB connection successful")

    # 2. Check database
    db = client["rag_db"]
    print("Database:", db.name)

    # 3. Check collection
    collection = db["chunks"]
    print("Collection:", collection.name)

    # 4. READ ONLY — count documents
    count = collection.count_documents({})
    print("Number of chunks:", count)

    # 5. READ ONLY — inspect one document
    document = collection.find_one({})

    if document:
        print("\nExample document:")
        print("ID:", document.get("_id"))
        print("source:", document.get("source"))
        print("chunk id:", document.get("id"))
        print("text preview:", document.get("text", "")[:150])
    else:
        print("⚠️ Collection is empty")

    print("\n✅ MongoDB read-only test passed")

except Exception as e:
    print("\n❌ MongoDB test failed")
    print(type(e).__name__, ":", e)

finally:
    try:
        client.close()
        print("MongoDB connection closed")
    except:
        pass
