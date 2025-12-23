# Monitoring Metrics Reference

## 🎯 Quick Metrics Reference

### ML Model Metrics

#### catvsdog_predictions_total
- **Type**: Counter
- **Labels**: `prediction_class` (cat, dog)
- **Description**: Total number of predictions made
- **Example Query**: `rate(catvsdog_predictions_total[5m])`
- **Use Cases**:
  - Monitor prediction volume
  - Track class distribution
  - Detect traffic anomalies
  - Calculate prediction ratios

#### catvsdog_prediction_confidence
- **Type**: Histogram
- **Buckets**: 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0
- **Description**: Distribution of prediction confidence scores
- **Example Query**: `histogram_quantile(0.95, rate(catvsdog_prediction_confidence_bucket[5m]))`
- **Use Cases**:
  - Monitor model confidence
  - Detect model drift
  - Identify low-confidence predictions
  - Track model degradation

#### catvsdog_prediction_latency_seconds
- **Type**: Histogram
- **Buckets**: 0.1, 0.25, 0.5, 0.75, 1.0, 2.0, 5.0
- **Description**: Time taken for model inference
- **Example Query**: `histogram_quantile(0.99, rate(catvsdog_prediction_latency_seconds_bucket[5m]))`
- **Use Cases**:
  - Monitor inference performance
  - Detect performance regression
  - Identify slow predictions
  - Plan resource scaling

#### catvsdog_image_processing_errors_total
- **Type**: Counter
- **Labels**: None
- **Description**: Total number of image processing errors
- **Example Query**: `rate(catvsdog_image_processing_errors_total[5m])`
- **Use Cases**:
  - Monitor data quality issues
  - Track error rates
  - Alert on high failure rates
  - Debug preprocessing issues

#### catvsdog_active_predictions
- **Type**: Gauge
- **Labels**: None
- **Description**: Number of predictions currently being processed
- **Example Query**: `catvsdog_active_predictions`
- **Use Cases**:
  - Monitor concurrency
  - Detect stuck requests
  - Plan scaling strategies
  - Track load patterns

#### catvsdog_model_info
- **Type**: Info
- **Labels**: `version`, `api_version`
- **Description**: Metadata about deployed model
- **Example Query**: `catvsdog_model_info`
- **Use Cases**:
  - Track model versions
  - Verify deployments
  - Audit model lineage
  - Correlate versions with performance

---

## 📊 Example Dashboards

### Real-Time Monitoring Dashboard

```
┌────────────────────────────────────────────────────────────────┐
│  Cat vs Dog ML Model - Real-Time Monitoring                    │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Prediction Rate                       Total Predictions        │
│  ┌─────────────────────┐              ┌──────────────────┐    │
│  │    Cat: 45/s        │              │  Cat: 45,231     │    │
│  │    Dog: 55/s        │              │  Dog: 54,769     │    │
│  │    Total: 100/s     │              │  Total: 100,000  │    │
│  └─────────────────────┘              └──────────────────┘    │
│                                                                 │
│  Prediction Latency                    Confidence Score        │
│  ┌─────────────────────┐              ┌──────────────────┐    │
│  │  p50: 0.15s         │              │  p50: 0.92       │    │
│  │  p95: 0.45s         │              │  p95: 0.98       │    │
│  │  p99: 0.78s         │              │  p99: 0.99       │    │
│  └─────────────────────┘              └──────────────────┘    │
│                                                                 │
│  Active Predictions     Error Rate     API Uptime             │
│  ┌──────────────┐     ┌──────────┐    ┌───────────────┐     │
│  │      5       │     │  0.01/s  │    │   100% UP     │     │
│  └──────────────┘     └──────────┘    └───────────────┘     │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Model Performance Dashboard

```
┌────────────────────────────────────────────────────────────────┐
│  Model Performance Analysis - Last 24 Hours                    │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Confidence Distribution                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │     ▁▂▃▄▅▆▇███████████████████▇▆▅▄▃▂▁                  │  │
│  │  0.5  0.6  0.7  0.8  0.9  1.0                           │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Latency Percentiles Over Time                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  1.0s ┤               ┌─p99                             │  │
│  │  0.8s ┤          ┌────┘                                 │  │
│  │  0.5s ┤     ┌────┘  ─p95                                │  │
│  │  0.3s ┤─────────────────p50                             │  │
│  │       └───────────────────────────────────────────────▶ │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Class Distribution                                            │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Cat: █████████████████████████ 45%                     │  │
│  │  Dog: ██████████████████████████████ 55%                │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔔 Alert Examples

### Critical: API Down
```yaml
alert: APIDown
expr: up{job="catvsdog-api"} == 0
for: 2m
severity: critical
description: "API pod {{ $labels.pod }} is down"
```

**When to expect**: Pod crashes, deployment issues, health check failures

**Action items**:
1. Check pod logs: `kubectl logs -n catvsdog <pod-name>`
2. Check pod events: `kubectl describe pod -n catvsdog <pod-name>`
3. Verify resource limits
4. Check application startup logs

---

### Warning: High Error Rate
```yaml
alert: HighPredictionErrorRate
expr: rate(catvsdog_image_processing_errors_total[5m]) > 0.1
for: 5m
severity: warning
description: "Error rate is {{ $value }} errors/sec"
```

**When to expect**: Bad input data, corrupted images, preprocessing issues

**Action items**:
1. Check recent predictions for error patterns
2. Verify image format/quality
3. Review application logs for stack traces
4. Check if specific users/sources have issues

---

### Warning: High Latency
```yaml
alert: HighPredictionLatency
expr: histogram_quantile(0.95, rate(catvsdog_prediction_latency_seconds_bucket[5m])) > 2
for: 5m
severity: warning
description: "95th percentile latency is {{ $value }}s"
```

**When to expect**: High load, resource contention, model complexity

**Action items**:
1. Check CPU/memory usage
2. Verify concurrent requests
3. Consider horizontal scaling
4. Review model optimization opportunities

---

### Info: Low Confidence
```yaml
alert: LowConfidencePredictions
expr: histogram_quantile(0.50, rate(catvsdog_prediction_confidence_bucket[10m])) < 0.7
for: 10m
severity: info
description: "Median confidence is {{ $value }}"
```

**When to expect**: Model drift, unusual input distribution, edge cases

**Action items**:
1. Review recent predictions
2. Check for data distribution changes
3. Consider model retraining
4. Analyze low-confidence examples

---

## 📈 Common Queries

### Calculate Success Rate
```promql
(
  sum(rate(catvsdog_predictions_total[5m])) -
  rate(catvsdog_image_processing_errors_total[5m])
) / sum(rate(catvsdog_predictions_total[5m])) * 100
```

### Cat vs Dog Ratio
```promql
sum(rate(catvsdog_predictions_total{prediction_class="cat"}[5m])) /
sum(rate(catvsdog_predictions_total{prediction_class="dog"}[5m]))
```

### Average Confidence by Class
```promql
avg by (prediction_class) (
  rate(catvsdog_prediction_confidence_sum[5m]) /
  rate(catvsdog_prediction_confidence_count[5m])
)
```

### Requests per Minute
```promql
sum(rate(catvsdog_predictions_total[1m])) * 60
```

### Error Percentage
```promql
rate(catvsdog_image_processing_errors_total[5m]) /
sum(rate(catvsdog_predictions_total[5m])) * 100
```

---

## 🎨 Visualization Tips

### Graph Types by Metric

| Metric | Best Visualization | Why |
|--------|-------------------|-----|
| Prediction Rate | Line graph | Shows trends over time |
| Total Predictions | Stat panel | Single number for current total |
| Latency | Multi-line graph | Compare percentiles (p50, p95, p99) |
| Confidence | Histogram | Shows distribution |
| Active Predictions | Gauge | Current value, not historical |
| Errors | Line graph with alert threshold | Spot anomalies |
| Class Distribution | Pie chart or bar chart | Compare proportions |
| API Status | Single stat with thresholds | Up/Down indicator |

### Color Schemes

- **Green**: Normal operation (confidence > 0.8, latency < 0.5s)
- **Yellow**: Warning (confidence 0.6-0.8, latency 0.5-1s)
- **Red**: Critical (confidence < 0.6, latency > 1s)

### Time Ranges

- **Real-time monitoring**: Last 5-15 minutes, auto-refresh 10s
- **Recent analysis**: Last 1-6 hours
- **Daily review**: Last 24 hours
- **Trend analysis**: Last 7-30 days

---

## 🔍 Debugging with Metrics

### Scenario 1: Slow Predictions

**Symptoms**: High latency alerts, user complaints

**Queries to run**:
```promql
# Check latency percentiles
histogram_quantile(0.50, rate(catvsdog_prediction_latency_seconds_bucket[5m]))
histogram_quantile(0.95, rate(catvsdog_prediction_latency_seconds_bucket[5m]))
histogram_quantile(0.99, rate(catvsdog_prediction_latency_seconds_bucket[5m]))

# Check if it's load-related
catvsdog_active_predictions
rate(catvsdog_predictions_total[5m])

# Check resource usage
container_cpu_usage_seconds_total{pod=~"catvsdog-api.*"}
container_memory_usage_bytes{pod=~"catvsdog-api.*"}
```

**Diagnosis**:
- If all percentiles high → System-wide issue (CPU, memory)
- If only p99 high → Occasional outliers (GC, network)
- If active predictions high → Concurrency limit reached

---

### Scenario 2: Model Drift

**Symptoms**: Low confidence alerts, changing class distribution

**Queries to run**:
```promql
# Check confidence trends
rate(catvsdog_prediction_confidence_sum[5m]) /
rate(catvsdog_prediction_confidence_count[5m])

# Check class distribution changes
rate(catvsdog_predictions_total{prediction_class="cat"}[1h]) /
rate(catvsdog_predictions_total{prediction_class="dog"}[1h])

# Compare to baseline (7 days ago)
rate(catvsdog_predictions_total{prediction_class="cat"}[1h] offset 7d) /
rate(catvsdog_predictions_total{prediction_class="dog"}[1h] offset 7d)
```

**Diagnosis**:
- Sudden drop in confidence → Model drift or new data patterns
- Changed class ratio → Input distribution shift
- Gradual decline → Model degradation over time

---

### Scenario 3: High Error Rate

**Symptoms**: Error rate alerts, failed predictions

**Queries to run**:
```promql
# Error rate
rate(catvsdog_image_processing_errors_total[5m])

# Error percentage
rate(catvsdog_image_processing_errors_total[5m]) /
sum(rate(catvsdog_predictions_total[5m])) * 100

# Correlate with traffic
rate(http_requests_total[5m])
```

**Diagnosis**:
- Consistent error rate → Systematic issue (bad data source)
- Spike in errors → Specific event (new data format, corrupted batch)
- Errors with specific endpoint → Integration issue

---

## 📊 Metric Cardinality

### Current Cardinality

| Metric | Labels | Approximate Series |
|--------|--------|-------------------|
| catvsdog_predictions_total | 1 (prediction_class: 2 values) | 2 |
| catvsdog_prediction_confidence | 0 (histogram: 8 buckets) | 10 |
| catvsdog_prediction_latency_seconds | 0 (histogram: 7 buckets) | 9 |
| catvsdog_image_processing_errors_total | 0 | 1 |
| catvsdog_active_predictions | 0 | 1 |
| catvsdog_model_info | 2 (version, api_version) | 1 |
| **Total** | | **~24 series** |

**Note**: Low cardinality means efficient storage and fast queries!

---

## 💡 Best Practices

### 1. Naming Conventions
- **Prefix**: All metrics start with `catvsdog_`
- **Suffix**: Use `_total` for counters, `_seconds` for time
- **Snake_case**: Use underscores, not camelCase

### 2. Label Usage
- **Good labels**: prediction_class (low cardinality, meaningful)
- **Bad labels**: user_id (high cardinality), timestamp (unbounded)
- **Rule**: Keep label cardinality < 100 values per label

### 3. Histogram Buckets
- **Latency**: 0.1, 0.25, 0.5, 0.75, 1.0, 2.0, 5.0 (covers typical ranges)
- **Confidence**: 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0 (focuses on high confidence)
- **Rule**: Design buckets around expected value distribution

### 4. Query Optimization
- **Use rate()**: For counters, always use `rate()` or `irate()`
- **Choose window**: Larger windows (5m) for smoothing, smaller (1m) for real-time
- **Avoid regex**: Use exact matches when possible
- **Recording rules**: Pre-compute expensive queries

---

## 🎓 Learning Resources

- **PromQL**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Histograms**: https://prometheus.io/docs/practices/histograms/
- **Metric Types**: https://prometheus.io/docs/concepts/metric_types/
- **Best Practices**: https://prometheus.io/docs/practices/naming/

---

**Happy Monitoring!** 📊
