"""
MULTI-TIMEFRAME CORRELATION
1m, 5m, 15m, 1h, 4h, 1d sinyallerinin uyumunu kontrol et
Hangi timeframe'lerde LONG? Hangi timeframe'lerde SHORT?

⚠️ REAL DATA: Gerçek price verileri her TF için
"""

import asyncio
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class MultiTimeframeCorrelation:
    """
    Multi-timeframe sinyal analizi
    Zaman dilimleri arası uyum kontrol
    """
    
    async def analyze_all_timeframes(self, symbol: str, layer_instance) -> Dict:
        """
        Tüm zaman dilimlerinde sinyal uyumunu analiz et
        
        Args:
            symbol: Coin symbolu (BTCUSDT)
            layer_instance: Analysis layer instance
        
        Returns:
            Dict: Multi-timeframe analysis
            
        ⚠️ REAL DATA: Her TF'de gerçek veri analizi
        """
        
        timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
        signals_by_tf = {}
        
        # Her TF'de sinyal al
        for tf in timeframes:
            try:
                signal = await layer_instance.get_signal(symbol, tf)
                signals_by_tf[tf] = signal.get('signal', 'NEUTRAL')
            except Exception as e:
                logger.warning(f"Failed to get signal for {tf}: {e}")
                signals_by_tf[tf] = 'NEUTRAL'
        
        # Uyum analizi
        alignment = self._calculate_alignment(signals_by_tf)
        
        return {
            'symbol': symbol,
            'signals_by_tf': signals_by_tf,
            'alignment': alignment,
            'recommendation': self._get_recommendation(alignment),
            'details': {
                'total_tf': len(signals_by_tf),
                'long_tf': alignment['long_count'],
                'short_tf': alignment['short_count'],
                'neutral_tf': alignment['neutral_count']
            }
        }
    
    @staticmethod
    def _calculate_alignment(signals_by_tf: Dict) -> Dict:
        """Zaman dilimleri uyumunu hesapla"""
        
        long_count = 0
        short_count = 0
        neutral_count = 0
        
        for tf, signal in signals_by_tf.items():
            if signal == 'LONG':
                long_count += 1
            elif signal == 'SHORT':
                short_count += 1
            else:
                neutral_count += 1
        
        total = len(signals_by_tf)
        
        return {
            'long_count': long_count,
            'short_count': short_count,
            'neutral_count': neutral_count,
            'long_percent': (long_count / total * 100) if total > 0 else 0,
            'short_percent': (short_count / total * 100) if total > 0 else 0,
            'alignment_score': max(long_count, short_count) / total if total > 0 else 0
        }
    
    @staticmethod
    def _get_recommendation(alignment: Dict) -> str:
        """Tavsiye döndür"""
        
        long_pct = alignment['long_percent']
        short_pct = alignment['short_percent']
        
        if long_pct >= 80:
            return 'STRONG_LONG_SIGNAL'
        elif short_pct >= 80:
            return 'STRONG_SHORT_SIGNAL'
        elif long_pct >= 60:
            return 'WEAK_LONG_SIGNAL'
        elif short_pct >= 60:
            return 'WEAK_SHORT_SIGNAL'
        else:
            return 'CONFLICTING_SIGNALS'
