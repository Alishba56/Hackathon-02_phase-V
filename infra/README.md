# Kubernetes Infrastructure

**Feature**: Cloud-Native Todo AI Chatbot Kubernetes Deployment
**Purpose**: Complete infrastructure setup for local Kubernetes deployment with Minikube

## Overview

This directory contains all infrastructure code for deploying the Todo AI Chatbot to Kubernetes:

- **Docker**: Multi-stage Dockerfiles for frontend and backend
- **Helm**: Complete Helm chart for Kubernetes deployment
- **Kubernetes**: Minikube setup and configuration scripts
- **Scripts**: Automation scripts for build, load, and deploy workflows

## Directory Structure

```
infra/
├── docker/                    # Docker containerization
│   ├── frontend/             # Next.js frontend container
│   │   ├── Dockerfile        # Multi-stage build (deps → builder → runner)
│   │   └── .dockerignore     # Exclude unnecessary files
│   └── backend/              # FastAPI backend container
│       ├── Dockerfile        # Python 3.11 slim with uvicorn
│       └── .dockerignore     # Exclude unnecessary files
│
├── helm/                      # Helm chart for Kubernetes
│   └── todo-app/             # Main application chart
│       ├── Chart.yaml        # Chart metadata
│       ├── values.yaml       # Default configuration
│       ├── values-dev.yaml   # Development overrides
│       ├── .helmignore       # Exclude unnecessary files
│       └── templates/        # Kubernetes resource templates
│           ├── _helpers.tpl          # Template helpers
│           ├── deployment-frontend.yaml
│           ├── deployment-backend.yaml
│           ├── service-frontend.yaml
│           ├── service-backend.yaml
│           ├── ingress.yaml
│           ├── secrets.yaml
│           ├── configmap.yaml
│           └── NOTES.txt     # Post-install instructions
│
├── k8s/                       # Kubernetes cluster setup
│   └── minikube/             # Minikube configuration
│       ├── setup.sh          # Linux/macOS setup script
│       ├── setup.ps1         # Windows PowerShell setup script
│       └── teardown.sh       # Cleanup script
│
└── scripts/                   # Automation scripts
    ├── build-images.sh       # Build Docker images
    ├── load-images.sh        # Load images into Minikube
    ├── deploy.sh             # Deploy with Helm
    └── demo.sh               # AI-powered demo workflow
```

## Quick Start

### Prerequisites

- **Docker**: 20.10+ (Docker Desktop 4.53+ Beta for Gordon AI)
- **Minikube**: 1.30+
- **kubectl**: 1.27+
- **Helm**: 3.12+
- **System Resources**: 4 CPU cores, 8GB RAM minimum

### Installation Steps

1. **Setup Minikube**:
   ```bash
   # Linux/macOS
   ./infra/k8s/minikube/setup.sh

   # Windows PowerShell
   .\infra\k8s\minikube\setup.ps1
   ```

2. **Build Docker Images**:
   ```bash
   ./infra/scripts/build-images.sh
   ```

3. **Load Images into Minikube**:
   ```bash
   ./infra/scripts/load-images.sh
   ```

4. **Deploy Application**:
   ```bash
   # Set required secrets
   export BETTER_AUTH_SECRET="your-secret-here"
   export COHERE_API_KEY="your-api-key-here"
   export DATABASE_URL="postgresql://user:pass@host:5432/dbname"

   # Deploy with Helm
   ./infra/scripts/deploy.sh
   ```

5. **Access Application**:
   - Add to hosts file: `127.0.0.1 todo.local`
   - Open browser: http://todo.local

## Docker Containerization

### Frontend Container (Next.js)

**Image**: `todo-frontend:latest`
**Base**: `node:20-alpine`
**Size**: ~150MB (optimized with standalone output)

**Build Strategy**:
- **Stage 1 (deps)**: Install production dependencies only
- **Stage 2 (builder)**: Install all dependencies and build application
- **Stage 3 (runner)**: Copy standalone output, run as non-root user

**Key Features**:
- Multi-stage build for minimal image size
- Standalone output mode (no node_modules in final image)
- Non-root user execution (nextjs:1001)
- Optimized layer caching
- Telemetry disabled

**Build Command**:
```bash
docker build -t todo-frontend:latest -f infra/docker/frontend/Dockerfile frontend/
```

**Local Test**:
```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL="http://localhost:8000" \
  todo-frontend:latest
```

### Backend Container (FastAPI)

**Image**: `todo-backend:latest`
**Base**: `python:3.11-slim`
**Size**: ~300MB

**Build Strategy**:
- Single-stage build with optimized dependency installation
- Health check endpoint configured
- Non-root user execution (appuser:1001)
- Uvicorn production configuration

**Key Features**:
- Efficient pip installation with --no-cache-dir
- Health check on /api/health endpoint
- Environment variable configuration
- Production-ready uvicorn settings

**Build Command**:
```bash
docker build -t todo-backend:latest -f infra/docker/backend/Dockerfile backend/
```

**Local Test**:
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e BETTER_AUTH_SECRET="test" \
  -e COHERE_API_KEY="test" \
  todo-backend:latest
```

## Helm Chart

### Chart Information

**Name**: `todo-app`
**Version**: `0.1.0`
**App Version**: `1.0.0`
**Type**: `application`

### Configuration

The Helm chart is highly configurable through `values.yaml`:

**Frontend Configuration**:
```yaml
frontend:
  replicaCount: 1
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
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

**Backend Configuration**:
```yaml
backend:
  replicaCount: 1
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: IfNotPresent
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
    initialDelaySeconds: 15
    periodSeconds: 10
```

**Ingress Configuration**:
```yaml
ingress:
  enabled: true
  className: nginx
  host: todo.local
  paths:
    frontend: /
    backend: /api
```

### Helm Commands

**Install**:
```bash
helm install todo-app ./infra/helm/todo-app \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.cohereApiKey="$COHERE_API_KEY" \
  --set secrets.databaseUrl="$DATABASE_URL"
```

**Upgrade**:
```bash
helm upgrade todo-app ./infra/helm/todo-app \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.cohereApiKey="$COHERE_API_KEY" \
  --set secrets.databaseUrl="$DATABASE_URL"
```

**Uninstall**:
```bash
helm uninstall todo-app
```

**Lint**:
```bash
helm lint ./infra/helm/todo-app
```

**Template (dry-run)**:
```bash
helm template todo-app ./infra/helm/todo-app \
  --set secrets.betterAuthSecret="test" \
  --set secrets.cohereApiKey="test" \
  --set secrets.databaseUrl="test"
```

**List Releases**:
```bash
helm list
```

**Get Values**:
```bash
helm get values todo-app
```

## Kubernetes Resources

### Deployments

**Frontend Deployment**:
- Name: `todo-app-frontend`
- Replicas: 1 (configurable)
- Strategy: RollingUpdate (maxSurge=1, maxUnavailable=0)
- Container Port: 3000
- Readiness Probe: HTTP GET / on port 3000
- Liveness Probe: HTTP GET / on port 3000

**Backend Deployment**:
- Name: `todo-app-backend`
- Replicas: 1 (configurable)
- Strategy: RollingUpdate (maxSurge=1, maxUnavailable=0)
- Container Port: 8000
- Readiness Probe: HTTP GET /api/health on port 8000
- Liveness Probe: HTTP GET /api/health on port 8000

### Services

**Frontend Service**:
- Name: `todo-app-frontend`
- Type: ClusterIP
- Port: 3000 → TargetPort: 3000
- Selector: `app.kubernetes.io/component=frontend`

**Backend Service**:
- Name: `todo-app-backend`
- Type: ClusterIP
- Port: 8000 → TargetPort: 8000
- Selector: `app.kubernetes.io/component=backend`

### Ingress

**Ingress Resource**:
- Name: `todo-app-ingress`
- Class: `nginx`
- Host: `todo.local`
- Rules:
  - Path `/` → Frontend Service (port 3000)
  - Path `/api` → Backend Service (port 8000)

### Secrets

**Secret Resource**:
- Name: `todo-app-secrets`
- Type: `Opaque`
- Data:
  - `better-auth-secret`: Base64 encoded authentication secret
  - `cohere-api-key`: Base64 encoded Cohere API key
  - `database-url`: Base64 encoded PostgreSQL connection string

### ConfigMap

**ConfigMap Resource**:
- Name: `todo-app-config`
- Data:
  - `NEXT_PUBLIC_API_URL`: Backend API URL for frontend
  - `NODE_ENV`: Environment (production)
  - `PYTHONUNBUFFERED`: Python output buffering (1)

## Automation Scripts

### build-images.sh

Builds both frontend and backend Docker images.

**Usage**:
```bash
./infra/scripts/build-images.sh
```

**What it does**:
1. Checks if Docker is installed
2. Builds frontend image with tag `todo-frontend:latest`
3. Builds backend image with tag `todo-backend:latest`
4. Reports image sizes

### load-images.sh

Loads Docker images into Minikube's image cache.

**Usage**:
```bash
./infra/scripts/load-images.sh
```

**What it does**:
1. Checks if Minikube is running
2. Verifies images exist locally
3. Loads frontend image into Minikube
4. Loads backend image into Minikube
5. Verifies images in Minikube cache

### deploy.sh

Deploys application using Helm with secret injection.

**Usage**:
```bash
# Set environment variables first
export BETTER_AUTH_SECRET="your-secret"
export COHERE_API_KEY="your-key"
export DATABASE_URL="postgresql://..."

# Run deployment
./infra/scripts/deploy.sh
```

**What it does**:
1. Checks prerequisites (Helm, kubectl, Minikube)
2. Prompts for secrets if not set
3. Lints Helm chart
4. Installs or upgrades Helm release
5. Waits for pods to be ready
6. Displays deployment status and access information

### demo.sh

Comprehensive AI-powered DevOps demo script.

**Usage**:
```bash
./infra/scripts/demo.sh
```

**What it does**:
1. **Phase 0**: Prerequisites check
2. **Phase 1**: Containerization with Gordon (or fallback)
3. **Phase 2**: Deployment with kubectl-ai (or Helm)
4. **Phase 3**: Operations (scaling, failure simulation)
5. **Phase 4**: Monitoring with kagent
6. **Phase 5**: Optimization and final health checks

See `docs/deployment/AI_TOOLS_GUIDE.md` for detailed AI tool workflows.

## Minikube Configuration

### Setup

**Linux/macOS**:
```bash
./infra/k8s/minikube/setup.sh
```

**Windows PowerShell**:
```powershell
.\infra\k8s\minikube\setup.ps1
```

**Configuration**:
- CPUs: 4
- Memory: 8192MB (8GB)
- Driver: docker (default)
- Kubernetes Version: stable
- Addons: ingress, metrics-server

### Teardown

```bash
./infra/k8s/minikube/teardown.sh
```

**What it does**:
1. Confirms deletion
2. Stops Minikube
3. Deletes Minikube cluster
4. Removes all data

## Resource Requirements

### Minimum System Requirements

- **CPU**: 4 cores
- **Memory**: 8GB RAM
- **Disk**: 20GB free space
- **OS**: Linux, macOS, or Windows 10/11

### Kubernetes Resource Allocation

**Frontend Pod**:
- Requests: 256Mi memory, 200m CPU
- Limits: 512Mi memory, 500m CPU

**Backend Pod**:
- Requests: 512Mi memory, 300m CPU
- Limits: 1Gi memory, 1000m CPU

**Total Cluster Usage** (1 replica each):
- Memory: ~768Mi requested, ~1.5Gi limit
- CPU: ~500m requested, ~1500m limit

## Monitoring and Debugging

### Check Deployment Status

```bash
# All resources
kubectl get all -l app.kubernetes.io/instance=todo-app

# Pods only
kubectl get pods -l app.kubernetes.io/instance=todo-app

# Services
kubectl get svc -l app.kubernetes.io/instance=todo-app

# Ingress
kubectl get ingress -l app.kubernetes.io/instance=todo-app
```

### View Logs

```bash
# Frontend logs
kubectl logs -l app.kubernetes.io/component=frontend -f

# Backend logs
kubectl logs -l app.kubernetes.io/component=backend -f

# All logs
kubectl logs -l app.kubernetes.io/instance=todo-app --all-containers=true -f
```

### Check Resource Usage

```bash
# Pod resource usage
kubectl top pods -l app.kubernetes.io/instance=todo-app

# Node resource usage
kubectl top nodes
```

### Troubleshooting

For comprehensive troubleshooting procedures, see:
- `docs/deployment/TROUBLESHOOTING.md` - Complete debugging guide
- `docs/deployment/AI_TOOLS_GUIDE.md` - AI-powered troubleshooting with kubectl-ai and kagent

## AI-Powered DevOps Tools

This infrastructure showcases three AI-powered DevOps tools:

### Gordon (Docker AI Agent)

**Purpose**: AI-assisted Dockerfile generation and optimization

**Installation**: Docker Desktop 4.53+ Beta

**Example Usage**:
```bash
docker ai "Create production Dockerfile for Next.js 16 with standalone output"
```

**Fallback**: Pre-generated Dockerfiles in `infra/docker/`

### kubectl-ai

**Purpose**: Natural language Kubernetes operations

**Installation**: https://github.com/sozercan/kubectl-ai

**Example Usage**:
```bash
kubectl-ai "Scale backend to 3 replicas"
kubectl-ai "Why is the backend pod failing?"
```

**Fallback**: Standard kubectl commands

### kagent

**Purpose**: Cluster health analysis and optimization

**Installation**: https://github.com/kubeshop/kagent

**Example Usage**:
```bash
kagent "Check cluster health"
kagent "Analyze resource usage and suggest optimizations"
```

**Fallback**: kubectl top and manual analysis

See `docs/deployment/AI_TOOLS_GUIDE.md` for complete workflows.

## Best Practices

### Docker

- ✅ Use multi-stage builds to minimize image size
- ✅ Run containers as non-root users
- ✅ Use specific base image versions (not `latest`)
- ✅ Leverage layer caching for faster builds
- ✅ Use .dockerignore to exclude unnecessary files
- ✅ Include health checks in Dockerfiles

### Kubernetes

- ✅ Define resource requests and limits
- ✅ Configure readiness and liveness probes
- ✅ Use rolling update strategy for zero downtime
- ✅ Store sensitive data in Secrets
- ✅ Use ConfigMaps for configuration
- ✅ Label resources consistently
- ✅ Use namespaces for isolation (production)

### Helm

- ✅ Parameterize all environment-specific values
- ✅ Use values.yaml for defaults
- ✅ Create environment-specific value files
- ✅ Lint charts before deployment
- ✅ Test with `helm template` before applying
- ✅ Version charts semantically
- ✅ Document all values in comments

### Security

- ✅ Never commit secrets to version control
- ✅ Use Kubernetes Secrets for sensitive data
- ✅ Run containers as non-root users
- ✅ Scan images for vulnerabilities
- ✅ Use network policies (production)
- ✅ Enable RBAC (production)
- ✅ Keep base images updated

## Production Considerations

This infrastructure is designed for **local development with Minikube**. For production deployment, consider:

### High Availability

- Increase replica counts (3+ for critical services)
- Use pod anti-affinity rules
- Deploy across multiple availability zones
- Configure pod disruption budgets

### Scalability

- Implement Horizontal Pod Autoscaler (HPA)
- Configure cluster autoscaling
- Use persistent volumes for stateful data
- Implement caching strategies

### Security

- Enable network policies
- Configure RBAC with least privilege
- Use pod security policies/standards
- Implement secrets management (Vault, Sealed Secrets)
- Enable audit logging
- Use private container registry

### Monitoring

- Deploy Prometheus and Grafana
- Configure alerting rules
- Implement distributed tracing
- Set up log aggregation (ELK, Loki)
- Monitor SLIs and SLOs

### Backup and Disaster Recovery

- Implement database backups
- Use persistent volume snapshots
- Document recovery procedures
- Test disaster recovery regularly

## Additional Resources

- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Minikube Documentation**: https://minikube.sigs.k8s.io/docs/
- **Helm Documentation**: https://helm.sh/docs/
- **Docker Documentation**: https://docs.docker.com/

## Support

For issues and questions:
- Review troubleshooting guide: `docs/deployment/TROUBLESHOOTING.md`
- Check AI tools guide: `docs/deployment/AI_TOOLS_GUIDE.md`
- Review quickstart: `specs/001-k8s-deployment/quickstart.md`
