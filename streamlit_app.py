"""
🔱 DEMIR AI TRADING BOT - DASHBOARD v7.1 FIXED
TELEGRAM ALERTS + COIN MANAGER + MULTI-COIN WATCHLIST  
Date: 1 Kasım 2025

v7.1 FIX'LER:
✅ Telegram mesajları düzeltildi (info + açıklayıcı)
✅ Component scores uyarısı düzeltildi
✅ Pozisyon planı NEUTRAL kontrolü eklendi
✅ Hata mesajları daha açıklayıcı
✅ Arka plan rengi açık gri (göz yormaz)
✅ Tüm yazılar net okunuyor

PHASE 3.1 ÖZELLİKLER:
✅ Telegram Alert System entegrasyonu  
✅ AI analiz sonrası otomatik Telegram bildirimi  
✅ Sidebar'da Telegram toggle  
✅ Manuel test butonu  

MEVCUT ÖZELLİKLER:
✅ Manuel coin ekleme (BTC+ETH+LTC sabit)
✅ Multi-Coin Watchlist
✅ One-Click Copy (Entry/SL/TP)
✅ Mobile Responsive
✅ 11 Layer detaylı analiz
✅ Trade History + Performance tracking
✅ Progress bar + Optimizations
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime
import pandas as pd

# Phase 1 imports
import trade_history_db as db
import win_rate_calculator as wrc

# Phase 3.1: Telegram Alert System
try:
    from telegram_alert_system import TelegramAlertSystem
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        telegram_alert = TelegramAlertSystem(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        TELEGRAM_AVAILABLE = True
    else:
        telegram_alert = None
        TELEGRAM_AVAILABLE = False
except Exception as e:
    telegram_alert = None
    TELEGRAM_AVAILABLE = False
    print(f"⚠️ Telegram unavailable: {e}")

# AI Brain import
try:
    import ai_brain as brain
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

st.set_page_config(
    page_title="🔱 DEMIR AI v7.1",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State
if 'watchlist_coins' not in st.session_state:
    st.session_state.watchlist_coins = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'BNBUSDT', 'SOLUSDT']
if 'telegram_alerts_enabled' not in st.session_state:
    st.session_state.telegram_alerts_enabled = True

def get_binance_price(symbol):
    try:
        url = f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            d = r.json()
            return {'price': float(d['lastPrice']), 'change_24h': float(d['priceChangePercent']),
                   'volume': float(d['quoteVolume']), 'high_24h': float(d['highPrice']),
                   'low_24h': float(d['lowPrice']), 'available': True}
    except: pass
    return {'price': 0, 'change_24h': 0, 'volume': 0, 'high_24h': 0, 'low_24h': 0, 'available': False}

def add_coin_to_watchlist(symbol):
    symbol = (symbol.upper() + 'USDT') if not symbol.endswith('USDT') else symbol.upper()
    if symbol in st.session_state.watchlist_coins:
        st.warning(f"⚠️ {symbol} zaten watchlist'te!")
        return False
    if not get_binance_price(symbol)['available']:
        st.error(f"❌ {symbol} Binance'de bulunamadı!")
        return False
    st.session_state.watchlist_coins.append(symbol)
    st.success(f"✅ {symbol} eklendi!")
    return True

def remove_coin_from_watchlist(symbol):
    if symbol in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']:
        st.error(f"❌ {symbol} sabit - silinemez!")
        return False
    if symbol in st.session_state.watchlist_coins:
        st.session_state.watchlist_coins.remove(symbol)
        st.success(f"✅ {symbol} silindi!")
        return True
    return False

def get_quick_signal(symbol, interval='1h', progress_bar=None, idx=0, total=10):
    try:
        if progress_bar:
            progress_bar.progress((idx + 1) / total, f"Analyzing {symbol}... ({idx + 1}/{total})")
        if not AI_AVAILABLE:
            return {'signal': 'N/A', 'score': 0, 'confidence': 0}
        decision = brain.make_trading_decision(symbol, interval, 10000, 200)
        return {'signal': decision.get('decision', 'NEUTRAL'),
                'score': decision.get('final_score', 0),
                'confidence': decision.get('confidence', 0) * 100}
    except: return {'signal': 'ERROR', 'score': 0, 'confidence': 0}

def render_progress_bar(value, max_val=100, color='#667eea'):
    pct = (value / max_val) * 100
    return f"""<div style="background: #f0f0f0; border-radius: 10px; height: 20px; overflow: hidden; margin: 5px 0;">
    <div style="background: {color}; width: {pct}%; height: 100%; border-radius: 10px; display: flex; 
    align-items: center; justify-content: center; color: white; font-size: 0.75em; font-weight: 600;">{value:.1f}</div></div>"""

def copy_button(text, label="📋"):
    return f"""<button onclick="navigator.clipboard.writeText('{text}').then(function(){{alert('✅ Kopyalandı: {text}');}}, function(err){{alert('❌ Hata');}});" 
    style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; padding: 6px 12px; 
    border-radius: 6px; cursor: pointer; font-size: 0.85em; font-weight: 600; margin: 2px;">{label}</button>"""

st.markdown("""<style>
/* ✅ AÇIK & TEMİZ ARKA PLAN */
.main{background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
.stApp{background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}

/* ✅ KARTLAR - BEYAZ & NET */
.card{background: white; border-radius: 15px; padding: 20px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);}
.price-card{background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 12px; padding: 20px; margin: 10px 0;}
.price-big{font-size: 2.5em; font-weight: 700; margin: 10px 0;}
.price-detail{display: flex; justify-content: space-between; margin: 5px 0; font-size: 0.9em; opacity: 0.9;}
.tp-box{background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-left: 4px solid #667eea; padding: 15px; margin: 10px 0; border-radius: 8px;}
.stat-box{background: linear-gradient(135deg, #11998e, #38ef7d); color: white; border-radius: 10px; padding: 15px; margin: 5px 0; text-align: center;}
.stat-value{font-size: 1.8em; font-weight: 700;}
.layer-card{background: #f8f9fa; border-radius: 10px; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea;}
.signal-badge{display: inline-block; padding: 8px 20px; border-radius: 20px; font-weight: 600; font-size: 1.1em;}
.badge-long{background: linear-gradient(135deg, #10b981, #059669); color: white;}
.badge-short{background: linear-gradient(135deg, #ef4444, #dc2626); color: white;}
.badge-neutral{background: linear-gradient(135deg, #6b7280, #4b5563); color: white;}
@media (max-width: 768px){.price-big{font-size: 1.8em;} .stat-value{font-size: 1.5em;} .tp-box, .card{padding: 10px;}}</style>""", unsafe_allow_html=True)

st.markdown("""<div class="card" style="text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); color: white;">
<h1 style="color: white; margin: 0;">🔱 DEMIR AI TRADING BOT v7.1</h1>
<p style="color: rgba(255,255,255,0.9);">PHASE 3: Telegram Alerts + Coin Manager (FIXED)</p></div>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚙️ Ayarlar")
    selected_coin = st.selectbox("Coin", st.session_state.watchlist_coins, key='coin')
    interval = st.selectbox("Timeframe", ['1m', '5m', '15m', '1h', '4h', '1d'], index=3)
    st.markdown("### 💰 Portfolio")
    portfolio = st.number_input("Portfolio ($)", value=10000, step=100)
    risk = st.number_input("Risk/Trade ($)", value=200, step=10)
    st.markdown("---")
    
    st.markdown("### 📱 Telegram Alerts")
    if TELEGRAM_AVAILABLE:
        st.session_state.telegram_alerts_enabled = st.checkbox("📱 Bildirimleri Aç", value=st.session_state.telegram_alerts_enabled, help="AI analiz sonrası otomatik bildirim")
        if st.button("📱 Test Telegram", use_container_width=True):
            with st.spinner("Test mesajı gönderiliyor..."):
                success = telegram_alert.test_connection()
                if success:
                    st.success("✅ Telegram çalışıyor!")
                else:
                    st.error("❌ Bağlantı hatası - Token/Chat ID kontrol edin!")
    else:
        st.info("💡 **Telegram Setup:** Render'da environment variables ekleyin:\n\n- `TELEGRAM_TOKEN` (Bot token)\n- `TELEGRAM_CHAT_ID` (Your chat ID)")
    st.markdown("---")
    
    st.markdown("### 📊 Performance")
    perf = wrc.get_performance_dashboard()
    if perf['total_trades'] > 0:
        wr_col = '#10b981' if perf['win_rate'] >= 50 else '#ef4444'
        st.markdown(f"""<div class="stat-box" style="background: linear-gradient(135deg, {wr_col}, #38ef7d);">
        <div style="font-size: 0.9em; opacity: 0.9;">Win Rate</div><div class="stat-value">{perf['win_rate']:.1f}%</div>
        <div style="font-size: 0.85em;">{perf['winning_trades']}W / {perf['losing_trades']}L</div></div>""", unsafe_allow_html=True)
        
        pnl_col = '#10b981' if perf['total_pnl_usd'] >= 0 else '#ef4444'
        st.markdown(f"""<div class="stat-box" style="background: linear-gradient(135deg, {pnl_col}, #667eea);">
        <div style="font-size: 0.9em; opacity: 0.9;">Total PNL</div><div class="stat-value">${perf['total_pnl_usd']:,.2f}</div>
        <div style="font-size: 0.85em;">{perf['total_trades']} Trades</div></div>""", unsafe_allow_html=True)
        
        st.markdown(f"""<div class="stat-box" style="background: linear-gradient(135deg, #667eea, #764ba2);">
        <div style="font-size: 0.9em; opacity: 0.9;">Sharpe Ratio</div><div class="stat-value">{perf['sharpe_ratio']:.2f}</div>
        <div style="font-size: 0.85em;">PF: {perf['profit_factor']:.2f}</div></div>""", unsafe_allow_html=True)
    else:
        st.info("📊 Trade kaydı yok")
    st.markdown("---")
    analyze_btn = st.button("🔍 AI ANALİZ YAP", use_container_width=True, type="primary")
    st.markdown("---")
    show_help = st.checkbox("❓ Terimler Rehberi")

if show_help:
    with st.expander("📚 TERİMLER", expanded=True):
        st.markdown("""**LONG**: Al | **SHORT**: Sat | **Confidence**: AI güven | **Score**: Final puan | **R/R**: Risk/Reward  
**Entry**: Açılış | **SL**: Stop Loss | **TP**: Take Profit | **Win Rate**: Kazanan % | **Sharpe**: Risk-adj. getiri""")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Live Dashboard", "🔍 Watchlist", "⚙️ Coin Manager", "📜 Trade History"])

with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 Canlı Fiyatlar (BTC+ETH+LTC)")
    cols = st.columns(3)
    for idx, coin in enumerate(['BTCUSDT', 'ETHUSDT', 'LTCUSDT']):
        data = get_binance_price(coin)
        with cols[idx]:
            if data['available']:
                arrow = '↗' if data['change_24h'] >= 0 else '↘'
                st.markdown(f"""<div class="price-card">
                <div style="font-size: 1.2em; font-weight: 600; opacity: 0.9;">{coin.replace('USDT', '')}</div>
                <div class="price-big">${data['price']:,.2f}</div>
                <div style="color: white; font-weight: 700; font-size: 1.2em; margin: 10px 0;">{data['change_24h']:+.2f}% {arrow}</div>
                <div class="price-detail"><span>24h High:</span><span>${data['high_24h']:,.2f}</span></div>
                <div class="price-detail"><span>24h Low:</span><span>${data['low_24h']:,.2f}</span></div>
                <div class="price-detail" style="margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px;">
                <span>Volume:</span><span>${data['volume']/1e6:.1f}M</span></div></div>""", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; color: #333; font-size: 0.9em; margin-top: 10px; background: white; padding: 8px; border-radius: 8px;'>Son güncelleme: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if analyze_btn and AI_AVAILABLE:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🎯 AI Analiz Sonucu")
        with st.spinner('🧠 AI analizi yapılıyor...'):
            try:
                decision = brain.make_trading_decision(selected_coin, interval, portfolio, risk)
                trade_id = db.log_trade(decision)
                st.session_state.last_decision = decision
                
                # ✅ PHASE 3.1: TELEGRAM ALERT
                if TELEGRAM_AVAILABLE and st.session_state.telegram_alerts_enabled:
                    telegram_success = telegram_alert.send_signal_alert(decision)
                    if telegram_success:
                        st.success("📱 Telegram'a sinyal gönderildi!")
                
                signal = decision['decision']
                badge_class = {'LONG': 'badge-long', 'SHORT': 'badge-short', 'NEUTRAL': 'badge-neutral', 'WAIT': 'badge-neutral'}
                emoji = {'LONG': '📈', 'SHORT': '📉', 'NEUTRAL': '⏸️', 'WAIT': '⏳'}
                
                st.markdown(f"""<div style="text-align: center; padding: 30px;">
                <div class="signal-badge {badge_class.get(signal, 'badge-neutral')}">{emoji.get(signal, '🎯')} {signal} {decision.get('signal', '')}</div>
                <div style="font-size: 1.3em; margin: 20px 0; color: #333;">
                Confidence: <strong>{decision['confidence']*100:.0f}%</strong> | Score: <strong>{decision['final_score']:.1f}/100</strong> | R/R: <strong>1:{decision['risk_reward']:.2f}</strong>
                </div><div style="font-size: 0.95em; color: #666; margin-top: 15px;">Trade ID: #{trade_id} | ✅ Database'e kaydedildi</div></div>""", unsafe_allow_html=True)
                
                st.markdown("**💡 Karar Gerekçesi:**")
                st.info(decision['reason'])
                
                st.markdown("---")
                st.markdown("### 🧠 11 Layer Detaylı Analiz")
                if 'component_scores' in decision and decision.get('component_scores'):
                    scores = decision['component_scores']
                    col1, col2 = st.columns(2)
                    layer_info = {
                        'volume_profile': {'name': 'Volume Profile', 'desc': 'POC, VAH, VAL', 'weight': 0.12},
                        'pivot_points': {'name': 'Pivot Points', 'desc': 'Destek/Direnç', 'weight': 0.10},
                        'fibonacci': {'name': 'Fibonacci', 'desc': 'Retracement', 'weight': 0.10},
                        'vwap': {'name': 'VWAP', 'desc': 'Volume-weighted', 'weight': 0.08},
                        'news_sentiment': {'name': 'News Sentiment', 'desc': 'Fear & Greed', 'weight': 0.08},
                        'garch': {'name': 'GARCH Volatility', 'desc': 'Vol. tahmin', 'weight': 0.15},
                        'markov': {'name': 'Markov Regime', 'desc': 'Piyasa rejimi', 'weight': 0.15},
                        'hvi': {'name': 'Historical Vol.', 'desc': 'Geçmiş vol.', 'weight': 0.12},
                        'squeeze': {'name': 'Vol. Squeeze', 'desc': 'BB + KC', 'weight': 0.10}
                    }
                    idx = 0
                    for key, info in layer_info.items():
                        if key in scores:
                            score_val = scores[key].get('score', 0)
                            available = scores[key].get('available', False)
                            target_col = col1 if idx % 2 == 0 else col2
                            with target_col:
                                status_icon = '✅' if available else '❌'
                                color = '#667eea' if available else '#d1d5db'
                                st.markdown(f"""<div class="layer-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <strong style="font-size: 1.05em;">{status_icon} {info['name']}</strong>
                                <span style="font-weight: 700; color: {color};">{score_val:.1f}/100</span></div>
                                <div style="font-size: 0.85em; color: #666; margin-bottom: 8px;">{info['desc']}</div>
                                {render_progress_bar(score_val, color=color)}
                                <div style="font-size: 0.8em; color: #999; margin-top: 5px;">Weight: {info['weight']*100:.0f}%</div></div>""", unsafe_allow_html=True)
                            idx += 1
                else:
                    st.info("💡 **Layer Analiz:** Component scores yükleniyor... AI Brain çalışıyor (ilk analiz biraz uzun sürebilir)")
                
                st.markdown("---")
                st.markdown("### 💼 Pozisyon Planı")
                if decision.get('entry_price') and decision.get('stop_loss') and decision['decision'] in ['LONG', 'SHORT']:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📍 Entry", f"${decision['entry_price']:,.2f}")
                        components.html(copy_button(str(decision['entry_price']), "📋 Entry"), height=40)
                        st.metric("💰 Position", f"${decision['position_size_usd']:,.2f}")
                    with col2:
                        sl_pct = ((decision['stop_loss'] - decision['entry_price']) / decision['entry_price'] * 100)
                        st.metric("🛡️ Stop Loss", f"${decision['stop_loss']:,.2f}", f"{sl_pct:.2f}%")
                        components.html(copy_button(str(decision['stop_loss']), "📋 SL"), height=40)
                        st.metric("⚠️ Risk", f"${decision['risk_amount_usd']:,.2f}")
                    
                    st.markdown("---")
                    st.markdown("### 🎯 Take Profit Seviyeleri")
                    risk_amount = abs(decision['entry_price'] - decision['stop_loss'])
                    if decision['decision'] == 'LONG':
                        tp1, tp2, tp3 = decision['entry_price'] + (risk_amount * 1.0), decision['entry_price'] + (risk_amount * 1.618), decision['entry_price'] + (risk_amount * 2.618)
                    else:
                        tp1, tp2, tp3 = decision['entry_price'] - (risk_amount * 1.0), decision['entry_price'] - (risk_amount * 1.618), decision['entry_price'] - (risk_amount * 2.618)
                    
                    for tp_num, tp_val, rr, close_pct, desc in [(1, tp1, "1:1", "50%", "Kar garantiye al"), (2, tp2, "1:1.62", "30%", "Fibonacci golden ratio"), (3, tp3, "1:2.62", "20%", "Maksimum kar")]:
                        tp_pct = ((tp_val - decision['entry_price']) / decision['entry_price'] * 100)
                        st.markdown(f"""<div class="tp-box"><div><strong style="font-size: 1.1em;">🎯 TP{tp_num}:</strong> ${tp_val:,.2f} ({tp_pct:+.2f}%) [R/R: {rr}]<br>
                        <span style="font-size: 0.9em; color: #666;">→ Close {close_pct} | {desc}</span></div></div>""", unsafe_allow_html=True)
                        components.html(copy_button(str(tp_val), f"📋 TP{tp_num}"), height=40)
                    
                    all_text = f"Entry: {decision['entry_price']}, SL: {decision['stop_loss']}, TP1: {tp1:.2f}, TP2: {tp2:.2f}, TP3: {tp3:.2f}"
                    st.markdown("---")
                    components.html(copy_button(all_text, "📋 HEPSİNİ KOPYALA"), height=50)
                    st.info("**📈 Trailing Stop:** TP1 → SL'i entry'e | TP2 → SL'i TP1'e çek")
                else:
                    if decision['decision'] == 'NEUTRAL':
                        st.info("⏸️ **NEUTRAL Sinyal:** Piyasa belirsiz - pozisyon açma önerilmiyor. Düşük confidence nedeniyle bekleyin.")
                    elif decision['decision'] == 'WAIT':
                        st.warning("⏳ **WAIT Sinyal:** AI daha fazla veri bekliyor - şu an trade açmayın.")
                    else:
                        st.warning("⚠️ **Pozisyon Planı Hesaplanamadı:** Entry/SL değerleri eksik - AI Brain kontrol edin.")
            except Exception as e:
                st.error(f"❌ **Analiz Hatası:** {str(e)}")
                with st.expander("🐛 Debug Detayları (Geliştiriciler için)"):
                    st.code(str(e))
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"### 🔍 Multi-Coin Watchlist ({len(st.session_state.watchlist_coins)} Coins)")
    st.info("💡 BTC+ETH+LTC sabit, diğerleri eklenebilir/silinebilir")
    progress_bar = st.progress(0, "Başlatılıyor...")
    watchlist_data = []
    for idx, coin in enumerate(st.session_state.watchlist_coins):
        price_data = get_binance_price(coin)
        signal_data = get_quick_signal(coin, interval, progress_bar, idx, len(st.session_state.watchlist_coins))
        if price_data['available']:
            coin_display = coin.replace('USDT', '')
            if coin in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']:
                coin_display = f"🔒 {coin_display}"
            watchlist_data.append({'Coin': coin_display, 'Price': f"${price_data['price']:,.2f}",
                                   '24h %': f"{price_data['change_24h']:+.2f}%", 'Signal': signal_data['signal'],
                                   'Score': f"{signal_data['score']:.0f}/100", 'Confidence': f"{signal_data['confidence']:.0f}%"})
    progress_bar.empty()
    if watchlist_data:
        df = pd.DataFrame(watchlist_data)
        def color_signal(val):
            if val == 'LONG': return 'background-color: #d1fae5; color: #065f46;'
            elif val == 'SHORT': return 'background-color: #fee2e2; color: #991b1b;'
            elif val == 'NEUTRAL': return 'background-color: #f3f4f6; color: #374151;'
            return ''
        st.dataframe(df.style.applymap(color_signal, subset=['Signal']), use_container_width=True)
        st.markdown("---")
        st.markdown("**🔍 Detaylı Analiz İçin:**")
        cols_per_row = 5
        for i in range(0, len(st.session_state.watchlist_coins), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, coin in enumerate(st.session_state.watchlist_coins[i:i+cols_per_row]):
                with cols[j]:
                    btn_label = coin.replace('USDT', '')
                    if coin in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']: btn_label = f"🔒 {btn_label}"
                    if st.button(btn_label, key=f"watch_{coin}", use_container_width=True):
                        st.session_state.coin = coin
                        st.rerun()
    else:
        st.error("❌ Watchlist verisi alınamadı")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Coin Manager")
    st.info("💡 **BTCUSDT, ETHUSDT, LTCUSDT** sabit - silinemez!")
    st.markdown("#### ➕ Yeni Coin Ekle")
    col_add1, col_add2 = st.columns([3, 1])
    with col_add1:
        new_coin = st.text_input("Coin Symbol (örn: SOL, BNB)", key="new_coin_input", placeholder="BNB")
    with col_add2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Ekle", type="primary", use_container_width=True):
            if new_coin:
                add_coin_to_watchlist(new_coin)
                st.rerun()
            else:
                st.warning("⚠️ Coin symbol girin!")
    st.markdown("---")
    st.markdown("#### 📋 Mevcut Watchlist")
    for coin in st.session_state.watchlist_coins:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.markdown(f"**🔒 {coin}** (Sabit)" if coin in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT'] else f"**{coin}**")
        with col2:
            price_data = get_binance_price(coin)
            if price_data['available']:
                change_icon = '↗' if price_data['change_24h'] >= 0 else '↘'
                st.markdown(f"${price_data['price']:,.2f} ({price_data['change_24h']:+.2f}% {change_icon})")
        with col3:
            if coin not in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']:
                if st.button("🗑️ Sil", key=f"remove_{coin}", use_container_width=True):
                    remove_coin_from_watchlist(coin)
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📜 Trade History")
    trades_df = db.get_all_trades()
    if not trades_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Total Trades", len(trades_df))
        with col2: st.metric("Pending", len(trades_df[trades_df['status'] == 'PENDING']))
        with col3: 
            closed = len(trades_df[trades_df['status'].isin(['WIN', 'LOSS', 'BREAKEVEN'])])
            st.metric("Closed", closed)
        with col4:
            if closed > 0:
                wins = len(trades_df[trades_df['status'] == 'WIN'])
                st.metric("Win Rate", f"{(wins / closed * 100):.1f}%")
            else:
                st.metric("Win Rate", "N/A")
        st.markdown("---")
        st.dataframe(trades_df[['id', 'timestamp', 'symbol', 'signal', 'confidence', 'final_score', 
                                'entry_price', 'stop_loss', 'position_size_usd', 'status', 'pnl_usd', 'pnl_pct']], use_container_width=True)
        st.markdown("---")
        if st.button("📥 Export to Excel", type="primary"):
            filename = db.export_to_excel()
            st.success(f"✅ Exported: {filename}")
            with open(filename, 'rb') as f:
                st.download_button("⬇️ Download Excel", f.read(), filename, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        st.markdown("---")
        st.markdown("### ✏️ Update Trade Result")
        col_u1, col_u2, col_u3, col_u4 = st.columns(4)
        with col_u1: trade_id_update = st.number_input("Trade ID", min_value=1, step=1)
        with col_u2: close_price = st.number_input("Close Price", min_value=0.0, step=0.01)
        with col_u3: status = st.selectbox("Status", ['WIN', 'LOSS', 'BREAKEVEN'])
        with col_u4:
            if st.button("Update"):
                db.update_trade_result(trade_id_update, close_price, status)
                st.success(f"✅ Trade #{trade_id_update} updated!")
                st.rerun()
    else:
        st.info("📊 Trade kaydı yok. AI Analiz yapın!")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("""<div style='text-align: center; color: #333; padding: 20px; background: white; border-radius: 12px; margin: 10px;'>
<p><strong>🔱 DEMIR AI Trading Bot v7.1 FIXED</strong></p>
<p style='font-size: 0.9em; opacity: 0.7;'>Telegram Alerts + Coin Manager + All Bugs Fixed | © 2025</p></div>""", unsafe_allow_html=True)
