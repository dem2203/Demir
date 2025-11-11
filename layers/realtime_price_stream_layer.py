```python
import json
import threading
import time
from websocket import WebSocketApp
import os
from binance.client import Client

class RealtimePriceStreamLayer:
    """24/7 Real-time price stream from Binance WebSocket"""
    
    def __init__(self, symbols=['BTCUSDT', 'ETHUSDT']):
        self.symbols = [s.lower() for s in symbols]
        self.prices = {s.upper(): None for s in symbols}
        self.ws = None
        self.thread = None
        self.running = False
        
    def on_message(self, ws, msg):
        """Handle WebSocket messages"""
        try:
            data = json.loads(msg)
            symbol = data.get('s', '').upper()
            price = float(data.get('p', 0))
            self.prices[symbol] = price
        except Exception as e:
            print(f"Stream error: {e}")
    
    def create_stream_url(self):
        """Create WebSocket URL for multiple streams"""
        streams = [f"{s.lower()}@ticker" for s in self.symbols]
        return f"wss://stream.binance.com:9443/stream?streams=" + "/".join(streams)
    
    def start(self):
        """Start WebSocket stream"""
        if self.running:
            return
        
        self.running = True
        self.ws = WebSocketApp(
            self.create_stream_url(),
            on_message=self.on_message,
            on_error=lambda ws, err: print(f"WS Error: {err}"),
            on_close=lambda ws: print("WS Closed")
        )
        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop WebSocket stream"""
        self.running = False
        if self.ws:
            self.ws.close()
    
    def analyze(self, symbol='BTCUSDT'):
        """Get real-time price data"""
        try:
            self.start()
            price = self.prices.get(symbol)
            
            if price is None:
                # Fallback to REST API
                api_key = os.getenv('BINANCE_API_KEY')
                api_secret = os.getenv('BINANCE_API_SECRET')
                client = Client(api_key, api_secret)
                ticker = client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])
                self.prices[symbol] = price
            
            return {
                'symbol': symbol,
                'price': float(price) if price else 0,
                'stream': 'live' if self.running else 'api',
                'timestamp': int(time.time() * 1000),
                'status': 'active'
            }
        except Exception as e:
            return {'error': str(e), 'status': 'error'}

realtime_stream = RealtimePriceStreamLayer()
```
