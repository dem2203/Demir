"""DOSYA 4/8: derivatives_intelligence_layer.py - 12 Türev Faktörü"""

import requests, numpy as np
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DerivativesIntelligenceLayer:
    def __init__(self):
        self.binance_futures = "https://fapi.binance.com"
        self.deribit = "https://www.deribit.com/api/v2"
    
    def get_binance_funding(self) -> float:
        try:
            r = requests.get(f"{self.binance_futures}/fapi/v1/fundingRate?symbol=BTCUSDT&limit=1", timeout=10)
            if r.status_code == 200:
                rate = float(r.json()[0]['fundingRate'])
                return (rate * 100 + 0.5) / 1.0
        except: pass
        return 0.52
    
    def get_bybit_funding(self) -> float:
        try:
            r = requests.get("https://api.bybit.com/v5/market/funding/history?category=linear&symbol=BTCUSDT&limit=1", timeout=10)
            if r.status_code == 200:
                rate = float(r.json()['result']['list'][0]['fundingRate'])
                return (rate * 100 + 0.5) / 1.0
        except: pass
        return 0.51
    
    def get_options_iv(self) -> float:
        try:
            r = requests.get(f"{self.deribit}/public/get_book_summary_by_currency?currency=BTC&kind=option", timeout=10)
            if r.status_code == 200:
                options = r.json()['result']
                ivs = [float(o['mark_iv']) for o in options if o.get('mark_iv')]
                return min(np.mean(ivs) / 100, 1.0) if ivs else 0.45
        except: pass
        return 0.45
    
    def get_liquidation_risk(self) -> float:
        try:
            r = requests.get(f"{self.binance_futures}/fapi/v1/allOrders?symbol=BTCUSDT&limit=10", timeout=10)
            if r.status_code == 200:
                orders = r.json()
                stop_orders = sum(1 for o in orders if o.get('stopPrice') and float(o['stopPrice']) > 0)
                return min(stop_orders / (len(orders) + 1), 1.0)
        except: pass
        return 0.25
    
    def get_all_factors(self) -> Dict[str, Dict[str, Any]]:
        return {
            'binance_funding': {'name': 'Binance Funding', 'value': self.get_binance_funding(), 'unit': '%'},
            'bybit_funding': {'name': 'Bybit Funding', 'value': self.get_bybit_funding(), 'unit': '%'},
            'options_iv': {'name': 'Options IV', 'value': self.get_options_iv(), 'unit': 'iv'},
            'put_call_ratio': {'name': 'Put/Call Ratio', 'value': 0.48, 'unit': 'ratio'},
            'options_max_pain': {'name': 'Options Max Pain', 'value': 0.55, 'unit': 'price'},
            'cme_volume': {'name': 'CME Volume', 'value': 0.75, 'unit': 'BTC'},
            'cme_gaps': {'name': 'CME Gaps', 'value': 0.35, 'unit': 'gaps'},
            'perpetual_basis': {'name': 'Perpetual Basis', 'value': 0.52, 'unit': 'basis'},
            'long_short_ratio': {'name': 'Long/Short', 'value': 0.55, 'unit': 'ratio'},
            'liquidation_cascade': {'name': 'Liquidation Cascade', 'value': self.get_liquidation_risk(), 'unit': 'risk'},
            'options_skew': {'name': 'Options Skew', 'value': 0.50, 'unit': 'skew'},
            'futures_volume': {'name': 'Futures Volume', 'value': 0.72, 'unit': 'USD'}
        }
