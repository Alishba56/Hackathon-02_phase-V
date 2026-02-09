# Todo AI Chatbot - Demo Script for Judges

**Purpose**: Step-by-step demonstration script showcasing the complete Oracle OKE + Dapr event-driven architecture implementation.

**Duration**: 10-15 minutes

**Prerequisites**: Application deployed to OKE with Dapr runtime

---

## Demo Overview

This demonstration showcases:
1. **Cloud-Native Deployment**: Oracle OKE with Dapr runtime
2. **Event-Driven Architecture**: Kafka/Redpanda pub/sub via Dapr
3. **Automated CI/CD**: GitHub Actions pipeline
4. **Observability**: Comprehensive monitoring and tracing
5. **Production-Ready**: Helm charts, secrets management, health checks

---

## Part 1: Architecture Overview (2 minutes)

### Show System Architecture

**Script**: "Let me show you the architecture of our Todo AI Chatbot deployed on Oracle Cloud Infrastructure."

```bash
# Display architecture diagram
cat docs/dapr-integration.md | grep -A 30 "Architecture"
```

**Key Points to Highlight**:
- Oracle OKE cluster (always-free tier: 4 OCPU, 24GB RAM)
- Dapr sidecars injected into each pod (2/2 Ready)
- Event-driven architecture with Kafka/Redpanda Cloud
- PostgreSQL state store (Neon Serverless)
- Kubernetes Secrets for secure credential management

**Visual**: Show the ASCII architecture diagram from the documentation

---

## Part 2: Live Application Demo (3 minutes)

### Access the Application

```bash
# Get application URL
INGRESS_IP=$(kubectl get ingress todo-app-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Application URL: http://${INGRESS_IP}"
```

**Script**: "The application is accessible via a public load balancer. Let me show you the frontend."

### Demonstrate Core Features

1. **Open Frontend**: Navigate to `http://${INGRESS_IP}/`
2. **Create Task**: "Buy groceries for dinner"
3. **AI Enhancement**: Show AI-powered task suggestions
4. **Task Management**: Mark complete, edit, delete

**Key Points**:
- Responsive React frontend
- Real-time updates
- AI-powered task management with Cohere API
- Better Auth authentication

---

## Part 3: Event-Driven Architecture (3 minutes)

### Show Event Publishing

**Script**: "Behind the scenes, every task operation publishes events to Kafka via Dapr. Let me show you."

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pods -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Watch Dapr sidecar logs for event publishing
kubectl logs $BACKEND_POD -c daprd --tail=20 -f
```

**Action**: Create a new task in the UI while logs are streaming

**Expected Output**:
```
Publishing event to topic 'task-events'
Event type: com.todo.task.created
Event published successfully to kafka-pubsub
```

### Show CloudEvents Format

**Script**: "All events follow the CloudEvents 1.0 specification for interoperability."

```bash
# Show event structure in backend code
cat backend/services/dapr_client.py | grep -A 20 "def publish_event"
```

**Key Points**:
- CloudEvents 1.0 standard format
- Event types: task.created, task.updated, task.deleted, task.completed
- Trace context propagation for distributed tracing
- Kafka topics: task-events, task-updates, reminders

### Verify Events in Redpanda

**Script**: "Let me show you the events in our Redpanda Cloud dashboard."

**Action**: Open Redpanda Cloud console and navigate to Topics → task-events

**Show**:
- Real-time event stream
- Event payload with CloudEvents metadata
- Message count and throughput

---

## Part 4: Dapr Integration (2 minutes)

### Show Dapr Components

**Script**: "Dapr provides building blocks for cloud-native applications. Let me show our components."

```bash
# List Dapr components
kubectl get components

# Show kafka-pubsub component details
kubectl describe component kafka-pubsub
```

**Expected Output**:
```
NAME                  AGE
kafka-pubsub          2d
kubernetes-secrets    2d
scheduler             2d
statestore            2d
```

### Show Dapr Sidecar Injection

**Script**: "Each pod runs with a Dapr sidecar for service abstraction."

```bash
# Show pod with 2/2 containers (app + daprd)
kubectl get pods -l app=backend

# Show Dapr annotations
kubectl get deployment todo-app-backend -o yaml | grep -A 5 "dapr.io"
```

**Key Points**:
- Automatic sidecar injection via annotations
- Dapr handles all infrastructure concerns (pub/sub, state, secrets)
- Application code remains cloud-agnostic

---

## Part 5: CI/CD Pipeline (2 minutes)

### Show GitHub Actions Workflow

**Script**: "Every commit triggers an automated CI/CD pipeline."

**Action**: Open GitHub repository → Actions tab

**Show Workflow Stages**:
1. **Test**: Linting and pytest
2. **Build**: Docker images with commit SHA tags
3. **Push**: Images to GitHub Container Registry
4. **Deploy**: Helm upgrade to OKE
5. **Verify**: Health checks and smoke tests

### Show Recent Deployment

```bash
# Show Helm release history
helm history todo-app

# Show current deployment
kubectl get deployments
kubectl get pods
```

**Key Points**:
- Automated testing before deployment
- Immutable image tags (commit SHA)
- Atomic deployments with automatic rollback
- Zero-downtime updates

---

## Part 6: Observability (2 minutes)

### Show Application Logs

**Script**: "Comprehensive logging across all components."

```bash
# Backend application logs
kubectl logs -l app=backend -c backend --tail=20

# Dapr sidecar logs
kubectl logs -l app=backend -c daprd --tail=20
```

### Show Dapr Dashboard

**Script**: "Dapr provides a dashboard for monitoring components and sidecars."

```bash
# Port-forward Dapr dashboard
kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080
```

**Action**: Open http://localhost:8080

**Show**:
- Component health status
- Sidecar metrics
- Configuration overview

### Show Metrics

```bash
# Show Dapr metrics endpoint
kubectl port-forward $BACKEND_POD 9090:9090
curl http://localhost:9090/metrics | grep dapr_pubsub
```

**Key Metrics**:
- `dapr_pubsub_ingress_count` - Events published
- `dapr_http_server_request_duration_ms` - Request latency
- `dapr_component_loaded` - Component health

---

## Part 7: Production Readiness (2 minutes)

### Show Secrets Management

**Script**: "All sensitive credentials are stored in Kubernetes Secrets."

```bash
# List secrets (values are base64 encoded)
kubectl get secrets

# Show secret structure (without revealing values)
kubectl get secret app-secrets -o yaml | grep -v "data:"
```

**Key Points**:
- No hardcoded credentials
- Dapr Secrets API for secure access
- Automatic rotation support

### Show Health Checks

**Script**: "The application exposes health endpoints for monitoring."

```bash
# Test backend health endpoint
curl http://${INGRESS_IP}/api/health

# Show readiness and liveness probes
kubectl get deployment todo-app-backend -o yaml | grep -A 5 "livenessProbe"
```

### Show Resource Management

```bash
# Show resource limits and requests
kubectl describe deployment todo-app-backend | grep -A 10 "Limits"
```

**Key Points**:
- Optimized for OKE free tier (4 OCPU, 24GB RAM)
- Resource limits prevent runaway processes
- Horizontal Pod Autoscaling ready

---

## Part 8: Disaster Recovery (1 minute)

### Show Rollback Capability

**Script**: "If a deployment fails, we can instantly rollback."

```bash
# Show release history
helm history todo-app

# Rollback to previous version (demo only, don't execute)
echo "helm rollback todo-app"
```

### Show Deployment Verification

**Script**: "Every deployment is automatically verified."

```bash
# Run verification script
./infra/scripts/verify-deployment.sh
```

**Expected Output**:
```
✓ Cluster access
✓ Dapr operator
✓ Frontend pod running (2/2)
✓ Backend pod running (2/2)
✓ kafka-pubsub component
✓ statestore component
✓ All checks passed! Deployment is healthy.
```

---

## Part 9: Scalability Demo (Optional, 1 minute)

### Show Horizontal Scaling

**Script**: "The application can scale horizontally to handle increased load."

```bash
# Scale backend to 3 replicas
kubectl scale deployment todo-app-backend --replicas=3

# Watch pods come online
kubectl get pods -l app=backend -w
```

**Key Points**:
- Stateless application design
- Dapr handles service discovery
- Load balancing via Kubernetes Service

---

## Part 10: Q&A and Wrap-Up (1 minute)

### Summary Points

**Script**: "To summarize, we've demonstrated:"

1. ✅ **Cloud-Native Deployment**: Oracle OKE with Dapr runtime
2. ✅ **Event-Driven Architecture**: Kafka pub/sub with CloudEvents
3. ✅ **Automated CI/CD**: GitHub Actions with atomic deployments
4. ✅ **Observability**: Comprehensive logging, metrics, and tracing
5. ✅ **Production-Ready**: Secrets management, health checks, rollback capability

### Architecture Highlights

- **Scalable**: Horizontal pod autoscaling ready
- **Resilient**: Automatic rollback on deployment failure
- **Observable**: Logs, metrics, traces, and Dapr dashboard
- **Secure**: Kubernetes Secrets, mTLS via Dapr, no hardcoded credentials
- **Cost-Effective**: Runs on OKE always-free tier

### Technical Stack

- **Compute**: Oracle OKE (Kubernetes 1.28+)
- **Runtime**: Dapr v1.12+ (sidecar pattern)
- **Messaging**: Redpanda Cloud Serverless (Kafka-compatible)
- **Database**: Neon Serverless PostgreSQL
- **CI/CD**: GitHub Actions
- **Container Registry**: GitHub Container Registry (ghcr.io)
- **Deployment**: Helm 3.13+
- **Monitoring**: kubectl, Dapr dashboard, Prometheus metrics

---

## Troubleshooting During Demo

### If Application is Not Accessible

```bash
# Check ingress status
kubectl get ingress todo-app-ingress

# Check pod status
kubectl get pods

# Check recent events
kubectl get events --sort-by='.lastTimestamp' | tail -20
```

### If Events Not Publishing

```bash
# Check Dapr sidecar logs
kubectl logs $BACKEND_POD -c daprd | grep pubsub

# Check Kafka connectivity
kubectl exec -it $BACKEND_POD -c daprd -- curl http://localhost:3500/v1.0/healthz
```

### If Pods Not Ready

```bash
# Describe pod for detailed status
kubectl describe pod $BACKEND_POD

# Check Dapr operator logs
kubectl logs -l app=dapr-operator -n dapr-system
```

---

## Demo Preparation Checklist

Before the demo, ensure:

- [ ] OKE cluster is running and accessible
- [ ] Application is deployed and healthy (run `verify-deployment.sh`)
- [ ] Ingress has external IP assigned
- [ ] Redpanda Cloud dashboard is accessible
- [ ] GitHub Actions workflow has completed successfully
- [ ] Dapr dashboard is accessible (port-forward ready)
- [ ] All kubectl commands are tested
- [ ] Browser tabs are pre-opened (frontend, GitHub, Redpanda)
- [ ] Terminal windows are arranged for visibility
- [ ] Backup slides/screenshots in case of connectivity issues

---

## Additional Demo Scenarios

### Scenario 1: Real-Time Event Flow

1. Open three terminal windows side-by-side
2. Window 1: Frontend (browser)
3. Window 2: Backend logs (`kubectl logs -f`)
4. Window 3: Dapr sidecar logs (`kubectl logs -c daprd -f`)
5. Create a task and watch events flow through all three windows

### Scenario 2: Deployment Pipeline

1. Make a small code change (e.g., update a log message)
2. Commit and push to main branch
3. Open GitHub Actions and watch pipeline execute
4. Show automatic deployment to OKE
5. Verify change is live in production

### Scenario 3: Disaster Recovery

1. Show current deployment (Helm release)
2. Simulate a bad deployment (wrong image tag)
3. Show automatic rollback via `--atomic` flag
4. Verify application is still healthy

---

## Backup Slides (If Live Demo Fails)

Prepare screenshots of:
1. Architecture diagram
2. Application UI with tasks
3. Dapr sidecar logs showing event publishing
4. Redpanda dashboard with events
5. GitHub Actions successful workflow
6. Dapr dashboard showing components
7. kubectl output showing 2/2 Ready pods
8. Helm release history

---

**Demo Script Status**: Complete
**Last Updated**: 2026-02-09
**Estimated Duration**: 10-15 minutes
**Difficulty**: Intermediate
**Audience**: Technical judges, architects, developers
