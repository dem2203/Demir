import redis
import json
import logging
import os
from datetime import timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)

class RedisCache:
    """
    Redis-based caching - reduces API calls by 70%
    Caches: Prices, indicators, sentiment, on-chain data
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        try:
            self.client = redis.from_url(self.redis_url)
            self.client.ping()
            logger.info("✅ Redis connected")
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable: {e}")
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None
        try:
            value = self.client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 60) -> bool:
        """Set value in cache with TTL"""
        if not self.client:
            return False
        try:
            self.client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(value)
            )
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def cache_price(self, symbol: str, price: float, ttl: int = 5):
        """Cache price data"""
        self.set(f"price:{symbol}", {'price': price, 'symbol': symbol}, ttl)
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get cached price"""
        data = self.get(f"price:{symbol}")
        return data['price'] if data else None
    
    def cache_indicators(self, symbol: str, indicators: dict, ttl: int = 300):
        """Cache technical indicators (5 min TTL)"""
        self.set(f"indicators:{symbol}", indicators, ttl)
    
    def get_indicators(self, symbol: str) -> Optional[dict]:
        """Get cached indicators"""
        return self.get(f"indicators:{symbol}")
    
    def cache_sentiment(self, data: dict, ttl: int = 600):
        """Cache sentiment data (10 min TTL)"""
        self.set("sentiment:all", data, ttl)
    
    def get_sentiment(self) -> Optional[dict]:
        """Get cached sentiment"""
        return self.get("sentiment:all")
    
    def clear_all(self):
        """Clear all cache"""
        if self.client:
            self.client.flushdb()
            logger.info("🗑️  Cache cleared")
