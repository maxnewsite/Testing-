import redis
from app.core.config import settings

# Redis client for caching
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_cache(key: str):
    """Get value from cache"""
    try:
        return redis_client.get(key)
    except Exception as e:
        print(f"Redis get error: {e}")
        return None


def set_cache(key: str, value: str, expire: int = 3600):
    """Set value in cache with expiration (default 1 hour)"""
    try:
        redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"Redis set error: {e}")
        return False


def delete_cache(key: str):
    """Delete key from cache"""
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Redis delete error: {e}")
        return False


def clear_pattern(pattern: str):
    """Delete all keys matching pattern"""
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
        return True
    except Exception as e:
        print(f"Redis clear pattern error: {e}")
        return False
