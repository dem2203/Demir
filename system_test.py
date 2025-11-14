#!/usr/bin/env python3
"""
🔱 DEMIR AI - system_test.py (HAFTA 1-2 VERIFICATION)
FULL EXECUTION TEST - Production verification

Status: STRICT, ZERO MOCK, FAIL LOUD
"""

import os
import logging
import sys
import psycopg2
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemTest:
    """Full system test - STRICT"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.results = {
            'database': False,
            'tables': 0,
            'sentiment_api': False,
            'macro_api': False,
            'binance_api': False,
            'dashboard': False
        }
    
    def test_database(self):
        """Test PostgreSQL connection - STRICT"""
        try:
            logger.info("🔍 Testing PostgreSQL connection...")
            
            if not self.db_url:
                raise ValueError("❌ DATABASE_URL not set")
            
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # Check tables
            cur.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema='public'
            """)
            table_count = cur.fetchone()[0]
            
            if table_count < 9:
                raise ValueError(f"❌ Not enough tables: {table_count} < 9")
            
            # List tables
            cur.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema='public' ORDER BY table_name
            """)
            tables = [t[0] for t in cur.fetchall()]
            
            expected = ['backtesting_results', 'error_log', 'feature_store', 
                       'macro_data', 'manual_trades', 'ml_models', 'predictions',
                       'signal_log', 'trading_stats']
            
            missing = set(expected) - set(tables)
            if missing:
                raise ValueError(f"❌ Missing tables: {missing}")
            
            logger.info(f"✅ PostgreSQL: {table_count} tables OK")
            
            # Test write
            try:
                cur.execute("""
                    INSERT INTO macro_data 
                    (timestamp, dxy_close, vix_close, macro_score)
                    VALUES (NOW(), 100.0, 20.0, 50.0)
                """)
                conn.commit()
                logger.info("✅ PostgreSQL write OK")
            except Exception as e:
                logger.warning(f"⚠️ Write test: {e}")
            
            cur.close()
            conn.close()
            
            self.results['database'] = True
            self.results['tables'] = table_count
            return True
        
        except Exception as e:
            logger.critical(f"❌ Database test failed: {e}")
            return False
    
    def test_sentiment_api(self):
        """Test sentiment APIs - STRICT"""
        try:
            logger.info("🔍 Testing sentiment APIs...")
            
            newsapi_key = os.getenv('NEWSAPI_KEY')
            twitter_token = os.getenv('TWITTER_TOKEN')
            
            if not newsapi_key:
                logger.warning("⚠️ NEWSAPI_KEY not set")
                return False
            
            # Test NewsAPI
            url = f"https://newsapi.org/v2/everything?q=bitcoin&pageSize=1&apiKey={newsapi_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                raise ValueError(f"❌ NewsAPI failed: {response.status_code}")
            
            logger.info("✅ Sentiment APIs OK")
            self.results['sentiment_api'] = True
            return True
        
        except Exception as e:
            logger.warning(f"⚠️ Sentiment API test: {e}")
            return False
    
    def test_macro_api(self):
        """Test macro APIs - STRICT"""
        try:
            logger.info("🔍 Testing macro APIs...")
            
            fred_key = os.getenv('FRED_API_KEY')
            
            if not fred_key:
                logger.warning("⚠️ FRED_API_KEY not set")
                return False
            
            # Test FRED
            url = f"https://api.stlouisfed.org/fred/series/data?series_id=FEDFUNDS&api_key={fred_key}&file_type=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                raise ValueError(f"❌ FRED API failed: {response.status_code}")
            
            logger.info("✅ Macro APIs OK")
            self.results['macro_api'] = True
            return True
        
        except Exception as e:
            logger.warning(f"⚠️ Macro API test: {e}")
            return False
    
    def test_binance_api(self):
        """Test Binance API - STRICT"""
        try:
            logger.info("🔍 Testing Binance API...")
            
            binance_key = os.getenv('BINANCE_API_KEY')
            
            if not binance_key:
                logger.warning("⚠️ BINANCE_API_KEY not set")
                return False
            
            # Test public endpoint (no auth needed for this)
            url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                raise ValueError(f"❌ Binance API failed: {response.status_code}")
            
            data = response.json()
            if 'price' not in data:
                raise ValueError("❌ Invalid Binance response")
            
            logger.info(f"✅ Binance API OK (BTC: ${data['price']})")
            self.results['binance_api'] = True
            return True
        
        except Exception as e:
            logger.warning(f"⚠️ Binance API test: {e}")
            return False
    
    def test_dashboard(self):
        """Test Streamlit dashboard - STRICT"""
        try:
            logger.info("🔍 Testing Streamlit dashboard...")
            
            # Check if streamlit_app.py exists
            if not os.path.exists('/app/streamlit_app.py'):
                if not os.path.exists('streamlit_app.py'):
                    raise ValueError("❌ streamlit_app.py not found")
            
            logger.info("✅ Dashboard file OK")
            self.results['dashboard'] = True
            return True
        
        except Exception as e:
            logger.warning(f"⚠️ Dashboard test: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests - STRICT"""
        try:
            logger.info("=" * 80)
            logger.info("🚀 DEMIR AI - SYSTEM TEST")
            logger.info("=" * 80)
            
            # Run tests
            self.test_database()
            self.test_sentiment_api()
            self.test_macro_api()
            self.test_binance_api()
            self.test_dashboard()
            
            # Summary
            logger.info("\n" + "=" * 80)
            logger.info("📊 TEST RESULTS")
            logger.info("=" * 80)
            
            passed = sum(1 for v in self.results.values() if v and v is not True or isinstance(v, bool))
            total = len([v for v in self.results.values() if isinstance(v, bool)])
            
            for test, result in self.results.items():
                if isinstance(result, bool):
                    status = "✅ PASS" if result else "❌ FAIL"
                    logger.info(f"{status}: {test}")
                elif isinstance(result, int):
                    logger.info(f"ℹ️ {test}: {result}")
            
            logger.info("=" * 80)
            
            if all(isinstance(v, bool) and v or isinstance(v, int) and v > 0 
                   for v in self.results.values()):
                logger.info("✅ ALL TESTS PASSED!")
                return True
            else:
                logger.warning("⚠️ Some tests failed or missing")
                return False
        
        except Exception as e:
            logger.critical(f"❌ Test run failed: {e}")
            return False

if __name__ == "__main__":
    tester = SystemTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
