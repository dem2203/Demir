"""
Utils module for DEMIR AI
Contains: Retry, Telegram Queue, Parallel Analyzer, Caching, etc.
"""

import logging

logger = logging.getLogger(__name__)

# Import all utility classes for easy access
try:
    from .retry_manager import RetryStrategy, retry_on_exception
    logger.info("✅ Retry manager imported")
except ImportError as e:
    logger.warning(f"⚠️ Retry manager not available: {e}")
    RetryStrategy = None
    retry_on_exception = None

try:
    from .telegram_queue import TelegramAlertQueue
    logger.info("✅ Telegram queue imported")
except ImportError as e:
    logger.warning(f"⚠️ Telegram queue not available: {e}")
    TelegramAlertQueue = None

try:
    from .parallel_analyzer import ParallelAnalyzer
    logger.info("✅ Parallel analyzer imported")
except ImportError as e:
    logger.warning(f"⚠️ Parallel analyzer not available: {e}")
    ParallelAnalyzer = None

try:
    from .redis_cache import RedisCache
    logger.info("✅ Redis cache imported")
except ImportError as e:
    logger.warning(f"⚠️ Redis cache not available: {e}")
    RedisCache = None

try:
    from .model_trainer import IncrementalModelTrainer
    logger.info("✅ Model trainer imported")
except ImportError as e:
    logger.warning(f"⚠️ Model trainer not available: {e}")
    IncrementalModelTrainer = None

try:
    from .ab_testing import ABTestingEngine
    logger.info("✅ A/B testing imported")
except ImportError as e:
    logger.warning(f"⚠️ A/B testing not available: {e}")
    ABTestingEngine = None

try:
    from .circuit_breaker import CircuitBreaker, CircuitState
    logger.info("✅ Circuit breaker imported")
except ImportError as e:
    logger.warning(f"⚠️ Circuit breaker not available: {e}")
    CircuitBreaker = None
    CircuitState = None

try:
    from .multi_exchange_failover import MultiExchangeFailover
    logger.info("✅ Multi-exchange failover imported")
except ImportError as e:
    logger.warning(f"⚠️ Multi-exchange failover not available: {e}")
    MultiExchangeFailover = None

try:
    from .backtest_integration import BacktestIntegration
    logger.info("✅ Backtest integration imported")
except ImportError as e:
    logger.warning(f"⚠️ Backtest integration not available: {e}")
    BacktestIntegration = None

try:
    from .model_versioning import ModelVersionManager
    logger.info("✅ Model versioning imported")
except ImportError as e:
    logger.warning(f"⚠️ Model versioning not available: {e}")
    ModelVersionManager = None

# Export all
__all__ = [
    'RetryStrategy',
    'retry_on_exception',
    'TelegramAlertQueue',
    'ParallelAnalyzer',
    'RedisCache',
    'IncrementalModelTrainer',
    'ABTestingEngine',
    'CircuitBreaker',
    'CircuitState',
    'MultiExchangeFailover',
    'BacktestIntegration',
    'ModelVersionManager'
]

logger.info(f"✅ Utils module initialized ({len([x for x in __all__ if x])} utilities available)")
