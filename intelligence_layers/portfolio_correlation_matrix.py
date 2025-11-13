"""
PORTFÖY CORRELATION MATRİKSİ
- Portföy coin'lerinin korelasyon analizini yapar.
"""
import numpy as np

class PortfolioCorrelationMatrix:
    def calculate(self, returns_dict: dict) -> dict:
        # returns_dict: {"BTC": [..], "ETH": [..], ...}
        coins = list(returns_dict.keys())
        rets = np.array([returns_dict[c] for c in coins])
        matrix = np.corrcoef(rets)
        result = {coins[i]: dict(zip(coins, row)) for i, row in enumerate(matrix)}
        # Diverzifikasyon uyarısı
        divers_ok = all(abs(result[c1][c2]) < 0.7 for c1 in coins for c2 in coins if c1 != c2)
        return {"matrix": result, "diversified": divers_ok}

