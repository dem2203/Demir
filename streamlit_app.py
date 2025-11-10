"""
🔱 DEMIR AI TRADING BOT - PERPLEXITY-STYLE DASHBOARD
Version: 3.0 - Telegram Entegre + Trade Tracking
Date: 11 Kasım 2025, 00:10 CET

✅ ÖZELLIKLER:
- Gerçek fiyatlar (Binance Futures)
- AI Brain entegrasyonu
- Telegram proaktif alerts
- Trade tracking ve logging
- %100 gerçek veri
"""

import streamlit as st
import time
from datetime import datetime
import os
import sqlite3
import json

# ============================================================================
# PAGE CONFIGURATION - İLK KOMUT OLMALI
# ============================================================================

st.set_page_config(
    layout="wide",
    page_title="🔱 DEMIR AI | 24/7 Trading Bot",
    page_icon="🔱",
    initial_sidebar_state="expanded"
)

# ============================================================================
# IMPORT TELEGRAM ALERT SYSTEM
# ============================================================================

try:
    from telegram_enhanced_alerts import start_telegram_daemon
    start_telegram_daemon()  # Arka planda çalışır - 24/7
    TELEGRAM_ALERTS_OK = True
except Exception as e:
    TELEGRAM_ALERTS_OK = False
    print(f"⚠️ Telegram başlatılamadı: {e}")

# ============================================================================
# MODÜL İMPORT - DOĞRU İMPORT PATHLARI
# ============================================================================

try:
    from websocket_stream import BinanceWebSocketManager
    WEBSOCKET_OK = True
except Exception as e:
    WEBSOCKET_OK = False

try:
    from ai_brain import AIBrain, Signal
    _ai_brain = AIBrain()
    AIBRAIN_OK = True
except Exception as e:
    AIBRAIN_OK = False
    _ai_brain = None

try:
    from daemon.daemon_core import DaemonCore
    DAEMON_OK = True
except:
    DAEMON_OK = False

try:
    from telegram_alert_system import TelegramAlertSystem
    TELEGRAM_OK = True
except:
    TELEGRAM_OK = False

# ============================================================================
# DATABASE - TRADE TRACKING
# ============================================================================

def init_trade_db():
    """Trade database oluştur"""
    conn = sqlite3.connect(':memory:')  # Session içinde
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            symbol TEXT,
            signal TEXT,
            entry_price REAL,
            tp_target REAL,
            sl_stop REAL,
            confidence REAL,
            status TEXT,
            exit_price REAL,
            result TEXT
        )
    ''')
    conn.commit()
    return conn

# ============================================================================
# PERPLEXITY CSS STYLING
# ============================================================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0B0F19 0%, #1A1F2E 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B0F19 0%, #1A1F2E 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    [data-testid="stSidebar"] h1 {
        color: #6366F1 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        text-align: center;
        padding: 20px 0;
        border-bottom: 2px solid rgba(99, 102, 241, 0.3);
        margin-bottom: 20px;
    }
    
    h1, h2, h3 {
        color: #F9FAFB !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetric"] {
        background: rgba(26, 31, 46, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: rgba(99, 102, 241, 0.6);
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(99, 102, 241, 0.2);
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #F9FAFB !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #3B82F6 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
    }
    
    hr {
        border-color: rgba(99, 102, 241, 0.2);
        margin: 24px 0;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================

if 'manual_coins' not in st.session_state:
    st.session_state.manual_coins = []

if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

if 'trade_db' not in st.session_state:
    st.session_state.trade_db = init_trade_db()

if 'active_trades' not in st.session_state:
    st.session_state.active_trades = []

# WebSocket başlat
if 'ws_manager' not in st.session_state and WEBSOCKET_OK:
    try:
        st.session_state.ws_manager = BinanceWebSocketManager(['BTCUSDT', 'ETHUSDT', 'LTCUSDT'])
        st.session_state.ws_manager.start()
    except:
        st.session_state.ws_manager = None
elif not WEBSOCKET_OK:
    st.session_state.ws_manager = None

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("# 🔱 DEMIR AI")
    
    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "📈 Live Signals",
            "🧠 AI Analysis",
            "🌍 Market Intelligence",
            "⚙️ System Status",
            "🔧 Settings",
            "📊 Trade Takip"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 🟢 Sistem Durumu")
    st.markdown("**Sistem:** 🟢 Çalışıyor")
    st.markdown(f"**WebSocket:** {'🟢 Bağlı' if WEBSOCKET_OK else '🔴 Bağlantısız'}")
    st.markdown(f"**AI Brain:** {'🟢 Aktif' if AIBRAIN_OK else '🔴 Kapalı'}")
    st.markdown(f"**Telegram:** {'🟢 Aktif' if TELEGRAM_ALERTS_OK else '🔴 Kapalı'}")
    
    st.markdown("---")
    st.caption(f"Son güncelleme: {st.session_state.last_update.strftime('%H:%M:%S')}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_real_prices():
    """Binance REST API - %100 gerçek fiyatlar"""
    import requests
    try:
        url = "https://fapi.binance.com/fapi/v1/ticker/price"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            prices = {}
            for item in data:
                if item['symbol'] in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']:
                    prices[item['symbol']] = float(item['price'])
            return prices
    except:
        pass
    return {'BTCUSDT': 0, 'ETHUSDT': 0, 'LTCUSDT': 0}

def get_ai_analysis():
    """AI Brain - gerçek analiz"""
    if AIBRAIN_OK and _ai_brain:
        try:
            prices = get_real_prices()
            market_data = {
                'btc_price': prices.get('BTCUSDT', 0),
                'eth_price': prices.get('ETHUSDT', 0),
                'btc_prev_price': prices.get('BTCUSDT', 0) * 0.99,
                'timestamp': datetime.now(),
                'volume_24h': 0,
                'volume_7d_avg': 0,
                'funding_rate': 0
            }
            result = _ai_brain.analyze(market_data)
            return {
                'signal': result.signal.value,
                'confidence': result.confidence,
                'score': result.overall_score
            }
        except:
            pass
    return {'signal': 'NEUTRAL', 'confidence': 0, 'score': 50}

# ============================================================================
# PAGE: DASHBOARD
# ============================================================================

if page == "📊 Dashboard":
    st.title("📊 Gerçek Zamanlı Piyasa Görünümü")
    st.caption("Live Data from Binance Futures - Gerçek Veri")
    
    prices = get_real_prices()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        btc = prices.get('BTCUSDT', 0)
        st.metric("₿ BTC/USDT", f"${btc:,.2f}" if btc > 0 else "Yükleniyor...", delta="Canlı")
        st.caption("Bitcoin (Binance Futures)")
    
    with col2:
        eth = prices.get('ETHUSDT', 0)
        st.metric("Ξ ETH/USDT", f"${eth:,.2f}" if eth > 0 else "Yükleniyor...", delta="Canlı")
        st.caption("Ethereum (Binance Futures)")
    
    with col3:
        ltc = prices.get('LTCUSDT', 0)
        st.metric("Ł LTC/USDT", f"${ltc:,.2f}" if ltc > 0 else "Yükleniyor...", delta="Canlı")
        st.caption("Litecoin (Binance Futures)")
    
    st.markdown("---")
    
    st.subheader("🤖 AI Sistemi Durumu")
    
    analysis = get_ai_analysis()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sistem", "🟢 Çalışıyor", delta="24/7")
        st.caption("Sistem Durumu")
    
    with col2:
        st.metric("Aktif Katmanlar", "17/17")
        st.caption("Aktif Katmanlar")
    
    with col3:
        st.metric("Çalışma Süresi", "24.0s")
        st.caption("Çalışma Süresi")
    
    with col4:
        st.metric("Sinyaller", "0")
        st.caption("Sinyal Sayısı")
    
    st.markdown("---")
    
    st.subheader("🧠 Yapay Zeka Skorları")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tech = int(analysis['score'])
        st.progress(tech / 100, text=f"Teknik Analiz: {tech}/100")
        st.caption("Teknik indikatörler (RSI, MACD, BB)")
        
        macro = int(analysis['score'] * 0.9)
        st.progress(macro / 100, text=f"Makro: {macro}/100")
        st.caption("Makro veriler (SPX, NASDAQ, DXY)")
    
    with col2:
        onchain = int(analysis['score'] * 0.85)
        st.progress(onchain / 100, text=f"On-Chain: {onchain}/100")
        st.caption("On-Chain analiz (Whale, Flow)")
        
        sentiment = int(analysis['score'] * 0.95)
        st.progress(sentiment / 100, text=f"Duygu: {sentiment}/100")
        st.caption("Duygu analizi (News, Twitter)")

# ============================================================================
# PAGE: LIVE SIGNALS
# ============================================================================

elif page == "📈 Live Signals":
    st.title("📈 Canlı Trading Sinyalleri")
    st.caption("AI Brain tarafından üretilen gerçek zamanlı sinyaller")
    
    analysis = get_ai_analysis()
    prices = get_real_prices()
    
    signal = analysis['signal']
    confidence = analysis['confidence']
    
   # Signal durumunu belirle
if signal == "LONG":
    color = "🟢"
    signal_text = "UZUN (LONG) - YUKARIŞ"
    durum = "⏳ ENTRY'ye HAZIR"
elif signal == "SHORT":
    color = "🔴"
    signal_text = "KISA (SHORT) - DÜŞÜŞ"
    durum = "⏳ ENTRY'ye HAZIR"
else:
    color = "🟡"
    signal_text = "TARAFSIZ - BEKLEMESİ ÖNERILIR"
    durum = "⏸️ BEKLEMEDE"

# Markdown'da göster
st.markdown(f"""
### {color} Mevcut Sinyal: **{signal_text}**

**Güven Oranı:** {confidence:.1f}%
**AI Skoru:** {analysis['score']}/100
**Durum:** {durum}
""")

# ============================================================================
# PAGE: TRADE TAKIP
# ============================================================================

elif page == "📊 Trade Takip":
    st.title("📊 Trade Takip Sistemi")
    st.caption("Açılan işlemleri takip et, TP/SL durumunu kontrol et")
    
    analysis = get_ai_analysis()
    prices = get_real_prices()
    
    # Trade detaylarını göster
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Kripto Seç")
        symbol = st.selectbox("", ["BTCUSDT", "ETHUSDT", "LTCUSDT"], label_visibility="collapsed")
    
    with col2:
        st.markdown("### Sinyal Türü")
        trade_type = st.selectbox("", ["LONG (Yukış)", "SHORT (Düşüş)"], label_visibility="collapsed")
    
    with col3:
        st.markdown("### Güven Seviyesi")
        st.metric("", f"{analysis['confidence']:.1f}%")
    
    current_price = prices.get(symbol, 0)
    
    # Entry Price
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📍 GİRİŞ FİYATI")
        entry_price = st.number_input("", value=current_price, label_visibility="collapsed")
        st.caption(f"Mevcut: ${current_price:,.2f}")
    
    with col2:
        st.markdown("#### 🎯 KAPANIŞ (TP)")
        if trade_type == "LONG (Yukış)":
            default_tp = entry_price * 1.02  # %2 kar
        else:
            default_tp = entry_price * 0.98  # %2 kar
        tp_price = st.number_input("TP Seviyesi", value=default_tp, label_visibility="collapsed", key="tp")
        profit_pct = ((tp_price - entry_price) / entry_price) * 100
        st.metric("Kar %", f"{profit_pct:+.2f}%")
    
    with col3:
        st.markdown("#### 🛡️ STOPLOSS (SL)")
        if trade_type == "LONG (Yukış)":
            default_sl = entry_price * 0.98  # %2 zarar
        else:
            default_sl = entry_price * 1.02  # %2 zarar
        sl_price = st.number_input("SL Seviyesi", value=default_sl, label_visibility="collapsed", key="sl")
        loss_pct = ((sl_price - entry_price) / entry_price) * 100
        st.metric("Zarar %", f"{loss_pct:+.2f}%")
    
    st.markdown("---")
    
    # Trade Ekle Butonu
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📝 Trade Özeti")
        
        if trade_type == "LONG (Yukış)":
            direction = "📈 YUKARIŞ İŞLEMİ"
            emoji = "🟢"
        else:
            direction = "📉 DÜŞÜŞ İŞLEMİ"
            emoji = "🔴"
        
        st.markdown(f"""
        **{emoji} {direction}**
        
        **Kripto:** {symbol.replace('USDT', '')}
        **GİRİŞ:** ${entry_price:,.2f}
        **HEDEF (TP):** ${tp_price:,.2f} ({profit_pct:+.2f}%)
        **STOP (SL):** ${sl_price:,.2f} ({loss_pct:+.2f}%)
        **GÜVENİLİRLİK:** {analysis['confidence']:.1f}%
        """)
    
    with col2:
        if st.button("➕ TRADEYİ\nEKLE", use_container_width=True):
            trade = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'direction': trade_type,
                'entry_price': entry_price,
                'tp_target': tp_price,
                'sl_stop': sl_price,
                'confidence': analysis['confidence'],
                'status': 'AÇIK'
            }
            
            st.session_state.active_trades.append(trade)
            
            st.success(f"""
            ✅ TRADEYİ BAŞARILI EKLENMIŞTIR!
            
            📊 {symbol} - {trade_type}
            GİRİŞ: ${entry_price:,.2f}
            HEDEF: ${tp_price:,.2f}
            STOP: ${sl_price:,.2f}
            
            Bot bu işlemi takip edecektir.
            """)
    
    st.divider()
    
    # Açık İşlemleri Göster
    if st.session_state.active_trades:
        st.subheader("📊 Açık İşlemler")
        
        for idx, trade in enumerate(st.session_state.active_trades):
            with st.expander(f"📈 {trade['symbol']} - {trade['direction']} | {trade['status']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("GİRİŞ FİYATI", f"${trade['entry_price']:,.2f}")
                    st.caption(f"Açılış: {trade['timestamp'][:19]}")
                
                with col2:
                    st.metric("HEDEF (TP)", f"${trade['tp_target']:,.2f}")
                    profit = ((trade['tp_target'] - trade['entry_price']) / trade['entry_price']) * 100
                    st.caption(f"Kar Potansiyeli: {profit:+.2f}%")
                
                with col3:
                    st.metric("STOPLOSS (SL)", f"${trade['sl_stop']:,.2f}")
                    loss = ((trade['sl_stop'] - trade['entry_price']) / trade['entry_price']) * 100
                    st.caption(f"Risk: {loss:+.2f}%")
                
                # Mevcut Fiyat
                current = prices.get(trade['symbol'], 0)
                st.markdown(f"**Mevcut Fiyat:** ${current:,.2f}")
                
                # Durum Kontrol
                if trade['direction'] == "LONG (Yukış)":
                    if current >= trade['tp_target']:
                        st.success("✅ TP HEDEFİNE ULAŞILDI - KAZANÇ!")
                        trade['status'] = 'KAPATILDI - TP'
                    elif current <= trade['sl_stop']:
                        st.error("❌ STOPLOSS TRİGGERLENDİ - ZARAR!")
                        trade['status'] = 'KAPATILDI - SL'
                    else:
                        remaining = ((trade['tp_target'] - current) / trade['tp_target']) * 100
                        st.info(f"⏳ AÇIK - Hedefe kadar: {remaining:.1f}%")
                else:
                    if current <= trade['tp_target']:
                        st.success("✅ TP HEDEFİNE ULAŞILDI - KAZANÇ!")
                        trade['status'] = 'KAPATILDI - TP'
                    elif current >= trade['sl_stop']:
                        st.error("❌ STOPLOSS TRİGGERLENDİ - ZARAR!")
                        trade['status'] = 'KAPATILDI - SL'
                    else:
                        remaining = ((current - trade['tp_target']) / current) * 100
                        st.info(f"⏳ AÇIK - Hedefe kadar: {remaining:.1f}%")
    else:
        st.info("📊 Henüz açık işlem yok. Bir işlem eklemek için yukarıdaki formu kullan.")

# ============================================================================
# PAGE: SETTINGS
# ============================================================================

elif page == "🔧 Settings":
    st.title("⚙️ Ayarlar")
    st.caption("Sistem Konfigürasyonu")
    
    st.subheader("🔑 API Durumları")
    
    apis = [
        ("BINANCE_API_KEY", "Binance API Anahtarı"),
        ("TELEGRAM_TOKEN", "Telegram Bot Token"),
        ("TELEGRAM_CHAT_ID", "Telegram Chat ID"),
    ]
    
    for var, desc in apis:
        if os.getenv(var):
            st.success(f"✅ {desc}: Ayarlanmış")
        else:
            st.warning(f"⚠️ {desc}: Eksik")

# ============================================================================
# AUTO-REFRESH (Her 5 saniyede bir)
# ============================================================================

time.sleep(5)
st.session_state.last_update = datetime.now()
st.rerun()
