# Docker Setup - Cats vs Dogs Classifier

## Problem Solved

The Docker build was failing due to a **Python version incompatibility**:
- Requirements file needed Python 3.11+ (for `contourpy==1.3.3`)
- Dockerfile was using Python 3.10

**Fix Applied:** Updated both Dockerfiles to use `python:3.11-slim`

## Quick Start

### Option 1: Using the Build Script (Easiest)

```bash
# Make script executable
chmod +x docker-build.sh

# Fast build (API only, ~5-10 minutes)
./docker-build.sh simple

# Full build (all features, ~20-30 minutes)
./docker-build.sh full
```

### Option 2: Using Docker Compose

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f catvsdog-api

# Stop services
docker-compose down
```

### Option 3: Manual Docker Commands

**Simple Version (Recommended for API deployment):**
```bash
docker build -f Dockerfile.simple -t catvsdog-classifier:simple .
docker run -d -p 8001:8001 --name catvsdog-api catvsdog-classifier:simple
```

**Full Version (All dependencies):**
```bash
docker build -t catvsdog-classifier:latest .
docker run -d -p 8001:8001 --name catvsdog-api catvsdog-classifier:latest
```

## Accessing the Application

Once running, access at:
- **Web UI**: http://localhost:8001
- **Health Check**: http://localhost:8001/health
- **API Docs**: http://localhost:8001/docs

## File Structure

```
.
├── Dockerfile              # Full build with all dependencies
├── Dockerfile.simple       # Lightweight API-only build
├── docker-compose.yml      # Multi-service orchestration
├── .dockerignore          # Excludes unnecessary files
├── docker-build.sh         # Helper build script
├── DOCKER_INSTRUCTIONS.md  # Detailed usage guide
├── DOCKER_TROUBLESHOOTING.md  # Common issues and solutions
└── requirements/
    ├── requirements.txt       # Full dependencies (190 packages)
    └── api_requirements.txt   # Minimal API dependencies (11 packages)
```

## Choosing the Right Dockerfile

| Feature | Dockerfile (Full) | Dockerfile.simple |
|---------|------------------|-------------------|
| Build Time | 20-30 min | 5-10 min |
| Image Size | ~3-4 GB | ~1.5-2 GB |
| Dependencies | 190 packages | 11 packages |
| Model Training | ✅ Yes | ❌ No |
| API Serving | ✅ Yes | ✅ Yes |
| MLflow | ✅ Yes | ❌ No |
| DVC | ✅ Yes | ❌ No |
| **Use Case** | Development & Training | Production API |

## Common Commands

```bash
# View running containers
docker ps

# View all containers
docker ps -a

# View logs
docker logs catvsdog-api
docker logs -f catvsdog-api  # Follow mode

# Stop container
docker stop catvsdog-api

# Start container
docker start catvsdog-api

# Restart container
docker restart catvsdog-api

# Remove container
docker rm catvsdog-api

# Remove image
docker rmi catvsdog-classifier:latest

# Execute bash inside container
docker exec -it catvsdog-api /bin/bash

# Test API from command line
curl http://localhost:8001/health
```

## Testing the API

### Using curl
```bash
curl -X POST "http://localhost:8001/predict/" \
  -F "file=@/path/to/your/image.jpg"
```

### Using Python
```python
import requests

url = "http://localhost:8001/predict/"
files = {"file": open("cat_image.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### Using the Web Interface
1. Open http://localhost:8001 in your browser
2. Upload an image
3. View prediction result

## Environment Variables

You can customize the container with environment variables:

```bash
docker run -d \
  -e MODEL_PATH=/custom/path \
  -e PYTHONUNBUFFERED=1 \
  -p 8001:8001 \
  catvsdog-classifier:latest
```

## Volume Mounts

Mount directories for easier updates:

```bash
docker run -d \
  -v $(pwd)/catvsdog_model/trained_models:/app/catvsdog_model/trained_models:ro \
  -v $(pwd)/catvsdog_model_api/app/static:/app/catvsdog_model_api/app/static \
  -p 8001:8001 \
  catvsdog-classifier:latest
```

## Troubleshooting

If you encounter issues, check [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md) for common problems and solutions.

### Quick Checks

1. **Container not starting:**
   ```bash
   docker logs catvsdog-api
   ```

2. **Port already in use:**
   ```bash
   # Use a different port
   docker run -d -p 9000:8001 catvsdog-classifier:latest
   ```

3. **Model not found:**
   ```bash
   # Check if model files exist
   ls -la catvsdog_model/trained_models/
   ```

4. **Clean rebuild:**
   ```bash
   docker build --no-cache -t catvsdog-classifier:latest .
   ```

## Production Deployment

For production, consider:

1. **Use the simple Dockerfile** for smaller image size
2. **Set up proper logging:**
   ```bash
   docker run -d \
     --log-driver=json-file \
     --log-opt max-size=10m \
     --log-opt max-file=3 \
     catvsdog-classifier:latest
   ```

3. **Add resource limits:**
   ```bash
   docker run -d \
     --memory="4g" \
     --cpus="2" \
     catvsdog-classifier:latest
   ```

4. **Use a reverse proxy** (nginx/traefik) for SSL/TLS
5. **Implement monitoring** (Prometheus, Grafana)
6. **Set up auto-restart:**
   ```bash
   docker run -d --restart=unless-stopped catvsdog-classifier:latest
   ```

## Pushing to Registry

To share your image:

```bash
# Tag for Docker Hub
docker tag catvsdog-classifier:latest yourusername/catvsdog-classifier:latest

# Login
docker login

# Push
docker push yourusername/catvsdog-classifier:latest

# Pull on another machine
docker pull yourusername/catvsdog-classifier:latest
```

## Next Steps

1. ✅ Build the Docker image
2. ✅ Test the API locally
3. Set up CI/CD pipeline
4. Deploy to cloud (AWS ECS, Google Cloud Run, Azure Container Instances)
5. Set up monitoring and logging
6. Implement auto-scaling

## Support

- Full instructions: [DOCKER_INSTRUCTIONS.md](DOCKER_INSTRUCTIONS.md)
- Troubleshooting: [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md)
- Docker docs: https://docs.docker.com/
