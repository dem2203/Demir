import requests
import pandas as pd
import numpy as np
import os
import yfinance as yf

class InterestRatesLayer:

    def __init__(self):
        self.alpha_vantage_api_key = os.getenv('ALPHAVANTAGEAPIKEY')
        self.twelve_data_api_key = os.getenv('TWELVEDATAAPIKEY')

    def _fetch_alpha_vantage(self, symbol):
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TREASURY_YIELD",
            "interval": "daily",
            "apikey": self.alpha_vantage_api_key
        }
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            if 'data' not in data:
                return None, "No data from Alpha Vantage"
            df = pd.DataFrame(data['data'])
            # Convert yield fields to float
            for col in df.columns:
                try:
                    df[col] = df[col].astype(float)
                except Exception:
                    pass
            return df, None
        except Exception as e:
            return None, str(e)

    def _fetch_twelve_data(self, symbol):
        # Twelve Data does not provide interest rates, so skip or extend if you have another source
        return None, "Twelve Data does not support interest rates"

    def _fetch_yfinance(self, symbol='^IRX'):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="2mo")
            if df.empty:
                return None, "No data from Yahoo Finance"
            return df, None
        except Exception as e:
            return None, str(e)

    def get_interest_rates_signal(self):
        df, error = self._fetch_alpha_vantage('TNX')
        source = "Alpha Vantage"
        if df is None:
            # falling back to yfinance 10-year treasury rate proxy
            df, error = self._fetch_yfinance('^TNX')
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
            # Use latest yield as score proxy
            if '10 Yr' in df.columns:
                latest_value = df['10 Yr'].iloc[-1]
            elif 'Close' in df.columns:
                latest_value = df['Close'].iloc[-1]
            else:
                # fallback if specific column names not found
                latest_value = df.iloc[-1].iloc[0]

            # normalize score between 0-100
            score = np.clip(latest_value * 10, 0, 100)

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
