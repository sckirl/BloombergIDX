import redis
import json
import decimal
from datetime import date, datetime
from .database import settings
from .logger import logger

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        # Handle Decimal (including variants from different modules)
        if isinstance(obj, decimal.Decimal) or (hasattr(obj, '__class__') and obj.__class__.__name__ == 'Decimal'):
            return float(obj)
        # Handle dates and datetimes
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super(CustomEncoder, self).default(obj)

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
        logger.error(f"Cache get error: {key} - {e}")
        return None

def set_cache(key: str, value: any, ttl: int = 300):
    if not redis_client: return
    try:
        # We don't use decode_responses=True for the whole client if we want to store raw JSON strings easily?
        # Actually decode_responses=True means get() returns strings, which is fine for json.loads.
        serialized = json.dumps(value, cls=CustomEncoder)
        redis_client.setex(key, ttl, serialized)
    except Exception as e:
        logger.error(f"Cache set error for {key}: {e}")

def invalidate_cache(pattern: str):
    if not redis_client: return
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache keys for pattern {pattern}")
    except Exception as e:
        logger.error(f"Cache invalidate error: {e}")
