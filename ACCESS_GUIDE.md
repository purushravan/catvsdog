# Service Access Guide for Docker Desktop Kubernetes

## 🎯 Quick Access

You're using **Docker Desktop with Kind**, which requires **port-forwarding** to access services.

### ✅ Easy Access (Recommended)

```bash
# Start all services
./start-services.sh

# Access URLs:
# - Cat vs Dog API: http://localhost:8001
# - Prometheus:     http://localhost:9090
# - Grafana:        http://localhost:3000

# Stop all services
./stop-services.sh
```

## 🔗 Access URLs

Once port-forwarding is active:

| Service | URL | Purpose |
|---------|-----|---------|
| **Cat vs Dog API** | http://localhost:8001 | Web UI to upload images |
| API Health | http://localhost:8001/health | Health check endpoint |
| API Metrics | http://localhost:8001/metrics | Prometheus metrics |
| **Prometheus** | http://localhost:9090 | Metrics database & queries |
| Prometheus Targets | http://localhost:9090/targets | Check scraping status |
| Prometheus Alerts | http://localhost:9090/alerts | View active alerts |
| **Grafana** | http://localhost:3000 | Dashboards & visualization |
| Grafana Login | Username: `admin`<br>Password: `admin` | Default credentials |

## 🛠️ Manual Port-Forwarding

If you prefer to do it manually:

```bash
# Cat vs Dog API
kubectl port-forward -n catvsdog svc/catvsdog-api-service 8001:8001 &

# Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &

# Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000 &

# Check running port-forwards
ps aux | grep port-forward

# Stop all port-forwards
pkill -f port-forward
```

## 🔍 Troubleshooting

### Services Not Accessible

**Check if pods are running:**
```bash
kubectl get pods -n catvsdog
kubectl get pods -n monitoring
```

All pods should show `Running` status.

**Check if services exist:**
```bash
kubectl get svc -n catvsdog
kubectl get svc -n monitoring
```

**View pod logs if issues:**
```bash
# Application logs
kubectl logs -n catvsdog deployment/catvsdog-api

# Prometheus logs
kubectl logs -n monitoring deployment/prometheus

# Grafana logs
kubectl logs -n monitoring deployment/grafana
```

### Port Already in Use

If you get "address already in use" errors:

```bash
# Find what's using the port (example: port 8001)
lsof -i :8001

# Kill the process
kill -9 <PID>

# Or stop all port-forwards
./stop-services.sh
```

### Port-Forward Disconnects

Port-forwards can disconnect. If a service becomes inaccessible:

```bash
# Restart all services
./stop-services.sh
./start-services.sh
```

## 📋 Why NodePort Doesn't Work

Docker Desktop Kubernetes uses Kind under the hood, which runs Kubernetes in containers. The NodePort services (30001, 30090, 30300) are exposed inside the Docker network but not directly accessible from your host machine.

**Solutions:**
1. ✅ **Port-forwarding** (recommended, most reliable)
2. Use LoadBalancer with MetalLB (advanced)
3. Use Ingress controller (production setup)

## 🎨 Grafana Dashboard Access

1. Start services: `./start-services.sh`
2. Open Grafana: http://localhost:3000
3. Login with `admin` / `admin`
4. Go to: **Dashboards** → **Cat vs Dog ML Model Monitoring**
5. Make some predictions on the API to see metrics populate

## 🧪 Test the Setup

```bash
# 1. Start services
./start-services.sh

# 2. Test API health
curl http://localhost:8001/health

# Expected output:
# {"name":"Cats & Dogs Image Classification API","api_version":"0.0.1","model_version":"0.0.1"}

# 3. Test metrics endpoint
curl http://localhost:8001/metrics | grep catvsdog_

# Expected output:
# catvsdog_predictions_total{prediction_class="cat"} 0.0
# catvsdog_predictions_total{prediction_class="dog"} 0.0
# ...

# 4. Open in browser
open http://localhost:8001      # API
open http://localhost:9090      # Prometheus
open http://localhost:3000      # Grafana
```

## 🚀 Quick Start Workflow

```bash
# Step 1: Ensure deployments are running
kubectl get pods -n catvsdog
kubectl get pods -n monitoring

# Step 2: Start port-forwarding
./start-services.sh

# Step 3: Access services
# - Make predictions: http://localhost:8001
# - Check metrics: http://localhost:9090
# - View dashboard: http://localhost:3000

# Step 4: When done, stop port-forwarding
./stop-services.sh
```

## 💡 Pro Tips

1. **Keep terminal open**: Port-forwarding runs in background but attached to your shell
2. **Use separate terminal**: Run `start-services.sh` in a dedicated terminal window
3. **Bookmark URLs**: Save the localhost URLs for quick access
4. **Auto-restart**: Add `start-services.sh` to your development workflow script
5. **Monitor logs**: Keep an eye on `/tmp/pf-*.log` files for port-forward logs

## 🔐 Security Note

Default Grafana credentials are `admin`/`admin`. In production:
```bash
# Change Grafana password
kubectl exec -n monitoring deployment/grafana -- \
  grafana-cli admin reset-admin-password YourNewPassword
```

## 📞 Need Help?

1. Check logs: `kubectl logs -n <namespace> <pod-name>`
2. Describe pod: `kubectl describe pod -n <namespace> <pod-name>`
3. Check events: `kubectl get events -n <namespace>`
4. Restart pod: `kubectl rollout restart -n <namespace> deployment/<name>`

---

**Ready to monitor!** Start with `./start-services.sh` and access your services at localhost.
