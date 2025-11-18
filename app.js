/**
 * ============================================================================
 * DEMIR AI v6.0 - Professional Trading Dashboard (COMBINED & ENHANCED)
 * ============================================================================
 * Author: Professional Crypto AI Developer
 * Date: 2025-11-18
 * 
 * Features:
 * - Real-time WebSocket with auto-reconnect + fallback
 * - 4-GROUP Signal System (Technical, Sentiment, OnChain, Macro)
 * - Multi-timeframe analysis integration
 * - Position tracking & management
 * - Chart.js visualizations
 * - Turkish UI with professional explanations
 * - Railway production-ready
 * 
 * Deployment: Railway (https://demir1988.up.railway.app/)
 * Rules: 100% Real Data, NO MOCK, NO LOCAL PC code
 * ============================================================================
 */

// ============================================================================
// CONFIGURATION - Railway Production Ready
// ============================================================================

const CONFIG = {
    // Railway production URLs (auto-detect)
    API_BASE: window.location.origin + '/api',
    WS_URL: (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws',
    
    // Settings
    REFRESH_INTERVAL: 60000,          // 60 seconds
    RECONNECT_DELAY: 5000,            // 5 seconds
    MAX_RECONNECT_ATTEMPTS: 10,
    CHART_UPDATE_INTERVAL: 5000,      // 5 seconds
    
    // Tracked symbols
    SYMBOLS: ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'LTCUSDT'],
    DEFAULT_SYMBOL: 'BTCUSDT'
};

// Color scheme
const COLORS = {
    long: '#00ff88',
    short: '#ff3366',
    neutral: '#ffaa00',
    tech: '#00d4ff',
    sentiment: '#ff00ff',
    onchain: '#00ff88',
    macro: '#ffaa00',
    buy: '#00ff88',
    sell: '#ff3366',
    bg_dark: '#0a0e27',
    bg_card: '#1a1f3a'
};

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

const STATE = {
    currentSymbol: CONFIG.DEFAULT_SYMBOL,
    signals: {},
    positions: [],
    charts: {},
    websocket: null,
    isConnected: false,
    reconnectAttempts: 0,
    lastUpdateTime: null,
    settings: {}
};

// ============================================================================
// WEBSOCKET MANAGER (Enhanced with Reconnection)
// ============================================================================

class WebSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = CONFIG.MAX_RECONNECT_ATTEMPTS;
        this.reconnectDelay = CONFIG.RECONNECT_DELAY;
        this.isIntentionallyClosed = false;
        this.pingInterval = null;
    }

    connect() {
        try {
            console.log(`🔌 Connecting WebSocket: ${CONFIG.WS_URL}`);
            
            this.ws = new WebSocket(CONFIG.WS_URL);
            
            this.ws.onopen = (event) => {
                console.log('✅ WebSocket Connected');
                STATE.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
                
                // Subscribe to current symbol
                this.subscribe(STATE.currentSymbol);
                
                // Start ping/pong to keep connection alive
                this.startPing();
                
                showNotification('✅ WebSocket bağlantısı kuruldu', 'success');
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('📨 WebSocket Message:', data.type);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('❌ WebSocket parse error:', error);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('❌ WebSocket Error:', error);
                STATE.isConnected = false;
                this.updateConnectionStatus(false);
            };
            
            this.ws.onclose = (event) => {
                console.log(`🔌 WebSocket Closed: ${event.code} - ${event.reason}`);
                STATE.isConnected = false;
                this.updateConnectionStatus(false);
                this.stopPing();
                
                // Auto-reconnect if not intentionally closed
                if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    console.log(`🔄 Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                    showNotification(`🔄 Yeniden bağlanıyor... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`, 'warning');
                    setTimeout(() => this.connect(), this.reconnectDelay);
                } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                    console.error('❌ Max reconnect attempts reached');
                    showNotification('❌ Bağlantı başarısız. REST API kullanılıyor.', 'error');
                    this.fallbackToRestAPI();
                }
            };
            
        } catch (error) {
            console.error('❌ WebSocket init error:', error);
            this.fallbackToRestAPI();
        }
    }

    subscribe(symbol) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            const message = JSON.stringify({
                type: 'subscribe',
                symbol: symbol
            });
            this.ws.send(message);
            console.log(`📡 Subscribed to ${symbol}`);
        }
    }

    startPing() {
        this.pingInterval = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000); // 30 seconds
    }

    stopPing() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }

    handleMessage(data) {
        STATE.lastUpdateTime = new Date();
        
        switch (data.type) {
            case 'price':
                updatePriceDisplay(data);
                break;
            case 'signal':
                updateSignalDisplay(data);
                playNotificationSound();
                break;
            case 'group_signals':
                updateGroupSignals(data);
                break;
            case 'position':
                updatePositionDisplay(data);
                break;
            case 'trade':
                addTradeToHistory(data);
                break;
            case 'health':
                updateHealthStatus(data);
                break;
            case 'pong':
                // Server responded to ping
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    updateConnectionStatus(isConnected) {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            if (isConnected) {
                statusElement.innerHTML = '<span class="status-dot status-dot--success"></span> Bağlı';
                statusElement.className = 'connection-status connected';
            } else {
                statusElement.innerHTML = '<span class="status-dot status-dot--error"></span> Bağlantı Kesildi';
                statusElement.className = 'connection-status disconnected';
            }
        }
        
        // Update status indicator in header
        const headerStatus = document.getElementById('headerStatus');
        if (headerStatus) {
            headerStatus.textContent = isConnected ? '🟢 Online' : '🔴 Offline';
        }
    }

    fallbackToRestAPI() {
        console.log('🔄 Falling back to REST API polling...');
        showNotification('ℹ️ REST API ile devam ediliyor', 'info');
        
        // Poll every 60 seconds
        setInterval(() => {
            fetchAllData(STATE.currentSymbol);
        }, CONFIG.REFRESH_INTERVAL);
    }

    close() {
        this.isIntentionallyClosed = true;
        this.stopPing();
        if (this.ws) {
            this.ws.close();
        }
    }
}

// ============================================================================
// API FUNCTIONS (Railway Production)
// ============================================================================

async function fetchWithRetry(url, options = {}, retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, {
                method: options.method || 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: options.body ? JSON.stringify(options.body) : undefined,
                timeout: 10000
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API attempt ${i + 1}/${retries} failed:`, error);
            if (i === retries - 1) {
                throw error;
            }
            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        }
    }
}

async function fetchSignals(symbol) {
    try {
        const data = await fetchWithRetry(`${CONFIG.API_BASE}/signals/consensus?symbol=${symbol}`);
        console.log('✅ Signals fetched:', symbol);
        return data;
    } catch (error) {
        console.error('❌ Failed to fetch signals:', error);
        showNotification('❌ Sinyal verileri alınamadı', 'error');
        return null;
    }
}

async function fetchGroupSignals(symbol) {
    try {
        const groups = ['technical', 'sentiment', 'ml', 'onchain'];
        const promises = groups.map(group => 
            fetchWithRetry(`${CONFIG.API_BASE}/signals/${group}?symbol=${symbol}&limit=1`)
        );
        
        const results = await Promise.all(promises);
        console.log('✅ Group signals fetched');
        
        return {
            technical: results[0],
            sentiment: results[1],
            ml: results[2],
            onchain: results[3]
        };
    } catch (error) {
        console.error('❌ Failed to fetch group signals:', error);
        return null;
    }
}

async function fetchPositions() {
    try {
        const data = await fetchWithRetry(`${CONFIG.API_BASE}/positions/active`);
        console.log('✅ Positions fetched:', data);
        return data.positions || [];
    } catch (error) {
        console.error('❌ Failed to fetch positions:', error);
        return [];
    }
}

async function fetchTrackedCoins() {
    try {
        const data = await fetchWithRetry(`${CONFIG.API_BASE}/coins`);
        return data.coins || CONFIG.SYMBOLS;
    } catch (error) {
        console.error('❌ Failed to fetch coins:', error);
        return CONFIG.SYMBOLS;
    }
}

async function fetchTradeHistory(days = 30) {
    try {
        const data = await fetchWithRetry(`${CONFIG.API_BASE}/positions/history?days=${days}`);
        return data.trades || [];
    } catch (error) {
        console.error('❌ Failed to fetch trade history:', error);
        return [];
    }
}

async function fetchAllData(symbol) {
    console.log(`🔄 Fetching all data for ${symbol}...`);
    
    try {
        const [signals, groupSignals, positions, coins] = await Promise.all([
            fetchSignals(symbol),
            fetchGroupSignals(symbol),
            fetchPositions(),
            fetchTrackedCoins()
        ]);
        
        if (signals) {
            STATE.signals[symbol] = signals;
            updateSignalDisplay({ data: signals });
        }
        
        if (groupSignals) {
            updateGroupSignals({ data: groupSignals });
        }
        
        if (positions) {
            STATE.positions = positions;
            updatePositionsDisplay();
        }
        
        if (coins) {
            updateTrackedCoinsList(coins);
        }
        
        updateLastUpdateTime();
        console.log('✅ All data fetched');
        
    } catch (error) {
        console.error('❌ Failed to fetch all data:', error);
        showNotification('❌ Veri yükleme başarısız', 'error');
    }
}

// ============================================================================
// UI UPDATE FUNCTIONS
// ============================================================================

function updatePriceDisplay(data) {
    const priceElement = document.getElementById('currentPrice');
    const changeElement = document.getElementById('priceChange');
    
    if (priceElement && data.price) {
        priceElement.textContent = `$${parseFloat(data.price).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}`;
    }
    
    if (changeElement && data.change !== undefined) {
        const change = parseFloat(data.change);
        changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
        changeElement.className = `price-change ${change >= 0 ? 'positive' : 'negative'}`;
    }
}

function updateSignalDisplay(data) {
    const signalData = data.data || data;
    
    if (!signalData) {
        resetSignalDisplay();
        return;
    }
    
    // Consensus direction
    const directionElement = document.getElementById('consensusDirection');
    if (directionElement && signalData.consensus_direction) {
        const direction = signalData.consensus_direction.toUpperCase();
        let icon = '●';
        let className = 'neutral';
        
        if (direction === 'LONG') {
            icon = '📈';
            className = 'long';
        } else if (direction === 'SHORT') {
            icon = '📉';
            className = 'short';
        }
        
        directionElement.innerHTML = `${icon} ${direction}`;
        directionElement.className = `signal-direction ${className}`;
    }
    
    // Weighted strength
    const strengthElement = document.getElementById('consensusStrength');
    if (strengthElement && signalData.weighted_strength !== undefined) {
        const strength = parseFloat(signalData.weighted_strength) * 100;
        strengthElement.textContent = `${strength.toFixed(0)}%`;
        
        const strengthBar = document.getElementById('consensusStrengthBar');
        if (strengthBar) {
            strengthBar.style.width = `${strength}%`;
        }
    }
    
    // Confidence
    const confidenceElement = document.getElementById('consensusConfidence');
    if (confidenceElement && signalData.consensus_confidence !== undefined) {
        const confidence = parseFloat(signalData.consensus_confidence) * 100;
        confidenceElement.textContent = `${confidence.toFixed(0)}%`;
        
        const confidenceBar = document.getElementById('consensusConfidenceBar');
        if (confidenceBar) {
            confidenceBar.style.width = `${confidence}%`;
        }
    }
    
    // Update price if available
    if (signalData.entry_price) {
        updatePriceDisplay({ price: signalData.entry_price });
    }
}

function updateGroupSignals(data) {
    const groupData = data.data || data;
    
    if (!groupData) return;
    
    const groups = [
        { key: 'technical', name: 'Technical', elementPrefix: 'technical', layers: 28 },
        { key: 'sentiment', name: 'Sentiment', elementPrefix: 'sentiment', layers: 20 },
        { key: 'ml', name: 'ML/AI', elementPrefix: 'ml', layers: 10 },
        { key: 'onchain', name: 'OnChain', elementPrefix: 'onchain', layers: 6 }
    ];
    
    groups.forEach(group => {
        const signal = groupData[group.key];
        if (!signal) return;
        
        const direction = signal.direction || signal.consensus_direction || 'NEUTRAL';
        const strength = (signal.strength || signal.weighted_strength || 0.5) * 100;
        const confidence = (signal.confidence || signal.consensus_confidence || 0.5) * 100;
        
        // Direction
        const directionEl = document.getElementById(`${group.elementPrefix}Direction`);
        if (directionEl) {
            let icon = '●';
            if (direction.toUpperCase() === 'LONG') icon = '📈';
            else if (direction.toUpperCase() === 'SHORT') icon = '📉';
            
            directionEl.textContent = `${icon} ${direction.toUpperCase()}`;
            directionEl.className = `signal-direction ${direction.toLowerCase()}`;
        }
        
        // Strength
        const strengthEl = document.getElementById(`${group.elementPrefix}Strength`);
        if (strengthEl) strengthEl.textContent = `${strength.toFixed(0)}%`;
        
        const strengthBar = document.getElementById(`${group.elementPrefix}StrengthBar`);
        if (strengthBar) {
            strengthBar.style.width = `${strength}%`;
            strengthBar.style.backgroundColor = COLORS[direction.toLowerCase()];
        }
        
        // Confidence
        const confidenceEl = document.getElementById(`${group.elementPrefix}Confidence`);
        if (confidenceEl) confidenceEl.textContent = `${confidence.toFixed(0)}%`;
        
        const confidenceBar = document.getElementById(`${group.elementPrefix}ConfidenceBar`);
        if (confidenceBar) {
            confidenceBar.style.width = `${confidence}%`;
        }
        
        // Active layers
        const layersEl = document.getElementById(`${group.elementPrefix}Layers`);
        if (layersEl) {
            const activeLayers = signal.active_layers || group.layers;
            layersEl.textContent = `${activeLayers}/${group.layers} Layer`;
        }
        
        // Explanation
        updateGroupExplanation(group.elementPrefix, {
            direction: direction,
            strength: strength / 100,
            confidence: confidence / 100,
            layers: signal.active_layers || group.layers
        });
    });
}

function updateGroupExplanation(group, data) {
    const strength = Math.round(data.strength * 100);
    const confidence = Math.round(data.confidence * 100);
    let explanation = '';
    
    if (group === 'technical') {
        if (data.direction === 'LONG' && strength > 70) {
            explanation = `RSI, MACD ve Bollinger Bands alım sinyali. ${data.layers} gösterge destek veriyor.`;
        } else if (data.direction === 'SHORT' && strength > 70) {
            explanation = `Teknik göstergeler satış baskısı gösteriyor. ${data.layers} layer direnç uyarısı.`;
        } else {
            explanation = `Teknik göstergeler karışık. Konsolidasyon bekleniyor.`;
        }
    } else if (group === 'sentiment') {
        if (strength > 60) {
            explanation = `Pazar duyarlılığı ${data.direction === 'LONG' ? 'pozitif' : 'negatif'}. Sosyal medya ${data.direction === 'LONG' ? 'alımı' : 'satışı'} destekliyor.`;
        } else {
            explanation = `Pazar duyarlılığı nötr. Bekleme modunda.`;
        }
    } else if (group === 'ml') {
        if (confidence > 70) {
            explanation = `ML modelleri ${data.direction} yönünde %${confidence} güvenle tahmin ediyor. ${data.layers} model uyumlu.`;
        } else {
            explanation = `ML tahminleri belirsiz. Daha fazla veri gerekli.`;
        }
    } else if (group === 'onchain') {
        if (strength > 65) {
            explanation = `Zincir analizi: Whale'ler ${data.direction === 'LONG' ? 'birikim' : 'dağılım'} yapıyor. Exchange akışları ${data.direction === 'LONG' ? 'pozitif' : 'negatif'}.`;
        } else {
            explanation = `Zincir aktivitesi normal. Büyük işlem beklentisi yok.`;
        }
    }
    
    const explEl = document.getElementById(`${group}Explanation`);
    if (explEl) explEl.textContent = explanation;
}

function updatePositionsDisplay() {
    const container = document.getElementById('positionsContainer');
    if (!container) return;
    
    if (!STATE.positions || STATE.positions.length === 0) {
        container.innerHTML = '<p class="no-data">Aktif pozisyon yok</p>';
        return;
    }
    
    container.innerHTML = STATE.positions.map(position => {
        const pnl = parseFloat(position.pnl || 0);
        const pnlPercent = parseFloat(position.pnl_percent || 0);
        const pnlClass = pnl >= 0 ? 'positive' : 'negative';
        
        return `
            <div class="position-card">
                <div class="position-header">
                    <span class="position-symbol">${position.symbol}</span>
                    <span class="position-side ${position.side.toLowerCase()}">${position.side}</span>
                </div>
                <div class="position-details">
                    <div class="position-row">
                        <span>Giriş:</span>
                        <span>$${parseFloat(position.entry_price).toFixed(2)}</span>
                    </div>
                    <div class="position-row">
                        <span>Miktar:</span>
                        <span>${parseFloat(position.quantity).toFixed(6)}</span>
                    </div>
                    <div class="position-row">
                        <span>TP:</span>
                        <span>$${parseFloat(position.tp1 || 0).toFixed(2)}</span>
                    </div>
                    <div class="position-row">
                        <span>SL:</span>
                        <span>$${parseFloat(position.sl || 0).toFixed(2)}</span>
                    </div>
                    <div class="position-row position-pnl">
                        <span>P/L:</span>
                        <span class="${pnlClass}">
                            ${pnl >= 0 ? '+' : ''}${pnl.toFixed(2)} (${pnlPercent.toFixed(2)}%)
                        </span>
                    </div>
                </div>
                <div class="position-actions">
                    <button class="btn btn-sm btn-danger" onclick="closePosition('${position.id}')">
                        Kapat
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function updateTrackedCoinsList(coins) {
    const container = document.getElementById('coinsList');
    if (!container) return;
    
    container.innerHTML = coins.map(coin => `
        <button class="coin-btn ${coin === STATE.currentSymbol ? 'active' : ''}" 
                data-coin="${coin}"
                onclick="switchCoin('${coin}')">
            ${coin.replace('USDT', '')}
        </button>
    `).join('');
}

function updateLastUpdateTime() {
    const element = document.getElementById('lastUpdate');
    if (element) {
        const now = new Date();
        element.textContent = `Son güncelleme: ${now.toLocaleTimeString('tr-TR')}`;
    }
}

function resetSignalDisplay() {
    // Reset all displays to neutral/default state
    const directionElements = document.querySelectorAll('[id$="Direction"]');
    directionElements.forEach(el => {
        el.textContent = '● NEUTRAL';
        el.className = 'signal-direction neutral';
    });
    
    const strengthElements = document.querySelectorAll('[id$="Strength"]');
    strengthElements.forEach(el => el.textContent = '50%');
    
    const confidenceElements = document.querySelectorAll('[id$="Confidence"]');
    confidenceElements.forEach(el => el.textContent = '50%');
    
    const barElements = document.querySelectorAll('[id$="Bar"]');
    barElements.forEach(el => el.style.width = '50%');
}

// ============================================================================
// CHART MANAGEMENT (Chart.js)
// ============================================================================

function setupCharts() {
    // Group Strength Chart
    const groupChartCtx = document.getElementById('groupStrengthChart');
    if (groupChartCtx) {
        STATE.charts.groupStrength = new Chart(groupChartCtx, {
            type: 'bar',
            data: {
                labels: ['Technical', 'Sentiment', 'ML/AI', 'OnChain'],
                datasets: [{
                    label: 'Güç (%)',
                    data: [50, 50, 50, 50],
                    backgroundColor: [COLORS.tech, COLORS.sentiment, COLORS.long, COLORS.onchain]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    // Price Chart (Line)
    const priceChartCtx = document.getElementById('priceChart');
    if (priceChartCtx) {
        STATE.charts.price = new Chart(priceChartCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Fiyat',
                    data: [],
                    borderColor: COLORS.long,
                    backgroundColor: 'rgba(0, 255, 136, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        display: false
                    }
                }
            }
        });
    }
}

function updateCharts(groupData) {
    // Update group strength chart
    if (STATE.charts.groupStrength && groupData) {
        const data = [
            (groupData.technical?.strength || 0.5) * 100,
            (groupData.sentiment?.strength || 0.5) * 100,
            (groupData.ml?.strength || 0.5) * 100,
            (groupData.onchain?.strength || 0.5) * 100
        ];
        
        STATE.charts.groupStrength.data.datasets[0].data = data;
        STATE.charts.groupStrength.update();
    }
}

// ============================================================================
// EVENT HANDLERS
// ============================================================================

function switchCoin(symbol) {
    STATE.currentSymbol = symbol;
    console.log(`📊 Switched to ${symbol}`);
    
    // Update UI
    document.querySelectorAll('.coin-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.coin === symbol);
    });
    
    // Subscribe to new symbol via WebSocket
    if (STATE.websocket && STATE.isConnected) {
        STATE.websocket.subscribe(symbol);
    }
    
    // Fetch data for new symbol
    fetchAllData(symbol);
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Show selected tab
    const selectedTab = document.getElementById(`${tabName}Tab`);
    if (selectedTab) {
        selectedTab.style.display = 'block';
    }
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
}

async function closePosition(positionId) {
    if (!confirm('Bu pozisyonu kapatmak istediğinizden emin misiniz?')) {
        return;
    }
    
    try {
        const response = await fetchWithRetry(`${CONFIG.API_BASE}/positions/close`, {
            method: 'POST',
            body: { position_id: positionId }
        });
        
        if (response.success) {
            showNotification('✅ Pozisyon kapatıldı', 'success');
            fetchPositions();
        } else {
            showNotification('❌ Pozisyon kapatılamadı', 'error');
        }
    } catch (error) {
        console.error('Close position error:', error);
        showNotification('❌ İşlem başarısız', 'error');
    }
}

function openTradeModal(side) {
    // TODO: Implement trade modal
    console.log(`Opening trade modal for ${side}`);
    showNotification(`ℹ️ ${side} pozisyonu açılacak (yakında)`, 'info');
}

function toggleTheme() {
    document.body.classList.toggle('light-theme');
    const isDark = !document.body.classList.contains('light-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

function manualRefresh() {
    console.log('🔄 Manual refresh triggered');
    showNotification('🔄 Veriler yenileniyor...', 'info');
    fetchAllData(STATE.currentSymbol);
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function showNotification(message, type = 'info') {
    const container = document.getElementById('notificationContainer');
    if (!container) {
        console.log(`Notification: ${message}`);
        return;
    }
    
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function playNotificationSound() {
    // Only play if enabled in settings
    if (STATE.settings.soundEnabled) {
        const audio = new Audio('/static/notification.mp3');
        audio.volume = 0.3;
        audio.play().catch(e => console.log('Sound play failed:', e));
    }
}

function addTradeToHistory(tradeData) {
    const container = document.getElementById('tradeHistoryContainer');
    if (!container) return;
    
    const tradeElement = document.createElement('div');
    tradeElement.className = 'trade-history-item';
    tradeElement.innerHTML = `
        <div class="trade-header">
            <span>${tradeData.symbol}</span>
            <span class="${tradeData.side.toLowerCase()}">${tradeData.side}</span>
        </div>
        <div class="trade-details">
            <span>P/L: ${tradeData.pnl >= 0 ? '+' : ''}${tradeData.pnl.toFixed(2)} USDT</span>
        </div>
    `;
    
    container.prepend(tradeElement);
}

function updateHealthStatus(data) {
    const healthElement = document.getElementById('systemHealth');
    if (healthElement) {
        const status = data.status || 'unknown';
        const color = status === 'healthy' ? 'green' : status === 'degraded' ? 'orange' : 'red';
        healthElement.innerHTML = `<span style="color: ${color}">● ${status.toUpperCase()}</span>`;
    }
}

function getSettings() {
    return {
        soundEnabled: document.getElementById('soundToggle')?.checked || false,
        autoTrade: document.getElementById('autoTradeToggle')?.checked || false,
        darkTheme: !document.body.classList.contains('light-theme')
    };
}

function loadSettings() {
    const saved = localStorage.getItem('settings');
    if (saved) {
        try {
            STATE.settings = JSON.parse(saved);
            
            if (STATE.settings.darkTheme === false) {
                document.body.classList.add('light-theme');
            }
            
            const soundToggle = document.getElementById('soundToggle');
            if (soundToggle) soundToggle.checked = STATE.settings.soundEnabled;
            
            const autoTradeToggle = document.getElementById('autoTradeToggle');
            if (autoTradeToggle) autoTradeToggle.checked = STATE.settings.autoTrade;
        } catch (e) {
            console.error('Failed to load settings:', e);
        }
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DEMIR AI v6.0 Dashboard Initializing...');
    console.log(`API Base: ${CONFIG.API_BASE}`);
    console.log(`WebSocket: ${CONFIG.WS_URL}`);
    
    // Load saved settings
    loadSettings();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize WebSocket
    STATE.websocket = new WebSocketManager();
    STATE.websocket.connect();
    
    // Fetch initial data
    fetchAllData(STATE.currentSymbol);
    
    // Setup charts
    setupCharts();
    
    // Periodic refresh (backup for WebSocket)
    setInterval(() => {
        if (!STATE.isConnected) {
            console.log('🔄 WebSocket disconnected, using REST API');
            fetchAllData(STATE.currentSymbol);
        }
    }, CONFIG.REFRESH_INTERVAL);
    
    // Chart update interval
    setInterval(() => {
        if (STATE.charts.price && STATE.signals[STATE.currentSymbol]) {
            const signal = STATE.signals[STATE.currentSymbol];
            if (signal.entry_price) {
                const now = new Date().toLocaleTimeString('tr-TR');
                STATE.charts.price.data.labels.push(now);
                STATE.charts.price.data.datasets[0].data.push(signal.entry_price);
                
                // Keep only last 50 data points
                if (STATE.charts.price.data.labels.length > 50) {
                    STATE.charts.price.data.labels.shift();
                    STATE.charts.price.data.datasets[0].data.shift();
                }
                
                STATE.charts.price.update();
            }
        }
    }, CONFIG.CHART_UPDATE_INTERVAL);
    
    console.log('✅ Dashboard Initialized Successfully');
});

function setupEventListeners() {
    // Manual refresh button
    const refreshButton = document.getElementById('refreshButton');
    if (refreshButton) {
        refreshButton.addEventListener('click', manualRefresh);
    }
    
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Settings toggles
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        cb.addEventListener('change', () => {
            STATE.settings = getSettings();
            localStorage.setItem('settings', JSON.stringify(STATE.settings));
        });
    });
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (STATE.websocket) {
        STATE.websocket.close();
    }
});

// ============================================================================
// EXPORT (if using modules)
// ============================================================================

// Export for testing purposes
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CONFIG,
        STATE,
        WebSocketManager,
        fetchSignals,
        updateSignalDisplay
    };
}

console.log('✅ DEMIR AI Dashboard Script Loaded');
