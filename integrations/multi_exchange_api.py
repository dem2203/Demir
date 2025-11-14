# multi_exchange_api.py - Multi-Exchange Real Data Integration
# DEMIR AI v5.0 - Enterprise Grade
# Binance + Bybit + Coinbase with automatic failover

import requests
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
import json
import asyncio

logger = logging.getLogger(__name__)

class BinanceExchange:
    """Real Binance REST API"""
    
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY', '')
        self.api_secret = os.getenv('BINANCE_API_SECRET', '')
        self.base_url = "https://api.binance.com/api/v3"
    
    def get_ticker(self, symbol):
        """Get REAL Binance ticker"""
        try:
            url = f"{self.base_url}/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Binance {symbol}: ${data['price']}")
                return {
                    'exchange': 'binance',
                    'symbol': symbol,
                    'price': float(data['price']),
                    'timestamp': datetime.now()
                }
            
            logger.error(f"Binance error: {response.status_code}")
            return None
        
        except Exception as e:
            logger.error(f"Binance fetch error: {e}")
            return None
    
    def get_24h_stats(self, symbol):
        """Get REAL 24h stats from Binance"""
        try:
            url = f"{self.base_url}/ticker/24hr?symbol={symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'exchange': 'binance',
                    'high': float(data['highPrice']),
                    'low': float(data['lowPrice']),
                    'volume': float(data['volume']),
                    'change_percent': float(data['priceChangePercent'])
                }
            
            return None
        except Exception as e:
            logger.error(f"24h stats error: {e}")
            return None

class BybitExchange:
    """Real Bybit REST API - Backup/Failover"""
    
    def __init__(self):
        self.api_key = os.getenv('BYBIT_API_KEY', '')
        self.api_secret = os.getenv('BYBIT_API_SECRET', '')
        self.base_url = "https://api.bybit.com/v5/market"
    
    def get_ticker(self, symbol):
        """Get REAL Bybit ticker"""
        try:
            # Convert symbol format (BTCUSDT -> BTCUSDT)
            url = f"{self.base_url}/tickers?category=spot&symbol={symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['result']['list']:
                    ticker = data['result']['list'][0]
                    logger.info(f"✅ Bybit {symbol}: ${ticker['lastPrice']}")
                    return {
                        'exchange': 'bybit',
                        'symbol': symbol,
                        'price': float(ticker['lastPrice']),
                        'timestamp': datetime.now()
                    }
            
            return None
        except Exception as e:
            logger.error(f"Bybit fetch error: {e}")
            return None

class CoinbaseExchange:
    """Real Coinbase REST API"""
    
    def __init__(self):
        self.api_key = os.getenv('COINBASE_API_KEY', '')
        self.api_secret = os.getenv('COINBASE_API_SECRET', '')
        self.base_url = "https://api.coinbase.com/v2"
    
    def get_ticker(self, symbol):
        """Get REAL Coinbase ticker"""
        try:
            # Convert symbol (BTCUSDT -> BTC-USD)
            cb_symbol = symbol.replace('USDT', '-USD')
            url = f"{self.base_url}/exchange-rates?currencies={cb_symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                usd_rate = float(data['rates']['USD'])
                logger.info(f"✅ Coinbase {cb_symbol}: ${1/usd_rate if usd_rate > 0 else 0}")
                return {
                    'exchange': 'coinbase',
                    'symbol': symbol,
                    'price': 1/usd_rate if usd_rate > 0 else 0,
                    'timestamp': datetime.now()
                }
            
            return None
        except Exception as e:
            logger.error(f"Coinbase fetch error: {e}")
            return None

class MultiExchangeAggregator:
    """Aggregate prices from all exchanges with fallback logic"""
    
    def __init__(self):
        self.binance = BinanceExchange()
        self.bybit = BybitExchange()
        self.coinbase = CoinbaseExchange()
        self.price_history = {}
    
    def get_best_price(self, symbol):
        """
        Get BEST price from all exchanges
        REAL data comparison - not mock
        """
        try:
            prices = {}
            
            # Try Binance (primary)
            binance_data = self.binance.get_ticker(symbol)
            if binance_data:
                prices['binance'] = binance_data['price']
            
            # Try Bybit (backup)
            bybit_data = self.bybit.get_ticker(symbol)
            if bybit_data:
                prices['bybit'] = bybit_data['price']
            
            # Try Coinbase (secondary)
            coinbase_data = self.coinbase.get_ticker(symbol)
            if coinbase_data:
                prices['coinbase'] = coinbase_data['price']
            
            if not prices:
                logger.error(f"No price data available for {symbol}")
                return None
            
            # Calculate best price
            best_price = max(prices.values()) if prices else None
            best_exchange = max(prices, key=prices.get) if prices else None
            
            logger.info(f"✅ Best price for {symbol}: ${best_price} (from {best_exchange})")
            logger.info(f"   Prices: {prices}")
            
            return {
                'symbol': symbol,
                'price': best_price,
                'best_exchange': best_exchange,
                'all_prices': prices,
                'timestamp': datetime.now()
            }
        
        except Exception as e:
            logger.error(f"Price aggregation error: {e}")
            return None
    
    def compare_spreads(self, symbol):
        """Compare spreads between exchanges"""
        try:
            best = self.get_best_price(symbol)
            
            if not best:
                return None
            
            spreads = {}
            for exchange, price in best['all_prices'].items():
                spread = ((best['price'] - price) / best['price'] * 100)
                spreads[exchange] = {
                    'price': price,
                    'spread_percent': spread
                }
            
            logger.info(f"Spreads for {symbol}: {spreads}")
            return spreads
        
        except Exception as e:
            logger.error(f"Spread calculation error: {e}")
            return None
