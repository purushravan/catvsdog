#!/bin/bash

# Stop Port-Forwarding for Cat vs Dog Services

echo "Stopping port-forwarding..."

# Read PIDs from file if exists
if [ -f /tmp/catvsdog-pf-pids.txt ]; then
    PIDS=$(cat /tmp/catvsdog-pf-pids.txt)
    for PID in $PIDS; do
        if ps -p $PID > /dev/null 2>&1; then
            echo "  Stopping PID: $PID"
            kill $PID 2>/dev/null || true
        fi
    done
    rm /tmp/catvsdog-pf-pids.txt
fi

# Also kill by name pattern
pkill -f "port-forward.*catvsdog" 2>/dev/null || true
pkill -f "port-forward.*prometheus" 2>/dev/null || true
pkill -f "port-forward.*grafana" 2>/dev/null || true

echo "✓ All port-forwards stopped"
