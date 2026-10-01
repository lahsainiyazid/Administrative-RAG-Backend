import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

# Get Redis URL from .env
redis_url = os.getenv("UPSTASH_REDIS_URL")

if not redis_url:
    raise ValueError("UPSTASH_REDIS_URL not found in .env")

print("Redis URL found:", redis_url[:30] + "...")

# Create Redis client
redis_client = redis.from_url(
    redis_url,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5
)

# -------------------------
# 1. PING TEST
# -------------------------

print("\n--- PING TEST ---")

try:
    result = redis_client.ping()
    print("Redis PING:", result)
except Exception as e:
    print("❌ PING FAILED")
    print(type(e).__name__, ":", e)
    exit()


# -------------------------
# 2. SET TEST
# -------------------------

print("\n--- SET TEST ---")

try:
    redis_client.set(
        "test_key",
        "hello_redis",
        ex=60
    )
    print("✅ SET successful")
except Exception as e:
    print("❌ SET FAILED")
    print(type(e).__name__, ":", e)
    exit()


# -------------------------
# 3. GET TEST
# -------------------------

print("\n--- GET TEST ---")

try:
    value = redis_client.get("test_key")

    print("Value:", value)

    if value == "hello_redis":
        print("✅ GET successful")
    else:
        print("❌ GET returned unexpected value")

except Exception as e:
    print("❌ GET FAILED")
    print(type(e).__name__, ":", e)
    exit()


# -------------------------
# 4. RAG CACHE TEST
# -------------------------

print("\n--- RAG CACHE TEST ---")

try:
    cache_key = "rag_cache:test_question"

    response = {
        "Question": "What is RAG?",
        "Answer": "Retrieval-Augmented Generation",
        "cached": False
    }

    # Store
    redis_client.setex(
        cache_key,
        86400,
        json.dumps(response)
    )

    print("✅ RAG cache SET successful")

    # Retrieve
    cached = redis_client.get(cache_key)

    if cached:
        cached_data = json.loads(cached)

        print("Retrieved:", cached_data)
        print("✅ RAG cache GET successful")
    else:
        print("❌ RAG cache GET returned nothing")

except Exception as e:
    print("❌ RAG CACHE TEST FAILED")
    print(type(e).__name__, ":", e)


# -------------------------
# 5. CLEANUP
# -------------------------

print("\n--- CLEANUP ---")

try:
    redis_client.delete("test_key")
    redis_client.delete("rag_cache:test_question")

    print("✅ Test keys deleted")

except Exception as e:
    print("Cleanup error:", e)


print("\n======================")
print("Redis test completed")
print("======================")
