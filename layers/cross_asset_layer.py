import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import yfinance as yf

class CrossAssetLayer:
    def __init__(self):
        self.alpha_vantage_api_key = os.getenv('ALPHAVANTAGEAPIKEY')
        self.twelve_data_api_key = os.getenv('TWELVEDATAAPIKEY')

    def get_data_yfinance(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="60d")
            if df.empty:
                return None, "No data from Yahoo Finance"
            return df, None
        except Exception as e:
            return None, str(e)

    def get_data_binance(self, symbol, interval="1h", limit=100):
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            closes = [float(c[4]) for c in data]
            df = pd.DataFrame(closes, columns=["Close"])
            return df, None
        except Exception as e:
            return None, str(e)

    def cross_asset_signal(self, symbol="BTCUSDT"):
        df, err = self.get_data_binance(symbol)
        source = "Binance"
        if df is None:
            df, err = self.get_data_yfinance(symbol)
            source = "YahooFinance"
        if df is None:
            return {
                "available": False,
                "score": 50.0,
                "signal": "NEUTRAL",
                "error": f"Data fetch failed: {err}",
                "source": None,
            }
        try:
            df['returns'] = df['Close'].pct_change()
            recent_return = df['returns'].iloc[-1]
            score = np.clip((recent_return + 0.05) * 100, 0, 100)
            signal = "BULLISH" if score > 55 else "BEARISH" if score < 45 else "NEUTRAL"
        except Exception as e:
            return {
                "available": False,
                "score": 50.0,
                "signal": "NEUTRAL",
                "error": str(e),
                "source": source,
            }
        return {
            "available": True,
            "score": float(score),
            "signal": signal,
            "error": None,
            "source": source,
        }

    def analyze_all(self, symbol="BTCUSDT", assets=None, days=30):
        if not assets:
            assets = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SPY", "QQQ"]
        result = {
            "available": False,
            "totalscore": 50.0,
            "signal": "NEUTRAL",
            "details": [],
            "error": ""
        }
        try:
            scores = []
            for asset in assets:
                res = self.cross_asset_signal(symbol=asset)
                result["details"].append({asset: res})
                if res["available"]:
                    scores.append(res["score"])
            if scores:
                avg_score = np.mean(scores)
                result["totalscore"] = avg_score
                result["signal"] = "BULLISH" if avg_score > 55 else "BEARISH" if avg_score < 45 else "NEUTRAL"
                result["available"] = True
            else:
                result["error"] = "No cross-asset signals available"
        except Exception as e:
            result["error"] = f"analyze_all exception: {str(e)}"
        return result
