# ============================================================================
# LAYER 5: LAYER PERFORMANCE CACHE (YENİ DOSYA)
# ============================================================================
# Dosya: Demir/layers/layer_performance_cache_v5.py
# Durum: YENİ (eski mock versiyonu replace et)

class LayerPerformanceCache:
    """
    Cache layer performance metrics
    - Track layer accuracy
    - Track layer speed
    - Auto-weight optimization
    """
    
    def __init__(self):
        logger.info("✅ LayerPerformanceCache initialized")
        self.cache = {}
        self.performance = {}

    def record_performance(self, layer_name: str, signal: str, 
                         actual_outcome: str, latency: float):
        """
        Record REAL performance data
        - NOT mock statistics
        - Real tracking
        """
        
        if layer_name not in self.performance:
            self.performance[layer_name] = {
                'correct': 0,
                'incorrect': 0,
                'total_latency': 0,
                'call_count': 0
            }
        
        is_correct = (signal == actual_outcome)
        
        self.performance[layer_name]['correct'] += 1 if is_correct else 0
        self.performance[layer_name]['incorrect'] += 0 if is_correct else 1
        self.performance[layer_name]['total_latency'] += latency
        self.performance[layer_name]['call_count'] += 1
        
        logger.debug(f"Performance recorded for {layer_name}: correct={is_correct}, latency={latency:.3f}s")

    def get_layer_accuracy(self, layer_name: str) -> float:
        """Get REAL accuracy (not hardcoded!)"""
        
        if layer_name not in self.performance:
            return 0.5  # Unknown = neutral
        
        perf = self.performance[layer_name]
        total = perf['correct'] + perf['incorrect']
        
        if total == 0:
            return 0.5
        
        accuracy = perf['correct'] / total
        return accuracy

    def get_optimal_weights(self) -> dict:
        """
        Calculate OPTIMAL weights based on performance
        - NOT hardcoded!
        - Real accuracy data
        """
        
        accuracies = {}
        
        for layer_name, perf in self.performance.items():
            total = perf['correct'] + perf['incorrect']
            if total > 0:
                accuracies[layer_name] = perf['correct'] / total
            else:
                accuracies[layer_name] = 0.5
        
        if not accuracies:
            return {}
        
        # Normalize to weights
        total_accuracy = sum(accuracies.values())
        weights = {
            name: acc / total_accuracy 
            for name, acc in accuracies.items()
        }
        
        logger.info(f"✅ Optimal weights calculated: {weights}")
        
        return weights
