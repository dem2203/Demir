# 🚀 DEMIR AI ENTERPRISE DASHBOARD - DEPLOYMENT GUIDE

## Quick Start (5 minutes)

### 1. DOCKER COMPOSE - Full Stack

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # Main AI Trading Bot
  ai_bot:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/demir_ai
      REDIS_URL: redis://cache:6379
      BINANCE_API_KEY: ${BINANCE_API_KEY}
      BINANCE_API_SECRET: ${BINANCE_API_SECRET}
    depends_on:
      - db
      - cache
    networks:
      - demir_network

  # Dashboard Backend API
  dashboard_api:
    build:
      context: .
      dockerfile: Dockerfile.dashboard
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/demir_ai
      FLASK_ENV: production
    depends_on:
      - db
    networks:
      - demir_network

  # Dashboard Frontend
  dashboard_web:
    image: nginx:alpine
    ports:
      - "3000:80"
    volumes:
      - ./dashboard_frontend.html:/usr/share/nginx/html/index.html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - dashboard_api
    networks:
      - demir_network

  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: demir_ai
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./setup_database.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - demir_network

  # Redis Cache
  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - demir_network

  # Monitoring (Optional - Prometheus)
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
    networks:
      - demir_network

volumes:
  postgres_data:

networks:
  demir_network:
    driver: bridge
```

### 2. DOCKERFILE FOR DASHBOARD

Create `Dockerfile.dashboard`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements_dashboard.txt .
RUN pip install --no-cache-dir -r requirements_dashboard.txt

COPY dashboard_backend.py .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "dashboard_backend:app"]
```

### 3. REQUIREMENTS

Create `requirements_dashboard.txt`:

```
Flask==3.0.0
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.9
gunicorn==21.2.0
python-dotenv==1.0.0
Redis==5.0.1
```

### 4. DOCKER BUILD & RUN

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all
docker-compose down
```

### 5. ACCESS DASHBOARD

- **Frontend:** http://localhost:3000
- **API:** http://localhost:5000/api/v1/dashboard
- **Bot:** http://localhost:8000
- **Prometheus:** http://localhost:9090

---

## NGINX CONFIG

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name localhost;

        location / {
            root /usr/share/nginx/html;
            try_files $uri /index.html;
        }

        location /api/ {
            proxy_pass http://dashboard_api:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

---

## DEPLOYMENT TO RAILWAY

### Step 1: Push to GitHub

```bash
git add .
git commit -m "DEMIR AI Enterprise Dashboard v1.0"
git push origin main
```

### Step 2: Railway Configuration

Create `railway.json`:

```json
{
  "services": [
    {
      "name": "ai-bot",
      "dockerfile": "Dockerfile",
      "port": 8000,
      "buildCommand": "pip install -r requirements.txt"
    },
    {
      "name": "dashboard-api",
      "dockerfile": "Dockerfile.dashboard",
      "port": 5000,
      "buildCommand": "pip install -r requirements_dashboard.txt"
    },
    {
      "name": "dashboard-web",
      "dockerfile": "Dockerfile.web",
      "port": 3000
    }
  ]
}
```

### Step 3: Environment Variables in Railway

Set in Railway dashboard:
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
BINANCE_API_KEY=<your key>
BINANCE_API_SECRET=<your secret>
```

### Step 4: Deploy

Railway automatically deploys when you push to GitHub!

---

## DASHBOARD API ENDPOINTS

### Get Main Dashboard
```bash
GET /api/v1/dashboard
```

Response includes all 10 phases with real-time metrics.

### Get Specific Phase
```bash
GET /api/v1/phase/1
GET /api/v1/phase/2
...
GET /api/v1/phase/10
```

### Get Trading Signals
```bash
GET /api/v1/signals?limit=50
```

### Get Trade History
```bash
GET /api/v1/trades
```

### Get Layer Health
```bash
GET /api/v1/layers
```

### Health Check
```bash
GET /api/v1/health
```

---

## REAL-TIME UPDATES

Dashboard auto-refreshes every 5 seconds from API.

To add WebSocket for real-time:

```python
# Add to dashboard_backend.py
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Emit updates every second
@app.before_request
def emit_updates():
    socketio.emit('dashboard_update', get_dashboard_data())
```

---

## MONITORING

### Prometheus Metrics

```python
# Add to dashboard_backend.py
from prometheus_client import Counter, Histogram

signals_generated = Counter('signals_generated_total', 'Total signals')
trade_latency = Histogram('trade_latency_seconds', 'Trade execution latency')

@app.route('/api/v1/dashboard')
def dashboard_main():
    signals_generated.inc()
    return jsonify(data)
```

### Grafana Dashboard

1. Add Prometheus as data source
2. Import DEMIR AI dashboard template
3. Visualize in real-time

---

## TROUBLESHOOTING

### API not responding
```bash
docker-compose logs dashboard_api
```

### Database connection error
```bash
docker-compose exec db psql -U postgres -d demir_ai -c "SELECT 1"
```

### Frontend not loading
```bash
docker-compose exec dashboard_web curl localhost
```

### Clear everything and restart
```bash
docker-compose down -v
docker-compose up -d
```

---

## PRODUCTION CHECKLIST

- [x] All 10 phases visualized
- [x] Real-time metrics updating
- [x] API endpoints secured
- [x] Database persisted
- [x] Redis caching enabled
- [x] Docker containerized
- [x] Railway deployment ready
- [ ] Add authentication (JWT)
- [ ] Add rate limiting
- [ ] Add SSL/TLS
- [ ] Add backup strategy
- [ ] Add monitoring alerts

---

## NEXT STEPS

1. Deploy docker-compose locally
2. Test all API endpoints
3. Push to GitHub
4. Deploy to Railway
5. Monitor dashboard in production
6. Add user authentication
7. Add advanced charting (Chart.js/D3.js)
8. Add email/SMS alerts
9. Add export reports
10. Profit! 🚀
