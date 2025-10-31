"""
🔱 DEMIR AI TRADING BOT - DASHBOARD v4
Phase 1: Trade History + Win Rate + Excel Export
Tarih: 31 Ekim 2025

YENİ ÖZELLİKLER:
✅ Trade history database
✅ Win rate calculator
✅ Performance dashboard (sidebar)
✅ Excel export
✅ Auto-save AI decisions
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime
import time

# Phase 1 imports
import trade_history_db as db
import win_rate_calculator as wrc

# AI Brain import
try:
    import ai_brain as brain
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

# ============================================================================
# Page Config
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
    .stat-box {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
        text-align: center;
    }
    .stat-value {
        font-size: 1.8em;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Header
# ============================================================================
st.markdown("""
<div class="card" style="text-align: center;">
    <h1 style="color: #667eea; margin: 0;">🔱 DEMIR AI TRADING BOT v4</h1>
    <p style="color: #666;">Phase 1: Trade History + Performance Tracking</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar - Performance Dashboard
# ============================================================================
with st.sidebar:
    st.markdown("## ⚙️ Ayarlar")
    
    selected_coin = st.selectbox("Coin Seç", ['BTCUSDT', 'ETHUSDT', 'LTCUSDT'], key='coin')
    interval = st.selectbox("Timeframe", ['1m', '5m', '15m', '1h', '4h', '1d'], index=3)
    
    st.markdown("### 💰 Portfolio")
    portfolio = st.number_input("Portfolio ($)", value=10000, step=100)
    risk = st.number_input("Risk per Trade ($)", value=200, step=10)
    
    st.markdown("---")
    
    # Performance Dashboard Widget
    st.markdown("### 📊 Performance")
    
    perf = wrc.get_performance_dashboard()
    
    if perf['total_trades'] > 0:
        # Win Rate
        win_rate_color = '#10b981' if perf['win_rate'] >= 50 else '#ef4444'
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg, {win_rate_color}, #38ef7d);">
            <div style="font-size: 0.9em; opacity: 0.9;">Win Rate</div>
            <div class="stat-value">{perf['win_rate']:.1f}%</div>
            <div style="font-size: 0.85em;">{perf['winning_trades']}W / {perf['losing_trades']}L</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Total PNL
        pnl_color = '#10b981' if perf['total_pnl_usd'] >= 0 else '#ef4444'
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg, {pnl_color}, #667eea);">
            <div style="font-size: 0.9em; opacity: 0.9;">Total PNL</div>
            <div class="stat-value">${perf['total_pnl_usd']:,.2f}</div>
            <div style="font-size: 0.85em;">{perf['total_trades']} Trades</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sharpe Ratio
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg, #667eea, #764ba2);">
            <div style="font-size: 0.9em; opacity: 0.9;">Sharpe Ratio</div>
            <div class="stat-value">{perf['sharpe_ratio']:.2f}</div>
            <div style="font-size: 0.85em;">Profit Factor: {perf['profit_factor']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("📊 Henüz trade kaydı yok")
    
    st.markdown("---")
    
    # Analyze button
    analyze_btn = st.button("🔍 AI ANALİZ YAP", use_container_width=True, type="primary")
    
    # Trade History button
    if st.button("📜 Trade History", use_container_width=True):
        st.session_state.show_history = True

# ============================================================================
# Main Content - Tabs
# ============================================================================
tab1, tab2 = st.tabs(["📈 Live Dashboard", "📜 Trade History"])

# ============================================================================
# TAB 1: Live Dashboard
# ============================================================================
with tab1:
    col_left, col_right = st.columns([2, 1])
    
    # SOL: TradingView
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
    
    # SAĞ: Canlı Fiyatlar
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
    
    # AI Analiz Sonucu
    if analyze_btn and AI_AVAILABLE:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🎯 AI Analiz Sonucu")
        
        with st.spinner('AI analizi yapılıyor...'):
            try:
                decision = brain.make_trading_decision(
                    symbol=selected_coin,
                    interval=interval,
                    portfolio_value=portfolio,
                    risk_per_trade=risk
                )
                
                # ✅ PHASE 1: Otomatik database'e kaydet
                trade_id = db.log_trade(decision)
                st.session_state.last_trade_id = trade_id
                
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
                    <div style="font-size: 0.9em; margin-top: 10px; opacity: 0.9;">
                        Trade ID: #{trade_id} | Saved to database ✅
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**💡 Sebep:** {decision['reason']}")
                
                # Pozisyon Planı + TP
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
                    
                    # TP Levels
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
# TAB 2: Trade History
# ============================================================================
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📜 Trade History")
    
    trades_df = db.get_all_trades()
    
    if not trades_df.empty:
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Trades", len(trades_df))
        with col2:
            pending = len(trades_df[trades_df['status'] == 'PENDING'])
            st.metric("Pending", pending)
        with col3:
            closed = len(trades_df[trades_df['status'].isin(['WIN', 'LOSS', 'BREAKEVEN'])])
            st.metric("Closed", closed)
        with col4:
            if closed > 0:
                wins = len(trades_df[trades_df['status'] == 'WIN'])
                wr = (wins / closed * 100)
                st.metric("Win Rate", f"{wr:.1f}%")
            else:
                st.metric("Win Rate", "N/A")
        
        st.markdown("---")
        
        # Table
        st.dataframe(
            trades_df[['id', 'timestamp', 'symbol', 'signal', 'confidence', 'final_score', 
                       'entry_price', 'stop_loss', 'position_size_usd', 'status', 'pnl_usd', 'pnl_pct']],
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Export button
        if st.button("📥 Export to Excel", type="primary"):
            filename = db.export_to_excel()
            st.success(f"✅ Exported to {filename}")
            st.download_button(
                label="⬇️ Download Excel",
                data=open(filename, 'rb').read(),
                file_name=filename,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        # Manual trade update
        st.markdown("---")
        st.markdown("### ✏️ Update Trade Result")
        
        col_u1, col_u2, col_u3, col_u4 = st.columns(4)
        
        with col_u1:
            trade_id_update = st.number_input("Trade ID", min_value=1, step=1)
        with col_u2:
            close_price = st.number_input("Close Price", min_value=0.0, step=0.01)
        with col_u3:
            status = st.selectbox("Status", ['WIN', 'LOSS', 'BREAKEVEN'])
        with col_u4:
            if st.button("Update"):
                db.update_trade_result(trade_id_update, close_price, status)
                st.success(f"✅ Trade #{trade_id_update} updated!")
                st.rerun()
    
    else:
        st.info("📊 Henüz trade kaydı yok. AI Analiz yapın!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 20px;'>
    <p><strong>🔱 DEMIR AI Trading Bot v4</strong></p>
    <p style='font-size: 0.9em; opacity: 0.8;'>Phase 1: Trade History + Performance Tracking | © 2025</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh (sadece Live Dashboard tab için)
if not analyze_btn:
    time.sleep(5)
    st.rerun()
