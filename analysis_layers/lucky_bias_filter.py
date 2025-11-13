"""
LUCKY BIAS FILTERING
Şansa kazanan stratejileri filtrele

Sorun: Eğer sadece 1 coin'de kazandıysak = şans mı?
Çözüm: Statistical significance testi
"""

from typing import Dict, List
import numpy as np
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class LuckyBiasFilter:
    """
    Lucky bias tespiti
    Stratejinin gerçekten iyi mi yoksa şanslı mı?
    """
    
    def __init__(self, min_trades: int = 30):
        """
        Initialize
        
        Args:
            min_trades: Minimum istatistiksel anlamlılık için trade sayısı
        """
        self.min_trades = min_trades
    
    async def detect_lucky_bias(self, trades: List[Dict]) -> Dict:
        """
        Lucky bias tespiti
        
        Args:
            trades: Trade history
                [{
                    'symbol': 'BTCUSDT',
                    'pnl': 150,  # +$150
                    'pnl_percent': 1.5,
                    'timestamp': datetime
                }, ...]
        
        Returns:
            Dict: Lucky bias analysis
        """
        
        if len(trades) < self.min_trades:
            return {
                'enough_data': False,
                'trades': len(trades),
                'min_required': self.min_trades,
                'warning': 'Insufficient data for statistical significance'
            }
        
        # Coin'e göre grupla
        by_coin = {}
        
        for trade in trades:
            symbol = trade.get('symbol', 'UNKNOWN')
            if symbol not in by_coin:
                by_coin[symbol] = []
            
            by_coin[symbol].append(trade)
        
        # Her coin'in win rate'i hesapla
        lucky_winners = []
        
        for symbol, symbol_trades in by_coin.items():
            if len(symbol_trades) < 5:  # Min 5 trade per coin
                continue
            
            wins = sum(1 for t in symbol_trades if t.get('pnl', 0) > 0)
            losses = len(symbol_trades) - wins
            win_rate = wins / len(symbol_trades)
            
            # Binomial test - kazanma oranı istatistiksel anlamlı mı?
            binom_test = stats.binom_test(wins, len(symbol_trades), 0.5, alternative='greater')
            
            # p-value < 0.05 = istatistiksel anlamlı
            is_significant = binom_test < 0.05
            
            if win_rate > 0.80 and not is_significant:
                # Yüksek win rate fakat istatistiksel anlamlı değil = lucky bias
                lucky_winners.append({
                    'symbol': symbol,
                    'win_rate': win_rate * 100,
                    'trades': len(symbol_trades),
                    'wins': wins,
                    'losses': losses,
                    'p_value': binom_test,
                    'is_significant': is_significant,
                    'warning': 'POSSIBLE LUCKY BIAS - High win rate but not statistically significant'
                })
        
        # Overall statistics
        total_trades = len(trades)
        total_wins = sum(1 for t in trades if t.get('pnl', 0) > 0)
        overall_win_rate = total_wins / total_trades if total_trades > 0 else 0
        
        overall_significant = stats.binom_test(total_wins, total_trades, 0.5, alternative='greater') < 0.05
        
        return {
            'total_trades': total_trades,
            'total_wins': total_wins,
            'overall_win_rate': overall_win_rate * 100,
            'statistically_significant': overall_significant,
            'lucky_coins': lucky_winners,
            'recommendation': self._get_recommendation(lucky_winners, overall_significant)
        }
    
    @staticmethod
    def _get_recommendation(lucky_coins: List, overall_sig: bool) -> str:
        """Tavsiye döndür"""
        
        if lucky_coins:
            symbols = [c['symbol'] for c in lucky_coins]
            return f"⚠️ Possible lucky bias detected in: {', '.join(symbols)} - Consider reducing weight"
        
        if overall_sig:
            return "✅ Strategy performance is statistically significant"
        else:
            return "⚠️ Strategy results may be due to luck - Need more data"
