"""FAZ 12 - DOSYA 2: factor_optimizer.py - Faktör Ağırlıklarını Optimize Et"""

import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class FactorOptimizer:
    """Genetic Algorithm + Gradient Descent ile faktör ağırlıklarını optimize et"""
    
    def __init__(self, learning_history: List[Dict]):
        self.history = learning_history
        self.population_size = 20
        self.generations = 50
        self.mutation_rate = 0.1
    
    def fitness_score(self, weights: Dict[str, float]) -> float:
        """Ağırlıkların kaç trade'i doğru tahmin ettiğini hesapla"""
        correct = 0
        total = 0
        
        for trade in self.history[-100:]:
            factors = trade.get('factors', {})
            weighted_signal = sum(factors.get(f, 0.5) * weights.get(f, 0.5) for f in weights)
            
            prediction = 'UP' if weighted_signal > 0.5 else 'DOWN'
            actual = 'UP' if trade.get('pnl', 0) > 0 else 'DOWN'
            
            if prediction == actual:
                correct += 1
            total += 1
        
        return correct / (total + 1)
    
    def genetic_algorithm_optimize(self, initial_weights: Dict[str, float]) -> Dict[str, float]:
        """Genetic Algorithm ile optimize et"""
        # Population initialize
        population = []
        for _ in range(self.population_size):
            individual = {k: v + np.random.normal(0, 0.1) for k, v in initial_weights.items()}
            individual = {k: max(0, min(1, v)) for k, v in individual.items()}
            population.append(individual)
        
        for generation in range(self.generations):
            # Evaluate
            fitness_scores = [(ind, self.fitness_score(ind)) for ind in population]
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Keep top 50%
            survivors = [ind for ind, _ in fitness_scores[:self.population_size//2]]
            
            # Crossover + Mutation
            new_population = survivors.copy()
            while len(new_population) < self.population_size:
                parent1, parent2 = np.random.choice(len(survivors), 2, replace=False)
                
                child = {}
                for key in initial_weights.keys():
                    child[key] = (survivors[parent1][key] + survivors[parent2][key]) / 2
                    
                    # Mutation
                    if np.random.random() < self.mutation_rate:
                        child[key] += np.random.normal(0, 0.05)
                    
                    child[key] = max(0, min(1, child[key]))
                
                new_population.append(child)
            
            population = new_population
            
            best_score = fitness_scores[0][1]
            logger.info(f"Generation {generation}: Best fitness = {best_score:.4f}")
        
        # Return best
        best = max(population, key=self.fitness_score)
        return best
    
    def gradient_descent_optimize(self, weights: Dict[str, float], learning_rate: float = 0.01) -> Dict[str, float]:
        """Gradient Descent ile fine-tune"""
        optimized = weights.copy()
        
        for iteration in range(100):
            gradients = {}
            epsilon = 0.001
            
            for factor in weights.keys():
                # Gradient calculation
                w_plus = optimized.copy()
                w_plus[factor] += epsilon
                
                w_minus = optimized.copy()
                w_minus[factor] -= epsilon
                
                f_plus = self.fitness_score(w_plus)
                f_minus = self.fitness_score(w_minus)
                
                gradients[factor] = (f_plus - f_minus) / (2 * epsilon)
            
            # Update weights
            for factor in optimized.keys():
                optimized[factor] += learning_rate * gradients[factor]
                optimized[factor] = max(0, min(1, optimized[factor]))
        
        return optimized
    
    def optimize(self, initial_weights: Dict[str, float]) -> Dict[str, float]:
        """Kombinasyon: GA + GD"""
        logger.info("Starting Genetic Algorithm optimization...")
        ga_optimized = self.genetic_algorithm_optimize(initial_weights)
        
        logger.info("Fine-tuning with Gradient Descent...")
        final_optimized = self.gradient_descent_optimize(ga_optimized)
        
        return final_optimized
    
    def calculate_improvement(self, original_weights: Dict[str, float], optimized_weights: Dict[str, float]) -> float:
        """İyileşme yüzdesini hesapla"""
        original_score = self.fitness_score(original_weights)
        optimized_score = self.fitness_score(optimized_weights)
        
        improvement = (optimized_score - original_score) / (original_score + 1e-10)
        return float(improvement * 100)
