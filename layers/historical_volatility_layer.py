"""
DEMIR AI Trading Bot - Historical Volatility Index (HVI) Layer
Phase 3B Module 3: Normalized Volatility Measurement
Tarih: 31 Ekim 2025

HVI - Historical Volatility Index
Fiyat hareketlerinin normalize edilmiş volatilitesini ölçer
Z-score normalization ile
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
            
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            
            print(f"✅ HVI: Fetched {len(df)} bars for {symbol} {interval}")
            return df
        else:
            return None
    except Exception as e:
        print(f"❌ HVI: Data fetch error: {e}")
        return None


def calculate_historical_volatility(df, window=20):
    """
    Historical Volatility (Parkinson estimator)
    Uses high-low range for better volatility estimation
    
    HV = sqrt( (1/(4*ln(2))) * mean((ln(H/L))^2) )
    """
    df['hl_ratio'] = np.log(df['high'] / df['low'])
    df['hl_ratio_sq'] = df['hl_ratio'] ** 2
    
    # Parkinson volatility
    df['parkinson_vol'] = np.sqrt(
        (1 / (4 * np.log(2))) * df['hl_ratio_sq'].rolling(window=window).mean()
    )
    
    return df


def calculate_hvi_zscore(df):
    """
    HVI Z-Score:
    Z = (Current Vol - Mean Vol) / StdDev Vol
    
    Interpretation:
    - Z > 2: Very high volatility (2+ std above mean)
    - Z > 1: High volatility
    - -1 < Z < 1: Normal volatility
    - Z < -1: Low volatility
    """
    current_vol = df['parkinson_vol'].iloc[-1]
    mean_vol = df['parkinson_vol'].mean()
    std_vol = df['parkinson_vol'].std()
    
    z_score = (current_vol - mean_vol) / std_vol if std_vol > 0 else 0
    
    return z_score, current_vol, mean_vol, std_vol


def interpret_hvi(z_score):
    """HVI Z-Score yorumlama"""
    if z_score > 2.0:
        level = 'VERY_HIGH'
        description = f'{z_score:.2f}σ (Very high) - Extreme volatility, high risk'
    elif z_score > 1.0:
        level = 'HIGH'
        description = f'{z_score:.2f}σ (High) - Above average volatility'
    elif z_score > -1.0:
        level = 'NORMAL'
        description = f'{z_score:.2f}σ (Normal) - Average volatility range'
    else:
        level = 'LOW'
        description = f'{z_score:.2f}σ (Low) - Below average, potential breakout'
    
    return level, description


def get_hvi_signal(symbol, interval='1h', lookback=100, window=20):
    """
    HVI (Historical Volatility Index) signal
    
    Returns:
        dict: {
            'signal': str,
            'hvi_zscore': float,
            'volatility_level': str,
            'current_vol': float,
            'mean_vol': float,
            'description': str,
            'available': bool
        }
    """
    
    print(f"\n{'='*80}")
    print(f"📊 HVI ANALYSIS: {symbol} {interval}")
    print(f"{'='*80}")
    
    try:
        # 1. Fetch data
        df = fetch_ohlcv_data(symbol, interval, lookback)
        
        if df is None or len(df) < window + 10:
            print(f"⚠️ HVI: Insufficient data")
            return {
                'signal': 'NEUTRAL',
                'hvi_zscore': 0.0,
                'volatility_level': 'UNKNOWN',
                'current_vol': 0.0,
                'mean_vol': 0.0,
                'description': 'Insufficient data for HVI',
                'available': False
            }
        
        # 2. Calculate historical volatility
        df = calculate_historical_volatility(df, window=window)
        
        # 3. Calculate HVI Z-Score
        z_score, current_vol, mean_vol, std_vol = calculate_hvi_zscore(df)
        
        # 4. Interpret level
        level, level_desc = interpret_hvi(z_score)
        
        print(f"\n📊 HVI Results:")
        print(f"   Current Vol: {current_vol*100:.3f}%")
        print(f"   Mean Vol: {mean_vol*100:.3f}%")
        print(f"   StdDev Vol: {std_vol*100:.3f}%")
        print(f"   Z-Score: {z_score:.2f}")
        print(f"   Level: {level}")
        
        # 5. Trading signal based on HVI
        if level == 'VERY_HIGH':
            signal = 'WAIT'
            signal_desc = 'Very high volatility - Wait for stabilization'
        elif level == 'HIGH':
            signal = 'NEUTRAL'
            signal_desc = 'High volatility - Proceed with caution'
        elif level == 'LOW':
            signal = 'LONG'
            signal_desc = 'Low volatility - Breakout potential, consider entry'
        else:
            signal = 'NEUTRAL'
            signal_desc = 'Normal volatility - Standard trading conditions'
        
        description = f"HVI: {level_desc} [{symbol}][{interval}][W:{window}]"
        
        print(f"\n✅ HVI Signal: {signal}")
        print(f"   {signal_desc}")
        print(f"{'='*80}\n")
        
        return {
            'signal': signal,
            'hvi_zscore': float(z_score),
            'volatility_level': level,
            'current_vol': float(current_vol * 100),
            'mean_vol': float(mean_vol * 100),
            'std_vol': float(std_vol * 100),
            'description': description,
            'signal_description': signal_desc,
            'available': True
        }
        
    except Exception as e:
        print(f"❌ HVI: Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'signal': 'NEUTRAL',
            'hvi_zscore': 0.0,
            'volatility_level': 'UNKNOWN',
            'current_vol': 0.0,
            'mean_vol': 0.0,
            'description': f'HVI error: {str(e)}',
            'available': False
        }


# Test
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 DEMIR AI - HVI Layer Test")
    print("=" * 80)
    
    symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
    
    for symbol in symbols:
        result = get_hvi_signal(symbol, interval='1h', lookback=100, window=20)
        
        print(f"\n✅ {symbol} HVI RESULTS:")
        print(f"   Signal: {result['signal']}")
        print(f"   Z-Score: {result['hvi_zscore']:.2f}")
        print(f"   Level: {result['volatility_level']}")
        print(f"   Available: {result['available']}")
        
        if result['available']:
            print(f"   Current Vol: {result['current_vol']:.3f}%")
            print(f"   Mean Vol: {result['mean_vol']:.3f}%")
    
    print("\n" + "=" * 80)
