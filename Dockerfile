FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential gcc g++ libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Copy ve install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy APP FILES (MAIN)
COPY main.py .
COPY ai_brain_ensemble.py .
COPY index.html .
COPY app.js .
COPY style.css .

# Create logs dir
RUN mkdir -p /app/logs && echo "=== DOCKER BUILD COMPLETE ===" && ls -la /app/

# Expose
EXPOSE 8000

# ENV
ENV PYTHONUNBUFFERED=1 PORT=8000

# HEALTH
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# RUN
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "main:app"]
