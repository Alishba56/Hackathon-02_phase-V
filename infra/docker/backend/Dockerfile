# Dockerfile for FastAPI Backend
# Optimized for production deployment with Python 3.11
# Final image size: ~300MB (vs ~1GB with full Python image)

# ============================================================================
# Base Image: Python 3.11 Slim
# ============================================================================
# Using slim variant instead of full Python image reduces size significantly
# python:3.11-slim: ~120MB base vs python:3.11: ~900MB base
# Slim includes Python and essential libraries but excludes unnecessary packages
FROM python:3.11-slim

# Set working directory
# All subsequent commands execute in this directory
WORKDIR /app

# ============================================================================
# Python Environment Variables
# ============================================================================
# PYTHONDONTWRITEBYTECODE=1: Prevents Python from writing .pyc files
#   - Reduces image size and eliminates unnecessary disk I/O
#   - .pyc files are bytecode cache, not needed in containers (immutable)
#
# PYTHONUNBUFFERED=1: Forces Python output to be unbuffered
#   - Ensures logs appear immediately in kubectl logs
#   - Critical for debugging and monitoring in Kubernetes
#   - Without this, logs may be delayed or lost if container crashes
#
# PIP_NO_CACHE_DIR=1: Disables pip cache
#   - Reduces image size by not storing downloaded packages
#   - Cache is useless in containers (rebuilt from scratch each time)
#
# PIP_DISABLE_PIP_VERSION_CHECK=1: Disables pip version check
#   - Speeds up pip commands slightly
#   - Reduces unnecessary network calls during build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ============================================================================
# System Dependencies
# ============================================================================
# Install minimal system dependencies required for Python packages
# gcc: C compiler needed for building some Python packages (e.g., psycopg2)
# --no-install-recommends: Only install essential packages, not suggested ones
# rm -rf /var/lib/apt/lists/*: Clean up apt cache to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Python Dependencies
# ============================================================================
# Copy requirements file first to leverage Docker layer caching
# If requirements.txt hasn't changed, Docker reuses cached layer
# This is the most frequently cached layer (dependencies change less than code)
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: Don't cache downloaded packages (reduces image size)
# This installs FastAPI, uvicorn, psycopg2, cohere, and other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Application Code
# ============================================================================
# Copy application code last to maximize cache hits
# Source code changes frequently, so this layer is rebuilt often
# By copying code last, we avoid rebuilding dependency layers
COPY . .

# ============================================================================
# Security: Non-Root User
# ============================================================================
# Create non-root user for security best practices
# Running as root is a security risk in containers
# If container is compromised, attacker has limited privileges
# UID 1001 matches Kubernetes security context conventions
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
# All subsequent commands and container runtime use this user
USER appuser

# ============================================================================
# Port Configuration
# ============================================================================
# Expose port 8000 for FastAPI application
# This is documentation only; doesn't actually publish the port
# Kubernetes Service configuration determines actual port mapping
EXPOSE 8000

# ============================================================================
# Health Check
# ============================================================================
# Docker health check monitors container health
# Kubernetes uses readiness/liveness probes instead, but this provides fallback
# --interval=30s: Check every 30 seconds
# --timeout=3s: Fail if check takes longer than 3 seconds
# --start-period=5s: Grace period during startup (don't fail immediately)
# --retries=3: Mark unhealthy after 3 consecutive failures
# Checks /api/health endpoint (must be implemented in FastAPI app)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health', timeout=2)" || exit 1

# ============================================================================
# Application Startup
# ============================================================================
# Start FastAPI application with uvicorn ASGI server
# uvicorn: Production-ready ASGI server for async Python web apps
# main:app: Import 'app' from 'main.py' module
# --host 0.0.0.0: Listen on all network interfaces (required for Kubernetes)
# --port 8000: Listen on port 8000
#
# Production considerations (not included for simplicity):
# --workers: Number of worker processes (default: 1, increase for production)
# --log-level: Logging verbosity (info, warning, error)
# --access-log: Enable/disable access logs
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
