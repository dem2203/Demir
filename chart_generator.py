# chart_generator.py - ADVANCED CHARTING MODULE

"""
🔱 DEMIR AI TRADING BOT - CHART GENERATOR v1.0
=================================================================
PHASE 5.3: Advanced Interactive Charts
Date: 3 Kasım 2025, 23:30 CET
Version: 1.0 - PRODUCTION READY

✅ ÖZELLİKLER:
--------------
✅ TradingView-style candlestick charts (Plotly)
✅ Entry/TP/SL level markers with annotations
✅ AI confidence score timeline
✅ Multiple indicator overlays (RSI, MACD, Bollinger Bands)
✅ Interactive zoom, pan, hover
✅ Volume bars subplot
✅ Export to HTML/PNG
✅ Responsive design
✅ Dark/Light mode support

USAGE:
------
```python
from chart_generator import ChartGenerator

# Create chart
chart_gen = ChartGenerator()

# OHLCV data (pandas DataFrame)
df = chart_gen.fetch_ohlcv('BTCUSDT', interval='1h', days=7)

# Generate candlestick chart with indicators
fig = chart_gen.create_candlestick_chart(
    df,
    symbol='BTCUSDT',
    show_volume=True,
    indicators=['RSI', 'MACD', 'Bollinger']
)

# Add trade levels
chart_gen.add_trade_levels(
    fig,
    entry_price=67500,
    stop_loss=67000,
    take_profits=[68000, 68500, 69000],
    signal='LONG'
)

# Show or save
fig.show()
chart_gen.save_to_html(fig, 'chart.html')
```
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class ChartGenerator:
    """
    Advanced chart generator for crypto trading analysis
    Production-ready with Plotly
    """
    
    def __init__(self, theme='dark'):
        """
        Initialize Chart Generator
        
        Args:
            theme: 'dark' or 'light' mode
        """
        self.theme = theme
        self.colors = self._get_theme_colors()
        
    def _get_theme_colors(self) -> Dict:
        """Get color scheme based on theme"""
        if self.theme == 'dark':
            return {
                'background': '#1e1e1e',
                'grid': '#2d2d2d',
                'text': '#ffffff',
                'candle_up': '#26a69a',
                'candle_down': '#ef5350',
                'volume': '#64b5f6',
                'entry': '#ffa726',
                'stop_loss': '#ef5350',
                'take_profit': '#66bb6a',
                'indicator': '#7e57c2'
            }
        else:  # light mode
            return {
                'background': '#ffffff',
                'grid': '#e0e0e0',
                'text': '#000000',
                'candle_up': '#00897b',
                'candle_down': '#d32f2f',
                'volume': '#1976d2',
                'entry': '#f57c00',
                'stop_loss': '#c62828',
                'take_profit': '#388e3c',
                'indicator': '#5e35b1'
            }
    
    def fetch_ohlcv(self, symbol='BTCUSDT', interval='1h', days=7) -> pd.DataFrame:
        """
        Fetch OHLCV data from Binance
        
        Args:
            symbol: Trading pair
            interval: Candle interval (1m, 5m, 15m, 1h, 4h, 1d)
            days: Number of days to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            url = "https://fapi.binance.com/fapi/v1/klines"
            
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            params = {
                'symbol': symbol,
                'interval': interval,
                'startTime': start_time,
                'endTime': end_time,
                'limit': 1500
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                    'taker_buy_quote', 'ignore'
                ])
                
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
                
                return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            else:
                print(f"❌ API Error: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return pd.DataFrame()
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators
        
        Args:
            df: OHLCV DataFrame
            
        Returns:
            DataFrame with indicators added
        """
        df = df.copy()
        
        # RSI (14 periods)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD (12, 26, 9)
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands (20, 2)
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # EMA (50, 200)
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()
        
        return df
    
    def create_candlestick_chart(
        self,
        df: pd.DataFrame,
        symbol: str = 'BTCUSDT',
        show_volume: bool = True,
        indicators: List[str] = None,
        height: int = 800
    ) -> go.Figure:
        """
        Create interactive candlestick chart with indicators
        
        Args:
            df: OHLCV DataFrame
            symbol: Trading pair name
            show_volume: Show volume subplot
            indicators: List of indicators to show ['RSI', 'MACD', 'Bollinger', 'EMA']
            height: Chart height in pixels
            
        Returns:
            Plotly Figure object
        """
        if indicators is None:
            indicators = []
        
        # Calculate indicators if requested
        if len(indicators) > 0:
            df = self.calculate_indicators(df)
        
        # Create subplots
        subplot_count = 1
        if show_volume:
            subplot_count += 1
        if 'RSI' in indicators:
            subplot_count += 1
        if 'MACD' in indicators:
            subplot_count += 1
        
        row_heights = [0.6] + [0.2] * (subplot_count - 1)
        
        subplot_titles = [f'{symbol} Candlestick']
        if show_volume:
            subplot_titles.append('Volume')
        if 'RSI' in indicators:
            subplot_titles.append('RSI (14)')
        if 'MACD' in indicators:
            subplot_titles.append('MACD (12, 26, 9)')
        
        fig = make_subplots(
            rows=subplot_count,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=row_heights,
            subplot_titles=subplot_titles
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Price',
                increasing_line_color=self.colors['candle_up'],
                decreasing_line_color=self.colors['candle_down']
            ),
            row=1, col=1
        )
        
        # Bollinger Bands
        if 'Bollinger' in indicators:
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['bb_upper'],
                    name='BB Upper',
                    line=dict(color=self.colors['indicator'], dash='dash', width=1),
                    opacity=0.5
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['bb_middle'],
                    name='BB Middle',
                    line=dict(color=self.colors['indicator'], width=1),
                    opacity=0.5
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['bb_lower'],
                    name='BB Lower',
                    line=dict(color=self.colors['indicator'], dash='dash', width=1),
                    opacity=0.5,
                    fill='tonexty'
                ),
                row=1, col=1
            )
        
        # EMA
        if 'EMA' in indicators:
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['ema_50'],
                    name='EMA 50',
                    line=dict(color='#ff9800', width=1.5)
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['ema_200'],
                    name='EMA 200',
                    line=dict(color='#2196f3', width=1.5)
                ),
                row=1, col=1
            )
        
        current_row = 2
        
        # Volume
        if show_volume:
            colors = [self.colors['candle_up'] if row['close'] >= row['open'] 
                     else self.colors['candle_down'] for idx, row in df.iterrows()]
            
            fig.add_trace(
                go.Bar(
                    x=df['timestamp'],
                    y=df['volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.7
                ),
                row=current_row, col=1
            )
            current_row += 1
        
        # RSI
        if 'RSI' in indicators:
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['rsi'],
                    name='RSI',
                    line=dict(color=self.colors['indicator'], width=2)
                ),
                row=current_row, col=1
            )
            
            # RSI levels (70, 30)
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=current_row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=current_row, col=1)
            
            current_row += 1
        
        # MACD
        if 'MACD' in indicators:
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['macd'],
                    name='MACD',
                    line=dict(color='#2196f3', width=2)
                ),
                row=current_row, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['macd_signal'],
                    name='Signal',
                    line=dict(color='#ff9800', width=2)
                ),
                row=current_row, col=1
            )
            
            # MACD histogram
            colors_macd = ['green' if val >= 0 else 'red' for val in df['macd_hist']]
            fig.add_trace(
                go.Bar(
                    x=df['timestamp'],
                    y=df['macd_hist'],
                    name='Histogram',
                    marker_color=colors_macd,
                    opacity=0.5
                ),
                row=current_row, col=1
            )
        
        # Layout
        fig.update_layout(
            height=height,
            template='plotly_dark' if self.theme == 'dark' else 'plotly_white',
            hovermode='x unified',
            showlegend=True,
            xaxis_rangeslider_visible=False,
            paper_bgcolor=self.colors['background'],
            plot_bgcolor=self.colors['background'],
            font=dict(color=self.colors['text'])
        )
        
        # Update axes
        fig.update_xaxes(gridcolor=self.colors['grid'])
        fig.update_yaxes(gridcolor=self.colors['grid'])
        
        return fig
    
    def add_trade_levels(
        self,
        fig: go.Figure,
        entry_price: float,
        stop_loss: float,
        take_profits: List[float],
        signal: str = 'LONG',
        row: int = 1
    ):
        """
        Add trade entry, SL, and TP levels to chart
        
        Args:
            fig: Plotly Figure
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profits: List of take profit levels
            signal: 'LONG' or 'SHORT'
            row: Subplot row number
        """
        # Entry level
        fig.add_hline(
            y=entry_price,
            line_dash="solid",
            line_color=self.colors['entry'],
            line_width=2,
            annotation_text=f"Entry: ${entry_price:,.2f}",
            annotation_position="right",
            row=row, col=1
        )
        
        # Stop Loss
        fig.add_hline(
            y=stop_loss,
            line_dash="dot",
            line_color=self.colors['stop_loss'],
            line_width=2,
            annotation_text=f"SL: ${stop_loss:,.2f}",
            annotation_position="right",
            row=row, col=1
        )
        
        # Take Profits
        for i, tp in enumerate(take_profits, 1):
            fig.add_hline(
                y=tp,
                line_dash="dash",
                line_color=self.colors['take_profit'],
                line_width=1.5,
                annotation_text=f"TP{i}: ${tp:,.2f}",
                annotation_position="right",
                row=row, col=1
            )
    
    def add_ai_confidence_timeline(
        self,
        fig: go.Figure,
        timestamps: List,
        confidence_scores: List[float],
        row: int
    ):
        """
        Add AI confidence score timeline subplot
        
        Args:
            fig: Plotly Figure
            timestamps: List of timestamps
            confidence_scores: List of AI confidence scores (0-100)
            row: Subplot row number
        """
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=confidence_scores,
                name='AI Confidence',
                line=dict(color='#7e57c2', width=2),
                fill='tozeroy',
                fillcolor='rgba(126, 87, 194, 0.2)'
            ),
            row=row, col=1
        )
        
        # Confidence thresholds
        fig.add_hline(y=70, line_dash="dash", line_color="green", opacity=0.3, row=row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="red", opacity=0.3, row=row, col=1)
    
    def save_to_html(self, fig: go.Figure, filename: str = 'chart.html'):
        """
        Save chart to interactive HTML file
        
        Args:
            fig: Plotly Figure
            filename: Output filename
        """
        try:
            fig.write_html(filename, include_plotlyjs='cdn')
            print(f"✅ Chart saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving chart: {e}")
            return False
    
    def save_to_png(self, fig: go.Figure, filename: str = 'chart.png', width: int = 1920, height: int = 1080):
        """
        Save chart to PNG image (requires kaleido)
        
        Args:
            fig: Plotly Figure
            filename: Output filename
            width: Image width
            height: Image height
        """
        try:
            fig.write_image(filename, width=width, height=height)
            print(f"✅ Chart saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving PNG: {e}")
            print("💡 Install kaleido: pip install kaleido")
            return False

# TEST EXAMPLE
if __name__ == "__main__":
    print("🔱 DEMIR AI CHART GENERATOR v1.0 - PRODUCTION READY")
    print("="*60)
    
    # Create chart generator
    chart_gen = ChartGenerator(theme='dark')
    
    # Fetch data
    print("\n📊 Fetching BTCUSDT data...")
    df = chart_gen.fetch_ohlcv('BTCUSDT', interval='1h', days=7)
    
    if not df.empty:
        print(f"✅ Loaded {len(df)} candles")
        
        # Create chart with all indicators
        print("\n📈 Generating advanced chart...")
        fig = chart_gen.create_candlestick_chart(
            df,
            symbol='BTCUSDT',
            show_volume=True,
            indicators=['RSI', 'MACD', 'Bollinger', 'EMA'],
            height=1000
        )
        
        # Add trade levels (example)
        current_price = df['close'].iloc[-1]
        chart_gen.add_trade_levels(
            fig,
            entry_price=current_price,
            stop_loss=current_price * 0.97,
            take_profits=[
                current_price * 1.01,
                current_price * 1.0162,
                current_price * 1.0262
            ],
            signal='LONG'
        )
        
        # Save
        chart_gen.save_to_html(fig, 'test_chart.html')
        
        print("\n✅ Chart generated successfully!")
        print("📌 Open 'test_chart.html' in browser to view")
        print("📌 This module is ready for streamlit_app.py integration\n")
    else:
        print("❌ No data loaded - check connection")
