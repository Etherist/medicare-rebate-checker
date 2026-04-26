# Multi-stage build for production-ready container
FROM python:3.12-slim-bookworm AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    # libpq-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install UV (modern Python package installer)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Copy dependency files
COPY pyproject.toml .

# Install Python dependencies (production only)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-editable

# --- Runtime layer ---
FROM python:3.12-slim-bookworm AS runtime

# Create non-root user
RUN useradd --create-home appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Ensure virtual environment is used
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set environment (default to production)
ENV APP_ENV=production
ENV LOG_LEVEL=INFO

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser scripts/ ./scripts/
COPY --chown=appuser:appuser data/ ./src/data/

# Create reports directory
RUN mkdir -p reports && chown appuser:appuser reports

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000   # FastAPI
EXPOSE 8501   # Streamlit

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "from src.app.main import app; print('OK')" || exit 1

# Default command (can be overridden)
CMD ["python", "-m", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]