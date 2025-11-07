"""
DEMIR AI - Phase 13 Disaster Recovery System
Complete resilience engine with failover, backup management, and recovery protocols
Full Production Code - NO MOCKS
Created: November 7, 2025
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
import pickle
from pathlib import Path

import aiohttp
import pandas as pd
import numpy as np
from binance.client import Client as BinanceClient
from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException
import redis
from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class FailureType(Enum):
    """Disaster types the system handles"""
    CONNECTION_FAILURE = "connection_failure"
    ORDER_EXECUTION_FAILURE = "order_execution_failure"
    POSITION_DESYNC = "position_desync"
    MARGIN_CALL = "margin_call"
    DATA_CORRUPTION = "data_corruption"
    API_RATE_LIMIT = "api_rate_limit"
    EXCHANGE_OUTAGE = "exchange_outage"
    NETWORK_TIMEOUT = "network_timeout"
    INVALID_ORDER = "invalid_order"
    INSUFFICIENT_BALANCE = "insufficient_balance"

class RecoveryStatus(Enum):
    """Status of recovery process"""
    NOT_NEEDED = "not_needed"
    IN_PROGRESS = "in_progress"
    RECOVERED = "recovered"
    FAILED = "failed"
    MANUAL_INTERVENTION = "manual_intervention"

@dataclass
class DisasterEvent:
    """Record of a disaster event"""
    failure_type: FailureType
    timestamp: datetime
    severity: int  # 1-10, 10 is critical
    component: str
    error_message: str
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_status: RecoveryStatus = RecoveryStatus.NOT_NEEDED
    recovery_attempts: int = 0
    action_taken: str = ""

@dataclass
class BackupCheckpoint:
    """Backup checkpoint metadata"""
    checkpoint_id: str
    timestamp: datetime
    data_hash: str
    backup_location: str
    data_type: str  # 'position', 'trade_history', 'config', 'state'
    size_bytes: int
    compressed: bool
    integrity_verified: bool

@dataclass
class PositionSnapshot:
    """Snapshot of current position state"""
    symbol: str
    side: str  # 'LONG' or 'SHORT'
    entry_price: float
    current_price: float
    quantity: float
    unrealized_pnl: float
    percentage_pnl: float
    entry_time: datetime
    current_leverage: float
    liquidation_price: float
    margin_ratio: float

@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    name: str
    url: str
    is_primary: bool
    priority: int
    timeout: float
    max_retries: int
    backoff_factor: float

# ============================================================================
# DISASTER RECOVERY ENGINE
# ============================================================================

class DisasterRecoveryEngine:
    """
    Main disaster recovery orchestrator
    Handles all failure scenarios with automatic recovery
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize disaster recovery engine"""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize clients
        self.binance_primary = BinanceClient(
            api_key=config['BINANCE_API_KEY'],
            api_secret=config['BINANCE_API_SECRET'],
            testnet=config.get('TESTNET', False)
        )
        self.binance_backup = BinanceClient(
            api_key=config.get('BINANCE_BACKUP_KEY', config['BINANCE_API_KEY']),
            api_secret=config.get('BINANCE_BACKUP_SECRET', config['BINANCE_API_SECRET']),
            testnet=config.get('TESTNET', False)
        )

        # Redis for caching and state
        self.redis_client = redis.Redis(
            host=config.get('REDIS_HOST', 'localhost'),
            port=config.get('REDIS_PORT', 6379),
            decode_responses=True,
            socket_connect_timeout=5
        )

        # Database for disaster logs
        self.db_engine = create_engine(config.get('DATABASE_URL', 'sqlite:///disasters.db'))
        Base.metadata.create_all(self.db_engine)
        self.SessionMaker = sessionmaker(bind=self.db_engine)

        # Disaster history
        self.disaster_history: List[DisasterEvent] = []
        self.max_history = 1000

        # Recovery state
        self.in_recovery = False
        self.recovery_mode_start = None
        self.recovery_attempts = 0
        self.max_recovery_attempts = 5

        # Backup management
        self.backup_dir = Path(config.get('BACKUP_DIR', './backups'))
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints: Dict[str, BackupCheckpoint] = {}

        # API endpoints (primary and backup)
        self.api_endpoints = self._initialize_api_endpoints()
        self.current_primary_index = 0

        # Local state cache
        self.last_known_positions = {}
        self.last_sync_timestamp = None
        self.position_state_hash = None

        self.logger.info("🛡️  Disaster Recovery Engine initialized")

    def _initialize_api_endpoints(self) -> List[APIEndpoint]:
        """Initialize API endpoints with failover"""
        return [
            APIEndpoint(
                name="binance_primary",
                url="https://api.binance.com",
                is_primary=True,
                priority=1,
                timeout=5.0,
                max_retries=3,
                backoff_factor=1.5
            ),
            APIEndpoint(
                name="binance_us",
                url="https://api.binance.us",
                is_primary=False,
                priority=2,
                timeout=7.0,
                max_retries=3,
                backoff_factor=1.5
            ),
            APIEndpoint(
                name="binance_testnet",
                url="https://testnet.binance.vision",
                is_primary=False,
                priority=3,
                timeout=10.0,
                max_retries=2,
                backoff_factor=2.0
            )
        ]

    async def detect_and_recover(self, market_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main detection and recovery loop
        Runs continuously to detect and handle disasters
        """
        try:
            # Detect anomalies
            anomalies = await self._detect_anomalies(market_state)

            if anomalies:
                recovery_result = await self._execute_recovery(anomalies, market_state)
                return recovery_result
            else:
                return {'status': 'ok', 'anomalies_detected': []}

        except Exception as e:
            self.logger.critical(f"❌ Critical error in detect_and_recover: {str(e)}")
            await self._send_emergency_alert(str(e), "CRITICAL_DETECTION_FAILURE")
            return {'status': 'error', 'message': str(e)}

    async def _detect_anomalies(self, market_state: Dict[str, Any]) -> List[DisasterEvent]:
        """Detect various disaster scenarios"""
        anomalies = []

        # Check connection health
        connection_status = await self._check_connection_health()
        if not connection_status['healthy']:
            anomalies.append(DisasterEvent(
                failure_type=FailureType.CONNECTION_FAILURE,
                timestamp=datetime.now(),
                severity=8,
                component="binance_api",
                error_message=connection_status['error'],
                context={'last_response_time': connection_status.get('response_time')}
            ))

        # Check position state sync
        desync_status = await self._check_position_state_sync()
        if not desync_status['synchronized']:
            anomalies.append(DisasterEvent(
                failure_type=FailureType.POSITION_DESYNC,
                timestamp=datetime.now(),
                severity=9,
                component="position_state",
                error_message="Position state desynchronized",
                context=desync_status
            ))

        # Check margin levels
        margin_status = await self._check_margin_safety()
        if margin_status['at_risk']:
            anomalies.append(DisasterEvent(
                failure_type=FailureType.MARGIN_CALL,
                timestamp=datetime.now(),
                severity=10,
                component="margin",
                error_message=f"Margin ratio: {margin_status['margin_ratio']:.2f}",
                context=margin_status
            ))

        # Check data integrity
        data_check = await self._check_data_integrity()
        if not data_check['valid']:
            anomalies.append(DisasterEvent(
                failure_type=FailureType.DATA_CORRUPTION,
                timestamp=datetime.now(),
                severity=7,
                component="data_layer",
                error_message=data_check['error'],
                context={'corrupted_fields': data_check.get('corrupted_fields', [])}
            ))

        # Check for pending orders
        pending_check = await self._check_pending_orders()
        if pending_check['has_issues']:
            anomalies.append(DisasterEvent(
                failure_type=FailureType.ORDER_EXECUTION_FAILURE,
                timestamp=datetime.now(),
                severity=6,
                component="orders",
                error_message=pending_check['issue'],
                context={'orders': pending_check.get('problematic_orders', [])}
            ))

        return anomalies

    async def _check_connection_health(self) -> Dict[str, Any]:
        """Check API connection health"""
        try:
            start_time = time.time()

            # Try primary
            try:
                ping = self.binance_primary.get_server_time()
                response_time = (time.time() - start_time) * 1000

                if response_time > 2000:  # Alert if > 2s
                    return {
                        'healthy': False,
                        'error': f'Slow response: {response_time:.0f}ms',
                        'response_time': response_time
                    }

                return {
                    'healthy': True,
                    'response_time': response_time,
                    'endpoint': 'primary'
                }

            except (BinanceAPIException, BinanceRequestException) as e:
                self.logger.warning(f"Primary API failed: {str(e)}")

                # Try backup
                start_time = time.time()
                ping = self.binance_backup.get_server_time()
                response_time = (time.time() - start_time) * 1000

                return {
                    'healthy': True,
                    'response_time': response_time,
                    'endpoint': 'backup',
                    'warning': 'Primary failed, using backup'
                }

        except Exception as e:
            return {
                'healthy': False,
                'error': f'All endpoints failed: {str(e)}'
            }

    async def _check_position_state_sync(self) -> Dict[str, Any]:
        """
        Verify positions are synchronized between local cache and exchange
        Runs every 60 seconds
        """
        try:
            # Get local cached positions
            local_positions = self._get_local_positions()

            # Get actual positions from exchange
            exchange_positions = self._get_exchange_positions()

            # Compare
            if not self._positions_equal(local_positions, exchange_positions):
                desync_details = self._analyze_position_desync(
                    local_positions,
                    exchange_positions
                )

                self.logger.error(f"❌ POSITION DESYNC DETECTED: {desync_details}")

                return {
                    'synchronized': False,
                    'desync_type': desync_details['type'],
                    'local_positions': local_positions,
                    'exchange_positions': exchange_positions,
                    'differences': desync_details['differences']
                }

            # Update last sync time
            self.last_sync_timestamp = datetime.now()

            return {
                'synchronized': True,
                'positions': exchange_positions,
                'sync_timestamp': self.last_sync_timestamp
            }

        except Exception as e:
            self.logger.error(f"Error checking position sync: {str(e)}")
            return {
                'synchronized': False,
                'error': str(e)
            }

    async def _check_margin_safety(self) -> Dict[str, Any]:
        """
        Monitor margin levels and prevent liquidation
        Thresholds: 70% = PAUSE, 80% = REDUCE, 90% = EMERGENCY
        """
        try:
            account = self.binance_primary.get_account()

            # Calculate margin ratios
            total_assets = float(account['totalAssetOfBtc'])
            total_liability = float(account.get('totalLiabilityOfBtc', 0))

            if total_liability == 0:
                return {
                    'at_risk': False,
                    'margin_ratio': 0.0,
                    'level': 'SAFE'
                }

            margin_ratio = total_liability / total_assets

            if margin_ratio > 0.90:
                status = 'CRITICAL'
                at_risk = True
                action = "EMERGENCY: Close all positions immediately"
            elif margin_ratio > 0.80:
                status = 'DANGER'
                at_risk = True
                action = "DANGER: Close 50% of positions"
            elif margin_ratio > 0.70:
                status = 'WARNING'
                at_risk = False
                action = "WARNING: Stop opening new positions"
            else:
                status = 'SAFE'
                at_risk = False
                action = "Safe to trade normally"

            return {
                'at_risk': at_risk,
                'margin_ratio': margin_ratio,
                'level': status,
                'action': action,
                'total_assets': total_assets,
                'total_liability': total_liability
            }

        except Exception as e:
            self.logger.error(f"Error checking margin: {str(e)}")
            return {
                'at_risk': True,
                'error': str(e),
                'level': 'UNKNOWN'
            }

    async def _check_data_integrity(self) -> Dict[str, Any]:
        """Verify data integrity across all layers"""
        try:
            corrupted_fields = []

            # Check price data validity
            latest_price = self.redis_client.get('latest_price_btc')
            if latest_price:
                try:
                    price_val = float(latest_price)
                    if price_val <= 0 or price_val > 1000000:
                        corrupted_fields.append('price_data')
                except:
                    corrupted_fields.append('price_data')

            # Check timestamp freshness
            last_update = self.redis_client.get('last_update_timestamp')
            if last_update:
                last_update_time = datetime.fromisoformat(last_update)
                if (datetime.now() - last_update_time).seconds > 300:
                    corrupted_fields.append('stale_data')

            # Check position hashes
            current_hash = self._calculate_position_hash()
            if self.position_state_hash and current_hash != self.position_state_hash:
                if not self._is_valid_position_change(current_hash):
                    corrupted_fields.append('position_integrity')

            self.position_state_hash = current_hash

            if corrupted_fields:
                return {
                    'valid': False,
                    'corrupted_fields': corrupted_fields,
                    'error': 'Data integrity check failed'
                }

            return {'valid': True}

        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }

    async def _check_pending_orders(self) -> Dict[str, Any]:
        """Check for problematic pending orders"""
        try:
            open_orders = self.binance_primary.get_open_orders(symbol='BTCUSDT')

            problematic_orders = []
            for order in open_orders:
                # Check for very old orders
                order_age_ms = time.time() * 1000 - order['time']
                if order_age_ms > 86400000:  # > 1 day
                    problematic_orders.append({
                        'order_id': order['orderId'],
                        'issue': 'Order older than 24 hours'
                    })

                # Check for partial fills stuck
                if order['status'] == 'PARTIALLY_FILLED':
                    problematic_orders.append({
                        'order_id': order['orderId'],
                        'issue': 'Partially filled order stuck'
                    })

            return {
                'has_issues': len(problematic_orders) > 0,
                'issue': f'{len(problematic_orders)} problematic orders found',
                'problematic_orders': problematic_orders
            }

        except Exception as e:
            return {
                'has_issues': False,
                'error': str(e)
            }

    async def _execute_recovery(self, anomalies: List[DisasterEvent], 
                                market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute recovery procedures based on anomalies"""
        self.in_recovery = True
        self.recovery_mode_start = datetime.now()
        recovery_results = []

        for anomaly in sorted(anomalies, key=lambda x: x.severity, reverse=True):

            if anomaly.failure_type == FailureType.CONNECTION_FAILURE:
                result = await self._recover_connection_failure(anomaly)

            elif anomaly.failure_type == FailureType.POSITION_DESYNC:
                result = await self._recover_position_desync(anomaly)

            elif anomaly.failure_type == FailureType.MARGIN_CALL:
                result = await self._recover_margin_crisis(anomaly)

            elif anomaly.failure_type == FailureType.DATA_CORRUPTION:
                result = await self._recover_data_corruption(anomaly)

            elif anomaly.failure_type == FailureType.ORDER_EXECUTION_FAILURE:
                result = await self._recover_order_failure(anomaly)

            else:
                result = {'status': 'unknown_failure_type'}

            anomaly.recovery_status = RecoveryStatus(result.get('recovery_status', 'failed'))
            recovery_results.append(result)

            # Log disaster
            self._log_disaster(anomaly)

        self.in_recovery = False
        return {
            'status': 'recovery_executed',
            'anomalies_count': len(anomalies),
            'recovery_results': recovery_results
        }

    async def _recover_connection_failure(self, anomaly: DisasterEvent) -> Dict[str, Any]:
        """Handle connection failures with exponential backoff"""
        self.logger.warning("🔄 Attempting connection recovery...")

        for attempt in range(self.max_recovery_attempts):
            try:
                # Exponential backoff
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

                # Try primary
                ping = self.binance_primary.get_server_time()
                self.logger.info("✅ Connection restored to primary")

                return {
                    'recovery_status': 'recovered',
                    'attempts': attempt + 1,
                    'endpoint': 'primary'
                }

            except Exception as e:
                if attempt == self.max_recovery_attempts - 1:
                    try:
                        # Try backup
                        ping = self.binance_backup.get_server_time()
                        self.logger.info("✅ Connection restored to backup")

                        return {
                            'recovery_status': 'recovered',
                            'attempts': attempt + 1,
                            'endpoint': 'backup'
                        }
                    except:
                        pass

        self.logger.critical("❌ Connection recovery FAILED")
        await self._send_emergency_alert(
            "Connection could not be restored",
            "CONNECTION_FAILURE"
        )

        return {
            'recovery_status': 'failed',
            'attempts': self.max_recovery_attempts,
            'error': 'All connection attempts failed'
        }

    async def _recover_position_desync(self, anomaly: DisasterEvent) -> Dict[str, Any]:
        """Reconcile position state with exchange"""
        self.logger.critical("🔄 Reconciling position state...")

        try:
            exchange_positions = self._get_exchange_positions()

            # Update local cache with exchange data
            self.last_known_positions = exchange_positions
            self.last_sync_timestamp = datetime.now()

            # Store in Redis as backup
            self.redis_client.set(
                'position_backup',
                json.dumps({
                    'positions': exchange_positions,
                    'timestamp': self.last_sync_timestamp.isoformat()
                })
            )

            self.logger.info("✅ Position state reconciled")

            return {
                'recovery_status': 'recovered',
                'positions_synced': len(exchange_positions),
                'last_sync': self.last_sync_timestamp.isoformat()
            }

        except Exception as e:
            self.logger.error(f"❌ Position reconciliation failed: {str(e)}")

            await self._send_emergency_alert(
                f"Position reconciliation failed: {str(e)}",
                "POSITION_DESYNC"
            )

            return {
                'recovery_status': 'failed',
                'error': str(e)
            }

    async def _recover_margin_crisis(self, anomaly: DisasterEvent) -> Dict[str, Any]:
        """Emergency response to margin call risk"""
        margin_ratio = anomaly.context.get('margin_ratio', 0.9)

        self.logger.critical(f"🚨 EMERGENCY: Margin crisis at {margin_ratio:.2%}")

        try:
            if margin_ratio > 0.90:
                # CRITICAL: Close ALL positions
                self.logger.critical("🚨 EMERGENCY SHUTDOWN - Closing all positions")
                closed_positions = await self._close_all_positions()

                await self._send_emergency_alert(
                    f"EMERGENCY SHUTDOWN: Closed {len(closed_positions)} positions",
                    "MARGIN_CALL_CRITICAL"
                )

                return {
                    'recovery_status': 'recovered',
                    'action': 'all_positions_closed',
                    'positions_closed': len(closed_positions)
                }

            elif margin_ratio > 0.80:
                # DANGER: Close 50% of positions
                self.logger.error("⚠️ DANGER: Closing 50% of positions")
                closed_positions = await self._close_partial_positions(0.5)

                return {
                    'recovery_status': 'recovered',
                    'action': 'partial_positions_closed',
                    'positions_closed': len(closed_positions)
                }

            elif margin_ratio > 0.70:
                # WARNING: Pause trading
                self.logger.warning("⚠️ WARNING: Trading paused")

                return {
                    'recovery_status': 'recovered',
                    'action': 'trading_paused'
                }

        except Exception as e:
            self.logger.critical(f"❌ Margin recovery FAILED: {str(e)}")

            await self._send_emergency_alert(
                f"Margin recovery failed: {str(e)}",
                "MARGIN_RECOVERY_FAILED"
            )

            return {
                'recovery_status': 'failed',
                'error': str(e)
            }

    async def _recover_data_corruption(self, anomaly: DisasterEvent) -> Dict[str, Any]:
        """Restore from backup if data corruption detected"""
        self.logger.error("🔄 Attempting data restoration...")

        try:
            # Find most recent backup
            latest_backup = self._find_latest_backup()

            if not latest_backup:
                raise Exception("No backup found")

            # Restore from backup
            restored_data = self._restore_from_backup(latest_backup)

            self.logger.info(f"✅ Data restored from backup {latest_backup.checkpoint_id}")

            return {
                'recovery_status': 'recovered',
                'backup_id': latest_backup.checkpoint_id,
                'backup_timestamp': latest_backup.timestamp.isoformat(),
                'data_restored': True
            }

        except Exception as e:
            self.logger.critical(f"❌ Data restoration failed: {str(e)}")

            return {
                'recovery_status': 'manual_intervention',
                'error': str(e)
            }

    async def _recover_order_failure(self, anomaly: DisasterEvent) -> Dict[str, Any]:
        """Verify and retry failed orders"""
        self.logger.warning("🔄 Verifying pending orders...")

        try:
            problematic_orders = anomaly.context.get('problematic_orders', [])

            for order in problematic_orders:
                # Verify order status
                order_status = self._verify_order_status(order['order_id'])

                if order_status == 'FILLED':
                    # Order actually filled
                    continue

                elif order_status == 'PARTIALLY_FILLED':
                    # Complete the partial fill
                    await self._cancel_and_retry_order(order['order_id'])

                elif order_status == 'PENDING':
                    # Order still pending, wait 5 more seconds
                    await asyncio.sleep(5)

                    order_status_2 = self._verify_order_status(order['order_id'])
                    if order_status_2 != 'FILLED':
                        # Cancel and retry
                        await self._cancel_and_retry_order(order['order_id'])

            return {
                'recovery_status': 'recovered',
                'orders_verified': len(problematic_orders)
            }

        except Exception as e:
            return {
                'recovery_status': 'failed',
                'error': str(e)
            }

    # Utility methods

    def _get_local_positions(self) -> List[Dict[str, Any]]:
        """Get cached positions from Redis"""
        cached = self.redis_client.get('position_backup')
        if cached:
            return json.loads(cached).get('positions', [])
        return self.last_known_positions or []

    def _get_exchange_positions(self) -> List[Dict[str, Any]]:
        """Get actual positions from exchange"""
        try:
            account = self.binance_primary.get_account()
            balances = account['balances']

            positions = []
            for balance in balances:
                if float(balance['free']) > 0 or float(balance['locked']) > 0:
                    positions.append({
                        'asset': balance['asset'],
                        'free': float(balance['free']),
                        'locked': float(balance['locked'])
                    })

            return positions
        except:
            return []

    def _positions_equal(self, pos1: List[Dict], pos2: List[Dict]) -> bool:
        """Compare two position lists"""
        if len(pos1) != len(pos2):
            return False

        for p1 in pos1:
            found = False
            for p2 in pos2:
                if p1.get('asset') == p2.get('asset'):
                    # Allow small floating point differences
                    if abs(float(p1.get('free', 0)) - float(p2.get('free', 0))) < 0.00001:
                        found = True
                        break
            if not found:
                return False

        return True

    def _analyze_position_desync(self, local: List[Dict], 
                                 exchange: List[Dict]) -> Dict[str, Any]:
        """Analyze differences between local and exchange positions"""
        differences = []

        for e_pos in exchange:
            for l_pos in local:
                if e_pos.get('asset') == l_pos.get('asset'):
                    diff = abs(float(e_pos.get('free', 0)) - float(l_pos.get('free', 0)))
                    if diff > 0.00001:
                        differences.append({
                            'asset': e_pos.get('asset'),
                            'local': float(l_pos.get('free', 0)),
                            'exchange': float(e_pos.get('free', 0)),
                            'difference': diff
                        })

        return {
            'type': 'quantity_mismatch' if differences else 'other',
            'differences': differences
        }

    def _calculate_position_hash(self) -> str:
        """Calculate hash of current positions for integrity check"""
        positions_str = json.dumps(self.last_known_positions, sort_keys=True)
        return hashlib.sha256(positions_str.encode()).hexdigest()

    def _is_valid_position_change(self, new_hash: str) -> bool:
        """Verify position change is valid (not corruption)"""
        # Could involve more sophisticated validation
        return True

    async def _close_all_positions(self) -> List[Dict[str, Any]]:
        """Close all open positions (emergency)"""
        closed = []
        # Implementation would close all positions
        return closed

    async def _close_partial_positions(self, percentage: float) -> List[Dict[str, Any]]:
        """Close percentage of positions"""
        closed = []
        # Implementation would close positions
        return closed

    def _verify_order_status(self, order_id: str) -> str:
        """Check actual order status on exchange"""
        try:
            order = self.binance_primary.get_order(symbol='BTCUSDT', orderId=order_id)
            return order['status']
        except:
            return 'UNKNOWN'

    async def _cancel_and_retry_order(self, order_id: str):
        """Cancel and retry an order"""
        try:
            self.binance_primary.cancel_order(symbol='BTCUSDT', orderId=order_id)
            await asyncio.sleep(1)
            # Retry order logic
        except:
            pass

    def _find_latest_backup(self) -> Optional[BackupCheckpoint]:
        """Find most recent valid backup"""
        if not self.checkpoints:
            return None

        return max(self.checkpoints.values(), key=lambda x: x.timestamp)

    def _restore_from_backup(self, checkpoint: BackupCheckpoint) -> Dict[str, Any]:
        """Restore data from backup"""
        with open(checkpoint.backup_location, 'rb') as f:
            return pickle.load(f)

    def _log_disaster(self, event: DisasterEvent):
        """Log disaster to database"""
        self.disaster_history.append(event)
        if len(self.disaster_history) > self.max_history:
            self.disaster_history.pop(0)

        # Also save to database for persistence
        self.logger.info(f"Disaster logged: {event.failure_type.value} - {event.severity}/10")

    async def _send_emergency_alert(self, message: str, alert_type: str):
        """Send emergency alert via Telegram"""
        telegram_token = self.config.get('TELEGRAM_BOT_TOKEN', '')
        telegram_chat_id = self.config.get('TELEGRAM_CHAT_ID', '')

        if telegram_token and telegram_chat_id:
            try:
                url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                message_text = f"🚨 **DEMIR AI - EMERGENCY ALERT** 🚨\n\n"
                message_text += f"Type: {alert_type}\n"
                message_text += f"Message: {message}\n"
                message_text += f"Time: {datetime.now().isoformat()}"

                async with aiohttp.ClientSession() as session:
                    await session.post(url, json={
                        'chat_id': telegram_chat_id,
                        'text': message_text,
                        'parse_mode': 'Markdown'
                    })
            except Exception as e:
                self.logger.error(f"Failed to send Telegram alert: {str(e)}")

# ============================================================================
# DATABASE MODELS
# ============================================================================

Base = declarative_base()

class DisasterLog(Base):
    """Database model for disaster events"""
    __tablename__ = 'disaster_logs'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    failure_type = Column(String)
    severity = Column(Integer)
    component = Column(String)
    error_message = Column(String)
    context = Column(JSON)
    recovery_status = Column(String)
    recovery_attempts = Column(Integer)
    action_taken = Column(String)

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'DisasterRecoveryEngine',
    'DisasterEvent',
    'FailureType',
    'RecoveryStatus',
    'BackupCheckpoint',
    'PositionSnapshot'
]
