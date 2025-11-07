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

    def _get_alpha_vantage_data(self, symbol):
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
            json_data = res.json()
            time_series = json_data.get("Time Series (Daily)")
            if not time_series:
                return None, "No data from Alpha Vantage"
            df = pd.DataFrame.from_dict(time_series, orient='index')
            # alpha vantageda veriler string, float yapalım
            df = df.astype(float)
            return df, None
        except Exception as e:
            return None, str(e)

    def _get_twelve_data(self, symbol):
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&apikey={self.twelve_data_api_key}"
        try:
            res = requests.get(url, timeout=15)
            res.raise_for_status()
            data = res.json()
            if 'values' not in data:
                return None, "No data from Twelve Data"
            df = pd.DataFrame(data['values'])
            # floatize columns
            for col in df.columns:
                try:
                    df[col] = df[col].astype(float)
                except:
                    pass
            return df, None
        except Exception as e:
            return None, str(e)

    def _get_yfinance_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="60d")
            if df.empty:
                return None, "No data from Yahoo Finance"
            return df, None
        except Exception as e:
            return None, str(e)

    def get_macrosignal(self, symbol="SPY"):
        df, error = self._get_alpha_vantage_data(symbol)
        source = "Alpha Vantage"
        if df is None:
            df, error = self._get_twelve_data(symbol)
            source = "Twelve Data"
        if df is None:
            df, error = self._get_yfinance_data(symbol)
            source = "Yahoo Finance"
        if df is None:
            return {
                "available": False,
                "score": 50.0,
                "signal": "NEUTRAL",
                "error": f"Failed to get data from all sources: {error}",
                "source": None
            }
        try:
            close_col = None
            for col in ['4. close', 'close', 'Close']:
                if col in df.columns:
                    close_col = col
                    break
            if close_col is None:
                raise ValueError("Close price column not found")
            df['returns'] = df[close_col].pct_change()
            recent_return = df['returns'].iloc[-1]
            score = np.clip((recent_return + 0.05) * 100, 0, 100)
            if score > 55:
                signal = "BULLISH"
            elif score < 45:
                signal = "BEARISH"
            else:
                signal = "NEUTRAL"
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
