"""
DEMIR - Analysis Layer v3.1 FIXED
Binance Futures + Technical Analysis
"""

import pandas as pd
import numpy as np
import requests
from typing import Dict

try:
    from ta.trend import EMAIndicator, MACD, ADXIndicator
    from ta.volatility import BollingerBands, AverageTrueRange
    from ta.momentum import RSIIndicator
except ImportError:
    pass


def get_binance_data(symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
    """Binance FUTURES verisini çek"""
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
        print(f"❌ Binance error: {e}")
        return pd.DataFrame()


def run_technical_analysis(df: pd.DataFrame) -> Dict:
    """Teknik analiz"""
    if df.empty:
        return {'error': 'Empty dataframe'}
    
    try:
        # RSI
        rsi_indicator = RSIIndicator(close=df['Close'], window=14)
        df['RSI'] = rsi_indicator.rsi()
        
        # MACD
        macd = MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        df['MACD_diff'] = macd.macd_diff()
        
        # Bollinger Bands
        bb = BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['BB_High'] = bb.bollinger_hband()
        df['BB_Low'] = bb.bollinger_lband()
        df['BB_Mid'] = bb.bollinger_mavg()
        
        # ATR
        atr = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14)
        df['ATR'] = atr.average_true_range()
        
        # ADX
        adx = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=14)
        df['ADX'] = adx.adx()
        
        # EMA - FIXED: Added EMA_9 and EMA_21
        ema_9 = EMAIndicator(close=df['Close'], window=9)
        ema_20 = EMAIndicator(close=df['Close'], window=20)
        ema_21 = EMAIndicator(close=df['Close'], window=21)
        ema_50 = EMAIndicator(close=df['Close'], window=50)
        
        df['EMA_9'] = ema_9.ema_indicator()
        df['EMA_20'] = ema_20.ema_indicator()
        df['EMA_21'] = ema_21.ema_indicator()
        df['EMA_50'] = ema_50.ema_indicator()
        
        return {
            'dataframe': df,
            'price': float(df['Close'].iloc[-1]),
            'rsi': float(df['RSI'].iloc[-1]) if 'RSI' in df.columns else 50,
            'macd': float(df['MACD'].iloc[-1]) if 'MACD' in df.columns else 0,
            'macd_signal': float(df['MACD_signal'].iloc[-1]) if 'MACD_signal' in df.columns else 0,
            'macd_histogram': float(df['MACD_diff'].iloc[-1]) if 'MACD_diff' in df.columns else 0,
            'BB_High': float(df['BB_High'].iloc[-1]) if 'BB_High' in df.columns else 0,
            'BB_Low': float(df['BB_Low'].iloc[-1]) if 'BB_Low' in df.columns else 0,
            'BB_Mid': float(df['BB_Mid'].iloc[-1]) if 'BB_Mid' in df.columns else 0,
            'atr': float(df['ATR'].iloc[-1]) if 'ATR' in df.columns else 0,
            'adx': float(df['ADX'].iloc[-1]) if 'ADX' in df.columns else 0,
            'ema_9': float(df['EMA_9'].iloc[-1]) if 'EMA_9' in df.columns else 0,
            'ema_20': float(df['EMA_20'].iloc[-1]) if 'EMA_20' in df.columns else 0,
            'ema_21': float(df['EMA_21'].iloc[-1]) if 'EMA_21' in df.columns else 0,
            'ema_50': float(df['EMA_50'].iloc[-1]) if 'EMA_50' in df.columns else 0
        }
    except Exception as e:
        print(f"❌ Technical analysis error: {e}")
        return {'error': str(e)}


def run_full_analysis(symbol: str, timeframe: str = '1h') -> Dict:
    """Full analiz pipeline"""
    df = get_binance_data(symbol, timeframe, limit=100)
    
    if df.empty:
        return {'error': 'No data from Binance'}
    
    tech_data = run_technical_analysis(df)
    
    if 'error' in tech_data:
        return tech_data
    
    # Fibonacci
    high = df['High'].max()
    low = df['Low'].min()
    diff = high - low
    
    tech_data['fibonacci'] = {
        'fib_236': high - 0.236 * diff,
        'fib_382': high - 0.382 * diff,
        'fib_500': high - 0.500 * diff,
        'fib_618': high - 0.618 * diff,
        'fib_786': high - 0.786 * diff
    }
    
    # Volume Profile
    tech_data['volume_profile'] = {
        'vah': high * 0.98,
        'val': low * 1.02,
        'poc': (high + low) / 2
    }
    
    return tech_data
