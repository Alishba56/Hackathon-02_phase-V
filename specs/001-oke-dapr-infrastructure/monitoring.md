# Monitoring and Observability Strategy

**Date**: 2026-02-09
**Feature**: Oracle OKE Dapr Infrastructure Integration
**Branch**: `001-oke-dapr-infrastructure`

## Overview

This document describes the monitoring and observability strategy for the Phase V Todo AI Chatbot deployment on Oracle OKE with Dapr runtime. The strategy focuses on practical, cost-effective observability using built-in Kubernetes tools, Dapr dashboard, and AI-powered cluster analysis.

## Observability Pillars

### 1. Logs
Structured application and infrastructure logs for debugging and audit trails.

### 2. Metrics
Performance and health metrics for proactive monitoring and capacity planning.

### 3. Traces
Distributed tracing for understanding request flow across services and Dapr components.

## Logging Strategy

### Application Logs

#### Log Structure

All application logs follow structured JSON format:

```json
{
  "timestamp": "2026-02-09T10:00:00.123Z",
  "level": "INFO",
  "service": "backend",
  "trace_id": "abc123def456",
  "span_id": "789ghi012jkl",
  "user_id": "user-456",
  "task_id": "task-789",
  "event_id": "evt-xyz",
  "message": "Task created successfully",
  "duration_ms": 45,
  "metadata": {
    "endpoint": "/api/user-456/tasks",
    "method": "POST",
    "status_code": 201
  }
}
```

#### Log Levels

| Level | Usage | Examples |
|-------|-------|----------|
| DEBUG | Development debugging | Variable values, function entry/exit |
| INFO | Normal operations | Task created, user logged in, event published |
| WARNING | Recoverable issues | Retry attempt, deprecated API usage |
| ERROR | Operation failures | Database connection failed, API error |
| CRITICAL | System failures | Service unavailable, data corruption |

#### Backend Logging Implementation

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)

        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(self._json_formatter())
        self.logger.addHandler(handler)

    def _json_formatter(self):
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "level": record.levelname,
                    "service": record.name,
                    "message": record.getMessage(),
                }
                # Add trace context if available
                if hasattr(record, 'trace_id'):
                    log_data['trace_id'] = record.trace_id
                if hasattr(record, 'user_id'):
                    log_data['user_id'] = record.user_id
                return json.dumps(log_data)
        return JSONFormatter()

    def info(self, message: str, **kwargs):
        extra = {k: v for k, v in kwargs.items()}
        self.logger.info(message, extra=extra)

# Usage
logger = StructuredLogger("backend")
logger.info("Task created", user_id="user-456", task_id="task-789")
```

### Dapr Sidecar Logs

Dapr sidecars automatically log all operations:

```json
{
  "time": "2026-02-09T10:00:00.123Z",
  "level": "info",
  "type": "log",
  "scope": "dapr.runtime.http",
  "msg": "HTTP API Called",
  "app_id": "backend",
  "instance": "backend-abc123-xyz",
  "method": "POST",
  "path": "/v1.0/publish/kafka-pubsub/task-events",
  "status": 200,
  "duration": "45ms"
}
```

### Log Access Commands

#### View Application Logs

```bash
# Frontend logs
kubectl logs -l app=frontend -c frontend --tail=100 -f

# Backend logs
kubectl logs -l app=backend -c backend --tail=100 -f

# All backend pods
kubectl logs -l app=backend -c backend --all-containers=true
```

#### View Dapr Sidecar Logs

```bash
# Dapr sidecar for backend
kubectl logs -l app=backend -c daprd --tail=100 -f

# Dapr sidecar for frontend
kubectl logs -l app=frontend -c daprd --tail=100 -f
```

#### View Dapr Control Plane Logs

```bash
# Dapr operator
kubectl logs -l app=dapr-operator -n dapr-system --tail=100 -f

# Dapr sidecar injector
kubectl logs -l app=dapr-sidecar-injector -n dapr-system --tail=100 -f

# Dapr placement
kubectl logs -l app=dapr-placement -n dapr-system --tail=100 -f
```

#### Filter Logs by Pattern

```bash
# Find errors in backend logs
kubectl logs -l app=backend -c backend | grep -i error

# Find specific user's operations
kubectl logs -l app=backend -c backend | grep "user-456"

# Find event publishing logs
kubectl logs -l app=backend -c daprd | grep "publish"
```

### Log Aggregation (Optional)

For production environments, consider log aggregation:

**Option 1: Loki + Grafana** (Lightweight)
```bash
# Install Loki stack
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  --set grafana.enabled=true \
  --set promtail.enabled=true
```

**Option 2: ELK Stack** (Full-featured)
- Elasticsearch for storage
- Logstash for processing
- Kibana for visualization

## Metrics Strategy

### Dapr Metrics

Dapr sidecars expose Prometheus-compatible metrics on port 9090:

**Key Metrics**:
- `dapr_http_server_request_count` - Total HTTP requests
- `dapr_http_server_request_duration_ms` - Request latency
- `dapr_component_loaded` - Component health status
- `dapr_pubsub_ingress_count` - Events published
- `dapr_pubsub_egress_count` - Events consumed

### Application Metrics

**Backend Metrics** (FastAPI with Prometheus client):

```python
from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import make_asgi_app

# Define metrics
task_operations = Counter(
    'todo_task_operations_total',
    'Total task operations',
    ['operation', 'status']
)

event_publish_duration = Histogram(
    'todo_event_publish_duration_seconds',
    'Event publishing duration',
    ['topic']
)

active_users = Gauge(
    'todo_active_users',
    'Number of active users'
)

# Add metrics endpoint to FastAPI
from fastapi import FastAPI
app = FastAPI()
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Use metrics
task_operations.labels(operation='create', status='success').inc()
```

### Resource Metrics

```bash
# Pod resource usage
kubectl top pods

# Node resource usage
kubectl top nodes

# Detailed pod metrics
kubectl describe pod <pod-name> | grep -A 5 "Limits\|Requests"
```

### Dapr Dashboard

Deploy and access Dapr dashboard for visual metrics:

```bash
# Deploy Dapr dashboard
dapr dashboard -k

# Access at http://localhost:8080
# Shows:
# - Component health status
# - Sidecar metrics
# - Configuration overview
# - Logs aggregation
```

**Dashboard Features**:
- Real-time component status
- Sidecar health checks
- Metrics visualization
- Log streaming
- Configuration inspection

## Tracing Strategy

### Distributed Tracing with Dapr

Dapr automatically injects trace headers for distributed tracing:

**W3C Trace Context Headers**:
- `traceparent`: `00-<trace-id>-<span-id>-<flags>`
- `tracestate`: Additional vendor-specific data

### Application Trace Propagation

```python
from fastapi import Request, Response

@app.post("/api/{user_id}/tasks")
async def create_task(user_id: str, request: Request):
    # Extract trace context from Dapr headers
    trace_id = request.headers.get("traceparent", "").split("-")[1]

    # Log with trace context
    logger.info(
        "Creating task",
        trace_id=trace_id,
        user_id=user_id
    )

    # Propagate trace context to Dapr Pub/Sub
    headers = {
        "traceparent": request.headers.get("traceparent"),
        "tracestate": request.headers.get("tracestate")
    }

    # Publish event with trace context
    response = requests.post(
        "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
        json=event_data,
        headers=headers
    )

    return {"status": "created", "trace_id": trace_id}
```

### Trace Visualization (Optional)

**Jaeger Integration**:
```bash
# Install Jaeger
kubectl apply -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/deploy/crds/jaegertracing.io_jaegers_crd.yaml
kubectl apply -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/deploy/operator.yaml

# Configure Dapr to use Jaeger
kubectl apply -f - <<EOF
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://jaeger-collector:9411/api/v2/spans"
EOF
```

## AI-Powered Cluster Analysis

### kubectl-ai

**Installation**:
```bash
# Install kubectl-ai
kubectl krew install ai

# Configure OpenAI API key (or use local model)
export OPENAI_API_KEY=<your-key>
```

**Usage Examples**:

```bash
# Analyze cluster health
kubectl ai "analyze cluster health"

# Diagnose pod issues
kubectl ai "why is backend pod pending?"

# Optimize resources
kubectl ai "optimize deployment backend for cost"

# Troubleshoot networking
kubectl ai "why can't frontend reach backend?"

# Generate manifests
kubectl ai "create a deployment for nginx with 3 replicas"
```

### kagent

**Installation**:
```bash
# Install kagent
pip install kagent

# Or use Docker
docker run -v ~/.kube:/root/.kube kagent/kagent
```

**Usage Examples**:

```bash
# Cluster health analysis
kagent analyze cluster

# Pod debugging
kagent debug pod backend-abc123-xyz

# Log analysis
kagent logs backend --analyze --last 1h

# Resource optimization
kagent optimize deployment backend

# Security audit
kagent security scan

# Cost analysis
kagent cost analyze
```

**Sample Output**:
```
🔍 Analyzing cluster health...

✅ Cluster Status: Healthy
   - Nodes: 2/2 Ready
   - Pods: 8/8 Running
   - Services: 4/4 Active

⚠️  Warnings:
   - backend pod using 85% of memory limit
   - frontend pod has 3 restarts in last 24h

💡 Recommendations:
   1. Increase backend memory limit to 1.5Gi
   2. Investigate frontend restart cause (check logs)
   3. Consider adding HPA for backend (high CPU usage)

📊 Resource Utilization:
   - CPU: 2.1/4.0 OCPU (52%)
   - Memory: 16.5/24.0 GB (69%)
   - Storage: 45/100 GB (45%)
```

## Health Checks

### Application Health Endpoints

**Backend Health Endpoint**:
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/ready")
async def readiness_check():
    # Check dependencies
    db_healthy = await check_database()
    dapr_healthy = await check_dapr()

    if db_healthy and dapr_healthy:
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Not ready")
```

**Frontend Health Endpoint**:
```typescript
// pages/api/health.ts
export default function handler(req, res) {
  res.status(200).json({
    status: 'healthy',
    service: 'frontend',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
}
```

### Kubernetes Probes

**Liveness Probe** (Is the container alive?):
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 3
```

**Readiness Probe** (Is the container ready to serve traffic?):
```yaml
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  successThreshold: 1
  failureThreshold: 3
```

### Dapr Health Checks

```bash
# Check Dapr sidecar health
curl http://localhost:3500/v1.0/healthz

# Check Dapr component health
kubectl get components
kubectl describe component kafka-pubsub
```

## Alerting Strategy

### Basic Alerting (kubectl-ai/kagent)

Set up periodic health checks:

```bash
#!/bin/bash
# health-check.sh

# Run kagent analysis
REPORT=$(kagent analyze cluster --json)

# Check for critical issues
CRITICAL=$(echo $REPORT | jq '.critical_issues | length')

if [ $CRITICAL -gt 0 ]; then
  echo "🚨 Critical issues detected!"
  echo $REPORT | jq '.critical_issues'
  # Send notification (email, Slack, etc.)
fi
```

### Advanced Alerting (Optional - Prometheus + Alertmanager)

**Alert Rules**:
```yaml
groups:
- name: todo-app-alerts
  rules:
  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.pod }}"

  - alert: PodCrashLooping
    expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Pod {{ $labels.pod }} is crash looping"

  - alert: DaprComponentUnhealthy
    expr: dapr_component_loaded == 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Dapr component {{ $labels.component }} is unhealthy"
```

## Troubleshooting Runbook

### Common Issues and Diagnosis

#### Issue 1: Pod Not Starting

**Symptoms**:
```bash
kubectl get pods
# NAME                        READY   STATUS             RESTARTS
# backend-abc123-xyz          0/2     CrashLoopBackOff   5
```

**Diagnosis**:
```bash
# Check pod events
kubectl describe pod backend-abc123-xyz

# Check application logs
kubectl logs backend-abc123-xyz -c backend

# Check Dapr sidecar logs
kubectl logs backend-abc123-xyz -c daprd

# Use AI analysis
kagent debug pod backend-abc123-xyz
```

**Common Causes**:
- Missing environment variables
- Database connection failure
- Dapr component misconfiguration
- Image pull errors

#### Issue 2: High Latency

**Symptoms**:
- Slow API responses (>2s)
- Timeout errors

**Diagnosis**:
```bash
# Check resource usage
kubectl top pods

# Check Dapr metrics
curl http://localhost:9090/metrics | grep duration

# Analyze logs for slow operations
kubectl logs -l app=backend -c backend | grep "duration_ms"

# Use AI analysis
kubectl ai "why is backend slow?"
```

**Common Causes**:
- Resource constraints (CPU/memory)
- Database query performance
- Network latency to external services
- Dapr component overhead

#### Issue 3: Event Not Publishing

**Symptoms**:
- Events not appearing in Kafka
- No consumer processing

**Diagnosis**:
```bash
# Check Dapr Pub/Sub component
kubectl get component kafka-pubsub
kubectl describe component kafka-pubsub

# Check Dapr sidecar logs
kubectl logs -l app=backend -c daprd | grep pubsub

# Check Kafka connectivity
kubectl exec -it backend-abc123-xyz -c daprd -- curl http://localhost:3500/v1.0/healthz

# Use AI analysis
kagent logs backend --analyze --filter "publish"
```

**Common Causes**:
- Kafka credentials incorrect
- Network connectivity to Redpanda Cloud
- Topic doesn't exist
- Dapr component not loaded

#### Issue 4: Secrets Not Accessible

**Symptoms**:
- Application errors: "API key not found"
- 500 errors on authenticated endpoints

**Diagnosis**:
```bash
# Check secrets exist
kubectl get secret app-secrets

# Check secret contents (base64 encoded)
kubectl get secret app-secrets -o yaml

# Check Dapr secrets component
kubectl get component kubernetes-secrets
kubectl describe component kubernetes-secrets

# Test secret access via Dapr
kubectl exec -it backend-abc123-xyz -c backend -- \
  curl http://localhost:3500/v1.0/secrets/kubernetes-secrets/app-secrets
```

**Common Causes**:
- Secret not created
- Secret in wrong namespace
- Dapr component misconfigured
- RBAC permissions missing

## Monitoring Dashboard

### Dapr Dashboard Access

```bash
# Port-forward Dapr dashboard
kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080

# Access at http://localhost:8080
```

**Dashboard Sections**:
1. **Overview**: Cluster summary, component count, sidecar count
2. **Applications**: List of Dapr-enabled apps with health status
3. **Components**: Component types, status, metadata
4. **Configurations**: Dapr configurations and features
5. **Control Plane**: Dapr system services status

### Custom Grafana Dashboard (Optional)

**Metrics to Track**:
- Request rate (requests/second)
- Error rate (errors/total requests)
- Latency (p50, p95, p99)
- Resource usage (CPU, memory)
- Event throughput (events/second)
- Dapr component health

## Performance Baselines

### Expected Metrics

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| API Response Time (p95) | <500ms | >1s | >2s |
| Event Publishing Latency | <50ms | >100ms | >200ms |
| Pod Memory Usage | <70% | >85% | >95% |
| Pod CPU Usage | <60% | >80% | >90% |
| Pod Restart Count | 0 | >3/day | >10/day |
| Dapr Sidecar Memory | <128MB | >200MB | >256MB |

### Capacity Planning

**Current Capacity** (OKE Always-Free Tier):
- Total: 4 OCPU, 24GB RAM
- Available for apps: ~2.5 OCPU, ~18GB RAM

**Resource Allocation**:
- Frontend (1 replica): 0.5 OCPU, 512MB RAM
- Backend (1 replica): 1 OCPU, 1GB RAM
- Dapr sidecars (2): 0.4 OCPU, 512MB RAM
- System overhead: 0.6 OCPU, 1GB RAM

**Scaling Limits**:
- Max frontend replicas: 3
- Max backend replicas: 2
- Total max pods: ~8-10 (including system pods)

---

**Monitoring Strategy Status**: ✅ Complete - Ready for Implementation
**Next Steps**: Create quickstart deployment guide
