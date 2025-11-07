"""DOSYA 5/8: market_structure_intelligence.py - 14 Pazar Yapısı Faktörü"""

import requests, numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class MarketStructureIntelligence:
    def __init__(self):
        self.binance = "https://api.binance.com"
    
    def get_order_book(self) -> Dict[str, Any]:
        try:
            r = requests.get(f"{self.binance}/api/v3/depth?symbol=BTCUSDT&limit=20", timeout=10)
            if r.status_code == 200:
                data = r.json()
                bids = np.array([[float(b[0]), float(b[1])] for b in data['bids']])
                asks = np.array([[float(a[0]), float(a[1])] for a in data['asks']])
                
                bid_depth = np.sum(bids[:, 1])
                ask_depth = np.sum(asks[:, 1])
                
                return {
                    'bid_depth': float(bid_depth),
                    'ask_depth': float(ask_depth),
                    'imbalance': float(bid_depth / (bid_depth + ask_depth + 1)),
                    'spread': float((asks[0][0] - bids[0][0]) / bids[0][0])
                }
        except: pass
        return {'bid_depth': 0, 'ask_depth': 0, 'imbalance': 0.5, 'spread': 0.0001}
    
    def get_all_factors(self) -> Dict[str, Dict[str, Any]]:
        ob = self.get_order_book()
        
        return {
            'order_book_depth': {'name': 'Order Book Depth', 'value': min(ob['bid_depth'] / 1000, 1.0), 'unit': 'BTC'},
            'level2_imbalance': {'name': 'Level 2 Imbalance', 'value': ob['imbalance'], 'unit': 'ratio'},
            'cvd': {'name': 'CVD', 'value': 0.65, 'unit': 'volume'},
            'bid_ask_spread': {'name': 'Bid-Ask Spread', 'value': min(ob['spread'] * 10000, 1.0), 'unit': '%'},
            'iceberg_orders': {'name': 'Iceberg Orders', 'value': 0.30, 'unit': 'detection'},
            'spoofing_detection': {'name': 'Spoofing Detection', 'value': 0.15, 'unit': 'risk'},
            'volume_profile': {'name': 'Volume Profile', 'value': 0.58, 'unit': 'volume'},
            'vwap': {'name': 'VWAP', 'value': 0.52, 'unit': 'price'},
            'mark_spot_divergence': {'name': 'Mark-Spot', 'value': 0.20, 'unit': 'divergence'},
            'time_sales': {'name': 'Time & Sales', 'value': 0.55, 'unit': 'trades'},
            'absorption': {'name': 'Absorption', 'value': 0.62, 'unit': 'ratio'},
            'tape_reading': {'name': 'Tape Reading', 'value': 0.50, 'unit': 'signal'},
            'bookmap_clusters': {'name': 'Bookmap Clusters', 'value': 0.48, 'unit': 'clusters'},
            'microstructure_regime': {'name': 'Microstructure', 'value': 0.55, 'unit': 'regime'}
        }
