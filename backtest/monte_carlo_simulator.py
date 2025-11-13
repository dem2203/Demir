"""
MONTE CARLO SIMULATION
Stress testing
"""

import numpy as np

class MonteCarloSimulator:
    
    @staticmethod
    def run_monte_carlo(returns: list, num_sims: int = 10000) -> Dict:
        """Monte Carlo future scenarios simüle et"""
        
        simulated_returns = []
        
        for _ in range(num_sims):
            simulated_seq = np.random.choice(returns, size=len(returns), replace=True)
            cumulative = np.prod(1 + np.array(simulated_seq)) - 1
            simulated_returns.append(cumulative)
        
        return {
            'mean_return': np.mean(simulated_returns),
            'std_return': np.std(simulated_returns),
            'var_95': np.percentile(simulated_returns, 5),
            'var_99': np.percentile(simulated_returns, 1),
            'best_case': np.max(simulated_returns),
            'worst_case': np.min(simulated_returns)
        }
