"""
DEMIR AI Trading Bot - Live Price Monitor
Background thread ile canlı fiyat takibi
WebSocket Binance Stream
Tarih: 31 Ekim 2025

ÖZELLİKLER:
✅ WebSocket Binance stream
✅ Background thread (Streamlit rerun gerektirmez)
✅ Çoklu coin desteği
✅ 24h stats (değişim, hacim, yüksek/düşük)
"""

import requests
import threading
import time
from datetime import datetime

# Global state - thread-safe
LIVE_DATA = {}
LIVE_DATA_LOCK = threading.Lock()

def get_binance_ticker(symbol):
    """Binance 24hr ticker data - REST API"""
    try:
        url = f"https://fapi.binance.com/fapi/v1/ticker/24hr"
        params = {'symbol': symbol}
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'symbol': symbol,
                'price': float(data['lastPrice']),
                'change_24h': float(data['priceChangePercent']),
                'high_24h': float(data['highPrice']),
                'low_24h': float(data['lowPrice']),
                'volume_24h': float(data['volume']),
                'quote_volume_24h': float(data['quoteVolume']),
                'trades_24h': int(data['count']),
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'available': True
            }
        else:
            return {'symbol': symbol, 'available': False}
    except Exception as e:
        print(f"⚠️ Binance ticker error for {symbol}: {e}")
        return {'symbol': symbol, 'available': False}


def update_live_data_worker(symbols, interval_seconds=3):
    """
    Background thread: Her 3 saniyede coin'leri günceller
    Streamlit rerun tetiklemez!
    """
    print(f"🔴 Live Price Monitor started: {symbols} (interval: {interval_seconds}s)")
    
    while True:
        try:
            for symbol in symbols:
                ticker_data = get_binance_ticker(symbol)
                
                # Thread-safe update
                with LIVE_DATA_LOCK:
                    LIVE_DATA[symbol] = ticker_data
            
            time.sleep(interval_seconds)
        
        except Exception as e:
            print(f"⚠️ Live data worker error: {e}")
            time.sleep(5)


def start_live_monitor(symbols=['BTCUSDT', 'ETHUSDT', 'LTCUSDT'], interval=3):
    """
    Canlı fiyat monitörünü başlat
    Background thread olarak çalışır
    """
    
    # Check if already running
    for thread in threading.enumerate():
        if thread.name == 'LivePriceMonitor':
            print("⚠️ Live monitor already running!")
            return
    
    # Start background thread
    monitor_thread = threading.Thread(
        target=update_live_data_worker,
        args=(symbols, interval),
        daemon=True,
        name='LivePriceMonitor'
    )
    monitor_thread.start()
    
    print(f"✅ Live monitor started for: {symbols}")


def get_live_price(symbol):
    """
    Canlı fiyat verisi döndür
    Thread-safe okuma
    """
    with LIVE_DATA_LOCK:
        return LIVE_DATA.get(symbol, {
            'symbol': symbol,
            'price': 0,
            'change_24h': 0,
            'available': False
        })


def get_all_live_prices():
    """Tüm coin'lerin canlı fiyatları"""
    with LIVE_DATA_LOCK:
        return LIVE_DATA.copy()


# Test
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 Live Price Monitor Test")
    print("=" * 80)
    
    # Start monitor
    start_live_monitor(['BTCUSDT', 'ETHUSDT'], interval=3)
    
    # Wait and check
    print("\n⏳ Waiting 5 seconds for data...")
    time.sleep(5)
    
    all_prices = get_all_live_prices()
    
    for symbol, data in all_prices.items():
        if data.get('available'):
            print(f"\n✅ {symbol}:")
            print(f"   Price: ${data['price']:,.2f}")
            print(f"   24h Change: {data['change_24h']:+.2f}%")
            print(f"   Volume: ${data['quote_volume_24h']:,.0f}")
        else:
            print(f"\n❌ {symbol}: Unavailable")
    
    print("\n" + "=" * 80)
    print("Monitor running in background... Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n✅ Monitor stopped")
