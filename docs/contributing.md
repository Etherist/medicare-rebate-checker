# Contributing to Medicare Rebate Checker

Thank you for your interest in contributing! This document outlines the process for contributing to the project.

## Code of Conduct

By participating, you are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

Before creating a bug report:
- Check existing issues to avoid duplicates
- Ensure you're using the latest version
- Collect relevant information (logs, steps to reproduce, environment)

Bug reports should include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Screenshots if applicable

### Suggesting Features

Feature suggestions are welcome! Please:
- Open an issue with the "enhancement" label
- Describe the feature and its use case
- Consider alignment with project scope (agent-based healthcare systems)

### Pull Requests

1. **Fork the repository**

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   uv sync
   source .venv/bin/activate
   ```

4. **Make your changes**
   - Follow coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

5. **Run quality checks**
   ```bash
   make lint
   make test
   make typecheck
   ```

6. **Commit with conventional commits**
   ```bash
   git commit -m "feat: add new validation rule for overseas patients"
   git commit -m "fix: correct rebate calculation for after-hours services"
   ```

7. **Push and open PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Fill PR template completely
   - Link related issues
   - Request review from maintainers

## Development Setup

### Install Dependencies

```bash
uv sync --all-extras  # Includes dev dependencies
```

### Pre-commit Hooks

Install pre-commit hooks for automated checks:

```bash
pre-commit install
```

This runs on every commit and checks:
- Code formatting (black, isort)
- Linting (ruff)
- Type checking (mypy)
- Test execution (pytest)

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/test_agents.py -v

# Specific test
pytest tests/test_agents.py::TestMBSDataFetcher::test_fetch_mbs_item_success -v
```

### Building Documentation

```bash
mkdocs serve  # Live preview at http://localhost:8000
mkdocs build  # Static site to docs/_site
```

## Coding Standards

### Python Style

- **Formatter**: Black (line length 100)
- **Import sorting**: isort
- **Linter**: Ruff (configured in `ruff.toml`)
- **Type hints**: Required for all public functions/methods
- **Docstrings**: Google style

Example:
```python
def calculate_rebate(
    schedule_fee: float,
    rebate_percentage: float
) -> float:
    """Calculate Medicare rebate amount.

    Args:
        schedule_fee: Base fee from MBS schedule
        rebate_percentage: Rebate percentage (0-100)

    Returns:
        Rebate amount rounded to 2 decimal places

    Raises:
        ValueError: If percentage outside 0-100 range
    """
    if not 0 <= rebate_percentage <= 100:
        raise ValueError("Rebate percentage must be 0-100")
    return round(schedule_fee * rebate_percentage / 100, 2)
```

### Project Structure

```
medicare-rebate-checker/
├── src/
│   ├── agents/      # Agent implementations
│   ├── app/         # Interfaces (CLI, API, Streamlit)
│   └── utils/       # Shared utilities
├── tests/           # Mirror src/ structure
├── docs/            # MkDocs documentation
└── scripts/         # Maintenance scripts
```

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat: add support for telehealth rebates
fix: correct age restriction logic for 45-49 health assessment
docs: update API documentation with new endpoints
test: add coverage for after-hours multiplier calculations
```

## Review Process

### PR Requirements

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Code coverage ≥ 85%
- [ ] No linting errors (`make lint`)
- [ ] Type checking passes (`make typecheck`)
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (if user-facing change)
- [ ] Two approvals from maintainers

### Review Timeline

- Initial response within 48 hours
- Reviews aim for completion within 7 days
- Large changes may require extended discussion

## Adding New Agents

When adding a new agent type:

1. Create class in `src/agents/` following existing patterns
2. Implement required methods (see base classes)
3. Add unit tests in `tests/test_agents.py`
4. Integrate into all interfaces (CLI, API, Streamlit)
5. Document in `docs/agent_workflow.md`
6. Update README.md agent table

## Adding New MBS Items

To add MBS items:

1. Edit `src/data/mbs_items.json`
2. Follow existing JSON structure
3. Include item number (padded to 4 digits), description, schedule fee, rules
4. Add corresponding tests to validate behavior
5. Update documentation if adding new categories

## Release Process

Releases are automated via GitHub Actions:

1. Merge to `main` branch with semantic version tag
2. Create GitHub Release with changelog
3. Docker image published to registry
4. Helm chart updated (if applicable)
5. Documentation deployed to GitHub Pages

## Questions?

Open an issue or reach out to maintainers via GitHub Discussions.