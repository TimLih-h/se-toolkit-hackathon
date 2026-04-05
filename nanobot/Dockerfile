# Stage 1: build
ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

# Copy entire workspace root
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY nanobot/ ./nanobot/
COPY mcp/ ./mcp/
COPY backend/ ./backend/
COPY qwen-code-api/ ./qwen-code-api/

# Sync dependencies
WORKDIR /app/nanobot
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# ---
# Stage 2: final image
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends gosu && rm -rf /var/lib/apt/lists/*

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy the entire workspace from builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Set PATH to include venv (workspace root venv)
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/nanobot

ENTRYPOINT ["python", "/app/nanobot/entrypoint.py"]
