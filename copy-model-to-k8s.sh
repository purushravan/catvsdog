#!/bin/bash
# Copy trained model to Kubernetes persistent volume

set -e

echo "=== Copying Model Files to Kubernetes PVC ==="
echo ""

# Create a temporary pod to copy files
echo "Creating temporary helper pod..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: model-copier
  namespace: catvsdog
spec:
  containers:
  - name: copier
    image: busybox
    command: ['sh', '-c', 'sleep 3600']
    volumeMounts:
    - name: models
      mountPath: /models
    - name: static
      mountPath: /static
  volumes:
  - name: models
    persistentVolumeClaim:
      claimName: catvsdog-models-pvc
  - name: static
    persistentVolumeClaim:
      claimName: catvsdog-static-pvc
  restartPolicy: Never
EOF

# Wait for pod to be ready
echo "Waiting for helper pod to be ready..."
kubectl wait --for=condition=Ready pod/model-copier -n catvsdog --timeout=60s

# Copy model files
echo "Copying model files..."
kubectl cp catvsdog_model/trained_models/catvsdog__model_output_v0.0.1.keras \
  catvsdog/model-copier:/models/catvsdog__model_output_v0.0.1.keras

echo "Copying __init__.py..."
kubectl cp catvsdog_model/trained_models/__init__.py \
  catvsdog/model-copier:/models/__init__.py

# Verify files were copied
echo ""
echo "Verifying files in PVC..."
kubectl exec -n catvsdog model-copier -- ls -lh /models/

# Clean up
echo ""
read -p "Delete helper pod? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kubectl delete pod model-copier -n catvsdog
    echo "Helper pod deleted"
else
    echo "Helper pod kept. Delete manually with: kubectl delete pod model-copier -n catvsdog"
fi

echo ""
echo "✓ Model files copied successfully!"
echo ""
echo "Next steps:"
echo "1. Restart the deployment: kubectl rollout restart deployment/catvsdog-api -n catvsdog"
echo "2. Watch the pods: kubectl get pods -n catvsdog -w"
echo "3. Check logs: kubectl logs -n catvsdog -l app=catvsdog-api -f"
