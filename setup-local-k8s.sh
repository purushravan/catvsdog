#!/bin/bash
# Setup script for local Kubernetes cluster with Minikube

set -e

echo "=== Cats vs Dogs Kubernetes Local Setup ==="
echo ""

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "Minikube not found. Installing..."
    brew install minikube
else
    echo "✓ Minikube is already installed"
fi

# Check if cluster is running
if minikube status &> /dev/null; then
    echo "✓ Minikube cluster is already running"
else
    echo "Starting Minikube cluster..."
    minikube start --driver=docker --cpus=4 --memory=8192
fi

# Verify cluster is accessible
echo ""
echo "Verifying cluster connectivity..."
kubectl cluster-info

# Build Docker image in Minikube's Docker environment
echo ""
echo "Building Docker image in Minikube environment..."
eval $(minikube docker-env)
docker build -t catvsdog-classifier:latest .

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Deploy the application: kubectl apply -f k8s/"
echo "2. Check status: kubectl get pods -n catvsdog"
echo "3. Access the app: minikube service -n catvsdog catvsdog-api-service"
echo ""
echo "To stop the cluster: minikube stop"
echo "To delete the cluster: minikube delete"
