import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def fetch_ohlcv(symbol, interval='1h', limit=200):
    debug = {}
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            debug['http_error'] = f"HTTP status {response.status_code}"
            return None, debug
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        df['close'] = df['close'].astype(float)
        df['low'] = df['low'].astype(float)
        debug['info'] = f"Fetched {len(df)} candles"
        return df, debug
    except Exception as e:
        debug['exception'] = str(e)
        return None, debug

def calculate_atr(df, length=14):
    try:
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        close = df['close'].astype(float)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=length).mean()
        return atr.iloc[-1]
    except Exception as e:
        print(f"⚠️ ATR calculation error: {e}")
        return None

def kalman_filter(prices):
    try:
        n = len(prices)
        sz = (n,) # size of array

        Q = 1e-5 # process variance
        R = 0.01 # estimate of measurement variance

        xhat = np.zeros(sz)
        P = np.zeros(sz)
        xhatminus = np.zeros(sz)
        Pminus = np.zeros(sz)
        K = np.zeros(sz)

        xhat[0] = prices[0]
        P[0] = 1.0

        for k in range(1, n):
            # Time update
            xhatminus[k] = xhat[k-1]
            Pminus[k] = P[k-1] + Q

            # Measurement update
            K[k] = Pminus[k] / (Pminus[k] + R)
            xhat[k] = xhatminus[k] + K[k]*(prices[k] - xhatminus[k])
            P[k] = (1 - K[k]) * Pminus[k]

        return xhat[-1]
    except Exception as e:
        print(f"⚠️ Kalman filter error: {e}")
        return None

def analyze_kalman_regime(symbol='BTCUSDT', interval='1h', length=14):
    crypto_price_debug = {}
    try:
        df, crypto_price_debug = fetch_ohlcv(symbol, interval, 200)
        if df is None or df.empty:
            return {
                'available': False,
                'score': 50,
                'signal': 'NEUTRAL',
                'error_message': 'OHLCV data fetch failed or empty',
                'data_debug': crypto_price_debug
            }

        atr = calculate_atr(df, length)
        if atr is None:
            return {
                'available': False,
                'score': 50,
                'signal': 'NEUTRAL',
                'error_message': 'ATR calculation failed',
                'data_debug': crypto_price_debug
            }

        prices = df['close'].values
        kalman_value = kalman_filter(prices)
        if kalman_value is None:
            return {
                'available': False,
                'score': 50,
                'signal': 'NEUTRAL',
                'error_message': 'Kalman filter failed',
                'data_debug': crypto_price_debug
            }

        latest_price = prices[-1]
        score = 50
        if latest_price > kalman_value + atr:
            score = 80
            signal = "BULLISH"
        elif latest_price < kalman_value - atr:
            score = 20
            signal = "BEARISH"
        else:
            score = 50
            signal = "NEUTRAL"

        return {
            'available': True,
            'score': score,
            'signal': signal,
            'atr': atr,
            'kalman_value': kalman_value,
            'latest_price': latest_price,
            'timestamp': datetime.now().isoformat(),
            'data_debug': crypto_price_debug
        }
    except Exception as e:
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL',
            'error_message': str(e),
            'data_debug': crypto_price_debug
        }

if __name__ == "__main__":
    print("Testing kalman_regime_layer.py")
    result = analyze_kalman_regime()
    print(result)
