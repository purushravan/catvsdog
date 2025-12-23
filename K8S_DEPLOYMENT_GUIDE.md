# Kubernetes Deployment Guide for Cats vs Dogs Classifier

This guide will help you deploy the Cats vs Dogs image classification application to a Kubernetes cluster.

## Prerequisites

- Kubernetes cluster (local or cloud-based)
- kubectl configured to access your cluster
- Docker installed (for building the image)
- Access to push images to a container registry (Docker Hub, GCR, ECR, etc.)

## Quick Start

### 1. Build and Push Docker Image

First, build your Docker image and push it to a container registry:

```bash
# Build the image
docker build -t catvsdog-classifier:latest .

# Tag for your registry (replace with your registry URL)
docker tag catvsdog-classifier:latest <your-registry>/catvsdog-classifier:latest

# Push to registry
docker push <your-registry>/catvsdog-classifier:latest
```

**For local development (Minikube/Kind):**
```bash
# If using Minikube
eval $(minikube docker-env)
docker build -t catvsdog-classifier:latest .

# If using Kind
kind load docker-image catvsdog-classifier:latest
```

### 2. Update Deployment Configuration

Edit [k8s/deployment.yaml](k8s/deployment.yaml#L22) and update the image reference:

```yaml
image: <your-registry>/catvsdog-classifier:latest
imagePullPolicy: Always
```

If using local images (Minikube/Kind), keep:
```yaml
image: catvsdog-classifier:latest
imagePullPolicy: IfNotPresent
```

### 3. Prepare Model Files

Before deploying, you need to copy your trained model to the persistent volume:

```bash
# Create a temporary pod to copy files
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/pvc.yaml

# Wait for PVCs to be bound
kubectl get pvc -n catvsdog --watch

# Create a helper pod to copy model files
kubectl run -n catvsdog model-copier --image=busybox --rm -it --restart=Never \
  --overrides='
{
  "spec": {
    "containers": [{
      "name": "model-copier",
      "image": "busybox",
      "command": ["sh"],
      "stdin": true,
      "tty": true,
      "volumeMounts": [{
        "name": "models",
        "mountPath": "/models"
      }]
    }],
    "volumes": [{
      "name": "models",
      "persistentVolumeClaim": {
        "claimName": "catvsdog-models-pvc"
      }
    }]
  }
}' -- sh
```

Then in another terminal, copy your model:
```bash
kubectl cp catvsdog_model/trained_models/. catvsdog/model-copier:/models/
```

Exit the helper pod by typing `exit`.

### 4. Deploy the Application

Deploy all Kubernetes resources:

```bash
# Apply all manifests in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Optional: Apply HPA for autoscaling
kubectl apply -f k8s/hpa.yaml

# Optional: Apply Ingress (requires ingress controller)
kubectl apply -f k8s/ingress.yaml
```

Or apply everything at once:
```bash
kubectl apply -f k8s/
```

### 5. Verify Deployment

Check the deployment status:

```bash
# Check all resources
kubectl get all -n catvsdog

# Check pod logs
kubectl logs -n catvsdog -l app=catvsdog-api -f

# Check deployment status
kubectl get deployment -n catvsdog catvsdog-api

# Check service
kubectl get service -n catvsdog catvsdog-api-service
```

### 6. Access the Application

**Using LoadBalancer (Cloud providers):**
```bash
# Get external IP
kubectl get service -n catvsdog catvsdog-api-service

# Access the API
curl http://<EXTERNAL-IP>:8001/health
```

**Using NodePort (Local clusters):**

Edit [k8s/service.yaml](k8s/service.yaml#L9) and change:
```yaml
type: NodePort
```

Add nodePort:
```yaml
ports:
  - port: 8001
    targetPort: 8001
    nodePort: 30001
```

Apply changes:
```bash
kubectl apply -f k8s/service.yaml

# Get node IP
kubectl get nodes -o wide

# Access the API
curl http://<NODE-IP>:30001/health
```

**Using Port Forwarding (Development):**
```bash
kubectl port-forward -n catvsdog service/catvsdog-api-service 8001:8001

# Access locally
curl http://localhost:8001/health
```

## Architecture

The Kubernetes deployment includes:

- **Namespace**: Isolated environment for the application
- **ConfigMap**: Environment variables configuration
- **PersistentVolumeClaims**: Storage for models and static files
- **Deployment**: Application pods with health checks and resource limits
- **Service**: Load balancing and service discovery
- **HPA**: Horizontal Pod Autoscaler for automatic scaling
- **Ingress**: External access with domain routing (optional)

## Configuration Files

| File | Description |
|------|-------------|
| [k8s/namespace.yaml](k8s/namespace.yaml) | Namespace definition |
| [k8s/configmap.yaml](k8s/configmap.yaml) | Environment variables |
| [k8s/pvc.yaml](k8s/pvc.yaml) | Persistent volume claims for models and static files |
| [k8s/deployment.yaml](k8s/deployment.yaml) | Application deployment with 2 replicas |
| [k8s/service.yaml](k8s/service.yaml) | LoadBalancer service exposing port 8001 |
| [k8s/hpa.yaml](k8s/hpa.yaml) | Horizontal Pod Autoscaler (2-10 replicas) |
| [k8s/ingress.yaml](k8s/ingress.yaml) | Ingress for domain-based routing |

## Scaling

### Manual Scaling

```bash
# Scale to 5 replicas
kubectl scale deployment -n catvsdog catvsdog-api --replicas=5

# Check scaling status
kubectl get deployment -n catvsdog catvsdog-api
```

### Automatic Scaling (HPA)

The HPA is configured to scale based on CPU and memory usage:

- Min replicas: 2
- Max replicas: 10
- CPU target: 70%
- Memory target: 80%

Check HPA status:
```bash
kubectl get hpa -n catvsdog
kubectl describe hpa -n catvsdog catvsdog-api-hpa
```

## Resource Requirements

Each pod requests:
- Memory: 512Mi (limit: 2Gi)
- CPU: 250m (limit: 1000m)

Adjust these in [k8s/deployment.yaml](k8s/deployment.yaml#L36-L42) based on your workload.

## Storage

Two PersistentVolumeClaims are created:

1. **catvsdog-models-pvc** (5Gi): Stores trained models (read-only)
2. **catvsdog-static-pvc** (2Gi): Stores uploaded images and static files

Update storage class in [k8s/pvc.yaml](k8s/pvc.yaml) based on your cluster:
```yaml
storageClassName: standard  # or gp2, fast, etc.
```

## Health Checks

The deployment includes:

- **Liveness Probe**: Checks if the application is running (restarts if unhealthy)
- **Readiness Probe**: Checks if the application is ready to serve traffic

Both probes use the `/health` endpoint.

## Updating the Application

### Update Docker Image

```bash
# Build new image
docker build -t catvsdog-classifier:v2 .

# Push to registry
docker tag catvsdog-classifier:v2 <your-registry>/catvsdog-classifier:v2
docker push <your-registry>/catvsdog-classifier:v2

# Update deployment
kubectl set image deployment/catvsdog-api -n catvsdog \
  catvsdog-api=<your-registry>/catvsdog-classifier:v2

# Check rollout status
kubectl rollout status deployment/catvsdog-api -n catvsdog
```

### Rollback Deployment

```bash
# View rollout history
kubectl rollout history deployment/catvsdog-api -n catvsdog

# Rollback to previous version
kubectl rollout undo deployment/catvsdog-api -n catvsdog

# Rollback to specific revision
kubectl rollout undo deployment/catvsdog-api -n catvsdog --to-revision=2
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n catvsdog

# Describe pod for events
kubectl describe pod -n catvsdog <pod-name>

# Check logs
kubectl logs -n catvsdog <pod-name>
```

### PVC Not Binding

```bash
# Check PVC status
kubectl get pvc -n catvsdog

# Describe PVC
kubectl describe pvc -n catvsdog catvsdog-models-pvc

# Check available storage classes
kubectl get storageclass
```

### Service Not Accessible

```bash
# Check service
kubectl get service -n catvsdog

# Check endpoints
kubectl get endpoints -n catvsdog catvsdog-api-service

# Test from within cluster
kubectl run -n catvsdog debug --rm -it --image=busybox --restart=Never -- \
  wget -qO- http://catvsdog-api-service:8001/health
```

### HPA Not Scaling

```bash
# Check metrics server is installed
kubectl get deployment metrics-server -n kube-system

# Check HPA status
kubectl describe hpa -n catvsdog catvsdog-api-hpa

# Check pod metrics
kubectl top pods -n catvsdog
```

## Ingress Setup

To use the ingress:

1. Install an ingress controller (e.g., nginx-ingress):
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

2. Update [k8s/ingress.yaml](k8s/ingress.yaml) with your domain:
```yaml
host: catvsdog.example.com
```

3. Apply the ingress:
```bash
kubectl apply -f k8s/ingress.yaml
```

4. Configure DNS to point to the ingress controller's external IP:
```bash
kubectl get service -n ingress-nginx ingress-nginx-controller
```

## Clean Up

Remove all resources:

```bash
# Delete all resources in namespace
kubectl delete -f k8s/

# Or delete namespace (removes everything)
kubectl delete namespace catvsdog
```

## Production Considerations

1. **Use a Container Registry**: Push images to a registry instead of local images
2. **Configure Storage Class**: Use appropriate storage class for your cloud provider
3. **Set Resource Limits**: Adjust based on actual usage and load testing
4. **Enable TLS**: Configure ingress with SSL/TLS certificates
5. **Add Monitoring**: Integrate with Prometheus/Grafana for monitoring
6. **Configure Logging**: Use ELK or similar for centralized logging
7. **Implement Network Policies**: Restrict network access between pods
8. **Use Secrets**: Store sensitive data in Kubernetes Secrets
9. **Configure Backup**: Regular backups of PVCs and application data
10. **Multi-zone Deployment**: Deploy across multiple availability zones

## Example API Calls

Once deployed, test the API:

```bash
# Health check
curl http://<SERVICE-IP>:8001/health

# API documentation
curl http://<SERVICE-IP>:8001/docs

# Predict endpoint (upload an image)
curl -X POST http://<SERVICE-IP>:8001/predict \
  -F "file=@/path/to/cat.jpg"
```

## Support

For issues or questions:
- Check application logs: `kubectl logs -n catvsdog -l app=catvsdog-api`
- Review Kubernetes events: `kubectl get events -n catvsdog --sort-by='.lastTimestamp'`
- Check resource usage: `kubectl top pods -n catvsdog`
