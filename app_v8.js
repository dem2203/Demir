// ================================================================
// DEMIR AI v8.0 - DASHBOARD JAVASCRIPT
// Complete Frontend Logic with Phase 1-4 Module Integrations
// ================================================================

// ================================================================
// GLOBAL STATE
// ================================================================

let socket = null;
let isConnected = false;
let signalCount = 0;
let performanceChart = null;

const priceCache = {};
const layerScoresCache = {};

// ================================================================
// WEBSOCKET CONNECTION
// ================================================================

function initializeWebSocket() {
    console.log('🔌 Connecting to WebSocket...');
    
    socket = io({
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: Infinity
    });
    
    // Connection events
    socket.on('connect', () => {
        console.log('✅ WebSocket connected');
        isConnected = true;
        updateConnectionStatus(true);
        
        // Subscribe to primary symbols
        socket.emit('subscribe_symbol', { symbol: 'BTCUSDT' });
        socket.emit('subscribe_symbol', { symbol: 'ETHUSDT' });
        socket.emit('subscribe_symbol', { symbol: 'BNBUSDT' });
    });
    
    socket.on('disconnect', () => {
        console.log('❌ WebSocket disconnected');
        isConnected = false;
        updateConnectionStatus(false);
    });
    
    socket.on('connect_error', (error) => {
        console.error('WebSocket error:', error);
        isConnected = false;
        updateConnectionStatus(false);
    });
    
    // Data events
    socket.on('price_update', handlePriceUpdate);
    socket.on('price_bulk', handlePriceBulk);
    socket.on('signal', handleNewSignal);
    socket.on('layer_scores', handleLayerScores);
    socket.on('performance_update', handlePerformanceUpdate);
    socket.on('health_status', handleHealthStatus);
}

function updateConnectionStatus(connected) {
    const dot = document.getElementById('connection-dot');
    const text = document.getElementById('connection-text');
    
    if (connected) {
        dot.classList.remove('disconnected');
        text.textContent = 'Bağlı';
    } else {
        dot.classList.add('disconnected');
        text.textContent = 'Bağlantı Kesildi';
    }
}

// ================================================================
// PRICE UPDATES
// ================================================================

function handlePriceUpdate(data) {
    const { symbol, price, change_24h } = data;
    priceCache[symbol] = { price, change_24h, timestamp: Date.now() };
    updatePriceCard(symbol, price, change_24h);
}

function handlePriceBulk(data) {
    for (const [symbol, info] of Object.entries(data)) {
        priceCache[symbol] = info;
        updatePriceCard(symbol, info.price, info.change_24h);
    }
}

function updatePriceCard(symbol, price, change_24h) {
    const ticker = document.getElementById('price-ticker');
    let card = document.getElementById(`price-card-${symbol}`);
    
    if (!card) {
        card = document.createElement('div');
        card.id = `price-card-${symbol}`;
        card.className = 'price-card';
        card.innerHTML = `
            <div class="price-symbol">
                <span>${symbol}</span>
                <span class="status-dot"></span>
            </div>
            <div class="price-value">$${formatPrice(price)}</div>
            <div class="price-change ${change_24h >= 0 ? 'positive' : 'negative'}">
                <span class="price-change-icon">${change_24h >= 0 ? '▲' : '▼'}</span>
                <span>${change_24h >= 0 ? '+' : ''}${change_24h.toFixed(2)}%</span>
            </div>
        `;
        const loading = ticker.querySelector('.loading');
        if (loading) loading.remove();
        ticker.appendChild(card);
    } else {
        card.querySelector('.price-value').textContent = `$${formatPrice(price)}`;
        const changeEl = card.querySelector('.price-change');
        changeEl.className = `price-change ${change_24h >= 0 ? 'positive' : 'negative'}`;
        changeEl.innerHTML = `
            <span class="price-change-icon">${change_24h >= 0 ? '▲' : '▼'}</span>
            <span>${change_24h >= 0 ? '+' : ''}${change_24h.toFixed(2)}%</span>
        `;
    }
}

function formatPrice(price) {
    return price.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// ================================================================
// SIGNALS
// ================================================================

function handleNewSignal(data) {
    signalCount++;
    document.getElementById('signal-count').textContent = signalCount;
    
    const signalList = document.getElementById('signal-list');
    const emptyState = signalList.querySelector('.empty-state');
    if (emptyState) emptyState.remove();
    
    const signalItem = document.createElement('div');
    signalItem.className = `signal-item ${data.direction.toLowerCase()}`;
    signalItem.innerHTML = `
        <div class="signal-header">
            <div class="signal-symbol">${data.symbol}</div>
            <div class="signal-direction ${data.direction.toLowerCase()}">${data.direction}</div>
        </div>
        <div class="signal-details">
            Entry: $${data.entry.toFixed(2)} | 
            TP1: $${data.tp1.toFixed(2)} | 
            SL: $${data.sl.toFixed(2)}
        </div>
        <div class="signal-confidence">
            <span>Confidence:</span>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: ${data.confidence * 100}%"></div>
            </div>
            <span>${(data.confidence * 100).toFixed(1)}%</span>
        </div>
    `;
    
    signalList.insertBefore(signalItem, signalList.firstChild);
    
    while (signalList.children.length > 20) {
        signalList.removeChild(signalList.lastChild);
    }
    
    playNotificationSound();
}

function playNotificationSound() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
    } catch (e) {
        console.log('Audio not supported');
    }
}

// ================================================================
// LAYER SCORES
// ================================================================

function handleLayerScores(data) {
    const { symbol, scores } = data;
    layerScoresCache[symbol] = scores;
    
    const selectedSymbol = document.getElementById('layer-symbol-select').value;
    if (symbol === selectedSymbol) {
        updateLayerGrid(scores);
    }
}

function updateLayerGrid(scores) {
    const grid = document.getElementById('layer-grid');
    const loading = grid.querySelector('.loading');
    if (loading) loading.remove();
    
    grid.innerHTML = '';
    
    const categories = {
        'Sentiment': [],
        'Technical': [],
        'ML Models': [],
        'On-Chain': []
    };
    
    for (const [name, score] of Object.entries(scores)) {
        if (name.includes('Sentiment') || name.includes('News') || name.includes('Fear')) {
            categories['Sentiment'].push({ name, score });
        } else if (name.includes('RSI') || name.includes('MACD') || name.includes('MA')) {
            categories['Technical'].push({ name, score });
        } else if (name.includes('LSTM') || name.includes('XGBoost') || name.includes('RF')) {
            categories['ML Models'].push({ name, score });
        } else {
            categories['On-Chain'].push({ name, score });
        }
    }
    
    for (const [category, layers] of Object.entries(categories)) {
        if (layers.length === 0) continue;
        
        layers.sort((a, b) => Math.abs(b.score) - Math.abs(a.score));
        
        const categoryCard = document.createElement('div');
        categoryCard.className = 'layer-category';
        categoryCard.innerHTML = `
            <div class="layer-category-title">${category}</div>
            <div class="layer-bars">
                ${layers.map(layer => `
                    <div class="layer-bar">
                        <div class="layer-name" title="${layer.name}">${layer.name}</div>
                        <div class="layer-progress">
                            <div class="layer-progress-fill ${layer.score < 0 ? 'negative' : ''}" 
                                 style="width: ${Math.abs(layer.score) * 100}%">
                                ${(layer.score * 100).toFixed(1)}%
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        grid.appendChild(categoryCard);
    }
}

document.getElementById('layer-symbol-select').addEventListener('change', (e) => {
    const symbol = e.target.value;
    if (layerScoresCache[symbol]) {
        updateLayerGrid(layerScoresCache[symbol]);
    }
    
    if (socket && isConnected) {
        socket.emit('subscribe_symbol', { symbol });
    }
});

// ================================================================
// PERFORMANCE CHART
// ================================================================

function initializePerformanceChart() {
    const ctx = document.getElementById('performance-canvas').getContext('2d');
    
    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Portfolio Value (USDT)',
                data: [],
                borderColor: '#00ff88',
                backgroundColor: 'rgba(0, 255, 136, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: '#00ff88',
                pointHoverBorderColor: '#fff',
                pointHoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(26, 31, 58, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#8892b0',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `$${context.parsed.y.toLocaleString('en-US', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            })}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.02)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#5a637a',
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.02)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#5a637a',
                        font: {
                            size: 11
                        },
                        callback: function(value) {
                            return '$' + value.toLocaleString('en-US', {
                                minimumFractionDigits: 0,
                                maximumFractionDigits: 0
                            });
                        }
                    }
                }
            }
        }
    });
}

function handlePerformanceUpdate(data) {
    document.getElementById('metric-total-signals').textContent = data.total_signals || 0;
    document.getElementById('metric-win-rate').textContent = `${(data.win_rate * 100).toFixed(1)}%`;
    document.getElementById('metric-pnl').textContent = `$${data.total_pnl.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
    document.getElementById('metric-sharpe').textContent = (data.sharpe_ratio || 0).toFixed(2);
    
    if (performanceChart && data.history) {
        performanceChart.data.labels = data.history.timestamps;
        performanceChart.data.datasets[0].data = data.history.values;
        performanceChart.update('none');
    }
}

// ================================================================
// NEW v8.0: ANALYTICS SUMMARY (ALL NEW WIDGETS)
// ================================================================

async function fetchAnalyticsSummary() {
    try {
        const response = await fetch('/api/analytics/summary');
        const result = await response.json();
        
        if (result.status === 'success' && result.data) {
            const data = result.data;
            
            // Smart Money Tracker
            if (data.smart_money) {
                updateSmartMoneyWidget(data.smart_money);
            }
            
            // Risk Engine
            if (data.risk_report) {
                updateRiskWidget(data.risk_report);
            }
            
            // Sentiment Gauge
            if (data.sentiment) {
                updateSentimentWidget(data.sentiment);
            }
            
            // Arbitrage Opportunities
            if (data.arbitrage_opportunity) {
                updateArbitrageWidget(data.arbitrage_opportunity);
            }
            
            // On-Chain Metrics
            if (data.onchain) {
                updateOnChainWidget(data.onchain);
            }
            
            // Pattern Recognition
            if (data.patterns) {
                updatePatternWidget(data.patterns);
            }
        }
    } catch (error) {
        console.error('Error fetching analytics summary:', error);
    }
}

// ================================================================
// NEW v8.0: SMART MONEY TRACKER WIDGET
// ================================================================

function updateSmartMoneyWidget(data) {
    const list = document.getElementById('smart-money-list');
    const emptyState = list.querySelector('.empty-state');
    if (emptyState) emptyState.remove();
    
    list.innerHTML = '';
    
    if (!data || !data.signals || data.signals.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🐳</div>
                <div>Whale hareketleri tespit edilemedi</div>
            </div>
        `;
        return;
    }
    
    data.signals.slice(0, 5).forEach(signal => {
        const transaction = document.createElement('div');
        transaction.className = 'whale-transaction';
        transaction.innerHTML = `
            <div class="whale-header">
                <div class="whale-amount">$${(signal.amount / 1000000).toFixed(2)}M</div>
                <div class="whale-type ${signal.type.toLowerCase()}">${signal.type}</div>
            </div>
            <div class="whale-details">
                <div>${signal.symbol} • ${signal.exchange || 'Unknown'}</div>
                <div style="font-size: 11px; opacity: 0.6; margin-top: 4px;">
                    ${new Date(signal.timestamp).toLocaleTimeString('tr-TR')}
                </div>
            </div>
        `;
        list.appendChild(transaction);
    });
}

// ================================================================
// NEW v8.0: RISK ENGINE WIDGET
// ================================================================

function updateRiskWidget(data) {
    if (!data) return;
    
    // Update VAR
    const varValue = data.var || data.portfolio_var || 0;
    document.getElementById('risk-var').textContent = `$${Math.abs(varValue).toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    })}`;
    
    // Update needle position (0-100 scale, rotate from -90deg to +90deg)
    const riskScore = data.risk_score || 50; // 0-100
    const needleRotation = -90 + (riskScore * 1.8); // Map 0-100 to -90 to +90
    document.getElementById('risk-needle').style.transform = `translateX(-50%) rotate(${needleRotation}deg)`;
    
    // Update metrics
    document.getElementById('risk-sharpe').textContent = (data.sharpe_ratio || 0).toFixed(2);
    document.getElementById('risk-kelly').textContent = `${((data.kelly_fraction || 0) * 100).toFixed(1)}%`;
    document.getElementById('risk-drawdown').textContent = `${(Math.abs(data.max_drawdown || 0) * 100).toFixed(1)}%`;
    document.getElementById('risk-position').textContent = `${((data.position_size || 0) * 100).toFixed(1)}%`;
}

// ================================================================
// NEW v8.0: SENTIMENT WIDGET
// ================================================================

function updateSentimentWidget(data) {
    if (!data) return;
    
    const score = data.aggregate_sentiment || data.score || 50; // 0-100
    const circle = document.getElementById('sentiment-circle');
    const scoreEl = document.getElementById('sentiment-score');
    const labelEl = document.getElementById('sentiment-label');
    
    scoreEl.textContent = Math.round(score);
    
    // Determine sentiment class
    if (score >= 60) {
        circle.className = 'sentiment-circle bullish';
        labelEl.textContent = 'BULLISH';
    } else if (score <= 40) {
        circle.className = 'sentiment-circle bearish';
        labelEl.textContent = 'BEARISH';
    } else {
        circle.className = 'sentiment-circle neutral';
        labelEl.textContent = 'NEUTRAL';
    }
    
    // Update sources (if available)
    if (data.sources && Array.isArray(data.sources)) {
        const sourcesEl = document.getElementById('sentiment-sources');
        sourcesEl.innerHTML = data.sources.map(source => 
            `<span class="sentiment-source">${source}</span>`
        ).join('');
    }
}

// ================================================================
// NEW v8.0: ARBITRAGE WIDGET
// ================================================================

function updateArbitrageWidget(data) {
    const list = document.getElementById('arbitrage-list');
    const emptyState = list.querySelector('.empty-state');
    if (emptyState) emptyState.remove();
    
    list.innerHTML = '';
    
    if (!data || !data.opportunities || data.opportunities.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔄</div>
                <div>Arbitrage fırsatı bulunamadı</div>
            </div>
        `;
        return;
    }
    
    data.opportunities.slice(0, 5).forEach(opp => {
        const item = document.createElement('div');
        item.className = 'arbitrage-opportunity';
        item.innerHTML = `
            <div class="arb-header">
                <div class="arb-symbol">${opp.symbol}</div>
                <div class="arb-spread">+${(opp.spread * 100).toFixed(2)}%</div>
            </div>
            <div class="arb-exchanges">
                <div class="arb-exchange">
                    <div style="font-weight: 600;">${opp.buy_exchange}</div>
                    <div>$${opp.buy_price.toFixed(2)}</div>
                </div>
                <div class="arb-arrow">→</div>
                <div class="arb-exchange">
                    <div style="font-weight: 600;">${opp.sell_exchange}</div>
                    <div>$${opp.sell_price.toFixed(2)}</div>
                </div>
            </div>
        `;
        list.appendChild(item);
    });
}

// ================================================================
// NEW v8.0: ON-CHAIN WIDGET
// ================================================================

function updateOnChainWidget(data) {
    const container = document.getElementById('onchain-metrics');
    const loading = container.querySelector('.loading');
    if (loading) loading.remove();
    
    container.innerHTML = '';
    
    if (!data) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">⛓️</div>
                <div>On-chain veri yüklenemiyor</div>
            </div>
        `;
        return;
    }
    
    const metrics = [
        { label: 'BTC UTXO Age', value: data.btc_utxo_age || 'N/A', change: data.btc_utxo_change || 0 },
        { label: 'ETH Gas Price', value: `${data.eth_gas_price || 0} Gwei`, change: data.eth_gas_change || 0 },
        { label: 'DeFi TVL', value: `$${((data.defi_tvl || 0) / 1000000000).toFixed(2)}B`, change: data.defi_tvl_change || 0 },
        { label: 'Whale Supply', value: `${(data.whale_supply || 0).toFixed(1)}%`, change: data.whale_supply_change || 0 }
    ];
    
    metrics.forEach(metric => {
        const metricEl = document.createElement('div');
        metricEl.className = 'onchain-metric';
        metricEl.innerHTML = `
            <div class="onchain-metric-info">
                <div class="onchain-metric-label">${metric.label}</div>
                <div class="onchain-metric-value">${metric.value}</div>
            </div>
            <div class="onchain-metric-change ${metric.change >= 0 ? 'positive' : 'negative'}">
                ${metric.change >= 0 ? '+' : ''}${metric.change.toFixed(1)}%
            </div>
        `;
        container.appendChild(metricEl);
    });
}

// ================================================================
// NEW v8.0: PATTERN WIDGET
// ================================================================

function updatePatternWidget(data) {
    const list = document.getElementById('pattern-list');
    const emptyState = list.querySelector('.empty-state');
    if (emptyState) emptyState.remove();
    
    list.innerHTML = '';
    
    if (!data || !data.detected || data.detected.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <div>Pattern tespit edilemedi</div>
            </div>
        `;
        return;
    }
    
    data.detected.slice(0, 5).forEach(pattern => {
        const alert = document.createElement('div');
        alert.className = 'pattern-alert';
        alert.innerHTML = `
            <div class="pattern-header">
                <div class="pattern-name">${pattern.name}</div>
                <div class="pattern-confidence">${(pattern.confidence * 100).toFixed(0)}%</div>
            </div>
            <div class="pattern-details">
                ${pattern.symbol} • ${pattern.timeframe || '1H'}
            </div>
            <div class="pattern-direction ${pattern.direction.toLowerCase()}">
                ${pattern.direction}
            </div>
        `;
        list.appendChild(alert);
    });
}

// ================================================================
// HEALTH STATUS
// ================================================================

function handleHealthStatus(data) {
    const healthPercentage = Object.values(data).filter(v => v === true).length / 
                             Object.keys(data).filter(k => k !== 'last_check').length * 100;
    
    document.getElementById('metric-api-health').textContent = `${Math.round(healthPercentage)}%`;
}

// ================================================================
// OPPORTUNITIES (EXISTING)
// ================================================================

async function fetchOpportunities() {
    try {
        const response = await fetch('/api/advisor/opportunities?limit=10&min_confidence=0.75');
        const result = await response.json();
        
        if (result.status === 'success') {
            updateOpportunities(result.data);
        }
    } catch (error) {
        console.error('Error fetching opportunities:', error);
    }
}

function updateOpportunities(opportunities) {
    const list = document.getElementById('opportunity-list');
    const emptyState = list.querySelector('.empty-state');
    if (emptyState) emptyState.remove();
    
    list.innerHTML = '';
    
    if (opportunities.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <div>Şu anda fırsat bulunamadı</div>
            </div>
        `;
        return;
    }
    
    opportunities.forEach(opp => {
        const card = document.createElement('div');
        card.className = 'opportunity-card';
        card.innerHTML = `
            <div class="opportunity-header">
                <div class="opportunity-symbol">${opp.symbol}</div>
                <div class="opportunity-score">${(opp.score * 100).toFixed(0)}%</div>
            </div>
            <div class="opportunity-details">
                <div>Direction: <strong>${opp.direction}</strong></div>
                <div>Entry: $${opp.entry_price.toFixed(2)}</div>
                <div>Target: $${opp.target_price.toFixed(2)} (+${opp.potential_gain.toFixed(1)}%)</div>
            </div>
        `;
        list.appendChild(card);
    });
}

// ================================================================
// SYSTEM TIME
// ================================================================

function updateSystemTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('tr-TR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('system-time').textContent = timeString;
}

setInterval(updateSystemTime, 1000);

// ================================================================
// INITIALIZATION
// ================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DEMIR AI Dashboard v8.0 - Initializing...');
    
    // Initialize chart
    initializePerformanceChart();
    
    // Connect WebSocket
    initializeWebSocket();
    
    // Start system time
    updateSystemTime();
    
    // Fetch initial data
    fetchOpportunities();
    fetchAnalyticsSummary();
    
    // Set up polling for v8.0 widgets (every 30 seconds)
    setInterval(fetchAnalyticsSummary, 30000);
    setInterval(fetchOpportunities, 30000);
    
    console.log('✅ Dashboard v8.0 initialized with all Phase 1-4 widgets');
});
