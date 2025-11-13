"""
MULTI-TIMEFRAME CORRELATION
1m, 5m, 15m, 1h, 4h, 1d sinyallerinin uyumunu kontrol et
"""

import asyncio

class MultiTimeframeCorrelation:
    
    async def analyze_all_timeframes(self, symbol: str, layer_instance) -> Dict:
        """Tüm timeframe'lerde sinyal uyumu"""
        
        timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
        signals = {}
        
        # Paralel olarak tüm TF analiz et
        for tf in timeframes:
            try:
                signal = await layer_instance.get_signal(symbol, tf)
                signals[tf] = signal.get('signal', 'NEUTRAL')
            except:
                signals[tf] = 'NEUTRAL'
        
        # Alignment hesapla
        long_count = sum(1 for s in signals.values() if s == 'LONG')
        short_count = sum(1 for s in signals.values() if s == 'SHORT')
        
        total = len(signals)
        alignment = {
            'long_percent': (long_count / total * 100) if total > 0 else 0,
            'short_percent': (short_count / total * 100) if total > 0 else 0
        }
        
        # Recommendation
        if alignment['long_percent'] >= 80:
            recommendation = 'STRONG_LONG'
        elif alignment['short_percent'] >= 80:
            recommendation = 'STRONG_SHORT'
        elif alignment['long_percent'] >= 60:
            recommendation = 'WEAK_LONG'
        elif alignment['short_percent'] >= 60:
            recommendation = 'WEAK_SHORT'
        else:
            recommendation = 'CONFLICTING'
        
        return {
            'signals_by_tf': signals,
            'alignment': alignment,
            'recommendation': recommendation
        }
