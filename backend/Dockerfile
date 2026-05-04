# Dockerfile
# Multi-stage build: builder installs deps, final image is lean.

# ── Stage 1: dependency builder ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# System deps for binary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --upgrade pip \
    && pip install --prefix=/install ".[rerank,logging]"


# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL maintainer="QuestionCraft Team"
LABEL version="3.0.0"

# Runtime system deps (libgomp for FAISS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app/ ./app/

# Persistent volumes for indexes and uploads
RUN mkdir -p /data/rag_index /data/uploads /data/temp \
    && chown -R appuser:appuser /app /data

USER appuser

# Environment defaults (override via docker-compose or k8s secrets)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    LOG_JSON=true \
    RAG_INDEX_DIR=/data/rag_index \
    UPLOAD_DIR=/data/uploads \
    TEMP_DIR=/data/temp

EXPOSE 8000

# Graceful shutdown: SIGTERM is forwarded to uvicorn
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--log-level", "warning", \
     "--no-access-log"]