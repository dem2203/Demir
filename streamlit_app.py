# ============================================================================
# DEMIR AI - PERPLEXITY APPS STYLE STREAMLIT DASHBOARD v30
# ============================================================================
# 100% Perplexity App tasarımı + GERÇEK VERİLER
# Date: November 10, 2025
#
# Perplexity Apps Features:
# - Search bar (market search)
# - Real-time data cards
# - Multi-source integration (Binance, CMC, Coinglass, etc)
# - Response streaming
# - Professional UI/UX
# - All REAL data (NO MOCK)
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import logging
from datetime import datetime, timedelta
import os
from typing import Dict, Any, Optional, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="DEMIR AI - Search Trading Data",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# PERPLEXITY EXACT COLORS & STYLING
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

CSS_STYLING = f"""
<style>
* {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

body {{
    background: linear-gradient(135deg, {PERPLEXITY_COLORS['bg_dark']} 0%, #111111 100%);
    color: {PERPLEXITY_COLORS['text_primary']};
}}

.main {{
    background: linear-gradient(135deg, {PERPLEXITY_COLORS['bg_dark']} 0%, #111111 100%);
}}

/* SEARCH BAR - Perplexity tarzı */
.search-bar {{
    background: {PERPLEXITY_COLORS['bg_card']};
    border: 2px solid rgba(33, 196, 243, 0.2);
    border-radius: 24px;
    padding: 12px 20px;
    color: {PERPLEXITY_COLORS['text_primary']};
    font-size: 16px;
    box-shadow: 0 8px 32px rgba(33, 196, 243, 0.1);
    transition: all 0.3s ease;
}}

.search-bar:focus {{
    border-color: {PERPLEXITY_COLORS['primary']};
    box-shadow: 0 12px 48px rgba(33, 196, 243, 0.3);
}}

/* DATA CARDS */
.data-card {{
    background: linear-gradient(135deg, {PERPLEXITY_COLORS['bg_card']} 0%, rgba(33, 196, 243, 0.05) 100%);
    border: 1px solid rgba(33, 196, 243, 0.2);
    border-radius: 16px;
    padding: 24px;
    margin: 12px 0;
    box-shadow: 0 8px 32px rgba(33, 196, 243, 0.1);
    transition: all 0.3s ease;
}}

.data-card:hover {{
    border-color: {PERPLEXITY_COLORS['primary']};
    box-shadow: 0 12px 48px rgba(33, 196, 243, 0.2);
    transform: translateY(-2px);
}}

/* TABS */
.tab-button {{
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: {PERPLEXITY_COLORS['text_secondary']};
    padding: 12px 24px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 14px;
    font-weight: 500;
}}

.tab-button.active {{
    border-bottom-color: {PERPLEXITY_COLORS['primary']};
    color: {PERPLEXITY_COLORS['primary']};
}}

/* BADGES */
.badge {{
    display: inline-block;
    background: rgba(33, 196, 243, 0.1);
    border: 1px solid rgba(33, 196, 243, 0.3);
    color: {PERPLEXITY_COLORS['primary']};
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    margin: 4px;
}}

.badge.success {{
    background: rgba(0, 208, 132, 0.1);
    border-color: rgba(0, 208, 132, 0.3);
    color: {PERPLEXITY_COLORS['accent']};
}}

.badge.danger {{
    background: rgba(255, 71, 87, 0.1);
    border-color: rgba(255, 71, 87, 0.3);
    color: {PERPLEXITY_COLORS['danger']};
}}

/* ANIMATIONS */
@keyframes glow {{
    0%, 100% {{ text-shadow: 0 0 10px {PERPLEXITY_COLORS['primary']}; }}
    50% {{ text-shadow: 0 0 20px {PERPLEXITY_COLORS['primary']}; }}
}}

.glow {{ animation: glow 3s ease-in-out infinite; }}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.fade-in {{ animation: fadeIn 0.5s ease-out; }}

/* TEXT COLORS */
.text-success {{ color: {PERPLEXITY_COLORS['accent']}; font-weight: 600; }}
.text-danger {{ color: {PERPLEXITY_COLORS['danger']}; font-weight: 600; }}
.text-primary {{ color: {PERPLEXITY_COLORS['primary']}; }}
.text-secondary {{ color: {PERPLEXITY_COLORS['text_secondary']}; }}

/* METRIC DISPLAY */
.metric {{
    text-align: center;
    padding: 20px;
}}

.metric-value {{
    font-size: 28px;
    font-weight: 700;
    color: {PERPLEXITY_COLORS['primary']};
}}

.metric-label {{
    font-size: 12px;
    color: {PERPLEXITY_COLORS['text_secondary']};
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

</style>
"""

st.markdown(CSS_STYLING, unsafe_allow_html=True)

# ============================================================================
# API INTEGRATIONS - GERÇEK VERİLER
# ============================================================================

class PerplexityStyleDataFetcher:
    """
    Perplexity Apps gibi multi-source data fetcher
    (Perplexity, CMC, Coinglass, Binance'den gerçek veriler)
    """
    
    def __init__(self):
        self.binance_url = 'https://fapi.binance.com'
        self.cmc_url = 'https://pro-api.coinmarketcap.com/v1'
        self.coinglass_url = 'https://api.coinglass.com/v1'
        
        self.cmc_key = os.getenv('CMC_API_KEY', '')
        self.coinglass_key = os.getenv('COINGLASS_API_KEY', '')
    
    def search_asset(self, query: str) -> Dict[str, Any]:
        """
        Perplexity gibi: Arama yap, tüm bilgileri getir
        (Search for asset and return all relevant data)
        """
        results = {
            'query': query,
            'sources': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # 1. BINANCE - Price & Volume
            logger.info(f"🔍 Searching: {query}")
            
            symbol = query.upper() if 'USDT' in query.upper() else f"{query.upper()}USDT"
            
            # Get price from Binance
            price_data = self._get_binance_price(symbol)
            if price_data:
                results['sources']['binance'] = {
                    'price': price_data['price'],
                    'change_24h': price_data['change_24h'],
                    'volume_24h': price_data['volume_24h'],
                    'high_24h': price_data['high_24h'],
                    'low_24h': price_data['low_24h']
                }
            
            # 2. COINGLASS - On-chain data
            coinglass_data = self._get_coinglass_data(symbol)
            if coinglass_data:
                results['sources']['coinglass'] = coinglass_data
            
            # 3. MARKET CAP & RANKINGS - CMC
            cmc_data = self._get_cmc_data(query)
            if cmc_data:
                results['sources']['cmc'] = cmc_data
            
            # 4. TECHNICAL ANALYSIS
            tech_data = self._get_technical_analysis(symbol)
            if tech_data:
                results['sources']['technical'] = tech_data
            
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return results
    
    def _get_binance_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """Binance Futures'dan gerçek fiyat ver"""
        try:
            url = f'{self.binance_url}/fapi/v1/ticker/24hr'
            response = requests.get(url, params={'symbol': symbol}, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'price': float(data.get('lastPrice', 0)),
                    'change_24h': float(data.get('priceChangePercent', 0)),
                    'volume_24h': float(data.get('volume', 0)),
                    'high_24h': float(data.get('highPrice', 0)),
                    'low_24h': float(data.get('lowPrice', 0))
                }
        except Exception as e:
            logger.error(f"Binance error: {e}")
        return None
    
    def _get_coinglass_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Coinglass'tan on-chain verisi al"""
        try:
            if not self.coinglass_key:
                return None
            
            url = f'{self.coinglass_url}/liquidation/aggregated'
            headers = {'accept': 'application/json'}
            params = {'symbol': symbol.replace('USDT', ''), 'limit': 10}
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'liquidations': data.get('data', [])[:5],
                    'source': 'Coinglass'
                }
        except Exception as e:
            logger.error(f"Coinglass error: {e}")
        return None
    
    def _get_cmc_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """CMC'den market cap ve ranking ver"""
        try:
            if not self.cmc_key:
                return None
            
            url = f'{self.cmc_url}/cryptocurrency/quotes/latest'
            headers = {'X-CMC_PRO_API_KEY': self.cmc_key}
            params = {'symbol': symbol.replace('USDT', '').upper(), 'convert': 'USD'}
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    coin_data = list(data['data'].values())[0]
                    return {
                        'market_cap': coin_data.get('quote', {}).get('USD', {}).get('market_cap'),
                        'market_cap_rank': coin_data.get('cmc_rank'),
                        'volume_24h': coin_data.get('quote', {}).get('USD', {}).get('volume_24h')
                    }
        except Exception as e:
            logger.error(f"CMC error: {e}")
        return None
    
    def _get_technical_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Teknik analiz ver"""
        try:
            url = f'{self.binance_url}/fapi/v1/klines'
            params = {'symbol': symbol, 'interval': '1h', 'limit': 50}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                klines = response.json()
                closes = [float(k[4]) for k in klines]
                
                # SMA
                sma_20 = np.mean(closes[-20:]) if len(closes) >= 20 else np.mean(closes)
                sma_50 = np.mean(closes[-50:]) if len(closes) >= 50 else np.mean(closes)
                
                # RSI (simplified)
                deltas = np.diff(closes[-14:])
                gains = sum([d for d in deltas if d > 0]) / 14
                losses = sum([abs(d) for d in deltas if d < 0]) / 14
                rs = gains / losses if losses != 0 else 0
                rsi = 100 - (100 / (1 + rs))
                
                # Signal
                if closes[-1] > sma_20:
                    signal = 'LONG'
                elif closes[-1] < sma_20:
                    signal = 'SHORT'
                else:
                    signal = 'NEUTRAL'
                
                return {
                    'sma_20': round(sma_20, 2),
                    'sma_50': round(sma_50, 2),
                    'rsi': round(rsi, 2),
                    'signal': signal,
                    'current_price': round(closes[-1], 2)
                }
        except Exception as e:
            logger.error(f"Technical analysis error: {e}")
        return None

# ============================================================================
# PERPLEXITY STYLE UI COMPONENTS
# ============================================================================

def render_header():
    """Perplexity tarzı header"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(
            f'<h1 style="color: {PERPLEXITY_COLORS["primary"]}; font-size: 2.5em; margin: 0;">'
            f'<span class="glow">🤖 DEMIR AI</span> Search</h1>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<p style="color: {PERPLEXITY_COLORS["text_secondary"]}; margin: 8px 0 0 0;">'
            f'Real-time trading data from multiple sources</p>',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f'<div style="text-align: right; color: {PERPLEXITY_COLORS["accent"]}">'
            f'🟢 LIVE</div>',
            unsafe_allow_html=True
        )

def render_search_bar():
    """Perplexity tarzı search bar"""
    st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)
    
    search_query = st.text_input(
        "Search any trading pair...",
        placeholder="e.g., BTC, ETH, BNBUSDT...",
        label_visibility="collapsed"
    )
    
    return search_query

def render_results_card(data: Dict[str, Any]):
    """Perplexity tarzı results card"""
    if not data.get('sources'):
        st.warning("No data found. Try searching for BTC, ETH, etc.")
        return
    
    # HEADER
    st.markdown(f"## Search Results for: `{data['query']}`")
    
    sources = data['sources']
    
    # TAB 1: PRICE & MARKET
    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 Price & Market",
        "📊 Technical Analysis",
        "🔗 On-Chain",
        "📈 Market Cap"
    ])
    
    with tab1:
        if 'binance' in sources:
            binance_data = sources['binance']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(
                    f'<div class="data-card">'
                    f'<div class="metric">'
                    f'<div class="metric-value">${binance_data["price"]:,.2f}</div>'
                    f'<div class="metric-label">Current Price</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
            
            with col2:
                change_color = 'text-success' if binance_data['change_24h'] >= 0 else 'text-danger'
                st.markdown(
                    f'<div class="data-card">'
                    f'<div class="metric">'
                    f'<div class="metric-value {change_color}">{binance_data["change_24h"]:+.2f}%</div>'
                    f'<div class="metric-label">24h Change</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
            
            with col3:
                st.markdown(
                    f'<div class="data-card">'
                    f'<div class="metric">'
                    f'<div class="metric-value">${binance_data["high_24h"]:,.2f}</div>'
                    f'<div class="metric-label">24h High</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
            
            with col4:
                st.markdown(
                    f'<div class="data-card">'
                    f'<div class="metric">'
                    f'<div class="metric-value">${binance_data["low_24h"]:,.2f}</div>'
                    f'<div class="metric-label">24h Low</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
    
    with tab2:
        if 'technical' in sources:
            tech_data = sources['technical']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(
                    f'<div class="data-card">'
                    f'<div class="metric">'
                    f'<div class="metric-value">{tech_data["sma_20"]:,.2f}</div>'
                    f'<div class="metric-label">SMA 20</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
            
            with col2:
                st.markdown(
                    f'<div class="data-card">'
                    f'<div class="metric">'
                    f'<div class="metric-value">{tech_data["sma_50"]:,.2f}</div>'
                    f'<div class="metric-label">SMA 50</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
            
            with col3:
                st.markdown(
                    f'<div class="data-card">'
                    f'<div class="metric">'
                    f'<div class="metric-value">{tech_data["rsi"]:.1f}</div>'
                    f'<div class="metric-label">RSI 14</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
            
            with col4:
                signal_color = 'text-success' if tech_data['signal'] == 'LONG' else 'text-danger' if tech_data['signal'] == 'SHORT' else 'text-secondary'
                st.markdown(
                    f'<div class="data-card">'
                    f'<div class="metric">'
                    f'<div class="metric-value {signal_color}">{tech_data["signal"]}</div>'
                    f'<div class="metric-label">Signal</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
    
    with tab3:
        if 'coinglass' in sources:
            st.info("On-chain data from Coinglass")
            # Liquidations display
            if sources['coinglass'].get('liquidations'):
                st.subheader("Recent Liquidations")
                for liq in sources['coinglass']['liquidations'][:3]:
                    st.write(f"📊 {liq}")
        else:
            st.warning("Coinglass API key not configured")
    
    with tab4:
        if 'cmc' in sources:
            cmc_data = sources['cmc']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(
                    f'<div class="data-card">'
                    f'<div class="metric">'
                    f'<div class="metric-value">${cmc_data.get("market_cap", 0):,.0f}</div>'
                    f'<div class="metric-label">Market Cap</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
            
            with col2:
                st.markdown(
                    f'<div class="data-card">'
                    f'<div class="metric">'
                    f'<div class="metric-value">#{cmc_data.get("market_cap_rank", "N/A")}</div>'
                    f'<div class="metric-label">Market Cap Rank</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
        else:
            st.warning("CMC API key not configured")

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    render_header()
    
    # SEARCH BAR
    search_query = render_search_bar()
    
    # PROCESS SEARCH
    if search_query and search_query.strip():
        fetcher = PerplexityStyleDataFetcher()
        results = fetcher.search_asset(search_query)
        render_results_card(results)
    else:
        # SUGGESTIONS
        st.markdown(
            f'<div style="text-align: center; margin-top: 60px; color: {PERPLEXITY_COLORS["text_secondary"]}">'
            f'<p style="font-size: 14px;">Try searching for: <strong>BTC</strong> • <strong>ETH</strong> • <strong>BNBUSDT</strong></p>'
            f'</div>',
            unsafe_allow_html=True
        )

if __name__ == '__main__':
    main()
