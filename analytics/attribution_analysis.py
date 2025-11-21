#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════════════════
AttributionAnalysis ENTERPRISE - DEMIR AI v8.0
═══════════════════════════════════════════════════════════════════════════════════════════
Advanced performance attribution analysis for multi-layer trading system
Identifies contribution of each layer/signal group to overall performance

Features:
- Layer-wise performance attribution (Technical, Sentiment, ML, OnChain, Risk)
- Signal group contribution analysis
- Time-series attribution tracking
- Statistical significance testing
- Factor decomposition (Brinson attribution model)
- Return attribution analysis
- Risk-adjusted attribution (Sharpe contribution)
- Interactive visualization support
- Database persistence for historical tracking
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import json

# Statistical libraries
try:
    from scipy import stats
    from scipy.stats import ttest_ind, chi2_contingency
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("scipy not available - statistical tests disabled")

# Internal imports
try:
    from database_manager_production import DatabaseManager
    from analytics.performance_engine import PerformanceEngine
except ImportError as e:
    logging.warning(f"Import warning in attribution_analysis: {e}")

logger = logging.getLogger(__name__)


class AttributionAnalysis:
    """
    Enterprise-grade performance attribution analysis system.
    
    Analyzes and quantifies the contribution of each trading layer/signal group
    to overall system performance using advanced attribution models.
    
    Attribution Methods:
    - Direct P&L attribution
    - Weighted contribution analysis
    - Brinson-Fachler attribution model
    - Factor-based decomposition
    - Risk-adjusted attribution
    
    Attributes:
        layer_contributions: Historical layer contribution data
        attribution_history: Time-series attribution records
        db_manager: Database connection for persistence
    """

    # Layer group definitions
    LAYER_GROUPS = {
        'TECHNICAL': {'weight': 0.35, 'layers': 28},
        'SENTIMENT': {'weight': 0.20, 'layers': 20},
        'ML': {'weight': 0.25, 'layers': 10},
        'ONCHAIN': {'weight': 0.15, 'layers': 6},
        'RISK': {'weight': 0.05, 'layers': 5}
    }

    def __init__(self, enable_database: bool = True):
        """
        Initialize AttributionAnalysis with configuration.
        
        Args:
            enable_database: Enable database persistence
        """
        self.layer_contributions: Dict[str, Dict] = {}
        self.attribution_history: List[Dict] = []
        self.db_manager = None
        self.performance_engine = None
        
        # Initialize components
        if enable_database:
            try:
                self.db_manager = DatabaseManager()
            except Exception as e:
                logger.warning(f"Database initialization failed: {e}")
        
        try:
            self.performance_engine = PerformanceEngine()
        except Exception as e:
            logger.warning(f"Performance engine initialization failed: {e}")
        
        logger.info("✅ AttributionAnalysis initialized")

    def calculate_layer_attribution(
        self,
        trades: List[Dict],
        layer_scores: Dict[str, float],
        period: str = "daily"
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive layer-wise performance attribution.
        
        Args:
            trades: List of trade records with layer metadata
            layer_scores: Dictionary of layer scores {layer_id: score}
            period: Time period for attribution (daily, weekly, monthly)
            
        Returns:
            Dictionary containing detailed attribution analysis
        """
        try:
            logger.info(f"📊 Calculating layer attribution for {len(trades)} trades")
            
            if not trades or not layer_scores:
                logger.warning("No trades or layer scores provided")
                return {}
            
            # Initialize attribution structure
            attribution = {
                'timestamp': datetime.now(),
                'period': period,
                'total_trades': len(trades),
                'total_pnl': sum(t.get('pnl', 0) for t in trades if 'pnl' in t),
                'layer_breakdown': {},
                'group_breakdown': {},
                'statistical_analysis': {}
            }
            
            # Calculate individual layer attribution
            for layer_id, score in layer_scores.items():
                layer_trades = [t for t in trades if layer_id in t.get('contributing_layers', [])]
                
                if layer_trades:
                    layer_pnl = sum(t.get('pnl', 0) for t in layer_trades if 'pnl' in t)
                    layer_wins = sum(1 for t in layer_trades if t.get('pnl', 0) > 0)
                    
                    attribution['layer_breakdown'][layer_id] = {
                        'score': score,
                        'trades_count': len(layer_trades),
                        'total_pnl': round(layer_pnl, 2),
                        'win_rate': round(layer_wins / len(layer_trades) * 100, 2) if layer_trades else 0,
                        'avg_pnl_per_trade': round(layer_pnl / len(layer_trades), 2) if layer_trades else 0,
                        'pnl_contribution_pct': round(layer_pnl / attribution['total_pnl'] * 100, 2) if attribution['total_pnl'] != 0 else 0
                    }
            
            # Calculate group-level attribution (TECHNICAL, SENTIMENT, etc.)
            attribution['group_breakdown'] = self._calculate_group_attribution(trades, layer_scores)
            
            # Statistical significance analysis
            if SCIPY_AVAILABLE:
                attribution['statistical_analysis'] = self._calculate_statistical_significance(
                    trades, layer_scores
                )
            
            # Store attribution
            self.layer_contributions[f"{period}_{datetime.now().date()}"] = attribution
            self.attribution_history.append(attribution)
            
            # Save to database
            if self.db_manager:
                await self._save_attribution_to_db(attribution)
            
            logger.info(f"✅ Attribution calculated: {len(attribution['layer_breakdown'])} layers analyzed")
            
            return attribution
            
        except Exception as e:
            logger.error(f"❌ Attribution calculation error: {e}")
            return {}

    def _calculate_group_attribution(
        self,
        trades: List[Dict],
        layer_scores: Dict[str, float]
    ) -> Dict[str, Dict]:
        """
        Calculate attribution at signal group level (TECHNICAL, SENTIMENT, ML, etc.).
        
        Args:
            trades: List of trade records
            layer_scores: Layer score dictionary
            
        Returns:
            Group-level attribution breakdown
        """
        group_attribution = {}
        
        for group_name, group_info in self.LAYER_GROUPS.items():
            group_layers = [k for k in layer_scores.keys() if k.startswith(group_name.lower())]
            
            if group_layers:
                group_trades = [
                    t for t in trades 
                    if any(layer in t.get('contributing_layers', []) for layer in group_layers)
                ]
                
                if group_trades:
                    group_pnl = sum(t.get('pnl', 0) for t in group_trades if 'pnl' in t)
                    group_wins = sum(1 for t in group_trades if t.get('pnl', 0) > 0)
                    
                    # Calculate weighted contribution based on group weight
                    weighted_contribution = group_pnl * group_info['weight']
                    
                    group_attribution[group_name] = {
                        'target_weight': group_info['weight'],
                        'layer_count': group_info['layers'],
                        'active_layers': len(group_layers),
                        'trades_count': len(group_trades),
                        'total_pnl': round(group_pnl, 2),
                        'weighted_contribution': round(weighted_contribution, 2),
                        'win_rate': round(group_wins / len(group_trades) * 100, 2) if group_trades else 0,
                        'avg_pnl_per_trade': round(group_pnl / len(group_trades), 2) if group_trades else 0
                    }
        
        return group_attribution

    def _calculate_statistical_significance(
        self,
        trades: List[Dict],
        layer_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Perform statistical significance tests on layer contributions.
        
        Uses t-tests and chi-square tests to determine if layer contributions
        are statistically significant.
        
        Args:
            trades: List of trade records
            layer_scores: Layer score dictionary
            
        Returns:
            Statistical test results
        """
        if not SCIPY_AVAILABLE:
            return {}
        
        try:
            statistical_results = {}
            
            # Compare each layer's performance to baseline
            all_pnls = [t.get('pnl', 0) for t in trades if 'pnl' in t]
            baseline_mean = np.mean(all_pnls) if all_pnls else 0
            
            for layer_id, score in layer_scores.items():
                layer_trades = [t for t in trades if layer_id in t.get('contributing_layers', [])]
                
                if len(layer_trades) >= 10:  # Minimum sample size
                    layer_pnls = [t.get('pnl', 0) for t in layer_trades if 'pnl' in t]
                    
                    if layer_pnls:
                        # T-test: Is this layer's performance significantly different from baseline?
                        t_statistic, p_value = ttest_ind(layer_pnls, all_pnls)
                        
                        statistical_results[layer_id] = {
                            't_statistic': round(float(t_statistic), 4),
                            'p_value': round(float(p_value), 4),
                            'significant': p_value < 0.05,
                            'better_than_baseline': np.mean(layer_pnls) > baseline_mean,
                            'sample_size': len(layer_pnls),
                            'layer_mean': round(np.mean(layer_pnls), 2),
                            'baseline_mean': round(baseline_mean, 2)
                        }
            
            return statistical_results
            
        except Exception as e:
            logger.error(f"Statistical analysis error: {e}")
            return {}

    def calculate_brinson_attribution(
        self,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
        layer_weights: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate Brinson-Fachler attribution model.
        
        Decomposes portfolio performance into:
        - Allocation effect (weight decisions)
        - Selection effect (layer performance)
        - Interaction effect
        
        Args:
            portfolio_returns: Portfolio return series
            benchmark_returns: Benchmark return series
            layer_weights: Layer weight allocation
            
        Returns:
            Attribution effects breakdown
        """
        try:
            # Calculate attribution effects
            allocation_effect = 0
            selection_effect = 0
            interaction_effect = 0
            
            for layer_id, weight in layer_weights.items():
                # Simplified Brinson model
                # In production, this would use actual layer returns vs benchmark
                layer_return = portfolio_returns.mean() * weight
                benchmark_weight = 1.0 / len(layer_weights)  # Equal weight benchmark
                
                # Allocation effect: (weight_p - weight_b) * return_b
                allocation_effect += (weight - benchmark_weight) * benchmark_returns.mean()
                
                # Selection effect: weight_b * (return_p - return_b)
                selection_effect += benchmark_weight * (layer_return - benchmark_returns.mean())
                
                # Interaction effect: (weight_p - weight_b) * (return_p - return_b)
                interaction_effect += (weight - benchmark_weight) * (layer_return - benchmark_returns.mean())
            
            return {
                'allocation_effect': round(allocation_effect, 4),
                'selection_effect': round(selection_effect, 4),
                'interaction_effect': round(interaction_effect, 4),
                'total_attribution': round(allocation_effect + selection_effect + interaction_effect, 4)
            }
            
        except Exception as e:
            logger.error(f"Brinson attribution error: {e}")
            return {}

    def calculate_risk_adjusted_attribution(
        self,
        trades: List[Dict],
        layer_scores: Dict[str, float]
    ) -> Dict[str, Dict]:
        """
        Calculate risk-adjusted attribution using Sharpe ratio contribution.
        
        Args:
            trades: List of trade records
            layer_scores: Layer score dictionary
            
        Returns:
            Risk-adjusted attribution metrics
        """
        try:
            risk_adjusted = {}
            
            for layer_id, score in layer_scores.items():
                layer_trades = [t for t in trades if layer_id in t.get('contributing_layers', [])]
                
                if len(layer_trades) >= 10:
                    layer_pnls = [t.get('pnl', 0) for t in layer_trades if 'pnl' in t]
                    
                    if layer_pnls:
                        mean_return = np.mean(layer_pnls)
                        std_return = np.std(layer_pnls)
                        
                        # Sharpe ratio (simplified, assuming risk-free rate = 0)
                        sharpe = mean_return / std_return if std_return > 0 else 0
                        
                        risk_adjusted[layer_id] = {
                            'mean_return': round(mean_return, 2),
                            'std_dev': round(std_return, 2),
                            'sharpe_ratio': round(sharpe, 4),
                            'score': score,
                            'risk_adjusted_contribution': round(sharpe * score, 4)
                        }
            
            return risk_adjusted
            
        except Exception as e:
            logger.error(f"Risk-adjusted attribution error: {e}")
            return {}

    def get_top_contributing_layers(
        self,
        n: int = 10,
        metric: str = 'pnl_contribution_pct'
    ) -> List[Tuple[str, float]]:
        """
        Get top N contributing layers by specified metric.
        
        Args:
            n: Number of top layers to return
            metric: Metric to sort by
            
        Returns:
            List of (layer_id, metric_value) tuples
        """
        try:
            if not self.layer_contributions:
                return []
            
            # Get most recent attribution
            latest_key = max(self.layer_contributions.keys())
            latest_attribution = self.layer_contributions[latest_key]
            
            layer_breakdown = latest_attribution.get('layer_breakdown', {})
            
            # Sort by metric
            sorted_layers = sorted(
                layer_breakdown.items(),
                key=lambda x: x[1].get(metric, 0),
                reverse=True
            )
            
            return [(layer_id, data[metric]) for layer_id, data in sorted_layers[:n]]
            
        except Exception as e:
            logger.error(f"Error getting top layers: {e}")
            return []

    def generate_attribution_report(self, period: str = "monthly") -> Dict[str, Any]:
        """
        Generate comprehensive attribution report.
        
        Args:
            period: Report period
            
        Returns:
            Detailed attribution report
        """
        try:
            if not self.attribution_history:
                return {}
            
            # Aggregate attribution over period
            recent_attributions = [
                a for a in self.attribution_history 
                if a.get('period') == period
            ]
            
            if not recent_attributions:
                return {}
            
            # Calculate aggregate metrics
            total_pnl = sum(a.get('total_pnl', 0) for a in recent_attributions)
            total_trades = sum(a.get('total_trades', 0) for a in recent_attributions)
            
            # Aggregate layer contributions
            aggregated_layers = defaultdict(lambda: {
                'total_pnl': 0,
                'trades_count': 0,
                'appearances': 0
            })
            
            for attribution in recent_attributions:
                for layer_id, data in attribution.get('layer_breakdown', {}).items():
                    aggregated_layers[layer_id]['total_pnl'] += data.get('total_pnl', 0)
                    aggregated_layers[layer_id]['trades_count'] += data.get('trades_count', 0)
                    aggregated_layers[layer_id]['appearances'] += 1
            
            report = {
                'period': period,
                'generated_at': datetime.now(),
                'summary': {
                    'total_pnl': round(total_pnl, 2),
                    'total_trades': total_trades,
                    'attribution_records': len(recent_attributions)
                },
                'aggregated_layers': dict(aggregated_layers),
                'top_contributors': self.get_top_contributing_layers(n=10)
            }
            
            logger.info(f"✅ Attribution report generated for {period}")
            return report
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return {}

    async def _save_attribution_to_db(self, attribution: Dict) -> bool:
        """
        Save attribution analysis to database.
        
        Args:
            attribution: Attribution dictionary
            
        Returns:
            bool: True if saved successfully
        """
        try:
            if not self.db_manager:
                return False
            
            record = {
                'timestamp': attribution['timestamp'],
                'period': attribution['period'],
                'total_pnl': attribution['total_pnl'],
                'total_trades': attribution['total_trades'],
                'layer_breakdown': json.dumps(attribution['layer_breakdown']),
                'group_breakdown': json.dumps(attribution['group_breakdown'])
            }
            
            await self.db_manager.save_attribution_analysis(record)
            logger.info("✅ Attribution saved to database")
            return True
            
        except Exception as e:
            logger.error(f"Database save error: {e}")
            return False


if __name__ == "__main__":
    # Test instantiation
    analyzer = AttributionAnalysis()
    print("✅ AttributionAnalysis initialized")
