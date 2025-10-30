"""
DEMIR - Professional AI Trading Dashboard (v3.0)
Binance Futures + Multi-Coin Tabs + Türkçe Açıklamalar
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
    
    .metric-hint {
        color: #8b92a7;
        font-size: 0.8rem;
        font-style: italic;
        margin-top: 0.3rem;
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
        st.session_state.tracked_coins = ['btcusdt', 'ethusdt', 'ltcusdt']


# ============================================
# CANDLESTICK CHART ENGINE
# ============================================

def create_advanced_chart(df, symbol, tech_data):
    """TradingView-style candlestick chart"""
    
    # Kolon isimlerini normalize et
    df_chart = df.copy()
    
    # Timestamp kolonu
    if 'Timestamp' in df_chart.columns:
        timestamp_col = 'Timestamp'
    elif 'timestamp' in df_chart.columns:
        timestamp_col = 'timestamp'
    else:
        timestamp_col = df_chart.index
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f'{symbol.upper()} Price Action', 'RSI', 'MACD')
    )
    
    fig.add_trace(
        go.Candlestick(
            x=df_chart[timestamp_col] if isinstance(timestamp_col, str) else timestamp_col,
            open=df_chart['Open'],
            high=df_chart['High'],
            low=df_chart['Low'],
            close=df_chart['Close'],
            name='Price',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ),
        row=1, col=1
    )
    
    # EMA overlays
    if 'EMA_9' in df_chart.columns:
        fig.add_trace(
            go.Scatter(x=df_chart[timestamp_col] if isinstance(timestamp_col, str) else timestamp_col, 
                      y=df_chart['EMA_9'], 
                      name='EMA 9', line=dict(color='#ff9800', width=1)),
            row=1, col=1
        )
    
    if 'EMA_21' in df_chart.columns:
        fig.add_trace(
            go.Scatter(x=df_chart[timestamp_col] if isinstance(timestamp_col, str) else timestamp_col, 
                      y=df_chart['EMA_21'], 
                      name='EMA 21', line=dict(color='#2196f3', width=1)),
            row=1, col=1
        )
    
    # RSI
    if 'RSI' in df_chart.columns:
        fig.add_trace(
            go.Scatter(x=df_chart[timestamp_col] if isinstance(timestamp_col, str) else timestamp_col, 
                      y=df_chart['RSI'], 
                      name='RSI', line=dict(color='#9c27b0', width=2)),
            row=2, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # MACD
    macd_col = 'MACD' if 'MACD' in df_chart.columns else 'MACD_12_26_9'
    signal_col = 'MACD_signal' if 'MACD_signal' in df_chart.columns else 'MACDs_12_26_9'
    
    if macd_col in df_chart.columns and signal_col in df_chart.columns:
        fig.add_trace(
            go.Scatter(x=df_chart[timestamp_col] if isinstance(timestamp_col, str) else timestamp_col, 
                      y=df_chart[macd_col], 
                      name='MACD', line=dict(color='#00bcd4', width=2)),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=df_chart[timestamp_col] if isinstance(timestamp_col, str) else timestamp_col, 
                      y=df_chart[signal_col], 
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
    if not st.session_state.ws_
        st.markdown('<div class="price-ticker">⏳ Canlı veriye bağlanılıyor...</div>', unsafe_allow_html=True)
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
        
        with st.spinner(f"🔍 {symbol.upper()} analiz ediliyor..."):
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
        st.error(f"❌ Analiz hatası: {e}")
        st.session_state.analysis_running = False
        return None


def run_ai_brain_analysis(symbol):
    """AI Brain ile profesyonel analiz"""
    try:
        st.session_state.analysis_running = True
        
        with st.spinner(f"🧠 AI Brain {symbol.upper()} analiz ediyor..."):
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
        st.error(f"❌ AI Brain hatası: {e}")
        st.session_state.analysis_running = False
        return None


# ============================================
# SIGNAL DISPLAYS
# ============================================

def display_signal(signal_data):
    if not signal_
        return
    
    signal = signal_data.get('signal', 'HOLD')
    confidence = signal_data.get('confidence', 0)
    factors = signal_data.get('factors', {})
    
    if signal == 'BUY':
        st.markdown(f"""
        <div class="signal-card-buy">
            <h2>🟢 ALIŞ SİNYALİ</h2>
            <p style="font-size:1.3rem;">Güven: <strong>{confidence:.1f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)
    elif signal == 'SELL':
        st.markdown(f"""
        <div class="signal-card-sell">
            <h2>🔴 SATIŞ SİNYALİ</h2>
            <p style="font-size:1.3rem;">Güven: <strong>{confidence:.1f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="signal-card-hold">
            <h2>🟡 BEKLE</h2>
            <p style="font-size:1.3rem;">Güven: <strong>{confidence:.1f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("🧠 AI Karar Faktörleri")
    
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
    """AI Brain kararını Türkçe açıklamalarla göster"""
    if not decision_
        return
    
    signal = decision_data.get('signal', 'HOLD')
    confidence = decision_data.get('confidence', 0)
    reasoning = decision_data.get('reasoning', [])
    metadata = decision_data.get('metadata', {})
    current_price = metadata.get('current_price', 0)
    
    if signal == 'BUY':
        st.markdown(f"""
        <div class="signal-card-buy">
            <h2>🟢 AI BRAIN: GÜÇLÜ ALIŞ</h2>
            <p style="font-size:1.3rem;">Güven: <strong>{confidence:.1f}%</strong></p>
            <p style="font-size:1.1rem;">Güncel Fiyat: <strong>${current_price:,.2f}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    elif signal == 'SELL':
        st.markdown(f"""
        <div class="signal-card-sell">
            <h2>🔴 AI BRAIN: GÜÇLÜ SATIŞ</h2>
            <p style="font-size:1.3rem;">Güven: <strong>{confidence:.1f}%</strong></p>
            <p style="font-size:1.1rem;">Güncel Fiyat: <strong>${current_price:,.2f}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="signal-card-hold">
            <h2>🟡 AI BRAIN: BEKLE</h2>
            <p style="font-size:1.3rem;">Güven: <strong>{confidence:.1f}%</strong></p>
            <p style="font-size:1.1rem;">Güncel Fiyat: <strong>${current_price:,.2f}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("💰 Pozisyon & Risk Yönetimi")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pos_size = decision_data.get('position_size', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Pozisyon Büyüklüğü</div>
            <div class="metric-value">${pos_size:.0f}</div>
            <div class="metric-hint">İşleme girecek miktar</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        stop_loss = decision_data.get('stop_loss', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Stop Loss (Zarar Durdur)</div>
            <div class="metric-value" style="color:#ef5350;">${stop_loss:.2f}</div>
            <div class="metric-hint">Fiyat buraya gelirse kapat</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        take_profit = decision_data.get('take_profit_1', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Take Profit (Kar Al)</div>
            <div class="metric-value" style="color:#26a69a;">${take_profit:.2f}</div>
            <div class="metric-hint">Fiyat buraya gelirse karla kapat</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        rr = decision_data.get('risk_reward_ratio', 0)
        rr_color = '#26a69a' if rr >= 2 else '#ff9800' if rr >= 1.5 else '#ef5350'
        rr_hint = "Mükemmel!" if rr >= 3 else "İyi" if rr >= 2 else "Orta" if rr >= 1.5 else "Zayıf"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">R/R Oranı</div>
            <div class="metric-value" style="color:{rr_color};">1:{rr:.2f}</div>
            <div class="metric-hint">{rr_hint} - Risk/Ödül dengesi</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("🧠 AI Karar Açıklaması")
    
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
    if regime_
        regime = regime_data.get('regime', 'UNKNOWN')
        regime_conf = regime_data.get('confidence', 0)
        regime_exp = regime_data.get('explanation', '')
        
        regime_colors = {
            'TREND': '#26a69a',
            'RANGE': '#ff9800',
            'VOLATILE': '#ef5350'
        }
        
        st.markdown(f"""
        <div class="metric-card" style="border-left-color:{regime_colors.get(regime, '#666')};">
            <div class="metric-label">Piyasa Durumu</div>
            <div class="metric-value" style="color:{regime_colors.get(regime, '#666')};">{regime}</div>
            <div style="color:#8b92a7;">Güven: {regime_conf:.0f}%</div>
            <div class="metric-hint">{regime_exp}</div>
        </div>
        """, unsafe_allow_html=True)
    
    mtf_data = metadata.get('mtf_confluence', {})
    if mtf_
        st.subheader("⏱️ Çoklu Zaman Dilimi Analizi")
        
        tf_signals = mtf_data.get('timeframe_signals', {})
        aligned = mtf_data.get('aligned', False)
        mtf_exp = mtf_data.get('explanation', '')
        
        cols = st.columns(len(tf_signals))
        
        for idx, (tf, sig) in enumerate(tf_signals.items()):
            with cols[idx]:
                sig_emoji = '🟢' if sig == 'BUY' else '🔴' if sig == 'SELL' else '🟡'
                sig_text = 'ALIŞ' if sig == 'BUY' else 'SATIŞ' if sig == 'SELL' else 'BEKLE'
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{tf.upper()}</div>
                    <div class="metric-value">{sig_emoji} {sig_text}</div>
                </div>
                """, unsafe_allow_html=True)
        
        if aligned:
            st.success(f"✅ {mtf_exp}")
        else:
            st.warning(f"⚠️ {mtf_exp}")


# ============================================
# MAIN APP
# ============================================

def main():
    init_session_state()
    
    st.markdown('<h1 class="main-title">⚡ DEMIR AI TRADING</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Profesyonel AI-Destekli Binance Futures Trading Sistemi</p>', unsafe_allow_html=True)
    
    # CUSTOM COIN INPUT + SABİT 3 COİN
    col_input, col_add, col_tf, col_ws, col_ai, col_analyze = st.columns([2, 0.8, 1.5, 0.8, 0.8, 1])
    
    with col_input:
        new_coin = st.text_input("➕ Coin Ekle (örn: SOLUSDT)", "").upper()
    
    with col_add:
        st.write("")
        st.write("")
        if st.button("Ekle"):
            if new_coin and new_coin.lower() not in st.session_state.tracked_coins:
                st.session_state.tracked_coins.append(new_coin.lower())
                st.success(f"✅ {new_coin} eklendi!")
            elif new_coin.lower() in st.session_state.tracked_coins:
                st.warning(f"⚠️ {new_coin} zaten listede!")
    
    with col_tf:
        timeframe = st.selectbox("⏱️ Zaman Dilimi", ['15m', '1h', '4h', '1d'], index=1)
    
    with col_ws:
        st.write("")
        st.write("")
        if st.button("▶️ Canlı Veri"):
            start_websocket(st.session_state.tracked_coins)
            st.success("✅ Aktif!")
    
    with col_ai:
        st.write("")
        st.write("")
        if AI_BRAIN_AVAILABLE:
            st.session_state.ai_mode = st.toggle("🧠 AI", value=st.session_state.ai_mode)
    
    with col_analyze:
        st.write("")
        st.write("")
        if st.button("🚀 Tümünü Analiz Et"):
            for coin in st.session_state.tracked_coins:
                if st.session_state.ai_mode and AI_BRAIN_AVAILABLE:
                    run_ai_brain_analysis(coin)
                else:
                    run_analysis(coin, timeframe)
    
    st.caption(f"📊 Takip edilen: {', '.join([c.upper() for c in st.session_state.tracked_coins])}")
    
    display_price_ticker()
    
    st.divider()
    
    # MULTI-COIN TABS
    if st.session_state.tracked_coins:
        tabs = st.tabs([coin.upper() for coin in st.session_state.tracked_coins])
        
        for idx, coin in enumerate(st.session_state.tracked_coins):
            with tabs[idx]:
                if coin in st.session_state.last_analysis:
                    analysis = st.session_state.last_analysis[coin]
                    
                    if analysis.get('mode') == 'AI_BRAIN':
                        ai_decision = analysis.get('ai_decision')
                        display_ai_decision(ai_decision)
                        
                        tech_data = ai_decision.get('metadata', {}).get('base_signal', {})
                        if tech_data and 'dataframe' in tech_
                            df = tech_data['dataframe']
                            if not df.empty:
                                st.subheader("📈 Teknik Grafik")
                                fig = create_advanced_chart(df, coin, tech_data)
                                st.plotly_chart(fig, use_container_width=True)
                    
                    else:
                        display_signal(analysis.get('signal'))
                        
                        tech_data = analysis.get('technical', {})
                        if 'dataframe' in tech_
                            df = tech_data['dataframe']
                            if not df.empty:
                                st.subheader("📈 Teknik Analiz Grafiği")
                                fig = create_advanced_chart(df, coin, tech_data)
                                st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"💡 {coin.upper()} için henüz analiz yapılmadı. 'Tümünü Analiz Et' butonuna tıklayın.")
    
    else:
        st.warning("⚠️ Takip listesinde coin yok")
    
    st.divider()
    st.caption("🔥 DEMIR AI Trading System | Powered by Advanced Machine Learning | Binance Futures API")
    
    time.sleep(1)
    st.rerun()


if __name__ == "__main__":
    main()
