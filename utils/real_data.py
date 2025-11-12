import requests
import pandas as pd
from datetime import datetime

def get_real_prices():
    """Binance'ten GERÇEKten fiyat al"""
    try:
        url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        prices = {}
        for item in data:
            if item['symbol'] in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']:
                prices[item['symbol']] = {
                    'price': float(item['lastPrice']),
                    'change': float(item['priceChangePercent']),
                    'high': float(item['highPrice']),
                    'low': float(item['lowPrice']),
                    'volume': float(item['volume']),
                    'timestamp': datetime.now().isoformat()
                }
        return prices
    except:
        return None

def get_real_klines(symbol, limit=100):
    """Binance'ten geçmiş fiyatları al"""
    try:
        url = "https://fapi.binance.com/fapi/v1/klines"
        params = {'symbol': symbol, 'interval': '1h', 'limit': limit}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        df = pd.DataFrame(data, columns=[
            'time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        
        df['close'] = df['close'].astype(float)
        return df
    except:
        return None

def calculate_entry_tp_sl(price):
    """Fiyatlardan Entry/TP/SL hesapla"""
    entry = price
    tp1 = price * 1.015
    tp2 = price * 1.035
    sl = price * 0.985
    return entry, tp1, tp2, sl
