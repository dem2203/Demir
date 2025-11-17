"""
DEMIR AI BOT - Database Manager (UPDATED)
Group-based signal logging & persistence
PostgreSQL 7 tables + group-based operations
Production-grade database layer
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GroupBasedDatabaseManager:
    """Manage database operations for group-based signals."""
    
    def __init__(self, database_url: str = None):
        """Initialize database manager."""
        self.database_url = database_url
        self.schema = None
        logger.info("GroupBasedDatabaseManager initialized")
    
    def initialize_schema(self):
        """Create all group signal tables."""
        try:
            from ui.signal_groups_schema import SignalGroupsSchema
            self.schema = SignalGroupsSchema()
            result = self.schema.create_all_tables()
            logger.info(f"Schema initialization: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            return False
    
    def log_group_signals(self, symbol: str, group_signals: Dict[str, Any]) -> bool:
        """Log all group signals to database."""
        try:
            timestamp = datetime.now()
            
            # Log Technical
            if group_signals.get('technical'):
                tech = group_signals['technical']
                self.schema.log_technical_signal(
                    symbol=symbol,
                    direction=tech.get('direction'),
                    strength=tech.get('strength', 0.0),
                    confidence=tech.get('confidence', 0.0),
                    active_layers=tech.get('active_layers', 0),
                    top_layers=list(tech.get('layer_details', {}).keys())[:5]
                )
            
            # Log Sentiment
            if group_signals.get('sentiment'):
                sent = group_signals['sentiment']
                self.schema.log_sentiment_signal(
                    symbol=symbol,
                    direction=sent.get('direction'),
                    strength=sent.get('strength', 0.0),
                    confidence=sent.get('confidence', 0.0),
                    active_layers=sent.get('active_layers', 0),
                    sources=[]
                )
            
            # Log ML
            if group_signals.get('ml'):
                ml = group_signals['ml']
                self.schema.log_ml_signal(
                    symbol=symbol,
                    direction=ml.get('direction'),
                    strength=ml.get('strength', 0.0),
                    confidence=ml.get('confidence', 0.0),
                    active_layers=ml.get('active_layers', 0),
                    models=[]
                )
            
            # Log OnChain
            if group_signals.get('onchain'):
                oc = group_signals['onchain']
                self.schema.log_onchain_signal(
                    symbol=symbol,
                    direction=oc.get('direction'),
                    strength=oc.get('strength', 0.0),
                    confidence=oc.get('confidence', 0.0),
                    active_layers=oc.get('active_layers', 0),
                    indicators=[]
                )
            
            logger.info(f"Group signals logged for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log group signals: {e}")
            return False
    
    def log_risk_assessment(self, symbol: str, risk_data: Dict[str, Any]) -> bool:
        """Log risk assessment to database."""
        try:
            if self.schema:
                self.schema.log_risk_assessment(
                    symbol=symbol,
                    volatility_score=risk_data.get('volatility_score', 0.5),
                    max_loss_exposure=risk_data.get('max_loss_exposure'),
                    kelly_fraction=risk_data.get('kelly_fraction', 0.1),
                    active_layers=risk_data.get('active_layers', 0)
                )
                logger.info(f"Risk assessment logged for {symbol}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to log risk assessment: {e}")
            return False
    
    def log_consensus_signal(
        self,
        symbol: str,
        consensus_data: Dict[str, Any],
        conflict_detected: bool = False,
        conflicts: List[str] = None
    ) -> bool:
        """Log consensus signal to database."""
        try:
            if self.schema:
                self.schema.log_consensus_signal(
                    symbol=symbol,
                    direction=consensus_data.get('direction', 'NEUTRAL'),
                    strength=consensus_data.get('strength', 0.5),
                    confidence=consensus_data.get('confidence', 0.0),
                    conflict_detected=conflict_detected,
                    active_groups=consensus_data.get('active_groups', 0),
                    recommendation=None,
                    conflicts=conflicts or []
                )
                logger.info(f"Consensus signal logged for {symbol}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to log consensus signal: {e}")
            return False
    
    def update_group_performance(
        self,
        group_name: str,
        symbol: str,
        total_trades: int,
        winning_trades: int,
        avg_pnl: float = 0.0,
        sharpe_ratio: float = 0.0,
        max_drawdown: float = 0.0
    ) -> bool:
        """Update group performance metrics."""
        try:
            if self.schema:
                self.schema.update_group_performance(
                    group_name=group_name,
                    symbol=symbol,
                    total_trades=total_trades,
                    winning_trades=winning_trades,
                    avg_pnl=avg_pnl,
                    sharpe_ratio=sharpe_ratio,
                    max_drawdown=max_drawdown
                )
                logger.info(f"Performance metrics updated for {group_name}/{symbol}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update performance metrics: {e}")
            return False
    
    def get_group_statistics(
        self,
        group_name: str,
        symbol: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get group statistics from database."""
        try:
            if self.schema:
                stats = self.schema.get_group_statistics(group_name, symbol, days)
                logger.info(f"Retrieved statistics for {group_name}/{symbol}")
                return stats
            return {}
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def get_recent_signals(
        self,
        group_name: str,
        symbol: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent signals for a group/symbol."""
        try:
            if self.schema:
                signals = self.schema.get_recent_signals(symbol, group_name, limit)
                logger.debug(f"Retrieved {len(signals)} recent signals")
                return signals
            return []
        except Exception as e:
            logger.error(f"Failed to get recent signals: {e}")
            return []
    
    def cleanup_old_data(self, days: int = 90) -> int:
        """Clean up old signals from database."""
        try:
            if self.schema:
                deleted = self.schema.cleanup_old_signals(days)
                logger.info(f"Cleaned up {deleted} old signal records")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0
    
    def get_all_table_names(self) -> List[str]:
        """Get all table names."""
        try:
            if self.schema:
                return self.schema.get_table_names()
            return []
        except Exception as e:
            logger.error(f"Failed to get table names: {e}")
            return []
    
    def get_database_health(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            tables = self.get_all_table_names()
            health = {
                'status': 'healthy' if len(tables) == 7 else 'degraded',
                'tables_count': len(tables),
                'required_tables': 7,
                'tables': tables
            }
            logger.info(f"Database health: {health['status']}")
            return health
        except Exception as e:
            logger.error(f"Failed to check database health: {e}")
            return {'status': 'error', 'message': str(e)}
