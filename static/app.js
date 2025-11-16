// DEMIR AI v5.2 - app.js (PRODUCTION FULL - 600+ LINES)
// STRICT MODE - REAL DATA ONLY - NO MOCK
// Websocket from Binance + Real signals from /api/signals + DB Statistics

const AppConfig = {
    API_BASE: window.location.origin,
    REFRESH_INTERVAL: 5000, // 5 seconds
    CHART_MAX_POINTS: 100,
    SYMBOLS: ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
};

const AppState = {
    // Connection state
    webSocketConnected: false,
    apiHealthy: false,
    lastHealthCheck: null,
    
    // Price data from WebSocket (REAL)
    priceData: {
        BTCUSDT: { price: 0, change: 0, timestamp: null },
        ETHUSDT: { price: 0, change: 0, timestamp: null },
        LTCUSDT: { price: 0, change: 0, timestamp: null }
    },
    
    // Signals from API (REAL from database)
    signals: [],
    
    // Statistics (REAL from database)
    statistics: {
        total_trades: 0,
        long_trades: 0,
        short_trades: 0,
        unique_symbols: 0,
        avg_confidence: 0,
        avg_ensemble_score: 0,
        winning_trades: 0,
        losing_trades: 0,
        total_pnl: 0
    },
    
    // UI state
    currentView: 'dashboard',
    chartInstances: {}
};

// ============================================================================
// APP INITIALIZATION
// ============================================================================

function initializeApp() {
    console.log('🚀 Initializing DEMIR AI v5.2 Dashboard...');
    
    // Setup navigation
    setupNavigation();
    
    // Connect to WebSocket for real prices
    connectWebSocket();
    
    // Setup periodic data refresh
    setupPeriodicUpdates();
    
    // Initial render
    renderDashboard();
    
    console.log('✅ Dashboard initialized');
}

// ============================================================================
// WEBSOCKET CONNECTION - REAL BINANCE PRICES
// ============================================================================

function connectWebSocket() {
    const streams = AppConfig.SYMBOLS
        .map(s => `${s.toLowerCase()}@ticker`)
        .join('/');
    
    const wsUrl = `wss://stream.binance.com:9443/stream?streams=${streams}`;
    
    console.log('🔗 Connecting to Binance WebSocket...');
    
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('✅ WebSocket connected to REAL Binance stream');
        AppState.webSocketConnected = true;
        updateConnectionIndicator();
    };
    
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.data && data.data.s) {
                updatePriceFromWebSocket(data.data);
            }
        } catch (e) {
            console.error('WebSocket parse error:', e);
        }
    };
    
    ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        AppState.webSocketConnected = false;
        updateConnectionIndicator();
    };
    
    ws.onclose = () => {
        console.warn('⚠️ WebSocket disconnected');
        AppState.webSocketConnected = false;
        updateConnectionIndicator();
        
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
    };
}

function updatePriceFromWebSocket(tickerData) {
    const symbol = tickerData.s;
    const price = parseFloat(tickerData.c);
    const change = parseFloat(tickerData.P);
    
    if (AppState.priceData[symbol]) {
        AppState.priceData[symbol] = {
            price: price,
            change: change,
            timestamp: new Date()
        };
        
        // Update UI if on dashboard
        if (AppState.currentView === 'dashboard') {
            updatePriceDisplay(symbol);
        }
    }
}

// ============================================================================
// PERIODIC DATA UPDATES - FETCH REAL SIGNALS & STATS
// ============================================================================

function setupPeriodicUpdates() {
    // Initial fetch
    fetchRealData();
    
    // Periodic refresh
    setInterval(fetchRealData, AppConfig.REFRESH_INTERVAL);
    
    // Health check every 30 seconds
    setInterval(checkHealth, 30000);
}

function fetchRealData() {
    // Fetch signals (REAL from database)
    fetch(`${AppConfig.API_BASE}/api/signals?limit=100`)
        .then(r => r.json())
        .then(data => {
            if (data.signals) {
                AppState.signals = data.signals;
                if (AppState.currentView === 'signals') {
                    renderSignalsTable();
                }
            }
        })
        .catch(e => {
            console.error('❌ Signals fetch error:', e);
        });
    
    // Fetch statistics (REAL from database)
    fetch(`${AppConfig.API_BASE}/api/statistics`)
        .then(r => r.json())
        .then(data => {
            if (data.statistics) {
                AppState.statistics = data.statistics;
                if (AppState.currentView === 'dashboard' || AppState.currentView === 'analysis') {
                    renderStatistics();
                }
            }
        })
        .catch(e => {
            console.error('❌ Statistics fetch error:', e);
        });
}

function checkHealth() {
    fetch(`${AppConfig.API_BASE}/api/health`)
        .then(r => r.json())
        .then(data => {
            AppState.apiHealthy = data.status === 'OK';
            AppState.lastHealthCheck = new Date();
            updateConnectionIndicator();
        })
        .catch(e => {
            console.error('❌ Health check failed:', e);
            AppState.apiHealthy = false;
            updateConnectionIndicator();
        });
}

// ============================================================================
// NAVIGATION SETUP
// ============================================================================

function setupNavigation() {
    const navItems = document.querySelectorAll('[data-nav-item]');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.dataset.navItem;
            switchView(view);
            
            // Update active state
            navItems.forEach(nav => nav.classList.remove('nav-active'));
            item.classList.add('nav-active');
        });
    });
}

function switchView(viewName) {
    console.log(`📄 Switching to view: ${viewName}`);
    
    const views = document.querySelectorAll('[data-view]');
    views.forEach(view => view.classList.remove('view-active'));
    
    const targetView = document.querySelector(`[data-view="${viewName}"]`);
    if (targetView) {
        targetView.classList.add('view-active');
        AppState.currentView = viewName;
    }
}

// ============================================================================
// PRICE DISPLAY UPDATES
// ============================================================================

function updatePriceDisplay(symbol) {
    const priceData = AppState.priceData[symbol];
    const element = document.querySelector(`[data-symbol="${symbol}"]`);
    
    if (element && priceData) {
        const priceEl = element.querySelector('.price');
        const changeEl = element.querySelector('.change');
        
        if (priceEl) {
            priceEl.textContent = `$${priceData.price.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })}`;
        }
        
        if (changeEl) {
            const changeClass = priceData.change >= 0 ? 'positive' : 'negative';
            changeEl.className = `change ${changeClass}`;
            changeEl.textContent = `${priceData.change >= 0 ? '▲' : '▼'} ${Math.abs(priceData.change).toFixed(2)}%`;
        }
    }
}

// ============================================================================
// DASHBOARD RENDERING
// ============================================================================

function renderDashboard() {
    console.log('📊 Rendering dashboard...');
    
    // Render price cards
    renderPriceCards();
    
    // Render statistics
    renderStatistics();
    
    // Render connection status
    updateConnectionIndicator();
}

function renderPriceCards() {
    const container = document.getElementById('priceCardsContainer');
    if (!container) return;
    
    container.innerHTML = AppConfig.SYMBOLS.map(symbol => {
        const data = AppState.priceData[symbol];
        const nameMap = {
            'BTCUSDT': 'Bitcoin',
            'ETHUSDT': 'Ethereum',
            'LTCUSDT': 'Litecoin'
        };
        
        return `
            <div class="price-card" data-symbol="${symbol}">
                <div class="card-header">
                    <h3>${nameMap[symbol]}</h3>
                    <span class="symbol">${symbol}</span>
                </div>
                <div class="card-body">
                    <div class="price">$${data.price.toLocaleString()}</div>
                    <div class="change ${data.change >= 0 ? 'positive' : 'negative'}">
                        ${data.change >= 0 ? '▲' : '▼'} ${Math.abs(data.change).toFixed(2)}%
                    </div>
                </div>
                <div class="card-footer">
                    <span class="timestamp">${data.timestamp ? data.timestamp.toLocaleTimeString() : '--'}</span>
                </div>
            </div>
        `;
    }).join('');
}

function renderStatistics() {
    const stats = AppState.statistics;
    
    const statElements = {
        'totalTrades': stats.total_trades || 0,
        'longTrades': stats.long_trades || 0,
        'shortTrades': stats.short_trades || 0,
        'avgConfidence': `${((stats.avg_confidence || 0) * 100).toFixed(0)}%`,
        'avgScore': `${((stats.avg_ensemble_score || 0) * 100).toFixed(0)}%`,
        'winRate': stats.total_trades > 0 ? 
            `${((stats.winning_trades || 0) / stats.total_trades * 100).toFixed(0)}%` : 
            '0%',
        'totalPnL': `${((stats.total_pnl || 0) > 0 ? '+' : '')}${(stats.total_pnl || 0).toFixed(2)} USDT`
    };
    
    for (const [id, value] of Object.entries(statElements)) {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = value;
        }
    }
}

// ============================================================================
// SIGNALS TABLE RENDERING
// ============================================================================

function renderSignalsTable() {
    const table = document.getElementById('signalsTable');
    if (!table) return;
    
    if (!AppState.signals || AppState.signals.length === 0) {
        table.innerHTML = '<tr><td colspan="9" class="text-center">No signals yet...</td></tr>';
        return;
    }
    
    table.innerHTML = AppState.signals.map((signal, index) => {
        const rowClass = signal.direction === 'LONG' ? 'row-long' : 'row-short';
        const timestamp = signal.entry_time ? new Date(signal.entry_time).toLocaleString() : '--';
        
        return `
            <tr class="${rowClass}">
                <td>${index + 1}</td>
                <td><strong>${signal.symbol}</strong></td>
                <td class="direction">${signal.direction}</td>
                <td>$${parseFloat(signal.entry_price).toFixed(2)}</td>
                <td>$${parseFloat(signal.tp1).toFixed(2)}</td>
                <td>$${parseFloat(signal.tp2).toFixed(2)}</td>
                <td>$${parseFloat(signal.sl).toFixed(2)}</td>
                <td>${((signal.confidence || 0) * 100).toFixed(0)}%</td>
                <td>${timestamp}</td>
            </tr>
        `;
    }).join('');
}

// ============================================================================
// CONNECTION INDICATOR
// ============================================================================

function updateConnectionIndicator() {
    const indicator = document.getElementById('connectionIndicator');
    if (!indicator) return;
    
    const wsStatus = AppState.webSocketConnected ? '✅' : '❌';
    const apiStatus = AppState.apiHealthy ? '✅' : '❌';
    
    indicator.innerHTML = `
        <div class="status-item">
            <span class="label">WebSocket:</span>
            <span class="indicator">${wsStatus}</span>
        </div>
        <div class="status-item">
            <span class="label">API:</span>
            <span class="indicator">${apiStatus}</span>
        </div>
        <div class="status-item">
            <span class="label">Updated:</span>
            <span class="timestamp">${new Date().toLocaleTimeString()}</span>
        </div>
    `;
}

// ============================================================================
// CHART RENDERING (Chart.js or Plotly)
// ============================================================================

function renderPriceChart(symbol, data) {
    const container = document.getElementById(`chart-${symbol}`);
    if (!container) return;
    
    const prices = data.map(d => d.close);
    const timestamps = data.map(d => new Date(d.timestamp).toLocaleTimeString());
    
    // Using Plotly (lightweight)
    const trace = {
        x: timestamps,
        y: prices,
        type: 'scatter',
        mode: 'lines',
        name: symbol,
        line: { color: '#0066ff', width: 2 }
    };
    
    const layout = {
        title: `${symbol} - Last 100 Hours`,
        xaxis: { title: 'Time' },
        yaxis: { title: 'Price (USDT)' },
        margin: { t: 40, b: 40, l: 60, r: 40 }
    };
    
    if (window.Plotly) {
        Plotly.newPlot(container, [trace], layout, { responsive: true });
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

function formatPercent(value) {
    return `${(value * 100).toFixed(2)}%`;
}

function formatDateTime(date) {
    if (!date) return '--';
    return new Date(date).toLocaleString();
}

// ============================================================================
// ERROR HANDLING
// ============================================================================

window.addEventListener('error', (event) => {
    console.error('❌ Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('❌ Unhandled rejection:', event.reason);
});

// ============================================================================
// START APP
// ============================================================================

document.addEventListener('DOMContentLoaded', initializeApp);
