```python
class GithubActionsCI:
    """GitHub Actions automation"""
    
    @staticmethod
    def get_github_workflow() -> str:
        return """
name: DEMIR AI Production Deployment

on:
  push:
    branches: [main, production]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.12
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov black flake8 mypy
    
    - name: Code formatting check
      run: black --check .
    
    - name: Linting
      run: flake8 . --count --select=E9,F63,F7,F82 --show-source
    
    - name: Type checking
      run: mypy . --ignore-missing-imports
    
    - name: Unit tests
      run: pytest tests/ -v --cov=. --cov-report=xml
    
    - name: Integration tests
      run: pytest tests/integration/ -v
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t demir-ai:latest .
    
    - name: Push to registry
      run: |
        docker tag demir-ai:latest ${{secrets.REGISTRY}}/demir-ai:latest
        docker push ${{secrets.REGISTRY}}/demir-ai:latest

  deploy-railway:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Railway
      uses: railwayapp/railway-action@v1
      with:
        token: ${{ secrets.RAILWAY_TOKEN }}
        service: demir-ai
        environment: production

  deploy-k8s:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/production'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set kubeconfig
      run: |
        mkdir -p $HOME/.kube
        echo "${{ secrets.KUBE_CONFIG }}" | base64 --decode > $HOME/.kube/config
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/namespace.yml
        kubectl apply -f k8s/configmap.yml
        kubectl apply -f k8s/secret.yml
        kubectl apply -f k8s/deployment.yml
        kubectl set image deployment/demir-ai-trading-bot \\
          demir-ai=${{secrets.REGISTRY}}/demir-ai:latest
"""
