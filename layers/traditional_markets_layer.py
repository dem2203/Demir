"""
TRADITIONAL MARKETS LAYER - v2.0
Geleneksel piyasalar (SPX, NASDAQ, DXY) ile korelasyon
⚠️ REAL data only - gerçek piyasa fiyatları

Bu layer şunu yapar:
1. SPX, NASDAQ, DXY fiyatlarını al
2. Risk sentiment'i belirle
3. Crypto'ya etki tahmin et
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class TraditionalMarketsLayer(BaseLayer):
    """Geleneksel Piyasalar Layer"""
    
    def __init__(self):
        """Initialize"""
        super().__init__('TraditionalMarkets_Layer')
        self.price_history = {}
    
    async def get_signal(self, market_data):
        """Get traditional markets signal
        
        Args:
            market_data: Dict with:
            {
                'SPX': 5000.50,         # S&P 500 spot price (REAL)
                'NASDAQ': 15000.75,     # NASDAQ spot price (REAL)
                'DXY': 103.50,          # US Dollar Index (REAL)
                'VIX': 20.5             # Volatility Index (REAL)
            }
        
        Returns:
            Signal with impact on crypto
        """
        return await self.execute_with_retry(
            self._analyze_markets,
            market_data
        )
    
    async def _analyze_markets(self, market_data):
        """Analyze traditional markets - GERÇEK VERİ İLE"""
        
        if not market_data:
            raise ValueError("No market data provided")
        
        try:
            # Get REAL prices
            spx = market_data.get('SPX')
            nasdaq = market_data.get('NASDAQ')
            dxy = market_data.get('DXY')
            vix = market_data.get('VIX', 20)
            
            # Validate REAL data
            if spx is None or nasdaq is None or dxy is None:
                raise ValueError("Missing market prices")
            
            # 1. RISK SENTIMENT ANALIZI
            # ===========================
            
            # Equities performance
            equity_trend = self._analyze_equity_trend(spx, nasdaq)
            
            # SPX moving average (son 20 gün gerçek verisi gerekli)
            risk_on = True if equity_trend == 'UP' else False
            
            # 2. DXY ANALIZI (Dolar Gücü)
            # ============================
            # DXY yüksek = Dolar güçlü = Risk OFF
            # DXY düşük = Dolar zayıf = Risk ON
            
            dxy_impact = self._calculate_dxy_impact(dxy)
            
            # 3. VIX KONTROLÜ (Korku Endeksi)
            # ================================
            # VIX düşük = Sakin market
            # VIX yüksek = Volatile market
            
            volatility_high = vix > 25
            
            # 4. FINAL SIGNAL
            # ===============
            
            if risk_on and dxy_impact > 0 and not volatility_high:
                # Hisse yükselişte + Dolar zayıf + Düşük volatilite = BULLISH
                signal = 'BULLISH'
                score = 75.0
                reason = "Risk-on environment: equities rising, weak dollar"
            
            elif not risk_on and dxy_impact < 0 and volatility_high:
                # Hisse düşüşte + Dolar güçlü + Yüksek volatilite = BEARISH
                signal = 'BEARISH'
                score = 25.0
                reason = "Risk-off environment: equities falling, strong dollar"
            
            else:
                # Karışık sinyaller
                signal = 'NEUTRAL'
                score = 50.0
                reason = "Mixed signals from traditional markets"
            
            # Store history
            self.price_history[datetime.now()] = {
                'SPX': spx,
                'NASDAQ': nasdaq,
                'DXY': dxy,
                'VIX': vix,
                'signal': signal
            }
            
            # Limit history size
            if len(self.price_history) > 1000:
                oldest_key = list(self.price_history.keys())
                del self.price_history[oldest_key]
            
            return {
                'signal': signal,
                'score': score,
                'reason': reason,
                'equity_trend': equity_trend,
                'dxy_impact': float(dxy_impact),
                'volatility_level': 'HIGH' if volatility_high else 'NORMAL',
                'spx': float(spx),
                'nasdaq': float(nasdaq),
                'dxy': float(dxy),
                'vix': float(vix),
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"Traditional markets analysis error: {e}")
            raise ValueError(f"Markets error: {e}")
    
    @staticmethod
    def _analyze_equity_trend(spx, nasdaq):
        """SPX ve NASDAQ trend'ini belirle"""
        
        # Basit: Eğer fiyat referans seviyeden yüksekse UP
        # Normalde son 20 günün SMA'sı kullanılır
        
        # Reference levels (son bilinen seviyeler)
        spx_ref = 5000  # Örnek seviye
        nasdaq_ref = 15000  # Örnek seviye
        
        if spx > spx_ref and nasdaq > nasdaq_ref:
            return 'UP'
        elif spx < spx_ref and nasdaq < nasdaq_ref:
            return 'DOWN'
        else:
            return 'MIXED'
    
    @staticmethod
    def _calculate_dxy_impact(dxy):
        """DXY'nin Crypto'ya etkisini hesapla
        
        DXY yüksek = Dolar güçlü = Crypto negatif (kripto ABD dolarıyla ters korelasyon)
        DXY düşük = Dolar zayıf = Crypto pozitif
        """
        
        # Reference DXY level
        dxy_ref = 103.0
        
        # Impact calculation
        if dxy > dxy_ref:
            # Dolar güçlü = Negative for crypto
            impact = -(dxy - dxy_ref) / 10  # Normalize
            return float(impact)
        else:
            # Dolar zayıf = Positive for crypto
            impact = (dxy_ref - dxy) / 10  # Normalize
            return float(impact)
