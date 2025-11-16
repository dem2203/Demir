FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential gcc g++ libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy main Python files (MUST EXIST)
COPY main.py .
COPY ai_brain_ensemble.py .

# Copy all other files from repo (COPY . . works fine here)
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Show what was copied
RUN echo "=== FILES IN CONTAINER ===" && ls -la /app/ && echo "=== END ==="

# Expose port
EXPOSE 8000

# Environment
ENV PYTHONUNBUFFERED=1 PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "main:app"]
