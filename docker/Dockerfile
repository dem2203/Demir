FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Create entrypoint script that runs database_init.py first
RUN mkdir -p /app && \
    echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo 'set -e' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo 'echo "🚀 DEMIR AI - Starting Application"' >> /app/entrypoint.sh && \
    echo 'echo "======================================"' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo 'echo "📊 Step 1: Initializing Database..."' >> /app/entrypoint.sh && \
    echo 'python database_init.py' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo 'echo "======================================"' >> /app/entrypoint.sh && \
    echo 'echo "✅ Database Ready!"' >> /app/entrypoint.sh && \
    echo 'echo ""' >> /app/entrypoint.sh && \
    echo 'echo "🎨 Step 2: Starting Streamlit Dashboard..."' >> /app/entrypoint.sh && \
    echo 'streamlit run streamlit_app.py \' >> /app/entrypoint.sh && \
    echo '    --server.port=8501 \' >> /app/entrypoint.sh && \
    echo '    --server.address=0.0.0.0 \' >> /app/entrypoint.sh && \
    echo '    --logger.level=info' >> /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run entrypoint script
CMD ["/app/entrypoint.sh"]
