import requests
import streamlit as st
from datetime import datetime
import time
from config import (
    BINANCE_API_KEY, BINANCE_API_SECRET,
    COINGLASS_API_KEY, ALPHA_VANTAGE_API_KEY,
    FRED_API_KEY, NEWSAPI_KEY,
    BINANCE_BASE_URL, BINANCE_FUTURES_URL,
    COINGLASS_BASE_URL, ALPHA_VANTAGE_BASE_URL,
    FRED_BASE_URL, NEWSAPI_BASE_URL,
    CACHE_TTL, API_TIMEOUT_SECONDS
)


class APIManager:
    """Manages all API calls with caching and error handling"""
    
    def __init__(self):
        self.cache = {}
        self.last_update = {}
    
    def _is_cached(self, key):
        """Check if data is still fresh in cache"""
        if key not in self.cache:
            return False
        
        elapsed = time.time() - self.last_update.get(key, 0)
        return elapsed < CACHE_TTL
    
    def _get_cached(self, key):
        """Retrieve cached data"""
        if self._is_cached(key):
            return self.cache[key]
        return None
    
    def _set_cache(self, key, value):
        """Store data in cache"""
        self.cache[key] = value
        self.last_update[key] = time.time()
    
    @st.cache_data(ttl=60)
    def get_binance_price(self, symbol):
        """Get current BTC/ETH/LTC price from Binance"""
        try:
            cache_key = f"binance_price_{symbol}"
            
            # Check cache first
            cached = self._get_cached(cache_key)
            if cached:
                return cached
            
            url = f"{BINANCE_BASE_URL}/api/v3/ticker/price"
            params = {"symbol": f"{symbol}USDT"}
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT_SECONDS)
            response.raise_for_status()
            
            data = response.json()
            price = float(data['price'])
            
            # Cache result
            self._set_cache(cache_key, price)
            return price
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching {symbol} price: {str(e)}")
            return None
    
    def get_order_book(self, symbol, limit=20):
        """Get order book data from Binance"""
        try:
            url = f"{BINANCE_BASE_URL}/api/v3/depth"
            params = {"symbol": f"{symbol}USDT", "limit": limit}
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT_SECONDS)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching order book: {str(e)}")
            return None
    
    def get_futures_price(self, symbol):
        """Get futures price from Binance"""
        try:
            url = f"{BINANCE_FUTURES_URL}/fapi/v1/ticker/price"
            params = {"symbol": f"{symbol}USDT"}
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT_SECONDS)
            response.raise_for_status()
            
            data = response.json()
            price = float(data['price'])
            return price
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching futures price: {str(e)}")
            return None
    
    def get_24h_stats(self, symbol):
        """Get 24h high/low/volume from Binance"""
        try:
            url = f"{BINANCE_BASE_URL}/api/v3/ticker/24hr"
            params = {"symbol": f"{symbol}USDT"}
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT_SECONDS)
            response.raise_for_status()
            
            data = response.json()
            return {
                "high": float(data['highPrice']),
                "low": float(data['lowPrice']),
                "volume": float(data['volume']),
                "change_percent": float(data['priceChangePercent'])
            }
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching 24h stats: {str(e)}")
            return None
    
    def get_coinglass_data(self, symbol):
        """Get on-chain data from Coinglass"""
        try:
            if not COINGLASS_API_KEY:
                st.warning("Coinglass API key not configured")
                return None
            
            url = f"{COINGLASS_BASE_URL}/api/v2/whale_alert"
            headers = {"Authorization": f"Bearer {COINGLASS_API_KEY}"}
            params = {"symbol": symbol}
            
            response = requests.get(url, headers=headers, params=params, timeout=API_TIMEOUT_SECONDS)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            st.warning(f"Coinglass API error: {str(e)}")
            return None
    
    def get_alpha_vantage_data(self, symbol, interval="5min"):
        """Get technical indicators from Alpha Vantage"""
        try:
            if not ALPHA_VANTAGE_API_KEY:
                st.warning("Alpha Vantage API key not configured")
                return None
            
            url = ALPHA_VANTAGE_BASE_URL
            params = {
                "function": "FX_INTRADAY",
                "from_symbol": symbol[:3],
                "to_symbol": "USD",
                "interval": interval,
                "apikey": ALPHA_VANTAGE_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT_SECONDS)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            st.warning(f"Alpha Vantage API error: {str(e)}")
            return None
    
    def get_fred_data(self, series_id):
        """Get economic data from FRED"""
        try:
            if not FRED_API_KEY:
                st.warning("FRED API key not configured")
                return None
            
            url = f"{FRED_BASE_URL}/series/observations"
            params = {
                "series_id": series_id,
                "api_key": FRED_API_KEY,
                "file_type": "json"
            }
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT_SECONDS)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            st.warning(f"FRED API error: {str(e)}")
            return None
    
    def get_news_sentiment(self, query):
        """Get news sentiment data"""
        try:
            if not NEWSAPI_KEY:
                st.warning("NewsAPI key not configured")
                return None
            
            url = f"{NEWSAPI_BASE_URL}/v2/everything"
            params = {
                "q": query,
                "apiKey": NEWSAPI_KEY,
                "sortBy": "publishedAt",
                "language": "en"
            }
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT_SECONDS)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            st.warning(f"NewsAPI error: {str(e)}")
            return None
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        self.last_update.clear()
        st.success("Cache cleared!")


# Global API Manager instance
api_manager = APIManager()
