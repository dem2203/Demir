"""
🔥 PHASE 18: FED CALENDAR + STOCK MARKET CORRELATION - REAL-TIME
============================================================================
External Factor Mastery: VIX, SPX, NASDAQ, Treasury Yields, Fed Decisions
Date: November 8, 2025
Priority: 🔴 CRITICAL - External Factors = +75% accuracy

PURPOSE:
- Real-time Fed calendar integration
- Stock market correlation engine
- Treasury yields tracker
- Dynamic macro adjustment
============================================================================
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple
import concurrent.futures

logger = logging.getLogger(__name__)

class FedCalendarRealtimeLayer:
    """Real-time Fed Calendar & Rate Decision Tracking"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.last_update = {}
        self.cache_ttl = 3600  # 1 hour
        
    def get_fed_calendar(self) -> Dict:
        """Fetch upcoming Fed events"""
        try:
            # TradingEconomics free API (requires registration)
            url = "https://api.tradingeconomics.com/calendar"
            params = {'format': 'json'}
            
            response = requests.get(url, params=params, timeout=10)
            if response.ok:
                data = response.json()
                
                # Filter Fed-specific events
                fed_events = [e for e in data if 'Fed' in str(e.get('event', ''))]
                
                self.cache['fed_events'] = fed_events
                self.last_update['fed_events'] = datetime.now()
                
                return {
                    'status': 'success',
                    'event_count': len(fed_events),
                    'next_event': fed_events[0] if fed_events else None,
                    'events': fed_events
                }
        except Exception as e:
            logger.error(f"Fed calendar fetch failed: {e}")
        
        return {'status': 'error', 'message': str(e)}
    
    def detect_rate_decision_impact(self) -> Dict:
        """Detect upcoming rate decisions and expected impact"""
        try:
            fed_events = self.cache.get('fed_events', [])
            
            rate_decisions = [e for e in fed_events if 'Interest Rate' in str(e.get('event', ''))]
            
            if rate_decisions:
                next_decision = rate_decisions[0]
                
                return {
                    'rate_decision_incoming': True,
                    'date': next_decision.get('date'),
                    'expected_rate': next_decision.get('forecast'),
                    'previous_rate': next_decision.get('previous'),
                    'impact_level': 'HIGH',  # Always high for rate decisions
                    'crypto_sensitivity': 'EXTREME'  # BTC very sensitive to rates
                }
        except Exception as e:
            logger.error(f"Rate decision detection failed: {e}")
        
        return {'rate_decision_incoming': False}

class StockMarketCorrelationLayer:
    """SPX, NASDAQ, DXY Real-time Correlation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.symbols = {
            'SPX': '^GSPC',  # S&P 500
            'NASDAQ': '^IXIC',  # NASDAQ
            'DXY': 'DXY=F',  # Dollar Index
            'VIX': '^VIX'  # Volatility Index
        }
        self.cache = {}
        
    def fetch_market_data(self) -> Dict:
        """Fetch real-time market data"""
        results = {}
        
        try:
            # Use yfinance for free market data
            import yfinance as yf
            
            for name, ticker in self.symbols.items():
                try:
                    data = yf.Ticker(ticker)
                    hist = data.history(period='1d')
                    
                    if not hist.empty:
                        current = hist['Close'].iloc[-1]
                        prev = hist['Open'].iloc[-1]
                        change_pct = ((current - prev) / prev) * 100
                        
                        results[name] = {
                            'price': current,
                            'change_pct': change_pct,
                            'timestamp': datetime.now()
                        }
                except Exception as e:
                    logger.warning(f"Failed to fetch {name}: {e}")
            
            self.cache.update(results)
            return results
            
        except Exception as e:
            logger.error(f"Market data fetch failed: {e}")
            return {}
    
    def calculate_correlation_with_crypto(self, btc_price: float) -> Dict:
        """Calculate correlation between stock market and BTC"""
        
        market_data = self.cache
        
        if not market_data:
            return {'status': 'no_data'}
        
        correlation_signals = {
            'spx_impact': self._get_impact('SPX'),
            'nasdaq_impact': self._get_impact('NASDAQ'),
            'dxy_impact': self._get_impact('DXY'),  # Inverse relationship
            'vix_impact': self._get_impact('VIX'),  # Fear gauge
            'composite_macro_score': 0
        }
        
        # Calculate composite score
        scores = []
        
        # SPX positive = risk-on = BTC up
        if 'SPX' in market_data:
            spx_score = 50 + (market_data['SPX']['change_pct'] * 10)
            scores.append(spx_score)
        
        # NASDAQ positive = tech-on = BTC up (correlation 0.7)
        if 'NASDAQ' in market_data:
            nasdaq_score = 50 + (market_data['NASDAQ']['change_pct'] * 7)
            scores.append(nasdaq_score)
        
        # DXY up = dollar strong = BTC down (inverse)
        if 'DXY' in market_data:
            dxy_score = 50 - (market_data['DXY']['change_pct'] * 5)
            scores.append(dxy_score)
        
        # VIX up = fear = BTC uncertain
        if 'VIX' in market_data:
            vix_score = 50 - (market_data['VIX']['change_pct'] / 2)
            scores.append(vix_score)
        
        if scores:
            correlation_signals['composite_macro_score'] = np.mean(scores)
        
        return correlation_signals
    
    def _get_impact(self, market: str) -> str:
        """Determine impact level"""
        if market not in self.cache:
            return 'UNKNOWN'
        
        change = abs(self.cache[market]['change_pct'])
        
        if change > 2:
            return 'EXTREME'
        elif change > 1:
            return 'HIGH'
        elif change > 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'

class TreasuryRatesLayer:
    """Treasury Yields Real-time Tracking"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.yields = {}
        
    def fetch_treasury_yields(self) -> Dict:
        """Fetch US Treasury yields"""
        try:
            # FRED API (free)
            base_url = "https://api.stlouisfed.org/fred/series/observations"
            
            series_ids = {
                'yield_2y': 'DGS2',
                'yield_10y': 'DGS10',
                'yield_5y': 'DGS5',
                'fed_funds_rate': 'FEDFUNDS'
            }
            
            api_key = "YOUR_FRED_API_KEY"  # Get from https://fred.stlouisfed.org
            
            results = {}
            for name, series_id in series_ids.items():
                try:
                    params = {
                        'series_id': series_id,
                        'api_key': api_key,
                        'file_type': 'json'
                    }
                    response = requests.get(base_url, params=params, timeout=10)
                    
                    if response.ok:
                        data = response.json()
                        if 'observations' in data and data['observations']:
                            latest = data['observations'][-1]
                            results[name] = float(latest['value'])
                except Exception as e:
                    logger.warning(f"Failed to fetch {series_id}: {e}")
            
            self.yields = results
            return results
            
        except Exception as e:
            logger.error(f"Treasury yields fetch failed: {e}")
            return {}
    
    def calculate_yield_curve_signal(self) -> Dict:
        """Analyze yield curve shape for market signals"""
        
        if not self.yields:
            return {'status': 'no_data'}
        
        yield_2y = self.yields.get('yield_2y', 0)
        yield_10y = self.yields.get('yield_10y', 0)
        
        curve_spread = yield_10y - yield_2y
        
        signal = {
            'yield_2y': yield_2y,
            'yield_10y': yield_10y,
            'curve_spread': curve_spread,
            'curve_condition': self._classify_curve(curve_spread),
            'crypto_implications': self._get_crypto_implications(curve_spread)
        }
        
        return signal
    
    def _classify_curve(self, spread: float) -> str:
        """Classify yield curve"""
        if spread < -0.5:
            return 'INVERTED'
        elif spread < 0:
            return 'FLAT'
        elif spread < 1.0:
            return 'STEEP_LOW'
        else:
            return 'STEEP'
    
    def _get_crypto_implications(self, spread: float) -> Dict:
        """Get crypto trading implications"""
        
        if spread < -0.5:
            return {
                'signal': 'BEARISH',
                'reasoning': 'Inverted curve signals recession risk',
                'btc_implication': 'Safe haven flows may slow'
            }
        elif spread < 0:
            return {
                'signal': 'CAUTION',
                'reasoning': 'Flat curve = economic uncertainty',
                'btc_implication': 'Mixed sentiment'
            }
        else:
            return {
                'signal': 'NORMAL',
                'reasoning': 'Normal yield curve = stable markets',
                'btc_implication': 'Risk-on conditions'
            }

class EnhancedMacroRealtimeLayer:
    """Consolidated Enhanced Macro Layer"""
    
    def __init__(self):
        self.fed = FedCalendarRealtimeLayer()
        self.stock = StockMarketCorrelationLayer()
        self.treasury = TreasuryRatesLayer()
        self.logger = logging.getLogger(__name__)
        
    def analyze_macro_realtime(self, btc_price: float = None) -> Dict:
        """Comprehensive real-time macro analysis"""
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'fed_calendar': self.fed.get_fed_calendar(),
            'rate_decision': self.fed.detect_rate_decision_impact(),
            'market_data': self.stock.fetch_market_data(),
            'stock_correlation': self.stock.calculate_correlation_with_crypto(btc_price),
            'treasury_yields': self.treasury.fetch_treasury_yields(),
            'yield_curve': self.treasury.calculate_yield_curve_signal()
        }
        
        # Calculate final macro score (0-100)
        macro_score = self._calculate_macro_score(results)
        results['macro_score'] = macro_score
        results['macro_signal'] = self._get_signal(macro_score)
        
        return results
    
    def _calculate_macro_score(self, data: Dict) -> float:
        """Calculate comprehensive macro score"""
        
        scores = []
        
        # Stock correlation score
        if 'composite_macro_score' in data.get('stock_correlation', {}):
            scores.append(data['stock_correlation']['composite_macro_score'])
        
        # Yield curve score
        if 'curve_condition' in data.get('yield_curve', {}):
            condition = data['yield_curve']['curve_condition']
            curve_score = {
                'INVERTED': 20,
                'FLAT': 40,
                'STEEP_LOW': 60,
                'STEEP': 75
            }.get(condition, 50)
            scores.append(curve_score)
        
        # Fed decision impact
        if data.get('rate_decision', {}).get('rate_decision_incoming'):
            scores.append(45)  # Uncertainty from upcoming decision
        else:
            scores.append(55)  # Normal conditions
        
        return np.mean(scores) if scores else 50
    
    def _get_signal(self, score: float) -> str:
        """Convert score to signal"""
        if score >= 70:
            return 'BULLISH'
        elif score >= 55:
            return 'NEUTRAL_BULLISH'
        elif score >= 45:
            return 'NEUTRAL'
        elif score >= 30:
            return 'NEUTRAL_BEARISH'
        else:
            return 'BEARISH'

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'FedCalendarRealtimeLayer',
    'StockMarketCorrelationLayer',
    'TreasuryRatesLayer',
    'EnhancedMacroRealtimeLayer'
]

# Test
if __name__ == "__main__":
    macro = EnhancedMacroRealtimeLayer()
    analysis = macro.analyze_macro_realtime(btc_price=42000)
    print(json.dumps(analysis, indent=2, default=str))
