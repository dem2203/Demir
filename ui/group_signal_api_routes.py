"""
DEMIR AI BOT - Group Signal API Routes
Separate endpoints for each signal group
Professional REST API architecture
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class GroupSignalAPIRoutes:
    """Define group-based API routes."""
    
    ROUTES = {
        '/api/signals/technical': {
            'method': 'GET',
            'description': 'Get technical analysis signals (28 layers)',
            'query_params': {
                'symbol': 'str',
                'limit': 'int (optional, default 100)'
            },
            'response': {
                'group': 'technical',
                'symbol': 'BTCUSDT',
                'direction': 'LONG',
                'strength': 0.82,
                'confidence': 0.88,
                'active_layers': 12,
                'top_layers': ['RSI', 'MACD', 'Bollinger'],
                'timestamp': 1700000000
            }
        },
        
        '/api/signals/sentiment': {
            'method': 'GET',
            'description': 'Get sentiment analysis signals (20 layers)',
            'query_params': {
                'symbol': 'str'
            },
            'response': {
                'group': 'sentiment',
                'symbol': 'BTCUSDT',
                'direction': 'NEUTRAL',
                'strength': 0.52,
                'confidence': 0.65,
                'active_layers': 8,
                'sources': ['NewsSentiment', 'FearGreedIndex'],
                'timestamp': 1700000000
            }
        },
        
        '/api/signals/ml': {
            'method': 'GET',
            'description': 'Get machine learning signals (10 layers)',
            'query_params': {
                'symbol': 'str'
            },
            'response': {
                'group': 'ml',
                'symbol': 'BTCUSDT',
                'direction': 'LONG',
                'strength': 0.79,
                'confidence': 0.85,
                'active_layers': 5,
                'models': ['XGBoost', 'LSTM'],
                'timestamp': 1700000000
            }
        },
        
        '/api/signals/onchain': {
            'method': 'GET',
            'description': 'Get on-chain analysis signals (6 layers)',
            'query_params': {
                'symbol': 'str'
            },
            'response': {
                'group': 'onchain',
                'symbol': 'BTCUSDT',
                'direction': 'LONG',
                'strength': 0.71,
                'confidence': 0.78,
                'active_layers': 4,
                'indicators': ['WhaleAlert', 'NetworkActivity'],
                'timestamp': 1700000000
            }
        },
        
        '/api/signals/risk': {
            'method': 'GET',
            'description': 'Get risk assessment (5 layers, NOT buy/sell)',
            'query_params': {
                'symbol': 'str'
            },
            'response': {
                'group': 'risk',
                'symbol': 'BTCUSDT',
                'volatility_score': 0.68,
                'max_loss_exposure': '2.5%',
                'kelly_fraction': 0.15,
                'active_layers': 5,
                'timestamp': 1700000000
            }
        },
        
        '/api/signals/latest': {
            'method': 'GET',
            'description': 'Get all group signals + consensus',
            'query_params': {
                'symbol': 'str',
                'include_conflicts': 'bool (optional, default true)'
            },
            'response': {
                'timestamp': 1700000000,
                'symbol': 'BTCUSDT',
                'groups': {
                    'technical': {},
                    'sentiment': {},
                    'ml': {},
                    'onchain': {},
                    'risk': {}
                },
                'consensus': {
                    'direction': 'LONG',
                    'strength': 0.76,
                    'confidence': 0.82,
                    'conflict_detected': False,
                    'active_groups': 5
                }
            }
        },
        
        '/api/signals/consensus': {
            'method': 'GET',
            'description': 'Get consensus signal only (optional)',
            'query_params': {
                'symbol': 'str'
            },
            'response': {
                'symbol': 'BTCUSDT',
                'direction': 'LONG',
                'strength': 0.76,
                'confidence': 0.82,
                'conflict_detected': False,
                'active_groups': 5,
                'timestamp': 1700000000
            }
        },
        
        '/api/analytics/group-performance': {
            'method': 'GET',
            'description': 'Get group-based performance metrics',
            'query_params': {
                'days': 'int (optional, default 30)',
                'group': 'str (optional, filter specific group)'
            },
            'response': {
                'period_days': 30,
                'groups': {
                    'technical': {
                        'total_signals': 1250,
                        'winning': 775,
                        'win_rate': 0.62,
                        'avg_pnl': '+1.5%',
                        'sharpe_ratio': 1.45,
                        'max_drawdown': -8.5
                    },
                    'ml': {
                        'total_signals': 1100,
                        'winning': 782,
                        'win_rate': 0.71,
                        'avg_pnl': '+2.1%',
                        'sharpe_ratio': 1.82,
                        'max_drawdown': -6.2
                    },
                    'sentiment': {
                        'total_signals': 800,
                        'winning': 384,
                        'win_rate': 0.48,
                        'avg_pnl': '+0.8%',
                        'sharpe_ratio': 0.95,
                        'max_drawdown': -12.1
                    }
                }
            }
        },
        
        '/api/signals/conflicts': {
            'method': 'GET',
            'description': 'Get current group conflicts',
            'query_params': {
                'symbol': 'str'
            },
            'response': {
                'symbol': 'BTCUSDT',
                'has_conflict': False,
                'conflicts': [],
                'conflict_details': {
                    'long_groups': [],
                    'short_groups': [],
                    'neutral_groups': ['sentiment']
                },
                'timestamp': 1700000000,
                'recommendation': 'PAPER_TRADING_SKIP'
            }
        }
    }
    
    @staticmethod
    def get_all_routes() -> Dict[str, Dict[str, Any]]:
        """Get all API routes."""
        logger.info(f"Returning {len(GroupSignalAPIRoutes.ROUTES)} API routes")
        return GroupSignalAPIRoutes.ROUTES
    
    @staticmethod
    def get_route(path: str) -> Dict[str, Any]:
        """Get specific route definition."""
        if path not in GroupSignalAPIRoutes.ROUTES:
            logger.warning(f"Route not found: {path}")
            return {}
        return GroupSignalAPIRoutes.ROUTES[path]
    
    @staticmethod
    def get_documentation() -> str:
        """Get complete API documentation."""
        docs = "# DEMIR AI BOT - Group Signal API Documentation\n\n"
        docs += "## Base URL\n`https://your-app.up.railway.app`\n\n"
        docs += "## Authentication\nAll endpoints are public (read-only)\n\n"
        docs += "## Endpoints\n\n"
        
        for path, definition in sorted(GroupSignalAPIRoutes.ROUTES.items()):
            docs += f"### {definition['method']} {path}\n"
            docs += f"**Description:** {definition['description']}\n\n"
            
            if 'query_params' in definition:
                docs += "**Query Parameters:**\n"
                for param, param_type in definition['query_params'].items():
                    docs += f"- `{param}` ({param_type})\n"
                docs += "\n"
            
            docs += "**Response:**\n```json\n"
            import json
            docs += json.dumps(definition.get('response', {}), indent=2)
            docs += "\n```\n\n"
        
        return docs
    
    @staticmethod
    def validate_query_params(path: str, params: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate query parameters for a route."""
        if path not in GroupSignalAPIRoutes.ROUTES:
            return False, f"Route {path} not found"
        
        route = GroupSignalAPIRoutes.ROUTES[path]
        required_params = route.get('query_params', {})
        
        # Check required parameters
        for param, param_type in required_params.items():
            if 'optional' not in param_type and param not in params:
                return False, f"Missing required parameter: {param}"
        
        logger.info(f"Query parameters validated for {path}")
        return True, "OK"
    
    @staticmethod
    def get_endpoint_count() -> int:
        """Get total number of endpoints."""
        return len(GroupSignalAPIRoutes.ROUTES)
    
    @staticmethod
    def get_endpoints_by_category() -> Dict[str, List[str]]:
        """Get endpoints grouped by category."""
        categories = {
            'signals': ['/api/signals/technical', '/api/signals/sentiment', '/api/signals/ml', '/api/signals/onchain', '/api/signals/risk'],
            'combined': ['/api/signals/latest', '/api/signals/consensus'],
            'analytics': ['/api/analytics/group-performance'],
            'diagnostics': ['/api/signals/conflicts']
        }
        return categories


def create_group_signal_routes():
    """Factory function to create routes instance."""
    return GroupSignalAPIRoutes()
