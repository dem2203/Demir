-- ============================================================================
-- DEMIR AI v7.0 - DATABASE SCHEMA UPGRADE
-- Trade Tracking & AI Learning Tables
-- ============================================================================
-- Date: 2025-11-20
-- Purpose: Enable AI to learn from every trade
-- ============================================================================

-- ============================================================================
-- TRADES TABLE - Her trade'ı kaydet
-- ============================================================================

CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Trade details
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('LONG', 'SHORT')),
    entry_price NUMERIC(20, 8) NOT NULL,
    exit_price NUMERIC(20, 8) NOT NULL,
    entry_time TIMESTAMP WITH TIME ZONE NOT NULL,
    exit_time TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Signal information
    signal_id INTEGER REFERENCES signals(id),
    signal_confidence NUMERIC(5, 4) NOT NULL,
    signal_layers JSONB NOT NULL,  -- Layer scores that triggered signal
    
    -- Outcome
    pnl NUMERIC(20, 8) NOT NULL,  -- Profit/Loss in $
    pnl_percent NUMERIC(10, 4) NOT NULL,  -- P/L percentage
    is_win BOOLEAN NOT NULL,
    
    -- Market context
    market_regime VARCHAR(50) NOT NULL,  -- trending, ranging, volatile
    volatility NUMERIC(10, 4),
    volume_profile VARCHAR(20),  -- high, medium, low
    
    -- Exit details
    exit_reason VARCHAR(50) NOT NULL,  -- tp, sl, manual, timeout
    notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_exit_time ON trades(exit_time DESC);
CREATE INDEX IF NOT EXISTS idx_trades_is_win ON trades(is_win);
CREATE INDEX IF NOT EXISTS idx_trades_pnl ON trades(pnl DESC);
CREATE INDEX IF NOT EXISTS idx_trades_signal_id ON trades(signal_id);

-- ============================================================================
-- LAYER PERFORMANCE TABLE - Her layer'ın performansı
-- ============================================================================

CREATE TABLE IF NOT EXISTS layer_performance (
    id SERIAL PRIMARY KEY,
    layer_name VARCHAR(100) UNIQUE NOT NULL,
    
    -- Performance metrics
    total_signals INTEGER DEFAULT 0,
    winning_signals INTEGER DEFAULT 0,
    losing_signals INTEGER DEFAULT 0,
    win_rate NUMERIC(5, 4) DEFAULT 0.0,
    
    -- Financial metrics
    avg_pnl NUMERIC(20, 8) DEFAULT 0.0,
    total_pnl NUMERIC(20, 8) DEFAULT 0.0,
    sharpe_ratio NUMERIC(10, 4) DEFAULT 0.0,
    
    -- Calibration
    confidence_calibration NUMERIC(5, 4) DEFAULT 1.0,  -- How well calibrated
    
    -- Metadata
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_layer_perf_name ON layer_performance(layer_name);
CREATE INDEX IF NOT EXISTS idx_layer_perf_win_rate ON layer_performance(win_rate DESC);

-- ============================================================================
-- ACTIVE POSITIONS TABLE - Açık pozisyonlar
-- ============================================================================

CREATE TABLE IF NOT EXISTS active_positions (
    id SERIAL PRIMARY KEY,
    position_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Position details
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('LONG', 'SHORT')),
    entry_price NUMERIC(20, 8) NOT NULL,
    position_size NUMERIC(20, 8) NOT NULL,  -- Amount in $
    
    -- Targets
    stop_loss NUMERIC(20, 8) NOT NULL,
    take_profit_1 NUMERIC(20, 8) NOT NULL,
    take_profit_2 NUMERIC(20, 8),
    take_profit_3 NUMERIC(20, 8),
    
    -- Signal reference
    signal_id INTEGER REFERENCES signals(id),
    signal_confidence NUMERIC(5, 4),
    
    -- Status
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'closed', 'partial')),
    remaining_size NUMERIC(20, 8),  -- For partial closes
    
    -- Unrealized P/L
    current_price NUMERIC(20, 8),
    unrealized_pnl NUMERIC(20, 8) DEFAULT 0.0,
    unrealized_pnl_percent NUMERIC(10, 4) DEFAULT 0.0,
    
    -- Timestamps
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_active_pos_symbol ON active_positions(symbol);
CREATE INDEX IF NOT EXISTS idx_active_pos_status ON active_positions(status);
CREATE INDEX IF NOT EXISTS idx_active_pos_opened_at ON active_positions(opened_at DESC);

-- ============================================================================
-- TRADE JOURNAL TABLE - Detailed trade notes
-- ============================================================================

CREATE TABLE IF NOT EXISTS trade_journal (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(100) REFERENCES trades(trade_id),
    
    -- Entry analysis
    entry_analysis TEXT,  -- Why did we enter?
    market_conditions TEXT,  -- Market state at entry
    risk_assessment TEXT,  -- Risk factors identified
    
    -- Exit analysis
    exit_analysis TEXT,  -- Why did we exit?
    lessons_learned TEXT,  -- What did we learn?
    
    -- Improvement notes
    what_went_well TEXT,
    what_went_wrong TEXT,
    next_time_improvements TEXT,
    
    -- Screenshots/charts (URLs)
    entry_chart_url TEXT,
    exit_chart_url TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_journal_trade_id ON trade_journal(trade_id);

-- ============================================================================
-- LEARNING INSIGHTS TABLE - AI'ın öğrendikleri
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_insights (
    id SERIAL PRIMARY KEY,
    insight_type VARCHAR(50) NOT NULL,  -- pattern, regime, layer_performance
    
    -- Insight details
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    confidence NUMERIC(5, 4) NOT NULL,
    
    -- Supporting data
    data JSONB,  -- Additional structured data
    
    -- Impact
    recommendation TEXT,  -- What action to take
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    
    -- Status
    status VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'reviewed', 'applied', 'dismissed')),
    
    -- Metadata
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_insights_type ON learning_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_insights_status ON learning_insights(status);
CREATE INDEX IF NOT EXISTS idx_insights_priority ON learning_insights(priority);

-- ============================================================================
-- PERFORMANCE SUMMARY TABLE - Daily/Weekly/Monthly stats
-- ============================================================================

CREATE TABLE IF NOT EXISTS performance_summary (
    id SERIAL PRIMARY KEY,
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly')),
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Trading stats
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate NUMERIC(5, 4) DEFAULT 0.0,
    
    -- Financial stats
    total_pnl NUMERIC(20, 8) DEFAULT 0.0,
    avg_win NUMERIC(20, 8) DEFAULT 0.0,
    avg_loss NUMERIC(20, 8) DEFAULT 0.0,
    largest_win NUMERIC(20, 8) DEFAULT 0.0,
    largest_loss NUMERIC(20, 8) DEFAULT 0.0,
    
    -- Risk metrics
    sharpe_ratio NUMERIC(10, 4) DEFAULT 0.0,
    sortino_ratio NUMERIC(10, 4) DEFAULT 0.0,
    max_drawdown NUMERIC(10, 4) DEFAULT 0.0,
    
    -- Additional data
    details JSONB,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(period_type, period_start)
);

CREATE INDEX IF NOT EXISTS idx_perf_summary_period ON performance_summary(period_type, period_start DESC);

-- ============================================================================
-- DATABASE BACKUP LOG TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS database_backups (
    id SERIAL PRIMARY KEY,
    backup_type VARCHAR(50) NOT NULL,  -- full, incremental
    backup_location TEXT NOT NULL,  -- S3, Railway, local path
    backup_size_mb NUMERIC(10, 2),
    status VARCHAR(20) DEFAULT 'completed',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_backups_created_at ON database_backups(created_at DESC);

-- ============================================================================
-- VIEWS FOR QUICK ANALYTICS
-- ============================================================================

-- Daily performance view
CREATE OR REPLACE VIEW daily_performance AS
SELECT 
    DATE(exit_time) as trade_date,
    COUNT(*) as total_trades,
    SUM(CASE WHEN is_win THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN NOT is_win THEN 1 ELSE 0 END) as losses,
    ROUND(AVG(CASE WHEN is_win THEN 1.0 ELSE 0.0 END), 4) as win_rate,
    SUM(pnl) as total_pnl,
    AVG(pnl) as avg_pnl,
    MAX(pnl) as best_trade,
    MIN(pnl) as worst_trade
FROM trades
GROUP BY DATE(exit_time)
ORDER BY trade_date DESC;

-- Layer performance summary view
CREATE OR REPLACE VIEW layer_performance_summary AS
SELECT 
    layer_name,
    total_signals,
    winning_signals,
    losing_signals,
    win_rate,
    avg_pnl,
    total_pnl,
    CASE 
        WHEN win_rate > 0.60 THEN 'excellent'
        WHEN win_rate > 0.55 THEN 'good'
        WHEN win_rate > 0.50 THEN 'average'
        WHEN win_rate > 0.45 THEN 'poor'
        ELSE 'very_poor'
    END as performance_grade
FROM layer_performance
WHERE total_signals >= 10
ORDER BY win_rate DESC, total_signals DESC;

-- Open positions summary
CREATE OR REPLACE VIEW open_positions_summary AS
SELECT 
    symbol,
    direction,
    entry_price,
    current_price,
    unrealized_pnl,
    unrealized_pnl_percent,
    EXTRACT(EPOCH FROM (NOW() - opened_at))/3600 as hours_open,
    status
FROM active_positions
WHERE status = 'open'
ORDER BY opened_at DESC;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to calculate Sharpe ratio
CREATE OR REPLACE FUNCTION calculate_sharpe_ratio(
    pnl_values NUMERIC[]
) RETURNS NUMERIC AS $$
DECLARE
    avg_return NUMERIC;
    std_return NUMERIC;
    sharpe NUMERIC;
BEGIN
    -- Calculate average return
    SELECT AVG(val) INTO avg_return FROM UNNEST(pnl_values) AS val;
    
    -- Calculate standard deviation
    SELECT STDDEV(val) INTO std_return FROM UNNEST(pnl_values) AS val;
    
    -- Calculate Sharpe (assuming risk-free rate = 0)
    IF std_return > 0 THEN
        sharpe := avg_return / std_return;
    ELSE
        sharpe := 0;
    END IF;
    
    RETURN sharpe;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert default market regimes (for reference)
CREATE TABLE IF NOT EXISTS market_regimes (
    regime VARCHAR(50) PRIMARY KEY,
    description TEXT
);

INSERT INTO market_regimes (regime, description) VALUES
    ('trending_up', 'Strong upward trend with higher highs'),
    ('trending_down', 'Strong downward trend with lower lows'),
    ('ranging', 'Sideways movement between support and resistance'),
    ('volatile', 'High volatility with rapid price swings'),
    ('consolidation', 'Low volatility, tight range'),
    ('breakout', 'Price breaking out of range')
ON CONFLICT (regime) DO NOTHING;

-- ============================================================================
-- MAINTENANCE QUERIES (Run periodically)
-- ============================================================================

-- Archive old trades (older than 1 year)
-- CREATE TABLE IF NOT EXISTS trades_archive (LIKE trades INCLUDING ALL);
-- INSERT INTO trades_archive SELECT * FROM trades WHERE exit_time < NOW() - INTERVAL '1 year';
-- DELETE FROM trades WHERE exit_time < NOW() - INTERVAL '1 year';

-- Vacuum tables for performance
-- VACUUM ANALYZE trades;
-- VACUUM ANALYZE layer_performance;
-- VACUUM ANALYZE active_positions;

-- ============================================================================
-- GRANT PERMISSIONS (if needed)
-- ============================================================================

-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO demir_ai_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO demir_ai_user;

-- ============================================================================
-- END OF SCHEMA UPGRADE
-- ============================================================================
