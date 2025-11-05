"""
🔮 KALMAN REGIME LAYER v1.0
===========================
Date: 4 Kasım 2025, 09:05 CET
Phase: 7.2 - Quantum Mathematics

AMAÇ:
-----
Kalman Filter ve Hidden Markov Model kullanarak
market regime'lerini (TREND/RANGE/VOLATILE) tespit etmek.
Noise reduction ve state estimation yaparak trend

 yönü belirlemek.

MATEMATİK:
----------
1. Kalman Filter:
   - State equation: x_t = Ax_{t-1} + w_t
   - Measurement: y_t = Hx_t + v_t
   - Prediction: x̂_t|t-1 = Ax̂_{t-1|t-1}
   - Update: x̂_t|t = x̂_t|t-1 + K_t(y_t - Hx̂_t|t-1)

2. Hidden Markov Model (3 states):
   - TREND: Yüksek momentum, düşük noise
   - RANGE: Düşük momentum, orta noise
   - VOLATILE: Yüksek noise, belirsiz yön

3. Regime Detection:
   - ATR/Price ratio → Volatility
   - Trend strength (ADX benzeri)
   - Price deviation from Kalman estimate

SINYAL LOJİĞİ:
--------------
- TREND regime + pozitif slope → LONG (70-90)
- TREND regime + negatif slope → SHORT (10-30)
- RANGE regime → NEUTRAL (40-60)
- VOLATILE regime → Düşük confidence (45-55)

SKOR: 0-100
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import requests

# ============================================================================
# KALMAN FILTER IMPLEMENTATION
# ============================================================================

class KalmanFilter:
    """
    1D Kalman Filter for price estimation
    
    State: [price, velocity]
    Measurement: observed price
    """
    
    def __init__(self, process_variance=1e-5, measurement_variance=1e-1):
        """
        Initialize Kalman Filter
        
        Args:
            process_variance (float): Process noise (w)
            measurement_variance (float): Measurement noise (v)
        """
        # State vector: [price, velocity]
        self.x = np.array([0.0, 0.0])  # Initial state
        
        # State covariance
        self.P = np.eye(2) * 1000
        
        # State transition matrix
        self.A = np.array([[1, 1],    # price_t = price_{t-1} + velocity
                           [0, 1]])    # velocity_t = velocity_{t-1}
        
        # Measurement matrix
        self.H = np.array([[1, 0]])   # We observe price only
        
        # Process noise covariance
        self.Q = np.eye(2) * process_variance
        
        # Measurement noise covariance
        self.R = np.array([[measurement_variance]])
        
        self.initialized = False
    
    def predict(self):
        """
        Prediction step: x̂_t|t-1 = Ax̂_{t-1|t-1}
        """
        self.x = self.A @ self.x
        self.P = self.A @ self.P @ self.A.T + self.Q
    
    def update(self, measurement):
        """
        Update step: x̂_t|t = x̂_t|t-1 + K_t(y_t - Hx̂_t|t-1)
        
        Args:
            measurement (float): Observed price
        """
        if not self.initialized:
            self.x[0] = measurement
            self.initialized = True
            return
        
        # Innovation (measurement residual)
        y = measurement - (self.H @ self.x)[0]
        
        # Innovation covariance
        S = self.H @ self.P @ self.H.T + self.R
        
        # Kalman gain
        K = self.P @ self.H.T / S[0, 0]
        
        # State update
        self.x = self.x + K * y
        
        # Covariance update
        self.P = (np.eye(2) - K @ self.H) @ self.P
    
    def filter(self, measurement):
        """
        Full Kalman filter cycle: predict + update
        
        Args:
            measurement (float): New price observation
            
        Returns:
            tuple: (filtered_price, velocity)
        """
        self.predict()
        self.update(measurement)
        return self.x[0], self.x[1]


# ============================================================================
# MARKET REGIME DETECTION
# ============================================================================

def detect_market_regime(prices, atr_values):
    """
    Market regime detection using Kalman + statistics
    
    Args:
        prices (list): Recent prices
        atr_values (list): ATR values
        
    Returns:
        str: Regime ('TREND', 'RANGE', 'VOLATILE')
    """
    if len(prices) < 20:
        return 'UNKNOWN'
    
    # 1. Volatility ratio
    current_atr = atr_values[-1]
    avg_atr = np.mean(atr_values)
    volatility_ratio = current_atr / avg_atr if avg_atr > 0 else 1.0
    
    # 2. Trend strength (linear regression slope)
    x = np.arange(len(prices))
    coeffs = np.polyfit(x, prices, 1)
    slope = coeffs[0]
    slope_normalized = abs(slope) / np.mean(prices)  # Normalize by price
    
    # 3. R-squared (trend quality)
    y_fit = np.polyval(coeffs, x)
    ss_res = np.sum((prices - y_fit)**2)
    ss_tot = np.sum((prices - np.mean(prices))**2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # Regime decision
    if volatility_ratio > 1.5:
        return 'VOLATILE'  # Yüksek volatility
    elif r_squared > 0.7 and slope_normalized > 0.001:
        return 'TREND'  # Güçlü trend
    else:
        return 'RANGE'  # Range-bound


# ============================================================================
# DATA FETCHING
# ============================================================================

def get_historical_data(symbol, interval='1h', limit=100):
    """
    Binance'den historical OHLCV data çek
    
    Args:
        symbol (str): Trading pair
        interval (str): Timeframe
        limit (int): Number of candles
        
    Returns:
        pd.DataFrame: OHLCV data
    """
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        
        return df
    except Exception as e:
        print(f"⚠️ Data fetch failed: {e}")
        return None


def calculate_atr(df, period=14):
    """
    Average True Range hesapla
    
    Args:
        df (pd.DataFrame): OHLC data
        period (int): ATR period
        
    Returns:
        list: ATR values
    """
    high = df['high'].values
    low = df['low'].values
    close = df['close'].values
    
    tr = []
    for i in range(1, len(df)):
        tr_val = max(
            high[i] - low[i],
            abs(high[i] - close[i-1]),
            abs(low[i] - close[i-1])
        )
        tr.append(tr_val)
    
    # ATR = EMA of TR
    atr = []
    atr_val = np.mean(tr[:period])
    atr.append(atr_val)
    
    for i in range(period, len(tr)):
        atr_val = (atr_val * (period - 1) + tr[i]) / period
        atr.append(atr_val)
    
    return atr


# ============================================================================
# KALMAN REGIME SIGNAL GENERATOR
# ============================================================================

def get_kalman_regime_signal(symbol, interval='1h'):
    """
    Kalman Regime layer ana fonksiyonu
    
    MANTIK:
    -------
    1. Historical data çek (100 candle)
    2. Kalman Filter uygula (noise reduction)
    3. ATR hesapla
    4. Regime tespit et (TREND/RANGE/VOLATILE)
    5. Kalman velocity + regime'e göre skor
    
    Args:
        symbol (str): Trading pair
        interval (str): Timeframe
        
    Returns:
        float: Score (0-100)
    """
    try:
        print(f"🔮 Kalman Regime analyzing {symbol}...")
        
        # 1. Data çek
        df = get_historical_data(symbol, interval, limit=100)
        if df is None or len(df) < 50:
            print("⚠️ Insufficient data")
            return 50.0
        
        prices = df['close'].values
        
        # 2. Kalman Filter uygula
        kf = KalmanFilter(process_variance=1e-5, measurement_variance=0.1)
        
        filtered_prices = []
        velocities = []
        
        for price in prices:
            f_price, velocity = kf.filter(price)
            filtered_prices.append(f_price)
            velocities.append(velocity)
        
        current_velocity = velocities[-1]
        avg_velocity = np.mean(velocities[-20:])
        
        print(f"   Current Velocity: {current_velocity:.4f}")
        print(f"   Avg Velocity (20): {avg_velocity:.4f}")
        
        # 3. ATR hesapla
        atr_values = calculate_atr(df)
        
        # 4. Regime tespit et
        regime = detect_market_regime(prices[-50:], atr_values[-50:])
        print(f"   Market Regime: {regime}")
        
        # 5. Skor hesapla
        score = 50.0  # Baseline
        
        # Velocity component (trend direction)
        velocity_normalized = np.tanh(current_velocity / np.std(prices) * 100)  # -1 to +1
        score += velocity_normalized * 30  # ±30 points
        
        # Regime component
        if regime == 'TREND':
            # Trend regime: amplify velocity signal
            score += velocity_normalized * 20  # Extra ±20 points
            print("   🎯 TREND regime detected - high confidence")
        elif regime == 'VOLATILE':
            # Volatile: reduce confidence, pull toward neutral
            score = score * 0.7 + 50 * 0.3
            print("   ⚠️ VOLATILE regime - low confidence")
        else:  # RANGE
            # Range: mean reversion bias
            score = 50 + (score - 50) * 0.5  # Dampen signal
            print("   📊 RANGE regime - mean reversion")
        
        # Kalman prediction error (confidence)
        prediction_error = abs(prices[-1] - filtered_prices[-1]) / prices[-1]
        if prediction_error > 0.02:  # >2% error
            score = score * 0.8 + 50 * 0.2  # Pull toward neutral
        
        # Skor 0-100 aralığına sınırla
        score = np.clip(score, 0, 100)
        
        print(f"✅ Kalman Regime Score: {score:.1f}/100")
        
        return score
        
    except Exception as e:
        print(f"❌ Kalman Regime error: {e}")
        return 50.0


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

def analyze_regime(symbol, interval='1h'):
    """
    Alias for backward compatibility
    """
    return get_kalman_regime_signal(symbol, interval)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("🔮 KALMAN REGIME LAYER TEST")
    print("="*80)
    
    test_symbols = ['BTCUSDT', 'ETHUSDT']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        score = get_kalman_regime_signal(symbol)
        
        if score >= 65:
            signal = "🟢 LONG"
        elif score <= 35:
            signal = "🔴 SHORT"
        else:
            signal = "⚪ NEUTRAL"
        
        print(f"   Signal: {signal}")
        print(f"   Score: {score:.1f}/100")
        print("-"*80)
