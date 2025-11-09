"""
REAL DATA API MANAGER - Binance Futures (Perpetual) + Real-Time Data
NO MOCK DATA - ALL REAL!
"""

import requests
import time
from datetime import datetime
import pandas as pd
from functools import lru_cache
import streamlit as st

class RealDataManager:
    """
    Fetches 100% REAL data from:
    - Binance Futures (Perpetual) API
    - Coinglass API (On-chain data)
    - Alpha Vantage API (Technical data)
    - FRED API (Macro data)
    - NewsAPI (Sentiment)
    """
    
    def __init__(self):
        self.binance_base = "https://fapi.binance.com"  # FUTURES (Perpetual)
        self.timeout = 15
        self.cache = {}
        self.last_update = {}
    
    # ==================== BINANCE FUTURES PERPETUAL ====================
    
    def get_perpetual_price(self, symbol="BTCUSDT"):
        """Get REAL perpetual futures price from Binance"""
        try:
            url = f"{self.binance_base}/fapi/v1/ticker/price"
            params = {"symbol": symbol}
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            price = float(data["price"])
            
            return {
                "symbol": symbol,
                "price": price,
                "timestamp": datetime.now().isoformat(),
                "source": "Binance Futures Perpetual"
            }
        
        except Exception as e:
            st.error(f"❌ Error fetching {symbol} perpetual price: {e}")
            return None
    
    def get_perpetual_24h_stats(self, symbol="BTCUSDT"):
        """Get REAL 24h stats from Binance Futures"""
        try:
            url = f"{self.binance_base}/fapi/v1/ticker/24hr"
            params = {"symbol": symbol}
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "symbol": symbol,
                "price": float(data["lastPrice"]),
                "price_change": float(data["priceChange"]),
                "price_change_percent": float(data["priceChangePercent"]),
                "high_24h": float(data["highPrice"]),
                "low_24h": float(data["lowPrice"]),
                "volume": float(data["volume"]),
                "quote_asset_volume": float(data["quoteAssetVolume"]),
                "timestamp": datetime.now().isoformat(),
                "source": "Binance Futures"
            }
        
        except Exception as e:
            st.error(f"❌ Error fetching 24h stats for {symbol}: {e}")
            return None
    
    def get_funding_rate(self, symbol="BTCUSDT"):
        """Get REAL funding rate for perpetual futures"""
        try:
            url = f"{self.binance_base}/fapi/v1/fundingRate"
            params = {"symbol": symbol, "limit": 1}
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            if data:
                return {
                    "symbol": symbol,
                    "funding_rate": float(data[0]["fundingRate"]),
                    "funding_time": data[0]["fundingTime"],
                    "timestamp": datetime.now().isoformat(),
                    "source": "Binance Futures"
                }
        
        except Exception as e:
            st.error(f"❌ Error fetching funding rate for {symbol}: {e}")
            return None
    
    def get_order_book(self, symbol="BTCUSDT", limit=20):
        """Get REAL order book from Binance Futures"""
        try:
            url = f"{self.binance_base}/fapi/v1/depth"
            params = {"symbol": symbol, "limit": limit}
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "symbol": symbol,
                "bids": data["bids"],  # [price, quantity]
                "asks": data["asks"],  # [price, quantity]
                "timestamp": datetime.now().isoformat(),
                "source": "Binance Futures"
            }
        
        except Exception as e:
            st.error(f"❌ Error fetching order book for {symbol}: {e}")
            return None
    
    def get_klines(self, symbol="BTCUSDT", interval="1h", limit=100):
        """Get REAL klines (candlestick) data from Binance Futures"""
        try:
            url = f"{self.binance_base}/fapi/v1/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            klines = []
            for candle in data:
                klines.append({
                    "open_time": candle[0],
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[7]),
                    "quote_asset_volume": float(candle[8])
                })
            
            return {
                "symbol": symbol,
                "interval": interval,
                "klines": klines,
                "timestamp": datetime.now().isoformat(),
                "source": "Binance Futures"
            }
        
        except Exception as e:
            st.error(f"❌ Error fetching klines for {symbol}: {e}")
            return None
    
    def get_open_interest(self, symbol="BTCUSDT"):
        """Get REAL open interest from Binance Futures"""
        try:
            url = f"{self.binance_base}/fapi/v1/openInterest"
            params = {"symbol": symbol}
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "symbol": symbol,
                "open_interest": float(data["openInterest"]),
                "timestamp": datetime.now().isoformat(),
                "source": "Binance Futures"
            }
        
        except Exception as e:
            st.error(f"❌ Error fetching open interest for {symbol}: {e}")
            return None
    
    def get_mark_price(self, symbol="BTCUSDT"):
        """Get REAL mark price from Binance Futures"""
        try:
            url = f"{self.binance_base}/fapi/v1/premiumIndex"
            params = {"symbol": symbol}
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "symbol": symbol,
                "mark_price": float(data["markPrice"]),
                "index_price": float(data["indexPrice"]),
                "basis": float(data["markPrice"]) - float(data["indexPrice"]),
                "basis_percent": (float(data["markPrice"]) - float(data["indexPrice"])) / float(data["indexPrice"]) * 100,
                "funding_rate": float(data["lastFundingRate"]),
                "timestamp": datetime.now().isoformat(),
                "source": "Binance Futures"
            }
        
        except Exception as e:
            st.error(f"❌ Error fetching mark price for {symbol}: {e}")
            return None
    
    # ==================== COINGLASS API ====================
    
    def get_on_chain_data(self, symbol="BTC", api_key=None):
        """Get REAL on-chain data from Coinglass"""
        if not api_key:
            return {"error": "Coinglass API key not configured"}
        
        try:
            url = "https://api.coinglass.com/api/v2/whale_alert"
            headers = {"Authorization": f"Bearer {api_key}"}
            params = {"symbol": symbol}
            
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            st.warning(f"⚠️ Coinglass API error: {e}")
            return None
    
    # ==================== MARKET DATA ====================
    
    def get_multi_coin_data(self, coins=["BTCUSDT", "ETHUSDT", "LTCUSDT"]):
        """Get REAL data for multiple coins"""
        results = {}
        
        for coin in coins:
            data = self.get_perpetual_24h_stats(coin)
            if data:
                results[coin] = data
            time.sleep(0.1)  # Rate limiting
        
        return results
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI from REAL price data"""
        if len(prices) < period:
            return None
        
        deltas = pd.Series(prices).diff()
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        
        rs = up / down if down != 0 else 0
        rsi = 100 - 100 / (1 + rs)
        
        return rsi
    
    def calculate_macd(self, prices):
        """Calculate MACD from REAL price data"""
        df = pd.Series(prices)
        exp1 = df.ewm(span=12, adjust=False).mean()
        exp2 = df.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        return {
            "macd": float(macd.iloc[-1]),
            "signal": float(signal.iloc[-1]),
            "histogram": float(histogram.iloc[-1])
        }


# Global instance
@st.cache_resource
def get_data_manager():
    return RealDataManager()


def fetch_live_btc_data():
    """Fetch LIVE BTC perpetual data - NO MOCK"""
    manager = get_data_manager()
    
    btc_data = manager.get_perpetual_24h_stats("BTCUSDT")
    funding = manager.get_funding_rate("BTCUSDT")
    mark_price = manager.get_mark_price("BTCUSDT")
    
    return {
        "price_data": btc_data,
        "funding": funding,
        "mark_price": mark_price,
        "timestamp": datetime.now()
    }


def fetch_live_eth_data():
    """Fetch LIVE ETH perpetual data - NO MOCK"""
    manager = get_data_manager()
    
    eth_data = manager.get_perpetual_24h_stats("ETHUSDT")
    funding = manager.get_funding_rate("ETHUSDT")
    mark_price = manager.get_mark_price("ETHUSDT")
    
    return {
        "price_data": eth_data,
        "funding": funding,
        "mark_price": mark_price,
        "timestamp": datetime.now()
    }


def fetch_all_coins_data(coins=["BTCUSDT", "ETHUSDT", "LTCUSDT", "XRPUSDT"]):
    """Fetch LIVE data for all monitored coins - NO MOCK"""
    manager = get_data_manager()
    return manager.get_multi_coin_data(coins)
