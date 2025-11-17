# DEMIR AI BOT - UI Requirements & Specifications

## Overview
Modern, responsive HTML/CSS/JS frontend for DEMIR AI Bot
Real-time WebSocket integration + REST API
Production-grade dashboard with interactive components

## Technology Stack
- Frontend: HTML5, CSS3, JavaScript (ES6+)
- Real-time: WebSocket (Binance data)
- API: REST (FastAPI/Flask backend)
- Charts: Chart.js or TradingView Lightweight Charts
- State Management: Vanilla JS or Vue.js
- Deployment: Railway (static files)

## Page Structure

### 1. Dashboard (Main Page)
- **Header**
  - Bot status (🟢 Active / 🔴 Inactive)
  - System uptime
  - Last signal timestamp
  - API health indicators

- **Market Status Card** (Real-time WebSocket)
  - BTC/USD, ETH/USD, LTC/USD price tickers
  - 24h change %, volume
  - Update every 1 second (no page refresh)

- **Signal Panel** (REST API)
  - Latest signals: BTCUSDT, ETHUSDT, LTCUSDT + manual coins
  - Signal strength indicator (color-coded)
  - Entry, TP1, TP2, SL prices
  - Confidence score
  - Time ago

- **Statistics Widget**
  - Win rate: X%
  - Total trades: N
  - Total PnL: $X
  - Sharpe ratio: X.XX
  - Max drawdown: -X%

- **Layer Performance** (optional toggle)
  - Top 5 performing layers
  - Underperforming layers
  - Layer health score

### 2. Coins Management Page
- **Default Coins** (Read-only)
  - ✅ BTCUSDT
  - ✅ ETHUSDT
  - ✅ LTCUSDT

- **Manual Coin Addition**
  - Input field: "Add coin (e.g., SOLUSDT)"
  - Button: "ADD COIN"
  - Auto-validate format (must end with USDT)
  - Add to database (persistent)
  - Remove button for each manual coin

- **Coin Signals**
  - Mini-cards for each tracked coin
  - Current signal + strength
  - Delete button (for manual coins)

### 3. Analytics & Reports Page
- **Performance Chart**
  - Equity curve (line chart)
  - Dates on X-axis
  - Cumulative PnL on Y-axis
  - Drawdown visualization below

- **Trade History Table**
  - Date, Symbol, Direction, Entry, Exit, PnL, PnL%
  - Sortable columns
  - Filter by symbol, date range
  - Pagination (50 rows/page)

- **Win Rate Analysis**
  - Monthly win rates (bar chart)
  - Win rate trend (line chart)
  - Statistics table

### 4. Settings & Configuration
- **API Status**
  - Binance: 🟢 Healthy (98% uptime)
  - Bybit: 🟢 Healthy (99% uptime)
  - Coinbase: 🟢 Healthy (97% uptime)
  - Other APIs status

- **Bot Configuration**
  - Layer count display: 71 active, 40 optimal
  - Backtest option (button)
  - Reset system (warning)

- **Log Viewer**
  - Last 100 log entries
  - Filter by level (DEBUG, INFO, WARNING, ERROR)
  - Auto-scroll to latest

### 5. System Monitoring
- **Real-time Metrics**
  - CPU usage
  - Memory usage
  - Active threads
  - API call rate
  - Signal generation rate

- **API Health Dashboard**
  - Each API's uptime graph
  - Failure alerts
  - Response time trends

## Design System

### Color Scheme
- Primary: #0066CC (Crypto Blue)
- Success: #00AA00 (Green - Bullish)
- Danger: #CC0000 (Red - Bearish)
- Neutral: #CCCCCC (Gray)
- Background: #111111 (Dark)
- Text: #EEEEEE (Light)

### Components

**Signal Strength Indicator**
- 🟢🟢🟢🟢🟢 Extreme Bullish (0.9-1.0)
- 🟢🟢🟢🟢 Strong Bullish (0.8-0.89)
- 🟢🟢🟢 Bullish (0.65-0.79)
- ⚪ Neutral (0.35-0.64)
- 🔴🔴 Bearish (0.2-0.34)
- 🔴🔴🔴 Strong Bearish (0.0-0.19)

**Status Badges**
- 🟢 Healthy / Active
- 🟡 Degraded / Warning
- 🔴 Failed / Error
- ⚪ Neutral / Inactive

### Responsive Design
- Desktop: Full layout (1920px+)
- Tablet: Side menu collapsible (768px-1920px)
- Mobile: Bottom navigation (< 768px)

## API Integration Points

### WebSocket (Real-time)
```javascript
// Market status - every second
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updatePriceTicker(data);
};
```

### REST API Endpoints
```
GET /api/signals/latest → Display latest signals
GET /api/market/{symbol} → Update price
GET /api/coins → List tracked coins
POST /api/coins → Add new coin
DELETE /api/coins/{symbol} → Remove coin
GET /api/analytics/performance → Performance chart
GET /api/trades/history → Trade history
GET /api/health → System health
GET /api/status → Bot status
```

## Performance Requirements
- Page load: < 2 seconds
- Signal update latency: < 500ms
- Price update: < 1 second (WebSocket)
- Charts render: < 1 second
- Database queries: < 100ms

## Security Considerations
- HTTPS only (Railway SSL)
- CSRF protection
- Rate limiting on API endpoints
- No sensitive data in localStorage
- Secure WebSocket (WSS)

## Browser Support
- Chrome/Chromium: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Edge: Latest 2 versions
- Mobile browsers: iOS Safari, Chrome Android

## Deployment Instructions

1. **Build UI files**
   ```bash
   npm run build  # if using build tools
   # OR static files in /ui folder
   ```

2. **Upload to Railway**
   ```bash
   git add .
   git commit -m "feat: Production UI with WebSocket/REST"
   git push  # Auto-deploys to Railway
   ```

3. **Configure environment**
   - Set SERVE_TEMPLATES=true in Railway
   - API_URL pointing to backend

## Testing Checklist
- [ ] Responsive on mobile/tablet/desktop
- [ ] WebSocket reconnection on failure
- [ ] API call error handling
- [ ] Signal updates in real-time
- [ ] Coin addition/removal works
- [ ] Charts render correctly
- [ ] Performance under load
- [ ] Cross-browser compatibility

## Future Enhancements
- Dark/Light mode toggle
- Customizable dashboard layout
- Advanced analytics (ML-powered insights)
- Trading simulation mode
- Mobile app (React Native)
- Multi-language support
- Email/SMS alerts
