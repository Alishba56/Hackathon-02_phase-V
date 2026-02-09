# AI DevOps Workflows: Cloud-Native Todo AI Chatbot

**Feature**: 001-k8s-deployment
**Date**: 2026-02-08
**Purpose**: AI-powered DevOps tool integration patterns and workflows

## Overview

This document provides comprehensive workflows for using AI-powered DevOps tools (Gordon, kubectl-ai, kagent) throughout the Kubernetes deployment lifecycle. Each tool is used for specific phases where it provides maximum value, with documented fallback procedures when tools are unavailable.

## Tool Responsibilities

| Tool | Primary Use Cases | Phase |
|------|------------------|-------|
| **Gordon** | Dockerfile generation, image optimization, build troubleshooting | Containerization |
| **kubectl-ai** | Manifest generation, deployment operations, scaling, debugging | Deployment & Operations |
| **kagent** | Cluster health analysis, resource optimization, log analysis | Monitoring & Optimization |

## Gordon (Docker AI Agent) Workflows

### Prerequisites

- Docker Desktop 4.53+ Beta installed
- Gordon feature enabled in Docker Desktop settings
- Access to frontend/ and backend/ directories

### Workflow 1: Generate Frontend Dockerfile

**Objective**: Create production-ready Dockerfile for Next.js application

**Command**:
```bash
cd frontend
docker ai "Create a production-ready multi-stage Dockerfile for Next.js 16 application with standalone output mode"
```

**Expected AI Response**:
Gordon analyzes the project structure and generates a Dockerfile with:
- Multi-stage build (dependencies → builder → runner)
- node:20-alpine base images
- Standalone output configuration
- Proper layer caching
- Non-root user execution

**Validation**:
```bash
# Build image
docker build -t todo-frontend:latest .

# Test locally
docker run -p 3000:3000 todo-frontend:latest

# Check image size
docker images todo-frontend:latest
# Expected: ~150MB
```

**Fallback (Gordon Unavailable)**:
Use pre-generated Dockerfile in `infra/docker/frontend/Dockerfile`:
```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
USER nextjs
EXPOSE 3000
ENV PORT 3000
CMD ["node", "server.js"]
```

### Workflow 2: Generate Backend Dockerfile

**Objective**: Create production-ready Dockerfile for FastAPI application

**Command**:
```bash
cd backend
docker ai "Create a production Dockerfile for FastAPI application with uvicorn, optimized for Python 3.11"
```

**Expected AI Response**:
Gordon generates a Dockerfile with:
- python:3.11-slim base image
- Efficient dependency installation
- Health check configuration
- Proper working directory setup
- Uvicorn production configuration

**Validation**:
```bash
# Build image
docker build -t todo-backend:latest .

# Test locally
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e BETTER_AUTH_SECRET="test" \
  -e COHERE_API_KEY="test" \
  todo-backend:latest

# Check image size
docker images todo-backend:latest
# Expected: ~300MB
```

**Fallback (Gordon Unavailable)**:
Use pre-generated Dockerfile in `infra/docker/backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Workflow 3: Optimize Existing Dockerfiles

**Objective**: Get AI suggestions for improving existing Dockerfiles

**Command**:
```bash
docker ai "Analyze this Dockerfile and suggest optimizations for size and build speed" < Dockerfile
```

**Expected AI Response**:
- Layer caching improvements
- Base image recommendations
- Multi-stage build suggestions
- Security enhancements (non-root user)
- .dockerignore recommendations

**Action**: Apply suggested optimizations and rebuild images

### Workflow 4: Troubleshoot Build Failures

**Objective**: Debug Docker build issues with AI assistance

**Command**:
```bash
docker ai "Why is my Docker build failing with error: [paste error message]"
```

**Expected AI Response**:
- Root cause analysis
- Specific fix recommendations
- Alternative approaches
- Related documentation links

## kubectl-ai Workflows

### Prerequisites

- kubectl-ai installed and configured
- Minikube cluster running
- kubectl context set to minikube

### Workflow 1: Generate Deployment Manifests

**Objective**: Create Kubernetes deployment manifests from natural language

**Command**:
```bash
kubectl-ai "Create a deployment for todo-frontend with 1 replica, 256Mi memory request, 512Mi memory limit, 200m CPU request, 500m CPU limit, and readiness probe on port 3000"
```

**Expected Output**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-frontend
  template:
    metadata:
      labels:
        app: todo-frontend
    spec:
      containers:
      - name: frontend
        image: todo-frontend:latest
        ports:
        - containerPort: 3000
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
```

**Action**: Review and apply the generated manifest

### Workflow 2: Scale Deployments

**Objective**: Scale application replicas using natural language

**Command**:
```bash
kubectl-ai "Scale backend deployment to 3 replicas"
```

**Expected Execution**:
```bash
kubectl scale deployment backend --replicas=3
```

**Validation**:
```bash
kubectl get pods -l app=backend
# Should show 3 pods
```

### Workflow 3: Debug Pod Failures

**Objective**: Diagnose why pods are not starting

**Command**:
```bash
kubectl-ai "Why is the backend pod in CrashLoopBackOff state?"
```

**Expected AI Analysis**:
1. Checks pod status and events
2. Analyzes recent logs
3. Identifies common issues:
   - Missing environment variables
   - Database connection failures
   - Port conflicts
   - Resource constraints
4. Provides specific remediation steps

**Follow-up Commands**:
```bash
# Get detailed pod information
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name> --tail=50

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Workflow 4: Create Services

**Objective**: Generate service manifests for deployments

**Command**:
```bash
kubectl-ai "Create a ClusterIP service for frontend deployment exposing port 3000"
```

**Expected Output**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  type: ClusterIP
  selector:
    app: frontend
  ports:
  - port: 3000
    targetPort: 3000
    protocol: TCP
```

### Workflow 5: Configure Ingress

**Objective**: Create ingress resource with path-based routing

**Command**:
```bash
kubectl-ai "Create an ingress for todo.local routing / to frontend:3000 and /api to backend:8000 using nginx ingress class"
```

**Expected Output**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
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

### Workflow 6: Analyze Resource Usage

**Objective**: Get recommendations for resource optimization

**Command**:
```bash
kubectl-ai "Analyze resource usage for all pods and suggest optimal requests and limits"
```

**Expected Analysis**:
- Current resource usage metrics
- Comparison with configured requests/limits
- Recommendations for right-sizing
- Potential cost savings

### Workflow 7: Troubleshoot Networking

**Objective**: Debug service connectivity issues

**Command**:
```bash
kubectl-ai "Why can't frontend pod connect to backend service?"
```

**Expected AI Analysis**:
1. Checks service endpoints
2. Verifies pod labels and selectors
3. Tests DNS resolution
4. Checks network policies
5. Provides specific fix

## kagent Workflows

### Prerequisites

- kagent installed and configured
- Access to Minikube cluster
- kubectl context set to minikube

### Workflow 1: Cluster Health Check

**Objective**: Comprehensive cluster health analysis

**Command**:
```bash
kagent "Check overall cluster health"
```

**Expected Analysis**:
- Node status and resource availability
- Pod health across all namespaces
- Service endpoint status
- Persistent volume claims
- Recent events and warnings
- Resource pressure indicators

**Sample Output**:
```
✅ Cluster Health: HEALTHY

Nodes:
  ✅ minikube: Ready (CPU: 45%, Memory: 60%)

Pods:
  ✅ 4/4 pods running
  ⚠️  backend-xyz: High memory usage (850Mi/1Gi)

Services:
  ✅ All services have endpoints

Recent Issues:
  ⚠️  ImagePullBackOff in namespace default (resolved)

Recommendations:
  - Consider increasing backend memory limit
  - Review recent pod restarts in default namespace
```

### Workflow 2: Resource Optimization

**Objective**: Get recommendations for resource allocation

**Command**:
```bash
kagent "Analyze resource usage and suggest optimizations"
```

**Expected Analysis**:
- Current vs requested resources
- Over-provisioned pods
- Under-provisioned pods
- Cluster capacity utilization
- Cost optimization opportunities

**Sample Output**:
```
Resource Analysis:

Frontend Pod:
  Current: CPU 50m, Memory 120Mi
  Requested: CPU 200m, Memory 256Mi
  Recommendation: Reduce requests to CPU 100m, Memory 150Mi

Backend Pod:
  Current: CPU 280m, Memory 850Mi
  Requested: CPU 300m, Memory 512Mi
  Recommendation: Increase memory limit to 1.5Gi

Cluster Utilization:
  CPU: 35% (room for more workloads)
  Memory: 65% (approaching capacity)
```

### Workflow 3: Log Analysis

**Objective**: Analyze logs for errors and patterns

**Command**:
```bash
kagent "Analyze logs from backend pods for errors in the last hour"
```

**Expected Analysis**:
- Error frequency and patterns
- Common error messages
- Correlation with events
- Root cause suggestions
- Remediation recommendations

**Sample Output**:
```
Log Analysis (last 1 hour):

Errors Found: 12
Most Common:
  - "Database connection timeout" (8 occurrences)
  - "Cohere API rate limit" (4 occurrences)

Timeline:
  10:15 - Database connection issues started
  10:20 - Multiple retry attempts
  10:25 - Connection restored

Root Cause:
  Likely network latency to external database

Recommendations:
  - Increase database connection timeout
  - Implement connection pooling
  - Add retry logic with exponential backoff
```

### Workflow 4: Performance Bottleneck Detection

**Objective**: Identify performance issues

**Command**:
```bash
kagent "Identify performance bottlenecks in the application"
```

**Expected Analysis**:
- Response time analysis
- Resource saturation points
- Slow endpoints
- Database query performance
- External API latency

### Workflow 5: Predict Resource Needs

**Objective**: Forecast resource requirements

**Command**:
```bash
kagent "Based on current usage patterns, predict resource needs for 3x traffic"
```

**Expected Analysis**:
- Current baseline metrics
- Projected resource requirements
- Scaling recommendations
- Potential bottlenecks at scale

### Workflow 6: Security Audit

**Objective**: Identify security concerns

**Command**:
```bash
kagent "Audit cluster for security issues"
```

**Expected Analysis**:
- Pods running as root
- Missing resource limits
- Exposed secrets
- Network policy gaps
- Image vulnerability scan results

## Integrated Demo Script

### Complete AI-Powered Deployment Workflow

**Phase 1: Containerization with Gordon**

```bash
# Step 1: Generate frontend Dockerfile
cd frontend
docker ai "Create production Dockerfile for Next.js 16 with standalone output"

# Step 2: Build and test frontend
docker build -t todo-frontend:latest .
docker run -p 3000:3000 todo-frontend:latest

# Step 3: Generate backend Dockerfile
cd ../backend
docker ai "Create production Dockerfile for FastAPI with uvicorn"

# Step 4: Build and test backend
docker build -t todo-backend:latest .
docker run -p 8000:8000 -e DATABASE_URL="..." todo-backend:latest

# Step 5: Load images into Minikube
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
```

**Phase 2: Deployment with kubectl-ai**

```bash
# Step 6: Generate deployment manifests
kubectl-ai "Create deployment for frontend with 1 replica, 256Mi memory, readiness probe"
kubectl-ai "Create deployment for backend with 1 replica, 512Mi memory, readiness probe"

# Step 7: Create services
kubectl-ai "Create ClusterIP service for frontend on port 3000"
kubectl-ai "Create ClusterIP service for backend on port 8000"

# Step 8: Configure ingress
kubectl-ai "Create ingress for todo.local routing / to frontend and /api to backend"

# Step 9: Apply manifests (or use Helm)
helm install todo-app ./infra/helm/todo-app \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.cohereApiKey="$COHERE_API_KEY" \
  --set secrets.databaseUrl="$DATABASE_URL"

# Step 10: Verify deployment
kubectl get pods,svc,ingress
```

**Phase 3: Operations with kubectl-ai**

```bash
# Step 11: Scale backend
kubectl-ai "Scale backend to 3 replicas"

# Step 12: Check scaling status
kubectl get pods -l component=backend

# Step 13: Simulate failure
kubectl delete pod <backend-pod-name>

# Step 14: Debug with kubectl-ai
kubectl-ai "Why did the backend pod restart?"
```

**Phase 4: Monitoring with kagent**

```bash
# Step 15: Health check
kagent "Check cluster health"

# Step 16: Resource analysis
kagent "Analyze resource usage and suggest optimizations"

# Step 17: Log analysis
kagent "Analyze backend logs for errors"

# Step 18: Performance check
kagent "Identify any performance bottlenecks"
```

**Phase 5: Optimization**

```bash
# Step 19: Apply kagent recommendations
kubectl-ai "Update backend deployment with memory limit 1.5Gi"

# Step 20: Verify improvements
kagent "Compare resource usage before and after optimization"

# Step 21: Final health check
kagent "Confirm cluster is healthy and optimized"
```

## Fallback Procedures

### When Gordon is Unavailable

1. Use pre-generated Dockerfiles in `infra/docker/`
2. Document that Dockerfiles were created following Gordon's best practices
3. Manually optimize images using Docker best practices
4. Reference Gordon in demo as "would be used if available"

### When kubectl-ai is Unavailable

1. Use Helm chart templates (already generated)
2. Use standard kubectl commands for operations
3. Document kubectl-ai commands that would be used
4. Show example outputs from kubectl-ai documentation

### When kagent is Unavailable

1. Use standard kubectl commands for monitoring
2. Use kubectl top for resource metrics
3. Manually analyze logs with kubectl logs
4. Document kagent analysis that would be performed

## Best Practices

1. **Always validate AI-generated configs** before applying to cluster
2. **Test in dry-run mode** when possible
3. **Keep fallback procedures documented** for tool unavailability
4. **Record all AI interactions** in PHRs for traceability
5. **Use AI tools iteratively** - refine prompts based on outputs
6. **Combine AI tools** - use each for its strengths
7. **Maintain baseline configs** - don't rely solely on AI generation
8. **Document AI decisions** - explain why AI recommendations were accepted/rejected

## Troubleshooting AI Tools

### Gordon Not Responding

- Check Docker Desktop version (4.53+ Beta required)
- Verify Gordon feature is enabled in settings
- Restart Docker Desktop
- Check Docker Desktop logs for errors

### kubectl-ai Errors

- Verify kubectl-ai installation: `kubectl-ai version`
- Check kubectl context: `kubectl config current-context`
- Ensure cluster is accessible: `kubectl cluster-info`
- Review kubectl-ai logs for errors

### kagent Connection Issues

- Verify kagent installation: `kagent version`
- Check cluster connectivity: `kubectl get nodes`
- Ensure proper RBAC permissions
- Review kagent configuration

## Success Metrics

Track AI tool effectiveness:

- **Gordon**: Image size reduction, build time improvement
- **kubectl-ai**: Time saved vs manual manifest creation
- **kagent**: Issues detected, optimizations applied
- **Overall**: Deployment time, error reduction, resource efficiency
