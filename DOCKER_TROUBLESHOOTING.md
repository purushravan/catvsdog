# Docker Build Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Python Version Compatibility Error

**Error Message:**
```
ERROR: Ignored the following versions that require a different python version: 1.3.3 Requires-Python >=3.11
ERROR: Could not find a version that satisfies the requirement contourpy==1.3.3
```

**Cause:**
The `requirements.txt` contains packages (like `contourpy==1.3.3`) that require Python 3.11 or higher, but the Dockerfile was using Python 3.10.

**Solution:**
Updated the Dockerfile to use Python 3.11:
```dockerfile
FROM python:3.11-slim  # Changed from python:3.10-slim
```

### Issue 2: Build Takes Too Long

**Cause:**
The full `requirements.txt` has 190 packages including many training-related dependencies (MLflow, DVC, etc.) that aren't needed for just running the API.

**Solutions:**

#### Option 1: Use the Simple Dockerfile (Recommended for API only)
```bash
docker build -f Dockerfile.simple -t catvsdog-classifier:simple .
```

This dockerfile:
- Uses minimal dependencies (only 11 packages)
- Builds much faster (~5-10 minutes vs 20-30 minutes)
- Sufficient for running the prediction API
- Does NOT support model training

#### Option 2: Use the Full Dockerfile (For complete functionality)
```bash
docker build -t catvsdog-classifier:latest .
```

This dockerfile:
- Installs all 190 dependencies
- Takes longer to build
- Supports both training and API
- Needed if you want to train models inside the container

#### Option 3: Use api_requirements.txt
Create a minimal requirements file with only API dependencies:
```txt
requirements/api_requirements.txt
```

### Issue 3: Out of Disk Space

**Error:**
```
ERROR: failed to build: no space left on device
```

**Solutions:**
```bash
# Clean up Docker system
docker system prune -a

# Remove unused images
docker image prune -a

# Remove unused containers
docker container prune

# Check disk usage
docker system df
```

### Issue 4: Build Context Too Large

**Symptom:** Build takes forever to start (stuck at "transferring context")

**Cause:** Including large files/directories in the Docker build context

**Solution:**
Ensure `.dockerignore` is properly configured:
```bash
# Check what's being included
ls -lah

# Make sure .dockerignore excludes:
# - .git/
# - mlruns/
# - catvsdog_model/datasets/data/
# - *.ipynb
```

### Issue 5: Permission Denied on Static Files

**Error:**
```
Permission denied: '/app/catvsdog_model_api/app/static/'
```

**Solution:**
```bash
# On host machine, fix permissions
chmod -R 755 catvsdog_model_api/app/static

# Or in Dockerfile, add:
RUN chmod -R 777 /app/catvsdog_model_api/app/static
```

### Issue 6: Model File Not Found

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: '...catvsdog__model_output_v0.0.1.keras'
```

**Solution:**
1. Ensure model file exists:
   ```bash
   ls -la catvsdog_model/trained_models/
   ```

2. Check that model file isn't excluded in `.dockerignore`

3. Mount the model directory as a volume:
   ```bash
   docker run -v ./catvsdog_model/trained_models:/app/catvsdog_model/trained_models ...
   ```

### Issue 7: Health Check Failing

**Error:**
```
unhealthy: Health check failed
```

**Solutions:**
1. Check if the application started:
   ```bash
   docker logs catvsdog-api
   ```

2. Test health endpoint manually:
   ```bash
   docker exec catvsdog-api curl http://localhost:8001/health
   ```

3. Temporarily disable health check:
   ```dockerfile
   # Comment out HEALTHCHECK line in Dockerfile
   # HEALTHCHECK --interval=30s ...
   ```

## Quick Reference

### Fast Build (API Only)
```bash
./docker-build.sh simple
```

### Full Build (All Features)
```bash
./docker-build.sh full
```

### Check Build Progress
```bash
docker ps -a
docker logs -f <container-id>
```

### Debugging Inside Container
```bash
# Start container with bash
docker run -it catvsdog-classifier:latest /bin/bash

# Or exec into running container
docker exec -it catvsdog-api /bin/bash
```

### Clean Start
```bash
# Remove all containers and images
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi -f catvsdog-classifier:latest

# Rebuild
docker build --no-cache -t catvsdog-classifier:latest .
```

## Platform-Specific Issues

### macOS ARM (M1/M2/M3)
If you see warnings about platform compatibility:
```bash
# Build for ARM explicitly
docker build --platform linux/arm64 -t catvsdog-classifier:latest .

# Or for cross-platform
docker buildx build --platform linux/amd64,linux/arm64 -t catvsdog-classifier:latest .
```

### Windows
If you encounter path issues:
```bash
# Use PowerShell or WSL2
# Make sure Docker Desktop is running
# Use forward slashes in paths
```

## Performance Tips

1. **Use Docker BuildKit** (faster builds):
   ```bash
   export DOCKER_BUILDKIT=1
   docker build -t catvsdog-classifier:latest .
   ```

2. **Layer Caching**: Don't change `requirements.txt` unnecessarily - it's copied early for better caching

3. **Multi-stage Builds**: The full Dockerfile can be converted to multi-stage for smaller final images

4. **Pre-built Base Image**: Create a base image with common dependencies:
   ```dockerfile
   FROM python:3.11-slim as base
   RUN pip install tensorflow==2.16.1 fastapi==0.126.0
   # Then use FROM base in your main Dockerfile
   ```

## Getting Help

If you're still stuck:
1. Check the full build log: `cat /tmp/docker-build.log`
2. Verify Docker version: `docker --version` (needs 20.10+)
3. Check system resources: `docker system df`
4. Review container logs: `docker logs catvsdog-api`
