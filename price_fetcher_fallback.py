#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 PRICE FETCHER FALLBACK - Real-time Price Data Provider
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE:
Provides real-time price data via Binance REST API as fallback when WebSocket is unavailable
or not pushing data to global_state.

FEATURES:
✅ Binance REST API integration
✅ Multi-symbol support (BTC, ETH, LTC, etc.)
✅ Automatic 5-second refresh
✅ global_state.market_data integration
✅ Circuit breaker for API failures
✅ Thread-safe operations
✅ Production-ready error handling

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sys
import time
import logging
import requests
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# ════════════════════════════════════════════════════════════════════════════════════════════════════════
# LOGGING CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════════════════════════════════

logger = logging.getLogger('PRICE_FETCHER_FALLBACK')
logger.setLevel(logging.INFO)

# ════════════════════════════════════════════════════════════════════════════════════════════════════════
# PRICE FETCHER CLASS
# ════════════════════════════════════════════════════════════════════════════════════════════════════════

class PriceFetcherFallback:
    """
    Real-time price data fetcher using Binance REST API
    
    Provides continuous price updates for tracked symbols when WebSocket is unavailable.
    Thread-safe with circuit breaker pattern for reliability.
    """
    
    def __init__(self, symbols: List[str], update_interval: int = 5, global_state=None):
        """
        Initialize Price Fetcher
        
        Args:
            symbols: List of symbols to track (e.g., ['BTCUSDT', 'ETHUSDT'])
            update_interval: Update interval in seconds (default: 5)
            global_state: Global state manager instance
        """
        self.symbols = symbols
        self.update_interval = update_interval
        self.global_state = global_state
        self.running = False
        self.thread = None
        
        # Binance REST API base URL
        self.base_url = "https://api.binance.com/api/v3"
        
        # Circuit breaker state
        self.circuit_breaker = {
            'failures': 0,
            'max_failures': 5,
            'is_open': False,
            'last_failure_time': None,
            'reset_timeout': 60  # seconds
        }
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'last_update_time': None,
            'average_latency_ms': 0.0
        }
        
        logger.info(f"✅ PriceFetcherFallback initialized | Symbols: {len(symbols)} | Interval: {update_interval}s")
    
    def start(self):
        """Start the price fetching background thread"""
        if self.running:
            logger.warning("⚠️ Price fetcher already running")
            return
        
        self.running = True
        self.thread = threading.Thread(
            target=self._fetch_loop,
            daemon=True,
            name="PriceFetcherThread"
        )
        self.thread.start()
        logger.info("🚀 Price fetcher background thread started")
    
    def stop(self):
        """Stop the price fetching thread"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        logger.info("🛑 Price fetcher stopped")
    
    def _fetch_loop(self):
        """Main fetching loop (runs in background thread)"""
        logger.info("🔄 Price fetch loop started")
        
        while self.running:
            try:
                # Check circuit breaker
                if self._is_circuit_open():
                    logger.warning("⚠️ Circuit breaker OPEN - skipping fetch")
                    time.sleep(self.update_interval)
                    continue
                
                # Fetch prices for all symbols
                self._fetch_all_prices()
                
                # Sleep until next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"❌ Price fetch loop error: {e}")
                self._record_failure()
                time.sleep(10)
    
    def _fetch_all_prices(self):
        """Fetch prices for all tracked symbols"""
        start_time = time.time()
        
        try:
            # Binance API: Get all ticker prices in one request
            url = f"{self.base_url}/ticker/price"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            all_tickers = response.json()
            
            # Filter for our tracked symbols
            symbol_prices = {
                ticker['symbol']: float(ticker['price'])
                for ticker in all_tickers
                if ticker['symbol'] in self.symbols
            }
            
            # Also fetch 24h volume
            volume_url = f"{self.base_url}/ticker/24hr"
            volume_response = requests.get(volume_url, timeout=10)
            volume_response.raise_for_status()
            
            all_volumes = volume_response.json()
            symbol_volumes = {
                ticker['symbol']: float(ticker['quoteVolume'])
                for ticker in all_volumes
                if ticker['symbol'] in self.symbols
            }
            
              # Update global_state with fetched data
            if self.global_state:
                for symbol in self.symbols:
                    if symbol in symbol_prices:
                        market_data = {
                            'price': symbol_prices[symbol],
                            'volume': symbol_volumes.get(symbol, 0),
                            'source': 'BINANCE_REST_API',
                            'metadata': {
                                'fetch_method': 'REST_FALLBACK',
                                'latency_ms': (time.time() - start_time) * 1000
                            }
                        }
                        
                        # 🔍 Clean symbol before updating (uppercase, strip spaces)
                        clean_symbol = symbol.strip().upper()
                        self.global_state.update_market_data(clean_symbol, market_data)
                        logger.info(f"  💰 {clean_symbol}: ${symbol_prices[symbol]:,.2f} → global_state")
                
                logger.info(
                    f"✅ Prices updated: {len(symbol_prices)} symbols | "
                    f"Latency: {(time.time() - start_time) * 1000:.1f}ms"
                )
                                          
            # Record success
            self._record_success((time.time() - start_time) * 1000)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Binance API request failed: {e}")
            self._record_failure()
        except Exception as e:
            logger.error(f"❌ Price fetch error: {e}")
            self._record_failure()
    
    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is open"""
        if not self.circuit_breaker['is_open']:
            return False
        
        # Check if reset timeout has passed
        if self.circuit_breaker['last_failure_time']:
            elapsed = time.time() - self.circuit_breaker['last_failure_time']
            if elapsed > self.circuit_breaker['reset_timeout']:
                # Reset circuit breaker
                self.circuit_breaker['is_open'] = False
                self.circuit_breaker['failures'] = 0
                logger.info("✅ Circuit breaker CLOSED (reset timeout passed)")
                return False
        
        return True
    
    def _record_success(self, latency_ms: float):
        """Record successful API call"""
        self.stats['total_requests'] += 1
        self.stats['successful_requests'] += 1
        self.stats['last_update_time'] = datetime.now(timezone.utc)
        
        # Update average latency
        total_latency = self.stats['average_latency_ms'] * (self.stats['successful_requests'] - 1)
        self.stats['average_latency_ms'] = (total_latency + latency_ms) / self.stats['successful_requests']
        
        # Reset circuit breaker on success
        self.circuit_breaker['failures'] = 0
        if self.circuit_breaker['is_open']:
            self.circuit_breaker['is_open'] = False
            logger.info("✅ Circuit breaker CLOSED (successful request)")
    
    def _record_failure(self):
        """Record failed API call"""
        self.stats['total_requests'] += 1
        self.stats['failed_requests'] += 1
        
        # Increment circuit breaker failures
        self.circuit_breaker['failures'] += 1
        self.circuit_breaker['last_failure_time'] = time.time()
        
        # Open circuit breaker if max failures reached
        if self.circuit_breaker['failures'] >= self.circuit_breaker['max_failures']:
            self.circuit_breaker['is_open'] = True
            logger.error(
                f"🚨 Circuit breaker OPENED | "
                f"Failures: {self.circuit_breaker['failures']}/{self.circuit_breaker['max_failures']} | "
                f"Reset in {self.circuit_breaker['reset_timeout']}s"
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get fetcher statistics"""
        success_rate = 0.0
        if self.stats['total_requests'] > 0:
            success_rate = (self.stats['successful_requests'] / self.stats['total_requests']) * 100
        
        return {
            'running': self.running,
            'symbols': self.symbols,
            'update_interval': self.update_interval,
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'success_rate': round(success_rate, 2),
            'average_latency_ms': round(self.stats['average_latency_ms'], 2),
            'last_update_time': self.stats['last_update_time'].isoformat() if self.stats['last_update_time'] else None,
            'circuit_breaker': {
                'is_open': self.circuit_breaker['is_open'],
                'failures': self.circuit_breaker['failures'],
                'max_failures': self.circuit_breaker['max_failures']
            }
        }
    
    def fetch_single_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch price for a single symbol (synchronous)
        
        Args:
            symbol: Symbol to fetch (e.g., 'BTCUSDT')
            
        Returns:
            Dict with price data or None on failure
        """
        try:
            url = f"{self.base_url}/ticker/price"
            params = {'symbol': symbol}
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            # Also get volume
            volume_url = f"{self.base_url}/ticker/24hr"
            volume_response = requests.get(volume_url, params=params, timeout=5)
            volume_data = volume_response.json()
            
            return {
                'symbol': symbol,
                'price': float(data['price']),
                'volume': float(volume_data.get('quoteVolume', 0)),
                'change_24h': float(volume_data.get('priceChangePercent', 0)),
                'source': 'BINANCE_REST_API',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch price for {symbol}: {e}")
            return None

# ════════════════════════════════════════════════════════════════════════════════════════════════════════
# STANDALONE TEST
# ════════════════════════════════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("="*100)
    print("🚀 PRICE FETCHER FALLBACK - STANDALONE TEST")
    print("="*100)
    
    # Test symbols
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    
    # Create mock global_state for testing
    class MockGlobalState:
        def update_market_data(self, symbol, data):
            print(f"✅ Mock update: {symbol} → ${data['price']:.2f} | Volume: ${data['volume']:,.0f}")
    
    mock_state = MockGlobalState()
    
    # Initialize fetcher
    fetcher = PriceFetcherFallback(
        symbols=test_symbols,
        update_interval=5,
        global_state=mock_state
    )
    
    # Test single fetch
    print("\n📊 Testing single symbol fetch...")
    btc_data = fetcher.fetch_single_price('BTCUSDT')
    if btc_data:
        print(f"✅ BTC Price: ${btc_data['price']:,.2f}")
        print(f"✅ 24h Volume: ${btc_data['volume']:,.0f}")
        print(f"✅ 24h Change: {btc_data['change_24h']:+.2f}%")
    
    # Start background thread
    print("\n🚀 Starting background thread (5 second updates)...")
    fetcher.start()
    
    # Let it run for 20 seconds
    try:
        print("⏱️  Running for 20 seconds (Ctrl+C to stop early)...")
        time.sleep(20)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    
    # Stop and show stats
    fetcher.stop()
    
    print("\n📊 Final Statistics:")
    stats = fetcher.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Test complete!")
