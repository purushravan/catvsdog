# Quick Start: ArgoCD CI/CD Pipeline

Get your GitOps pipeline running in 10 minutes!

## Prerequisites

- Kubernetes cluster running (minikube, kind, or cloud)
- kubectl configured
- Git repository access

## Step 1: Install ArgoCD (2 minutes)

```bash
# Run the install script
./argocd/install-argocd.sh

# Wait for pods to be ready
kubectl get pods -n argocd -w
```

## Step 2: Access ArgoCD UI (1 minute)

```bash
# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
echo

# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Open https://localhost:8080
- Username: `admin`
- Password: (from above command)

## Step 3: Deploy Application (1 minute)

```bash
# Deploy to development
kubectl apply -f argocd/application-dev.yaml

# Or deploy to production
kubectl apply -f argocd/application-prod.yaml
```

## Step 4: Setup GitHub Actions (3 minutes)

### A. Generate ArgoCD Token

```bash
# Install ArgoCD CLI (macOS M3/Apple Silicon)
brew install argocd

# Login (use --insecure for local development)
argocd login localhost:8080 --insecure

# Generate token
argocd account generate-token --account admin
```

### B. Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
1. **ARGOCD_SERVER**: `localhost:8080` (or your server URL)
2. **ARGOCD_AUTH_TOKEN**: (token from previous step)

## Step 5: Update Image Registry (2 minutes)

Edit [k8s/deployment.yaml](k8s/deployment.yaml):

```yaml
spec:
  containers:
  - name: catvsdog-api
    image: ghcr.io/purushravan/catvsdog/catvsdog-classifier:latest
    imagePullPolicy: Always
```

## Step 6: Test the Pipeline (1 minute)

```bash
# Make a change
echo "# Testing CI/CD" >> README.md

# Commit and push
git add .
git commit -m "test: trigger CI/CD pipeline"
git push origin main
```

## Verify Deployment

### GitHub Actions

Check: https://github.com/purushravan/catvsdog/actions

### ArgoCD UI

1. Open https://localhost:8080
2. Click on your application
3. Watch the sync status

### Kubernetes

```bash
# Watch pods
kubectl get pods -n catvsdog-prod -w

# Check deployment
kubectl get deploy -n catvsdog-prod

# View application logs
kubectl logs -f -n catvsdog-prod -l app=catvsdog-api
```

## Architecture Flow

```
Git Push → GitHub Actions → Build Image → Push to Registry
                ↓
         Update k8s/deployment.yaml
                ↓
         ArgoCD Detects Change
                ↓
         Deploy to Kubernetes
```

## Common Commands

```bash
# View app status
argocd app get catvsdog-prod

# Manual sync
argocd app sync catvsdog-prod

# Rollback
argocd app rollback catvsdog-prod

# View history
argocd app history catvsdog-prod

# Delete app
argocd app delete catvsdog-prod
```

## Troubleshooting

### Image Pull Error

```bash
# Create registry secret
kubectl create secret docker-registry regcred \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_TOKEN \
  -n catvsdog-prod

# Update deployment to use it
# Add under spec.template.spec:
imagePullSecrets:
- name: regcred
```

### Application OutOfSync

```bash
# Force sync
argocd app sync catvsdog-prod --force

# Hard refresh
argocd app get catvsdog-prod --hard-refresh
```

### Pipeline Not Triggering

Check:
1. GitHub Actions enabled in repo settings
2. Workflow file in `.github/workflows/` directory
3. Push to correct branch (main/develop)
4. No syntax errors in workflow file

## Next Steps

- Set up staging environment
- Configure Slack notifications
- Add security scanning
- Implement canary deployments
- Configure monitoring alerts

For detailed documentation, see [ARGOCD_SETUP_GUIDE.md](ARGOCD_SETUP_GUIDE.md)
