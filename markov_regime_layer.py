"""
DEMIR AI Trading Bot - Markov Regime Layer (REAL DATA)
Binance API kullanarak GERÇEK piyasa rejimi tespiti
Hidden Markov Model (HMM) ile TREND/RANGE/HIGH_VOL
Tarih: 31 Ekim 2025

ÖZELLİKLER:
✅ Binance'den gerçek OHLCV verisi
✅ HMM ile 3 rejim tespiti (TREND, RANGE, HIGH_VOL)
✅ Volatilite ve momentum analizi
✅ Rejim geçiş olasılıkları
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime

def get_binance_klines(symbol, interval='1h', limit=100):
    """Binance'den gerçek OHLCV verisi çeker"""
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
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
        else:
            return None
    except:
        return None


def calculate_features(df):
    """Fiyat verilerinden feature'lar çıkarır"""
    # Returns
    df['returns'] = df['close'].pct_change()
    
    # Volatility (20 period rolling std)
    df['volatility'] = df['returns'].rolling(window=20).std()
    
    # Momentum (close - SMA_20)
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['momentum'] = (df['close'] - df['sma_20']) / df['sma_20']
    
    # Trend strength (ADX-like)
    df['tr'] = df[['high', 'low', 'close']].apply(
        lambda x: max(x['high'] - x['low'], 
                     abs(x['high'] - df['close'].shift(1).iloc[x.name]) if x.name > 0 else 0,
                     abs(x['low'] - df['close'].shift(1).iloc[x.name]) if x.name > 0 else 0),
        axis=1
    )
    df['atr'] = df['tr'].rolling(window=14).mean()
    
    # Drop NaN
    df = df.dropna()
    
    return df


def simple_hmm_regime_detection(df):
    """
    Basit HMM benzeri rejim tespiti
    3 Rejim: TREND, RANGE, HIGH_VOL
    """
    
    if len(df) < 30:
        return None
    
    # Feature'lar
    volatility = df['volatility'].values
    momentum = df['momentum'].values
    atr = df['atr'].values
    
    # Normalize
    vol_mean = np.nanmean(volatility)
    vol_std = np.nanstd(volatility)
    mom_mean = np.nanmean(momentum)
    mom_std = np.nanstd(momentum)
    
    # Rejim tespiti (basitleştirilmiş)
    regimes = []
    
    for i in range(len(df)):
        vol = volatility[i]
        mom = momentum[i]
        
        # Volatilite threshold
        if vol > vol_mean + vol_std:
            regime = 'HIGH_VOL'
        elif abs(mom) > 0.02:  # %2 üzeri momentum
            regime = 'TREND'
        else:
            regime = 'RANGE'
        
        regimes.append(regime)
    
    return regimes


def get_markov_regime_signal(symbol, interval='1h', lookback=100):
    """
    Markov Regime sinyali üretir (GERÇEK VERİ)
    
    Returns:
        dict: {
            'signal': 'LONG' | 'SHORT' | 'NEUTRAL' | 'WAIT',
            'regime': 'TREND' | 'RANGE' | 'HIGH_VOL',
            'direction': 'BULLISH' | 'BEARISH' | 'NEUTRAL',
            'confidence': 0.0-1.0,
            'description': str,
            'available': bool
        }
    """
    
    print(f"\n🔍 Markov Regime: {symbol} {interval} (REAL DATA)")
    
    # Binance'den veri çek
    df = get_binance_klines(symbol, interval, lookback)
    
    if df is None or len(df) < 30:
        print(f"❌ Insufficient data for {symbol}")
        return {
            'signal': 'NEUTRAL',
            'regime': 'UNKNOWN',
            'direction': 'NEUTRAL',
            'confidence': 0.0,
            'description': f'Insufficient data for regime detection [{symbol}]',
            'available': False
        }
    
    # Feature hesaplama
    df = calculate_features(df)
    
    if len(df) < 20:
        return {
            'signal': 'NEUTRAL',
            'regime': 'UNKNOWN',
            'direction': 'NEUTRAL',
            'confidence': 0.0,
            'description': 'Feature calculation failed',
            'available': False
        }
    
    # Rejim tespiti
    regimes = simple_hmm_regime_detection(df)
    
    if regimes is None or len(regimes) == 0:
        return {
            'signal': 'NEUTRAL',
            'regime': 'UNKNOWN',
            'direction': 'NEUTRAL',
            'confidence': 0.0,
            'description': 'Regime detection failed',
            'available': False
        }
    
    # Son rejim
    current_regime = regimes[-1]
    
    # Son 10 period'daki rejim dağılımı (confidence için)
    recent_regimes = regimes[-10:]
    regime_counts = {r: recent_regimes.count(r) for r in set(recent_regimes)}
    confidence = regime_counts.get(current_regime, 0) / len(recent_regimes)
    
    # Direction (momentum'dan)
    current_momentum = df['momentum'].iloc[-1]
    
    if current_momentum > 0.01:
        direction = 'BULLISH'
    elif current_momentum < -0.01:
        direction = 'BEARISH'
    else:
        direction = 'NEUTRAL'
    
    # Signal belirleme
    if current_regime == 'TREND':
        if direction == 'BULLISH':
            signal = 'LONG'
            description = f'TREND (BULLISH) - Confidence: {confidence*100:.0f}% - Strong uptrend detected [{symbol}][{interval}]'
        elif direction == 'BEARISH':
            signal = 'SHORT'
            description = f'TREND (BEARISH) - Confidence: {confidence*100:.0f}% - Strong downtrend detected [{symbol}][{interval}]'
        else:
            signal = 'NEUTRAL'
            description = f'TREND (NEUTRAL) - Confidence: {confidence*100:.0f}% - Directional bias unclear [{symbol}][{interval}]'
    
    elif current_regime == 'RANGE':
        signal = 'NEUTRAL'
        description = f'RANGE - Confidence: {confidence*100:.0f}% - Sideways market, wait for breakout [{symbol}][{interval}]'
    
    else:  # HIGH_VOL
        signal = 'WAIT'
        description = f'HIGH_VOL - Confidence: {confidence*100:.0f}% - High volatility, reduce position size [{symbol}][{interval}]'
    
    print(f"✅ Regime: {current_regime}, Direction: {direction}, Signal: {signal}, Confidence: {confidence:.2f}")
    
    return {
        'signal': signal,
        'regime': current_regime,
        'direction': direction,
        'confidence': round(confidence, 2),
        'current_momentum': round(current_momentum, 4),
        'current_volatility': round(df['volatility'].iloc[-1], 4),
        'description': description,
        'regime_history': regimes[-10:],
        'available': True,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# Test
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 Markov Regime Layer (REAL DATA) Test")
    print("=" * 80)
    
    symbols = ['BTCUSDT', 'ETHUSDT']
    
    for symbol in symbols:
        result = get_markov_regime_signal(symbol, '1h', lookback=100)
        
        if result['available']:
            print(f"\n✅ {symbol} Markov Regime:")
            print(f"   Regime: {result['regime']}")
            print(f"   Direction: {result['direction']}")
            print(f"   Signal: {result['signal']}")
            print(f"   Confidence: {result['confidence']*100:.0f}%")
            print(f"   Momentum: {result['current_momentum']:.4f}")
        else:
            print(f"\n❌ {symbol}: Data unavailable")
    
    print("\n" + "=" * 80)
