```python
"""
Professional Binance API Integration
Real-time WebSocket data collection
Advanced market data processing
Production-grade reliability

Author: DEMIR AI v5.0
License: Professional Use
"""

import websocket
import json
import logging
import os
import requests
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Optional, Callable
import threading
import time
from enum import Enum

logger = logging.getLogger(__name__)

class KlineInterval(Enum):
    """Supported kline intervals"""
    ONE_MIN = "1m"
    FIVE_MIN = "5m"
    FIFTEEN_MIN = "15m"
    THIRTY_MIN = "30m"
    ONE_HOUR = "1h"
    FOUR_HOUR = "4h"
    ONE_DAY = "1d"

class BinanceAdvancedAPI:
    """
    Professional Binance API Client
    WebSocket + REST API integration
    Real-time market data with reliability
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 symbols: Optional[List[str]] = None,
                 reconnect_attempts: int = 5,
                 reconnect_delay: int = 3):
        
        # API credentials
        self.api_key = api_key or os.getenv('BINANCE_API_KEY', '')
        self.api_secret = api_secret or os.getenv('BINANCE_API_SECRET', '')
        
        # Configuration
        self.symbols = symbols or ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']
        self.base_url = "https://api.binance.com/api/v3"
        self.websocket_url = "wss://stream.binance.com:9443/ws"
        
        # Reconnection
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay
        
        # Data storage - REAL market data
        self.klines = {s: deque(maxlen=10000) for s in self.symbols}
        self.trades = {s: deque(maxlen=5000) for s in self.symbols}
        self.depth = {s: {'bids': [], 'asks': []} for s in self.symbols}
        self.prices = {s: None for s in self.symbols}
        self.volumes = {s: 0.0 for s in self.symbols}
        
        # WebSocket connections
        self.ws_connections = {}
        self.connection_status = {s: False for s in self.symbols}
        
        # Running state
        self.running = False
        self.last_update = {}
        
        # Callbacks
        self.callbacks = {
            'kline': None,
            'trade': None,
            'depth': None
        }
        
        logger.info("✅ Binance API initialized")
    
    def connect_all_streams(self, interval: KlineInterval = KlineInterval.ONE_MIN):
        """Connect to all symbols' streams"""
        for symbol in self.symbols:
            self.connect_kline_stream(symbol, interval)
        
        self.running = True
        logger.info(f"✅ Connected to {len(self.symbols)} streams")
    
    def connect_kline_stream(self, 
                            symbol: str,
                            interval: KlineInterval = KlineInterval.ONE_MIN,
                            callback: Optional[Callable] = None) -> bool:
        """
        Connect to real kline stream
        Stream REAL market data continuously
        """
        
        stream_name = f"{symbol.lower()}@kline_{interval.value}"
        url = f"{self.websocket_url}/{stream_name}"
        
        def on_message(ws, message):
            """Handle incoming WebSocket message"""
            try:
                data = json.loads(message)
                
                if 'k' in data:
                    kline = data['k']
                    
                    # Parse REAL kline data
                    kline_data = {
                        'symbol': symbol,
                        'timestamp': int(kline['t']),
                        'open': float(kline['o']),
                        'high': float(kline['h']),
                        'low': float(kline['l']),
                        'close': float(kline['c']),
                        'volume': float(kline['v']),
                        'quote_asset_volume': float(kline['q']),
                        'number_of_trades': int(kline['n']),
                        'taker_buy_base_asset_volume': float(kline['V']),
                        'taker_buy_quote_asset_volume': float(kline['Q']),
                        'is_closed': kline['x'],
                        'interval': interval.value
                    }
                    
                    # Store in buffer
                    self.klines[symbol].append(kline_data)
                    self.prices[symbol] = float(kline['c'])
                    self.volumes[symbol] = float(kline['v'])
                    self.last_update[symbol] = datetime.now()
                    
                    # Execute callback if provided
                    if callback:
                        callback(kline_data)
                    if self.callbacks['kline']:
                        self.callbacks['kline'](kline_data)
                    
                    logger.debug(f"✅ {symbol} {interval.value}: {self.prices[symbol]:.2f}")
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
            except KeyError as e:
                logger.error(f"Key error in message: {e}")
            except Exception as e:
                logger.error(f"Message processing error: {e}")
        
        def on_error(ws, error):
            """Handle WebSocket error"""
            logger.error(f"WebSocket error for {symbol}: {error}")
            self.connection_status[symbol] = False
            
            # Attempt reconnection
            if self.running:
                for attempt in range(self.reconnect_attempts):
                    delay = self.reconnect_delay * (2 ** attempt)
                    logger.warning(f"Reconnecting {symbol} in {delay}s (attempt {attempt+1})")
                    time.sleep(delay)
                    try:
                        self.connect_kline_stream(symbol, interval, callback)
                        return
                    except Exception as e:
                        logger.error(f"Reconnection attempt {attempt+1} failed: {e}")
        
        def on_close(ws, close_status_code, close_msg):
            """Handle WebSocket close"""
            logger.warning(f"Connection closed for {symbol}: {close_msg}")
            self.connection_status[symbol] = False
        
        def on_open(ws):
            """Handle WebSocket open"""
            logger.info(f"✅ Connected to {stream_name}")
            self.connection_status[symbol] = True
        
        try:
            # Create WebSocket
            ws = websocket.WebSocketApp(
                url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            self.ws_connections[symbol] = ws
            
            # Run in daemon thread
            wst = threading.Thread(target=ws.run_forever, daemon=True)
            wst.start()
            
            logger.info(f"✅ Started stream thread for {symbol}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to connect {symbol}: {e}")
            return False
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get REAL current price"""
        return self.prices.get(symbol)
    
    def get_current_volume(self, symbol: str) -> float:
        """Get REAL current volume"""
        return self.volumes.get(symbol, 0.0)
    
    def get_klines(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Get REAL kline history"""
        klines = list(self.klines.get(symbol, []))
        return klines[-limit:] if limit else klines
    
    def get_last_kline(self, symbol: str) -> Optional[Dict]:
        """Get most recent REAL kline"""
        klines = self.klines.get(symbol, deque())
        return klines[-1] if klines else None
    
    def get_24h_stats(self, symbol: str) -> Optional[Dict]:
        """Get REAL 24h statistics from REST API"""
        try:
            response = requests.get(
                f"{self.base_url}/ticker/24hr",
                params={'symbol': symbol},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                stats = {
                    'symbol': symbol,
                    'high': float(data['highPrice']),
                    'low': float(data['lowPrice']),
                    'open': float(data['openPrice']),
                    'close': float(data['lastPrice']),
                    'volume': float(data['volume']),
                    'quote_volume': float(data['quoteAssetVolume']),
                    'price_change': float(data['priceChange']),
                    'price_change_percent': float(data['priceChangePercent']),
                    'bid': float(data['bidPrice']),
                    'ask': float(data['askPrice']),
                    'count': int(data['count'])
                }
                logger.info(f"✅ 24h stats {symbol}: {stats['price_change_percent']:.2f}%")
                return stats
            
            return None
        
        except requests.Timeout:
            logger.error(f"Timeout getting 24h stats for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Error getting 24h stats for {symbol}: {e}")
            return None
    
    def get_order_book(self, symbol: str, limit: int = 20) -> Optional[Dict]:
        """Get REAL order book"""
        try:
            response = requests.get(
                f"{self.base_url}/depth",
                params={'symbol': symbol, 'limit': limit},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                orderbook = {
                    'symbol': symbol,
                    'timestamp': data.get('T', int(time.time() * 1000)),
                    'bids': [(float(b[0]), float(b[1])) for b in data['bids']],
                    'asks': [(float(a[0]), float(a[1])) for a in data['asks']]
                }
                
                self.depth[symbol] = orderbook
                return orderbook
            
            return None
        
        except Exception as e:
            logger.error(f"Order book error for {symbol}: {e}")
            return None
    
    def calculate_vwap(self, symbol: str, limit: int = 20) -> Optional[float]:
        """Calculate Volume-Weighted Average Price"""
        try:
            klines = self.get_klines(symbol, limit)
            
            if not klines or len(klines) < 2:
                return None
            
            total_volume = 0.0
            weighted_price = 0.0
            
            for kline in klines:
                tp = (float(kline['high']) + float(kline['low']) + float(kline['close'])) / 3
                v = float(kline['volume'])
                
                weighted_price += tp * v
                total_volume += v
            
            if total_volume > 0:
                vwap = weighted_price / total_volume
                logger.info(f"✅ VWAP {symbol}: {vwap:.2f}")
                return vwap
            
            return None
        
        except Exception as e:
            logger.error(f"VWAP calculation error: {e}")
            return None
    
    def get_connection_status(self) -> Dict[str, bool]:
        """Get all connection statuses"""
        return self.connection_status.copy()
    
    def is_connected(self, symbol: str) -> bool:
        """Check if specific symbol is connected"""
        return self.connection_status.get(symbol, False)
    
    def stop(self):
        """Stop all streams"""
        self.running = False
        
        for symbol, ws in self.ws_connections.items():
            try:
                ws.close()
                logger.info(f"✅ Closed connection for {symbol}")
            except Exception as e:
                logger.error(f"Error closing {symbol}: {e}")
        
        self.ws_connections.clear()
        logger.info("✅ All streams stopped")
    
    def register_callback(self, 
                         event_type: str,
                         callback: Callable):
        """Register callback for events"""
        if event_type in self.callbacks:
            self.callbacks[event_type] = callback
            logger.info(f"✅ Registered callback for {event_type}")
        else:
            logger.warning(f"Unknown event type: {event_type}")
    
    def get_statistics(self) -> Dict:
        """Get API statistics"""
        return {
            'connected_symbols': sum(1 for v in self.connection_status.values() if v),
            'total_symbols': len(self.symbols),
            'total_klines': sum(len(k) for k in self.klines.values()),
            'connection_status': self.connection_status.copy(),
            'last_updates': self.last_update.copy()
        }


# Convenience function for quick start
def create_binance_client(symbols: List[str] = None) -> BinanceAdvancedAPI:
    """Create and connect Binance client"""
    client = BinanceAdvancedAPI(symbols=symbols)
    client.connect_all_streams()
    return client
```
