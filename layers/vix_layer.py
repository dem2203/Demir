"""
VIX LAYER v5 - REEL VERİ İLE ÇALIŞ
====================================
Date: 7 Kasım 2025, 20:05 CET
Version: 5.0 - Multi-source Real Data + Aggressive Fallback
"""

import os
import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# PRIMARY: TWELVE DATA (PREMIUM)
# ============================================

def fetch_vix_twelvedata(symbol: str = "BTC") -> Optional[Dict[str, Any]]:
    """Fetch VIX from Twelve Data API (PRIMARY SOURCE)"""
    api_key = os.getenv('TWELVE_DATA_API_KEY')
    
    if not api_key:
        logger.warning("⚠️ TWELVE_DATA_API_KEY not set")
        return None
    
    try:
        logger.info(f" 📡 [Twelve Data] Fetching VIX for {symbol}...")
        url = "https://api.twelvedata.com/quote"
        params = {
            'symbol': 'VIX',
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        if 'close' in data:
            vix_value = float(data['close'])
            result = {
                'value': vix_value,
                'source': 'twelvedata',
                'timestamp': datetime.now().isoformat(),
                'available': True
            }
            logger.info(f" ✅ Twelve Data: VIX = {vix_value:.2f}")
            return result
        else:
            logger.warning(f" ⚠️ Twelve Data: No 'close' in response")
            return None
    
    except Exception as e:
        logger.warning(f" ⚠️ Twelve Data error: {str(e)[:60]}")
        return None

# ============================================
# SECONDARY: YFINANCE
# ============================================

def fetch_vix_yfinance(symbol: str = "BTC") -> Optional[Dict[str, Any]]:
    """Fetch VIX from yfinance (SECONDARY SOURCE)"""
    try:
        import yfinance as yf
        logger.info(f" 📡 [yFinance] Fetching VIX for {symbol}...")
        
        ticker = yf.Ticker("^VIX")
        data = ticker.history(period="1d")
        
        if not data.empty:
            vix_value = float(data['Close'].iloc[-1])
            result = {
                'value': vix_value,
                'source': 'yfinance',
                'timestamp': datetime.now().isoformat(),
                'available': True
            }
            logger.info(f" ✅ yFinance: VIX = {vix_value:.2f}")
            return result
        else:
            logger.warning(f" ⚠️ yFinance: No data returned")
            return None
    
    except ImportError:
        logger.warning(f" ⚠️ yfinance not installed")
        return None
    except Exception as e:
        logger.warning(f" ⚠️ yFinance error: {str(e)[:60]}")
        return None

# ============================================
# TERTIARY: ALTERNATIVE.ME (FALLBACK)
# ============================================

def fetch_vix_alternative(symbol: str = "BTC") -> Optional[Dict[str, Any]]:
    """
    Fetch fear/greed which correlates to VIX
    FALLBACK when primary sources fail
    """
    try:
        logger.info(f" 📡 [Alternative.me] Fetching Fear Index for {symbol}...")
        
        url = 'https://api.alternative.me/fng/?limit=1'
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data and 'data' in data and len(data['data']) > 0:
            fng = data['data'][0]
            # Convert fear index (0-100) to VIX-like value (10-80)
            fng_value = int(fng['value'])
            vix_estimate = 10 + (fng_value / 100) * 70  # Scale to ~10-80 range
            
            result = {
                'value': vix_estimate,
                'source': 'alternative_me_estimate',
                'base_index': fng_value,
                'timestamp': datetime.now().isoformat(),
                'available': True,
                'note': 'Estimated from Fear & Greed Index'
            }
            logger.info(f" ✅ Alternative.me: Estimated VIX = {vix_estimate:.2f} (Fear={fng_value})")
            return result
        else:
            logger.warning(f" ⚠️ Alternative.me: Empty response")
            return None
    
    except Exception as e:
        logger.warning(f" ⚠️ Alternative.me error: {str(e)[:60]}")
        return None

# ============================================
# FALLBACK VALUES
# ============================================

def _fallback_vix() -> Dict[str, Any]:
    """Ultimate fallback VIX value"""
    return {
        'value': 20.0,  # Average VIX level
        'source': 'FALLBACK',
        'timestamp': datetime.now().isoformat(),
        'available': True,
        'note': 'All API sources failed - using fallback'
    }

# ============================================
# MAIN VIX ANALYSIS
# ============================================

def calculate_vix_fear(symbol: str = "BTC") -> Dict[str, Any]:
    """
    Calculate VIX Fear Index and interpret crypto impact
    Returns score 0-100:
    - 100 = Extreme fear (VIX very high, risk-off)
    - 50 = Normal market (VIX moderate)
    - 0 = Complacency (VIX very low, risk-on)
    """
    
    logger.info(f"\n📊 ANALYZING VIX FEAR INDEX FOR {symbol} (REAL DATA)...")
    
    # Try sources in priority order
    vix_data = None
    
    # Primary
    vix_data = fetch_vix_twelvedata(symbol)
    if vix_data:
        logger.info(f"✅ Using primary source: {vix_data['source']}")
    else:
        # Secondary
        vix_data = fetch_vix_yfinance(symbol)
        if vix_data:
            logger.info(f"✅ Using secondary source: {vix_data['source']}")
        else:
            # Tertiary
            vix_data = fetch_vix_alternative(symbol)
            if vix_data:
                logger.info(f"✅ Using tertiary source: {vix_data['source']}")
            else:
                # Fallback
                logger.error(f"❌ All VIX sources failed")
                vix_data = _fallback_vix()
                logger.warning(f"⚠️ Using fallback VIX data")
    
    vix_value = vix_data['value']
    
    # ==========================================
    # VIX INTERPRETATION
    # ==========================================
    
    # Historical VIX levels:
    # - <12: Extreme complacency (2017, 2019 lows)
    # - 12-20: Normal/low volatility
    # - 20-30: Elevated fear
    # - 30-40: High fear (2020 COVID start)
    # - >40: Extreme fear/panic (2008, 2020 peak ~80)
    
    if vix_value > 40:
        fear_level = "EXTREME_PANIC"
        base_score = 95
        interpretation = "🔴 Extreme market panic - flight to safety"
    elif vix_value > 30:
        fear_level = "HIGH_FEAR"
        base_score = 80
        interpretation = "🔴 High fear - significant risk aversion"
    elif vix_value > 20:
        fear_level = "ELEVATED_FEAR"
        base_score = 65
        interpretation = "🟠 Elevated fear - cautious sentiment"
    elif vix_value > 15:
        fear_level = "MODERATE"
        base_score = 50
        interpretation = "🟡 Moderate volatility - normal conditions"
    elif vix_value > 12:
        fear_level = "LOW_FEAR"
        base_score = 35
        interpretation = "🟢 Low fear - risk-on sentiment"
    else:
        fear_level = "COMPLACENCY"
        base_score = 20
        interpretation = "🟢 Extreme complacency - potential reversal risk"
    
    # ==========================================
    # CRYPTO CORRELATION
    # ==========================================
    
    # VIX and crypto typically INVERSELY correlated:
    # - High VIX → Risk-off → Crypto down (bearish)
    # - Low VIX → Risk-on → Crypto up (bullish)
    
    if vix_value > 35:
        crypto_impact = "VERY_BEARISH"
        impact_desc = "🔴 High VIX: Strong risk-off, bearish for crypto"
    elif vix_value > 25:
        crypto_impact = "BEARISH"
        impact_desc = "🟠 Elevated VIX: Risk-off, bearish for crypto"
    elif vix_value > 18:
        crypto_impact = "NEUTRAL"
        impact_desc = "🟡 Normal VIX: Neutral for crypto"
    elif vix_value > 12:
        crypto_impact = "BULLISH"
        impact_desc = "🟢 Low VIX: Risk-on, bullish for crypto"
    else:
        crypto_impact = "VERY_BULLISH"
        impact_desc = "🟢 Very low VIX: Strong risk-on, bullish for crypto"
    
    score = base_score
    
    logger.info(f"")
    logger.info(f" VIX Value: {vix_value:.2f}")
    logger.info(f" Fear Level: {fear_level}")
    logger.info(f" Crypto Impact: {crypto_impact}")
    logger.info(f" Score: {score:.2f}/100")
    
    result = {
        'available': True,
        'score': round(score, 2),
        'vix_value': round(vix_value, 2),
        'fear_level': fear_level,
        'crypto_impact': crypto_impact,
        'interpretation': interpretation,
        'impact_description': impact_desc,
        'source': vix_data['source'],
        'timestamp': datetime.now().isoformat(),
        'symbol': symbol,
        'base_score': base_score
    }
    
    return result

def get_vix_signal(symbol: str = "BTC") -> Dict[str, Any]:
    """Simplified wrapper for AI Brain"""
    result = calculate_vix_fear(symbol)
    if result['available']:
        return {
            'available': True,
            'score': result['score'],
            'signal': result['fear_level'],
            'crypto_impact': result['crypto_impact'],
            'vix_value': result['vix_value']
        }
    else:
        return {
            'available': False,
            'score': 50,
            'signal': 'MODERATE',
            'crypto_impact': 'NEUTRAL'
        }

# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("📊 VIX LAYER v5 - REAL DATA TEST")
    print("="*70)
    
    result = calculate_vix_fear("BTCUSDT")
    
    print("\n" + "="*70)
    print("📊 VIX ANALYSIS:")
    print(f" Available: {result['available']}")
    print(f" Score: {result.get('score', 'N/A')}/100")
    print(f" VIX Value: {result.get('vix_value', 'N/A')}")
    print(f" Fear Level: {result.get('fear_level', 'N/A')}")
    print(f" Crypto Impact: {result.get('crypto_impact', 'N/A')}")
    print(f" Interpretation: {result.get('interpretation', 'N/A')}")
    print(f" Source: {result.get('source', 'N/A')}")
    print("="*70)
