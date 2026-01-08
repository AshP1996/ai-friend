"""
Performance monitoring and optimization helpers
"""
import time
from typing import Dict, Any
from functools import wraps
from utils.logger import Logger

logger = Logger("PerformanceMonitor")

class PerformanceMonitor:
    """Track and optimize performance metrics"""
    
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "avg_response_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "agent_timeouts": 0,
            "llm_timeouts": 0
        }
        self.response_times = []
    
    def track_response_time(self, duration: float):
        """Track response time for averaging"""
        self.response_times.append(duration)
        if len(self.response_times) > 100:  # Keep last 100
            self.response_times.pop(0)
        
        self.metrics["total_requests"] += 1
        self.metrics["avg_response_time"] = sum(self.response_times) / len(self.response_times)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            **self.metrics,
            "p95_response_time": self._percentile(95),
            "p99_response_time": self._percentile(99),
            "min_response_time": min(self.response_times) if self.response_times else 0,
            "max_response_time": max(self.response_times) if self.response_times else 0
        }
    
    def _percentile(self, p: int) -> float:
        """Calculate percentile"""
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * p / 100)
        return sorted_times[min(index, len(sorted_times) - 1)]


def track_performance(func):
    """Decorator to track function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            duration = time.perf_counter() - start
            if duration > 1.0:  # Log slow operations
                logger.debug(f"{func.__name__} took {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.perf_counter() - start
            logger.warning(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    return wrapper

# Global monitor instance
perf_monitor = PerformanceMonitor()
