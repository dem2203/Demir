# --- Dosya başlığı, açıklama ve copyrights aynen korunmalı ---
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
        # Orijinaldeki ek parametre varsa eklenmeli

    # Orijinalde varsa, ek API veri çekme fonksiyonları burada olmalı
    def get_data_alpha_vantage(self, symbol):
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
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
            df = pd.DataFrame.from_dict(time_series, orient='index').astype(float)
            return df, None
        except Exception as e:
            return None, str(e)

    # Orijinalde diğer API'ler veya fallback fonksiyonları varsa eklenmeli
    def get_data_twelve_data(self, symbol):
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&apikey={self.twelve_data_api_key}"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            if 'values' not in data:
                return None, "No data from Twelve Data"
            df = pd.DataFrame(data['values'])
            for col in df.columns:
                try:
                    df[col] = df[col].astype(float)
                except:
                    pass
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

    # Orijinaldeki macro analiz fonksiyonu ve scoring algoritması
    def getmacrosignal(self, symbol="SPY"):
        df, error = self.get_data_alpha_vantage(symbol)
        source = "Alpha Vantage"
        if df is None:
            df, error = self.get_data_twelve_data(symbol)
            source = "Twelve Data"
        if df is None:
            df, error = self.get_data_yfinance(symbol)
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
            close_col = next((col for col in ['4. close', 'close', 'Close'] if col in df.columns), None)
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

    # Panelin ve workflow'un gerektirdiği toplu analiz fonksiyonu orijinal haliyle
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

# Dosya sonunda varsa eski ek fonksiyonlar/utility'ler aynen bırakılır, sadece zorunlu teknik güncellemeler yapılır.
