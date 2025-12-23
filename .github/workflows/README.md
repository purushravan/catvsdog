# GitHub Actions CI/CD Pipeline

This directory contains GitHub Actions workflows for continuous integration and deployment.

## Workflows

### ci-cd.yaml

Complete CI/CD pipeline with the following jobs:

#### 1. Test Job
- Runs on every push and pull request
- Executes pytest with coverage
- Uploads coverage reports to Codecov

#### 2. Build Job
- Runs on push to main/develop branches
- Builds multi-platform Docker images (amd64/arm64)
- Pushes to GitHub Container Registry
- Generates build attestation

#### 3. Update Manifests Job
- Updates Kubernetes deployment with new image tag
- Commits changes back to repository
- Triggers ArgoCD sync

#### 4. Deploy Job
- Triggers ArgoCD to sync application
- Waits for deployment completion
- Only runs on main branch

#### 5. Notify Job
- Reports deployment status
- Runs after all jobs complete

## Triggers

### Push Events
- Branches: `main`, `develop`
- Paths: model code, API code, Docker, k8s manifests

### Pull Request Events
- Branches: `main`, `develop`
- Runs tests only (no deployment)

## Required Secrets

Configure in GitHub repository settings:

| Secret | Description |
|--------|-------------|
| `GITHUB_TOKEN` | Auto-provided by GitHub |
| `ARGOCD_SERVER` | ArgoCD server URL |
| `ARGOCD_AUTH_TOKEN` | ArgoCD authentication token |

## Environment Variables

```yaml
REGISTRY: ghcr.io  # GitHub Container Registry
IMAGE_NAME: ${{ github.repository }}/catvsdog-classifier
```

## Image Tagging Strategy

Images are tagged with:
- Branch name (e.g., `main`, `develop`)
- Git SHA (e.g., `main-a1b2c3d`)
- Semantic version (if tagged)
- `latest` for default branch

## Cache Strategy

Uses GitHub Actions cache for:
- Docker layer caching
- Pip dependencies

## Platforms

Builds for multiple architectures:
- linux/amd64
- linux/arm64

## Usage

### Manual Trigger

```bash
# Trigger workflow manually
gh workflow run ci-cd.yaml
```

### View Workflow Status

```bash
# List workflow runs
gh run list --workflow=ci-cd.yaml

# View specific run
gh run view <run-id>
```

### Skip CI

Add `[skip ci]` to commit message:

```bash
git commit -m "docs: update README [skip ci]"
```

## Local Testing

Test the workflow locally with [act](https://github.com/nektos/act):

```bash
# Install act
brew install act

# Run workflow
act push
```

## Troubleshooting

### Build Failures

Check logs:
```bash
gh run view --log-failed
```

### Image Push Failures

Verify permissions:
```bash
# Check package permissions in GitHub settings
# Ensure GITHUB_TOKEN has write:packages scope
```

### Deployment Timeout

Increase timeout in workflow:
```yaml
- name: Trigger ArgoCD Sync
  timeout-minutes: 10
```

For complete pipeline setup, see [ARGOCD_SETUP_GUIDE.md](../../ARGOCD_SETUP_GUIDE.md)
