import redis.asyncio as redis
from core.config import config

redis_client = None

async def connect_redis():
    global redis_client
    redis_client = redis.from_url(
        config.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    await redis_client.ping()

async def close_redis():
    if redis_client:
        await redis_client.close()
