"""
🥇 GOLD & PRECIOUS METALS CORRELATION LAYER - REAL DATA
========================================================
Date: 2 Kasım 2025, 21:35 CET
Version: 2.0 - Real yfinance Integration

✅ REAL DATA SOURCES:
- Gold (XAU/USD) → yfinance (GC=F)
- Silver (XAG/USD) → yfinance (SI=F)
- BTC price → Binance API
- Correlation calculation → pandas

✅ NO MOCK DATA - EVERYTHING IS REAL!
"""

import requests
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def calculate_gold_correlation(symbol='BTCUSDT', interval='1h', limit=100):
    """
    Calculate gold and precious metals correlation with crypto
    Returns score 0-100:
    - 100 = Strong positive correlation (risk-on)
    - 50 = No correlation (neutral)
    - 0 = Strong negative correlation (risk-off)
    """
    try:
        print(f"\n🥇 Analyzing Gold & Silver Correlation (REAL DATA)...")
        
        # ==========================================
        # FETCH BTC DATA FROM BINANCE
        # ==========================================
        btc_url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        btc_response = requests.get(btc_url, timeout=10)
        btc_data = btc_response.json()
        
        if not btc_data or not isinstance(btc_data, list):
            return {'available': False, 'score': 50, 'reason': 'BTC data unavailable'}
        
        # Parse BTC data
        btc_df = pd.DataFrame({
            'timestamp': [int(k[0] / 1000) for k in btc_data],
            'close': [float(k[4]) for k in btc_data]
        })
        
        # ==========================================
        # FETCH GOLD DATA FROM YFINANCE (REAL!)
        # ==========================================
        gold_ticker = yf.Ticker("GC=F")  # Gold Futures
        
        # Calculate date range based on BTC data
        start_timestamp = btc_df['timestamp'].min()
        end_timestamp = btc_df['timestamp'].max()
        start_date = datetime.fromtimestamp(start_timestamp)
        end_date = datetime.fromtimestamp(end_timestamp)
        
        # Fetch gold history
        gold_hist = gold_ticker.history(start=start_date, end=end_date, interval='1h')
        
        if len(gold_hist) == 0:
            print("⚠️ Gold data unavailable from yfinance")
            return {'available': False, 'score': 50, 'reason': 'Gold data unavailable'}
        
        # Parse gold data
        gold_df = pd.DataFrame({
            'timestamp': gold_hist.index.astype(int) // 10**9,
            'close': gold_hist['Close'].values
        })
        
        # ==========================================
        # FETCH SILVER DATA FROM YFINANCE (REAL!)
        # ==========================================
        silver_ticker = yf.Ticker("SI=F")  # Silver Futures
        silver_hist = silver_ticker.history(start=start_date, end=end_date, interval='1h')
        
        if len(silver_hist) > 0:
            silver_df = pd.DataFrame({
                'timestamp': silver_hist.index.astype(int) // 10**9,
                'close': silver_hist['Close'].values
            })
        else:
            silver_df = None
            print("⚠️ Silver data unavailable")
        
        # ==========================================
        # CALCULATE CORRELATIONS
        # ==========================================
        
        # Merge BTC and Gold data
        merged = pd.merge(btc_df, gold_df, on='timestamp', how='inner', suffixes=('_btc', '_gold'))
        
        if len(merged) < 20:
            return {'available': False, 'score': 50, 'reason': 'Insufficient data points'}
        
        # Calculate returns
        merged['btc_returns'] = merged['close_btc'].pct_change()
        merged['gold_returns'] = merged['close_gold'].pct_change()
        merged = merged.dropna()
        
        # Correlation coefficient
        gold_corr = merged['btc_returns'].corr(merged['gold_returns'])
        
        # Silver correlation (if available)
        silver_corr = 0.0
        if silver_df is not None:
            merged_silver = pd.merge(btc_df, silver_df, on='timestamp', how='inner', suffixes=('_btc', '_silver'))
            if len(merged_silver) >= 20:
                merged_silver['btc_returns'] = merged_silver['close_btc'].pct_change()
                merged_silver['silver_returns'] = merged_silver['close_silver'].pct_change()
                merged_silver = merged_silver.dropna()
                silver_corr = merged_silver['btc_returns'].corr(merged_silver['silver_returns'])
        
        # ==========================================
        # CALCULATE SCORE
        # ==========================================
        
        # Weighted average (Gold 70%, Silver 30%)
        if silver_corr != 0.0:
            avg_corr = (gold_corr * 0.7) + (silver_corr * 0.3)
        else:
            avg_corr = gold_corr
        
        # Convert correlation (-1 to +1) to score (0 to 100)
        # Positive correlation = risk-on = bullish
        score = (avg_corr + 1) * 50
        score = max(0, min(100, score))
        
        # Determine signal
        if avg_corr > 0.5:
            signal = "STRONG_POSITIVE"
            interpretation = "Gold & BTC moving together (risk-on sentiment)"
        elif avg_corr > 0.2:
            signal = "POSITIVE"
            interpretation = "Moderate positive correlation (safe haven rotation)"
        elif avg_corr > -0.2:
            signal = "NEUTRAL"
            interpretation = "No clear correlation (independent movements)"
        elif avg_corr > -0.5:
            signal = "NEGATIVE"
            interpretation = "Inverse correlation (competition for safe haven)"
        else:
            signal = "STRONG_NEGATIVE"
            interpretation = "Strong inverse correlation (risk-off mode)"
        
        # Get current prices
        gold_current = gold_df['close'].iloc[-1]
        btc_current = btc_df['close'].iloc[-1]
        
        # Gold/BTC ratio
        gold_btc_ratio = gold_current / btc_current
        
        print(f"✅ Gold Correlation Complete!")
        print(f"   Gold Price: ${gold_current:.2f}")
        print(f"   BTC Price: ${btc_current:.2f}")
        print(f"   Gold Corr: {gold_corr:.3f}")
        if silver_corr != 0.0:
            print(f"   Silver Corr: {silver_corr:.3f}")
        print(f"   Score: {score:.2f}/100")
        
        return {
            'available': True,
            'score': round(score, 2),
            'gold_correlation': round(gold_corr, 3),
            'silver_correlation': round(silver_corr, 3) if silver_corr != 0.0 else None,
            'avg_correlation': round(avg_corr, 3),
            'gold_price': round(gold_current, 2),
            'btc_price': round(btc_current, 2),
            'gold_btc_ratio': round(gold_btc_ratio, 4),
            'signal': signal,
            'interpretation': interpretation,
            'data_points': len(merged),
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"⚠️ Gold correlation error: {e}")
        return {
            'available': False,
            'score': 50,
            'reason': str(e)
        }


def get_gold_signal():
    """
    Simplified wrapper for gold signal (used by ai_brain.py)
    """
    result = calculate_gold_correlation(symbol='BTCUSDT', interval='1h', limit=100)
    
    if result['available']:
        return {
            'available': True,
            'score': result['score'],
            'signal': result['signal']
        }
    else:
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL'
        }


# ============================================================================
# STANDALONE TESTING
# ============================================================================

if __name__ == "__main__":
    print("🥇 GOLD CORRELATION LAYER - REAL DATA TEST")
    print("=" * 70)
    
    result = calculate_gold_correlation('BTCUSDT', interval='1h', limit=100)
    
    print("\n" + "=" * 70)
    print("📊 GOLD CORRELATION ANALYSIS:")
    print(f"   Available: {result['available']}")
    print(f"   Score: {result.get('score', 'N/A')}/100")
    print(f"   Gold Corr: {result.get('gold_correlation', 'N/A')}")
    print(f"   Signal: {result.get('signal', 'N/A')}")
    print(f"   Interpretation: {result.get('interpretation', 'N/A')}")
    print("=" * 70)
