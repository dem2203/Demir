"""
🔱 DEMIR AI TRADING BOT - LIVE DASHBOARD v3
Akıllı Hibrit: TradingView + WebSocket + TP1/TP2/TP3
Tarih: 31 Ekim 2025

YENİ ÖZELLİKLER:
✅ TradingView chart embed
✅ Canlı fiyat (3s refresh - background thread)
✅ AI analizi (manuel button)
✅ TP1/TP2/TP3 + SL (Fibonacci)
✅ Render dostu (düşük yük)
"""

import streamlit as st
import streamlit.components.v1 as components
import ai_brain as brain
import live_price_monitor as live_mon
import tp_calculator as tp_calc
from datetime import datetime
import time

# ============================================================================
# Sayfa Yapılandırması
# ============================================================================
st.set_page_config(
    page_title="🔱 DEMIR AI Live Dashboard",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS (aynı kalıyor - zaten güzel!)
# ============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
    }
    
    .header {
        background: white;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
    }
    
    .header h1 {
        color: #667eea !important;
        margin: 0;
        font-size: 3em;
        font-weight: 700;
    }
    
    .card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .live-price {
        font-size: 2.5em;
        font-weight: 700;
        color: #1e293b;
    }
    
    .price-up {
        color: #10b981 !important;
    }
    
    .price-down {
        color: #ef4444 !important;
    }
    
    .tp-level {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Live Price Monitor Başlat (Background Thread)
# ============================================================================
if 'live_monitor_started' not in st.session_state:
    # Sidebar'dan seçilen coin'leri al
    default_coins = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
    live_mon.start_live_monitor(default_coins, interval=3)
    st.session_state.live_monitor_started = True
    print("✅ Live price monitor started!")

# ============================================================================
# Header
# ============================================================================
st.markdown("""
<div class="header">
    <h1>🔱 DEMIR AI TRADING BOT</h1>
    <p>Professional Live Dashboard | Phase 3A + 3B + Multiple TP</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar - Ayarlar
# ============================================================================
with st.sidebar:
    st.markdown("## ⚙️ Ayarlar")
    
    # Coin seçimi
    st.markdown("### 🪙 Coin Seç")
    
    if 'coin_list' not in st.session_state:
        st.session_state.coin_list = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
    
    selected_coin = st.selectbox(
        "Aktif Coin",
        st.session_state.coin_list,
        key='selected_coin'
    )
    
    # Interval
    st.markdown("### ⏰ Interval")
    interval = st.selectbox(
        "Timeframe",
        ['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
        index=4
    )
    
    # Portfolio
    st.markdown("### 💰 Portfolio")
    portfolio_value = st.number_input(
        "Portfolio ($)",
        min_value=100,
        max_value=1000000,
        value=10000,
        step=100
    )
    
    risk_per_trade = st.number_input(
        "Risk per Trade ($)",
        min_value=10,
        max_value=10000,
        value=200,
        step=10
    )
    
    st.markdown("---")
    
    # AI Analiz butonu (MANUEL)
    analyze_button = st.button("🔍 AI ANALİZ YAP", use_container_width=True, type="primary")

# ============================================================================
# Ana Layout: 2 Column
# ============================================================================
col_left, col_right = st.columns([2, 1])

# ============================================================================
# SOL KOLON: TradingView Chart
# ============================================================================
with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📈 TradingView Chart")
    
    # TradingView widget
    tradingview_symbol = f"BINANCE:{selected_coin}"
    
    tradingview_html = f"""
    <div class="tradingview-widget-container">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "width": "100%",
        "height": 500,
        "symbol": "{tradingview_symbol}",
        "interval": "{interval}",
        "timezone": "Europe/Istanbul",
        "theme": "light",
        "style": "1",
        "locale": "tr",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": false,
        "container_id": "tradingview_chart",
        "studies": [
          "BB@tv-basicstudies",
          "RSI@tv-basicstudies"
        ]
      }});
      </script>
    </div>
    """
    
    components.html(tradingview_html, height=550)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# SAĞ KOLON: Canlı Fiyatlar (3s refresh)
# ============================================================================
with col_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 Canlı Fiyatlar")
    
    # Her coin için placeholder
    for coin in st.session_state.coin_list:
        live_data = live_mon.get_live_price(coin)
        
        if live_data.get('available'):
            price = live_data['price']
            change = live_data['change_24h']
            
            # Renk belirleme
            price_class = 'price-up' if change >= 0 else 'price-down'
            arrow = '↗' if change >= 0 else '↘'
            
            st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <div style="font-weight: 600; color: #64748b; font-size: 0.9em;">{coin.replace('USDT', '')}</div>
                <div class="live-price {price_class}">${price:,.2f}</div>
                <div style="color: {'#10b981' if change >= 0 else '#ef4444'}; font-weight: 600;">
                    {change:+.2f}% {arrow}
                </div>
                <div style="font-size: 0.8em; color: #94a3b8;">
                    Vol: ${live_data['quote_volume_24h']/1e6:.1f}M
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"{coin} - Veri alınamadı")
    
    st.markdown(f"<div style='text-align: center; color: #94a3b8; font-size: 0.8em; margin-top: 10px;'>Son güncelleme: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Auto-refresh her 3 saniyede (sadece canlı fiyatlar için)
    time.sleep(0.1)  # Küçük delay
    st.rerun()

# ============================================================================
# ALT KISIM: AI Analizi (MANUEL)
# ============================================================================
if analyze_button or 'last_analysis' in st.session_state:
    
    if analyze_button:
        with st.spinner('🔍 AI analizi yapılıyor (11 modül)...'):
            try:
                decision = brain.make_trading_decision(
                    symbol=selected_coin,
                    interval=interval,
                    portfolio_value=portfolio_value,
                    risk_per_trade=risk_per_trade
                )
                st.session_state.last_analysis = decision
            except Exception as e:
                st.error(f"❌ Analiz hatası: {e}")
                st.stop()
    
    decision = st.session_state.last_analysis
    
    # AI Kararı Kartı
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🎯 AI Kararı")
    
    signal_class = {
        'LONG': 'signal-long',
        'SHORT': 'signal-short',
        'NEUTRAL': 'signal-neutral',
        'WAIT': 'signal-wait'
    }.get(decision['decision'], 'signal-neutral')
    
    st.markdown(
        f'<div class="signal-badge {signal_class}">'
        f'{decision["decision"]} {decision["signal"]}'
        f'</div>',
        unsafe_allow_html=True
    )
    
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        st.metric("Confidence", f"{decision['confidence']*100:.0f}%")
    with col_m2:
        st.metric("Score", f"{decision['final_score']:.0f}/100")
    with col_m3:
        st.metric("R/R", f"1:{decision['risk_reward']:.2f}")
    
    st.markdown(f"**Sebep:** {decision['reason']}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # POZİSYON PLANI - TP1/TP2/TP3
    if decision.get('entry_price') and decision['decision'] in ['LONG', 'SHORT']:
        
        # TP seviyelerini hesapla
        tp_levels = tp_calc.calculate_multiple_take_profits(
            entry_price=decision['entry_price'],
            stop_loss=decision['stop_loss'],
            atr=decision.get('atr', 100),
            signal_direction=decision['decision']
        )
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 💼 Pozisyon Planı")
        
        # Entry ve SL
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            st.markdown(f"**📍 Entry:** ${decision['entry_price']:,.2f}")
            st.markdown(f"**💰 Position:** ${decision['position_size_usd']:,.2f} ({decision['position_size_pct']:.2f}%)")
        
        with col_p2:
            st.markdown(f"**🛡️ Stop Loss:** ${decision['stop_loss']:,.2f} ({((decision['stop_loss']-decision['entry_price'])/decision['entry_price']*100):.2f}%)")
            st.markdown(f"**⚠️ Risk:** ${decision['risk_amount_usd']:,.2f}")
        
        st.markdown("---")
        
        # TP Levels
        st.markdown("**🎯 Take Profit Seviyeleri:**")
        
        for i, tp_key in enumerate(['tp1', 'tp2', 'tp3'], 1):
            tp = tp_levels[tp_key]
            
            st.markdown(
                f'<div class="tp-level">'
                f'<strong>TP{i}: ${tp["price"]:,.2f}</strong> '
                f'(+{tp["pct"]:.2f}%) '
                f'[R/R: 1:{tp["rr"]:.2f}]<br>'
                f'<span style="color: #64748b;">→ {tp["partial_close"]} | {tp["description"]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        # Trailing Stop
        st.info(f"**📈 Trailing Stop Stratejisi:** {tp_levels['trailing_stop']}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: white; padding: 20px;'>
        <p><strong>🔱 DEMIR AI Trading Bot v3 LIVE</strong></p>
        <p>TradingView + WebSocket + Multiple TP | Professional Dashboard</p>
        <p style='font-size: 0.9em; opacity: 0.8;'>© 2025 | Phase 3A + 3B Active</p>
    </div>
    """,
    unsafe_allow_html=True
)
