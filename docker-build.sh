#!/bin/bash

# Docker Build Script for Cats vs Dogs Classifier
# Usage: ./docker-build.sh [simple|full]

set -e

MODE="${1:-full}"

echo "===================================="
echo "Cats vs Dogs Docker Build Script"
echo "===================================="
echo ""

if [ "$MODE" = "simple" ]; then
    echo "Building SIMPLE version (minimal dependencies, faster build)..."
    docker build -f Dockerfile.simple -t catvsdog-classifier:simple .
    echo ""
    echo "Build complete! Run with:"
    echo "  docker run -d -p 8001:8001 --name catvsdog-api catvsdog-classifier:simple"

elif [ "$MODE" = "full" ]; then
    echo "Building FULL version (all dependencies, slower build)..."
    docker build -t catvsdog-classifier:latest .
    echo ""
    echo "Build complete! Run with:"
    echo "  docker run -d -p 8001:8001 --name catvsdog-api catvsdog-classifier:latest"

else
    echo "Invalid mode: $MODE"
    echo "Usage: ./docker-build.sh [simple|full]"
    exit 1
fi

echo ""
echo "Or use docker-compose:"
echo "  docker-compose up -d"
echo ""
echo "Access the application at: http://localhost:8001"
