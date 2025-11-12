import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="📊 Performance", layout="wide")

st.title("📊 Performance Dashboard - Türkçe v10")
st.markdown("**AI'ın ticaret performansını detaylı analiz et**")

st.markdown("""
<div style="background: #1A1F2E; padding: 15px; border-radius: 8px; margin: 15px 0;">
<strong>🔹 Ne Demek?</strong><br>
Bu sayfada:<br>
• <strong>Açık Trades:</strong> Şu anda işlem gören pozisyonlar<br>
• <strong>Kapalı Trades:</strong> Bitmiş işlemlerin detayları<br>
• <strong>Win Rate:</strong> Kazanma oranı (kaç işlem kârlı oldu)<br>
• <strong>P&L:</strong> Kar ve Zarar (toplam ne kadar kazandığın)<br>
• <strong>Best Time:</strong> AI'ın en başarılı olduğu saatler<br>
• <strong>Best Coin:</strong> En çok kâr getiren coin
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("## 📊 Özet İstatistikler")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📊 Açık Trades",
        "5",
        "Toplam: 5 işlem",
        delta_color="off"
    )

with col2:
    st.metric(
        "✅ Kapalı Trades",
        "145",
        "Kazanmış: 98 (67.6%)",
        delta_color="off"
    )

with col3:
    st.metric(
        "📈 Win Rate",
        "67.6%",
        "Son 7 gün: 72%",
        delta_color="off"
    )

with col4:
    st.metric(
        "💰 Total P&L",
        "+$15,890",
        "7-Day: +$3,240",
        delta_color="off"
    )

st.markdown("---")

st.markdown("## 📈 AI Doğruluğu (Signal Accuracy)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🟢 LONG Sinyalleri")
    st.markdown("**71% Doğruluk**")
    st.markdown("- Toplam: 98 sinyal")
    st.markdown("- Kârlı: 70 işlem")
    st.markdown("- Zararı: 28 işlem")

with col2:
    st.markdown("### 🔴 SHORT Sinyalleri")
    st.markdown("**62% Doğruluk**")
    st.markdown("- Toplam: 47 sinyal")
    st.markdown("- Kârlı: 28 işlem")
    st.markdown("- Zararı: 19 işlem")

st.markdown("---")

st.markdown("## 🕐 En İyi Ticaret Saatleri")

data = {
    'Saat Aralığı': ['00:00-04:00', '04:00-08:00', '08:00-12:00', '12:00-16:00', '16:00-20:00', '20:00-00:00'],
    'Sinyal Sayısı': [12, 18, 25, 31, 28, 15],
    'Win Rate': ['68%', '65%', '70%', '75%', '72%', '66%'],
    'Avg P&L': ['+$180', '+$220', '+$310', '+$425', '+$380', '+$150']
}

df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)

st.markdown("💡 **En Kârlı Zaman:** 12:00-16:00 UTC (75% win rate)")

st.markdown("---")

st.markdown("## 🪙 Coin'e Göre Performance")

coin_data = {
    'Coin': ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'SOLUSDT', 'BNB'],
    'Toplam Trade': [45, 38, 32, 20, 10],
    'Win Rate': ['72%', '65%', '68%', '60%', '70%'],
    'Total P&L': ['+$8,230', '+$4,560', '+$2,100', '+$890', '+$1,110']
}

df_coins = pd.DataFrame(coin_data)
st.dataframe(df_coins, use_container_width=True)

st.markdown("🏆 **En Kârlı Coin:** Bitcoin (72% win rate, +$8,230)")

---

st.markdown("---")

st.markdown("## 📊 Açık Trades (Şu Anda)")

trades = {
    'ID': ['TRADE_001', 'TRADE_002', 'TRADE_003', 'TRADE_004', 'TRADE_005'],
    'Coin': ['BTCUSDT', 'ETHUSDT', 'BTCUSDT', 'LTCUSDT', 'SOLUSDT'],
    'Direction': ['LONG', 'SHORT', 'LONG', 'LONG', 'SHORT'],
    'Entry': ['$45,230', '$2,450', '$45,100', '$125.50', '$165.80'],
    'Current': ['$45,420', '$2,380', '$45,350', '$126.20', '$164.50'],
    'P&L': ['+$190', '-$70', '+$250', '+$0.70', '-$1.30'],
    'TP': ['$46,500', '$2,300', '$46,500', '$127.50', '$160.00'],
    'SL': ['$44,800', '$2,600', '$44,800', '$124.00', '$171.00']
}

df_trades = pd.DataFrame(trades)
st.dataframe(df_trades, use_container_width=True)

st.markdown("---")

st.markdown("## 💡 AI'ın Önerisi")

st.success("""
✅ **YÜKSEK PERFORMANS DÖNEM**
- Confidence > 75%: 70% doğruluk (devam et!)
- LONG sinyalleri SHORT'tan daha başarılı
- 12:00-16:00 UTC'de daha fazla işlem yap

⚠️ **OPTİMİZASYON ÖNERILERI**
- SHORT sinyalleri geliştirilmeli (şu an 62% accuracy)
- Risk/Reward < 1.5 olan işlemleri atla
- Gecenin 00:00-04:00 saatlerinde çıkış yap
""")
