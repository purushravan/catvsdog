#!/bin/bash
# Deploy Cats vs Dogs Classifier to Kubernetes

set -e

echo "=== Deploying Cats vs Dogs Classifier to Kubernetes ==="
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to Kubernetes cluster"
    echo "Please start your cluster first (e.g., 'minikube start')"
    exit 1
fi

# Apply resources in order
echo "1. Creating namespace..."
kubectl apply -f k8s/namespace.yaml

echo "2. Creating ConfigMap..."
kubectl apply -f k8s/configmap.yaml

echo "3. Creating PersistentVolumeClaims..."
kubectl apply -f k8s/pvc.yaml

echo "4. Creating Deployment..."
kubectl apply -f k8s/deployment.yaml

echo "5. Creating Service..."
kubectl apply -f k8s/service.yaml

# Optional resources
read -p "Do you want to apply HPA (Horizontal Pod Autoscaler)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "6. Creating HPA..."
    kubectl apply -f k8s/hpa.yaml
fi

echo ""
echo "✓ Deployment complete!"
echo ""
echo "Checking deployment status..."
kubectl get all -n catvsdog

echo ""
echo "Useful commands:"
echo "  - Check pods: kubectl get pods -n catvsdog"
echo "  - View logs: kubectl logs -n catvsdog -l app=catvsdog-api -f"
echo "  - Port forward: kubectl port-forward -n catvsdog service/catvsdog-api-service 8001:8001"
echo "  - Delete all: kubectl delete namespace catvsdog"
