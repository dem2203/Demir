# Dockerfile - DEMIR AI v8.0 - PRODUCTION READY
# Optimized for Railway deployment with staged pip install to prevent timeout
FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ libpq-dev curl git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --upgrade pip

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with extended timeout and retry logic
# This prevents Railway timeout errors for large packages (xgboost, scipy, etc.)
RUN pip install --no-cache-dir \
    --default-timeout=300 \
    --retries=5 \
    -r requirements.txt

# Copy entire application
COPY . .

# Runtime directories
RUN mkdir -p /app/logs /app/data /app/models

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    FLASK_ENV=production \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start with optimized gunicorn config for Railway
# Using gevent worker for WebSocket support
# Reduced workers to 1 for Railway's resource limits
CMD ["gunicorn", \
     "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", \
     "-w", "1", \
     "-b", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--worker-connections", "1000", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "main:app"]
