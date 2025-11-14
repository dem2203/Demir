```python
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
import logging
import yaml

logger = logging.getLogger(__name__)

class KubernetesOrchestrator:
    """Enterprise Kubernetes management for DEMIR AI"""
    
    def __init__(self, kubeconfig_path: str = None):
        try:
            config.load_kube_config(kubeconfig_path)
        except:
            config.load_incluster_config()
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.batch_v1 = client.BatchV1Api()
    
    def deploy_demir_ai(self, namespace: str = "default") -> bool:
        """Deploy complete DEMIR AI stack on Kubernetes"""
        
        # StatefulSet for main trading bot
        statefulset = {
            'apiVersion': 'apps/v1',
            'kind': 'StatefulSet',
            'metadata': {
                'name': 'demir-ai-trading-bot',
                'namespace': namespace
            },
            'spec': {
                'serviceName': 'demir-ai',
                'replicas': 3,
                'selector': {
                    'matchLabels': {'app': 'demir-ai-bot'}
                },
                'template': {
                    'metadata': {
                        'labels': {'app': 'demir-ai-bot'}
                    },
                    'spec': {
                        'containers': [{
                            'name': 'demir-ai',
                            'image': 'demir-ai:latest',
                            'resources': {
                                'requests': {
                                    'memory': '4Gi',
                                    'cpu': '2'
                                },
                                'limits': {
                                    'memory': '8Gi',
                                    'cpu': '4'
                                }
                            },
                            'env': [
                                {'name': 'DATABASE_URL', 'valueFrom': {'secretKeyRef': {
                                    'name': 'demir-secrets', 'key': 'database-url'}}},
                                {'name': 'BINANCE_API_KEY', 'valueFrom': {'secretKeyRef': {
                                    'name': 'demir-secrets', 'key': 'binance-key'}}},
                            ],
                            'livenessProbe': {
                                'httpGet': {'path': '/health', 'port': 8000},
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10
                            },
                            'readinessProbe': {
                                'httpGet': {'path': '/ready', 'port': 8000},
                                'initialDelaySeconds': 5,
                                'periodSeconds': 5
                            }
                        }],
                        'affinity': {
                            'podAntiAffinity': {
                                'preferredDuringSchedulingIgnoredDuringExecution': [{
                                    'weight': 100,
                                    'podAffinityTerm': {
                                        'labelSelector': {
                                            'matchExpressions': [{
                                                'key': 'app',
                                                'operator': 'In',
                                                'values': ['demir-ai-bot']
                                            }]
                                        },
                                        'topologyKey': 'kubernetes.io/hostname'
                                    }
                                }]
                            }
                        }
                    }
                }
            }
        }
        
        # Deploy
        try:
            self.apps_v1.create_namespaced_stateful_set(namespace, statefulset)
            logger.info("✅ StatefulSet deployed")
            return True
        except ApiException as e:
            logger.error(f"Deployment error: {e}")
            return False
    
    def setup_horizontal_autoscaling(self, namespace: str = "default"):
        """Setup HPA for dynamic scaling"""
        
        hpa = {
            'apiVersion': 'autoscaling/v2',
            'kind': 'HorizontalPodAutoscaler',
            'metadata': {
                'name': 'demir-ai-hpa',
                'namespace': namespace
            },
            'spec': {
                'scaleTargetRef': {
                    'apiVersion': 'apps/v1',
                    'kind': 'StatefulSet',
                    'name': 'demir-ai-trading-bot'
                },
                'minReplicas': 2,
                'maxReplicas': 10,
                'metrics': [{
                    'type': 'Resource',
                    'resource': {
                        'name': 'cpu',
                        'target': {
                            'type': 'Utilization',
                            'averageUtilization': 70
                        }
                    }
                }, {
                    'type': 'Resource',
                    'resource': {
                        'name': 'memory',
                        'target': {
                            'type': 'Utilization',
                            'averageUtilization': 80
                        }
                    }
                }]
            }
        }
        
        try:
            client.CustomObjectsApi().create_namespaced_custom_object(
                'autoscaling', 'v2', namespace, 'horizontalpodautoscalers',
                hpa
            )
            logger.info("✅ HPA configured")
        except Exception as e:
            logger.error(f"HPA error: {e}")

class DockerComposeManager:
    """Docker Compose for local/testing deployments"""
    
    @staticmethod
    def get_docker_compose() -> str:
        return """
version: '3.8'

services:
  demir-ai:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8501:8501"
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/demir_ai
      - BINANCE_API_KEY=${BINANCE_API_KEY}
      - BYBIT_API_KEY=${BYBIT_API_KEY}
      - COINBASE_API_KEY=${COINBASE_API_KEY}
      - FRED_API_KEY=${FRED_API_KEY}
      - TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
    depends_on:
      - postgres
      - redis
    networks:
      - demir-network
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=demir_ai
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - demir-network
    restart: always

  redis:
    image: redis:7-alpine
    networks:
      - demir-network
    restart: always

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - demir-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - demir-network

volumes:
  postgres_data:
  prometheus_data:
  grafana_data:

networks:
  demir-network:
    driver: bridge
"""
