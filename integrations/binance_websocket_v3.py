# integrations/binance_websocket_v3.py
"""
🚀 DEMIR AI v6.0 - ADVANCED BINANCE WEBSOCKET MANAGER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ENTERPRISE-GRADE WEBSOCKET:
    ✅ Auto-reconnection with exponential backoff
    ✅ Health monitoring (ping/pong every 30s)
    ✅ Multi-stream management (prices, depth, trades, klines)
    ✅ Circuit breaker for failed connections
    ✅ Real-time data verification (NO MOCK DATA)
    ✅ Thread-safe event handling
    ✅ Graceful shutdown
    
DEPLOYMENT: Railway + GitHub
AUTHOR: DEMIR AI Research Team
DATE: 2025-11-19
VERSION: 6.0
"""

import os
import sys
import json
import time
import asyncio
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict, deque
import websockets
from websockets.exceptions import (
    ConnectionClosed,
    ConnectionClosedError,
    ConnectionClosedOK,
    WebSocketException
)

from utils.logger_setup import setup_logger
from utils.real_data_verifier_pro import RealDataVerifier

logger = setup_logger(__name__)

# ============================================================================
# WEBSOCKET MANAGER
# ============================================================================

class BinanceWebSocketManager:
    """
    Enterprise-grade Binance WebSocket Manager
    
    Features:
        - Multi-stream support (price, depth, trades, klines)
        - Auto-reconnection with exponential backoff
        - Health monitoring with ping/pong
        - Circuit breaker for failed connections
        - Real-time data verification
        - Thread-safe callbacks
    """
    
    # Binance WebSocket endpoints
    STREAM_URL = "wss://stream.binance.com:9443"
    TESTNET_URL = "wss://testnet.binance.vision/ws"
    
    # Configuration
    PING_INTERVAL = 30  # seconds
    PONG_TIMEOUT = 10   # seconds
    MAX_RECONNECT_ATTEMPTS = 10
    RECONNECT_DELAY_BASE = 2  # seconds
    RECONNECT_DELAY_MAX = 300  # 5 minutes
    
    # Stream types
    STREAM_TICKER = "ticker"
    STREAM_DEPTH = "depth"
    STREAM_TRADE = "trade"
    STREAM_KLINE = "kline"
    STREAM_BOOK_TICKER = "bookTicker"
    STREAM_AGG_TRADE = "aggTrade"
    
    def __init__(self, testnet: bool = False):
        """
        Initialize WebSocket Manager
        
        Args:
            testnet: Use testnet endpoint (for testing only)
        """
        self.base_url = self.TESTNET_URL if testnet else self.STREAM_URL
        
        # Connection state
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False
        self.is_running = False
        self.reconnect_count = 0
        self.last_pong_time = None
        
        # Subscriptions
        self.subscriptions: Dict[str, Dict[str, Any]] = {}
        self.callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # Threading
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        # Circuit breaker
        self.circuit_state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.failure_threshold = 5
        self.circuit_open_time = None
        self.circuit_timeout = 60  # seconds
        
        # Data verification
        self.data_verifier = RealDataVerifier()
        
        # Metrics
        self.metrics = {
            'messages_received': 0,
            'messages_failed': 0,
            'reconnections': 0,
            'last_message_time': None,
            'uptime_start': None
        }
        
        # Message buffer for replay on reconnect
        self.message_buffer = deque(maxlen=100)
        
        logger.info("BinanceWebSocketManager initialized")
    
    # ========================================================================
    # CONNECTION MANAGEMENT
    # ========================================================================
    
    def start(self):
        """Start WebSocket manager in background thread"""
        if self.is_running:
            logger.warning("WebSocket manager already running")
            return
        
        self.is_running = True
        self.metrics['uptime_start'] = datetime.now()
        
        # Start in separate thread
        self.thread = threading.Thread(
            target=self._run_event_loop,
            daemon=True,
            name="BinanceWebSocket"
        )
        self.thread.start()
        
        logger.info("✅ WebSocket manager started in background thread")
    
    def _run_event_loop(self):
        """Run asyncio event loop in thread"""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            self.loop.run_until_complete(self._maintain_connection())
        except Exception as e:
            logger.error(f"Event loop error: {e}")
        finally:
            if self.loop:
                self.loop.close()
    
    async def _maintain_connection(self):
        """Maintain WebSocket connection with auto-reconnect"""
        while self.is_running:
            try:
                # Check circuit breaker
                if not self._check_circuit_breaker():
                    logger.warning("Circuit breaker OPEN - waiting before retry")
                    await asyncio.sleep(self.circuit_timeout)
                    continue
                
                # Connect
                await self._connect()
                
                # Health monitor task
                health_task = asyncio.create_task(self._health_monitor())
                
                # Message handler task
                handler_task = asyncio.create_task(self._message_handler())
                
                # Wait for tasks
                await asyncio.gather(health_task, handler_task)
                
            except (ConnectionClosed, ConnectionClosedError, ConnectionClosedOK) as e:
                logger.warning(f"WebSocket connection closed: {e}")
                self.is_connected = False
                await self._handle_reconnect()
                
            except WebSocketException as e:
                logger.error(f"WebSocket error: {e}")
                self.is_connected = False
                self._record_failure()
                await self._handle_reconnect()
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                import traceback
                logger.error(traceback.format_exc())
                self.is_connected = False
                self._record_failure()
                await self._handle_reconnect()
    
    async def _connect(self):
        """Establish WebSocket connection"""
        try:
            # Build stream URL
            if self.subscriptions:
                streams = "/".join([
                    self._build_stream_name(symbol, stream_type)
                    for symbol, config in self.subscriptions.items()
                    for stream_type in config['streams']
                ])
                url = f"{self.base_url}/stream?streams={streams}"
            else:
                url = f"{self.base_url}/ws"
            
            logger.info(f"Connecting to {url}")
            
            # Connect with timeout
            self.websocket = await asyncio.wait_for(
                websockets.connect(
                    url,
                    ping_interval=None,  # We handle ping/pong manually
                    close_timeout=10
                ),
                timeout=30
            )
            
            self.is_connected = True
            self.reconnect_count = 0
            self.last_pong_time = time.time()
            
            # Reset circuit breaker on successful connection
            self._reset_circuit_breaker()
            
            logger.info("✅ WebSocket connected successfully")
            
            # Re-subscribe if needed
            await self._resubscribe()
            
        except asyncio.TimeoutError:
            logger.error("Connection timeout")
            raise
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise
    
    async def _handle_reconnect(self):
        """Handle reconnection with exponential backoff"""
        self.reconnect_count += 1
        self.metrics['reconnections'] += 1
        
        if self.reconnect_count > self.MAX_RECONNECT_ATTEMPTS:
            logger.error(f"Max reconnection attempts ({self.MAX_RECONNECT_ATTEMPTS}) reached")
            self._open_circuit_breaker()
            return
        
        # Calculate backoff delay
        delay = min(
            self.RECONNECT_DELAY_BASE ** self.reconnect_count,
            self.RECONNECT_DELAY_MAX
        )
        
        logger.info(f"Reconnecting in {delay}s (attempt {self.reconnect_count}/{self.MAX_RECONNECT_ATTEMPTS})")
        await asyncio.sleep(delay)
    
    async def _resubscribe(self):
        """Re-subscribe to streams after reconnection"""
        if not self.subscriptions:
            return
        
        logger.info("Re-subscribing to streams...")
        
        # Binance streams are automatically subscribed via URL
        # No action needed for combined streams
        
        logger.info("✅ Re-subscribed to all streams")
    
    # ========================================================================
    # MESSAGE HANDLING
    # ========================================================================
    
    async def _message_handler(self):
        """Handle incoming WebSocket messages"""
        try:
            async for message in self.websocket:
                try:
                    # Parse message
                    data = json.loads(message)
                    
                    # Update metrics
                    self.metrics['messages_received'] += 1
                    self.metrics['last_message_time'] = datetime.now()
                    
                    # Store in buffer
                    self.message_buffer.append(data)
                    
                    # Process based on stream type
                    await self._process_message(data)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    self.metrics['messages_failed'] += 1
                    
                except Exception as e:
                    logger.error(f"Message processing error: {e}")
                    self.metrics['messages_failed'] += 1
        
        except Exception as e:
            logger.error(f"Message handler error: {e}")
            raise
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process message based on stream type"""
        try:
            # Get stream type
            stream = data.get('stream', '')
            event_data = data.get('data', data)
            event_type = event_data.get('e', '')
            
            # Route to appropriate handler
            if '24hrTicker' in stream or event_type == '24hrTicker':
                await self._handle_ticker(event_data)
            
            elif 'depth' in stream or event_type == 'depthUpdate':
                await self._handle_depth(event_data)
            
            elif 'trade' in stream or event_type == 'trade':
                await self._handle_trade(event_data)
            
            elif 'kline' in stream or event_type == 'kline':
                await self._handle_kline(event_data)
            
            elif 'bookTicker' in stream or event_type == 'bookTicker':
                await self._handle_book_ticker(event_data)
            
            elif 'aggTrade' in stream or event_type == 'aggTrade':
                await self._handle_agg_trade(event_data)
            
            else:
                logger.debug(f"Unknown message type: {event_type}")
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _handle_ticker(self, data: Dict[str, Any]):
        """Handle 24hr ticker data"""
        try:
            symbol = data.get('s', '')
            price = float(data.get('c', 0))
            change_24h = float(data.get('P', 0))
            volume = float(data.get('v', 0))
            
            # Verify real data
            is_valid = await self.data_verifier.verify_price(
                symbol=symbol,
                price=price,
                exchange='binance'
            )
            
            if not is_valid:
                logger.warning(f"⚠️ INVALID TICKER DATA for {symbol} - REJECTED")
                return
            
            # Call callbacks
            await self._trigger_callbacks(f"{symbol}:ticker", {
                'symbol': symbol,
                'price': price,
                'change_24h': change_24h,
                'volume': volume,
                'timestamp': time.time()
            })
            
        except Exception as e:
            logger.error(f"Error handling ticker: {e}")
    
    async def _handle_depth(self, data: Dict[str, Any]):
        """Handle order book depth data"""
        try:
            symbol = data.get('s', '')
            bids = data.get('b', [])
            asks = data.get('a', [])
            
            # Parse order book
            bids_parsed = [[float(p), float(q)] for p, q in bids[:20]]
            asks_parsed = [[float(p), float(q)] for p, q in asks[:20]]
            
            # Call callbacks
            await self._trigger_callbacks(f"{symbol}:depth", {
                'symbol': symbol,
                'bids': bids_parsed,
                'asks': asks_parsed,
                'timestamp': time.time()
            })
            
        except Exception as e:
            logger.error(f"Error handling depth: {e}")
    
    async def _handle_trade(self, data: Dict[str, Any]):
        """Handle trade data"""
        try:
            symbol = data.get('s', '')
            price = float(data.get('p', 0))
            quantity = float(data.get('q', 0))
            is_buyer_maker = data.get('m', False)
            
            # Call callbacks
            await self._trigger_callbacks(f"{symbol}:trade", {
                'symbol': symbol,
                'price': price,
                'quantity': quantity,
                'side': 'sell' if is_buyer_maker else 'buy',
                'timestamp': time.time()
            })
            
        except Exception as e:
            logger.error(f"Error handling trade: {e}")
    
    async def _handle_kline(self, data: Dict[str, Any]):
        """Handle kline/candlestick data"""
        try:
            symbol = data.get('s', '')
            kline = data.get('k', {})
            
            # Call callbacks
            await self._trigger_callbacks(f"{symbol}:kline", {
                'symbol': symbol,
                'interval': kline.get('i', ''),
                'open': float(kline.get('o', 0)),
                'high': float(kline.get('h', 0)),
                'low': float(kline.get('l', 0)),
                'close': float(kline.get('c', 0)),
                'volume': float(kline.get('v', 0)),
                'closed': kline.get('x', False),
                'timestamp': time.time()
            })
            
        except Exception as e:
            logger.error(f"Error handling kline: {e}")
    
    async def _handle_book_ticker(self, data: Dict[str, Any]):
        """Handle book ticker data (best bid/ask)"""
        try:
            symbol = data.get('s', '')
            best_bid = float(data.get('b', 0))
            best_ask = float(data.get('a', 0))
            
            # Call callbacks
            await self._trigger_callbacks(f"{symbol}:bookTicker", {
                'symbol': symbol,
                'best_bid': best_bid,
                'best_ask': best_ask,
                'spread': best_ask - best_bid,
                'timestamp': time.time()
            })
            
        except Exception as e:
            logger.error(f"Error handling book ticker: {e}")
    
    async def _handle_agg_trade(self, data: Dict[str, Any]):
        """Handle aggregated trade data"""
        try:
            symbol = data.get('s', '')
            price = float(data.get('p', 0))
            quantity = float(data.get('q', 0))
            is_buyer_maker = data.get('m', False)
            
            # Call callbacks
            await self._trigger_callbacks(f"{symbol}:aggTrade", {
                'symbol': symbol,
                'price': price,
                'quantity': quantity,
                'side': 'sell' if is_buyer_maker else 'buy',
                'timestamp': time.time()
            })
            
        except Exception as e:
            logger.error(f"Error handling agg trade: {e}")
    
    # ========================================================================
    # HEALTH MONITORING
    # ========================================================================
    
    async def _health_monitor(self):
        """Monitor connection health with ping/pong"""
        try:
            while self.is_connected and self.is_running:
                # Wait for ping interval
                await asyncio.sleep(self.PING_INTERVAL)
                
                # Send ping
                if self.websocket and self.is_connected:
                    try:
                        pong = await asyncio.wait_for(
                            self.websocket.ping(),
                            timeout=self.PONG_TIMEOUT
                        )
                        await pong
                        
                        self.last_pong_time = time.time()
                        logger.debug("Ping/pong successful")
                        
                    except asyncio.TimeoutError:
                        logger.error("Pong timeout - connection may be dead")
                        raise ConnectionClosedError(None, None)
                    
                    except Exception as e:
                        logger.error(f"Ping/pong error: {e}")
                        raise
        
        except Exception as e:
            logger.error(f"Health monitor error: {e}")
            raise
    
    # ========================================================================
    # SUBSCRIPTION MANAGEMENT
    # ========================================================================
    
    def subscribe(
        self,
        symbol: str,
        stream_types: List[str],
        callback: Optional[Callable] = None
    ):
        """
        Subscribe to WebSocket streams for a symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            stream_types: List of stream types (ticker, depth, trade, kline)
            callback: Optional callback function
        """
        with self.lock:
            # Normalize symbol
            symbol = symbol.upper()
            
            # Add subscription
            if symbol not in self.subscriptions:
                self.subscriptions[symbol] = {
                    'streams': set(),
                    'added_at': datetime.now()
                }
            
            # Add stream types
            for stream_type in stream_types:
                self.subscriptions[symbol]['streams'].add(stream_type)
                
                # Register callback
                if callback:
                    callback_key = f"{symbol}:{stream_type}"
                    if callback not in self.callbacks[callback_key]:
                        self.callbacks[callback_key].append(callback)
            
            logger.info(f"Subscribed to {stream_types} for {symbol}")
        
        # Restart connection if already running (to update subscriptions)
        if self.is_connected:
            asyncio.run_coroutine_threadsafe(
                self._reconnect_for_subscription(),
                self.loop
            )
    
    def unsubscribe(self, symbol: str, stream_types: Optional[List[str]] = None):
        """
        Unsubscribe from WebSocket streams
        
        Args:
            symbol: Trading pair
            stream_types: Specific stream types to unsubscribe (None = all)
        """
        with self.lock:
            symbol = symbol.upper()
            
            if symbol not in self.subscriptions:
                return
            
            if stream_types is None:
                # Remove all streams for symbol
                del self.subscriptions[symbol]
                logger.info(f"Unsubscribed from all streams for {symbol}")
            else:
                # Remove specific streams
                for stream_type in stream_types:
                    self.subscriptions[symbol]['streams'].discard(stream_type)
                
                # Remove symbol if no streams left
                if not self.subscriptions[symbol]['streams']:
                    del self.subscriptions[symbol]
                
                logger.info(f"Unsubscribed from {stream_types} for {symbol}")
        
        # Restart connection if already running
        if self.is_connected:
            asyncio.run_coroutine_threadsafe(
                self._reconnect_for_subscription(),
                self.loop
            )
    
    async def _reconnect_for_subscription(self):
        """Reconnect to apply subscription changes"""
        try:
            if self.websocket:
                await self.websocket.close()
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error reconnecting for subscription: {e}")
    
    # ========================================================================
    # CALLBACK MANAGEMENT
    # ========================================================================
    
    async def _trigger_callbacks(self, key: str, data: Dict[str, Any]):
        """Trigger registered callbacks"""
        if key in self.callbacks:
            for callback in self.callbacks[key]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
    
    # ========================================================================
    # CIRCUIT BREAKER
    # ========================================================================
    
    def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker allows connection"""
        if self.circuit_state == "CLOSED":
            return True
        
        if self.circuit_state == "OPEN":
            # Check if timeout elapsed
            if time.time() - self.circuit_open_time > self.circuit_timeout:
                logger.info("Circuit breaker entering HALF_OPEN state")
                self.circuit_state = "HALF_OPEN"
                return True
            return False
        
        if self.circuit_state == "HALF_OPEN":
            return True
        
        return False
    
    def _record_failure(self):
        """Record connection failure"""
        self.failure_count += 1
        
        if self.failure_count >= self.failure_threshold:
            self._open_circuit_breaker()
    
    def _open_circuit_breaker(self):
        """Open circuit breaker"""
        self.circuit_state = "OPEN"
        self.circuit_open_time = time.time()
        logger.error(f"🔴 Circuit breaker OPEN - too many failures ({self.failure_count})")
    
    def _reset_circuit_breaker(self):
        """Reset circuit breaker on successful connection"""
        if self.circuit_state != "CLOSED":
            logger.info("🟢 Circuit breaker CLOSED - connection restored")
        
        self.circuit_state = "CLOSED"
        self.failure_count = 0
        self.circuit_open_time = None
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _build_stream_name(self, symbol: str, stream_type: str) -> str:
        """Build Binance stream name"""
        symbol_lower = symbol.lower()
        
        if stream_type == self.STREAM_TICKER:
            return f"{symbol_lower}@ticker"
        elif stream_type == self.STREAM_DEPTH:
            return f"{symbol_lower}@depth@100ms"
        elif stream_type == self.STREAM_TRADE:
            return f"{symbol_lower}@trade"
        elif stream_type == self.STREAM_KLINE:
            return f"{symbol_lower}@kline_1m"
        elif stream_type == self.STREAM_BOOK_TICKER:
            return f"{symbol_lower}@bookTicker"
        elif stream_type == self.STREAM_AGG_TRADE:
            return f"{symbol_lower}@aggTrade"
        else:
            return f"{symbol_lower}@{stream_type}"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get WebSocket metrics"""
        uptime = None
        if self.metrics['uptime_start']:
            uptime = (datetime.now() - self.metrics['uptime_start']).total_seconds()
        
        return {
            'is_connected': self.is_connected,
            'circuit_state': self.circuit_state,
            'subscriptions': len(self.subscriptions),
            'messages_received': self.metrics['messages_received'],
            'messages_failed': self.metrics['messages_failed'],
            'reconnections': self.metrics['reconnections'],
            'last_message_time': self.metrics['last_message_time'],
            'uptime_seconds': uptime,
            'last_pong_time': self.last_pong_time
        }
    
    def is_healthy(self) -> bool:
        """Check if WebSocket is healthy"""
        if not self.is_connected:
            return False
        
        if self.circuit_state == "OPEN":
            return False
        
        # Check if received message recently (within 60 seconds)
        if self.metrics['last_message_time']:
            time_since_message = (datetime.now() - self.metrics['last_message_time']).total_seconds()
            if time_since_message > 60:
                return False
        
        return True
    
    # ========================================================================
    # SHUTDOWN
    # ========================================================================
    
    async def _close(self):
        """Close WebSocket connection"""
        try:
            self.is_running = False
            
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
            
            self.is_connected = False
            
            logger.info("WebSocket closed")
        
        except Exception as e:
            logger.error(f"Error closing WebSocket: {e}")
    
    def stop(self):
        """Stop WebSocket manager"""
        logger.info("Stopping WebSocket manager...")
        
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._close(), self.loop)
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        logger.info("✅ WebSocket manager stopped")
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.stop()
        except:
            pass

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def start_price_stream(
    symbols: List[str],
    callback: Callable[[str, float, float], None]
):
    """
    Convenience function to start price stream
    
    Args:
        symbols: List of trading pairs
        callback: Callback function(symbol, price, change_24h)
    """
    manager = BinanceWebSocketManager()
    
    async def price_callback(data):
        await callback(
            data['symbol'],
            data['price'],
            data['change_24h']
        )
    
    for symbol in symbols:
        manager.subscribe(
            symbol=symbol,
            stream_types=[BinanceWebSocketManager.STREAM_TICKER],
            callback=price_callback
        )
    
    manager.start()
    return manager

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """Example usage"""
    
    async def on_price_update(symbol: str, price: float, change_24h: float):
        print(f"{symbol}: ${price:,.2f} ({change_24h:+.2f}%)")
    
    async def main():
        # Start price stream
        manager = await start_price_stream(
            symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
            callback=on_price_update
        )
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            manager.stop()
    
    asyncio.run(main())

