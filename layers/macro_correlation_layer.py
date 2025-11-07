import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import yfinance as yf

class MacroCorrelationLayer:
    def __init__(self):
        self.alpha_vantage_api_key = os.getenv('ALPHAVANTAGEAPIKEY')
        self.twelve_data_api_key = os.getenv('TWELVEDATAAPIKEY')
        self.cmc_api_key = os.getenv('CMCAPIKEY')

    def get_data_alpha_vantage(self, symbol):
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "apikey": self.alpha_vantage_api_key,
            "outputsize": "compact"
        }
        try:
            res = requests.get(url, params=params, timeout=15)
            res.raise_for_status()
            js = res.json()
            time_series = js.get("Time Series (Daily)")
            if not time_series:
                return None, "No data from Alpha Vantage"
            df = pd.DataFrame.from_dict(time_series, orient='index').astype(float)
            return df, None
        except Exception as e:
            return None, str(e)

    def get_data_twelve_data(self, symbol):
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&apikey={self.twelve_data_api_key}"
        try:
            res = requests.get(url, timeout=15)
            res.raise_for_status()
            data = res.json()
            if 'values' not in data:
                return None, "No data from Twelve Data"
            df = pd.DataFrame(data['values'])
            for col in df.columns:
                try: df[col] = df[col].astype(float)
                except: pass
            return df, None
        except Exception as e:
            return None, str(e)

    def get_data_yfinance(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="60d")
            if df.empty:
                return None, "No data from Yahoo Finance"
            return df, None
        except Exception as e:
            return None, str(e)

    def getmacrosignal(self, symbol="SPY"):
        df, err = self.get_data_alpha_vantage(symbol)
        source = "AlphaVantage"
        if df is None:
            df, err = self.get_data_twelve_data(symbol)
            source = "TwelveData"
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
            close_col = next((col for col in ['4. close', 'close', 'Close'] if col in df.columns), None)
            if close_col is None:
                raise ValueError("No close column found")
            df['returns'] = df[close_col].pct_change()
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

    def analyze_all(self, symbol="BTCUSDT", days=30):
        result = {
            "available": False,
            "totalscore": 50.0,
            "signal": "NEUTRAL",
            "details": [],
            "error": ""
        }
        try:
            macro_assets = ["SPY", "QQQ", "GLD", "DXY", "VIX"]
            scores = []
            for asset in macro_assets:
                res = self.getmacrosignal(symbol=asset)
                result["details"].append({asset: res})
                if res["available"]:
                    scores.append(res["score"])
            # Weighted sum veya ortalama skor
            if scores:
                avg_score = np.mean(scores)
                result["totalscore"] = avg_score
                result["signal"] = "BULLISH" if avg_score > 55 else "BEARISH" if avg_score < 45 else "NEUTRAL"
                result["available"] = True
            else:
                result["error"] = "No macro scores available"
        except Exception as e:
            result["error"] = f"analyze_all exception: {str(e)}"
        return result
