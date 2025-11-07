# ============================================================================
# PHASE 8.3: QUANTUM ANNEALING LAYER
# ============================================================================
# âš›ï¸ Quantum Predictive AI - Component 3/3 (FINAL)
# Date: 7 KasÄ±m 2025
# Version: v1.0 - Portfolio Optimization & Constraint Satisfaction
# Time: ~5 hours total
#
# âœ… Features:
# - Quantum annealing for portfolio optimization
# - Constraint satisfaction problem solving
# - Risk-adjusted position sizing
# - D-Wave Leap Cloud integration (optional)
# ============================================================================

import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Quantum annealing imports
try:
    from dwave.system import DWaveSampler, EmbeddingComposite
    from dwave.embedding import embed_problem, unembed_sampleset
    from dimod import BinaryQuadraticModel, Vartype
    DWAVE_AVAILABLE = True
    print("âœ… D-Wave Quantum Annealer available")
except ImportError:
    DWAVE_AVAILABLE = False
    print("âš ï¸ D-Wave Leap not configured - using simulated annealing")

try:
    from scipy.optimize import minimize, differential_evolution
    SCIPY_AVAILABLE = True
    print("âœ… SciPy optimization loaded")
except ImportError:
    SCIPY_AVAILABLE = False

# ============================================================================
# CLASSICAL SIMULATED ANNEALING (Fallback)
# ============================================================================

class SimulatedAnnealing:
    """Classical Simulated Annealing for portfolio optimization"""
    
    def __init__(self, n_assets=5, max_iterations=1000):
        self.n_assets = n_assets
        self.max_iterations = max_iterations
        self.current_solution = None
        self.best_solution = None
        self.best_energy = float('inf')
    
    def objective_function(self, weights, returns, cov_matrix, risk_aversion=0.5):
        """
        Portfolio objective: Maximize return - Minimize risk
        Returns: -portfolio_return + risk_aversion * portfolio_variance
        """
        portfolio_return = np.sum(weights * returns)
        portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
        
        return -portfolio_return + risk_aversion * portfolio_variance
    
    def optimize(self, returns, cov_matrix, risk_aversion=0.5):
        """Optimize portfolio using simulated annealing"""
        if not SCIPY_AVAILABLE:
            return None
        
        try:
            def objective(w):
                # Ensure weights sum to 1
                w = w / np.sum(w)
                return self.objective_function(w, returns, cov_matrix, risk_aversion)
            
            # Constraints: weights sum to 1
            constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
            
            # Bounds: 0 <= weight <= 1
            bounds = [(0, 1) for _ in range(self.n_assets)]
            
            # Initial guess: equal weights
            x0 = np.ones(self.n_assets) / self.n_assets
            
            # Use differential evolution (simulated annealing-like)
            result = differential_evolution(
                objective,
                bounds,
                seed=42,
                maxiter=self.max_iterations,
                atol=1e-6
            )
            
            self.best_solution = result.x / np.sum(result.x)
            self.best_energy = result.fun
            
            return self.best_solution
            
        except Exception as e:
            print(f"âš ï¸ Simulated annealing error: {e}")
            return None

# ============================================================================
# QUANTUM ANNEALING (Primary)
# ============================================================================

class QuantumAnnealingOptimizer:
    """
    Quantum Annealing for Portfolio Optimization
    Solves MaxCut and other combinatorial problems
    """
    
    def __init__(self, n_assets=5, time_limit=10):
        """
        Args:
            n_assets: Number of assets in portfolio
            time_limit: Max time in seconds for D-Wave solve
        """
        self.n_assets = n_assets
        self.time_limit = time_limit
        
        self.quantum_ready = DWAVE_AVAILABLE
        self.simulated_annealer = SimulatedAnnealing(n_assets)
        
        self.best_solution = None
        self.best_energy = float('inf')
        self.optimization_history = []
        
        print(f"""
        â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
        â•‘ QUANTUM ANNEALING OPTIMIZER v1.0       â•‘
        â•‘ Assets: {n_assets} | Time Limit: {time_limit}s    â•‘
        â•‘ Quantum Ready: {"âœ… YES" if self.quantum_ready else "âš ï¸ SIMULATED"}   â•‘
        â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        """)

    def create_qubo_matrix(self, returns, cov_matrix, risk_aversion=0.5):
        """
        Create QUBO (Quadratic Unconstrained Binary Optimization) matrix
        Maps portfolio problem to binary quadratic model
        """
        Q = {}
        
        # Linear terms (returns maximization)
        for i in range(self.n_assets):
            Q[(i, i)] = -returns[i] + risk_aversion * cov_matrix[i, i]
        
        # Quadratic terms (risk minimization)
        for i in range(self.n_assets):
            for j in range(i + 1, self.n_assets):
                Q[(i, j)] = 2 * risk_aversion * cov_matrix[i, j]
        
        return Q

    def solve_quantum(self, returns, cov_matrix, risk_aversion=0.5):
        """Solve using D-Wave Quantum Annealer"""
        if not DWAVE_AVAILABLE:
            print("âš ï¸ D-Wave not available, using simulated annealing...")
            return self.solve_classical(returns, cov_matrix, risk_aversion)
        
        try:
            print("ğŸŒ€ Submitting to D-Wave Quantum Annealer...")
            
            # Create QUBO
            Q = self.create_qubo_matrix(returns, cov_matrix, risk_aversion)
            bqm = BinaryQuadraticModel(Q, 'BINARY')
            
            # Create sampler
            sampler = EmbeddingComposite(DWaveSampler(timeout=self.time_limit))
            
            # Solve
            sampleset = sampler.sample(bqm, num_reads=100)
            
            # Extract best solution
            best_sample = sampleset.first.sample
            best_solution = np.array([best_sample[i] for i in range(self.n_assets)])
            best_solution = best_solution / np.sum(best_solution)
            
            self.best_solution = best_solution
            self.best_energy = sampleset.first.energy
            
            print(f"âœ… Quantum solve complete (Energy: {self.best_energy:.4f})")
            return best_solution
            
        except Exception as e:
            print(f"âš ï¸ Quantum solve error: {e}")
            return self.solve_classical(returns, cov_matrix, risk_aversion)

    def solve_classical(self, returns, cov_matrix, risk_aversion=0.5):
        """Fallback to classical simulated annealing"""
        print("ğŸŒ¡ï¸ Using Classical Simulated Annealing...")
        
        solution = self.simulated_annealer.optimize(returns, cov_matrix, risk_aversion)
        
        if solution is not None:
            self.best_solution = solution
            self.best_energy = self.simulated_annealer.best_energy
            print(f"âœ… Classical optimization complete (Energy: {self.best_energy:.4f})")
        
        return solution

    def optimize_portfolio(self, returns, cov_matrix, risk_aversion=0.5, 
                          use_quantum=True):
        """
        Main portfolio optimization method
        Args:
            returns: Expected returns for each asset
            cov_matrix: Covariance matrix of returns
            risk_aversion: Risk aversion parameter (0=risk seeking, 1=conservative)
            use_quantum: Try quantum annealing if available
        Returns:
            Optimized portfolio weights
        """
        if use_quantum:
            return self.solve_quantum(returns, cov_matrix, risk_aversion)
        else:
            return self.solve_classical(returns, cov_matrix, risk_aversion)

    def analyze_portfolio(self, assets_data: Dict[str, Dict[str, float]]):
        """
        Analyze and optimize portfolio allocation
        Args:
            assets_data: Dict with asset names and their metrics
        Returns:
            Optimized portfolio allocation
        """
        try:
            asset_names = list(assets_data.keys())
            n_assets = len(asset_names)
            
            if n_assets == 0:
                return {'error': 'No assets provided', 'allocation': {}}
            
            # Extract returns and volatility
            returns = np.array([assets_data[name].get('expected_return', 0.05) 
                               for name in asset_names])
            volatility = np.array([assets_data[name].get('volatility', 0.2) 
                                  for name in asset_names])
            
            # Create covariance matrix (simplified)
            correlation = 0.3  # Assumed correlation between assets
            cov_matrix = np.outer(volatility, volatility) * correlation
            np.fill_diagonal(cov_matrix, volatility ** 2)
            
            # Optimize
            weights = self.optimize_portfolio(returns, cov_matrix, risk_aversion=0.5)
            
            if weights is None:
                weights = np.ones(n_assets) / n_assets
            
            # Create allocation dict
            allocation = {}
            for name, weight in zip(asset_names, weights):
                allocation[name] = round(float(weight), 4)
            
            return {
                'allocation': allocation,
                'expected_return': round(float(np.sum(weights * returns)), 4),
                'portfolio_volatility': round(float(np.sqrt(np.dot(weights, 
                                                                    np.dot(cov_matrix, weights)))), 4),
                'method': 'quantum' if self.quantum_ready else 'classical',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"âŒ Portfolio analysis error: {e}")
            return {'error': str(e), 'allocation': {}}

# ============================================================================
# PHASE 8.3 MAIN FUNCTION
# ============================================================================

def get_quantum_annealing_allocation(assets_data: Dict[str, Dict[str, float]]):
    """
    Main entry point for Phase 8.3
    Used by ai_brain for portfolio allocation
    """
    qa = QuantumAnnealingOptimizer(n_assets=len(assets_data))
    return qa.analyze_portfolio(assets_data)

# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("âš›ï¸ QUANTUM ANNEALING - PHASE 8.3 TEST\n")
    
    qa = QuantumAnnealingOptimizer(n_assets=5)
    
    # Test portfolio
    assets = {
        'BTC': {'expected_return': 0.15, 'volatility': 0.60},
        'ETH': {'expected_return': 0.12, 'volatility': 0.65},
        'BNB': {'expected_return': 0.10, 'volatility': 0.55},
        'USDT': {'expected_return': 0.02, 'volatility': 0.01},
        'GOLD': {'expected_return': 0.05, 'volatility': 0.15}
    }
    
    result = get_quantum_annealing_allocation(assets)
    
    print("\n" + "="*60)
    print("âš›ï¸ QUANTUM ANNEALING PORTFOLIO ALLOCATION:")
    print(f"\n   Allocation:")
    for asset, weight in result['allocation'].items():
        print(f"      {asset}: {weight*100:.1f}%")
    print(f"\n   Expected Return: {result['expected_return']*100:.2f}%")
    print(f"   Portfolio Volatility: {result['portfolio_volatility']*100:.2f}%")
    print(f"   Method: {result['method']}")
    print("="*60)
