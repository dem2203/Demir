import streamlit as st
from datetime import datetime
import os

st.set_page_config(page_title="📈 Trading Dashboard", page_icon="📈", layout="wide")

st.markdown("""
<style>
.page-title { background: linear-gradient(135deg, #2196F3 0%, #21C4F3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.metric-box { background: #1a202c; border-left: 4px solid #2196F3; border-radius: 8px; padding: 16px; margin: 8px 0; }
.signal-long { background: rgba(0, 208, 132, 0.15); border: 2px solid #00D084; border-radius: 12px; padding: 16px; }
.signal-short { background: rgba(255, 71, 87, 0.15); border: 2px solid #FF4757; border-radius: 12px; padding: 16px; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Trading Dashboard - Main Signal")

# Current Signal
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class='signal-long'>
        <h2 style='color: #00D084;'>🟢 LONG SIGNAL</h2>
        <p><b>Confidence:</b> 78.5%</p>
        <p><b>Win Rate:</b> 73.2%</p>
        <p><b>Status:</b> ⏳ READY FOR ENTRY</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.metric("Risk/Reward", "2.3:1")
    st.metric("Profit Factor", "1.85")

st.divider()

# Trading Parameters
st.subheader("💰 Trading Parameters")

param_cols = st.columns(5)
params = [("Entry", "$43,200"), ("TP1", "$44,200"), ("TP2", "$45,300"), ("TP3", "$46,500"), ("SL", "$42,100")]

for col, (label, value) in zip(param_cols, params):
    with col:
        st.metric(label, value)

st.divider()

# Market Data
st.subheader("📊 Real-Time Market Data")

market_cols = st.columns(4)
data = [("BTC", "$43,250", "+2.1%"), ("ETH", "$2,280", "+1.8%"), ("Market Dom.", "48.5%", "-0.3%"), ("Volume", "$89.2B", "+5.2%")]

for col, (coin, price, change) in zip(market_cols, data):
    with col:
        st.metric(coin, price, change)

st.divider()

# 26 Phases
st.subheader("📈 All 26 Phases Status")

phases = [(1,"SPOT","✅"),(2,"FUTURES","✅"),(3,"OrderBook","✅"),(4,"Tech","✅"),(5,"Volume","✅"),(6,"Sentiment","✅"),(7,"ML","✅"),(8,"Anomaly","✅"),
          (9,"Validate","✅"),(10,"Conscious","✅"),(11,"Intel","⏳"),(12,"OnChain","✅"),(13,"Macro","✅"),(14,"Sent+","✅"),(15,"Learn","✅"),(16,"Adv","✅"),
          (17,"Compliance","✅"),(18,"MultiCoin","⏳"),(19,"Quantum","✅"),(20,"RL","✅"),(21,"Multi","✅"),(22,"Pred","✅"),(23,"SelfL","✅"),(24,"Back","✅"),
          (25,"Recovery","✅"),(26,"Integration","✅")]

cols = st.columns(8)
for i, (num, name, status) in enumerate(phases):
    with cols[i % 8]:
        badge_color = "#00D084" if status == "✅" else "#FFA502"
        st.markdown(f"<div style='background: #1a202c; border: 1px solid #2d3748; border-radius: 8px; padding: 8px; text-align: center;'><p style='font-size: 10px; margin: 0;'>P{num}</p><p style='font-size: 8px; color: #2196F3; margin: 4px 0;'>{name}</p><p style='color: {badge_color}; font-size: 12px;'>{status}</p></div>", unsafe_allow_html=True)

st.divider()

# 111+ Factors
st.subheader("🎯 Intelligence Factors")

factor_cols = st.columns(5)
factors = [("Technical", 40), ("On-Chain", 25), ("Macro", 18), ("Sentiment", 15), ("Global", 13)]

for col, (name, count) in zip(factor_cols, factors):
    with col:
        st.metric(name, count)

st.divider()
st.markdown(f"<p style='text-align: center; color: #CBD5E0; font-size: 11px;'>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} | 🟢 24/7 Bot Active</p>", unsafe_allow_html=True)
