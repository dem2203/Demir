"""
🚀 DEMIR AI v7.0 - Multi-Exchange Data Fetcher
Production-grade real-time data aggregation with automatic failover
Author: DEMIR AI Research Team
Date: 2025-11-20
License: Professional Use
"""

import os
import time
import logging
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime
from collections import deque
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum

from utils.retry_manager import RetryManager
from utils.circuit_breaker import CircuitBreaker

# ============================================================================
# LOGGING SETUP
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Exchange configurations
BINANCE_CONFIG = {
    'name': 'BINANCE',
    'rest_url': 'https://api.binance.com',
    'ws_url': 'wss://stream.binance.com:9443',
    'endpoints': {
        'price': '/api/v3/ticker/price',
        'klines': '/api/v3/klines',
        'depth': '/api/v3/depth',
        'ticker24h': '/api/v3/ticker/24hr'
    },
    'rate_limit': 1200,  # requests per minute
    'weight_limit': 6000  # weight per minute
}

BYBIT_CONFIG = {
    'name': 'BYBIT',
    'rest_url': 'https://api.bybit.com',
    'endpoints': {
        'price': '/v2/public/tickers',
        'klines': '/v2/public/kline/list',
        'depth': '/v2/public/orderBook/L2'
    },
    'rate_limit': 600
}

COINBASE_CONFIG = {
    'name': 'COINBASE',
    'rest_url': 'https://api.pro.coinbase.com',
    'endpoints': {
        'price': '/products/{symbol}/ticker',
        'klines': '/products/{symbol}/candles'
    },
    'rate_limit': 600
}

# Timeout settings
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3

# ============================================================================
# MULTI-EXCHANGE DATA FETCHER
# ============================================================================

class MultiExchangeDataFetcher:
    """
    Multi-exchange data fetcher with automatic failover.
    
    Priority order:
    1. Binance (Primary - most liquid)
    2. Bybit (Secondary)
    3. Coinbase (Tertiary)
    
    Features:
    - Automatic failover on errors
    - Circuit breaker pattern (SINGLE instance)
    - Rate limit management
    - Health monitoring
    - Data validation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the multi-exchange data fetcher."""
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # ================================================================
        # CIRCUIT BREAKER (Single instance - NOT duplicated)
        # ================================================================
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=300
        )
        
        # ================================================================
        # EXCHANGE CONFIGURATIONS
        # ================================================================
        self.exchanges = {
            'BINANCE': BINANCE_CONFIG,
            'BYBIT': BYBIT_CONFIG,
            'COINBASE': COINBASE_CONFIG
        }
        
        # ================================================================
        # RETRY MANAGERS (one per exchange)
        # ================================================================
        self.retry_managers = {
            name: RetryManager(max_retries=MAX_RETRIES)
            for name in self.exchanges.keys()
        }
        
        # ================================================================
        # HEALTH TRACKING
        # ================================================================
        self.exchange_health = {
            name: {
                'is_healthy': True,
                'last_success': None,
                'last_failure': None,
                'failure_count': 0,
                'success_count': 0,
                'avg_latency': 0.0
            }
            for name in self.exchanges.keys()
        }
        
        # ================================================================
        # RATE LIMIT TRACKING
        # ================================================================
        self.rate_limits = {
            name: deque(maxlen=100)
            for name in self.exchanges.keys()
        }
        
        # ================================================================
        # STATISTICS
        # ================================================================
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'binance_requests': 0,
            'bybit_requests': 0,
            'coinbase_requests': 0
        }
        
        self.logger.info('✅ MultiExchangeDataFetcher initialized (Binance, Bybit, Coinbase)')
    
    # ====================================================================
    # PRICE FETCHING
    # ====================================================================
    
    async def get_price_with_fallback(self, symbol: str) -> Tuple[Optional[float], str]:
        """
        Get current price with automatic exchange fallback.
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
        
        Returns:
            Tuple of (price, exchange_source)
        
        Raises:
            Exception: If all exchanges fail
        """
        self.stats['total_requests'] += 1
        
        # Try exchanges in priority order
        exchange_order = ['BINANCE', 'BYBIT', 'COINBASE']
        
        for exchange_name in exchange_order:
            try:
                # Check circuit breaker
                if not self.circuit_breaker.can_execute:
                    self.logger.debug(f'Circuit breaker OPEN for {exchange_name}, skipping')
                    continue
                
                # Fetch price
                price = await self._fetch_price_from_exchange(symbol, exchange_name)
                
                if price and price > 0:
                    # Record success
                    self.circuit_breaker.record_success()
                    self._record_success(exchange_name)
                    self.stats['successful_requests'] += 1
                    self.stats[f'{exchange_name.lower()}_requests'] += 1
                    
                    self.logger.debug(f'✅ Price fetched from {exchange_name}: {price:.2f}')
                    return price, exchange_name
                    
            except Exception as e:
                self.logger.warning(f'⚠️ Failed to fetch from {exchange_name}: {e}')
                self.circuit_breaker.record_failure()
                self._record_failure(exchange_name)
                continue
        
        # All exchanges failed
        self.stats['failed_requests'] += 1
        error_msg = f'❌ All exchanges failed for {symbol}'
        self.logger.error(error_msg)
        raise Exception(error_msg)
    
    async def _fetch_price_from_exchange(self, symbol: str, exchange: str) -> Optional[float]:
        """
        Fetch price from specific exchange.
        
        Args:
            symbol: Trading pair
            exchange: Exchange name
        
        Returns:
            Price or None
        """
        config = self.exchanges[exchange]
        
        if exchange == 'BINANCE':
            return await self._fetch_binance_price(symbol, config)
        elif exchange == 'BYBIT':
            return await self._fetch_bybit_price(symbol, config)
        elif exchange == 'COINBASE':
            return await self._fetch_coinbase_price(symbol, config)
        else:
            return None
    
    async def _fetch_binance_price(self, symbol: str, config: Dict[str, Any]) -> Optional[float]:
        """Fetch price from Binance."""
        url = f"{config['rest_url']}{config['endpoints']['price']}"
        params = {'symbol': symbol}
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
                ) as response:
                    latency = time.time() - start_time
                    self._record_latency('BINANCE', latency)
                    
                    if response.status == 200:
                        data = await response.json()
                        price = float(data['price'])
                        return price
                    else:
                        self.logger.error(f'❌ Binance API error: {response.status}')
                        return None
        except Exception as e:
            self.logger.error(f'❌ Binance fetch error: {e}')
            return None
    
    async def _fetch_bybit_price(self, symbol: str, config: Dict[str, Any]) -> Optional[float]:
        """Fetch price from Bybit."""
        # Bybit uses different symbol format
        bybit_symbol = symbol.replace('USDT', '')
        
        url = f"{config['rest_url']}{config['endpoints']['price']}"
        params = {'symbol': f'{bybit_symbol}USDT'}
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
                ) as response:
                    latency = time.time() - start_time
                    self._record_latency('BYBIT', latency)
                    
                    if response.status == 200:
                        data = await response.json()
                        if data.get('retcode') == 0:
                            result = data.get('result')
                            if isinstance(result, list) and len(result) > 0:
                                price = float(result[0]['last_price'])
                                return price
                    return None
        except Exception as e:
            self.logger.error(f'❌ Bybit fetch error: {e}')
            return None
    
    async def _fetch_coinbase_price(self, symbol: str, config: Dict[str, Any]) -> Optional[float]:
        """Fetch price from Coinbase."""
        # Coinbase uses format BTC-USDT
        coinbase_symbol = symbol.replace('USDT', '-USDT')
        
        url = f"{config['rest_url']}{config['endpoints']['price'].format(symbol=coinbase_symbol)}"
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
                ) as response:
                    latency = time.time() - start_time
                    self._record_latency('COINBASE', latency)
                    
                    if response.status == 200:
                        data = await response.json()
                        price = float(data['price'])
                        return price
                    return None
        except Exception as e:
            self.logger.error(f'❌ Coinbase fetch error: {e}')
            return None
    
    # ====================================================================
    # OHLCV DATA FETCHING
    # ====================================================================
    
    async def get_ohlcv(
        self,
        symbol: str,
        interval: str = '1h',
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        """
        Get OHLCV candlestick data.
        
        Args:
            symbol: Trading pair
            interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles
        
        Returns:
            DataFrame with columns [timestamp, open, high, low, close, volume]
        """
        # Try Binance first (most reliable)
        try:
            df = await self._fetch_binance_klines(symbol, interval, limit)
            if df is not None and len(df) > 0:
                return df
        except Exception as e:
            self.logger.warning(f'⚠️ Binance OHLCV fetch failed: {e}')
        
        # Try Bybit as fallback
        try:
            df = await self._fetch_bybit_klines(symbol, interval, limit)
            if df is not None and len(df) > 0:
                return df
        except Exception as e:
            self.logger.warning(f'⚠️ Bybit OHLCV fetch failed: {e}')
        
        self.logger.error(f'❌ Failed to fetch OHLCV for {symbol} {interval}')
        return None
    
    async def _fetch_binance_klines(
        self,
        symbol: str,
        interval: str,
        limit: int
    ) -> Optional[pd.DataFrame]:
        """Fetch klines from Binance."""
        url = f"{BINANCE_CONFIG['rest_url']}{BINANCE_CONFIG['endpoints']['klines']}"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse klines
                        df = pd.DataFrame(
                            data,
                            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                                    'taker_buy_quote', 'ignore']
                        )
                        
                        # Convert to proper types
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        df['open'] = df['open'].astype(float)
                        df['high'] = df['high'].astype(float)
                        df['low'] = df['low'].astype(float)
                        df['close'] = df['close'].astype(float)
                        df['volume'] = df['volume'].astype(float)
                        
                        # Keep only essential columns
                        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                        return df
                    return None
        except Exception as e:
            self.logger.error(f'❌ Binance klines error: {e}')
            return None
    
    async def _fetch_bybit_klines(
        self,
        symbol: str,
        interval: str,
        limit: int
    ) -> Optional[pd.DataFrame]:
        """Fetch klines from Bybit."""
        # Bybit interval mapping
        interval_map = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '1h': 60,
            '4h': 240,
            '1d': 'D'
        }
        
        bybit_interval = interval_map.get(interval, 60)
        bybit_symbol = symbol.replace('USDT', '') + 'USDT'
        
        url = f"{BYBIT_CONFIG['rest_url']}{BYBIT_CONFIG['endpoints']['klines']}"
        params = {
            'symbol': bybit_symbol,
            'interval': bybit_interval,
            'limit': limit
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('retcode') == 0:
                            klines = data.get('result')
                            df = pd.DataFrame(klines)
                            df['timestamp'] = pd.to_datetime(df['open_time'], unit='s')
                            df = df.rename(columns={
                                'open': 'open',
                                'high': 'high',
                                'low': 'low',
                                'close': 'close',
                                'volume': 'volume'
                            })
                            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                            return df
                    return None
        except Exception as e:
            self.logger.error(f'❌ Bybit klines error: {e}')
            return None
    
    # ====================================================================
    # 24H TICKER DATA
    # ====================================================================
    
    async def get_24h_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get 24-hour ticker data."""
        try:
            url = f"{BINANCE_CONFIG['rest_url']}{BINANCE_CONFIG['endpoints']['ticker24h']}"
            params = {'symbol': symbol}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'symbol': data.get('symbol'),
                            'price_change': float(data.get('priceChange', 0)),
                            'price_change_percent': float(data.get('priceChangePercent', 0)),
                            'volume': float(data.get('volume', 0)),
                            'quote_volume': float(data.get('quoteVolume', 0)),
                            'high': float(data.get('highPrice', 0)),
                            'low': float(data.get('lowPrice', 0)),
                            'open': float(data.get('openPrice', 0)),
                            'close': float(data.get('lastPrice', 0))
                        }
        except Exception as e:
            self.logger.error(f'❌ 24h ticker fetch error: {e}')
        
        return None
    
    # ====================================================================
    # HEALTH MONITORING
    # ====================================================================
    
    def _record_success(self, exchange: str) -> None:
        """Record successful request for health tracking."""
        health = self.exchange_health[exchange]
        health['is_healthy'] = True
        health['last_success'] = datetime.now()
        health['success_count'] += 1
        health['failure_count'] = 0  # Reset failure count
    
    def _record_failure(self, exchange: str) -> None:
        """Record failed request for health tracking."""
        health = self.exchange_health[exchange]
        health['last_failure'] = datetime.now()
        health['failure_count'] += 1
        
        # Mark as unhealthy after 3 consecutive failures
        if health['failure_count'] >= 3:
            health['is_healthy'] = False
            self.logger.warning(f'⚠️ {exchange} marked as unhealthy')
    
    def _record_latency(self, exchange: str, latency: float) -> None:
        """Record request latency."""
        health = self.exchange_health[exchange]
        
        # Running average
        if health['avg_latency'] == 0:
            health['avg_latency'] = latency
        else:
            health['avg_latency'] = health['avg_latency'] * 0.9 + latency * 0.1
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all exchanges."""
        return {
            exchange: {
                'is_healthy': health['is_healthy'],
                'last_success': health['last_success'].isoformat() if health['last_success'] else None,
                'last_failure': health['last_failure'].isoformat() if health['last_failure'] else None,
                'success_count': health['success_count'],
                'failure_count': health['failure_count'],
                'avg_latency_ms': health['avg_latency'] * 1000
            }
            for exchange, health in self.exchange_health.items()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get fetcher statistics."""
        return {
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'success_rate': (self.stats['successful_requests'] / max(self.stats['total_requests'], 1)) * 100,
            'requests_per_exchange': {
                'binance': self.stats['binance_requests'],
                'bybit': self.stats['bybit_requests'],
                'coinbase': self.stats['coinbase_requests']
            },
            'exchange_health': self.get_health_status()
        }

# ============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================================

# Alias for backward compatibility with main.py imports
MultiExchangeAPI = MultiExchangeDataFetcher

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def fetch_price(symbol: str) -> float:
    """Quick price fetch."""
    fetcher = MultiExchangeDataFetcher()
    price, _ = await fetcher.get_price_with_fallback(symbol)
    return price

async def fetch_ohlcv(
    symbol: str,
    interval: str = '1h',
    limit: int = 100
) -> Optional[pd.DataFrame]:
    """Quick OHLCV fetch."""
    fetcher = MultiExchangeDataFetcher()
    df = await fetcher.get_ohlcv(symbol, interval, limit)
    return df
