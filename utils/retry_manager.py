# utils/retry_manager.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 DEMIR AI v7.0 - RETRY MANAGER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROFESSIONAL RETRY LOGIC WITH EXPONENTIAL BACKOFF

Features:
    ✅ Exponential backoff with jitter
    ✅ Configurable max attempts
    ✅ Decorator support
    ✅ Production-grade error handling

DEPLOYMENT: Railway Production
AUTHOR: DEMIR AI Research Team
DATE: 2025-11-19
VERSION: 7.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import logging
from functools import wraps
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)

# ============================================================================
# RETRY STRATEGY
# ============================================================================

class RetryStrategy:
    """Exponential backoff retry strategy"""
    
    def __init__(
        self,
        max_attempts: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 60.0
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt"""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        return delay + (0.1 * attempt)  # Add jitter
    
    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """Retry function with exponential backoff"""
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.max_attempts}: {func.__name__}")
                return func(*args, **kwargs)
            
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_attempts - 1:
                    delay = self.get_delay(attempt)
                    logger.warning(f"⚠️ {func.__name__} failed: {e}. Retry in {delay:.1f}s")
                    time.sleep(delay)
                else:
                    logger.error(f"❌ {func.__name__} failed after {self.max_attempts} attempts")
        
        raise last_exception

# ============================================================================
# RETRY MANAGER (for backward compatibility)
# ============================================================================

class RetryManager:
    """
    Retry manager with exponential backoff
    
    Compatible interface for legacy code
    """
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.strategy = RetryStrategy(max_retries, base_delay)
    
    def execute(self, func: Callable, *args, **kwargs) -> Optional[Any]:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Function result or None
        """
        try:
            return self.strategy.retry(func, *args, **kwargs)
        except Exception as e:
            logger.error(f"All retries failed: {e}")
            return None

# ============================================================================
# DECORATOR
# ============================================================================

def retry_on_exception(max_attempts: int = 5, base_delay: float = 1.0):
    """Decorator for automatic retry"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            strategy = RetryStrategy(max_attempts, base_delay)
            return strategy.retry(func, *args, **kwargs)
        return wrapper
    return decorator
