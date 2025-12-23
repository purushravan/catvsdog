# Docker Instructions for Cats vs Dogs Image Classifier

This guide explains how to build and run the Cats vs Dogs image classification application using Docker.

## Prerequisites

- Docker installed on your system (version 20.10+)
- Docker Compose installed (version 1.29+)
- At least 4GB of free disk space
- Trained model file in `catvsdog_model/trained_models/`

## Quick Start

### Option 1: Using Docker Compose (Recommended)

The easiest way to run the application with all services:

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build

# View logs
docker-compose logs -f catvsdog-api

# Stop all services
docker-compose down
```

### Option 2: Using Docker Commands

Build and run the API container manually:

```bash
# Build the Docker image
docker build -t catvsdog-classifier:latest .

# Run the container
docker run -d \
  --name catvsdog-api \
  -p 8001:8001 \
  -v $(pwd)/catvsdog_model/trained_models:/app/catvsdog_model/trained_models:ro \
  -v $(pwd)/catvsdog_model_api/app/static:/app/catvsdog_model_api/app/static \
  catvsdog-classifier:latest

# View logs
docker logs -f catvsdog-api

# Stop the container
docker stop catvsdog-api

# Remove the container
docker rm catvsdog-api
```

## Accessing the Application

Once the container is running:

- **Web UI**: http://localhost:8001
- **Health Check**: http://localhost:8001/health
- **API Docs**: http://localhost:8001/docs
- **MLflow UI** (if enabled): http://localhost:5000

## Docker Compose Services

The `docker-compose.yml` file includes two services:

### 1. catvsdog-api (Main Application)
- Port: 8001
- FastAPI web application for image classification
- Includes health checks and auto-restart

### 2. mlflow-server (Optional)
- Port: 5000
- MLflow tracking server for experiment tracking
- Comment out if not needed

## Configuration

### Environment Variables

You can customize the application by setting environment variables in `docker-compose.yml`:

```yaml
environment:
  - MODEL_PATH=/app/catvsdog_model/trained_models
  - PYTHONUNBUFFERED=1
```

### Volume Mounts

The following directories are mounted as volumes:

1. **Trained Models**: `./catvsdog_model/trained_models` (read-only)
   - Allows updating models without rebuilding the image

2. **Static Files**: `./catvsdog_model_api/app/static`
   - Stores uploaded images from the web interface

## Advanced Usage

### Building for Production

```bash
# Build with specific tags
docker build -t catvsdog-classifier:v0.0.1 -t catvsdog-classifier:latest .

# Build with no cache
docker build --no-cache -t catvsdog-classifier:latest .
```

### Running with Custom Settings

```bash
# Run with custom port
docker run -d -p 9000:8001 catvsdog-classifier:latest

# Run with environment variables
docker run -d \
  -e MODEL_PATH=/custom/path \
  -p 8001:8001 \
  catvsdog-classifier:latest

# Run with GPU support (requires nvidia-docker)
docker run -d \
  --gpus all \
  -p 8001:8001 \
  catvsdog-classifier:latest
```

### Inspecting the Container

```bash
# Execute bash inside the container
docker exec -it catvsdog-api bash

# Check container stats
docker stats catvsdog-api

# Inspect container details
docker inspect catvsdog-api
```

### Managing Docker Resources

```bash
# View all containers
docker ps -a

# View images
docker images

# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Clean up everything (use with caution!)
docker system prune -a
```

## Troubleshooting

### Container Won't Start

1. Check if the port is already in use:
   ```bash
   lsof -i :8001
   ```

2. View container logs:
   ```bash
   docker logs catvsdog-api
   ```

3. Ensure model file exists:
   ```bash
   ls -la catvsdog_model/trained_models/
   ```

### Health Check Failing

```bash
# Check health status
docker inspect --format='{{json .State.Health}}' catvsdog-api

# Test health endpoint manually
curl http://localhost:8001/health
```

### Memory Issues

```bash
# Increase Docker memory limit in Docker Desktop settings
# Or run with memory limits
docker run -d --memory="4g" -p 8001:8001 catvsdog-classifier:latest
```

### Permission Issues

If you encounter permission errors with volumes:

```bash
# On Linux/Mac, fix permissions
sudo chown -R $USER:$USER catvsdog_model_api/app/static
chmod -R 755 catvsdog_model_api/app/static
```

## Multi-Stage Build Explanation

The Dockerfile uses a multi-stage build approach:

1. **Stage 1 (builder)**:
   - Builds the Python package wheel
   - Compiles dependencies
   - Creates distribution files

2. **Stage 2 (runtime)**:
   - Lighter image with only runtime dependencies
   - Copies built wheels from stage 1
   - Installs the application

This approach reduces the final image size significantly.

## Testing the Deployment

```bash
# Test health endpoint
curl http://localhost:8001/health

# Test prediction with an image (replace with your image path)
curl -X POST "http://localhost:8001/predict/" \
  -F "file=@/path/to/cat_or_dog_image.jpg"

# Or use the web interface
open http://localhost:8001
```

## Updating the Application

### Update Model Without Rebuilding

Simply replace the model file in `catvsdog_model/trained_models/` and restart:

```bash
docker-compose restart catvsdog-api
```

### Update Code (Requires Rebuild)

```bash
# Rebuild and restart
docker-compose up -d --build

# Or with Docker commands
docker build -t catvsdog-classifier:latest .
docker stop catvsdog-api
docker rm catvsdog-api
docker run -d --name catvsdog-api -p 8001:8001 catvsdog-classifier:latest
```

## Deployment to Cloud

### Push to Docker Hub

```bash
# Tag the image
docker tag catvsdog-classifier:latest yourusername/catvsdog-classifier:latest

# Login to Docker Hub
docker login

# Push the image
docker push yourusername/catvsdog-classifier:latest
```

### Deploy to Production

For production deployment, consider:
- Using orchestration tools like Kubernetes or Docker Swarm
- Setting up proper logging and monitoring
- Implementing SSL/TLS certificates
- Using a reverse proxy (nginx/traefik)
- Implementing rate limiting and security measures

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [TensorFlow Docker Guide](https://www.tensorflow.org/install/docker)
