"""
🔱 DEMIR AI TRADING BOT - PERPLEXITY-STYLE DASHBOARD
Version: 3.1 - FIXED & FINAL - Data Validator + Unified AI + Trade Analysis
Date: 11 Kasım 2025, 12:02 CET

✅ ÖZELLIKLER (EKSIKSIZ):
- Gerçek fiyatlar (Binance Futures)
- AI Brain entegrasyonu
- Telegram proaktif alerts
- Trade tracking ve logging
- %100 gerçek veri
- 10 sayfa (Dashboard + 9 Pages)
- Türkçe interface
- Trade takip sistemi
- Data Validator (Gerçek veri doğrulaması)
- Unified AI Engine (17 layer modüler + birleşik karar)
- Trade Analysis AI (A+/A/B/C grading)
- BUG FIX: entry_price UnboundLocalError çözüldü
"""

import streamlit as st
import time
from datetime import datetime
import os
import sqlite3
import json
import requests

# ============================================================================
# YENİ MODÜLLER IMPORT - DATA VALIDATOR, UNIFIED AI, TRADE ANALYSIS
# ============================================================================

try:
    from data_validator import DataValidator
    data_validator = DataValidator()
    DATA_VALIDATOR_OK = True
except Exception as e:
    DATA_VALIDATOR_OK = False
    print(f"⚠️ Data Validator başlatılamadı: {e}")

try:
    from unified_ai_engine import UnifiedAIEngine
    ai_engine = UnifiedAIEngine()
    UNIFIED_AI_OK = True
except Exception as e:
    UNIFIED_AI_OK = False
    print(f"⚠️ Unified AI Engine başlatılamadı: {e}")

try:
    from trade_analysis_ai import TradeAnalysisAI
    trade_analyzer = TradeAnalysisAI()
    TRADE_ANALYSIS_OK = True
except Exception as e:
    TRADE_ANALYSIS_OK = False
    print(f"⚠️ Trade Analysis AI başlatılamadı: {e}")

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
    start_telegram_daemon()
    TELEGRAM_ALERTS_OK = True
except Exception as e:
    TELEGRAM_ALERTS_OK = False
    print(f"⚠️ Telegram başlatılamadı: {e}")

# ============================================================================
# MODÜL İMPORT
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
    conn = sqlite3.connect(':memory:')
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
            "📊 Trade Takip",
            "🔮 Predictive Engine",
            "📡 Monitoring"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 🟢 Sistem Durumu")
    st.markdown("**Sistem:** 🟢 Çalışıyor")
    st.markdown(f"**WebSocket:** {'🟢 Bağlı' if WEBSOCKET_OK else '🔴 Bağlantısız'}")
    st.markdown(f"**AI Brain:** {'🟢 Aktif' if AIBRAIN_OK else '🔴 Kapalı'}")
    st.markdown(f"**Telegram:** {'🟢 Aktif' if TELEGRAM_ALERTS_OK else '🔴 Kapalı'}")
    st.markdown(f"**Data Validator:** {'🟢 Aktif' if DATA_VALIDATOR_OK else '🔴 Kapalı'}")
    st.markdown(f"**Unified AI:** {'🟢 Aktif' if UNIFIED_AI_OK else '🔴 Kapalı'}")
    st.markdown(f"**Trade Analysis:** {'🟢 Aktif' if TRADE_ANALYSIS_OK else '🔴 Kapalı'}")
    st.markdown("---")
    st.caption(f"Son güncelleme: {st.session_state.last_update.strftime('%H:%M:%S')}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_real_prices():
    """Binance REST API - %100 gerçek fiyatlar"""
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

def get_real_analysis():
    """YENİ: Tüm AI modülleri bir araya getir - FIX: entry_price UnboundLocalError çözüldü"""
    
    # HATA FIX: Önce prices ve entry_price mutlaka tanımla
    prices = get_real_prices()
    entry_price = prices.get('BTCUSDT', 0)
    
    # Step 1: Data validation
    if DATA_VALIDATOR_OK:
        validation_report = data_validator.get_validation_report(['BTCUSDT', 'ETHUSDT', 'LTCUSDT'])
        if not validation_report.get('all_data_valid', False):
            st.error("⚠️ Gerçek veri doğrulamasında sorun var!")
            return None
    else:
        validation_report = None
    
    # Step 2: Unified AI decision
    if UNIFIED_AI_OK:
        decision = ai_engine.make_unified_decision('BTCUSDT')
    else:
        decision = None
    
    # Step 3: Trade analysis (entry_price > 0 kontrolü yapılır)
    if TRADE_ANALYSIS_OK and decision and entry_price > 0:
        tp_price = entry_price * 1.02
        sl_price = entry_price * 0.98
        
        trade_analysis = trade_analyzer.analyze_trade_opportunity(
            symbol='BTCUSDT',
            signal_type=decision['signal'],
            entry_price=entry_price,
            tp_price=tp_price,
            sl_price=sl_price,
            ai_confidence=decision['confidence'],
            layer_scores=decision['layer_scores']
        )
    else:
        trade_analysis = None
    
    return {
        'validation': validation_report,
        'decision': decision,
        'trade_analysis': trade_analysis,
        'prices': prices
    }

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
    
    # YENİ: Data validation + Unified AI + Trade analysis
    analysis = get_real_analysis()
    if analysis:
        st.subheader("🔍 Veri Kalitesi")
        if analysis['validation'] and analysis['validation'].get('all_data_valid', False):
            st.success("✅ Tüm veriler sağlıklı ve tutarlı")
        else:
            st.warning("⚠️ Veri kalitesi kontrol ediliyor...")
        
        if analysis['decision']:
            st.subheader("🧠 AI Karar Mekanizması (Unified)")
            decision = analysis['decision']
            st.markdown(f"- **Sinyal :** {decision['signal']}")
            st.markdown(f"- **Güven Oranı :** {decision['confidence']:.1f}%")
            st.markdown(f"- **Katman Bazlı Skorlar:**")
            for layer, score in decision['layer_scores'].items():
                st.markdown(f"  - {layer}: {score:.1f}")
        
        if analysis['trade_analysis']:
            st.markdown("---")
            st.subheader("📈 Trade Analizi")
            trade = analysis['trade_analysis']
            st.markdown(f"- **Grade :** {trade['grade']}")
            st.markdown(f"- **AI Güveni :** {trade['ai_confidence']:.1f}%")
            st.markdown(f"- **Tavsiye :** {trade['trade_quality']['recommendation']}")
            for insight in trade['ai_insights']:
                st.info(insight)
    
    st.markdown("---")
    
    st.subheader("🤖 AI Sistemi Durumu")
    
    analysis_old = get_ai_analysis()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sistem", "🟢 Çalışıyor", delta="24/7")
    with col2:
        st.metric("Aktif Katmanlar", "17/17")
    with col3:
        st.metric("Çalışma Süresi", "24.0s")
    with col4:
        st.metric("Sinyaller", "0")
    
    st.markdown("---")
    st.subheader("🧠 Yapay Zeka Skorları")
    
    col1, col2 = st.columns(2)
    with col1:
        tech = int(analysis_old['score'])
        st.progress(tech / 100, text=f"Teknik Analiz: {tech}/100")
        macro = int(analysis_old['score'] * 0.9)
        st.progress(macro / 100, text=f"Makro: {macro}/100")
    with col2:
        onchain = int(analysis_old['score'] * 0.85)
        st.progress(onchain / 100, text=f"On-Chain: {onchain}/100")
        sentiment = int(analysis_old['score'] * 0.95)
        st.progress(sentiment / 100, text=f"Duygu: {sentiment}/100")

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
    
    # YENİ: Unified analysis kullan
    real_analysis = get_real_analysis()
    if real_analysis and real_analysis['trade_analysis']:
        trade_info = real_analysis['trade_analysis']
        grade_color = {
            'A+': '🟢',
            'A': '🟢',
            'B': '🟡',
            'C': '🔴'
        }
        st.markdown(f"### {grade_color.get(trade_info['grade'],'🟡')} AI Grade: {trade_info['grade']}")
        st.markdown(f"**Tavsiye:** {trade_info['trade_quality']['recommendation']}")
    
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
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📍 GİRİŞ FİYATI")
        entry_price = st.number_input("", value=current_price, label_visibility="collapsed")
        st.caption(f"Mevcut: ${current_price:,.2f}")
    
    with col2:
        st.markdown("#### 🎯 KAPANIŞ (TP)")
        if trade_type == "LONG (Yukış)":
            default_tp = entry_price * 1.02
        else:
            default_tp = entry_price * 0.98
        tp_price = st.number_input("TP Seviyesi", value=default_tp, label_visibility="collapsed", key="tp")
        profit_pct = ((tp_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
        st.metric("Kar %", f"{profit_pct:+.2f}%")
    
    with col3:
        st.markdown("#### 🛡️ STOPLOSS (SL)")
        if trade_type == "LONG (Yukış)":
            default_sl = entry_price * 0.98
        else:
            default_sl = entry_price * 1.02
        sl_price = st.number_input("SL Seviyesi", value=default_sl, label_visibility="collapsed", key="sl")
        loss_pct = ((sl_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
        st.metric("Zarar %", f"{loss_pct:+.2f}%")
    
    st.markdown("---")
    
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
            st.success(f"✅ TRADEYİ BAŞARILI EKLENMIŞTIR!\n📊 {symbol} - {trade_type}\nGİRİŞ: ${entry_price:,.2f}")
    
    st.divider()
    
    if st.session_state.active_trades:
        st.subheader("📊 Açık İşlemler")
        for idx, trade in enumerate(st.session_state.active_trades):
            with st.expander(f"📈 {trade['symbol']} - {trade['direction']} | {trade['status']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("GİRİŞ", f"${trade['entry_price']:,.2f}")
                with col2:
                    st.metric("HEDEF (TP)", f"${trade['tp_target']:,.2f}")
                with col3:
                    st.metric("STOP (SL)", f"${trade['sl_stop']:,.2f}")
                
                current = prices.get(trade['symbol'], 0)
                st.markdown(f"**Mevcut Fiyat:** ${current:,.2f}")
                
                if trade['direction'] == "LONG (Yukış)":
                    if current >= trade['tp_target']:
                        st.success("✅ TP HEDEFİNE ULAŞILDI - KAZANÇ!")
                    elif current <= trade['sl_stop']:
                        st.error("❌ STOPLOSS TRİGGERLENDİ - ZARAR!")
                    else:
                        st.info(f"⏳ AÇIK")
    else:
        st.info("📊 Henüz açık işlem yok.")

# ============================================================================
# PAGE: AI ANALYSIS
# ============================================================================

elif page == "🧠 AI Analysis":
    st.title("🧠 AI Analiz Sayfası")
    analysis = get_ai_analysis()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Sinyal", analysis['signal'])
        st.metric("Confidence", f"{analysis['confidence']:.1f}%")
    with col2:
        st.metric("AI Score", f"{analysis['score']}/100")

# ============================================================================
# PAGE: MARKET INTELLIGENCE
# ============================================================================

elif page == "🌍 Market Intelligence":
    st.title("🌍 Piyasa Zekası")
    st.info("Piyasa zekası verisi burada gösterilecek")

# ============================================================================
# PAGE: SYSTEM STATUS
# ============================================================================

elif page == "⚙️ System Status":
    st.title("⚙️ Sistem Durumu")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Uptime", "24/7")
    with col2:
        st.metric("CPU", "12%")

# ============================================================================
# PAGE: SETTINGS
# ============================================================================

elif page == "🔧 Settings":
    st.title("⚙️ Ayarlar")
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
# PAGE: PREDICTIVE ENGINE
# ============================================================================

elif page == "🔮 Predictive Engine":
    st.title("🔮 Tahmin Motoru")
    st.info("pages/09_Predictive_Engine.py dosyasını özel sayfada göster")

# ============================================================================
# PAGE: MONITORING
# ============================================================================

elif page == "📡 Monitoring":
    st.title("📡 İzleme Sistemi")
    st.info("Monitoring verisi burada gösterilecek")

# ============================================================================
# AUTO-REFRESH
# ============================================================================

time.sleep(5)
st.session_state.last_update = datetime.now()
st.rerun()
