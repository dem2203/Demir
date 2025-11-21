/**
 * ═══════════════════════════════════════════════════════════════════════════════════════
 * 🚀 DEMIR AI v8.0 - ULTRA-PROFESSIONAL MODULAR DASHBOARD
 * ═══════════════════════════════════════════════════════════════════════════════════════
 * 
 * ENTERPRISE-GRADE AI CRYPTO TRADING DASHBOARD
 * 
 * ✅ NEW v8.0 FEATURES:
 * - 5 Independent Signal Groups (Technical, Sentiment, ML, OnChain, Risk)
 * - Each group has its own: Entry, TP1, TP2, TP3, SL, Risk/Reward
 * - Real-time WebSocket Updates
 * - 60+ AI Layer Visualization
 * - Smart Money Tracker (Whale movements)
 * - Arbitrage Scanner (Multi-exchange opportunities)
 * - Pattern Recognition Engine
 * - On-Chain Analytics Pro
 * - Advanced Risk Engine v2
 * - Sentiment Analysis Gauge
 * - Validator Metrics Dashboard (Zero Mock Data Enforcement)
 * - 100% Real Exchange Data - Zero Tolerance for Mock/Fake Data
 * 
 * @version 8.0.0
 * @author DEMIR AI Professional Team
 * @license Proprietary & Confidential
 * ═══════════════════════════════════════════════════════════════════════════════════════
 */

// ═══════════════════════════════════════════════════════════════════════════════════════
// GLOBAL STATE MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════════════════

const DashboardState = {
    socket: null,
    connected: false,
    prices: {},
    signals: [],
    
    // ★ NEW v8.0: Independent group signals
    groupSignals: {
        technical: {}, // { 'BTCUSDT': { direction, entry, tp1, tp2, tp3, sl, ... } }
        sentiment: {},
        ml: {},
        onchain: {},
        risk: {}
    },
    
    opportunities: [],
    smartMoney: [],
    arbitrage: [],
    patterns: [],
    onchainMetrics: {},
    validatorMetrics: {},
    
    performanceChart: null,
    currentSymbol: 'BTCUSDT',
    updateInterval: null,
    validatorInterval: null
};

// ═══════════════════════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DEMIR AI v8.0 Dashboard initializing...');
    console.log('✅ NEW: 5-Group Independent Signal System Active');
    
    // Initialize components
    initializeWebSocket();
    initializePerformanceChart();
    startSystemClock();
    loadInitialData();
    setupEventListeners();
    
    // Start periodic updates
    DashboardState.updateInterval = setInterval(updateAllData, 5000); // Update every 5 seconds
    DashboardState.validatorInterval = setInterval(fetchValidatorMetrics, 10000); // Validator metrics every 10s
    
    console.log('✅ Dashboard initialization complete');
    console.log('✅ Validator monitoring: 10-second polling active');
});

// ═══════════════════════════════════════════════════════════════════════════════════════
// WEBSOCKET CONNECTION
// ═══════════════════════════════════════════════════════════════════════════════════════

function initializeWebSocket() {
    try {
        // Connect to Flask-SocketIO server
        DashboardState.socket = io({
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: 10
        });
        
        // Connection events
        DashboardState.socket.on('connect', () => {
            console.log('✅ WebSocket connected');
            DashboardState.connected = true;
            updateConnectionStatus(true);
            
            // Subscribe to updates
            DashboardState.socket.emit('subscribe', {
                symbols: ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
            });
        });
        
        DashboardState.socket.on('disconnect', () => {
            console.log('⚠️  WebSocket disconnected');
            DashboardState.connected = false;
            updateConnectionStatus(false);
        });
        
        // Data events
        DashboardState.socket.on('price_update', handlePriceUpdate);
        DashboardState.socket.on('price_bulk', handlePriceBulk);
        DashboardState.socket.on('signal_update', handleSignalUpdate);
        DashboardState.socket.on('group_signal_update', handleGroupSignalUpdate); // ★ NEW
        DashboardState.socket.on('opportunity_detected', handleOpportunityDetected);
        DashboardState.socket.on('smart_money_alert', handleSmartMoneyAlert);
        DashboardState.socket.on('arbitrage_opportunity', handleArbitrageOpportunity);
        DashboardState.socket.on('pattern_detected', handlePatternDetected);
        DashboardState.socket.on('validator_alert', handleValidatorAlert);
        DashboardState.socket.on('performance_update', handlePerformanceUpdate);
        DashboardState.socket.on('health_status', handleHealthStatus);
        DashboardState.socket.on('layer_scores', handleLayerScores);
        
    } catch (error) {
        console.error('❌ WebSocket initialization error:', error);
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(connected) {
    const dot = document.getElementById('connection-dot');
    const text = document.getElementById('connection-text');
    
    if (connected) {
        dot.classList.remove('disconnected');
        text.textContent = 'Bağlı (Live)';
    } else {
        dot.classList.add('disconnected');
        text.textContent = 'Bağlantı kesildi';
    }
}

// ═══════════════════════════════════════════════════════════════════════════════════════
// DATA LOADING
// ═══════════════════════════════════════════════════════════════════════════════════════

async function loadInitialData() {
    try {
        console.log('📂 Loading initial data...');
        
        // Load prices
        await fetchPrices();
        
        // ★ NEW v8.0: Load independent group signals
        await fetchGroupSignals();
        
        // Load opportunities
        await fetchOpportunities();
        
        // Load v8.0 widgets data
        await fetchSmartMoney();
        await fetchArbitrage();
        await fetchPatterns();
        await fetchOnChainMetrics();
        await fetchValidatorMetrics();
        
        // Load system metrics
        await fetchSystemMetrics();
        
        console.log('✅ Initial data loaded successfully');
    } catch (error) {
        console.error('❌ Error loading initial data:', error);
    }
}

async function updateAllData() {
    if (!DashboardState.connected) {
        await fetchPrices(); // Fallback to REST API if WebSocket is down
        await fetchGroupSignals();
        await fetchOpportunities();
    }
    
    await fetchSystemMetrics();
}

// ═══════════════════════════════════════════════════════════════════════════════════════
// API CALLS
// ═══════════════════════════════════════════════════════════════════════════════════════

async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API call failed for ${endpoint}:`, error);
        throw error;
    }
}

async function fetchPrices() {
    try {
        const data = await apiCall('/api/prices');
        if (data && data.prices) {
            DashboardState.prices = data.prices;
            renderPrices();
        }
    } catch (error) {
        console.error('Error fetching prices:', error);
    }
}

// ★★★ NEW v8.0: INDEPENDENT GROUP SIGNALS ★★★
async function fetchGroupSignals() {
    try {
        const symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'];
        const groups = ['technical', 'sentiment', 'ml', 'onchain', 'risk'];
        
        console.log('🔄 Fetching independent group signals...');
        
        for (const symbol of symbols) {
            for (const group of groups) {
                try {
                    const endpoint = `/api/signals/${group}?symbol=${symbol}`;
                    const data = await apiCall(endpoint);
                    
                    if (data && data.signal) {
                        if (!DashboardState.groupSignals[group]) {
                            DashboardState.groupSignals[group] = {};
                        }
                        DashboardState.groupSignals[group][symbol] = data.signal;
                    }
                } catch (error) {
                    console.warn(`Failed to fetch ${group} signal for ${symbol}:`, error.message);
                }
            }
        }
        
        renderGroupSignals();
        console.log('✅ Group signals fetched and rendered');
    } catch (error) {
        console.error('❌ Error fetching group signals:', error);
    }
}

async function fetchOpportunities() {
    try {
        const data = await apiCall('/api/opportunities?min_confidence=0.7&limit=10');
        if (data && data.opportunities) {
            DashboardState.opportunities = data.opportunities;
            renderOpportunities();
        }
    } catch (error) {
        console.error('Error fetching opportunities:', error);
    }
}

async function fetchSmartMoney() {
    try {
        const data = await apiCall('/api/smart-money/recent?limit=5');
        if (data && data.transactions) {
            DashboardState.smartMoney = data.transactions;
            renderSmartMoney();
        }
    } catch (error) {
        console.warn('Smart money data not available');
    }
}

async function fetchArbitrage() {
    try {
        const data = await apiCall('/api/arbitrage/opportunities?min_spread=0.1');
        if (data && data.opportunities) {
            DashboardState.arbitrage = data.opportunities;
            renderArbitrage();
        }
    } catch (error) {
        console.warn('Arbitrage data not available');
    }
}

async function fetchPatterns() {
    try {
        const data = await apiCall('/api/patterns/detected?min_confidence=0.7');
        if (data && data.patterns) {
            DashboardState.patterns = data.patterns;
            renderPatterns();
        }
    } catch (error) {
        console.warn('Pattern data not available');
    }
}

async function fetchOnChainMetrics() {
    try {
        const data = await apiCall('/api/onchain/metrics');
        if (data && data.metrics) {
            DashboardState.onchainMetrics = data.metrics;
            renderOnChainMetrics();
        }
    } catch (error) {
        console.warn('On-chain data not available');
    }
}

async function fetchValidatorMetrics() {
    try {
        const data = await apiCall('/api/validators/status');
        if (data && data.status === 'success') {
            DashboardState.validatorMetrics = data.data;
            renderValidatorMetrics(data.data);
        }
    } catch (error) {
        console.warn('Validator metrics not available');
    }
}

async function fetchSystemMetrics() {
    try {
        const data = await apiCall('/api/analytics/summary');
        if (data && data.status === 'success') {
            renderSystemMetrics(data.data);
        }
    } catch (error) {
        console.error('Error fetching system metrics:', error);
    }
}

// ═══════════════════════════════════════════════════════════════════════════════════════
// WEBSOCKET EVENT HANDLERS
// ═══════════════════════════════════════════════════════════════════════════════════════

function handlePriceUpdate(data) {
    if (data.symbol && data.price) {
        DashboardState.prices[data.symbol] = {
            price: data.price,
            change_24h: data.change_24h || 0,
            volume: data.volume || 0,
            timestamp: Date.now()
        };
        updatePriceCard(data.symbol, data.price, data.change_24h);
    }
}

function handlePriceBulk(data) {
    if (!data) return;
    
    for (const [symbol, info] of Object.entries(data)) {
        DashboardState.prices[symbol] = {
            price: info.price,
            change_24h: info.change_24h || 0,
            volume: info.volume || 0,
            timestamp: Date.now()
        };
        updatePriceCard(symbol, info.price, info.change_24h || 0);
    }
}

function handleSignalUpdate(data) {
    if (data.signal) {
        DashboardState.signals.unshift(data.signal);
        if (DashboardState.signals.length > 100) {
            DashboardState.signals.pop();
        }
        renderSignals();
    }
}

// ★ NEW v8.0: Handle independent group signal updates via WebSocket
function handleGroupSignalUpdate(data) {
    if (data.group && data.symbol && data.signal) {
        if (!DashboardState.groupSignals[data.group]) {
            DashboardState.groupSignals[data.group] = {};
        }
        DashboardState.groupSignals[data.group][data.symbol] = data.signal;
        
        console.log(`✅ Group signal updated: ${data.group} - ${data.symbol}`);
        renderGroupSignals();
    }
}

function handleOpportunityDetected(data) {
    if (data.opportunity) {
        DashboardState.opportunities.unshift(data.opportunity);
        if (DashboardState.opportunities.length > 20) {
            DashboardState.opportunities.pop();
        }
        renderOpportunities();
        showToast('💡 Yeni Fırsat Tespit Edildi!', 'info');
    }
}

function handleSmartMoneyAlert(data) {
    if (data.transaction) {
        DashboardState.smartMoney.unshift(data.transaction);
        if (DashboardState.smartMoney.length > 10) {
            DashboardState.smartMoney.pop();
        }
        renderSmartMoney();
        showToast('🐳 Whale Hareketi Tespit Edildi!', 'warning');
    }
}

function handleArbitrageOpportunity(data) {
    if (data.opportunity) {
        DashboardState.arbitrage.unshift(data.opportunity);
        if (DashboardState.arbitrage.length > 10) {
            DashboardState.arbitrage.pop();
        }
        renderArbitrage();
        showToast('🔄 Arbitrage Fırsatı!', 'success');
    }
}

function handlePatternDetected(data) {
    if (data.pattern) {
        DashboardState.patterns.unshift(data.pattern);
        if (DashboardState.patterns.length > 10) {
            DashboardState.patterns.pop();
        }
        renderPatterns();
        showToast('📊 Pattern Tespit Edildi!', 'info');
    }
}

function handleValidatorAlert(data) {
    if (data.alert_type === 'MOCK_DATA_DETECTED') {
        showToast('🚨 UYARI: Mock Data Tespit Edildi!', 'error');
        console.error('🚨 VALIDATOR ALERT:', data);
    }
}

function handlePerformanceUpdate(data) {
    if (!data) return;
    
    safeSetText('metric-total-signals', data.total_signals || 0);
    safeSetText('metric-win-rate', `${formatPercent((data.win_rate || 0) * 100)}%`);
    safeSetText('metric-pnl', `$${formatNumber(data.total_pnl || 0)}`);
    safeSetText('metric-sharpe', (data.sharpe_ratio || 0).toFixed(2));
    
    if (DashboardState.performanceChart && data.history) {
        DashboardState.performanceChart.data.labels = data.history.timestamps || [];
        DashboardState.performanceChart.data.datasets[0].data = data.history.values || [];
        DashboardState.performanceChart.update('none');
    }
}

function handleHealthStatus(data) {
    if (!data) return;
    
    const healthKeys = Object.keys(data).filter(k => k !== 'last_check');
    const healthyCount = healthKeys.filter(k => data[k] === true).length;
    const healthPercentage = (healthyCount / healthKeys.length) * 100;
    
    safeSetText('metric-api-health', `${Math.round(healthPercentage)}%`);
}

function handleLayerScores(data) {
    if (!data || !data.symbol || !data.scores) return;
    
    const selectedSymbol = document.getElementById('layer-symbol-select')?.value;
    if (data.symbol === selectedSymbol) {
        renderLayerGrid(data.scores);
    }
}

// Gerisini devam ettirmek için size 2. kısım gelecek...