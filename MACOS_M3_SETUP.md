# macOS M3 (Apple Silicon) Setup Guide for ArgoCD CI/CD

This guide is optimized for macOS with Apple Silicon (M1/M2/M3 chips).

## Prerequisites for macOS M3

### 1. Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Required Tools

```bash
# Docker Desktop for Mac (with Kubernetes enabled)
brew install --cask docker

# Kubernetes CLI
brew install kubectl

# ArgoCD CLI
brew install argocd

# GitHub CLI (optional but helpful)
brew install gh

# Or use minikube if you prefer
# brew install minikube
```

### 3. Setup Local Kubernetes

#### Option A: Docker Desktop Kubernetes (Recommended for M3)

1. Open Docker Desktop
2. Go to Settings → Kubernetes
3. Check "Enable Kubernetes"
4. Click "Apply & Restart"
5. Wait for Kubernetes to start (green icon)

```bash
# Verify installation
kubectl cluster-info
kubectl get nodes
```

#### Option B: Minikube with ARM64 Support

```bash
# Install minikube
brew install minikube

# Start with ARM64 driver
minikube start --driver=docker --kubernetes-version=stable

# Verify
kubectl get nodes
```

## Quick Start for M3

### Step 1: Build Docker Image Locally (ARM64)

```bash
# Build for local testing on M3
docker build -t catvsdog-classifier:simple -f Dockerfile .

# Verify it works
docker run -p 8001:8001 catvsdog-classifier:simple

# Test the API
curl http://localhost:8001/health
```

### Step 2: Install ArgoCD

```bash
# Make script executable
chmod +x argocd/install-argocd.sh

# Run installation
./argocd/install-argocd.sh

# Wait for pods to be ready
kubectl wait --for=condition=available --timeout=300s \
  deployment/argocd-server -n argocd
```

### Step 3: Access ArgoCD UI

```bash
# Get the initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d && echo

# Port forward to access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Open in browser (Command+Click or copy)
echo "https://localhost:8080"
```

**Login credentials:**
- Username: `admin`
- Password: (from the command above)

### Step 4: Load Docker Image into Kubernetes

Since you're using local Kubernetes, you need to make your Docker image available:

#### For Docker Desktop Kubernetes:

```bash
# The image is already available since Docker Desktop shares with K8s
docker images | grep catvsdog-classifier
```

#### For Minikube:

```bash
# Point Docker to minikube's Docker daemon
eval $(minikube docker-env)

# Build image in minikube
docker build -t catvsdog-classifier:simple -f Dockerfile .

# Verify
docker images | grep catvsdog-classifier

# When done, reset to host Docker
eval $(minikube docker-env -u)
```

### Step 5: Deploy Application

```bash
# Deploy to development environment
kubectl apply -f argocd/application-dev.yaml

# Check status
kubectl get applications -n argocd

# Watch the deployment
kubectl get pods -n catvsdog-dev -w
```

### Step 6: Setup GitHub Container Registry (for CI/CD)

```bash
# Login to GitHub CLI
gh auth login

# Create a Personal Access Token
# Go to: https://github.com/settings/tokens/new
# Scopes needed: write:packages, read:packages, repo

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

### Step 7: Configure GitHub Actions Secrets

```bash
# Generate ArgoCD token
argocd login localhost:8080 --insecure
argocd account generate-token --account admin

# Add secrets using GitHub CLI
gh secret set ARGOCD_SERVER --body "localhost:8080"
gh secret set ARGOCD_AUTH_TOKEN --body "YOUR_TOKEN_HERE"
```

Or manually:
1. Go to: https://github.com/purushravan/catvsdog/settings/secrets/actions
2. Add secrets:
   - `ARGOCD_SERVER`: `localhost:8080` (or your server URL)
   - `ARGOCD_AUTH_TOKEN`: (from argocd command above)

## M3-Specific Optimizations

### 1. Docker Build Performance

The Dockerfile is already optimized for ARM64. For faster builds:

```bash
# Enable BuildKit (better caching)
export DOCKER_BUILDKIT=1

# Build with cache
docker build \
  --platform linux/arm64 \
  --cache-from catvsdog-classifier:latest \
  -t catvsdog-classifier:simple \
  -f Dockerfile .
```

### 2. Resource Limits for M3

Update [k8s/deployment.yaml](k8s/deployment.yaml) for M3 development:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"      # M3 has plenty of power
  limits:
    memory: "2Gi"
    cpu: "2000m"     # Can use more on M3
```

### 3. Multi-Platform Builds

For CI/CD to support both ARM64 (M3) and AMD64 (cloud):

```bash
# Create a multi-platform builder
docker buildx create --name multiplatform --use
docker buildx inspect --bootstrap

# Build for both platforms
docker buildx build \
  --platform linux/arm64,linux/amd64 \
  -t ghcr.io/purushravan/catvsdog/catvsdog-classifier:latest \
  --push \
  -f Dockerfile .
```

## Troubleshooting for M3

### Issue: "exec format error"

**Cause**: Trying to run AMD64 image on ARM64

**Solution**:
```bash
# Rebuild for ARM64
docker build --platform linux/arm64 -t catvsdog-classifier:simple .

# Or enable Rosetta emulation in Docker Desktop
# Settings → Features in development → Use Rosetta
```

### Issue: Image pull errors in Kubernetes

**For Docker Desktop:**
```bash
# Ensure imagePullPolicy is set correctly
kubectl patch deployment catvsdog-api -n catvsdog-dev -p \
  '{"spec":{"template":{"spec":{"containers":[{"name":"catvsdog-api","imagePullPolicy":"IfNotPresent"}]}}}}'
```

**For Minikube:**
```bash
# Use minikube's Docker daemon
eval $(minikube docker-env)
docker build -t catvsdog-classifier:simple .
```

### Issue: Port already in use

```bash
# Find process using port 8080
lsof -ti:8080

# Kill the process
kill -9 $(lsof -ti:8080)

# Or use different port
kubectl port-forward svc/argocd-server -n argocd 8888:443
```

### Issue: Slow builds on M3

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Use layer caching
docker build --cache-from catvsdog-classifier:latest \
  -t catvsdog-classifier:simple .

# Increase Docker Desktop resources
# Docker Desktop → Settings → Resources
# - CPUs: 4-6
# - Memory: 8GB
# - Swap: 2GB
```

### Issue: ArgoCD login fails

```bash
# Use --insecure flag for local development
argocd login localhost:8080 --insecure --username admin

# Or update /etc/hosts if using domain
echo "127.0.0.1 argocd.local" | sudo tee -a /etc/hosts
```

## Verification Commands

```bash
# Check architecture
uname -m  # Should show: arm64

# Verify Docker platform
docker info | grep "OSType\|Architecture"

# Check Kubernetes is running
kubectl cluster-info

# Verify ArgoCD installation
kubectl get pods -n argocd

# Check application status
argocd app list

# View logs
kubectl logs -f -n catvsdog-dev -l app=catvsdog-api
```

## Performance Tips for M3

1. **Use Docker Desktop over Virtualization**: M3 handles Docker Desktop efficiently
2. **Enable BuildKit**: Faster, more efficient builds
3. **Allocate Resources**: Give Docker Desktop 6-8GB RAM
4. **Use ARM64 images**: Always specify platform when possible
5. **Enable Rosetta**: For compatibility with AMD64 images (Settings → Features)

## Next Steps

1. Test the local deployment
2. Push to GitHub to trigger CI/CD
3. Monitor in ArgoCD UI
4. Set up production with cloud provider

## Useful Aliases for M3 Development

```bash
# Add to ~/.zshrc (macOS default shell)
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deployments'
alias klf='kubectl logs -f'
alias argocd-ui='kubectl port-forward svc/argocd-server -n argocd 8080:443'
alias docker-clean='docker system prune -af --volumes'

# Reload shell
source ~/.zshrc
```

## Local Development Workflow

```bash
# 1. Make code changes
vim catvsdog_model_api/app/main.py

# 2. Build locally
docker build -t catvsdog-classifier:simple .

# 3. Load into Kubernetes (Docker Desktop - automatic)
# Or for minikube:
eval $(minikube docker-env) && docker build -t catvsdog-classifier:simple .

# 4. Restart deployment
kubectl rollout restart deployment/dev-catvsdog-api -n catvsdog-dev

# 5. Watch rollout
kubectl rollout status deployment/dev-catvsdog-api -n catvsdog-dev

# 6. Test
kubectl port-forward svc/dev-catvsdog-api -n catvsdog-dev 8001:8001
curl http://localhost:8001/health
```

## Resources for M3

- [Docker Desktop for Mac (Apple Silicon)](https://docs.docker.com/desktop/mac/apple-silicon/)
- [Kubernetes on Docker Desktop](https://docs.docker.com/desktop/kubernetes/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [BuildKit on ARM](https://docs.docker.com/build/building/multi-platform/)

Happy GitOps on your M3! 🚀
