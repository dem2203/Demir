"""
LIQUIDITY CRISIS DETECTİON
- Ani borsa likidite çıkışlarını tespit eder.
"""
class LiquidityCrisisDetector:
    @staticmethod
    def detect_liquidity_crisis(exchange_flows: list, threshold: float = 10000000.0) -> dict:
        # exchange_flows: [{exchange:"binance", "net_delta": -1e7, "timestamp": ...}, ...]
        crisis_exchanges = [
            f for f in exchange_flows if f['net_delta'] < -threshold
        ]
        return {
            "crisis_detected": bool(crisis_exchanges),
            "details": crisis_exchanges
        }
