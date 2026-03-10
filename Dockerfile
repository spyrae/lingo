FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies via pip from pyproject (builds wheel)
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy content data
COPY data/ ./data/

# Runtime environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATA_DIR=/app/data

# Health: compile sources to catch syntax errors
RUN python -m compileall -q src

# Entrypoint: run bot
CMD ["python", "-m", "lingo"]
