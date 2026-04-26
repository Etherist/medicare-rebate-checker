# Testing Strategy

## Overview

The Medicare Rebate Checker employs a comprehensive, multi-layered testing strategy to ensure reliability and correctness.

## Test Pyramid

```
          E2E Tests (Streamlit/FastAPI)
           /                 \
      Integration Tests      Manual QA
        /           \
  Agent Tests      API Tests
     /   \           /
Unit Tests (Agents, Utils)
```

## Test Types

### 1. Unit Tests

**Location**: `tests/test_agents.py`, `tests/test_utils.py`

Unit tests focus on isolated components:
- Each agent tested independently with mocked dependencies
- Edge cases and error handling
- Mathematical properties (rebate calculations)

**Run**:
```bash
pytest tests/test_agents.py -v
```

**Coverage target**: 90%+ of agent code

### 2. Integration Tests

**Location**: `tests/test_integration.py`

Test agent interactions and full workflows:
- End-to-end eligibility checking
- Report generation pipeline
- Cache behavior across agents

**Run**:
```bash
pytest tests/test_integration.py -v
```

### 3. API Contract Tests

**Location**: `tests/test_api.py`

Validate FastAPI endpoints:
- Request/response schema validation
- Error handling (400, 404, 500)
- OpenAPI specification conformance

**Run**:
```bash
pytest tests/test_api.py -v
```

### 4. UI Tests (Streamlit)

**Location**: `tests/test_streamlit.py` (optional)

Smoke tests for Streamlit app:
- Page loads without errors
- Key widgets render correctly
- Form submission flows

**Requires**: `playwright` or `selenium` install

### 5. Performance Tests

**Location**: `tests/performance/`

Load testing with Locust:
- Simulation of concurrent users
- Response time thresholds (<200ms p95)
- Throughput measurement

**Run**:
```bash
locust -f tests/performance/locustfile.py --host http://localhost:8000
```

### 6. Property-Based Tests

**Location**: `tests/test_properties.py`

Using Hypothesis to generate random inputs:
- Rebate calculation invariants (rebate ≤ schedule fee)
- Percentage bounds (0% ≤ rebate% ≤ 100%)
- Idempotency of cache operations

## Running Tests

### Full Test Suite

```bash
# All tests with coverage
pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# Generate XML coverage for CI
pytest tests/ --cov=src --cov-report=xml:coverage.xml
```

### Specific Suites

```bash
# Unit only
make test-unit

# Integration only
make test-int

# Fast API checks
pytest tests/test_app.py -v
```

### Coverage Breakdown

| Module | Coverage | Target |
|--------|----------|--------|
| agents/ | TBD | 90% |
| app/cli.py | TBD | 85% |
| app/main.py | TBD | 90% |
| app/streamlit_app.py | TBD | 80% |

## CI/CD Integration

Tests run automatically on:
- Every push to `main`/`develop`
- Every pull request to `main`
- Nightly scheduled run (for flaky detection)

### GitHub Actions Workflow

1. Install dependencies (`uv sync`)
2. Run linting (ruff, black, isort)
3. Run type checking (mypy)
4. Run security scans (bandit, safety)
5. Execute test suite with coverage
6. Upload coverage to Codecov

## Test Data

### Fixtures

- `tests/conftest.py` – shared fixtures (sample MBS items, patients, agents)
- Mock MBS data for deterministic tests
- Factory pattern for generating test patients

### VCR Cassettes (Optional)

Record/replay external API interactions (if connecting to live MBS Online):
```bash
pip install vcrpy
```

## Mocking Strategy

- **External APIs**: Mocked using `unittest.mock`
- **File I/O**: Use temporary directories (`tmp_path` fixture)
- **Time**: Freeze time with `freezegun` for timestamp tests
- **Network**: Completely blocked in tests via `requests-mock`

## Flaky Test Handling

- Tests marked with `@pytest.mark.flaky` retry automatically
- Flaky tests investigated within 24h
- Temporary skips via `pytest.skip()` with issue reference

## Performance Benchmarks

### Baseline Metrics

| Operation | Target Latency | Max Latency |
|-----------|---------------|-------------|
| Fetch MBS item | < 50ms | 200ms |
| Validate eligibility | < 30ms | 100ms |
| Calculate rebate | < 10ms | 50ms |
| API request (full) | < 150ms | 500ms |

Benchmarks run in CI on each release.

## Property-Based Testing

Using Hypothesis to explore edge cases:

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=0, max_value=150))
def test_age_boundaries(age):
    patient = {'age': age, 'has_medicare_card': True}
    result = validator.validate_eligibility(mbs_item, patient)
    assert isinstance(result, dict)
```

## Mutation Testing

Periodically run mutation testing to ensure test effectiveness:

```bash
# Install cosmic-ray
cosmic-ray init cosmic-ray.yml
cosmic-ray execute
cosmic-ray report
```

## Debugging Failed Tests

```bash
# Verbose output
pytest tests/test_agents.py::TestMBSDataFetcher::test_fetch_mbs_item_success -vv

# Drop to debugger on failure
pytest --pdb tests/

# Show locals in tracebacks
pytest --tb=long --showlocals
```

## Adding New Tests

When adding a feature:
1. Write failing test first (TDD)
2. Implement minimal code to pass
3. Refactor while keeping tests green
4. Ensure coverage doesn't drop

Example:
```python
def test_new_feature():
    # Arrange
    agent = NewAgent()
    input = {...}
    expected = {...}

    # Act
    result = agent.process(input)

    # Assert
    assert result == expected
```