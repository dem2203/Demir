// State Management
const state = {
    coins: {
        core: [
            { symbol: 'BTCUSDT', name: 'Bitcoin', icon: '₿', price: 0, change: 0, lastUpdate: null },
            { symbol: 'ETHUSDT', name: 'Ethereum', icon: 'Ξ', price: 0, change: 0, lastUpdate: null },
            { symbol: 'LTCUSDT', name: 'Litecoin', icon: 'Ł', price: 0, change: 0, lastUpdate: null }
        ],
        manual: []
    },
    websocket: null,
    currentView: 'dashboard',
    systemStartTime: Date.now(),
    lastPrices: {},
    signals: [],
    layers: {
        technical: [
            { name: 'Strategy Layer', description: 'Technical indicator analysis', weight: 0.15, score: 0 },
            { name: 'Kelly Criterion', description: 'Position sizing optimization', weight: 0.10, score: 0 },
            { name: 'Monte Carlo', description: 'Risk simulation', weight: 0.08, score: 0 }
        ],
        macro: [
            { name: 'Enhanced Macro', description: 'SPX, NASDAQ, DXY correlation', weight: 0.12, score: 0 },
            { name: 'Enhanced Gold', description: 'Safe-haven analysis', weight: 0.08, score: 0 },
            { name: 'Enhanced VIX', description: 'Fear index tracking', weight: 0.08, score: 0 },
            { name: 'Enhanced Rates', description: 'Interest rate impact', weight: 0.07, score: 0 }
        ],
        quantum: [
            { name: 'Black-Scholes', description: 'Option pricing model', weight: 0.06, score: 0 },
            { name: 'Kalman Regime', description: 'Market regime detection', weight: 0.06, score: 0 },
            { name: 'Fractal Chaos', description: 'Non-linear dynamics', weight: 0.05, score: 0 },
            { name: 'Fourier Cycle', description: 'Cyclical pattern detection', weight: 0.05, score: 0 },
            { name: 'Copula Correlation', description: 'Dependency modeling', weight: 0.05, score: 0 }
        ],
        intelligence: [
            { name: 'Consciousness Core', description: 'Bayesian decision engine', weight: 0.15, score: 0 },
            { name: 'Macro Intelligence', description: 'Economic factor analysis', weight: 0.10, score: 0 },
            { name: 'On-Chain Intelligence', description: 'Blockchain metrics', weight: 0.10, score: 0 },
            { name: 'Sentiment Layer', description: 'Social & news sentiment', weight: 0.10, score: 0 }
        ]
    },
    marketIntelligence: {
        macro: [
            { label: 'SPX', value: 0, change: 0 },
            { label: 'NASDAQ', value: 0, change: 0 },
            { label: 'DXY', value: 0, change: 0 },
            { label: 'VIX', value: 0, change: 0 },
            { label: 'Gold', value: 0, change: 0 }
        ],
        onchain: [
            { label: 'Whale Activity', value: 'Moderate' },
            { label: 'Exchange Inflow', value: 'Low' },
            { label: 'Exchange Outflow', value: 'High' },
            { label: 'Active Addresses', value: '1.2M' }
        ],
        sentiment: [
            { label: 'Fear & Greed', value: 65 },
            { label: 'Social Sentiment', value: 72 },
            { label: 'News Sentiment', value: 58 }
        ]
    },
    apiStatus: [
        { name: 'Binance', connected: false },
        { name: 'Alpha Vantage', connected: true },
        { name: 'CoinMarketCap', connected: true },
        { name: 'CoinGlass', connected: true },
        { name: 'TwelveData', connected: true },
        { name: 'NewsAPI', connected: true },
        { name: 'Telegram', connected: true }
    ]
};

// Initialize Application
function init() {
    setupNavigation();
    connectWebSocket();
    startUptime();
    renderCoreCoins();
    renderManualCoins();
    updateSystemStatus();
    generateMockSignals();
    renderLayers();
    renderMarketIntelligence();
    renderSystemStatus();
    renderSettings();
    startTelegramPing();
    startIntelligenceUpdates();
}

// Navigation
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.dataset.view;
            switchView(view);
            
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function switchView(viewName) {
    const views = document.querySelectorAll('.view');
    views.forEach(view => view.classList.remove('active'));
    
    const targetView = document.getElementById(`${viewName}View`);
    if (targetView) {
        targetView.classList.add('active');
        state.currentView = viewName;
    }
}

// WebSocket Connection
function connectWebSocket() {
    const streams = [...state.coins.core, ...state.coins.manual]
        .map(coin => `${coin.symbol.toLowerCase()}@ticker`)
        .join('/');
    
    const wsUrl = `wss://stream.binance.com:9443/stream?streams=${streams}`;
    
    if (state.websocket) {
        state.websocket.close();
    }
    
    state.websocket = new WebSocket(wsUrl);
    
    state.websocket.onopen = () => {
        console.log('WebSocket Connected');
        updateConnectionStatus(true);
        state.apiStatus[0].connected = true;
        renderSystemStatus();
    };
    
    state.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.data && data.data.s) {
            updateCoinPrice(data.data);
        }
    };
    
    state.websocket.onerror = (error) => {
        console.error('WebSocket Error:', error);
        updateConnectionStatus(false);
    };
    
    state.websocket.onclose = () => {
        console.log('WebSocket Disconnected');
        updateConnectionStatus(false);
        state.apiStatus[0].connected = false;
        // Reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
    };
}

function updateConnectionStatus(connected) {
    const wsStatus = document.getElementById('wsStatus');
    if (connected) {
        wsStatus.classList.add('connected');
        wsStatus.querySelector('span').textContent = 'Connected';
    } else {
        wsStatus.classList.remove('connected');
        wsStatus.querySelector('span').textContent = 'Disconnected';
    }
}

function updateCoinPrice(tickerData) {
    const symbol = tickerData.s;
    const price = parseFloat(tickerData.c);
    const change = parseFloat(tickerData.P);
    
    // Update core coins
    const coreCoin = state.coins.core.find(c => c.symbol === symbol);
    if (coreCoin) {
        coreCoin.price = price;
        coreCoin.change = change;
        coreCoin.lastUpdate = new Date();
    }
    
    // Update manual coins
    const manualCoin = state.coins.manual.find(c => c.symbol === symbol);
    if (manualCoin) {
        manualCoin.price = price;
        manualCoin.change = change;
        manualCoin.lastUpdate = new Date();
    }
    
    // Re-render
    renderCoreCoins();
    renderManualCoins();
}

// Render Core Coins
function renderCoreCoins() {
    const grid = document.getElementById('coreCoinsGrid');
    if (!grid) return;
    
    grid.innerHTML = state.coins.core.map(coin => {
        const changeClass = coin.change >= 0 ? 'positive' : 'negative';
        const changeSymbol = coin.change >= 0 ? '▲' : '▼';
        const lastUpdate = coin.lastUpdate ? formatTime(coin.lastUpdate) : '--';
        
        return `
            <div class="coin-card">
                <div class="coin-header">
                    <div class="coin-info">
                        <div class="coin-icon">${coin.icon}</div>
                        <div class="coin-details">
                            <div class="coin-symbol">${coin.symbol.replace('USDT', '')}</div>
                            <div class="coin-name">${coin.name}</div>
                        </div>
                    </div>
                </div>
                <div class="coin-body">
                    <div class="coin-price">$${coin.price > 0 ? formatPrice(coin.price) : '--'}</div>
                </div>
                <div class="coin-footer">
                    <div class="coin-change ${changeClass}">
                        ${changeSymbol} ${Math.abs(coin.change).toFixed(2)}%
                    </div>
                    <div class="coin-update">${lastUpdate}</div>
                </div>
            </div>
        `;
    }).join('');
}

// Render Manual Coins
function renderManualCoins() {
    const grid = document.getElementById('manualCoinsGrid');
    if (!grid) return;
    
    if (state.coins.manual.length === 0) {
        grid.innerHTML = '<div class="empty-state">No manual coins added yet</div>';
        return;
    }
    
    grid.innerHTML = state.coins.manual.map((coin, index) => {
        const changeClass = coin.change >= 0 ? 'positive' : 'negative';
        const changeSymbol = coin.change >= 0 ? '▲' : '▼';
        const lastUpdate = coin.lastUpdate ? formatTime(coin.lastUpdate) : '--';
        
        return `
            <div class="coin-card">
                <div class="coin-header">
                    <div class="coin-info">
                        <div class="coin-icon">${coin.icon || '◆'}</div>
                        <div class="coin-details">
                            <div class="coin-symbol">${coin.symbol.replace('USDT', '')}</div>
                            <div class="coin-name">${coin.name || 'Manual Coin'}</div>
                        </div>
                    </div>
                    <button class="remove-coin-btn" onclick="removeCoin(${index})">Remove</button>
                </div>
                <div class="coin-body">
                    <div class="coin-price">$${coin.price > 0 ? formatPrice(coin.price) : '--'}</div>
                </div>
                <div class="coin-footer">
                    <div class="coin-change ${changeClass}">
                        ${changeSymbol} ${Math.abs(coin.change).toFixed(2)}%
                    </div>
                    <div class="coin-update">${lastUpdate}</div>
                </div>
            </div>
        `;
    }).join('');
}

// Add Manual Coin
function addManualCoin() {
    const input = document.getElementById('manualCoinInput');
    const symbol = input.value.trim().toUpperCase();
    
    if (!symbol) return;
    
    // Validate format
    if (!symbol.endsWith('USDT')) {
        alert('Symbol must end with USDT (e.g., SOLUSDT)');
        return;
    }
    
    // Check if already exists
    const exists = [...state.coins.core, ...state.coins.manual].some(c => c.symbol === symbol);
    if (exists) {
        alert('Coin already exists');
        return;
    }
    
    // Add coin
    state.coins.manual.push({
        symbol: symbol,
        name: symbol.replace('USDT', ''),
        icon: '◆',
        price: 0,
        change: 0,
        lastUpdate: null
    });
    
    // Reconnect WebSocket with new symbol
    connectWebSocket();
    
    // Clear input and render
    input.value = '';
    renderManualCoins();
    updateSystemStatus();
}

// Remove Manual Coin
function removeCoin(index) {
    state.coins.manual.splice(index, 1);
    connectWebSocket();
    renderManualCoins();
    updateSystemStatus();
}

// Setup Add Coin Button
document.addEventListener('DOMContentLoaded', () => {
    const addBtn = document.getElementById('addCoinBtn');
    if (addBtn) {
        addBtn.addEventListener('click', addManualCoin);
    }
    
    const input = document.getElementById('manualCoinInput');
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                addManualCoin();
            }
        });
    }
});

// Update System Status
function updateSystemStatus() {
    const systemStatus = document.getElementById('systemStatus');
    const activeLayers = document.getElementById('activeLayers');
    const lastAnalysis = document.getElementById('lastAnalysis');
    const signalConfidence = document.getElementById('signalConfidence');
    
    if (systemStatus) systemStatus.textContent = 'Running';
    
    // Calculate total active layers
    const totalLayers = Object.values(state.layers).flat().length;
    if (activeLayers) activeLayers.textContent = totalLayers;
    
    if (lastAnalysis) lastAnalysis.textContent = formatTime(new Date());
    
    // Generate random confidence for demo
    const confidence = Math.floor(Math.random() * 20 + 75);
    if (signalConfidence) signalConfidence.textContent = `${confidence}%`;
}

// Start Intelligence Updates
function startIntelligenceUpdates() {
    updateIntelligenceScores();
    setInterval(updateIntelligenceScores, 5000);
}

function updateIntelligenceScores() {
    // Generate realistic scores
    const technicalScore = Math.floor(Math.random() * 30 + 60);
    const macroScore = Math.floor(Math.random() * 30 + 55);
    const onchainScore = Math.floor(Math.random() * 30 + 65);
    const sentimentScore = Math.floor(Math.random() * 30 + 50);
    
    // Update DOM
    updateScore('technicalScore', 'technicalProgress', technicalScore);
    updateScore('macroScore', 'macroProgress', macroScore);
    updateScore('onchainScore', 'onchainProgress', onchainScore);
    updateScore('sentimentScore', 'sentimentProgress', sentimentScore);
    
    // Update layer scores
    Object.keys(state.layers).forEach(category => {
        state.layers[category].forEach(layer => {
            layer.score = Math.floor(Math.random() * 30 + 65);
        });
    });
}

function updateScore(valueId, progressId, score) {
    const valueEl = document.getElementById(valueId);
    const progressEl = document.getElementById(progressId);
    
    if (valueEl) valueEl.textContent = score;
    if (progressEl) progressEl.style.width = `${score}%`;
}

// Generate Mock Signals
function generateMockSignals() {
    state.signals = [
        {
            symbol: 'BTCUSDT',
            direction: 'LONG',
            confidence: 87,
            entry: 42500,
            takeProfit: 44000,
            stopLoss: 41500
        },
        {
            symbol: 'ETHUSDT',
            direction: 'SHORT',
            confidence: 72,
            entry: 2250,
            takeProfit: 2100,
            stopLoss: 2350
        }
    ];
    
    renderSignals();
}

function renderSignals() {
    const container = document.getElementById('signalsContainer');
    if (!container) return;
    
    if (state.signals.length === 0) {
        container.innerHTML = '<div class="empty-state">No active signals</div>';
        return;
    }
    
    container.innerHTML = state.signals.map(signal => `
        <div class="signal-card ${signal.direction.toLowerCase()}">
            <div class="signal-header">
                <div class="signal-symbol">${signal.symbol.replace('USDT', '')}/USDT</div>
                <div class="signal-direction ${signal.direction.toLowerCase()}">${signal.direction}</div>
            </div>
            <div class="signal-body">
                <div class="signal-confidence">
                    <div class="signal-confidence-label">Confidence</div>
                    <div class="signal-confidence-bar">
                        <div class="signal-confidence-fill" style="width: ${signal.confidence}%"></div>
                    </div>
                </div>
                <div class="signal-prices">
                    <div class="signal-price">
                        <div class="signal-price-label">Entry</div>
                        <div class="signal-price-value">$${formatPrice(signal.entry)}</div>
                    </div>
                    <div class="signal-price">
                        <div class="signal-price-label">TP</div>
                        <div class="signal-price-value">$${formatPrice(signal.takeProfit)}</div>
                    </div>
                    <div class="signal-price">
                        <div class="signal-price-label">SL</div>
                        <div class="signal-price-value">$${formatPrice(signal.stopLoss)}</div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Render Layers
function renderLayers() {
    const container = document.getElementById('layersContainer');
    if (!container) return;
    
    const categories = [
        { key: 'technical', title: 'Technical Layers' },
        { key: 'macro', title: 'Macro Layers' },
        { key: 'quantum', title: 'Quantum Layers' },
        { key: 'intelligence', title: 'Intelligence Layers' }
    ];
    
    container.innerHTML = categories.map(category => {
        const layers = state.layers[category.key];
        return `
            <div class="layer-category">
                <div class="layer-category-header">
                    <div class="layer-category-title">${category.title}</div>
                    <div class="layer-category-count">${layers.length} layers</div>
                </div>
                <div class="layer-list">
                    ${layers.map(layer => `
                        <div class="layer-item">
                            <div class="layer-info">
                                <div class="layer-name">${layer.name}</div>
                                <div class="layer-description">${layer.description}</div>
                            </div>
                            <div class="layer-meta">
                                <div class="layer-status active">
                                    <span class="layer-status-dot"></span>
                                    Active
                                </div>
                                <div class="layer-score">${layer.score || '--'}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }).join('');
}

// Render Market Intelligence
function renderMarketIntelligence() {
    renderMacroFactors();
    renderOnChainMetrics();
    renderSentimentIndicators();
}

function renderMacroFactors() {
    const grid = document.getElementById('macroGrid');
    if (!grid) return;
    
    // Generate random values for demo
    state.marketIntelligence.macro = [
        { label: 'SPX', value: 4512.23, change: 0.45 },
        { label: 'NASDAQ', value: 14235.67, change: -0.23 },
        { label: 'DXY', value: 103.45, change: 0.12 },
        { label: 'VIX', value: 15.67, change: -2.34 },
        { label: 'Gold', value: 1995.50, change: 1.23 }
    ];
    
    grid.innerHTML = state.marketIntelligence.macro.map(metric => {
        const changeClass = metric.change >= 0 ? 'positive' : 'negative';
        const changeSymbol = metric.change >= 0 ? '+' : '';
        return `
            <div class="metric-card">
                <div class="metric-label">${metric.label}</div>
                <div class="metric-value">${formatPrice(metric.value)}</div>
                <div class="metric-change ${changeClass}">${changeSymbol}${metric.change.toFixed(2)}%</div>
            </div>
        `;
    }).join('');
}

function renderOnChainMetrics() {
    const grid = document.getElementById('onchainGrid');
    if (!grid) return;
    
    grid.innerHTML = state.marketIntelligence.onchain.map(metric => `
        <div class="metric-card">
            <div class="metric-label">${metric.label}</div>
            <div class="metric-value">${metric.value}</div>
        </div>
    `).join('');
}

function renderSentimentIndicators() {
    const grid = document.getElementById('sentimentGrid');
    if (!grid) return;
    
    grid.innerHTML = state.marketIntelligence.sentiment.map(metric => `
        <div class="metric-card">
            <div class="metric-label">${metric.label}</div>
            <div class="metric-value">${metric.value}</div>
        </div>
    `).join('');
}

// Render System Status
function renderSystemStatus() {
    updateDaemonStatus();
    updateAPIConnections();
    updateTelegramStatus();
    updateSystemMetrics();
}

function updateDaemonStatus() {
    const uptime = document.getElementById('daemonUptime');
    if (uptime) {
        const elapsed = Date.now() - state.systemStartTime;
        const hours = Math.floor(elapsed / 3600000);
        const minutes = Math.floor((elapsed % 3600000) / 60000);
        uptime.textContent = `${hours}h ${minutes}m`;
    }
}

function updateAPIConnections() {
    const container = document.getElementById('apiConnections');
    if (!container) return;
    
    container.innerHTML = state.apiStatus.map(api => `
        <div class="api-status-item">
            <div class="api-name">${api.name}</div>
            <div class="api-status ${api.connected ? 'connected' : 'disconnected'}">
                ${api.connected ? 'Connected' : 'Disconnected'}
            </div>
        </div>
    `).join('');
}

function updateTelegramStatus() {
    const lastPing = document.getElementById('lastPing');
    const nextUpdate = document.getElementById('nextUpdate');
    
    if (lastPing) lastPing.textContent = formatTime(new Date());
    
    if (nextUpdate) {
        const next = new Date(Date.now() + 3600000); // +1 hour
        nextUpdate.textContent = formatTime(next);
    }
}

function updateSystemMetrics() {
    const wsMetric = document.getElementById('wsMetric');
    const activeStreams = document.getElementById('activeStreams');
    
    if (wsMetric) {
        wsMetric.textContent = state.websocket && state.websocket.readyState === WebSocket.OPEN ? 'Connected' : 'Disconnected';
    }
    
    if (activeStreams) {
        const count = state.coins.core.length + state.coins.manual.length;
        activeStreams.textContent = count;
    }
}

// Render Settings
function renderSettings() {
    const apiList = document.getElementById('apiStatusList');
    if (!apiList) return;
    
    apiList.innerHTML = state.apiStatus.map(api => `
        <div class="api-status-item">
            <div class="api-name">${api.name}</div>
            <div class="api-status ${api.connected ? 'connected' : 'disconnected'}">
                ${api.connected ? 'Connected' : 'Disconnected'}
            </div>
        </div>
    `).join('');
}

// Start Uptime Counter
function startUptime() {
    updateUptime();
    setInterval(updateUptime, 1000);
}

function updateUptime() {
    const display = document.getElementById('uptimeDisplay');
    if (!display) return;
    
    const elapsed = Date.now() - state.systemStartTime;
    const hours = Math.floor(elapsed / 3600000);
    const minutes = Math.floor((elapsed % 3600000) / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    
    display.textContent = `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
}

// Start Telegram Ping Simulation
function startTelegramPing() {
    setInterval(() => {
        console.log('Telegram Ping: Market monitoring active');
        updateTelegramStatus();
    }, 3600000); // Every hour
}

// Utility Functions
function formatPrice(price) {
    if (price >= 1000) {
        return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    return price.toFixed(2);
}

function formatTime(date) {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function pad(num) {
    return num.toString().padStart(2, '0');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}