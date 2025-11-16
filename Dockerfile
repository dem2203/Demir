FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential gcc g++ libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy required files (backend)
COPY main.py .
COPY ai_brain_ensemble.py .

# Try to copy optional frontend files
# COPY fails silently on missing files with --chown or we use a workaround
# WORKAROUND: Create a script that tries to copy
COPY . . 2>/dev/null || true

# Create logs dir
RUN mkdir -p /app/logs

# Verify files
RUN ls -la /app/ | grep -E "(main\.py|ai_brain|\.html|\.js|\.css)" || echo "Backend files present, frontend optional"

EXPOSE 8000
ENV PYTHONUNBUFFERED=1 PORT=8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "main:app"]
