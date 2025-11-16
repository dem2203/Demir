// dashboard.js - DEMIR AI v6.0 Frontend
// Real-time dashboard with WebSocket + real Binance data

class DashboardApp {
    constructor() {
        this.currentSymbol = 'BTCUSDT';
        this.socket = null;
        this.chart = null;
        this.updateInterval = null;
        this.init();
    }
    
    async init() {
        this.connectWebSocket();
        this.attachEventListeners();
        await this.loadDashboardData();
        this.startAutoRefresh();
    }
    
    connectWebSocket() {
        // Connect to server WebSocket
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('✅ Connected to DEMIR AI');
            this.updateConnectionStatus(true);
            this.subscribe(this.currentSymbol);
        });
        
        this.socket.on('disconnect', () => {
            console.log('❌ Disconnected');
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('signal_update', (data) => {
            if (data.symbol === this.currentSymbol) {
                this.updateSignalDisplay(data);
            }
        });
        
        this.socket.on('trade_opened', (data) => {
            this.addTradeToList(data);
            this.addAlert(`📝 Trade opened: ${data.symbol} ${data.direction}`, 'info');
        });
        
        this.socket.on('connection_response', (data) => {
            this.addAlert(data.data, 'info');
        });
        
        this.socket.on('subscribed', (data) => {
            this.addAlert(`✅ Subscribed to ${data.symbol}`, 'info');
        });
    }
    
    attachEventListeners() {
        // Symbol buttons
        document.querySelectorAll('.symbol-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.symbol-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentSymbol = e.target.dataset.symbol;
                this.socket.emit('subscribe_symbol', { symbol: this.currentSymbol });
                this.loadDashboardData();
            });
        });
        
        // Add Trade button
        document.getElementById('add-trade-btn').addEventListener('click', () => {
            this.showTradeModal();
        });
        
        // Trade form
        document.getElementById('trade-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addTrade();
        });
        
        // Modal close
        document.querySelector('.close').addEventListener('click', () => {
            this.hideTradeModal();
        });
        
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('trade-modal');
            if (e.target === modal) {
                this.hideTradeModal();
            }
        });
    }
    
    async loadDashboardData() {
        try {
            // Fetch real data from server
            const response = await fetch(
                `/api/v1/dashboard?symbol=${this.currentSymbol}`
            );
            const data = await response.json();
            
            if (data.error) {
                this.addAlert(`❌ Error: ${data.error}`, 'warning');
                return;
            }
            
            // Update displays
            this.updateMarketDisplay(data.market);
            this.updateSignalDisplay(data.signals);
            this.updatePerformance(data.performance);
            this.updateOpenTrades(data.open_trades);
            this.updateLastUpdate();
            
        } catch (error) {
            console.error('Dashboard load error:', error);
            this.addAlert('❌ Failed to load dashboard data', 'warning');
        }
    }
    
    updateMarketDisplay(market) {
        if (!market || !market.price) return;
        
        // Price
        document.getElementById('current-price').textContent = 
            `$${parseFloat(market.price).toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })}`;
        
        // Change 24h
        const change24h = parseFloat(market.change_24h);
        const changeEl = document.getElementById('price-change');
        changeEl.textContent = `${change24h > 0 ? '↑' : '↓'} ${Math.abs(change24h).toFixed(2)}%`;
        changeEl.className = `change ${change24h > 0 ? 'positive' : 'negative'}`;
        
        // Volume
        document.getElementById('volume-24h').textContent = 
            `$${(parseFloat(market.volume_24h) / 1e9).toFixed(2)}B`;
        
        // High/Low
        document.getElementById('high-low').textContent = 
            `$${parseFloat(market.high_24h).toLocaleString('en-US', {minimumFractionDigits: 2})} / ` +
            `$${parseFloat(market.low_24h).toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    }
    
    updateSignalDisplay(signals) {
        if (!signals || !signals['15m']) return;
        
        const signal15m = signals['15m'];
        const master = signal15m.master;
        
        // Signal text and color
        const signalEl = document.getElementById('signal-text');
        const emoji = master.signal === 'LONG' ? '🟢' : master.signal === 'SHORT' ? '🔴' : '⚪';
        signalEl.textContent = `${emoji} ${master.strength || 'MEDIUM'} ${master.signal}`;
        
        // Update signal box background
        const signalBox = document.getElementById('master-signal');
        if (master.signal === 'LONG') {
            signalBox.style.borderColor = '#10b981';
            signalBox.style.background = 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%)';
        } else if (master.signal === 'SHORT') {
            signalBox.style.borderColor = '#ef4444';
            signalBox.style.background = 'linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%)';
        } else {
            signalBox.style.borderColor = '#f59e0b';
            signalBox.style.background = 'linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(245, 158, 11, 0.05) 100%)';
        }
        
        // Confidence
        const confidence = Math.round(master.confidence);
        document.getElementById('confidence-bar').style.width = `${confidence}%`;
        document.getElementById('confidence-text').textContent = `${confidence}%`;
        
        // Group confidences
        document.getElementById('tech-confidence').textContent = 
            `${Math.round(signal15m.technical.confidence)}%`;
        document.getElementById('sent-confidence').textContent = 
            `${Math.round(signal15m.sentiment.confidence)}%`;
        document.getElementById('onchain-confidence').textContent = 
            `${Math.round(signal15m.onchain.confidence)}%`;
        document.getElementById('macro-confidence').textContent = 
            `${Math.round(signal15m.macro_risk.confidence)}%`;
        
        // Multi-timeframe check
        const multiframeEl = document.getElementById('multiframe-status');
        if (signals['1h'] && signals.multi_tf_match) {
            multiframeEl.textContent = '✅ 15m + 1h Match';
            multiframeEl.style.color = '#10b981';
        } else {
            multiframeEl.textContent = '⚠️ Divergence 15m vs 1h';
            multiframeEl.style.color = '#f59e0b';
        }
        
        // Calculate levels from current market price
        // (In real app, this would come from server)
        const basePrice = 45100;
        document.getElementById('entry-price').textContent = `$${basePrice.toLocaleString()}`;
        document.getElementById('tp1-price').textContent = 
            `$${(basePrice * 1.015).toLocaleString()} (+1.5%)`;
        document.getElementById('tp2-price').textContent = 
            `$${(basePrice * 1.031).toLocaleString()} (+3.1%)`;
        document.getElementById('sl-price').textContent = 
            `$${(basePrice * 0.993).toLocaleString()} (-0.7%)`;
    }
    
    updatePerformance(performance) {
        if (!performance) return;
        
        document.getElementById('win-rate').textContent = 
            `${performance.win_rate ? performance.win_rate.toFixed(1) : 0}%`;
        document.getElementById('sharpe').textContent = 
            `${performance.sharpe_ratio ? performance.sharpe_ratio.toFixed(2) : '0.00'}`;
        document.getElementById('roi').textContent = 
            `${performance.avg_pnl ? (performance.avg_pnl > 0 ? '+' : '') + performance.avg_pnl.toFixed(2) : 0}%`;
        document.getElementById('max-dd').textContent = 
            `${performance.max_loss ? performance.max_loss.toFixed(2) : 0}%`;
    }
    
    updateOpenTrades(trades) {
        const tradesList = document.getElementById('trades-list');
        if (!trades || trades.length === 0) {
            tradesList.innerHTML = '<div class="trade-item"><p style="color: #94a3b8;">No open trades</p></div>';
            return;
        }
        
        tradesList.innerHTML = trades.map(trade => {
            const pnl = trade.pnl_percent || 0;
            const pnlClass = pnl > 0 ? 'green' : 'red';
            
            return `
                <div class="trade-item ${pnlClass}">
                    <div class="trade-header">
                        <h4>${trade.symbol} ${trade.direction}</h4>
                        <span class="trade-status">${pnl > 0 ? '+' : ''}${pnl.toFixed(2)}%</span>
                    </div>
                    <p class="trade-info">Entry: $${parseFloat(trade.entry_price).toLocaleString('en-US', {maximumFractionDigits: 8})}</p>
                    <p class="trade-current">TP1: $${parseFloat(trade.tp1).toLocaleString('en-US', {maximumFractionDigits: 8})}</p>
                </div>
            `;
        }).join('');
    }
    
    updateConnectionStatus(connected) {
        const status = document.getElementById('connection-status');
        if (connected) {
            status.textContent = '🟢 Connected';
            status.style.borderColor = '#10b981';
        } else {
            status.textContent = '🔴 Disconnected';
            status.style.borderColor = '#ef4444';
        }
    }
    
    updateLastUpdate() {
        const now = new Date();
        const time = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        document.getElementById('update-time').textContent = `Last: ${time}`;
    }
    
    startAutoRefresh() {
        if (this.updateInterval) clearInterval(this.updateInterval);
        this.updateInterval = setInterval(() => {
            this.loadDashboardData();
        }, 10000); // Every 10 seconds
    }
    
    subscribe(symbol) {
        if (this.socket) {
            this.socket.emit('subscribe_symbol', { symbol });
        }
    }
    
    showTradeModal() {
        document.getElementById('trade-modal').style.display = 'block';
        document.getElementById('trade-symbol').value = this.currentSymbol;
    }
    
    hideTradeModal() {
        document.getElementById('trade-modal').style.display = 'none';
        document.getElementById('trade-form').reset();
    }
    
    async addTrade() {
        const form = document.getElementById('trade-form');
        const direction = form.querySelector('input[name="direction"]:checked').value;
        const entryPrice = parseFloat(document.getElementById('entry-input').value);
        
        if (!entryPrice || entryPrice <= 0) {
            this.addAlert('❌ Invalid entry price', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/api/v1/add-trade', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    symbol: this.currentSymbol,
                    direction,
                    entry_price: entryPrice
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.addAlert(`✅ Trade added: ${this.currentSymbol} ${direction} @ $${entryPrice}`, 'success');
                this.hideTradeModal();
                this.loadDashboardData();
            } else {
                this.addAlert(`❌ Error: ${data.error}`, 'warning');
            }
        } catch (error) {
            console.error('Add trade error:', error);
            this.addAlert('❌ Failed to add trade', 'warning');
        }
    }
    
    addTradeToList(trade) {
        const tradesList = document.getElementById('trades-list');
        const tradeEl = document.createElement('div');
        tradeEl.className = `trade-item ${trade.direction === 'LONG' ? 'green' : 'red'}`;
        tradeEl.innerHTML = `
            <div class="trade-header">
                <h4>${trade.symbol} ${trade.direction}</h4>
                <span class="trade-status">0.0%</span>
            </div>
            <p class="trade-info">Entry: $${parseFloat(trade.entry_price).toLocaleString('en-US', {maximumFractionDigits: 8})}</p>
            <p class="trade-current">TP1: $${parseFloat(trade.tp1).toLocaleString('en-US', {maximumFractionDigits: 8})}</p>
        `;
        tradesList.insertBefore(tradeEl, tradesList.firstChild);
    }
    
    addAlert(message, type = 'info') {
        const alertsContainer = document.getElementById('alerts-container');
        const alertEl = document.createElement('div');
        alertEl.className = `alert alert-${type}`;
        alertEl.textContent = message;
        
        alertsContainer.insertBefore(alertEl, alertsContainer.firstChild);
        
        // Keep only last 10 alerts
        while (alertsContainer.children.length > 10) {
            alertsContainer.removeChild(alertsContainer.lastChild);
        }
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            alertEl.remove();
        }, 10000);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardApp = new DashboardApp();
});
