# ============================================================================
# DEMIR AI TRADING BOT - STREAMLIT DASHBOARD v20.0
# ============================================================================
# Perplexity-Stili Profesyonel Arayüz + Tüm Gerçek Veriler
# Date: November 10, 2025
# 
# 🔒 KURALLAR:
# - ZERO MOCK DATA - Her veri gerçek API'dan
# - Perplexity renk kodları ve tasarımı
# - Multi-page Streamlit navigasyonu
# - Responsive design
# - Smooth animations ve transitions
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import asyncio
import threading
import os
from typing import Dict, Any, Optional, Tuple
import json
import time

# ============================================================================
# CONFIG & CONSTANTS
# ============================================================================

# Perplexity Brand Colors
PERPLEXITY_COLORS = {
    'primary': '#21C4F3',      # Açık mavi
    'secondary': '#2196F3',     # Mavi
    'accent': '#00D084',        # Yeşil (success)
    'danger': '#FF4757',        # Kırmızı
    'warning': '#FFA502',       # Turuncu
    'bg_dark': '#0F1419',       # Koyu arka plan
    'bg_card': '#1a1a2e',       # Kart arka planı
    'text_primary': '#FFFFFF',  # Beyaz
    'text_secondary': '#B0B0B0',# Açık gri
}

# API Keys - Gerçek API'ler (Railway env'den alınıyor)
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
CMC_API_KEY = os.getenv('CMC_API_KEY')
COINGLASS_API_KEY = os.getenv('COINGLASS_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title='DEMIR AI - Professional Trading Dashboard',
    page_icon='🤖',
    layout='wide',
    initial_sidebar_state='expanded',
    menu_items={
        'Get Help': 'https://github.com/dem2203/Demir',
        'Report a bug': 'https://github.com/dem2203/Demir/issues',
        'About': '🔱 DEMIR AI Trading Bot v20.0 - Powered by Real APIs'
    }
)

# ============================================================================
# CSS STYLING - Perplexity Theme
# ============================================================================

def apply_perplexity_styling():
    \"\"\"Uygula Perplexity tarzı CSS styling\"\"\"
    css = f\"\"\"
    <style>
    /* GLOBAL STYLES */
    * {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    }}
    
    /* BACKGROUND */
    .main {{
        background: linear-gradient(135deg, {PERPLEXITY_COLORS['bg_dark']} 0%, #111111 100%);
        color: {PERPLEXITY_COLORS['text_primary']};
    }}
    
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(135deg, {PERPLEXITY_COLORS['bg_dark']} 0%, #111111 100%);
    }}
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0a0e27 0%, {PERPLEXITY_COLORS['bg_dark']} 100%);
        border-right: 1px solid rgba(33, 196, 243, 0.1);
    }}
    
    /* METRIC CARDS */
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
    
    /* BUTTONS */
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
    
    /* HEADER */
    h1, h2, h3 {{
        color: {PERPLEXITY_COLORS['text_primary']};
        font-weight: 700;
        letter-spacing: -0.5px;
    }}
    
    /* STATUS BADGES */
    .status-online {{
        color: {PERPLEXITY_COLORS['accent']};
        text-shadow: 0 0 10px {PERPLEXITY_COLORS['accent']};
    }}
    
    .status-offline {{
        color: {PERPLEXITY_COLORS['danger']};
        text-shadow: 0 0 10px {PERPLEXITY_COLORS['danger']};
    }}
    
    /* TABS */
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
    
    /* ANIMATION: Glow */
    @keyframes glow {{
        0%, 100% {{ text-shadow: 0 0 10px {PERPLEXITY_COLORS['primary']}, 0 0 20px {PERPLEXITY_COLORS['primary']}40%; }}
        50% {{ text-shadow: 0 0 20px {PERPLEXITY_COLORS['primary']}, 0 0 30px {PERPLEXITY_COLORS['primary']}60%; }}
    }}
    
    .glow {{
        animation: glow 3s ease-in-out infinite;
    }}
    
    /* ANIMATION: Pulse */
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}
    
    .pulse {{
        animation: pulse 2s ease-in-out infinite;
    }}
    
    /* TEXT STYLES */
    .text-muted {{
        color: {PERPLEXITY_COLORS['text_secondary']};
    }}
    
    .text-success {{
        color: {PERPLEXITY_COLORS['accent']};
        font-weight: 600;
    }}
    
    .text-danger {{
        color: {PERPLEXITY_COLORS['danger']};
        font-weight: 600;
    }}
    
    .text-warning {{
        color: {PERPLEXITY_COLORS['warning']};
        font-weight: 600;
    }}
    
    /* SCROLLBAR */
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
    \"\"\"
    st.markdown(css, unsafe_allow_html=True)

# ============================================================================
# REAL DATA FETCHERS - 100% Gerçek API
# ============================================================================

class RealDataManager:
    \"\"\"Tüm gerçek veriler Binance Futures ve diğer API'lerden\"\"\"
    
    def __init__(self):
        self.binance_url = 'https://fapi.binance.com'
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 60  # 1 minute
    
    def get_btc_price_real(self) -> Tuple[float, float, float]:
        \"\"\"
        Binance Futures'dan gerçek BTC fiyatı al
        Returns: (current_price, 24h_change_percent, 24h_volume)
        \"\"\"\n        try:
            # Binance Ticker endpoint
            url = f'{self.binance_url}/fapi/v1/ticker/24hr'\n            params = {'symbol': 'BTCUSDT'}\n            response = requests.get(url, params=params, timeout=5)\n            \n            if response.status_code == 200:\n                data = response.json()\n                current_price = float(data['lastPrice'])\n                change_percent = float(data['priceChangePercent'])\n                volume = float(data['quoteAssetVolume'])\n                \n                return current_price, change_percent, volume\n        except Exception as e:\n            st.error(f'Binance API Hatası (Binance Futures fiyat sorgusu başarısız): {e}')\n        \n        return None, None, None\n    \n    def get_market_data_real(self, symbol: str = 'BTCUSDT', limit: int = 100):\n        \"\"\"Gerçek OHLCV verisi Binance Futures'dan\"\"\" \n        try:\n            url = f'{self.binance_url}/fapi/v1/klines'\n            params = {\n                'symbol': symbol,\n                'interval': '1h',\n                'limit': limit\n            }\n            response = requests.get(url, params=params, timeout=10)\n            \n            if response.status_code == 200:\n                klines = response.json()\n                df = pd.DataFrame(klines, columns=[\n                    'open_time', 'open', 'high', 'low', 'close', 'volume',\n                    'close_time', 'quote_asset_volume', 'number_of_trades',\n                    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'\n                ])\n                \n                # Convert to numeric\n                df['close'] = pd.to_numeric(df['close'])\n                df['open'] = pd.to_numeric(df['open'])\n                df['high'] = pd.to_numeric(df['high'])\n                df['low'] = pd.to_numeric(df['low'])\n                df['volume'] = pd.to_numeric(df['volume'])\n                df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')\n                \n                return df\n        except Exception as e:\n            st.error(f'Market Data API Hatası: {e}')\n        \n        return None\n    \n    def get_funding_rates_real(self) -> Dict[str, float]:\n        \"\"\"Gerçek funding rates\"\"\" \n        try:\n            url = f'{self.binance_url}/fapi/v1/fundingRate'\n            params = {\n                'symbol': 'BTCUSDT',\n                'limit': 1\n            }\n            response = requests.get(url, params=params, timeout=5)\n            \n            if response.status_code == 200:\n                data = response.json()[0]\n                return {\n                    'funding_rate': float(data['fundingRate']) * 100,\n                    'funding_time': datetime.fromtimestamp(data['fundingTime']/1000)\n                }\n        except Exception as e:\n            st.error(f'Funding Rate API Hatası: {e}')\n        \n        return None\n\n# ============================================================================\n# MAIN APP\n# ============================================================================\n\ndef main():\n    # Apply styling\n    apply_perplexity_styling()\n    \n    # Initialize session state\n    if 'selected_symbol' not in st.session_state:\n        st.session_state.selected_symbol = 'BTCUSDT'\n    if 'data_manager' not in st.session_state:\n        st.session_state.data_manager = RealDataManager()\n    \n    data_manager = st.session_state.data_manager\n    \n    # HEADER\n    header_col1, header_col2 = st.columns([3, 1])\n    \n    with header_col1:\n        st.markdown(\n            f'<h1 style=\"text-align: center; font-size: 3em; margin: 0;\">'\n            f'<span class=\"glow\">🤖 DEMIR AI</span></h1>',\n            unsafe_allow_html=True\n        )\n        st.markdown(\n            f'<p style=\"text-align: center; color: {PERPLEXITY_COLORS[\"text_secondary\"]}; '\n            f'margin-top: -10px;\">Professional AI Trading Dashboard v20.0</p>',\n            unsafe_allow_html=True\n        )\n    \n    with header_col2:\n        # Status badge\n        status_color = 'status-online' if BINANCE_API_KEY else 'status-offline'\n        st.markdown(\n            f'<div class=\"{status_color}\" style=\"font-size: 0.9em; text-align: right; '\n            f'padding: 10px; background: rgba(33, 196, 243, 0.1); border-radius: 8px;\">'\n            f'🟢 LIVE | UTC: {datetime.utcnow().strftime(\"%H:%M:%S\")}</div>',\n            unsafe_allow_html=True\n        )\n    \n    st.divider()\n    \n    # SIDEBAR\n    with st.sidebar:\n        st.markdown(f'## ⚙️ Ayarlar')\n        \n        # Symbol selection\n        st.session_state.selected_symbol = st.selectbox(\n            'Sembol Seç (Select Symbol)',\n            ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT'],\n            index=0\n        )\n        \n        # API Status\n        st.markdown('### API Durumu (API Status)')\n        col1, col2 = st.columns(2)\n        with col1:\n            if BINANCE_API_KEY:\n                st.success('✅ Binance')\n            else:\n                st.error('❌ Binance')\n        with col2:\n            if TELEGRAM_TOKEN:\n                st.success('✅ Telegram')\n            else:\n                st.warning('⚠️ Telegram')\n        \n        st.divider()\n        \n        # Test button\n        if st.button('🧪 Test Telegram Alert'):\n            if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:\n                try:\n                    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'\n                    msg = f'🤖 DEMIR AI Test Alert\\n✅ Bot aktif ve çalışıyor!\\nTime: {datetime.now().strftime(\"%H:%M:%S %d.%m.%Y\")}'\n                    params = {'chat_id': TELEGRAM_CHAT_ID, 'text': msg}\n                    requests.post(url, params=params, timeout=5)\n                    st.success('✅ Telegram mesajı gönderildi!')\n                except Exception as e:\n                    st.error(f'Telegram hatası: {e}')\n            else:\n                st.error('Telegram anahtarları yapılandırılmamış')\n    \n    # MAIN TABS\n    tab1, tab2, tab3, tab4, tab5 = st.tabs([\n        '📊 Dashboard',\n        '🤖 AI Analysis',\n        '📈 Price Charts',\n        '💰 Portfolio',\n        '⚙️ Settings'\n    ])\n    \n    # ========================================================================\n    # TAB 1: DASHBOARD\n    # ========================================================================\n    with tab1:\n        st.markdown('## 📊 Market Overview (Piyasa Özeti)')\n        \n        # Fetch real data\n        price, change_24h, volume_24h = data_manager.get_btc_price_real()\n        \n        if price:\n            col1, col2, col3, col4 = st.columns(4)\n            \n            with col1:\n                st.markdown(f'<div class=\"metric-card\">'\n                    f'<p style=\"color: {PERPLEXITY_COLORS[\"text_secondary\"]}; margin: 0; font-size: 0.9em;\">'\n                    f'CURRENT PRICE (Mevcut Fiyat)</p>'\n                    f'<h3 style=\"margin: 10px 0; color: {PERPLEXITY_COLORS[\"primary\"]};\">${price:,.2f}</h3>'\n                    f'</div>', unsafe_allow_html=True)\n            \n            with col2:\n                change_color = PERPLEXITY_COLORS['accent'] if change_24h >= 0 else PERPLEXITY_COLORS['danger']\n                st.markdown(f'<div class=\"metric-card\">'\n                    f'<p style=\"color: {PERPLEXITY_COLORS[\"text_secondary\"]}; margin: 0; font-size: 0.9em;\">'\n                    f'24H CHANGE (24S Değişim)</p>'\n                    f'<h3 style=\"margin: 10px 0; color: {change_color};\">{change_24h:+.2f}%</h3>'\n                    f'</div>', unsafe_allow_html=True)\n            \n            with col3:\n                st.markdown(f'<div class=\"metric-card\">'\n                    f'<p style=\"color: {PERPLEXITY_COLORS[\"text_secondary\"]}; margin: 0; font-size: 0.9em;\">'\n                    f'24H VOLUME (24S Hacim)</p>'\n                    f'<h3 style=\"margin: 10px 0; color: {PERPLEXITY_COLORS[\"primary\"]};\">${volume_24h/1e9:,.1f}B</h3>'\n                    f'</div>', unsafe_allow_html=True)\n            \n            with col4:\n                # Funding rate\n                funding = data_manager.get_funding_rates_real()\n                if funding:\n                    funding_color = PERPLEXITY_COLORS['accent'] if funding['funding_rate'] >= 0 else PERPLEXITY_COLORS['danger']\n                    st.markdown(f'<div class=\"metric-card\">'\n                        f'<p style=\"color: {PERPLEXITY_COLORS[\"text_secondary\"]}; margin: 0; font-size: 0.9em;\">'\n                        f'FUNDING RATE (Finansman Oranı)</p>'\n                        f'<h3 style=\"margin: 10px 0; color: {funding_color};\">{funding[\"funding_rate\"]:+.3f}%</h3>'\n                        f'</div>', unsafe_allow_html=True)\n        else:\n            st.error('Gerçek veriler alınamadı. API anahtarlarını kontrol edin.')\n    \n    # ========================================================================\n    # TAB 2: AI ANALYSIS\n    # ========================================================================\n    with tab2:\n        st.markdown('## 🤖 AI Trading Signals (AI Ticaret Sinyalleri)')\n        \n        # Fetch market data\n        df = data_manager.get_market_data_real(st.session_state.selected_symbol, limit=100)\n        \n        if df is not None and len(df) > 0:\n            # Simple momentum indicator\n            closes = df['close'].values\n            sma20 = np.mean(closes[-20:])\n            sma50 = np.mean(closes[-50:])\n            momentum = (closes[-1] - closes[-5]) / closes[-5] * 100\n            \n            # Determine signal\n            if closes[-1] > sma20 > sma50:\n                signal = 'LONG'\n                signal_color = PERPLEXITY_COLORS['accent']\n                confidence = min(90, abs(momentum) * 2)\n            elif closes[-1] < sma20 < sma50:\n                signal = 'SHORT'\n                signal_color = PERPLEXITY_COLORS['danger']\n                confidence = min(90, abs(momentum) * 2)\n            else:\n                signal = 'NEUTRAL'\n                signal_color = PERPLEXITY_COLORS['warning']\n                confidence = 50\n            \n            # Display signal\n            col1, col2 = st.columns(2)\n            \n            with col1:\n                st.markdown(f'<div class=\"metric-card\" style=\"border-left: 4px solid {signal_color};\">'\n                    f'<p style=\"color: {PERPLEXITY_COLORS[\"text_secondary\"]}; margin: 0; font-size: 0.9em;\">'\n                    f'AI SIGNAL (AI Sinyali)</p>'\n                    f'<h2 style=\"margin: 15px 0; color: {signal_color};\">{signal}</h2>'\n                    f'</div>', unsafe_allow_html=True)\n            \n            with col2:\n                st.markdown(f'<div class=\"metric-card\">'\n                    f'<p style=\"color: {PERPLEXITY_COLORS[\"text_secondary\"]}; margin: 0; font-size: 0.9em;\">'\n                    f'CONFIDENCE (Güven)</p>'\n                    f'<h3 style=\"margin: 10px 0; color: {PERPLEXITY_COLORS[\"primary\"]};\">{confidence:.1f}%</h3>'\n                    f'</div>', unsafe_allow_html=True)\n            \n            st.divider()\n            \n            # Metrics\n            col1, col2, col3, col4 = st.columns(4)\n            with col1:\n                st.metric('Current Price', f'${closes[-1]:,.2f}')\n            with col2:\n                st.metric('SMA 20', f'${sma20:,.2f}')\n            with col3:\n                st.metric('SMA 50', f'${sma50:,.2f}')\n            with col4:\n                st.metric('Momentum', f'{momentum:+.2f}%')\n        else:\n            st.error('Market data alınamadı')\n    \n    # ========================================================================\n    # TAB 3: PRICE CHARTS\n    # ========================================================================\n    with tab3:\n        st.markdown('## 📈 Price Charts (Fiyat Grafikleri)')\n        \n        df = data_manager.get_market_data_real(st.session_state.selected_symbol, limit=100)\n        \n        if df is not None and len(df) > 0:\n            # Candlestick chart\n            fig = go.Figure(data=[go.Candlestick(\n                x=df['open_time'],\n                open=df['open'],\n                high=df['high'],\n                low=df['low'],\n                close=df['close'],\n                increasing_line_color=PERPLEXITY_COLORS['accent'],\n                decreasing_line_color=PERPLEXITY_COLORS['danger']\n            )])\n            \n            fig.update_layout(\n                title=f'{st.session_state.selected_symbol} - 1H Chart',\n                yaxis_title='Price (USD)',\n                xaxis_title='Time',\n                template='plotly_dark',\n                hovermode='x unified',\n                plot_bgcolor=PERPLEXITY_COLORS['bg_card'],\n                paper_bgcolor=PERPLEXITY_COLORS['bg_dark'],\n                font=dict(color=PERPLEXITY_COLORS['text_primary'])\n            )\n            \n            st.plotly_chart(fig, use_container_width=True)\n    \n    # ========================================================================\n    # TAB 4: PORTFOLIO\n    # ========================================================================\n    with tab4:\n        st.markdown('## 💰 Portfolio Management (Portföy Yönetimi)')\n        st.info('Portfolio yönetimi ve backtesting özellikleri yakında eklenecek.')\n    \n    # ========================================================================\n    # TAB 5: SETTINGS\n    # ========================================================================\n    with tab5:\n        st.markdown('## ⚙️ Dashboard Settings (Ayarlar)')\n        \n        st.markdown('### API Configuration (API Yapılandırması)')\n        col1, col2 = st.columns(2)\n        with col1:\n            if BINANCE_API_KEY:\n                st.success(f'✅ Binance API: {BINANCE_API_KEY[:10]}...')\n            else:\n                st.warning('⚠️ Binance API key bulunamadı')\n        with col2:\n            if TELEGRAM_TOKEN:\n                st.success(f'✅ Telegram: Configured')\n            else:\n                st.warning('⚠️ Telegram not configured')\n        \n        st.divider()\n        \n        st.markdown('### System Information (Sistem Bilgileri)')\n        st.write(f'Dashboard Version: v20.0')\n        st.write(f'Theme: Perplexity Professional')\n        st.write(f'Real Data Mode: ✅ ENABLED')\n        st.write(f'Last Update: {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S UTC\")}')\n\nif __name__ == '__main__':\n    main()
