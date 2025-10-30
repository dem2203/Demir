"""
DEMIR - Professional AI Trading Dashboard
Ultra-Modern UI with AI Brain Integration + Custom Coin Input
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# Modül importları
try:
    import config
    import db_layer
    import external_data
    import analysis_layer
    import strategy_layer
    from websocket_client import BinanceFuturesWebSocket
except ImportError as e:
    st.error(f"⚠️ Modül yükleme hatası: {e}")
    st.stop()

# AI Brain import
try:
    from ai_brain import AIBrain
    AI_BRAIN_AVAILABLE = True
except ImportError:
    AI_BRAIN_AVAILABLE = False
    st.warning("⚠️ AI Brain modülü yüklenemedi. Normal mode aktif.")

# Sayfa yapılandırması
st.set_page_config(
    page_title="DEMIR AI Trading",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# MODERN DARK THEME CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
    }
    
    .sub-title {
        text-align: center;
        color: #8b92a7;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 1rem;
    }
    
    .price-ticker {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .ticker-coin {
        display: inline-block;
        margin-right: 2rem;
        color: white;
        font-weight: 600;
    }
    
    .signal-card-buy {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 8px 25px rgba(56, 239, 125, 0.4);
        animation: pulse 2s infinite;
    }
    
    .signal-card-sell {
        background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 8px 25px rgba(238, 9, 121, 0.4);
        animation: pulse 2s infinite;
    }
    
    .signal-card-hold {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 8px 25px rgba(240, 147, 251, 0.4);
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.08);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .metric-label {
        color: #8b92a7;
        font-size: 0.9rem;
        margin-bottom: 0.3rem;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.7rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0e27;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# SESSION STATE
# ============================================

def init_session_state():
    if 'ws_data' not in st.session_state:
        st.session_state.ws_data = {}
    if 'ws_clients' not in st.session_state:
        st.session_state.ws_clients = {}
    if 'last_analysis' not in st.session_state:
        st.session_state.last_analysis = {}
    if 'analysis_running' not in st.session_state:
        st.session_state.analysis_running = False
    if 'ai_mode' not in st.session_state:
        st.session_state.ai_mode = False
    if 'capital' not in st.session_state:
        st.session_state.capital = 10000
    if 'tracked_coins' not in st.session_state:
        # SABİT 3 COİN
        st.session_state.tracked_coins = ['btcusdt', 'ethusdt', 'ltcusdt']


# ============================================
# CANDLESTICK CHART ENGINE
# ============================================

def create_advanced_chart(df, symbol, tech_data):
    """TradingView-style candlestick chart"""
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f'{symbol.upper()} Price Action', 'RSI', 'MACD')
    )
    
    fig.add_trace(
        go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ),
        row=1, col=1
    )
    
    if 'EMA_9' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['EMA_9'], 
                      name='EMA 9', line=dict(color='#ff9800', width=1)),
            row=1, col=1
        )
    
    if 'EMA_21' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['EMA_21'], 
                      name='EMA 21', line=dict(color='#2196f3', width=1)),
            row=1, col=1
        )
    
    if all(k in df.columns for k in ['BB_upper', 'BB_lower']):
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['BB_upper'], 
                      name='BB Upper', line=dict(color='rgba(250, 250, 250, 0.2)', width=1)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['BB_lower'], 
                      name='BB Lower', line=dict(color='rgba(250, 250, 250, 0.2)', width=1),
                      fill='tonexty', fillcolor='rgba(250, 250, 250, 0.05)'),
            row=1, col=1
        )
    
    if 'RSI' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['RSI'], 
                      name='RSI', line=dict(color='#9c27b0', width=2)),
            row=2, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    if all(k in df.columns for k in ['MACD', 'MACD_signal']):
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['MACD'], 
                      name='MACD', line=dict(color='#00bcd4', width=2)),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['MACD_signal'], 
                      name='Signal', line=dict(color='#ff5722', width=1)),
            row=3, col=1
        )
    
    fig.update_layout(
        template='plotly_dark',
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.3)',
        font=dict(color='#ffffff')
    )
    
    return fig


# ============================================
# WEBSOCKET FUNCTIONS
# ============================================

def start_websocket(symbols):
    for symbol in symbols:
        if symbol not in st.session_state.ws_clients:
            try:
                ws = BinanceFuturesWebSocket(symbol)
                
                def price_callback(data, sym=symbol):
                    st.session_state.ws_data[sym] = data
                
                ws.on_price_update = price_callback
                ws.start()
                st.session_state.ws_clients[symbol] = ws
            except Exception as e:
                st.error(f"WebSocket error ({symbol}): {e}")


def stop_websocket():
    for ws in st.session_state.ws_clients.values():
        try:
            ws.stop()
        except:
            pass
    st.session_state.ws_clients = {}


# ============================================
# PRICE TICKER
# ============================================

def display_price_ticker():
    if not st.session_state.ws_data:
        st.markdown('<div class="price-ticker">⏳ Connecting to live data...</div>', unsafe_allow_html=True)
        return
    
    ticker_html = '<div class="price-ticker">'
    for symbol, data in st.session_state.ws_data.items():
        price = data.get('price', 0)
        coin = symbol.replace('usdt', '').upper()
        ticker_html += f'<span class="ticker-coin">🪙 {coin}: ${price:,.2f}</span>'
    ticker_html += '</div>'
    
    st.markdown(ticker_html, unsafe_allow_html=True)


# ============================================
# ANALYSIS RUNNERS
# ============================================

def run_analysis(symbol, timeframe='1h'):
    try:
        st.session_state.analysis_running = True
        
        with st.spinner(f"🔍 Analyzing {symbol.upper()}..."):
            ext_data = external_data.get_all_external_data()
            tech_analysis = analysis_layer.run_full_analysis(symbol, timeframe)
            signal = strategy_layer.generate_signal(
                symbol=symbol,
                tech_data=tech_analysis,
                external_data=ext_data
            )
            
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': datetime.now(),
                'external_data': ext_data,
                'technical': tech_analysis,
                'signal': signal,
                'mode': 'NORMAL'
            }
            
            st.session_state.last_analysis[symbol] = result
            
        st.session_state.analysis_running = False
        return result
        
    except Exception as e:
        st.error(f"❌ Analysis error: {e}")
        st.session_state.analysis_running = False
        return None


def run_ai_brain_analysis(symbol):
    """AI Brain ile profesyonel analiz"""
    try:
        st.session_state.analysis_running = True
        
        with st.spinner(f"🧠 AI Brain analyzing {symbol.upper()}..."):
            brain = AIBrain()
            decision = brain.make_decision(symbol, st.session_state.capital)
            
            result = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'ai_decision': decision,
                'mode': 'AI_BRAIN'
            }
            
            st.session_state.last_analysis[symbol] = result
            
        st.session_state.analysis_running = False
        return result
        
    except Exception as e:
        st.error(f"❌ AI Brain error: {e}")
        st.session_state.analysis_running = False
        return None


# ============================================
# SIGNAL DISPLAYS
# ============================================

def display_signal(signal_data):
    if not signal_data:
        return
    
    signal = signal_data.get('signal', 'HOLD')
    confidence = signal_data.get('confidence', 0)
    factors = signal_data.get('factors', {})
    
    if signal == 'BUY':
        st.markdown(f"""
        <div class="signal-card-buy">
            <h2>🟢 STRONG BUY SIGNAL</h2>
            <p style="font-size:1.3rem;">Confidence: <strong>{confidence:.1f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)
    elif signal == 'SELL':
        st.markdown(f"""
        <div class="signal-card-sell">
            <h2>🔴 STRONG SELL SIGNAL</h2>
            <p style="font-size:1.3rem;">Confidence: <strong>{confidence:.1f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="signal-card-hold">
            <h2>🟡 HOLD / WAIT</h2>
            <p style="font-size:1.3rem;">Confidence: <strong>{confidence:.1f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("🧠 AI Decision Breakdown")
    
    cols = st.columns(3)
    for idx, (factor, score) in enumerate(sorted(factors.items(), key=lambda x: abs(x[1]), reverse=True)[:6]):
        with cols[idx % 3]:
            color = '#26a69a' if score > 0 else '#ef5350'
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{factor.upper()}</div>
                <div class="metric-value" style="color:{color};">{score:+.1f}</div>
            </div>
            """, unsafe_allow_html=True)


def display_ai_decision(decision_data):
    """AI Brain kararını profesyonel göster"""
    if not decision_data:
        return
    
    signal = decision_data.get('signal', 'HOLD')
    confidence = decision_data.get('confidence', 0)
    reasoning = decision_data.get('reasoning', [])
    metadata = decision_data.get('metadata', {})
    
    if signal == 'BUY':
        st.markdown(f"""
        <div class="signal-card-buy">
            <h2>🟢 AI BRAIN: STRONG BUY</h2>
            <p style="font-size:1.3rem;">Confidence: <strong>{confidence:.1f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)
    elif signal == 'SELL':
        st.markdown(f"""
        <div class="signal-card-sell">
            <h2>🔴 AI BRAIN: STRONG SELL</h2>
            <p style="font-size:1.3rem;">Confidence: <strong>{confidence:.1f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="signal-card-hold">
            <h2>🟡 AI BRAIN: HOLD / WAIT</h2>
            <p style="font-size:1.3rem;">Confidence: <strong>{confidence:.1f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("💰 Position & Risk Management")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Position Size</div>
            <div class="metric-value">${decision_data.get('position_size', 0):.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Stop Loss</div>
            <div class="metric-value" style="color:#ef5350;">${decision_data.get('stop_loss', 0):.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Take Profit</div>
            <div class="metric-value" style="color:#26a69a;">${decision_data.get('take_profit_1', 0):.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        rr = decision_data.get('risk_reward_ratio', 0)
        rr_color = '#26a69a' if rr >= 2 else '#ff9800' if rr >= 1.5 else '#ef5350'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">R/R Ratio</div>
            <div class="metric-value" style="color:{rr_color};">1:{rr:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("🧠 AI Decision Reasoning")
    
    for reason in reasoning:
        if '✅' in reason:
            st.success(reason)
        elif '⚠️' in reason:
            st.warning(reason)
        elif '❌' in reason:
            st.error(reason)
        else:
            st.info(reason)
    
    regime_data = metadata.get('regime', {})
    if regime_data:
        regime = regime_data.get('regime', 'UNKNOWN')
        regime_conf = regime_data.get('confidence', 0)
        
        regime_colors = {
            'TREND': '#26a69a',
            'RANGE': '#ff9800',
            'VOLATILE': '#ef5350'
        }
        
        st.markdown(f"""
        <div class="metric-card" style="border-left-color:{regime_colors.get(regime, '#666')};">
            <div class="metric-label">Market Regime</div>
            <div class="metric-value" style="color:{regime_colors.get(regime, '#666')};">{regime}</div>
            <div style="color:#8b92a7;">Confidence: {regime_conf:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    mtf_data = metadata.get('mtf_confluence', {})
    if mtf_data:
        st.subheader("⏱️ Multi-Timeframe Analysis")
        
        tf_signals = mtf_data.get('timeframe_signals', {})
        aligned = mtf_data.get('aligned', False)
        
        cols = st.columns(len(tf_signals))
        
        for idx, (tf, sig) in enumerate(tf_signals.items()):
            with cols[idx]:
                sig_emoji = '🟢' if sig == 'BUY' else '🔴' if sig == 'SELL' else '🟡'
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{tf.upper()}</div>
                    <div class="metric-value">{sig_emoji} {sig}</div>
                </div>
                """, unsafe_allow_html=True)
        
        if aligned:
            st.success("✅ All timeframes are aligned!")
        else:
            st.warning("⚠️ Timeframes show divergence")


# ============================================
# MAIN APP
# ============================================

def main():
    init_session_state()
    
    st.markdown('<h1 class="main-title">⚡ DEMIR AI TRADING</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Professional-Grade AI-Powered Crypto Trading System</p>', unsafe_allow_html=True)
    
    # CUSTOM COIN INPUT + SABİT 3 COİN
    col_input, col_add, col_tf, col_ws, col_ai, col_analyze = st.columns([2, 0.8, 1.5, 0.8, 0.8, 1])
    
    with col_input:
        new_coin = st.text_input("➕ Coin Ekle (örn: SOLUSDT)", "").upper()
    
    with col_add:
        st.write("")  # Boşluk
        st.write("")  # Boşluk
        if st.button("Ekle"):
            if new_coin and new_coin.lower() not in st.session_state.tracked_coins:
                st.session_state.tracked_coins.append(new_coin.lower())
                st.success(f"✅ {new_coin} eklendi!")
            elif new_coin.lower() in st.session_state.tracked_coins:
                st.warning(f"⚠️ {new_coin} zaten listede!")
    
    with col_tf:
        timeframe = st.selectbox("⏱️ Timeframe", ['15m', '1h', '4h', '1d'], index=1)
    
    with col_ws:
        st.write("")
        st.write("")
        if st.button("▶️ Start WS"):
            start_websocket(st.session_state.tracked_coins)
            st.success("✅ Live!")
    
    with col_ai:
        st.write("")
        st.write("")
        if AI_BRAIN_AVAILABLE:
            st.session_state.ai_mode = st.toggle("🧠 AI", value=st.session_state.ai_mode)
    
    with col_analyze:
        st.write("")
        st.write("")
        if st.button("🚀 Analyze All"):
            for coin in st.session_state.tracked_coins:
                if st.session_state.ai_mode and AI_BRAIN_AVAILABLE:
                    run_ai_brain_analysis(coin)
                else:
                    run_analysis(coin, timeframe)
    
    # SABİT COİN GÖSTERİMİ
    st.caption(f"📊 Takip edilen coinler: {', '.join([c.upper() for c in st.session_state.tracked_coins])}")
    
    display_price_ticker()
    
    st.divider()
    
    if st.session_state.tracked_coins:
        # Seçili coin için analiz göster
        selected_coin_display = st.selectbox("Analiz görüntülenecek coin", st.session_state.tracked_coins)
        
        if selected_coin_display in st.session_state.last_analysis:
            analysis = st.session_state.last_analysis[selected_coin_display]
            
            if analysis.get('mode') == 'AI_BRAIN':
                ai_decision = analysis.get('ai_decision')
                display_ai_decision(ai_decision)
                
                tech_data = ai_decision.get('metadata', {}).get('base_signal', {})
                if tech_data and 'dataframe' in tech_data and not tech_data['dataframe'].empty:
                    st.subheader("📈 Technical Chart")
                    df = tech_data['dataframe']
                    fig = create_advanced_chart(df, selected_coin_display, tech_data)
                    st.plotly_chart(fig, use_container_width=True)
            
            else:
                display_signal(analysis.get('signal'))
                
                tech_data = analysis.get('technical', {})
                if 'dataframe' in tech_data and not tech_data['dataframe'].empty:
                    st.subheader("📈 Technical Analysis Chart")
                    df = tech_data['dataframe']
                    fig = create_advanced_chart(df, selected_coin_display, tech_data)
                    st.plotly_chart(fig, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fg = analysis['external_data'].get('fear_greed', {})
                    if isinstance(fg, dict):
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Fear & Greed Index</div>
                            <div class="metric-value">{fg.get('value', 'N/A')}</div>
                            <div style="color:#8b92a7;">{fg.get('classification', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    rsi = tech_data.get('rsi', 0)
                    rsi_color = '#ef5350' if rsi > 70 else '#26a69a' if rsi < 30 else '#ff9800'
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">RSI (14)</div>
                        <div class="metric-value" style="color:{rsi_color};">{rsi:.1f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    macd_val = tech_data.get('macd_histogram', 0)
                    macd_status = "Bullish ↑" if macd_val > 0 else "Bearish ↓"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">MACD Signal</div>
                        <div class="metric-value">{macd_status}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        else:
            st.info("💡 Click 'Analyze All' button to generate signals")
    
    else:
        st.warning("⚠️ No coins in tracking list")
    
    st.divider()
    st.caption("🔥 DEMIR AI Trading System | Powered by Advanced Machine Learning")
    
    time.sleep(1)
    st.rerun()


if __name__ == "__main__":
    main()
