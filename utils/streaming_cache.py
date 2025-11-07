"""
🔮 PHASE 8.4 - STREAMING CACHE & ASYNC EXECUTOR v1.0
====================================================

Path: utils/streaming_cache.py
Date: 7 Kasım 2025, 15:08 CET

Cache layer results, async execution, rate limiting, error recovery.
"""

import time
import threading
from collections import OrderedDict
from datetime import datetime, timedelta
import json

class StreamingCache:
    """In-memory cache with TTL"""
    
    def __init__(self, ttl_seconds=300):  # 5 min default
        self.cache = OrderedDict()
        self.ttl = ttl_seconds
        self.lock = threading.Lock()
    
    def get(self, key):
        """Get cached value if not expired"""
        with self.lock:
            if key not in self.cache:
                return None
            
            value, expiry = self.cache[key]
            if datetime.now() > expiry:
                del self.cache[key]
                return None
            
            return value
    
    def set(self, key, value, ttl=None):
        """Set cache value with TTL"""
        with self.lock:
            expiry = datetime.now() + timedelta(seconds=ttl or self.ttl)
            self.cache[key] = (value, expiry)
            
            # Keep cache size manageable
            if len(self.cache) > 1000:
                self.cache.popitem(last=False)
    
    def clear_expired(self):
        """Remove all expired entries"""
        with self.lock:
            now = datetime.now()
            expired = [k for k, (v, exp) in self.cache.items() 
                      if now > exp]
            for k in expired:
                del self.cache[k]
    
    def stats(self):
        """Cache statistics"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': 1000
            }


class RateLimiter:
    """Rate limit API calls"""
    
    def __init__(self, max_per_second=10):
        self.max_per_second = max_per_second
        self.calls = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        """Wait if rate limit exceeded"""
        with self.lock:
            now = time.time()
            
            # Remove old calls
            self.calls = [t for t in self.calls if now - t < 1.0]
            
            if len(self.calls) >= self.max_per_second:
                wait_time = 1.0 - (now - self.calls[0])
                if wait_time > 0:
                    time.sleep(wait_time)
            
            self.calls.append(time.time())
    
    def call(self, func, *args, **kwargs):
        """Call function with rate limiting"""
        self.wait_if_needed()
        return func(*args, **kwargs)


class AsyncLayerExecutor:
    """Execute layers in parallel threads"""
    
    def __init__(self, cache=None, rate_limiter=None):
        self.cache = cache or StreamingCache()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.results = {}
        self.errors = {}
        self.lock = threading.Lock()
    
    def execute_layer(self, layer_name, layer_func, symbol, timeout=5):
        """
        Execute single layer function
        Cache result
        """
        cache_key = f"{layer_name}_{symbol}"
        
        # Check cache first
        cached = self.cache.get(cache_key)
        if cached:
            with self.lock:
                self.results[layer_name] = cached
            return
        
        try:
            # Rate limit API calls
            result = self.rate_limiter.call(layer_func, symbol)
            
            if result is None:
                result = {'score': 50, 'signal': 'NEUTRAL', 'source': 'FALLBACK'}
            
            # Cache result
            self.cache.set(cache_key, result, ttl=300)  # 5 min
            
            with self.lock:
                self.results[layer_name] = result
        
        except Exception as e:
            with self.lock:
                self.errors[layer_name] = str(e)
                self.results[layer_name] = {
                    'score': 50, 
                    'signal': 'NEUTRAL', 
                    'source': 'FALLBACK',
                    'error': str(e)
                }
    
    def execute_all_layers(self, layer_config, symbol, timeout=30):
        """
        Execute all layers in parallel
        
        Args:
            layer_config: dict {layer_name: layer_func}
            symbol: trading symbol
            timeout: max wait time
        
        Returns:
            {layer_name: result}
        """
        self.results = {}
        self.errors = {}
        threads = []
        
        start = time.time()
        
        # Start all threads
        for layer_name, layer_func in layer_config.items():
            t = threading.Thread(
                target=self.execute_layer,
                args=(layer_name, layer_func, symbol),
                daemon=True
            )
            t.start()
            threads.append(t)
        
        # Wait for all threads with timeout
        for t in threads:
            elapsed = time.time() - start
            remaining = max(0, timeout - elapsed)
            t.join(timeout=remaining)
        
        return self.results
    
    def get_error_report(self):
        """Get errors from execution"""
        with self.lock:
            return self.errors.copy()


class ErrorRecoveryManager:
    """Manage fallback chains"""
    
    def __init__(self):
        self.error_history = {}  # layer -> [error_count, last_error_time]
        self.failed_threshold = 3  # Disable after 3 failures
    
    def record_error(self, layer_name):
        """Record layer error"""
        if layer_name not in self.error_history:
            self.error_history[layer_name] = [0, datetime.now()]
        
        self.error_history[layer_name][0] += 1
        self.error_history[layer_name][1] = datetime.now()
    
    def is_layer_healthy(self, layer_name):
        """Check if layer should be called"""
        if layer_name not in self.error_history:
            return True
        
        error_count, last_error = self.error_history[layer_name]
        
        # Disable if too many errors
        if error_count > self.failed_threshold:
            return False
        
        # Re-enable after 5 minutes
        if datetime.now() - last_error > timedelta(minutes=5):
            self.error_history[layer_name] = [0, datetime.now()]
            return True
        
        return error_count <= self.failed_threshold
    
    def reset_errors(self, layer_name):
        """Reset error count for layer"""
        if layer_name in self.error_history:
            self.error_history[layer_name] = [0, datetime.now()]


# Global instances
_cache = StreamingCache(ttl_seconds=300)
_rate_limiter = RateLimiter(max_per_second=20)
_executor = AsyncLayerExecutor(_cache, _rate_limiter)
_recovery = ErrorRecoveryManager()


def execute_layers_async(layer_config, symbol, timeout=30):
    """
    Main function: execute all layers asynchronously
    
    Args:
        layer_config: {layer_name: layer_func}
        symbol: trading symbol
        timeout: max execution time
    
    Returns:
        {layer_name: result}
    """
    # Filter unhealthy layers
    healthy_config = {
        name: func for name, func in layer_config.items()
        if _recovery.is_layer_healthy(name)
    }
    
    results = _executor.execute_all_layers(healthy_config, symbol, timeout)
    
    # Record errors
    errors = _executor.get_error_report()
    for layer_name in errors:
        _recovery.record_error(layer_name)
    
    return results


def get_cache_stats():
    """Get cache performance stats"""
    return {
        'cache': _cache.stats(),
        'error_layers': [k for k, v in _recovery.error_history.items() 
                        if v[0] > 0]
    }


def clear_all_cache():
    """Clear all cached data"""
    _cache.cache.clear()
