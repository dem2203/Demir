"""
🔱 DEMIR AI TRADING BOT - WEBSOCKET STREAM MANAGER
Version: 1.0
Date: 1 Kasım 2025
Purpose: Real-time Binance WebSocket price streams

FEATURES:
- Real-time price updates (every second)
- Multi-coin simultaneous streams (BTC/ETH/LTC)
- Auto-reconnect on disconnect
- Background thread (non-blocking)
- Streamlit session state integration
"""

import json
import threading
import time
from websocket import WebSocketApp

class BinanceWebSocketManager:
    def __init__(self, symbols):
        """
        Initialize WebSocket manager for multiple trading pairs
        
        Args:
            symbols: list of trading pairs, e.g., ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
        """
        self.symbols = [s.lower() for s in symbols]
        self.prices = {s.upper(): None for s in symbols}
        self.ws = None
        self.thread = None
        self.running = False
        self.connected = False
        self.last_update = {}
        
    def _create_stream_url(self):
        """Create Binance WebSocket URL for multiple streams"""
        streams = [f"{symbol}@ticker" for symbol in self.symbols]
        stream_names = "/".join(streams)
        return f"wss://stream.binance.com:9443/stream?streams={stream_names}"
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            if 'data' in data:
                ticker = data['data']
                symbol = ticker['s']  # e.g., 'BTCUSDT'
                price = float(ticker['c'])  # Last price
                
                # Update internal state
                self.prices[symbol] = price
                self.last_update[symbol] = time.time()
                
                # Note: Streamlit session state updated in main app
                
        except Exception as e:
            print(f"❌ WebSocket message error: {e}")
    
    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"❌ WebSocket error: {error}")
        self.connected = False
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print(f"⚠️ WebSocket closed: {close_status_code} - {close_msg}")
        self.connected = False
        
        # Auto-reconnect after 5 seconds
        if self.running:
            print("🔄 Reconnecting in 5 seconds...")
            time.sleep(5)
            if self.running:  # Check again in case stopped during sleep
                self._start_connection()
    
    def _on_open(self, ws):
        """Handle WebSocket open"""
        print(f"✅ WebSocket connected: {len(self.symbols)} streams")
        self.connected = True
    
    def _start_connection(self):
        """Start WebSocket connection"""
        url = self._create_stream_url()
        self.ws = WebSocketApp(
            url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        self.ws.run_forever()
    
    def start(self):
        """Start WebSocket in background thread"""
        if self.running:
            print("⚠️ WebSocket already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._start_connection, daemon=True)
        self.thread.start()
        print(f"🚀 WebSocket thread started for {self.symbols}")
    
    def stop(self):
        """Stop WebSocket"""
        self.running = False
        self.connected = False
        if self.ws:
            self.ws.close()
        print("🛑 WebSocket stopped")
    
    def get_price(self, symbol):
        """Get latest price for a symbol"""
        return self.prices.get(symbol.upper())
    
    def get_all_prices(self):
        """Get all latest prices"""
        return self.prices.copy()
    
    def is_connected(self):
        """Check if WebSocket is connected"""
        return self.connected
    
    def get_connection_status(self):
        """Get detailed connection status"""
        return {
            'connected': self.connected,
            'running': self.running,
            'symbols': [s.upper() for s in self.symbols],
            'prices': self.prices.copy(),
            'last_updates': self.last_update.copy()
        }


# Singleton instance for Streamlit
_ws_manager = None

def get_websocket_manager(symbols=None):
    """
    Get or create WebSocket manager singleton
    
    Args:
        symbols: list of trading pairs (only used on first call)
    
    Returns:
        BinanceWebSocketManager instance
    """
    global _ws_manager
    
    if _ws_manager is None and symbols:
        _ws_manager = BinanceWebSocketManager(symbols)
        _ws_manager.start()
    
    return _ws_manager

def stop_websocket():
    """Stop WebSocket manager"""
    global _ws_manager
    if _ws_manager:
        _ws_manager.stop()
        _ws_manager = None


# Usage Example (for testing):
if __name__ == "__main__":
    # Test WebSocket with BTC, ETH, LTC
    ws = BinanceWebSocketManager(['BTCUSDT', 'ETHUSDT', 'LTCUSDT'])
    ws.start()
    
    try:
        # Run for 30 seconds
        for i in range(30):
            time.sleep(1)
            prices = ws.get_all_prices()
            status = "🟢 LIVE" if ws.is_connected() else "🔴 DISCONNECTED"
            print(f"{status} | BTC: ${prices.get('BTCUSDT', 'N/A'):,.2f} | ETH: ${prices.get('ETHUSDT', 'N/A'):,.2f} | LTC: ${prices.get('LTCUSDT', 'N/A'):,.2f}")
    except KeyboardInterrupt:
        print("\n⚠️ Stopping...")
    finally:
        ws.stop()
        print("✅ Test completed")
