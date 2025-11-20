# main.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 DEMIR AI v7.0 - ENTERPRISE MASTER ORCHESTRATOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ULTRA PROFESSIONAL AI TRADING SYSTEM - NO COMPROMISES

ARCHITECTURE:
    ✅ 50+ Layer Signal Generation (Technical, Sentiment, ML, On-Chain, Risk)
    ✅ Real-time WebSocket + REST API Hybrid
    ✅ Multi-Exchange Price Verification (Binance, Bybit, Coinbase)
    ✅ PostgreSQL with Connection Pooling
    ✅ Circuit Breaker Pattern for API Calls
    ✅ Distributed Task Queue (Celery-like)
    ✅ Advanced Monitoring & Alerting
    ✅ AI Self-Learning System
    ✅ Advisory Mode (NO AUTO-TRADING)
    ✅ Production-Grade Error Handling
    ✅ Zero-Downtime Deployment Ready

DATA INTEGRITY:
    ❌ ZERO Mock Data
    ❌ ZERO Fake Data
    ❌ ZERO Test Data
    ❌ ZERO Fallback Data
    ❌ ZERO Hardcoded Data
    ✅ 100% Real Exchange Data Only

DEPLOYMENT:
    - Railway Production Environment
    - GitHub CI/CD Integration
    - Docker Container Support
    - Kubernetes Ready
    - Auto-Scaling Enabled

AUTHOR: DEMIR AI Research Team
VERSION: 7.0
DATE: 2025-11-20
LICENSE: Proprietary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ============================================================================
# IMPORTS
# ============================================================================

import os
import sys
import time
import json
import signal
import asyncio
import logging
import threading
import traceback
import requests  # For Telegram and HTTP requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from collections import defaultdict, deque
from functools import wraps
import queue

# Third-party
import pytz
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Load environment variables
load_dotenv()

# Project imports
from config import (
    ADVISORY_MODE,
    DEFAULT_TRACKED_SYMBOLS,
    OPPORTUNITY_THRESHOLDS,
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    DATABASE_URL,
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID
)

# Advanced AI Components
from advanced_ai.signal_engine_integration import SignalGroupOrchestrator
from advanced_ai.opportunity_engine import OpportunityEngine, TradePlan
from advanced_ai.advisor_core import AdvisorCore
from advanced_ai.regime_detector import MarketRegimeDetector
from advanced_ai.layer_optimizer import LayerOptimizer
try:
    from advanced_ai.causal_reasoning import CausalReasoningEngine
    print("✅ CausalReasoningEngine loaded")
except (ImportError, ModuleNotFoundError, SyntaxError) as e:
    print(f"⚠️  CausalReasoningEngine skipped: {e}")
    CausalReasoningEngine = None

# Analytics Components
from analytics.advisor_opportunity_service import AdvisorOpportunityService
from analytics.performance_engine import PerformanceEngine
try:
    from analytics.backtest_engine_production import BacktestEngine
    print("✅ BacktestEngine loaded")
except (ImportError, ModuleNotFoundError, SyntaxError) as e:
    print(f"⚠️  BacktestEngine skipped: {e}")
    BacktestEngine = None
from analytics.trade_analyzer import TradeAnalyzer
from analytics.report_generator import ReportGenerator

# Integration Components
from integrations.binance_websocket_v3 import BinanceWebSocketManager
from integrations.multi_exchange_api import MultiExchangeDataFetcher
try:
    from integrations.market_intelligence import MarketIntelligenceEngine
    MarketIntelligenceAggregator = MarketIntelligenceEngine  # Alias for compatibility
    print("✅ MarketIntelligenceEngine loaded")
except (ImportError, ModuleNotFoundError, SyntaxError) as e:
    print(f"⚠️  MarketIntelligenceEngine skipped: {e}")
    MarketIntelligenceEngine = None
    MarketIntelligenceAggregator = None
from integrations.sentiment_aggregator import SentimentAggregator
try:
    from integrations.macro_data_aggregator import MacroAggregator
    MacroDataAggregator = MacroAggregator  # Alias for compatibility
    print("✅ MacroAggregator loaded")
except (ImportError, ModuleNotFoundError, SyntaxError) as e:
    print(f"⚠️  MacroAggregator skipped: {e}")
    MacroAggregator = None
    MacroDataAggregator = None

# Utility Components
from utils.logger_setup import setup_logger
from utils.real_data_verifier_pro import RealDataVerifier
from utils.signal_validator_comprehensive import SignalValidator
from utils.signal_processor_advanced import AdvancedSignalProcessor
from utils.circuit_breaker import CircuitBreaker
from utils.retry_manager import RetryManager
from utils.redis_cache import RedisCache
from utils.health_monitor import HealthMonitor

# UI Components
from ui.data_fetcher_realtime import RealtimeDataFetcher
from ui.telegram_tradeplan_notifier import TelegramTradePlanNotifier
# ✅ FIXED: Import actual Flask app components instead of non-existent EnterpriseDashboard
from ui.dashboard_backend import app as dashboard_app, socketio as dashboard_socketio, initialize_services as initialize_dashboard

# Database
from database_manager_production import DatabaseManager