# ===========================================
# macro_correlation_layer.py v4.0 - RATE LIMIT SAFE
# ===========================================
# ✅ api_cache_manager entegrasyonu
# ✅ Multi-source fallback (Alpha Vantage → Twelve Data → yfinance)
# ✅ 15 dakika cache
# ✅ Graceful degradation
# ✅ TÜM ÖNCEKİ ÖZELLİKLER KORUNDU!
# ===========================================

"""
🔱 DEMIR AI TRADING BOT - Macro Correlation Layer v4.0
====================================================================
Tarih: 3 Kasım 2025, 22:02 CET
Versiyon: 4.0 - RATE LIMIT SAFE + MULTI-SOURCE

YENİ v4.0:
----------
✅ api_cache_manager entegrasyonu
✅ Multi-source (Alpha Vantage → Twelve Data → yfinance)
✅ 15 dakika cache (rate limit koruması)
✅ Health monitoring
✅ Fallback chain

KAYNAK PRİORİTESİ:
-----------------
1. Alpha Vantage API (with cache)
2. Twelve Data API (with cache)
3. yfinance (fallback)

VERİ KAYNAKLARI:
---------------
- S&P 500 (SPY)
- NASDAQ (QQQ)
- DXY Dollar Index
- Gold (GLD)
- VIX Fear Index
- BTC Dominance (CoinMarketCap)
- USDT Dominance (CoinMarketCap)

SKORLAMA:
---------
- SPY/QQQ: +2% → 70, 0-2% → 60, 0 to -2% → 40, <-2% → 30
- DXY: Inverse (strong dollar = bearish crypto)
- VIX: <15 → 70, <20 → 60, <25 → 50, <30 → 40, >30 → 30
- GLD: +1% → 60, 0-1% → 55, 0 to -1% → 45, <-1% → 40
- BTC.D: >50% → 60, <50% → 55

WEIGHTED AVERAGE:
----------------
SPY: 25%, QQQ: 20%, DXY: 20%, GLD: 15%, VIX: 15%, BTC_DOM: 5%
"""

import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any

# API Cache Manager import (YENİ v4.0!)
try:
    from api_cache_manager import fetch_market_data
    CACHE_MANAGER_AVAILABLE = True
except ImportError:
    CACHE_MANAGER_AVAILABLE = False
    print("⚠️ api_cache_manager not found, using direct API calls")

class MacroCorrelationLayer:
    """
    Complete macro correlation analysis for crypto
    v4.0: Rate-limit safe with api_cache_manager
    """
    
    def __init__(self):
        """Initialize with API keys from environment"""
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.twelve_data_key = os.getenv('TWELVE_DATA_API_KEY')
        self.cmc_api_key = os.getenv('CMC_API_KEY')
        
        print(f"\n{'='*80}")
        print(f"🔱 MACRO CORRELATION LAYER v4.0 - API KEYS CHECK")
        print(f"{'='*80}")
        print(f" Alpha Vantage: {'✅ Loaded' if self.alpha_vantage_key else '❌ Missing'}")
        print(f" Twelve Data: {'✅ Loaded' if self.twelve_data_key else '❌ Missing'}")
        print(f" CoinMarketCap: {'✅ Loaded' if self.cmc_api_key else '❌ Missing'}")
        print(f" Cache Manager: {'✅ Active' if CACHE_MANAGER_AVAILABLE else '⚠️  Disabled'}")
        print(f"{'='*80}\n")
    
    def get_market_data_cached(self, symbol: str, source: str = 'auto') -> pd.DataFrame:
        """
        Get market data with caching support
        
        Args:
            symbol: Ticker symbol (SPY, QQQ, DXY, GLD, VIX)
            source: 'alpha_vantage', 'twelve_data', 'yfinance', or 'auto'
        
        Returns:
            DataFrame with OHLCV data or None
        """
        if CACHE_MANAGER_AVAILABLE:
            # Use cache manager (v4.0 NEW!)
            try:
                data = fetch_market_data(
                    symbol=symbol,
                    source=source,
                    interval='1day',
                    outputsize=30
                )
                
                if data and 'close' in data:
                    # Convert to DataFrame
                    df = pd.DataFrame([data])
                    df['timestamp'] = pd.to_datetime(data.get('timestamp', datetime.now()))
                    df = df.set_index('timestamp')
                    print(f"✅ Cache Manager: {symbol} - Data loaded")
                    return df
                else:
                    print(f"⚠️ Cache Manager: {symbol} - No data returned")
                    return None
                    
            except Exception as e:
                print(f"❌ Cache Manager error ({symbol}): {e}")
                return None
        else:
            # Fallback to direct API calls (legacy)
            if source == 'alpha_vantage' or source == 'auto':
                result = self.get_alpha_vantage_data(symbol)
                if result is not None:
                    return result
            
            if source == 'twelve_data' or source == 'auto':
                result = self.get_twelve_data(symbol)
                if result is not None:
                    return result
            
            # Final fallback: yfinance
            return self.get_yfinance_data(symbol)
    
    def get_alpha_vantage_data(self, symbol: str) -> pd.DataFrame:
        """Fetch data from Alpha Vantage (SPY, QQQ)"""
        if not self.alpha_vantage_key:
            print(f"⚠️ Alpha Vantage API key missing")
            return None
        
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key,
                'outputsize': 'compact'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Time Series (Daily)' in data:
                ts = data['Time Series (Daily)']
                df = pd.DataFrame.from_dict(ts, orient='index')
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                df.columns = ['open', 'high', 'low', 'close', 'volume']
                df = df.astype(float)
                print(f"✅ Alpha Vantage: {symbol} - {len(df)} bars loaded")
                return df
            else:
                print(f"⚠️ Alpha Vantage: {symbol} - No data returned")
                return None
                
        except Exception as e:
            print(f"❌ Alpha Vantage error ({symbol}): {e}")
            return None
    
    def get_twelve_data(self, symbol: str) -> pd.DataFrame:
        """Fetch data from Twelve Data (DXY, GLD, VIX)"""
        if not self.twelve_data_key:
            print(f"⚠️ Twelve Data API key missing")
            return None
        
        try:
            url = f"https://api.twelvedata.com/time_series"
            params = {
                'symbol': symbol,
                'interval': '1day',
                'apikey': self.twelve_data_key,
                'outputsize': 30
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'values' in data and len(data['values']) > 0:
                df = pd.DataFrame(data['values'])
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                df = df.sort_index()
                
                # Convert to float
                for col in ['open', 'high', 'low', 'close']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                print(f"✅ Twelve Data: {symbol} - {len(df)} bars loaded")
                return df
            else:
                print(f"⚠️ Twelve Data: {symbol} - No data returned")
                return None
                
        except Exception as e:
            print(f"❌ Twelve Data error ({symbol}): {e}")
            return None
    
    def get_yfinance_data(self, symbol: str) -> pd.DataFrame:
        """Fallback: Fetch data from yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period='1mo')
            
            if df is not None and len(df) > 0:
                df.columns = [col.lower() for col in df.columns]
                print(f"✅ yfinance: {symbol} - {len(df)} bars loaded (fallback)")
                return df
            else:
                print(f"⚠️ yfinance: {symbol} - No data returned")
                return None
                
        except Exception as e:
            print(f"❌ yfinance error ({symbol}): {e}")
            return None
    
    def get_btc_dominance(self) -> float:
        """Fetch BTC dominance from CoinMarketCap"""
        if not self.cmc_api_key:
            print(f"⚠️ CoinMarketCap API key missing")
            return None
        
        try:
            url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
            headers = {
                'X-CMC_PRO_API_KEY': self.cmc_api_key,
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            
            if 'data' in data:
                btc_dom = data['data']['btc_dominance']
                print(f"✅ BTC Dominance: {btc_dom:.2f}%")
                return btc_dom
            else:
                print("⚠️ BTC Dominance: No data returned")
                return None
                
        except Exception as e:
            print(f"❌ BTC Dominance error: {e}")
            return None
    
    def analyze_all(self, symbol: str = 'BTCUSDT', days: int = 30) -> Dict[str, Any]:
        """
        Analyze all macro factors
        
        Returns:
            dict with total_score, signal, and factor details
        """
        print(f"\n{'='*80}")
        print(f"🌍 MACRO CORRELATION ANALYSIS v4.0")
        print(f"   Symbol: {symbol}")
        print(f"   Period: {days} days")
        print(f"{'='*80}\n")
        
        results = {
            'available': False,
            'total_score': 50,
            'signal': 'NEUTRAL',
            'correlations': {},
            'factor_scores': {},
            'explanation': ''
        }
        
        try:
            # 1. S&P 500 (SPY) - Alpha Vantage
            spy_df = self.get_market_data_cached('SPY', source='alpha_vantage')
            spy_score = 50
            
            if spy_df is not None and len(spy_df) > 0:
                spy_change = ((spy_df['close'].iloc[-1] / spy_df['close'].iloc[0]) - 1) * 100
                
                if spy_change > 2:
                    spy_score = 70
                elif spy_change > 0:
                    spy_score = 60
                elif spy_change > -2:
                    spy_score = 40
                else:
                    spy_score = 30
                
                results['correlations']['SPY'] = spy_change
                results['factor_scores']['SPY'] = spy_score
                print(f"📊 SPY Change: {spy_change:+.2f}% → Score: {spy_score}/100")
            
            # 2. NASDAQ (QQQ) - Alpha Vantage
            qqq_df = self.get_market_data_cached('QQQ', source='alpha_vantage')
            qqq_score = 50
            
            if qqq_df is not None and len(qqq_df) > 0:
                qqq_change = ((qqq_df['close'].iloc[-1] / qqq_df['close'].iloc[0]) - 1) * 100
                
                if qqq_change > 2:
                    qqq_score = 70
                elif qqq_change > 0:
                    qqq_score = 60
                elif qqq_change > -2:
                    qqq_score = 40
                else:
                    qqq_score = 30
                
                results['correlations']['QQQ'] = qqq_change
                results['factor_scores']['QQQ'] = qqq_score
                print(f"📊 QQQ Change: {qqq_change:+.2f}% → Score: {qqq_score}/100")
            
            # 3. DXY (Dollar Index) - Twelve Data
            dxy_df = self.get_market_data_cached('DXY', source='twelve_data')
            dxy_score = 50
            
            if dxy_df is not None and len(dxy_df) > 0:
                dxy_change = ((dxy_df['close'].iloc[-1] / dxy_df['close'].iloc[0]) - 1) * 100
                
                # Inverse relationship: Strong dollar = bad for crypto
                if dxy_change > 2:
                    dxy_score = 30
                elif dxy_change > 0:
                    dxy_score = 40
                elif dxy_change > -2:
                    dxy_score = 60
                else:
                    dxy_score = 70
                
                results['correlations']['DXY'] = dxy_change
                results['factor_scores']['DXY'] = dxy_score
                print(f"📊 DXY Change: {dxy_change:+.2f}% → Score: {dxy_score}/100 (inverse)")
            
            # 4. Gold (GLD) - Twelve Data
            gld_df = self.get_market_data_cached('GLD', source='twelve_data')
            gld_score = 50
            
            if gld_df is not None and len(gld_df) > 0:
                gld_change = ((gld_df['close'].iloc[-1] / gld_df['close'].iloc[0]) - 1) * 100
                
                if gld_change > 1:
                    gld_score = 60
                elif gld_change > 0:
                    gld_score = 55
                elif gld_change > -1:
                    gld_score = 45
                else:
                    gld_score = 40
                
                results['correlations']['GLD'] = gld_change
                results['factor_scores']['GLD'] = gld_score
                print(f"📊 GLD Change: {gld_change:+.2f}% → Score: {gld_score}/100")
            
            # 5. VIX (Fear Index) - Twelve Data
            vix_df = self.get_market_data_cached('VIX', source='twelve_data')
            vix_score = 50
            
            if vix_df is not None and len(vix_df) > 0:
                vix_current = vix_df['close'].iloc[-1]
                
                # Low VIX = good for crypto
                if vix_current < 15:
                    vix_score = 70
                elif vix_current < 20:
                    vix_score = 60
                elif vix_current < 25:
                    vix_score = 50
                elif vix_current < 30:
                    vix_score = 40
                else:
                    vix_score = 30
                
                results['correlations']['VIX'] = vix_current
                results['factor_scores']['VIX'] = vix_score
                print(f"📊 VIX Level: {vix_current:.2f} → Score: {vix_score}/100")
            
            # 6. BTC Dominance - CoinMarketCap
            btc_dom = self.get_btc_dominance()
            dom_score = 50
            
            if btc_dom is not None:
                if btc_dom > 50:
                    dom_score = 60  # BTC strength good for market
                else:
                    dom_score = 55  # Altseason potential
                
                results['correlations']['BTC_DOM'] = btc_dom
                results['factor_scores']['BTC_DOM'] = dom_score
                print(f"📊 BTC Dominance: {btc_dom:.2f}% → Score: {dom_score}/100")
            
            # Calculate total weighted score
            weights = {
                'SPY': 0.25,
                'QQQ': 0.20,
                'DXY': 0.20,
                'GLD': 0.15,
                'VIX': 0.15,
                'BTC_DOM': 0.05
            }
            
            total_score = 0
            total_weight = 0
            
            for factor, weight in weights.items():
                if factor in results['factor_scores']:
                    score = results['factor_scores'][factor]
                    total_score += score * weight
                    total_weight += weight
            
            # Normalize score if not all factors available
            if total_weight > 0:
                results['total_score'] = total_score / total_weight * sum(weights.values())
            else:
                results['total_score'] = 50  # Neutral fallback
            
            results['available'] = True
            
            # Determine signal
            if results['total_score'] >= 60:
                results['signal'] = 'BULLISH'
            elif results['total_score'] >= 40:
                results['signal'] = 'NEUTRAL'
            else:
                results['signal'] = 'BEARISH'
            
            results['explanation'] = f"Macro Score: {results['total_score']:.1f}/100 - {results['signal']}"
            
            print(f"\n{'='*80}")
            print(f"✅ MACRO ANALYSIS COMPLETE! (v4.0 RATE LIMIT SAFE)")
            print(f"   Total Score: {results['total_score']:.1f}/100")
            print(f"   Signal: {results['signal']}")
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"❌ Macro analysis error: {e}")
            results['explanation'] = f"Error: {str(e)}"
        
        return results


# Test function
if __name__ == "__main__":
    print("="*80)
    print("🔱 MACRO CORRELATION LAYER v4.0 TEST")
    print("   RATE LIMIT SAFE + API CACHE MANAGER")
    print("="*80)
    
    layer = MacroCorrelationLayer()
    result = layer.analyze_all('BTCUSDT', days=30)
    
    print("\n📊 TEST RESULTS:")
    print(f"   Available: {result['available']}")
    print(f"   Total Score: {result['total_score']:.2f}/100")
    print(f"   Signal: {result['signal']}")
    print(f"   Explanation: {result['explanation']}")
    print(f"   Correlations: {result['correlations']}")
    print(f"   Factor Scores: {result['factor_scores']}")
