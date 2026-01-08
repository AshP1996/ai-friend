import redis.asyncio as redis
from utils.logger import Logger
import os

logger = Logger("RedisClient")

redis_client = None
redis_available = False

async def connect_redis():
    """Connect to Redis with graceful failure handling"""
    global redis_client, redis_available
    
    # Get Redis URL from environment or use default
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    try:
        redis_client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2,  # 2 second timeout
            socket_timeout=2
        )
        await redis_client.ping()
        redis_available = True
        logger.info("✅ Redis connected successfully")
    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed: {e}")
        logger.warning("⚠️ Continuing without Redis (caching and rate limiting disabled)")
        redis_client = None
        redis_available = False

async def close_redis():
    """Close Redis connection if available"""
    global redis_client, redis_available
    if redis_client:
        try:
            await redis_client.close()
            logger.info("🔌 Redis connection closed")
        except Exception as e:
            logger.debug(f"Error closing Redis: {e}")
        finally:
            redis_client = None
            redis_available = False

def is_redis_available():
    """Check if Redis is available"""
    return redis_available and redis_client is not None
