"""
🔱 DEMIR AI TRADING BOT - DASHBOARD v5
ULTIMATE EDITION: Detaylı Analiz + Yardım Butonu + Zengin UI
Tarih: 1 Kasım 2025

YENİ ÖZELLİKLER:
✅ 11 Layer detaylı skorlar
✅ Component breakdown
✅ Yardım/Glossary butonu
✅ TradingView kaldırıldı (canlı fiyatlar büyütüldü)
✅ Entry/SL/TP her zaman göster
✅ Görsel score progress bar'lar
✅ Detaylı "Reason" açıklamaları
"""

import streamlit as st
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
    page_title="🔱 DEMIR AI Dashboard v5",
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
                'high_24h': float(data['highPrice']),
                'low_24h': float(data['lowPrice']),
                'available': True
            }
    except:
        pass
    return {'price': 0, 'change_24h': 0, 'volume': 0, 'high_24h': 0, 'low_24h': 0, 'available': False}

def render_progress_bar(value, max_val=100, color='#667eea'):
    """Progress bar HTML"""
    pct = (value / max_val) * 100
    return f"""
    <div style="background: #f0f0f0; border-radius: 10px; height: 20px; overflow: hidden; margin: 5px 0;">
        <div style="background: {color}; width: {pct}%; height: 100%; border-radius: 10px; 
                    display: flex; align-items: center; justify-content: center; color: white; font-size: 0.75em; font-weight: 600;">
            {value:.1f}
        </div>
    </div>
    """

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
        padding: 20px;
        margin: 10px 0;
    }
    .price-big {
        font-size: 2.5em;
        font-weight: 700;
        margin: 10px 0;
    }
    .price-detail {
        display: flex;
        justify-content: space-between;
        margin: 5px 0;
        font-size: 0.9em;
        opacity: 0.9;
    }
    .tp-box {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
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
    .layer-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    .signal-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 1.1em;
    }
    .badge-long {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }
    .badge-short {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
    }
    .badge-neutral {
        background: linear-gradient(135deg, #6b7280, #4b5563);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Header
# ============================================================================
st.markdown("""
<div class="card" style="text-align: center;">
    <h1 style="color: #667eea; margin: 0;">🔱 DEMIR AI TRADING BOT v5</h1>
    <p style="color: #666;">ULTIMATE EDITION: Detaylı Analiz + 11 Layer Breakdown + Performance Tracking</p>
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
    
    # ✅ YARDIM BUTONU (YENİ!)
    st.markdown("---")
    show_help = st.checkbox("❓ Terimler Rehberi", help="Tüm terimlerin açıklamasını göster")

# ============================================================================
# YARDIM/GLOSSARY EXPANDER (YENİ!)
# ============================================================================
if show_help:
    with st.expander("📚 TERİMLER KILAVUZU - Tıklayın", expanded=True):
        st.markdown("""
        ### 🎯 Temel Terimler
        
        **LONG**: Al (fiyat yükselecek) - Fiyat artarsa kazanırsın  
        **SHORT**: Sat (fiyat düşecek) - Fiyat düşerse kazanırsın  
        **Confidence**: AI'ın ne kadar emin (≥70% = güçlü, <50% = zayıf)  
        **Score**: AI'ın final puanı (≥65=LONG, ≤35=SHORT, 35-65=NEUTRAL)  
        **R/R**: Risk/Reward (1:2 = $1 risk → $2 kazanç)  
        
        ### 💼 Pozisyon Planı
        
        **Entry**: Trade açma fiyatı  
        **SL (Stop Loss)**: Zarar durdur - fiyat buraya gelirse kapat  
        **Position**: Trade için toplam yatırım ($)  
        **Risk**: Maksimum kaybedebileceğin para  
        
        ### 🎯 Take Profit (TP)
        
        **TP1**: İlk kar al (1:1) → %50 pozisyon kapat  
        **TP2**: İkinci kar al (1:1.62 Fibonacci) → %30 kapat  
        **TP3**: Üçüncü kar al (1:2.62) → %20 kapat  
        
        ### 📊 Performance Metrikleri
        
        **Win Rate**: Kazanan trade % (≥60% = mükemmel)  
        **Sharpe Ratio**: Risk-adjusted getiri (>3 = profesyonel)  
        **Profit Factor**: Toplam kar / Toplam zarar (>2 = çok iyi)  
        **Max Drawdown**: En büyük portfolio düşüşü (<20% = iyi)  
        
        ### 🧠 AI Layer'ları
        
        **Volume Profile**: POC, VAH, VAL seviyelerini analiz eder  
        **Pivot Points**: Önceki gün H/L/C'den destek/direnç hesaplar  
        **Fibonacci**: 0.236, 0.382, 0.618, 0.786 retracement seviyeleri  
        **VWAP**: Volume-weighted average price + std dev bantları  
        **News Sentiment**: Fear & Greed Index + volume trend  
        **GARCH**: Volatilite tahmini (GARCH(1,1) modeli)  
        **Markov**: Piyasa rejimi (TREND/RANGE/HIGH_VOL)  
        **HVI**: Historical volatility index (σ score)  
        **Volatility Squeeze**: BB + KC squeeze detection  
        
        Daha fazla detay için: **GLOSSARY_DASHBOARD_TR.md** dosyasını inceleyin!
        """)

# ============================================================================
# Main Content - Tabs
# ============================================================================
tab1, tab2 = st.tabs(["📈 Live Dashboard", "📜 Trade History"])

# ============================================================================
# TAB 1: Live Dashboard
# ============================================================================
with tab1:
    # ✅ CANLI FİYATLAR (TradingView kaldırıldı - daha büyük)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 Canlı Fiyatlar")
    
    cols = st.columns(3)
    coins = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
    
    for idx, coin in enumerate(coins):
        data = get_binance_price(coin)
        
        with cols[idx]:
            if data['available']:
                change_color = '#10b981' if data['change_24h'] >= 0 else '#ef4444'
                arrow = '↗' if data['change_24h'] >= 0 else '↘'
                
                st.markdown(f"""
                <div class="price-card">
                    <div style="font-size: 1.2em; font-weight: 600; opacity: 0.9;">{coin.replace('USDT', '')}</div>
                    <div class="price-big">${data['price']:,.2f}</div>
                    <div style="color: white; font-weight: 700; font-size: 1.2em; margin: 10px 0;">
                        {data['change_24h']:+.2f}% {arrow}
                    </div>
                    <div class="price-detail">
                        <span>24h High:</span>
                        <span>${data['high_24h']:,.2f}</span>
                    </div>
                    <div class="price-detail">
                        <span>24h Low:</span>
                        <span>${data['low_24h']:,.2f}</span>
                    </div>
                    <div class="price-detail" style="margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px;">
                        <span>Volume:</span>
                        <span>${data['volume']/1e6:.1f}M</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"<div style='text-align: center; color: white; font-size: 0.9em; margin-top: 10px;'>Son güncelleme: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ✅ AI ANALİZ SONUCU (DETAYLI!)
    if analyze_btn and AI_AVAILABLE:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🎯 AI Analiz Sonucu")
        
        with st.spinner('AI analizi yapılıyor... (11 layer hesaplanıyor)'):
            try:
                decision = brain.make_trading_decision(
                    symbol=selected_coin,
                    interval=interval,
                    portfolio_value=portfolio,
                    risk_per_trade=risk
                )
                
                # ✅ Database'e kaydet
                trade_id = db.log_trade(decision)
                st.session_state.last_trade_id = trade_id
                
                # ✅ Signal Badge
                signal = decision['decision']
                signal_emoji = {'LONG': '📈', 'SHORT': '📉', 'NEUTRAL': '⏸️', 'WAIT': '⏳'}
                badge_class = {
                    'LONG': 'badge-long',
                    'SHORT': 'badge-short',
                    'NEUTRAL': 'badge-neutral',
                    'WAIT': 'badge-neutral'
                }
                
                st.markdown(f"""
                <div style="text-align: center; padding: 30px;">
                    <div class="signal-badge {badge_class.get(signal, 'badge-neutral')}">
                        {signal_emoji.get(signal, '🎯')} {signal} {decision['signal']}
                    </div>
                    <div style="font-size: 1.3em; margin: 20px 0; color: #333;">
                        Confidence: <strong>{decision['confidence']*100:.0f}%</strong> | 
                        Score: <strong>{decision['final_score']:.1f}/100</strong> | 
                        R/R: <strong>1:{decision['risk_reward']:.2f}</strong>
                    </div>
                    <div style="font-size: 0.95em; color: #666; margin-top: 15px;">
                        Trade ID: #{trade_id} | Saved to database ✅
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # ✅ REASON (detaylı açıklama)
                st.markdown(f"**💡 Karar Gerekçesi:**")
                st.info(decision['reason'])
                
                # ✅ LAYER BREAKDOWN (YENİ!)
                st.markdown("---")
                st.markdown("### 🧠 11 Layer Detaylı Analiz")
                
                # Component scores varsa göster
                if 'component_scores' in decision:
                    scores = decision['component_scores']
                    
                    col1, col2 = st.columns(2)
                    
                    layer_info = {
                        'volume_profile': {'name': 'Volume Profile', 'desc': 'POC, VAH, VAL analizi', 'weight': 0.12},
                        'pivot_points': {'name': 'Pivot Points', 'desc': 'Destek/Direnç seviyeleri', 'weight': 0.10},
                        'fibonacci': {'name': 'Fibonacci', 'desc': 'Retracement seviyeleri', 'weight': 0.10},
                        'vwap': {'name': 'VWAP', 'desc': 'Volume-weighted price', 'weight': 0.08},
                        'news_sentiment': {'name': 'News Sentiment', 'desc': 'Fear & Greed Index', 'weight': 0.08},
                        'garch': {'name': 'GARCH Volatility', 'desc': 'Volatilite tahmini', 'weight': 0.15},
                        'markov': {'name': 'Markov Regime', 'desc': 'Piyasa rejimi tespiti', 'weight': 0.15},
                        'hvi': {'name': 'Historical Vol.', 'desc': 'Geçmiş volatilite', 'weight': 0.12},
                        'squeeze': {'name': 'Vol. Squeeze', 'desc': 'BB + KC squeeze', 'weight': 0.10}
                    }
                    
                    idx = 0
                    for key, info in layer_info.items():
                        if key in scores:
                            score_val = scores[key].get('score', 0)
                            available = scores[key].get('available', False)
                            
                            target_col = col1 if idx % 2 == 0 else col2
                            
                            with target_col:
                                status_icon = '✅' if available else '❌'
                                color = '#667eea' if available else '#d1d5db'
                                
                                st.markdown(f"""
                                <div class="layer-card">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                        <strong style="font-size: 1.05em;">{status_icon} {info['name']}</strong>
                                        <span style="font-weight: 700; color: {color};">{score_val:.1f}/100</span>
                                    </div>
                                    <div style="font-size: 0.85em; color: #666; margin-bottom: 8px;">{info['desc']}</div>
                                    {render_progress_bar(score_val, color=color)}
                                    <div style="font-size: 0.8em; color: #999; margin-top: 5px;">Weight: {info['weight']*100:.0f}%</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            idx += 1
                
                else:
                    st.warning("⚠️ Component scores mevcut değil (decision dict'te 'component_scores' key'i eksik)")
                
                # ✅ POZİSYON PLANI + TP (HER ZAMAN GÖSTER)
                st.markdown("---")
                st.markdown("### 💼 Pozisyon Planı")
                
                if decision.get('entry_price') and decision['decision'] in ['LONG', 'SHORT', 'NEUTRAL']:
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
                        <strong style="font-size: 1.1em;">🎯 TP1:</strong> ${tp1:,.2f} ({tp1_pct:+.2f}%) [R/R: 1:1]<br>
                        <span style="font-size: 0.9em; color: #666;">→ Close 50% of position | Kar garantiye al</span>
                    </div>
                    <div class="tp-box">
                        <strong style="font-size: 1.1em;">🎯 TP2:</strong> ${tp2:,.2f} ({tp2_pct:+.2f}%) [R/R: 1:1.62]<br>
                        <span style="font-size: 0.9em; color: #666;">→ Close 30% of position | Fibonacci golden ratio</span>
                    </div>
                    <div class="tp-box">
                        <strong style="font-size: 1.1em;">🎯 TP3:</strong> ${tp3:,.2f} ({tp3_pct:+.2f}%) [R/R: 1:2.62]<br>
                        <span style="font-size: 0.9em; color: #666;">→ Close 20% of position | Maksimum kar hedefi</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.info("**📈 Trailing Stop Stratejisi:** TP1 sonrası SL'i entry'e çek (breakeven). TP2 sonrası SL'i TP1 seviyesine çek.")
                
                else:
                    st.warning("⚠️ Pozisyon planı mevcut değil - Entry price hesaplanamadı veya sinyal WAIT/NEUTRAL")
            
            except Exception as e:
                st.error(f"❌ Analiz hatası: {e}")
                st.exception(e)
        
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
    <p><strong>🔱 DEMIR AI Trading Bot v5 - ULTIMATE EDITION</strong></p>
    <p style='font-size: 0.9em; opacity: 0.8;'>Detaylı Analiz + 11 Layer Breakdown + Performance Tracking | © 2025</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh (sadece Live Dashboard tab için)
if not analyze_btn:
    time.sleep(5)
    st.rerun()
