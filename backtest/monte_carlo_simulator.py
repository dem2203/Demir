"""
MONTE CARLO SIMULATION
Stress testing - worst case scenarios

⚠️ REAL DATA: Gerçek historical returns
"""

import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class MonteCarloSimulator:
    """Monte Carlo stress testing"""
    
    @staticmethod
    def run_monte_carlo(returns: List[float], 
                       num_sims: int = 10000) -> Dict:
        """
        Monte Carlo future scenarios simüle et
        
        Args:
            returns: Historical returns (REAL)
            num_sims: Number of simulations
        
        Returns:
            Dict: Simulation results
        """
        
        simulated_returns = []
        
        for _ in range(num_sims):
            # Random olarak geçmiş returns'leri seç (replacement ile)
            simulated_seq = np.random.choice(returns, size=len(returns), replace=True)
            
            # Cumulative return
            cumulative = np.prod(1 + np.array(simulated_seq)) - 1
            simulated_returns.append(cumulative)
        
        return {
            'mean_return': np.mean(simulated_returns),
            'std_return': np.std(simulated_returns),
            'var_95': np.percentile(simulated_returns, 5),     # Worst case %95
            'var_99': np.percentile(simulated_returns, 1),     # Worst case %99
            'best_case': np.max(simulated_returns),
            'worst_case': np.min(simulated_returns),
            'simulations': num_sims,
            'confidence_interval_95': (
                np.percentile(simulated_returns, 2.5),
                np.percentile(simulated_returns, 97.5)
            )
        }
