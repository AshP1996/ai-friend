"""
Services package for AI Friend system

Contains external integrations such as Redis, databases,
message queues, and third-party APIs.
"""

# ---- Redis Service ----
from .redis_client import (
    redis_client,
    connect_redis,
    close_redis,
)

__all__ = [
    "redis_client",
    "connect_redis",
    "close_redis",
]
