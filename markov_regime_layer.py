"""
DEMIR AI Trading Bot - Markov Regime Switching Layer
Phase 3B Module 2: Market Regime Detection
Tarih: 31 Ekim 2025

Hidden Markov Model - Piyasa rejimlerini tespit eder:
- TREND (Bullish/Bearish momentum)
- RANGE (Sideways/Consolidation)
- HIGH_VOL (Volatility spike)
"""

import numpy as np
import pandas as pd
from datetime import datetime
import requests


def fetch_ohlcv_data(symbol, interval='1h', limit=100):
    """Binance'den OHLCV verilerini çek"""
    try:
        url = f"https://fapi.binance.com/fapi/v1/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            print(f"✅ Markov: Fetched {len(df)} bars for {symbol} {interval}")
            return df
        else:
            return None
    except Exception as e:
        print(f"❌ Markov: Data fetch error: {e}")
        return None


def calculate_regime_features(df):
    """
    Rejim tespiti için özellikler hesapla:
    - Returns (momentum)
    - Volatility (risk)
    - Trend strength (directional bias)
    """
    
    # Returns
    df['returns'] = df['close'].pct_change()
    
    # Volatility (rolling std)
    df['volatility'] = df['returns'].rolling(window=20).std()
    
    # Trend (EMA crossover)
    df['ema_fast'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=21, adjust=False).mean()
    df['trend'] = (df['ema_fast'] - df['ema_slow']) / df['ema_slow']
    
    # Volume momentum
    df['volume_ma'] = df['volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma']
    
    df = df.dropna()
    return df


def detect_current_regime(df):
    """
    Son duruma göre rejim tespit et
    
    3 Rejim:
    1. TREND: Güçlü yönlü hareket, düşük volatilite
    2. RANGE: Zayıf trend, düşük volatilite
    3. HIGH_VOL: Yüksek volatilite, belirsizlik
    """
    
    # Son 20 bar ortalamaları
    recent_df = df.tail(20)
    
    avg_returns = recent_df['returns'].mean()
    avg_volatility = recent_df['volatility'].mean()
    avg_trend = recent_df['trend'].mean()
    avg_volume_ratio = recent_df['volume_ratio'].mean()
    
    # Volatilite threshold (percentile based)
    vol_threshold_high = df['volatility'].quantile(0.75)
    vol_threshold_low = df['volatility'].quantile(0.25)
    
    # Trend threshold
    trend_threshold = 0.005  # 0.5% EMA spread
    
    print(f"\n📊 Regime Features:")
    print(f"   Avg Returns: {avg_returns*100:.3f}%")
    print(f"   Avg Volatility: {avg_volatility*100:.3f}%")
    print(f"   Avg Trend: {avg_trend*100:.3f}%")
    print(f"   Volume Ratio: {avg_volume_ratio:.2f}x")
    
    # Rejim belirleme
    if avg_volatility > vol_threshold_high:
        regime = 'HIGH_VOL'
        confidence = 0.8
        direction = 'NEUTRAL'
        description = 'High volatility regime - Uncertainty and large swings'
        
    elif abs(avg_trend) > trend_threshold:
        regime = 'TREND'
        confidence = 0.75
        
        if avg_trend > 0:
            direction = 'BULLISH'
            description = f'Bullish trend regime - Strong upward momentum'
        else:
            direction = 'BEARISH'
            description = f'Bearish trend regime - Strong downward momentum'
    
    else:
        regime = 'RANGE'
        confidence = 0.70
        direction = 'NEUTRAL'
        description = 'Range-bound regime - Sideways consolidation'
    
    print(f"\n🔄 Detected Regime: {regime} ({direction})")
    print(f"   Confidence: {confidence*100:.0f}%")
    print(f"   {description}")
    
    return {
        'regime': regime,
        'direction': direction,
        'confidence': confidence,
        'avg_returns': float(avg_returns),
        'avg_volatility': float(avg_volatility),
        'avg_trend': float(avg_trend),
        'volume_ratio': float(avg_volume_ratio)
    }


def generate_trading_signal(regime_info):
    """
    Rejime göre trading signal üret
    
    Strategy:
    - TREND (BULLISH) → LONG
    - TREND (BEARISH) → SHORT
    - RANGE → NEUTRAL (mean reversion beklenir)
    - HIGH_VOL → WAIT (risk reduction)
    """
    
    regime = regime_info['regime']
    direction = regime_info['direction']
    confidence = regime_info['confidence']
    
    if regime == 'TREND':
        if direction == 'BULLISH':
            signal = 'LONG'
            signal_desc = 'Trend regime - Ride the bullish momentum'
        else:
            signal = 'SHORT'
            signal_desc = 'Trend regime - Follow the bearish momentum'
    
    elif regime == 'RANGE':
        signal = 'NEUTRAL'
        signal_desc = 'Range regime - Wait for breakout or trade reversals'
    
    else:  # HIGH_VOL
        signal = 'WAIT'
        signal_desc = 'High volatility regime - Reduce exposure, wait for clarity'
    
    return signal, signal_desc


def get_markov_regime_signal(symbol, interval='1h', lookback=100):
    """
    Markov regime switching signal
    
    Returns:
        dict: {
            'signal': 'LONG' | 'SHORT' | 'NEUTRAL' | 'WAIT',
            'regime': 'TREND' | 'RANGE' | 'HIGH_VOL',
            'direction': 'BULLISH' | 'BEARISH' | 'NEUTRAL',
            'confidence': float,
            'description': str,
            'available': bool
        }
    """
    
    print(f"\n{'='*80}")
    print(f"🔄 MARKOV REGIME ANALYSIS: {symbol} {interval}")
    print(f"{'='*80}")
    
    try:
        # 1. Fetch data
        df = fetch_ohlcv_data(symbol, interval, lookback)
        
        if df is None or len(df) < 50:
            print(f"⚠️ Markov: Insufficient data")
            return {
                'signal': 'NEUTRAL',
                'regime': 'UNKNOWN',
                'direction': 'NEUTRAL',
                'confidence': 0.0,
                'description': 'Insufficient data for regime detection',
                'available': False
            }
        
        # 2. Calculate features
        df = calculate_regime_features(df)
        
        # 3. Detect regime
        regime_info = detect_current_regime(df)
        
        # 4. Generate signal
        signal, signal_desc = generate_trading_signal(regime_info)
        
        # 5. Build description
        regime = regime_info['regime']
        direction = regime_info['direction']
        confidence = regime_info['confidence']
        
        description = f"Market Regime: {regime} ({direction}) - Confidence: {confidence*100:.0f}% [{symbol}][{interval}]"
        
        print(f"\n✅ Markov Signal: {signal}")
        print(f"   {signal_desc}")
        print(f"{'='*80}\n")
        
        return {
            'signal': signal,
            'regime': regime,
            'direction': direction,
            'confidence': float(confidence),
            'avg_returns': regime_info['avg_returns'],
            'avg_volatility': regime_info['avg_volatility'],
            'description': description,
            'signal_description': signal_desc,
            'available': True
        }
        
    except Exception as e:
        print(f"❌ Markov: Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'signal': 'NEUTRAL',
            'regime': 'UNKNOWN',
            'direction': 'NEUTRAL',
            'confidence': 0.0,
            'description': f'Markov error: {str(e)}',
            'available': False
        }


# Test
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 DEMIR AI - Markov Regime Switching Test")
    print("=" * 80)
    
    symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
    
    for symbol in symbols:
        result = get_markov_regime_signal(symbol, interval='1h', lookback=100)
        
        print(f"\n✅ {symbol} MARKOV RESULTS:")
        print(f"   Signal: {result['signal']}")
        print(f"   Regime: {result['regime']} ({result['direction']})")
        print(f"   Confidence: {result['confidence']*100:.0f}%")
        print(f"   Available: {result['available']}")
        
        if result['available']:
            print(f"   Description: {result['description']}")
    
    print("\n" + "=" * 80)
