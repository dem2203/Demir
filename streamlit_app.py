# ============================================================================
# DEMIR AI TRADING BOT - STREAMLIT DASHBOARD v20.1 FIXED
# ============================================================================
# FIX: Binance API hatası + Error handling + Perplexity UI complete
# Date: November 10, 2025
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import logging
import os
import json
import sqlite3
from enum import Enum
from typing import Dict, Any, Optional, Tuple, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PAGE CONFIG FIRST
# ============================================================================

st.set_page_config(
    page_title='DEMIR AI - Professional Trading Dashboard',
    page_icon='🤖',
    layout='wide',
    initial_sidebar_state='expanded'
)

# ============================================================================
# PERPLEXITY COLORS
# ============================================================================

PERPLEXITY_COLORS = {
    'primary': '#21C4F3',
    'secondary': '#2196F3',
    'accent': '#00D084',
    'danger': '#FF4757',
    'warning': '#FFA502',
    'bg_dark': '#0F1419',
    'bg_card': '#1a1a2e',
    'text_primary': '#FFFFFF',
    'text_secondary': '#B0B0B0',
}

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# ============================================================================
# CSS STYLING
# ============================================================================

def apply_perplexity_styling():
    """Perplexity tarzı CSS"""
    css = f"""
    <style>
    * {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}
    
    /* Background */
    .main {{
        background: linear-gradient(135deg, {PERPLEXITY_COLORS['bg_dark']} 0%, #111111 100%);
        color: {PERPLEXITY_COLORS['text_primary']};
    }}
    
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(135deg, {PERPLEXITY_COLORS['bg_dark']} 0%, #111111 100%);
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0a0e27 0%, {PERPLEXITY_COLORS['bg_dark']} 100%);
        border-right: 1px solid rgba(33, 196, 243, 0.1);
    }}
    
    /* Metric Cards */
    .metric-card {{
        background: linear-gradient(135deg, {PERPLEXITY_COLORS['bg_card']} 0%, rgba(33, 196, 243, 0.05) 100%);
        border: 1px solid rgba(33, 196, 243, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(33, 196, 243, 0.1);
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        border-color: {PERPLEXITY_COLORS['primary']};
        box-shadow: 0 12px 48px rgba(33, 196, 243, 0.2);
        transform: translateY(-2px);
    }}
    
    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {PERPLEXITY_COLORS['primary']} 0%, {PERPLEXITY_COLORS['secondary']} 100%);
        color: {PERPLEXITY_COLORS['text_primary']};
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(33, 196, 243, 0.3);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(33, 196, 243, 0.5);
    }}
    
    /* Headers */
    h1, h2, h3 {{
        color: {PERPLEXITY_COLORS['text_primary']};
        font-weight: 700;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button {{
        background: transparent;
        border-bottom: 2px solid transparent;
        color: {PERPLEXITY_COLORS['text_secondary']};
        transition: all 0.3s ease;
    }}
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        border-bottom-color: {PERPLEXITY_COLORS['primary']};
        color: {PERPLEXITY_COLORS['primary']};
    }}
    
    /* Animations */
    @keyframes glow {{
        0%, 100% {{ text-shadow: 0 0 10px {PERPLEXITY_COLORS['primary']}; }}
        50% {{ text-shadow: 0 0 20px {PERPLEXITY_COLORS['primary']}; }}
    }}
    
    .glow {{ animation: glow 3s ease-in-out infinite; }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}
    
    .pulse {{ animation: pulse 2s ease-in-out infinite; }}
    
    /* Text */
    .text-success {{ color: {PERPLEXITY_COLORS['accent']}; font-weight: 600; }}
    .text-danger {{ color: {PERPLEXITY_COLORS['danger']}; font-weight: 600; }}
    .text-warning {{ color: {PERPLEXITY_COLORS['warning']}; font-weight: 600; }}
    .text-muted {{ color: {PERPLEXITY_COLORS['text_secondary']}; }}
    
    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: transparent;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: rgba(33, 196, 243, 0.3);
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: rgba(33, 196, 243, 0.5);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Apply styling IMMEDIATELY
apply_perplexity_styling()

# ============================================================================
# REAL DATA MANAGER - FIXED API CALLS
# ============================================================================

class RealDataManager:
    """Binance API'dan gerçek veriler al - FIXED"""
    
    def __init__(self):
        self.binance_url = 'https://fapi.binance.com'
        self.cache = {}
        self.cache_time = {}
    
    def get_btc_price_real(self) -> Tuple[float, float, float]:
        """
        Binance Futures'dan gerçek BTC fiyatı al
        Returns: (price, change_24h, volume_24h)
        """
        try:
            url = f'{self.binance_url}/fapi/v1/ticker/24hr'
            params = {'symbol': 'BTCUSDT'}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                price = float(data.get('lastPrice', 0))
                change = float(data.get('priceChangePercent', 0))
                # FIX: quoteAssetVolume yerine volume kullan
                volume = float(data.get('volume', 0))
                
                logger.info(f"✅ BTC: ${price:,.2f} | Change: {change:+.2f}%")
                return price, change, volume
            else:
                logger.error(f"API error: {response.status_code}")
                return None, None, None
                
        except Exception as e:
            logger.error(f"❌ Binance API error: {e}")
            return None, None, None
    
    def get_market_data_real(self, symbol: str = 'BTCUSDT', limit: int = 100):
        """Gerçek OHLCV verisi al"""
        try:
            url = f'{self.binance_url}/fapi/v1/klines'
            params = {
                'symbol': symbol,
                'interval': '1h',
                'limit': limit
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                klines = response.json()
                df = pd.DataFrame(klines, columns=[
                    'open_time', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_asset_volume', 'number_of_trades',
                    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                ])
                
                for col in ['close', 'open', 'high', 'low', 'volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
                logger.info(f"✅ {symbol} data: {len(df)} candles loaded")
                return df
            else:
                logger.error(f"Klines error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Market data error: {e}")
            return None
    
    def get_funding_rates_real(self) -> Optional[Dict[str, Any]]:
        """Gerçek funding rates al"""
        try:
            url = f'{self.binance_url}/fapi/v1/fundingRate'
            params = {'symbol': 'BTCUSDT', 'limit': 1}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()[0]
                return {
                    'funding_rate': float(data['fundingRate']) * 100,
                    'funding_time': datetime.fromtimestamp(data['fundingTime']/1000)
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Funding rate error: {e}")
            return None

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Initialize session state
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = RealDataManager()
    
    data_manager = st.session_state.data_manager
    
    # ====================================================================
    # HEADER
    # ====================================================================
    
    header_col1, header_col2 = st.columns([3, 1])
    
    with header_col1:
        st.markdown(
            f'<h1 style="text-align: center; font-size: 3em; margin: 0; color: {PERPLEXITY_COLORS["primary"]}">'
            f'<span class="glow">🤖 DEMIR AI</span></h1>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<p style="text-align: center; color: {PERPLEXITY_COLORS["text_secondary"]}; margin-top: -10px;">'
            f'Professional AI Trading Dashboard v20.1</p>',
            unsafe_allow_html=True
        )
    
    with header_col2:
        st.markdown(
            f'<div style="font-size: 0.9em; text-align: right; padding: 10px; '
            f'background: rgba(33, 196, 243, 0.1); border-radius: 8px; color: {PERPLEXITY_COLORS["accent"]}">'
            f'🟢 LIVE | UTC: {datetime.utcnow().strftime("%H:%M:%S")}</div>',
            unsafe_allow_html=True
        )
    
    st.divider()
    
    # ====================================================================
    # SIDEBAR
    # ====================================================================
    
    with st.sidebar:
        st.markdown("## ⚙️ Ayarlar")
        
        selected_symbol = st.selectbox(
            'Sembol Seç',
            ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT'],
            index=0
        )
        
        st.markdown("### API Durumu")
        col1, col2 = st.columns(2)
        
        with col1:
            if BINANCE_API_KEY:
                st.success('✅ Binance')
            else:
                st.warning('⚠️ Binance')
        
        with col2:
            if TELEGRAM_TOKEN:
                st.success('✅ Telegram')
            else:
                st.warning('⚠️ Telegram')
        
        st.divider()
        
        if st.button('🧪 Test Telegram', use_container_width=True):
            if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                try:
                    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
                    msg = f'✅ DEMIR AI Test - Sistema Çalışıyor!\nTime: {datetime.now().strftime("%H:%M:%S")}'
                    params = {'chat_id': TELEGRAM_CHAT_ID, 'text': msg}
                    resp = requests.post(url, params=params, timeout=5)
                    
                    if resp.status_code == 200:
                        st.success('✅ Telegram mesajı gönderildi!')
                    else:
                        st.error('❌ Telegram gönderme hatası')
                except Exception as e:
                    st.error(f'Telegram error: {e}')
            else:
                st.error('Telegram anahtarları yapılandırılmamış')
    
    # ====================================================================
    # MAIN TABS
    # ====================================================================
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        '📊 Dashboard',
        '🤖 AI Analysis',
        '📈 Charts',
        '💰 Portfolio',
        '⚙️ Settings'
    ])
    
    # ====================================================================
    # TAB 1: DASHBOARD
    # ====================================================================
    
    with tab1:
        st.markdown('## 📊 Piyasa Özeti (Market Overview)')
        
        # Fetch real data with error handling
        price, change_24h, volume_24h = data_manager.get_btc_price_real()
        
        if price and change_24h is not None:
            col1, col2, col3, col4 = st.columns(4)
            
            # Card 1: Current Price
            with col1:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<p style="color: {PERPLEXITY_COLORS["text_secondary"]}; margin: 0; font-size: 0.9em;">Mevcut Fiyat</p>'
                    f'<h3 style="margin: 10px 0; color: {PERPLEXITY_COLORS["primary"]};">${price:,.2f}</h3>'
                    f'<p style="color: {PERPLEXITY_COLORS["text_secondary"]}; margin: 0; font-size: 0.8em;">BTCUSDT</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            # Card 2: 24h Change
            with col2:
                change_color = PERPLEXITY_COLORS['accent'] if change_24h >= 0 else PERPLEXITY_COLORS['danger']
                st.markdown(
                    f'<div class="metric-card">'
                    f'<p style="color: {PERPLEXITY_COLORS["text_secondary"]}; margin: 0; font-size: 0.9em;">24S Değişim</p>'
                    f'<h3 style="margin: 10px 0; color: {change_color};">{change_24h:+.2f}%</h3>'
                    f'<p style="color: {PERPLEXITY_COLORS["text_secondary"]}; margin: 0; font-size: 0.8em;">Last 24h</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            # Card 3: 24h Volume
            with col3:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<p style="color: {PERPLEXITY_COLORS["text_secondary"]}; margin: 0; font-size: 0.9em;">24S Hacim</p>'
                    f'<h3 style="margin: 10px 0; color: {PERPLEXITY_COLORS["primary"]};">{volume_24h/1e9:,.1f}B</h3>'
                    f'<p style="color: {PERPLEXITY_COLORS["text_secondary"]}; margin: 0; font-size: 0.8em;">USDT</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            # Card 4: Funding Rate
            with col4:
                funding = data_manager.get_funding_rates_real()
                if funding:
                    funding_color = PERPLEXITY_COLORS['accent'] if funding['funding_rate'] >= 0 else PERPLEXITY_COLORS['danger']
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<p style="color: {PERPLEXITY_COLORS["text_secondary"]}; margin: 0; font-size: 0.9em;">Funding Rate</p>'
                        f'<h3 style="margin: 10px 0; color: {funding_color};">{funding["funding_rate"]:+.3f}%</h3>'
                        f'<p style="color: {PERPLEXITY_COLORS["text_secondary"]}; margin: 0; font-size: 0.8em;">Perpetual</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<p style="color: {PERPLEXITY_COLORS["text_secondary"]};">Funding Rate</p>'
                        f'<p style="color: {PERPLEXITY_COLORS["danger"]};">Data unavailable</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            
            st.divider()
            st.success('✅ Real-time data loaded from Binance Futures')
        
        else:
            st.error('❌ Gerçek veriler alınamadı - Binance API kontrol et')
            st.info('💡 Binance API key'ini Railway environment variables'a ekle')
    
    # ====================================================================
    # TAB 2: AI ANALYSIS
    # ====================================================================
    
    with tab2:
        st.markdown('## 🤖 AI Trading Signals')
        
        df = data_manager.get_market_data_real(selected_symbol, limit=100)
        
        if df is not None and len(df) > 0:
            # Simple momentum analysis
            closes = df['close'].values
            sma20 = np.mean(closes[-20:]) if len(closes) >= 20 else np.mean(closes)
            sma50 = np.mean(closes[-50:]) if len(closes) >= 50 else np.mean(closes)
            momentum = (closes[-1] - closes[-5]) / closes[-5] * 100 if len(closes) >= 5 else 0
            
            # Signal
            if closes[-1] > sma20 > sma50:
                signal = 'LONG'
                signal_color = PERPLEXITY_COLORS['accent']
                confidence = min(90, abs(momentum) * 2)
            elif closes[-1] < sma20 < sma50:
                signal = 'SHORT'
                signal_color = PERPLEXITY_COLORS['danger']
                confidence = min(90, abs(momentum) * 2)
            else:
                signal = 'NEUTRAL'
                signal_color = PERPLEXITY_COLORS['warning']
                confidence = 50
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(
                    f'<div class="metric-card" style="border-left: 4px solid {signal_color};">'
                    f'<p style="color: {PERPLEXITY_COLORS["text_secondary"]}; margin: 0;">AI Sinyali</p>'
                    f'<h2 style="margin: 15px 0; color: {signal_color};">{signal}</h2>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            with col2:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<p style="color: {PERPLEXITY_COLORS["text_secondary"]}; margin: 0;">Güven Skoru</p>'
                    f'<h3 style="margin: 10px 0; color: {PERPLEXITY_COLORS["primary"]};">{confidence:.1f}%</h3>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            st.divider()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric('Current Price', f'${closes[-1]:,.2f}')
            with col2:
                st.metric('SMA 20', f'${sma20:,.2f}')
            with col3:
                st.metric('SMA 50', f'${sma50:,.2f}')
            with col4:
                st.metric('Momentum', f'{momentum:+.2f}%')
        
        else:
            st.error('❌ Market verisi alınamadı')
    
    # ====================================================================
    # TAB 3: CHARTS
    # ====================================================================
    
    with tab3:
        st.markdown('## 📈 Fiyat Grafikleri')
        
        df = data_manager.get_market_data_real(selected_symbol, limit=100)
        
        if df is not None and len(df) > 0:
            fig = go.Figure(data=[go.Candlestick(
                x=df['open_time'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                increasing_line_color=PERPLEXITY_COLORS['accent'],
                decreasing_line_color=PERPLEXITY_COLORS['danger']
            )])
            
            fig.update_layout(
                title=f'{selected_symbol} - 1H Chart',
                yaxis_title='Price (USD)',
                xaxis_title='Time',
                template='plotly_dark',
                hovermode='x unified',
                plot_bgcolor=PERPLEXITY_COLORS['bg_card'],
                paper_bgcolor=PERPLEXITY_COLORS['bg_dark'],
                font=dict(color=PERPLEXITY_COLORS['text_primary'])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.error('❌ Chart data not available')
    
    # ====================================================================
    # TAB 4: PORTFOLIO
    # ====================================================================
    
    with tab4:
        st.markdown('## 💰 Portföy Yönetimi')
        st.info('Portfolio yönetimi yakında eklenecek...')
    
    # ====================================================================
    # TAB 5: SETTINGS
    # ====================================================================
    
    with tab5:
        st.markdown('## ⚙️ Sistem Ayarları')
        
        st.markdown("### API Yapılandırması")
        col1, col2 = st.columns(2)
        
        with col1:
            if BINANCE_API_KEY:
                st.success(f'✅ Binance API: {BINANCE_API_KEY[:10]}...')
            else:
                st.warning('⚠️ Binance API key bulunamadı')
        
        with col2:
            if TELEGRAM_TOKEN:
                st.success('✅ Telegram: Configured')
            else:
                st.warning('⚠️ Telegram not configured')
        
        st.divider()
        
        st.markdown("### Sistem Bilgileri")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric('Version', 'v20.1 Fixed')
        with col2:
            st.metric('Theme', 'Perplexity Pro')
        with col3:
            st.metric('Data', 'Real-time')

if __name__ == '__main__':
    main()
