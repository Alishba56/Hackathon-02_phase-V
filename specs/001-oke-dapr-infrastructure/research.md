# Research: Oracle OKE Dapr Infrastructure Integration

**Date**: 2026-02-09
**Feature**: Oracle OKE Dapr Infrastructure Integration
**Branch**: `001-oke-dapr-infrastructure`

## Overview

This document captures all research findings and architectural decisions for deploying the Phase IV Todo AI Chatbot to Oracle Cloud Infrastructure Kubernetes Engine (OKE) with Dapr runtime, event-driven architecture, and automated CI/CD.

## Decision 1: Kafka Backend - Redpanda Cloud Serverless

### Chosen Solution
**Redpanda Cloud Serverless (Free Tier)**

### Rationale
- **Zero Management**: No infrastructure to maintain, no Zookeeper dependencies
- **Free Tier**: Generous free tier with sufficient throughput for demo purposes
- **Kafka-Compatible**: 100% Kafka API compatible, works with Dapr Kafka Pub/Sub component
- **Fast Setup**: Sign up → create cluster → get credentials in minutes
- **Cloud-Native**: Serverless architecture aligns with modern cloud-native principles
- **Performance**: Low latency, high throughput even on free tier

### Alternatives Considered

#### Strimzi Self-Hosted in OKE
- **Pros**: Full control, no external dependencies, data stays in cluster
- **Cons**:
  - Requires significant cluster resources (Kafka brokers, Zookeeper ensemble)
  - Management overhead (upgrades, monitoring, troubleshooting)
  - Consumes precious OKE always-free tier resources (4 OCPU, 24GB RAM)
  - Complex setup and configuration
- **Rejected Because**: Resource constraints and management complexity outweigh benefits for hackathon demo

#### Confluent Cloud
- **Pros**: Enterprise-grade, excellent tooling, managed service
- **Cons**: No free tier, paid service violates Phase V constraints
- **Rejected Because**: Violates free tier compliance requirement

### Implementation Details

**Setup Steps**:
1. Sign up at https://redpanda.com/try-redpanda
2. Create serverless cluster (select region close to OKE region for low latency)
3. Create topics: `task-events`, `task-updates`, `reminders`
4. Generate SASL credentials (username/password)
5. Get bootstrap server URL (e.g., `seed-abc123.cloud.redpanda.com:9092`)
6. Store credentials in Kubernetes Secrets
7. Configure Dapr Kafka Pub/Sub component with connection details

**Connection Configuration**:
```yaml
brokers: "seed-abc123.cloud.redpanda.com:9092"
authType: "password"
saslUsername: "<username>"
saslPassword: "<password>"
saslMechanism: "SCRAM-SHA-256"
```

**Topic Configuration**:
- Partitions: 3 (sufficient for demo, allows parallel processing)
- Retention: 7 days (default)
- Compression: snappy (good balance of speed and size)

---

## Decision 2: Dapr Jobs vs Cron Bindings for Reminders

### Chosen Solution
**Dapr Jobs API (Scheduler Component)**

### Rationale
- **Exact Timing**: Jobs execute at precise datetime, no polling delays
- **No Polling**: Event-driven callbacks, efficient resource usage
- **Better Demo**: Judges can see exact-time reminders trigger instantly
- **Scalable**: Jobs managed by Dapr runtime, not application code
- **Portable**: Works across any Kubernetes cluster with Dapr

### Alternatives Considered

#### Cron Bindings
- **Pros**: Simple cron expression syntax, familiar pattern
- **Cons**:
  - Polling-based (checks every minute)
  - Less precise timing
  - Requires application to maintain cron schedules
- **Rejected Because**: Polling overhead and imprecise timing unsuitable for reminder feature

#### Application-Level Scheduler (APScheduler, Celery Beat)
- **Pros**: Full control, rich features
- **Cons**:
  - Requires additional dependencies
  - State management complexity
  - Not cloud-native
  - Violates Dapr abstraction principle
- **Rejected Because**: Adds complexity and violates Dapr-only infrastructure access constraint

### Implementation Details

**Dapr Jobs API Usage**:
```python
# Schedule a reminder job
job_data = {
    "schedule": "@every 1s",  # Or specific datetime
    "data": {
        "task_id": task_id,
        "user_id": user_id,
        "reminder_time": due_date.isoformat()
    }
}
response = requests.post(
    f"http://localhost:3500/v1.0-alpha1/jobs/{job_name}",
    json=job_data
)
```

**Callback Endpoint**:
- Application exposes `/api/jobs/reminder-callback` endpoint
- Dapr invokes callback at scheduled time
- Application publishes reminder event to Kafka

---

## Decision 3: Secret Storage - Dapr Secretstores

### Chosen Solution
**Dapr Secretstores (Kubernetes Secret Store Component)**

### Rationale
- **Portable**: Same API works with Kubernetes Secrets, Azure Key Vault, AWS Secrets Manager, HashiCorp Vault
- **Unified API**: Single interface for all secret access (`GET /v1.0/secrets/{store}/{key}`)
- **Future-Proof**: Easy migration to cloud secret managers without code changes
- **Security**: Secrets never exposed in environment variables or logs
- **Audit Trail**: Dapr logs secret access for compliance

### Alternatives Considered

#### Kubernetes Secrets Only (Direct Environment Variables)
- **Pros**: Simple, native Kubernetes feature, no additional components
- **Cons**:
  - Vendor lock-in (Kubernetes-specific)
  - Secrets visible in pod specs and environment
  - No unified API for multi-cloud
  - Harder to rotate secrets
- **Rejected Because**: Violates portability principle and less secure

#### External Secret Manager (HashiCorp Vault)
- **Pros**: Enterprise-grade, advanced features (dynamic secrets, rotation)
- **Cons**:
  - Additional infrastructure to manage
  - Complexity overkill for demo
  - Requires Vault server deployment
- **Rejected Because**: Unnecessary complexity for Phase V scope

### Implementation Details

**Dapr Component Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
  - name: vaultName
    value: ""  # Empty for default namespace
```

**Application Usage**:
```python
# Fetch secret via Dapr API
response = requests.get(
    "http://localhost:3500/v1.0/secrets/kubernetes-secrets/cohere-api-key"
)
api_key = response.json()["cohere-api-key"]
```

**Kubernetes Secret Creation**:
```bash
kubectl create secret generic app-secrets \
  --from-literal=cohere-api-key=$COHERE_API_KEY \
  --from-literal=better-auth-secret=$BETTER_AUTH_SECRET \
  --from-literal=database-url=$DATABASE_URL
```

---

## Decision 4: Helm Upgrade Strategy

### Chosen Solution
**Patch Existing Phase IV Chart (Incremental Evolution)**

### Rationale
- **Version Continuity**: Maintains chart history (0.1.0 → 0.2.0)
- **Incremental Changes**: Clear diff shows exactly what Phase V adds
- **Rollback Safety**: Easy to rollback to Phase IV version if needed
- **Minimal Risk**: Existing templates remain mostly unchanged
- **Best Practice**: Semantic versioning for infrastructure as code

### Alternatives Considered

#### Create New Chart (todo-app-v2)
- **Pros**: Clean slate, no legacy baggage
- **Cons**:
  - Breaks version continuity
  - Harder to track changes from Phase IV
  - Duplicate configuration
  - Confusing for judges reviewing evolution
- **Rejected Because**: Violates incremental evolution principle

#### Separate Dapr Chart
- **Pros**: Modular, Dapr components separate from application
- **Cons**:
  - Two charts to manage
  - Dependency coordination complexity
  - Not a single deployable unit
- **Rejected Because**: Increases operational complexity

### Implementation Details

**Version Bump**:
- Current: `version: 0.1.0` (Phase IV)
- New: `version: 0.2.0` (Phase V - minor bump for new features)

**Changes to Existing Templates**:
- `deployment-frontend.yaml`: Add Dapr annotations
- `deployment-backend.yaml`: Add Dapr annotations
- `secrets.yaml`: Add Kafka credentials
- `values.yaml`: Add Dapr configuration section

**New Templates**:
- `templates/dapr-components.yaml`: Deploy Dapr components to cluster

**New Values File**:
- `values-oke.yaml`: OKE-specific overrides (image registry, resource limits, ingress)

---

## Decision 5: GitHub Actions Runner

### Chosen Solution
**ubuntu-latest (GitHub-Hosted Runner)**

### Rationale
- **Free**: Included in GitHub Actions free tier (2000 minutes/month)
- **Sufficient**: Adequate resources for Docker builds and Helm deployments
- **Zero Maintenance**: No infrastructure to manage
- **Fast Setup**: Works immediately, no configuration needed
- **Standard Environment**: Consistent, well-documented tooling

### Alternatives Considered

#### Self-Hosted Runner
- **Pros**: Unlimited build minutes, full control, custom tools
- **Cons**:
  - Requires server infrastructure
  - Maintenance overhead (updates, security patches)
  - Additional cost (server hosting)
  - Complexity for demo purposes
- **Rejected Because**: Unnecessary complexity and cost for hackathon demo

#### Larger GitHub-Hosted Runner (ubuntu-latest-4-cores)
- **Pros**: Faster builds, more parallelism
- **Cons**:
  - Paid feature (not in free tier)
  - Violates free tier compliance
- **Rejected Because**: Standard runner sufficient for build times

### Implementation Details

**Runner Specification**:
```yaml
runs-on: ubuntu-latest
```

**Available Tools** (pre-installed):
- Docker 24+
- kubectl 1.28+
- Helm 3.x
- Python 3.11
- Node.js 20
- Git, curl, jq

**Build Time Estimates**:
- Test stage: ~2 minutes
- Build stage: ~3 minutes (Docker multi-stage builds)
- Push stage: ~1 minute
- Deploy stage: ~2 minutes
- **Total**: ~8 minutes (well within 10-minute target)

---

## Decision 6: Container Registry

### Chosen Solution
**GitHub Container Registry (ghcr.io)**

### Rationale
- **Integrated**: Native GitHub integration, automatic authentication
- **Free**: Unlimited public images, generous private image storage
- **Private Option**: Can keep images private for security
- **No Rate Limits**: Unlike Docker Hub free tier (100 pulls/6 hours)
- **GitHub Actions Native**: Seamless authentication with `GITHUB_TOKEN`
- **Package Linking**: Images linked to repository for traceability

### Alternatives Considered

#### Docker Hub
- **Pros**: Popular, familiar, good documentation
- **Cons**:
  - Rate limits on free tier (100 pulls/6 hours)
  - Requires separate authentication
  - Not integrated with GitHub
- **Rejected Because**: Rate limits problematic for CI/CD, less integrated

#### Oracle Container Registry (OCIR)
- **Pros**: Native OCI integration, close to OKE cluster
- **Cons**:
  - Additional setup (OCI authentication, tenancy configuration)
  - Less familiar to judges
  - Requires OCI CLI configuration in GitHub Actions
- **Rejected Because**: Additional complexity without significant benefit

### Implementation Details

**Registry URL Format**:
```
ghcr.io/<github-username>/<image-name>:<tag>
```

**Authentication in GitHub Actions**:
```yaml
- name: Login to GitHub Container Registry
  uses: docker/login-action@v2
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

**Image Tagging Strategy**:
- Development: `latest`
- Production: `v<semver>` (e.g., `v1.0.0`)
- CI builds: `sha-<git-commit-sha>` (e.g., `sha-abc1234`)

**Image Names**:
- Frontend: `ghcr.io/<username>/todo-frontend:latest`
- Backend: `ghcr.io/<username>/todo-backend:latest`

---

## Dapr Component Specifications

### Component 1: Kafka Pub/Sub

**File**: `infra/dapr-components/kafka-pubsub.yaml`

**Purpose**: Enable event publishing and subscription via Kafka/Redpanda

**Configuration**:
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
  - name: brokers
    value: "seed-abc123.cloud.redpanda.com:9092"
  - name: authType
    value: "password"
  - name: saslUsername
    secretKeyRef:
      name: kafka-secrets
      key: username
  - name: saslPassword
    secretKeyRef:
      name: kafka-secrets
      key: password
  - name: saslMechanism
    value: "SCRAM-SHA-256"
  - name: consumerGroup
    value: "todo-app-group"
  - name: clientId
    value: "todo-app"
scopes:
- backend
- chat-api
```

**Key Metadata**:
- `brokers`: Redpanda Cloud bootstrap server
- `authType`: SASL authentication
- `saslMechanism`: SCRAM-SHA-256 (Redpanda requirement)
- `consumerGroup`: Logical grouping for consumers
- `scopes`: Only backend and chat-api can use this component

### Component 2: PostgreSQL State Store

**File**: `infra/dapr-components/state-postgresql.yaml`

**Purpose**: Provide state management via Neon PostgreSQL

**Configuration**:
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
  - name: connectionString
    secretKeyRef:
      name: app-secrets
      key: database-url
  - name: tableName
    value: "dapr_state"
  - name: keyPrefix
    value: "todo-app"
scopes:
- backend
- chat-api
```

**Key Metadata**:
- `connectionString`: Neon PostgreSQL connection string from secrets
- `tableName`: Dapr creates this table automatically
- `keyPrefix`: Namespace for state keys

### Component 3: Scheduler/Jobs

**File**: `infra/dapr-components/scheduler-jobs.yaml`

**Purpose**: Enable scheduled job execution for reminders

**Configuration**:
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
  - name: namespace
    value: "default"
scopes:
- backend
```

**Key Metadata**:
- `namespace`: Kubernetes namespace for job resources
- Uses Kubernetes CronJob resources under the hood

### Component 4: Kubernetes Secrets Store

**File**: `infra/dapr-components/secretstores-kubernetes.yaml`

**Purpose**: Provide unified secret access API

**Configuration**:
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
```

**Key Metadata**:
- No additional metadata required for default namespace
- Reads from Kubernetes Secrets in same namespace

---

## Oracle OKE Cluster Setup

### Provisioning Options

#### Option 1: OCI Console (Recommended for First-Time Setup)
1. Navigate to OCI Console → Developer Services → Kubernetes Clusters (OKE)
2. Click "Create Cluster"
3. Select "Quick Create" workflow
4. Configure:
   - Name: `todo-app-cluster`
   - Kubernetes Version: 1.28 or later
   - Node Pool Shape: `VM.Standard.E2.1.Micro` (always-free)
   - Number of Nodes: 2 (within free tier)
   - Node Pool Subnet: Public subnet
5. Click "Create Cluster" and wait ~10 minutes

#### Option 2: OCI CLI (Recommended for Automation)
```bash
# Create VCN and subnets (if not exists)
oci network vcn create \
  --compartment-id <compartment-ocid> \
  --display-name todo-app-vcn \
  --cidr-block 10.0.0.0/16

# Create OKE cluster
oci ce cluster create \
  --compartment-id <compartment-ocid> \
  --name todo-app-cluster \
  --kubernetes-version v1.28.2 \
  --vcn-id <vcn-ocid> \
  --service-lb-subnet-ids '["<subnet-ocid>"]'

# Create node pool
oci ce node-pool create \
  --cluster-id <cluster-ocid> \
  --compartment-id <compartment-ocid> \
  --name todo-app-nodes \
  --node-shape VM.Standard.E2.1.Micro \
  --size 2 \
  --kubernetes-version v1.28.2 \
  --node-image-id <image-ocid>
```

### kubectl Access Configuration

```bash
# Generate kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file $HOME/.kube/config \
  --region <region> \
  --token-version 2.0.0

# Verify access
kubectl get nodes
```

### Dapr Installation on OKE

```bash
# Install Dapr CLI (if not installed)
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr installation
dapr status -k

# Expected output:
# NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
# dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   1m   2024-02-09 10:00:00
# dapr-sentry            dapr-system  True     Running  1         1.12.0   1m   2024-02-09 10:00:00
# dapr-operator          dapr-system  True     Running  1         1.12.0   1m   2024-02-09 10:00:00
# dapr-placement         dapr-system  True     Running  1         1.12.0   1m   2024-02-09 10:00:00
```

### Resource Allocation Strategy

**OKE Always-Free Tier Limits**:
- Total: 4 OCPU, 24GB RAM across all nodes
- Per Node (2 nodes): 2 OCPU, 12GB RAM

**Resource Distribution**:
- Kubernetes System Pods: ~1 OCPU, ~4GB RAM
- Dapr System Pods: ~0.5 OCPU, ~2GB RAM
- Application Pods: ~2.5 OCPU, ~18GB RAM

**Pod Resource Requests/Limits**:
- Frontend: 200m CPU / 256Mi RAM (requests), 500m CPU / 512Mi RAM (limits)
- Backend: 300m CPU / 512Mi RAM (requests), 1000m CPU / 1Gi RAM (limits)
- Dapr Sidecars: 100m CPU / 128Mi RAM (requests), 200m CPU / 256Mi RAM (limits)

---

## GitHub Actions Workflow Design

### Pipeline Stages

#### Stage 1: Test
```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    - name: Run tests
      run: |
        cd backend
        pytest tests/ -v
```

#### Stage 2: Build
```yaml
build:
  needs: test
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    - name: Build frontend image
      run: |
        docker build -t ghcr.io/${{ github.repository_owner }}/todo-frontend:${{ github.sha }} ./frontend
    - name: Build backend image
      run: |
        docker build -t ghcr.io/${{ github.repository_owner }}/todo-backend:${{ github.sha }} ./backend
```

#### Stage 3: Push
```yaml
push:
  needs: build
  runs-on: ubuntu-latest
  steps:
    - name: Login to GitHub Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    - name: Push images
      run: |
        docker push ghcr.io/${{ github.repository_owner }}/todo-frontend:${{ github.sha }}
        docker push ghcr.io/${{ github.repository_owner }}/todo-backend:${{ github.sha }}
```

#### Stage 4: Deploy
```yaml
deploy:
  needs: push
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Configure kubectl
      run: |
        mkdir -p $HOME/.kube
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > $HOME/.kube/config
    - name: Deploy with Helm
      run: |
        helm upgrade --install todo-app ./infra/helm/todo-app \
          --values ./infra/helm/todo-app/values-oke.yaml \
          --set frontend.image.tag=${{ github.sha }} \
          --set backend.image.tag=${{ github.sha }} \
          --wait --timeout 5m
```

### Authentication Strategy

**GitHub Secrets Required**:
- `KUBECONFIG`: Base64-encoded kubeconfig file for OKE cluster
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions
- `COHERE_API_KEY`: Cohere API key (for Kubernetes Secrets creation)
- `BETTER_AUTH_SECRET`: JWT secret (for Kubernetes Secrets creation)
- `DATABASE_URL`: Neon PostgreSQL connection string (for Kubernetes Secrets creation)

**OCI Authentication**:
- Use kubeconfig with token-based authentication
- Token auto-refreshes via OCI CLI integration
- No need for separate OCI credentials in GitHub Actions

### Rollback Procedures

**Automatic Rollback** (via Helm):
```bash
# Helm automatically rolls back on deployment failure
helm upgrade --install todo-app ./infra/helm/todo-app --atomic
```

**Manual Rollback**:
```bash
# List releases
helm history todo-app

# Rollback to previous version
helm rollback todo-app <revision-number>
```

---

## Monitoring and Logging Strategy

### Log Sources

1. **Application Logs** (kubectl logs):
   ```bash
   # Frontend logs
   kubectl logs -l app=frontend -c frontend

   # Backend logs
   kubectl logs -l app=backend -c backend

   # Dapr sidecar logs
   kubectl logs -l app=backend -c daprd
   ```

2. **Dapr Dashboard**:
   ```bash
   # Deploy Dapr dashboard
   dapr dashboard -k

   # Access at http://localhost:8080
   ```

3. **kubectl-ai/kagent Commands**:
   ```bash
   # Cluster health analysis
   kagent analyze cluster

   # Pod debugging
   kagent debug pod backend-<pod-id>

   # Resource optimization
   kubectl-ai optimize deployment backend

   # Log analysis
   kagent logs backend --analyze
   ```

### Log Structure

**Structured JSON Logging**:
```json
{
  "timestamp": "2026-02-09T10:00:00Z",
  "level": "INFO",
  "service": "backend",
  "trace_id": "abc123",
  "user_id": "user-456",
  "task_id": "task-789",
  "message": "Task created successfully",
  "event_id": "evt-xyz"
}
```

**Correlation IDs**:
- Dapr automatically injects `trace_id` in headers
- Application propagates `trace_id` through all operations
- Events include `event_id` for end-to-end tracing

### Troubleshooting Guide

**Common Issues**:

1. **Pod Not Starting**:
   ```bash
   kubectl describe pod <pod-name>
   kubectl logs <pod-name> -c daprd
   ```

2. **Dapr Component Not Ready**:
   ```bash
   kubectl get components
   kubectl describe component kafka-pubsub
   ```

3. **Event Not Publishing**:
   ```bash
   # Check Dapr sidecar logs
   kubectl logs <pod-name> -c daprd | grep pubsub

   # Check application logs
   kubectl logs <pod-name> -c backend | grep event
   ```

4. **Secrets Not Accessible**:
   ```bash
   # Verify secret exists
   kubectl get secret app-secrets

   # Check Dapr secrets component
   kubectl describe component kubernetes-secrets
   ```

---

## Summary

All architectural decisions have been documented with clear rationale, alternatives considered, and implementation details. The research phase is complete and ready for Phase 1 (Design) execution.

**Key Decisions**:
1. ✅ Redpanda Cloud Serverless for Kafka (zero management, free)
2. ✅ Dapr Jobs API for reminders (exact timing, no polling)
3. ✅ Dapr Secretstores for portable secret management
4. ✅ Patch existing Helm chart for incremental evolution
5. ✅ GitHub-hosted ubuntu-latest runner (free, sufficient)
6. ✅ GitHub Container Registry (ghcr.io) for images (integrated, no rate limits)

**Next Steps**:
- Proceed to Phase 1 (Design) to create architecture diagrams and detailed specifications
- Generate artifacts: architecture.md, dapr-components.md, cicd-pipeline.md, monitoring.md, quickstart.md
