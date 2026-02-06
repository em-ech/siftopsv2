"""
Caching Layer
In-memory cache with TTL support for search results and embeddings.

For production, consider using Redis for distributed caching.
"""

import time
import hashlib
import asyncio
from typing import Any, Optional, Callable, TypeVar
from functools import wraps
from collections import OrderedDict

T = TypeVar('T')


class Cache:
    """
    In-memory cache with TTL (Time-To-Live) support.

    Features:
    - Automatic expiration of entries
    - LRU eviction when max size reached
    - Thread-safe operations
    - Async-compatible

    For production with multiple workers, use Redis instead.
    """

    def __init__(
        self,
        default_ttl: int = 300,  # 5 minutes default
        max_size: int = 1000,
        name: str = "cache",
    ):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.name = name
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = asyncio.Lock()

    def _is_expired(self, expiry: float) -> bool:
        """Check if an entry has expired."""
        return time.time() > expiry

    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_data = f"{args}:{sorted(kwargs.items())}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Returns None if not found or expired.
        """
        async with self._lock:
            if key not in self._cache:
                return None

            value, expiry = self._cache[key]

            if self._is_expired(expiry):
                del self._cache[key]
                return None

            # Move to end (LRU)
            self._cache.move_to_end(key)
            return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        ttl = ttl if ttl is not None else self.default_ttl
        expiry = time.time() + ttl

        async with self._lock:
            # Evict oldest if at max size
            while len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)

            self._cache[key] = (value, expiry)

    async def delete(self, key: str) -> bool:
        """Delete a key from cache. Returns True if key existed."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> int:
        """Clear all entries. Returns count of cleared entries."""
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    async def cleanup_expired(self) -> int:
        """Remove all expired entries. Returns count of removed entries."""
        now = time.time()
        async with self._lock:
            expired_keys = [
                k for k, (_, expiry) in self._cache.items()
                if now > expiry
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)

    def stats(self) -> dict:
        """Get cache statistics."""
        now = time.time()
        active = sum(1 for _, (_, expiry) in self._cache.items() if now <= expiry)
        return {
            "name": self.name,
            "total_entries": len(self._cache),
            "active_entries": active,
            "expired_entries": len(self._cache) - active,
            "max_size": self.max_size,
            "default_ttl": self.default_ttl,
        }


def cached(
    cache: Cache,
    key_func: Optional[Callable[..., str]] = None,
    ttl: Optional[int] = None,
):
    """
    Decorator for caching async function results.

    Args:
        cache: Cache instance to use
        key_func: Function to generate cache key from arguments
        ttl: Override TTL for this function

    Example:
        @cached(search_cache, key_func=lambda q, t: f"{t}:{hash(q)}")
        async def search(query: str, tenant_id: str) -> list:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = cache._generate_key(*args, **kwargs)

            # Check cache
            cached_value = await cache.get(key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await cache.set(key, result, ttl)

            return result

        return wrapper
    return decorator


# ==================== CACHE INSTANCES ====================

# Search results cache (short TTL - results change with inventory)
search_cache = Cache(
    default_ttl=300,  # 5 minutes
    max_size=1000,
    name="search_cache",
)

# Embedding cache (longer TTL - embeddings are deterministic)
embedding_cache = Cache(
    default_ttl=3600,  # 1 hour
    max_size=5000,
    name="embedding_cache",
)

# Query understanding cache (medium TTL)
query_cache = Cache(
    default_ttl=600,  # 10 minutes
    max_size=500,
    name="query_cache",
)
