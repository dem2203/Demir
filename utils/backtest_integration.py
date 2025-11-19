# utils/backtest_integration.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DEMIR AI v7.0 - BACKTEST INTEGRATION (PRODUCTION-GRADE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPREHENSIVE BACKTESTING ENGINE

Features:
    ✅ Per-group backtesting & performance analysis
    ✅ Ranking & comparison across groups
    ✅ CSV export functionality
    ✅ Portfolio metrics calculation
    ✅ Best/worst performer identification
    ✅ Full pipeline automation

Groups:
    - Technical Analysis
    - Sentiment Analysis  
    - Machine Learning
    - On-Chain Analysis
    - Macro & Risk

DEPLOYMENT: Railway Production
AUTHOR: DEMIR AI Research Team
DATE: 2025-11-19
VERSION: 7.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import logging
from typing import Dict, Any, List
import numpy as np

logger = logging.getLogger(__name__)

# ============================================================================
# GROUP-BASED BACKTEST INTEGRATION
# ============================================================================

class GroupBasedBacktestIntegration:
    """
    Manage backtesting for group-based signals
    
    Provides comprehensive backtesting capabilities for all signal groups
    with detailed performance metrics, ranking, and export functionality.
    """
    
    def __init__(self):
        """Initialize backtest integration"""
        try:
            from ui.group_signal_backtest import GroupSignalBacktester
            self.backtester = GroupSignalBacktester()
            logger.info("✅ GroupSignalBacktester initialized")
        except ImportError as e:
            logger.error(f"❌ Failed to import GroupSignalBacktester: {e}")
            raise
    
    # ========================================================================
    # MAIN BACKTESTING METHODS
    # ========================================================================
    
    def backtest_all_groups(
        self,
        signals: List[Dict],
        ohlcv_data: List[Dict]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Backtest all signal groups
        
        Args:
            signals: List of signal dictionaries
            ohlcv_data: List of OHLCV data dictionaries
        
        Returns:
            Dictionary with backtest results for each group
        """
        try:
            logger.info("📊 Starting backtest for all groups")
            results = {}
            
            # Backtest technical group
            logger.info("🔧 Backtesting technical signals...")
            results['technical'] = self.backtester.backtest_technical_signals(
                signals, ohlcv_data
            )
            
            # Backtest sentiment group
            logger.info("💭 Backtesting sentiment signals...")
            results['sentiment'] = self.backtester.backtest_sentiment_signals(
                signals, ohlcv_data
            )
            
            # Backtest ML group
            logger.info("🧠 Backtesting ML signals...")
            results['ml'] = self.backtester.backtest_ml_signals(
                signals, ohlcv_data
            )
            
            # Backtest OnChain group
            logger.info("⛓️ Backtesting OnChain signals...")
            results['onchain'] = self.backtester.backtest_onchain_signals(
                signals, ohlcv_data
            )
            
            logger.info("✅ Backtest complete for all groups")
            return results
        
        except Exception as e:
            logger.error(f"❌ Failed to backtest groups: {e}")
            return {}
    
    # ========================================================================
    # PERFORMANCE ANALYSIS
    # ========================================================================
    
    def compare_group_performance(
        self,
        backtest_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare and rank group performance
        
        Args:
            backtest_results: Backtest results from all groups
        
        Returns:
            Ranked performance dictionary
        """
        try:
            logger.info("📈 Comparing group performance")
            ranked = self.backtester.compare_group_performance(backtest_results)
            
            # Log ranking
            logger.info("🏆 Group Performance Ranking:")
            for i, (group, metrics) in enumerate(ranked.items(), 1):
                win_rate = metrics.get('win_rate', 0)
                total_trades = metrics.get('total_trades', 0)
                total_pnl = metrics.get('total_pnl', 0)
                logger.info(
                    f"  {i}. {group.upper():15} | "
                    f"Win Rate: {win_rate:6.1%} | "
                    f"Trades: {total_trades:5} | "
                    f"Total PnL: {total_pnl:8.2f}%"
                )
            
            return ranked
        
        except Exception as e:
            logger.error(f"❌ Failed to compare performance: {e}")
            return {}
    
    def generate_performance_report(
        self,
        backtest_results: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Generate comprehensive performance report
        
        Args:
            backtest_results: Backtest results from all groups
        
        Returns:
            Formatted report string
        """
        try:
            logger.info("📄 Generating backtest report")
            report = self.backtester.generate_backtest_report(backtest_results)
            logger.info(f"✅ Report generated:\n{report}")
            return report
        except Exception as e:
            logger.error(f"❌ Failed to generate report: {e}")
            return ""
    
    # ========================================================================
    # EXPORT FUNCTIONALITY
    # ========================================================================
    
    def export_csv_results(
        self,
        backtest_results: Dict[str, Dict[str, Any]],
        filename: str = "group_backtest_results.csv"
    ) -> bool:
        """
        Export backtest results to CSV
        
        Args:
            backtest_results: Backtest results from all groups
            filename: Output CSV filename
        
        Returns:
            True if export successful, False otherwise
        """
        try:
            logger.info(f"💾 Exporting results to {filename}")
            result = self.backtester.export_results_csv(
                backtest_results, filename
            )
            
            if result:
                logger.info(f"✅ Results exported successfully to {filename}")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to export results: {e}")
            return False
    
    # ========================================================================
    # DETAILED STATISTICS
    # ========================================================================
    
    def get_group_statistics(
        self,
        group_name: str,
        backtest_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get detailed statistics for a specific group
        
        Args:
            group_name: Name of the group
            backtest_results: Backtest results from all groups
        
        Returns:
            Dictionary with detailed statistics
        """
        try:
            if group_name not in backtest_results:
                logger.warning(f"⚠️ Group {group_name} not found in results")
                return {}
            
            metrics = backtest_results[group_name]
            
            stats = {
                'group': group_name,
                'total_trades': metrics.get('total_trades', 0),
                'winning_trades': metrics.get('winning_trades', 0),
                'losing_trades': metrics.get('losing_trades', 0),
                'win_rate': metrics.get('win_rate', 0),
                'total_pnl': metrics.get('total_pnl', 0),
                'avg_pnl': metrics.get('avg_pnl', 0),
                'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                'max_drawdown': metrics.get('max_drawdown', 0)
            }
            
            logger.info(f"📊 Statistics for {group_name}: {stats}")
            return stats
        
        except Exception as e:
            logger.error(f"❌ Failed to get statistics: {e}")
            return {}
    
    # ========================================================================
    # PERFORMER IDENTIFICATION
    # ========================================================================
    
    def identify_best_performer(
        self,
        backtest_results: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Identify best performing group
        
        Args:
            backtest_results: Backtest results from all groups
        
        Returns:
            Name of best performing group
        """
        try:
            if not backtest_results:
                return ""
            
            best_group = max(
                backtest_results.items(),
                key=lambda x: x[1].get('win_rate', 0)
            )
            
            logger.info(
                f"🏆 Best performer: {best_group[0]} "
                f"({best_group[1].get('win_rate', 0):.1%})"
            )
            return best_group[0]
        
        except Exception as e:
            logger.error(f"❌ Failed to identify best performer: {e}")
            return ""
    
    def identify_weak_performer(
        self,
        backtest_results: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Identify weakest performing group
        
        Args:
            backtest_results: Backtest results from all groups
        
        Returns:
            Name of weakest performing group
        """
        try:
            if not backtest_results:
                return ""
            
            weak_group = min(
                backtest_results.items(),
                key=lambda x: x[1].get('win_rate', 0)
            )
            
            logger.info(
                f"📉 Weak performer: {weak_group[0]} "
                f"({weak_group[1].get('win_rate', 0):.1%})"
            )
            return weak_group[0]
        
        except Exception as e:
            logger.error(f"❌ Failed to identify weak performer: {e}")
            return ""
    
    # ========================================================================
    # PORTFOLIO METRICS
    # ========================================================================
    
    def calculate_portfolio_metrics(
        self,
        backtest_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate overall portfolio metrics
        
        Args:
            backtest_results: Backtest results from all groups
        
        Returns:
            Dictionary with portfolio-wide metrics
        """
        try:
            total_trades = sum(
                r.get('total_trades', 0) for r in backtest_results.values()
            )
            
            total_winning = sum(
                r.get('winning_trades', 0) for r in backtest_results.values()
            )
            
            total_pnl = sum(
                r.get('total_pnl', 0) for r in backtest_results.values()
            )
            
            metrics = {
                'total_trades': total_trades,
                'total_winning': total_winning,
                'total_losing': total_trades - total_winning,
                'portfolio_win_rate': (
                    total_winning / total_trades if total_trades > 0 else 0
                ),
                'total_pnl': total_pnl,
                'avg_pnl_per_group': (
                    total_pnl / len(backtest_results) if backtest_results else 0
                ),
                'num_groups': len(backtest_results)
            }
            
            logger.info(f"📊 Portfolio metrics: {metrics}")
            return metrics
        
        except Exception as e:
            logger.error(f"❌ Failed to calculate portfolio metrics: {e}")
            return {}
    
    # ========================================================================
    # FULL PIPELINE
    # ========================================================================
    
    def run_full_backtest_pipeline(
        self,
        signals: List[Dict],
        ohlcv_data: List[Dict],
        export_csv: bool = True,
        csv_filename: str = "backtest_results.csv"
    ) -> Dict[str, Any]:
        """
        Run complete backtest pipeline
        
        Executes all backtesting steps in sequence:
        1. Backtest all groups
        2. Compare performance
        3. Generate report
        4. Export CSV (optional)
        5. Calculate portfolio metrics
        6. Identify best/worst performers
        
        Args:
            signals: List of signal dictionaries
            ohlcv_data: List of OHLCV data dictionaries
            export_csv: Whether to export results to CSV
            csv_filename: CSV filename
        
        Returns:
            Dictionary with complete pipeline results
        """
        try:
            logger.info("🚀 Starting full backtest pipeline")
            
            # Step 1: Backtest all groups
            backtest_results = self.backtest_all_groups(signals, ohlcv_data)
            
            if not backtest_results:
                logger.error("❌ No backtest results generated")
                return {}
            
            # Step 2: Compare performance
            ranked = self.compare_group_performance(backtest_results)
            
            # Step 3: Generate report
            report = self.generate_performance_report(backtest_results)
            
            # Step 4: Export CSV (optional)
            csv_exported = False
            if export_csv:
                csv_exported = self.export_csv_results(
                    backtest_results, csv_filename
                )
            
            # Step 5: Calculate portfolio metrics
            portfolio_metrics = self.calculate_portfolio_metrics(backtest_results)
            
            # Step 6: Identify best/worst performers
            best_group = self.identify_best_performer(backtest_results)
            weak_group = self.identify_weak_performer(backtest_results)
            
            # Compile results
            result = {
                'status': 'completed',
                'backtest_results': backtest_results,
                'ranked': ranked,
                'report': report,
                'csv_exported': csv_exported,
                'portfolio_metrics': portfolio_metrics,
                'best_group': best_group,
                'weak_group': weak_group,
                'csv_filename': csv_filename
            }
            
            logger.info("✅ Full backtest pipeline completed successfully")
            return result
        
        except Exception as e:
            logger.error(f"❌ Failed to run backtest pipeline: {e}")
            return {'status': 'error', 'message': str(e)}

# ============================================================================
# ALIAS FOR BACKWARD COMPATIBILITY
# ============================================================================

BacktestIntegration = GroupBasedBacktestIntegration

__all__ = ['GroupBasedBacktestIntegration', 'BacktestIntegration']
