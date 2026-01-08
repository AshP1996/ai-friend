"""
Response caching for lightning-fast repeated queries
"""
import hashlib
import json
from typing import Optional, Dict, Any
from services.redis_client import redis_client
from utils.logger import Logger
import asyncio

logger = Logger("ResponseCache")

class ResponseCache:
    """Cache LLM responses to avoid redundant API calls"""
    
    def __init__(self, ttl: int = 3600):  # 1 hour default
        self.ttl = ttl
        self.cache_hits = 0
        self.cache_misses = 0
    
    def _generate_key(self, messages: list, context: Dict[str, Any]) -> str:
        """Generate cache key from messages and context"""
        # Use last user message + key context fields
        last_message = messages[-1].get('content', '') if messages else ''
        context_key = json.dumps({
            'emotion': context.get('emotion', {}).get('emotion', 'neutral'),
            'user': context.get('user', 'default')
        }, sort_keys=True)
        
        cache_string = f"{last_message.lower().strip()}:{context_key}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    async def get(self, messages: list, context: Dict[str, Any]) -> Optional[str]:
        """Get cached response if available"""
        if not redis_client:
            return None
        
        try:
            cache_key = f"response:{self._generate_key(messages, context)}"
            cached = await redis_client.get(cache_key)
            
            if cached:
                self.cache_hits += 1
                logger.debug(f"Cache HIT: {cache_key[:16]}")
                return cached
            
            self.cache_misses += 1
            return None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    async def set(self, messages: list, context: Dict[str, Any], response: str):
        """Cache response for future use"""
        if not redis_client:
            return
        
        try:
            cache_key = f"response:{self._generate_key(messages, context)}"
            await redis_client.setex(cache_key, self.ttl, response)
            logger.debug(f"Cached response: {cache_key[:16]}")
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
    
    async def clear_user_cache(self, user_id: str):
        """Clear all cached responses for a user"""
        if not redis_client:
            return
        
        try:
            pattern = f"response:*"
            keys = await redis_client.keys(pattern)
            if keys:
                await redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cached responses")
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate": round(hit_rate, 2)
        }

# Global cache instance
response_cache = ResponseCache()
