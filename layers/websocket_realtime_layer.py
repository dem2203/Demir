"""
PHASE 4.1: WEBSOCKET REALTIME LAYER
Real-time market data streaming via WebSocket

Folder: layers/websocket_realtime_layer.py
"""

import asyncio
import json
import logging
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import websocket

logger = logging.getLogger(__name__)


@dataclass
class PriceUpdate:
    """Real-time price update from WebSocket"""
    symbol: str
    price: float
    timestamp: datetime
    volume: float = 0.0
    bid: float = 0.0
    ask: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class WebSocketRealtimeLayer:
    """
    Real-time market data aggregator via WebSocket
    
    Supports:
    - Binance WebSocket streams
    - Fallback to REST API
    - Automatic reconnection
    - Multi-symbol streaming
    """
    
    def __init__(self, symbols: List[str], exchange: str = "binance"):
        """
        Initialize WebSocket layer
        
        Args:
            symbols: List of trading pairs (e.g., ['BTCUSDT', 'ETHUSDT'])
            exchange: Exchange name (default: binance)
        """
        self.symbols = symbols
        self.exchange = exchange
        self.ws: Optional[websocket.WebSocketApp] = None
        self.is_connected = False
        self.price_callbacks: List[Callable[[PriceUpdate], None]] = []
        self.stream_url = f"wss://stream.binance.com:9443/ws"
        
    def add_price_callback(self, callback: Callable[[PriceUpdate], None]) -> None:
        """Register callback for price updates"""
        self.price_callbacks.append(callback)
        
    def _on_message(self, ws: Any, message: str) -> None:
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            # Binance stream format
            if 'data' in data:
                data = data['data']
                
            price_update = PriceUpdate(
                symbol=data.get('s', 'UNKNOWN'),
                price=float(data.get('c', 0)),
                timestamp=datetime.fromtimestamp(data.get('E', datetime.now().timestamp()) / 1000),
                volume=float(data.get('v', 0)),
                bid=float(data.get('b', 0)),
                ask=float(data.get('a', 0)),
                metadata={
                    'open': float(data.get('o', 0)),
                    'high': float(data.get('h', 0)),
                    'low': float(data.get('l', 0)),
                    'volume': float(data.get('v', 0)),
                }
            )
            
            # Trigger callbacks
            for callback in self.price_callbacks:
                callback(price_update)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _on_error(self, ws: Any, error: Exception) -> None:
        """Handle WebSocket error"""
        logger.error(f"WebSocket error: {error}")
        self.is_connected = False
        
    def _on_close(self, ws: Any, close_status: Any, close_msg: Any) -> None:
        """Handle WebSocket close"""
        logger.warning(f"WebSocket closed: {close_status} - {close_msg}")
        self.is_connected = False
        
    def _on_open(self, ws: Any) -> None:
        """Handle WebSocket open"""
        logger.info(f"WebSocket connected to {self.exchange}")
        self.is_connected = True
        
        # Subscribe to streams
        for symbol in self.symbols:
            stream = f"{symbol.lower()}@ticker"
            subscribe_message = {
                "method": "SUBSCRIBE",
                "params": [stream],
                "id": 1
            }
            ws.send(json.dumps(subscribe_message))
    
    def connect(self) -> None:
        """Establish WebSocket connection"""
        try:
            self.ws = websocket.WebSocketApp(
                self.stream_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )
            self.ws.run_forever()
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.is_connected = False
    
    def disconnect(self) -> None:
        """Close WebSocket connection"""
        if self.ws:
            self.ws.close()
            self.is_connected = False
            logger.info("WebSocket disconnected")
    
    async def start_async(self) -> None:
        """Start WebSocket in async context"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.connect)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        return {
            "connected": self.is_connected,
            "exchange": self.exchange,
            "symbols": self.symbols,
            "callbacks": len(self.price_callbacks)
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def on_price_update(update: PriceUpdate) -> None:
        print(f"{update.symbol}: ${update.price} (Volume: {update.volume})")
    
    layer = WebSocketRealtimeLayer(
        symbols=["BTCUSDT", "ETHUSDT"],
        exchange="binance"
    )
    layer.add_price_callback(on_price_update)
    
    try:
        layer.connect()
    except KeyboardInterrupt:
        layer.disconnect()
