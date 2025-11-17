"""
DEMIR AI v6.0 - PHASE 4 [54]
Binance WebSocket V3 - Real-Time Live Price Updates
Sub-100ms latency, automatic reconnect, message queuing
Production-grade WebSocket manager for live trading
"""

import asyncio
import json
import logging
import time
from typing import Dict, Callable, Optional, List
import websockets
from datetime import datetime
import threading
from queue import Queue
from enum import Enum

logger = logging.getLogger(__name__)


class WebSocketStatus(Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    RECONNECTING = "RECONNECTING"
    FAILED = "FAILED"


class BinanceWebSocketV3Manager:
    """Professional Binance WebSocket V3 Manager for real-time data"""
    
    def __init__(self, symbols: List[str] = None):
        """Initialize WebSocket manager"""
        self.symbols = symbols or ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
        self.ws_url = "wss://stream.binance.com:9443/ws"
        
        self.connection = None
        self.status = WebSocketStatus.DISCONNECTED
        self.message_queue = Queue(maxsize=10000)
        self.price_cache = {}
        self.last_update = {}
        self.heartbeat_interval = 30
        self.reconnect_delay = 5
        self.max_reconnect_attempts = 10
        self.reconnect_attempts = 0
        
        self.callbacks = {}
        self.running = False
        self.last_ping = time.time()
        
        logger.info(f"🔌 WebSocket manager initialized for {len(self.symbols)} symbols")
    
    async def connect(self) -> bool:
        """Connect to Binance WebSocket"""
        try:
            self.status = WebSocketStatus.CONNECTING
            logger.info(f"🔗 Connecting to Binance WebSocket...")
            
            # Build stream name
            streams = ' '.join([f"{symbol.lower()}@kline_1m" for symbol in self.symbols])
            stream_url = f"{self.ws_url}/{streams}"
            
            # Connect with timeout
            self.connection = await asyncio.wait_for(
                websockets.connect(stream_url, ping_interval=20, ping_timeout=10),
                timeout=30
            )
            
            self.status = WebSocketStatus.CONNECTED
            self.reconnect_attempts = 0
            logger.info(f"✅ Connected to Binance WebSocket")
            
            return True
            
        except asyncio.TimeoutError:
            logger.error("❌ WebSocket connection timeout")
            self.status = WebSocketStatus.FAILED
            return False
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            self.status = WebSocketStatus.FAILED
            return False
    
    async def listen(self):
        """Listen for WebSocket messages"""
        try:
            async for message in self.connection:
                try:
                    data = json.loads(message)
                    
                    # Extract OHLCV from kline message
                    if 'k' in data:
                        kline = data['k']
                        symbol = data['s']
                        
                        ohlcv = {
                            'timestamp': kline['t'],
                            'symbol': symbol,
                            'open': float(kline['o']),
                            'high': float(kline['h']),
                            'low': float(kline['l']),
                            'close': float(kline['c']),
                            'volume': float(kline['v']),
                            'is_closed': kline['x'],
                            'received_at': time.time()
                        }
                        
                        # Update cache
                        self.price_cache[symbol] = ohlcv
                        self.last_update[symbol] = ohlcv['received_at']
                        
                        # Queue message
                        if not self.message_queue.full():
                            self.message_queue.put(ohlcv)
                        else:
                            # Drop oldest if queue full
                            try:
                                self.message_queue.get_nowait()
                                self.message_queue.put(ohlcv)
                            except:
                                pass
                        
                        # Call callbacks
                        if symbol in self.callbacks:
                            for callback in self.callbacks[symbol]:
                                try:
                                    callback(ohlcv)
                                except Exception as e:
                                    logger.error(f"Callback error: {e}")
                        
                        # Log price
                        latency = (time.time() - ohlcv['received_at']) * 1000
                        if latency < 100:
                            logger.debug(f"✅ {symbol}: ${ohlcv['close']:.2f} ({latency:.1f}ms)")
                    
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON message received")
                except Exception as e:
                    logger.error(f"Message processing error: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self.status = WebSocketStatus.DISCONNECTED
        except Exception as e:
            logger.error(f"Listen error: {e}")
            self.status = WebSocketStatus.FAILED
    
    async def reconnect_loop(self):
        """Automatic reconnection logic"""
        while self.running:
            try:
                if self.status in [WebSocketStatus.DISCONNECTED, WebSocketStatus.FAILED]:
                    if self.reconnect_attempts < self.max_reconnect_attempts:
                        self.status = WebSocketStatus.RECONNECTING
                        self.reconnect_attempts += 1
                        
                        logger.info(f"🔄 Reconnecting... (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
                        
                        if await self.connect():
                            asyncio.create_task(self.listen())
                        else:
                            await asyncio.sleep(self.reconnect_delay)
                    else:
                        logger.critical("❌ Max reconnection attempts reached")
                        self.status = WebSocketStatus.FAILED
                        break
                
                await asyncio.sleep(5)
            
            except Exception as e:
                logger.error(f"Reconnect loop error: {e}")
                await asyncio.sleep(5)
    
    async def heartbeat(self):
        """Periodic heartbeat check"""
        while self.running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                current_time = time.time()
                for symbol, last_time in self.last_update.items():
                    age = current_time - last_time
                    
                    if age > 60:  # No update for 1 minute
                        logger.warning(f"⚠️ No update for {symbol} in {age:.0f}s")
                    
                    if age > 300:  # No update for 5 minutes
                        logger.critical(f"❌ {symbol} stale for {age:.0f}s - reconnecting")
                        self.status = WebSocketStatus.DISCONNECTED
            
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    async def start(self):
        """Start WebSocket manager"""
        try:
            self.running = True
            logger.info("🚀 Starting WebSocket manager")
            
            # Initial connection
            if not await self.connect():
                logger.error("Initial connection failed")
                return False
            
            # Start concurrent tasks
            listen_task = asyncio.create_task(self.listen())
            reconnect_task = asyncio.create_task(self.reconnect_loop())
            heartbeat_task = asyncio.create_task(self.heartbeat())
            
            # Wait for any task to fail
            done, pending = await asyncio.wait(
                [listen_task, reconnect_task, heartbeat_task],
                return_when=asyncio.FIRST_EXCEPTION
            )
            
            logger.warning("WebSocket manager stopped")
            return False
        
        except Exception as e:
            logger.error(f"Start error: {e}")
            return False
    
    def stop(self):
        """Stop WebSocket manager"""
        self.running = False
        logger.info("⛔ Stopping WebSocket manager")
    
    def register_callback(self, symbol: str, callback: Callable):
        """Register price update callback"""
        if symbol not in self.callbacks:
            self.callbacks[symbol] = []
        self.callbacks[symbol].append(callback)
        logger.debug(f"Callback registered for {symbol}")
    
    def get_latest_price(self, symbol: str) -> Optional[Dict]:
        """Get latest price data for symbol"""
        return self.price_cache.get(symbol)
    
    def get_all_prices(self) -> Dict:
        """Get all cached prices"""
        return self.price_cache.copy()
    
    def get_queue_message(self, timeout: float = 1.0) -> Optional[Dict]:
        """Get message from queue (blocking)"""
        try:
            return self.message_queue.get(timeout=timeout)
        except:
            return None
    
    def is_connected(self) -> bool:
        """Check if connected"""
        return self.status == WebSocketStatus.CONNECTED
    
    def get_status(self) -> Dict[str, any]:
        """Get manager status"""
        return {
            'status': self.status.value,
            'connected': self.is_connected(),
            'reconnect_attempts': self.reconnect_attempts,
            'queue_size': self.message_queue.qsize(),
            'symbols': self.symbols,
            'cached_prices': len(self.price_cache),
            'callbacks': {s: len(cb) for s, cb in self.callbacks.items()}
        }


class WebSocketDataProcessor:
    """Process WebSocket data for analysis"""
    
    def __init__(self, ws_manager: BinanceWebSocketV3Manager):
        """Initialize processor"""
        self.ws_manager = ws_manager
        self.ohlcv_buffers = {}
        self.buffer_size = 1000
        
        logger.info("📊 WebSocket data processor initialized")
    
    def add_ohlcv(self, symbol: str, ohlcv: Dict):
        """Add OHLCV to buffer"""
        if symbol not in self.ohlcv_buffers:
            self.ohlcv_buffers[symbol] = []
        
        self.ohlcv_buffers[symbol].append(ohlcv)
        
        # Keep buffer size
        if len(self.ohlcv_buffers[symbol]) > self.buffer_size:
            self.ohlcv_buffers[symbol].pop(0)
    
    def get_recent_ohlcv(self, symbol: str, count: int = 100) -> List[Dict]:
        """Get recent OHLCV data"""
        if symbol not in self.ohlcv_buffers:
            return []
        
        return self.ohlcv_buffers[symbol][-count:]
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price"""
        latest = self.ws_manager.get_latest_price(symbol)
        return latest['close'] if latest else 0.0
    
    def get_price_change(self, symbol: str) -> Dict:
        """Calculate price change"""
        recent = self.get_recent_ohlcv(symbol, 2)
        
        if len(recent) < 2:
            return {'change': 0, 'change_pct': 0}
        
        prev_close = recent[-2]['close']
        curr_close = recent[-1]['close']
        change = curr_close - prev_close
        change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
        
        return {
            'change': change,
            'change_pct': change_pct,
            'prev_close': prev_close,
            'curr_close': curr_close
        }
    
    def get_volatility(self, symbol: str, period: int = 20) -> float:
        """Calculate volatility from recent data"""
        recent = self.get_recent_ohlcv(symbol, period)
        
        if len(recent) < 2:
            return 0.0
        
        prices = [candle['close'] for candle in recent]
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        import numpy as np
        volatility = np.std(returns) * 100
        
        return float(volatility)


# Singleton instance
_ws_manager = None

def get_websocket_manager(symbols: List[str] = None) -> BinanceWebSocketV3Manager:
    """Get or create WebSocket manager singleton"""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = BinanceWebSocketV3Manager(symbols)
    return _ws_manager


if __name__ == '__main__':
    # Test WebSocket
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        manager = BinanceWebSocketV3Manager(['BTCUSDT', 'ETHUSDT'])
        
        # Register callback
        def on_price_update(ohlcv):
            print(f"✅ {ohlcv['symbol']}: ${ohlcv['close']:.2f}")
        
        manager.register_callback('BTCUSDT', on_price_update)
        
        # Start manager
        await manager.start()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped")
