# FILE 2: whale_tracker.py
# Lokasyon: intelligence_layers/whale_tracker.py

import os
import asyncio
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class WhaleWalletTracker:
    """Phase 18: Track whale wallet movements"""
    
    def __init__(self):
        self.alchemy_key = os.getenv("ALCHEMY_API_KEY", "")
        
        try:
            from alchemy_sdk import Alchemy, Network
            self.alchemy = Alchemy(
                api_key=self.alchemy_key,
                network=Network.ETH_MAINNET
            )
            self.has_alchemy = True
        except ImportError:
            logger.warning("Alchemy SDK not installed.")
            self.has_alchemy = False
        
        self.whale_wallets = {
            "whale_1": "0x2fbed0ced83bb3c1fa15c22f037ba89d7357cabe",
            "whale_2": "0xbe0eb53f46cd790cd13851d5eff43d12404d33e8",
            "whale_3": "0x1db3439a222c519ab44bb1144ce329b5d6f51581",
        }
        
        self.transfer_history = {}
    
    async def track_whale_movements(self) -> Dict:
        """Track recent whale movements"""
        if not self.has_alchemy:
            logger.warning("Alchemy not available, using mock data")
            return await self.mock_whale_data()
        
        try:
            movements = {}
            
            for whale_name, wallet in self.whale_wallets.items():
                try:
                    transfers = await self.alchemy.core.get_asset_transfers(
                        from_address=wallet,
                        category=["external", "internal"],
                        max_count=5
                    )
                    
                    large_transfers = []
                    for transfer in transfers.get("transfers", []):
                        if float(transfer.get("value", 0)) > 1:
                            large_transfers.append({
                                "value": transfer["value"],
                                "to": transfer.get("to", "unknown"),
                                "timestamp": transfer.get("blockNum", "N/A"),
                            })
                    
                    movements[whale_name] = large_transfers
                
                except Exception as e:
                    logger.error(f"Error tracking {whale_name}: {e}")
            
            return movements
        
        except Exception as e:
            logger.error(f"Whale tracking error: {e}")
            return {}
    
    async def mock_whale_data(self) -> Dict:
        """Mock data for testing without Alchemy"""
        import random
        
        return {
            "whale_1": [
                {"value": random.uniform(1, 50), "to": "exchange", "timestamp": "recent"}
            ],
            "whale_2": [
                {"value": random.uniform(1, 50), "to": "personal_wallet", "timestamp": "recent"}
            ],
        }
    
    def calculate_whale_score(self, movements: Dict) -> float:
        """Calculate whale sentiment score (0=selling, 1=buying)"""
        if not movements:
            return 0.5
        
        buying_signals = 0
        selling_signals = 0
        
        for whale_name, transfers in movements.items():
            for transfer in transfers:
                if "exchange" in str(transfer.get("to", "")).lower():
                    selling_signals += 1
                else:
                    buying_signals += 1
        
        total = buying_signals + selling_signals
        if total == 0:
            return 0.5
        
        whale_score = buying_signals / total
        return whale_score
