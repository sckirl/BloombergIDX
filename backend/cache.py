import redis
import json
from .database import settings
from .logger import logger

try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    logger.info(f"Redis connected at {settings.REDIS_URL}")
except Exception as e:
    logger.error(f"Redis connection failed: {e}")
    redis_client = None

def get_cache(key: str):
    if not redis_client: return None
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None

def set_cache(key: str, value: any, ttl: int = 300):
    if not redis_client: return
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.error(f"Cache set error: {e}")

def invalidate_cache(pattern: str):
    if not redis_client: return
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache keys for pattern {pattern}")
    except Exception as e:
        logger.error(f"Cache invalidate error: {e}")
