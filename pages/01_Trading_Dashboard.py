import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="📊 Trading Dashboard", layout="wide")

st.title("📊 Trading Dashboard - Türkçe v10")
st.markdown("**Açık ve kapalı alım-satımları gösterir**")

st.markdown("""
<div style="background: #1A1F2E; padding: 15px; border-radius: 8px; margin: 15px 0;">
<strong>🔹 Ne Demek?</strong><br>
• <strong>Açık Trades:</strong> Şu anda işlem gören pozisyonlar<br>
• <strong>Entry:</strong> Giriş fiyatı<br>
• <strong>TP:</strong> Hedef fiyat<br>
• <strong>SL:</strong> Zarar durdur<br>
• <strong>P&L:</strong> Kar/Zarar
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("## 📊 Açık Trades")

trades = {
    'ID': ['TRADE_001', 'TRADE_002', 'TRADE_003', 'TRADE_004', 'TRADE_005'],
    'Coin': ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'SOLUSDT', 'BNBUSDT'],
    'Direction': ['🟢 LONG', '🔴 SHORT', '🟢 LONG', '🟢 LONG', '🔴 SHORT'],
    'Entry': ['$45,230', '$2,450', '$125.50', '$165.80', '$650'],
    'Current': ['$45,420', '$2,380', '$126.20', '$164.50', '$630'],
    'TP': ['$46,500', '$2,300', '$127.50', '$170.00', '$620'],
    'SL': ['$44,800', '$2,600', '$124.00', '$160.00', '$680'],
    'P&L': ['+$190', '-$70', '+$0.70', '-$1.30', '-$20']
}

df = pd.DataFrame(trades)
st.dataframe(df, use_container_width=True)

st.markdown("---")

st.markdown("## 📊 Kapalı Trades (Son 10)")

closed = {
    'ID': ['TRADE_891', 'TRADE_890', 'TRADE_889'],
    'Coin': ['BTCUSDT', 'ETHUSDT', 'LTCUSDT'],
    'Result': ['✅ Win', '❌ Loss', '✅ Win'],
    'Profit/Loss': ['+$450', '-$120', '+$320']
}

df_closed = pd.DataFrame(closed)
st.dataframe(df_closed, use_container_width=True)

st.markdown("---")

st.markdown("## 📈 Özet")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Açık Trades", "5", "Total")
with col2:
    st.metric("Kapalı Trades", "891", "Total")
with col3:
    st.metric("Total P&L", "+$15,890", "All Time")

st.markdown(f"<small>Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>", unsafe_allow_html=True)
