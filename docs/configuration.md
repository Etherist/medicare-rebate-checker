# Configuration

This page describes all configuration options for the Medicare Rebate Checker.

## Configuration Methods

Configuration can be provided via:
1. **Environment variables** (preferred for production)
2. **`.env` file** (local development)
3. **Python settings module** (advanced)

## Environment Variables

### Application

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `APP_ENV` | str | `development` | Environment: `development`, `staging`, `production` |
| `LOG_LEVEL` | str | `INFO` | Python logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |
| `LOG_FORMAT` | str | `json` | Log format: `json` (structured) or `text` |
| `CACHE_TTL` | int | `3600` | Cache TTL in seconds (default: 1 hour) |

### MBS Data

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MBS_CACHE_ENABLED` | bool | `true` | Enable in-memory caching of MBS items |
| `MBS_CACHE_BACKEND` | str | `memory` | Cache backend: `memory`, `redis` |
| `MBS_CACHE_REDIS_URL` | str | `redis://localhost:6379` | Redis connection string (when using Redis) |
| `MBS_UPDATE_FREQUENCY` | str | `daily` | Frequency of MBS data refresh: `hourly`, `daily`, `weekly` |
| `MBS_DATA_PATH` | str | `src/data/mbs_items.json` | Path to local MBS JSON file |

### Security

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RATE_LIMIT_ENABLED` | bool | `true` | Enable rate limiting |
| `RATE_LIMIT_REQUESTS` | int | `100` | Max requests per window |
| `RATE_LIMIT_WINDOW` | int | `3600` | Window in seconds (default: 1 hour) |
| `INPUT_SANITIZATION_LEVEL` | str | `strict` | Input validation strictness: `strict`, `moderate`, `lenient` |

### Reporting

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `REPORT_STORAGE_PATH` | str | `reports` | Directory to save generated reports |
| `REPORT_FORMATS` | str | `markdown,json` | Comma-separated list of enabled formats |
| `REPORT_RETENTION_DAYS` | int | `30` | Days to keep reports before auto-deletion |
| `REPORT_INCLUDE_METADATA` | bool | `true` | Include processing metadata in reports |

### External APIs (Optional)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MBS_API_ENDPOINT` | str | — | Official MBS Online API base URL |
| `MBS_API_KEY` | str | — | API key for MBS Online (if using live data) |
| `MBS_API_TIMEOUT` | int | `10` | Timeout for external API calls (seconds) |

### Observability

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | str | — | OpenTelemetry collector endpoint |
| `PROMETHEUS_METRICS_ENABLED` | bool | `true` | Expose /metrics endpoint |
| `SENTRY_DSN` | str | — | Sentry DSN for error tracking |
| `SENTRY_TRACES_SAMPLE_RATE` | float | `0.1` | 10% of transactions traced |

## .env File Example

```bash
# .env
APP_ENV=production
LOG_LEVEL=WARNING
CACHE_TTL=7200

# Redis cache
MBS_CACHE_ENABLED=true
MBS_CACHE_BACKEND=redis
MBS_CACHE_REDIS_URL=redis://:password@redis:6379/0

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Reports
REPORT_STORAGE_PATH=/var/lib/medicare/reports
REPORT_RETENTION_DAYS=90

# Observability
PROMETHEUS_METRICS_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

**Important**: Add `.env` to `.gitignore` — never commit secrets.

## Configuration hierarchies

Settings are loaded in this order (later overrides earlier):
1. Defaults (in code)
2. `.env` file (if present)
3. Environment variables

## Advanced Configuration

### Custom Cache Backend

Implement `CacheBackend` protocol:

```python
from typing import Protocol
from typing import Optional

class CacheBackend(Protocol):
    def get(self, key: str) -> Optional[Any]: ...
    def set(self, key: str, value: Any, ttl: int) -> None: ...
    def delete(self, key: str) -> None: ...
    def clear(self) -> None: ...

# Set environment
export MBS_CACHE_BACKEND=myapp.cache.RedisBackend
```

### Custom Validation Rules

Place custom rule modules in `src/agents/rules/` and set:

```bash
VALIDATION_RULE_MODULES=custom_rules.age,custom_rules.overseas
```

### Report Templates

Override templates by placing Jinja2 templates in `templates/`:

```
templates/
├── report.md.j2      # Markdown template
└── report.html.j2   # HTML template
```

Then set:
```bash
REPORT_TEMPLATE_DIR=/app/templates
```

## Validation

Validate your configuration:

```bash
python -c "from utils.config import settings; print(settings.model_dump())"
```

Or with Pydantic:

```python
from utils.config import Settings
s = Settings()  # Raises error if invalid
print(s.dict())
```

## Troubleshooting

### Common Issues

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Redis connection refused | `MBS_CACHE_REDIS_URL` wrong or Redis not running | `docker-compose up redis` or fix URL |
| Reports not saving | `REPORT_STORAGE_PATH` not writable | `chmod 755 reports/` or choose different path |
| High latency | `CACHE_TTL` too low or cache disabled | Enable cache, increase TTL |
| Import errors | Missing `PYTHONPATH` | `export PYTHONPATH=/app/src:$PYTHONPATH` |

---

*See also: [Security](security.md) | [Monitoring](monitoring.md) | [Deployment](deployment.md)*