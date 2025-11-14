# metrics_collector.py - Metrics Collection

import logging
import json
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and aggregate system metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.aggregated = {}
    
    def collect_metric(self, metric_name, value, tags=None):
        """Collect metric"""
        self.metrics[metric_name].append({
            'timestamp': datetime.now(),
            'value': value,
            'tags': tags or {}
        })
    
    def get_average(self, metric_name, window=100):
        """Get metric average"""
        if metric_name not in self.metrics:
            return None
        
        recent = self.metrics[metric_name][-window:]
        values = [m['value'] for m in recent]
        
        return sum(values) / len(values) if values else None
