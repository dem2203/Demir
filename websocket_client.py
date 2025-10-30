# websocket_client.py
"""
Binance Futures WebSocket Client
Gerçek zamanlı fiyat, hacim ve funding rate akışı
"""

import json
import threading
import time
from typing import Callable, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import websocket
except ImportError:
    logger.warning("websocket-client kütüphanesi yüklü değil. pip install websocket-client")
    websocket = None


class BinanceFuturesWebSocket:
    """
    Binance Futures WebSocket bağlantısı
    7/24 canlı veri akışı sağlar
    """
    
    BASE_URL = "wss://fstream.binance.com/ws"
    
    def __init__(self, symbol: str = "btcusdt"):
        """
        Args:
            symbol: Trading pair (örn: btcusdt, ethusdt)
        """
        if websocket is None:
            raise ImportError("websocket-client kütüphanesi gerekli")
            
        self.symbol = symbol.lower()
        self.ws = None
        self.thread = None
        self.running = False
        
        # Callbacks
        self.on_price_update: Optional[Callable] = None
        self.on_funding_rate: Optional[Callable] = None
        self.on_liquidation: Optional[Callable] = None
        
        # Data storage
        self.latest_price = 0.0
        self.latest_volume = 0.0
        self.latest_funding_rate = 0.0
        self.trade_count = 0
        
    def start(self):
        """WebSocket bağlantısını başlat"""
        if self.running:
            logger.warning("WebSocket zaten çalışıyor")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info(f"✅ WebSocket başlatıldı: {self.symbol}")
    
    def stop(self):
        """WebSocket bağlantısını durdur"""
        self.running = False
        if self.ws:
            self.ws.close()
        logger.info(f"🛑 WebSocket durduruldu: {self.symbol}")
    
    def _run(self):
        """Ana WebSocket döngüsü"""
        while self.running:
            try:
                # Trade stream (fiyat + hacim)
                stream_url = f"{self.BASE_URL}/{self.symbol}@trade"
                
                self.ws = websocket.WebSocketApp(
                    stream_url,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                    on_open=self._on_open
                )
                
                self.ws.run_forever()
                
            except Exception as e:
                logger.error(f"❌ WebSocket hatası: {e}")
                if self.running:
                    time.sleep(5)  # 5 saniye bekle, tekrar dene
    
    def _on_open(self, ws):
        """Bağlantı açıldığında"""
        logger.info(f"🟢 WebSocket bağlantısı kuruldu: {self.symbol}")
    
    def _on_message(self, ws, message):
        """Her yeni veri geldiğinde"""
        try:
            data = json.loads(message)
            
            # Fiyat ve hacim güncelleme
            self.latest_price = float(data.get('p', 0))
            self.latest_volume = float(data.get('q', 0))
            self.trade_count += 1
            
            # Callback çağır (eğer tanımlıysa)
            if self.on_price_update:
                self.on_price_update({
                    'symbol': self.symbol,
                    'price': self.latest_price,
                    'volume': self.latest_volume,
                    'timestamp': data.get('T', 0)
                })
            
        except Exception as e:
            logger.error(f"❌ Mesaj işleme hatası: {e}")
    
    def _on_error(self, ws, error):
        """Hata olduğunda"""
        logger.error(f"❌ WebSocket hatası: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Bağlantı kapandığında"""
        logger.warning(f"⚠️ WebSocket bağlantısı kapandı: {close_status_code}")
        if self.running:
            logger.info("🔄 5 saniye içinde yeniden bağlanılacak...")
    
    def get_latest_data(self) -> Dict[str, Any]:
        """Son veriyi döndür"""
        return {
            'symbol': self.symbol,
            'price': self.latest_price,
            'volume': self.latest_volume,
            'funding_rate': self.latest_funding_rate,
            'trade_count': self.trade_count
        }


class MultiSymbolWebSocket:
    """
    Birden fazla coin'i aynı anda izle
    """
    
    def __init__(self, symbols: list):
        """
        Args:
            symbols: Coin listesi ['btcusdt', 'ethusdt', 'bnbusdt']
        """
        self.symbols = symbols
        self.clients = {}
        
        for symbol in symbols:
            self.clients[symbol] = BinanceFuturesWebSocket(symbol)
    
    def start_all(self):
        """Tüm WebSocket'leri başlat"""
        for symbol, client in self.clients.items():
            client.start()
            logger.info(f"✅ {symbol.upper()} izleniyor")
    
    def stop_all(self):
        """Tüm WebSocket'leri durdur"""
        for client in self.clients.values():
            client.stop()
    
    def get_all_data(self) -> Dict[str, Dict]:
        """Tüm coinlerin son verilerini döndür"""
        return {
            symbol: client.get_latest_data()
            for symbol, client in self.clients.items()
        }


# Test fonksiyonu
if __name__ == "__main__":
    # Tek coin testi
    ws = BinanceFuturesWebSocket("btcusdt")
    
    def price_callback(data):
        print(f"💰 {data['symbol'].upper()}: ${data['price']:,.2f} | Volume: {data['volume']:.4f}")
    
    ws.on_price_update = price_callback
    ws.start()
    
    # 30 saniye çalıştır
    time.sleep(30)
    ws.stop()
    
    print(f"\n📊 Son Veri: {ws.get_latest_data()}")

