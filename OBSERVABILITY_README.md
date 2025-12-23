# Cat vs Dog ML Model - Complete Observability Setup

## 📋 Overview

This repository includes a complete observability and monitoring solution for the Cat vs Dog classification ML model, featuring:

- **Prometheus** for metrics collection and alerting
- **Grafana** for visualization and dashboards
- **Custom ML metrics** for model performance monitoring
- **Kubernetes-native deployment** with service discovery
- **Pre-configured dashboards** and alert rules

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                            │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    catvsdog Namespace                          │ │
│  │                                                                 │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  Cat vs Dog API Deployment (2 replicas)                  │ │ │
│  │  │  ┌──────────────────┐  ┌──────────────────┐            │ │ │
│  │  │  │  Pod 1           │  │  Pod 2           │            │ │ │
│  │  │  │  - FastAPI       │  │  - FastAPI       │            │ │ │
│  │  │  │  - TensorFlow    │  │  - TensorFlow    │            │ │ │
│  │  │  │  - /metrics      │  │  - /metrics      │            │ │ │
│  │  │  │    endpoint      │  │    endpoint      │            │ │ │
│  │  │  └──────────────────┘  └──────────────────┘            │ │ │
│  │  │           ▲                      ▲                       │ │ │
│  │  │           │                      │                       │ │ │
│  │  │           └──────────┬───────────┘                       │ │ │
│  │  └──────────────────────┼───────────────────────────────────┘ │ │
│  │                         │                                      │ │
│  │  Service (NodePort 30001)                                      │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                           │                                          │
│                           │ Prometheus scrapes :8001/metrics         │
│                           │                                          │
│  ┌────────────────────────┼──────────────────────────────────────┐ │
│  │              monitoring Namespace                │            │ │
│  │                        │                                       │ │
│  │  ┌─────────────────────▼──────────────┐  ┌──────────────────┐│ │
│  │  │         Prometheus                  │  │    Grafana       ││ │
│  │  │  - Service discovery (K8s API)      │─▶│  - Dashboards    ││ │
│  │  │  - Metrics storage (15d retention)  │  │  - Alerts        ││ │
│  │  │  - Alert evaluation                 │  │  - Query UI      ││ │
│  │  │  - PromQL queries                   │  │  - Admin panel   ││ │
│  │  │                                     │  │                  ││ │
│  │  │  Service (NodePort 30090)           │  │  (NodePort 30300)││ │
│  │  └─────────────────────────────────────┘  └──────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
           │                                          │
           │ http://localhost:30090                   │ http://localhost:30300
           │                                          │
           ▼                                          ▼
     [Prometheus UI]                           [Grafana UI]
     - Metrics explorer                        - Cat vs Dog Dashboard
     - Alert manager                           - Real-time metrics
     - Target status                           - Visualizations
```

## 📁 Files Created

### Application Instrumentation
- **catvsdog_model_api/app/main.py** - Updated with Prometheus metrics
- **requirements/api_requirements.txt** - Added monitoring dependencies

### Kubernetes Manifests (k8s/)
- **monitoring-namespace.yaml** - Monitoring namespace
- **prometheus-rbac.yaml** - RBAC for Prometheus
- **prometheus-config.yaml** - Prometheus configuration with alert rules
- **prometheus-deployment.yaml** - Prometheus deployment and service
- **grafana-config.yaml** - Grafana datasource configuration
- **grafana-dashboard.yaml** - Pre-built ML monitoring dashboard
- **grafana-deployment.yaml** - Grafana deployment and service
- **kustomization-monitoring.yaml** - Kustomize configuration
- **deployment.yaml** - Updated with Prometheus annotations
- **service.yaml** - Updated to NodePort for easy access

### Scripts
- **deploy-monitoring.sh** - Automated deployment script

### Documentation
- **MONITORING_GUIDE.md** - Comprehensive monitoring guide (60+ pages)
- **MONITORING_QUICKSTART.md** - Quick start guide (get running in 5 min)
- **OBSERVABILITY_README.md** - This file

## 🚀 Quick Start

### Prerequisites
- Kubernetes cluster (Minikube, Kind, or cloud provider)
- kubectl configured
- Docker image built: `catvsdog-classifier:simple`

### Deploy Everything

```bash
# 1. Deploy the application (if not already deployed)
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 2. Deploy monitoring stack
chmod +x deploy-monitoring.sh
./deploy-monitoring.sh

# 3. Wait for everything to be ready
kubectl get pods -n monitoring
kubectl get pods -n catvsdog
```

### Access Dashboards

| Service | URL | Credentials |
|---------|-----|-------------|
| Prometheus | http://localhost:30090 | None |
| Grafana | http://localhost:30300 | admin/admin |
| Cat vs Dog API | http://localhost:30001 | None |

### Alternative: Port Forwarding

```bash
# Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# API
kubectl port-forward -n catvsdog svc/catvsdog-api-service 8001:8001
```

## 📊 What's Being Monitored?

### ML Model Metrics

| Metric Name | Type | Description | Use Case |
|-------------|------|-------------|----------|
| `catvsdog_predictions_total` | Counter | Total predictions by class (cat/dog) | Track prediction volume and class distribution |
| `catvsdog_prediction_confidence` | Histogram | Distribution of confidence scores | Monitor model confidence, detect drift |
| `catvsdog_prediction_latency_seconds` | Histogram | Time taken for predictions | Track inference performance, optimize |
| `catvsdog_image_processing_errors_total` | Counter | Image processing failures | Monitor data quality issues |
| `catvsdog_active_predictions` | Gauge | Current in-flight predictions | Monitor concurrency, scaling |
| `catvsdog_model_info` | Info | Model and API version | Track deployments, versioning |

### HTTP/API Metrics (Auto-instrumented)

- `http_requests_total` - Total HTTP requests by method, endpoint, status
- `http_requests_inprogress` - Current in-flight HTTP requests
- `http_request_duration_seconds` - Request duration histogram

### Infrastructure Metrics (Kubernetes)

- `container_cpu_usage_seconds_total` - CPU usage per container
- `container_memory_usage_bytes` - Memory usage per container
- `kube_pod_container_status_restarts_total` - Container restarts
- `up` - Service availability (1=up, 0=down)

## 🎯 Grafana Dashboard

The pre-configured dashboard includes 13 panels:

### Model Performance
1. **Prediction Rate** - Predictions per second by class
2. **Total Predictions** - Cumulative counts
3. **Prediction Latency** - p50, p95, p99 percentiles
4. **Confidence Distribution** - Confidence score percentiles
5. **Active Predictions** - Concurrent predictions
6. **Processing Errors** - Error rate over time

### API Health
7. **API Request Rate** - Requests per second by endpoint
8. **HTTP Status Codes** - Distribution of response codes
13. **API Uptime** - Service availability indicator

### Infrastructure
9. **Pod CPU Usage** - CPU utilization by pod
10. **Pod Memory Usage** - Memory consumption by pod
12. **Pod Restart Count** - Container restart tracking

### Metadata
11. **Model Information** - Model and API versions

## 🚨 Pre-configured Alerts

| Alert | Severity | Condition | Duration |
|-------|----------|-----------|----------|
| APIDown | Critical | Service unavailable | 2 minutes |
| HighPredictionErrorRate | Warning | >0.1 errors/sec | 5 minutes |
| HighPredictionLatency | Warning | p95 > 2 seconds | 5 minutes |
| LowConfidencePredictions | Info | Median confidence < 70% | 10 minutes |
| HighMemoryUsage | Warning | Memory > 90% | 5 minutes |
| HighCPUUsage | Warning | CPU > 90% | 5 minutes |

## 🔍 Example Queries

### Model Performance

```promql
# Prediction rate by class
rate(catvsdog_predictions_total[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(catvsdog_prediction_latency_seconds_bucket[5m]))

# Average confidence score
rate(catvsdog_prediction_confidence_sum[5m]) / rate(catvsdog_prediction_confidence_count[5m])

# Error rate
rate(catvsdog_image_processing_errors_total[5m])

# Cat vs Dog ratio
sum(rate(catvsdog_predictions_total{prediction_class="cat"}[5m])) /
sum(rate(catvsdog_predictions_total{prediction_class="dog"}[5m]))
```

### API Health

```promql
# Request rate by endpoint
rate(http_requests_total{job="catvsdog-api"}[5m])

# Success rate (non-5xx responses)
sum(rate(http_requests_total{job="catvsdog-api",status!~"5.."}[5m])) /
sum(rate(http_requests_total{job="catvsdog-api"}[5m]))

# 99th percentile response time
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

### Infrastructure

```promql
# Memory usage percentage
container_memory_usage_bytes{pod=~"catvsdog-api.*"} /
container_spec_memory_limit_bytes{pod=~"catvsdog-api.*"} * 100

# CPU usage percentage
rate(container_cpu_usage_seconds_total{pod=~"catvsdog-api.*"}[5m]) /
container_spec_cpu_quota{pod=~"catvsdog-api.*"} * 100

# Pod restart rate
rate(kube_pod_container_status_restarts_total{namespace="catvsdog"}[1h])
```

## 🧪 Testing the Setup

### 1. Verify Metrics Endpoint

```bash
# Check if metrics are being exposed
curl http://localhost:30001/metrics | grep catvsdog_

# Expected output:
# catvsdog_predictions_total{prediction_class="cat"} 0.0
# catvsdog_predictions_total{prediction_class="dog"} 0.0
# catvsdog_prediction_confidence_bucket{le="0.5"} 0.0
# ...
```

### 2. Generate Test Traffic

```bash
# Option 1: Use the web UI
open http://localhost:30001

# Option 2: Make predictions via API
for i in {1..100}; do
  curl http://localhost:30001/health
  sleep 1
done
```

### 3. Check Prometheus Targets

1. Go to http://localhost:30090/targets
2. Find "catvsdog-api" job
3. Verify status is "UP" (green)

### 4. View Grafana Dashboard

1. Go to http://localhost:30300
2. Login with admin/admin
3. Navigate to Dashboards → "Cat vs Dog ML Model Monitoring"
4. Watch metrics populate in real-time

## 🛠️ Customization

### Add Custom Metrics

Edit [catvsdog_model_api/app/main.py](catvsdog_model_api/app/main.py):

```python
from prometheus_client import Counter, Histogram, Gauge

# Define custom metric
custom_metric = Counter(
    'catvsdog_custom_metric',
    'Description of custom metric',
    ['label1', 'label2']
)

# Update metric
custom_metric.labels(label1='value1', label2='value2').inc()
```

### Modify Dashboard

Edit [k8s/grafana-dashboard.yaml](k8s/grafana-dashboard.yaml) or use Grafana UI:
1. Edit dashboard in Grafana
2. Export dashboard JSON
3. Update ConfigMap with new JSON

### Adjust Alert Thresholds

Edit [k8s/prometheus-config.yaml](k8s/prometheus-config.yaml):

```yaml
- alert: HighPredictionLatency
  expr: histogram_quantile(0.95, rate(catvsdog_prediction_latency_seconds_bucket[5m])) > 2
  for: 5m
  # Change > 2 to your desired threshold
```

### Change Retention Period

Edit [k8s/prometheus-deployment.yaml](k8s/prometheus-deployment.yaml):

```yaml
args:
  - '--storage.tsdb.retention.time=15d'  # Change to 30d, 90d, etc.
```

## 📦 Components Used

| Component | Version | Purpose |
|-----------|---------|---------|
| Prometheus | 2.55.1 | Metrics collection and alerting |
| Grafana | 11.4.0 | Visualization and dashboards |
| prometheus-client | 0.21.0 | Python client for Prometheus |
| prometheus-fastapi-instrumentator | 7.0.0 | FastAPI auto-instrumentation |

## 🔒 Security Considerations

### Default Setup (Development)
- Grafana default password: `admin/admin`
- Prometheus has no authentication
- Services exposed via NodePort

### Production Recommendations
1. **Change Grafana password** immediately
2. **Enable Prometheus authentication** (use OAuth proxy or basic auth)
3. **Use Ingress** instead of NodePort with TLS
4. **Implement RBAC** for Grafana users
5. **Store secrets** in Kubernetes Secrets, not ConfigMaps
6. **Enable audit logging** for both Prometheus and Grafana
7. **Use network policies** to restrict traffic

Example: Change Grafana password
```bash
kubectl exec -n monitoring deployment/grafana -- \
  grafana-cli admin reset-admin-password NewSecurePassword123!
```

## 📈 Scaling Considerations

### Prometheus
- Use **remote storage** (Thanos, Cortex, M3DB) for long-term metrics
- Implement **federation** for multi-cluster deployments
- Use **recording rules** for expensive queries
- Consider **Prometheus Operator** for easier management

### Grafana
- Run **multiple replicas** with shared database (PostgreSQL/MySQL)
- Use **provisioning** for automated dashboard deployment
- Implement **LDAP/OAuth** for centralized authentication

### Application
- Metrics scraping adds minimal overhead (~1-2ms per request)
- Use **horizontal pod autoscaling** based on metrics
- Consider **metric relabeling** to reduce cardinality

## 🐛 Troubleshooting

### Prometheus Not Scraping

```bash
# 1. Check pod annotations
kubectl get pods -n catvsdog -o yaml | grep -A 5 annotations

# 2. Check Prometheus logs
kubectl logs -n monitoring deployment/prometheus

# 3. Restart Prometheus
kubectl rollout restart -n monitoring deployment/prometheus
```

### Grafana Shows No Data

```bash
# 1. Test Prometheus datasource in Grafana
# UI: Configuration → Data Sources → Prometheus → Test

# 2. Check if metrics exist
curl http://localhost:30090/api/v1/query?query=up

# 3. Verify time range in Grafana (not looking at future)
```

### High Cardinality Issues

```bash
# Check cardinality
curl http://localhost:30090/api/v1/status/tsdb

# If too high, consider:
# - Reducing label values
# - Using recording rules
# - Implementing metric relabeling
```

## 📚 Documentation

- **[MONITORING_QUICKSTART.md](MONITORING_QUICKSTART.md)** - Get started in 5 minutes
- **[MONITORING_GUIDE.md](MONITORING_GUIDE.md)** - Comprehensive guide with examples
- **[OBSERVABILITY_README.md](OBSERVABILITY_README.md)** - This file

## 🎓 Learning Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Monitoring Best Practices](https://prometheus.io/docs/practices/)
- [ML Model Monitoring Guide](https://christophergs.com/machine%20learning/2020/03/14/how-to-monitor-machine-learning-models/)

## 🤝 Contributing

To add new metrics or dashboards:

1. Add metrics to application code
2. Update Grafana dashboard JSON
3. Test locally
4. Submit PR with documentation

## 📝 License

Same as the main project.

---

**Questions?** Check the troubleshooting section or consult the full monitoring guide.

**Ready to monitor!** 🚀 Start with `./deploy-monitoring.sh`
