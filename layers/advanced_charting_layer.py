"""
PHASE 5.2: ADVANCED CHARTING LAYER
File 2 of 10 (ayrı dosyalar)
Folder: layers/advanced_charting_layer.py

Advanced financial charting with Plotly
- Candlestick charts
- Technical indicators
- Multi-timeframe support
- Interactive features
"""

import plotly.graph_objects as go
import pandas as pd
from typing import List, Optional, Dict, Any
import numpy as np
import logging

logger = logging.getLogger(__name__)


class AdvancedChartingLayer:
    """
    Advanced financial charting engine with Plotly
    
    Features:
    - Interactive candlestick charts
    - Multiple technical indicators
    - Multi-asset comparison
    - Export capabilities
    """
    
    @staticmethod
    def create_candlestick_chart(df: pd.DataFrame, title: str = "Price Chart",
                                height: int = 600) -> go.Figure:
        """
        Create interactive candlestick chart
        
        Args:
            df: DataFrame with OHLC columns (open, high, low, close)
            title: Chart title
            height: Chart height in pixels
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='OHLC',
            increasing_line_color='green',
            decreasing_line_color='red'
        )])
        
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            template='plotly_dark',
            hovermode='x unified',
            height=height,
            xaxis_rangeslider_visible=False,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    
    @staticmethod
    def add_moving_averages(fig: go.Figure, df: pd.DataFrame,
                           sma_periods: List[int] = [20, 50, 200]) -> go.Figure:
        """
        Add simple moving averages to chart
        
        Args:
            fig: Existing Plotly figure
            df: Price dataframe with 'close' column
            sma_periods: List of SMA periods
            
        Returns:
            Updated figure with SMAs
        """
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'yellow']
        
        for i, period in enumerate(sma_periods):
            sma = df['close'].rolling(window=period).mean()
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=sma,
                mode='lines',
                name=f'SMA {period}',
                line=dict(color=colors[i % len(colors)], width=1.5),
                hoverinfo='y+name'
            ))
        
        return fig
    
    @staticmethod
    def add_bollinger_bands(fig: go.Figure, df: pd.DataFrame,
                           period: int = 20, std_dev: float = 2) -> go.Figure:
        """
        Add Bollinger Bands
        
        Args:
            fig: Existing figure
            df: Dataframe with 'close'
            period: BB period
            std_dev: Standard deviations
            
        Returns:
            Updated figure
        """
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        fig.add_trace(go.Scatter(
            x=df.index, y=upper_band,
            mode='lines', name='BB Upper',
            line=dict(width=0), showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index, y=lower_band,
            mode='lines', name='BB Lower',
            fill='tonexty',
            line=dict(width=0),
            fillcolor='rgba(68, 68, 68, 0.2)',
            showlegend=True
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index, y=sma,
            mode='lines', name='BB Middle',
            line=dict(color='rgba(100, 100, 100, 0.5)', width=1, dash='dash')
        ))
        
        return fig
    
    @staticmethod
    def add_volume_subplot(fig: go.Figure, df: pd.DataFrame,
                          color_scheme: str = 'auto') -> go.Figure:
        """
        Add volume subplot to chart
        
        Args:
            fig: Existing figure
            df: Dataframe with 'volume' and 'close'
            color_scheme: Volume bar colors
            
        Returns:
            Updated figure
        """
        if color_scheme == 'auto':
            colors = ['red' if close < open_ else 'green'
                     for close, open_ in zip(df['close'], df['open'])]
        else:
            colors = 'rgba(100, 100, 100, 0.5)'
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['volume'],
            name='Volume',
            yaxis='y2',
            marker=dict(color=colors),
            opacity=0.7
        ))
        
        fig.update_layout(
            yaxis2=dict(
                title='Volume',
                overlaying='y',
                side='right'
            )
        )
        
        return fig
    
    @staticmethod
    def add_rsi(fig: go.Figure, df: pd.DataFrame, period: int = 14) -> go.Figure:
        """Add RSI indicator subplot"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        fig.add_trace(go.Scatter(
            x=df.index, y=rsi,
            mode='lines', name=f'RSI {period}',
            line=dict(color='orange', width=1),
            yaxis='y3'
        ))
        
        fig.update_layout(
            yaxis3=dict(
                title='RSI',
                overlaying='y',
                side='right',
                range=[0, 100]
            )
        )
        
        return fig
    
    @staticmethod
    def create_comparison_chart(datasets: Dict[str, pd.DataFrame],
                               title: str = "Asset Comparison") -> go.Figure:
        """
        Create comparison chart for multiple assets
        
        Args:
            datasets: Dict of {asset_name: DataFrame}
            title: Chart title
            
        Returns:
            Comparison figure
        """
        fig = go.Figure()
        
        for asset_name, df in datasets.items():
            normalized_price = (df['close'] / df['close'].iloc[0]) * 100
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=normalized_price,
                mode='lines',
                name=asset_name,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Performance (%)',
            template='plotly_dark',
            hovermode='x unified',
            height=600
        )
        
        return fig


if __name__ == "__main__":
    print("✅ PHASE 5.2: Advanced Charting Ready")
