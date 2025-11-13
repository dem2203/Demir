"""
🔱 DEMIR AI - STREAMLIT v6 (SADECE GERÇEK VERİ - MOCK HAYIR!)
============================================================================
KRİTİK DÜZELTME:
- ❌ Mock/Fake değerler KALDIRILIYOR
- ❌ 72.5% başarı oranı KALDIRILIYOR (gerçek olmadığı için)
- ❌ 142 sinyal, +$2,450 kar KALDIRILIYOR (veri yok çünkü)
- ❌ Açık pozisyon örneği KALDIRILIYOR (veri yok çünkü)
- ✅ SADECE GERÇEK VERİ GÖSTERİLECEK
- ✅ Veri yok ise "Veri Yok" yazacak
- ✅ Varsayılan değer 50 KALDIRILIYOR

Date: 13 Kasım 2025
Version: 6.0 - GERÇEK VERİ ONLY, NO MOCK!
============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
import os
import sys
import traceback

# Backend
sys.path.insert(0, '/app')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BACKEND_AVAILABLE = False

try:
    if os.path.exists('/app/layers'):
        from layers.risk_management_layer import RiskManagementLayer
        from layers.atr_layer import ATRLayer
        from layers.enhanced_macro_layer import EnhancedMacroLayer
        BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"❌ Backend import hatası: {e}")
    BACKEND_AVAILABLE = False

st.set_page_config(page_title="🔱 DEMIR AI", page_icon="🔱", layout="wide")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    
    .header-main {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        padding: 30px; border-radius: 15px; color: white;
        margin-bottom: 20px; border-left: 5px solid #00ff88;
    }
    
    .header-main h1 {
        font-size: 2.5em; margin: 0; font-weight: 800;
        background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 20px; border-radius: 10px; border: 1px solid #00ff88;
        color: white; margin: 10px 0;
    }
    
    .stat-box {
        text-align: center; padding: 20px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 8px; border: 1px solid #00ff88;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# CACHE
# ============================================================================

@st.cache_resource
def load_backend_layers():
    """Backend yükle"""
    if not BACKEND_AVAILABLE:
        return None
    try:
        layers = {
            'risk': RiskManagementLayer(),
            'atr': ATRLayer(),
            'macro': EnhancedMacroLayer()
        }
        logger.info("✅ Backend layers yüklendi")
        return layers
    except Exception as e:
        logger.error(f"❌ Backend hatası: {e}")
        return None


# ============================================================================
# GERÇEK VERİ ÇEKME (MOCK HAYIR!)
# ============================================================================

def get_real_price(layers, symbol: str) -> tuple[float, bool]:
    """
    Binance API'dan gerçek fiyat çek
    Return: (fiyat, başarı)
    Eğer başarısızsa: (0, False) - MOCK DEĞİL!
    """
    try:
        if layers and 'risk' in layers:
            analysis = layers['risk'].analyze(symbol=symbol)
            price = float(analysis.get('entry_price', 0))
            if price > 0:
                logger.info(f"✅ {symbol} gerçek fiyat: ${price:.2f}")
                return price, True
        logger.warning(f"❌ {symbol} fiyat çekilemedi")
        return 0, False
    except Exception as e:
        logger.error(f"Fiyat hatası {symbol}: {e}")
        return 0, False


def get_real_atr(layers, symbol: str) -> tuple[float, bool]:
    """
    ATR çek
    Return: (atr, başarı)
    """
    try:
        if layers and 'atr' in layers:
            atr_value = layers['atr'].get_atr(symbol)
            if atr_value and atr_value > 0:
                logger.info(f"✅ {symbol} gerçek ATR: ${atr_value:.2f}")
                return float(atr_value), True
        logger.warning(f"❌ {symbol} ATR çekilemedi")
        return 0, False
    except Exception as e:
        logger.error(f"ATR hatası {symbol}: {e}")
        return 0, False


def get_macro_analysis(layers) -> tuple[dict, float, bool]:
    """
    Makro analiz çek
    Return: (data, score, başarı)
    Başarısızsa: (None, 0, False) - MOCK DEĞİL!
    """
    try:
        if layers and 'macro' in layers:
            macro_data = layers['macro'].analyze_macro_factors()
            if macro_data:
                score = layers['macro'].calculate_macro_score(macro_data)
                logger.info(f"✅ Makro analiz: {score:.1f}%")
                return macro_data, score, True
        logger.warning("❌ Makro veri çekilemedi")
        return None, 0, False
    except Exception as e:
        logger.error(f"Makro hatası: {e}")
        return None, 0, False


def calculate_levels(entry: float, atr: float) -> tuple[float, float, float, float]:
    """GERÇEK formüllerle hesapla"""
    if atr == 0 or entry == 0:
        return 0, 0, 0, 0
    
    sl = entry - (atr * 2)
    risk = entry - sl
    tp1 = entry + (risk * 1.8)
    tp2 = entry + (risk * 2.7)
    
    return entry, tp1, tp2, sl


# ============================================================================
# SAYFA 1: İŞLEM REHBERİ (SADECE GERÇEK VERİ!)
# ============================================================================

def page_trading_guide():
    """İşlem rehberi - MOCK VAR MI? HAYIR!"""
    
    st.markdown("""
        <div class="header-main">
            <h1>🔱 DEMIR AI - İŞLEM REHBERİ</h1>
            <p>Yapay Zeka - SADECE GERÇEK VERİ (Mock/Fake YOK!)</p>
        </div>
    """, unsafe_allow_html=True)
    
    layers = load_backend_layers()
    
    if not BACKEND_AVAILABLE or layers is None:
        st.error("❌ Backend bağlantısı yok!")
        st.info("Backend yüklenemediği için veri gösterilemiyor.")
        st.stop()
    
    st.subheader("🎯 AKTIF SİNYALLER")
    st.info("📡 Binance Futures API'dan GERÇEK veri çekiliyor...")
    
    # MAKRO VERİ
    with st.spinner("Makro veri çekiliyor..."):
        macro_data, macro_score, macro_success = get_macro_analysis(layers)
    
    if not macro_success:
        st.error("❌ MAKRO VERİ ÇEKİLEMEDİ - Sinyal üretilemiyor!")
        st.warning("Nedeni: FRED API bağlantısı yok veya rate limit")
        return
    
    st.success(f"""
    ✅ Makro Veri Başarılı:
    - 10Y Treasury: {macro_data.get('t10y', 'N/A'):.2f}%
    - Fed Rate: {macro_data.get('fedrate', 'N/A'):.2f}%
    - Skor: {macro_score:.1f}/100
    """)
    
    symbols = ["BTCUSDT", "ETHUSDT", "LTCUSDT"]
    
    for symbol in symbols:
        try:
            with st.spinner(f"📊 {symbol} çekiliyor..."):
                # ✅ GERÇEK FİYAT
                price, price_ok = get_real_price(layers, symbol)
                
                if not price_ok:
                    st.error(f"❌ {symbol} FİYAT ÇEKİLEMEDİ")
                    st.warning(f"Nedeni: Binance API bağlantısı yok veya rate limit")
                    st.divider()
                    continue
                
                # ✅ GERÇEK ATR
                atr_value, atr_ok = get_real_atr(layers, symbol)
                
                if not atr_ok:
                    st.error(f"❌ {symbol} ATR ÇEKİLEMEDİ")
                    st.warning(f"Nedeni: Historical data alınamıyor")
                    st.divider()
                    continue
                
                # ✅ GERÇEK LEVELS
                entry, tp1, tp2, sl = calculate_levels(price, atr_value)
                
                if entry == 0:
                    st.error(f"❌ {symbol} Levels hesaplanamadı")
                    st.divider()
                    continue
                
                # ✅ SİNYAL
                if macro_score >= 65:
                    signal_text = "🚀 ÇOOK GÜÇLÜ ALIM"
                    signal_color = "#00ff88"
                elif macro_score >= 50:
                    signal_text = "🟢 ALIM"
                    signal_color = "#00dd66"
                else:
                    signal_text = "🟡 BEKLE"
                    signal_color = "#ffcc00"
                
                # GÖSTER
                col1, col2, col3 = st.columns([2, 3, 2])
                
                with col1:
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                                    padding: 20px; border-radius: 10px; border-left: 5px solid {signal_color};
                                    color: white;">
                            <div style="font-size: 1.3em; font-weight: 700;">{symbol}</div>
                            <div style="font-size: 0.9em; opacity: 0.7;">Fiyat: ${price:,.2f}</div>
                            <div style="font-size: 2em; font-weight: 800; color: {signal_color}; margin: 10px 0;">
                                {signal_text}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    profit_tp1 = ((tp1 - entry) / entry) * 100
                    profit_tp2 = ((tp2 - entry) / entry) * 100
                    loss_sl = ((entry - sl) / entry) * 100
                    
                    st.markdown(f"""
                        <div class="metric-card">
                            <table style="width: 100%; font-size: 0.85em; color: white;">
                                <tr><td><b>GİRİŞ:</b></td><td style="text-align: right;">${entry:,.2f}</td></tr>
                                <tr><td><b>TP1:</b></td><td style="text-align: right; color: #00ff88;">
                                    ${tp1:,.2f} (+{profit_tp1:.2f}%)</td></tr>
                                <tr><td><b>TP2:</b></td><td style="text-align: right; color: #00ff88;">
                                    ${tp2:,.2f} (+{profit_tp2:.2f}%)</td></tr>
                                <tr><td><b>SL:</b></td><td style="text-align: right; color: #ff4444;">
                                    ${sl:,.2f}</td></tr>
                                <tr><td><b>RISK:</b></td><td style="text-align: right; color: #ff4444;">
                                    {loss_sl:.2f}%</td></tr>
                                <tr><td><b>ATR:</b></td><td style="text-align: right;">
                                    ${atr_value:,.2f}</td></tr>
                            </table>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    confidence_color = "#00ff88" if macro_score >= 80 else "#00dd66" if macro_score >= 70 else "#ffcc00"
                    
                    st.markdown(f"""
                        <div class="stat-box">
                            <div style="font-size: 0.8em; opacity: 0.7;">GÜVEN</div>
                            <div style="font-size: 2.5em; font-weight: 800; color: {confidence_color};">
                                {macro_score:.1f}%
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                                padding: 15px; border-radius: 8px; border-left: 3px solid {signal_color};
                                color: white; font-size: 0.85em; margin-top: 10px;">
                        <b>📊 HESAPLAMA (GERÇEK FORMÜLLER):</b><br/>
                        • ATR (14-günlük Binance): ${atr_value:,.2f}<br/>
                        • Entry = Güncel Fiyat: ${entry:,.2f}<br/>
                        • SL = Entry - (ATR × 2): ${sl:,.2f}<br/>
                        • TP1 = Entry + (Risk × 1.8): ${tp1:,.2f}<br/>
                        • Makro Skor (FRED API): {macro_score:.1f}/100
                    </div>
                """, unsafe_allow_html=True)
                
                st.divider()
        
        except Exception as e:
            st.error(f"❌ {symbol} hatası: {str(e)}")
            st.divider()


# ============================================================================
# SAYFA 2: PERFORMANS (SADECE GERÇEK İSTATİSTİK!)
# ============================================================================

def page_performance():
    """Performans - SADECE GERÇEK VERI VARSA GÖSTERİLİR!"""
    
    st.markdown("""
        <div class="header-main">
            <h1>📈 PERFORMANS & İSTATİSTİKLER</h1>
            <p>SADECE GERÇEK İSTATİSTİK</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.error("❌ UYARI: Performans verisi şu anda HAYIR!")
    st.warning("""
    Neden?
    - 72.5% başarı oranı: MOCK VERİ (kaldırıldı)
    - +$2,450 kar: MOCK VERİ (kaldırıldı)
    - 142 sinyal: MOCK VERİ (kaldırıldı)
    
    Gerçek performans verisine sahip olmak için:
    1. Gerçek trading history database'i gerekli
    2. Gerçek açık/kapalı pozisyonlar gerekli
    3. Gerçek P&L hesaplaması gerekli
    
    ❌ HİÇBİRİ ŞU ANDA YOK - MOCK İLE DEĞİL DOLDURULSUN!
    """)
    
    st.info("""
    Ne yapacak?
    ✅ PostgreSQL/MySQL database oluştur
    ✅ Tüm trading history kaydet
    ✅ P&L hesapla ve veritabanına kaydet
    ✅ O zaman gerçek performans gösterilsin
    """)


# ============================================================================
# SAYFA 3: POZİSYON TAKIBI
# ============================================================================

def page_position_tracking():
    """Pozisyon takibi - SADECE GERÇEK POZISYONLAR!"""
    
    st.markdown("""
        <div class="header-main">
            <h1>📍 POZİSYON TAKIBI (7/24 CANLI)</h1>
            <p>SADECE GERÇEK AÇIK POZİSYONLAR GÖSTERİLİR</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.error("❌ UYARI: Pozisyon verisi şu anda HAYIR!")
    st.warning("""
    Ne görmek istiyorsun?
    - BTCUSDT: $42,800'de girmiş, +$225 kar → MOCK (kaldırıldı)
    - ETHUSDT: $2,450'de girmiş, +$30 kar → MOCK (kaldırıldı)
    
    Gerçek pozisyonlar için:
    1. Binance Futures API'ya bağlan
    2. Açık pozisyonları çek: client.futures_position_information()
    3. Her pozisyon için gerçek P&L hesapla
    4. Veritabanına kaydet
    
    ❌ ŞU ANDA KODU YOK - MOCK İLE DEĞİL DOLDURULSUN!
    """)


# ============================================================================
# SAYFA 4: AYARLAR
# ============================================================================

def page_settings():
    """Ayarlar"""
    
    st.markdown("""
        <div class="header-main">
            <h1>⚙️ AYARLAR & KONFİGÜRASYON</h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("API Bağlantı Durumu (GERÇEK)")
    
    layers = load_backend_layers()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = "🟢 BAĞLI" if BACKEND_AVAILABLE and layers else "🔴 BAĞLI DEĞİL"
        st.metric("Backend", status)
    
    with col2:
        if layers:
            price, ok = get_real_price(layers, "BTCUSDT")
            status = "🟢 BAĞLI" if ok else "🔴 HATA"
        else:
            status = "🔴 BAĞLI DEĞİL"
        st.metric("Binance API", status)
    
    with col3:
        if layers:
            atr, ok = get_real_atr(layers, "BTCUSDT")
            status = "🟢 ÇALIŞIYOR" if ok else "🔴 HATA"
        else:
            status = "🔴 BAĞLI DEĞİL"
        st.metric("ATR Layer", status)
    
    with col4:
        if layers:
            _, _, ok = get_macro_analysis(layers)
            status = "🟢 ÇALIŞIYOR" if ok else "🔴 HATA"
        else:
            status = "🔴 BAĞLI DEĞİL"
        st.metric("Macro Layer", status)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main"""
    
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 2.5em;">🔱</div>
                <div style="font-size: 1.2em; font-weight: 700;">DEMIR AI</div>
                <div style="font-size: 0.9em; opacity: 0.7;">v6.0 - SADECE GERÇEK VERİ</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        page = st.radio("MENU", [
            "🎯 İşlem Rehberi",
            "📈 Performans",
            "📍 Pozisyon Takibi",
            "⚙️ Ayarlar"
        ])
    
    if page == "🎯 İşlem Rehberi":
        page_trading_guide()
    elif page == "📈 Performans":
        page_performance()
    elif page == "📍 Pozisyon Takibi":
        page_position_tracking()
    elif page == "⚙️ Ayarlar":
        page_settings()
    
    st.markdown("---")
    st.markdown(f"""
        <div style="text-align: center; opacity: 0.6; font-size: 0.85em;">
            🔱 DEMIR AI v6.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')} CET<br/>
            ✅ SADECE GERÇEK VERİ - MOCK HAYIR! | Backend: {'ENTEGRE' if BACKEND_AVAILABLE else 'YOK'}
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
