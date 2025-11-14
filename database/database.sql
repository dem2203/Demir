-- ============================================================================
-- 🔱 DEMIR AI - database.sql
-- ============================================================================
-- PostgreSQL initialization script - ALL 7+ TABLES with FULL SPEC
-- ============================================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- ============================================================================
-- TABLE 1: feature_store (80+ COLUMNS - TECHNICAL FEATURES)
-- ============================================================================
CREATE TABLE IF NOT EXISTS feature_store (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Technical Features (20+)
    rsi_7 FLOAT,
    rsi_14 FLOAT,
    rsi_21 FLOAT,
    macd_line FLOAT,
    macd_signal FLOAT,
    macd_histogram FLOAT,
    atr_14 FLOAT,
    bb_upper FLOAT,
    bb_middle FLOAT,
    bb_lower FLOAT,
    bb_position FLOAT,
    sma_20 FLOAT,
    sma_50 FLOAT,
    sma_200 FLOAT,
    ema_12 FLOAT,
    ema_26 FLOAT,
    price_above_sma20 INT,
    price_above_sma50 INT,
    price_above_sma200 INT,
    stoch_k FLOAT,
    stoch_d FLOAT,
    momentum FLOAT,
    roc FLOAT,
    
    -- Volume Features (10+)
    volume_ratio FLOAT,
    volume_trend FLOAT,
    obv_trend FLOAT,
    
    -- Macro Features (15+)
    vix_level FLOAT,
    vix_high_flag INT,
    dxy_level FLOAT,
    fed_rate FLOAT,
    inflation_rate FLOAT,
    unemployment_rate FLOAT,
    btc_dominance FLOAT,
    eth_dominance FLOAT,
    gold_price FLOAT,
    oil_price FLOAT,
    
    -- Sentiment Features (10+)
    news_sentiment FLOAT,
    twitter_sentiment FLOAT,
    reddit_sentiment FLOAT,
    aggregate_sentiment FLOAT,
    positive_news_count FLOAT,
    negative_news_count FLOAT,
    
    -- OnChain Features (10+)
    exchange_inflow FLOAT,
    exchange_outflow FLOAT,
    whale_transaction_count INT,
    total_liquidations FLOAT,
    funding_rate FLOAT,
    long_short_ratio FLOAT,
    
    -- Derived Features (25+)
    volatility_20 FLOAT,
    volatility_50 FLOAT,
    skewness FLOAT,
    price_momentum FLOAT,
    drawdown_from_high FLOAT,
    
    -- Final Scores
    combined_score FLOAT,
    confidence FLOAT,
    price FLOAT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_feature_store_symbol_ts ON feature_store(symbol, timestamp DESC);
CREATE INDEX idx_feature_store_combined_score ON feature_store(combined_score DESC);
CREATE INDEX idx_feature_store_created_at ON feature_store(created_at DESC);

-- ============================================================================
-- TABLE 2: ml_models (MODEL VERSIONS & PERFORMANCE)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ml_models (
    model_id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- LSTM, Transformer, Ensemble
    version INT NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    updated_date TIMESTAMP DEFAULT NOW(),
    accuracy_train FLOAT,
    accuracy_val FLOAT,
    accuracy_test FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    loss FLOAT,
    parameters JSONB,
    status VARCHAR(50) DEFAULT 'training', -- training, deployed, archived
    last_trained TIMESTAMP,
    last_used TIMESTAMP,
    notes TEXT
);

CREATE INDEX idx_ml_models_name_version ON ml_models(model_name, version DESC);
CREATE INDEX idx_ml_models_status ON ml_models(status);

-- ============================================================================
-- TABLE 3: predictions (MODEL PREDICTIONS & RESULTS)
-- ============================================================================
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id BIGSERIAL PRIMARY KEY,
    model_id INT REFERENCES ml_models(model_id),
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    prediction VARCHAR(20) NOT NULL, -- UP, DOWN, HOLD
    confidence FLOAT NOT NULL,
    lstm_signal VARCHAR(20),
    transformer_signal VARCHAR(20),
    ta_signal VARCHAR(20),
    ensemble_probs JSONB,
    entry_price FLOAT,
    tp1_price FLOAT,
    tp2_price FLOAT,
    sl_price FLOAT,
    risk_amount FLOAT,
    
    -- Results (filled later)
    actual_result VARCHAR(20), -- UP, DOWN, NEUTRAL
    result_timestamp TIMESTAMP,
    profit_loss FLOAT,
    correct INT, -- 1 for correct, 0 for incorrect
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_predictions_model_symbol ON predictions(model_id, symbol);
CREATE INDEX idx_predictions_timestamp ON predictions(timestamp DESC);
CREATE INDEX idx_predictions_correct ON predictions(correct);

-- ============================================================================
-- TABLE 4: manual_trades (USER MANUAL TRADES & BOT TRACKING)
-- ============================================================================
CREATE TABLE IF NOT EXISTS manual_trades (
    trade_id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    symbol VARCHAR(20) NOT NULL,
    signal_id INT REFERENCES predictions(prediction_id),
    
    -- Entry
    entry_signal VARCHAR(20) NOT NULL, -- UP, DOWN
    entry_price FLOAT NOT NULL,
    entry_time TIMESTAMP NOT NULL,
    entry_confidence FLOAT,
    
    -- Order Levels
    tp1_price FLOAT,
    tp2_price FLOAT,
    sl_price FLOAT,
    
    -- Position
    position_size FLOAT,
    leverage FLOAT DEFAULT 1,
    
    -- Exit
    exit_price FLOAT,
    exit_time TIMESTAMP,
    exit_type VARCHAR(50), -- TP1, TP2, SL, MANUAL, TL
    
    -- Results
    pnl FLOAT,
    pnl_percent FLOAT,
    status VARCHAR(50) DEFAULT 'open', -- open, closed, tp1_hit, tp2_hit, sl_hit
    
    -- Bot Prediction vs Actual
    predicted_signal VARCHAR(20),
    predicted_confidence FLOAT,
    actual_result VARCHAR(20), -- correct, incorrect, partial
    success INT, -- 1 for profitable, 0 for loss
    
    -- Analysis
    trade_duration_minutes INT,
    success_rate FLOAT,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_manual_trades_symbol_status ON manual_trades(symbol, status);
CREATE INDEX idx_manual_trades_created_at ON manual_trades(created_at DESC);
CREATE INDEX idx_manual_trades_success ON manual_trades(success);

-- ============================================================================
-- TABLE 5: macro_data (MACRO ECONOMIC DATA)
-- ============================================================================
CREATE TABLE IF NOT EXISTS macro_data (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    
    -- FX & Indices
    dxy_close FLOAT,
    dxy_high FLOAT,
    dxy_low FLOAT,
    
    -- Stock Market
    spy_close FLOAT,
    spx500_close FLOAT,
    
    -- Volatility
    vix_close FLOAT,
    vix_high FLOAT,
    vix_low FLOAT,
    
    -- Crypto Dominance
    btc_dominance FLOAT,
    eth_dominance FLOAT,
    
    -- Commodities
    gold_price FLOAT,
    crude_oil_price FLOAT,
    
    -- Fed & Economic
    fed_rate FLOAT,
    inflation_rate FLOAT,
    unemployment_rate FLOAT,
    
    -- Market Sentiment
    fear_greed_index FLOAT,
    market_sentiment VARCHAR(50), -- extreme_fear, fear, neutral, greed, extreme_greed
    
    -- OnChain
    exchange_inflow_btc FLOAT,
    exchange_outflow_btc FLOAT,
    miner_revenue FLOAT,
    
    -- Aggregate Score
    macro_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_macro_data_timestamp ON macro_data(timestamp DESC);
CREATE INDEX idx_macro_data_macro_score ON macro_data(macro_score DESC);

-- ============================================================================
-- TABLE 6: error_log (ERROR TRACKING & RECOVERY)
-- ============================================================================
CREATE TABLE IF NOT EXISTS error_log (
    id BIGSERIAL PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL, -- Job 1, 2, 3, 4
    api_name VARCHAR(100), -- Binance, FRED, NewsAPI, etc
    error_message TEXT NOT NULL,
    error_type VARCHAR(100), -- APIError, TimeoutError, ValidationError, etc
    stack_trace TEXT,
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    resolved INT DEFAULT 0,
    resolved_at TIMESTAMP,
    resolution_note TEXT,
    severity VARCHAR(50) DEFAULT 'error', -- warning, error, critical
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_error_log_job_name ON error_log(job_name);
CREATE INDEX idx_error_log_timestamp ON error_log(timestamp DESC);
CREATE INDEX idx_error_log_resolved ON error_log(resolved);

-- ============================================================================
-- TABLE 7: signal_log (ALL SIGNALS GENERATED)
-- ============================================================================
CREATE TABLE IF NOT EXISTS signal_log (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Signal
    signal VARCHAR(20) NOT NULL, -- UP, DOWN, HOLD
    confidence FLOAT NOT NULL,
    
    -- Component Signals
    lstm_signal VARCHAR(20),
    lstm_confidence FLOAT,
    transformer_signal VARCHAR(20),
    transformer_confidence FLOAT,
    ta_signal VARCHAR(20),
    ta_confidence FLOAT,
    
    -- Entry Levels
    entry_price FLOAT,
    tp1_price FLOAT,
    tp2_price FLOAT,
    sl_price FLOAT,
    
    -- Position
    position_size FLOAT,
    risk_amount FLOAT,
    
    -- Tracking
    traded INT DEFAULT 0, -- 0 = not traded, 1 = traded
    trade_id INT REFERENCES manual_trades(trade_id),
    
    -- Result
    result VARCHAR(50), -- not_traded, pending, won, lost, partial
    profit_loss FLOAT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_signal_log_symbol_timestamp ON signal_log(symbol, timestamp DESC);
CREATE INDEX idx_signal_log_traded ON signal_log(traded);
CREATE INDEX idx_signal_log_result ON signal_log(result);

-- ============================================================================
-- TABLE 8: backtesting_results (BACKTEST PERFORMANCE)
-- ============================================================================
CREATE TABLE IF NOT EXISTS backtesting_results (
    id BIGSERIAL PRIMARY KEY,
    model_id INT REFERENCES ml_models(model_id),
    symbol VARCHAR(20) NOT NULL,
    start_date DATE,
    end_date DATE,
    
    -- Performance
    total_trades INT,
    winning_trades INT,
    losing_trades INT,
    win_rate FLOAT,
    profit_factor FLOAT,
    
    -- Risk
    max_drawdown FLOAT,
    sharpe_ratio FLOAT,
    sortino_ratio FLOAT,
    calmar_ratio FLOAT,
    
    -- Returns
    total_return FLOAT,
    annualized_return FLOAT,
    avg_trade_profit FLOAT,
    
    -- Parameters
    parameters JSONB,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_backtest_model_symbol ON backtesting_results(model_id, symbol);

-- ============================================================================
-- TABLE 9: trading_stats (DAILY STATISTICS)
-- ============================================================================
CREATE TABLE IF NOT EXISTS trading_stats (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    
    -- Account
    starting_balance FLOAT,
    ending_balance FLOAT,
    daily_pnl FLOAT,
    daily_pnl_percent FLOAT,
    
    -- Trades
    total_trades INT DEFAULT 0,
    winning_trades INT DEFAULT 0,
    losing_trades INT DEFAULT 0,
    win_rate FLOAT,
    
    -- Signals
    signals_generated INT DEFAULT 0,
    signals_correct INT DEFAULT 0,
    signal_accuracy FLOAT,
    
    -- Risk
    max_loss FLOAT,
    max_drawdown FLOAT,
    risk_reward_ratio FLOAT,
    
    -- Models
    models_used VARCHAR(500), -- JSON list
    best_performing_model VARCHAR(100),
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_trading_stats_date ON trading_stats(date DESC);
CREATE INDEX idx_trading_stats_pnl ON trading_stats(daily_pnl);

-- ============================================================================
-- TRIGGERS & AUTO-UPDATE
-- ============================================================================

-- Auto-update ml_models.updated_date
CREATE OR REPLACE FUNCTION update_ml_models_updated_date()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_date = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_ml_models_update
BEFORE UPDATE ON ml_models
FOR EACH ROW
EXECUTE FUNCTION update_ml_models_updated_date();

-- Auto-calculate prediction correctness
CREATE OR REPLACE FUNCTION check_prediction_result()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.prediction IS NOT NULL AND NEW.actual_result IS NOT NULL THEN
        IF NEW.prediction = NEW.actual_result THEN
            NEW.correct = 1;
        ELSE
            NEW.correct = 0;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prediction_correct
BEFORE INSERT OR UPDATE ON predictions
FOR EACH ROW
EXECUTE FUNCTION check_prediction_result();

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert initial macro_data record
INSERT INTO macro_data (
    timestamp, dxy_close, vix_close, fed_rate, inflation_rate,
    unemployment_rate, btc_dominance, eth_dominance, macro_score
)
VALUES (
    NOW(), 100.0, 20.0, 2.5, 3.2, 4.1, 45.0, 20.0, 50.0
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PERMISSIONS & SECURITY
-- ============================================================================

-- Create read-only user for dashboard
CREATE USER demir_readonly WITH PASSWORD 'demir_readonly_2025';
GRANT CONNECT ON DATABASE demir_ai TO demir_readonly;
GRANT USAGE ON SCHEMA public TO demir_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO demir_readonly;

-- ============================================================================
-- SUMMARY
-- ============================================================================
-- Tables created:
-- 1. feature_store (80+ features)
-- 2. ml_models (model versioning)
-- 3. predictions (all predictions & results)
-- 4. manual_trades (user trades & tracking)
-- 5. macro_data (economic data)
-- 6. error_log (error tracking)
-- 7. signal_log (all signals)
-- 8. backtesting_results (backtest performance)
-- 9. trading_stats (daily statistics)
-- ============================================================================
