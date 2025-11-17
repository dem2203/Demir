"""
DEMIR AI BOT - Group Signal Backtest
Backtest individual signal groups
Performance analysis and ranking per group
Production-grade backtesting engine
"""

import logging
from typing import Dict, Any, List, Tuple
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class GroupSignalBacktester:
    """Backtest individual signal groups."""
    
    def __init__(self):
        """Initialize backtester."""
        self.group_results = {}
        logger.info("GroupSignalBacktester initialized")
    
    def backtest_technical_signals(
        self,
        signals: List[Dict],
        ohlcv_data: List[Dict]
    ) -> Dict[str, Any]:
        """Backtest technical signals only."""
        
        trades = []
        logger.info("Starting technical signals backtest")
        
        for signal in signals:
            if signal.get('group') != 'technical':
                continue
            
            symbol = signal.get('symbol')
            entry_price = signal.get('entry_price', 0)
            tp1_price = signal.get('tp1', 0)
            tp2_price = signal.get('tp2', 0)
            sl_price = signal.get('sl', 0)
            direction = signal.get('direction', '')
            timestamp = signal.get('timestamp')
            
            if not entry_price or not tp1_price:
                continue
            
            # Calculate PnL
            if direction == 'LONG':
                pnl_tp1 = (tp1_price - entry_price) * 100
                pnl_tp2 = (tp2_price - entry_price) * 100 if tp2_price else 0
            elif direction == 'SHORT':
                pnl_tp1 = (entry_price - tp1_price) * 100
                pnl_tp2 = (entry_price - tp2_price) * 100 if tp2_price else 0
            else:
                continue
            
            trades.append({
                'symbol': symbol,
                'entry': entry_price,
                'tp1': tp1_price,
                'tp2': tp2_price,
                'sl': sl_price,
                'pnl_tp1': pnl_tp1,
                'pnl_tp2': pnl_tp2,
                'direction': direction,
                'timestamp': timestamp
            })
        
        if not trades:
            logger.warning("No technical trades found for backtest")
            return {
                'group': 'technical',
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_pnl': 0.0
            }
        
        # Calculate metrics
        winning = len([t for t in trades if t['pnl_tp1'] > 0])
        losing = len(trades) - winning
        total_pnl = sum(t['pnl_tp1'] for t in trades)
        avg_pnl = total_pnl / len(trades) if trades else 0
        max_pnl = max([t['pnl_tp1'] for t in trades])
        min_pnl = min([t['pnl_tp1'] for t in trades])
        
        # Calculate Sharpe ratio
        pnl_list = [t['pnl_tp1'] for t in trades]
        std_dev = np.std(pnl_list) if pnl_list else 1.0
        sharpe = (avg_pnl / std_dev) if std_dev > 0 else 0
        
        # Calculate max drawdown
        cumulative_pnl = np.cumsum(pnl_list)
        running_max = np.maximum.accumulate(cumulative_pnl)
        drawdown = (cumulative_pnl - running_max) / running_max
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
        
        metrics = {
            'group': 'technical',
            'total_trades': len(trades),
            'winning_trades': winning,
            'losing_trades': losing,
            'win_rate': winning / len(trades) if trades else 0,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'max_pnl': max_pnl,
            'min_pnl': min_pnl,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown
        }
        
        logger.info(
            f"Technical backtest: {metrics['total_trades']} trades, "
            f"{metrics['win_rate']:.1%} win rate, {metrics['avg_pnl']:.2f}% avg PnL"
        )
        
        return metrics
    
    def backtest_sentiment_signals(
        self,
        signals: List[Dict],
        ohlcv_data: List[Dict]
    ) -> Dict[str, Any]:
        """Backtest sentiment signals only."""
        
        trades = []
        logger.info("Starting sentiment signals backtest")
        
        for signal in signals:
            if signal.get('group') != 'sentiment':
                continue
            
            entry_price = signal.get('entry_price', 0)
            tp1_price = signal.get('tp1', 0)
            direction = signal.get('direction', '')
            
            if not entry_price or not tp1_price:
                continue
            
            if direction == 'LONG':
                pnl = (tp1_price - entry_price) * 100
            elif direction == 'SHORT':
                pnl = (entry_price - tp1_price) * 100
            else:
                continue
            
            trades.append({'pnl': pnl})
        
        if not trades:
            logger.warning("No sentiment trades found for backtest")
            return {
                'group': 'sentiment',
                'total_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_pnl': 0.0
            }
        
        winning = len([t for t in trades if t['pnl'] > 0])
        total_pnl = sum(t['pnl'] for t in trades)
        
        metrics = {
            'group': 'sentiment',
            'total_trades': len(trades),
            'winning_trades': winning,
            'losing_trades': len(trades) - winning,
            'win_rate': winning / len(trades),
            'total_pnl': total_pnl,
            'avg_pnl': total_pnl / len(trades)
        }
        
        logger.info(
            f"Sentiment backtest: {metrics['total_trades']} trades, "
            f"{metrics['win_rate']:.1%} win rate"
        )
        
        return metrics
    
    def backtest_ml_signals(
        self,
        signals: List[Dict],
        ohlcv_data: List[Dict]
    ) -> Dict[str, Any]:
        """Backtest ML signals only."""
        
        trades = []
        logger.info("Starting ML signals backtest")
        
        for signal in signals:
            if signal.get('group') != 'ml':
                continue
            
            entry_price = signal.get('entry_price', 0)
            tp1_price = signal.get('tp1', 0)
            direction = signal.get('direction', '')
            
            if not entry_price or not tp1_price:
                continue
            
            if direction == 'LONG':
                pnl = (tp1_price - entry_price) * 100
            elif direction == 'SHORT':
                pnl = (entry_price - tp1_price) * 100
            else:
                continue
            
            trades.append({'pnl': pnl})
        
        if not trades:
            logger.warning("No ML trades found for backtest")
            return {
                'group': 'ml',
                'total_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_pnl': 0.0
            }
        
        winning = len([t for t in trades if t['pnl'] > 0])
        total_pnl = sum(t['pnl'] for t in trades)
        
        metrics = {
            'group': 'ml',
            'total_trades': len(trades),
            'winning_trades': winning,
            'losing_trades': len(trades) - winning,
            'win_rate': winning / len(trades),
            'total_pnl': total_pnl,
            'avg_pnl': total_pnl / len(trades)
        }
        
        logger.info(
            f"ML backtest: {metrics['total_trades']} trades, "
            f"{metrics['win_rate']:.1%} win rate"
        )
        
        return metrics
    
    def backtest_onchain_signals(
        self,
        signals: List[Dict],
        ohlcv_data: List[Dict]
    ) -> Dict[str, Any]:
        """Backtest OnChain signals only."""
        
        trades = []
        logger.info("Starting OnChain signals backtest")
        
        for signal in signals:
            if signal.get('group') != 'onchain':
                continue
            
            entry_price = signal.get('entry_price', 0)
            tp1_price = signal.get('tp1', 0)
            direction = signal.get('direction', '')
            
            if not entry_price or not tp1_price:
                continue
            
            if direction == 'LONG':
                pnl = (tp1_price - entry_price) * 100
            elif direction == 'SHORT':
                pnl = (entry_price - tp1_price) * 100
            else:
                continue
            
            trades.append({'pnl': pnl})
        
        if not trades:
            logger.warning("No OnChain trades found for backtest")
            return {
                'group': 'onchain',
                'total_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0
            }
        
        winning = len([t for t in trades if t['pnl'] > 0])
        total_pnl = sum(t['pnl'] for t in trades)
        
        metrics = {
            'group': 'onchain',
            'total_trades': len(trades),
            'winning_trades': winning,
            'losing_trades': len(trades) - winning,
            'win_rate': winning / len(trades),
            'total_pnl': total_pnl,
            'avg_pnl': total_pnl / len(trades)
        }
        
        logger.info(f"OnChain backtest: {metrics['total_trades']} trades")
        
        return metrics
    
    def compare_group_performance(
        self,
        all_results: Dict[str, Dict]
    ) -> Dict[str, Dict]:
        """Compare performance across all groups."""
        
        # Rank groups by win rate
        ranked = sorted(
            all_results.items(),
            key=lambda x: x[1].get('win_rate', 0),
            reverse=True
        )
        
        logger.info("="*60)
        logger.info("GROUP PERFORMANCE RANKING")
        logger.info("="*60)
        
        for i, (group, metrics) in enumerate(ranked, 1):
            total = metrics.get('total_trades', 0)
            win_rate = metrics.get('win_rate', 0)
            pnl = metrics.get('total_pnl', 0)
            avg_pnl = metrics.get('avg_pnl', 0)
            
            logger.info(
                f"{i}. {group.upper():15} | "
                f"Win Rate: {win_rate:6.1%} | "
                f"Trades: {total:5} | "
                f"Total PnL: {pnl:8.2f}% | "
                f"Avg PnL: {avg_pnl:6.2f}%"
            )
        
        logger.info("="*60)
        
        return dict(ranked)
    
    def generate_backtest_report(
        self,
        all_results: Dict[str, Dict]
    ) -> str:
        """Generate comprehensive backtest report."""
        
        report = "\n"
        report += "="*80 + "\n"
        report += "GROUP-BASED SIGNAL BACKTEST REPORT\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "="*80 + "\n\n"
        
        # Overall statistics
        total_trades = sum(r.get('total_trades', 0) for r in all_results.values())
        total_winning = sum(r.get('winning_trades', 0) for r in all_results.values())
        total_pnl = sum(r.get('total_pnl', 0) for r in all_results.values())
        
        report += f"OVERALL STATISTICS\n"
        report += f"Total Trades: {total_trades}\n"
        report += f"Total Winning: {total_winning}\n"
        report += f"Overall Win Rate: {(total_winning/total_trades*100):.1f}% if total_trades > 0\n"
        report += f"Total PnL: {total_pnl:.2f}%\n\n"
        
        # Per-group details
        report += "DETAILED GROUP PERFORMANCE\n"
        report += "-"*80 + "\n"
        
        for group, metrics in sorted(all_results.items(), key=lambda x: x[1].get('win_rate', 0), reverse=True):
            report += f"\n{group.upper()}\n"
            report += f"  Trades: {metrics.get('total_trades', 0)}\n"
            report += f"  Win Rate: {metrics.get('win_rate', 0):.1%}\n"
            report += f"  Total PnL: {metrics.get('total_pnl', 0):.2f}%\n"
            report += f"  Avg PnL: {metrics.get('avg_pnl', 0):.2f}%\n"
            if 'sharpe_ratio' in metrics:
                report += f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}\n"
            if 'max_drawdown' in metrics:
                report += f"  Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%\n"
        
        report += "\n" + "="*80 + "\n"
        
        return report
    
    def export_results_csv(
        self,
        all_results: Dict[str, Dict],
        filename: str = "group_backtest_results.csv"
    ) -> bool:
        """Export backtest results to CSV."""
        try:
            import csv
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Group', 'Total Trades', 'Winning', 'Losing', 
                    'Win Rate %', 'Total PnL %', 'Avg PnL %', 
                    'Sharpe Ratio', 'Max Drawdown %'
                ])
                
                for group, metrics in sorted(all_results.items(), key=lambda x: x[1].get('win_rate', 0), reverse=True):
                    writer.writerow([
                        group,
                        metrics.get('total_trades', 0),
                        metrics.get('winning_trades', 0),
                        metrics.get('losing_trades', 0),
                        f"{metrics.get('win_rate', 0)*100:.2f}",
                        f"{metrics.get('total_pnl', 0):.2f}",
                        f"{metrics.get('avg_pnl', 0):.2f}",
                        f"{metrics.get('sharpe_ratio', 0):.2f}" if 'sharpe_ratio' in metrics else "N/A",
                        f"{metrics.get('max_drawdown', 0)*100:.2f}" if 'max_drawdown' in metrics else "N/A"
                    ])
            
            logger.info(f"Backtest results exported to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to export results: {e}")
            return False
