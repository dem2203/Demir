// DEMIR AI v6.0 - app.js (Full JavaScript)
// 4-GROUP SYSTEM + ADD COIN FEATURE

class DemirAIDashboard {
    constructor() {
        this.currentSymbol = 'BTCUSDT';
        this.trackedCoins = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT'];
        this.apiBaseUrl = '/api';
        this.refreshInterval = 5000; // 5 seconds
        this.init();
    }

    async init() {
        console.log('🤖 DEMIR AI v6.0 Dashboard initializing...');
        
        await this.loadTrackedCoins();
        this.renderCoinButtons();
        this.attachEventListeners();
        
        // Initial data load
        await this.refreshDashboard();
        
        // Auto-refresh every 5 seconds
        setInterval(() => this.refreshDashboard(), this.refreshInterval);
        
        console.log('✅ Dashboard initialized');
    }

    async loadTrackedCoins() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/coins`);
            const data = await response.json();
            
            if (data.status === 'success' && data.coins.length > 0) {
                this.trackedCoins = data.coins;
                console.log('📊 Tracked coins:', this.trackedCoins);
            }
        } catch (error) {
            console.error('❌ Load coins error:', error);
        }
    }

    renderCoinButtons() {
        const container = document.getElementById('coin-buttons');
        container.innerHTML = '';
        
        this.trackedCoins.forEach(symbol => {
            const btn = document.createElement('button');
            btn.className = `coin-btn ${symbol === this.currentSymbol ? 'active' : ''}`;
            btn.textContent = symbol.replace('USDT', '');
            btn.onclick = () => this.selectCoin(symbol);
            container.appendChild(btn);
        });
    }

    selectCoin(symbol) {
        this.currentSymbol = symbol;
        document.getElementById('selected-symbol').textContent = symbol;
        
        // Update active button
        document.querySelectorAll('.coin-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        
        // Refresh dashboard
        this.refreshDashboard();
    }

    attachEventListeners() {
        // Add coin button
        document.getElementById('add-coin-btn').addEventListener('click', () => {
            this.addNewCoin();
        });

        // Enter key in input
        document.getElementById('new-coin-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.addNewCoin();
            }
        });
    }

    async addNewCoin() {
        const input = document.getElementById('new-coin-input');
        let symbol = input.value.trim().toUpperCase();
        
        if (!symbol) {
            alert('❌ Please enter a symbol');
            return;
        }

        // Add USDT suffix if not present
        if (!symbol.endsWith('USDT')) {
            symbol += 'USDT';
        }

        // Check if already tracked
        if (this.trackedCoins.includes(symbol)) {
            alert(`✅ ${symbol} already tracked!`);
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/coins/add`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symbol })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                console.log(`✅ ${symbol} added!`);
                input.value = '';
                
                await this.loadTrackedCoins();
                this.renderCoinButtons();
                
                // Select newly added coin
                this.selectCoin(symbol);
            } else {
                alert(`❌ Error: ${data.message}`);
            }
        } catch (error) {
            console.error('❌ Add coin error:', error);
            alert('❌ Failed to add coin');
        }
    }

    async refreshDashboard() {
        try {
            // Fetch signals
            const signalsResponse = await fetch(`${this.apiBaseUrl}/signals`);
            const signalsData = await signalsResponse.json();
            
            if (signalsData.status === 'success') {
                this.updateSignalsDisplay(signalsData.data);
            }

            // Fetch statistics
            const statsResponse = await fetch(`${this.apiBaseUrl}/statistics`);
            const statsData = await statsResponse.json();
            
            if (statsData.status === 'success') {
                this.updateStatistics(statsData.data);
            }

            // Update connection status
            this.updateConnectionStatus(true);
            
        } catch (error) {
            console.error('❌ Refresh error:', error);
            this.updateConnectionStatus(false);
        }
    }

    updateSignalsDisplay(signals) {
        if (!signals || signals.length === 0) {
            document.getElementById('signals-list').innerHTML = '<p class="loading">No signals yet</p>';
            return;
        }

        const html = signals.slice(0, 10).map(signal => {
            const date = new Date(signal.entry_time).toLocaleString();
            const direction = signal.direction === 'LONG' ? '🟢 LONG' : '🔴 SHORT';
            const tech = (signal.tech_group_score * 100).toFixed(0);
            const sentiment = (signal.sentiment_group_score * 100).toFixed(0);
            const onchain = (signal.onchain_group_score * 100).toFixed(0);
            const macro = (signal.macro_risk_group_score * 100).toFixed(0);
            const ensemble = (signal.ensemble_score * 100).toFixed(0);

            return `
                <div class="signal-row ${signal.direction === 'LONG' ? 'long' : 'short'}">
                    <div class="signal-info">
                        <span class="symbol">${signal.symbol}</span>
                        <span class="direction">${direction}</span>
                        <span class="time">${date}</span>
                    </div>
                    <div class="signal-scores">
                        <span class="badge" title="Technical">T:${tech}%</span>
                        <span class="badge" title="Sentiment">S:${sentiment}%</span>
                        <span class="badge" title="On-Chain">O:${onchain}%</span>
                        <span class="badge" title="Macro+Risk">M:${macro}%</span>
                    </div>
                    <div class="signal-ensemble">
                        <span class="ensemble">E:${ensemble}%</span>
                    </div>
                </div>
            `;
        }).join('');

        document.getElementById('signals-list').innerHTML = html;
    }

    updateStatistics(stats) {
        if (!stats) return;

        document.getElementById('stat-total').textContent = stats.total_trades || 0;
        
        if (stats.total_trades && stats.winning_trades) {
            const winRate = ((stats.winning_trades / stats.total_trades) * 100).toFixed(1);
            document.getElementById('stat-winrate').textContent = `${winRate}%`;
        }
        
        if (stats.avg_confidence) {
            document.getElementById('stat-confidence').textContent = 
                `${(stats.avg_confidence * 100).toFixed(0)}%`;
        }
        
        if (stats.total_pnl !== undefined) {
            document.getElementById('stat-pnl').textContent = 
                `${stats.total_pnl > 0 ? '+' : ''}${stats.total_pnl.toFixed(2)}%`;
        }

        // Update 4-GROUP display
        if (stats.avg_tech_group) {
            const techPercent = (stats.avg_tech_group * 100).toFixed(0);
            document.getElementById('tech-score').style.width = `${techPercent}%`;
            document.getElementById('tech-percent').textContent = `${techPercent}%`;
        }

        if (stats.avg_sentiment_group) {
            const sentPercent = (stats.avg_sentiment_group * 100).toFixed(0);
            document.getElementById('sentiment-score').style.width = `${sentPercent}%`;
            document.getElementById('sentiment-percent').textContent = `${sentPercent}%`;
        }

        if (stats.avg_onchain_group) {
            const onchainPercent = (stats.avg_onchain_group * 100).toFixed(0);
            document.getElementById('onchain-score').style.width = `${onchainPercent}%`;
            document.getElementById('onchain-percent').textContent = `${onchainPercent}%`;
        }

        if (stats.avg_macro_risk_group) {
            const macroPercent = (stats.avg_macro_risk_group * 100).toFixed(0);
            document.getElementById('macro-score').style.width = `${macroPercent}%`;
            document.getElementById('macro-percent').textContent = `${macroPercent}%`;
        }

        if (stats.avg_ensemble_score) {
            const ensemblePercent = (stats.avg_ensemble_score * 100).toFixed(0);
            document.getElementById('ensemble-value').textContent = `${ensemblePercent}%`;
        }
    }

    updateConnectionStatus(connected) {
        const status = document.getElementById('connection-status');
        if (connected) {
            status.textContent = '🟢 Connected';
            status.style.color = '#10b981';
        } else {
            status.textContent = '🔴 Disconnected';
            status.style.color = '#ef4444';
        }

        const updateTime = document.getElementById('update-time');
        const now = new Date().toLocaleTimeString();
        updateTime.textContent = `Last: ${now}`;
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DemirAIDashboard();
});
