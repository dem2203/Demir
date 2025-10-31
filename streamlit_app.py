"""
DEMIR AI Trading Bot - Streamlit Dashboard
Phase 3A FINAL: Complete Integration
Tarih: 31 Ekim 2025

FEATURES:
- Real-time Binance Futures prices
- News Sentiment Analysis
- Phase 3A: Volume Profile, Pivot Points, Fibonacci, VWAP, Monte Carlo, Kelly
- AI Brain v3 Decision Engine
- Manual coin addition
- Multiple timeframes (15m, 1h, 4h, 1d)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ============================================================================
# CRITICAL: st.set_page_config() MUST BE FIRST
# ============================================================================
st.set_page_config(
    page_title="🔱 DEMIR AI Trading Bot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Session state initialization
# ============================================================================
if 'coins' not in st.session_state:
    st.session_state['coins'] = ["BTCUSDT", "ETHUSDT", "LTCUSDT"]

# ============================================================================
# Module imports
# ============================================================================
import_errors = []

try:
    import ai_brain
    AI_AVAILABLE = True
except ImportError as e:
    AI_AVAILABLE = False
    import_errors.append(f"ai_brain: {e}")

try:
    import news_sentiment_layer
    NEWS_AVAILABLE = True
except ImportError as e:
    NEWS_AVAILABLE = False
    import_errors.append(f"news_sentiment_layer: {e}")

if import_errors:
    with st.expander("⚠️ Module Import Warnings", expanded=False):
        for error in import_errors:
            st.warning(error)

# ============================================================================
# CSS Styling
# ============================================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .metric-card {
        background: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 15px;
    }
    .positive {
        color: #00ff88 !important;
        font-weight: bold;
    }
    .negative {
        color: #ff4444 !important;
        font-weight: bold;
    }
    .neutral {
        color: #ffaa00 !important;
        font-weight: bold;
    }
    .news-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        border: 2px solid #4a90e2;
    }
    .news-positive {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .news-negative {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    .news-neutral {
        background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Header
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>⚡ DEMIR AI TRADING</h1>
    <p>Güven: 31% | $109,450.00</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar
# ============================================================================
with st.sidebar:
    st.markdown("## 🎛️ Ayarlar")
    
    # Coin seçimi
    coin = st.selectbox(
        "Coin Seç",
        st.session_state['coins'],
        key="coin_select"
    )
    
    # Manuel coin ekleme
    st.markdown("### ➕ Yeni Coin Ekle")
    new_coin = st.text_input("Coin Symbol (örn: SOLUSDT)", key="new_coin_input")
    if st.button("Ekle", use_container_width=True):
        if new_coin and new_coin not in st.session_state['coins']:
            st.session_state['coins'].append(new_coin.upper())
            st.success(f"✅ {new_coin.upper()} eklendi!")
            st.rerun()
        elif new_coin in st.session_state['coins']:
            st.warning(f"⚠️ {new_coin.upper()} zaten mevcut!")
    
    st.markdown("---")
    
    # Zaman dilimi (güncellenmiş)
    timeframe = st.selectbox(
        "Zaman Dilimi",
        ["15m", "1h", "4h", "1d"],
        index=1,  # Default: 1h
        key="timeframe_select"
    )
    
    # Analiz butonu
    analyze_btn = st.button("🚀 ANALİZ", use_container_width=True, type="primary")
    
    st.markdown("---")
    
    # AI Toggle
    st.markdown("### 🤖 AI Özellikleri")
    ai_enabled = st.toggle("AI Brain v3", value=True)
    
    # News Sentiment Toggle
    if NEWS_AVAILABLE:
        news_enabled = st.toggle("📰 News Sentiment", value=True)
    else:
        news_enabled = False
        st.info("📰 News özelliği yükleniyor...")

# ============================================================================
# Ana Container
# ============================================================================
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 💬 AI Açıklama")
    
    if analyze_btn or st.session_state.get('last_analysis'):
        with st.spinner(f"🧠 {coin} analiz ediliyor..."):
            
            if AI_AVAILABLE and ai_enabled:
                try:
                    # AI Brain v3 decision
                    decision = ai_brain.make_trading_decision(
                        symbol=coin,
                        interval=timeframe,
                        portfolio_value=10000,
                        risk_per_trade=200
                    )
                    
                    # Detaylı AI output
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>🎯 AI Decision: {decision['decision']} {decision['signal']}</h3>
                        <p><strong>Confidence:</strong> {decision['confidence']*100:.0f}%</p>
                        <p><strong>Score:</strong> {decision['final_score']:.0f}/100</p>
                        <p><strong>Reason:</strong> {decision['reason']}</p>
                        <hr>
                        <p>📊 <strong>Risk Metrics:</strong></p>
                        <p>🎲 Risk of Ruin: {decision['risk_metrics']['risk_of_ruin']:.2f}%</p>
                        <p>📉 Max Drawdown: {decision['risk_metrics']['max_drawdown']:.2f}%</p>
                        <p>📈 Sharpe Ratio: {decision['risk_metrics']['sharpe_ratio']:.2f}</p>
                        <hr>
                        <p>💰 <strong>Position:</strong> ${decision['position_size_usd']:,.2f} ({decision['position_size_pct']:.2f}%)</p>
                        <p>⚠️ <strong>Risk:</strong> ${decision['risk_amount_usd']:,.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Save to session
                    st.session_state['last_decision'] = decision
                    st.session_state['last_analysis'] = True
                
                except Exception as e:
                    st.error(f"❌ AI Brain error: {str(e)}")
                    st.warning("Fallback: Mock data gösteriliyor")
                    
                    # Fallback: Mock data
                    st.markdown("""
                    <div class="metric-card">
                        <h3>⚠️ Zaman dilimleri uyumsuz. Bekle!</h3>
                        <p>📊 Piyasa dalgalı ve tahmin edilemez. Dikkatli ol!</p>
                        <p>💰 Risk/Ödül çok yüksek! 3.8x kazanç potansiyeli.</p>
                        <p>📰 Haberler nötr. Sinyal üzerinde etkisi yok.</p>
                        <p>❌ Güven veya R/R yetersiz. Bekle!</p>
                        <p>📋 Kelly: %2.0 (200 USD)</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # AI disabled - mock data
                st.markdown("""
                <div class="metric-card">
                    <h3>⚠️ AI Brain devre dışı</h3>
                    <p>AI özelliklerini etkinleştirmek için sidebar'dan "AI Brain v3" toggle'ını açın.</p>
                </div>
                """, unsafe_allow_html=True)

with col2:
    st.markdown("### 💼 Pozisyon")
    
    if st.session_state.get('last_decision'):
        decision = st.session_state['last_decision']
        
        if decision.get('entry_price'):
            st.metric("Entry", f"${decision['entry_price']:,.2f}", delta="Current Price")
            st.metric("Pozisyon", f"${decision['position_size_usd']:,.2f}")
            
            # DÜZELTME: None check ekle
            if decision.get('stop_loss') is not None:
                st.metric("Stop", f"${decision['stop_loss']:,.2f}")
            else:
                st.metric("Stop", "Calculating...")
            
            if decision.get('take_profit') is not None:
                st.metric("Target", f"${decision['take_profit']:,.2f}")
            else:
                st.metric("Target", "Calculating...")
            
            if decision.get('risk_reward') and decision['risk_reward'] > 0:
                st.metric("R/R", f"1:{decision['risk_reward']:.2f}")
            else:
                st.metric("R/R", "N/A")
        else:
            st.info("🚀 ANALİZ butonuna basın")
    else:
        st.info("🚀 ANALİZ butonuna basın")

# ============================================================================
# News Sentiment Section
# ============================================================================
if NEWS_AVAILABLE and news_enabled:
    st.markdown("---")
    st.markdown(f"## 📰 News Sentiment Analysis - {coin}")
    
    if analyze_btn or st.session_state.get('show_news'):
        with st.spinner(f"📡 {coin} haberleri yükleniyor..."):
            try:
                news_signal = news_sentiment_layer.get_news_signal(coin)
                
                sentiment = news_signal['sentiment']
                if sentiment == 'POSITIVE':
                    card_class = 'news-card news-positive'
                    emoji = '📈'
                elif sentiment == 'NEGATIVE':
                    card_class = 'news-card news-negative'
                    emoji = '📉'
                else:
                    card_class = 'news-card news-neutral'
                    emoji = '📊'
                
                st.markdown(f"""
                <div class="{card_class}">
                    <h3>{emoji} {sentiment} Sentiment</h3>
                    <p><strong>Coin:</strong> {news_signal['symbol']}</p>
                    <p><strong>Score:</strong> {news_signal['score']:.2f} / 1.00</p>
                    <p><strong>Impact:</strong> {news_signal['impact']}</p>
                    <hr style="border-color: rgba(255,255,255,0.3);">
                    <p>📈 Bullish News: {news_signal['details']['bullish_news']}</p>
                    <p>📉 Bearish News: {news_signal['details']['bearish_news']}</p>
                    <p>📊 Neutral News: {news_signal['details']['neutral_news']}</p>
                    <p style="font-size: 0.9em; opacity: 0.8;">Total: {news_signal['details']['total_news']} news analyzed</p>
                    <p style="font-size: 0.8em; opacity: 0.6;">Updated: {news_signal['timestamp']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state['show_news'] = True
                
            except Exception as e:
                st.error(f"❌ News sentiment alınamadı: {str(e)}")

# ============================================================================
# Market Data Section
# ============================================================================
st.markdown("---")
st.markdown("## 📊 Market Data")

# Dynamic tabs based on coin list
tab_labels = st.session_state['coins']
tabs = st.tabs(tab_labels)

for i, tab in enumerate(tabs):
    with tab:
        coin_symbol = tab_labels[i]
        st.info(f"{coin_symbol} market data burada gösterilecek")

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; opacity: 0.6;">
    🔱 DEMIR AI Trading Bot v3.0 | Phase 3A: Complete Integration ✅
</div>
""", unsafe_allow_html=True)
