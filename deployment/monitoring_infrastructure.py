```python
class PrometheusMetrics:
    """Prometheus metrics collection"""
    
    def __init__(self):
        from prometheus_client import Counter, Gauge, Histogram, Summary
        
        # Trading metrics
        self.trades_total = Counter(
            'demir_trades_total',
            'Total trades executed',
            ['symbol', 'side']
        )
        
        self.trades_pnl = Gauge(
            'demir_trades_pnl',
            'Trade P&L',
            ['symbol']
        )
        
        self.signals_generated = Counter(
            'demir_signals_generated',
            'Signals generated',
            ['type']
        )
        
        # System metrics
        self.api_latency = Histogram(
            'demir_api_latency_seconds',
            'API latency',
            ['exchange']
        )
        
        self.model_inference_time = Histogram(
            'demir_model_inference_ms',
            'Model inference time',
            ['model']
        )
```
