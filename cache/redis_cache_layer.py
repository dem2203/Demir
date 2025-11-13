"""
REDIS CACHE LAYER
Real-time veri caching - performance optimization

⚠️ REAL DATA: Redis'e gerçek veri cache'le
"""

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

from typing import Dict, Any, Optional
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RedisCacheLayer:
    """
    Redis cache management
    Real-time data'yı cache'le
    """
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """
        Initialize Redis client
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
        """
        
        if not HAS_REDIS:
            logger.warning("⚠️ Redis not installed - using fallback in-memory cache")
            self.redis_client = None
            self.fallback_cache = {}
            return
        
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5
            )
            
            # Connection test
            self.redis_client.ping()
            logger.info("✅ Redis connected")
        
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e} - Using fallback cache")
            self.redis_client = None
            self.fallback_cache = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Cache'den veri al
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None
        """
        
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                return self.fallback_cache.get(key)
        
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """
        Veriyi cache'e kaydet
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live (seconds)
        """
        
        try:
            value_str = json.dumps(value, default=str)
            
            if self.redis_client:
                self.redis_client.setex(key, ttl_seconds, value_str)
            else:
                self.fallback_cache[key] = {
                    'value': value,
                    'expires_at': datetime.now() + timedelta(seconds=ttl_seconds)
                }
            
            logger.debug(f"✅ Cache set: {key} (TTL: {ttl_seconds}s)")
        
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
    
    async def delete(self, key: str):
        """Cache'den sil"""
        
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.fallback_cache.pop(key, None)
        
        except Exception as e:
            logger.warning(f"Cache delete failed: {e}")
    
    async def clear_all(self):
        """Tüm cache'i temizle"""
        
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                self.fallback_cache.clear()
            
            logger.info("✅ Cache cleared")
        
        except Exception as e:
            logger.warning(f"Cache clear failed: {e}")
    
    async def get_stats(self) -> Dict:
        """Cache istatistikleri"""
        
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    'used_memory': info.get('used_memory_human'),
                    'connected_clients': info.get('connected_clients'),
                    'keys': self.redis_client.dbsize()
                }
            else:
                return {
                    'cache_type': 'FALLBACK_IN_MEMORY',
                    'items': len(self.fallback_cache)
                }
        
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {'error': str(e)}
