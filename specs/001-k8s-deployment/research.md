# Research: Cloud-Native Todo AI Chatbot Deployment

**Feature**: 001-k8s-deployment
**Date**: 2026-02-08
**Purpose**: Technology research and decision documentation for Kubernetes deployment

## Overview

This document captures research findings, technology decisions, and best practices for containerizing and deploying the Phase III Todo AI Chatbot to local Kubernetes (Minikube). All decisions prioritize AI-assisted workflows while maintaining production-ready patterns.

## 1. Next.js Containerization Best Practices

### Research Findings

**Multi-Stage Build Pattern**:
- Stage 1 (dependencies): Install all dependencies with package-lock.json
- Stage 2 (builder): Build Next.js application with `next build`
- Stage 3 (runner): Copy only production artifacts to minimal runtime image

**Standalone Output Mode**:
- Next.js 16+ supports `output: 'standalone'` in next.config.js
- Generates self-contained server with minimal dependencies
- Reduces image size by ~80% compared to full node_modules copy
- Includes only necessary files for production runtime

**Environment Variable Strategy**:
- Build-time variables: Baked into static assets (NEXT_PUBLIC_*)
- Runtime variables: Injected via environment at container startup
- For Kubernetes: Use ConfigMap/Secret mounted as env vars
- Recommendation: Runtime injection for API URLs to support environment portability

**Static Asset Optimization**:
- Next.js automatically optimizes images and static files
- Use nginx as reverse proxy for serving static assets efficiently
- Configure proper caching headers in nginx.conf
- Separate static assets from dynamic routes for better performance

### Decision: Multi-Stage Build with Standalone Output

**Chosen Approach**:
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
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

**Rationale**:
- Minimal final image size (~150MB vs ~1GB with full node_modules)
- Fast startup time (< 5 seconds)
- Production-optimized runtime
- Clear separation of build and runtime dependencies

**Alternatives Considered**:
- Single-stage build: Rejected (large image size, includes dev dependencies)
- nginx + static export: Rejected (loses API routes, SSR capabilities)
- Distroless base: Rejected (debugging complexity, not worth minimal size gain)

## 2. FastAPI Production Deployment

### Research Findings

**Uvicorn Worker Configuration**:
- Single worker sufficient for local Minikube demo
- Multiple workers for production (workers = 2 * CPU cores + 1)
- Use `--host 0.0.0.0` to bind to all interfaces in container
- Configure graceful shutdown timeout (--timeout-graceful-shutdown 30)

**Python Dependency Management**:
- pip with requirements.txt: Simple, widely supported, fast
- poetry: Better dependency resolution, but slower builds
- pip-tools: Deterministic builds with requirements.in → requirements.txt
- Recommendation: pip with requirements.txt for simplicity

**Health Check Endpoints**:
- FastAPI automatic /docs and /redoc endpoints
- Custom /health or /api/health endpoint for K8s probes
- Return 200 OK with basic status (database connectivity optional)
- Keep health checks lightweight (< 100ms response time)

**Graceful Shutdown**:
- Uvicorn handles SIGTERM for graceful shutdown
- Close database connections in shutdown event handler
- Kubernetes sends SIGTERM, waits terminationGracePeriodSeconds (default 30s)
- Ensure all in-flight requests complete before shutdown

### Decision: Single-Stage Build with Slim Python Base

**Chosen Approach**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Rationale**:
- python:3.11-slim provides good balance (size ~150MB)
- Single stage sufficient (no compiled dependencies)
- Fast build and startup
- Standard uvicorn configuration

**Alternatives Considered**:
- python:3.11-alpine: Rejected (compilation issues with some packages, slower builds)
- Multi-stage with builder: Rejected (unnecessary complexity for pure Python)
- Gunicorn + uvicorn workers: Rejected (overkill for local demo)

## 3. Helm Chart Design Patterns

### Research Findings

**Template Organization**:
- Separate templates per resource type (deployment, service, ingress)
- Use _helpers.tpl for common labels and selectors
- Prefix templates with resource type (deployment-frontend.yaml)
- Keep templates focused and readable

**Values.yaml Structure**:
```yaml
# Global settings
global:
  environment: development

# Per-service configuration
frontend:
  image:
    repository: todo-frontend
    tag: latest
  replicas: 1
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"

backend:
  image:
    repository: todo-backend
    tag: latest
  replicas: 1
  resources:
    requests:
      memory: "512Mi"
      cpu: "300m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

# Secrets (provided at install time)
secrets:
  betterAuthSecret: ""
  cohereApiKey: ""
  databaseUrl: ""

# Ingress configuration
ingress:
  enabled: true
  host: todo.local
  className: nginx
```

**Secret Management**:
- Option 1: Inline secrets in values.yaml (simple, less secure)
- Option 2: External secret management (Sealed Secrets, External Secrets Operator)
- Option 3: Helm --set flags at install time (secure, no secrets in repo)
- Recommendation: Option 3 for local demo, Option 2 for production

**Ingress Configuration**:
- Use IngressClass for controller selection (nginx)
- Host-based routing for clean URLs (todo.local)
- Path-based routing for backend API (/api → backend service)
- Annotations for nginx-specific configuration

### Decision: Focused Helm Chart with Runtime Secret Injection

**Rationale**:
- Clear template organization for maintainability
- Secrets provided via --set flags (never committed to repo)
- Comprehensive values.yaml with sensible defaults
- Production-ready patterns (probes, limits, rolling updates)

**Alternatives Considered**:
- Kustomize: Rejected (Helm provides better templating and versioning)
- Raw manifests: Rejected (no parameterization, hard to maintain)
- Helmfile: Rejected (unnecessary complexity for single chart)

## 4. Minikube Ingress Configuration

### Research Findings

**Nginx Ingress Controller**:
- Minikube addon: `minikube addons enable ingress`
- Installs nginx ingress controller in ingress-nginx namespace
- Supports standard Ingress resources with IngressClass
- Works with host-based and path-based routing

**Host-Based Routing**:
- Requires /etc/hosts entry: `127.0.0.1 todo.local`
- Ingress resource specifies host: todo.local
- Nginx routes requests based on Host header
- Clean URLs without port numbers

**Path Rewriting**:
- Frontend: / → frontend service (no rewrite needed)
- Backend: /api → backend service (preserve /api prefix)
- Use path type: Prefix for flexible matching
- No rewrite needed if backend expects /api prefix

**TLS Termination**:
- Optional for local demo (adds complexity)
- Would require cert-manager or manual certificate creation
- Recommendation: Skip TLS for local Minikube demo

### Decision: Nginx Ingress with Host-Based Routing

**Configuration**:
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

**Rationale**:
- Standard Kubernetes ingress pattern
- Clean URLs with host-based routing
- Path-based routing for API separation
- No TLS complexity for local demo

**Alternatives Considered**:
- NodePort: Rejected (requires port management, not production-like)
- LoadBalancer + minikube tunnel: Rejected (requires tunnel management)
- Traefik ingress: Rejected (nginx is more common, better documented)

## 5. AI Tool Integration Patterns

### Research Findings

**Gordon (Docker AI Agent)**:
- Command: `docker ai build --tag <image>:<tag> <context>`
- Capabilities: Dockerfile generation, optimization suggestions, build troubleshooting
- Limitations: Beta feature, requires Docker Desktop 4.53+, may not be available
- Fallback: Pre-generated Dockerfiles in repository

**kubectl-ai**:
- Natural language commands: "deploy backend with 3 replicas"
- Generates Kubernetes manifests from descriptions
- Can analyze existing resources and suggest improvements
- Useful for scaling, debugging, resource analysis

**kagent**:
- Cluster health analysis: "check cluster health"
- Log analysis: "analyze logs for errors"
- Resource optimization: "suggest resource limits"
- Debugging: "why is pod crashing?"

### Decision: Layered AI Tool Usage

**Gordon**: Containerization phase
- Generate Dockerfiles with AI assistance
- Optimize images for size and performance
- Fallback to pre-generated Dockerfiles if unavailable

**kubectl-ai**: Deployment and operations phase
- Generate Helm templates from natural language
- Scale deployments with AI commands
- Debug pod failures with AI assistance

**kagent**: Monitoring and optimization phase
- Analyze cluster health and resource usage
- Identify performance bottlenecks
- Suggest optimizations

**Rationale**:
- Each tool showcases different AI capabilities
- Clear separation of responsibilities
- Multiple impressive demo moments
- Practical workflow that could be used in production

## 6. Kubernetes Resource Optimization

### Research Findings

**Resource Requests vs Limits**:
- Requests: Guaranteed resources, used for scheduling
- Limits: Maximum resources, enforced by kubelet
- Best practice: Set both to prevent resource starvation
- Local Minikube: Conservative values to fit in single node

**Readiness vs Liveness Probes**:
- Readiness: Is the pod ready to serve traffic?
- Liveness: Is the pod healthy and should be restarted?
- Readiness failures: Remove from service endpoints
- Liveness failures: Restart the pod
- Best practice: Different endpoints or different thresholds

**Rolling Update Strategy**:
- maxSurge: How many extra pods during update (default 25%)
- maxUnavailable: How many pods can be down during update (default 25%)
- For zero-downtime: maxSurge=1, maxUnavailable=0
- Requires readiness probes to work correctly

**Pod Disruption Budgets**:
- Ensures minimum availability during voluntary disruptions
- Not critical for single-replica local demo
- Important for production with multiple replicas

### Decision: Conservative Resources with Proper Probes

**Resource Configuration**:
```yaml
frontend:
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"

backend:
  resources:
    requests:
      memory: "512Mi"
      cpu: "300m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
```

**Probe Configuration**:
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  successThreshold: 1
  failureThreshold: 3

livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 3
  successThreshold: 1
  failureThreshold: 3
```

**Rationale**:
- Conservative resources fit in typical developer machine
- Proper probes ensure zero-downtime deployments
- Liveness probe more lenient than readiness (longer delays, fewer checks)
- Production-ready patterns demonstrated

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Frontend Container | Multi-stage build with standalone output | Minimal image size, fast startup |
| Backend Container | Single-stage with python:3.11-slim | Simple, sufficient for pure Python |
| Helm Chart | Focused chart with runtime secrets | Production patterns, secure secret handling |
| Ingress | Nginx with host-based routing | Standard pattern, clean URLs |
| AI Tools | Layered by function (Gordon/kubectl-ai/kagent) | Showcase breadth, clear responsibilities |
| Resources | Conservative limits for local Minikube | Fits typical machines, demonstrates best practices |
| Probes | Separate readiness and liveness | Zero-downtime deployments, proper health checks |
| Database | External Neon (no local pod) | Simplicity, consistency with Phase III |

## Risk Mitigation Strategies

1. **Gordon Unavailable**: Maintain pre-generated Dockerfiles as fallback
2. **Resource Constraints**: Conservative limits, documented minimum requirements
3. **Ingress Issues**: Detailed setup docs, automated host file configuration
4. **Database Connectivity**: Test from Minikube, document network requirements
5. **AI Tool Failures**: Validate all AI-generated configs, maintain baseline configs

## Next Steps

1. Use these research findings to create detailed architecture design
2. Design Helm chart structure based on best practices identified
3. Document AI tool workflows with specific command examples
4. Create quickstart guide incorporating all decisions
5. Implement infrastructure following researched patterns
