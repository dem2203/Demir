"""
DEMIR AI Trading Bot - VWAP Layer
Phase 3A: Institutional Benchmark Analysis
Tarih: 31 Ekim 2025

VWAP (Volume Weighted Average Price):
- VWAP = Σ(Price × Volume) / Σ(Volume)
- Standard Deviations: ±0.5σ, ±1σ, ±2σ, ±3σ

Kullanım:
- Price > VWAP → Bullish, institutions buying
- Price < VWAP → Bearish, institutions selling
- Price at +2σ → Overbought, mean reversion beklenir
- Price at -2σ → Oversold, bounce beklenir
- Price at ±3σ → Extreme, high probability reversal
"""

import numpy as np
import pandas as pd
import requests
from datetime import datetime
from binance.client import Client
import os

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

try:
    binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET) if BINANCE_API_KEY else None
except:
    binance_client = None


def get_intraday_data(symbol, interval='5m', lookback=100):
    """Intraday data çeker (VWAP için)"""
    try:
        if binance_client:
            klines = binance_client.futures_klines(
                symbol=symbol,
                interval=interval,
                limit=lookback
            )
        else:
            url = f"https://fapi.binance.com/fapi/v1/klines"
            params = {'symbol': symbol, 'interval': interval, 'limit': lookback}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                klines = response.json()
            else:
                return None
        
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        
        return df[['timestamp', 'high', 'low', 'close', 'volume', 'typical_price']]
    
    except Exception as e:
        print(f"❌ Intraday data error: {e}")
        return None


def calculate_vwap_bands(symbol, interval='5m', lookback=100):
    """
    VWAP ve deviation bands hesaplar
    
    Returns:
        dict: {
            'vwap': float,
            'upper_05std': float,
            'upper_1std': float,
            'upper_2std': float,
            'upper_3std': float,
            'lower_05std': float,
            'lower_1std': float,
            'lower_2std': float,
            'lower_3std': float
        }
    """
    df = get_intraday_data(symbol, interval, lookback)
    if df is None or df.empty:
        return None
    
    # VWAP = Σ(typical_price × volume) / Σ(volume)
    df['pv'] = df['typical_price'] * df['volume']
    cumulative_pv = df['pv'].cumsum()
    cumulative_volume = df['volume'].cumsum()
    df['vwap'] = cumulative_pv / cumulative_volume
    
    # Standard Deviation = sqrt(Σ((price - vwap)² × volume) / Σvolume)
    df['variance'] = ((df['typical_price'] - df['vwap']) ** 2) * df['volume']
    cumulative_variance = df['variance'].cumsum()
    std_dev = np.sqrt(cumulative_variance / cumulative_volume)
    
    # Current VWAP ve Std Dev
    current_vwap = df['vwap'].iloc[-1]
    current_std = std_dev.iloc[-1]
    
    return {
        'symbol': symbol,
        'interval': interval,
        'vwap': round(current_vwap, 2),
        'std_dev': round(current_std, 2),
        'upper_05std': round(current_vwap + (0.5 * current_std), 2),
        'upper_1std': round(current_vwap + (1.0 * current_std), 2),
        'upper_2std': round(current_vwap + (2.0 * current_std), 2),
        'upper_3std': round(current_vwap + (3.0 * current_std), 2),
        'lower_05std': round(current_vwap - (0.5 * current_std), 2),
        'lower_1std': round(current_vwap - (1.0 * current_std), 2),
        'lower_2std': round(current_vwap - (2.0 * current_std), 2),
        'lower_3std': round(current_vwap - (3.0 * current_std), 2),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def get_vwap_signal(symbol, interval='5m', current_price=None, lookback=100):
    """VWAP sinyali üretir"""
    vwap_data = calculate_vwap_bands(symbol, interval, lookback)
    if not vwap_data:
        return None
    
    if current_price is None:
        try:
            url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                current_price = float(response.json()['price'])
        except:
            return None
    
    vwap = vwap_data['vwap']
    upper_2std = vwap_data['upper_2std']
    upper_3std = vwap_data['upper_3std']
    lower_2std = vwap_data['lower_2std']
    lower_3std = vwap_data['lower_3std']
    
    signal = 'NEUTRAL'
    strength = 0.5
    zone = 'UNKNOWN'
    description = ""
    
    # Extreme overbought (+3σ)
    if current_price >= upper_3std:
        zone = '+3STD'
        signal = 'SHORT'
        strength = 0.95
        description = f"Fiyat +3σ seviyesinde ({current_price} >= {upper_3std}). Extreme overbought - güçlü short sinyali."
    
    # Overbought (+2σ)
    elif current_price >= upper_2std:
        zone = '+2STD'
        signal = 'SHORT'
        strength = 0.75
        description = f"Fiyat +2σ seviyesinde ({current_price} >= {upper_2std}). Overbought - mean reversion beklenir."
    
    # Above VWAP (bullish)
    elif current_price > vwap:
        zone = 'ABOVE_VWAP'
        signal = 'LONG'
        strength = 0.65
        description = f"Fiyat VWAP üzerinde ({current_price} > {vwap}). Bullish - institutions buying."
    
    # Below VWAP (bearish)
    elif current_price < vwap and current_price > lower_2std:
        zone = 'BELOW_VWAP'
        signal = 'SHORT'
        strength = 0.65
        description = f"Fiyat VWAP altında ({current_price} < {vwap}). Bearish - institutions selling."
    
    # Oversold (-2σ)
    elif current_price <= lower_2std and current_price > lower_3std:
        zone = '-2STD'
        signal = 'LONG'
        strength = 0.75
        description = f"Fiyat -2σ seviyesinde ({current_price} <= {lower_2std}). Oversold - bounce beklenir."
    
    # Extreme oversold (-3σ)
    elif current_price <= lower_3std:
        zone = '-3STD'
        signal = 'LONG'
        strength = 0.95
        description = f"Fiyat -3σ seviyesinde ({current_price} <= {lower_3std}). Extreme oversold - güçlü long sinyali."
    
    # At VWAP
    else:
        zone = 'AT_VWAP'
        signal = 'NEUTRAL'
        strength = 0.5
        description = f"Fiyat VWAP'ta ({current_price} ≈ {vwap}). Neutral zone."
    
    return {
        'symbol': symbol,
        'signal': signal,
        'strength': strength,
        'zone': zone,
        'description': description,
        'current_price': current_price,
        'vwap_data': vwap_data,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


if __name__ == "__main__":
    print("=" * 80)
    print("🔱 DEMIR AI - VWAP Layer Test")
    print("=" * 80)
    
    print("\n📈 Calculating VWAP for BTCUSDT...")
    vwap_data = calculate_vwap_bands('BTCUSDT', interval='5m', lookback=100)
    
    if vwap_data:
        print(f"\n✅ VWAP Bands:")
        print(f"   +3σ: ${vwap_data['upper_3std']:,.2f}")
        print(f"   +2σ: ${vwap_data['upper_2std']:,.2f}")
        print(f"   +1σ: ${vwap_data['upper_1std']:,.2f}")
        print(f"  VWAP: ${vwap_data['vwap']:,.2f} ⭐")
        print(f"   -1σ: ${vwap_data['lower_1std']:,.2f}")
        print(f"   -2σ: ${vwap_data['lower_2std']:,.2f}")
        print(f"   -3σ: ${vwap_data['lower_3std']:,.2f}")
        print(f"   Std Dev: ${vwap_data['std_dev']:,.2f}")
        
        signal = get_vwap_signal('BTCUSDT', interval='5m')
        if signal:
            print(f"\n🎯 Trading Signal:")
            print(f"   Signal: {signal['signal']}")
            print(f"   Strength: {signal['strength']:.2f}")
            print(f"   Zone: {signal['zone']}")
            print(f"   Description: {signal['description']}")
    else:
        print("❌ VWAP calculation failed")
    
    print("\n" + "=" * 80)
