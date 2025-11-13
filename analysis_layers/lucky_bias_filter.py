"""
LUCKY BIAS FILTERING
- Sıkça rastgele aşırı iyi sonuç alan coinleri/sinyalleri filtreler.
"""
class LuckyBiasFilter:
    @staticmethod
    def detect_lucky_bias(trades: list, win_rate_threshold: float = 0.8, min_trades: int = 10):
        by_coin = {}
        for trade in trades:
            c = trade['symbol']
            by_coin.setdefault(c, []).append(trade['pnl'])
        lucky = []
        for c, vals in by_coin.items():
            wrate = sum(p>0 for p in vals) / len(vals)
            if wrate >= win_rate_threshold and len(vals) >= min_trades:
                lucky.append({"coin": c, "win_rate": wrate, "trades": len(vals)})
        return lucky
