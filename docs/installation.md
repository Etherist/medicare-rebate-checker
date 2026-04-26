# Installation Guide

## Prerequisites

- Python 3.12+
- UV package manager (recommended) or pip
- Git

## Quick Start (Development)

### Using UV (Recommended)

```bash
# Clone repository
git clone https://github.com/your-username/medicare-rebate-checker.git
cd medicare-rebate-checker

# Sync dependencies (creates virtual environment automatically)
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or on Windows: .venv\Scripts\activate

# Run the application
streamlit run src/app/streamlit_app.py
```

### Using pip + venv

```bash
# Clone repository
git clone https://github.com/your-username/medicare-rebate-checker.git
cd medicare-rebate-checker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests to verify installation
pytest tests/ -v
```

## Docker Installation

### Build and Run with Docker

```bash
# Build production image
docker build -t medicare-rebate-checker:latest .

# Run container
docker run -d \
  --name medicare-checker \
  -p 8000:8000 \
  -p 8501:8501 \
  -v $(pwd)/reports:/app/reports \
  medicare-rebate-checker:latest
```

### Using Docker Compose (Development)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Kubernetes Deployment

### Prerequisites

- kubectl configured with cluster access
- Helm 3+ (optional, for Helm chart deployment)

### Deploy with kubectl

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=medicare-checker

# Port forward for local access
kubectl port-forward svc/medicare-checker 8000:8000
```

### Deploy with Helm

```bash
# Install Helm chart
helm install medicare-checker ./helm \
  --namespace healthcare \
  --create-namespace \
  --set image.tag=latest

# Upgrade
helm upgrade medicare-checker ./helm \
  --set image.tag=v1.0.1

# Uninstall
helm uninstall medicare-checker -n healthcare
```

## Production Deployment

### Environment Configuration

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with production values:
   ```env
   APP_ENV=production
   LOG_LEVEL=WARNING
   CACHE_TTL=3600
   MBS_CACHE_ENABLED=true
   MBS_CACHE_REDIS_URL=redis://redis-service:6379
   ```

### Database Setup (Optional)

For production with persistent cache:

```bash
# Start Redis
docker run -d --name redis -p 6379:6379 redis:alpine

# Initialize cache
python scripts/init_cache.py
```

### Security Hardening

```bash
# Run security scans
bandit -r src/ -ll
safety check --full-report

# Generate SBOM
cyclonedx-bom -o sbom.xml
```

## Verification

### Run Full Test Suite

```bash
# Unit tests with coverage
pytest tests/ -v --cov=src --cov-report=html

# Integration tests
pytest tests/integration/ -v

# Performance benchmarks
pytest tests/performance/ -v
```

### Manual Verification

```bash
# Test CLI
python src/app/cli.py --mbs-item 13200 --age 35 --has-medicare-card True

# Test API
curl http://localhost:8000/health

# Test Streamlit UI
streamlit run src/app/streamlit_app.py
```

## Troubleshooting

### Common Issues

**Import errors**: Ensure virtual environment is activated and dependencies installed:
```bash
source .venv/bin/activate
uv sync
```

**Port already in use**: Change ports in configuration or stop conflicting service:
```bash
lsof -ti:8000 | xargs kill -9
```

**Cache errors**: Clear cache and reinitialize:
```bash
rm -rf reports/
python scripts/init_cache.py
```

### Getting Help

- Open an issue on GitHub
- Check existing documentation in `/docs`
- Review logs in `logs/` directory (if configured)