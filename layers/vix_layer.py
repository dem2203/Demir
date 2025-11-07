import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np

class VixLayer:
    def __init__(self):
        self.alpha_vantage_api_key = os.getenv('ALPHAVANTAGEAPIKEY')
        self.twelve_data_api_key = os.getenv('TWELVEDATAAPIKEY')

    def _fetch_alpha_vantage(self, symbol="VIX"):
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.alpha_vantage_api_key,
            "outputsize": "compact"
        }
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            time_series = data.get("Time Series (Daily)")
            if not time_series:
                return None, "No data from Alpha Vantage"
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df = df.astype(float)
            return df, None
        except Exception as e:
            return None, str(e)

    def _fetch_twelve_data(self, symbol="VIX"):
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&apikey={self.twelve_data_api_key}"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            if "values" not in data:
                return None, "No data from Twelve Data"
            df = pd.DataFrame(data["values"])
            for col in df.columns:
                try:
                    df[col] = df[col].astype(float)
                except:
                    continue
            return df, None
        except Exception as e:
            return None, str(e)

    def _fetch_yfinance(self, symbol="^VIX"):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="2mo")
            if df.empty:
                return None, "No data from Yahoo Finance"
            return df, None
        except Exception as e:
            return None, str(e)

    def get_vix_signal(self, symbol="VIX"):
        df, error = self._fetch_alpha_vantage(symbol)
        source = "Alpha Vantage"
        if df is None:
            df, error = self._fetch_twelve_data(symbol)
            source = "Twelve Data"
        if df is None:
            # Yahoo Finance VIX symbol is ^VIX
            df, error = self._fetch_yfinance("^VIX")
            source = "Yahoo Finance"
        if df is None:
            return {
                "available": False,
                "score": 50.0,
                "signal": "NEUTRAL",
                "error": f"Failed to fetch data from all sources: {error}",
                "source": None,
            }
        try:
            close_col = next(
                (col for col in ['4. close', 'close', 'Close'] if col in df.columns), None
            )
            if close_col is None:
                raise ValueError("No close column found in VIX data")
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
