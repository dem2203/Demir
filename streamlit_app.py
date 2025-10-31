"""
DEMIR - AI Trading Dashboard v3.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime

try:
    import analysis_layer
    import strategy_layer
    import external_data
except ImportError as e:
    st.error(f"Import hatası: {e}")
    st.stop()

try:
    from ai_brain import AIBrain
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

st.set_page_config(page_title="DEMIR AI", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%); }
    .signal-buy { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1.5rem; border-radius: 15px; color: white; }
    .signal-sell { background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%); padding: 1.5rem; border-radius: 15px; color: white; }
    .signal-hold { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 15px; color: white; }
</style>
""", unsafe_allow_html=True)

if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = {}
if 'ai_mode' not in st.session_state:
    st.session_state.ai_mode = False
if 'coins' not in st.session_state:
    st.session_state.coins = ['btcusdt', 'ethusdt', 'solusdt']

def run_normal_analysis(symbol, timeframe='1h'):
    try:
        with st.spinner(f"Analiz: {symbol.upper()}"):
            tech = analysis_layer.run_full_analysis(symbol, timeframe)
            if 'error' in tech:
                st.error(f"❌ {tech['error']}")
                return
            ext = external_data.get_all_external_data()
            signal = strategy_layer.generate_signal(symbol, tech, ext)
            st.session_state.last_analysis[symbol] = {
                'mode': 'NORMAL',
                'signal': signal,
                'tech': tech
            }
    except Exception as e:
        st.error(f"❌ Hata: {e}")

def run_ai_analysis(symbol):
    if not AI_AVAILABLE:
        st.error("AI Brain yok!")
        return
    try:
        with st.spinner(f"AI analiz: {symbol.upper()}"):
            brain = AIBrain()
            decision = brain.make_decision(symbol, 10000)
            st.session_state.last_analysis[symbol] = {
                'mode': 'AI',
                'decision': decision
            }
    except Exception as e:
        st.error(f"❌ AI hatası: {e}")

def show_signal(data):
    signal = data.get('signal', 'HOLD')
    conf = data.get('confidence', 0)
    if signal == 'BUY':
        st.markdown(f'<div class="signal-buy"><h2>🟢 ALIŞ</h2><p>Güven: {conf:.0f}%</p></div>', unsafe_allow_html=True)
    elif signal == 'SELL':
        st.markdown(f'<div class="signal-sell"><h2>🔴 SATIŞ</h2><p>Güven: {conf:.0f}%</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-hold"><h2>🟡 BEKLE</h2><p>Güven: {conf:.0f}%</p></div>', unsafe_allow_html=True)

def show_ai(data):
    signal = data.get('signal', 'HOLD')
    conf = data.get('confidence', 0)
    price = data.get('metadata', {}).get('current_price', 0)
    
    if signal == 'BUY':
        st.markdown(f'<div class="signal-buy"><h2>🟢 AI ALIŞ</h2><p>Güven: {conf:.0f}% | ${price:,.2f}</p></div>', unsafe_allow_html=True)
    elif signal == 'SELL':
        st.markdown(f'<div class="signal-sell"><h2>🔴 AI SATIŞ</h2><p>Güven: {conf:.0f}% | ${price:,.2f}</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-hold"><h2>🟡 AI BEKLE</h2><p>Güven: {conf:.0f}% | ${price:,.2f}</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pozisyon", f"${data.get('position_size', 0):.0f}")
    col2.metric("Stop", f"${data.get('stop_loss', 0):.2f}")
    col3.metric("Target", f"${data.get('take_profit_1', 0):.2f}")
    col4.metric("R/R", f"1:{data.get('risk_reward_ratio', 0):.2f}")
    
    st.subheader("🧠 Açıklama")
    for reason in data.get('reasoning', []):
        if '✅' in reason:
            st.success(reason)
        elif '⚠️' in reason:
            st.warning(reason)
        elif '❌' in reason:
            st.error(reason)
        else:
            st.info(reason)

st.title("⚡ DEMIR AI TRADING")

col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    new_coin = st.text_input("Coin ekle", "").upper()
with col2:
    timeframe = st.selectbox("Zaman", ['15m', '1h', '4h'], index=1)
with col3:
    st.write(""); st.write("")
    if st.button("Ekle") and new_coin and new_coin.lower() not in st.session_state.coins:
        st.session_state.coins.append(new_coin.lower())
with col4:
    st.write(""); st.write("")
    if AI_AVAILABLE:
        st.session_state.ai_mode = st.toggle("🧠 AI", value=st.session_state.ai_mode)

if st.button("🚀 ANALİZ"):
    for coin in st.session_state.coins:
        if st.session_state.ai_mode:
            run_ai_analysis(coin)
        else:
            run_normal_analysis(coin, timeframe)

st.divider()

tabs = st.tabs([c.upper() for c in st.session_state.coins])
for idx, coin in enumerate(st.session_state.coins):
    with tabs[idx]:
        if coin in st.session_state.last_analysis:
            analysis = st.session_state.last_analysis[coin]
            if analysis['mode'] == 'AI':
                show_ai(analysis['decision'])
            else:
                show_signal(analysis['signal'])
        else:
            st.info(f"💡 {coin.upper()} için '🚀 ANALİZ' basın")
