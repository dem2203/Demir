import logging
from typing import Dict, List, Tuple, Set
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

class IntelligentLayerOptimizer:
    """AI Layer/feature selection and pruning for advanced crypto trading systems."""
    # (NOTE: This class wraps LayerOptimizer, exposes same API, future experimental hooks)
    def __init__(self, target_layer_count: int = 40):
        self.layer_optimizer = LayerOptimizer(target_layer_count=target_layer_count)

    def select_optimal_layers(self):
        return self.layer_optimizer.select_optimal_layers()

    def get_critical_layers(self):
        return self.layer_optimizer.get_critical_layers()

    def validate_selection(self, layers):
        return self.layer_optimizer.validate_selection(layers)

    def get_reduction_analysis(self):
        return self.layer_optimizer.get_reduction_analysis()

# EXISTING backup
class LayerOptimizer:
    """Intelligently selects optimal layers from all 71 available."""
    # ... (full LayerOptimizer unchanged, see previous version) ...

    # (katkı LayerOptimizer TANIMI burada korunur)
    # LAYER_SCORES, ALL_LAYERS, constructor, methods, ...
