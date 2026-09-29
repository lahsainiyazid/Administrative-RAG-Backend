import redis
from app.config import REDIS_URL

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2
)

def clear_cache():
    try:
        keys = redis_client.keys('rag_cache:*')
        if keys:
            redis_client.delete(*keys)
    except Exception as e:
        print(f"Error:{e} while clearing the cache!")
