FROM python:3.11-slim

WORKDIR /app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies via pip from pyproject (builds wheel)
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "uv==0.4.23" && \
    uv pip install --no-cache-dir . --system

# Copy application sources and data
COPY src/ ./src/
COPY data/ ./data/

# Runtime environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health: simple command to compile sources
RUN python -m compileall -q src

# Entrypoint: run bot
CMD ["python", "-m", "lingo"]

