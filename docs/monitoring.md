# Monitoring & Observability

## Overview

The system provides comprehensive observability through structured logging, metrics, and health checks.

## Metrics Collection

### Prometheus Metrics Exposed

The FastAPI application exposes metrics at `/metrics` endpoint:

```python
# Instrumented endpoints
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
ELIGIBILITY_CHECKS = Counter('eligibility_checks_total', 'Total eligibility checks')
CACHE_HITS = Counter('cache_hits_total', 'Total cache hits')
CACHE_MISSES = Counter('cache_misses_total', 'Total cache misses')
```

### Key Metrics

| Metric | Type | Description | Target |
|--------|------|-------------|--------|
| `http_request_duration_seconds` | Histogram | Request latency by endpoint | p95 < 200ms |
| `eligibility_checks_total` | Counter | Number of eligibility checks | N/A |
| `eligibility_check_errors_total` | Counter | Errors during validation | < 1% |
| `cache_hit_ratio` | Gauge | Fraction of cache hits | > 80% |
| `rebate_calculations_total` | Counter | Number of calculations | N/A |
| `report_generations_total` | Counter | Reports generated | N/A |
| `agent_initializations_total` | Counter | Agent startup events | N/A |
| `mbs_items_loaded` | Gauge | Number of MBS items in cache | ≥ 20 |

## Structured Logging

### Log Format

All logs use JSON format for easy parsing:

```json
{
  "timestamp": "2026-04-26T14:31:29.123Z",
  "level": "INFO",
  "component": "EligibilityValidator",
  "message": "Eligibility check completed",
  "mbs_item": "13200",
  "eligible": true,
  "processing_time_ms": 127,
  "cache_hit": false,
  "user_id": "clinician_123"
}
```

### Log Levels

- `DEBUG`: Detailed internal state (development only)
- `INFO`: Normal operations (agent init, cache stats)
- `WARNING`: Recoverable issues (fallbacks, retries)
- `ERROR`: Failed requests, agent errors
- `CRITICAL`: System instability, cascading failures

### Log Fields

| Field | Component | Description |
|-------|-----------|-------------|
| `timestamp` | All | ISO 8601 UTC timestamp |
| `level` | All | Log severity |
| `component` | All | Agent or module name |
| `message` | All | Human-readable description |
| `mbs_item` | MBSDataFetcher | Item number looked up |
| `eligible` | EligibilityValidator | Eligibility result |
| `rebate_amount` | RebateCalculator | Calculated rebate |
| `processing_time_ms` | All | Duration in milliseconds |
| `cache_hit` | MBSDataFetcher | Whether item was cached |
| `error` | All | Error details (if applicable) |

## Health Checks

### Application Health

Three health endpoints available:

#### `GET /health`

Basic liveness check:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-26T14:31:29.123Z",
  "version": "1.0.0"
}
```

#### `GET /ready` (optional)

Readiness check verifies:
- MBS data loaded
- Cache responding
- Redis connection (if configured)

#### `GET /metrics`

Prometheus metrics scrape endpoint.

## Alerting Rules

### Recommended Alerts

```yaml
# In your Prometheus alertmanager config
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "High HTTP 5xx error rate"

- alert: SlowResponses
  expr: histogram_quantile(0.95, http_request_duration_seconds) > 0.5
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "95th percentile latency > 500ms"

- alert: CacheDegradation
  expr: rate(cache_misses_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) > 0.3
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "Cache hit ratio < 70%"

- alert: MbsDataStale
  expr: time() - mbs_last_updated_timestamp > 86400
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "MBS data older than 24 hours"
```

## Dashboards

### Grafana Dashboard (Recommended)

Import the following panels:

#### Overview Panel
- Request rate (RPS)
- Error rate (4xx/5xx)
- P95/P99 latency
- Cache hit ratio

#### Agent Performance
- MBS fetcher latency distribution
- Eligibility validator throughput
- Calculator execution time
- Report generation duration

#### System Resources
- CPU usage
- Memory consumption
- Redis memory usage
- Disk I/O (reports directory)

#### Business Metrics
- Top 10 MBS items requested
- Average rebate amount
- Eligibility rate
- Reports generated per day

### Sample Grafana JSON

Available in `docs/grafana-dashboard.json` (create separately).

## Distributed Tracing

### OpenTelemetry Integration

Enable tracing with:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Configure exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-agent",
    agent_port=6831,
)

# Set up tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
```

Then instrument agent methods:
```python
with tracer.start_as_current_span("validate_eligibility"):
    # validation logic
```

## Log Aggregation

### ELK Stack (Elasticsearch, Logstash, Kibana)

Configure Filebeat to ship logs:

```yaml
filebeat.inputs:
- type: log
  paths:
    - /var/log/medicare-checker/*.log
  json.keys_under_root: true
  json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "medicare-checker-%{+yyyy.MM.dd}"
```

### CloudWatch (AWS)

```python
import watchtower
import logging

handler = watchtower.CloudWatchLogHandler(
    boto3_session=boto3.Session(),
    log_group='medicare-checker',
    stream_name='api'
)
logger.addHandler(handler)
```

## Resource Monitoring

### Kubernetes

Deploy with resource limits:

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "512Mi"
  limits:
    cpu: "500m"
    memory: "1Gi"
```

Monitor with:
- Kubernetes Metrics Server
- kube-state-metrics
- Custom metrics via Prometheus adapter

### Docker

Use `docker stats` or cAdvisor for container metrics.

## Incident Response

### Runbook

When alerts fire:

1. **Check service health**: `curl http://<host>:8000/health`
2. **Review recent logs**: `journalctl -u medicare-checker -n 100`
3. **Check cache**: `redis-cli info stats | grep keyspace`
4. **Verify MBS data**: `python scripts/init_cache.py`
5. **Scale if needed**: `kubectl scale deployment/medicare-checker-api --replicas=5`
6. **Rollback if bug**: `kubectl rollout undo deployment/medicare-checker-api`

### Escalation Matrix

| Severity | Response Time | Notification | Runbook |
|----------|--------------|--------------|---------|
| P0 – System down | 15 min | PagerDuty (on-call) | Runbook A |
| P1 – Degraded | 1 hour | Slack #incidents | Runbook B |
| P2 – Warning | 4 hours | Email | Runbook C |
| P3 – Info | Daily | Jira ticket | N/A |

## Cost Monitoring

Track infrastructure spend:
- Pod resource utilization vs limits
- Redis memory usage (pay-per-GB)
- Network egress (if cloud)
- Storage (reports directory growth)

Set budgets and alerts in cloud provider console.

## Security Monitoring

### Audit Log Events

Log all:
- Agent initializations
- Eligibility checks (metadata only)
- Configuration changes
- Cache clear operations
- Report deletions

### Intrusion Detection

Consider Falco or open-source EDR for container runtime security.

## Maintenance Windows

Schedule regular:
- Dependency updates (weekly)
- Security scans (daily)
- Log rotation (daily)
- Cache pruning (weekly)
- Backup verification (monthly)

---

*For detailed configuration, see `/docs/operations` (to be created)*