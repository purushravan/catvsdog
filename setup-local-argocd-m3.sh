#!/bin/bash
# Complete ArgoCD setup for macOS M3

set -e

echo "🍎 ArgoCD Setup for macOS M3"
echo "=============================="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is for macOS only"
    exit 1
fi

# Check if running on ARM64
ARCH=$(uname -m)
if [ "$ARCH" != "arm64" ]; then
    echo "⚠️  Warning: Expected ARM64 (M1/M2/M3), found: $ARCH"
fi

echo "Step 1: Checking prerequisites..."
echo ""

# Check for kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Installing via Homebrew..."
    brew install kubectl
else
    echo "✅ kubectl found: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/"
    exit 1
else
    echo "✅ Docker found: $(docker --version)"
fi

# Check Kubernetes cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes cluster not accessible"
    echo ""
    echo "Please enable Kubernetes in Docker Desktop:"
    echo "1. Open Docker Desktop"
    echo "2. Go to Settings → Kubernetes"
    echo "3. Check 'Enable Kubernetes'"
    echo "4. Click 'Apply & Restart'"
    exit 1
else
    echo "✅ Kubernetes cluster accessible"
    kubectl get nodes
fi

echo ""
echo "Step 2: Installing ArgoCD..."
echo ""

# Create ArgoCD namespace
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

# Install ArgoCD
echo "📥 Downloading and installing ArgoCD..."
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for ArgoCD to be ready
echo "⏳ Waiting for ArgoCD pods to be ready (this may take 2-3 minutes)..."
kubectl wait --for=condition=available --timeout=300s \
    deployment/argocd-server -n argocd

echo ""
echo "✅ ArgoCD installed successfully!"
echo ""

# Install ArgoCD CLI if not present
# https://argo-cd.readthedocs.io/en/stable/cli_installation/
if ! command -v argocd &> /dev/null; then
    echo "📥 Installing ArgoCD CLI..."
    brew install argocd
else
    echo "✅ ArgoCD CLI already installed: $(argocd version --client --short 2>/dev/null || echo 'installed')"
fi

echo ""
echo "Step 3: Getting ArgoCD credentials..."
echo ""

# Get initial admin password
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 ArgoCD Login Credentials"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Username: admin"
echo "Password: $ARGOCD_PASSWORD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start port forwarding in background
echo "🌐 Starting ArgoCD UI port forward..."
kubectl port-forward svc/argocd-server -n argocd 8090:443 > /dev/null 2>&1 &
PORT_FORWARD_PID=$!

sleep 3

echo ""
echo "✅ ArgoCD UI is now accessible at: https://localhost:8090"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Open ArgoCD UI:"
echo "   open https://localhost:8090"
echo ""
echo "2. Login with the credentials above"
echo ""
echo "3. Build and deploy your application:"
echo "   ./local-build-m3.sh"
echo "   kubectl apply -f argocd/application-dev.yaml"
echo ""
echo "4. Or run the complete setup:"
echo "   ./argocd/setup-argocd.sh"
echo ""
echo "💡 Useful commands:"
echo "   argocd login localhost:8090 --insecure"
echo "   argocd app list"
echo "   argocd app get catvsdog-dev"
echo ""
echo "📝 To stop port forwarding:"
echo "   kill $PORT_FORWARD_PID"
echo ""
echo "📚 See MACOS_M3_SETUP.md for detailed documentation"
