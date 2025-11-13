"""
CONSCIOUSNESS - ROOT CAUSE ANALYZER
AI kendi başarısızlıklarını analiz et
Hangi signal'lar düşük win rate?
Hangi coin'lerde hata yapıyoruz?
Hangi saatlerde başarısız?

⚠️ REAL DATA: Trade history üzerinde gerçek analiz
"""

from typing import List, Dict
import numpy as np
import logging

logger = logging.getLogger(__name__)


class RootCauseAnalyzer:
    """
    Root Cause Analysis
    AI'nin başarısızlık nedenlerini bul
    """
    
    def __init__(self):
        self.trade_history = []
    
    def analyze_failures(self, trades: List[Dict]) -> Dict:
        """
        Başarısızlık nedenlerini analiz et
        
        ⚠️ REAL DATA: Gerçek trade history
        
        Args:
            trades: [{
                'symbol': 'BTCUSDT',
                'signal_type': 'RSI_OVERBOUGHT',
                'entry_time': datetime,
                'pnl': 150.0,  # Positive = win
                'timestamp': datetime
            }, ...]
        
        Returns:
            Dict: Zayıf alanları ve öneriler
        """
        
        by_signal_type = {}
        by_coin = {}
        by_hour = {}
        
        # Trade'leri grupla
        for trade in trades:
            # Signal türüne göre
            signal_type = trade.get('signal_type', 'UNKNOWN')
            if signal_type not in by_signal_type:
                by_signal_type[signal_type] = {'wins': 0, 'losses': 0}
            
            if trade.get('pnl', 0) > 0:
                by_signal_type[signal_type]['wins'] += 1
            else:
                by_signal_type[signal_type]['losses'] += 1
            
            # Coin'e göre
            coin = trade.get('symbol', 'UNKNOWN')
            if coin not in by_coin:
                by_coin[coin] = {'wins': 0, 'losses': 0}
            
            if trade.get('pnl', 0) > 0:
                by_coin[coin]['wins'] += 1
            else:
                by_coin[coin]['losses'] += 1
            
            # Saat'e göre
            try:
                hour = trade['timestamp'].hour if 'timestamp' in trade else 0
            except:
                hour = 0
            
            if hour not in by_hour:
                by_hour[hour] = {'wins': 0, 'losses': 0}
            
            if trade.get('pnl', 0) > 0:
                by_hour[hour]['wins'] += 1
            else:
                by_hour[hour]['losses'] += 1
        
        # Zayıf alanları tespit et
        weak_signals = []
        for signal, stats in by_signal_type.items():
            total = stats['wins'] + stats['losses']
            if total > 0:
                win_rate = stats['wins'] / total
                if win_rate < 0.50:  # Win rate < %50
                    weak_signals.append({
                        'signal': signal,
                        'win_rate': win_rate * 100,
                        'trades': total,
                        'severity': 'CRITICAL' if win_rate < 0.30 else 'WARNING'
                    })
        
        weak_coins = []
        for coin, stats in by_coin.items():
            total = stats['wins'] + stats['losses']
            if total > 0:
                win_rate = stats['wins'] / total
                if win_rate < 0.50:
                    weak_coins.append({
                        'coin': coin,
                        'win_rate': win_rate * 100,
                        'trades': total
                    })
        
        weak_hours = []
        for hour, stats in by_hour.items():
            total = stats['wins'] + stats['losses']
            if total > 0:
                win_rate = stats['wins'] / total
                if win_rate < 0.50:
                    weak_hours.append({
                        'hour': hour,
                        'win_rate': win_rate * 100,
                        'trades': total
                    })
        
        return {
            'weak_signals': weak_signals,
            'weak_coins': weak_coins,
            'weak_hours': weak_hours,
            'recommendations': self.generate_recommendations(
                weak_signals, weak_coins, weak_hours
            )
        }
    
    def generate_recommendations(self, weak_signals, weak_coins, weak_hours):
        """Öneriler döndür"""
        
        recommendations = []
        
        for signal in weak_signals:
            action = "DISABLE" if signal['win_rate'] < 30 else "REDUCE_WEIGHT"
            recommendations.append({
                'type': 'SIGNAL_ACTION',
                'signal': signal['signal'],
                'win_rate': signal['win_rate'],
                'action': action,
                'reason': f"Low win rate: {signal['win_rate']:.1f}%"
            })
        
        for coin in weak_coins:
            recommendations.append({
                'type': 'COIN_ACTION',
                'coin': coin['coin'],
                'win_rate': coin['win_rate'],
                'action': 'REDUCE_POSITION_SIZE',
                'reason': f"Poor performance on {coin['coin']}"
            })
        
        for hour in weak_hours:
            recommendations.append({
                'type': 'TIME_ACTION',
                'hour': hour['hour'],
                'win_rate': hour['win_rate'],
                'action': 'AVOID_TRADING',
                'reason': f"Low success rate at {hour['hour']:02d}:00"
            })
        
        return recommendations
