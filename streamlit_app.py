"""
DEMIR - Professional AI Trading Dashboard (v3.0)
Binance Futures + Multi-Coin Tabs + Türkçe Açıklamalar
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# Modül importları
try:
    import config
    import db_layer
    import external_data
    import analysis_layer
    import strategy_layer
except ImportError as e:
    st.error(f"⚠️ Modül yükleme hatası: {e}")
    st.stop()

# AI Brain import
try:
    from ai_brain import AIBrain
    AI_BRAIN_AVAILABLE = True
except ImportError:
    AI_BRAIN_AVAILABLE = False

# Sayfa yapılandırması
st.set_page_config(
    page_title="DEMIR AI Trading",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%); }
    .main-title { font-size: 3.5rem; font-weight: 800; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 0.5rem; }
    .sub-title { text-align: center; color: #8b92a7; font-size: 1.1rem; margin-bottom: 2rem; }
    .price-ticker { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 15px; margin-bottom: 1.5rem; }
    .ticker-coin { display: inline-block; margin-right: 2rem; color: white; font-weight: 600; }
    .signal-card-buy { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 1rem; animation: pulse 2s infinite; }
    .signal-card-sell { background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%); padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 1rem; animation: pulse 2s infinite; }
    .signal-card-hold { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 1rem; }
    @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.02); } }
    .metric-card { background: rgba(255, 255, 255, 0.08); padding: 1.2rem; border-radius: 12px; border-left: 4px solid #667eea; margin-bottom: 1rem; }
    .metric-value { font-size: 2rem; font-weight: 700; color: #667eea; }
    .metric-label { color: #8b92a7; font-size: 0.9rem; margin-bottom: 0.3rem; }
    .metric-hint { color: #8b92a7; font-size: 0.8rem; font-style: italic; margin-top: 0.3rem; }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    if 'ws_data' not in st.session_state:
        st.session_state.ws_data = {}
    if 'last_analysis' not in st.session_state:
        st.session_state.last_analysis = {}
    if 'ai_mode' not in st.session_state:
        st.session_state.ai_mode = False
    if 'capital' not in st.session_state:
        st.session_state.capital = 10000
    if 'tracked_coins' not in st.session_state:
        st.session_state.tracked_coins = ['btcusdt', 'ethusdt', 'ltcusdt']

def create_advanced_chart(df, symbol, tech_data):
    df_chart = df.copy()
    timestamp_col = 'Timestamp' if 'Timestamp' in df_chart.columns else 'timestamp'
    
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f'{symbol.upper()} Price', 'RSI', 'MACD')
    )
    
    fig.add_trace(go.Candlestick(
        x=df_chart[timestamp_col], open=df_chart['Open'], high=df_chart['High'],
        low=df_chart['Low'], close=df_chart['Close'], name='Price',
        increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
    ), row=1, col=1)
    
    if 'RSI' in df_chart.columns:
        fig.add_trace(go.Scatter(x=df_chart[timestamp_col], y=df_chart['RSI'], 
                      name='RSI', line=dict(color='#9c27b0', width=2)), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    fig.update_layout(template='plotly_dark', height=800, showlegend=True,
                     xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)',
                     plot_bgcolor='rgba(0,0,0,0.3)', font=dict(color='#ffffff'))
    return fig

def display_price_ticker():
    if not st.session_state.ws_data:
        st.markdown('<div class="price-ticker">⏳ Canlı veriye bağlanılıyor...</div>', unsafe_allow_html=True)
        return
    ticker_html = '<div class="price-ticker">'
    for symbol, data in st.session_state.ws_data.items():
        price = data.get('price', 0)
        coin = symbol.replace('usdt', '').upper()
        ticker_html += f'<span class="ticker-coin">🪙 {coin}: ${price:,.2f}</span>'
    ticker_html += '</div>'
    st.markdown(ticker_html, unsafe_allow_html=True)

def run_analysis(symbol, timeframe='1h'):
    try:
        with st.spinner(f"🔍 {symbol.upper()} analiz ediliyor..."):
            ext_data = external_data.get_all_external_data()
            tech_analysis = analysis_layer.run_full_analysis(symbol, timeframe)
            signal = strategy_layer.generate_signal(symbol, tech_analysis, ext_data)
            st.session_state.last_analysis[symbol] = {
                'symbol': symbol, 'timestamp': datetime.now(),
                'technical': tech_analysis, 'signal': signal, 'mode': 'NORMAL'
            }
    except Exception as e:
        st.error(f"❌ Analiz hatası: {e}")

def run_ai_brain_analysis(symbol):
    try:
        with st.spinner(f"🧠 AI Brain {symbol.upper()} analiz ediyor..."):
            brain = AIBrain()
            decision = brain.make_decision(symbol, st.session_state.capital)
            st.session_state.last_analysis[symbol] = {
                'symbol': symbol, 'timestamp': datetime.now(),
                'ai_decision': decision, 'mode': 'AI_BRAIN'
            }
    except Exception as e:
        st.error(f"❌ AI Brain hatası: {e}")

def display_signal(signal_data):
    if not signal_data:
        return
    signal = signal_data.get('signal', 'HOLD')
    confidence = signal_data.get('confidence', 0)
    
    if signal == 'BUY':
        st.markdown(f'<div class="signal-card-buy"><h2>🟢 ALIŞ</h2><p>Güven: {confidence:.1f}%</p></div>', unsafe_allow_html=True)
    elif signal == 'SELL':
        st.markdown(f'<div class="signal-card-sell"><h2>🔴 SATIŞ</h2><p>Güven: {confidence:.1f}%</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-card-hold"><h2>🟡 BEKLE</h2><p>Güven: {confidence:.1f}%</p></div>', unsafe_allow_html=True)

def display_ai_decision(decision_data):
    if not decision_data:
        return
    
    signal = decision_data.get('signal', 'HOLD')
    confidence = decision_data.get('confidence', 0)
    reasoning = decision_data.get('reasoning', [])
    metadata = decision_data.get('metadata', {})
    current_price = metadata.get('current_price', 0)
    
    if signal == 'BUY':
        st.markdown(f'<div class="signal-card-buy"><h2>🟢 AI ALIŞ</h2><p>Güven: {confidence:.1f}%</p><p>Fiyat: ${current_price:,.2f}</p></div>', unsafe_allow_html=True)
    elif signal == 'SELL':
        st.markdown(f'<div class="signal-card-sell"><h2>🔴 AI SATIŞ</h2><p>Güven: {confidence:.1f}%</p><p>Fiyat: ${current_price:,.2f}</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-card-hold"><h2>🟡 AI BEKLE</h2><p>Güven: {confidence:.1f}%</p><p>Fiyat: ${current_price:,.2f}</p></div>', unsafe_allow_html=True)
    
    st.subheader("💰 Pozisyon & Risk")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Pozisyon</div><div class="metric-value">${decision_data.get("position_size", 0):.0f}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Stop Loss</div><div class="metric-value" style="color:#ef5350;">${decision_data.get("stop_loss", 0):.2f}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Take Profit</div><div class="metric-value" style="color:#26a69a;">${decision_data.get("take_profit_1", 0):.2f}</div></div>', unsafe_allow_html=True)
    with col4:
        rr = decision_data.get('risk_reward_ratio', 0)
        rr_color = '#26a69a' if rr >= 2 else '#ff9800' if rr >= 1.5 else '#ef5350'
        st.markdown(f'<div class="metric-card"><div class="metric-label">R/R</div><div class="metric-value" style="color:{rr_color};">1:{rr:.2f}</div></div>', unsafe_allow_html=True)
    
    st.subheader("🧠 AI Açıklaması")
    for reason in reasoning:
        if '✅' in reason:
            st.success(reason)
        elif '⚠️' in reason:
            st.warning(reason)
        elif '❌' in reason:
            st.error(reason)
        else:
            st.info(reason)

def main():
    init_session_state()
    
    st.markdown('<h1 class="main-title">⚡ DEMIR AI TRADING</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Profesyonel AI Binance Futures Trading</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6 = st.columns([2, 0.8, 1.5, 0.8, 0.8, 1])
    
    with col1:
        new_coin = st.text_input("➕ Coin Ekle (SOLUSDT)", "").upper()
    with col2:
        st.write(""); st.write("")
        if st.button("Ekle") and new_coin and new_coin.lower() not in st.session_state.tracked_coins:
            st.session_state.tracked_coins.append(new_coin.lower())
    with col3:
        timeframe = st.selectbox("⏱️ Zaman", ['15m', '1h', '4h', '1d'], index=1)
    with col4:
        st.write(""); st.write("")
        st.write("WS Disabled")
    with col5:
        st.write(""); st.write("")
        if AI_BRAIN_AVAILABLE:
            st.session_state.ai_mode = st.toggle("🧠 AI", value=st.session_state.ai_mode)
    with col6:
        st.write(""); st.write("")
        if st.button("🚀 Analiz"):
            for coin in st.session_state.tracked_coins:
                if st.session_state.ai_mode and AI_BRAIN_AVAILABLE:
                    run_ai_brain_analysis(coin)
                else:
                    run_analysis(coin, timeframe)
    
    st.caption(f"📊 Takip: {', '.join([c.upper() for c in st.session_state.tracked_coins])}")
    display_price_ticker()
    st.divider()
    
    if st.session_state.tracked_coins:
        tabs = st.tabs([coin.upper() for coin in st.session_state.tracked_coins])
        for idx, coin in enumerate(st.session_state.tracked_coins):
            with tabs[idx]:
                if coin in st.session_state.last_analysis:
                    analysis = st.session_state.last_analysis[coin]
                    if analysis.get('mode') == 'AI_BRAIN':
                        display_ai_decision(analysis.get('ai_decision'))
                    else:
                        display_signal(analysis.get('signal'))
                    
                    tech_data = analysis.get('ai_decision', {}).get('metadata', {}).get('base_signal', {}) if analysis.get('mode') == 'AI_BRAIN' else analysis.get('technical', {})
                    if 'dataframe' in tech_data and not tech_data['dataframe'].empty:
                        st.plotly_chart(create_advanced_chart(tech_data['dataframe'], coin, tech_data), use_container_width=True)
                else:
                    st.info(f"💡 {coin.upper()} için analiz yok")
    
    st.caption("🔥 DEMIR AI | Binance Futures")
    time.sleep(1)
    st.rerun()

if __name__ == "__main__":
    main()
