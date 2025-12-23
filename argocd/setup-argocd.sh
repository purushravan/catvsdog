#!/bin/bash
# Complete ArgoCD setup script

set -e

echo "🔧 Setting up ArgoCD for CatVsDog Project..."
echo ""

# Step 1: Install ArgoCD
echo "Step 1: Installing ArgoCD..."
./argocd/install-argocd.sh

# Wait for user to access ArgoCD UI
echo ""
read -p "Press enter after you've accessed ArgoCD UI and are ready to continue..."

# Step 2: Deploy application
echo ""
echo "Step 2: Deploying CatVsDog application to ArgoCD..."
kubectl apply -f argocd/application.yaml
kubectl apply -f argocd/application-monitoring.yaml

echo ""
echo "✅ ArgoCD applications created!"
echo ""

# Step 3: Check application status
echo "Step 3: Checking application status..."
echo ""
kubectl get applications -n argocd

echo ""
echo "🎉 ArgoCD setup complete!"
echo ""
echo "Next steps:"
echo "1. Access ArgoCD UI: kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "2. View application: https://localhost:8080"
echo "3. Configure GitHub Actions secrets:"
echo "   - ARGOCD_SERVER: Your ArgoCD server URL"
echo "   - ARGOCD_AUTH_TOKEN: ArgoCD auth token"
echo "4. Push code changes to trigger CI/CD pipeline"
echo ""
echo "📚 To get ArgoCD auth token:"
echo "   argocd account generate-token --account admin"
