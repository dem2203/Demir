"""
DEMIR - Analysis Layer (v50.0)
Binance Futures API Integration
"""

import pandas as pd
import numpy as np
import requests
from typing import Dict, Tuple, Optional
from scipy.fft import fft
from math import sqrt, log, log2

# Gerekli kütüphaneler
try:
    from arch import arch_model
except ImportError:
    arch_model = None

try:
    import statsmodels.api as sm
except ImportError:
    sm = None

try:
    from ta.trend import EMAIndicator, MACD, ADXIndicator
    from ta.volatility import BollingerBands, AverageTrueRange
    from ta.momentum import RSIIndicator, StochasticOscillator
    from ta.volume import OnBalanceVolumeIndicator, ChaikinMoneyFlowIndicator
except ImportError:
    pass

def get_binance_data(symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
    """
    Binance FUTURES (Perpetual) verisini çek
    """
    url = "https://fapi.binance.com/fapi/v1/klines"
    
    params = {
        'symbol': symbol.upper(),
        'interval': timeframe,
        'limit': limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume',
            'timestamp': 'Timestamp'
        }, inplace=True)
        
        return df
        
    except Exception as e:
        print(f"❌ Binance FUTURES data error ({symbol}): {e}")
        return pd.DataFrame()


def run_full_analysis(symbol: str, timeframe: str = '1h') -> dict:
    """
    Sembol için tam teknik analiz (GÜNCELLENMİŞ)
    """
    df = get_binance_data(symbol, timeframe, limit=200)
    
    if df.empty:
        return {'error': 'Veri çekilemedi'}
    
    # Teknik analiz
    df = run_technical_analysis(df)
    
    if df.empty:
        return {'error': 'Analiz başarısız'}
    
    # Son değerleri al
    last_row = df.iloc[-1]
    current_price = float(last_row['Close'])
    
    return {
        'symbol': symbol,
        'price': current_price,
        'dataframe': df,
        'rsi': float(last_row.get('RSI', 0)),
        'macd_histogram': float(last_row.get('MACDh_12_26_9', 0)),
        'adx': float(last_row.get('ADX', 0)),
        'atr': float(last_row.get('ATR', 0)),
        'volume': float(last_row.get('Volume', 0)),
        'fibonacci': {
            'fib_236': float(last_row.get('fib_236', 0)),
            'fib_382': float(last_row.get('fib_382', 0)),
            'fib_618': float(last_row.get('fib_618', 0))
        },
        'volume_profile': {
            'poc': float(last_row.get('vp_poc', 0)),
            'vah': float(last_row.get('vp_vah', 0)),
            'val': float(last_row.get('vp_val', 0))
        }
    }
