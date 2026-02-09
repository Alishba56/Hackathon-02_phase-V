# Dapr Integration Guide

**Purpose**: Guide for integrating Dapr runtime with the Todo AI Chatbot application for event-driven architecture and cloud-native service abstraction.

## Overview

Dapr (Distributed Application Runtime) provides building blocks for microservices, enabling:
- **Pub/Sub**: Event publishing to Kafka via unified API
- **State Management**: Conversation state persistence in PostgreSQL
- **Secrets Management**: Secure access to Kubernetes Secrets
- **Service Invocation**: Service-to-service communication with mTLS
- **Scheduler/Jobs**: Exact-time reminders without polling

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Application Pod (Backend)                                   │
│  ┌────────────────────┐      ┌─────────────────────────┐   │
│  │  FastAPI App       │◄────►│  Dapr Sidecar (daprd)   │   │
│  │  (Port 8000)       │      │  (Port 3500)            │   │
│  │                    │      │                         │   │
│  │  - Task Routes     │      │  - Pub/Sub API          │   │
│  │  - Event Publishing│      │  - State API            │   │
│  │  - State Access    │      │  - Secrets API          │   │
│  └────────────────────┘      └─────────┬───────────────┘   │
└────────────────────────────────────────┼───────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
         ┌──────────▼─────────┐  ┌──────▼──────┐  ┌────────▼────────┐
         │  Kafka/Redpanda    │  │  PostgreSQL │  │  K8s Secrets    │
         │  (Pub/Sub)         │  │  (State)    │  │  (Secrets)      │
         └────────────────────┘  └─────────────┘  └─────────────────┘
```

## Dapr Components

### 1. Kafka Pub/Sub Component

**File**: `infra/dapr-components/kafka-pubsub.yaml`

**Purpose**: Publish task events to Kafka topics

**Configuration**:
- Component name: `kafka-pubsub`
- Type: `pubsub.kafka`
- Broker: Redpanda Cloud serverless
- Authentication: SASL/SCRAM-SHA-256
- Topics: `task-events`, `task-updates`, `reminders`

**Usage in Application**:
```python
from services.dapr_client import DaprClient

dapr_client = DaprClient()

# Publish event
dapr_client.publish_event(
    topic="task-events",
    event_type="com.todo.task.created",
    data={
        "task_id": "task-123",
        "user_id": "user-456",
        "title": "Buy groceries"
    }
)
```

### 2. PostgreSQL State Store Component

**File**: `infra/dapr-components/state-postgresql.yaml`

**Purpose**: Store conversation state and application data

**Configuration**:
- Component name: `statestore`
- Type: `state.postgresql`
- Database: Neon Serverless PostgreSQL
- Table: `dapr_state` (auto-created)

**Usage in Application**:
```python
# Save state
dapr_client.save_state(
    store_name="statestore",
    key="conversation-123",
    value={"messages": [...], "context": {...}}
)

# Get state
state = dapr_client.get_state(
    store_name="statestore",
    key="conversation-123"
)
```

### 3. Kubernetes Secrets Component

**File**: `infra/dapr-components/secretstores-kubernetes.yaml`

**Purpose**: Access Kubernetes Secrets without direct environment variable exposure

**Configuration**:
- Component name: `kubernetes-secrets`
- Type: `secretstores.kubernetes`
- Scope: All services

**Usage in Application**:
```python
# Get secret
api_key = dapr_client.get_secret(
    secret_store="kubernetes-secrets",
    secret_key="cohere-api-key"
)
```

### 4. Scheduler/Jobs Component

**File**: `infra/dapr-components/scheduler-jobs.yaml`

**Purpose**: Schedule exact-time reminders

**Configuration**:
- Component name: `scheduler`
- Type: `scheduler.kubernetes`
- Uses Kubernetes CronJob resources

**Usage in Application**:
```python
import requests
from datetime import datetime, timedelta

# Schedule reminder
reminder_time = datetime.utcnow() + timedelta(hours=1)

job_data = {
    "schedule": reminder_time.isoformat() + "Z",
    "data": {
        "task_id": "task-789",
        "user_id": "user-456"
    }
}

requests.post(
    "http://localhost:3500/v1.0-alpha1/jobs/reminder-task-789",
    json=job_data
)
```

## Dapr Sidecar Configuration

### Deployment Annotations

Dapr sidecars are injected via Kubernetes annotations:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
        dapr.io/enable-metrics: "true"
```

**Annotation Descriptions**:
- `dapr.io/enabled`: Enable Dapr sidecar injection
- `dapr.io/app-id`: Unique application identifier
- `dapr.io/app-port`: Application HTTP port
- `dapr.io/log-level`: Dapr logging level (debug/info/warn/error)
- `dapr.io/enable-metrics`: Enable Prometheus metrics

### Sidecar Communication

Application communicates with Dapr sidecar via localhost:

- **HTTP API**: `http://localhost:3500`
- **gRPC API**: `localhost:50001`
- **Metrics**: `http://localhost:9090/metrics`

## Event Publishing Implementation

### CloudEvents Format

All events follow CloudEvents 1.0 specification:

```json
{
  "specversion": "1.0",
  "type": "com.todo.task.created",
  "source": "backend",
  "id": "evt-abc123",
  "time": "2026-02-09T10:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": "task-789",
    "user_id": "user-456",
    "title": "Buy groceries",
    "created_at": "2026-02-09T10:00:00Z"
  }
}
```

### Event Types

| Event Type | Topic | Description |
|------------|-------|-------------|
| `com.todo.task.created` | task-events | Task created |
| `com.todo.task.updated` | task-updates | Task modified |
| `com.todo.task.deleted` | task-events | Task deleted |
| `com.todo.task.completed` | task-events | Task marked complete |
| `com.todo.reminder.due` | reminders | Reminder triggered |

### Trace Context Propagation

Dapr automatically propagates W3C Trace Context:

```python
# Extract trace ID from request
trace_id = request.headers.get("traceparent", "").split("-")[1]

# Pass to Dapr for distributed tracing
dapr_client.publish_event(
    topic="task-events",
    event_type="com.todo.task.created",
    data=event_data,
    trace_id=trace_id
)
```

## Testing Dapr Integration

### Local Testing with Dapr CLI

```bash
# Run application with Dapr sidecar
dapr run --app-id backend \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --components-path ./infra/dapr-components \
  -- python backend/main.py
```

### Verify Dapr Sidecar

```bash
# Check Dapr sidecar health
curl http://localhost:3500/v1.0/healthz

# List loaded components
curl http://localhost:3500/v1.0/metadata
```

### Test Event Publishing

```bash
# Publish test event
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/test-topic \
  -H "Content-Type: application/json" \
  -d '{
    "specversion": "1.0",
    "type": "test.event",
    "source": "test",
    "id": "test-123",
    "data": {"message": "Hello Dapr!"}
  }'
```

### Test State Store

```bash
# Save state
curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key": "test-key", "value": "test-value"}]'

# Get state
curl http://localhost:3500/v1.0/state/statestore/test-key
```

## Monitoring Dapr

### Dapr Dashboard

```bash
# Deploy Dapr dashboard
dapr dashboard -k

# Access at http://localhost:8080
```

**Dashboard Features**:
- Component health status
- Sidecar metrics
- Configuration overview
- Log streaming

### Dapr Metrics

Dapr exposes Prometheus metrics on port 9090:

```bash
# View metrics
curl http://localhost:9090/metrics
```

**Key Metrics**:
- `dapr_http_server_request_count` - Total HTTP requests
- `dapr_http_server_request_duration_ms` - Request latency
- `dapr_component_loaded` - Component health
- `dapr_pubsub_ingress_count` - Events published
- `dapr_pubsub_egress_count` - Events consumed

### Dapr Logs

```bash
# View Dapr sidecar logs
kubectl logs <pod-name> -c daprd

# Filter for specific operations
kubectl logs <pod-name> -c daprd | grep pubsub
kubectl logs <pod-name> -c daprd | grep state
kubectl logs <pod-name> -c daprd | grep secrets
```

## Troubleshooting

### Sidecar Not Injecting

**Symptoms**: Pod shows 1/1 Ready instead of 2/2

**Solutions**:
1. Verify Dapr operator is running:
   ```bash
   kubectl get pods -n dapr-system
   ```

2. Check deployment annotations:
   ```bash
   kubectl get deployment <name> -o yaml | grep dapr.io
   ```

3. Check Dapr operator logs:
   ```bash
   kubectl logs -l app=dapr-operator -n dapr-system
   ```

### Component Not Loading

**Symptoms**: Events not publishing, state not saving

**Solutions**:
1. Verify component exists:
   ```bash
   kubectl get components
   ```

2. Check component configuration:
   ```bash
   kubectl describe component <component-name>
   ```

3. Check Dapr sidecar logs:
   ```bash
   kubectl logs <pod-name> -c daprd | grep component
   ```

### Events Not Publishing

**Symptoms**: No events in Kafka topics

**Solutions**:
1. Check Dapr Pub/Sub logs:
   ```bash
   kubectl logs <pod-name> -c daprd | grep pubsub
   ```

2. Verify Kafka connectivity:
   ```bash
   kubectl exec -it <pod-name> -c daprd -- curl http://localhost:3500/v1.0/healthz
   ```

3. Check Kafka credentials:
   ```bash
   kubectl get secret kafka-secrets -o yaml
   ```

## Best Practices

### 1. Component Scoping

Limit component access to specific applications:

```yaml
scopes:
- backend
- chat-api
```

### 2. Error Handling

Always handle Dapr API errors:

```python
try:
    success = dapr_client.publish_event(...)
    if not success:
        logger.error("Failed to publish event")
except Exception as e:
    logger.error(f"Dapr error: {e}")
```

### 3. Retry Configuration

Configure retry policies in Dapr components:

```yaml
metadata:
- name: maxRetries
  value: "3"
- name: retryBackoff
  value: "exponential"
```

### 4. Resource Limits

Set appropriate resource limits for Dapr sidecars:

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"
```

## References

- **Dapr Documentation**: https://docs.dapr.io/
- **Dapr Pub/Sub**: https://docs.dapr.io/developing-applications/building-blocks/pubsub/
- **Dapr State Management**: https://docs.dapr.io/developing-applications/building-blocks/state-management/
- **Dapr Secrets**: https://docs.dapr.io/developing-applications/building-blocks/secrets/
- **CloudEvents Specification**: https://cloudevents.io/

---

**Integration Guide Status**: Complete
**Last Updated**: 2026-02-09
