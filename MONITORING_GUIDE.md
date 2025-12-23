# Cat vs Dog ML Model - Observability and Monitoring Guide

## Overview

This guide explains the comprehensive observability and monitoring setup for the Cat vs Dog classification model using Prometheus and Grafana on Kubernetes.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         catvsdog Namespace                           │  │
│  │  ┌──────────────────────────────────────────┐       │  │
│  │  │  Cat vs Dog API Pods                     │       │  │
│  │  │  - FastAPI Application                   │       │  │
│  │  │  - /metrics endpoint (Prometheus format) │       │  │
│  │  │  - Custom ML metrics                     │       │  │
│  │  └──────────────────────────────────────────┘       │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ▲                                  │
│                          │ scrapes metrics                  │
│                          │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         monitoring Namespace                         │  │
│  │  ┌─────────────────────┐  ┌────────────────────┐   │  │
│  │  │   Prometheus        │  │    Grafana         │   │  │
│  │  │  - Metrics storage  │─▶│  - Visualization   │   │  │
│  │  │  - Alerting rules   │  │  - Dashboards      │   │  │
│  │  │  - Service discovery│  │  - Admin UI        │   │  │
│  │  └─────────────────────┘  └────────────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │                              │
         │ NodePort :30090              │ NodePort :30300
         ▼                              ▼
    http://localhost:9090        http://localhost:3000
```

## Components

### 1. Application Instrumentation

The FastAPI application in `catvsdog_model_api/app/main.py` has been instrumented with:

#### Custom ML Metrics

- **catvsdog_predictions_total**: Counter tracking total predictions by class (cat/dog)
- **catvsdog_prediction_confidence**: Histogram of prediction confidence scores
- **catvsdog_prediction_latency_seconds**: Histogram of prediction processing time
- **catvsdog_image_processing_errors_total**: Counter for image processing errors
- **catvsdog_active_predictions**: Gauge showing current in-flight predictions
- **catvsdog_model_info**: Info metric with model and API version

#### HTTP Metrics (Auto-instrumented)

- **http_requests_total**: Total HTTP requests by method, handler, and status
- **http_requests_inprogress**: Current in-flight HTTP requests
- **http_request_duration_seconds**: HTTP request duration histogram

### 2. Prometheus

Prometheus configuration includes:

- **Scrape Interval**: 15 seconds
- **Retention**: 15 days
- **Service Discovery**: Automatic discovery of Kubernetes pods and services
- **Alert Rules**: Pre-configured alerts for model and infrastructure monitoring

### 3. Grafana

Grafana provides visualization with:

- **Pre-configured Datasource**: Connected to Prometheus
- **Custom Dashboard**: ML model monitoring dashboard with 13 panels
- **Auto-refresh**: Dashboard refreshes every 10 seconds

## Deployment Instructions

### Prerequisites

- Kubernetes cluster running (Minikube, Kind, or production cluster)
- kubectl configured
- Docker image built: `catvsdog-classifier:simple`

### Step 1: Create Monitoring Namespace

```bash
kubectl apply -f k8s/monitoring-namespace.yaml
```

### Step 2: Deploy RBAC for Prometheus

```bash
kubectl apply -f k8s/prometheus-rbac.yaml
```

### Step 3: Deploy Prometheus

```bash
# Create Prometheus configuration
kubectl apply -f k8s/prometheus-config.yaml

# Deploy Prometheus
kubectl apply -f k8s/prometheus-deployment.yaml
```

### Step 4: Deploy Grafana

```bash
# Create Grafana configuration
kubectl apply -f k8s/grafana-config.yaml

# Create Grafana dashboard
kubectl apply -f k8s/grafana-dashboard.yaml

# Deploy Grafana
kubectl apply -f k8s/grafana-deployment.yaml
```

### Step 5: Deploy the Application

```bash
# Apply all application manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Step 6: Verify Deployment

```bash
# Check monitoring namespace
kubectl get pods -n monitoring

# Check application namespace
kubectl get pods -n catvsdog

# Check if metrics endpoint is working
kubectl port-forward -n catvsdog svc/catvsdog-api-service 8001:8001
curl http://localhost:8001/metrics
```

## Accessing the Monitoring Stack

### Prometheus

**URL**: http://localhost:30090 (or your Kubernetes node IP)

**NodePort Service**: Port 30090

**Usage**:
1. Access Prometheus UI
2. Go to "Status" → "Targets" to verify all targets are being scraped
3. Go to "Alerts" to see active alerts
4. Use PromQL to query metrics:
   ```
   rate(catvsdog_predictions_total[5m])
   histogram_quantile(0.95, rate(catvsdog_prediction_latency_seconds_bucket[5m]))
   ```

### Grafana

**URL**: http://localhost:30300 (or your Kubernetes node IP)

**Default Credentials**:
- Username: `admin`
- Password: `admin`

**NodePort Service**: Port 30300

**Usage**:
1. Log in with admin credentials
2. Navigate to "Dashboards" → "Cat vs Dog ML Model Monitoring"
3. View real-time metrics and visualizations

### Port Forwarding (Alternative Access)

If NodePort is not accessible:

```bash
# Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

## Metrics Available

### ML Model Metrics

| Metric | Type | Description |
|--------|------|-------------|
| catvsdog_predictions_total | Counter | Total predictions made, labeled by class (cat/dog) |
| catvsdog_prediction_confidence | Histogram | Distribution of prediction confidence scores |
| catvsdog_prediction_latency_seconds | Histogram | Time taken for each prediction |
| catvsdog_image_processing_errors_total | Counter | Total image processing errors |
| catvsdog_active_predictions | Gauge | Current number of in-flight predictions |
| catvsdog_model_info | Info | Model version and API version information |

### HTTP Metrics

| Metric | Type | Description |
|--------|------|-------------|
| http_requests_total | Counter | Total HTTP requests by method, handler, status |
| http_requests_inprogress | Gauge | Current in-flight HTTP requests |
| http_request_duration_seconds | Histogram | HTTP request duration distribution |

### Infrastructure Metrics

| Metric | Type | Description |
|--------|------|-------------|
| container_cpu_usage_seconds_total | Counter | CPU usage of containers |
| container_memory_usage_bytes | Gauge | Memory usage of containers |
| kube_pod_container_status_restarts_total | Counter | Number of container restarts |
| up | Gauge | Service availability (1=up, 0=down) |

## Grafana Dashboard Panels

The pre-configured dashboard includes:

1. **Prediction Rate**: Real-time prediction rate by class
2. **Total Predictions**: Cumulative predictions by class
3. **Prediction Latency**: p50, p95, p99 latency percentiles
4. **Prediction Confidence**: Distribution of confidence scores
5. **Active Predictions**: Current in-flight predictions
6. **Image Processing Errors**: Error rate over time
7. **API Request Rate**: HTTP request rate by endpoint
8. **HTTP Status Codes**: Distribution of response codes
9. **Pod CPU Usage**: CPU utilization by pod
10. **Pod Memory Usage**: Memory consumption by pod
11. **Model Information**: Model and API version details
12. **Pod Restart Count**: Container restart tracking
13. **API Uptime**: Service availability indicator

## Alert Rules

Pre-configured alerts in Prometheus:

### High Priority

- **APIDown**: API pod is not responding (triggers after 2 minutes)
- **HighMemoryUsage**: Memory usage > 90% (triggers after 5 minutes)
- **HighCPUUsage**: CPU usage > 90% (triggers after 5 minutes)

### Medium Priority

- **HighPredictionErrorRate**: Error rate > 0.1 errors/sec (triggers after 5 minutes)
- **HighPredictionLatency**: p95 latency > 2 seconds (triggers after 5 minutes)

### Low Priority

- **LowConfidencePredictions**: Median confidence < 70% (triggers after 10 minutes)

## Querying Metrics with PromQL

### Example Queries

**Prediction rate over the last 5 minutes:**
```promql
rate(catvsdog_predictions_total[5m])
```

**95th percentile prediction latency:**
```promql
histogram_quantile(0.95, rate(catvsdog_prediction_latency_seconds_bucket[5m]))
```

**Error rate:**
```promql
rate(catvsdog_image_processing_errors_total[5m])
```

**Average prediction confidence:**
```promql
rate(catvsdog_prediction_confidence_sum[5m]) / rate(catvsdog_prediction_confidence_count[5m])
```

**HTTP requests by status code:**
```promql
sum by (status) (rate(http_requests_total{job="catvsdog-api"}[5m]))
```

**Pod memory usage percentage:**
```promql
container_memory_usage_bytes{pod=~"catvsdog-api.*"} / container_spec_memory_limit_bytes{pod=~"catvsdog-api.*"} * 100
```

## Testing the Monitoring Setup

### Generate Test Traffic

```bash
# Port-forward to the application
kubectl port-forward -n catvsdog svc/catvsdog-api-service 8001:8001

# Make predictions using the web UI
open http://localhost:8001

# Or use curl to hit the health endpoint repeatedly
for i in {1..100}; do
  curl http://localhost:8001/health
  sleep 1
done
```

### Verify Metrics

```bash
# Check if metrics are being exposed
curl http://localhost:8001/metrics | grep catvsdog_

# You should see output like:
# catvsdog_predictions_total{prediction_class="cat"} 45.0
# catvsdog_predictions_total{prediction_class="dog"} 55.0
# catvsdog_prediction_latency_seconds_bucket{le="0.1"} 80.0
```

## Troubleshooting

### Prometheus Not Scraping Targets

1. Check if pods have the correct annotations:
```bash
kubectl get pods -n catvsdog -o yaml | grep -A 3 annotations
```

2. Check Prometheus targets:
- Go to http://localhost:30090/targets
- Look for `catvsdog-api` job
- Check if targets are "UP"

3. Check logs:
```bash
kubectl logs -n monitoring deployment/prometheus
```

### Grafana Dashboard Not Showing Data

1. Verify Prometheus datasource:
- Go to Grafana → Configuration → Data Sources
- Test the Prometheus connection

2. Check if metrics are available in Prometheus:
- Go to Prometheus UI
- Run query: `catvsdog_predictions_total`

3. Check Grafana logs:
```bash
kubectl logs -n monitoring deployment/grafana
```

### Metrics Not Being Generated

1. Verify the application is instrumented:
```bash
curl http://localhost:8001/metrics
```

2. Make some predictions to generate metrics:
- Upload images through the web UI at http://localhost:8001

3. Check application logs:
```bash
kubectl logs -n catvsdog deployment/catvsdog-api
```

## Best Practices

### 1. Alerting

- Configure AlertManager for email/Slack notifications
- Set appropriate thresholds based on SLOs
- Use alert severity levels (critical, warning, info)

### 2. Data Retention

- Adjust Prometheus retention based on storage capacity
- Consider using remote storage for long-term metrics
- Archive important metrics to external systems

### 3. Dashboard Organization

- Create separate dashboards for different personas (ops, data science, business)
- Use variables for filtering by pod, namespace, etc.
- Set appropriate time ranges and refresh intervals

### 4. Performance Optimization

- Use recording rules for frequently queried metrics
- Adjust scrape intervals based on metric importance
- Set appropriate resource limits for Prometheus and Grafana

### 5. Security

- Change default Grafana admin password
- Use RBAC to control access to dashboards
- Enable authentication for Prometheus if exposed externally
- Use secrets for sensitive configuration

## Integration with CI/CD

### Adding Monitoring to Deployment Pipeline

```bash
#!/bin/bash
# deploy-with-monitoring.sh

# Deploy application
kubectl apply -f k8s/deployment.yaml

# Wait for rollout
kubectl rollout status -n catvsdog deployment/catvsdog-api

# Verify metrics endpoint
kubectl port-forward -n catvsdog svc/catvsdog-api-service 8001:8001 &
PF_PID=$!
sleep 5

# Check if metrics are available
curl -f http://localhost:8001/metrics || exit 1

# Kill port-forward
kill $PF_PID

# Run smoke tests and monitor metrics
# Add your smoke tests here

echo "Deployment successful and metrics are being collected"
```

## Advanced Configuration

### Custom Metrics

To add custom metrics to your application:

```python
from prometheus_client import Counter, Histogram

# Define custom metric
model_drift_score = Gauge(
    'catvsdog_model_drift_score',
    'Score indicating model drift from training distribution'
)

# Update metric
model_drift_score.set(calculate_drift_score())
```

### External Metrics

To scrape metrics from external sources:

```yaml
# Add to prometheus-config.yaml
- job_name: 'external-service'
  static_configs:
    - targets: ['external-service.example.com:9090']
```

### Recording Rules

For frequently used complex queries:

```yaml
# Add to prometheus-config.yaml under rule_files
groups:
  - name: catvsdog_recording_rules
    interval: 30s
    rules:
      - record: catvsdog:prediction_success_rate:5m
        expr: |
          (
            rate(catvsdog_predictions_total[5m]) -
            rate(catvsdog_image_processing_errors_total[5m])
          ) / rate(catvsdog_predictions_total[5m])
```

## Production Considerations

### High Availability

- Run multiple Prometheus replicas with Thanos for HA
- Use Grafana clustering for redundancy
- Store metrics in remote storage (e.g., Thanos, Cortex, M3DB)

### Scalability

- Use federation for large-scale deployments
- Implement metric relabeling to reduce cardinality
- Use horizontal pod autoscaling based on metrics

### Backup and Disaster Recovery

```bash
# Backup Grafana dashboards
kubectl get configmap -n monitoring grafana-dashboard-catvsdog -o yaml > backup/grafana-dashboard.yaml

# Backup Prometheus configuration
kubectl get configmap -n monitoring prometheus-config -o yaml > backup/prometheus-config.yaml
```

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)

## Support

For issues and questions:
- Check the troubleshooting section above
- Review Prometheus and Grafana logs
- Consult the official documentation
- Open an issue in the project repository
