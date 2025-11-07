# Enhanced Interest Rates Layer - Phase 6.5 MERGED & FIXED
# Date: 7 Kasım 2025
# Version: 2.5 - Senin kod + Benim bugfixes birleştirildi
#
# ✅ IMPROVEMENTS:
# - Timeout increased: 10s → 20s
# - Retry logic: 2 attempts with 2s delay
# - Fallback values: Realistic defaults instead of NULL
# - Better error handling
# - Always returns valid score (no NULL)
# ============================================================================

import requests
import time
from typing import Dict, Optional

class EnhancedRatesLayer:
    """Enhanced Interest Rates Layer with robust error handling"""
    
    def __init__(self):
        """Initialize with timeout and retry settings"""
        self.timeout = 20  # INCREASED from 10
        self.max_retries = 2  # NEW: Retry logic
        self.fallback_rate = 4.25  # NEW: Realistic fallback (avg US 10Y)
        print("✅ Enhanced Rates Layer v2.5 initialized (Timeout: 20s, Retries: 2)")
    
    def get_10y_treasury_yield(self) -> Optional[float]:
        """
        Get 10-Year US Treasury Yield with retry logic
        Returns: Float or None on failure
        """
        for attempt in range(self.max_retries):  # NEW: Retry loop
            try:
                print(f"  📡 Fetching 10Y Treasury Yield (Attempt {attempt+1}/{self.max_retries})...")
                
                url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ETNX"
                response = requests.get(
                    url, 
                    params={'interval': '1d', 'range': '5d'}, 
                    timeout=self.timeout  # INCREASED timeout
                )
                
                data = response.json()
                closes = [c for c in data['chart']['result'][0]['indicators']['quote'][0]['close'] if c]
                
                if closes:
                    yield_value = closes[-1]
                    print(f"     ✅ Got 10Y yield: {yield_value:.2f}%")
                    return yield_value
                else:
                    print(f"     ⚠️ No data in response")
                    if attempt < self.max_retries - 1:
                        time.sleep(2)
                        continue
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"     ⚠️ Timeout on attempt {attempt+1}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
                    continue
                return None
                
            except requests.exceptions.ConnectionError as e:
                print(f"     ⚠️ Connection error: {str(e)[:50]}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
                    continue
                return None
                
            except Exception as e:
                print(f"     ⚠️ Error: {str(e)[:50]}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
                    continue
                return None
        
        print(f"     ❌ All {self.max_retries} attempts failed")
        return None

    def calculate_rates_score(self, symbol: str = 'BTCUSDT') -> Dict:
        """
        Calculate interest rates score for crypto market
        
        Logic:
        - Lower rates (< 4.0%) = Bullish for crypto → Score 60+
        - Higher rates (> 5.0%) = Bearish for crypto → Score 40-
        - Medium rates = Neutral → Score 50
        
        Args:
            symbol: Trading pair (unused, for compatibility)
        
        Returns:
            Dict with score, signal, yield, confidence
        """
        print(f"\n📊 Calculating Rates Score...")
        
        # Get 10Y yield
        yield_10y = self.get_10y_treasury_yield()
        
        # NEW: Always use fallback if None
        if not yield_10y:
            print(f"     📌 Using fallback rate: {self.fallback_rate}%")
            yield_10y = self.fallback_rate
            using_fallback = True
        else:
            using_fallback = False
        
        # Calculate score based on yield level
        if yield_10y < 4.0:
            score = 60
            signal = 'LONG'
            explanation = "Low interest rates favor crypto (capital flows to risk assets)"
        elif yield_10y > 5.0:
            score = 40
            signal = 'SHORT'
            explanation = "High interest rates deter crypto (flight to safety)"
        else:
            score = 50
            signal = 'NEUTRAL'
            explanation = "Moderate interest rates - balanced crypto sentiment"
        
        # Calculate trend (how much rates changed recently)
        recent_trend = 0  # Can be enhanced with historical data
        
        # Confidence based on data freshness
        confidence = 0.8 if not using_fallback else 0.6
        
        result = {
            'score': score,
            'signal': signal,
            'explanation': explanation,
            'yield_10y': round(yield_10y, 2),
            'confidence': confidence,
            'using_fallback': using_fallback,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'available': True  # NEW: Always True now (fallback ensures this)
        }
        
        print(f"     📊 Score: {score}/100 | Signal: {signal}")
        print(f"     10Y Yield: {yield_10y:.2f}% | Confidence: {confidence:.0%}")
        
        return result

    def get_rates_signal(self, symbol: str = 'BTCUSDT') -> Dict:
        """
        Wrapper function for compatibility
        Returns: Same as calculate_rates_score
        """
        return self.calculate_rates_score(symbol)

# ============================================================================
# WRAPPER FUNCTIONS FOR AI_BRAIN COMPATIBILITY
# ============================================================================

def get_rates_signal(symbol: str = 'BTCUSDT') -> Dict:
    """
    Main entry point for ai_brain
    Usage: from layers.enhanced_rates_layer import get_rates_signal
    """
    layer = EnhancedRatesLayer()
    return layer.calculate_rates_score(symbol)

def get_interest_rates_signal(symbol: str = 'BTCUSDT') -> Dict:
    """Alternative function name for compatibility"""
    layer = EnhancedRatesLayer()
    return layer.calculate_rates_score(symbol)

# ============================================================================
# TEST & DEBUG
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🏦 ENHANCED INTEREST RATES LAYER v2.5 - TEST")
    print("=" * 70)
    
    layer = EnhancedRatesLayer()
    result = layer.calculate_rates_score("BTCUSDT")
    
    print("\n" + "=" * 70)
    print("📊 FINAL RESULT:")
    print(f"   Score: {result['score']}/100")
    print(f"   Signal: {result['signal']}")
    print(f"   10Y Yield: {result['yield_10y']}%")
    print(f"   Confidence: {result['confidence']:.0%}")
    print(f"   Available: {result['available']}")
    print(f"   Using Fallback: {result['using_fallback']}")
    print(f"   Explanation: {result['explanation']}")
    print("=" * 70)
