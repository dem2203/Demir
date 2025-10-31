"""
DEMIR AI Trading Bot - Volatility Squeeze Detection Layer
Phase 3B Module 4: Breakout Signal Detection
Tarih: 31 Ekim 2025

Volatility Squeeze: Bollinger Bands + Keltner Channels
Büyük hareket öncesi fiyat daralmasını tespit eder
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
            
            for col in ['open', 'high', 'low', 'close']:
                df[col] = df[col].astype(float)
            
            print(f"✅ Squeeze: Fetched {len(df)} bars for {symbol} {interval}")
            return df
        else:
            return None
    except Exception as e:
        print(f"❌ Squeeze: Data fetch error: {e}")
        return None


def calculate_bollinger_bands(df, period=20, std_dev=2):
    """
    Bollinger Bands
    Middle Band: SMA
    Upper Band: SMA + (std * σ)
    Lower Band: SMA - (std * σ)
    """
    df['bb_middle'] = df['close'].rolling(window=period).mean()
    df['bb_std'] = df['close'].rolling(window=period).std()
    df['bb_upper'] = df['bb_middle'] + (std_dev * df['bb_std'])
    df['bb_lower'] = df['bb_middle'] - (std_dev * df['bb_std'])
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
    
    return df


def calculate_keltner_channels(df, period=20, atr_mult=1.5):
    """
    Keltner Channels
    Middle Line: EMA
    Upper Channel: EMA + (ATR * multiplier)
    Lower Channel: EMA - (ATR * multiplier)
    """
    df['kc_middle'] = df['close'].ewm(span=period, adjust=False).mean()
    
    # ATR calculation
    df['tr'] = np.maximum(
        df['high'] - df['low'],
        np.maximum(
            abs(df['high'] - df['close'].shift(1)),
            abs(df['low'] - df['close'].shift(1))
        )
    )
    df['atr'] = df['tr'].rolling(window=period).mean()
    
    df['kc_upper'] = df['kc_middle'] + (atr_mult * df['atr'])
    df['kc_lower'] = df['kc_middle'] - (atr_mult * df['atr'])
    df['kc_width'] = (df['kc_upper'] - df['kc_lower']) / df['kc_middle']
    
    return df


def detect_squeeze(df):
    """
    Squeeze Detection:
    Squeeze ON: BB inside KC (Bollinger Bands narrower than Keltner Channels)
    Squeeze OFF: BB outside KC (Expansion begins)
    
    Returns:
        squeeze_status: 'ON' | 'OFF'
        squeeze_duration: Number of periods in squeeze
        breakout_direction: 'BULLISH' | 'BEARISH' | None
    """
    
    # Squeeze condition: BB inside KC
    df['squeeze_on'] = (df['bb_lower'] > df['kc_lower']) & (df['bb_upper'] < df['kc_upper'])
    
    # Current status
    current_squeeze = df['squeeze_on'].iloc[-1]
    
    # Squeeze duration (consecutive periods)
    squeeze_duration = 0
    for i in range(len(df) - 1, -1, -1):
        if df['squeeze_on'].iloc[i]:
            squeeze_duration += 1
        else:
            break
    
    # Breakout detection
    if not current_squeeze and squeeze_duration == 0:
        # Just broke out - check direction
        prev_close = df['close'].iloc[-2]
        current_close = df['close'].iloc[-1]
        bb_middle = df['bb_middle'].iloc[-1]
        
        if current_close > bb_middle:
            breakout_direction = 'BULLISH'
        else:
            breakout_direction = 'BEARISH'
    else:
        breakout_direction = None
    
    squeeze_status = 'ON' if current_squeeze else 'OFF'
    
    print(f"\n🎯 Squeeze Detection:")
    print(f"   Status: {squeeze_status}")
    print(f"   Duration: {squeeze_duration} periods")
    if breakout_direction:
        print(f"   Breakout Direction: {breakout_direction}")
    
    return {
        'squeeze_status': squeeze_status,
        'squeeze_duration': squeeze_duration,
        'breakout_direction': breakout_direction,
        'bb_width': float(df['bb_width'].iloc[-1]),
        'kc_width': float(df['kc_width'].iloc[-1])
    }


def get_squeeze_signal(symbol, interval='1h', lookback=100):
    """
    Volatility Squeeze signal
    
    Returns:
        dict: {
            'signal': str,
            'squeeze_status': 'ON' | 'OFF',
            'squeeze_duration': int,
            'breakout_direction': str | None,
            'description': str,
            'available': bool
        }
    """
    
    print(f"\n{'='*80}")
    print(f"🎯 VOLATILITY SQUEEZE ANALYSIS: {symbol} {interval}")
    print(f"{'='*80}")
    
    try:
        # 1. Fetch data
        df = fetch_ohlcv_data(symbol, interval, lookback)
        
        if df is None or len(df) < 50:
            print(f"⚠️ Squeeze: Insufficient data")
            return {
                'signal': 'NEUTRAL',
                'squeeze_status': 'UNKNOWN',
                'squeeze_duration': 0,
                'breakout_direction': None,
                'description': 'Insufficient data for squeeze detection',
                'available': False
            }
        
        # 2. Calculate indicators
        df = calculate_bollinger_bands(df, period=20, std_dev=2)
        df = calculate_keltner_channels(df, period=20, atr_mult=1.5)
        
        # 3. Detect squeeze
        squeeze_info = detect_squeeze(df)
        
        # 4. Generate signal
        squeeze_status = squeeze_info['squeeze_status']
        squeeze_duration = squeeze_info['squeeze_duration']
        breakout_direction = squeeze_info['breakout_direction']
        
        if squeeze_status == 'ON':
            if squeeze_duration >= 10:
                signal = 'WAIT'
                signal_desc = f'Squeeze active ({squeeze_duration} periods) - Breakout imminent, prepare'
            else:
                signal = 'NEUTRAL'
                signal_desc = f'Squeeze active ({squeeze_duration} periods) - Consolidation phase'
        
        else:  # OFF
            if breakout_direction == 'BULLISH':
                signal = 'LONG'
                signal_desc = 'Bullish breakout detected - Strong upward momentum'
            elif breakout_direction == 'BEARISH':
                signal = 'SHORT'
                signal_desc = 'Bearish breakout detected - Strong downward momentum'
            else:
                signal = 'NEUTRAL'
                signal_desc = 'No active squeeze - Normal volatility'
        
        description = f"Volatility Squeeze: {squeeze_status} ({squeeze_duration}p) [{symbol}][{interval}]"
        
        print(f"\n✅ Squeeze Signal: {signal}")
        print(f"   {signal_desc}")
        print(f"{'='*80}\n")
        
        return {
            'signal': signal,
            'squeeze_status': squeeze_status,
            'squeeze_duration': squeeze_duration,
            'breakout_direction': breakout_direction,
            'bb_width': squeeze_info['bb_width'],
            'kc_width': squeeze_info['kc_width'],
            'description': description,
            'signal_description': signal_desc,
            'available': True
        }
        
    except Exception as e:
        print(f"❌ Squeeze: Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'signal': 'NEUTRAL',
            'squeeze_status': 'UNKNOWN',
            'squeeze_duration': 0,
            'breakout_direction': None,
            'description': f'Squeeze error: {str(e)}',
            'available': False
        }


# Test
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 DEMIR AI - Volatility Squeeze Test")
    print("=" * 80)
    
    symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
    
    for symbol in symbols:
        result = get_squeeze_signal(symbol, interval='1h', lookback=100)
        
        print(f"\n✅ {symbol} SQUEEZE RESULTS:")
        print(f"   Signal: {result['signal']}")
        print(f"   Status: {result['squeeze_status']}")
        print(f"   Duration: {result['squeeze_duration']} periods")
        print(f"   Available: {result['available']}")
        
        if result['available'] and result['breakout_direction']:
            print(f"   Breakout: {result['breakout_direction']}")
    
    print("\n" + "=" * 80)
