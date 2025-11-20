#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 DEMIR AI - DATABASE BACKUP SCRIPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OTOMATIK DATABASE BACKUP

Features:
    ✅ PostgreSQL backup (pg_dump)
    ✅ Compression (gzip)
    ✅ Timestamped files
    ✅ Old backup cleanup (keep last 30 days)
    ✅ Telegram notification
    ✅ Error handling

Usage:
    # Manual
    python scripts/backup_database.py
    
    # Cron (daily at 2 AM)
    0 2 * * * python /path/to/scripts/backup_database.py

AUTHOR: DEMIR AI Research Team
DATE: 2025-11-20
VERSION: 7.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sys
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BACKUP_DIR = Path("backups/database")
BACKUP_RETENTION_DAYS = 30  # Keep backups for 30 days
DATABASE_URL = os.getenv("DATABASE_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ============================================================================
# BACKUP FUNCTION
# ============================================================================

def create_backup():
    """
    Create PostgreSQL database backup
    
    Returns:
        tuple: (success, backup_path, size_mb)
    """
    try:
        logger.info("💾 Starting database backup...")
        
        # Create backup directory
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"demir_ai_backup_{timestamp}.sql.gz"
        backup_path = BACKUP_DIR / backup_filename
        
        # Parse DATABASE_URL
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Extract connection details from DATABASE_URL
        # Format: postgresql://user:password@host:port/database
        import re
        match = re.match(
            r'postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+)',
            DATABASE_URL
        )
        
        if not match:
            raise ValueError("Invalid DATABASE_URL format")
        
        user, password, host, port, database = match.groups()
        
        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        # Run pg_dump with compression
        logger.info(f"🗄️ Dumping database: {database}")
        
        dump_command = [
            'pg_dump',
            '-h', host,
            '-p', port,
            '-U', user,
            '-d', database,
            '--no-owner',
            '--no-acl',
            '--clean',
            '--if-exists'
        ]
        
        # Pipe to gzip
        with open(backup_path, 'wb') as f:
            dump_process = subprocess.Popen(
                dump_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            gzip_process = subprocess.Popen(
                ['gzip'],
                stdin=dump_process.stdout,
                stdout=f,
                stderr=subprocess.PIPE
            )
            
            dump_process.stdout.close()
            gzip_process.communicate()
        
        # Check for errors
        if dump_process.returncode != 0:
            error = dump_process.stderr.read().decode()
            raise Exception(f"pg_dump failed: {error}")
        
        # Get backup size
        size_bytes = backup_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        
        logger.info(f"✅ Backup created: {backup_filename} ({size_mb:.2f} MB)")
        
        return True, backup_path, size_mb
        
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        return False, None, 0

# ============================================================================
# CLEANUP OLD BACKUPS
# ============================================================================

def cleanup_old_backups():
    """
    Delete backups older than BACKUP_RETENTION_DAYS
    """
    try:
        logger.info("🧹 Cleaning up old backups...")
        
        if not BACKUP_DIR.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=BACKUP_RETENTION_DAYS)
        deleted_count = 0
        
        for backup_file in BACKUP_DIR.glob("demir_ai_backup_*.sql.gz"):
            # Get file modification time
            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            if file_time < cutoff_date:
                logger.info(f"🗑️ Deleting old backup: {backup_file.name}")
                backup_file.unlink()
                deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"✅ Deleted {deleted_count} old backup(s)")
        else:
            logger.info("✅ No old backups to delete")
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")

# ============================================================================
# TELEGRAM NOTIFICATION
# ============================================================================

def send_telegram_notification(success, backup_path=None, size_mb=0, error=None):
    """
    Send backup status to Telegram
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("⚠️ Telegram credentials not configured")
        return
    
    try:
        if success:
            message = f"""
💾 <b>DATABASE BACKUP SUCCESSFUL</b>

<b>File:</b> {backup_path.name if backup_path else 'unknown'}
<b>Size:</b> {size_mb:.2f} MB
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
<b>Retention:</b> {BACKUP_RETENTION_DAYS} days

✅ Backup completed successfully
            """
        else:
            message = f"""
🔥 <b>DATABASE BACKUP FAILED</b>

<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
<b>Error:</b> {error or 'Unknown error'}

❌ Please check logs immediately!
            """
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message.strip(),
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ Telegram notification sent")
        else:
            logger.error(f"❌ Telegram notification failed: {response.status_code}")
        
    except Exception as e:
        logger.error(f"❌ Failed to send Telegram notification: {e}")

# ============================================================================
# DATABASE BACKUP LOG
# ============================================================================

def log_backup_to_database(success, backup_path=None, size_mb=0, error=None):
    """
    Log backup operation to database
    """
    try:
        import psycopg2
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        query = """
            INSERT INTO database_backups (
                backup_type, backup_location, backup_size_mb,
                status, error_message
            ) VALUES (
                'full', %s, %s, %s, %s
            )
        """
        
        location = str(backup_path) if backup_path else 'N/A'
        status = 'completed' if success else 'failed'
        
        cursor.execute(query, (location, size_mb, status, error))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Backup logged to database")
        
    except Exception as e:
        logger.error(f"❌ Failed to log backup: {e}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """
    Main backup routine
    """
    logger.info("="*80)
    logger.info("💾 DEMIR AI - DATABASE BACKUP")
    logger.info("="*80)
    
    try:
        # 1. Create backup
        success, backup_path, size_mb = create_backup()
        
        if not success:
            error = "Backup creation failed"
            send_telegram_notification(False, error=error)
            log_backup_to_database(False, error=error)
            sys.exit(1)
        
        # 2. Cleanup old backups
        cleanup_old_backups()
        
        # 3. Send notification
        send_telegram_notification(True, backup_path, size_mb)
        
        # 4. Log to database
        log_backup_to_database(True, backup_path, size_mb)
        
        logger.info("="*80)
        logger.info("✅ BACKUP COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"❌ BACKUP FAILED: {e}")
        send_telegram_notification(False, error=str(e))
        log_backup_to_database(False, error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
