# ArgoCD CI/CD Pipeline Setup Guide

This guide will help you set up a complete GitOps-based CI/CD pipeline using ArgoCD for the CatVsDog ML project.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   GitHub    │─────▶│ GitHub       │─────▶│   Docker    │
│  (Code Push)│      │ Actions (CI) │      │   Registry  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐      ┌─────────────┐
                     │ Update K8s   │      │   ArgoCD    │
                     │  Manifests   │─────▶│    (CD)     │
                     └──────────────┘      └─────────────┘
                                                  │
                                                  ▼
                                           ┌─────────────┐
                                           │ Kubernetes  │
                                           │   Cluster   │
                                           └─────────────┘
```

## Prerequisites

1. **Kubernetes cluster** (minikube, kind, or cloud provider)
2. **kubectl** installed and configured
3. **GitHub account** with access to your repository
4. **Docker** for local testing (optional)

## Step 1: Install ArgoCD

### Quick Installation

```bash
# Run the installation script
./argocd/install-argocd.sh
```

### Manual Installation

```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods to be ready
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd
```

## Step 2: Access ArgoCD UI

### Get Admin Password

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### Port Forward to Access UI

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Open browser at: https://localhost:8080
- Username: `admin`
- Password: (from command above)

## Step 3: Install ArgoCD CLI (Optional but Recommended)

```bash
# macOS
brew install argocd

# Linux
curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x /usr/local/bin/argocd

# Login
argocd login localhost:8080
```

## Step 4: Deploy Applications to ArgoCD

```bash
# Deploy main application
kubectl apply -f argocd/application.yaml

# Deploy monitoring stack
kubectl apply -f argocd/application-monitoring.yaml

# Check status
kubectl get applications -n argocd
```

## Step 5: Configure GitHub Actions

### Required Secrets

Add these secrets in GitHub repository settings (Settings → Secrets and variables → Actions):

1. **ARGOCD_SERVER**
   - Value: Your ArgoCD server URL (e.g., `localhost:8080` or public URL)

2. **ARGOCD_AUTH_TOKEN**
   ```bash
   # Generate token
   argocd account generate-token --account admin
   ```

3. **GitHub Container Registry** (automatically available as `GITHUB_TOKEN`)

### Update Image Registry (if using private registry)

If using a different container registry (Docker Hub, ECR, GCR):

1. Update `.github/workflows/ci-cd.yaml`:
   ```yaml
   env:
     REGISTRY: docker.io  # or your registry
     IMAGE_NAME: your-username/catvsdog-classifier
   ```

2. Add registry credentials as secrets:
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`

## Step 6: Update Kubernetes Manifests

Update the deployment to use the container registry:

```yaml
# k8s/deployment.yaml
spec:
  containers:
  - name: catvsdog-api
    image: ghcr.io/purushravan/catvsdog/catvsdog-classifier:latest
    imagePullPolicy: Always
```

## Step 7: Test the Pipeline

### Trigger CI/CD Pipeline

```bash
# Make a change to your code
echo "# Testing CI/CD" >> README.md

# Commit and push
git add .
git commit -m "test: trigger CI/CD pipeline"
git push origin main
```

### Monitor Pipeline

1. **GitHub Actions**: Check the Actions tab in your repository
2. **ArgoCD UI**: Watch the sync status in ArgoCD dashboard
3. **Kubernetes**: Monitor deployment progress

```bash
# Watch pods
kubectl get pods -n catvsdog -w

# Check application status in ArgoCD
argocd app get catvsdog-app

# View sync history
argocd app history catvsdog-app
```

## CI/CD Pipeline Flow

### 1. **CI Stage** (GitHub Actions)

When you push to `main` or `develop`:

1. **Test Job**: Runs unit tests and generates coverage
2. **Build Job**: Builds Docker image and pushes to registry
3. **Update Manifests Job**: Updates `k8s/deployment.yaml` with new image tag
4. **Deploy Job**: Triggers ArgoCD sync (optional)

### 2. **CD Stage** (ArgoCD)

ArgoCD continuously monitors your Git repository:

1. **Detect Changes**: ArgoCD detects changes in `k8s/` directory
2. **Auto Sync**: Automatically syncs changes to Kubernetes (if enabled)
3. **Health Check**: Monitors deployment health
4. **Self-Heal**: Automatically fixes drift from desired state

## ArgoCD Features

### Auto-Sync

Automatically deploys when Git changes are detected:

```yaml
syncPolicy:
  automated:
    prune: true      # Delete resources not in Git
    selfHeal: true   # Revert manual changes
```

### Manual Sync

Disable auto-sync for manual control:

```bash
argocd app sync catvsdog-app
```

### Rollback

```bash
# View history
argocd app history catvsdog-app

# Rollback to specific revision
argocd app rollback catvsdog-app <revision-number>
```

### Diff

See what will change before syncing:

```bash
argocd app diff catvsdog-app
```

## Monitoring and Observability

### Application Health

ArgoCD monitors application health based on:
- Pod status
- Deployment rollout status
- Health checks (readiness/liveness probes)

### Sync Status

- **Synced**: Git state matches cluster state
- **OutOfSync**: Changes detected in Git
- **Unknown**: Unable to determine status

### Notifications

Configure notifications for deployment events:

```bash
# Install ArgoCD notifications
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj-labs/argocd-notifications/stable/manifests/install.yaml
```

## Troubleshooting

### ArgoCD Application Stuck in Progressing

```bash
# Check application details
argocd app get catvsdog-app

# View events
kubectl get events -n catvsdog --sort-by='.lastTimestamp'

# Check logs
kubectl logs -n catvsdog -l app=catvsdog-api
```

### Image Pull Errors

If using private registry:

```bash
# Create image pull secret
kubectl create secret docker-registry regcred \
  --docker-server=ghcr.io \
  --docker-username=$GITHUB_ACTOR \
  --docker-password=$GITHUB_TOKEN \
  -n catvsdog

# Update deployment to use secret
spec:
  imagePullSecrets:
  - name: regcred
```

### Sync Failed

```bash
# Get sync status
argocd app get catvsdog-app

# Force sync
argocd app sync catvsdog-app --force

# Hard refresh
argocd app get catvsdog-app --hard-refresh
```

### Manual Sync Timeout

```bash
# Increase timeout
argocd app sync catvsdog-app --timeout 600
```

## Best Practices

### 1. **GitOps Principles**

- All changes through Git (no kubectl apply)
- Git as single source of truth
- Automated synchronization

### 2. **Image Tagging Strategy**

- Use immutable tags (SHA-based)
- Avoid `latest` tag in production
- Tag with semantic versioning

### 3. **Environment Separation**

Create separate applications for each environment:

```yaml
# argocd/application-dev.yaml
spec:
  source:
    path: k8s/overlays/dev
  destination:
    namespace: catvsdog-dev

# argocd/application-prod.yaml
spec:
  source:
    path: k8s/overlays/prod
  destination:
    namespace: catvsdog-prod
```

### 4. **Secrets Management**

Never commit secrets to Git. Use:
- Sealed Secrets
- External Secrets Operator
- HashiCorp Vault

### 5. **Progressive Delivery**

Use ArgoCD Rollouts for:
- Blue/Green deployments
- Canary releases
- A/B testing

## Advanced Configuration

### Multi-Cluster Deployment

```bash
# Add another cluster
argocd cluster add <context-name>

# Deploy to multiple clusters
argocd app create catvsdog-prod \
  --dest-server https://production-cluster \
  --dest-namespace catvsdog
```

### App of Apps Pattern

Deploy multiple applications together:

```yaml
# argocd/app-of-apps.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: catvsdog-platform
spec:
  source:
    path: argocd/apps
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
```

## Cleanup

```bash
# Delete ArgoCD applications
kubectl delete -f argocd/application.yaml
kubectl delete -f argocd/application-monitoring.yaml

# Uninstall ArgoCD
kubectl delete namespace argocd
```

## Resources

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [GitOps Principles](https://www.gitops.tech/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Next Steps

1. Set up staging environment
2. Configure notifications (Slack, email)
3. Implement progressive delivery with Argo Rollouts
4. Add security scanning to CI pipeline
5. Set up disaster recovery procedures
