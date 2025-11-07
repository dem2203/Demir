"""
🔮 PHASE 8.3 - CROSS-LAYER ANALYZER v1.0
==========================================

Path: utils/cross_layer_analyzer.py
Date: 7 Kasım 2025, 15:07 CET

Detect layer redundancy, correlation clusters, and adjust weights accordingly.
"""

import numpy as np
from collections import defaultdict

def calculate_layer_correlations(history_data):
    """
    Calculate correlation matrix between layers
    
    Args:
        history_data: List of {layer: score} dicts from past analyses
        
    Returns:
        15x15 correlation matrix
    """
    layer_names = ['strategy','kelly','macro','gold','cross_asset',
                  'vix','monte_carlo','news','trad_markets',
                  'black_scholes','kalman','fractal','fourier','copula','rates']
    
    if not history_data or len(history_data) < 10:
        # Return neutral correlation
        return {layer: {layer: 1.0 for layer in layer_names} 
               for layer in layer_names}
    
    try:
        # Build score matrix
        scores = {}
        for layer in layer_names:
            scores[layer] = [h.get(layer, 50) for h in history_data]
        
        # Calculate correlations
        correlations = {}
        for l1 in layer_names:
            correlations[l1] = {}
            for l2 in layer_names:
                if l1 == l2:
                    correlations[l1][l2] = 1.0
                else:
                    try:
                        corr = np.corrcoef(scores[l1], scores[l2])[0, 1]
                        if np.isnan(corr):
                            corr = 0.0
                        correlations[l1][l2] = float(corr)
                    except:
                        correlations[l1][l2] = 0.0
        
        return correlations
    except:
        return {layer: {layer: 1.0 for layer in layer_names} 
               for layer in layer_names}

def detect_redundant_layers(correlations, threshold=0.85):
    """
    Detect layers with high correlation (redundancy)
    
    Returns:
        List of (layer1, layer2, correlation) tuples
    """
    redundant = []
    
    layer_names = list(correlations.keys())
    for i, l1 in enumerate(layer_names):
        for l2 in layer_names[i+1:]:
            corr = abs(correlations.get(l1, {}).get(l2, 0))
            if corr > threshold:
                redundant.append((l1, l2, corr))
    
    return sorted(redundant, key=lambda x: x[2], reverse=True)

def find_voting_blocks(correlations, threshold=0.6):
    """
    Find clusters of correlated layers (voting blocks)
    
    Returns:
        List of layer clusters
    """
    layer_names = list(correlations.keys())
    visited = set()
    blocks = []
    
    for layer in layer_names:
        if layer in visited:
            continue
        
        block = {layer}
        visited.add(layer)
        
        for other in layer_names:
            if other in visited:
                continue
            
            corr = abs(correlations.get(layer, {}).get(other, 0))
            if corr > threshold:
                block.add(other)
                visited.add(other)
        
        blocks.append(block)
    
    return blocks

def calculate_vif(correlations):
    """
    Calculate Variance Inflation Factor for each layer
    High VIF = multicollinearity issue
    """
    vif_scores = {}
    layer_names = list(correlations.keys())
    
    for layer in layer_names:
        # Simple VIF approximation
        avg_corr = np.mean([abs(correlations[layer][other]) 
                           for other in layer_names if other != layer])
        
        vif = 1.0 / (1.0 - avg_corr) if avg_corr < 1.0 else 10.0
        vif_scores[layer] = min(vif, 10.0)  # Cap at 10
    
    return vif_scores

def adjust_weights_for_correlation(base_weights, correlations):
    """
    Adjust weights based on correlation analysis
    
    Rules:
    - Reduce weight if highly correlated with others (redundant)
    - Increase weight if uncorrelated (unique signal)
    """
    adjusted = base_weights.copy()
    vif = calculate_vif(correlations)
    
    for layer in adjusted:
        # High VIF = reduce weight
        adjustment = 1.0 - (vif[layer] - 1.0) / 9.0  # Normalize to 0.1-1.0
        adjusted[layer] *= adjustment
    
    # Normalize
    total = sum(adjusted.values())
    adjusted = {k: v/total for k, v in adjusted.items()}
    
    return adjusted

class CrossLayerAnalyzer:
    """Main analyzer class"""
    
    def __init__(self, history_data=None):
        self.history_data = history_data or []
        self.correlations = {}
        self.redundant_pairs = []
        self.voting_blocks = []
        self.vif_scores = {}
    
    def analyze(self, history_data=None):
        """Run full analysis"""
        if history_data:
            self.history_data = history_data
        
        if len(self.history_data) < 5:
            return {'available': False, 'message': 'Need 5+ history samples'}
        
        self.correlations = calculate_layer_correlations(self.history_data)
        self.redundant_pairs = detect_redundant_layers(self.correlations)
        self.voting_blocks = find_voting_blocks(self.correlations)
        self.vif_scores = calculate_vif(self.correlations)
        
        return {
            'available': True,
            'redundant_count': len(self.redundant_pairs),
            'voting_blocks': len(self.voting_blocks),
            'vif_scores': self.vif_scores
        }
    
    def get_adjusted_weights(self, base_weights):
        """Get correlation-adjusted weights"""
        if not self.correlations:
            return base_weights
        
        return adjust_weights_for_correlation(base_weights, self.correlations)
    
    def get_report(self):
        """Generate analysis report"""
        return {
            'redundant_pairs': self.redundant_pairs[:5],  # Top 5
            'voting_blocks': [list(block) for block in self.voting_blocks],
            'vif_scores': self.vif_scores,
            'high_vif_layers': [k for k, v in self.vif_scores.items() if v > 5]
        }


def analyze_cross_layer_correlations(history_data, base_weights):
    """
    Convenience function
    
    Path: `utils/`
    """
    analyzer = CrossLayerAnalyzer(history_data)
    analyzer.analyze()
    
    adjusted_weights = analyzer.get_adjusted_weights(base_weights)
    report = analyzer.get_report()
    
    return {
        'adjusted_weights': adjusted_weights,
        'report': report,
        'improvement': 'Weights adjusted for layer correlations'
    }
