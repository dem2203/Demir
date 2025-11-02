"""
🔱 TRADITIONAL MARKETS CORRELATION LAYER - REAL DATA
====================================================
Date: 2 Kasım 2025, 21:55 CET
Version: 2.0 - Complete yfinance Integration

✅ REAL DATA SOURCES (ALL FROM YFINANCE - 100% FREE!):
- S&P 500 (^GSPC) → yfinance
- NASDAQ (^IXIC) → yfinance
- Dow Jones (^DJI) → yfinance
- DXY Dollar Index (DX-Y.NYB) → yfinance
- Russell 2000 (^RUT) → yfinance
- BTC correlation → Binance API

✅ NO API KEY REQUIRED - EVERYTHING IS FREE!
✅ ALL FEATURES PRESERVED - NOTHING REMOVED!
"""

import requests
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

class TraditionalMarketsLayer:
    """
    Analyzes correlation between crypto and traditional markets
    Uses REAL-TIME DATA from yfinance (FREE!)
    """
    
    def __init__(self):
        """Initialize with market symbols"""
        # Yahoo Finance symbol mappings
        self.symbols = {
            'SPX': '^GSPC',      # S&P 500
            'NASDAQ': '^IXIC',   # NASDAQ Composite
            'DJI': '^DJI',       # Dow Jones Industrial Average
            'DXY': 'DX-Y.NYB',   # US Dollar Index
            'RUSSELL': '^RUT'    # Russell 2000 (Small Cap)
        }
        
        # Correlation weights
        self.weights = {
            'SPX': 35,       # Highest - main market indicator
            'NASDAQ': 40,    # Highest - tech correlation with crypto
            'DJI': 10,       # Lower - traditional economy
            'DXY': 15,       # Important - inverse correlation
            'RUSSELL': 0     # Optional - not used in scoring by default
        }  # Total = 100
        
        print("✅ Traditional Markets Layer initialized (REAL DATA)")
    
    def fetch_market_data(self, symbol, days=30):
        """
        Fetch market data from Yahoo Finance
        Args:
            symbol: Yahoo Finance symbol
            days: Historical data window
        Returns:
            pandas.DataFrame or None
        """
        try:
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Fetch historical data
            hist = ticker.history(start=start_date, end=end_date)
            
            if len(hist) == 0:
                return None
            
            # Return DataFrame with timestamp and close price
            df = pd.DataFrame({
                'timestamp': hist.index.astype(int) // 10**9,
                'close': hist['Close'].values,
                'volume': hist['Volume'].values
            })
            
            return df if len(df) > 0 else None
            
        except Exception as e:
            print(f"⚠️ Market data fetch error for {symbol}: {e}")
            return None
    
    def fetch_crypto_data(self, symbol='BTCUSDT', days=30):
        """Fetch crypto data from Binance"""
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': '1d',
                'limit': days
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame({
                    'timestamp': [int(candle[0] / 1000) for candle in data],
                    'close': [float(candle[4]) for candle in data],
                    'volume': [float(candle[5]) for candle in data]
                })
                return df
            return None
            
        except Exception as e:
            print(f"⚠️ Crypto data fetch error: {e}")
            return None
    
    def calculate_correlation(self, crypto_df, market_df, window=14):
        """
        Calculate rolling correlation between crypto and market
        Returns:
            float: Correlation coefficient (-1 to +1)
        """
        try:
            if crypto_df is None or market_df is None:
                return 0.0
            
            # Merge dataframes on timestamp
            merged = pd.merge(
                crypto_df,
                market_df,
                on='timestamp',
                how='inner',
                suffixes=('_crypto', '_market')
            )
            
            if len(merged) < window:
                return 0.0
            
            # Calculate returns
            merged['crypto_returns'] = merged['close_crypto'].pct_change()
            merged['market_returns'] = merged['close_market'].pct_change()
            merged = merged.dropna()
            
            if len(merged) < window:
                return 0.0
            
            # Rolling correlation
            correlation = merged['crypto_returns'].rolling(window=window).corr(
                merged['market_returns']
            )
            
            latest_corr = correlation.iloc[-1]
            return latest_corr if not np.isnan(latest_corr) else 0.0
            
        except Exception as e:
            return 0.0
    
    def calculate_market_change(self, df):
        """
        Calculate price change percentage over period
        """
        if df is None or len(df) < 2:
            return 0.0
        
        first_price = df['close'].iloc[0]
        last_price = df['close'].iloc[-1]
        
        change_pct = ((last_price / first_price) - 1) * 100
        return change_pct
    
    def analyze_all_markets(self, crypto_symbol='BTCUSDT', days=30):
        """
        Perform complete traditional markets analysis with REAL DATA
        Returns:
            dict: Complete analysis with scores, correlations, changes
        """
        print(f"\n🌍 Analyzing Traditional Markets for {crypto_symbol} (REAL DATA)...")
        
        # ==========================================
        # FETCH CRYPTO DATA
        # ==========================================
        crypto_df = self.fetch_crypto_data(crypto_symbol, days)
        if crypto_df is None:
            return self._error_response("Failed to fetch crypto data")
        
        crypto_change = self.calculate_market_change(crypto_df)
        
        # ==========================================
        # FETCH ALL MARKET DATA (REAL!)
        # ==========================================
        
        market_data = {}
        correlations = {}
        changes = {}
        
        for name, symbol in self.symbols.items():
            print(f"   Fetching {name} ({symbol})...")
            df = self.fetch_market_data(symbol, days)
            market_data[name] = df
            
            if df is not None:
                # Calculate correlation
                corr = self.calculate_correlation(crypto_df, df)
                correlations[name] = corr
                
                # Calculate price change
                change = self.calculate_market_change(df)
                changes[name] = change
                
                print(f"   ✅ {name}: Corr={corr:.3f}, Change={change:+.2f}%")
            else:
                correlations[name] = 0.0
                changes[name] = 0.0
                print(f"   ⚠️ {name}: Data unavailable")
        
        # ==========================================
        # CALCULATE FACTOR SCORES
        # ==========================================
        
        factor_scores = {}
        
        # S&P 500 Score
        # Positive correlation = risk-on = bullish for crypto
        spx_corr = correlations.get('SPX', 0)
        factor_scores['SPX'] = (spx_corr + 1) * 50  # -1/+1 → 0-100
        
        # NASDAQ Score
        # Tech correlation - strongest predictor
        nasdaq_corr = correlations.get('NASDAQ', 0)
        factor_scores['NASDAQ'] = (nasdaq_corr + 1) * 50
        
        # Dow Jones Score
        dow_corr = correlations.get('DJI', 0)
        factor_scores['DJI'] = (dow_corr + 1) * 50
        
        # DXY Score (INVERSE!)
        # Strong dollar = weak crypto
        dxy_corr = correlations.get('DXY', 0)
        factor_scores['DXY'] = (-dxy_corr + 1) * 50  # Flip sign
        
        # ==========================================
        # CALCULATE WEIGHTED TOTAL SCORE
        # ==========================================
        
        total_score = 0
        for factor, score in factor_scores.items():
            weight = self.weights.get(factor, 0)
            total_score += (score * weight / 100)
        
        total_score = max(0, min(100, total_score))
        
        # ==========================================
        # DETERMINE MARKET REGIME
        # ==========================================
        
        # Analyze price movements
        spx_change = changes.get('SPX', 0)
        nasdaq_change = changes.get('NASDAQ', 0)
        dxy_change = changes.get('DXY', 0)
        
        # Risk-on vs Risk-off
        if spx_change > 3 and nasdaq_change > 3 and dxy_change < -1:
            market_regime = "STRONG_RISK_ON"
            regime_interpretation = "Strong risk-on environment - Very bullish for crypto"
        elif spx_change > 1 and nasdaq_change > 1:
            market_regime = "RISK_ON"
            regime_interpretation = "Risk-on sentiment - Bullish for crypto"
        elif spx_change < -3 and nasdaq_change < -3:
            market_regime = "RISK_OFF"
            regime_interpretation = "Risk-off environment - Bearish for crypto"
        elif spx_change < -1 or nasdaq_change < -1:
            market_regime = "CAUTIOUS"
            regime_interpretation = "Cautious market sentiment - Neutral to bearish"
        else:
            market_regime = "NEUTRAL"
            regime_interpretation = "Balanced market conditions"
        
        # ==========================================
        # DETERMINE SIGNAL
        # ==========================================
        
        if total_score >= 70:
            signal = "VERY_BULLISH"
            explanation = "Strong positive correlation with risk assets - Markets leading crypto higher"
        elif total_score >= 55:
            signal = "BULLISH"
            explanation = "Positive market environment - Favorable conditions for crypto"
        elif total_score >= 45:
            signal = "NEUTRAL"
            explanation = "Mixed signals from traditional markets"
        elif total_score >= 30:
            signal = "BEARISH"
            explanation = "Negative market environment - Headwinds for crypto"
        else:
            signal = "VERY_BEARISH"
            explanation = "Strong risk-off sentiment - Markets pressuring crypto lower"
        
        # ==========================================
        # BUILD RESULT
        # ==========================================
        
        result = {
            'available': True,
            'total_score': round(total_score, 2),
            'signal': signal,
            'explanation': explanation,
            'market_regime': market_regime,
            'regime_interpretation': regime_interpretation,
            
            # Correlations
            'correlations': {k: round(v, 3) for k, v in correlations.items()},
            
            # Factor scores
            'factor_scores': {k: round(v, 2) for k, v in factor_scores.items()},
            
            # Price changes (30-day)
            'price_changes': {
                'crypto': round(crypto_change, 2),
                'SPX': round(changes.get('SPX', 0), 2),
                'NASDAQ': round(changes.get('NASDAQ', 0), 2),
                'DJI': round(changes.get('DJI', 0), 2),
                'DXY': round(changes.get('DXY', 0), 2)
            },
            
            # Summary stats
            'avg_correlation': round(np.mean([v for v in correlations.values() if v != 0]), 3),
            'strongest_correlation': max(correlations.items(), key=lambda x: abs(x[1])) if correlations else ('N/A', 0),
            
            'timestamp': datetime.now().isoformat(),
            'crypto_symbol': crypto_symbol,
            'analysis_period_days': days
        }
        
        print(f"✅ Traditional Markets Analysis Complete!")
        print(f"   Total Score: {result['total_score']}/100")
        print(f"   Signal: {result['signal']}")
        print(f"   Market Regime: {result['market_regime']}")
        
        return result
    
    def _error_response(self, error_msg):
        """Return error response with neutral score"""
        return {
            'available': False,
            'total_score': 50.0,
            'signal': 'NEUTRAL',
            'explanation': f'Error: {error_msg}',
            'correlations': {},
            'factor_scores': {},
            'price_changes': {},
            'timestamp': datetime.now().isoformat(),
            'error': True
        }


# ============================================================================
# SIMPLIFIED WRAPPER FUNCTIONS (FOR ai_brain.py COMPATIBILITY)
# ============================================================================

def get_traditional_markets_signal():
    """
    Simplified wrapper for traditional markets signal
    Used by ai_brain.py for quick access
    
    Returns:
        dict: {'available': bool, 'score': float, 'signal': str}
    """
    layer = TraditionalMarketsLayer()
    result = layer.analyze_all_markets('BTCUSDT', days=30)
    
    return {
        'available': result['available'],
        'score': result.get('total_score', 50),
        'signal': result.get('signal', 'NEUTRAL')
    }


def calculate_traditional_correlation(symbol='BTCUSDT', days=30):
    """
    Full analysis function (backward compatibility)
    """
    layer = TraditionalMarketsLayer()
    return layer.analyze_all_markets(symbol, days)


# ============================================================================
# STANDALONE TESTING
# ============================================================================

if __name__ == "__main__":
    print("🔱 TRADITIONAL MARKETS LAYER - REAL DATA TEST")
    print("=" * 70)
    
    layer = TraditionalMarketsLayer()
    result = layer.analyze_all_markets('BTCUSDT', days=30)
    
    print("\n" + "=" * 70)
    print("📊 TRADITIONAL MARKETS ANALYSIS:")
    print(f"   Total Score: {result['total_score']}/100")
    print(f"   Signal: {result['signal']}")
    print(f"   Market Regime: {result['market_regime']}")
    print(f"   Explanation: {result['explanation']}")
    
    print("\n📈 CORRELATIONS:")
    for market, corr in result['correlations'].items():
        print(f"   {market}: {corr:.3f}")
    
    print("\n💹 PRICE CHANGES (30d):")
    for market, change in result['price_changes'].items():
        print(f"   {market}: {change:+.2f}%")
    
    print("\n🎯 FACTOR SCORES:")
    for factor, score in result['factor_scores'].items():
        print(f"   {factor}: {score:.2f}/100")
    
    print("=" * 70)
