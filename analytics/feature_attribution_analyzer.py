"""
=============================================================================
DEMIR AI v28+ - FEATURE ATTRIBUTION & INTERPRETABILITY ANALYZER
=============================================================================
Location: /analytics/ klasörü | Phase: Analysis Layer
=============================================================================
"""

import logging
import numpy as np
from typing import Dict, List
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FeatureContribution:
    """Özellik katkısı"""
    feature_name: str
    contribution_percent: float
    impact_on_pnl: float
    is_positive: bool


class FeatureAttributionAnalyzer:
    """
    Özellik Atıflandırma Analizi (SHAP-like)
    
    Hangi feature'ın ne kadar kâr/zarar yarattığını anlamak
    """
    
    def __init__(self):
        self.feature_contributions = {}
        self.trade_history = []
    
    def analyze_trade_contribution(self, trade: Dict) -> Dict[str, float]:
        """Trade için her feature'ın katkısını hesapla"""
        contributions = {
            "technical_signals": 0,
            "onchain_data": 0,
            "sentiment": 0,
            "anomaly_detection": 0,
            "market_regime": 0
        }
        
        # Her feature'ın confidence'ına göre katkı
        if "technical_confidence" in trade:
            contributions["technical_signals"] = trade["technical_confidence"] * 0.25
        
        if "onchain_confidence" in trade:
            contributions["onchain_data"] = trade["onchain_confidence"] * 0.20
        
        if "sentiment_score" in trade:
            contributions["sentiment"] = trade["sentiment_score"] * 0.15
        
        if "anomaly_detected" in trade:
            contributions["anomaly_detection"] = 30 if trade["anomaly_detected"] else 0
        
        if "regime_score" in trade:
            contributions["market_regime"] = trade["regime_score"] * 0.20
        
        # Normalize
        total = sum(contributions.values())
        if total > 0:
            contributions = {k: v/total*100 for k, v in contributions.items()}
        
        return contributions
    
    def get_feature_importance_ranking(self, trades: List[Dict]) -> List[FeatureContribution]:
        """Feature'ları kâra göre sırala"""
        rankings = {}
        
        for feature in ["technical_signals", "onchain_data", "sentiment", "anomaly_detection", "market_regime"]:
            pnls = []
            
            for trade in trades:
                contrib = self.analyze_trade_contribution(trade)
                if feature in contrib and trade.get('pnl', 0) != 0:
                    # Weight PnL by feature contribution %
                    weighted_pnl = trade['pnl'] * (contrib[feature] / 100)
                    pnls.append(weighted_pnl)
            
            avg_contribution = np.mean(pnls) if pnls else 0
            rankings[feature] = avg_contribution
        
        # Sort by impact
        sorted_features = sorted(rankings.items(), key=lambda x: abs(x[1]), reverse=True)
        
        result = []
        total_impact = sum(abs(v) for k, v in sorted_features)
        
        for feature_name, impact in sorted_features:
            contrib = FeatureContribution(
                feature_name=feature_name,
                contribution_percent=abs(impact) / total_impact * 100 if total_impact > 0 else 0,
                impact_on_pnl=impact,
                is_positive=impact > 0
            )
            result.append(contrib)
        
        return result
    
    def generate_report(self, trades: List[Dict]) -> str:
        """Feature atıflandırma raporu oluştur"""
        rankings = self.get_feature_importance_ranking(trades)
        
        report = """
╔════════════════════════════════════════════════════════════╗
║        FEATURE ATTRIBUTION REPORT | Özellik Analizi       ║
╚════════════════════════════════════════════════════════════╝

📊 Feature Importance Rankings:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        for i, contrib in enumerate(rankings, 1):
            status = "✅ Positive" if contrib.is_positive else "❌ Negative"
            report += f"{i}. {contrib.feature_name}\n"
            report += f"   Contribution: {contrib.contribution_percent:.1f}%\n"
            report += f"   Avg PnL Impact: ${contrib.impact_on_pnl:,.2f}\n"
            report += f"   Status: {status}\n\n"
        
        return report


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    analyzer = FeatureAttributionAnalyzer()
    
    # Mock trades
    trades = [
        {
            "pnl": 150,
            "technical_confidence": 85,
            "onchain_confidence": 70,
            "sentiment_score": 65,
            "anomaly_detected": False,
            "regime_score": 80
        },
        {
            "pnl": -50,
            "technical_confidence": 60,
            "onchain_confidence": 50,
            "sentiment_score": 40,
            "anomaly_detected": True,
            "regime_score": 55
        }
    ]
    
    report = analyzer.generate_report(trades)
    print(report)
