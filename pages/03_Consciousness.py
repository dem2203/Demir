# ============================================================================
# pages/03_Consciousness.py
# ============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="🧠 Consciousness", layout="wide")

st.title("🧠 Consciousness - Bayesian Karar Motoru")
st.markdown("**Yapay Zekanın Düşünme Sistemi**")

st.markdown("""
<div style="background: #1A1F2E; padding: 15px; border-radius: 8px;">
<strong>🔹 Ne Demek?</strong><br>
Bayesian: Olasılık teorisine dayalı karar sistemi. Yeni bilgiye göre kararını güncelleyen zeka.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("## 🧠 Consciousness Outputs")

consciousness = {
    'Coin': ['BTC', 'ETH', 'LTC', 'SOL', 'BNB'],
    'Decision': ['🟢 LONG', '🟡 NEUTRAL', '🟢 LONG', '🔴 SHORT', '🟢 LONG'],
    'Confidence': ['82%', '55%', '68%', '42%', '75%'],
    'Reasoning': [
        'Teknik + Makro pozitif',
        'Signals karışık',
        'Pattern bullish',
        'On-chain negatif',
        'ML modeli LONG'
    ]
}

df = pd.DataFrame(consciousness)
st.dataframe(df, use_container_width=True)

st.markdown("---")

st.markdown("## 🔧 Bayesian Update Mekanizması")

st.markdown("""
Prior Belief (İlk Kanı):
- P(LONG) = 0.5 (50%)

New Evidence (Yeni Kanıt):
- RSI = 75 (Aşırı alındı)
- MACD = Pozitif (Yükseliş)
- On-Chain = Satış (Düşüş)

Posterior (Güncellenmiş Kanı):
- P(LONG | Evidence) = 68% (Güven arttı)
""")

st.markdown(f"<small>Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>", unsafe_allow_html=True)
