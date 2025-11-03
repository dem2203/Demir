"""
📈 TRADITIONAL MARKETS LAYER v3.0 - ALPHA VANTAGE + TWELVE DATA
=================================================================
Date: 3 Kasım 2025, 10:58 CET
Version: 3.0 - Real API Integration

✅ REAL DATA SOURCES:
- S&P 500 (SPY) → Alpha Vantage API
- NASDAQ (QQQ) → Alpha Vantage API  
- DXY Dollar Index → Twelve Data API

✅ FEATURES:
- Real-time stock market data
- Dollar index tracking
- Crypto correlation analysis
- Fallback to neutral if API fails
"""

import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

class TraditionalMarketsLayer:
    """
    Traditional markets analysis for crypto correlation
    Uses Alpha Vantage + Twelve Data APIs
    """
    
    def __init__(self):
        """Initialize with API keys from environment"""
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.twelve_data_key = os.getenv('TWELVE_DATA_API_KEY')
        
        print(f"\n{'='*80}")
        print(f"📈 TRADITIONAL MARKETS LAYER v3.0 - API KEYS CHECK")
        print(f"{'='*80}")
        print(f"   Alpha Vantage: {'✅ Loaded' if self.alpha_vantage_key else '❌ Missing'}")
        print(f"   Twelve Data: {'✅ Loaded' if self.twelve_data_key else '❌ Missing'}")
        print(f"{'='*80}\n")
    
    def get_alpha_vantage_price(self, symbol):
        """
        Alpha Vantage'dan anlık fiyat çeker (SPY, QQQ)
        
        Args:
            symbol: Stock ticker (SPY, QQQ, etc.)
        
        Returns:
            float: Current price or None
        """
        if not self.alpha_vantage_key:
            print(f"⚠️ Alpha Vantage API key missing")
            return None
        
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Global Quote' in data and '05. price' in data['Global Quote']:
                price = float(data['Global Quote']['05. price'])
                change_pct = float(data['Global Quote']['10. change percent'].rstrip('%'))
                print(f"✅ Alpha Vantage: {symbol} = ${price:.2f} ({change_pct:+.2f}%)")
                return {'price': price, 'change_pct': change_pct}
            else:
                print(f"⚠️ Alpha Vantage: {symbol} - No price data")
                return None
                
        except Exception as e:
            print(f"❌ Alpha Vantage error ({symbol}): {e}")
            return None
    
    def get_twelve_data_price(self, symbol):
        """
        Twelve Data'dan anlık fiyat çeker (DXY)
        
        Args:
            symbol: Symbol (DXY, etc.)
        
        Returns:
            dict: price and change_pct or None
        """
        if not self.twelve_data_key:
            print(f"⚠️ Twelve Data API key missing")
            return None
        
        try:
            # Get current price
            url_price = f"https://api.twelvedata.com/price"
            params_price = {
                'symbol': symbol,
                'apikey': self.twelve_data_key
            }
            
            response_price = requests.get(url_price, params=params_price, timeout=10)
            data_price = response_price.json()
            
            if 'price' in data_price:
                price = float(data_price['price'])
                
                # Get quote for change percentage
                url_quote = f"https://api.twelvedata.com/quote"
                params_quote = {
                    'symbol': symbol,
                    'apikey': self.twelve_data_key
                }
                
                response_quote = requests.get(url_quote, params=params_quote, timeout=10)
                data_quote = response_quote.json()
                
                change_pct = 0
                if 'percent_change' in data_quote:
                    change_pct = float(data_quote['percent_change'])
                
                print(f"✅ Twelve Data: {symbol} = {price:.2f} ({change_pct:+.2f}%)")
                return {'price': price, 'change_pct': change_pct}
            else:
                print(f"⚠️ Twelve Data: {symbol} - No price data")
                return None
                
        except Exception as e:
            print(f"❌ Twelve Data error ({symbol}): {e}")
            return None
    
    def analyze_all_markets(self, crypto_symbol='BTCUSDT', days=30):
        """
        Analyze all traditional markets and their crypto impact
        
        Args:
            crypto_symbol: Crypto trading pair
            days: Analysis period
        
        Returns:
            dict with analysis results
        """
        print(f"\n{'='*80}")
        print(f"📈 TRADITIONAL MARKETS ANALYSIS")
        print(f"   Crypto: {crypto_symbol}")
        print(f"   Period: {days} days")
        print(f"{'='*80}\n")
        
        result = {
            'available': False,
            'total_score': 50,
            'signal': 'NEUTRAL',
            'markets': {},
            'interpretation': 'No data available'
        }
        
        try:
            scores = []
            weights = []
            
            # 1. S&P 500 (SPY)
            spy_data = self.get_alpha_vantage_price('SPY')
            if spy_data:
                spy_score = 50
                if spy_data['change_pct'] > 1:
                    spy_score = 65
                elif spy_data['change_pct'] > 0:
                    spy_score = 57
                elif spy_data['change_pct'] > -1:
                    spy_score = 43
                else:
                    spy_score = 35
                
                result['markets']['SPY'] = {
                    'price': spy_data['price'],
                    'change_pct': spy_data['change_pct'],
                    'score': spy_score
                }
                scores.append(spy_score)
                weights.append(0.35)
            
            # 2. NASDAQ (QQQ)
            qqq_data = self.get_alpha_vantage_price('QQQ')
            if qqq_data:
                qqq_score = 50
                if qqq_data['change_pct'] > 1:
                    qqq_score = 65
                elif qqq_data['change_pct'] > 0:
                    qqq_score = 57
                elif qqq_data['change_pct'] > -1:
                    qqq_score = 43
                else:
                    qqq_score = 35
                
                result['markets']['QQQ'] = {
                    'price': qqq_data['price'],
                    'change_pct': qqq_data['change_pct'],
                    'score': qqq_score
                }
                scores.append(qqq_score)
                weights.append(0.30)
            
            # 3. DXY (Dollar Index)
            dxy_data = self.get_twelve_data_price('DXY')
            if dxy_data:
                dxy_score = 50
                # Inverse relationship: Strong dollar = bad for crypto
                if dxy_data['change_pct'] > 0.5:
                    dxy_score = 35
                elif dxy_data['change_pct'] > 0:
                    dxy_score = 43
                elif dxy_data['change_pct'] > -0.5:
                    dxy_score = 57
                else:
                    dxy_score = 65
                
                result['markets']['DXY'] = {
                    'price': dxy_data['price'],
                    'change_pct': dxy_data['change_pct'],
                    'score': dxy_score
                }
                scores.append(dxy_score)
                weights.append(0.35)
            
            # Calculate weighted total score
            if scores and weights:
                total_weight = sum(weights)
                weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
                result['total_score'] = weighted_score
                result['available'] = True
                
                # Determine signal
                if weighted_score >= 60:
                    result['signal'] = 'BULLISH'
                elif weighted_score >= 40:
                    result['signal'] = 'NEUTRAL'
                else:
                    result['signal'] = 'BEARISH'
                
                result['interpretation'] = f"Traditional markets score: {weighted_score:.1f}/100 - {result['signal']}"
                
                print(f"\n✅ TRADITIONAL MARKETS ANALYSIS COMPLETE!")
                print(f"   Total Score: {weighted_score:.1f}/100")
                print(f"   Signal: {result['signal']}")
                print(f"{'='*80}\n")
            else:
                print("⚠️ Insufficient data for traditional markets analysis")
        
        except Exception as e:
            print(f"❌ Traditional markets analysis error: {e}")
            result['interpretation'] = f"Error: {str(e)}"
        
        return result

def get_traditional_markets_signal(crypto_symbol='BTCUSDT', days=30):
    """
    Simple wrapper for traditional markets signal
    
    Args:
        crypto_symbol: Crypto trading pair
        days: Analysis period
    
    Returns:
        dict with signal and score
    """
    layer = TraditionalMarketsLayer()
    result = layer.analyze_all_markets(crypto_symbol, days)
    
    return {
        'signal': result['signal'],
        'score': result['total_score'],
        'available': result['available'],
        'markets': result.get('markets', {})
    }

# Test function
if __name__ == "__main__":
    print("="*80)
    print("📈 TRADITIONAL MARKETS LAYER v3.0 TEST")
    print("   Alpha Vantage + Twelve Data Integration")
    print("="*80)
    
    layer = TraditionalMarketsLayer()
    result = layer.analyze_all_markets('BTCUSDT', days=30)
    
    print("\n📊 TEST RESULTS:")
    print(f"   Available: {result['available']}")
    print(f"   Total Score: {result['total_score']:.2f}/100")
    print(f"   Signal: {result['signal']}")
    print(f"   Interpretation: {result['interpretation']}")
    print(f"\n   Markets Data:")
    for market, data in result.get('markets', {}).items():
        print(f"      {market}: ${data['price']:.2f} ({data['change_pct']:+.2f}%) - Score: {data['score']}/100")
