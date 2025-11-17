# Dockerfile - DEMIR AI v6.0 - DASHBOARD & FRONTEND FIXED
# Build: Railway auto-detects and builds
# Includes: Frontend files (HTML/CSS/JS) + Python Backend

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ libpq-dev curl git \
    && rm -rf /var/lib/apt/lists/*

# Copy frontend files FIRST (HTML, CSS, JS)
COPY index.html .
COPY app.js .
COPY style.css .

# Copy requirements and install
COPY requirements.txt .
RUN pip install --default-timeout=1000 --retries 5 \
    -i https://pypi.mirrors.aliyun.com/simple -r requirements.txt

# Copy Python backend files
COPY main.py ai_brain_ensemble.py ./

# Copy additional config files (if exists)
COPY config.py .
COPY ai_brain_ensemble.py .

# Create runtime directories
RUN mkdir -p /app/logs /app/data /app/models /app/config

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    FLASK_ENV=production \
    DEBUG=False

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health 2>/dev/null || exit 1

# Start application
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers ${WORKERS:-4} --worker-class sync --timeout 120 --access-logfile - --error-logfile - main:app"]
