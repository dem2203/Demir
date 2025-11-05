"""
DEMIR AI Trading Bot - Volatility Squeeze Layer (REAL DATA)
Binance API kullanarak GERÇEK Bollinger Bands + Keltner Channel
Squeeze detection ve breakout analizi
Tarih: 31 Ekim 2025

ÖZELLİKLER:
✅ Binance'den gerçek OHLCV verisi
✅ Bollinger Bands hesaplama
✅ Keltner Channel hesaplama
✅ Squeeze ON/OFF tespiti
✅ Breakout direction analizi
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


def calculate_bollinger_bands(df, period=20, std_dev=2):
    """Bollinger Bands hesaplar"""
    df['bb_middle'] = df['close'].rolling(window=period).mean()
    df['bb_std'] = df['close'].rolling(window=period).std()
    df['bb_upper'] = df['bb_middle'] + (std_dev * df['bb_std'])
    df['bb_lower'] = df['bb_middle'] - (std_dev * df['bb_std'])
    return df


def calculate_keltner_channel(df, period=20, atr_mult=1.5):
    """Keltner Channel hesaplar"""
    # True Range
    df['tr'] = df[['high', 'low', 'close']].apply(
        lambda x: max(
            x['high'] - x['low'],
            abs(x['high'] - df['close'].shift(1).iloc[x.name]) if x.name > 0 else 0,
            abs(x['low'] - df['close'].shift(1).iloc[x.name]) if x.name > 0 else 0
        ),
        axis=1
    )
    
    # ATR
    df['atr'] = df['tr'].rolling(window=period).mean()
    
    # EMA basis
    df['kc_middle'] = df['close'].ewm(span=period, adjust=False).mean()
    df['kc_upper'] = df['kc_middle'] + (atr_mult * df['atr'])
    df['kc_lower'] = df['kc_middle'] - (atr_mult * df['atr'])
    
    return df


def detect_squeeze(df):
    """
    Squeeze tespiti: Bollinger Bands Keltner Channel içinde mi?
    Squeeze ON = BB içinde KC var
    Squeeze OFF = BB dışarı taştı
    """
    df['squeeze_on'] = (df['bb_lower'] > df['kc_lower']) & (df['bb_upper'] < df['kc_upper'])
    return df


def get_squeeze_signal(symbol, interval='1h', lookback=100):
    """
    Volatility Squeeze sinyali üretir (GERÇEK VERİ)
    
    Returns:
        dict: {
            'signal': 'LONG' | 'SHORT' | 'NEUTRAL',
            'squeeze_status': 'ON' | 'OFF',
            'squeeze_duration': int (periods),
            'breakout_direction': 'BULLISH' | 'BEARISH' | 'NONE',
            'description': str,
            'available': bool
        }
    """
    
    print(f"\n🔍 Volatility Squeeze: {symbol} {interval} (REAL DATA)")
    
    # Binance'den veri çek
    df = get_binance_klines(symbol, interval, lookback)
    
    if df is None or len(df) < 40:
        print(f"❌ Insufficient data for {symbol}")
        return {
            'signal': 'NEUTRAL',
            'squeeze_status': 'UNKNOWN',
            'squeeze_duration': 0,
            'breakout_direction': 'NONE',
            'description': f'Insufficient data for squeeze detection [{symbol}]',
            'available': False
        }
    
    # Bollinger Bands ve Keltner Channel hesapla
    df = calculate_bollinger_bands(df, period=20, std_dev=2)
    df = calculate_keltner_channel(df, period=20, atr_mult=1.5)
    df = detect_squeeze(df)
    
    # Drop NaN
    df = df.dropna()
    
    if len(df) < 20:
        return {
            'signal': 'NEUTRAL',
            'squeeze_status': 'UNKNOWN',
            'squeeze_duration': 0,
            'breakout_direction': 'NONE',
            'description': 'Calculation failed',
            'available': False
        }
    
    # Son durum
    current_squeeze = df['squeeze_on'].iloc[-1]
    
    # Squeeze duration (kaç period squeeze ON)
    squeeze_duration = 0
    for i in range(len(df) - 1, -1, -1):
        if df['squeeze_on'].iloc[i]:
            squeeze_duration += 1
        else:
            break
    
    # Breakout direction
    # Momentum: close vs kc_middle
    df['momentum'] = df['close'] - df['kc_middle']
    current_momentum = df['momentum'].iloc[-1]
    prev_momentum = df['momentum'].iloc[-2] if len(df) > 1 else 0
    
    if current_squeeze:
        # Squeeze ON - bekle
        squeeze_status = 'ON'
        signal = 'NEUTRAL'
        breakout_direction = 'NONE'
        
        if squeeze_duration >= 10:
            description = f'ON ({squeeze_duration}p) - Extended squeeze, breakout imminent [{symbol}][{interval}]'
        else:
            description = f'ON ({squeeze_duration}p) - Consolidation phase, wait for breakout [{symbol}][{interval}]'
    
    else:
        # Squeeze OFF - breakout başladı
        squeeze_status = 'OFF'
        
        # Momentum direction
        if current_momentum > 0 and current_momentum > prev_momentum:
            breakout_direction = 'BULLISH'
            signal = 'LONG'
            description = f'OFF ({squeeze_duration}p) - BULLISH breakout detected, momentum positive [{symbol}][{interval}]'
        
        elif current_momentum < 0 and current_momentum < prev_momentum:
            breakout_direction = 'BEARISH'
            signal = 'SHORT'
            description = f'OFF ({squeeze_duration}p) - BEARISH breakout detected, momentum negative [{symbol}][{interval}]'
        
        else:
            breakout_direction = 'NEUTRAL'
            signal = 'NEUTRAL'
            description = f'OFF ({squeeze_duration}p) - Breakout direction unclear [{symbol}][{interval}]'
    
    # Strength
    bb_width = df['bb_upper'].iloc[-1] - df['bb_lower'].iloc[-1]
    kc_width = df['kc_upper'].iloc[-1] - df['kc_lower'].iloc[-1]
    squeeze_ratio = bb_width / kc_width if kc_width > 0 else 1.0
    
    print(f"✅ Status: {squeeze_status}, Duration: {squeeze_duration}p, Breakout: {breakout_direction}, Signal: {signal}")
    
    return {
        'signal': signal,
        'squeeze_status': squeeze_status,
        'squeeze_duration': squeeze_duration,
        'breakout_direction': breakout_direction,
        'current_momentum': round(current_momentum, 2),
        'squeeze_ratio': round(squeeze_ratio, 3),
        'bb_width': round(bb_width, 2),
        'kc_width': round(kc_width, 2),
        'description': description,
        'available': True,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# Test
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 Volatility Squeeze Layer (REAL DATA) Test")
    print("=" * 80)
    
    symbols = ['BTCUSDT', 'ETHUSDT']
    
    for symbol in symbols:
        result = get_squeeze_signal(symbol, '1h', lookback=100)
        
        if result['available']:
            print(f"\n✅ {symbol} Volatility Squeeze:")
            print(f"   Status: {result['squeeze_status']}")
            print(f"   Duration: {result['squeeze_duration']} periods")
            print(f"   Breakout: {result['breakout_direction']}")
            print(f"   Signal: {result['signal']}")
            print(f"   Momentum: {result['current_momentum']}")
        else:
            print(f"\n❌ {symbol}: Data unavailable")
    
    print("\n" + "=" * 80)
