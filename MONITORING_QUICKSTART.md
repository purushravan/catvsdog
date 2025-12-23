# Monitoring Quick Start Guide

## 🚀 Quick Deploy (5 minutes)

### 1. Deploy Monitoring Stack

```bash
# Make script executable (if not already)
chmod +x deploy-monitoring.sh

# Deploy everything
./deploy-monitoring.sh
```

### 2. Access Dashboards

**Prometheus**: http://localhost:30090
```bash
# Or use port-forward
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

**Grafana**: http://localhost:30300
```bash
# Or use port-forward
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Login credentials:
# Username: admin
# Password: admin
```

**Cat vs Dog API**: http://localhost:30001
```bash
# Or use port-forward
kubectl port-forward -n catvsdog svc/catvsdog-api-service 8001:8001
```

### 3. View Metrics

1. Open Grafana at http://localhost:30300
2. Login with admin/admin
3. Go to **Dashboards** → **Cat vs Dog ML Model Monitoring**
4. Make some predictions on the API to see metrics

## 📊 Key Metrics at a Glance

| Metric | What it tells you | Where to see it |
|--------|------------------|----------------|
| Prediction Rate | How many predictions/sec | Grafana Panel #1 |
| Prediction Latency | How long predictions take | Grafana Panel #3 |
| Error Rate | How many predictions fail | Grafana Panel #6 |
| Confidence Score | How confident the model is | Grafana Panel #4 |
| API Uptime | Is the API running? | Grafana Panel #13 |

## 🔍 Quick Checks

### Verify Metrics are Being Collected

```bash
# Check if metrics endpoint is working
curl http://localhost:30001/metrics | grep catvsdog_

# Expected output:
# catvsdog_predictions_total{prediction_class="cat"} 45.0
# catvsdog_predictions_total{prediction_class="dog"} 55.0
# ...
```

### Check Prometheus Targets

1. Go to http://localhost:30090/targets
2. Find "catvsdog-api" job
3. Status should be "UP" (green)

### Generate Test Traffic

```bash
# Option 1: Use the web UI
open http://localhost:30001

# Option 2: Hit health endpoint
for i in {1..100}; do
  curl http://localhost:30001/health
  sleep 1
done
```

## 🎯 Common PromQL Queries

Copy-paste these into Prometheus or Grafana:

```promql
# Prediction rate by class
rate(catvsdog_predictions_total[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(catvsdog_prediction_latency_seconds_bucket[5m]))

# Error rate
rate(catvsdog_image_processing_errors_total[5m])

# HTTP requests per second
rate(http_requests_total{job="catvsdog-api"}[5m])

# Memory usage percentage
container_memory_usage_bytes{pod=~"catvsdog-api.*"} / container_spec_memory_limit_bytes{pod=~"catvsdog-api.*"} * 100
```

## 🔧 Troubleshooting

### Prometheus can't scrape metrics?

```bash
# 1. Check pod annotations
kubectl get pods -n catvsdog -o yaml | grep -A 3 annotations

# Should show:
# prometheus.io/scrape: "true"
# prometheus.io/port: "8001"
# prometheus.io/path: "/metrics"

# 2. Restart deployment
kubectl rollout restart deployment/catvsdog-api -n catvsdog
```

### Grafana shows "No data"?

```bash
# 1. Check Prometheus datasource in Grafana
# Go to: Configuration → Data Sources → Prometheus → Test

# 2. Verify metrics exist in Prometheus
# Go to Prometheus UI and query: catvsdog_predictions_total

# 3. Make some predictions to generate data
curl -X POST -F "file=@/path/to/image.jpg" http://localhost:30001/predict/
```

### Can't access dashboards?

```bash
# Check if services are running
kubectl get pods -n monitoring

# Both prometheus and grafana should be "Running"

# If using Minikube
minikube service prometheus -n monitoring
minikube service grafana -n monitoring
```

## 📖 Full Documentation

For detailed information, see [MONITORING_GUIDE.md](MONITORING_GUIDE.md)

## 🎓 What's Being Monitored?

### Application Layer
- ✅ Prediction counts (cat vs dog)
- ✅ Prediction latency
- ✅ Prediction confidence scores
- ✅ Image processing errors
- ✅ Active prediction count

### HTTP Layer
- ✅ Request rate
- ✅ Response times
- ✅ Status codes
- ✅ In-flight requests

### Infrastructure Layer
- ✅ CPU usage
- ✅ Memory usage
- ✅ Pod restarts
- ✅ Service availability

### Alerts
- ✅ API down
- ✅ High error rate
- ✅ High latency
- ✅ High resource usage
- ✅ Low confidence predictions

## 🚨 Alert Conditions

| Alert | Threshold | Duration |
|-------|-----------|----------|
| API Down | up == 0 | 2 minutes |
| High Error Rate | > 0.1 errors/sec | 5 minutes |
| High Latency | p95 > 2 seconds | 5 minutes |
| High Memory | > 90% | 5 minutes |
| High CPU | > 90% | 5 minutes |
| Low Confidence | median < 70% | 10 minutes |

## 💡 Pro Tips

1. **Bookmark these URLs:**
   - Prometheus: http://localhost:30090
   - Grafana: http://localhost:30300
   - API: http://localhost:30001

2. **Set up Grafana alerts:**
   - Go to Alert rules in Grafana
   - Configure notification channels (email, Slack)
   - Get notified when things go wrong

3. **Use Grafana variables:**
   - Filter by pod, time range, percentile
   - Create custom views for different teams

4. **Export dashboards:**
   ```bash
   # Backup your dashboards
   kubectl get configmap -n monitoring grafana-dashboard-catvsdog -o yaml > backup.yaml
   ```

5. **Monitor continuously:**
   - Set auto-refresh to 10s for real-time monitoring
   - Use the time range selector to investigate issues
   - Create annotations for deployments

## 📞 Need Help?

1. Check the [Full Monitoring Guide](MONITORING_GUIDE.md)
2. Review Prometheus logs: `kubectl logs -n monitoring deployment/prometheus`
3. Review Grafana logs: `kubectl logs -n monitoring deployment/grafana`
4. Review API logs: `kubectl logs -n catvsdog deployment/catvsdog-api`

---

**Ready to monitor!** 🎉

Start by accessing Grafana at http://localhost:30300 and exploring the pre-built dashboard.
