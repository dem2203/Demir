# attribution_analysis.py - Performance Attribution

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class AttributionAnalysis:
    """Analyze where performance comes from"""
    
    def __init__(self):
        self.layer_contributions = {}
    
    def calculate_layer_attribution(self, trades, layer_scores):
        """Calculate each layer's contribution to performance"""
        try:
            attribution = {}
            
            for layer_id, score in enumerate(layer_scores):
                weighted_trades = len(trades) * score
                layer_pnl = sum([t['pnl'] for t in trades]) * score
                
                attribution[f'layer_{layer_id}'] = {
                    'weight': score,
                    'contribution': layer_pnl,
                    'weighted_trades': weighted_trades
                }
            
            return attribution
        
        except Exception as e:
            logger.error(f"Attribution error: {e}")
            return {}

