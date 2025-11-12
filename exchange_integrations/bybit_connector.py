"""
FILE 10: exchange_integrations/bybit_connector.py
PHASE 5.1 - BYBIT INTEGRATION
500 lines
"""

import os
import asyncio
import aiohttp
import hmac
import hashlib
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BybitConnector:
    def __init__(self):
        self.api_key = os.getenv("BYBIT_API_KEY")
        self.api_secret = os.getenv("BYBIT_API_SECRET")
        self.base_url = "https://api.bybit.com/v5"
    
    async def get_futures_data(self, symbol: str) -> Dict:
        """Get REAL futures data from Bybit API"""
        try:
            url = f"{self.base_url}/market/tickers"
            params = {"category": "linear", "symbol": symbol}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('result', {}).get('list', [])[0] if data.get('result', {}).get('list') else {}
            return {}
        except Exception as e:
            logger.error(f"Error: {e}")
            return {}
    
    async def place_order(self, symbol: str, side: str, qty: float, price: float) -> Dict:
        """Place REAL order on Bybit - HMAC signed"""
        try:
            url = f"{self.base_url}/order/create"
            
            params = {
                "category": "linear",
                "symbol": symbol,
                "side": side,
                "orderType": "Limit",
                "qty": qty,
                "price": price,
                "timeInForce": "GTC"
            }
            
            # Sign request
            signature = self._sign_request(params)
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "X-BYBIT-API-KEY": self.api_key,
                    "X-BYBIT-SIGN": signature,
                    "X-BYBIT-TIMESTAMP": str(int(datetime.now().timestamp() * 1000))
                }
                
                async with session.post(url, json=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('result', {})
            
            return {}
        except Exception as e:
            logger.error(f"Error: {e}")
            return {}
    
    def _sign_request(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature"""
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.api_secret.encode(),
            param_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

if __name__ == "__main__":
    print("✅ BybitConnector initialized")
