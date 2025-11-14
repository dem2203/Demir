#!/usr/bin/env python3
"""
🔱 DEMIR AI - Signal Generator v1.0
HAFTA 1-2: Ensemble Signal Generation System

KURALLAR:
✅ Load live trained models (LSTM + Transformer + XGBoost)
✅ Real-time feature extraction
✅ Ensemble voting (3 model consensus)
✅ Signal confidence scoring
✅ Database signal storage
✅ Error loud - all signals logged
✅ ZERO MOCK - Real data only
"""

import os
import psycopg2
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import pickle

# TensorFlow
import tensorflow as tf
from tensorflow import keras

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']

SEQUENCE_LENGTH = 60
CONFIDENCE_THRESHOLD = 0.60  # Min confidence for signal

# ============================================================================
# MODEL MANAGER
# ============================================================================

class EnsembleModelManager:
    """Manage ensemble models"""
    
    @staticmethod
    def load_models(symbol: str) -> Dict:
        """Load all 3 models for symbol"""
        try:
            models = {}
            model_dir = f"models/{symbol}"
            
            # LSTM
            if os.path.exists(f"{model_dir}/lstm_model.h5"):
                models['lstm'] = keras.models.load_model(f"{model_dir}/lstm_model.h5")
                logger.info(f"✅ LSTM loaded for {symbol}")
            
            # Transformer
            if os.path.exists(f"{model_dir}/transformer_model.h5"):
                models['transformer'] = keras.models.load_model(f"{model_dir}/transformer_model.h5")
                logger.info(f"✅ Transformer loaded for {symbol}")
            
            # XGBoost
            if os.path.exists(f"{model_dir}/xgb_model.pkl"):
                with open(f"{model_dir}/xgb_model.pkl", 'rb') as f:
                    models['xgb'] = pickle.load(f)
                logger.info(f"✅ XGBoost loaded for {symbol}")
            
            if len(models) < 3:
                logger.warning(f"⚠️ Only {len(models)}/3 models loaded for {symbol}")
            
            return models if models else None
        
        except Exception as e:
            logger.error(f"❌ Model load failed for {symbol}: {e}")
            raise

# ============================================================================
# FEATURE EXTRACTOR
# ============================================================================

class RealTimeFeatureExtractor:
    """Extract features from database"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
    
    def get_recent_sequence(self, symbol: str, length: int = SEQUENCE_LENGTH) -> Optional[np.ndarray]:
        """Get recent price sequence"""
        try:
            query = """
                SELECT (string_to_array(ohlc_data, ','))[5]::float as close
                FROM feature_store
                WHERE symbol = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """
            
            df = pd.read_sql_query(query, self.db_conn, params=(symbol, length))
            
            if df.empty or len(df) < length:
                logger.warning(f"⚠️ Insufficient data for {symbol}: {len(df)} < {length}")
                return None
            
            prices = df['close'].values[::-1]  # Reverse to chronological order
            
            # Normalize
            prices_min = prices.min()
            prices_max = prices.max()
            if prices_max - prices_min == 0:
                normalized = np.zeros_like(prices)
            else:
                normalized = (prices - prices_min) / (prices_max - prices_min)
            
            return normalized.reshape(1, length, 1)
        
        except Exception as e:
            logger.error(f"❌ Feature extraction failed for {symbol}: {e}")
            return None

# ============================================================================
# SIGNAL GENERATOR
# ============================================================================

class EnsembleSignalGenerator:
    """Generate ensemble signals"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self.feature_extractor = RealTimeFeatureExtractor(db_conn)
    
    def generate_signal(self, symbol: str, models: Dict) -> Tuple[Optional[int], float, Dict]:
        """
        Generate signal: (signal, confidence, details)
        signal: 1=BUY, 0=SELL, -1=HOLD
        confidence: 0-1
        """
        try:
            # Get features
            features = self.feature_extractor.get_recent_sequence(symbol)
            if features is None:
                return -1, 0, {}
            
            # Get predictions from each model
            lstm_pred = models['lstm'].predict(features, verbose=0)[0][0]
            transformer_pred = models['transformer'].predict(features, verbose=0)[0][0]
            xgb_pred = models['xgb'].predict(features.reshape(1, -1))[0]
            
            # Ensemble voting (majority)
            votes = [
                1 if lstm_pred > 0.5 else 0,
                1 if transformer_pred > 0.5 else 0,
                1 if xgb_pred > 0.5 else 0
            ]
            
            vote_sum = sum(votes)
            
            # Signal decision
            if vote_sum >= 2:
                signal = 1  # BUY
                confidence = np.mean([lstm_pred, transformer_pred, xgb_pred])
            else:
                signal = 0  # SELL
                confidence = 1 - np.mean([lstm_pred, transformer_pred, xgb_pred])
            
            # Hold if confidence too low
            if confidence < CONFIDENCE_THRESHOLD:
                signal = -1
            
            details = {
                'lstm': float(lstm_pred),
                'transformer': float(transformer_pred),
                'xgb': float(xgb_pred),
                'votes': vote_sum,
                'confidence': float(confidence)
            }
            
            logger.info(f"📊 {symbol} Signal: {['SELL', 'BUY', 'HOLD'][signal+1]} (Confidence: {confidence:.2%})")
            
            return signal, confidence, details
        
        except Exception as e:
            logger.error(f"❌ Signal generation failed for {symbol}: {e}")
            return -1, 0, {}

# ============================================================================
# SIGNAL STORAGE
# ============================================================================

class SignalStorage:
    """Store signals in database"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
    
    def save_signal(self, symbol: str, signal: int, confidence: float, details: Dict):
        """Save signal to database"""
        try:
            cur = self.db_conn.cursor()
            
            insert_query = """
                INSERT INTO signal_log 
                (timestamp, symbol, signal, confidence, details)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            signal_text = {-1: 'HOLD', 0: 'SELL', 1: 'BUY'}[signal]
            
            cur.execute(insert_query, (
                datetime.now(),
                symbol,
                signal_text,
                confidence,
                json.dumps(details) if details else None
            ))
            
            self.db_conn.commit()
            cur.close()
            
            logger.info(f"💾 Signal saved: {symbol} {signal_text} ({confidence:.2%})")
        
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"❌ Failed to save signal: {e}")

# ============================================================================
# SIGNAL VALIDATOR
# ============================================================================

class SignalValidator:
    """Validate signals before execution"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
    
    def validate_signal(self, symbol: str, signal: int, confidence: float) -> bool:
        """Validate signal rules"""
        try:
            # Rule 1: Confidence threshold
            if confidence < CONFIDENCE_THRESHOLD:
                logger.warning(f"❌ {symbol}: Confidence {confidence:.2%} < {CONFIDENCE_THRESHOLD:.0%}")
                return False
            
            # Rule 2: Recent signal check (avoid duplicates within 1 hour)
            query = """
                SELECT COUNT(*) as recent_signals
                FROM signal_log
                WHERE symbol = %s 
                AND signal = %s
                AND timestamp >= NOW() - INTERVAL '1 hour'
            """
            
            signal_text = {-1: 'HOLD', 0: 'SELL', 1: 'BUY'}[signal]
            df = pd.read_sql_query(query, self.db_conn, params=(symbol, signal_text))
            
            if df['recent_signals'].values[0] > 0:
                logger.warning(f"⚠️ {symbol}: Recent {signal_text} signal exists")
                return False
            
            # Rule 3: Win rate check
            query = """
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades
                FROM manual_trades
                WHERE symbol = %s
                AND exit_time IS NOT NULL
            """
            
            df = pd.read_sql_query(query, self.db_conn, params=(symbol,))
            total = df['total_trades'].values[0]
            
            if total > 10:
                win_rate = df['winning_trades'].values[0] / total
                if win_rate < 0.40:
                    logger.warning(f"⚠️ {symbol}: Win rate {win_rate:.1%} too low")
                    return False
            
            logger.info(f"✅ {symbol} signal validated")
            return True
        
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    try:
        logger.info("=" * 80)
        logger.info("🚀 DEMIR AI - SIGNAL GENERATOR (HAFTA 1-2)")
        logger.info("=" * 80)
        
        db_conn = psycopg2.connect(DATABASE_URL)
        
        signal_gen = EnsembleSignalGenerator(db_conn)
        signal_storage = SignalStorage(db_conn)
        signal_validator = SignalValidator(db_conn)
        model_mgr = EnsembleModelManager()
        
        # Generate signals for all symbols
        for symbol in SYMBOLS:
            logger.info(f"\n📊 Processing {symbol}...")
            
            try:
                # Load models
                models = model_mgr.load_models(symbol)
                if not models:
                    logger.warning(f"⚠️ Skipping {symbol} - no models")
                    continue
                
                # Generate signal
                signal, confidence, details = signal_gen.generate_signal(symbol, models)
                
                if signal == -1:
                    logger.info(f"⏸️ {symbol}: HOLD")
                    continue
                
                # Validate signal
                if not signal_validator.validate_signal(symbol, signal, confidence):
                    logger.info(f"❌ {symbol} signal rejected")
                    continue
                
                # Store signal
                signal_storage.save_signal(symbol, signal, confidence, details)
            
            except Exception as e:
                logger.error(f"❌ Error processing {symbol}: {e}")
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ SIGNAL GENERATION COMPLETED")
        logger.info("=" * 80)
        
        db_conn.close()
    
    except Exception as e:
        logger.critical(f"❌ FATAL ERROR: {e}")
        raise

if __name__ == "__main__":
    import json
    main()
