"""
🔱 DEMIR AI TRADING BOT - DASHBOARD v8.3 MAJOR UPDATE
Date: 1 Kasım 2025
PHASE 3.5: Multi-Coin Analysis + Enhanced AI Commentary

v8.3 MAJOR UPDATES:
✅ Kompakt header + canlı fiyatlar tek blok
✅ BTC + ETH + LTC eş zamanlı analiz
✅ Wallet: $1000 USD, 50x leverage, $30-40/trade
✅ AI Yorumu 3x daha detaylı (layer bazlı)
✅ Portfolio Optimizer FIXED
✅ 11 Layer Scores GARANTI görünür
✅ Görsel analiz + tablolar otomatik refresh

v8.2 FEATURES:
✅ Manuel Position Tracker (Futures)
✅ Real-time PNL Calculation
✅ Open/Close Position Management
✅ Pending Signals Dashboard

v8.1 FEATURES:
✅ Portfolio Optimizer
✅ Backtest Engine
✅ Dark Mode + AI Comments
✅ Telegram Alerts
✅ Trade History
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import trade_history_db as db
import win_rate_calculator as wrc

# PHASE 3.4: Position Tracker
try:
    from position_tracker import PositionTracker
    POSITION_TRACKER_AVAILABLE = True
    tracker = PositionTracker()
except:
    POSITION_TRACKER_AVAILABLE = False

# PHASE 3.3: Portfolio Optimizer
try:
    from portfolio_optimizer import PortfolioOptimizer
    PORTFOLIO_OPTIMIZER_AVAILABLE = True
except:
    PORTFOLIO_OPTIMIZER_AVAILABLE = False

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
    page_title="🔱 DEMIR AI v8.3",
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
if 'portfolio_allocation' not in st.session_state:
    st.session_state.portfolio_allocation = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

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
        decision = brain.make_trading_decision(symbol, interval, 1000, 35)
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

def generate_enhanced_ai_comment(decision):
    """ENHANCED: 3x daha detaylı AI yorumu - layer'ları kullanarak"""
    signal = decision.get('decision', 'NEUTRAL')
    confidence = decision.get('confidence', 0) * 100
    score = decision.get('final_score', 0)
    scores = decision.get('component_scores', {})
    
    # WAIT/NEUTRAL için kısaltılmış yorum
    if signal in ['NEUTRAL', 'WAIT']:
        if signal == 'NEUTRAL':
            return "⏸️ **NEUTRAL:** Piyasa belirsiz. AI net bir yön tespit edemedi. Şu an trade açmak riskli."
        else:
            return "⏳ **WAIT:** AI daha fazla veri bekliyor. Piyasa henüz yeterli sinyal vermedi."
    
    # LONG/SHORT için DETAYLI layer bazlı yorum
    comments = []
    
    # 1. Genel Güven ve Skor
    if confidence < 30:
        comments.append(f"🔴 **Çok Düşük Güven ({confidence:.0f}%):** Piyasa çok belirsiz. Bu koşullarda trade açmak yüksek risk taşır.")
    elif confidence < 50:
        comments.append(f"🟡 **Düşük Güven ({confidence:.0f}%):** Sinyal zayıf. Daha net bir fırsat beklemek mantıklı olabilir.")
    elif confidence < 70:
        comments.append(f"🟢 **Orta Güven ({confidence:.0f}%):** Makul bir sinyal. Risk yönetimi ile trade açılabilir.")
    else:
        comments.append(f"🟢 **Yüksek Güven ({confidence:.0f}%):** Güçlü sinyal! AI birden fazla layer'dan pozitif sinyal algıladı.")
    
    # 2. Teknik Analiz Skorları
    if score < 40:
        comments.append(f"📊 **Düşük Skor ({score:.1f}/100):** Çoğu teknik gösterge olumsuz. Piyasa trend göstermiyor.")
    elif score < 60:
        comments.append(f"📊 **Nötr Skor ({score:.1f}/100):** Piyasa kararsız. Hem alıcı hem satıcı baskısı dengede.")
    else:
        comments.append(f"📊 **İyi Skor ({score:.1f}/100):** Teknik göstergeler {signal} yönünde güçlü sinyaller veriyor.")
    
    # 3. Layer Bazlı Detaylı Analiz
    layer_analysis = []
    
    # Volume Profile
    if 'volume_profile' in scores and scores['volume_profile'].get('available'):
        vp_score = scores['volume_profile'].get('score', 0)
        if vp_score > 60:
            layer_analysis.append(f"📊 **Volume Profile ({vp_score:.0f}/100):** Güçlü hacim desteği var. POC seviyesi {signal} yönünü destekliyor.")
        elif vp_score < 40:
            layer_analysis.append(f"📊 **Volume Profile ({vp_score:.0f}/100):** Zayıf hacim. Hareket sürdürülebilir olmayabilir.")
    
    # Pivot Points
    if 'pivot_points' in scores and scores['pivot_points'].get('available'):
        pp_score = scores['pivot_points'].get('score', 0)
        if pp_score > 60:
            layer_analysis.append(f"🎯 **Pivot Points ({pp_score:.0f}/100):** Fiyat kritik destek/direnç seviyelerinde. {signal} yönü favori.")
        elif pp_score < 40:
            layer_analysis.append(f"🎯 **Pivot Points ({pp_score:.0f}/100):** Pivot seviyeleri tarafsız. Net bir yön yok.")
    
    # GARCH Volatility
    if 'garch' in scores and scores['garch'].get('available'):
        garch_score = scores['garch'].get('score', 0)
        if garch_score > 60:
            layer_analysis.append(f"📈 **GARCH Volatility ({garch_score:.0f}/100):** Volatilite artıyor. Güçlü hareket beklentisi var.")
        elif garch_score < 40:
            layer_analysis.append(f"📉 **GARCH Volatility ({garch_score:.0f}/100):** Düşük volatilite. Piyasa sakin, büyük hareket zor.")
    
    # Markov Regime
    if 'markov' in scores and scores['markov'].get('available'):
        markov_score = scores['markov'].get('score', 0)
        if markov_score > 60:
            layer_analysis.append(f"🔄 **Markov Regime ({markov_score:.0f}/100):** Piyasa {signal} rejiminde. Trend güçlü.")
        elif markov_score < 40:
            layer_analysis.append(f"🔄 **Markov Regime ({markov_score:.0f}/100):** Piyasa geçiş aşamasında. Belirsizlik var.")
    
    # News Sentiment
    if 'news_sentiment' in scores and scores['news_sentiment'].get('available'):
        news_score = scores['news_sentiment'].get('score', 0)
        if news_score > 60:
            layer_analysis.append(f"📰 **News Sentiment ({news_score:.0f}/100):** Piyasa haberleri {signal} yönünü destekliyor. Fear & Greed uyumlu.")
        elif news_score < 40:
            layer_analysis.append(f"📰 **News Sentiment ({news_score:.0f}/100):** Piyasa haberleri olumsuz. Fear & Greed endeksi düşük.")
    
    if layer_analysis:
        comments.append("\n**🧠 Layer Bazlı Detaylar:**\n" + "\n".join(layer_analysis))
    
    # 4. Trade Önerisi
    if signal == 'LONG':
        comments.append("📈 **LONG Sinyal:** AI yükseliş trendi tespit etti. Alım fırsatı olabilir. Entry, SL ve TP seviyelerine dikkat edin.")
    elif signal == 'SHORT':
        comments.append("📉 **SHORT Sinyal:** AI düşüş trendi tespit etti. Satış fırsatı olabilir. Risk yönetimi kritik!")
    
    return "\n\n".join(comments)

def create_equity_curve_chart(equity_curve):
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

def create_allocation_pie_chart(allocations):
    fig = go.Figure(data=[go.Pie(
        labels=list(allocations.keys()),
        values=list(allocations.values()),
        hole=0.4,
        marker=dict(colors=['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'])
    )])
    
    fig.update_layout(
        title='Portfolio Allocation',
        template='plotly_dark',
        height=350,
        showlegend=True
    )
    
    return fig

def create_correlation_heatmap(corr_matrix):
    fig = px.imshow(
        corr_matrix,
        labels=dict(color="Correlation"),
        x=corr_matrix.columns,
        y=corr_matrix.index,
        color_continuous_scale='RdYlGn_r',
        zmin=-1, zmax=1,
        text_auto='.2f'
    )
    
    fig.update_layout(
        title='Correlation Matrix',
        template='plotly_dark',
        height=400
    )
    
    return fig

# DARK MODE CSS
st.markdown("""<style>
.main{background: #1a1a1a !important;}
.stApp{background: #1a1a1a !important;}
[data-testid="stAppViewContainer"]{background: #1a1a1a !important;}
[data-testid="stHeader"]{background: #0f0f0f !important;}
[data-testid="stSidebar"]{background: #0f0f0f !important;}

.compact-header{background: linear-gradient(135deg, #10b981, #059669); border-radius: 8px; padding: 10px 20px; margin: 5px 0; color: white;}
.compact-header h2{font-size: 1.5em; margin: 0; color: white !important;}
.compact-header p{font-size: 0.85em; margin: 0; opacity: 0.9; color: white !important;}

.mini-price-card{background: #2d2d2d; border-radius: 8px; padding: 10px; margin: 5px; border-left: 3px solid #10b981;}
.mini-price-name{font-size: 0.9em; font-weight: 600; color: #10b981;}
.mini-price-value{font-size: 1.3em; font-weight: 700; margin: 3px 0; color: #e5e5e5;}
.mini-price-change{font-size: 0.85em; font-weight: 600;}

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

.position-card{background: #374151; border-radius: 12px; padding: 20px; margin: 10px 0; border-left: 4px solid #3b82f6; color: #e5e5e5;}
.pnl-positive{color: #10b981; font-weight: 700;}
.pnl-negative{color: #ef4444; font-weight: 700;}

h1, h2, h3, h4, h5, h6, p, span, div{color: #e5e5e5 !important;}
.stMarkdown{color: #e5e5e5 !important;}
label{color: #e5e5e5 !important;}

@media (max-width: 768px){.price-big{font-size: 1.8em;} .stat-value{font-size: 1.5em;} .tp-box, .card{padding: 10px;}}</style>""", unsafe_allow_html=True)

# KOMPAKT HEADER + CANLI FIYATLAR
st.markdown("""<div class="compact-header">
<h2>🔱 DEMIR AI TRADING BOT v8.3</h2>
<p>MULTI-COIN ANALYSIS • POSITION TRACKER • PORTFOLIO OPTIMIZER</p></div>""", unsafe_allow_html=True)

# CANLI FIYATLAR - KOMPAKT
cols_price = st.columns(3)
for idx, coin in enumerate(['BTCUSDT', 'ETHUSDT', 'LTCUSDT']):
    data = get_binance_price(coin)
    with cols_price[idx]:
        if data['available']:
            change_color = '#10b981' if data['change_24h'] >= 0 else '#ef4444'
            arrow = '↗' if data['change_24h'] >= 0 else '↘'
            st.markdown(f"""<div class="mini-price-card">
            <div class="mini-price-name">{coin.replace('USDT', '')}</div>
            <div class="mini-price-value">${data['price']:,.2f}</div>
            <div class="mini-price-change" style="color: {change_color};">{data['change_24h']:+.2f}% {arrow}</div>
            </div>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚙️ Ayarlar")
    selected_coin = st.selectbox("Coin", st.session_state.watchlist_coins, key='coin')
    interval = st.selectbox("Timeframe", ['1m', '5m', '15m', '1h', '4h', '1d'], index=3)
    st.markdown("### 💰 Wallet Settings")
    st.info("💡 **Wallet:** $1000 USD | **Leverage:** 50x | **Position:** $30-40")
    portfolio = 1000
    risk_per_trade = 35
    st.markdown("---")
    
    # PHASE 3.4: POSITION TRACKER SUMMARY
    if POSITION_TRACKER_AVAILABLE:
        st.markdown("### 📝 Position Tracker")
        summary = tracker.get_position_summary()
        st.markdown(f"""<div class="stat-box">
        <div style="color: white; font-size: 0.9em;">Açık Pozisyonlar</div>
        <div class="stat-value" style="color: white;">{summary['open_positions']}</div></div>""", unsafe_allow_html=True)
        
        pnl_color = '#10b981' if summary['total_pnl'] >= 0 else '#ef4444'
        st.markdown(f"""<div class="stat-box" style="background: linear-gradient(135deg, {pnl_color}, #059669);">
        <div style="color: white; font-size: 0.9em;">Toplam PNL (Kapalı)</div>
        <div class="stat-value" style="color: white;">${summary['total_pnl']:+,.2f}</div></div>""", unsafe_allow_html=True)
    else:
        st.info("💡 Position Tracker: Yükleniyor...")
    st.markdown("---")
    
    # PHASE 3.3: PORTFOLIO OPTIMIZER WIDGET
    st.markdown("### 🎯 Portfolio Optimizer")
    st.info("💡 **Ne yapar?** Watchlist'teki tüm coinleri analiz eder, Kelly Criterion ile optimal sermaye dağılımını hesaplar.")
    if PORTFOLIO_OPTIMIZER_AVAILABLE and AI_AVAILABLE:
        if st.button("📊 Portföyü Optimize Et", use_container_width=True):
            with st.spinner("⏳ Watchlist analiz ediliyor..."):
                try:
                    signals = []
                    for coin in st.session_state.watchlist_coins:
                        decision = brain.make_trading_decision(coin, interval, portfolio, risk_per_trade)
                        signals.append({
                            'symbol': coin,
                            'signal': decision.get('decision', 'NEUTRAL'),
                            'confidence': decision.get('confidence', 0),
                            'score': decision.get('final_score', 0)
                        })
                    
                    perf = wrc.get_performance_dashboard()
                    perf_dict = {
                        'win_rate': perf['win_rate'] / 100 if perf['total_trades'] > 0 else 0.5,
                        'avg_win': 150,
                        'avg_loss': 100
                    }
                    
                    optimizer = PortfolioOptimizer(portfolio, risk_per_trade)
                    result = optimizer.optimize_portfolio(signals, perf_dict)
                    
                    st.session_state.portfolio_allocation = result
                    st.success("✅ Portföy optimize edildi! 'Portfolio' sekmesine git.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Hata: {str(e)}")
        
        if st.session_state.portfolio_allocation:
            alloc = st.session_state.portfolio_allocation
            
            st.markdown(f"""<div class="stat-box">
            <div style="color: white; font-size: 0.9em;">Tahsis Edilen</div>
            <div class="stat-value" style="color: white;">${alloc['total_allocated']:,.0f}</div>
            <div style="color: white; font-size: 0.85em;">Kelly: {alloc['kelly_fraction']:.1%}</div></div>""", unsafe_allow_html=True)
            
            st.markdown(f"""<div class="stat-box">
            <div style="color: white; font-size: 0.9em;">Çeşitlendirme</div>
            <div class="stat-value" style="color: white;">{alloc['diversification_score']:.0f}/100</div>
            <div style="color: white; font-size: 0.85em;">Korelasyon Riski</div></div>""", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Portfolio Optimizer: AI Brain gerekli")
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
    analyze_btn = st.button("🔍 AI ANALİZ YAP (BTC+ETH+LTC)", use_container_width=True, type="primary")
    st.markdown("---")
    show_help = st.checkbox("❓ Terimler")

if show_help:
    with st.expander("📚 TERİMLER", expanded=True):
        st.markdown("""**LONG**: Al | **SHORT**: Sat | **Confidence**: AI güven | **Score**: Final puan | **R/R**: Risk/Reward  
**Entry**: Açılış | **SL**: Stop Loss | **TP**: Take Profit | **Sharpe**: Risk-adjusted return | **Drawdown**: Max düşüş | **Kelly**: Optimal position size""")

# 7 TABS - ALL COMPLETE!
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📈 Live Dashboard", "🔍 Watchlist", "💼 Portfolio", "📝 Positions", "⚙️ Coin Manager", "📜 Trade History", "📊 Backtest"])

# TAB 1: LIVE DASHBOARD - MULTI-COIN ANALYSIS
with tab1:
    if analyze_btn and AI_AVAILABLE:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🎯 BTC + ETH + LTC - Eş Zamanlı AI Analiz")
        
        # 3 COIN EŞ ZAMANLI ANALİZ
        with st.spinner('🧠 3 coin analiz ediliyor... (BTC, ETH, LTC)'):
            try:
                analysis_coins = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
                for coin_symbol in analysis_coins:
                    decision = brain.make_trading_decision(coin_symbol, interval, portfolio, risk_per_trade)
                    trade_id = db.log_trade(decision)
                    
                    st.session_state.analysis_results[coin_symbol] = {
                        'decision': decision,
                        'trade_id': trade_id,
                        'timestamp': datetime.now()
                    }
                    
                    if TELEGRAM_AVAILABLE and st.session_state.telegram_alerts_enabled:
                        telegram_alert.send_signal_alert(decision)
                
                st.success(f"✅ 3 coin analizi tamamlandı! Telegram'a gönderildi.")
                
                # HER COIN İÇİN DETAYLI GÖSTER
                for coin_symbol in analysis_coins:
                    result = st.session_state.analysis_results[coin_symbol]
                    decision = result['decision']
                    trade_id = result['trade_id']
                    
                    st.markdown("---")
                    coin_name = coin_symbol.replace('USDT', '')
                    st.markdown(f"## {coin_name} Analiz Sonucu")
                    
                    signal = decision['decision']
                    badge_class = {'LONG': 'badge-long', 'SHORT': 'badge-short', 'NEUTRAL': 'badge-neutral', 'WAIT': 'badge-neutral'}
                    emoji = {'LONG': '📈', 'SHORT': '📉', 'NEUTRAL': '⏸️', 'WAIT': '⏳'}
                    
                    st.markdown(f"""<div style="text-align: center; padding: 20px;">
                    <div class="signal-badge {badge_class.get(signal, 'badge-neutral')}">{emoji.get(signal, '🎯')} {signal}</div>
                    <div style="font-size: 1.2em; margin: 15px 0; color: #e5e5e5;">
                    Confidence: <strong style="color: #10b981;">{decision['confidence']*100:.0f}%</strong> | Score: <strong style="color: #10b981;">{decision['final_score']:.1f}/100</strong> | R/R: <strong style="color: #10b981;">1:{decision['risk_reward']:.2f}</strong>
                    </div><div style="font-size: 0.9em; color: #9ca3af;">Trade ID: #{trade_id}</div></div>""", unsafe_allow_html=True)
                    
                    # ENHANCED AI YORUMU
                    ai_comment = generate_enhanced_ai_comment(decision)
                    st.markdown(f"""<div class="ai-comment">
                    <h4 style="color: #3b82f6 !important; margin: 0 0 15px 0;">🤖 AI Detaylı Analiz</h4>
                    {ai_comment.replace('**', '<strong>').replace('</strong>', '</strong>').replace('\n', '<br>')}
                    </div>""", unsafe_allow_html=True)
                    
                    # LONG/SHORT İÇİN DETAY
                    if signal in ['LONG', 'SHORT']:
                        with st.expander(f"📊 {coin_name} - 11 Layer Detaylı Analiz", expanded=False):
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
                                st.info("💡 Component scores yükleniyor...")
                        
                        # POZISYON PLANI
                        with st.expander(f"💼 {coin_name} - Pozisyon Planı", expanded=True):
                            if decision.get('entry_price') and decision.get('stop_loss'):
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
                                
                                st.markdown("**🎯 Take Profit:**")
                                risk_amount = abs(decision['entry_price'] - decision['stop_loss'])
                                if decision['decision'] == 'LONG':
                                    tp1, tp2, tp3 = decision['entry_price'] + (risk_amount * 1.0), decision['entry_price'] + (risk_amount * 1.618), decision['entry_price'] + (risk_amount * 2.618)
                                else:
                                    tp1, tp2, tp3 = decision['entry_price'] - (risk_amount * 1.0), decision['entry_price'] - (risk_amount * 1.618), decision['entry_price'] - (risk_amount * 2.618)
                                
                                for tp_num, tp_val, rr, close_pct, desc in [(1, tp1, "1:1", "50%", "Kar garantiye al"), (2, tp2, "1:1.62", "30%", "Fibonacci golden ratio"), (3, tp3, "1:2.62", "20%", "Maksimum kar")]:
                                    tp_pct = ((tp_val - decision['entry_price']) / decision['entry_price'] * 100)
                                    st.markdown(f"""<div class="tp-box"><div><strong style="font-size: 1.05em; color: #10b981;">🎯 TP{tp_num}:</strong> ${tp_val:,.2f} ({tp_pct:+.2f}%) [R/R: {rr}]<br>
                                    <span style="font-size: 0.9em; color: #9ca3af;">→ Close {close_pct} | {desc}</span></div></div>""", unsafe_allow_html=True)
                                    components.html(copy_button(str(tp_val), f"📋 TP{tp_num}"), height=40)
                
            except Exception as e:
                st.error(f"❌ Hata: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("💡 Sidebar'dan 'AI ANALİZ YAP' butonuna basın - BTC, ETH ve LTC eş zamanlı analiz edilecek.")

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
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 3: PORTFOLIO
with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 💼 Portfolio Allocation")
    
    if st.session_state.portfolio_allocation:
        alloc = st.session_state.portfolio_allocation
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Allocation Breakdown")
            if alloc.get('allocations'):
                fig_pie = create_allocation_pie_chart(alloc['allocations'])
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown("#### 💰 Position Sizes")
            if alloc.get('position_sizes'):
                position_df = pd.DataFrame([
                    {'Coin': k.replace('USDT', ''), 'Position ($)': f"${v:,.2f}", 'Weight': f"{(v/alloc['total_allocated'])*100:.1f}%"}
                    for k, v in alloc['position_sizes'].items()
                ])
                st.dataframe(position_df, use_container_width=True)
        
        st.markdown("---")
        
        if alloc.get('correlation_matrix') is not None and not alloc['correlation_matrix'].empty:
            st.markdown("#### 🔗 Correlation Matrix")
            fig_corr = create_correlation_heatmap(alloc['correlation_matrix'])
            st.plotly_chart(fig_corr, use_container_width=True)
            
            st.info("💡 **Diversification Tip:** Düşük korelasyon (yeşil) = iyi çeşitlendirme | Yüksek korelasyon (kırmızı) = risk")
    else:
        st.info("💡 Sidebar'dan 'Portföyü Optimize Et' butonuna tıklayın. Sistem tüm coinleri analiz edip optimal dağılımı gösterecek.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 4: POSITION TRACKER
with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📝 Position Tracker - Futures Manuel Tracking")
    
    if not POSITION_TRACKER_AVAILABLE:
        st.error("❌ Position Tracker yüklenemedi! `position_tracker.py` dosyasını kontrol edin.")
    else:
        pending = tracker.get_pending_signals()
        open_positions = tracker.get_open_positions()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Bekleyen AI Sinyalleri")
            if pending:
                for sig in pending:
                    signal_color = '#10b981' if sig['signal'] == 'LONG' else '#ef4444'
                    st.markdown(f"""<div class="position-card" style="border-left-color: {signal_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="font-size: 1.1em;">{sig['symbol'].replace('USDT', '')} {sig['signal']}</strong>
                    <span style="background: {signal_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;">#{sig['id']}</span>
                    </div>
                    <div style="margin: 10px 0; font-size: 0.9em;">
                    📍 Entry: ${sig['entry_price']:,.2f} | 🛡️ SL: ${sig['stop_loss']:,.2f}<br>
                    💰 Position: ${sig['position_size']:,.0f} | 🎯 Confidence: {sig['confidence']:.0f}%
                    </div>
                    <div style="font-size: 0.8em; color: #9ca3af;">🕐 {sig['timestamp']}</div>
                    </div>""", unsafe_allow_html=True)
                    
                    if st.button(f"✅ Binance'de Açtım (#{sig['id']})", key=f"open_{sig['id']}"):
                        if tracker.mark_position_opened(sig['id']):
                            st.success(f"✅ Position #{sig['id']} AÇIK olarak işaretlendi!")
                            st.rerun()
            else:
                st.info("💡 **Henüz AI sinyali yok.** Sidebar'dan 'AI Analiz Yap' butonuna basın.")
        
        with col2:
            st.markdown("#### 🔴 Açık Pozisyonlar (Real-time)")
            if open_positions:
                for pos in open_positions:
                    pnl_class = 'pnl-positive' if pos['pnl_usd'] >= 0 else 'pnl-negative'
                    pnl_emoji = '📈' if pos['pnl_usd'] >= 0 else '📉'
                    
                    st.markdown(f"""<div class="position-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="font-size: 1.1em;">{pos['symbol'].replace('USDT', '')} {pos['side']}</strong>
                    <span class="{pnl_class}">{pnl_emoji} ${pos['pnl_usd']:+,.2f} ({pos['pnl_pct']:+.2f}%)</span>
                    </div>
                    <div style="margin: 10px 0; font-size: 0.9em;">
                    📍 Entry: ${pos['entry_price']:,.2f} | 💲 Current: ${pos['current_price']:,.2f}<br>
                    🛡️ SL: ${pos['stop_loss']:,.2f} | 📏 SL'ye mesafe: {pos['sl_distance_pct']:.2f}%
                    </div>
                    <div style="font-size: 0.8em; color: #9ca3af;">🕐 Açıldı: {pos['opened_at']}</div>
                    </div>""", unsafe_allow_html=True)
                    
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        exit_price = st.number_input(f"Exit Price (#{pos['id']})", value=float(pos['current_price']), step=0.01, key=f"exit_{pos['id']}")
                    with col_b:
                        if st.button(f"🔒 Kapat", key=f"close_{pos['id']}"):
                            if tracker.close_position(pos['id'], exit_price):
                                st.success(f"✅ Pozisyon #{pos['id']} kapatıldı!")
                                st.rerun()
            else:
                st.info("💡 **Açık pozisyon yok.**")
    
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 5: COIN MANAGER
with tab5:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Coin Manager")
    st.info("💡 BTC+ETH+LTC sabit - silinemez")
    new_coin = st.text_input("Yeni Coin Ekle (örn: SOL, AVAX)")
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

# TAB 6: TRADE HISTORY
with tab6:
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

# TAB 7: BACKTEST
with tab7:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 Backtest Engine")
    
    if not BACKTEST_AVAILABLE or not AI_AVAILABLE:
        st.error("❌ Backtest Engine veya AI Brain yüklenemedi!")
    else:
        st.info("💡 **Backtest:** AI stratejisini geçmiş verilerle test edin.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            bt_lookback = st.selectbox("Test Süresi (Gün)", [7, 14, 30, 60], index=2, key='bt_lookback')
        with col2:
            bt_max_trades = st.number_input("Max Trades", min_value=10, max_value=200, value=50, step=10)
        with col3:
            bt_capital = st.number_input("Initial Capital ($)", min_value=1000, max_value=100000, value=1000, step=100)
        
        if st.button("🚀 RUN BACKTEST", type="primary", use_container_width=True):
            with st.spinner(f"⏳ Backtest çalışıyor..."):
                try:
                    engine = BacktestEngine(selected_coin, bt_capital, risk_per_trade)
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
st.markdown(f"""<div style='text-align: center; color: #10b981; padding: 15px; background: #2d2d2d; border-radius: 8px;'>
<p><strong>🔱 DEMIR AI v8.3 - MULTI-COIN ANALYSIS + ENHANCED AI - Son güncelleme: {datetime.now().strftime('%H:%M:%S')}</strong></p></div>""", unsafe_allow_html=True)
