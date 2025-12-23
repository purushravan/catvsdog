# Dockerfile for Cats vs Dogs Image Classification
# Optimized for Apple Silicon (M1/M2/M3) but supports multi-platform builds
ARG TARGETPLATFORM
ARG BUILDPLATFORM
FROM --platform=${TARGETPLATFORM:-linux/arm64} python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Copy requirements first for better caching
COPY requirements/api-requirements.txt /app/requirements/api-requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements/api-requirements.txt

# Copy model package files
COPY catvsdog_model/ /app/catvsdog_model/

# Add model package to PYTHONPATH instead of installing
ENV PYTHONPATH=/app:$PYTHONPATH

# Copy API application
COPY catvsdog_model_api/ /app/catvsdog_model_api/

# Create directory for static files and uploads
RUN mkdir -p /app/catvsdog_model_api/app/static

# Expose port
EXPOSE 8001

# Change to API directory
WORKDIR /app/catvsdog_model_api

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
