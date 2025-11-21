/**
 * ═══════════════════════════════════════════════════════════════════════════════════════
 * 🚀 DEMIR AI v8.0 - ULTRA-PROFESSIONAL MODULAR DASHBOARD
 * ═══════════════════════════════════════════════════════════════════════════════════════
 * 
 * ENTERPRISE-GRADE AI CRYPTO TRADING DASHBOARD - COMPLETE IMPLEMENTATION
 * 
 * ✅ FULL v8.0 FEATURES:
 * - 5 Independent Signal Groups (Each with Entry, TP1-3, SL, R:R)
 * - Real-time WebSocket Updates
 * - Smart Money Tracker
 * - Arbitrage Scanner  
 * - Pattern Recognition
 * - On-Chain Analytics
 * - Risk Engine v2
 * - Sentiment Gauge
 * - Validator Metrics
 * - Performance Charts
 * - Zero Mock Data
 * 
 * @version 8.0.0 - PRODUCTION READY
 * @author DEMIR AI Professional Team
 * @license Proprietary
 * ═══════════════════════════════════════════════════════════════════════════════════════
 */

// ═══ GLOBAL STATE MANAGEMENT ═══

const DashboardState = {
    socket: null,
    connected: false,
    prices: {},
    signals: [],
    groupSignals: { technical: {}, sentiment: {}, ml: {}, onchain: {}, risk: {} },
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

// ═══ INITIALIZATION ═══

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DEMIR AI v8.0 Dashboard initializing...');
    initializeWebSocket();
    initializePerformanceChart();
    startSystemClock();
    loadInitialData();
    setupEventListeners();
    DashboardState.updateInterval = setInterval(updateAllData, 5000);
    DashboardState.validatorInterval = setInterval(fetchValidatorMetrics, 10000);
    console.log('✅ Dashboard initialization complete');
});

// ═══ WEBSOCKET ═══

function initializeWebSocket() {
    try {
        DashboardState.socket = io({ transports: ['websocket', 'polling'], reconnection: true, reconnectionDelay: 1000, reconnectionAttempts: 10 });
        DashboardState.socket.on('connect', () => { console.log('✅ WebSocket connected'); DashboardState.connected = true; updateConnectionStatus(true); DashboardState.socket.emit('subscribe', { symbols: ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'] }); });
        DashboardState.socket.on('disconnect', () => { console.log('⚠️  WebSocket disconnected'); DashboardState.connected = false; updateConnectionStatus(false); });
        DashboardState.socket.on('price_update', handlePriceUpdate);
        DashboardState.socket.on('price_bulk', handlePriceBulk);
        DashboardState.socket.on('signal_update', handleSignalUpdate);
        DashboardState.socket.on('group_signal_update', handleGroupSignalUpdate);
        DashboardState.socket.on('opportunity_detected', handleOpportunityDetected);
        DashboardState.socket.on('smart_money_alert', handleSmartMoneyAlert);
        DashboardState.socket.on('arbitrage_opportunity', handleArbitrageOpportunity);
        DashboardState.socket.on('pattern_detected', handlePatternDetected);
        DashboardState.socket.on('validator_alert', handleValidatorAlert);
        DashboardState.socket.on('performance_update', handlePerformanceUpdate);
        DashboardState.socket.on('health_status', handleHealthStatus);
        DashboardState.socket.on('layer_scores', handleLayerScores);
    } catch (error) { console.error('❌ WebSocket error:', error); updateConnectionStatus(false); }
}

function updateConnectionStatus(connected) {
    const dot = document.getElementById('connection-dot'); const text = document.getElementById('connection-text');
    if (connected) { dot.classList.remove('disconnected'); text.textContent = 'Bağlı (Live)'; } 
    else { dot.classList.add('disconnected'); text.textContent = 'Bağlantı kesildi'; }
}

// ═══ DATA LOADING ═══

async function loadInitialData() {
    try {
        await fetchPrices(); await fetchGroupSignals(); await fetchOpportunities();
        await fetchSmartMoney(); await fetchArbitrage(); await fetchPatterns();
        await fetchOnChainMetrics(); await fetchValidatorMetrics(); await fetchSystemMetrics();
        console.log('✅ Initial data loaded');
    } catch (error) { console.error('❌ Error loading data:', error); }
}

async function updateAllData() { if (!DashboardState.connected) { await fetchPrices(); await fetchGroupSignals(); await fetchOpportunities(); } await fetchSystemMetrics(); }

// ═══ API CALLS ═══

async function apiCall(endpoint, options = {}) {
    try { const response = await fetch(endpoint, { ...options, headers: { 'Content-Type': 'application/json', ...options.headers } }); if (!response.ok) throw new Error(`API error: ${response.status}`); return await response.json(); } 
    catch (error) { console.error(`API call failed for ${endpoint}:`, error); throw error; }
}

async function fetchPrices() { try { const data = await apiCall('/api/prices'); if (data && data.prices) { DashboardState.prices = data.prices; renderPrices(); } } catch (error) { console.error('Error fetching prices:', error); } }

async function fetchGroupSignals() {
    try {
        const symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']; const groups = ['technical', 'sentiment', 'ml', 'onchain', 'risk'];
        for (const symbol of symbols) { for (const group of groups) { try { const data = await apiCall(`/api/signals/${group}?symbol=${symbol}`); if (data && data.signal) { if (!DashboardState.groupSignals[group]) DashboardState.groupSignals[group] = {}; DashboardState.groupSignals[group][symbol] = data.signal; } } catch (error) { console.warn(`Failed ${group} for ${symbol}`); } } }
        renderGroupSignals(); console.log('✅ Group signals fetched');
    } catch (error) { console.error('❌ Error fetching group signals:', error); }
}

async function fetchOpportunities() { try { const data = await apiCall('/api/opportunities?min_confidence=0.7&limit=10'); if (data && data.opportunities) { DashboardState.opportunities = data.opportunities; renderOpportunities(); } } catch (error) { console.error('Error opportunities:', error); } }
async function fetchSmartMoney() { try { const data = await apiCall('/api/smart-money/recent?limit=5'); if (data && data.transactions) { DashboardState.smartMoney = data.transactions; renderSmartMoney(); } } catch (error) { console.warn('Smart money N/A'); } }
async function fetchArbitrage() { try { const data = await apiCall('/api/arbitrage/opportunities?min_spread=0.1'); if (data && data.opportunities) { DashboardState.arbitrage = data.opportunities; renderArbitrage(); } } catch (error) { console.warn('Arbitrage N/A'); } }
async function fetchPatterns() { try { const data = await apiCall('/api/patterns/detected?min_confidence=0.7'); if (data && data.patterns) { DashboardState.patterns = data.patterns; renderPatterns(); } } catch (error) { console.warn('Patterns N/A'); } }
async function fetchOnChainMetrics() { try { const data = await apiCall('/api/onchain/metrics'); if (data && data.metrics) { DashboardState.onchainMetrics = data.metrics; renderOnChainMetrics(); } } catch (error) { console.warn('OnChain N/A'); } }
async function fetchValidatorMetrics() { try { const data = await apiCall('/api/validators/status'); if (data && data.status === 'success') { DashboardState.validatorMetrics = data.data; renderValidatorMetrics(data.data); } } catch (error) { console.warn('Validator metrics N/A'); } }
async function fetchSystemMetrics() { try { const data = await apiCall('/api/analytics/summary'); if (data && data.status === 'success') renderSystemMetrics(data.data); } catch (error) { console.error('Error system metrics:', error); } }

// ═══ WEBSOCKET HANDLERS ═══

function handlePriceUpdate(data) { if (data.symbol && data.price) { DashboardState.prices[data.symbol] = { price: data.price, change_24h: data.change_24h || 0, volume: data.volume || 0, timestamp: Date.now() }; updatePriceCard(data.symbol, data.price, data.change_24h); } }
function handlePriceBulk(data) { if (!data) return; for (const [symbol, info] of Object.entries(data)) { DashboardState.prices[symbol] = { price: info.price, change_24h: info.change_24h || 0, volume: info.volume || 0, timestamp: Date.now() }; updatePriceCard(symbol, info.price, info.change_24h || 0); } }
function handleSignalUpdate(data) { if (data.signal) { DashboardState.signals.unshift(data.signal); if (DashboardState.signals.length > 100) DashboardState.signals.pop(); renderSignals(); } }
function handleGroupSignalUpdate(data) { if (data.group && data.symbol && data.signal) { if (!DashboardState.groupSignals[data.group]) DashboardState.groupSignals[data.group] = {}; DashboardState.groupSignals[data.group][data.symbol] = data.signal; console.log(`✅ Group signal: ${data.group} - ${data.symbol}`); renderGroupSignals(); } }
function handleOpportunityDetected(data) { if (data.opportunity) { DashboardState.opportunities.unshift(data.opportunity); if (DashboardState.opportunities.length > 20) DashboardState.opportunities.pop(); renderOpportunities(); showToast('💡 Yeni Fırsat!', 'info'); } }
function handleSmartMoneyAlert(data) { if (data.transaction) { DashboardState.smartMoney.unshift(data.transaction); if (DashboardState.smartMoney.length > 10) DashboardState.smartMoney.pop(); renderSmartMoney(); showToast('🐳 Whale Hareketi!', 'warning'); } }
function handleArbitrageOpportunity(data) { if (data.opportunity) { DashboardState.arbitrage.unshift(data.opportunity); if (DashboardState.arbitrage.length > 10) DashboardState.arbitrage.pop(); renderArbitrage(); showToast('🔄 Arbitrage!', 'success'); } }
function handlePatternDetected(data) { if (data.pattern) { DashboardState.patterns.unshift(data.pattern); if (DashboardState.patterns.length > 10) DashboardState.patterns.pop(); renderPatterns(); showToast('📊 Pattern!', 'info'); } }
function handleValidatorAlert(data) { if (data.alert_type === 'MOCK_DATA_DETECTED') { showToast('🚨 MOCK DATA!', 'error'); console.error('🚨 VALIDATOR ALERT:', data); } }
function handlePerformanceUpdate(data) { if (!data) return; safeSetText('metric-total-signals', data.total_signals || 0); safeSetText('metric-win-rate', `${formatPercent((data.win_rate || 0) * 100)}%`); safeSetText('metric-pnl', `$${formatNumber(data.total_pnl || 0)}`); safeSetText('metric-sharpe', (data.sharpe_ratio || 0).toFixed(2)); if (DashboardState.performanceChart && data.history) { DashboardState.performanceChart.data.labels = data.history.timestamps || []; DashboardState.performanceChart.data.datasets[0].data = data.history.values || []; DashboardState.performanceChart.update('none'); } }
function handleHealthStatus(data) { if (!data) return; const keys = Object.keys(data).filter(k => k !== 'last_check'); const healthy = keys.filter(k => data[k] === true).length; const pct = (healthy / keys.length) * 100; safeSetText('metric-api-health', `${Math.round(pct)}%`); }
function handleLayerScores(data) { if (!data || !data.symbol || !data.scores) return; const sel = document.getElementById('layer-symbol-select')?.value; if (data.symbol === sel) renderLayerGrid(data.scores); }

// Devamı size ikinci mesajda gelecek, dosya boyutu limiti nedeniyle...