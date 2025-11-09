# FILE 3: micro_cap_scanner.py
# Lokasyon: intelligence_layers/micro_cap_scanner.py

import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class MicroCapOpportunitiesScanner:
    """Phase 19: Scan for micro-cap opportunities with safety filters"""
    
    def __init__(self):
        self.binance_client = None
        try:
            from binance.client import Client
            self.binance_client = Client(
                api_key=os.getenv("BINANCE_API_KEY", ""),
                api_secret=os.getenv("BINANCE_API_SECRET", "")
            )
        except:
            logger.warning("Binance client not available")
    
    async def scan_opportunities(self, market_cap_min: float = 1_000_000,
                                market_cap_max: float = 100_000_000) -> List[Dict]:
        """Scan for micro-cap coins with opportunity signals"""
        
        opportunities = []
        
        if not self.binance_client:
            logger.warning("Binance not available, returning empty opportunities")
            return []
        
        try:
            tickers = self.binance_client.get_all_tickers()
            
            for ticker in tickers:
                symbol = ticker["symbol"]
                price = float(ticker["price"])
                
                if not symbol.endswith("USDT"):
                    continue
                
                stats = self.binance_client.get_ticker(symbol=symbol)
                
                volume_24h = float(stats["quoteAssetVolume"])
                price_change_24h = float(stats["priceChangePercent"])
                
                if volume_24h < 10_000_000:
                    continue
                
                if -5 > price_change_24h > 20:
                    continue
                
                if price_change_24h > 5:
                    opportunities.append({
                        "symbol": symbol,
                        "price": price,
                        "volume_24h": volume_24h,
                        "price_change_24h": price_change_24h,
                        "signal": "BREAKOUT",
                        "confidence": 0.65,
                        "risk_level": "HIGH",
                    })
        
        except Exception as e:
            logger.error(f"Scanner error: {e}")
        
        return opportunities[:10]
