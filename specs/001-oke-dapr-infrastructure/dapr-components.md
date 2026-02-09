# Dapr Components Specification

**Date**: 2026-02-09
**Feature**: Oracle OKE Dapr Infrastructure Integration
**Branch**: `001-oke-dapr-infrastructure`

## Overview

This document provides detailed specifications for all Dapr components required for the Phase V deployment. Each component is defined as a Kubernetes Custom Resource (CRD) that Dapr uses to configure its building blocks.

## Component 1: Kafka Pub/Sub

### Purpose
Enable asynchronous event publishing and subscription using Kafka/Redpanda as the message broker.

### File Location
`infra/dapr-components/kafka-pubsub.yaml`

### Full Specification

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  # Kafka broker addresses (Redpanda Cloud)
  - name: brokers
    value: "seed-abc123.cloud.redpanda.com:9092"

  # Authentication type
  - name: authType
    value: "password"

  # SASL username (from Kubernetes Secret)
  - name: saslUsername
    secretKeyRef:
      name: kafka-secrets
      key: username

  # SASL password (from Kubernetes Secret)
  - name: saslPassword
    secretKeyRef:
      name: kafka-secrets
      key: password

  # SASL mechanism (required by Redpanda)
  - name: saslMechanism
    value: "SCRAM-SHA-256"

  # Consumer group ID
  - name: consumerGroup
    value: "todo-app-group"

  # Client ID for producer
  - name: clientId
    value: "todo-app-producer"

  # Initial offset for new consumers
  - name: initialOffset
    value: "newest"

  # Max message bytes
  - name: maxMessageBytes
    value: "1048576"  # 1MB

  # Enable idempotent producer
  - name: enableIdempotence
    value: "true"

  # Compression type
  - name: compressionType
    value: "snappy"

scopes:
- backend
- chat-api
```

### Metadata Fields Explained

| Field | Value | Description |
|-------|-------|-------------|
| `brokers` | Redpanda bootstrap URL | Comma-separated list of Kafka brokers |
| `authType` | `password` | Use SASL authentication |
| `saslUsername` | From secret | SASL username for authentication |
| `saslPassword` | From secret | SASL password for authentication |
| `saslMechanism` | `SCRAM-SHA-256` | SASL mechanism (Redpanda requirement) |
| `consumerGroup` | `todo-app-group` | Consumer group for subscribers |
| `clientId` | `todo-app-producer` | Client identifier for producers |
| `initialOffset` | `newest` | Start from latest messages for new consumers |
| `maxMessageBytes` | `1048576` | Maximum message size (1MB) |
| `enableIdempotence` | `true` | Ensure exactly-once delivery |
| `compressionType` | `snappy` | Compress messages for efficiency |

### Scopes

Only the following applications can use this component:
- `backend` - Main FastAPI backend
- `chat-api` - Chat API service (if separated in future)

### Topics

The following topics will be used:
- `task-events` - Task creation and deletion events
- `task-updates` - Task modification events
- `reminders` - Reminder trigger events

### Usage Example

**Publishing an Event**:
```python
import requests
import json

event_data = {
    "specversion": "1.0",
    "type": "com.todo.task.created",
    "source": "backend",
    "id": "evt-abc123",
    "datacontenttype": "application/json",
    "data": {
        "task_id": "task-789",
        "user_id": "user-456",
        "title": "Buy groceries",
        "created_at": "2026-02-09T10:00:00Z"
    }
}

response = requests.post(
    "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
    json=event_data
)
```

**Subscribing to Events** (Declarative):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: task-events-subscription
spec:
  pubsubname: kafka-pubsub
  topic: task-events
  route: /api/events/task-created
scopes:
- notification-service
```

### Kubernetes Secret

Create the Kafka credentials secret:
```bash
kubectl create secret generic kafka-secrets \
  --from-literal=username=<redpanda-username> \
  --from-literal=password=<redpanda-password>
```

---

## Component 2: PostgreSQL State Store

### Purpose
Provide distributed state management using Neon PostgreSQL as the backing store.

### File Location
`infra/dapr-components/state-postgresql.yaml`

### Full Specification

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
  # PostgreSQL connection string (from Kubernetes Secret)
  - name: connectionString
    secretKeyRef:
      name: app-secrets
      key: database-url

  # Table name for state storage
  - name: tableName
    value: "dapr_state"

  # Key prefix for namespacing
  - name: keyPrefix
    value: "todo-app"

  # Timeout for database operations (seconds)
  - name: timeout
    value: "20"

  # Enable transactions
  - name: actorStateStore
    value: "true"

scopes:
- backend
- chat-api
```

### Metadata Fields Explained

| Field | Value | Description |
|-------|-------|-------------|
| `connectionString` | From secret | PostgreSQL connection string (Neon) |
| `tableName` | `dapr_state` | Table for storing state (auto-created) |
| `keyPrefix` | `todo-app` | Prefix for all keys (namespace isolation) |
| `timeout` | `20` | Database operation timeout in seconds |
| `actorStateStore` | `true` | Enable transactional state operations |

### Database Schema

Dapr automatically creates the following table:
```sql
CREATE TABLE dapr_state (
  key TEXT NOT NULL PRIMARY KEY,
  value JSONB NOT NULL,
  isbinary BOOLEAN NOT NULL,
  insertdate TIMESTAMP NOT NULL DEFAULT NOW(),
  updatedate TIMESTAMP,
  etag VARCHAR(50)
);

CREATE INDEX idx_dapr_state_updatedate ON dapr_state(updatedate);
```

### Usage Example

**Saving State**:
```python
import requests
import json

state_data = [
    {
        "key": "conversation-123",
        "value": {
            "user_id": "user-456",
            "messages": [...],
            "created_at": "2026-02-09T10:00:00Z"
        }
    }
]

response = requests.post(
    "http://localhost:3500/v1.0/state/statestore",
    json=state_data
)
```

**Loading State**:
```python
response = requests.get(
    "http://localhost:3500/v1.0/state/statestore/conversation-123"
)
conversation = response.json()
```

**Deleting State**:
```python
response = requests.delete(
    "http://localhost:3500/v1.0/state/statestore/conversation-123"
)
```

### Transactional Operations

```python
transaction = {
    "operations": [
        {
            "operation": "upsert",
            "request": {
                "key": "conversation-123",
                "value": {...}
            }
        },
        {
            "operation": "delete",
            "request": {
                "key": "conversation-old"
            }
        }
    ]
}

response = requests.post(
    "http://localhost:3500/v1.0/state/statestore/transaction",
    json=transaction
)
```

---

## Component 3: Kubernetes Scheduler (Jobs API)

### Purpose
Enable scheduled job execution for reminders and recurring tasks.

### File Location
`infra/dapr-components/scheduler-jobs.yaml`

### Full Specification

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: scheduler
  namespace: default
spec:
  type: scheduler.kubernetes
  version: v1
  metadata:
  # Kubernetes namespace for job resources
  - name: namespace
    value: "default"

  # Job namespace (optional, defaults to component namespace)
  - name: jobNamespace
    value: "default"

scopes:
- backend
```

### Metadata Fields Explained

| Field | Value | Description |
|-------|-------|-------------|
| `namespace` | `default` | Namespace where scheduler component runs |
| `jobNamespace` | `default` | Namespace where Kubernetes Jobs are created |

### Usage Example

**Schedule a One-Time Job**:
```python
import requests
from datetime import datetime, timedelta

# Schedule reminder for 1 hour from now
reminder_time = datetime.utcnow() + timedelta(hours=1)

job_data = {
    "schedule": reminder_time.isoformat() + "Z",
    "data": {
        "task_id": "task-789",
        "user_id": "user-456",
        "reminder_message": "Time to buy groceries!"
    },
    "dueTime": reminder_time.isoformat() + "Z"
}

response = requests.post(
    f"http://localhost:3500/v1.0-alpha1/jobs/reminder-task-789",
    json=job_data
)
```

**Schedule a Recurring Job**:
```python
job_data = {
    "schedule": "@every 24h",  # Every 24 hours
    "data": {
        "task_id": "task-recurring-123",
        "user_id": "user-456"
    }
}

response = requests.post(
    f"http://localhost:3500/v1.0-alpha1/jobs/recurring-task-123",
    json=job_data
)
```

**Delete a Scheduled Job**:
```python
response = requests.delete(
    f"http://localhost:3500/v1.0-alpha1/jobs/reminder-task-789"
)
```

### Callback Endpoint

Application must expose a callback endpoint:
```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/api/jobs/reminder-callback")
async def reminder_callback(job_data: dict):
    task_id = job_data["data"]["task_id"]
    user_id = job_data["data"]["user_id"]

    # Publish reminder event to Kafka
    event = {
        "type": "com.todo.reminder.due",
        "data": {
            "task_id": task_id,
            "user_id": user_id,
            "triggered_at": datetime.utcnow().isoformat()
        }
    }

    # Publish via Dapr Pub/Sub
    requests.post(
        "http://localhost:3500/v1.0/publish/kafka-pubsub/reminders",
        json=event
    )

    return {"status": "processed"}
```

---

## Component 4: Kubernetes Secrets Store

### Purpose
Provide unified API for accessing Kubernetes Secrets without direct environment variable exposure.

### File Location
`infra/dapr-components/secretstores-kubernetes.yaml`

### Full Specification

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
scopes:
- backend
- frontend
- chat-api
```

### Metadata Fields Explained

No additional metadata required for default namespace. For cross-namespace access:

```yaml
metadata:
- name: vaultName
  value: "my-namespace"  # Access secrets from different namespace
```

### Usage Example

**Fetch Secret**:
```python
import requests

response = requests.get(
    "http://localhost:3500/v1.0/secrets/kubernetes-secrets/app-secrets/cohere-api-key"
)

if response.status_code == 200:
    secret_data = response.json()
    api_key = secret_data["cohere-api-key"]
```

**Fetch All Secrets from a Secret Object**:
```python
response = requests.get(
    "http://localhost:3500/v1.0/secrets/kubernetes-secrets/app-secrets"
)

secrets = response.json()
# Returns: {
#   "cohere-api-key": "...",
#   "better-auth-secret": "...",
#   "database-url": "..."
# }
```

### Kubernetes Secrets

Create application secrets:
```bash
kubectl create secret generic app-secrets \
  --from-literal=cohere-api-key=$COHERE_API_KEY \
  --from-literal=better-auth-secret=$BETTER_AUTH_SECRET \
  --from-literal=database-url=$DATABASE_URL
```

---

## Deployment Instructions

### 1. Create Kubernetes Secrets

```bash
# Application secrets
kubectl create secret generic app-secrets \
  --from-literal=cohere-api-key=$COHERE_API_KEY \
  --from-literal=better-auth-secret=$BETTER_AUTH_SECRET \
  --from-literal=database-url=$DATABASE_URL

# Kafka secrets
kubectl create secret generic kafka-secrets \
  --from-literal=username=$KAFKA_USERNAME \
  --from-literal=password=$KAFKA_PASSWORD
```

### 2. Apply Dapr Components

```bash
# Apply all components
kubectl apply -f infra/dapr-components/

# Verify components
kubectl get components

# Expected output:
# NAME                  AGE
# kafka-pubsub          10s
# kubernetes-secrets    10s
# scheduler             10s
# statestore            10s
```

### 3. Verify Component Status

```bash
# Check component details
kubectl describe component kafka-pubsub

# Check Dapr logs
kubectl logs -l app=dapr-operator -n dapr-system
```

### 4. Test Components

**Test Pub/Sub**:
```bash
# Publish test event
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/test-topic \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from Dapr!"}'
```

**Test State Store**:
```bash
# Save state
curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key": "test-key", "value": "test-value"}]'

# Get state
curl http://localhost:3500/v1.0/state/statestore/test-key
```

**Test Secrets**:
```bash
# Get secret
curl http://localhost:3500/v1.0/secrets/kubernetes-secrets/app-secrets/cohere-api-key
```

---

## Troubleshooting

### Component Not Ready

```bash
# Check component status
kubectl get components

# Check component details
kubectl describe component <component-name>

# Check Dapr operator logs
kubectl logs -l app=dapr-operator -n dapr-system
```

### Connection Errors

**Kafka Connection Failed**:
- Verify Redpanda Cloud credentials
- Check network connectivity from OKE to Redpanda
- Verify SASL mechanism matches Redpanda configuration

**PostgreSQL Connection Failed**:
- Verify Neon connection string format
- Check database URL includes SSL parameters
- Verify network connectivity from OKE to Neon

### Secret Access Denied

```bash
# Verify secret exists
kubectl get secret app-secrets

# Check secret contents (base64 encoded)
kubectl get secret app-secrets -o yaml

# Verify Dapr has RBAC permissions
kubectl get clusterrolebinding dapr-operator
```

---

## Security Considerations

### Secret Rotation

1. Update Kubernetes Secret:
   ```bash
   kubectl create secret generic app-secrets \
     --from-literal=cohere-api-key=$NEW_API_KEY \
     --dry-run=client -o yaml | kubectl apply -f -
   ```

2. Restart pods to pick up new secrets:
   ```bash
   kubectl rollout restart deployment backend
   ```

### Network Policies

Restrict component access:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: dapr-component-policy
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: dapr-sidecar
    ports:
    - protocol: TCP
      port: 3500
```

### Audit Logging

Enable Dapr audit logging:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
spec:
  tracing:
    samplingRate: "1"
  metric:
    enabled: true
  logging:
    level: info
```

---

**Component Specification Status**: ✅ Complete - Ready for Deployment
**Next Steps**: Create CI/CD pipeline design and monitoring strategy
