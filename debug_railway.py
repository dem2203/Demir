"""
🔴 DIAGNOSTIC & DEBUG SCRIPT
Full debugging tool to identify 404 error root cause
Çalıştır ve çıktıyı gönder!

Location: GitHub Root / debug_railway.py
Date: 2025-11-16 12:20 CET
"""

import os
import sys
import subprocess
import requests
import json
from datetime import datetime

print("=" * 80)
print("🔴 DEMIR AI - RAILWAY DEBUG DIAGNOSTIC")
print("=" * 80)

# ============================================================================
# 1. ENVIRONMENT VARIABLES CHECK
# ============================================================================

print("\n1️⃣ ENVIRONMENT VARIABLES:")
print("-" * 80)

required_vars = [
    'BINANCE_API_KEY',
    'BINANCE_API_SECRET',
    'DATABASE_URL',
    'TELEGRAM_TOKEN',
    'TELEGRAM_CHAT_ID',
    'PORT'
]

env_status = {}
for var in required_vars:
    value = os.getenv(var)
    status = "✅ SET" if value else "❌ MISSING"
    env_status[var] = status
    print(f"{var:30} {status}")
    if value and var not in ['BINANCE_API_SECRET', 'DATABASE_URL']:
        print(f"  → Value: {value[:20]}...")

# ============================================================================
# 2. PYTHON IMPORTS CHECK
# ============================================================================

print("\n2️⃣ PYTHON IMPORTS CHECK:")
print("-" * 80)

imports_to_check = [
    'psycopg2',
    'requests',
    'numpy',
    'pandas',
    'dotenv',
    'logging'
]

for module_name in imports_to_check:
    try:
        __import__(module_name)
        print(f"✅ {module_name:20} - OK")
    except ImportError as e:
        print(f"❌ {module_name:20} - FAILED: {e}")

# ============================================================================
# 3. CUSTOM IMPORTS CHECK
# ============================================================================

print("\n3️⃣ CUSTOM LAYER IMPORTS:")
print("-" * 80)

try:
    from layers.sentiment import SENTIMENT_LAYERS
    print(f"✅ Sentiment layers:    {len(SENTIMENT_LAYERS)} layers loaded")
except Exception as e:
    print(f"❌ Sentiment layers:    FAILED - {e}")

try:
    from layers.ml import ML_LAYERS
    print(f"✅ ML layers:           {len(ML_LAYERS)} layers loaded")
except Exception as e:
    print(f"❌ ML layers:           FAILED - {e}")

try:
    from ai_brain_ensemble import AiBrainEnsemble
    print(f"✅ AI Brain Ensemble:   Imported successfully")
except Exception as e:
    print(f"❌ AI Brain Ensemble:   FAILED - {e}")

try:
    from trading_executor import TradingExecutor
    print(f"✅ Trading Executor:    Imported successfully")
except Exception as e:
    print(f"❌ Trading Executor:    FAILED - {e}")

# ============================================================================
# 4. DATABASE CONNECTION CHECK
# ============================================================================

print("\n4️⃣ DATABASE CONNECTION:")
print("-" * 80)

try:
    import psycopg2
    db_url = os.getenv('DATABASE_URL')
    
    if db_url:
        try:
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            print(f"✅ PostgreSQL:          Connected successfully")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"❌ PostgreSQL:          Connection failed - {e}")
    else:
        print(f"❌ PostgreSQL:          DATABASE_URL not set")
except Exception as e:
    print(f"❌ PostgreSQL:          Error - {e}")

# ============================================================================
# 5. BINANCE API CHECK
# ============================================================================

print("\n5️⃣ BINANCE API CHECK:")
print("-" * 80)

try:
    response = requests.get('https://fapi.binance.com/fapi/v1/ticker/price?symbol=BTCUSDT', timeout=5)
    if response.status_code == 200:
        data = response.json()
        price = data.get('price')
        print(f"✅ Binance API:         Connected")
        print(f"  → BTC Price: ${price}")
    else:
        print(f"❌ Binance API:         Status code {response.status_code}")
except Exception as e:
    print(f"❌ Binance API:          Failed - {e}")

# ============================================================================
# 6. HEALTH SERVER CHECK
# ============================================================================

print("\n6️⃣ HEALTH SERVER CHECK:")
print("-" * 80)

PORT = int(os.getenv('PORT', 8000))
print(f"Expected PORT: {PORT}")

# Test local health endpoint
try:
    response = requests.get(f'http://localhost:{PORT}/health', timeout=2)
    if response.status_code == 200:
        print(f"✅ Health Server:       Running on port {PORT}")
        print(f"  → Response: {response.text}")
    else:
        print(f"❌ Health Server:       Status code {response.status_code}")
except requests.exceptions.ConnectionRefusedError:
    print(f"❌ Health Server:       NOT RUNNING on port {PORT}")
except Exception as e:
    print(f"❌ Health Server:       Error - {e}")

# ============================================================================
# 7. MAIN.PY EXECUTION TEST
# ============================================================================

print("\n7️⃣ MAIN.PY EXECUTION TEST:")
print("-" * 80)

try:
    # Try to import and initialize AI Brain
    from ai_brain_ensemble import AiBrainEnsemble
    
    print("Initializing AI Brain...")
    ai_brain = AiBrainEnsemble()
    
    health = ai_brain.get_health_status()
    print(f"✅ AI Brain:            Initialized successfully")
    print(f"  → Sentiment layers: {health['sentiment_layers']['count']}")
    print(f"  → ML layers: {health['ml_layers']['count']}")
    print(f"  → Status: {health['status']}")
    
except Exception as e:
    print(f"❌ AI Brain:            Failed to initialize - {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# 8. DOCKER INFORMATION
# ============================================================================

print("\n8️⃣ DOCKER INFORMATION:")
print("-" * 80)

try:
    import platform
    print(f"Python Version:      {platform.python_version()}")
    print(f"Platform:            {platform.platform()}")
    print(f"Current PID:         {os.getpid()}")
    
    # Check if running in Docker
    if os.path.exists('/.dockerenv'):
        print(f"Running in Docker:   ✅ YES")
    else:
        print(f"Running in Docker:   ⚠️ NO (running locally)")
        
except Exception as e:
    print(f"Error getting info: {e}")

# ============================================================================
# 9. RAILWAY SPECIFIC CHECKS
# ============================================================================

print("\n9️⃣ RAILWAY SPECIFIC CHECKS:")
print("-" * 80)

railway_vars = [
    'RAILWAY_ENVIRONMENT_NAME',
    'RAILWAY_PROJECT_ID',
    'RAILWAY_SERVICE_ID',
    'RAILWAY_DEPLOYMENT_ID'
]

for var in railway_vars:
    value = os.getenv(var)
    status = "✅" if value else "⚠️"
    print(f"{status} {var:35} {value or 'NOT SET'}")

# ============================================================================
# 10. FILE STRUCTURE CHECK
# ============================================================================

print("\n🔟 FILE STRUCTURE CHECK:")
print("-" * 80)

required_files = [
    'main.py',
    'ai_brain_ensemble.py',
    'requirements.txt',
    'Dockerfile',
    'layers/__init__.py',
    'layers/sentiment/__init__.py',
    'layers/ml/__init__.py'
]

for file_path in required_files:
    exists = os.path.exists(file_path)
    status = "✅" if exists else "❌"
    
    if exists:
        size = os.path.getsize(file_path)
        print(f"{status} {file_path:40} ({size} bytes)")
    else:
        print(f"{status} {file_path:40} MISSING")

# ============================================================================
# 11. FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("📋 DIAGNOSTIC SUMMARY:")
print("=" * 80)

issues = []

if not os.getenv('DATABASE_URL'):
    issues.append("❌ DATABASE_URL not set")
if not os.getenv('BINANCE_API_KEY'):
    issues.append("❌ BINANCE_API_KEY not set")
if not os.path.exists('main.py'):
    issues.append("❌ main.py file missing")
if not os.path.exists('Dockerfile'):
    issues.append("❌ Dockerfile missing")

if issues:
    print("\n⚠️ ISSUES FOUND:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("\n✅ No critical issues found")
    print("   If 404 still occurs, check:")
    print("   1. Railway logs for actual error messages")
    print("   2. Database connectivity")
    print("   3. Health server port binding")

print("\n" + "=" * 80)
print(f"Diagnostic completed: {datetime.now().isoformat()}")
print("=" * 80)
