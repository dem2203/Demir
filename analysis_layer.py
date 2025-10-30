"""
DEMIR - Analysis Layer
Technical Analysis Functions + Advanced Indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import requests
from scipy.signal import argrelextrema

# ============================================
# BİNANCE DATA FETCHİNG
# ============================================

def get_binance_klines(symbol='BTCUSDT', interval='1h', limit=500):
    """Binance Futures'tan kline verisi çek"""
    url = 'https://fapi.binance.com/fapi/v1/klines'
    params = {
        'symbol': symbol.upper(),
        'interval': interval,
        'limit': limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Tip dönüşümleri
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return pd.DataFrame()


# ============================================
# TEMEL TEKNİK GÖSTERGELER
# ============================================

def calculate_rsi(df, period=14, price_col='close'):
    """RSI (Relative Strength Index)"""
    delta = df[price_col].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(df, fast=12, slow=26, signal=9, price_col='close'):
    """MACD (Moving Average Convergence Divergence)"""
    ema_fast = df[price_col].ewm(span=fast).mean()
    ema_slow = df[price_col].ewm(span=slow).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(df, period=20, std_dev=2, price_col='close'):
    """Bollinger Bands"""
    sma = df[price_col].rolling(window=period).mean()
    std = df[price_col].rolling(window=period).std()
    
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    
    return upper_band, sma, lower_band


def calculate_ema(df, period, price_col='close'):
    """EMA (Exponential Moving Average)"""
    return df[price_col].ewm(span=period).mean()


# ============================================
# ADVANCED: RSI DIVERGENCE
# ============================================

def detect_rsi_divergence(df, rsi_col='RSI', price_col='close', period=14):
    """RSI Divergence tespiti (Bullish & Bearish)"""
    if len(df) < period * 2:
        return {'bullish_divergence': False, 'bearish_divergence': False, 'strength': 0}
    
    # Swing low/high bul
    price_lows_idx = argrelextrema(df[price_col].values, np.less, order=period)[0]
    price_highs_idx = argrelextrema(df[price_col].values, np.greater, order=period)[0]
    
    bullish_div = False
    bearish_div = False
    strength = 0
    
    # Bullish divergence: Price lower low, RSI higher low
    if len(price_lows_idx) >= 2:
        last_idx = price_lows_idx[-1]
        prev_idx = price_lows_idx[-2]
        
        rsi_at_last = df[rsi_col].iloc[last_idx]
        rsi_at_prev = df[rsi_col].iloc[prev_idx]
        
        price_at_last = df[price_col].iloc[last_idx]
        price_at_prev = df[price_col].iloc[prev_idx]
        
        if price_at_last < price_at_prev and rsi_at_last > rsi_at_prev:
            bullish_div = True
            strength = min(100, abs(rsi_at_last - rsi_at_prev) * 10)
    
    # Bearish divergence: Price higher high, RSI lower high
    if len(price_highs_idx) >= 2:
        last_idx = price_highs_idx[-1]
        prev_idx = price_highs_idx[-2]
        
        rsi_at_last = df[rsi_col].iloc[last_idx]
        rsi_at_prev = df[rsi_col].iloc[prev_idx]
        
        price_at_last = df[price_col].iloc[last_idx]
        price_at_prev = df[price_col].iloc[prev_idx]
        
        if price_at_last > price_at_prev and rsi_at_last < rsi_at_prev:
            bearish_div = True
            strength = min(100, abs(rsi_at_last - rsi_at_prev) * 10)
    
    return {
        'bullish_divergence': bullish_div,
        'bearish_divergence': bearish_div,
        'strength': strength
    }


# ============================================
# ADVANCED: FIBONACCI LEVELS
# ============================================

def calculate_fibonacci_levels(df, price_col='close', lookback=100):
    """Fibonacci retracement ve extension seviyeleri"""
    recent_df = df.tail(lookback)
    
    swing_high = recent_df[price_col].max()
    swing_low = recent_df[price_col].min()
    diff = swing_high - swing_low
    
    levels = {
        'swing_high': swing_high,
        'swing_low': swing_low,
        'fib_0': swing_low,
        'fib_236': swing_low + 0.236 * diff,
        'fib_382': swing_low + 0.382 * diff,
        'fib_50': swing_low + 0.5 * diff,
        'fib_618': swing_low + 0.618 * diff,
        'fib_786': swing_low + 0.786 * diff,
        'fib_100': swing_high,
        'fib_1272': swing_high + 0.272 * diff,
        'fib_1618': swing_high + 0.618 * diff
    }
    
    # Mevcut fiyat hangi seviyede?
    current_price = df[price_col].iloc[-1]
    
    if current_price <= levels['fib_236']:
        current_level = "below 23.6%"
    elif current_price <= levels['fib_382']:
        current_level = "23.6%-38.2%"
    elif current_price <= levels['fib_50']:
        current_level = "38.2%-50%"
    elif current_price <= levels['fib_618']:
        current_level = "50%-61.8%"
    elif current_price <= levels['fib_786']:
        current_level = "61.8%-78.6%"
    elif current_price <= levels['fib_100']:
        current_level = "78.6%-100%"
    else:
        current_level = "above 100%"
    
    levels['current_level'] = current_level
    return levels


# ============================================
# ADVANCED: VOLUME PROFILE
# ============================================

def calculate_volume_profile(df, price_col='close', volume_col='volume', bins=20):
    """Volume Profile - POC, VAH, VAL"""
    price_min = df[price_col].min()
    price_max = df[price_col].max()
    
    price_bins = np.linspace(price_min, price_max, bins + 1)
    volume_per_bin = np.zeros(bins)
    
    for i in range(len(df)):
        price = df[price_col].iloc[i]
        volume = df[volume_col].iloc[i]
        
        bin_idx = np.searchsorted(price_bins, price) - 1
        bin_idx = max(0, min(bins - 1, bin_idx))
        volume_per_bin[bin_idx] += volume
    
    # POC
    poc_idx = np.argmax(volume_per_bin)
    poc_price = (price_bins[poc_idx] + price_bins[poc_idx + 1]) / 2
    
    # Value Area (70% volume)
    total_volume = volume_per_bin.sum()
    target_volume = total_volume * 0.70
    
    value_area_indices = [poc_idx]
    accumulated_volume = volume_per_bin[poc_idx]
    
    left_idx = poc_idx - 1
    right_idx = poc_idx + 1
    
    while accumulated_volume < target_volume:
        left_vol = volume_per_bin[left_idx] if left_idx >= 0 else 0
        right_vol = volume_per_bin[right_idx] if right_idx < bins else 0
        
        if left_vol > right_vol and left_idx >= 0:
            value_area_indices.append(left_idx)
            accumulated_volume += left_vol
            left_idx -= 1
        elif right_idx < bins:
            value_area_indices.append(right_idx)
            accumulated_volume += right_vol
            right_idx += 1
        else:
            break
    
    vah_idx = max(value_area_indices)
    val_idx = min(value_area_indices)
    
    vah_price = price_bins[vah_idx + 1]
    val_price = price_bins[val_idx]
    
    return {
        'poc': poc_price,
        'vah': vah_price,
        'val': val_price,
        'value_area_volume': (accumulated_volume / total_volume) * 100
    }


# ============================================
# MAIN ANALYSIS RUNNER
# ============================================

def run_full_analysis(symbol='BTCUSDT', interval='1h') -> Dict[str, Any]:
    """Tüm teknikleri çalıştır"""
    
    # Veri çek
    df = get_binance_klines(symbol, interval, limit=500)
    
    if df.empty:
        return {}
    
    # Temel göstergeler
    df['RSI'] = calculate_rsi(df)
    df['MACD'], df['MACD_signal'], df['MACD_hist'] = calculate_macd(df)
    df['BB_upper'], df['BB_middle'], df['BB_lower'] = calculate_bollinger_bands(df)
    df['EMA_9'] = calculate_ema(df, 9)
    df['EMA_21'] = calculate_ema(df, 21)
    df['EMA_50'] = calculate_ema(df, 50)
    
    # Advanced
    rsi_div = detect_rsi_divergence(df)
    fib_levels = calculate_fibonacci_levels(df)
    volume_profile = calculate_volume_profile(df)
    
    # Son değerler
    last_row = df.iloc[-1]
    
    return {
        'symbol': symbol,
        'interval': interval,
        'timestamp': last_row['timestamp'],
        'price': last_row['close'],
        'rsi': last_row['RSI'],
        'macd': last_row['MACD'],
        'macd_signal': last_row['MACD_signal'],
        'macd_histogram': last_row['MACD_hist'],
        'bb_upper': last_row['BB_upper'],
        'bb_middle': last_row['BB_middle'],
        'bb_lower': last_row['BB_lower'],
        'ema_9': last_row['EMA_9'],
        'ema_21': last_row['EMA_21'],
        'ema_50': last_row['EMA_50'],
        'rsi_divergence': rsi_div,
        'fibonacci': fib_levels,
        'volume_profile': volume_profile,
        'dataframe': df  # Grafik için
    }
