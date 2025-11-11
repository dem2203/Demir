#============================================================================
# LAYER 1: ADVANCED CHARTING (YENİ DOSYA)
# ============================================================================
# Dosya: Demir/layers/advanced_charting_layer.py
# Durum: YENİ (eski mock versiyonu replace et)

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)

class AdvancedChartingLayer:
    """
    Production-grade charting with Plotly
    - Real klines data
    - Technical overlays
    - Interactive candlestick charts
    - Volume analysis
    - ZERO mock data!
    """
    
    def __init__(self):
        logger.info("✅ AdvancedChartingLayer initialized")
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes

    def create_trading_chart(self, symbol: str, timeframe: str = '1h', 
                            limit: int = 100) -> dict:
        """
        Create REAL trading chart from Binance data
        - NOT mock chart
        - Real OHLCV data
        - Technical indicators
        """
        
        logger.info(f"📊 Creating trading chart for {symbol} {timeframe}")
        
        try:
            # Fetch REAL klines
            klines = self._fetch_real_klines(symbol, timeframe, limit)
            
            if not klines:
                raise ValueError("No klines data available")
            
            # Convert to DataFrame
            df = pd.DataFrame(klines)
            df.columns = ['time', 'open', 'high', 'low', 'close', 'volume',
                         'close_time', 'quote_volume', 'trades', 'tb_volume', 'tq_volume', 'ignore']
            
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            
            # Calculate technical indicators
            df['sma_20'] = df['close'].rolling(20).mean()
            df['sma_50'] = df['close'].rolling(50).mean()
            df['bb_upper'] = df['close'].rolling(20).mean() + (df['close'].rolling(20).std() * 2)
            df['bb_lower'] = df['close'].rolling(20).mean() - (df['close'].rolling(20).std() * 2)
            
            # Create Plotly figure
            fig = go.Figure()
            
            # Add candlestick
            fig.add_trace(go.Candlestick(
                x=df['time'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='OHLC'
            ))
            
            # Add SMA 20
            fig.add_trace(go.Scatter(
                x=df['time'],
                y=df['sma_20'],
                name='SMA 20',
                line=dict(color='orange', width=1)
            ))
            
            # Add SMA 50
            fig.add_trace(go.Scatter(
                x=df['time'],
                y=df['sma_50'],
                name='SMA 50',
                line=dict(color='blue', width=1)
            ))
            
            # Add Bollinger Bands
            fig.add_trace(go.Scatter(
                x=df['time'],
                y=df['bb_upper'],
                name='BB Upper',
                line=dict(color='rgba(0,100,200,0.3)'),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=df['time'],
                y=df['bb_lower'],
                name='BB Lower',
                fill='tonexty',
                line=dict(color='rgba(0,100,200,0.3)'),
                showlegend=False
            ))
            
            # Update layout
            fig.update_layout(
                title=f"{symbol} {timeframe} - REAL Data",
                yaxis_title=f"{symbol} Price (USDT)",
                xaxis_title="Time",
                template='plotly_dark',
                height=600,
                xaxis_rangeslider_visible=False,
                hovermode='x unified'
            )
            
            logger.info(f"✅ Chart created successfully")
            
            return {
                'chart': fig,
                'data': df,
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"CRITICAL: Chart creation failed: {e}")
            raise

    def _fetch_real_klines(self, symbol: str, interval: str, limit: int):
        """Fetch REAL klines from Binance"""
        try:
            url = "https://fapi.binance.com/fapi/v1/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to fetch klines: {e}")
            raise

