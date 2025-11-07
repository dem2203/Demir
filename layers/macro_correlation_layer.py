# macro_correlation_layer.py - WITH SOURCE TRACKING (UPDATED)
# 7 Kasım 2025 - v4.1 - Source field eklendi

import requests
import pandas as pd
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

class MacroCorrelationLayer:
    """Macro correlation analysis layer"""
    
    def __init__(self):
        self.alpha_vantage_key = "YOUR_ALPHA_VANTAGE_KEY"
        self.twelve_data_key = "YOUR_TWELVE_DATA_KEY"
        self.coinmarketcap_key = "YOUR_COINMARKETCAP_KEY"
    
    def fetch_spy_data(self) -> Optional[float]:
        """Fetch SPY (S&P 500) data"""
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': 'SPY',
                'apikey': self.alpha_vantage_key
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Global Quote' in data and 'c' in data['Global Quote']:
                return float(data['Global Quote']['c'])
            return None
        except Exception as e:
            print(f"SPY Fetch Error: {e}")
            return None
    
    def fetch_qqq_data(self) -> Optional[float]:
        """Fetch QQQ (Nasdaq-100) data"""
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': 'QQQ',
                'apikey': self.alpha_vantage_key
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Global Quote' in data and 'c' in data['Global Quote']:
                return float(data['Global Quote']['c'])
            return None
        except Exception as e:
            print(f"QQQ Fetch Error: {e}")
            return None
    
    def fetch_dxy_data(self) -> Optional[float]:
        """Fetch DXY (US Dollar Index) data"""
        try:
            url = "https://api.twelvedata.com/price"
            params = {
                'symbol': 'DXY',
                'apikey': self.twelve_data_key
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'price' in data:
                return float(data['price'])
            return None
        except Exception as e:
            print(f"DXY Fetch Error: {e}")
            return None
    
    def fetch_gold_data(self) -> Optional[float]:
        """Fetch Gold (XAU/USD) data"""
        try:
            url = "https://api.twelvedata.com/price"
            params = {
                'symbol': 'XAU/USD',
                'apikey': self.twelve_data_key
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'price' in data:
                return float(data['price'])
            return None
        except Exception as e:
            print(f"Gold Fetch Error: {e}")
            return None
    
    def fetch_vix_data(self) -> Optional[float]:
        """Fetch VIX (Volatility Index) data"""
        try:
            url = "https://api.twelvedata.com/price"
            params = {
                'symbol': 'VIX',
                'apikey': self.twelve_data_key
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'price' in data:
                return float(data['price'])
            return None
        except Exception as e:
            print(f"VIX Fetch Error: {e}")
            return None
    
    def fetch_btc_dominance(self) -> Optional[float]:
        """Fetch BTC Dominance from CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/global"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if 'data' in data and 'btc_market_cap_percentage' in data['data']:
                return float(data['data']['btc_market_cap_percentage'])
            return None
        except Exception as e:
            print(f"BTC Dominance Fetch Error: {e}")
            return None
    
    def calculate_score(self, spy=None, qqq=None, dxy=None, gold=None, vix=None, btc_dom=None) -> float:
        """Calculate macro correlation score"""
        score = 50
        count = 0
        
        # SPY - S&P 500 correlation
        if spy:
            if spy > 450:  # Strong market
                score += 5
            elif spy < 400:  # Weak market
                score -= 5
            count += 1
        
        # QQQ - Tech correlation
        if qqq:
            if qqq > 350:  # Strong tech
                score += 5
            elif qqq < 300:  # Weak tech
                score -= 5
            count += 1
        
        # DXY - Dollar strength
        if dxy:
            if dxy > 105:  # Strong dollar
                score -= 10  # Bearish for crypto
            elif dxy < 100:  # Weak dollar
                score += 10  # Bullish for crypto
            count += 1
        
        # Gold - Safe haven
        if gold:
            if gold > 4000:  # High gold = risk off
                score -= 5
            elif gold < 3850:  # Low gold = risk on
                score += 5
            count += 1
        
        # VIX - Volatility
        if vix:
            if vix > 20:  # High volatility
                score -= 10
            elif vix < 15:  # Low volatility
                score += 10
            count += 1
        
        # BTC Dominance
        if btc_dom:
            if btc_dom > 55:  # High dominance
                score += 5
            elif btc_dom < 50:  # Low dominance
                score -= 5
            count += 1
        
        if count > 0:
            return min(100, max(0, score))
        return 50
    
    def analyze_all(self) -> Dict[str, Any]:
        """Analyze all macro factors"""
        
        print(f"\n{'='*80}")
        print(f"🌍 MACRO CORRELATION ANALYSIS")
        print(f"{'='*80}\n")
        
        # Fetch all data
        spy = self.fetch_spy_data()
        qqq = self.fetch_qqq_data()
        dxy = self.fetch_dxy_data()
        gold = self.fetch_gold_data()
        vix = self.fetch_vix_data()
        btc_dom = self.fetch_btc_dominance()
        
        print(f"📊 Market Data:")
        if spy:
            print(f"   SPY: ${spy:.2f}")
        else:
            print(f"   ⚠️ SPY: No data")
        
        if qqq:
            print(f"   QQQ: ${qqq:.2f}")
        else:
            print(f"   ⚠️ QQQ: No data")
        
        if dxy:
            print(f"   DXY: {dxy:.2f}")
        else:
            print(f"   ⚠️ DXY: No data")
        
        if gold:
            print(f"   Gold: ${gold:.2f}")
        else:
            print(f"   ⚠️ Gold: No data")
        
        if vix:
            print(f"   VIX: {vix:.2f}")
        else:
            print(f"   ⚠️ VIX: No data")
        
        if btc_dom:
            print(f"   BTC Dominance: {btc_dom:.2f}%")
        else:
            print(f"   ⚠️ BTC Dominance: No data")
        
        # Calculate score
        score = self.calculate_score(spy, qqq, dxy, gold, vix, btc_dom)
        
        if score >= 60:
            signal = 'BULLISH'
        elif score >= 40:
            signal = 'NEUTRAL'
        else:
            signal = 'BEARISH'
        
        result = {
            'available': True,
            'score': score,
            'signal': signal,
            'factors': {
                'spy': spy,
                'qqq': qqq,
                'dxy': dxy,
                'gold': gold,
                'vix': vix,
                'btc_dominance': btc_dom
            },
            'source': 'REAL'  # ← ADDED: Source tracking
        }
        
        print(f"\n✅ MACRO ANALYSIS COMPLETE!")
        print(f"   Total Score: {score}/100")
        print(f"   Signal: {signal}")
        print(f"{'='*80}\n")
        
        return result

if __name__ == "__main__":
    print("="*80)
    print("🔱 MACRO CORRELATION LAYER v4.1 TEST")
    print("="*80)
    
    layer = MacroCorrelationLayer()
    result = layer.analyze_all()
    print(f"📊 Final Result: {result}")
