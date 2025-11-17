"""
DEMIR AI BOT - API Routes Definition
REST API endpoints for frontend integration
Signal serving, metrics, management endpoints
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class APIRoutes:
    """Define REST API routes for DEMIR AI."""

    ROUTES = {
        # Signal Endpoints
        '/api/signals/latest': {
            'method': 'GET',
            'description': 'Get latest signals for all coins',
            'response': {'signals': []}
        },
        '/api/signals/{symbol}': {
            'method': 'GET',
            'description': 'Get signal for specific symbol',
            'response': {'signal': {}}
        },

        # Market Data
        '/api/market/{symbol}': {
            'method': 'GET',
            'description': 'Get current market data',
            'response': {'price': 0, 'volume': 0, 'change_24h': 0}
        },

        # Coin Management
        '/api/coins': {
            'method': 'GET',
            'description': 'Get all tracked coins',
            'response': {'coins': ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']}
        },
        '/api/coins': {
            'method': 'POST',
            'description': 'Add new coin to tracking',
            'request': {'symbol': 'SOLUSDT'},
            'response': {'status': 'ok', 'symbol': 'SOLUSDT'}
        },
        '/api/coins/{symbol}': {
            'method': 'DELETE',
            'description': 'Remove coin from tracking',
            'response': {'status': 'ok'}
        },

        # Analytics & Performance
        '/api/analytics/performance': {
            'method': 'GET',
            'description': 'Get bot performance metrics',
            'response': {
                'total_signals': 0,
                'winning_signals': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0
            }
        },
        '/api/analytics/layer-performance': {
            'method': 'GET',
            'description': 'Get layer performance metrics',
            'response': {'layers': {}}
        },

        # Health & Status
        '/api/health': {
            'method': 'GET',
            'description': 'Health check endpoint',
            'response': {'status': 'healthy', 'uptime': 0}
        },
        '/api/status': {
            'method': 'GET',
            'description': 'Get system status',
            'response': {
                'running': True,
                'layer_count': 71,
                'active_coins': 3
            }
        },

        # Configuration
        '/api/config': {
            'method': 'GET',
            'description': 'Get current configuration',
            'response': {}
        },

        # Backtest
        '/api/backtest': {
            'method': 'POST',
            'description': 'Run backtest on historical data',
            'request': {
                'start_date': '2023-01-01',
                'end_date': '2024-12-31'
            },
            'response': {'metrics': {}}
        },

        # Trading Operations
        '/api/trades/history': {
            'method': 'GET',
            'description': 'Get trade history',
            'response': {'trades': []}
        },
        '/api/positions': {
            'method': 'GET',
            'description': 'Get open positions',
            'response': {'positions': []}
        }
    }

    @staticmethod
    def get_all_routes() -> Dict[str, Dict[str, Any]]:
        """Get all API routes."""
        return APIRoutes.ROUTES

    @staticmethod
    def get_route(path: str) -> Dict[str, Any]:
        """Get specific route definition."""
        return APIRoutes.ROUTES.get(path, {})

    @staticmethod
    def get_documentation() -> str:
        """Get API documentation in markdown."""
        docs = "# DEMIR AI BOT - API Documentation\n\n"

        for path, definition in APIRoutes.ROUTES.items():
            docs += f"## {path}\n"
            docs += f"**Method:** {definition.get('method')}\n"
            docs += f"**Description:** {definition.get('description')}\n\n"

        return docs
