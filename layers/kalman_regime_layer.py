"""
🔮 KALMAN FILTER REGIME LAYER v16.5
===================================

Date: 7 Kasım 2025, 14:27 CET
Phase: 7+8 - Quantum Trading AI

AMAÇ:
-----
Kalman filter ile trend tracking ve state estimation.
REAL price data ile noise reduction ve smooth filtering.

MATHEMATIK:
-----------
Prediction: x_k = F*x_(k-1) + w_k
Measurement: z_k = H*x_k + v_k
Kalman Gain: K_k = P_k*H^T / (H*P_k*H^T + R)
State Update: x_k = x_(k-1) + K_k*(z_k - x_(k-1))
"""

import numpy as np
import requests
import pandas as pd
from datetime import datetime

def fetch_ohlcv(symbol, interval='1h', limit=200):
    """Fetch REAL OHLCV data from Binance"""
    debug = {}
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            debug['http_error'] = f"HTTP {response.status_code}"
            return None, debug
        
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base', 
            'taker_buy_quote', 'ignore'
        ])
        
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        
        debug['info'] = f"Fetched {len(df)} real candles"
        return df, debug
        
    except Exception as e:
        debug['exception'] = str(e)
        return None, debug

def calculate_atr(df, length=14):
    """Calculate True Range for volatility"""
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
    except:
        return None

def kalman_filter(prices, process_noise=1e-5, measurement_noise=0.01):
    """
    Kalman filter state estimation
    
    MANTIK:
    1. Initialize Kalman matrices
    2. For each price: predict, then update
    3. Return filtered trend
    """
    try:
        n = len(prices)
        
        # Kalman matrices
        Q = process_noise  # Process variance
        R = measurement_noise  # Measurement variance
        
        xhat = np.zeros(n)
        P = np.zeros(n)
        K = np.zeros(n)
        
        xhat[0] = prices[0]
        P[0] = 1.0
        
        # Apply Kalman filter
        for k in range(1, n):
            # Prediction
            xhat_minus = xhat[k-1]
            P_minus = P[k-1] + Q
            
            # Update
            K[k] = P_minus / (P_minus + R)
            xhat[k] = xhat_minus + K[k] * (prices[k] - xhat_minus)
            P[k] = (1 - K[k]) * P_minus
        
        return xhat[-1]
        
    except:
        return None

def analyze_kalman_regime(symbol='BTCUSDT', interval='1h', length=14):
    """
    Kalman Regime Layer ana fonksiyonu
    
    MANTIK:
    1. Fetch REAL price data
    2. Apply Kalman filter
    3. Calculate ATR volatility
    4. Compare price vs filtered value
    5. Generate signal (0-100)
    """
    debug = {}
    
    try:
        print(f"🔮 Kalman Filter analyzing {symbol}...")
        
        # 1. Get REAL data
        df, fetch_debug = fetch_ohlcv(symbol, interval, 200)
        debug.update(fetch_debug)
        
        if df is None or len(df) < 100:
            print(f"❌ Data fetch failed")
            return {
                'available': False,
                'score': 50,
                'signal': 'NEUTRAL',
                'error_message': 'OHLCV fetch failed',
                'data_debug': debug
            }
        
        prices = df['close'].values
        print(f" 📊 Prices fetched: {len(prices)} real candles")
        
        # 2. Calculate ATR
        atr = calculate_atr(df, length)
        if atr is None:
            atr = np.std(np.diff(prices))
        print(f" 📈 ATR: {atr:.4f}")
        
        # 3. Apply Kalman filter
        kalman_value = kalman_filter(prices)
        if kalman_value is None:
            kalman_value = np.mean(prices)
        print(f" 🔮 Kalman Value: {kalman_value:.2f}")
        
        # 4. Current price
        latest_price = prices[-1]
        print(f" 💰 Latest Price: {latest_price:.2f}")
        
        # 5. Distance from Kalman line
        distance = latest_price - kalman_value
        relative_distance = distance / atr if atr > 0 else 0
        
        print(f" Distance from Kalman: {distance:.4f} ({relative_distance:.2f}σ)")
        
        # 6. Score
        score = 50.0
        
        if latest_price > kalman_value + atr:
            # Above Kalman + ATR
            score = min(90, 50 + abs(relative_distance) * 20)
            signal = "BULLISH"
            print(f" 🚀 Above Kalman channel")
            
        elif latest_price < kalman_value - atr:
            # Below Kalman - ATR
            score = max(10, 50 - abs(relative_distance) * 20)
            signal = "BEARISH"
            print(f" 📉 Below Kalman channel")
            
        else:
            # Within Kalman channel
            score = 50 + relative_distance * 10
            signal = "NEUTRAL"
            print(f" ⚖️ Within Kalman channel")
        
        score = max(0, min(100, score))
        print(f"✅ Kalman Score: {score:.1f}/100")
        
        return {
            'available': True,
            'score': round(score, 2),
            'signal': signal,
            'kalman_value': round(kalman_value, 2),
            'atr': round(atr, 4),
            'latest_price': round(latest_price, 2),
            'distance': round(distance, 4),
            'timestamp': datetime.now().isoformat(),
            'data_debug': debug
        }
        
    except Exception as e:
        print(f"❌ Kalman Filter error: {e}")
        debug['exception'] = str(e)
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL',
            'error_message': str(e),
            'data_debug': debug
        }


if __name__ == "__main__":
    print("="*80)
    print("🔮 KALMAN FILTER REGIME LAYER TEST")
    print("="*80)
    
    test_symbols = ['BTCUSDT', 'ETHUSDT']
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        result = analyze_kalman_regime(symbol)
        print(f" Score: {result['score']}, Signal: {result['signal']}\n")
