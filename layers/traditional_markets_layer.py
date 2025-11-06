# traditional_markets_layer.py - v3.2 - Complete Real Data + Fallbacks

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

try:
    from api_cache_manager import fetch_market_data
    CACHE_MANAGER_AVAILABLE = True
except ImportError:
    CACHE_MANAGER_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

class TraditionalMarketsLayer:
    def __init__(self):
        self.symbols = {
            'SPX': 'SPY',
            'NASDAQ': 'QQQ',
            'DJI': '^DJI',
            'DXY': 'DX-Y.NYB',
            'RUSSELL': '^RUT'
        }
        self.weights = {
            'SPX': 35,
            'NASDAQ': 40,
            'DJI': 10,
            'DXY': 15,
            'RUSSELL': 0
        }
        print("✅ Traditional Markets Layer v3.2 initialized")

    def fetch_market_data(self, symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
        if CACHE_MANAGER_AVAILABLE:
            try:
                result = fetch_market_data(
                    symbol=symbol,
                    source_priority=['alpha_vantage', 'twelve_data', 'yfinance'],
                    days=days
                )
                if result['success'] and result['data']:
                    df = pd.DataFrame(result['data'])
                    df['timestamp'] = pd.to_datetime(df['date']).astype(int) // 10**9
                    df['close'] = df['close'].astype(float)
                    df['volume'] = df['volume'].astype(float)
                    return df[['timestamp', 'close', 'volume']]
            except Exception as e:
                print(f"⚠️ Cache Manager error ({symbol}): {e}")

        if YFINANCE_AVAILABLE:
            try:
                ticker = yf.Ticker(symbol)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                hist = ticker.history(start=start_date, end=end_date)
                if not hist.empty:
                    df = pd.DataFrame({
                        'timestamp': hist.index.astype(int) // 10**9,
                        'close': hist['Close'].values,
                        'volume': hist['Volume'].values
                    })
                    return df
            except Exception as e:
                print(f"⚠️ yfinance error ({symbol}): {e}")
        print(f"⚠️ All sources failed for {symbol}")
        return None

    def fetch_crypto_data(self, symbol: str = 'BTCUSDT', days: int = 30) -> Optional[pd.DataFrame]:
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {'symbol': symbol, 'interval': '1d', 'limit': days}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame({
                    'timestamp': [int(candle[0]/1000) for candle in data],
                    'close': [float(candle[4]) for candle in data],
                    'volume': [float(candle[5]) for candle in data]
                })
                return df
            return None
        except Exception as e:
            print(f"⚠️ Crypto data fetch error: {e}")
            return None

    def calculate_correlation(self, crypto_df: pd.DataFrame, market_df: pd.DataFrame, window: int = 14) -> float:
        try:
            if crypto_df is None or market_df is None:
                return 0.0
            merged = pd.merge(crypto_df, market_df, on='timestamp', how='inner', suffixes=('_crypto', '_market'))
            if len(merged) < window:
                return 0.0
            merged['crypto_returns'] = merged['close_crypto'].pct_change()
            merged['market_returns'] = merged['close_market'].pct_change()
            merged = merged.dropna()
            if len(merged) < window:
                return 0.0
            correlation = merged['crypto_returns'].rolling(window=window).corr(merged['market_returns'])
            latest_corr = correlation.iloc[-1]
            return latest_corr if not np.isnan(latest_corr) else 0.0
        except Exception as e:
            print(f"⚠️ Correlation error for {crypto_df} and {market_df}: {e}")
            return 0.0

    def calculate_market_change(self, df: pd.DataFrame) -> float:
        if df is None or len(df) < 2:
            return 0.0
        first_price = df['close'].iloc[0]
        last_price = df['close'].iloc[-1]
        return ((last_price / first_price) - 1) * 100

    def analyze_all_markets(self, crypto_symbol: str = 'BTCUSDT', days: int = 30) -> Dict[str, Any]:
        print(f"\n{'='*80}")
        print(f"🌍 Traditional Markets Analysis v3.2")
        print(f"{'='*80}\n")

        crypto_df = self.fetch_crypto_data(crypto_symbol, days)
        if crypto_df is None:
            return self._error_response("Failed to fetch crypto data")

        crypto_change = self.calculate_market_change(crypto_df)

        market_data = {}
        correlations = {}
        changes = {}

        for name, symbol in self.symbols.items():
            print(f"  📊 Fetching {name} ({symbol})...")
            df = self.fetch_market_data(symbol, days)
            market_data[name] = df

            if df is not None:
                corr = self.calculate_correlation(crypto_df, df)
                correlations[name] = corr
                change = self.calculate_market_change(df)
                changes[name] = change
                print(f"     ✅ {name}: Corr={corr:.3f}, Change={change:+.2f}%")
            else:
                correlations[name] = 0.0
                changes[name] = 0.0
                print(f"     ⚠️ {name}: Data not available")

        factor_scores = {}
        spx_corr = correlations.get('SPX', 0)
        factor_scores['SPX'] = (spx_corr + 1) * 50
        nasdaq_corr = correlations.get('NASDAQ', 0)
        factor_scores['NASDAQ'] = (nasdaq_corr + 1) * 50
        dow_corr = correlations.get('DJI', 0)
        factor_scores['DJI'] = (dow_corr + 1) * 50
        dxy_corr = correlations.get('DXY', 0)
        factor_scores['DXY'] = (-dxy_corr + 1) * 50

        total_score = 0
        for factor, score in factor_scores.items():
            weight = self.weights.get(factor, 0)
            total_score += (score * weight / 100)
        total_score = max(0, min(100, total_score))

        spx_change = changes.get('SPX', 0)
        nasdaq_change = changes.get('NASDAQ', 0)
        dxy_change = changes.get('DXY', 0)

        if spx_change > 3 and nasdaq_change > 3 and dxy_change < -1:
            market_regime = "STRONG_RISK_ON"
            regime_interpretation = "Strong risk-on - Very bullish for crypto"
        elif spx_change > 1 and nasdaq_change > 1:
            market_regime = "RISK_ON"
            regime_interpretation = "Risk-on sentiment - Bullish for crypto"
        elif spx_change < -3 and nasdaq_change < -3:
            market_regime = "RISK_OFF"
            regime_interpretation = "Risk-off - Bearish for crypto"
        elif spx_change < -1 or nasdaq_change < -1:
            market_regime = "CAUTIOUS"
            regime_interpretation = "Cautious sentiment - Neutral to bearish"
        else:
            market_regime = "NEUTRAL"
            regime_interpretation = "Balanced conditions"

        if total_score >= 70:
            signal = "VERY_BULLISH"
            explanation = "Strong positive correlation - Markets leading crypto higher"
        elif total_score >= 55:
            signal = "BULLISH"
            explanation = "Positive environment - Favorable for crypto"
        elif total_score >= 45:
            signal = "NEUTRAL"
            explanation = "Mixed signals from traditional markets"
        elif total_score >= 30:
            signal = "BEARISH"
            explanation = "Negative environment - Headwinds for crypto"
        else:
            signal = "VERY_BEARISH"
            explanation = "Strong risk-off - Markets pressuring crypto"

        result = {
            'available': True,
            'total_score': round(total_score, 2),
            'signal': signal,
            'explanation': explanation,
            'market_regime': market_regime,
            'regime_interpretation': regime_interpretation,
            'correlations': {k: round(v, 3) for k,v in correlations.items()},
            'factor_scores': {k: round(v, 2) for k,v in factor_scores.items()},
            'price_changes': {
                'crypto': round(crypto_change, 2),
                'SPX': round(changes.get('SPX',0),2),
                'NASDAQ': round(changes.get('NASDAQ',0),2),
                'DJI': round(changes.get('DJI',0),2),
                'DXY': round(changes.get('DXY',0),2)
            },
            'avg_correlation': round(np.mean([v for v in correlations.values() if v != 0]),3),
            'strongest_correlation': max(correlations.items(), key=lambda x: abs(x[1])) if correlations else ('N/A',0),
            'timestamp': datetime.now().isoformat(),
            'crypto_symbol': crypto_symbol,
            'analysis_period_days': days
        }
        print(f"\n{'='*80}")
        print(f"✅ Traditional Markets Analysis Complete!")
        print(f"  Total Score: {result['total_score']}/100")
        print(f"  Signal: {result['signal']}")
        print(f"  Market Regime: {result['market_regime']}")
        print(f"{'='*80}\n")

        return result

    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        return {
            'available': False,
            'total_score': 50,
            'signal': 'NEUTRAL',
            'explanation': error_msg,
            'correlations': {},
            'factor_scores': {},
            'price_changes': {},
            'timestamp': datetime.now().isoformat(),
            'error': True
        }

def get_traditional_markets_signal() -> Dict[str, Any]:
    try:
        layer = TraditionalMarketsLayer()
        result = layer.analyze_all_markets('BTCUSDT', days=30)
        return {
            'available': result['available'],
            'score': result.get('total_score',50),
            'signal': result.get('signal','NEUTRAL')
        }
    except Exception as e:
        print(f"⚠️ Traditional Markets Layer Error: {e}")
        return {'available': True, 'score': 50, 'signal': 'NEUTRAL'}

def calculate_traditional_correlation(symbol: str = 'BTCUSDT', days: int = 30) -> Dict[str, Any]:
    layer = TraditionalMarketsLayer()
    return layer.analyze_all_markets(symbol, days)

if __name__ == "__main__":
    print("Testing traditional_markets_layer.py")
    layer = TraditionalMarketsLayer()
    result = layer.analyze_all_markets('BTCUSDT', days=30)
    print(result)
