# Architecture: Cloud-Native Todo AI Chatbot Deployment

**Feature**: 001-k8s-deployment
**Date**: 2026-02-08
**Purpose**: Infrastructure architecture design for Kubernetes deployment

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Developer Machine                         │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Minikube Cluster                         │ │
│  │                                                              │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │              Ingress Controller (nginx)               │  │ │
│  │  │              Host: todo.local                         │  │ │
│  │  └────────────┬─────────────────────────┬────────────────┘  │ │
│  │               │                         │                    │ │
│  │               │ /                       │ /api               │ │
│  │               ▼                         ▼                    │ │
│  │  ┌─────────────────────┐  ┌─────────────────────┐          │ │
│  │  │  Frontend Service   │  │  Backend Service    │          │ │
│  │  │  (ClusterIP:3000)   │  │  (ClusterIP:8000)   │          │ │
│  │  └──────────┬──────────┘  └──────────┬──────────┘          │ │
│  │             │                        │                      │ │
│  │             ▼                        ▼                      │ │
│  │  ┌─────────────────────┐  ┌─────────────────────┐          │ │
│  │  │  Frontend Pod       │  │  Backend Pod        │          │ │
│  │  │  ┌───────────────┐  │  │  ┌───────────────┐ │          │ │
│  │  │  │ Next.js App   │  │  │  │ FastAPI App   │ │          │ │
│  │  │  │ Port: 3000    │  │  │  │ Port: 8000    │ │          │ │
│  │  │  │ Resources:    │  │  │  │ Resources:    │ │          │ │
│  │  │  │ 256Mi/200m    │  │  │  │ 512Mi/300m    │ │          │ │
│  │  │  └───────────────┘  │  │  └───────────────┘ │          │ │
│  │  │                     │  │                     │          │ │
│  │  │  Env from:          │  │  Env from:          │          │ │
│  │  │  - ConfigMap        │  │  - ConfigMap        │          │ │
│  │  │  - Secrets          │  │  - Secrets          │          │ │
│  │  └─────────────────────┘  └──────────┬──────────┘          │ │
│  │                                       │                      │ │
│  └───────────────────────────────────────┼──────────────────────┘ │
│                                          │                        │
└──────────────────────────────────────────┼────────────────────────┘
                                           │
                                           │ HTTPS
                                           ▼
                        ┌──────────────────────────────────┐
                        │   External Dependencies          │
                        │                                  │
                        │  ┌────────────────────────────┐  │
                        │  │  Neon PostgreSQL           │  │
                        │  │  (Serverless Database)     │  │
                        │  └────────────────────────────┘  │
                        │                                  │
                        │  ┌────────────────────────────┐  │
                        │  │  Cohere API                │  │
                        │  │  (AI Language Model)       │  │
                        │  └────────────────────────────┘  │
                        └──────────────────────────────────┘
```

## Container Architecture

### Frontend Container Design

**Multi-Stage Build Strategy**:

```
Stage 1: Dependencies (node:20-alpine)
├── Install production dependencies only
├── Use package-lock.json for deterministic builds
└── Output: node_modules/

Stage 2: Builder (node:20-alpine)
├── Install all dependencies (dev + prod)
├── Copy source code
├── Run next build with standalone output
└── Output: .next/standalone, .next/static, public/

Stage 3: Runner (node:20-alpine)
├── Copy standalone server from builder
├── Copy static assets from builder
├── Set NODE_ENV=production
├── Expose port 3000
└── Run: node server.js
```

**Image Characteristics**:
- Base image: node:20-alpine (~40MB)
- Final image size: ~150MB
- Startup time: < 5 seconds
- Memory footprint: ~100MB at idle

**Environment Variables**:
- `NEXT_PUBLIC_API_URL`: Backend API URL (injected at runtime)
- `NODE_ENV`: production (set in Dockerfile)

### Backend Container Design

**Single-Stage Build Strategy**:

```
Stage 1: Application (python:3.11-slim)
├── Install system dependencies (if needed)
├── Copy requirements.txt
├── Install Python packages with pip
├── Copy application code
├── Expose port 8000
└── Run: uvicorn main:app --host 0.0.0.0 --port 8000
```

**Image Characteristics**:
- Base image: python:3.11-slim (~150MB)
- Final image size: ~300MB
- Startup time: < 10 seconds
- Memory footprint: ~150MB at idle

**Environment Variables**:
- `DATABASE_URL`: Neon PostgreSQL connection string (from Secret)
- `BETTER_AUTH_SECRET`: JWT signing secret (from Secret)
- `COHERE_API_KEY`: Cohere API key (from Secret)
- `ENVIRONMENT`: production (from ConfigMap)

### Image Tagging Strategy

**Development**:
- Tag: `latest`
- Built locally, loaded into Minikube
- No registry push required

**Production** (future):
- Tag: `v{major}.{minor}.{patch}` (semantic versioning)
- Tag: `{git-sha}` (commit-specific)
- Push to container registry (Docker Hub, ECR, GCR)

## Kubernetes Resource Architecture

### Deployment Specifications

**Frontend Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  labels:
    app: todo-app
    component: frontend
spec:
  replicas: 1  # Single replica for local demo
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Zero-downtime updates
  selector:
    matchLabels:
      app: todo-app
      component: frontend
  template:
    metadata:
      labels:
        app: todo-app
        component: frontend
    spec:
      containers:
      - name: frontend
        image: todo-frontend:latest
        imagePullPolicy: Never  # Use local image
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          valueFrom:
            configMapKeyRef:
              name: todo-config
              key: apiUrl
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
```

**Backend Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  labels:
    app: todo-app
    component: backend
spec:
  replicas: 1  # Single replica for local demo
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Zero-downtime updates
  selector:
    matchLabels:
      app: todo-app
      component: backend
  template:
    metadata:
      labels:
        app: todo-app
        component: backend
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        imagePullPolicy: Never  # Use local image
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: todo-secrets
        - configMapRef:
            name: todo-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "300m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Service Discovery

**Frontend Service**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
  labels:
    app: todo-app
    component: frontend
spec:
  type: ClusterIP
  selector:
    app: todo-app
    component: frontend
  ports:
  - port: 3000
    targetPort: 3000
    protocol: TCP
    name: http
```

**Backend Service**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
  labels:
    app: todo-app
    component: backend
spec:
  type: ClusterIP
  selector:
    app: todo-app
    component: backend
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
```

### Ingress Configuration

**Ingress Resource**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  labels:
    app: todo-app
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: todo.local
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
```

**Host Mapping**:
- Add to /etc/hosts: `127.0.0.1 todo.local`
- Access application: http://todo.local
- API requests: http://todo.local/api/*

### Secret and ConfigMap Organization

**Secrets** (todo-secrets):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
type: Opaque
data:
  DATABASE_URL: <base64-encoded>
  BETTER_AUTH_SECRET: <base64-encoded>
  COHERE_API_KEY: <base64-encoded>
```

**ConfigMap** (todo-config):
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-config
data:
  ENVIRONMENT: "production"
  apiUrl: "http://todo.local/api"
```

## Network Architecture

### Pod-to-Pod Communication

- **Internal DNS**: Kubernetes DNS resolves service names
- **Frontend → Backend**: Uses service name `backend:8000`
- **Network Policy**: Not implemented (single-node cluster, trusted environment)

### Service-to-Service Routing

- **ClusterIP Services**: Internal load balancing
- **Service Discovery**: DNS-based (backend.default.svc.cluster.local)
- **Port Mapping**: Service port → Target port (container port)

### Ingress-to-Service Mapping

```
External Request (http://todo.local/api/tasks)
    ↓
Ingress Controller (nginx)
    ↓
Path Matching (/api → backend service)
    ↓
Backend Service (ClusterIP:8000)
    ↓
Backend Pod (Container:8000)
    ↓
FastAPI Application
```

### External Connectivity

**Database Connection**:
- Backend pods connect to Neon PostgreSQL via public internet
- Connection string includes SSL/TLS encryption
- No special network configuration required in Minikube

**Cohere API Connection**:
- Backend pods connect to Cohere API via public internet
- HTTPS with API key authentication
- No special network configuration required

## Observability Architecture

### Logging Strategy

**Log Collection**:
- All containers log to stdout/stderr
- Kubernetes captures logs automatically
- Access via: `kubectl logs <pod-name>`

**Log Format**:
- Frontend: Next.js default format (structured JSON in production)
- Backend: FastAPI/Uvicorn format (structured with timestamps)

**Log Retention**:
- Minikube: Logs retained until pod deletion
- Production: Use log aggregation (Loki, CloudWatch, etc.)

### Health Check Endpoints

**Frontend Health Check**:
- Endpoint: `GET /`
- Response: 200 OK (Next.js renders homepage)
- Used by: Readiness and liveness probes

**Backend Health Check**:
- Endpoint: `GET /api/health`
- Response: `{"status": "healthy", "timestamp": "..."}`
- Used by: Readiness and liveness probes
- Optional: Include database connectivity check

### Probe Configuration

**Readiness Probe**:
- Purpose: Is pod ready to serve traffic?
- Initial delay: 10s (allow startup time)
- Period: 5s (check frequently)
- Failure threshold: 3 (remove from service after 3 failures)

**Liveness Probe**:
- Purpose: Is pod healthy or should it be restarted?
- Initial delay: 30s (allow longer startup)
- Period: 10s (check less frequently)
- Failure threshold: 3 (restart after 3 failures)

### Resource Monitoring

**Metrics Collection**:
- Minikube metrics-server addon enabled
- Access via: `kubectl top pods`
- Metrics: CPU usage, memory usage

**Resource Limits**:
- Requests: Guaranteed resources for scheduling
- Limits: Maximum resources before throttling/OOMKill
- Conservative values for local Minikube

### Debugging Workflows

**Pod Inspection**:
```bash
# Check pod status
kubectl get pods

# Describe pod (events, conditions)
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>

# Follow logs in real-time
kubectl logs -f <pod-name>

# Execute commands in pod
kubectl exec -it <pod-name> -- /bin/sh
```

**AI-Assisted Debugging**:
```bash
# kubectl-ai: Analyze pod failures
kubectl-ai "why is backend pod crashing?"

# kagent: Cluster health analysis
kagent "check cluster health"

# kagent: Log analysis
kagent "analyze logs for errors in backend pod"
```

## Deployment Architecture

### Helm Release Lifecycle

**Installation**:
```bash
helm install todo-app ./infra/helm/todo-app \
  --set secrets.betterAuthSecret=$BETTER_AUTH_SECRET \
  --set secrets.cohereApiKey=$COHERE_API_KEY \
  --set secrets.databaseUrl=$DATABASE_URL
```

**Upgrade**:
```bash
helm upgrade todo-app ./infra/helm/todo-app \
  --set secrets.betterAuthSecret=$BETTER_AUTH_SECRET \
  --set secrets.cohereApiKey=$COHERE_API_KEY \
  --set secrets.databaseUrl=$DATABASE_URL
```

**Rollback**:
```bash
helm rollback todo-app <revision>
```

**Uninstallation**:
```bash
helm uninstall todo-app
```

### Zero-Downtime Deployment Strategy

**Rolling Update Process**:
1. Helm updates Deployment spec
2. Kubernetes creates new pod with updated image
3. New pod starts, readiness probe checks begin
4. Once ready, new pod added to service endpoints
5. Old pod receives SIGTERM, graceful shutdown begins
6. After terminationGracePeriodSeconds, old pod terminated
7. Process repeats for remaining replicas

**Configuration**:
- `maxSurge: 1`: One extra pod during update
- `maxUnavailable: 0`: No pods down during update
- Requires readiness probes to work correctly

## Security Architecture

### Secret Management

**Kubernetes Secrets**:
- Stored in etcd (base64 encoded, not encrypted by default)
- Mounted as environment variables in pods
- Never committed to version control
- Provided at Helm install time via --set flags

**Best Practices**:
- Use external secret management for production (Sealed Secrets, External Secrets Operator)
- Rotate secrets regularly
- Limit secret access with RBAC (not implemented in local demo)

### Container Security

**Non-Root User**:
- Containers should run as non-root user
- Not enforced in local demo (adds complexity)
- Recommended for production

**Image Scanning**:
- Scan images for vulnerabilities before deployment
- Use tools like Trivy, Snyk, or Docker Scout
- Not implemented in local demo

### Network Security

**Network Policies**:
- Not implemented (single-node cluster, trusted environment)
- Production: Restrict pod-to-pod communication
- Production: Deny all by default, allow specific traffic

## Scalability Considerations

### Horizontal Scaling

**Current Configuration**:
- Frontend: 1 replica (sufficient for local demo)
- Backend: 1 replica (sufficient for local demo)

**Production Scaling**:
- Frontend: 3+ replicas for high availability
- Backend: 3+ replicas for high availability
- Use Horizontal Pod Autoscaler (HPA) based on CPU/memory

**Database Scaling**:
- Neon PostgreSQL handles scaling automatically
- No application changes required

### Vertical Scaling

**Resource Adjustment**:
- Increase requests/limits in values.yaml
- Helm upgrade applies new resource configuration
- Pods recreated with new resource allocation

## Disaster Recovery

### Backup Strategy

**Application State**:
- Stateless applications (no local data)
- All state in external database (Neon)
- No backup required for application pods

**Database Backup**:
- Neon handles database backups automatically
- Point-in-time recovery available
- No manual backup required

### Recovery Procedures

**Pod Failure**:
- Kubernetes automatically restarts failed pods
- Liveness probes detect unhealthy pods
- Self-healing without manual intervention

**Node Failure**:
- Not applicable (single-node Minikube)
- Production: Pods rescheduled to healthy nodes

**Complete Cluster Failure**:
- Recreate Minikube cluster
- Redeploy with Helm install
- Application state preserved in external database

## Performance Optimization

### Image Optimization

- Multi-stage builds reduce image size
- Minimal base images (alpine, slim)
- Layer caching for faster builds
- .dockerignore excludes unnecessary files

### Resource Optimization

- Conservative requests prevent over-provisioning
- Limits prevent resource exhaustion
- Proper probe configuration prevents unnecessary restarts

### Network Optimization

- ClusterIP services for internal communication
- Ingress for external access (single entry point)
- Keep-alive connections for database

## Future Enhancements

### Observability

- Prometheus for metrics collection
- Grafana for visualization
- Loki for log aggregation
- Jaeger for distributed tracing

### Scalability

- Horizontal Pod Autoscaler (HPA)
- Vertical Pod Autoscaler (VPA)
- Cluster Autoscaler (for cloud deployments)

### Security

- Network policies for pod isolation
- Pod security policies/standards
- RBAC for access control
- Secret encryption at rest

### Reliability

- Pod disruption budgets
- Multi-zone deployment (cloud)
- Database read replicas
- CDN for static assets
