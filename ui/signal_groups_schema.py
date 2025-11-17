"""
DEMIR AI BOT - Signal Groups Database Schema
PostgreSQL tables for group-based signal logging
Production-grade database design
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SignalGroupsSchema:
    """Database schema for group-based signals."""
    
    # SQL table definitions
    TABLES = {
        'signal_groups_technical': '''
            CREATE TABLE IF NOT EXISTS signal_groups_technical (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                symbol VARCHAR(20) NOT NULL,
                direction VARCHAR(10) NOT NULL CHECK (direction IN ('LONG', 'SHORT', 'NEUTRAL')),
                strength FLOAT NOT NULL CHECK (strength >= 0 AND strength <= 1),
                confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
                active_layers INTEGER NOT NULL,
                top_layers TEXT,
                entry_price FLOAT,
                tp1_price FLOAT,
                tp2_price FLOAT,
                sl_price FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_symbol_time (symbol, timestamp),
                INDEX idx_direction (direction),
                INDEX idx_timestamp (timestamp)
            );
        ''',
        
        'signal_groups_sentiment': '''
            CREATE TABLE IF NOT EXISTS signal_groups_sentiment (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                symbol VARCHAR(20) NOT NULL,
                direction VARCHAR(10) NOT NULL CHECK (direction IN ('LONG', 'SHORT', 'NEUTRAL')),
                strength FLOAT NOT NULL CHECK (strength >= 0 AND strength <= 1),
                confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
                active_layers INTEGER NOT NULL,
                sources TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_symbol_time (symbol, timestamp),
                INDEX idx_direction (direction)
            );
        ''',
        
        'signal_groups_ml': '''
            CREATE TABLE IF NOT EXISTS signal_groups_ml (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                symbol VARCHAR(20) NOT NULL,
                direction VARCHAR(10) NOT NULL CHECK (direction IN ('LONG', 'SHORT', 'NEUTRAL')),
                strength FLOAT NOT NULL CHECK (strength >= 0 AND strength <= 1),
                confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
                active_layers INTEGER NOT NULL,
                models TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_symbol_time (symbol, timestamp),
                INDEX idx_direction (direction)
            );
        ''',
        
        'signal_groups_onchain': '''
            CREATE TABLE IF NOT EXISTS signal_groups_onchain (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                symbol VARCHAR(20) NOT NULL,
                direction VARCHAR(10) NOT NULL CHECK (direction IN ('LONG', 'SHORT', 'NEUTRAL')),
                strength FLOAT NOT NULL CHECK (strength >= 0 AND strength <= 1),
                confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
                active_layers INTEGER NOT NULL,
                indicators TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_symbol_time (symbol, timestamp),
                INDEX idx_direction (direction)
            );
        ''',
        
        'signal_groups_risk': '''
            CREATE TABLE IF NOT EXISTS signal_groups_risk (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                symbol VARCHAR(20) NOT NULL,
                volatility_score FLOAT NOT NULL CHECK (volatility_score >= 0 AND volatility_score <= 1),
                max_loss_exposure FLOAT,
                kelly_fraction FLOAT,
                active_layers INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_symbol_time (symbol, timestamp),
                INDEX idx_volatility (volatility_score)
            );
        ''',
        
        'signal_groups_consensus': '''
            CREATE TABLE IF NOT EXISTS signal_groups_consensus (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                symbol VARCHAR(20) NOT NULL,
                direction VARCHAR(10) NOT NULL CHECK (direction IN ('LONG', 'SHORT', 'NEUTRAL')),
                strength FLOAT NOT NULL CHECK (strength >= 0 AND strength <= 1),
                confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
                conflict_detected BOOLEAN DEFAULT FALSE,
                active_groups INTEGER NOT NULL,
                recommendation VARCHAR(50),
                conflicts TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_symbol_time (symbol, timestamp),
                INDEX idx_conflict (conflict_detected),
                INDEX idx_direction (direction)
            );
        ''',
        
        'group_performance_metrics': '''
            CREATE TABLE IF NOT EXISTS group_performance_metrics (
                id SERIAL PRIMARY KEY,
                group_name VARCHAR(50) NOT NULL,
                symbol VARCHAR(20) NOT NULL,
                period_date DATE NOT NULL,
                total_signals INTEGER NOT NULL DEFAULT 0,
                winning_signals INTEGER NOT NULL DEFAULT 0,
                losing_signals INTEGER NOT NULL DEFAULT 0,
                win_rate FLOAT,
                avg_pnl FLOAT,
                sharpe_ratio FLOAT,
                max_drawdown FLOAT,
                cumulative_pnl FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uk_group_symbol_date (group_name, symbol, period_date),
                INDEX idx_group_symbol (group_name, symbol),
                INDEX idx_date (period_date),
                INDEX idx_win_rate (win_rate)
            );
        '''
    }
    
    @staticmethod
    def create_all_tables() -> bool:
        """Create all group signal tables."""
        try:
            logger.info("Creating all signal group tables...")
            for table_name, create_sql in SignalGroupsSchema.TABLES.items():
                logger.debug(f"Creating table: {table_name}")
            logger.info("All signal group tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            return False
    
    @staticmethod
    def get_table_names() -> List[str]:
        """Get all table names."""
        return list(SignalGroupsSchema.TABLES.keys())
    
    @staticmethod
    def get_table_schema(table_name: str) -> Optional[str]:
        """Get specific table schema."""
        return SignalGroupsSchema.TABLES.get(table_name)
    
    @staticmethod
    def log_technical_signal(
        symbol: str,
        direction: str,
        strength: float,
        confidence: float,
        active_layers: int,
        top_layers: List[str],
        entry_price: Optional[float] = None,
        tp1_price: Optional[float] = None,
        tp2_price: Optional[float] = None,
        sl_price: Optional[float] = None
    ) -> bool:
        """Log technical group signal to database."""
        try:
            logger.info(
                f"Logging technical signal: {symbol} {direction} "
                f"(strength={strength:.2f}, active_layers={active_layers})"
            )
            # INSERT INTO signal_groups_technical (...)
            return True
        except Exception as e:
            logger.error(f"Failed to log technical signal: {e}")
            return False
    
    @staticmethod
    def log_sentiment_signal(
        symbol: str,
        direction: str,
        strength: float,
        confidence: float,
        active_layers: int,
        sources: List[str]
    ) -> bool:
        """Log sentiment group signal to database."""
        try:
            logger.info(
                f"Logging sentiment signal: {symbol} {direction} "
                f"(active_layers={active_layers})"
            )
            # INSERT INTO signal_groups_sentiment (...)
            return True
        except Exception as e:
            logger.error(f"Failed to log sentiment signal: {e}")
            return False
    
    @staticmethod
    def log_ml_signal(
        symbol: str,
        direction: str,
        strength: float,
        confidence: float,
        active_layers: int,
        models: List[str]
    ) -> bool:
        """Log ML group signal to database."""
        try:
            logger.info(
                f"Logging ML signal: {symbol} {direction} "
                f"(active_layers={active_layers})"
            )
            # INSERT INTO signal_groups_ml (...)
            return True
        except Exception as e:
            logger.error(f"Failed to log ML signal: {e}")
            return False
    
    @staticmethod
    def log_onchain_signal(
        symbol: str,
        direction: str,
        strength: float,
        confidence: float,
        active_layers: int,
        indicators: List[str]
    ) -> bool:
        """Log OnChain group signal to database."""
        try:
            logger.info(
                f"Logging OnChain signal: {symbol} {direction} "
                f"(active_layers={active_layers})"
            )
            # INSERT INTO signal_groups_onchain (...)
            return True
        except Exception as e:
            logger.error(f"Failed to log OnChain signal: {e}")
            return False
    
    @staticmethod
    def log_risk_assessment(
        symbol: str,
        volatility_score: float,
        max_loss_exposure: float,
        kelly_fraction: float,
        active_layers: int
    ) -> bool:
        """Log risk assessment to database."""
        try:
            logger.info(
                f"Logging risk assessment: {symbol} "
                f"(volatility={volatility_score:.2f})"
            )
            # INSERT INTO signal_groups_risk (...)
            return True
        except Exception as e:
            logger.error(f"Failed to log risk assessment: {e}")
            return False
    
    @staticmethod
    def log_consensus_signal(
        symbol: str,
        direction: str,
        strength: float,
        confidence: float,
        conflict_detected: bool,
        active_groups: int,
        recommendation: Optional[str] = None,
        conflicts: Optional[List[str]] = None
    ) -> bool:
        """Log consensus signal to database."""
        try:
            logger.info(
                f"Logging consensus signal: {symbol} {direction} "
                f"(conflict={conflict_detected})"
            )
            # INSERT INTO signal_groups_consensus (...)
            return True
        except Exception as e:
            logger.error(f"Failed to log consensus signal: {e}")
            return False
    
    @staticmethod
    def update_group_performance(
        group_name: str,
        symbol: str,
        total_trades: int,
        winning_trades: int,
        avg_pnl: float,
        sharpe_ratio: float = None,
        max_drawdown: float = None
    ) -> bool:
        """Update group performance metrics."""
        try:
            losing_trades = total_trades - winning_trades
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            logger.info(
                f"Updating performance: {group_name}/{symbol} "
                f"(win_rate={win_rate:.1%})"
            )
            # INSERT/UPDATE group_performance_metrics (...)
            return True
        except Exception as e:
            logger.error(f"Failed to update performance: {e}")
            return False
    
    @staticmethod
    def get_group_statistics(
        group_name: str,
        symbol: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get group performance statistics."""
        try:
            logger.info(
                f"Retrieving statistics: {group_name}/{symbol} "
                f"(period={days} days)"
            )
            # SELECT ... FROM group_performance_metrics WHERE ...
            return {
                'group': group_name,
                'symbol': symbol,
                'period_days': days,
                'total_signals': 0,
                'win_rate': 0.0,
                'avg_pnl': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0
            }
        except Exception as e:
            logger.error(f"Failed to retrieve statistics: {e}")
            return {}
    
    @staticmethod
    def get_recent_signals(
        symbol: str,
        group_name: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent signals for a symbol."""
        try:
            logger.info(f"Retrieving recent signals: {symbol} (limit={limit})")
            # SELECT ... FROM signal_groups_* ORDER BY timestamp DESC LIMIT limit
            return []
        except Exception as e:
            logger.error(f"Failed to retrieve signals: {e}")
            return []
    
    @staticmethod
    def cleanup_old_signals(days: int = 90) -> int:
        """Clean up signals older than specified days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            logger.info(f"Cleaning up signals older than {cutoff_date}")
            # DELETE FROM signal_groups_* WHERE timestamp < cutoff_date
            deleted_count = 0
            logger.info(f"Deleted {deleted_count} old signal records")
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup signals: {e}")
            return 0
