#!/bin/bash
# Script to install ArgoCD on Kubernetes cluster

set -e

echo "🚀 Installing ArgoCD..."

# Create ArgoCD namespace
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo "⏳ Waiting for ArgoCD to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

echo "✅ ArgoCD installed successfully!"
echo ""
echo "📝 Getting initial admin password..."
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
echo "ArgoCD Admin Password: $ARGOCD_PASSWORD"
echo ""
echo "🌐 To access ArgoCD UI:"
echo "1. Port forward: kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "2. Open browser: https://localhost:8080"
echo "3. Login with username 'admin' and the password above"
echo ""
echo "💡 Or use ArgoCD CLI:"
echo "brew install argocd"
echo "argocd login localhost:8080"
