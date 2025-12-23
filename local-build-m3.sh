#!/bin/bash
# Quick build script for macOS M3 (Apple Silicon)

set -e

echo "🍎 Building Docker image for macOS M3 (ARM64)..."
echo ""

# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Check if we're on ARM64
ARCH=$(uname -m)
if [ "$ARCH" != "arm64" ]; then
    echo "⚠️  Warning: This script is optimized for ARM64 (M1/M2/M3)"
    echo "Current architecture: $ARCH"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build for ARM64 (local M3)
echo "📦 Building image for ARM64..."
docker build \
    --platform linux/arm64 \
    -t catvsdog-classifier:simple \
    -t catvsdog-classifier:latest \
    -f Dockerfile \
    .

echo ""
echo "✅ Build complete!"
echo ""
echo "Image tags:"
docker images | grep catvsdog-classifier | head -2

echo ""
echo "🧪 Test the image:"
echo "   docker run -p 8001:8001 catvsdog-classifier:simple"
echo ""
echo "📝 Check health:"
echo "   curl http://localhost:8001/health"
echo ""
echo "🚀 Deploy to Kubernetes:"
echo "   kubectl rollout restart deployment/dev-catvsdog-api -n catvsdog-dev"
