# Multi-stage Dockerfile for GigBid Web Application (FastAPI + React 19)

# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /web
COPY apps/web/package*.json ./
RUN npm ci || npm install
COPY apps/web/ ./
RUN npm run build

# Stage 2: Python Backend Runtime
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e . \
    && pip install --no-cache-dir rank_bm25 scikit-learn pydantic fastapi uvicorn langgraph langchain mcp

# Copy full application code
COPY . .

# Copy compiled frontend assets from builder stage
COPY --from=frontend-builder /web/dist /app/apps/web/dist

ENV PYTHONPATH=/app
ENV MARKETPLACE_MODE=gigsim
ENV PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
