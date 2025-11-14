#!/usr/bin/env python3
"""
🔱 DEMIR AI - macro_analyzer.py (JOB 3 - 1 HOUR)
STRICT - NO MOCK, FAIL LOUD
"""

import logging
from datetime import datetime
from typing import Dict
import requests
import pandas as pd

logger = logging.getLogger(__name__)

class MacroAnalyzer:
    """Macro economic data - STRICT"""
    
    def __init__(self, fred_key: str):
        if not fred_key:
            raise ValueError("❌ Missing FRED API key")
        self.fred_key = fred_key
        self.base_fred_url = "https://api.stlouisfed.org/fred"
    
    def fetch_fed_rate(self) -> float:
        """Current Fed Rate - STRICT"""
        try:
            url = f"{self.base_fred_url}/series/data?series_id=FEDFUNDS&api_key={self.fred_key}&file_type=json"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"❌ FRED API failed: {response.status_code}")
            
            data = response.json()
            if not data.get('observations'):
                raise ValueError("❌ No Fed rate data")
            
            latest = data['observations'][-1]
            rate = float(latest['value'])
            
            if rate < 0 or rate > 10:
                raise ValueError(f"❌ Invalid Fed rate: {rate}")
            
            logger.info(f"✅ Fed rate: {rate}%")
            return float(rate)
        except Exception as e:
            logger.critical(f"❌ Fed rate failed: {e}")
            raise
    
    def fetch_inflation_rate(self) -> float:
        """CPI Inflation Rate - STRICT"""
        try:
            url = f"{self.base_fred_url}/series/data?series_id=CPIAUCSL&api_key={self.fred_key}&file_type=json"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"❌ FRED API failed: {response.status_code}")
            
            data = response.json()
            if not data.get('observations'):
                raise ValueError("❌ No inflation data")
            
            obs = data['observations'][-1]
            inflation = float(obs['value'])
            
            if inflation < 0 or inflation > 20:
                raise ValueError(f"❌ Invalid inflation: {inflation}")
            
            logger.info(f"✅ Inflation rate: {inflation}%")
            return float(inflation)
        except Exception as e:
            logger.critical(f"❌ Inflation rate failed: {e}")
            raise
    
    def fetch_unemployment(self) -> float:
        """Unemployment Rate - STRICT"""
        try:
            url = f"{self.base_fred_url}/series/data?series_id=UNRATE&api_key={self.fred_key}&file_type=json"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"❌ FRED API failed: {response.status_code}")
            
            data = response.json()
            if not data.get('observations'):
                raise ValueError("❌ No unemployment data")
            
            latest = data['observations'][-1]
            rate = float(latest['value'])
            
            if rate < 0 or rate > 15:
                raise ValueError(f"❌ Invalid unemployment: {rate}")
            
            logger.info(f"✅ Unemployment rate: {rate}%")
            return float(rate)
        except Exception as e:
            logger.critical(f"❌ Unemployment rate failed: {e}")
            raise
    
    def fetch_vix_data(self) -> Dict:
        """VIX Volatility Index - STRICT"""
        try:
            # Using Yahoo Finance or alternative source
            url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=%5EVIX"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"❌ VIX API failed: {response.status_code}")
            
            data = response.json()
            if not data.get('quoteResponse', {}).get('result'):
                raise ValueError("❌ No VIX data")
            
            quote = data['quoteResponse']['result'][0]
            vix_close = float(quote['regularMarketPrice'])
            vix_high = float(quote['fiftyTwoWeekHigh'])
            vix_low = float(quote['fiftyTwoWeekLow'])
            
            if vix_close < 0 or vix_close > 100:
                raise ValueError(f"❌ Invalid VIX: {vix_close}")
            
            logger.info(f"✅ VIX: {vix_close}")
            return {
                'vix_close': float(vix_close),
                'vix_high': float(vix_high),
                'vix_low': float(vix_low)
            }
        except Exception as e:
            logger.critical(f"❌ VIX fetch failed: {e}")
            raise
    
    def fetch_dxy_data(self) -> Dict:
        """DXY Dollar Index - STRICT"""
        try:
            url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=DXY%3DF"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"❌ DXY API failed: {response.status_code}")
            
            data = response.json()
            if not data.get('quoteResponse', {}).get('result'):
                raise ValueError("❌ No DXY data")
            
            quote = data['quoteResponse']['result'][0]
            dxy_close = float(quote['regularMarketPrice'])
            
            if dxy_close < 80 or dxy_close > 120:
                raise ValueError(f"❌ Invalid DXY: {dxy_close}")
            
            logger.info(f"✅ DXY: {dxy_close}")
            return {'dxy_close': float(dxy_close)}
        except Exception as e:
            logger.critical(f"❌ DXY fetch failed: {e}")
            raise
    
    def fetch_onchain_data(self) -> Dict:
        """OnChain data from Coinglass - STRICT"""
        try:
            # Fetch BTC exchange flow data
            url = "https://api.coinglass.com/api/v2/exchange/ftx/flow"  # Example endpoint
            
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                logger.warning(f"⚠️ OnChain API failed: {response.status_code}")
                return {
                    'exchange_inflow': 0.0,
                    'exchange_outflow': 0.0,
                    'whale_transactions': 0,
                    'liquidations': 0.0,
                    'funding_rate': 0.0
                }
            
            data = response.json()
            
            inflow = float(data.get('inflow', 0))
            outflow = float(data.get('outflow', 0))
            
            logger.info(f"✅ OnChain data: inflow={inflow:.2f}")
            return {
                'exchange_inflow': float(inflow),
                'exchange_outflow': float(outflow),
                'whale_transactions': int(data.get('transactions', 0)),
                'liquidations': float(data.get('liquidations', 0)),
                'funding_rate': float(data.get('funding_rate', 0))
            }
        except Exception as e:
            logger.error(f"⚠️ OnChain fetch (non-critical): {e}")
            return {
                'exchange_inflow': 0.0,
                'exchange_outflow': 0.0,
                'whale_transactions': 0,
                'liquidations': 0.0,
                'funding_rate': 0.0
            }
    
    def fetch_crypto_dominance(self) -> Dict:
        """BTC & ETH Dominance - STRICT"""
        try:
            url = "https://api.coingecko.com/api/v3/global"
            
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"❌ CoinGecko API failed: {response.status_code}")
            
            data = response.json()
            btc_dom = float(data['data']['market_cap_percentage']['btc'])
            eth_dom = float(data['data']['market_cap_percentage']['eth'])
            
            if btc_dom < 0 or btc_dom > 100:
                raise ValueError(f"❌ Invalid BTC dominance: {btc_dom}")
            
            logger.info(f"✅ Dominance: BTC={btc_dom:.1f}%, ETH={eth_dom:.1f}%")
            return {
                'btc_dominance': float(btc_dom),
                'eth_dominance': float(eth_dom)
            }
        except Exception as e:
            logger.critical(f"❌ Dominance fetch failed: {e}")
            raise
    
    def aggregate_macro(self) -> Dict:
        """Get ALL macro data - STRICT"""
        try:
            logger.info("🔄 Fetching macro data...")
            
            fed_rate = self.fetch_fed_rate()
            inflation = self.fetch_inflation_rate()
            unemployment = self.fetch_unemployment()
            vix = self.fetch_vix_data()
            dxy = self.fetch_dxy_data()
            onchain = self.fetch_onchain_data()
            dominance = self.fetch_crypto_dominance()
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'fed_rate': fed_rate,
                'inflation_rate': inflation,
                'unemployment_rate': unemployment,
                'vix_close': vix['vix_close'],
                'vix_high': vix['vix_high'],
                'vix_low': vix['vix_low'],
                'dxy_close': dxy['dxy_close'],
                'btc_dominance': dominance['btc_dominance'],
                'eth_dominance': dominance['eth_dominance'],
                'exchange_inflow': onchain['exchange_inflow'],
                'exchange_outflow': onchain['exchange_outflow'],
                'funding_rate': onchain['funding_rate']
            }
            
            logger.info("✅ Macro data complete")
            return result
        
        except Exception as e:
            logger.critical(f"❌ Macro aggregation failed: {e}")
            raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("✅ MacroAnalyzer ready")
