FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files and install dependencies
COPY pyproject.toml uv.lock README.md ./
COPY housing_monitor.py ./
RUN uv sync --frozen --no-dev

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --uid 1000 monitor
RUN chown -R monitor:monitor /app
USER monitor

# Create volume for persistent state
VOLUME ["/app/data"]

# Environment variables with defaults
ENV NOTIFICATION_METHOD=telegram
ENV CHECK_INTERVAL=30
ENV STATE_FILE=/app/data/housing_monitor_state.json

# Health check
HEALTHCHECK --interval=5m --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists(os.environ.get('STATE_FILE', '/app/data/housing_monitor_state.json')) else 1)"

# Default command
CMD ["uv", "run", "housing_monitor.py"]