/**
 * DEMIR AI v6.0 - Professional Trader Dashboard - Phase 4
 * Real-Time WebSocket + Advanced Analytics + Turkish UI
 * Dark Theme + 4-GROUP Signal System + Position Management
 * Production-Grade Frontend
 */

// ========== CONFIGURATION ==========
const API_BASE = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8000/ws';

let currentCoin = 'BTCUSDT';
let signals = {};
let positions = {};
let charts = {};
let websocket = null;
let updateInterval = null;

const COLORS = {
    long: '#00ff88',
    short: '#ff3366',
    neutral: '#ffaa00',
    tech: '#00d4ff',
    sentiment: '#ff00ff',
    onchain: '#00ff88',
    macro: '#ffaa00',
    buy: '#00ff88',
    sell: '#ff3366'
};

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DEMIR AI v6.0 Frontend Initializing...');
    
    setupEventListeners();
    loadInitialData();
    initializeWebSocket();
    setupCharts();
    loadTradeHistory();
    setupTelegramMonitoring();
    
    // Main update loop
    updateInterval = setInterval(updateRealTime, 5000);
    
    console.log('✅ Dashboard Ready');
});


// ========== EVENT LISTENERS ==========
function setupEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => switchTab(e.target.dataset.tab));
    });
    
    // Coin switching
    document.querySelectorAll('.coin-btn').forEach(btn => {
        btn.addEventListener('click', (e) => switchCoin(e.target.dataset.coin));
    });
    
    // Theme toggle
    document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);
    
    // Add coin
    document.getElementById('addCoinBtn')?.addEventListener('click', openAddCoinModal);
    
    // Action buttons
    document.getElementById('openLongBtn')?.addEventListener('click', () => openTradeModal('LONG'));
    document.getElementById('openShortBtn')?.addEventListener('click', () => openTradeModal('SHORT'));
    document.getElementById('closeAllBtn')?.addEventListener('click', closeAllPositions);
    
    // Settings
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        cb.addEventListener('change', () => {
            localStorage.setItem('settings', JSON.stringify(getSettings()));
        });
    });
}


// ========== DATA LOADING ==========
async function loadInitialData() {
    try {
        updateStatus('online');
        
        // Get signals for all coins
        const signalResp = await axios.get(`${API_BASE}/signals`);
        signals = signalResp.data.data || [];
        
        // Get tracked coins
        const coinsResp = await axios.get(`${API_BASE}/coins`);
        const coins = coinsResp.data.coins || ['BTCUSDT', 'ETHUSDT', 'LTCUSDT'];
        updateTrackedCoinsList(coins);
        
        // Get positions
        const posResp = await axios.get(`${API_BASE}/positions`);
        positions = posResp.data.data || [];
        
        updateSignalDisplay(currentCoin);
        updatePositionsDisplay();
        
        logger('✅ Veriler yüklendi');
    } catch (e) {
        logger(`❌ Veri yüklenirken hata: ${e.message}`, 'error');
        updateStatus('offline');
    }
}


// ========== WEBSOCKET INITIALIZATION ==========
function initializeWebSocket() {
    try {
        websocket = new WebSocket(WS_URL);
        
        websocket.onopen = () => {
            logger('✅ WebSocket bağlandı');
            updateStatus('connected');
        };
        
        websocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                if (data.type === 'signal') {
                    updateSignalDisplay(data.signal.symbol);
                    playNotificationSound();
                } else if (data.type === 'position') {
                    positions[data.position.id] = data.position;
                    updatePositionsDisplay();
                } else if (data.type === 'price') {
                    updatePriceDisplay(data.coin, data.price);
                }
            } catch (e) {
                logger(`WebSocket parse error: ${e.message}`, 'debug');
            }
        };
        
        websocket.onerror = (error) => {
            logger(`❌ WebSocket hatası: ${error}`, 'error');
            updateStatus('error');
        };
        
        websocket.onclose = () => {
            logger('⚠️ WebSocket bağlantısı kesildi');
            updateStatus('offline');
            // Reconnect in 5 seconds
            setTimeout(initializeWebSocket, 5000);
        };
    } catch (e) {
        logger(`WebSocket init error: ${e.message}`, 'error');
    }
}


// ========== REAL-TIME UPDATES ==========
async function updateRealTime() {
    try {
        // Refresh signals
        const resp = await axios.get(`${API_BASE}/signals?limit=50`);
        signals = resp.data.data || [];
        
        // Update current coin display
        updateSignalDisplay(currentCoin);
        updatePositionsDisplay();
        
    } catch (e) {
        logger(`Update error: ${e.message}`, 'debug');
    }
}


// ========== SIGNAL DISPLAY ==========
function updateSignalDisplay(coin) {
    const signal = signals.find(s => s.symbol === coin);
    
    if (!signal) {
        resetSignalDisplay();
        return;
    }
    
    try {
        // Current price
        const priceEl = document.getElementById('currentPrice');
        if (priceEl) priceEl.textContent = `$${signal.entry_price.toFixed(2)}`;
        
        // 4-GROUP Display
        updateGroupDisplay('technical', {
            direction: signal.direction || 'NEUTRAL',
            strength: signal.tech_group_score || 0,
            confidence: signal.confidence || 0,
            layers: 28
        });
        
        updateGroupDisplay('sentiment', {
            direction: signal.direction || 'NEUTRAL',
            strength: signal.sentiment_group_score || 0,
            confidence: signal.confidence || 0,
            layers: 20
        });
        
        updateGroupDisplay('onchain', {
            direction: signal.direction || 'NEUTRAL',
            strength: signal.onchain_group_score || 0,
            confidence: signal.confidence || 0,
            layers: 6
        });
        
        updateGroupDisplay('macro', {
            direction: signal.direction || 'NEUTRAL',
            strength: signal.macro_risk_group_score || 0,
            confidence: signal.confidence || 0,
            layers: 14
        });
        
        // Consensus
        updateConsensusDisplay(signal);
        
        // Risk metrics
        updateRiskDisplay(signal, coin);
        
        // Data source
        const sourceEl = document.getElementById('dataSource');
        if (sourceEl) sourceEl.textContent = `📊 Veri: ${signal.data_source || 'Unknown'}`;
        
        // AI Comment
        updateAIComment(signal, coin);
        
    } catch (e) {
        logger(`Signal display error: ${e.message}`, 'error');
    }
}


function updateGroupDisplay(group, data) {
    const directionText = {
        'LONG': '📈 LONG',
        'SHORT': '📉 SHORT',
        'NEUTRAL': '⏸️ NEUTRAL'
    }[data.direction] || '❓ ?';
    
    const directionColor = {
        'LONG': COLORS.long,
        'SHORT': COLORS.short,
        'NEUTRAL': COLORS.neutral
    }[data.direction] || COLORS.neutral;
    
    // Direction
    const dirEl = document.getElementById(`${group}Direction`);
    if (dirEl) {
        dirEl.textContent = directionText;
        dirEl.style.color = directionColor;
    }
    
    // Strength
    const strength = Math.round(data.strength * 100);
    const strengthEl = document.getElementById(`${group}Strength`);
    if (strengthEl) strengthEl.textContent = `${strength}%`;
    
    const strengthBar = document.getElementById(`${group}StrengthBar`);
    if (strengthBar) {
        strengthBar.style.width = `${strength}%`;
        strengthBar.style.backgroundColor = directionColor;
    }
    
    // Confidence
    const confidence = Math.round(data.confidence * 100);
    const confEl = document.getElementById(`${group}Confidence`);
    if (confEl) confEl.textContent = `${confidence}%`;
    
    const confBar = document.getElementById(`${group}ConfidenceBar`);
    if (confBar) {
        confBar.style.width = `${confidence}%`;
        confBar.style.backgroundColor = directionColor;
    }
    
    // Layers
    const layersEl = document.getElementById(`${group}Layers`);
    if (layersEl) layersEl.textContent = `${data.layers} Layer`;
    
    // Explanation
    updateGroupExplanation(group, data);
}


function updateGroupExplanation(group, data) {
    const strength = Math.round(data.strength * 100);
    const confidence = Math.round(data.confidence * 100);
    
    let explanation = '';
    
    if (group === 'technical') {
        if (data.direction === 'LONG' && strength > 70) {
            explanation = `RSI, MACD ve Bollinger Bands alım sinyali veriyor. Fiyat ${data.layers} teknik gösterge ile destek bulmuş.`;
        } else if (data.direction === 'SHORT' && strength > 70) {
            explanation = `Teknik göstergeler satış baskısı gösteriyor. ${data.layers} layer dirençte uyarı veriyor.`;
        } else {
            explanation = `Teknik göstergeler karışık sinyal veriyor. Konsolidasyon dönemindeyiz.`;
        }
    } 
    else if (group === 'sentiment') {
        if (strength > 60) {
            explanation = `Pazar duyarlılığı ${data.direction === 'LONG' ? 'pozitif' : 'negatif'}. Sosyal medya ${data.direction === 'LONG' ? 'alımı' : 'satışı'} destekliyor.`;
        } else {
            explanation = `Pazar duyarlılığı nötr. İnsanlar bekleme modunda.`;
        }
    }
    else if (group === 'onchain') {
        if (strength > 65) {
            explanation = `Zincir analizi: Büyük işlemler ${data.direction === 'LONG' ? 'birikim' : 'dağılım'} gösteriyor. Whale hareketleri ${data.direction === 'LONG' ? 'pozitif' : 'negatif'}.`;
        } else {
            explanation = `Zincir aktivitesi normal. Büyük işlem beklentisi yok.`;
        }
    }
    else if (group === 'macro') {
        if (strength > 70) {
            explanation = `Makro çerçeve ${data.direction === 'LONG' ? 'yükseliş' : 'düşüş'} gösteriyor. Volatilite ${confidence > 75 ? 'yüksek' : 'orta'} seviyede.`;
        } else {
            explanation = `Makro ortam belirsiz. Risk yönetimi çok önemli.`;
        }
    }
    
    const exEl = document.getElementById(`${group}Explanation`);
    if (exEl) exEl.textContent = explanation;
}


function updateConsensusDisplay(signal) {
    const score = signal.ensemble_score || 0;
    const direction = signal.direction || 'NEUTRAL';
    
    // Direction
    const dirEl = document.getElementById('consensusDirection');
    if (dirEl) {
        dirEl.textContent = direction;
        dirEl.style.color = COLORS[direction.toLowerCase()];
    }
    
    // Strength
    const strengthEl = document.getElementById('consensusStrength');
    if (strengthEl) strengthEl.textContent = `${Math.round(score * 100)}%`;
    
    const strengthBar = document.getElementById('consensusStrengthBar');
    if (strengthBar) {
        strengthBar.style.width = `${score * 100}%`;
        strengthBar.style.backgroundColor = COLORS[direction.toLowerCase()];
    }
    
    // Confidence
    const confEl = document.getElementById('consensusConfidence');
    if (confEl) confEl.textContent = `${Math.round(signal.confidence * 100)}%`;
    
    const confBar = document.getElementById('consensusConfidenceBar');
    if (confBar) {
        confBar.style.width = `${signal.confidence * 100}%`;
        confBar.style.backgroundColor = COLORS[direction.toLowerCase()];
    }
    
    // Action button
    const actionBtn = document.getElementById('actionButton');
    if (actionBtn) {
        if (score > 0.5) {
            actionBtn.disabled = false;
            actionBtn.textContent = direction === 'LONG' ? '📈 LONG AC' : '📉 SHORT AC';
            actionBtn.style.backgroundColor = COLORS[direction.toLowerCase()];
        } else {
            actionBtn.disabled = true;
            actionBtn.textContent = 'Bekleniyor...';
        }
    }
}


function updateRiskDisplay(signal, coin) {
    const riskScoreEl = document.getElementById('riskScore');
    if (riskScoreEl) riskScoreEl.textContent = `${Math.round((signal.risk_score || 0.5) * 100)}%`;
    
    const rrEl = document.getElementById('riskRewardRatio');
    if (rrEl) rrEl.textContent = `${(signal.risk_reward_ratio || 2.0).toFixed(2)}:1`;
    
    const posEl = document.getElementById('recommendedPosition');
    if (posEl) posEl.textContent = `${signal.position_size || 1.0} kontrat`;
}


function updateAIComment(signal, coin) {
    const tech = Math.round(signal.tech_group_score * 100);
    const sentiment = Math.round(signal.sentiment_group_score * 100);
    const onchain = Math.round(signal.onchain_group_score * 100);
    const macro = Math.round(signal.macro_risk_group_score * 100);
    const ensemble = Math.round(signal.ensemble_score * 100);
    
    let comment = `\n🤖 **${coin} AI Analizi**\n\n`;
    comment += `📊 Teknik: ${tech}% (${tech > 65 ? 'güçlü' : tech > 35 ? 'orta' : 'zayıf'})\n`;
    comment += `💭 Duygu: ${sentiment}% (${sentiment > 65 ? 'pozitif' : sentiment > 35 ? 'nötr' : 'negatif'})\n`;
    comment += `⛓️ Zincir: ${onchain}% (${onchain > 65 ? 'alım' : onchain > 35 ? 'dengeli' : 'satış'})\n`;
    comment += `⚠️ Makro: ${macro}% (${macro > 70 ? 'YÜKSEK RISK' : macro > 40 ? 'ORTA' : 'DÜŞÜK'})\n\n`;
    
    comment += `🎯 **Tavsiye:** `;
    if (ensemble > 75) {
        comment += `${signal.direction} sinyali YAGLI! Tüm göstergeler uyuşuyor.`;
    } else if (ensemble > 50) {
        comment += `${signal.direction} yönü favori ama tam güven yok. Pozisyon aç ama dikkatli.`;
    } else {
        comment += `Sinyal karışık. Bekleme yaparak şartlar netleşene kadar sabırlı.`;
    }
    
    const aiEl = document.getElementById('aiComment');
    if (aiEl) aiEl.textContent = comment;
}


// ========== POSITIONS DISPLAY ==========
function updatePositionsDisplay() {
    const container = document.getElementById('positionsContainer');
    if (!container) return;
    
    if (!positions || Object.keys(positions).length === 0) {
        container.innerHTML = '<div class="no-data">📭 Açık pozisyon yok</div>';
        return;
    }
    
    let html = '<div class="positions-grid">';
    
    for (const [id, pos] of Object.entries(positions)) {
        if (pos.status === 'open' || pos.status === 'partially_closed') {
            const pnl = (pos.current_price - pos.entry_price) * pos.quantity;
            const pnlPercent = (pnl / (pos.entry_price * pos.quantity)) * 100;
            const pnlColor = pnl >= 0 ? COLORS.buy : COLORS.sell;
            
            html += `
                <div class="position-card" style="border-left: 4px solid ${pnlColor}">
                    <div class="pos-header">
                        <h4>${pos.symbol}</h4>
                        <span class="pos-side ${pos.side}">${pos.side === 'long' ? '📈' : '📉'} ${pos.side.toUpperCase()}</span>
                    </div>
                    <div class="pos-details">
                        <div>Entry: $${pos.entry_price.toFixed(2)}</div>
                        <div>Current: $${pos.current_price.toFixed(2)}</div>
                        <div>Qty: ${pos.quantity.toFixed(4)}</div>
                    </div>
                    <div class="pos-levels">
                        <div>TP: $${pos.take_profit.toFixed(2)}</div>
                        <div>SL: $${pos.stop_loss.toFixed(2)}</div>
                    </div>
                    <div class="pos-pnl" style="color: ${pnlColor}">
                        <strong>P&L: $${pnl.toFixed(2)} (${pnlPercent.toFixed(2)}%)</strong>
                    </div>
                    <button onclick="closePosition('${id}')" class="btn btn-danger">Kapat</button>
                </div>
            `;
        }
    }
    
    html += '</div>';
    container.innerHTML = html;
}


// ========== CHARTS ==========
function setupCharts() {
    const groupCtx = document.getElementById('groupChart');
    if (!groupCtx) return;
    
    charts.groupChart = new Chart(groupCtx, {
        type: 'bar',
        data: {
            labels: ['Teknik', 'Duygu', 'Zincir', 'Makro'],
            datasets: [{
                label: 'Sinyal Gücü (%)',
                data: [65, 52, 71, 60],
                backgroundColor: [COLORS.tech, COLORS.sentiment, COLORS.onchain, COLORS.macro],
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { color: '#a0a0a0' },
                    grid: { color: '#1a1f3a' }
                }
            },
            plugins: { legend: { display: false } }
        }
    });
}


// ========== UTILITIES ==========
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    
    document.getElementById(tabName)?.classList.add('active');
    event.target.classList.add('active');
}


function switchCoin(coin) {
    currentCoin = coin;
    document.querySelectorAll('.coin-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    
    updateSignalDisplay(coin);
}


function toggleTheme() {
    document.body.classList.toggle('light-theme');
    localStorage.setItem('theme', document.body.classList.contains('light-theme') ? 'light' : 'dark');
}


function updateStatus(status) {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    
    if (status === 'online' || status === 'connected') {
        dot.className = 'status-dot online';
        text.textContent = '🟢 Bağlı';
    } else if (status === 'offline') {
        dot.className = 'status-dot offline';
        text.textContent = '🔴 Çevrimdışı';
    } else {
        dot.className = 'status-dot error';
        text.textContent = '🟠 Hata';
    }
}


function updateTrackedCoinsList(coins) {
    const container = document.getElementById('trackedCoins');
    if (!container) return;
    
    container.innerHTML = coins.map(coin => 
        `<button class="coin-btn ${coin === currentCoin ? 'active' : ''}" data-coin="${coin}">${coin}</button>`
    ).join('');
    
    // Re-attach listeners
    document.querySelectorAll('.coin-btn').forEach(btn => {
        btn.addEventListener('click', (e) => switchCoin(e.target.dataset.coin));
    });
}


function resetSignalDisplay() {
    document.getElementById('currentPrice').textContent = '-';
    document.querySelectorAll('.group-direction').forEach(el => el.textContent = '❓');
    document.getElementById('aiComment').textContent = 'Sinyal bekleniyor...';
}


function openAddCoinModal() {
    const coin = prompt('Coin sembolü girin (örn: BNBUSDT):');
    if (coin) {
        addCoin(coin.toUpperCase());
    }
}


async function addCoin(symbol) {
    try {
        const resp = await axios.post(`${API_BASE}/coins/add`, { symbol });
        logger(`✅ ${symbol} eklendi`);
        loadInitialData();
    } catch (e) {
        logger(`❌ Hata: ${e.response?.data?.message || e.message}`, 'error');
    }
}


function openTradeModal(direction) {
    const modal = document.getElementById('tradeModal');
    if (!modal) return;
    
    document.getElementById('tradeDirection').value = direction;
    document.getElementById('tradeSymbol').value = currentCoin;
    modal.style.display = 'block';
}


async function executeTrade(direction) {
    try {
        const symbol = document.getElementById('tradeSymbol')?.value || currentCoin;
        const amount = parseFloat(document.getElementById('tradeAmount')?.value || 0);
        
        if (!amount || amount <= 0) {
            logger('❌ Geçerli miktar girin', 'error');
            return;
        }
        
        const resp = await axios.post(`${API_BASE}/positions/open`, {
            symbol,
            side: direction.toLowerCase(),
            amount,
            leverage: parseInt(document.getElementById('tradeLeverage')?.value || 1)
        });
        
        logger(`✅ Pozisyon açıldı: ${direction} ${amount} USDT`);
        loadInitialData();
        
        document.getElementById('tradeModal').style.display = 'none';
    } catch (e) {
        logger(`❌ Hata: ${e.response?.data?.message || e.message}`, 'error');
    }
}


async function closePosition(positionId) {
    try {
        await axios.post(`${API_BASE}/positions/close`, { position_id: positionId });
        logger('✅ Pozisyon kapatıldı');
        loadInitialData();
    } catch (e) {
        logger(`❌ Hata: ${e.message}`, 'error');
    }
}


async function closeAllPositions() {
    if (!confirm('Tüm pozisyonları kapatmak istediğinizden emin misiniz?')) return;
    
    try {
        await axios.post(`${API_BASE}/positions/close-all`);
        logger('✅ Tüm pozisyonlar kapatıldı');
        loadInitialData();
    } catch (e) {
        logger(`❌ Hata: ${e.message}`, 'error');
    }
}


function loadTradeHistory() {
    // Placeholder
}


function setupTelegramMonitoring() {
    // Placeholder
}


function logger(msg, level = 'info') {
    const timestamp = new Date().toLocaleTimeString('tr-TR');
    console.log(`[${timestamp}] ${msg}`);
    
    const logContainer = document.getElementById('logContainer');
    if (logContainer) {
        const logEntry = document.createElement('div');
        logEntry.className = `log-${level}`;
        logEntry.textContent = `${timestamp} ${msg}`;
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }
}


function playNotificationSound() {
    // Play notification - uses Web Audio API
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gain = audioContext.createGain();
    
    oscillator.connect(gain);
    gain.connect(audioContext.destination);
    
    oscillator.frequency.value = 1000;
    oscillator.type = 'sine';
    
    gain.gain.setValueAtTime(0.3, audioContext.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
}


function getSettings() {
    return {
        autoTrade: document.getElementById('autoTradeCheck')?.checked || false,
        notifications: document.getElementById('notificationsCheck')?.checked || true,
        darkTheme: !document.body.classList.contains('light-theme')
    };
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (websocket) websocket.close();
    if (updateInterval) clearInterval(updateInterval);
});
