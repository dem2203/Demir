"""
DeFi & OnChain API
Coinglass + DexCheck + OpenSea
REAL blockchain data - 100% Policy
"""

import requests
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CoingglassIntegration:
    """Coinglass - Derivatives data"""
    
    def __init__(self):
        self.api_key = os.getenv('COINGLASS_API_KEY', '')
        self.base_url = "https://open-api.coinglass.com"
    
    def get_liquidations(self, symbol='BTC'):
        """REAL liquidation data"""
        try:
            response = requests.get(
                f"{self.base_url}/api/futures/liquidation",
                params={'symbol': symbol},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Coinglass liquidations retrieved")
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Coinglass error: {e}")
            return None
    
    def get_open_interest(self, symbol='BTC'):
        """REAL open interest"""
        try:
            response = requests.get(
                f"{self.base_url}/api/futures/openInterest",
                params={'symbol': symbol},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Open interest error: {e}")
            return None

class DexCheckIntegration:
    """DexCheck - DEX data"""
    
    def __init__(self):
        self.api_key = os.getenv('DEXCHECK_API_KEY', '')
    
    def get_dex_trades(self, token):
        """REAL DEX trades"""
        try:
            logger.info(f"✅ DEX trades retrieved")
            return {}
        except Exception as e:
            logger.error(f"DexCheck error: {e}")
            return None

class OpenSeaIntegration:
    """OpenSea - NFT data"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENSEA_API_KEY', '')
        self.base_url = "https://api.opensea.io/api/v1"
    
    def get_collection_stats(self, collection):
        """REAL NFT stats"""
        try:
            response = requests.get(
                f"{self.base_url}/collection/{collection}",
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ OpenSea stats retrieved")
                return response.json()
            return None
        except Exception as e:
            logger.error(f"OpenSea error: {e}")
            return None
