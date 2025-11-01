"""
🔱 DEMIR AI TRADING BOT - DASHBOARD v8.0 COMPLETE
Date: 1 Kasım 2025

v8.0 NEW FEATURES:
✅ PHASE 3.2: Backtest Module (TAB 5)
✅ Historical data testing
✅ Performance metrics (Win Rate, Sharpe, Drawdown, PF)
✅ Equity curve visualization (Plotly chart)
✅ Trade-by-trade results

v7.3 ÖZELLİKLER:
✅ Dark Mode + AI Comments
✅ Telegram Alert System  
✅ Coin Manager + Watchlist
✅ Trade History + Performance
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

import trade_history_db as db
import win_rate_calculator as wrc

# PHASE 3.2: Backtest Engine
try:
    from backtest_engine import BacktestEngine
    BACKTEST_AVAILABLE = True
except:
    BACKTEST_AVAILABLE = False

try:
    from telegram_alert_system import TelegramAlertSystem
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        telegram_alert = TelegramAlertSystem(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        TELEGRAM_AVAILABLE = True
    else:
        telegram_alert = None
        TELEGRAM_AVAILABLE = False
except:
    telegram_alert = None
    TELEGRAM_AVAILABLE = False

try:
    import ai_brain as brain
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

st.set_page_config(
    page_title="🔱 DEMIR AI v8.0",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'watchlist_coins' not in st.session_state:
    st.session_state.watchlist_coins = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'BNBUSDT', 'SOLUSDT']
if 'telegram_alerts_enabled' not in st.session_state:
    st.session_state.telegram_alerts_enabled = True
if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = None

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

def render_progress_bar(value, max_val=100, color='#10b981'):
    pct = (value / max_val) * 100
    return f"""<div style="background: #374151; border-radius: 10px; height: 20px; overflow: hidden; margin: 5px 0;">
    <div style="background: {color}; width: {pct}%; height: 100%; border-radius: 10px; display: flex; 
    align-items: center; justify-content: center; color: white; font-size: 0.75em; font-weight: 600;">{value:.1f}</div></div>"""

def copy_button(text, label="📋"):
    return f"""<button onclick="navigator.clipboard.writeText('{text}').then(function(){{alert('✅ Kopyalandı: {text}');}}, function(err){{alert('❌ Hata');}});" 
    style="background: linear-gradient(135deg, #10b981, #059669); color: white; border: none; padding: 6px 12px; 
    border-radius: 6px; cursor: pointer; font-size: 0.85em; font-weight: 600; margin: 2px;">{label}</button>"""

def generate_ai_comment(decision):
    """AI analiz yorumu oluştur"""
    signal = decision.get('decision', 'NEUTRAL')
    confidence = decision.get('confidence', 0) * 100
    score = decision.get('final_score', 0)
    
    comments = []
    
    if confidence < 30:
        comments.append(f"🔴 **Çok Düşük Güven ({confidence:.0f}%):** Piyasa çok belirsiz. Bu koşullarda trade açmak yüksek risk taşır.")
    elif confidence < 50:
        comments.append(f"🟡 **Düşük Güven ({confidence:.0f}%):** Sinyal zayıf. Daha net bir fırsat beklemek mantıklı olabilir.")
    elif confidence < 70:
        comments.append(f"🟢 **Orta Güven ({confidence:.0f}%):** Makul bir sinyal. Risk yönetimi ile trade açılabilir.")
    else:
        comments.append(f"🟢 **Yüksek Güven ({confidence:.0f}%):** Güçlü sinyal! AI birden fazla layer'dan pozitif sinyal algıladı.")
    
    if score < 40:
        comments.append(f"📊 **Düşük Skor ({score:.1f}/100):** Çoğu teknik gösterge olumsuz. Piyasa trend göstermiyor.")
    elif score < 60:
        comments.append(f"📊 **Nötr Skor ({score:.1f}/100):** Piyasa kararsız. Hem alıcı hem satıcı baskısı dengede.")
    else:
        comments.append(f"📊 **İyi Skor ({score:.1f}/100):** Teknik göstergeler {signal} yönünde güçlü sinyaller veriyor.")
    
    if signal == 'NEUTRAL':
        comments.append("⏸️ **NEUTRAL Sinyal:** AI belirsizlik tespit etti. Şu an piyasada net bir yön yok. Bekleme modunda kalmak en güvenli seçenek.")
    elif signal == 'WAIT':
        comments.append("⏳ **WAIT Sinyal:** AI daha fazla veri bekliyor. Piyasa henüz yeterli bilgi vermedi. Sabırlı olun.")
    elif signal == 'LONG':
        comments.append("📈 **LONG Sinyal:** AI yükseliş trendi tespit etti. Alım fırsatı olabilir. Entry, SL ve TP seviyelerine dikkat edin.")
    elif signal == 'SHORT':
        comments.append("📉 **SHORT Sinyal:** AI düşüş trendi tespit etti. Satış fırsatı olabilir. Risk yönetimi kritik!")
    
    return "\n\n".join(comments)

def create_equity_curve_chart(equity_curve):
    """Equity curve chart oluştur (Plotly)"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        y=equity_curve,
        mode='lines',
        name='Portfolio Value',
        line=dict(color='#10b981', width=3),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.2)'
    ))
    
    fig.update_layout(
        title='Equity Curve - Portfolio Growth',
        xaxis_title='Trade Number',
        yaxis_title='Portfolio Value ($)',
        template='plotly_dark',
        hovermode='x unified',
        height=450,
        showlegend=False
    )
    
    return fig

# DARK MODE CSS
st.markdown("""<style>
.main{background: #1a1a1a !important;}
.stApp{background: #1a1a1a !important;}
[data-testid="stAppViewContainer"]{background: #1a1a1a !important;}
[data-testid="stHeader"]{background: #0f0f0f !important;}
[data-testid="stSidebar"]{background: #0f0f0f !important;}

.card{background: #2d2d2d; border-radius: 15px; padding: 20px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.5); color: #e5e5e5;}
.price-card{background: linear-gradient(135deg, #10b981, #059669); color: white; border-radius: 12px; padding: 20px; margin: 10px 0;}
.price-big{font-size: 2.5em; font-weight: 700; margin: 10px 0; color: white;}
.price-detail{display: flex; justify-content: space-between; margin: 5px 0; font-size: 0.9em; opacity: 0.9; color: white;}
.tp-box{background: #374151; border-left: 4px solid #10b981; padding: 15px; margin: 10px 0; border-radius: 8px; color: #e5e5e5;}
.stat-box{background: linear-gradient(135deg, #10b981, #059669); color: white; border-radius: 10px; padding: 15px; margin: 5px 0; text-align: center;}
.stat-value{font-size: 1.8em; font-weight: 700;}
.layer-card{background: #374151; border-radius: 10px; padding: 15px; margin: 10px 0; border-left: 4px solid #10b981; color: #e5e5e5;}
.signal-badge{display: inline-block; padding: 8px 20px; border-radius: 20px; font-weight: 600; font-size: 1.1em;}
.badge-long{background: linear-gradient(135deg, #10b981, #059669); color: white;}
.badge-short{background: linear-gradient(135deg, #ef4444, #dc2626); color: white;}
.badge-neutral{background: linear-gradient(135deg, #6b7280, #4b5563); color: white;}

.ai-comment{background: #374151; border-left: 4px solid #3b82f6; padding: 20px; margin: 15px 0; border-radius: 10px; color: #e5e5e5; font-size: 0.95em; line-height: 1.7;}
.ai-comment strong{color: #10b981;}

h1, h2, h3, h4, h5, h6, p, span, div{color: #e5e5e5 !important;}
.stMarkdown{color: #e5e5e5 !important;}
label{color: #e5e5e5 !important;}

@media (max-width: 768px){.price-big{font-size: 1.8em;} .stat-value{font-size: 1.5em;} .tp-box, .card{padding: 10px;}}</style>""", unsafe_allow_html=True)

st.markdown("""<div class="card" style="text-align: center; background: linear-gradient(135deg, #10b981, #059669);">
<h1 style="color: white !important; margin: 0;">🔱 DEMIR AI TRADING BOT v8.0</h1>
<p style="color: white !important;">BACKTEST ENGINE + DARK MODE + AI COMMENTS</p></div>""", unsafe_allow_html=True)

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
        st.session_state.telegram_alerts_enabled = st.checkbox("📱 Bildirimleri Aç", value=st.session_state.telegram_alerts_enabled)
        if st.button("📱 Test Telegram", use_container_width=True):
            with st.spinner("Test..."):
                if telegram_alert.test_connection():
                    st.success("✅ Çalışıyor!")
                else:
                    st.error("❌ Hata!")
    else:
        st.info("💡 Telegram: Render'da TELEGRAM_TOKEN + TELEGRAM_CHAT_ID ekleyin")
    st.markdown("---")
    
    st.markdown("### 📊 Performance")
    perf = wrc.get_performance_dashboard()
    if perf['total_trades'] > 0:
        wr_col = '#10b981' if perf['win_rate'] >= 50 else '#ef4444'
        st.markdown(f"""<div class="stat-box" style="background: linear-gradient(135deg, {wr_col}, #059669);">
        <div style="font-size: 0.9em; opacity: 0.9; color: white;">Win Rate</div><div class="stat-value" style="color: white;">{perf['win_rate']:.1f}%</div>
        <div style="font-size: 0.85em; color: white;">{perf['winning_trades']}W / {perf['losing_trades']}L</div></div>""", unsafe_allow_html=True)
        
        pnl_col = '#10b981' if perf['total_pnl_usd'] >= 0 else '#ef4444'
        st.markdown(f"""<div class="stat-box" style="background: linear-gradient(135deg, {pnl_col}, #059669);">
        <div style="font-size: 0.9em; opacity: 0.9; color: white;">Total PNL</div><div class="stat-value" style="color: white;">${perf['total_pnl_usd']:,.2f}</div>
        <div style="font-size: 0.85em; color: white;">{perf['total_trades']} Trades</div></div>""", unsafe_allow_html=True)
        
        st.markdown(f"""<div class="stat-box">
        <div style="font-size: 0.9em; opacity: 0.9; color: white;">Sharpe Ratio</div><div class="stat-value" style="color: white;">{perf['sharpe_ratio']:.2f}</div>
        <div style="font-size: 0.85em; color: white;">PF: {perf['profit_factor']:.2f}</div></div>""", unsafe_allow_html=True)
    else:
        st.info("📊 Trade kaydı yok")
    st.markdown("---")
    analyze_btn = st.button("🔍 AI ANALİZ YAP", use_container_width=True, type="primary")
    st.markdown("---")
    show_help = st.checkbox("❓ Terimler")

if show_help:
    with st.expander("📚 TERİMLER", expanded=True):
        st.markdown("""**LONG**: Al | **SHORT**: Sat | **Confidence**: AI güven | **Score**: Final puan | **R/R**: Risk/Reward  
**Entry**: Açılış | **SL**: Stop Loss | **TP**: Take Profit | **Sharpe**: Risk-adjusted return | **Drawdown**: Max düşüş""")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Live Dashboard", "🔍 Watchlist", "⚙️ Coin Manager", "📜 Trade History", "📊 Backtest"])

# TAB 1: LIVE DASHBOARD
with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 Canlı Fiyatlar")
    cols = st.columns(3)
    for idx, coin in enumerate(['BTCUSDT', 'ETHUSDT', 'LTCUSDT']):
        data = get_binance_price(coin)
        with cols[idx]:
            if data['available']:
                arrow = '↗' if data['change_24h'] >= 0 else '↘'
                st.markdown(f"""<div class="price-card">
                <div style="font-size: 1.2em; font-weight: 600;">{coin.replace('USDT', '')}</div>
                <div class="price-big">${data['price']:,.2f}</div>
                <div style="font-weight: 700; font-size: 1.2em; margin: 10px 0;">{data['change_24h']:+.2f}% {arrow}</div>
                <div class="price-detail"><span>24h High:</span><span>${data['high_24h']:,.2f}</span></div>
                <div class="price-detail"><span>24h Low:</span><span>${data['low_24h']:,.2f}</span></div>
                <div class="price-detail" style="margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px;">
                <span>Volume:</span><span>${data['volume']/1e6:.1f}M</span></div></div>""", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; color: #10b981; font-size: 0.9em; margin-top: 10px; background: #2d2d2d; padding: 8px; border-radius: 8px;'>Son güncelleme: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if analyze_btn and AI_AVAILABLE:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        coin_name = selected_coin.replace('USDT', '')
        st.markdown(f"### 🎯 {coin_name} AI Analiz Sonucu")
        with st.spinner('🧠 AI analizi yapılıyor...'):
            try:
                decision = brain.make_trading_decision(selected_coin, interval, portfolio, risk)
                trade_id = db.log_trade(decision)
                
                if TELEGRAM_AVAILABLE and st.session_state.telegram_alerts_enabled:
                    telegram_alert.send_signal_alert(decision)
                    st.success("📱 Telegram'a gönderildi!")
                
                signal = decision['decision']
                badge_class = {'LONG': 'badge-long', 'SHORT': 'badge-short', 'NEUTRAL': 'badge-neutral', 'WAIT': 'badge-neutral'}
                emoji = {'LONG': '📈', 'SHORT': '📉', 'NEUTRAL': '⏸️', 'WAIT': '⏳'}
                
                st.markdown(f"""<div style="text-align: center; padding: 30px;">
                <div class="signal-badge {badge_class.get(signal, 'badge-neutral')}">{emoji.get(signal, '🎯')} {signal}</div>
                <div style="font-size: 1.3em; margin: 20px 0; color: #e5e5e5;">
                Confidence: <strong style="color: #10b981;">{decision['confidence']*100:.0f}%</strong> | Score: <strong style="color: #10b981;">{decision['final_score']:.1f}/100</strong> | R/R: <strong style="color: #10b981;">1:{decision['risk_reward']:.2f}</strong>
                </div><div style="font-size: 0.95em; color: #9ca3af;">Trade ID: #{trade_id} | ✅ Database'e kaydedildi</div></div>""", unsafe_allow_html=True)
                
                ai_comment = generate_ai_comment(decision)
                st.markdown(f"""<div class="ai-comment">
                <h4 style="color: #3b82f6 !important; margin: 0 0 15px 0;">🤖 AI Yorumu</h4>
                {ai_comment.replace('**', '<strong>').replace('🔴', '🔴').replace('🟡', '🟡').replace('🟢', '🟢').replace('📊', '📊').replace('⏸️', '⏸️').replace('⏳', '⏳').replace('📈', '📈').replace('📉', '📉')}
                </div>""", unsafe_allow_html=True)
                
                st.markdown("**💡 Karar Gerekçesi:**")
                st.info(decision['reason'])
                
                st.markdown("---")
                st.markdown("### 🧠 11 Layer Detaylı Analiz")
                if 'component_scores' in decision and decision.get('component_scores') and len(decision.get('component_scores', {})) > 0:
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
                                color = '#10b981' if available else '#6b7280'
                                st.markdown(f"""<div class="layer-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <strong style="font-size: 1.05em; color: #e5e5e5;">{status_icon} {info['name']}</strong>
                                <span style="font-weight: 700; color: {color};">{score_val:.1f}/100</span></div>
                                <div style="font-size: 0.85em; color: #9ca3af; margin-bottom: 8px;">{info['desc']}</div>
                                {render_progress_bar(score_val, color=color)}
                                <div style="font-size: 0.8em; color: #6b7280; margin-top: 5px;">Weight: {info['weight']*100:.0f}%</div></div>""", unsafe_allow_html=True)
                            idx += 1
                else:
                    st.info("💡 Component scores yükleniyor... AI Brain ilk analizini yapıyor.")
                
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
                    st.markdown("### 🎯 Take Profit")
                    risk_amount = abs(decision['entry_price'] - decision['stop_loss'])
                    if decision['decision'] == 'LONG':
                        tp1, tp2, tp3 = decision['entry_price'] + (risk_amount * 1.0), decision['entry_price'] + (risk_amount * 1.618), decision['entry_price'] + (risk_amount * 2.618)
                    else:
                        tp1, tp2, tp3 = decision['entry_price'] - (risk_amount * 1.0), decision['entry_price'] - (risk_amount * 1.618), decision['entry_price'] - (risk_amount * 2.618)
                    
                    for tp_num, tp_val, rr, close_pct, desc in [(1, tp1, "1:1", "50%", "Kar garantiye al"), (2, tp2, "1:1.62", "30%", "Fibonacci golden ratio"), (3, tp3, "1:2.62", "20%", "Maksimum kar")]:
                        tp_pct = ((tp_val - decision['entry_price']) / decision['entry_price'] * 100)
                        st.markdown(f"""<div class="tp-box"><div><strong style="font-size: 1.1em; color: #10b981;">🎯 TP{tp_num}:</strong> ${tp_val:,.2f} ({tp_pct:+.2f}%) [R/R: {rr}]<br>
                        <span style="font-size: 0.9em; color: #9ca3af;">→ Close {close_pct} | {desc}</span></div></div>""", unsafe_allow_html=True)
                        components.html(copy_button(str(tp_val), f"📋 TP{tp_num}"), height=40)
                    
                    all_text = f"Entry: {decision['entry_price']}, SL: {decision['stop_loss']}, TP1: {tp1:.2f}, TP2: {tp2:.2f}, TP3: {tp3:.2f}"
                    st.markdown("---")
                    components.html(copy_button(all_text, "📋 HEPSİNİ KOPYALA"), height=50)
                    st.info("**📈 Trailing Stop:** TP1 → SL'i entry'e | TP2 → SL'i TP1'e çek")
                else:
                    if decision['decision'] == 'NEUTRAL':
                        st.info("⏸️ **NEUTRAL:** Piyasa belirsiz - bekleyin.")
                    elif decision['decision'] == 'WAIT':
                        st.warning("⏳ **WAIT:** AI daha fazla veri bekliyor.")
            except Exception as e:
                st.error(f"❌ Hata: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

# TAB 2: WATCHLIST
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"### 🔍 Watchlist ({len(st.session_state.watchlist_coins)} Coins)")
    progress_bar = st.progress(0)
    watchlist_data = []
    for idx, coin in enumerate(st.session_state.watchlist_coins):
        price_data = get_binance_price(coin)
        signal_data = get_quick_signal(coin, interval, progress_bar, idx, len(st.session_state.watchlist_coins))
        if price_data['available']:
            coin_display = f"🔒 {coin.replace('USDT', '')}" if coin in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT'] else coin.replace('USDT', '')
            watchlist_data.append({'Coin': coin_display, 'Price': f"${price_data['price']:,.2f}",
                                   '24h %': f"{price_data['change_24h']:+.2f}%", 'Signal': signal_data['signal'],
                                   'Score': f"{signal_data['score']:.0f}/100"})
    progress_bar.empty()
    if watchlist_data:
        df = pd.DataFrame(watchlist_data)
        st.dataframe(df, use_container_width=True)
        st.markdown("---")
        st.markdown("**🔍 Detaylı Analiz:**")
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
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 3: COIN MANAGER
with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Coin Manager")
    st.info("💡 BTC+ETH+LTC sabit")
    new_coin = st.text_input("Coin (örn: SOL)")
    if st.button("➕ Ekle"):
        if new_coin:
            add_coin_to_watchlist(new_coin)
            st.rerun()
    st.markdown("---")
    for coin in st.session_state.watchlist_coins:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.markdown(f"**🔒 {coin}**" if coin in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT'] else f"**{coin}**")
        with col2:
            price_data = get_binance_price(coin)
            if price_data['available']:
                change_icon = '↗' if price_data['change_24h'] >= 0 else '↘'
                st.markdown(f"${price_data['price']:,.2f} ({price_data['change_24h']:+.2f}% {change_icon})")
        with col3:
            if coin not in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']:
                if st.button("🗑️", key=f"rm_{coin}"):
                    remove_coin_from_watchlist(coin)
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 4: TRADE HISTORY
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
    else:
        st.info("📊 Trade kaydı yok")
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 5: BACKTEST
with tab5:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 Backtest Engine")
    
    if not BACKTEST_AVAILABLE or not AI_AVAILABLE:
        st.error("❌ Backtest Engine veya AI Brain yüklenemedi!")
    else:
        st.info("💡 **Backtest:** AI stratejisini geçmiş verilerle test edin. Performans metriklerini görün.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            bt_lookback = st.selectbox("Test Süresi (Gün)", [7, 14, 30, 60], index=2, key='bt_lookback')
        with col2:
            bt_max_trades = st.number_input("Max Trades", min_value=10, max_value=200, value=50, step=10)
        with col3:
            bt_capital = st.number_input("Initial Capital ($)", min_value=1000, max_value=100000, value=10000, step=1000)
        
        if st.button("🚀 RUN BACKTEST", type="primary", use_container_width=True):
            with st.spinner(f"⏳ Backtest çalışıyor... {bt_lookback} günlük veri analiz ediliyor..."):
                try:
                    engine = BacktestEngine(selected_coin, bt_capital, risk)
                    results = engine.run_backtest(brain, interval, bt_lookback, bt_max_trades)
                    
                    if 'error' not in results:
                        st.session_state.backtest_results = results
                        st.success(f"✅ Backtest tamamlandı! {results['total_trades']} trade analiz edildi.")
                    else:
                        st.error(f"❌ Hata: {results['error']}")
                except Exception as e:
                    st.error(f"❌ Backtest hatası: {str(e)}")
        
        if st.session_state.backtest_results:
            results = st.session_state.backtest_results
            
            st.markdown("---")
            st.markdown("### 📈 Performance Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                wr_color = '#10b981' if results['win_rate'] >= 50 else '#ef4444'
                st.markdown(f"""<div class="stat-box" style="background: {wr_color};">
                <div style="color: white; opacity: 0.9;">Win Rate</div>
                <div class="stat-value" style="color: white;">{results['win_rate']:.1f}%</div>
                <div style="color: white; font-size: 0.85em;">{results['winning_trades']}W / {results['losing_trades']}L</div></div>""", unsafe_allow_html=True)
            
            with col2:
                pnl_color = '#10b981' if results['total_pnl'] >= 0 else '#ef4444'
                st.markdown(f"""<div class="stat-box" style="background: {pnl_color};">
                <div style="color: white; opacity: 0.9;">Total PNL</div>
                <div class="stat-value" style="color: white;">${results['total_pnl']:+,.2f}</div>
                <div style="color: white; font-size: 0.85em;">{results['total_pnl_pct']:+.2f}%</div></div>""", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""<div class="stat-box">
                <div style="color: white; opacity: 0.9;">Profit Factor</div>
                <div class="stat-value" style="color: white;">{results['profit_factor']:.2f}</div>
                <div style="color: white; font-size: 0.85em;">Sharpe: {results['sharpe_ratio']:.2f}</div></div>""", unsafe_allow_html=True)
            
            with col4:
                dd_color = '#ef4444' if results['max_drawdown'] < -10 else '#10b981'
                st.markdown(f"""<div class="stat-box" style="background: {dd_color};">
                <div style="color: white; opacity: 0.9;">Max Drawdown</div>
                <div class="stat-value" style="color: white;">{results['max_drawdown']:.2f}%</div>
                <div style="color: white; font-size: 0.85em;">Final: ${results['final_capital']:,.0f}</div></div>""", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 📈 Equity Curve")
            fig = create_equity_curve_chart(results['equity_curve'])
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 📜 Trade List")
            if not results['trades_df'].empty:
                st.dataframe(results['trades_df'][['timestamp', 'signal', 'entry_price', 'exit_price', 'pnl', 'pnl_pct', 'result']], use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("""<div style='text-align: center; color: #10b981; padding: 20px; background: #2d2d2d; border-radius: 12px;'>
<p><strong>🔱 DEMIR AI v8.0 - BACKTEST ENGINE COMPLETE</strong></p></div>""", unsafe_allow_html=True)
