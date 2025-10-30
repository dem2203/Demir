"""
DEMIR - AI-Powered Binance Futures Trading Bot
Professional-Grade Dashboard with Real-Time WebSocket
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import json

# Modül importları
try:
    import config
    import db_layer
    import external_data
    import analysis_layer
    import strategy_layer
    from websocket_client import BinanceFuturesWebSocket
except ImportError as e:
    st.error(f"Modül yükleme hatası: {e}")
    st.stop()

# Sayfa yapılandırması
st.set_page_config(
    page_title="DEMIR Trading Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Stilleri
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .signal-buy {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .signal-sell {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .signal-hold {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# SESSION STATE INITIALIZATION
# ============================================

def init_session_state():
    """Session state değişkenlerini başlat"""
    if 'ws_data' not in st.session_state:
        st.session_state.ws_data = {}
    
    if 'ws_clients' not in st.session_state:
        st.session_state.ws_clients = {}
    
    if 'last_analysis' not in st.session_state:
        st.session_state.last_analysis = {}
    
    if 'analysis_running' not in st.session_state:
        st.session_state.analysis_running = False


# ============================================
# WEBSOCKET FUNCTIONS
# ============================================

def start_websocket(symbols=['btcusdt', 'ethusdt']):
    """WebSocket bağlantısını başlat"""
    for symbol in symbols:
        if symbol not in st.session_state.ws_clients:
            try:
                ws = BinanceFuturesWebSocket(symbol)
                
                # Callback fonksiyonu
                def price_callback(data, sym=symbol):
                    st.session_state.ws_data[sym] = data
                
                ws.on_price_update = price_callback
                ws.start()
                
                st.session_state.ws_clients[symbol] = ws
                
            except Exception as e:
                st.error(f"WebSocket başlatma hatası ({symbol}): {e}")


def stop_websocket():
    """Tüm WebSocket bağlantılarını durdur"""
    for ws in st.session_state.ws_clients.values():
        try:
            ws.stop()
        except:
            pass
    st.session_state.ws_clients = {}


# ============================================
# REAL-TIME PRICE DISPLAY
# ============================================

def display_realtime_prices():
    """Canlı fiyat widget'ı"""
    st.subheader("💰 Canlı Fiyatlar (Real-Time WebSocket)")
    
    if not st.session_state.ws_data:
        st.info("WebSocket bağlantısı kuruluyor...")
        return
    
    # Coinleri sütunlara böl
    cols = st.columns(len(st.session_state.ws_data))
    
    for idx, (symbol, data) in enumerate(st.session_state.ws_data.items()):
        with cols[idx]:
            price = data.get('price', 0)
            volume = data.get('volume', 0)
            trade_count = data.get('trade_count', 0)
            
            # Coin ismi
            coin_name = symbol.replace('usdt', '').upper()
            
            # Metrik göster
            st.metric(
                label=f"🪙 {coin_name}/USDT",
                value=f"${price:,.2f}",
                delta=f"{trade_count} trades"
            )
            
            st.caption(f"Volume: {volume:.4f}")


# ============================================
# ANALYSIS FUNCTIONS
# ============================================

def run_analysis(symbol, timeframe='1h'):
    """Tam analiz çalıştır"""
    try:
        st.session_state.analysis_running = True
        
        with st.spinner(f"🔍 {symbol.upper()} analiz ediliyor..."):
            # External data
            ext_data = external_data.get_all_external_data()
            
            # Technical analysis
            tech_analysis = analysis_layer.run_full_analysis(symbol, timeframe)
            
            # Strategy signal
            signal = strategy_layer.generate_signal(
                symbol=symbol,
                tech_data=tech_analysis,
                external_data=ext_data
            )
            
            # Sonuçları kaydet
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': datetime.now(),
                'external_data': ext_data,
                'technical': tech_analysis,
                'signal': signal
            }
            
            st.session_state.last_analysis[symbol] = result
            
        st.session_state.analysis_running = False
        return result
        
    except Exception as e:
        st.error(f"Analiz hatası: {e}")
        st.session_state.analysis_running = False
        return None


def display_signal(signal_data):
    """Sinyal sonucunu görüntüle"""
    if not signal_data:
        return
    
    signal = signal_data.get('signal', 'HOLD')
    confidence = signal_data.get('confidence', 0)
    factors = signal_data.get('factors', {})
    
    # Sinyal kartı
    if signal == 'BUY':
        st.markdown(f"""
        <div class="signal-buy">
            <h3>🟢 ALIŞ SİNYALİ</h3>
            <p><strong>Güven Skoru:</strong> {confidence:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    elif signal == 'SELL':
        st.markdown(f"""
        <div class="signal-sell">
            <h3>🔴 SATIŞ SİNYALİ</h3>
            <p><strong>Güven Skoru:</strong> {confidence:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="signal-hold">
            <h3>🟡 BEKLE</h3>
            <p><strong>Güven Skoru:</strong> {confidence:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Faktör katkıları
    st.subheader("📊 Faktör Katkıları")
    
    factor_df = pd.DataFrame([
        {'Faktör': k, 'Skor': v} 
        for k, v in factors.items()
    ]).sort_values('Skor', ascending=False)
    
    fig = px.bar(
        factor_df,
        x='Skor',
        y='Faktör',
        orientation='h',
        color='Skor',
        color_continuous_scale='RdYlGn'
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ============================================
# MAIN DASHBOARD
# ============================================

def main():
    """Ana dashboard"""
    
    # Session state başlat
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 DEMIR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Binance Futures Trading Bot</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Ayarlar")
        
        # Coin seçimi
        selected_coins = st.multiselect(
            "Takip Edilecek Coinler",
            options=['btcusdt', 'ethusdt', 'bnbusdt', 'solusdt', 'adausdt'],
            default=['btcusdt', 'ethusdt']
        )
        
        # Timeframe
        timeframe = st.selectbox(
            "Zaman Dilimi",
            options=['15m', '1h', '4h', '1d'],
            index=1
        )
        
        # WebSocket kontrol
        st.subheader("🔌 WebSocket")
        
        if st.button("▶️ WebSocket Başlat", key="start_ws"):
            start_websocket(selected_coins)
            st.success("WebSocket başlatıldı!")
        
        if st.button("⏹️ WebSocket Durdur", key="stop_ws"):
            stop_websocket()
            st.success("WebSocket durduruldu!")
        
        st.divider()
        
        # Analiz butonu
        if st.button("🚀 Analiz Çalıştır", disabled=st.session_state.analysis_running):
            for coin in selected_coins:
                run_analysis(coin, timeframe)
    
    # Ana içerik
    
    # Real-time prices
    display_realtime_prices()
    
    st.divider()
    
    # Sekmeler
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Ana Dashboard",
        "🔬 Teknik Analiz",
        "🧠 AI İçgörüleri",
        "📊 Performans"
    ])
    
    with tab1:
        st.header("Ana Dashboard")
        
        # Coin seçimi
        if selected_coins:
            selected_coin = st.selectbox("Analiz edilecek coin", selected_coins)
            
            # Son analiz sonuçları
            if selected_coin in st.session_state.last_analysis:
                analysis = st.session_state.last_analysis[selected_coin]
                
                # Sinyal göster
                display_signal(analysis.get('signal'))
                
                # Metrikleri göster
                col1, col2, col3 = st.columns(3)
                
               with col1:
    fg_data = analysis.get('external_data', {}).get('fear_greed', {})
    if isinstance(fg_data, dict):
        fg_value = fg_data.get('value', 'N/A')
        fg_class = fg_data.get('classification', '')
        st.metric("Fear & Greed", f"{fg_value} - {fg_class}")
    else:
        st.metric("Fear & Greed", str(fg_data))
                
                with col2:
                    tech = analysis.get('technical', {})
                    st.metric("RSI", f"{tech.get('rsi', 0):.1f}")
                
                with col3:
                    st.metric("MACD", 
                             "Pozitif" if tech.get('macd', 0) > 0 else "Negatif")
            
            else:
                st.info("Henüz analiz yapılmadı. Sidebar'dan 'Analiz Çalıştır' butonuna basın.")
        
        else:
            st.warning("Lütfen en az bir coin seçin.")
    
    with tab2:
        st.header("Teknik Analiz Detayları")
        st.info("Bu bölüm geliştirilme aşamasında...")
    
    with tab3:
        st.header("AI İçgörüleri")
        st.info("AI katmanları geliştirilme aşamasında...")
    
    with tab4:
        st.header("Performans Metrikleri")
        st.info("Backtest ve performans analizi geliştirilme aşamasında...")
    
    # Footer
    st.divider()
    st.caption("💪 DEMIR Trading Bot - Professional AI-Powered Trading System")
    st.caption(f"Son güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Auto-refresh
    time.sleep(1)
    st.rerun()


if __name__ == "__main__":
    main()
