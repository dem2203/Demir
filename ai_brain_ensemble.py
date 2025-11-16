"""
🚀 DOCKERFILE - PRODUCTION FIXED VERSION
✅ Railway-compatible with health check + proper startup

Location: GitHub Root / Dockerfile
Date: 2025-11-16 12:10 CET
"""

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port that Railway will use
EXPOSE 8000

# ✅ CRITICAL: Set the environment variable for Railway
ENV PORT=8000

# ✅ Health check for Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ✅ Startup command - THIS WAS MISSING!
CMD ["python", "main.py"]
