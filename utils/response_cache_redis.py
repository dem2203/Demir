"""
DEMIR AI BOT - Response Cache Redis
Smart caching with TTL management and invalidation
Reduces API calls and improves performance
"""

import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import json
import hashlib

logger = logging.getLogger(__name__)


class ResponseCache:
    """
    In-memory cache for API responses.
    Production version would use Redis.
    This is local implementation for Railway.
    """

    def __init__(self, default_ttl_seconds: int = 300):
        """Initialize cache."""
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl_seconds

    def generate_key(self, api_name: str, params: Dict[str, Any]) -> str:
        """Generate cache key from API name and parameters."""
        params_str = json.dumps(params, sort_keys=True)
        hash_obj = hashlib.md5(params_str.encode())
        return f"{api_name}:{hash_obj.hexdigest()}"

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None
    ) -> None:
        """Set cache entry with TTL."""
        ttl = ttl_seconds or self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)

        self.cache[key] = {
            'value': value,
            'expiry': expiry.timestamp(),
            'created': datetime.now().timestamp()
        }

        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")

    def get(self, key: str) -> Optional[Any]:
        """Get cache entry if not expired."""
        if key not in self.cache:
            logger.debug(f"Cache MISS: {key}")
            return None

        entry = self.cache[key]

        # Check if expired
        if datetime.now().timestamp() > entry['expiry']:
            del self.cache[key]
            logger.debug(f"Cache EXPIRED: {key}")
            return None

        logger.debug(f"Cache HIT: {key}")
        return entry['value']

    def invalidate(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern."""
        keys_to_delete = [k for k in self.cache.keys() if pattern in k]

        for key in keys_to_delete:
            del self.cache[key]

        logger.info(f"Cache invalidated {len(keys_to_delete)} entries matching '{pattern}'")
        return len(keys_to_delete)

    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self.cache)
        expired_count = 0
        now = datetime.now().timestamp()

        for entry in self.cache.values():
            if now > entry['expiry']:
                expired_count += 1

        return {
            'total_entries': total_entries,
            'expired_entries': expired_count,
            'active_entries': total_entries - expired_count,
            'memory_estimate_kb': len(str(self.cache)) / 1024
        }

    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        now = datetime.now().timestamp()
        keys_to_delete = [
            k for k, v in self.cache.items()
            if now > v['expiry']
        ]

        for key in keys_to_delete:
            del self.cache[key]

        if keys_to_delete:
            logger.info(f"Cleaned up {len(keys_to_delete)} expired cache entries")

        return len(keys_to_delete)

    def get_hit_rate(self) -> float:
        """Get estimated cache hit rate."""
        if not hasattr(self, '_hits'):
            self._hits = 0
            self._misses = 0

        total = self._hits + self._misses
        if total == 0:
            return 0.0

        return (self._hits / total) * 100
