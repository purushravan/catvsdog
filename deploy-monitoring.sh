#!/bin/bash

# Deploy Monitoring Stack for Cat vs Dog ML Model
# This script deploys Prometheus and Grafana to Kubernetes

set -e

echo "=========================================="
echo "Cat vs Dog - Monitoring Stack Deployment"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if Kubernetes cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

print_status "Connected to Kubernetes cluster"
echo ""

# Step 1: Create monitoring namespace
echo "Step 1: Creating monitoring namespace..."
kubectl apply -f k8s/monitoring-namespace.yaml
print_status "Monitoring namespace created"
echo ""

# Step 2: Deploy Prometheus RBAC
echo "Step 2: Deploying Prometheus RBAC..."
kubectl apply -f k8s/prometheus-rbac.yaml
print_status "Prometheus RBAC configured"
echo ""

# Step 3: Deploy Prometheus configuration
echo "Step 3: Deploying Prometheus configuration..."
kubectl apply -f k8s/prometheus-config.yaml
print_status "Prometheus configuration created"
echo ""

# Step 4: Deploy Prometheus
echo "Step 4: Deploying Prometheus..."
kubectl apply -f k8s/prometheus-deployment.yaml
print_status "Prometheus deployment created"
echo ""

# Wait for Prometheus to be ready
echo "Waiting for Prometheus to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/prometheus -n monitoring
print_status "Prometheus is ready"
echo ""

# Step 5: Deploy Grafana configuration
echo "Step 5: Deploying Grafana configuration..."
kubectl apply -f k8s/grafana-config.yaml
kubectl apply -f k8s/grafana-dashboard.yaml
print_status "Grafana configuration created"
echo ""

# Step 6: Deploy Grafana
echo "Step 6: Deploying Grafana..."
kubectl apply -f k8s/grafana-deployment.yaml
print_status "Grafana deployment created"
echo ""

# Wait for Grafana to be ready
echo "Waiting for Grafana to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/grafana -n monitoring
print_status "Grafana is ready"
echo ""

# Step 7: Verify application deployment
echo "Step 7: Checking application deployment..."
if kubectl get namespace catvsdog &> /dev/null; then
    if kubectl get deployment catvsdog-api -n catvsdog &> /dev/null; then
        print_status "Application deployment found"

        # Update deployment to ensure Prometheus annotations are present
        echo "Updating application deployment with monitoring annotations..."
        kubectl apply -f k8s/deployment.yaml
        kubectl rollout restart deployment/catvsdog-api -n catvsdog
        print_status "Application deployment updated"
    else
        print_warning "Application deployment not found. Deploy the application first:"
        echo "  kubectl apply -f k8s/namespace.yaml"
        echo "  kubectl apply -f k8s/configmap.yaml"
        echo "  kubectl apply -f k8s/pvc.yaml"
        echo "  kubectl apply -f k8s/deployment.yaml"
        echo "  kubectl apply -f k8s/service.yaml"
    fi
else
    print_warning "Application namespace 'catvsdog' not found."
    print_warning "Deploy the application before monitoring can collect metrics."
fi
echo ""

# Display deployment status
echo "=========================================="
echo "Deployment Status"
echo "=========================================="
echo ""

echo "Monitoring namespace pods:"
kubectl get pods -n monitoring
echo ""

if kubectl get namespace catvsdog &> /dev/null; then
    echo "Application namespace pods:"
    kubectl get pods -n catvsdog
    echo ""
fi

# Display access information
echo "=========================================="
echo "Access Information"
echo "=========================================="
echo ""

# Get node IP (works for Minikube, Kind, and cloud providers)
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    NODE_IP=$(minikube ip)
    print_status "Detected Minikube cluster"
elif kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}' &> /dev/null; then
    NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
else
    NODE_IP="<your-node-ip>"
    print_warning "Could not detect node IP automatically"
fi

echo "Prometheus:"
echo "  URL: http://${NODE_IP}:30090"
echo "  NodePort: 30090"
echo "  Port-forward: kubectl port-forward -n monitoring svc/prometheus 9090:9090"
echo ""

echo "Grafana:"
echo "  URL: http://${NODE_IP}:30300"
echo "  NodePort: 30300"
echo "  Port-forward: kubectl port-forward -n monitoring svc/grafana 3000:3000"
echo "  Default credentials:"
echo "    Username: admin"
echo "    Password: admin"
echo ""

if kubectl get svc catvsdog-api-service -n catvsdog &> /dev/null; then
    echo "Cat vs Dog API:"
    echo "  URL: http://${NODE_IP}:30001"
    echo "  Metrics endpoint: http://${NODE_IP}:30001/metrics"
    echo "  Port-forward: kubectl port-forward -n catvsdog svc/catvsdog-api-service 8001:8001"
    echo ""
fi

echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Access Prometheus at http://${NODE_IP}:30090"
echo "   - Check 'Status' → 'Targets' to verify scraping is working"
echo "   - View alerts at 'Alerts'"
echo ""
echo "2. Access Grafana at http://${NODE_IP}:30300"
echo "   - Login with admin/admin"
echo "   - Navigate to 'Dashboards' → 'Cat vs Dog ML Model Monitoring'"
echo ""
echo "3. Generate test traffic:"
echo "   - Access the API and make predictions"
echo "   - Watch metrics appear in Grafana dashboard"
echo ""
echo "4. For detailed documentation, see:"
echo "   - MONITORING_GUIDE.md"
echo ""

print_status "Monitoring stack deployment completed successfully!"
