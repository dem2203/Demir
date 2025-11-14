# docker_config.py - Docker Configuration Management

import logging

logger = logging.getLogger(__name__)

class DockerConfig:
    """Docker deployment configuration"""
    
    @staticmethod
    def generate_dockerfile():
        """Generate production Dockerfile"""
        dockerfile = """
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    postgresql-client gcc g++ python3-dev && \\
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
"""
        return dockerfile


