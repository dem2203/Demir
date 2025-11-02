"""
🔗 CROSS-ASSET CORRELATION LAYER - Phase 6.4
============================================
Analyzes correlation patterns across major crypto assets
- BTC/ETH/LTC/BNB price movements
- Rotation detection
- Correlation strength
- Leader/laggard identification
"""

import requests
import numpy as np
from datetime import datetime

def calculate_cross_asset(interval='1h', limit=100):
    """
    Calculate cross-asset correlation and rotation
    
    Returns score 0-100:
    - 100 = Strong positive correlation (coordinated rally)
    - 50 = Mixed/rotation (assets moving independently)
    - 0 = Strong negative correlation (divergence/selloff)
    """
    
    try:
        symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'BNBUSDT']
        returns_data = {}
        
        # Fetch price data for all assets
        for symbol in symbols:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if not data or not isinstance(data, list):
                continue
            
            closes = np.array([float(candle[4]) for candle in data])
            returns = np.diff(closes) / closes[:-1]
            returns_data[symbol] = returns
        
        if len(returns_data) < 2:
            return {'available': False, 'score': 50, 'reason': 'Insufficient cross-asset data'}
        
        # Calculate pairwise correlations
        correlations = {}
        asset_names = list(returns_data.keys())
        
        for i in range(len(asset_names)):
            for j in range(i+1, len(asset_names)):
                asset1 = asset_names[i]
                asset2 = asset_names[j]
                
                returns1 = returns_data[asset1]
                returns2 = returns_data[asset2]
                
                # Ensure same length
                min_len = min(len(returns1), len(returns2))
                corr = np.corrcoef(returns1[:min_len], returns2[:min_len])[0, 1]
                
                pair_name = f"{asset1[:3]}/{asset2[:3]}"
                correlations[pair_name] = corr
        
        # Calculate average correlation
        avg_correlation = np.mean(list(correlations.values()))
        
        # Calculate recent performance (last 10 periods)
        recent_performance = {}
        for symbol, returns in returns_data.items():
            recent_ret = np.sum(returns[-10:]) * 100  # Last 10 periods cumulative return
            recent_performance[symbol[:3]] = recent_ret
        
        # Identify leader and laggard
        sorted_perf = sorted(recent_performance.items(), key=lambda x: x[1], reverse=True)
        leader = sorted_perf[0][0]
        leader_perf = sorted_perf[0][1]
        laggard = sorted_perf[-1][0]
        laggard_perf = sorted_perf[-1][1]
        
        # Score calculation
        # High positive correlation + positive returns = bullish coordination
        # High positive correlation + negative returns = bearish coordination
        # Low correlation = rotation/uncertainty
        
        if avg_correlation > 0.7:
            if leader_perf > 0:
                score = 75  # Strong coordinated rally
                sentiment = "BULLISH"
                reason = f"Strong positive correlation ({avg_correlation:.2f}) - coordinated rally"
            else:
                score = 25  # Strong coordinated selloff
                sentiment = "BEARISH"
                reason = f"Strong positive correlation ({avg_correlation:.2f}) - coordinated selloff"
        elif avg_correlation > 0.4:
            score = 50 + (leader_perf * 2)  # Moderate correlation, bias toward leader
            score = max(0, min(100, score))
            sentiment = "NEUTRAL"
            reason = f"Moderate correlation ({avg_correlation:.2f}) - some coordination"
        else:
            score = 50  # Low correlation = rotation
            sentiment = "ROTATION"
            reason = f"Low correlation ({avg_correlation:.2f}) - asset rotation active"
        
        return {
            'available': True,
            'score': round(score, 1),
            'sentiment': sentiment,
            'reason': reason,
            'avg_correlation': round(avg_correlation, 3),
            'correlations': {k: round(v, 3) for k, v in correlations.items()},
            'leader': leader,
            'leader_performance': round(leader_perf, 2),
            'laggard': laggard,
            'laggard_performance': round(laggard_perf, 2),
            'performance': {k: round(v, 2) for k, v in recent_performance.items()},
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'available': False,
            'score': 50,
            'reason': f'Cross-asset error: {str(e)[:50]}'
        }

if __name__ == "__main__":
    result = calculate_cross_asset('1h', 100)
    print(f"Cross-Asset Score: {result['score']}")
    print(f"Sentiment: {result.get('sentiment', 'N/A')}")
    print(f"Avg Correlation: {result.get('avg_correlation', 0)}")
    print(f"Leader: {result.get('leader', 'N/A')} ({result.get('leader_performance', 0)}%)")
    print(f"Reason: {result.get('reason', 'N/A')}")
