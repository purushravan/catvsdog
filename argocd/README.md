# ArgoCD Configuration

This directory contains ArgoCD application definitions and setup scripts for GitOps-based continuous deployment.

## Files

- **install-argocd.sh**: Install ArgoCD on Kubernetes cluster
- **setup-argocd.sh**: Complete setup including application deployment
- **application.yaml**: Main CatVsDog API application definition
- **application-monitoring.yaml**: Monitoring stack (Prometheus/Grafana) application

## Quick Start

```bash
# 1. Install ArgoCD
./argocd/install-argocd.sh

# 2. Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# 3. Deploy applications
kubectl apply -f argocd/application.yaml
kubectl apply -f argocd/application-monitoring.yaml
```

## Application Structure

### catvsdog-app
- **Source**: k8s/ directory
- **Namespace**: catvsdog
- **Auto-sync**: Enabled
- **Self-heal**: Enabled

### catvsdog-monitoring
- **Source**: k8s/ directory
- **Namespace**: monitoring
- **Auto-sync**: Enabled
- **Self-heal**: Enabled

## Configuration

### Sync Policy

Both applications use automated sync with:
- Prune: Delete resources not in Git
- Self-heal: Revert manual changes
- Retry: 5 attempts with exponential backoff

### Health Assessment

ArgoCD monitors:
- Deployment rollout status
- Pod health
- Service endpoints

## Usage

### View Application Status

```bash
argocd app get catvsdog-app
argocd app get catvsdog-monitoring
```

### Manual Sync

```bash
argocd app sync catvsdog-app
```

### Rollback

```bash
argocd app rollback catvsdog-app <revision>
```

For complete setup instructions, see [ARGOCD_SETUP_GUIDE.md](../ARGOCD_SETUP_GUIDE.md)
