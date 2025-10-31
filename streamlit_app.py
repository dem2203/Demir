"""
🔱 DEMIR AI TRADING BOT - SIMPLE LIVE DASHBOARD
Basit ama çalışan: Canlı fiyat + TradingView + AI Analiz + TP1/TP2/TP3
Tarih: 31 Ekim 2025
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime
import time

# ============================================================================
# Sayfa Yapılandırması
# ============================================================================
st.set_page_config(
    page_title="🔱 DEMIR AI Dashboard",
    page_icon="🔱",
    layout="wide"
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
                'available': True
            }
    except:
        pass
    return {'price': 0, 'change_24h': 0, 'volume': 0, 'available': False}


# ============================================================================
# CSS
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
        padding: 15px;
        margin: 10px 0;
    }
    .price-big {
        font-size: 2em;
        font-weight: 700;
    }
    .tp-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Header
# ============================================================================
st.markdown("""
<div class="card" style="text-align: center;">
    <h1 style="color: #667eea; margin: 0;">🔱 DEMIR AI TRADING BOT</h1>
    <p style="color: #666;">Live Dashboard | Phase 3A + 3B Active</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar
# ============================================================================
with st.sidebar:
    st.markdown("## ⚙️ Ayarlar")
    
    selected_coin = st.selectbox("Coin Seç", ['BTCUSDT', 'ETHUSDT', 'LTCUSDT'], key='coin')
    interval = st.selectbox("Timeframe", ['1m', '5m', '15m', '1h', '4h', '1d'], index=3)
    
    st.markdown("### 💰 Portfolio")
    portfolio = st.number_input("Portfolio ($)", value=10000, step=100)
    risk = st.number_input("Risk per Trade ($)", value=200, step=10)
    
    st.markdown("---")
    analyze_btn = st.button("🔍 AI ANALİZ YAP", use_container_width=True, type="primary")

# ============================================================================
# 2 Column Layout
# ============================================================================
col_left, col_right = st.columns([2, 1])

# ============================================================================
# SOL: TradingView Chart
# ============================================================================
with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📈 TradingView Chart")
    
    tv_symbol = f"BINANCE:{selected_coin}"
    
    tv_html = f"""
    <div style="height: 500px;">
        <iframe 
            src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_chart&symbol={tv_symbol}&interval={interval}&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=[]&theme=light&style=1&timezone=Europe%2FIstanbul&locale=tr"
            style="width: 100%; height: 100%; border: none;"
        ></iframe>
    </div>
    """
    
    components.html(tv_html, height=550)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# SAĞ: Canlı Fiyatlar
# ============================================================================
with col_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 Canlı Fiyatlar")
    
    coins = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
    
    for coin in coins:
        data = get_binance_price(coin)
        
        if data['available']:
            change_color = '#10b981' if data['change_24h'] >= 0 else '#ef4444'
            arrow = '↗' if data['change_24h'] >= 0 else '↘'
            
            st.markdown(f"""
            <div class="price-card">
                <div style="font-size: 0.9em; opacity: 0.9;">{coin.replace('USDT', '')}</div>
                <div class="price-big">${data['price']:,.2f}</div>
                <div style="color: white; font-weight: 600;">
                    {data['change_24h']:+.2f}% {arrow}
                </div>
                <div style="font-size: 0.85em; opacity: 0.8; margin-top: 5px;">
                    Vol: ${data['volume']/1e6:.1f}M
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown(f"<div style='text-align: center; color: #999; font-size: 0.8em; margin-top: 10px;'>{datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# ALT: AI Analizi
# ============================================================================
if analyze_btn:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🎯 AI Analiz Sonucu")
    
    with st.spinner('AI analizi yapılıyor...'):
        try:
            # ai_brain import
            import ai_brain as brain
            
            decision = brain.make_trading_decision(
                symbol=selected_coin,
                interval=interval,
                portfolio_value=portfolio,
                risk_per_trade=risk
            )
            
            # Karar göster
            signal_emoji = {'LONG': '📈', 'SHORT': '📉', 'NEUTRAL': '⏸️', 'WAIT': '⏳'}
            
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 12px; color: white;">
                <h2>{signal_emoji.get(decision['decision'], '🎯')} {decision['decision']} {decision['signal']}</h2>
                <div style="font-size: 1.2em; margin: 10px 0;">
                    Confidence: <strong>{decision['confidence']*100:.0f}%</strong> | 
                    Score: <strong>{decision['final_score']:.0f}/100</strong> | 
                    R/R: <strong>1:{decision['risk_reward']:.2f}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**💡 Sebep:** {decision['reason']}")
            
            # Pozisyon Planı
            if decision.get('entry_price') and decision['decision'] in ['LONG', 'SHORT']:
                st.markdown("---")
                st.markdown("### 💼 Pozisyon Planı")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("📍 Entry", f"${decision['entry_price']:,.2f}")
                    st.metric("💰 Position", f"${decision['position_size_usd']:,.2f}")
                
                with col2:
                    sl_pct = ((decision['stop_loss'] - decision['entry_price']) / decision['entry_price'] * 100)
                    st.metric("🛡️ Stop Loss", f"${decision['stop_loss']:,.2f}", f"{sl_pct:.2f}%")
                    st.metric("⚠️ Risk", f"${decision['risk_amount_usd']:,.2f}")
                
                # TP Levels (basit hesaplama)
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
                
                st.markdown(f"""
                <div class="tp-box">
                    <strong>TP1:</strong> ${tp1:,.2f} ({tp1_pct:+.2f}%) [R/R: 1:1] → Close 50%
                </div>
                <div class="tp-box">
                    <strong>TP2:</strong> ${tp2:,.2f} ({tp2_pct:+.2f}%) [R/R: 1:1.62] → Close 30%
                </div>
                <div class="tp-box">
                    <strong>TP3:</strong> ${tp3:,.2f} ({tp3_pct:+.2f}%) [R/R: 1:2.62] → Close 20%
                </div>
                """, unsafe_allow_html=True)
                
                st.info("**📈 Trailing Stop:** TP1 sonrası SL'i entry'e çek. TP2 sonrası SL'i TP1'e çek.")
        
        except Exception as e:
            st.error(f"❌ Analiz hatası: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 20px;'>
    <p><strong>🔱 DEMIR AI Trading Bot v3</strong></p>
    <p style='font-size: 0.9em; opacity: 0.8;'>© 2025 | Professional Live Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh her 5 saniye (sadece canlı fiyatlar için)
if not analyze_btn:
    time.sleep(5)
    st.rerun()
