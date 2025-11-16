FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ libpq-dev curl git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ONLY essential Python files
COPY main.py ai_brain_ensemble.py ./

# Create runtime directories
RUN mkdir -p /app/logs /app/data /app/models /app/config

ENV PYTHONUNBUFFERED=1 PORT=8000 FLASK_ENV=production DEBUG=False

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health 2>/dev/null || exit 1

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers ${WORKERS:-4} --worker-class sync --timeout 120 --access-logfile - --error-logfile - main:app"]
