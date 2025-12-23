#!/bin/bash

# Start Port-Forwarding for Cat vs Dog Services
# This script sets up port-forwarding for all services

set -e

echo "=========================================="
echo "Cat vs Dog - Service Access Helper"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Kill existing port-forwards
echo "Cleaning up existing port-forwards..."
pkill -f "port-forward.*catvsdog" 2>/dev/null || true
pkill -f "port-forward.*prometheus" 2>/dev/null || true
pkill -f "port-forward.*grafana" 2>/dev/null || true
sleep 2

# Check if services exist
echo "Checking service status..."
if ! kubectl get svc -n catvsdog catvsdog-api-service &> /dev/null; then
    echo "❌ Application service not found. Deploy the application first:"
    echo "   kubectl apply -f k8s/"
    exit 1
fi

if ! kubectl get svc -n monitoring prometheus &> /dev/null; then
    echo "❌ Prometheus service not found. Deploy monitoring first:"
    echo "   ./deploy-monitoring.sh"
    exit 1
fi

echo "✓ All services found"
echo ""

# Start port-forwarding
echo "Starting port-forwarding..."

echo "  → Cat vs Dog API (localhost:8001)"
kubectl port-forward -n catvsdog svc/catvsdog-api-service 8001:8001 > /tmp/pf-catvsdog.log 2>&1 &
APP_PID=$!
sleep 2

echo "  → Prometheus (localhost:9090)"
kubectl port-forward -n monitoring svc/prometheus 9090:9090 > /tmp/pf-prometheus.log 2>&1 &
PROM_PID=$!
sleep 2

echo "  → Grafana (localhost:3000)"
kubectl port-forward -n monitoring svc/grafana 3000:3000 > /tmp/pf-grafana.log 2>&1 &
GRAF_PID=$!
sleep 3

# Test connections
echo ""
echo "Testing connections..."

if curl -s -m 5 http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Cat vs Dog API: http://localhost:8001"
else
    echo -e "  ${YELLOW}⚠${NC} Cat vs Dog API: Connection failed"
fi

if curl -s -m 5 http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Prometheus: http://localhost:9090"
else
    echo -e "  ${YELLOW}⚠${NC} Prometheus: Connection failed"
fi

if curl -s -m 5 http://localhost:3000/api/health > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Grafana: http://localhost:3000"
else
    echo -e "  ${YELLOW}⚠${NC} Grafana: Connection failed"
fi

echo ""
echo "=========================================="
echo "Access URLs"
echo "=========================================="
echo ""
echo "Cat vs Dog API:"
echo "  Web UI:    http://localhost:8001"
echo "  Health:    http://localhost:8001/health"
echo "  Metrics:   http://localhost:8001/metrics"
echo ""
echo "Prometheus:"
echo "  Web UI:    http://localhost:9090"
echo "  Targets:   http://localhost:9090/targets"
echo "  Alerts:    http://localhost:9090/alerts"
echo ""
echo "Grafana:"
echo "  Web UI:    http://localhost:3000"
echo "  Username:  admin"
echo "  Password:  admin"
echo "  Dashboard: Dashboards → Cat vs Dog ML Model Monitoring"
echo ""
echo "=========================================="
echo "Port-forwarding is running in background"
echo "=========================================="
echo ""
echo "Process IDs:"
echo "  - App:        $APP_PID"
echo "  - Prometheus: $PROM_PID"
echo "  - Grafana:    $GRAF_PID"
echo ""
echo "To stop port-forwarding, run:"
echo "  kill $APP_PID $PROM_PID $GRAF_PID"
echo ""
echo "Or use: ./stop-services.sh"
echo ""

# Save PIDs to file for cleanup
echo "$APP_PID $PROM_PID $GRAF_PID" > /tmp/catvsdog-pf-pids.txt

echo "✓ Port-forwarding is active. Services are accessible!"
echo ""
