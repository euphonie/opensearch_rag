# Build stage
FROM python:3.10-slim as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive
ARG PIP_NO_CACHE_DIR=1
ARG PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Configure apt for reliability
RUN echo 'Acquire::Retries "3";' > /etc/apt/apt.conf.d/80-retries \
    && echo 'APT::Install-Recommends "false";' > /etc/apt/apt.conf.d/80-recommends \
    && echo 'APT::Get::Assume-Yes "true";' > /etc/apt/apt.conf.d/80-assume-yes \
    && echo 'Acquire::http::Pipeline-Depth "0";' > /etc/apt/apt.conf.d/80-pipeline-depth \
    && echo 'Acquire::http::No-Cache=True;' > /etc/apt/apt.conf.d/80-no-cache \
    && echo 'Acquire::BrokenProxy=true;' > /etc/apt/apt.conf.d/80-broken-proxy

# Install build dependencies with retry mechanism
RUN set -eux; \
    apt-get update -y; \
    for i in $(seq 1 3); do \
        apt-get install -y --no-install-recommends \
            build-essential \
            python3-dev \
        && break \
        || { echo "Retry attempt $i"; sleep 5; }; \
    done; \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies first
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application
COPY setup.py .
COPY src/ src/

# Install the application
RUN pip install --no-cache-dir -e .

# Runtime stage
FROM python:3.10-slim

# Set runtime arguments
ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Create directory for secrets
RUN mkdir -p /app/secrets

# Copy installed packages and application files
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /build/src /app/src
COPY --from=builder /build/setup.py /app/setup.py

# Set environment variables
ENV PYTHONPATH=/app/src:$PYTHONPATH \
    PYTHONUNBUFFERED=1 \
    APP_HOST=0.0.0.0 \
    APP_PORT=8081 \
    ENV_FILE=/app/secrets/.env

# Install runtime dependencies with retry mechanism
RUN set -eux; \
    apt-get update -y; \
    for i in $(seq 1 3); do \
        apt-get install -y --no-install-recommends \
            curl \
        && break \
        || { echo "Retry attempt $i"; sleep 5; }; \
    done; \
    rm -rf /var/lib/apt/lists/* && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${APP_PORT}/status || exit 1

# Add script to load environment variables
COPY --chown=appuser:appuser scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Command to run the application
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["app.app_rag"]
