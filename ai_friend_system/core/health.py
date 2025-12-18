from ..services.redis_client import connect_redis
from .config import settings

async def run_health_checks():
    if not settings.REDIS_URL:
        raise RuntimeError("REDIS_URL missing")

    await connect_redis()

    # Optional AI checks
    if settings.ENV == "production" and not settings.OPENAI_API_KEY:
        raise RuntimeError("OpenAI key missing")
