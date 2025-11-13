"""
CONSCIOUSNESS - AI kendi başarısızlıklarını analiz et
"""

from typing import List, Dict
import numpy as np

class RootCauseAnalyzer:
    
    def __init__(self):
        self.trade_history = []
    
    def analyze_failures(self, trades: List[Dict]) -> Dict:
        """
        Başarısızlık nedenlerini analiz et
        
        Sorular:
        - Hangi layer'lar düşük başarı oranında?
        - Hangi coin'lerde hata yapıyorum?
        - Hangi saatlerde başarısız?
        """
        
        by_signal_type = {}
        by_coin = {}
        by_hour = {}
        
        for trade in trades:
            # Signal türüne göre grupla
            signal_type = trade.get('signal_type', 'UNKNOWN')
            if signal_type not in by_signal_type:
                by_signal_type[signal_type] = {'wins': 0, 'losses': 0}
            
            if trade['pnl'] > 0:
                by_signal_type[signal_type]['wins'] += 1
            else:
                by_signal_type[signal_type]['losses'] += 1
            
            # Coin'e göre grupla
            coin = trade.get('symbol', 'UNKNOWN')
            if coin not in by_coin:
                by_coin[coin] = {'wins': 0, 'losses': 0}
            
            if trade['pnl'] > 0:
                by_coin[coin]['wins'] += 1
            else:
                by_coin[coin]['losses'] += 1
            
            # Saat'e göre grupla
            hour = trade['timestamp'].hour if 'timestamp' in trade else 0
            if hour not in by_hour:
                by_hour[hour] = {'wins': 0, 'losses': 0}
            
            if trade['pnl'] > 0:
                by_hour[hour]['wins'] += 1
            else:
                by_hour[hour]['losses'] += 1
        
        # Zayıf alanları tespit et
        weak_signals = []
        for signal, stats in by_signal_type.items():
            total = stats['wins'] + stats['losses']
            if total > 0:
                win_rate = stats['wins'] / total
                if win_rate < 0.50:
                    weak_signals.append({
                        'signal': signal,
                        'win_rate': win_rate * 100,
                        'trades': total
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
            'recommendations': self.generate_recommendations(weak_signals, weak_coins, weak_hours)
        }
    
    def generate_recommendations(self, weak_signals, weak_coins, weak_hours):
        """Öneriler döndür"""
        recommendations = []
        
        for signal in weak_signals:
            recommendations.append(f"⚠️ Signal '{signal['signal']}' low win rate ({signal['win_rate']:.1f}%) - Disable or reduce weight")
        
        for coin in weak_coins:
            recommendations.append(f"🪙 Coin '{coin['coin']}' low performance ({coin['win_rate']:.1f}%) - Focus on major coins (BTC, ETH)")
        
        for hour in weak_hours:
            recommendations.append(f"⏰ Hour {hour['hour']:02d}:00 weak performance ({hour['win_rate']:.1f}%) - Skip trading this hour")
        
        return recommendations
