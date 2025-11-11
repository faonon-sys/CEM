"""
Advanced Caching System for Performance Optimization
Implements Redis-based caching with TTL management
"""
import redis
import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
import asyncio
from datetime import timedelta
import os


class CacheManager:
    """Redis-based cache manager with automatic TTL and invalidation"""

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        default_ttl: int = 3600
    ):
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        self.default_ttl = default_ttl
        print(f"✅ Cache Manager initialized (Redis: {redis_host}:{redis_port})")

    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate deterministic cache key from function arguments"""
        # Serialize arguments
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        # Hash for consistent length
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()
        return f"cache:{prefix}:{key_hash}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            print(f"⚠️ Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with TTL"""
        try:
            serialized = json.dumps(value)
            ttl = ttl or self.default_ttl
            self.redis_client.setex(key, ttl, serialized)
        except (redis.RedisError, TypeError) as e:
            print(f"⚠️ Cache set error: {e}")

    def delete(self, key: str):
        """Delete key from cache"""
        try:
            self.redis_client.delete(key)
        except redis.RedisError as e:
            print(f"⚠️ Cache delete error: {e}")

    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                print(f"✅ Invalidated {len(keys)} cache keys matching {pattern}")
        except redis.RedisError as e:
            print(f"⚠️ Cache invalidation error: {e}")

    def cached(
        self,
        prefix: str,
        ttl: Optional[int] = None,
        skip_cache_if: Optional[Callable] = None
    ):
        """
        Decorator for caching function results

        Args:
            prefix: Cache key prefix for this function
            ttl: Time to live in seconds (None = use default)
            skip_cache_if: Function that returns True to skip cache
        """
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Check if we should skip cache
                if skip_cache_if and skip_cache_if(*args, **kwargs):
                    return await func(*args, **kwargs)

                # Generate cache key
                cache_key = self._generate_cache_key(prefix, *args, **kwargs)

                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    print(f"✅ Cache hit: {prefix}")
                    return cached_result

                # Cache miss - execute function
                print(f"⚠️ Cache miss: {prefix}")
                result = await func(*args, **kwargs)

                # Store in cache
                self.set(cache_key, result, ttl)

                return result

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Check if we should skip cache
                if skip_cache_if and skip_cache_if(*args, **kwargs):
                    return func(*args, **kwargs)

                # Generate cache key
                cache_key = self._generate_cache_key(prefix, *args, **kwargs)

                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    print(f"✅ Cache hit: {prefix}")
                    return cached_result

                # Cache miss - execute function
                print(f"⚠️ Cache miss: {prefix}")
                result = func(*args, **kwargs)

                # Store in cache
                self.set(cache_key, result, ttl)

                return result

            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator


# Global cache instance
cache_manager = CacheManager(
    redis_host=os.getenv("REDIS_HOST", "localhost"),
    redis_port=int(os.getenv("REDIS_PORT", 6379)),
    default_ttl=3600  # 1 hour default
)


# Specialized cache decorators for common use cases
def cache_llm_response(ttl: int = 7200):
    """
    Cache LLM responses for 2 hours
    LLM responses are expensive and deterministic for same input
    """
    return cache_manager.cached(prefix="llm", ttl=ttl)


def cache_analysis_result(ttl: int = 3600):
    """
    Cache analysis results for 1 hour
    Full workflow results
    """
    return cache_manager.cached(prefix="analysis", ttl=ttl)


def cache_database_query(ttl: int = 300):
    """
    Cache database queries for 5 minutes
    Frequently accessed data
    """
    return cache_manager.cached(prefix="db_query", ttl=ttl)


# Cache statistics
class CacheStats:
    """Track cache performance metrics"""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.errors = 0

    def record_hit(self):
        self.hits += 1

    def record_miss(self):
        self.misses += 1

    def record_error(self):
        self.errors += 1

    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def get_stats(self) -> dict:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
            "hit_rate": self.get_hit_rate(),
            "total_requests": self.hits + self.misses
        }


cache_stats = CacheStats()


# Example usage with LLM service
class CachedLLMService:
    """LLM service with automatic response caching"""

    def __init__(self, llm_provider):
        self.llm_provider = llm_provider

    @cache_llm_response(ttl=7200)
    async def generate_assumptions(self, scenario_text: str) -> dict:
        """
        Generate assumptions with caching
        Same scenario = same assumptions (deterministic with temperature=0)
        """
        return await self.llm_provider.generate_assumptions(scenario_text)

    @cache_llm_response(ttl=7200)
    async def generate_questions(self, assumptions: list) -> dict:
        """Generate questions with caching"""
        # Convert list to string for caching (lists aren't hashable)
        assumptions_str = json.dumps(assumptions, sort_keys=True)
        return await self.llm_provider.generate_questions(assumptions_str)

    @cache_llm_response(ttl=7200)
    async def generate_counterfactuals(self, scenario: str, assumptions: list) -> dict:
        """Generate counterfactuals with caching"""
        assumptions_str = json.dumps(assumptions, sort_keys=True)
        return await self.llm_provider.generate_counterfactuals(scenario, assumptions_str)


if __name__ == "__main__":
    # Test cache manager
    print("Testing Cache Manager...")

    # Set and get
    cache_manager.set("test_key", {"data": "test_value"}, ttl=10)
    result = cache_manager.get("test_key")
    print(f"Cached value: {result}")

    # Test decorator
    @cache_manager.cached(prefix="test_func", ttl=60)
    def expensive_function(x: int) -> int:
        print(f"Computing {x}^2...")
        return x ** 2

    # First call - cache miss
    result1 = expensive_function(5)
    print(f"Result 1: {result1}")

    # Second call - cache hit
    result2 = expensive_function(5)
    print(f"Result 2: {result2}")

    print("\n✅ Cache manager tests passed")
