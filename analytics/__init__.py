```python
"""
Analytics Module
Trade analysis, backtesting, performance attribution, reporting
Professional analytics for AI trading bot
"""

import logging

logger = logging.getLogger(__name__)

# Import all analytics classes
from .trade_analyzer import TradeAnalyzer
from .backtest_engine import BacktestEngine
from .attribution_analysis import AttributionAnalysis
from .report_generator import ReportGenerator

# Export all
__all__ = [
    'TradeAnalyzer',
    'BacktestEngine',
    'AttributionAnalysis',
    'ReportGenerator'
]

logger.info("✅ Analytics module loaded")
```
