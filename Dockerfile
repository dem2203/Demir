FROM python:3.11-slim

WORKDIR /app

# ✅ Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ✅ Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy application code
COPY . .

# ✅ Set environment variables
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ✅ Expose port (Railway will override if needed)
EXPOSE 8000

# ✅ CRITICAL: Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ✅ CRITICAL: Start command (must be last)
CMD ["python", "main.py"]
