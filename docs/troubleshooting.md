# Troubleshooting Guide

Common issues and their solutions.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Runtime Errors](#runtime-errors)
- [Performance Problems](#performance-problems)
- [Deployment Issues](#deployment-issues)
- [Data Issues](#data-issues)
- [Getting Help](#getting-help)

---

## Installation Issues

### `uv: command not found`

**Symptom**: Shell cannot find `uv` command.

**Cause**: UV not installed or not in PATH.

**Fix**:
```bash
# Install UV globally
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pipx
pipx install uv

# Verify
uv --version
```

### Virtual environment creation fails

**Symptom**: `python -m venv venv` or `uv venv` errors.

**Cause**: Python development headers missing.

**Fix (Ubuntu/Debian)**:
```bash
sudo apt install python3.12-venv python3.12-dev
```

**Fix (macOS)**:
```bash
brew install python@3.12
```

### Dependency resolution conflicts

**Symptom**: `uv sync` fails with version conflicts.

**Cause**: Pinned dependencies incompatible with platform.

**Fix**:
```bash
# Try relaxing constraints temporarily
uv sync --no-pin

# Or update requirements.txt
uv pip compile pyproject.toml -o requirements.txt

# If still failing, report issue with full error
```

---

## Runtime Errors

### `ModuleNotFoundError: No module named 'src'`

**Symptom**: Import errors when running scripts directly.

**Cause**: Python path does not include `src/`.

**Fix**:
```bash
# Run from project root
cd /path/to/medicare-rebate-checker

# Ensure PYTHONPATH includes src
export PYTHONPATH=/app/src:$PYTHONPATH

# Or use module execution
python -m src.app.cli --help
```

### `FileNotFoundError: MBS data file not found`

**Symptom**: `MBSDataFetcher` cannot locate JSON data.

**Cause**: Working directory wrong or file missing.

**Fix**:
```bash
# Check file exists
ls src/data/mbs_items.json

# Ensure you're in project root
pwd  # Should end in medicare-rebate-checker

# Override path if needed
export MBS_DATA_PATH=/full/path/to/mbs_items.json
```

### Redis connection refused

**Symptom**: `redis.exceptions.ConnectionError`.

**Cause**: Redis server not running or wrong URL.

**Fix**:
```bash
# Start Redis (Docker)
docker run -d -p 6379:6379 redis:alpine

# Or with docker-compose
docker-compose up redis

# Verify
redis-cli ping  # Should return PONG

# Update REDIS_URL if using password
export MBS_CACHE_REDIS_URL=redis://:password@localhost:6379
```

### Port already in use

**Symptom**: `OSError: [Errno 98] Address already in use`.

**Cause**: Another process using port 8000 or 8501.

**Fix**:
```bash
# Find process
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Or change port
export PORT=8080
```

### Rate limit exceeded

**Symptom**: HTTP 429 responses.

**Cause**: Too many requests in time window.

**Fix**:
- Wait for window to reset (default: 1 hour)
- Increase limits in `.env`:
  ```env
  RATE_LIMIT_REQUESTS=1000
  RATE_LIMIT_WINDOW=3600
  ```
- Disable for local dev:
  ```env
  RATE_LIMIT_ENABLED=false
  ```

---

## Performance Problems

### Slow first request

**Symptom**: First API call takes several seconds; subsequent calls fast.

**Cause**: Cold start loading MBS data into cache.

**Fix**:
```bash
# Warm cache at startup
python scripts/init_cache.py

# Or set CACHE_TTL longer
export CACHE_TTL=86400
```

### High memory usage

**Symptom**: Process consumes >1GB RAM.

**Cause**:
- Unbounded in-memory cache
- Large number of concurrent requests
- Memory leak in custom code

**Fix**:
```bash
# Set cache size limit (future enhancement)
export MAX_CACHE_ENTRIES=1000

# Use Redis backend instead of in-memory
export MBS_CACHE_BACKEND=redis

# Reduce worker count (if using gunicorn)
gunicorn --workers 2 ...
```

### Slow report generation

**Symptom**: Report generation takes >5 seconds.

**Cause**:
- Disk I/O contention (many reports in same directory)
- Large report files (include full item details)
- Synchronous file writes blocking

**Fix**:
```bash
# Use async report generation (if implemented)
# Or offload to background queue (Celery/RQ)

# Periodically clean old reports
find reports/ -type f -mtime +30 -delete

# Use faster disk (SSD) for reports
export REPORT_STORAGE_PATH=/tmp/reports
```

---

## Deployment Issues

### Pods in CrashLoopBackOff

**Symptom**: Kubernetes pod repeatedly crashes.

**Diagnosis**:
```bash
kubectl logs <pod-name> -n healthcare --previous  # Last crashed container logs
kubectl describe pod <pod-name> -n healthcare    # Events & reasons
```

Common fixes:
- Check `MEMORY` limits – increase if OOMKilled
- Verify `MBS_DATA_PATH` exists in image
- Ensure `src/` code copied correctly in Dockerfile

### 503 Service Unavailable

**Symptom**: Load balancer returns 503.

**Cause**:
- No ready pods (readiness probe failing)
- Ingress misconfiguration
- Service selector mismatch

**Fix**:
```bash
# Check pod status
kubectl get pods -n healthcare

# Check service
kubectl get svc -n healthcare

# Verify endpoints
kubectl get endpoints medicare-checker-api -n healthcare
```

### Certificate errors (HTTPS)

**Symptom**: Browser warns about certificate.

**Cause**:
- Self-signed cert not trusted
- cert-manager not configured
- DNS not pointing to cluster

**Fix**:
```bash
# Check certificate status
kubectl get certificates -n healthcare

# Reissue with Let's Encrypt (staging first)
kubectl annotate ingress medicare-checker-ingress \
  cert-manager.io/issuer=letsencrypt-staging \
  -n healthcare

# Or use self-signed for internal use
kubectl create certificate selfsigned-medicare \
  --cert=tls.crt --key=tls.key \
  --namespace=healthcare
```

---

## Data Issues

### MBS item not found

**Symptom**: API returns 404 for known item number.

**Cause**:
- Item number not in `mbs_items.json`
- Incorrect padding (use 4-digit format: `"0023"` not `"23"`)

**Fix**:
```bash
# Check JSON
grep -A 5 '"13200"' src/data/mbs_items.json

# Add missing item following schema

# Reload cache (agents use in-memory cache)
# Restart service or call fetcher.clear_cache()
```

### Incorrect rebate calculation

**Symptom**: Rebate amount differs from manual calculation.

**Diagnosis**:
1. Verify schedule fee in data: `fetch_mbs_item('13200')['schedule_fee']`
2. Check rebate percentage applied: Look in calculation output `rebate_percentage`
3. Confirm eligibility: `validate_eligibility()` result
4. Consider after-hours multiplier in item `rules`

If discrepancy persists:
- Open issue with item number, patient params, expected vs actual
- Include repr of `mbs_details` dict

### Stale MBS data

**Symptom**: Items out-of-date or missing new items.

**Fix**:
```bash
# Update from official source (requires credentials)
python scripts/scrape_mbs.py --output src/data/mbs_items.json

# Verify data
python scripts/validate_mbs_data.py

# Commit updated data with message "chore: update MBS items to Q2 2026"
```

---

## Testing Issues

### Tests pass locally but fail on CI

**Common causes**:
- Different Python versions (3.10 vs 3.12)
- Missing environment variables on CI
- Race conditions in parallel tests
- File path assumptions (use `pathlib`, not `os.getcwd()`)

**Fix**:
- Ensure `tox` runs successfully locally (`tox -e py312`)
- Use fixtures for temporary files (`tmp_path`)
- Avoid global state; reset between tests

### Coverage not uploading

**Symptom**: Codecov badge stays at 0%.

**Fix**:
- Ensure `coverage.xml` generated (`pytest --cov=src --cov-report=xml`)
- Check `codecov.yml` for paths to include/exclude
- Verify `CODECOV_TOKEN` set in GitHub secrets
- Upload step in workflow didn't fail

---

## Getting Help

### Self-Service

1. Check this troubleshooting guide
2. Search [GitHub Issues](https://github.com/your-username/medicare-rebate-checker/issues)
3. Review logs in `logs/` or `docker logs`
4. Run diagnostic script:
   ```bash
   python scripts/diagnose.py
   ```

### Ask the Community

- **GitHub Discussions**: For questions, ideas
- **GitHub Issues**: For bugs (include logs, version, repro steps)
- **Stack Overflow**: Tag with `medicare-rebate-checker`

### Provide Diagnostic Information

When asking for help, include:

```bash
# System info
python --version
uv --version
docker --version  # if using Docker

# Project info
git rev-parse HEAD
cat pyproject.toml | grep -A 5 "dependencies"

# Error output
# (paste full traceback, not just last line)

# Recent logs
tail -50 logs/app.log 2>/dev/null || docker logs medicare-checker-api
```

---

## Emergency Procedures

### System Unresponsive

1. **Stop accepting traffic** (disable load balancer)
2. **Access logs**: Determine cause (high CPU? memory? deadlock?)
3. **Rollback**: Deploy previous stable release
4. **Restore services**: Bring old version online
5. **Post-mortem**: Document root cause and fixes

### Corrupted Reports Directory

```bash
# Stop services
docker-compose down

# Backup current reports
tar czf reports-backup-$(date +%F).tar.gz reports/

# Clear potentially locked files
rm -rf reports/*

# Restart
docker-compose up -d
```

### Cache Poisoning

If cached MBS data corrupt:

```bash
# Clear all caches
docker-compose exec api python -c "from src.agents.mbs_fetcher import MBSDataFetcher; MBSDataFetcher().clear_cache()"

# Or delete Redis keys
redis-cli -u redis://:password@redis:6379 KEYS "*" | xargs redis-cli -u ... DEL

# Reload from source
python scripts/init_cache.py
```

---

## FAQ

**Q: Can I use this system for actual Medicare billing?**

A: This is a demonstration project. For production billing, integrate with official Medicare systems and consult billing experts.

**Q: Does it support telehealth items?**

A: Yes, items with `after_hours_multiplier` or telehealth-specific rules are handled. Add telehealth items to `mbs_items.json`.

**Q: How often is MBS data updated?**

A: Manual updates required. Subscribe to MBS Online updates and refresh quarterly.

**Q: Can I add my own private health insurer rules?**

A: Yes – extend `EligibilityValidator` with additional rule checks or create a new `PrivateHealthValidator` agent.

**Q: Is PHI stored anywhere?**

A: By default, no patient identifiers stored. Reports written to disk may contain PHI – secure appropriately.

---

*Last updated: April 2026*