st.markdown("""
<strong>🎯 Opportunity Scanner Nedir?</strong><br>

Fırsat bulmak için taradığımız veriler:

• Pattern Recognition: H&S, Double Bottom, Elliott Waves
• Support/Resistance: Önemli fiyat seviyeleri
• Whale Activity: Büyük oyuncu hareketleri
• Breakouts: Kırılma fırsatları
""")

# Opportunities
opps = {
    'Type': ['Head & Shoulders', 'Whale Buy', 'Breakout'],
    'Coin': ['BTC', 'ETH', 'LTC'],
    'Signal': ['🔴 SHORT', '🟢 LONG', '🟢 LONG'],
    'Confidence': ['68%', '82%', '75%']
}
st.dataframe(opps)

import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime

# ============================================================================
# SAFE IMPORTS - with fallback
# ============================================================================

try:
    from opportunity_scanner.pattern_recognition import PatternRecognizer
    patterns_ok = True
except:
    patterns_ok = False

try:
    from opportunity_scanner.whale_detector import WhaleDetector
    whale_ok = True
except:
    whale_ok = False

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="🎯 Opportunity Scanner",
    layout="wide"
)

st.title("🎯 Opportunity Scanner")

# ============================================================================
# UI
# ============================================================================

col1, col2, col3 = st.columns(3)

with col1:
    symbols = st.multiselect(
        "Select Symbols",
        ["BTCUSDT", "ETHUSDT", "LTCUSDT"],
        default=["BTCUSDT"]
    )

with col2:
    timeframe = st.selectbox("Timeframe", ["1h", "4h", "1d"])

with col3:
    if st.button("🔍 Scan Now"):
        st.info("Scanning patterns and whales...")

st.markdown("---")

# ============================================================================
# PATTERN RECOGNITION
# ============================================================================

if patterns_ok:
    st.markdown("### 📊 Pattern Recognition")
    
    recognizer = PatternRecognizer()
    
    for symbol in symbols:
        with st.expander(f"📈 {symbol} Patterns"):
            try:
                h_s = asyncio.run(recognizer.detect_head_and_shoulders(symbol, timeframe))
                
                if h_s.get('pattern_found'):
                    st.success(f"✅ H&S Pattern: {h_s.get('confidence', 0):.1f}% confidence")
                    st.info(f"Entry: ${h_s.get('entry'):.2f} | Target: ${h_s.get('target'):.2f} | SL: ${h_s.get('stop_loss'):.2f}")
                else:
                    st.info(f"No H&S pattern in {symbol}")
                    
            except Exception as e:
                st.warning(f"Could not scan {symbol}: {e}")
else:
    st.error("⚠️ Pattern Recognition module not available")

st.markdown("---")

# ============================================================================
# WHALE ACTIVITY
# ============================================================================

if whale_ok:
    st.markdown("### 🐋 Whale Activity")
    
    detector = WhaleDetector()
    
    for symbol in symbols:
        with st.expander(f"🐳 {symbol} Whale Activity"):
            try:
                whales = asyncio.run(detector.detect_large_transactions(symbol))
                
                if whales.get('large_buys', 0) > 0 or whales.get('large_sells', 0) > 0:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Large Buys", whales.get('large_buys', 0))
                    with col2:
                        st.metric("Large Sells", whales.get('large_sells', 0))
                    with col3:
                        st.metric("Net Position", f"${whales.get('net_position', 0):,.0f}")
                    
                    st.warning(f"🐋 Whale activity detected in {symbol}")
                else:
                    st.info(f"No significant whale activity in {symbol}")
                    
            except Exception as e:
                st.warning(f"Could not fetch whale data for {symbol}: {e}")
else:
    st.error("⚠️ Whale Detector module not available")

st.markdown("---")
st.caption("Real-time data from Binance + CoinGlass")
