#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════════════════
ParallelAnalyzer ENTERPRISE - DEMIR AI v8.0
════════════════════════════════════════════════════════════════════════════════
Production-grade parallel processing for multi-symbol/multi-timeframe analysis
- Concurrent analysis of multiple trading pairs
- Thread pool and process pool support
- Rate limiting for API compliance
- Error handling and retry logic
- Progress tracking and monitoring
- Result aggregation and validation
"""

import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime
import time
from functools import wraps

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator for automatic retry on function failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"❌ Failed after {max_retries} attempts: {e}")
                        raise
                    logger.warning(f"⚠️ Attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
        return wrapper
    return decorator


class RateLimiter:
    """
    Rate limiter for API call throttling.
    
    Attributes:
        max_calls: Maximum calls per time window
        time_window: Time window in seconds
    """
    
    def __init__(self, max_calls: int = 100, time_window: float = 60.0):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def wait_if_needed(self):
        """Block if rate limit would be exceeded."""
        now = time.time()
        
        # Remove old calls outside time window
        self.calls = [t for t in self.calls if now - t < self.time_window]
        
        if len(self.calls) >= self.max_calls:
            # Calculate wait time
            oldest_call = min(self.calls)
            wait_time = self.time_window - (now - oldest_call)
            
            if wait_time > 0:
                logger.debug(f"⏳ Rate limit reached, waiting {wait_time:.1f}s")
                time.sleep(wait_time)
                self.calls = []
        
        self.calls.append(now)


class ParallelAnalyzer:
    """
    Enterprise parallel processing system for multi-asset analysis.
    
    Features:
    - Concurrent processing with thread/process pools
    - Rate limiting for API compliance
    - Automatic retry on failures
    - Progress tracking
    - Result validation and aggregation
    
    Attributes:
        max_workers: Maximum concurrent workers
        rate_limiter: API rate limiter
        use_processes: Use ProcessPoolExecutor instead of threads
    """
    
    def __init__(
        self,
        max_workers: int = 10,
        rate_limit_calls: int = 100,
        rate_limit_window: float = 60.0,
        use_processes: bool = False
    ):
        """
        Initialize ParallelAnalyzer.
        
        Args:
            max_workers: Maximum concurrent workers
            rate_limit_calls: Max API calls per time window
            rate_limit_window: Rate limit time window (seconds)
            use_processes: Use processes instead of threads
        """
        self.max_workers = max_workers
        self.rate_limiter = RateLimiter(rate_limit_calls, rate_limit_window)
        self.use_processes = use_processes
        
        logger.info(
            f"✅ ParallelAnalyzer initialized: "
            f"workers={max_workers}, "
            f"rate_limit={rate_limit_calls}/{rate_limit_window}s, "
            f"mode={'process' if use_processes else 'thread'}"
        )
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def _execute_task(
        self,
        task_func: Callable,
        task_args: tuple,
        task_kwargs: dict
    ) -> Any:
        """
        Execute single task with rate limiting and retry logic.
        
        Args:
            task_func: Function to execute
            task_args: Positional arguments
            task_kwargs: Keyword arguments
            
        Returns:
            Task result
        """
        self.rate_limiter.wait_if_needed()
        return task_func(*task_args, **task_kwargs)
    
    def analyze_symbols(
        self,
        symbols: List[str],
        analysis_func: Callable,
        **func_kwargs
    ) -> Dict[str, Any]:
        """
        Analyze multiple symbols in parallel.
        
        Args:
            symbols: List of trading pair symbols
            analysis_func: Function to execute per symbol
            **func_kwargs: Additional arguments for analysis_func
            
        Returns:
            Dictionary of {symbol: result}
        """
        logger.info(f"🔄 Analyzing {len(symbols)} symbols in parallel...")
        start_time = time.time()
        
        results = {}
        errors = {}
        
        # Select executor type
        ExecutorClass = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor
        
        with ExecutorClass(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_symbol = {
                executor.submit(
                    self._execute_task,
                    analysis_func,
                    (symbol,),
                    func_kwargs
                ): symbol
                for symbol in symbols
            }
            
            # Process completed tasks
            completed = 0
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                completed += 1
                
                try:
                    result = future.result()
                    results[symbol] = result
                    logger.debug(f"✅ [{completed}/{len(symbols)}] {symbol} completed")
                    
                except Exception as e:
                    error_msg = str(e)
                    errors[symbol] = error_msg
                    logger.error(f"❌ [{completed}/{len(symbols)}] {symbol} failed: {error_msg}")
        
        elapsed = time.time() - start_time
        
        summary = {
            'total_symbols': len(symbols),
            'successful': len(results),
            'failed': len(errors),
            'duration_seconds': elapsed,
            'results': results,
            'errors': errors
        }
        
        logger.info(
            f"✅ Analysis complete: "
            f"{len(results)}/{len(symbols)} successful in {elapsed:.1f}s"
        )
        
        return summary
    
    def analyze_timeframes(
        self,
        symbol: str,
        timeframes: List[str],
        analysis_func: Callable,
        **func_kwargs
    ) -> Dict[str, Any]:
        """
        Analyze single symbol across multiple timeframes in parallel.
        
        Args:
            symbol: Trading pair symbol
            timeframes: List of timeframes (e.g., ['15m', '1h', '4h'])
            analysis_func: Function to execute per timeframe
            **func_kwargs: Additional arguments
            
        Returns:
            Dictionary of {timeframe: result}
        """
        logger.info(f"🔄 Analyzing {symbol} across {len(timeframes)} timeframes...")
        start_time = time.time()
        
        results = {}
        errors = {}
        
        ExecutorClass = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor
        
        with ExecutorClass(max_workers=self.max_workers) as executor:
            future_to_tf = {
                executor.submit(
                    self._execute_task,
                    analysis_func,
                    (symbol, tf),
                    func_kwargs
                ): tf
                for tf in timeframes
            }
            
            completed = 0
            for future in as_completed(future_to_tf):
                tf = future_to_tf[future]
                completed += 1
                
                try:
                    result = future.result()
                    results[tf] = result
                    logger.debug(f"✅ [{completed}/{len(timeframes)}] {tf} completed")
                    
                except Exception as e:
                    errors[tf] = str(e)
                    logger.error(f"❌ [{completed}/{len(timeframes)}] {tf} failed: {e}")
        
        elapsed = time.time() - start_time
        
        summary = {
            'symbol': symbol,
            'total_timeframes': len(timeframes),
            'successful': len(results),
            'failed': len(errors),
            'duration_seconds': elapsed,
            'results': results,
            'errors': errors
        }
        
        logger.info(
            f"✅ Timeframe analysis complete: "
            f"{len(results)}/{len(timeframes)} successful in {elapsed:.1f}s"
        )
        
        return summary
    
    async def analyze_async(
        self,
        tasks: List[tuple],
        async_func: Callable
    ) -> List[Any]:
        """
        Execute asynchronous analysis tasks.
        
        Args:
            tasks: List of (args, kwargs) tuples
            async_func: Async function to execute
            
        Returns:
            List of results
        """
        logger.info(f"🔄 Running {len(tasks)} async tasks...")
        
        async def rate_limited_task(args, kwargs):
            self.rate_limiter.wait_if_needed()
            return await async_func(*args, **kwargs)
        
        results = await asyncio.gather(
            *[rate_limited_task(args, kwargs) for args, kwargs in tasks],
            return_exceptions=True
        )
        
        # Separate successes and errors
        successes = [r for r in results if not isinstance(r, Exception)]
        errors = [r for r in results if isinstance(r, Exception)]
        
        logger.info(
            f"✅ Async analysis complete: "
            f"{len(successes)}/{len(tasks)} successful"
        )
        
        if errors:
            for error in errors:
                logger.error(f"❌ Async task error: {error}")
        
        return successes


if __name__ == "__main__":
    # Test instantiation
    analyzer = ParallelAnalyzer(max_workers=10, rate_limit_calls=100)
    print(f"✅ ParallelAnalyzer initialized: {analyzer.max_workers} workers")
