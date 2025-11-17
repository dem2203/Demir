"""
DEMIR AI BOT - API Routes Definition (UPDATED)
Group-based REST API endpoints
9 professional endpoints for group signals
Production-grade Flask/FastAPI routes
"""

import logging
from typing import Dict, Any, List, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class GroupBasedAPIRoutes:
    """Define and manage group-based API routes."""
    
    def __init__(self, app=None):
        """Initialize API routes."""
        self.app = app
        self.routes_registered = False
        logger.info("GroupBasedAPIRoutes initialized")
    
    def register_routes(self, app):
        """Register all group-based routes with Flask/FastAPI app."""
        self.app = app
        
        # Import group signal API
        try:
            from ui.group_signal_api_routes import GroupSignalAPIRoutes
            self.api_routes = GroupSignalAPIRoutes()
            logger.info("GroupSignalAPIRoutes imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import GroupSignalAPIRoutes: {e}")
            return False
        
        # Register all endpoints
        self._register_technical_endpoint()
        self._register_sentiment_endpoint()
        self._register_ml_endpoint()
        self._register_onchain_endpoint()
        self._register_risk_endpoint()
        self._register_latest_endpoint()
        self._register_consensus_endpoint()
        self._register_performance_endpoint()
        self._register_conflicts_endpoint()
        
        self.routes_registered = True
        logger.info("All group-based routes registered successfully")
        
        return True
    
    def _register_technical_endpoint(self):
        """GET /api/signals/technical - Technical signals only"""
        
        @self.app.route('/api/signals/technical', methods=['GET'])
        def get_technical_signals():
            """Get technical analysis signals (28 layers)."""
            try:
                symbol = self._get_request_arg('symbol', required=True)
                limit = self._get_request_arg('limit', default=100, type=int)
                
                logger.info(f"Retrieving technical signals for {symbol}")
                
                # Get from database
                signals = self._get_signals_from_db('technical', symbol, limit)
                
                response = {
                    'status': 'success',
                    'group': 'technical',
                    'symbol': symbol,
                    'signals': signals,
                    'count': len(signals)
                }
                
                return response, 200
            
            except Exception as e:
                logger.error(f"Error in technical endpoint: {e}")
                return {'status': 'error', 'message': str(e)}, 500
    
    def _register_sentiment_endpoint(self):
        """GET /api/signals/sentiment - Sentiment signals only"""
        
        @self.app.route('/api/signals/sentiment', methods=['GET'])
        def get_sentiment_signals():
            """Get sentiment analysis signals (20 layers)."""
            try:
                symbol = self._get_request_arg('symbol', required=True)
                
                logger.info(f"Retrieving sentiment signals for {symbol}")
                
                signals = self._get_signals_from_db('sentiment', symbol)
                
                response = {
                    'status': 'success',
                    'group': 'sentiment',
                    'symbol': symbol,
                    'signals': signals,
                    'count': len(signals)
                }
                
                return response, 200
            
            except Exception as e:
                logger.error(f"Error in sentiment endpoint: {e}")
                return {'status': 'error', 'message': str(e)}, 500
    
    def _register_ml_endpoint(self):
        """GET /api/signals/ml - ML signals only"""
        
        @self.app.route('/api/signals/ml', methods=['GET'])
        def get_ml_signals():
            """Get machine learning signals (10 layers)."""
            try:
                symbol = self._get_request_arg('symbol', required=True)
                
                logger.info(f"Retrieving ML signals for {symbol}")
                
                signals = self._get_signals_from_db('ml', symbol)
                
                response = {
                    'status': 'success',
                    'group': 'ml',
                    'symbol': symbol,
                    'signals': signals,
                    'count': len(signals)
                }
                
                return response, 200
            
            except Exception as e:
                logger.error(f"Error in ML endpoint: {e}")
                return {'status': 'error', 'message': str(e)}, 500
    
    def _register_onchain_endpoint(self):
        """GET /api/signals/onchain - OnChain signals only"""
        
        @self.app.route('/api/signals/onchain', methods=['GET'])
        def get_onchain_signals():
            """Get on-chain analysis signals (6 layers)."""
            try:
                symbol = self._get_request_arg('symbol', required=True)
                
                logger.info(f"Retrieving OnChain signals for {symbol}")
                
                signals = self._get_signals_from_db('onchain', symbol)
                
                response = {
                    'status': 'success',
                    'group': 'onchain',
                    'symbol': symbol,
                    'signals': signals,
                    'count': len(signals)
                }
                
                return response, 200
            
            except Exception as e:
                logger.error(f"Error in OnChain endpoint: {e}")
                return {'status': 'error', 'message': str(e)}, 500
    
    def _register_risk_endpoint(self):
        """GET /api/signals/risk - Risk assessment"""
        
        @self.app.route('/api/signals/risk', methods=['GET'])
        def get_risk_assessment():
            """Get risk assessment (5 layers, NOT buy/sell signal)."""
            try:
                symbol = self._get_request_arg('symbol', required=True)
                
                logger.info(f"Retrieving risk assessment for {symbol}")
                
                risk_data = self._get_risk_from_db(symbol)
                
                response = {
                    'status': 'success',
                    'group': 'risk',
                    'symbol': symbol,
                    'assessment': risk_data
                }
                
                return response, 200
            
            except Exception as e:
                logger.error(f"Error in risk endpoint: {e}")
                return {'status': 'error', 'message': str(e)}, 500
    
    def _register_latest_endpoint(self):
        """GET /api/signals/latest - All groups + consensus"""
        
        @self.app.route('/api/signals/latest', methods=['GET'])
        def get_all_signals():
            """Get all group signals + consensus."""
            try:
                symbol = self._get_request_arg('symbol', required=True)
                include_conflicts = self._get_request_arg('include_conflicts', default=True, type=bool)
                
                logger.info(f"Retrieving all signals for {symbol}")
                
                response = {
                    'status': 'success',
                    'symbol': symbol,
                    'groups': {
                        'technical': self._get_signals_from_db('technical', symbol, limit=1),
                        'sentiment': self._get_signals_from_db('sentiment', symbol, limit=1),
                        'ml': self._get_signals_from_db('ml', symbol, limit=1),
                        'onchain': self._get_signals_from_db('onchain', symbol, limit=1),
                        'risk': self._get_risk_from_db(symbol)
                    },
                    'consensus': self._get_consensus_from_db(symbol)
                }
                
                if include_conflicts:
                    response['conflicts'] = self._get_conflicts_from_db(symbol)
                
                return response, 200
            
            except Exception as e:
                logger.error(f"Error in latest endpoint: {e}")
                return {'status': 'error', 'message': str(e)}, 500
    
    def _register_consensus_endpoint(self):
        """GET /api/signals/consensus - Consensus signal only"""
        
        @self.app.route('/api/signals/consensus', methods=['GET'])
        def get_consensus():
            """Get consensus signal only."""
            try:
                symbol = self._get_request_arg('symbol', required=True)
                
                logger.info(f"Retrieving consensus for {symbol}")
                
                consensus = self._get_consensus_from_db(symbol)
                
                response = {
                    'status': 'success',
                    'symbol': symbol,
                    'consensus': consensus
                }
                
                return response, 200
            
            except Exception as e:
                logger.error(f"Error in consensus endpoint: {e}")
                return {'status': 'error', 'message': str(e)}, 500
    
    def _register_performance_endpoint(self):
        """GET /api/analytics/group-performance - Group performance metrics"""
        
        @self.app.route('/api/analytics/group-performance', methods=['GET'])
        def get_group_performance():
            """Get group-based performance metrics."""
            try:
                days = self._get_request_arg('days', default=30, type=int)
                group = self._get_request_arg('group', default=None)
                
                logger.info(f"Retrieving group performance metrics (days={days})")
                
                metrics = self._get_performance_metrics(days, group)
                
                response = {
                    'status': 'success',
                    'period_days': days,
                    'metrics': metrics
                }
                
                return response, 200
            
            except Exception as e:
                logger.error(f"Error in performance endpoint: {e}")
                return {'status': 'error', 'message': str(e)}, 500
    
    def _register_conflicts_endpoint(self):
        """GET /api/signals/conflicts - Group conflicts"""
        
        @self.app.route('/api/signals/conflicts', methods=['GET'])
        def get_conflicts():
            """Get current group conflicts."""
            try:
                symbol = self._get_request_arg('symbol', required=True)
                
                logger.info(f"Retrieving conflicts for {symbol}")
                
                conflicts = self._get_conflicts_from_db(symbol)
                
                response = {
                    'status': 'success',
                    'symbol': symbol,
                    'has_conflict': len(conflicts) > 0,
                    'conflicts': conflicts
                }
                
                return response, 200
            
            except Exception as e:
                logger.error(f"Error in conflicts endpoint: {e}")
                return {'status': 'error', 'message': str(e)}, 500
    
    def _get_request_arg(self, name: str, required: bool = False, default: Any = None, type: type = str):
        """Get request argument safely."""
        try:
            from flask import request
            value = request.args.get(name)
            
            if value is None:
                if required:
                    raise ValueError(f"Required parameter '{name}' not provided")
                return default
            
            if type and type != str:
                return type(value)
            
            return value
        except Exception as e:
            logger.error(f"Error getting request arg '{name}': {e}")
            if required:
                raise
            return default
    
    def _get_signals_from_db(self, group: str, symbol: str, limit: int = 100) -> List[Dict]:
        """Get signals from database."""
        try:
            # Placeholder: Actual DB query implementation
            logger.debug(f"Fetching {group} signals for {symbol} from database")
            return []
        except Exception as e:
            logger.error(f"Error fetching {group} signals: {e}")
            return []
    
    def _get_risk_from_db(self, symbol: str) -> Dict[str, Any]:
        """Get risk assessment from database."""
        try:
            logger.debug(f"Fetching risk assessment for {symbol} from database")
            return {}
        except Exception as e:
            logger.error(f"Error fetching risk assessment: {e}")
            return {}
    
    def _get_consensus_from_db(self, symbol: str) -> Dict[str, Any]:
        """Get consensus from database."""
        try:
            logger.debug(f"Fetching consensus for {symbol} from database")
            return {}
        except Exception as e:
            logger.error(f"Error fetching consensus: {e}")
            return {}
    
    def _get_conflicts_from_db(self, symbol: str) -> List[str]:
        """Get conflicts from database."""
        try:
            logger.debug(f"Fetching conflicts for {symbol} from database")
            return []
        except Exception as e:
            logger.error(f"Error fetching conflicts: {e}")
            return []
    
    def _get_performance_metrics(self, days: int = 30, group: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics from database."""
        try:
            logger.debug(f"Fetching performance metrics (days={days}, group={group})")
            return {}
        except Exception as e:
            logger.error(f"Error fetching performance metrics: {e}")
            return {}
    
    @staticmethod
    def get_api_documentation() -> str:
        """Get API documentation."""
        doc = """
# DEMIR AI BOT - Group-Based Signal API

## Base URL
`https://your-app.up.railway.app`

## Endpoints (9 Total)

### 1. GET /api/signals/technical
Get technical analysis signals (28 layers)
**Query Params**: symbol (required), limit (optional, default 100)

### 2. GET /api/signals/sentiment
Get sentiment analysis signals (20 layers)
**Query Params**: symbol (required)

### 3. GET /api/signals/ml
Get machine learning signals (10 layers)
**Query Params**: symbol (required)

### 4. GET /api/signals/onchain
Get on-chain analysis signals (6 layers)
**Query Params**: symbol (required)

### 5. GET /api/signals/risk
Get risk assessment (5 layers)
**Query Params**: symbol (required)

### 6. GET /api/signals/latest
Get all groups + consensus
**Query Params**: symbol (required), include_conflicts (optional, default true)

### 7. GET /api/signals/consensus
Get consensus signal only
**Query Params**: symbol (required)

### 8. GET /api/analytics/group-performance
Get group performance metrics
**Query Params**: days (optional, default 30), group (optional)

### 9. GET /api/signals/conflicts
Get current group conflicts
**Query Params**: symbol (required)

## Example Requests

### Get Technical Signals
```
GET /api/signals/technical?symbol=BTCUSDT&limit=100
```

### Get All Signals
```
GET /api/signals/latest?symbol=BTCUSDT&include_conflicts=true
```

### Get Performance
```
GET /api/analytics/group-performance?days=30
```
"""
        return doc
