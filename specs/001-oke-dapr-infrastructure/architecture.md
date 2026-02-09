# Architecture: Oracle OKE Dapr Infrastructure Integration

**Date**: 2026-02-09
**Feature**: Oracle OKE Dapr Infrastructure Integration
**Branch**: `001-oke-dapr-infrastructure`

## Overview

This document describes the final architecture for the Phase V Todo AI Chatbot deployment on Oracle Cloud Infrastructure Kubernetes Engine (OKE) with Dapr runtime, event-driven architecture, and automated CI/CD.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Oracle OKE Cluster (Always-Free Tier)              │
│                              4 OCPU, 24GB RAM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Ingress Controller (nginx)                    │   │
│  │                    http://todo-app.oke.example.com                   │   │
│  └────────────────────────┬────────────────────────────────────────────┘   │
│                           │                                                  │
│           ┌───────────────┴───────────────┐                                 │
│           │                               │                                  │
│  ┌────────▼────────┐            ┌────────▼────────┐                        │
│  │  Frontend Pod   │            │  Backend Pod    │                        │
│  ├─────────────────┤            ├─────────────────┤                        │
│  │ Next.js App     │            │ FastAPI App     │                        │
│  │ (Port 3000)     │            │ (Port 8000)     │                        │
│  │                 │            │                 │                        │
│  │ ┌─────────────┐ │            │ ┌─────────────┐ │                        │
│  │ │ Dapr Sidecar│ │            │ │ Dapr Sidecar│ │                        │
│  │ │  (daprd)    │ │            │ │  (daprd)    │ │                        │
│  │ │ Port 3500   │ │            │ │ Port 3500   │ │                        │
│  │ └─────────────┘ │            │ └──────┬──────┘ │                        │
│  └─────────────────┘            └─────────┼────────┘                        │
│                                            │                                 │
│                                            │ Dapr Pub/Sub API                │
│                                            │ POST /v1.0/publish/...          │
│                                            │                                 │
│  ┌─────────────────────────────────────────▼──────────────────────────┐   │
│  │                      Dapr Components (CRDs)                         │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  • kafka-pubsub (pubsub.kafka)                                      │   │
│  │  • statestore (state.postgresql)                                    │   │
│  │  • scheduler (scheduler.kubernetes)                                 │   │
│  │  • kubernetes-secrets (secretstores.kubernetes)                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Dapr Control Plane (dapr-system)                 │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  • dapr-operator       • dapr-sidecar-injector                      │   │
│  │  • dapr-sentry         • dapr-placement                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       Kubernetes Secrets                             │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  • app-secrets (COHERE_API_KEY, BETTER_AUTH_SECRET, DATABASE_URL)   │   │
│  │  • kafka-secrets (SASL_USERNAME, SASL_PASSWORD)                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
         ┌──────────▼─────────┐    │    ┌─────────▼──────────┐
         │  Redpanda Cloud    │    │    │  Neon PostgreSQL   │
         │  (Kafka-Compatible)│    │    │  (Serverless)      │
         ├────────────────────┤    │    ├────────────────────┤
         │ Topics:            │    │    │ Tables:            │
         │ • task-events      │    │    │ • users            │
         │ • task-updates     │    │    │ • tasks            │
         │ • reminders        │    │    │ • conversations    │
         └────────────────────┘    │    │ • messages         │
                                   │    │ • dapr_state       │
                                   │    └────────────────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  GitHub Actions     │
                        │  CI/CD Pipeline     │
                        ├─────────────────────┤
                        │ 1. Test             │
                        │ 2. Build Images     │
                        │ 3. Push to ghcr.io  │
                        │ 4. Helm Upgrade     │
                        └─────────────────────┘
```

## Component Interactions

### 1. User Request Flow

```
User Browser
    │
    │ HTTPS
    ▼
Ingress Controller (nginx)
    │
    ├─── / (frontend) ──────────────────────────────────────┐
    │                                                        │
    │                                                        ▼
    │                                              Frontend Pod (Next.js)
    │                                                        │
    │                                                        │ API calls
    │                                                        ▼
    └─── /api (backend) ────────────────────────────────────┐
                                                             │
                                                             ▼
                                                   Backend Pod (FastAPI)
                                                             │
                                                             │ JWT Auth
                                                             ▼
                                                   Task CRUD Operations
```

### 2. Event Publishing Flow

```
Backend Pod (FastAPI)
    │
    │ Task Operation (create/update/delete)
    ▼
Dapr Sidecar (localhost:3500)
    │
    │ POST /v1.0/publish/kafka-pubsub/task-events
    │ Body: { "task_id": "...", "user_id": "...", "action": "created" }
    ▼
Dapr Pub/Sub Component (kafka-pubsub)
    │
    │ Kafka Protocol (SASL/SCRAM-SHA-256)
    ▼
Redpanda Cloud
    │
    │ Topic: task-events (partition 0, 1, 2)
    ▼
Event Stored in Kafka
    │
    │ (Future: Consumer services subscribe here)
    ▼
Notification Service / Audit Service / Recurring Task Service
```

### 3. State Management Flow

```
Backend Pod (FastAPI)
    │
    │ Conversation state save/load
    ▼
Dapr Sidecar (localhost:3500)
    │
    │ POST /v1.0/state/statestore
    │ Body: [{ "key": "conv-123", "value": {...} }]
    ▼
Dapr State Component (state.postgresql)
    │
    │ PostgreSQL Protocol
    ▼
Neon PostgreSQL
    │
    │ Table: dapr_state
    │ Columns: key, value, etag, metadata
    ▼
State Persisted
```

### 4. Secrets Access Flow

```
Backend Pod (FastAPI)
    │
    │ Need COHERE_API_KEY
    ▼
Dapr Sidecar (localhost:3500)
    │
    │ GET /v1.0/secrets/kubernetes-secrets/cohere-api-key
    ▼
Dapr Secrets Component (secretstores.kubernetes)
    │
    │ Kubernetes API
    ▼
Kubernetes Secret (app-secrets)
    │
    │ Key: cohere-api-key
    │ Value: <encrypted>
    ▼
Secret Value Returned to Application
```

### 5. Reminder Scheduling Flow

```
Backend Pod (FastAPI)
    │
    │ Task created with due_date
    ▼
Dapr Sidecar (localhost:3500)
    │
    │ POST /v1.0-alpha1/jobs/reminder-{task-id}
    │ Body: { "schedule": "2026-02-10T15:00:00Z", "data": {...} }
    ▼
Dapr Scheduler Component (scheduler.kubernetes)
    │
    │ Creates Kubernetes CronJob
    ▼
Kubernetes CronJob
    │
    │ At scheduled time
    ▼
Dapr invokes callback endpoint
    │
    │ POST /api/jobs/reminder-callback
    ▼
Backend Pod (FastAPI)
    │
    │ Publishes reminder event to Kafka
    ▼
Redpanda Cloud (reminders topic)
```

## Network Architecture

### Ingress Configuration

```yaml
Host: todo-app.oke.example.com
Paths:
  - path: /api
    backend: backend-service:8000
  - path: /
    backend: frontend-service:3000
```

### Service Mesh (Dapr)

- **mTLS**: Enabled by default between Dapr sidecars
- **Service Invocation**: `http://localhost:3500/v1.0/invoke/{app-id}/method/{method}`
- **Observability**: Distributed tracing via Dapr trace headers

### External Connectivity

- **Neon PostgreSQL**: TLS connection from OKE to Neon cloud
- **Redpanda Cloud**: SASL/SCRAM-SHA-256 over TLS from OKE to Redpanda
- **GitHub Container Registry**: Pull images during deployment

## Data Flow

### Task Creation Event Flow

```
1. User creates task via chat interface
   └─> Frontend sends POST /api/{user_id}/chat

2. Backend processes chat message
   └─> Cohere API analyzes intent
   └─> MCP tool: add_task() called

3. Task saved to database
   └─> INSERT INTO tasks (user_id, title, description, ...)

4. Event published via Dapr
   └─> POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events
   └─> Body: {
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

5. Dapr Pub/Sub component forwards to Kafka
   └─> Kafka topic: task-events
   └─> Partition: hash(user_id) % 3

6. Event stored in Redpanda Cloud
   └─> Retention: 7 days
   └─> Available for consumers

7. (Future) Consumer services process event
   └─> Notification Service: Send notification
   └─> Audit Service: Log to audit trail
   └─> Analytics Service: Update metrics
```

## Security Architecture

### Authentication & Authorization

- **User Authentication**: Better Auth JWT tokens
- **Service-to-Service**: Dapr mTLS between sidecars
- **External Services**: SASL/SCRAM-SHA-256 for Kafka, TLS for PostgreSQL

### Secrets Management

```
Kubernetes Secrets (encrypted at rest)
    │
    │ Dapr Secrets API
    ▼
Application Code (never sees raw secrets in env vars)
```

### Network Policies (Optional)

```yaml
# Restrict backend to only communicate with:
# - Dapr sidecar (localhost)
# - Neon PostgreSQL (external)
# - No direct pod-to-pod communication
```

## Scalability Architecture

### Horizontal Scaling

```
Frontend: 1-3 replicas (stateless)
Backend: 1-3 replicas (stateless)
Dapr Sidecars: 1 per application pod (automatic)
```

### Resource Limits

```yaml
Frontend Pod:
  Requests: 200m CPU, 256Mi RAM
  Limits: 500m CPU, 512Mi RAM

Backend Pod:
  Requests: 300m CPU, 512Mi RAM
  Limits: 1000m CPU, 1Gi RAM

Dapr Sidecar:
  Requests: 100m CPU, 128Mi RAM
  Limits: 200m CPU, 256Mi RAM
```

### OKE Cluster Capacity

```
Total Available: 4 OCPU, 24GB RAM
System Overhead: ~1.5 OCPU, ~6GB RAM
Application Capacity: ~2.5 OCPU, ~18GB RAM

Max Pods:
- Frontend: 3 replicas × (500m + 200m) = 2.1 OCPU
- Backend: 2 replicas × (1000m + 200m) = 2.4 OCPU
- Total: ~4.5 OCPU (requires careful resource tuning)
```

## Deployment Architecture

### CI/CD Pipeline

```
GitHub Repository
    │
    │ Push to main
    ▼
GitHub Actions Workflow
    │
    ├─> Stage 1: Test (pytest, lint)
    │
    ├─> Stage 2: Build Docker Images
    │   └─> frontend:sha-abc123
    │   └─> backend:sha-abc123
    │
    ├─> Stage 3: Push to ghcr.io
    │   └─> ghcr.io/<user>/todo-frontend:sha-abc123
    │   └─> ghcr.io/<user>/todo-backend:sha-abc123
    │
    └─> Stage 4: Deploy to OKE
        └─> helm upgrade --install todo-app ./infra/helm/todo-app \
              --set frontend.image.tag=sha-abc123 \
              --set backend.image.tag=sha-abc123
```

### Helm Release Management

```
Chart Version: 0.2.0 (Phase V)
Release Name: todo-app
Namespace: default

Resources Managed:
- Deployments: frontend, backend
- Services: frontend-service, backend-service
- Ingress: todo-app-ingress
- Secrets: app-secrets, kafka-secrets
- ConfigMaps: app-config
- Dapr Components: kafka-pubsub, statestore, scheduler, kubernetes-secrets
```

## Observability Architecture

### Logging

```
Application Logs
    │
    │ stdout/stderr
    ▼
Kubernetes Pod Logs
    │
    │ kubectl logs <pod> -c <container>
    ▼
Log Aggregation (kubectl logs, optional Loki)
```

### Metrics

```
Dapr Sidecars
    │
    │ Prometheus metrics endpoint (:9090/metrics)
    ▼
Dapr Dashboard (optional Prometheus scraping)
```

### Tracing

```
HTTP Request
    │
    │ Dapr injects trace headers (traceparent, tracestate)
    ▼
Application Processing
    │
    │ Propagates trace context
    ▼
Dapr Pub/Sub
    │
    │ Trace ID in event metadata
    ▼
Kafka Event
    │
    │ Trace ID preserved
    ▼
Consumer Service (future)
```

## Disaster Recovery

### Backup Strategy

- **Database**: Neon automatic backups (managed service)
- **Kafka**: 7-day retention (Redpanda Cloud)
- **Kubernetes State**: Helm release history
- **Configuration**: Git repository (infrastructure as code)

### Rollback Procedures

```bash
# Rollback Helm release
helm rollback todo-app <revision>

# Rollback to previous image tags
helm upgrade todo-app ./infra/helm/todo-app \
  --set frontend.image.tag=<previous-sha> \
  --set backend.image.tag=<previous-sha>
```

## Architecture Decisions

### Why Dapr?

1. **Portability**: Same code runs on any Kubernetes cluster (OKE, AKS, GKE, Minikube)
2. **Abstraction**: Swap Kafka for Redis Pub/Sub with YAML-only change
3. **Best Practices**: Built-in retry, circuit breaker, observability
4. **Simplicity**: No direct client libraries, unified HTTP/gRPC API

### Why Redpanda Cloud?

1. **Zero Management**: No Kafka brokers or Zookeeper to maintain
2. **Free Tier**: Sufficient for demo and development
3. **Kafka-Compatible**: Works with Dapr Kafka Pub/Sub component
4. **Performance**: Low latency, high throughput

### Why Oracle OKE?

1. **Always-Free Tier**: 4 OCPU, 24GB RAM permanently free
2. **Production-Grade**: Real Kubernetes, not a toy environment
3. **Cloud-Native**: Demonstrates multi-cloud portability
4. **Cost-Effective**: Zero cost for hackathon demo

## Future Enhancements

### Phase VI: Consumer Services

```
┌─────────────────────────────────────────────────────────────┐
│  Notification Service Pod                                    │
│  ├─ FastAPI App (subscribes to reminders topic)             │
│  └─ Dapr Sidecar                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Recurring Task Service Pod                                  │
│  ├─ FastAPI App (subscribes to task-events topic)           │
│  └─ Dapr Sidecar                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Audit Service Pod                                           │
│  ├─ FastAPI App (subscribes to all topics)                  │
│  └─ Dapr Sidecar                                             │
└─────────────────────────────────────────────────────────────┘
```

### Phase VII: Advanced Observability

- Prometheus + Grafana dashboards
- Jaeger distributed tracing
- Loki log aggregation
- Alertmanager for proactive alerts

### Phase VIII: Multi-Region Deployment

- Active-active across multiple OCI regions
- Global load balancing
- Cross-region event replication

---

**Architecture Status**: ✅ Complete - Ready for Implementation
**Next Steps**: Create detailed Dapr component specifications and CI/CD pipeline design
