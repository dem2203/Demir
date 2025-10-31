"""
🔱 DEMIR AI TRADING BOT - DASHBOARD v6.1
OPTIMIZED: Hızlı Watchlist + Detaylı AI + Better UX
Tarih: 1 Kasım 2025

YENİ İYİLEŞTİRMELER (v6 → v6.1):
✅ Watchlist progress bar (10 coin hızlı)
✅ Component scores her zaman göster
✅ Daha iyi error handling
✅ Auto-refresh optimizasyonu
✅ UI/UX polish (daha temiz görünüm)

MEVCUT ÖZELLİKLER:
✅ Multi-Coin Watchlist (10 coin)
✅ One-Click Copy (Entry/SL/TP)
✅ Mobile Responsive
✅ 11 Layer detaylı analiz
✅ Trade History + Performance tracking
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime
import time
import pandas as pd

# Phase 1 imports
import trade_history_db as db
import win_rate_calculator as wrc

# AI Brain import
try:
    import ai_brain as brain
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

# ============================================================================
# Page Config
# ============================================================================
st.set_page_config(
    page_title="🔱 DEMIR AI Dashboard v6.1",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Helper Functions
# ============================================================================
def get_binance_price(symbol):
    """Binance'den canlı fiyat çek"""
    try:
        url = f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'price': float(data['lastPrice']),
                'change_24h': float(data['priceChangePercent']),
                'volume': float(data['quoteVolume']),
                'high_24h': float(data['highPrice']),
                'low_24h': float(data['lowPrice']),
                'available': True
            }
    except Exception as e:
        st.error(f"⚠️ Fiyat çekilemedi ({symbol}): {str(e)}")
    return {'price': 0, 'change_24h': 0, 'volume': 0, 'high_24h': 0, 'low_24h': 0, 'available': False}

def get_quick_signal(symbol, interval='1h', progress_bar=None, current_idx=0, total=10):
    """Hızlı AI sinyali al (progress bar ile)"""
    try:
        if progress_bar:
            progress_bar.progress((current_idx + 1) / total, f"Analyzing {symbol}... ({current_idx + 1}/{total})")
        
        if not AI_AVAILABLE:
            return {'signal': 'N/A', 'score': 0, 'confidence': 0}
        
        decision = brain.make_trading_decision(
            symbol=symbol,
            interval=interval,
            portfolio_value=10000,
            risk_per_trade=200
        )
        
        return {
            'signal': decision.get('decision', 'NEUTRAL'),
            'score': decision.get('final_score', 0),
            'confidence': decision.get('confidence', 0) * 100
        }
    except Exception as e:
        st.warning(f"⚠️ {symbol} analiz hatası: {str(e)}")
        return {'signal': 'ERROR', 'score': 0, 'confidence': 0}

def render_progress_bar(value, max_val=100, color='#667eea'):
    """Progress bar HTML"""
    pct = (value / max_val) * 100
    return f"""
    <div style="background: #f0f0f0; border-radius: 10px; height: 20px; overflow: hidden; margin: 5px 0;">
        <div style="background: {color}; width: {pct}%; height: 100%; border-radius: 10px; 
                    display: flex; align-items: center; justify-content: center; color: white; font-size: 0.75em; font-weight: 600;">
            {value:.1f}
        </div>
    </div>
    """

def copy_to_clipboard_button(text, label="📋 Kopyala", key=None):
    """Clipboard'a kopyalama butonu"""
    copy_js = f"""
    <button onclick="navigator.clipboard.writeText('{text}').then(function() {{
        alert('✅ Kopyalandı: {text}');
    }}, function(err) {{
        alert('❌ Kopyalama hatası');
    }});" 
    style="background: linear-gradient(135deg, #667eea, #764ba2); 
           color: white; 
           border: none; 
           padding: 6px 12px; 
           border-radius: 6px; 
           cursor: pointer; 
           font-size: 0.85em;
           font-weight: 600;
           margin: 2px;">
        {label}
    </button>
    """
    return copy_js

# ============================================================================
# CSS (Mobile Responsive + Polished)
# ============================================================================
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .price-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    .price-big {
        font-size: 2.5em;
        font-weight: 700;
        margin: 10px 0;
    }
    .price-detail {
        display: flex;
        justify-content: space-between;
        margin: 5px 0;
        font-size: 0.9em;
        opacity: 0.9;
    }
    .tp-box {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }
    .stat-box {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
        text-align: center;
    }
    .stat-value {
        font-size: 1.8em;
        font-weight: 700;
    }
    .layer-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    .signal-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 1.1em;
    }
    .badge-long {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }
    .badge-short {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
    }
    .badge-neutral {
        background: linear-gradient(135deg, #6b7280, #4b5563);
        color: white;
    }
    
    /* ✅ Mobile Responsive */
    @media (max-width: 768px) {
        .price-big {
            font-size: 1.8em;
        }
        .stat-value {
            font-size: 1.5em;
        }
        .tp-box {
            padding: 10px;
        }
        .card {
            padding: 15px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Header
# ============================================================================
st.markdown("""
<div class="card" style="text-align: center;">
    <h1 style="color: #667eea; margin: 0;">🔱 DEMIR AI TRADING BOT v6.1</h1>
    <p style="color: #666;">OPTIMIZED: Hızlı Watchlist + Detaylı AI + Better UX</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar
# ============================================================================
with st.sidebar:
    st.markdown("## ⚙️ Ayarlar")
    
    selected_coin = st.selectbox("Coin Seç", ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'BNBUSDT', 'SOLUSDT', 
                                                'ADAUSDT', 'DOGEUSDT', 'XRPUSDT', 'DOTUSDT', 'MATICUSDT'], key='coin')
    interval = st.selectbox("Timeframe", ['1m', '5m', '15m', '1h', '4h', '1d'], index=3)
    
    st.markdown("### 💰 Portfolio")
    portfolio = st.number_input("Portfolio ($)", value=10000, step=100)
    risk = st.number_input("Risk per Trade ($)", value=200, step=10)
    
    st.markdown("---")
    
    # Performance Dashboard Widget
    st.markdown("### 📊 Performance")
    
    perf = wrc.get_performance_dashboard()
    
    if perf['total_trades'] > 0:
        # Win Rate
        win_rate_color = '#10b981' if perf['win_rate'] >= 50 else '#ef4444'
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg, {win_rate_color}, #38ef7d);">
            <div style="font-size: 0.9em; opacity: 0.9;">Win Rate</div>
            <div class="stat-value">{perf['win_rate']:.1f}%</div>
            <div style="font-size: 0.85em;">{perf['winning_trades']}W / {perf['losing_trades']}L</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Total PNL
        pnl_color = '#10b981' if perf['total_pnl_usd'] >= 0 else '#ef4444'
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg, {pnl_color}, #667eea);">
            <div style="font-size: 0.9em; opacity: 0.9;">Total PNL</div>
            <div class="stat-value">${perf['total_pnl_usd']:,.2f}</div>
            <div style="font-size: 0.85em;">{perf['total_trades']} Trades</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sharpe Ratio
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg, #667eea, #764ba2);">
            <div style="font-size: 0.9em; opacity: 0.9;">Sharpe Ratio</div>
            <div class="stat-value">{perf['sharpe_ratio']:.2f}</div>
            <div style="font-size: 0.85em;">Profit Factor: {perf['profit_factor']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("📊 Henüz trade kaydı yok")
    
    st.markdown("---")
    
    # Analyze button
    analyze_btn = st.button("🔍 AI ANALİZ YAP", use_container_width=True, type="primary")
    
    # ✅ YARDIM BUTONU
    st.markdown("---")
    show_help = st.checkbox("❓ Terimler Rehberi", help="Tüm terimlerin açıklamasını göster")

# ============================================================================
# YARDIM/GLOSSARY EXPANDER
# ============================================================================
if show_help:
    with st.expander("📚 TERİMLER KILAVUZU", expanded=True):
        st.markdown("""
        ### 🎯 Temel Terimler
        
        **LONG**: Al (fiyat yükselecek) - Fiyat artarsa kazanırsın  
        **SHORT**: Sat (fiyat düşecek) - Fiyat düşerse kazanırsın  
        **Confidence**: AI'ın ne kadar emin (≥70% = güçlü, <50% = zayıf)  
        **Score**: AI'ın final puanı (≥65=LONG, ≤35=SHORT, 35-65=NEUTRAL)  
        **R/R**: Risk/Reward (1:2 = $1 risk → $2 kazanç)  
        
        ### 💼 Pozisyon Planı
        
        **Entry**: Trade açma fiyatı  
        **SL (Stop Loss)**: Zarar durdur - fiyat buraya gelirse kapat  
        **Position**: Trade için toplam yatırım ($)  
        **Risk**: Maksimum kaybedebileceğin para  
        
        ### 🎯 Take Profit (TP)
        
        **TP1**: İlk kar al (1:1) → %50 pozisyon kapat  
        **TP2**: İkinci kar al (1:1.62 Fibonacci) → %30 kapat  
        **TP3**: Üçüncü kar al (1:2.62) → %20 kapat  
        
        ### 📊 Performance Metrikleri
        
        **Win Rate**: Kazanan trade % (≥60% = mükemmel)  
        **Sharpe Ratio**: Risk-adjusted getiri (>3 = profesyonel)  
        **Profit Factor**: Toplam kar / Toplam zarar (>2 = çok iyi)  
        
        Daha fazla detay: **GLOSSARY_DASHBOARD_TR.md**
        """)

# ============================================================================
# Main Content - Tabs
# ============================================================================
tab1, tab2, tab3 = st.tabs(["📈 Live Dashboard", "🔍 Multi-Coin Watchlist", "📜 Trade History"])

# ============================================================================
# TAB 1: Live Dashboard
# ============================================================================
with tab1:
    # ✅ CANLI FİYATLAR
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 Canlı Fiyatlar")
    
    cols = st.columns(3)
    coins = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
    
    for idx, coin in enumerate(coins):
        data = get_binance_price(coin)
        
        with cols[idx]:
            if data['available']:
                change_color = '#10b981' if data['change_24h'] >= 0 else '#ef4444'
                arrow = '↗' if data['change_24h'] >= 0 else '↘'
                
                st.markdown(f"""
                <div class="price-card">
                    <div style="font-size: 1.2em; font-weight: 600; opacity: 0.9;">{coin.replace('USDT', '')}</div>
                    <div class="price-big">${data['price']:,.2f}</div>
                    <div style="color: white; font-weight: 700; font-size: 1.2em; margin: 10px 0;">
                        {data['change_24h']:+.2f}% {arrow}
                    </div>
                    <div class="price-detail">
                        <span>24h High:</span>
                        <span>${data['high_24h']:,.2f}</span>
                    </div>
                    <div class="price-detail">
                        <span>24h Low:</span>
                        <span>${data['low_24h']:,.2f}</span>
                    </div>
                    <div class="price-detail" style="margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px;">
                        <span>Volume:</span>
                        <span>${data['volume']/1e6:.1f}M</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"<div style='text-align: center; color: white; font-size: 0.9em; margin-top: 10px;'>Son güncelleme: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ✅ AI ANALİZ SONUCU (ALWAYS SHOW COMPONENT SCORES!)
    if analyze_btn and AI_AVAILABLE:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🎯 AI Analiz Sonucu")
        
        with st.spinner('🧠 AI analizi yapılıyor... (11 layer hesaplanıyor)'):
            try:
                decision = brain.make_trading_decision(
                    symbol=selected_coin,
                    interval=interval,
                    portfolio_value=portfolio,
                    risk_per_trade=risk
                )
                
                # ✅ Database'e kaydet
                trade_id = db.log_trade(decision)
                st.session_state.last_decision = decision
                
                # ✅ Signal Badge
                signal = decision['decision']
                signal_emoji = {'LONG': '📈', 'SHORT': '📉', 'NEUTRAL': '⏸️', 'WAIT': '⏳'}
                badge_class = {
                    'LONG': 'badge-long',
                    'SHORT': 'badge-short',
                    'NEUTRAL': 'badge-neutral',
                    'WAIT': 'badge-neutral'
                }
                
                st.markdown(f"""
                <div style="text-align: center; padding: 30px;">
                    <div class="signal-badge {badge_class.get(signal, 'badge-neutral')}">
                        {signal_emoji.get(signal, '🎯')} {signal} {decision['signal']}
                    </div>
                    <div style="font-size: 1.3em; margin: 20px 0; color: #333;">
                        Confidence: <strong>{decision['confidence']*100:.0f}%</strong> | 
                        Score: <strong>{decision['final_score']:.1f}/100</strong> | 
                        R/R: <strong>1:{decision['risk_reward']:.2f}</strong>
                    </div>
                    <div style="font-size: 0.95em; color: #666; margin-top: 15px;">
                        Trade ID: #{trade_id} | ✅ Database'e kaydedildi
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # ✅ REASON
                st.markdown(f"**💡 Karar Gerekçesi:**")
                st.info(decision['reason'])
                
                # ✅ LAYER BREAKDOWN (ALWAYS SHOW!)
                st.markdown("---")
                st.markdown("### 🧠 11 Layer Detaylı Analiz")
                
                if 'component_scores' in decision and decision['component_scores']:
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
                                
                                st.markdown(f"""
                                <div class="layer-card">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                        <strong style="font-size: 1.05em;">{status_icon} {info['name']}</strong>
                                        <span style="font-weight: 700; color: {color};">{score_val:.1f}/100</span>
                                    </div>
                                    <div style="font-size: 0.85em; color: #666; margin-bottom: 8px;">{info['desc']}</div>
                                    {render_progress_bar(score_val, color=color)}
                                    <div style="font-size: 0.8em; color: #999; margin-top: 5px;">Weight: {info['weight']*100:.0f}%</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            idx += 1
                else:
                    st.warning("⚠️ Component scores bulunamadı (ai_brain.py component_scores döndürmüyor olabilir)")
                
                # ✅ POZİSYON PLANI + COPY
                st.markdown("---")
                st.markdown("### 💼 Pozisyon Planı")
                
                if decision.get('entry_price') and decision['decision'] in ['LONG', 'SHORT', 'NEUTRAL']:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("📍 Entry", f"${decision['entry_price']:,.2f}")
                        components.html(copy_to_clipboard_button(str(decision['entry_price']), "📋 Entry"), height=40)
                        st.metric("💰 Position", f"${decision['position_size_usd']:,.2f}")
                    
                    with col2:
                        sl_pct = ((decision['stop_loss'] - decision['entry_price']) / decision['entry_price'] * 100)
                        st.metric("🛡️ Stop Loss", f"${decision['stop_loss']:,.2f}", f"{sl_pct:.2f}%")
                        components.html(copy_to_clipboard_button(str(decision['stop_loss']), "📋 SL"), height=40)
                        st.metric("⚠️ Risk", f"${decision['risk_amount_usd']:,.2f}")
                    
                    # TP Levels
                    st.markdown("---")
                    st.markdown("### 🎯 Take Profit Seviyeleri")
                    
                    risk_amount = abs(decision['entry_price'] - decision['stop_loss'])
                    
                    if decision['decision'] == 'LONG':
                        tp1 = decision['entry_price'] + (risk_amount * 1.0)
                        tp2 = decision['entry_price'] + (risk_amount * 1.618)
                        tp3 = decision['entry_price'] + (risk_amount * 2.618)
                    else:
                        tp1 = decision['entry_price'] - (risk_amount * 1.0)
                        tp2 = decision['entry_price'] - (risk_amount * 1.618)
                        tp3 = decision['entry_price'] - (risk_amount * 2.618)
                    
                    tp1_pct = ((tp1 - decision['entry_price']) / decision['entry_price'] * 100)
                    tp2_pct = ((tp2 - decision['entry_price']) / decision['entry_price'] * 100)
                    tp3_pct = ((tp3 - decision['entry_price']) / decision['entry_price'] * 100)
                    
                    # TP1-3 with copy buttons
                    for tp_num, tp_val, tp_pct_val, rr, close_pct, desc in [
                        (1, tp1, tp1_pct, "1:1", "50%", "Kar garantiye al"),
                        (2, tp2, tp2_pct, "1:1.62", "30%", "Fibonacci golden ratio"),
                        (3, tp3, tp3_pct, "1:2.62", "20%", "Maksimum kar hedefi")
                    ]:
                        st.markdown(f"""
                        <div class="tp-box">
                            <div>
                                <strong style="font-size: 1.1em;">🎯 TP{tp_num}:</strong> ${tp_val:,.2f} ({tp_pct_val:+.2f}%) [R/R: {rr}]<br>
                                <span style="font-size: 0.9em; color: #666;">→ Close {close_pct} | {desc}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        components.html(copy_to_clipboard_button(str(tp_val), f"📋 TP{tp_num}"), height=40)
                    
                    # Copy All
                    all_text = f"Entry: {decision['entry_price']}, SL: {decision['stop_loss']}, TP1: {tp1:.2f}, TP2: {tp2:.2f}, TP3: {tp3:.2f}"
                    st.markdown("---")
                    components.html(copy_to_clipboard_button(all_text, "📋 HEPSİNİ KOPYALA"), height=50)
                    
                    st.info("**📈 Trailing Stop:** TP1 → SL'i entry'e | TP2 → SL'i TP1'e çek")
                
                else:
                    st.warning("⚠️ Pozisyon planı mevcut değil (WAIT sinyali veya entry hesaplama hatası)")
            
            except Exception as e:
                st.error(f"❌ Analiz hatası: {e}")
                st.exception(e)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 2: MULTI-COIN WATCHLIST (OPTIMIZED WITH PROGRESS BAR!)
# ============================================================================
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Multi-Coin Watchlist (10 Coins)")
    
    st.info("💡 10 coin'i hızlı analiz et! Detaylı analiz için coin'e tıkla.")
    
    watchlist_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 
                       'DOGEUSDT', 'XRPUSDT', 'DOTUSDT', 'MATICUSDT', 'LTCUSDT']
    
    # ✅ Progress bar
    progress_bar = st.progress(0, "Başlatılıyor...")
    watchlist_data = []
    
    for idx, coin in enumerate(watchlist_coins):
        price_data = get_binance_price(coin)
        signal_data = get_quick_signal(coin, interval, progress_bar, idx, len(watchlist_coins))
        
        if price_data['available']:
            watchlist_data.append({
                'Coin': coin.replace('USDT', ''),
                'Price': f"${price_data['price']:,.2f}",
                '24h %': f"{price_data['change_24h']:+.2f}%",
                'Signal': signal_data['signal'],
                'Score': f"{signal_data['score']:.0f}/100",
                'Confidence': f"{signal_data['confidence']:.0f}%"
            })
    
    progress_bar.empty()  # Clear progress
    
    if watchlist_data:
        df = pd.DataFrame(watchlist_data)
        
        def color_signal(val):
            if val == 'LONG':
                return 'background-color: #d1fae5; color: #065f46;'
            elif val == 'SHORT':
                return 'background-color: #fee2e2; color: #991b1b;'
            elif val == 'NEUTRAL':
                return 'background-color: #f3f4f6; color: #374151;'
            return ''
        
        styled_df = df.style.applymap(color_signal, subset=['Signal'])
        st.dataframe(styled_df, use_container_width=True)
        
        st.markdown("---")
        st.markdown("**🔍 Detaylı Analiz İçin Coin Seçin:**")
        
        cols = st.columns(5)
        for idx, coin in enumerate(watchlist_coins):
            col_idx = idx % 5
            with cols[col_idx]:
                if st.button(coin.replace('USDT', ''), key=f"watch_{coin}", use_container_width=True):
                    st.session_state.coin = coin
                    st.rerun()
    else:
        st.error("❌ Watchlist verisi alınamadı")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 3: Trade History
# ============================================================================
with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📜 Trade History")
    
    trades_df = db.get_all_trades()
    
    if not trades_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Trades", len(trades_df))
        with col2:
            pending = len(trades_df[trades_df['status'] == 'PENDING'])
            st.metric("Pending", pending)
        with col3:
            closed = len(trades_df[trades_df['status'].isin(['WIN', 'LOSS', 'BREAKEVEN'])])
            st.metric("Closed", closed)
        with col4:
            if closed > 0:
                wins = len(trades_df[trades_df['status'] == 'WIN'])
                wr = (wins / closed * 100)
                st.metric("Win Rate", f"{wr:.1f}%")
            else:
                st.metric("Win Rate", "N/A")
        
        st.markdown("---")
        
        st.dataframe(
            trades_df[['id', 'timestamp', 'symbol', 'signal', 'confidence', 'final_score', 
                       'entry_price', 'stop_loss', 'position_size_usd', 'status', 'pnl_usd', 'pnl_pct']],
            use_container_width=True
        )
        
        st.markdown("---")
        
        if st.button("📥 Export to Excel", type="primary"):
            filename = db.export_to_excel()
            st.success(f"✅ Exported: {filename}")
            with open(filename, 'rb') as f:
                st.download_button(
                    label="⬇️ Download Excel",
                    data=f.read(),
                    file_name=filename,
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
        
        st.markdown("---")
        st.markdown("### ✏️ Update Trade Result")
        
        col_u1, col_u2, col_u3, col_u4 = st.columns(4)
        
        with col_u1:
            trade_id_update = st.number_input("Trade ID", min_value=1, step=1)
        with col_u2:
            close_price = st.number_input("Close Price", min_value=0.0, step=0.01)
        with col_u3:
            status = st.selectbox("Status", ['WIN', 'LOSS', 'BREAKEVEN'])
        with col_u4:
            if st.button("Update"):
                db.update_trade_result(trade_id_update, close_price, status)
                st.success(f"✅ Trade #{trade_id_update} updated!")
                st.rerun()
    else:
        st.info("📊 Henüz trade kaydı yok. AI Analiz yapın!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 20px;'>
    <p><strong>🔱 DEMIR AI Trading Bot v6.1 OPTIMIZED</strong></p>
    <p style='font-size: 0.9em; opacity: 0.8;'>Hızlı Watchlist + Detaylı AI + Better UX | © 2025</p>
</div>
""", unsafe_allow_html=True)
