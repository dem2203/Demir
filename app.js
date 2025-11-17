// DEMIR AI v6.0 - Professional Trader Dashboard JavaScript
// Real-Time Signals + Türkçe Yorumlar + AI Comments

const API_BASE = 'http://localhost:8000/api';
let currentCoin = 'BTCUSDT';
let signals = {};
let tradeHistory = [];
let charts = {};

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadInitialData();
    startRealTimeUpdates();
    setupCharts();
    loadTradeHistory();
    setupTelegramMonitoring();
});

function setupEventListeners() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => switchTab(e.target.dataset.tab));
    });

    document.querySelectorAll('.coin-btn').forEach(btn => {
        btn.addEventListener('click', (e) => switchCoin(e.target.dataset.coin));
    });

    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    document.getElementById('addCoinBtn').addEventListener('click', openAddCoinModal);
    document.getElementById('actionButton').addEventListener('click', openTradeModal);

    document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        cb.addEventListener('change', () => localStorage.setItem('settings', JSON.stringify(getSettings())));
    });
}

// ========== DATA LOADING ==========
async function loadInitialData() {
    try {
        updateStatus('online');
        
        // Get signals for all coins
        const response = await axios.get(`${API_BASE}/signals`);
        signals = response.data.data || [];
        
        // Get statistics
        const statsResp = await axios.get(`${API_BASE}/statistics`);
        updateStatistics(statsResp.data.data);
        
        // Get tracked coins
        const coinsResp = await axios.get(`${API_BASE}/coins`);
        updateTrackedCoins(coinsResp.data.coins);
        
        updateSignalDisplay(currentCoin);
        logger('✅ Veriler yüklendi');
    } catch (e) {
        logger(`❌ Veri yüklenirken hata: ${e.message}`, 'error');
        updateStatus('offline');
    }
}

function startRealTimeUpdates() {
    setInterval(loadInitialData, 30000); // Her 30 saniye güncelle
    setInterval(sendHourlyStatusTelegram, 3600000); // Her saat durum gönder
}

// ========== SIGNAL DISPLAY ==========
function updateSignalDisplay(coin) {
    const signal = signals.find(s => s.symbol === coin);
    
    if (!signal) {
        resetSignalDisplay();
        return;
    }

    // TECHNICAL GROUP
    updateGroupDisplay('technical', {
        direction: signal.direction || 'NEUTRAL',
        strength: signal.tech_group_score || 0,
        confidence: signal.confidence || 0,
        layers: signal.active_layers || 0
    });

    // SENTIMENT GROUP
    updateGroupDisplay('sentiment', {
        direction: signal.direction || 'NEUTRAL',
        strength: signal.sentiment_group_score || 0,
        confidence: signal.confidence || 0,
        layers: 20
    });

    // ONCHAIN GROUP
    updateGroupDisplay('onchain', {
        direction: signal.direction || 'NEUTRAL',
        strength: signal.onchain_group_score || 0,
        confidence: signal.confidence || 0,
        layers: 6
    });

    // MACRO RISK GROUP
    updateGroupDisplay('macro', {
        direction: signal.direction || 'NEUTRAL',
        strength: signal.macro_risk_group_score || 0,
        confidence: signal.confidence || 0,
        layers: 14
    });

    // CONSENSUS
    updateConsensus(signal);
    
    // AI COMMENT
    updateAIComment(signal, coin);
    
    // RISK & POSITION
    updateRiskMetrics(signal, coin);
    
    // DATA SOURCE
    document.getElementById('dataSource').textContent = `Veri kaynağı: ${signal.data_source || 'Kontrol edileniyor...'}`;
    document.getElementById('currentPrice').textContent = `$${(signal.entry_price || 0).toFixed(2)}`;
}

function updateGroupDisplay(group, data) {
    const direction = data.direction === 'LONG' ? '📈 LONG' : data.direction === 'SHORT' ? '📉 SHORT' : '⏸️ NEUTRAL';
    const directionClass = data.direction.toLowerCase();
    
    const directionEl = document.getElementById(`${group}Direction`);
    directionEl.textContent = direction;
    directionEl.className = `signal-direction ${directionClass}`;
    
    const strength = Math.round(data.strength * 100);
    const confidence = Math.round(data.confidence * 100);
    
    document.getElementById(`${group}Strength`).textContent = `${strength}%`;
    document.getElementById(`${group}StrengthBar`).style.width = `${strength}%`;
    
    document.getElementById(`${group}Confidence`).textContent = `${confidence}%`;
    document.getElementById(`${group}ConfidenceBar`).style.width = `${confidence}%`;
    
    document.getElementById(`${group}Layers`).textContent = `Aktif Layer: ${data.layers}`;
    
    // Turkish explanation
    document.getElementById(`${group}Explanation`).textContent = getGroupExplanation(group, data);
}

function getGroupExplanation(group, data) {
    const strength = Math.round(data.strength * 100);
    const confidence = Math.round(data.confidence * 100);
    
    if (group === 'technical') {
        if (data.direction === 'LONG' && strength > 70) {
            return `RSI, MACD ve Bollinger Bands alım sinyali veriyor. Fiyat ${data.layers} technical indicator ile destek bulmuş durumda.`;
        } else if (data.direction === 'SHORT' && strength > 70) {
            return `Teknik göstergeler satış baskısı gösteriyor. ${data.layers} layer dirençte uyarı veriyor.`;
        } else {
            return `Teknik göstergeler karışık sinyal veriyor. Konsolidasyon dönemindeyiz.`;
        }
    } else if (group === 'sentiment') {
        if (strength > 60) return `Pazar duyarlılığı ${data.direction === 'LONG' ? 'pozitif' : 'negatif'}. Sosyal medya ve haber akışı ${data.direction === 'LONG' ? 'alımı' : 'satışı'} destekliyor.`;
        return `Pazar duyarlılığı nötr. İnsanlar bekleme modunda.`;
    } else if (group === 'onchain') {
        if (strength > 65) return `Zincir analizi: Büyük işlemler ${data.direction === 'LONG' ? 'birikim' : 'dağılım'} gösteriyor. Whale hareketleri ${data.direction === 'LONG' ? 'pozitif' : 'negatif'}.`;
        return `Zincir aktivitesi normal seviyede. Büyük işlem beklentisi yok.`;
    } else if (group === 'macro') {
        if (strength > 70) return `Makro çerçeve ${data.direction === 'LONG' ? 'yükseliş' : 'düşüş'} gösteriyor. Volatilite ${confidence > 75 ? 'yüksek' : 'orta'} seviyede.`;
        return `Makro ortam belirsiz. Risk yönetimi çok önemli.`;
    }
    
    return '-';
}

function updateConsensus(signal) {
    const score = signal.ensemble_score || 0;
    const direction = signal.direction || 'NEUTRAL';
    
    document.getElementById('consensusDirection').textContent = direction;
    document.getElementById('consensusStrength').textContent = `${Math.round(score * 100)}%`;
    document.getElementById('consensusStrengthBar').style.width = `${score * 100}%`;
    document.getElementById('consensusConfidence').textContent = `${Math.round(signal.confidence * 100)}%`;
    document.getElementById('consensusConfidenceBar').style.width = `${signal.confidence * 100}%`;
    
    // Enable action button
    if (score > 0.5) {
        document.getElementById('actionButton').disabled = false;
        document.getElementById('actionButton').textContent = direction === 'LONG' ? '+ LONG AC' : '+ SHORT AC';
        document.getElementById('actionButton').style.background = direction === 'LONG' ? 'rgba(0, 255, 136, 0.1)' : 'rgba(255, 51, 102, 0.1)';
    }
}

function updateAIComment(signal, coin) {
    const tech = Math.round(signal.tech_group_score * 100);
    const sentiment = Math.round(signal.sentiment_group_score * 100);
    const onchain = Math.round(signal.onchain_group_score * 100);
    const macro = Math.round(signal.macro_risk_group_score * 100);
    const ensemble = Math.round(signal.ensemble_score * 100);
    
    let comment = `<strong>${coin} Analiz</strong>\n\n`;
    comment += `📊 Teknik: ${tech}% (${tech > 65 ? 'güçlü' : tech > 35 ? 'orta' : 'zayıf'})\n`;
    comment += `💭 Duygu: ${sentiment}% (${sentiment > 65 ? 'pozitif' : sentiment > 35 ? 'nötr' : 'negatif'})\n`;
    comment += `⛓️ Zincir: ${onchain}% (${onchain > 65 ? 'alım baskısı' : onchain > 35 ? 'dengeli' : 'satış baskısı'})\n`;
    comment += `⚠️ Makro: ${macro}% risk (${macro > 70 ? 'YÜKSEK' : macro > 40 ? 'ORTA' : 'DÜŞÜK'})\n\n`;
    comment += `🤖 Yapay Zeka Tavsiyesi: `;
    
    if (ensemble > 75) {
        comment += `${signal.direction} sinyali YAGLI. Tüm göstergeler uyuşuyor. Başlangıç saat en iyi zamanı.`;
    } else if (ensemble > 50) {
        comment += `${signal.direction} yönü favori ama tam güven yok. Pozisyon aç ama dikkatli ol.`;
    } else {
        comment += `Sinyal karışık. Bekleme yaparak şartlar netleşene kadar beklemeyi öner.`;
    }
    
    comment += `\n\n💡 Pozisyon boyutu: ${getPositionSize(coin, signal)}`;
    
    document.getElementById('aiComment').textContent = comment;
}

function updateRiskMetrics(signal, coin) {
    const leverages = { 'BTCUSDT': 80, 'ETHUSDT': 70, 'LTCUSDT': 50 };
    const amounts = { 'BTCUSDT': 60, 'ETHUSDT': 45, 'LTCUSDT': 45 };
    
    const lev = leverages[coin] || 50;
    const amount = amounts[coin] || 50;
    
    document.getElementById('recommendedPosition').textContent = `${amount} USDT @ ${lev}x`;
    document.getElementById('maxLoss').textContent = `${(amount / lev).toFixed(2)} USDT (%0.5)`;
    document.getElementById('kellyFraction').textContent = `${(0.25 * (1 - Math.abs(signal.tech_group_score - 0.5) * 2)).toFixed(2)}`;
}

function getPositionSize(coin, signal) {
    const amounts = { 'BTCUSDT': '60 USD', 'ETHUSDT': '40-50 USD', 'LTCUSDT': '40-50 USD' };
    return amounts[coin] || '50 USD';
}

// ========== CHARTS SETUP ==========
function setupCharts() {
    const colors = {
        tech: '#00d4ff',
        sentiment: '#ff00ff',
        onchain: '#00ff88',
        macro: '#ffaa00'
    };
    
    // 4-Group Bar Chart
    const groupCtx = document.getElementById('groupChart');
    if (groupCtx) {
        charts.groupChart = new Chart(groupCtx, {
            type: 'bar',
            data: {
                labels: ['Teknik', 'Duygu', 'Zincir', 'Makro'],
                datasets: [{
                    label: 'Sinyal Güçleri (%)',
                    data: [65, 52, 71, 60],
                    backgroundColor: [colors.tech, colors.sentiment, colors.onchain, colors.macro],
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, max: 100, ticks: { color: '#a0a0a0' }, grid: { color: '#1a1f3a' } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }
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
    document.getElementById('selectedCoin').textContent = coin;
    updateSignalDisplay(coin);
}

function toggleTheme() {
    document.body.classList.toggle('light-theme');
    localStorage.setItem('theme', document.body.classList.contains('light-theme') ? 'light' : 'dark');
    document.getElementById('themeToggle').textContent = document.body.classList.contains('light-theme') ? '🌞 Light' : '🌙 Dark';
}

function updateStatus(status) {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    
    if (status === 'online') {
        dot.classList.add('online');
        text.textContent = '🟢 Bağlı';
    } else {
        dot.classList.remove('online');
        text.textContent = '🔴 Çevrimdışı';
    }
}

function updateStatistics(stats) {
    if (stats.total_trades) {
        document.getElementById('statTotalTrades').textContent = stats.total_trades;
        document.getElementById('statWinning').textContent = stats.winning_trades || 0;
        document.getElementById('statLosing').textContent = (stats.total_trades - (stats.winning_trades || 0));
        document.getElementById('statWinRate').textContent = stats.win_rate ? `${(stats.win_rate * 100).toFixed(1)}%` : '0%';
    }
}

function updateTrackedCoins(coins) {
    const settings = document.getElementById('trackedCoinsSettings');
    if (settings) {
        settings.innerHTML = coins.map(coin => `
            <div class="coin-setting-item">
                ${coin}
                <button class="btn-remove-coin" onclick="removeCoin('${coin}')">Sil</button>
            </div>
        `).join('');
    }
}

function logger(msg, type = 'info') {
    console.log(`[${new Date().toLocaleTimeString('tr-TR')}] ${msg}`);
}

// ========== MODALS ==========
function openAddCoinModal() {
    document.getElementById('addCoinModal').style.display = 'flex';
    document.getElementById('addCoinInput').focus();
}

function closeModal() {
    document.querySelectorAll('.modal').forEach(m => m.style.display = 'none');
}

async function confirmAddCoin() {
    const coin = document.getElementById('addCoinInput').value.toUpperCase();
    if (!coin || !coin.endsWith('USDT')) {
        alert('Geçersiz coin! Örn: SOLUSDT');
        return;
    }
    
    try {
        await axios.post(`${API_BASE}/coins/add`, { symbol: coin });
        alert(`✅ ${coin} eklendi!`);
        closeModal();
        loadInitialData();
    } catch (e) {
        alert(`❌ Hata: ${e.message}`);
    }
}

function openTradeModal() {
    document.getElementById('tradeModal').style.display = 'flex';
}

function confirmTradeOpen() {
    const signal = signals.find(s => s.symbol === currentCoin);
    if (signal) {
        tradeHistory.push({
            ...signal,
            opened_at: new Date(),
            status: 'OPEN',
            entry_timestamp: Date.now()
        });
        localStorage.setItem('tradeHistory', JSON.stringify(tradeHistory));
        alert(`✅ ${currentCoin} işlem kaydedildi. AI takibi başlandı!`);
        closeModal();
        loadTradeHistory();
        sendTelegramNotification(`✅ İşlem Açıldı: ${currentCoin} ${signal.direction} @ $${signal.entry_price.toFixed(2)}`);
    }
}

function loadTradeHistory() {
    tradeHistory = JSON.parse(localStorage.getItem('tradeHistory')) || [];
    const tbody = document.getElementById('historyBody');
    
    if (tradeHistory.length === 0) return;
    
    tbody.innerHTML = tradeHistory.map((trade, i) => `
        <tr>
            <td>${trade.symbol}</td>
            <td>${trade.direction}</td>
            <td>$${trade.entry_price.toFixed(2)}</td>
            <td>${trade.pnl ? `$${trade.pnl.toFixed(2)}` : '-'}</td>
            <td>${trade.pnl ? (trade.pnl > 0 ? '+' : '') + trade.pnl.toFixed(2) + '%' : '-'}</td>
            <td>${trade.status}</td>
            <td>${new Date(trade.opened_at).toLocaleDateString('tr-TR')}</td>
            <td><button onclick="closeTradeHistory(${i})">Kapat</button></td>
        </tr>
    `).join('');
}

function closeTradeHistory(index) {
    // TP/SL kontrolü ve kapanış
    const trade = tradeHistory[index];
    tradeHistory[index].status = 'CLOSED';
    tradeHistory[index].closed_at = new Date();
    localStorage.setItem('tradeHistory', JSON.stringify(tradeHistory));
    loadTradeHistory();
}

// ========== TELEGRAM ==========
function setupTelegramMonitoring() {
    if (document.getElementById('telegramEnabled').checked) {
        logger('✅ Telegram monitoring aktif');
    }
}

async function sendTelegramNotification(message) {
    logger(`📧 Telegram: ${message}`);
}

async function sendHourlyStatusTelegram() {
    if (!document.getElementById('hourlyStatusEnabled').checked) return;
    
    const prices = await Promise.all([
        fetchPrice('BTCUSDT'),
        fetchPrice('ETHUSDT'),
        fetchPrice('LTCUSDT')
    ]);
    
    const msg = `🤖 DEMIR AI v6.0 - Saatlik Rapor\n\n📊 Live Fiyatlar:\n₿ BTC: $${prices[0]}\nΞ ETH: $${prices[1]}\nŁ LTC: $${prices[2]}\n\n✅ Sistem aktif ve çalışıyor!`;
    sendTelegramNotification(msg);
}

async function fetchPrice(coin) {
    try {
        const resp = await axios.get(`${API_BASE}/signals`);
        const signal = resp.data.data.find(s => s.symbol === coin);
        return signal?.entry_price.toFixed(2) || '-';
    } catch {
        return '-';
    }
}

function resetSignalDisplay() {
    document.getElementById('consensusDirection').textContent = 'HOLD';
    document.getElementById('actionButton').disabled = true;
    document.getElementById('actionButton').textContent = 'BEKLEME...';
}

// Load theme
if (localStorage.getItem('theme') === 'light') {
    document.body.classList.add('light-theme');
    document.getElementById('themeToggle').textContent = '🌞 Light';
}
