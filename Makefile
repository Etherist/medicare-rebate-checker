.PHONY: help install test lint typecheck format docs clean docker-build docker-run

# Default target
help:
	@echo "Medicare Rebate Checker - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install          Install dependencies with uv"
	@echo "  make sync            Sync dependencies (uv)"
	@echo ""
	@echo "Testing:"
	@echo "  make test            Run all tests"
	@echo "  make test-cov        Run tests with coverage report"
	@echo "  make test-unit       Run unit tests only"
	@echo "  make test-int        Run integration tests only"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            Run linters (ruff, black, isort)"
	@echo "  make typecheck       Run type checks (mypy)"
	@echo "  make format          Auto-format code (black, isort)"
	@echo "  make security        Run security scans"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs            Serve docs locally (http://localhost:8000)"
	@echo "  make docs-build      Build static docs to docs/_site"
	@echo ""
	@echo "Application:"
	@echo "  make run-cli         Run CLI with sample args"
	@echo "  make run-api         Start FastAPI server"
	@echo "  make run-streamlit   Start Streamlit web app"
	@echo ""
	@echo "Data & Cache:"
	@echo "  make init-cache      Initialize MBS data cache"
	@echo "  make clear-cache     Clear agent caches"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build    Build Docker image"
	@echo "  make docker-run      Run Docker container"
	@echo "  make docker-stop     Stop running container"
	@echo "  make docker-clean    Remove container & image"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           Remove generated files (cache, reports, __pycache__)"

# Installation
install:
	uv sync --all-extras

sync:
	uv sync

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html --cov-report=term

test-unit:
	pytest tests/test_agents.py -v

test-int:
	pytest tests/test_app.py -v

# Code Quality
lint:
	ruff check src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

typecheck:
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/
	isort src/ tests/

security:
	bandit -r src/ -llx
	safety check --full-report

# Documentation
docs:
	mkdocs serve

docs-build:
	mkdocs build

# Application
run-cli:
	python src/app/cli.py --mbs-item 13200 --age 35 --has-medicare-card True

run-api:
	uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

run-streamlit:
	streamlit run src/app/streamlit_app.py

# Data & Cache
init-cache:
	python scripts/init_cache.py

clear-cache:
	python -c "from src.agents.mbs_fetcher import MBSDataFetcher; MBSDataFetcher().clear_cache()"

# Docker
docker-build:
	docker build -t medicare-rebate-checker:latest .

docker-run:
	docker run -d --name medicare-checker -p 8000:8000 -p 8501:8501 medicare-rebate-checker:latest

docker-stop:
	docker stop medicare-checker && docker rm medicare-checker

docker-clean: docker-stop
	docker rmi medicare-rebate-checker:latest

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf reports/ coverage.xml .coverage htmlcov/ .pytest_cache/
	rm -rf docs/_site/
	rm -rf Medicare-Rebate-Eligibility-Checker.pdf 2>/dev/null || true