FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements WITHOUT hash verification
COPY requirements.txt .
RUN pip install --no-cache-dir --no-deps -r requirements.txt

# Copy application files
COPY main.py ai_brain_ensemble.py ./
COPY . .

# Create runtime directories
RUN mkdir -p /app/logs /app/data

EXPOSE 8000
ENV PYTHONUNBUFFERED=1 PORT=8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "main:app"]
