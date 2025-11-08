"""
🔥 PHASE 20 + 22: LIQUIDATION CASCADE + ANOMALY DETECTION - CRITICAL
============================================================================
Real-time Market Anomalies: Liquidations, Flash Crash, Black Swans
Date: November 8, 2025
Priority: 🔴 CRITICAL - Alerts = +80% system coverage

PURPOSE:
- Real-time liquidation monitoring
- Cascade prediction
- Flash crash detection
- Market anomaly identification
============================================================================
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class LiquidationDetector:
    """Real-time Liquidation Monitoring & Cascade Prediction"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.liquidation_history = []
        self.cascade_threshold = 10_000_000  # $10M cascade threshold
        
    def monitor_liquidations(self, 
                            exchange: str,  # Binance, Bybit, Deribit
                            symbol: str,
                            recent_liquidations: List[Dict]) -> Dict:
        """Monitor real-time liquidations"""
        
        if not recent_liquidations:
            return {'status': 'no_liquidations'}
        
        total_liquidation_vol = sum([l['volume'] for l in recent_liquidations])
        avg_liquidation_size = np.mean([l['volume'] for l in recent_liquidations])
        
        # Detect cascade
        cascade_detected = total_liquidation_vol > self.cascade_threshold
        
        analysis = {
            'exchange': exchange,
            'symbol': symbol,
            'total_liquidation_volume': total_liquidation_vol,
            'liquidation_count': len(recent_liquidations),
            'average_size': avg_liquidation_size,
            'cascade_detected': cascade_detected,
            'cascade_severity': self._get_cascade_severity(total_liquidation_vol),
            'top_liquidations': sorted(recent_liquidations, key=lambda x: x['volume'], reverse=True)[:5]
        }
        
        self.liquidation_history.append({
            'timestamp': datetime.now(),
            'data': analysis
        })
        
        return analysis
    
    def predict_cascade_momentum(self) -> Dict:
        """Predict if cascade will continue"""
        
        if len(self.liquidation_history) < 2:
            return {'prediction': 'insufficient_data'}
        
        # Get last 2 cascades
        recent = self.liquidation_history[-2:]
        
        vol_change = recent[1]['data']['total_liquidation_volume'] - recent[0]['data']['total_liquidation_volume']
        vol_change_pct = (vol_change / max(recent[0]['data']['total_liquidation_volume'], 1)) * 100
        
        if vol_change_pct > 20:
            momentum = 'ACCELERATING'
        elif vol_change_pct < -20:
            momentum = 'DECELERATING'
        else:
            momentum = 'STABLE'
        
        return {
            'cascade_momentum': momentum,
            'volume_change_pct': vol_change_pct,
            'prediction': 'CONTINUE' if momentum == 'ACCELERATING' else 'END'
        }
    
    def _get_cascade_severity(self, volume: float) -> str:
        """Classify cascade severity"""
        
        if volume > 50_000_000:
            return 'EXTREME'
        elif volume > 20_000_000:
            return 'CRITICAL'
        elif volume > 10_000_000:
            return 'HIGH'
        elif volume > 5_000_000:
            return 'MEDIUM'
        else:
            return 'LOW'

class FlashCrashDetector:
    """Flash Crash & Extreme Price Movement Detection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.price_history = []
        
    def detect_flash_crash(self,
                          current_price: float,
                          price_1m_ago: float,
                          volume_1m: float,
                          normal_volume: float) -> Dict:
        """Detect flash crash patterns"""
        
        # Calculate drawdown
        drawdown_pct = ((current_price - price_1m_ago) / price_1m_ago) * 100
        
        # Volume spike
        volume_spike = volume_1m / max(normal_volume, 1)
        
        flash_crash = False
        severity = 'LOW'
        
        if abs(drawdown_pct) > 5 and volume_spike > 2:
            flash_crash = True
            severity = 'EXTREME'
        elif abs(drawdown_pct) > 3 and volume_spike > 1.5:
            flash_crash = True
            severity = 'HIGH'
        elif abs(drawdown_pct) > 2 and volume_spike > 1.2:
            flash_crash = True
            severity = 'MEDIUM'
        
        detection = {
            'flash_crash_detected': flash_crash,
            'drawdown_pct': drawdown_pct,
            'volume_spike': volume_spike,
            'severity': severity,
            'recommendation': 'LIQUIDATE_SMALL' if flash_crash else 'NORMAL'
        }
        
        self.price_history.append({
            'timestamp': datetime.now(),
            'price': current_price,
            'flash_crash_detected': flash_crash
        })
        
        return detection
    
    def predict_recovery(self) -> Dict:
        """Predict recovery from flash crash"""
        
        if len(self.price_history) < 5:
            return {'prediction': 'insufficient_data'}
        
        recent = self.price_history[-5:]
        
        # Check recovery pattern
        recovering = any([p['flash_crash_detected'] for p in recent])
        
        if recovering:
            return {
                'recovery_expected': True,
                'timeframe': '5-30 minutes',
                'entry_opportunity': 'BUY_DIP'
            }
        
        return {
            'recovery_expected': False,
            'warning': 'Price may continue downward'
        }

class AnomalyDetectionEngine:
    """Comprehensive Market Anomaly Detection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.liquidation = LiquidationDetector()
        self.flash_crash = FlashCrashDetector()
        
    def detect_anomalies(self,
                        current_price: float,
                        volume_1m: float,
                        volume_avg: float,
                        recent_liquidations: List[Dict],
                        exchange_flows: Dict,
                        whale_activity: List[Dict]) -> Dict:
        """Comprehensive anomaly detection"""
        
        anomalies = []
        severity_scores = []
        
        # 1. Volume Spike
        volume_spike = volume_1m / max(volume_avg, 1)
        if volume_spike > 2:
            anomalies.append({
                'type': 'VOLUME_SPIKE',
                'severity': 'HIGH' if volume_spike > 5 else 'MEDIUM',
                'ratio': volume_spike
            })
            severity_scores.append(70 if volume_spike > 5 else 50)
        
        # 2. Liquidation Cascade
        liq_analysis = self.liquidation.monitor_liquidations('Binance', 'BTCUSDT', recent_liquidations)
        if liq_analysis.get('cascade_detected'):
            anomalies.append({
                'type': 'LIQUIDATION_CASCADE',
                'severity': liq_analysis['cascade_severity'],
                'volume': liq_analysis['total_liquidation_volume']
            })
            severity_scores.append(85 if liq_analysis['cascade_severity'] == 'EXTREME' else 60)
        
        # 3. Flash Crash
        flash_crash_analysis = self.flash_crash.detect_flash_crash(current_price, current_price * 0.98, volume_1m, volume_avg)
        if flash_crash_analysis['flash_crash_detected']:
            anomalies.append({
                'type': 'FLASH_CRASH',
                'severity': flash_crash_analysis['severity'],
                'drawdown': flash_crash_analysis['drawdown_pct']
            })
            severity_scores.append(90)
        
        # 4. Whale Activity
        whale_count = len(whale_activity)
        if whale_count > 5:
            anomalies.append({
                'type': 'WHALE_ACTIVITY',
                'severity': 'HIGH' if whale_count > 10 else 'MEDIUM',
                'count': whale_count
            })
            severity_scores.append(65)
        
        # 5. Exchange Flow Anomaly
        large_outflow = exchange_flows.get('large_outflow', False)
        if large_outflow:
            anomalies.append({
                'type': 'EXCHANGE_OUTFLOW',
                'severity': 'MEDIUM',
                'implication': 'Potential accumulation'
            })
            severity_scores.append(55)
        
        overall_severity = np.mean(severity_scores) if severity_scores else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'anomalies_detected': len(anomalies),
            'anomalies': anomalies,
            'overall_severity': overall_severity,
            'market_condition': self._classify_market(overall_severity),
            'recommendation': self._generate_recommendation(anomalies)
        }
    
    def _classify_market(self, severity: float) -> str:
        """Classify market condition"""
        if severity > 80:
            return 'PANIC'
        elif severity > 60:
            return 'UNSTABLE'
        elif severity > 40:
            return 'TURBULENT'
        else:
            return 'NORMAL'
    
    def _generate_recommendation(self, anomalies: List[Dict]) -> str:
        """Generate trading recommendation"""
        
        if not anomalies:
            return 'NORMAL_TRADING'
        
        critical = [a for a in anomalies if a['severity'] in ['EXTREME', 'CRITICAL', 'HIGH']]
        
        if len(critical) > 2:
            return 'REDUCE_POSITION'
        elif critical:
            return 'TIGHTEN_STOPS'
        else:
            return 'MONITOR'

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'LiquidationDetector',
    'FlashCrashDetector',
    'AnomalyDetectionEngine'
]
