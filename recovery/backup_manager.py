"""
DEMIR AI - Phase 13 Backup Manager
Complete backup and checkpoint management system
Full Production Code - NO MOCKS
Created: November 7, 2025
"""

import os
import json
import gzip
import shutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import pickle

import pandas as pd
from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class BackupType(Enum):
    """Types of backups"""
    POSITION_STATE = "position_state"
    TRADE_HISTORY = "trade_history"
    CONFIGURATION = "configuration"
    SYSTEM_STATE = "system_state"
    MARKET_DATA = "market_data"
    ML_MODELS = "ml_models"
    FULL_SYSTEM = "full_system"

class CompressionType(Enum):
    """Compression methods"""
    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"

@dataclass
class BackupMetadata:
    """Metadata for a backup"""
    backup_id: str
    backup_type: BackupType
    timestamp: datetime
    size_bytes: int
    compressed_size_bytes: int
    compression_type: CompressionType
    data_hash: str
    integrity_verified: bool
    location: str
    expires_at: Optional[datetime]
    retention_days: int
    tags: Dict[str, str]

@dataclass
class BackupIndexEntry:
    """Entry in backup index"""
    backup_id: str
    backup_type: str
    timestamp: datetime
    size_bytes: int
    integrity_hash: str
    accessible: bool

# ============================================================================
# BACKUP MANAGER
# ============================================================================

class BackupManager:
    """
    Comprehensive backup and checkpoint management
    Handles all backup operations with compression, verification, and rotation
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize backup manager"""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Backup directories
        self.base_backup_dir = Path(config.get('BACKUP_DIR', './backups'))
        self.base_backup_dir.mkdir(parents=True, exist_ok=True)

        self.backup_types_dir = {
            'position': self.base_backup_dir / 'positions',
            'trades': self.base_backup_dir / 'trades',
            'config': self.base_backup_dir / 'config',
            'system': self.base_backup_dir / 'system',
            'market': self.base_backup_dir / 'market',
            'models': self.base_backup_dir / 'models',
            'archive': self.base_backup_dir / 'archive'
        }

        for dir_path in self.backup_types_dir.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Database for backup metadata
        self.db_engine = create_engine(config.get('DATABASE_URL', 'sqlite:///backups.db'))
        Base.metadata.create_all(self.db_engine)
        self.SessionMaker = sessionmaker(bind=self.db_engine)

        # Backup index (in-memory cache)
        self.backup_index: Dict[str, BackupIndexEntry] = {}
        self.load_backup_index()

        # Configuration
        self.compression_type = CompressionType[config.get('BACKUP_COMPRESSION', 'GZIP')]
        self.retention_days_default = config.get('BACKUP_RETENTION_DAYS', 30)
        self.max_local_backups_per_type = config.get('MAX_BACKUPS_PER_TYPE', 10)
        self.backup_chunk_size = config.get('BACKUP_CHUNK_SIZE', 1024 * 1024)  # 1MB

        # Cloud backup settings
        self.cloud_enabled = config.get('CLOUD_BACKUP_ENABLED', False)
        self.cloud_bucket = config.get('CLOUD_BUCKET', '')

        self.logger.info("🔄 Backup Manager initialized")

    def backup_positions(self, positions_data: Dict[str, Any]) -> str:
        """Backup current position state"""
        backup_id = self._generate_backup_id(BackupType.POSITION_STATE)

        try:
            # Serialize data
            data_bytes = pickle.dumps(positions_data)

            # Compress
            compressed_data, compression_type = self._compress_data(data_bytes)

            # Calculate hashes
            data_hash = hashlib.sha256(data_bytes).hexdigest()

            # Save to file
            backup_path = self.backup_types_dir['position'] / f"{backup_id}.pkl.gz"
            with open(backup_path, 'wb') as f:
                f.write(compressed_data)

            # Create metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type=BackupType.POSITION_STATE,
                timestamp=datetime.now(),
                size_bytes=len(data_bytes),
                compressed_size_bytes=len(compressed_data),
                compression_type=compression_type,
                data_hash=data_hash,
                integrity_verified=True,
                location=str(backup_path),
                expires_at=datetime.now() + timedelta(days=self.retention_days_default),
                retention_days=self.retention_days_default,
                tags={'auto': 'true', 'symbol': 'BTCUSDT'}
            )

            # Store metadata
            self._store_backup_metadata(metadata)

            self.logger.info(f"✅ Position backup created: {backup_id}")

            # Cleanup old backups
            self._cleanup_old_backups(BackupType.POSITION_STATE)

            return backup_id

        except Exception as e:
            self.logger.error(f"❌ Position backup failed: {str(e)}")
            raise

    def backup_trade_history(self, trades_df: pd.DataFrame) -> str:
        """Backup trade history"""
        backup_id = self._generate_backup_id(BackupType.TRADE_HISTORY)

        try:
            # Convert DataFrame to JSON
            data_json = trades_df.to_json(orient='records')
            data_bytes = data_json.encode('utf-8')

            # Compress
            compressed_data, compression_type = self._compress_data(data_bytes)

            # Calculate hashes
            data_hash = hashlib.sha256(data_bytes).hexdigest()

            # Save
            backup_path = self.backup_types_dir['trades'] / f"{backup_id}.json.gz"
            with open(backup_path, 'wb') as f:
                f.write(compressed_data)

            # Metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type=BackupType.TRADE_HISTORY,
                timestamp=datetime.now(),
                size_bytes=len(data_bytes),
                compressed_size_bytes=len(compressed_data),
                compression_type=compression_type,
                data_hash=data_hash,
                integrity_verified=True,
                location=str(backup_path),
                expires_at=datetime.now() + timedelta(days=self.retention_days_default * 2),
                retention_days=self.retention_days_default * 2,
                tags={'trades_count': str(len(trades_df)), 'period': 'all'}
            )

            self._store_backup_metadata(metadata)

            self.logger.info(f"✅ Trade history backup created: {backup_id}")
            self._cleanup_old_backups(BackupType.TRADE_HISTORY)

            return backup_id

        except Exception as e:
            self.logger.error(f"❌ Trade history backup failed: {str(e)}")
            raise

    def backup_configuration(self, config_data: Dict[str, Any]) -> str:
        """Backup system configuration"""
        backup_id = self._generate_backup_id(BackupType.CONFIGURATION)

        try:
            # Remove sensitive data before backup
            safe_config = self._sanitize_config(config_data)

            data_json = json.dumps(safe_config, indent=2, default=str)
            data_bytes = data_json.encode('utf-8')

            # Compress
            compressed_data, compression_type = self._compress_data(data_bytes)

            # Hash
            data_hash = hashlib.sha256(data_bytes).hexdigest()

            # Save
            backup_path = self.backup_types_dir['config'] / f"{backup_id}.json.gz"
            with open(backup_path, 'wb') as f:
                f.write(compressed_data)

            # Metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type=BackupType.CONFIGURATION,
                timestamp=datetime.now(),
                size_bytes=len(data_bytes),
                compressed_size_bytes=len(compressed_data),
                compression_type=compression_type,
                data_hash=data_hash,
                integrity_verified=True,
                location=str(backup_path),
                expires_at=None,  # Keep config backups indefinitely
                retention_days=-1,
                tags={'config_version': '2.0', 'environment': 'production'}
            )

            self._store_backup_metadata(metadata)

            self.logger.info(f"✅ Configuration backup created: {backup_id}")
            self._cleanup_old_backups(BackupType.CONFIGURATION, keep_count=20)

            return backup_id

        except Exception as e:
            self.logger.error(f"❌ Configuration backup failed: {str(e)}")
            raise

    def backup_system_state(self, state_data: Dict[str, Any]) -> str:
        """Backup complete system state (checkpoint)"""
        backup_id = self._generate_backup_id(BackupType.SYSTEM_STATE)

        try:
            data_bytes = pickle.dumps(state_data)
            compressed_data, compression_type = self._compress_data(data_bytes)
            data_hash = hashlib.sha256(data_bytes).hexdigest()

            backup_path = self.backup_types_dir['system'] / f"{backup_id}.pkl.gz"
            with open(backup_path, 'wb') as f:
                f.write(compressed_data)

            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type=BackupType.SYSTEM_STATE,
                timestamp=datetime.now(),
                size_bytes=len(data_bytes),
                compressed_size_bytes=len(compressed_data),
                compression_type=compression_type,
                data_hash=data_hash,
                integrity_verified=True,
                location=str(backup_path),
                expires_at=datetime.now() + timedelta(days=7),
                retention_days=7,
                tags={'checkpoint': 'true', 'auto': 'true'}
            )

            self._store_backup_metadata(metadata)

            self.logger.info(f"✅ System state backup created: {backup_id}")
            self._cleanup_old_backups(BackupType.SYSTEM_STATE, keep_count=5)

            return backup_id

        except Exception as e:
            self.logger.error(f"❌ System state backup failed: {str(e)}")
            raise

    def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """Restore data from a backup"""
        try:
            # Get backup metadata
            session = self.SessionMaker()
            backup_record = session.query(BackupRecord).filter_by(
                backup_id=backup_id
            ).first()
            session.close()

            if not backup_record:
                raise FileNotFoundError(f"Backup {backup_id} not found")

            # Read backup file
            backup_path = Path(backup_record.location)
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file {backup_path} not found")

            # Decompress
            with open(backup_path, 'rb') as f:
                compressed_data = f.read()

            decompressed_data = self._decompress_data(
                compressed_data,
                backup_record.compression_type
            )

            # Verify integrity
            restored_hash = hashlib.sha256(decompressed_data).hexdigest()
            if restored_hash != backup_record.data_hash:
                raise ValueError("Backup integrity check failed - data corrupted")

            self.logger.info(f"✅ Backup restored: {backup_id}")

            # Return appropriate format based on type
            if backup_record.backup_type == BackupType.POSITION_STATE.value:
                return pickle.loads(decompressed_data)
            elif backup_record.backup_type == BackupType.TRADE_HISTORY.value:
                json_data = decompressed_data.decode('utf-8')
                return pd.read_json(json_data, orient='records')
            else:
                return pickle.loads(decompressed_data)

        except Exception as e:
            self.logger.error(f"❌ Backup restore failed: {str(e)}")
            raise

    def list_backups(self, backup_type: Optional[BackupType] = None) -> List[BackupMetadata]:
        """List all available backups"""
        session = self.SessionMaker()

        query = session.query(BackupRecord)
        if backup_type:
            query = query.filter_by(backup_type=backup_type.value)

        backups = query.order_by(BackupRecord.timestamp.desc()).all()
        session.close()

        return backups

    def delete_backup(self, backup_id: str) -> bool:
        """Delete a specific backup"""
        try:
            session = self.SessionMaker()
            backup_record = session.query(BackupRecord).filter_by(
                backup_id=backup_id
            ).first()

            if backup_record:
                # Delete file
                backup_path = Path(backup_record.location)
                if backup_path.exists():
                    backup_path.unlink()

                # Delete record
                session.delete(backup_record)
                session.commit()

                self.logger.info(f"✅ Backup deleted: {backup_id}")
                return True

            session.close()
            return False

        except Exception as e:
            self.logger.error(f"❌ Backup deletion failed: {str(e)}")
            return False

    def verify_backup_integrity(self, backup_id: str) -> bool:
        """Verify backup file integrity"""
        try:
            session = self.SessionMaker()
            backup_record = session.query(BackupRecord).filter_by(
                backup_id=backup_id
            ).first()
            session.close()

            if not backup_record:
                return False

            backup_path = Path(backup_record.location)
            if not backup_path.exists():
                return False

            # Read and check hash
            with open(backup_path, 'rb') as f:
                compressed_data = f.read()

            decompressed_data = self._decompress_data(
                compressed_data,
                backup_record.compression_type
            )

            restored_hash = hashlib.sha256(decompressed_data).hexdigest()

            is_valid = restored_hash == backup_record.data_hash

            # Update verification status
            session = self.SessionMaker()
            backup_record.integrity_verified = is_valid
            session.commit()
            session.close()

            self.logger.info(f"✅ Backup integrity check: {backup_id} - {'VALID' if is_valid else 'INVALID'}")

            return is_valid

        except Exception as e:
            self.logger.error(f"❌ Integrity check failed: {str(e)}")
            return False

    def get_backup_stats(self) -> Dict[str, Any]:
        """Get backup statistics"""
        session = self.SessionMaker()

        total_backups = session.query(BackupRecord).count()
        total_size = 0
        total_compressed_size = 0
        backups_by_type = {}

        for record in session.query(BackupRecord).all():
            total_size += record.size_bytes
            total_compressed_size += record.compressed_size_bytes

            backup_type = record.backup_type
            if backup_type not in backups_by_type:
                backups_by_type[backup_type] = {'count': 0, 'size': 0}

            backups_by_type[backup_type]['count'] += 1
            backups_by_type[backup_type]['size'] += record.size_bytes

        session.close()

        return {
            'total_backups': total_backups,
            'total_size_mb': total_size / (1024 * 1024),
            'total_compressed_size_mb': total_compressed_size / (1024 * 1024),
            'compression_ratio': total_compressed_size / total_size if total_size > 0 else 0,
            'backups_by_type': backups_by_type
        }

    # Private utility methods

    def _compress_data(self, data: bytes) -> Tuple[bytes, CompressionType]:
        """Compress data"""
        if self.compression_type == CompressionType.GZIP:
            compressed = gzip.compress(data, compresslevel=6)
            return compressed, CompressionType.GZIP
        else:
            return data, CompressionType.NONE

    def _decompress_data(self, data: bytes, compression_type: str) -> bytes:
        """Decompress data"""
        if compression_type == CompressionType.GZIP.value:
            return gzip.decompress(data)
        else:
            return data

    def _sanitize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from config"""
        sensitive_keys = [
            'API_KEY', 'API_SECRET', 'PRIVATE_KEY', 'PASSWORD',
            'TOKEN', 'SECRET', 'TELEGRAM_BOT_TOKEN'
        ]

        sanitized = {}
        for key, value in config.items():
            if any(sensitive in key.upper() for sensitive in sensitive_keys):
                sanitized[key] = '***REDACTED***'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_config(value)
            else:
                sanitized[key] = value

        return sanitized

    def _generate_backup_id(self, backup_type: BackupType) -> str:
        """Generate unique backup ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        type_prefix = backup_type.value[:3].upper()
        return f"{type_prefix}_{timestamp}"

    def _store_backup_metadata(self, metadata: BackupMetadata):
        """Store backup metadata in database"""
        session = self.SessionMaker()

        record = BackupRecord(
            backup_id=metadata.backup_id,
            backup_type=metadata.backup_type.value,
            timestamp=metadata.timestamp,
            size_bytes=metadata.size_bytes,
            compressed_size_bytes=metadata.compressed_size_bytes,
            compression_type=metadata.compression_type.value,
            data_hash=metadata.data_hash,
            integrity_verified=metadata.integrity_verified,
            location=metadata.location,
            expires_at=metadata.expires_at,
            retention_days=metadata.retention_days
        )

        session.add(record)
        session.commit()
        session.close()

    def _cleanup_old_backups(self, backup_type: BackupType, keep_count: Optional[int] = None):
        """Delete old backups beyond retention"""
        if keep_count is None:
            keep_count = self.max_local_backups_per_type

        session = self.SessionMaker()

        # Get backups ordered by timestamp
        backups = session.query(BackupRecord).filter_by(
            backup_type=backup_type.value
        ).order_by(BackupRecord.timestamp.desc()).all()

        # Delete old ones
        for i, backup in enumerate(backups):
            if i >= keep_count:
                # Check if expired
                if backup.expires_at and backup.expires_at < datetime.now():
                    backup_path = Path(backup.location)
                    if backup_path.exists():
                        backup_path.unlink()

                    session.delete(backup)

        session.commit()
        session.close()

    def load_backup_index(self):
        """Load backup index from database"""
        session = self.SessionMaker()

        for record in session.query(BackupRecord).all():
            self.backup_index[record.backup_id] = BackupIndexEntry(
                backup_id=record.backup_id,
                backup_type=record.backup_type,
                timestamp=record.timestamp,
                size_bytes=record.size_bytes,
                integrity_hash=record.data_hash,
                accessible=Path(record.location).exists()
            )

        session.close()

# ============================================================================
# DATABASE MODELS
# ============================================================================

Base = declarative_base()

class BackupRecord(Base):
    """Database model for backup records"""
    __tablename__ = 'backup_records'

    id = Column(Integer, primary_key=True)
    backup_id = Column(String, unique=True, index=True)
    backup_type = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    size_bytes = Column(Integer)
    compressed_size_bytes = Column(Integer)
    compression_type = Column(String)
    data_hash = Column(String)
    integrity_verified = Column(Boolean, default=False)
    location = Column(String)
    expires_at = Column(DateTime, nullable=True)
    retention_days = Column(Integer)

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'BackupManager',
    'BackupType',
    'CompressionType',
    'BackupMetadata',
    'BackupRecord'
]
