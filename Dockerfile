# ============================================================================
# DOCKERFILE - Container Configuration
# ============================================================================

DOCKERFILE_CONTENT = """
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set environment
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_LOGGER_LEVEL=warning

# Run main application
CMD ["python", "main.py"]
"""
