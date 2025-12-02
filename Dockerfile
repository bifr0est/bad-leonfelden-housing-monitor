# Use official uv image with Python 3.13
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Set working directory
WORKDIR /app

# Copy project files and install dependencies
COPY pyproject.toml uv.lock README.md ./
COPY housing_monitor.py ./

# Install dependencies and create non-root user for security
RUN uv sync --frozen --no-dev && \
    adduser --disabled-password --gecos '' --uid 1000 monitor && \
    chown -R monitor:monitor /app
USER monitor

# Create volume for persistent state
VOLUME ["/app/data"]

# Environment variables with defaults
ENV NOTIFICATION_METHOD=telegram
ENV CHECK_INTERVAL=30
ENV STATE_FILE=/app/data/housing_monitor_state.json

# Health check
HEALTHCHECK --interval=5m --timeout=10s --start-period=30s --retries=3 \
    CMD uv run python -c "import os; exit(0 if os.path.exists(os.environ.get('STATE_FILE', '/app/data/housing_monitor_state.json')) else 1)"

# Default command
CMD ["uv", "run", "housing_monitor.py"]
