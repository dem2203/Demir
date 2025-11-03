# ===========================================
# vix_layer.py v4.1 - SYNTAX ERROR FIXED
# ===========================================
# ✅ Line 210 syntax error fixed: print(f( → print(f"
# ✅ api_cache_manager entegrasyonu
# ✅ Multi-source fallback (Twelve Data → yfinance)
# ✅ 15 dakika cache
# ✅ Graceful degradation
# ===========================================

"""
🔱 DEMIR AI TRADING BOT - VIX Layer v4.1 (SYNTAX FIXED!)
====================================================================
Tarih: 3 Kasım 2025, 22:45 CET
Versiyon: 4.1 - SYNTAX ERROR FIXED

✅ YENİ v4.1:
------------
✅ Line 210 fixed: print(f( → print(f"
✅ Parantez hatası düzeltildi

YENİ v4.0:
----------
✅ api_cache_manager entegrasyonu
✅ Multi-source (Twelve Data → yfinance)
✅ 15 dakika cache (rate limit koruması)
✅ Health monitoring
✅ Fallback chain
"""

import os
import requests
from datetime import datetime
from typing import Dict, Any

# API Cache Manager import (YENİ!)
try:
    from api_cache_manager import fetch_market_data, fetch_quick_price
    CACHE_MANAGER_AVAILABLE = True
except ImportError:
    CACHE_MANAGER_AVAILABLE = False
    print("⚠️ api_cache_manager bulunamadı - direct API kullanılacak")

# ============================================================================
# VIX FEAR INDEX ANALİZİ (RATE LIMIT SAFE!)
# ============================================================================

def analyze_vix() -> Dict[str, Any]:
    """
    VIX Fear Index analizi (RATE LIMIT SAFE!)
    
    KAYNAK ÖNCELİĞİ:
    1. Twelve Data API (with cache)
    2. yfinance fallback
    
    Returns:
        dict: {
            'success': bool,
            'vix_current': float,
            'vix_level': str ('EXTREME_FEAR', 'FEAR', 'NEUTRAL', 'GREED'),
            'score': float (0-100),
            'signal': str,
            'interpretation': str,
            'data_source': str
        }
    """
    print(f"\n{'='*80}")
    print(f"😱 VIX FEAR INDEX ANALYSIS")
    print(f"{'='*80}\n")
    
    # Cache Manager kullanalım!
    if CACHE_MANAGER_AVAILABLE:
        try:
            # Twelve Data → yfinance chain
            result = fetch_market_data(
                symbol='^VIX',
                source_priority=['twelve_data', 'yfinance'],
                days=1
            )
            
            if result['success'] and result['price'] > 0:
                vix_current = result['price']
                data_source = result['source']
                
                print(f"✅ VIX verisi çekildi: {vix_current:.2f}")
                print(f"📊 Kaynak: {data_source}")
                
                # VIX seviye analizi
                if vix_current < 12:
                    vix_level = "EXTREME_GREED"
                    score = 70
                    signal = "BULLISH"
                    interp = f"VIX çok düşük ({vix_current:.1f}) - aşırı iyimserlik, düzeltme riski"
                elif vix_current < 20:
                    vix_level = "GREED"
                    score = 60
                    signal = "BULLISH"
                    interp = f"VIX normal ({vix_current:.1f}) - sağlıklı piyasa"
                elif vix_current < 30:
                    vix_level = "FEAR"
                    score = 40
                    signal = "NEUTRAL"
                    interp = f"VIX yükseldi ({vix_current:.1f}) - artan belirsizlik"
                else:
                    vix_level = "EXTREME_FEAR"
                    score = 20
                    signal = "BEARISH"
                    interp = f"VIX çok yüksek ({vix_current:.1f}) - panik, alım fırsatı?"
                
                print(f"\n{'='*80}")
                print(f"✅ VIX ANALYSIS COMPLETE!")
                print(f"   Level: {vix_level}")
                print(f"   Score: {score}/100")
                print(f"   Signal: {signal}")
                print(f"{'='*80}\n")
                
                return {
                    'success': True,
                    'available': True,
                    'vix_current': vix_current,
                    'vix_level': vix_level,
                    'score': score,
                    'signal': signal,
                    'interpretation': interp,
                    'data_source': data_source,
                    'timestamp': datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"⚠️ Cache Manager VIX hatası: {e}")
    
    # Fallback: Direct yfinance (cache yok)
    try:
        import yfinance as yf
        
        vix_ticker = yf.Ticker("^VIX")
        vix_hist = vix_ticker.history(period="1d")
        
        if not vix_hist.empty:
            vix_current = float(vix_hist['Close'].iloc[-1])
            print(f"✅ VIX verisi (yfinance direct): {vix_current:.2f}")
            
            if vix_current < 12:
                vix_level = "EXTREME_GREED"
                score = 70
                signal = "BULLISH"
            elif vix_current < 20:
                vix_level = "GREED"
                score = 60
                signal = "BULLISH"
            elif vix_current < 30:
                vix_level = "FEAR"
                score = 40
                signal = "NEUTRAL"
            else:
                vix_level = "EXTREME_FEAR"
                score = 20
                signal = "BEARISH"
            
            return {
                'success': True,
                'available': True,
                'vix_current': vix_current,
                'vix_level': vix_level,
                'score': score,
                'signal': signal,
                'interpretation': f"VIX: {vix_current:.1f} - {vix_level}",
                'data_source': 'yfinance (direct)',
                'timestamp': datetime.now().isoformat()
            }
    
    except Exception as e:
        print(f"⚠️ yfinance direct VIX hatası: {e}")
    
    # Tüm kaynaklar başarısız - neutral fallback
    print("⚠️ VIX data unavailable - using neutral score")
    
    return {
        'success': True,
        'available': False,
        'vix_current': 0,
        'vix_level': 'UNKNOWN',
        'score': 50,
        'signal': 'NEUTRAL',
        'interpretation': 'VIX verisi alınamadı - neutral skor kullanıldı',
        'data_source': 'FALLBACK',
        'timestamp': datetime.now().isoformat()
    }


# ============================================================================
# LEGACY FONKSİYON (GERİYE UYUMLULUK)
# ============================================================================

def get_vix_signal() -> Dict[str, Any]:
    """
    Legacy wrapper - analyze_vix() ile aynı
    """
    return analyze_vix()


# ============================================================================
# TEST
# ============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 VIX LAYER v4.1 - SYNTAX FIXED TEST!")
    print("=" * 80)
    print()
    
    result = analyze_vix()
    
    print("\n📊 SONUÇ:")
    print(f"   ✅ Başarılı: {result['success']}")
    print(f"   ✅ VIX: {result.get('vix_current', 0):.2f}")
    print(f"   ✅ Level: {result.get('vix_level', 'UNKNOWN')}")  # ✅ FIXED: print(f" → print(f"
    print(f"   ✅ Score: {result.get('score', 0)}/100")
    print(f"   ✅ Signal: {result.get('signal', 'UNKNOWN')}")
    print(f"   ✅ Source: {result.get('data_source', 'UNKNOWN')}")
    print("=" * 80)
