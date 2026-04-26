# Deployment Guide

## Overview

This guide covers production deployment options for the Medicare Rebate Checker.

## Deployment Options

Choose the option that matches your environment:

- **Docker Compose** – Simple single-server deployments
- **Kubernetes** – Scalable cloud-native deployments (recommended for production)
- **Helm** – Kubernetes with configurable releases
- **Bare metal** – Traditional VM/server installation

## Option 1: Docker Compose (Development/Staging)

### Prerequisites

- Docker Engine ≥ 24.0
- Docker Compose ≥ 2.0
- 2 GB RAM minimum, 4 GB recommended

### Steps

1. **Clone repository**
   ```bash
   git clone https://github.com/your-username/medicare-rebate-checker.git
   cd medicare-rebate-checker
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env as needed (see Configuration)
   ```

3. **Start services**
   ```bash
   # Development stack (API + Streamlit + Redis)
   docker-compose up -d

   # Production stack (uses docker-compose.prod.yml)
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Verify**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8501  # Streamlit health
   ```

5. **View logs**
   ```bash
   docker-compose logs -f api
   ```

### Scaling

Increase replica count in `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      replicas: 3
```

## Option 2: Kubernetes (Production)

### Prerequisites

- Kubernetes cluster (v1.24+)
- `kubectl` configured
- **Optional**: Helm 3+ for templated deployment

### Quick Deploy (Manifests)

1. **Create namespace**
   ```bash
   kubectl apply -f k8s/00-namespace.yaml
   ```

2. **Deploy Redis**
   ```bash
   kubectl apply -f k8s/20-redis.yaml
   ```

3. **Deploy application**
   ```bash
   kubectl apply -f k8s/10-api-deployment.yaml
   ```

4. **Verify**
   ```bash
   kubectl get pods -n healthcare
   kubectl logs -f deployment/medicare-checker-api -n healthcare
   ```

5. **Access service**
   ```bash
   # Port forward
   kubectl port-forward svc/medicare-checker-api 8000:8000 -n healthcare

   # Or via Ingress (if configured)
   # Ensure DNS record points to cluster ingress IP
   ```

### Deploy with Helm

1. **Install Helm chart**
   ```bash
   helm repo add medicare-checker ./helm
   helm install medicare-checker medicare-checker/medicare-checker \
     --namespace healthcare --create-namespace \
     --set image.tag=latest \
     --set replicas=3
   ```

2. **Upgrade**
   ```bash
   helm upgrade medicare-checker ./helm \
     --set image.tag=v1.0.1
   ```

3. **Uninstall**
   ```bash
   helm uninstall medicare-checker -n healthcare
   ```

### Helm Chart Structure

```
helm/
├── Chart.yaml           # Chart metadata
├── values.yaml          # Default configuration
├── values-prod.yaml     # Production overrides
├── templates/           # K8s manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   └── configmap.yaml
```

### Production Hardening

- Enable TLS via cert-manager
- Configure network policies
- Set resource requests/limits
- Enable PodDisruptionBudget for HA
- Use private container registry
- Enable audit logging

## Option 3: Virtual Machine (Bare Metal)

### Prerequisites

- Ubuntu 22.04 LTS or similar
- Python 3.12 installed
- Root or sudo access

### Steps

1. **Install system packages**
   ```bash
   sudo apt update
   sudo apt install -y python3.12 python3.12-venv python3-pip git
   ```

2. **Clone and setup**
   ```bash
   git clone https://github.com/your-username/medicare-rebate-checker.git
   cd medicare-rebate-checker
   python3.12 -m venv venv
   source venv/bin/activate
   uv sync --all-extras
   ```

3. **Create systemd service**
   ```bash
   sudo cp deploy/systemd/medicare-api.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable medicare-api
   sudo systemctl start medicare-api
   ```

4. **Configure Nginx reverse proxy**
   ```bash
   sudo cp deploy/nginx/medicare.conf /etc/nginx/sites-available/
   sudo ln -s /etc/nginx/sites-available/medicare.conf /etc/nginx/sites-enabled/
   sudo certbot --nginx -d medicare.example.com  # TLS
   sudo systemctl reload nginx
   ```

5. **Set up log rotation**
   ```bash
   sudo cp deploy/logrotate/medicare /etc/logrotate.d/
   ```

## Environment-Specific Considerations

### Development

- Use `docker-compose.yml` (includes hot-reload)
- Debug logging enabled
- No TLS (use HTTP)
- Redis cache optional

### Staging

- Mirror production Kubernetes config
- Realistic data (sanitized)
- TLS with self-signed or staging certificate
- Smaller replica count (1-2)
- Monitoring enabled, alerting to test channel

### Production

- Use `docker-compose.prod.yml` or K8s manifests
- TLS mandatory (via cert-manager or manual certs)
- **Multiple replicas** (minimum 2)
- Redis with authentication and persistence
- Rate limiting enabled
- Centralized logging & monitoring
- Automated backups of reports directory
- Regular security patches

## Zero-Downtime Deployments

### Kubernetes Rolling Update

Default strategy:

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

### Blue-Green with Helm

```bash
# Install to alternate release name
helm install medicare-checker-green ./helm --set image.tag=v1.0.1

# Switch traffic via Ingress annotation
kubectl annotate ingress medicare-checker-ingress nginx.ingress.kubernetes.io/canary="true" nginx.ingress.kubernetes.io/canary-weight="100"

# Remove old release
helm uninstall medicare-checker -n healthcare
```

## Rollback Procedures

### Kubernetes

```bash
# View revision history
kubectl rollout history deployment/medicare-checker-api -n healthcare

# Rollback to previous
kubectl rollout undo deployment/medicare-checker-api -n healthcare

# Rollback to specific revision
kubectl rollout undo deployment/medicare-checker-api --to-revision=2 -n healthcare
```

### Docker Compose

```bash
# Rebuild previous image tag
docker-compose pull medicare-checker:previous-tag

# Recreate containers
docker-compose up -d --force-recreate
```

## Post-Deployment Verification

Run the verification checklist:

```bash
# 1. Health endpoint
curl -f http://localhost:8000/health || echo "FAIL"

# 2. Sample API call
curl -X POST http://localhost:8000/check-rebate \
  -H "Content-Type: application/json" \
  -d '{"mbs_item":"13200","age":35,"has_medicare_card":true}'

# 3. Check metrics
curl http://localhost:8000/metrics | grep request

# 4. Verify cache
redis-cli ping

# 5. Check logs for errors
docker-compose logs api | grep -i error || echo "No errors"

# 6. Load test (optional)
locust -f tests/performance/locustfile.py --headless -u 10 -r 2 -t 30s
```

## Troubleshooting Deployments

### Pods not starting

```bash
kubectl describe pod <pod-name> -n healthcare
kubectl logs <pod-name> -n healthcare
```

### Redis connection refused

```bash
kubectl get pods -n healthcare  # Is redis running?
kubectl exec -it <api-pod> -n healthcare -- curl redis:6379
```

### Insufficient resources

```bash
kubectl describe node | grep -A 10 "Allocated resources"
# Reduce resource requests in deployment YAML
```

### TLS certificate not issuing

```bash
kubectl describe certificate -n healthcare
kubectl get orders,challenges -n healthcare  # Check cert-manager logs
```

---

*Next: [Monitoring](monitoring.md) | [Troubleshooting](troubleshooting.md)*