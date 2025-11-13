"""
LIQUIDATION CASCADE DETECTOR
- 3 ardışık/çok büyük likidasyonda krizi tespit eder.
"""
class LiquidationCascadeDetector:
    @staticmethod
    def detect(liquidations: list, min_count: int = 3, min_total: float = 10000000) -> dict:
        # liquidations: [{symbol:"BTC", amount:float, time:timestamp}]
        last_events = liquidations[-min_count:] if len(liquidations) >= min_count else []
        total_liq = sum(ev['amount'] for ev in last_events)
        return {
            "cascade": (len(last_events) >= min_count and total_liq > min_total),
            "total": total_liq,
            "events": last_events
        }
