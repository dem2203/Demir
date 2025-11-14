"""
ENHANCED RATES LAYER v3 - REEL VERİ İLE ÇALIŞ
==============================================
Date: 7 Kasım 2025, 20:00 CET
Version: 3.0 - Real Data + Retry Logic + Intelligent Fallbacks
"""

import requests
import os
import logging
import time
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedRatesLayer:
    """Enhanced Interest Rates Layer with robust real data handling"""
    
    def __init__(self):
        """Initialize with aggressive settings for Render"""
        self.timeout = 25  # Very long timeout for Render
        self.max_retries = 3  # Try 3 times
        self.retry_delay = 3  # 3 second delay between retries
        self.fallback_rate = 4.25  # Realistic fallback
        logger.info(f"✅ Enhanced Rates Layer v3 initialized (Timeout: {self.timeout}s, Retries: {self.max_retries})")
    
    def get_10y_treasury_yield(self) -> Optional[float]:
        """
        Get 10-Year US Treasury Yield with AGGRESSIVE retry logic
        Tries: Yahoo Finance → Direct API → Fallback
        """
        
        # Method 1: Yahoo Finance
        for attempt in range(self.max_retries):
            try:
                logger.info(f" 📡 [Yahoo Finance] Attempt {attempt+1}/{self.max_retries}...")
                url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ETNX"
                response = requests.get(
                    url,
                    params={'interval': '1d', 'range': '5d'},
                    timeout=self.timeout,
                    headers={'User-Agent': 'Mozilla/5.0'}  # Add header to avoid block
                )
                response.raise_for_status()
                data = response.json()
                
                if 'chart' in data and 'result' in data['chart']:
                    result = data['chart']['result'][0]
                    closes = result.get('indicators', {}).get('quote', [{}])[0].get('close', [])
                    closes = [c for c in closes if c]
                    
                    if closes:
                        yield_value = closes[-1]
                        logger.info(f" ✅ Yahoo Finance: 10Y yield = {yield_value:.3f}%")
                        return yield_value
                    else:
                        logger.warning(f" ⚠️ Yahoo Finance: No close data")
                else:
                    logger.warning(f" ⚠️ Yahoo Finance: Invalid response structure")
                    
            except requests.exceptions.Timeout:
                logger.warning(f" ⚠️ Yahoo Finance: Timeout (attempt {attempt+1})")
            except requests.exceptions.ConnectionError:
                logger.warning(f" ⚠️ Yahoo Finance: Connection error (attempt {attempt+1})")
            except Exception as e:
                logger.warning(f" ⚠️ Yahoo Finance: {str(e)[:60]} (attempt {attempt+1})")
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        # Method 2: US Treasury API
        for attempt in range(self.max_retries):
            try:
                logger.info(f" 📡 [US Treasury] Attempt {attempt+1}/{self.max_retries}...")
                # Direct Treasury data
                url = "https://www.treasurydirect.gov/NP_WS/debt/current"
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # US Treasury returns different format, extract if possible
                # This is a simplified version - full parsing needed
                logger.info(f" ✅ US Treasury: Connected")
                # For now, return None as we need to parse Treasury format
                return None
                
            except Exception as e:
                logger.warning(f" ⚠️ US Treasury: {str(e)[:50]} (attempt {attempt+1})")
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        logger.error(f" ❌ All yield fetching attempts failed")
        return None
    
    def calculate_rates_score(self, symbol: str = 'BTCUSDT') -> Dict:
        """
        Calculate interest rates score for crypto market
        
        Logic:
        - Lower rates (< 4.0%) = Bullish for crypto → Score 60+
        - Higher rates (> 5.0%) = Bearish for crypto → Score 40-
        - Medium rates = Neutral → Score 50
        
        Confidence based on data freshness:
        - Real API data: 0.95
        - Fallback data: 0.65
        """
        
        logger.info(f"\n📊 CALCULATING INTEREST RATES SCORE FOR {symbol}...")
        
        # Get 10Y yield
        yield_10y = self.get_10y_treasury_yield()
        
     # API failed - NO FALLBACK, return None
else:
    logger.error("❌ All attempts to fetch 10Y Treasury yield failed!")
    logger.error("⚠️ Policy: NO MOCK DATA, NO FALLBACK - Skipping this layer")
    self.send_telegram_alert("⚠️ Treasury Yield API Failed - Signal Analysis Skipped")
    return None  # Skip this layer entirely, don't use fake data
            confidence = 0.65
        else:
            using_fallback = False
            confidence = 0.95
        
        # Calculate score based on yield level
        if yield_10y < 3.5:
            score = 70
            signal = 'STRONG_LONG'
            explanation = "Very low rates → Crypto very bullish (risk-on, capital flows to alternatives)"
        elif yield_10y < 4.0:
            score = 60
            signal = 'LONG'
            explanation = "Low rates → Crypto bullish (cheap capital, risk assets favored)"
        elif yield_10y < 4.5:
            score = 55
            signal = 'LONG'
            explanation = "Moderate-low rates → Slightly bullish for crypto"
        elif yield_10y < 5.0:
            score = 50
            signal = 'NEUTRAL'
            explanation = "Moderate rates → Balanced sentiment for crypto"
        elif yield_10y < 5.5:
            score = 45
            signal = 'SHORT'
            explanation = "Moderate-high rates → Slightly bearish for crypto"
        elif yield_10y < 6.0:
            score = 40
            signal = 'SHORT'
            explanation = "High rates → Bearish for crypto (capital flows to bonds)"
        else:
            score = 30
            signal = 'STRONG_SHORT'
            explanation = "Very high rates → Very bearish for crypto (flight to safety)"
        
        result = {
            'score': score,
            'signal': signal,
            'explanation': explanation,
            'yield_10y': round(yield_10y, 3),
            'confidence': confidence,
            'using_fallback': using_fallback,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'available': True,
            'symbol': symbol,
            'source': 'FALLBACK' if using_fallback else 'REAL_API'
        }
        
        logger.info(f"")
        logger.info(f" 📊 Score: {score}/100 | Signal: {signal}")
        logger.info(f" 10Y Yield: {yield_10y:.3f}% | Confidence: {confidence:.0%}")
        logger.info(f" Source: {result['source']}")
        
        return result
    
    def get_rates_signal(self, symbol: str = 'BTCUSDT') -> Dict:
        """Wrapper function for compatibility"""
        return self.calculate_rates_score(symbol)

# ============================================
# MODULE-LEVEL FUNCTIONS FOR IMPORT
# ============================================

_layer_instance = None

def _get_instance():
    """Get or create layer instance"""
    global _layer_instance
    if _layer_instance is None:
        _layer_instance = EnhancedRatesLayer()
    return _layer_instance

def get_rates_signal(symbol: str = 'BTCUSDT') -> Dict:
    """Main entry point for ai_brain"""
    return _get_instance().calculate_rates_score(symbol)

def get_interest_rates_signal(symbol: str = 'BTCUSDT') -> Dict:
    """Alternative function name for compatibility"""
    return _get_instance().calculate_rates_score(symbol)

def calculate_rates_score(symbol: str = 'BTCUSDT') -> Dict:
    """Direct score calculation"""
    return _get_instance().calculate_rates_score(symbol)

# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🏦 ENHANCED RATES LAYER v3 - REAL DATA TEST")
    print("="*70)
    
    layer = EnhancedRatesLayer()
    result = layer.calculate_rates_score("BTCUSDT")
    
    print("\n" + "="*70)
    print("📊 FINAL RESULT:")
    print(f" Score: {result['score']}/100 | Signal: {result['signal']}")
    print(f" 10Y Yield: {result['yield_10y']}%")
    print(f" Confidence: {result['confidence']:.0%}")
    print(f" Using Fallback: {result['using_fallback']}")
    print(f" Source: {result['source']}")
    print(f" Explanation: {result['explanation']}")
    print("="*70)
