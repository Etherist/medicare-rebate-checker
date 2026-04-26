# Development Guide

Comprehensive guide for contributors and maintainers.

## Prerequisites

- **Python**: 3.12+ (use pyenv or system)
- **Package manager**: UV (recommended) or pip
- **Git**: Latest version
- **Docker** (optional): For containerised development
- **kubectl** (optional): For Kubernetes testing

## Quick Start

### 1. Fork & Clone

```bash
git clone https://github.com/YOUR-USERNAME/medicare-rebate-checker.git
cd medicare-rebate-checker
git remote add upstream https://github.com/your-username/medicare-rebate-checker.git
```

### 2. Set Up Development Environment

```bash
# Using UV (recommended)
uv sync --all-extras

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Install pre-commit hooks
pre-commit install
```

### 3. Verify Installation

```bash
# Run tests
make test

# Run linting
make lint

# Start Streamlit app
make run-streamlit
```

## Project Structure

```
medicare-rebate-checker/
├── src/
│   ├── agents/           # Autonomous agents
│   │   ├── mbs_fetcher.py   # Fetches MBS item data
│   │   ├── validator.py     # Eligibility rules engine
│   │   ├── calculator.py    # Rebate calculations
│   │   └── reporter.py      # Report generation
│   ├── app/              # User interfaces
│   │   ├── cli.py          # Command-line interface
│   │   ├── main.py         # FastAPI REST API
│   │   └── streamlit_app.py  # Web UI
│   ├── data/
│   │   └── mbs_items.json   # MBS item definitions
│   └── utils/            # Shared utilities
│       ├── helpers.py
│       └── config.py
├── tests/                # Test suite
│   ├── test_agents.py   # Unit & integration agent tests
│   └── test_app.py      # Interface tests
├── docs/                 # MkDocs documentation
├── scripts/              # Maintenance scripts
├── k8s/                  # Kubernetes manifests
└── deploy/               # Deployment configs (future)
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout develop
git pull upstream develop
git checkout -b feature/your-feature-name
```

**Naming conventions**:
- `feature/agent-telescope` – New functionality
- `fix/rebate-rounding` – Bug fix
- `docs/api-update` – Documentation update
- `refactor/validator-cleanup` – Refactoring

### 2. Make Changes

Follow coding standards (see below). Write tests alongside code.

### 3. Run Quality Checks

```bash
# Auto-fix formatting
make format

# Check everything
make lint
make typecheck
make test

# Run security scan
make security
```

**Pre-commit** runs automatically on `git commit`. To bypass:
```bash
git commit --no-verify
```

### 4. Commit Changes

```bash
git add .
git commit -m "type: concise description"
```

Use [Conventional Commits](https://www.conventionalcommits.org/):

| Type | When to use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting (no code change) |
| `refactor` | Code restructuring |
| `test` | Add/update tests |
| `chore` | Maintenance tasks |

### 5. Push & Create PR

```bash
git push origin feature/your-feature-name
```

Open a PR against `develop` branch with:
- Clear description
- Linked issue (if applicable)
- Screenshots (for UI changes)
- Test evidence

### 6. Code Review

- Address reviewer comments
- Keep PR small (< 400 lines diff ideal)
- Squash commits before merging

### 7. Merge & Deploy

Maintainer merges PR. CI automatically:
- Runs tests on multiple Python versions
- Builds and pushes Docker image
- Deploys to staging (if configured)
- Generates documentation

## Coding Standards

### Python Style

```bash
# Format with black (line length 100)
black src/ tests/

# Sort imports
isort src/ tests/

# Lint with ruff
ruff check src/ tests/ --fix
```

**Key rules**:
- 100 character line length
- Double quotes for strings
- Type hints for all public functions
- Google-style docstrings
- No `print()` in library code (use `logging`)

Example function:

```python
def calculate_gap_fee(
    schedule_fee: float,
    rebate_amount: float
) -> float:
    """Calculate out-of-pocket gap fee.

    Args:
        schedule_fee: Total service fee from MBS
        rebate_amount: Medicare rebate amount

    Returns:
        Gap fee (patient responsibility), never negative

    Raises:
        ValueError: If schedule_fee negative
    """
    if schedule_fee < 0:
        raise ValueError("Schedule fee cannot be negative")
    gap = schedule_fee - rebate_amount
    return max(gap, 0.0)
```

### Agent Design Principles

When writing agents:

1. **Single Responsibility** – One job per agent
2. **Explicit interfaces** – Clear method signatures
3. **No side effects** – Pure functions where possible
4. **Observability** – Log key decisions
5. **Error handling** – Graceful degradation

Example pattern:

```python
class MyAgent:
    def __init__(self, config: Optional[Dict] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self._cache: Dict = {}

    def process(self, input_data: Dict) -> Dict:
        """Main processing method."""
        self.logger.info("Processing started", extra={"input": input_data})
        try:
            result = self._do_work(input_data)
            return result
        except Exception as e:
            self.logger.error("Processing failed", exc_info=True)
            raise

    def _do_work(self, data: Dict) -> Dict:
        """Internal implementation."""
        # Implementation here
        return {}
```

### Testing Philosophy

- **TDD preferred**: Write failing test first, then code
- **Arrange-Act-Assert** pattern
- **Fixtures** for common test data
- **Mocks** for external dependencies
- **Property-based tests** for numeric invariants

Example:

```python
def test_rebate_calculation_never_exceeds_schedule_fee():
    """Property: rebate <= schedule_fee."""
    for fee in [10.0, 50.0, 100.0, 1000.0]:
        for pct in [0, 50, 85, 100]:
            rebate = calculate_rebate(fee, pct)
            assert rebate <= fee + 1e-9  # floating point tolerance
```

## Debugging Tips

### Run in Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python src/app/cli.py --mbs-item 13200 --age 35 --has-medicare-card True
```

### Use Breakpoints

```python
import pdb; pdb.set_trace()  # Classic
# or
breakpoint()  # Python 3.7+
```

### Inspect Agent State

```python
from src.agents.mbs_fetcher import MBSDataFetcher
f = MBSDataFetcher()
print(f.get_cache_info())
```

### View Logs

```bash
# Docker
docker-compose logs -f api

# Kubernetes
kubectl logs -f deployment/medicare-checker-api -n healthcare -c api
```

## Adding New MBS Items

### JSON Format

Edit `src/data/mbs_items.json`:

```json
{
  "12345": {
    "item_number": "12345",
    "description": "New service description",
    "category": "New Category",
    "schedule_fee": 150.00,
    "rebate_percentage": 85,
    "rules": {
      "requires_referral": false,
      "age_restriction": "18-64",
      "medicare_card_required": true,
      "bulk_billing_eligible": true,
      "after_hours_multiplier": 1.0
    },
    "notes": "Optional detailed notes"
  }
}
```

### Validation

```bash
python scripts/validate_mbs_data.py  # Create this script
```

## Adding New Agent Types

1. Create `src/agents/your_agent.py`
2. Implement base interface methods
3. Add unit tests in `tests/test_agents.py`
4. Integrate into CLI/API/Streamlit
5. Document in `docs/agent_workflow.md`
6. Update README agent table

## Database Migrations (Future)

If adding database:
- Use Alembic for migrations
- Migration files in `migrations/versions/`
- Never modify production data without migration
- Test migrations on staging first

## Performance Optimization

### Profiling

```bash
# Line profiler
python -m line_profiler -r -f profiler_output.txt script.py

# Memory profiler
mprof run script.py
mprof plot
```

### Benchmarking

```bash
# Time a function
python -m timeit -s "from src.agents.calculator import RebateCalculator; c=RebateCalculator()" "c.calculate_rebate({'schedule_fee': 100.0, 'rebate_percentage': 85.0}, {}, {'eligible': True})"

# Locust load test
locust -f tests/performance/locustfile.py --host http://localhost:8000
```

## Common Pitfalls

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError` | Wrong PYTHONPATH | `export PYTHONPATH=/app/src:$PYTHONPATH` |
| Tests fail on CI only | OS-specific path separators | Use `pathlib.Path`, not string concat |
| `ValidationError` from Pydantic | Missing required field | Check request model definitions |
| High memory usage | Unbounded cache | Set `CACHE_TTL` or implement LRU eviction |
| Slow first request | Cold start loading MBS data | Pre-warm cache with `make init-cache` |

## Getting Help

- **Documentation**: `/docs` folder, MkDocs site
- **Issues**: Search existing GitHub issues
- **Discussions**: GitHub Discussions board
- **Chat**: Matrix room #medicare-checker (invite from README)

## Acknowledgements

This project follows best practices from:
- **12-Factor App** methodology
- **Python Packaging User Guide**
- **FastAPI official docs**
- **LangChain agent patterns**
- **Site Reliability Engineering** (Google)