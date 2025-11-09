# PHASE 22: scenario_simulator.py
# Lokasyon: intelligence_layers/scenario_simulator.py

import numpy as np
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class ScenarioSimulator:
    """Phase 22: Monte Carlo scenario simulation"""
    
    def simulate_scenarios(self, current_price: float, volatility_scenarios: Dict) -> Dict:
        """Simulate price paths under different scenarios"""
        
        scenarios = {
            "bull": {"prob": 0.35, "drift": 0.05, "vol": 0.4},
            "stable": {"prob": 0.40, "drift": 0.01, "vol": 0.3},
            "crash": {"prob": 0.20, "drift": -0.10, "vol": 0.8},
            "black_swan": {"prob": 0.05, "drift": -0.40, "vol": 2.0},
        }
        
        results = {}
        
        for scenario_name, params in scenarios.items():
            paths = []
            for _ in range(10000):
                path = self._gbm_path(
                    current_price, 
                    params["drift"], 
                    params["vol"],
                    days=30
                )
                paths.append(path)
            
            final_prices = [p[-1] for p in paths]
            var_95 = np.percentile(final_prices, 5)
            cvar_95 = np.mean([p for p in final_prices if p < var_95])
            
            results[scenario_name] = {
                "probability": params["prob"],
                "expected_price": np.mean(final_prices),
                "var_95": var_95,
                "cvar_95": cvar_95,
            }
        
        return results
    
    def _gbm_path(self, S0: float, drift: float, vol: float, days: int = 30) -> List[float]:
        """Geometric Brownian Motion path"""
        dt = 1.0 / 252
        path = [S0]
        
        for _ in range(days):
            dW = np.random.normal(0, np.sqrt(dt))
            dS = drift * path[-1] * dt + vol * path[-1] * dW
            path.append(path[-1] + dS)
        
        return path
