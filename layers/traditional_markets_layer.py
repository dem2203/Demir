import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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
        print("✅ Traditional Markets Layer initialized")

    def fetch_market_data(self, symbol, days=30):
        debug = {}
        try:
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            hist = ticker.history(start=start_date, end=end_date)
            if hist.empty:
                debug['error'] = f"Empty history for {symbol}"
                return None, debug
            df = pd.DataFrame({
                'timestamp': hist.index.astype(int)//10**9,
                'close': hist['Close'].values,
                'volume': hist['Volume'].values
            })
            debug['info'] = f"Fetched {len(df)} rows for {symbol}"
            return df, debug
        except Exception as e:
            debug['exception'] = str(e)
            return None, debug

    def fetch_crypto_data(self, symbol='BTCUSDT', days=30):
        debug = {}
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {'symbol': symbol, 'interval': '1d', 'limit': days}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                debug['http_error'] = f"HTTP {response.status_code}"
                return None, debug
            data = response.json()
            df = pd.DataFrame({
                'timestamp': [int(candle[0]/1000) for candle in data],
                'close': [float(candle[4]) for candle in data],
                'volume': [float(candle[5]) for candle in data]
            })
            debug['info'] = f"Fetched {len(df)} crypto candles"
            return df, debug
        except Exception as e:
            debug['exception'] = str(e)
            return None, debug

    def calculate_correlation(self, crypto_df, market_df, window=14):
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
            print(f"⚠️ Correlation error: {e}")
            return 0.0

    def calculate_market_change(self, df):
        if df is None or len(df) < 2:
            return 0.0
        return ((df['close'].iloc[-1] / df['close'].iloc[0]) -1) * 100

    def analyze_all_markets(self, crypto_symbol='BTCUSDT', days=30):
        print(f"\n{'='*60}\n🌍 Traditional Markets Analysis\n{'='*60}\n")

        crypto_df, crypto_debug = self.fetch_crypto_data(crypto_symbol, days)
        if crypto_df is None:
            return {
                'available': False,
                'error_message': 'Failed to fetch crypto data',
                'data_debug': crypto_debug
            }

        crypto_change = self.calculate_market_change(crypto_df)

        correlations = {}
        changes = {}
        debug_layers = {}

        for name, symbol in self.symbols.items():
            df, debug = self.fetch_market_data(symbol, days)
            debug_layers[name] = debug

            if df is not None:
                corr = self.calculate_correlation(crypto_df, df)
                change = self.calculate_market_change(df)
                correlations[name] = corr
                changes[name] = change
                print(f"{name}: Corr={corr:.3f}, Change={change:+.2f}%")
            else:
                correlations[name] = 0.0
                changes[name] = 0.0
                print(f"{name}: Data not available")

        factor_scores = {}
        spx_corr = correlations.get('SPX', 0)
        nasdaq_corr = correlations.get('NASDAQ', 0)
        dow_corr = correlations.get('DJI', 0)
        dxy_corr = correlations.get('DXY', 0)

        factor_scores['SPX'] = (spx_corr + 1) * 50
        factor_scores['NASDAQ'] = (nasdaq_corr + 1) * 50
        factor_scores['DJI'] = (dow_corr + 1) * 50
        factor_scores['DXY'] = (-dxy_corr + 1) * 50

        total_score = sum(factor_scores.get(f,0) * self.weights.get(f,0) / 100 for f in factor_scores)
        total_score = max(0, min(100, total_score))

        spx_change = changes.get('SPX',0)
        nasdaq_change = changes.get('NASDAQ',0)
        dxy_change = changes.get('DXY',0)

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

        return {
            'available': True,
            'total_score': round(total_score,2),
            'signal': signal,
            'explanation': explanation,
            'market_regime': market_regime,
            'regime_interpretation': regime_interpretation,
            'correlations': {k: round(v,3) for k,v in correlations.items()},
            'factor_scores': {k: round(v,2) for k,v in factor_scores.items()},
            'price_changes': {k: round(v,2) for k,v in changes.items()},
            'crypto_change': round(crypto_change, 2),
            'debug_layers': debug_layers,
            'timestamp': datetime.now().isoformat(),
            'crypto_symbol': crypto_symbol,
            'analysis_period_days': days
        }

def get_traditional_markets_signal():
    layer = TraditionalMarketsLayer()
    return layer.analyze_all_markets()

def calculate_traditional_correlation(symbol='BTCUSDT', days=30):
    layer = TraditionalMarketsLayer()
    return layer.analyze_all_markets(symbol, days)

if __name__ == "__main__":
    layer = TraditionalMarketsLayer()
    res = layer.analyze_all_markets()
    print(res)
