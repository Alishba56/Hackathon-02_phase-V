# Todo AI Chatbot

A cloud-native todo application with an integrated AI chatbot powered by Cohere, featuring authentication, task management, and intelligent assistance.

## Features

### Core Functionality
- ✅ **User Authentication**: Secure sign-up and sign-in with Better Auth
- ✅ **Task Management**: Create, read, update, and delete tasks
- ✅ **AI Chatbot**: Intelligent task assistance powered by Cohere AI
- ✅ **Real-time Updates**: Instant task synchronization
- ✅ **Responsive Design**: Works on desktop and mobile devices

### Technical Features
- 🚀 **Cloud-Native Architecture**: Kubernetes-ready with Helm charts, Dapr runtime
- 🐳 **Containerized**: Docker multi-stage builds for optimal image size
- 🤖 **AI-Powered DevOps**: Integration with Gordon, kubectl-ai, and kagent
- 📊 **Production-Ready**: Health checks, resource limits, and monitoring
- 🔒 **Secure**: Non-root containers, secrets management, environment isolation
- 🔄 **Event-Driven**: Kafka pub/sub via Dapr for scalable event processing
- ⚡ **Oracle OKE**: Deployed on Oracle Cloud Infrastructure (always-free tier)
- 🔧 **CI/CD Pipeline**: Automated deployment via GitHub Actions

## Architecture

### Technology Stack

**Frontend**:
- Next.js 16 (React framework)
- TypeScript
- Tailwind CSS
- Better Auth (authentication)

**Backend**:
- FastAPI (Python web framework)
- PostgreSQL (database)
- Cohere API (AI chatbot)
- Uvicorn (ASGI server)

**Infrastructure**:
- Docker (containerization)
- Kubernetes (orchestration)
- Helm (package management)
- Dapr v1.12+ (distributed application runtime)
- Oracle OKE (production) / Minikube (local development)
- Kafka/Redpanda Cloud (event streaming)
- GitHub Actions (CI/CD)

### Architecture Diagram

**Local/Minikube Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│                         Ingress                              │
│                      (todo.local)                            │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│   Frontend   │  │   Backend    │
│   Service    │  │   Service    │
│  (Port 3000) │  │  (Port 8000) │
└──────┬───────┘  └──────┬───────┘
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│   Frontend   │  │   Backend    │
│     Pod      │  │     Pod      │
│  (Next.js)   │  │  (FastAPI)   │
└──────────────┘  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  PostgreSQL  │
                  │  (External)  │
                  └──────────────┘
```

**Oracle OKE Production Architecture** (with Dapr):
```
┌─────────────────────────────────────────────────────────────┐
│  OKE Load Balancer (Ingress)                                │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────────────────────────────┐
│   Frontend   │  │   Backend Pod (2/2 Ready)            │
│     Pod      │  │  ┌────────────┐  ┌────────────────┐  │
│  (Next.js)   │  │  │  FastAPI   │◄─┤  Dapr Sidecar  │  │
│              │  │  │  (Port     │  │  (Port 3500)   │  │
│              │  │  │   8000)    │  │                │  │
└──────────────┘  │  └────────────┘  └────────┬───────┘  │
                  └─────────────────────────────┼──────────┘
                                               │
                    ┌──────────────────────────┼──────────────┐
                    │                          │              │
         ┌──────────▼─────────┐  ┌────────────▼───┐  ┌──────▼──────┐
         │  Kafka/Redpanda    │  │  PostgreSQL    │  │  K8s        │
         │  Cloud (Pub/Sub)   │  │  (Neon)        │  │  Secrets    │
         └────────────────────┘  └────────────────┘  └─────────────┘
```

## Prerequisites

### System Requirements
- **CPU**: 4 cores minimum (6+ recommended)
- **Memory**: 8GB RAM minimum (12GB+ recommended)
- **Disk**: 20GB free space
- **OS**: Linux, macOS, or Windows 10/11

### Required Software

**For Local Development**:
- Node.js 20+
- Python 3.11+
- PostgreSQL 14+
- npm or yarn

**For Kubernetes Deployment**:
- Docker 20.10+ (Docker Desktop 4.53+ Beta for Gordon AI)
- Minikube 1.30+
- kubectl 1.27+
- Helm 3.12+

**Optional AI DevOps Tools**:
- Gordon (Docker AI) - Built into Docker Desktop 4.53+ Beta
- kubectl-ai - https://github.com/sozercan/kubectl-ai
- kagent - https://github.com/kubeshop/kagent

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here

# AI Integration
COHERE_API_KEY=your-cohere-api-key-here

# Frontend (optional)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Installation

### Option 1: Local Development

#### 1. Clone Repository
```bash
git clone <repository-url>
cd phase04
```

#### 2. Setup Database
```bash
# Create PostgreSQL database
createdb todo_db

# Run migrations (if applicable)
# psql -d todo_db -f migrations/schema.sql
```

#### 3. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### 4. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

#### 5. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Kubernetes Deployment (Minikube)

Deploy the application to a local Kubernetes cluster using Minikube.

#### Quick Start

```bash
# 1. Setup Minikube
./infra/k8s/minikube/setup.sh

# 2. Build Docker images
./infra/scripts/build-images.sh

# 3. Load images into Minikube
./infra/scripts/load-images.sh

# 4. Deploy with Helm
export BETTER_AUTH_SECRET="your-secret-here"
export COHERE_API_KEY="your-api-key-here"
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"

./infra/scripts/deploy.sh

# 5. Access application
# Add to /etc/hosts: 127.0.0.1 todo.local
# Open browser: http://todo.local
```

#### Detailed Kubernetes Setup

For comprehensive Kubernetes deployment instructions, see:
- **Quick Start Guide**: `specs/001-k8s-deployment/quickstart.md`
- **Infrastructure README**: `infra/README.md`
- **Minikube Setup**: `docs/deployment/MINIKUBE_SETUP.md`
- **AI Tools Guide**: `docs/deployment/AI_TOOLS_GUIDE.md`
- **Troubleshooting**: `docs/deployment/TROUBLESHOOTING.md`

### Option 3: Oracle OKE Production Deployment

Deploy the application to Oracle Cloud Infrastructure Kubernetes Engine (OKE) with Dapr runtime and event-driven architecture.

#### Features

- ✅ **Oracle OKE**: Always-free tier (4 OCPU, 24GB RAM)
- ✅ **Dapr Runtime**: Service abstraction with sidecar pattern
- ✅ **Event-Driven**: Kafka/Redpanda Cloud pub/sub
- ✅ **State Management**: PostgreSQL via Dapr state store
- ✅ **Secrets Management**: Kubernetes Secrets via Dapr
- ✅ **CI/CD Pipeline**: Automated deployment via GitHub Actions
- ✅ **Monitoring**: Dapr dashboard, metrics, and distributed tracing

#### Prerequisites

Before deploying to OKE:
- Oracle Cloud Infrastructure (OCI) account
- OKE cluster provisioned (see `infra/oke/README.md`)
- Dapr v1.12+ installed on cluster
- Redpanda Cloud serverless cluster
- GitHub repository with Actions enabled
- Docker images pushed to registry (ghcr.io)

#### Quick Deployment

**One-Command Deployment**:
```bash
# Set environment variables
export NAMESPACE=default
export COHERE_API_KEY="your-cohere-api-key"
export BETTER_AUTH_SECRET="your-auth-secret"
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
export KAFKA_USERNAME="your-kafka-username"
export KAFKA_PASSWORD="your-kafka-password"

# Run deployment script
chmod +x infra/scripts/deploy-oke.sh
./infra/scripts/deploy-oke.sh
```

The script will:
1. Check prerequisites (kubectl, helm, cluster access)
2. Create/update Kubernetes secrets
3. Apply Dapr components (Kafka, State, Secrets, Scheduler)
4. Deploy application with Helm
5. Verify deployment status
6. Display application URL

**Duration**: ~5 minutes

#### Manual Deployment Steps

**Step 1: Provision OKE Cluster**
```bash
# Follow OKE setup guide
cd infra/oke
./cluster-setup.sh

# Install Dapr on cluster
./dapr-init.sh
```

**Step 2: Setup Redpanda Cloud**
1. Create serverless cluster at https://redpanda.com/cloud
2. Create topics: `task-events`, `task-updates`, `reminders`
3. Generate SASL credentials
4. Note bootstrap URL

**Step 3: Create Kubernetes Secrets**
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

**Step 4: Update Dapr Configuration**

Edit `infra/dapr-components/kafka-pubsub.yaml`:
```yaml
metadata:
  - name: brokers
    value: "YOUR_REDPANDA_BOOTSTRAP_URL:9092"  # Update this
```

**Step 5: Deploy with Helm**
```bash
# Apply Dapr components
kubectl apply -f infra/dapr-components/

# Deploy application
helm upgrade --install todo-app ./infra/helm/todo-app \
  --values ./infra/helm/todo-app/values-oke.yaml \
  --wait \
  --timeout 5m
```

**Step 6: Verify Deployment**
```bash
# Run verification script
chmod +x infra/scripts/verify-deployment.sh
./infra/scripts/verify-deployment.sh
```

#### Accessing the Application

```bash
# Get ingress IP
kubectl get ingress todo-app-ingress

# Access application
# Frontend: http://<EXTERNAL-IP>/
# Backend API: http://<EXTERNAL-IP>/api/
# Health Check: http://<EXTERNAL-IP>/api/health
```

#### CI/CD Pipeline

The application includes automated CI/CD via GitHub Actions:

**Pipeline Stages**:
1. **Test**: Run pytest and linting
2. **Build**: Build Docker images with commit SHA tags
3. **Push**: Push images to GitHub Container Registry
4. **Deploy**: Helm upgrade to OKE cluster
5. **Verify**: Health checks and smoke tests

**Setup GitHub Secrets**:
```bash
# Required secrets in GitHub repository settings:
KUBECONFIG              # Base64-encoded kubeconfig
COHERE_API_KEY          # Cohere API key
BETTER_AUTH_SECRET      # Authentication secret
DATABASE_URL            # PostgreSQL connection string
KAFKA_USERNAME          # Redpanda username
KAFKA_PASSWORD          # Redpanda password
```

**Trigger Deployment**:
```bash
# Push to main branch triggers automatic deployment
git add .
git commit -m "Update application"
git push origin main

# Or trigger manually via GitHub Actions UI
```

#### Event-Driven Architecture

Every task operation publishes events to Kafka via Dapr:

**Event Types**:
- `com.todo.task.created` → task-events topic
- `com.todo.task.updated` → task-updates topic
- `com.todo.task.deleted` → task-events topic
- `com.todo.task.completed` → task-events topic

**CloudEvents Format**:
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
    "title": "Buy groceries"
  }
}
```

**Verify Event Publishing**:
```bash
# Check Dapr logs for event publishing
kubectl logs -l app=backend -c daprd | grep publish

# View events in Redpanda Cloud dashboard
# Navigate to Topics → task-events
```

#### Monitoring and Observability

**View Application Logs**:
```bash
# Backend logs
kubectl logs -l app=backend -c backend --tail=100 -f

# Dapr sidecar logs
kubectl logs -l app=backend -c daprd --tail=100 -f
```

**Dapr Dashboard**:
```bash
# Port-forward Dapr dashboard
kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080

# Access at http://localhost:8080
```

**Metrics**:
```bash
# View Dapr metrics
kubectl port-forward <backend-pod> 9090:9090
curl http://localhost:9090/metrics | grep dapr
```

#### Updating the Application

**Via CI/CD (Recommended)**:
```bash
# Push changes to main branch
git add .
git commit -m "Update application"
git push origin main

# GitHub Actions automatically deploys
```

**Manual Update**:
```bash
# Build and push new images
docker build -t ghcr.io/<username>/todo-frontend:v1.1.0 ./frontend
docker build -t ghcr.io/<username>/todo-backend:v1.1.0 ./backend
docker push ghcr.io/<username>/todo-frontend:v1.1.0
docker push ghcr.io/<username>/todo-backend:v1.1.0

# Update Helm release
helm upgrade todo-app ./infra/helm/todo-app \
  --values ./infra/helm/todo-app/values-oke.yaml \
  --set frontend.image.tag=v1.1.0 \
  --set backend.image.tag=v1.1.0 \
  --wait
```

#### Rollback

```bash
# List release history
helm history todo-app

# Rollback to previous version
helm rollback todo-app

# Rollback to specific revision
helm rollback todo-app <revision-number>
```

#### Troubleshooting

**Pods Not Starting**:
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name> -c backend
kubectl logs <pod-name> -c daprd
```

**Events Not Publishing**:
```bash
# Check Dapr Pub/Sub logs
kubectl logs -l app=backend -c daprd | grep pubsub

# Verify Kafka connectivity
kubectl exec -it <backend-pod> -c daprd -- curl http://localhost:3500/v1.0/healthz
```

**Dapr Sidecar Issues**:
```bash
# Check Dapr operator logs
kubectl logs -l app=dapr-operator -n dapr-system

# Restart pod
kubectl delete pod <pod-name>
```

#### OKE Documentation

For comprehensive OKE deployment documentation, see:
- **OKE Deployment Guide**: `docs/oke-deployment.md`
- **Dapr Integration Guide**: `docs/dapr-integration.md`
- **OKE Setup**: `infra/oke/README.md`
- **Demo Script**: `docs/demo-script.md`
- **Architecture Decisions**: `specs/001-oke-dapr-infrastructure/research.md`
- **CI/CD Pipeline**: `specs/001-oke-dapr-infrastructure/cicd-pipeline.md`
- **Monitoring Guide**: `specs/001-oke-dapr-infrastructure/monitoring.md`

#### Kubernetes Architecture

The Kubernetes deployment includes:

**Deployments**:
- Frontend (Next.js) - 1 replica, 256Mi/200m resources
- Backend (FastAPI) - 1 replica, 512Mi/300m resources

**Services**:
- Frontend ClusterIP service (port 3000)
- Backend ClusterIP service (port 8000)

**Ingress**:
- Host-based routing for `todo.local`
- Path-based routing: `/` → frontend, `/api` → backend

**Configuration**:
- Secrets for sensitive data (auth secret, API keys, database URL)
- ConfigMap for environment configuration

**Features**:
- Rolling updates with zero downtime
- Readiness and liveness probes
- Resource requests and limits
- Horizontal scaling support
- Self-healing with automatic pod restart

#### AI-Powered DevOps Workflow

This project showcases AI-powered DevOps tools:

**Phase 1: Containerization with Gordon**
```bash
# Generate optimized Dockerfiles with AI
docker ai "Create production Dockerfile for Next.js 16 with standalone output"
docker ai "Create production Dockerfile for FastAPI with uvicorn"
```

**Phase 2: Deployment with kubectl-ai**
```bash
# Deploy using natural language
kubectl-ai "Create deployment for frontend with 1 replica and readiness probe"
kubectl-ai "Scale backend to 3 replicas"
```

**Phase 3: Monitoring with kagent**
```bash
# Analyze cluster health with AI
kagent "Check cluster health"
kagent "Analyze resource usage and suggest optimizations"
```

See `docs/deployment/AI_TOOLS_GUIDE.md` for complete workflows.

#### Kubernetes Management Commands

```bash
# Check deployment status
kubectl get all -l app.kubernetes.io/instance=todo-app

# View logs
kubectl logs -l app.kubernetes.io/component=backend -f

# Check resource usage
kubectl top pods -l app.kubernetes.io/instance=todo-app

# Scale deployment
kubectl scale deployment todo-app-backend --replicas=3

# Update deployment
helm upgrade todo-app ./infra/helm/todo-app

# Uninstall
helm uninstall todo-app
```

## Usage

### Creating Tasks

1. Sign up or sign in to your account
2. Click "Add Task" or use the input field
3. Enter task description
4. Press Enter or click Submit

### Using AI Chatbot

1. Click the chat icon or open the chatbot panel
2. Ask questions about your tasks:
   - "What tasks do I have today?"
   - "Help me prioritize my tasks"
   - "Suggest a task for learning Python"
3. The AI will provide intelligent responses based on your task list

### Managing Tasks

- **Edit**: Click on a task to edit its description
- **Complete**: Check the checkbox to mark as complete
- **Delete**: Click the delete icon to remove a task
- **Filter**: Use filters to view all, active, or completed tasks

## Development

### Project Structure

```
phase04/
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/             # Next.js app directory
│   │   ├── components/      # React components
│   │   └── lib/             # Utilities and helpers
│   ├── public/              # Static assets
│   ├── package.json
│   └── next.config.js
│
├── backend/                  # FastAPI backend application
│   ├── main.py              # Application entry point
│   ├── requirements.txt     # Python dependencies
│   └── ...
│
├── infra/                    # Infrastructure as Code
│   ├── docker/              # Dockerfiles
│   │   ├── frontend/
│   │   └── backend/
│   ├── helm/                # Helm charts
│   │   └── todo-app/
│   ├── k8s/                 # Kubernetes configs
│   │   └── minikube/
│   └── scripts/             # Automation scripts
│
├── docs/                     # Documentation
│   └── deployment/          # Deployment guides
│
├── specs/                    # Feature specifications
│   └── 001-k8s-deployment/
│
└── README.md                # This file
```

### Running Tests

**Frontend**:
```bash
cd frontend
npm test
npm run test:e2e
```

**Backend**:
```bash
cd backend
pytest
pytest --cov
```

### Code Quality

**Frontend**:
```bash
npm run lint
npm run type-check
npm run format
```

**Backend**:
```bash
black .
flake8
mypy .
```

### Building for Production

**Docker Images**:
```bash
# Build both images
./infra/scripts/build-images.sh

# Or build individually
docker build -t todo-frontend:latest -f infra/docker/frontend/Dockerfile frontend/
docker build -t todo-backend:latest -f infra/docker/backend/Dockerfile backend/
```

**Helm Chart**:
```bash
# Lint chart
helm lint ./infra/helm/todo-app

# Package chart
helm package ./infra/helm/todo-app

# Test rendering
helm template todo-app ./infra/helm/todo-app
```

## Deployment Environments

### Local Development
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Database: localhost:5432

### Kubernetes (Minikube)
- Application: http://todo.local
- Frontend: http://todo.local/
- Backend API: http://todo.local/api

### Oracle OKE (Production)
- Application: http://<INGRESS-IP>
- Frontend: http://<INGRESS-IP>/
- Backend API: http://<INGRESS-IP>/api
- Health Check: http://<INGRESS-IP>/api/health
- Dapr Dashboard: kubectl port-forward (port 8080)

### Production Considerations

For production deployment, consider:

**Scalability**:
- Increase replica counts (3+ for high availability)
- Configure Horizontal Pod Autoscaler (HPA)
- Use cluster autoscaling

**Security**:
- Enable network policies
- Configure RBAC with least privilege
- Use secrets management (Vault, Sealed Secrets, or Dapr Secrets)
- Enable audit logging
- Use private container registry
- Enable mTLS via Dapr

**Monitoring**:
- Deploy Prometheus and Grafana
- Configure alerting rules
- Implement distributed tracing (W3C Trace Context via Dapr)
- Set up log aggregation (ELK, Loki)
- Use Dapr dashboard for component monitoring

**Backup**:
- Implement database backups
- Use persistent volume snapshots
- Document recovery procedures

See `infra/README.md` and `docs/oke-deployment.md` for detailed production considerations.

## Troubleshooting

### Common Issues

**Issue: Cannot connect to database**
```bash
# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql://username:password@host:port/database

# Test connection
psql $DATABASE_URL
```

**Issue: Cohere API errors**
```bash
# Verify API key
echo $COHERE_API_KEY

# Test API key
curl -X POST https://api.cohere.ai/v1/generate \
  -H "Authorization: Bearer $COHERE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test","max_tokens":10}'
```

**Issue: Kubernetes pods not starting**
```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/instance=todo-app

# View pod logs
kubectl logs <pod-name>

# Describe pod for events
kubectl describe pod <pod-name>
```

For comprehensive troubleshooting, see:
- `docs/deployment/TROUBLESHOOTING.md` - Complete debugging guide
- `docs/deployment/AI_TOOLS_GUIDE.md` - AI-powered troubleshooting

## Documentation

### Deployment Documentation

**Minikube (Local)**:
- **Quick Start**: `specs/001-k8s-deployment/quickstart.md`
- **Infrastructure Guide**: `infra/README.md`
- **Minikube Setup**: `docs/deployment/MINIKUBE_SETUP.md`
- **AI Tools Guide**: `docs/deployment/AI_TOOLS_GUIDE.md`
- **Troubleshooting**: `docs/deployment/TROUBLESHOOTING.md`

**Oracle OKE (Production)**:
- **OKE Deployment Guide**: `docs/oke-deployment.md`
- **Dapr Integration Guide**: `docs/dapr-integration.md`
- **OKE Setup**: `infra/oke/README.md`
- **Demo Script**: `docs/demo-script.md`

### Specification Documents

**Phase IV - Kubernetes Deployment**:
- **Feature Spec**: `specs/001-k8s-deployment/spec.md`
- **Implementation Plan**: `specs/001-k8s-deployment/plan.md`
- **Task List**: `specs/001-k8s-deployment/tasks.md`

**Phase V - Oracle OKE + Dapr**:
- **Research & Decisions**: `specs/001-oke-dapr-infrastructure/research.md`
- **Architecture**: `specs/001-oke-dapr-infrastructure/architecture.md`
- **Dapr Components**: `specs/001-oke-dapr-infrastructure/dapr-components.md`
- **CI/CD Pipeline**: `specs/001-oke-dapr-infrastructure/cicd-pipeline.md`
- **Monitoring**: `specs/001-oke-dapr-infrastructure/monitoring.md`
- **Quick Start**: `specs/001-oke-dapr-infrastructure/quickstart.md`
- **Task List**: `specs/001-oke-dapr-infrastructure/tasks.md`

## Contributing

### Development Workflow

1. Create a feature branch
2. Make changes
3. Run tests and linting
4. Commit with descriptive messages
5. Push and create pull request

### Commit Message Format

```
<type>: <description>

[optional body]

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## License

[Specify your license here]

## Support

For issues and questions:
- Review documentation in `docs/` directory
- Check troubleshooting guide
- Review AI tools guide for AI-powered debugging

## Acknowledgments

- **Next.js** - React framework
- **FastAPI** - Python web framework
- **Cohere** - AI language model
- **Better Auth** - Authentication library
- **Kubernetes** - Container orchestration
- **Helm** - Kubernetes package manager
- **Minikube** - Local Kubernetes cluster

## Project Status

### Phase III: Core Application ✅
- User authentication
- Task management
- AI chatbot integration
- Responsive UI

### Phase IV: Kubernetes Deployment ✅
- Docker containerization
- Helm chart deployment
- Minikube local cluster
- AI-powered DevOps tools
- Production-ready infrastructure
- Comprehensive documentation

### Phase V: Oracle OKE + Dapr Infrastructure ✅
- Oracle OKE cluster deployment (always-free tier)
- Dapr runtime integration (v1.12+)
- Event-driven architecture with Kafka/Redpanda Cloud
- Dapr building blocks (Pub/Sub, State, Secrets, Scheduler)
- CloudEvents 1.0 event format
- Automated CI/CD pipeline via GitHub Actions
- Comprehensive monitoring and observability
- Production-ready deployment scripts
- Complete documentation and demo script

## Quick Reference

### Start Local Development
```bash
# Backend
cd backend && uvicorn main:app --reload

# Frontend
cd frontend && npm run dev
```

### Start Kubernetes Deployment (Minikube)
```bash
# Setup and deploy
./infra/k8s/minikube/setup.sh
./infra/scripts/build-images.sh
./infra/scripts/load-images.sh
./infra/scripts/deploy.sh

# Access at http://todo.local
```

### Deploy to Oracle OKE (Production)
```bash
# One-command deployment
export NAMESPACE=default
export COHERE_API_KEY="your-key"
export BETTER_AUTH_SECRET="your-secret"
export DATABASE_URL="postgresql://..."
export KAFKA_USERNAME="your-username"
export KAFKA_PASSWORD="your-password"

./infra/scripts/deploy-oke.sh

# Verify deployment
./infra/scripts/verify-deployment.sh

# Get application URL
kubectl get ingress todo-app-ingress
```

### Useful Commands

**Minikube**:
```bash
# Kubernetes status
kubectl get all -l app.kubernetes.io/instance=todo-app

# View logs
kubectl logs -l app.kubernetes.io/component=backend -f

# Resource usage
kubectl top pods -l app.kubernetes.io/instance=todo-app

# Restart deployment
kubectl rollout restart deployment todo-app-backend
```

**Oracle OKE**:
```bash
# Check deployment status (with Dapr sidecars)
kubectl get pods  # Should show 2/2 Ready

# View application logs
kubectl logs -l app=backend -c backend -f

# View Dapr sidecar logs
kubectl logs -l app=backend -c daprd -f

# Check Dapr components
kubectl get components

# View events in real-time
kubectl logs -l app=backend -c daprd | grep publish

# Access Dapr dashboard
kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080

# Check Dapr metrics
kubectl port-forward <backend-pod> 9090:9090
curl http://localhost:9090/metrics | grep dapr

# Rollback deployment
helm rollback todo-app

# Update deployment
helm upgrade todo-app ./infra/helm/todo-app \
  --values ./infra/helm/todo-app/values-oke.yaml
```

---

**Built with ❤️ using AI-powered DevOps tools**
