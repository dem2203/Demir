# Dockerfile - DEMIR AI v7.0 - PRODUCTION READY
FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ libpq-dev curl git \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire application
COPY . .

# Runtime directories
RUN mkdir -p /app/logs /app/data /app/models

# Environment
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    FLASK_ENV=production

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "main:app"]
