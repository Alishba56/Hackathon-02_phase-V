# Quickstart: Deploy Todo AI Chatbot to Kubernetes

**Feature**: 001-k8s-deployment
**Date**: 2026-02-08
**Purpose**: Fast-track deployment guide for local Kubernetes

## Overview

This guide provides a streamlined path to deploy the Todo AI Chatbot to local Kubernetes (Minikube) in under 15 minutes. Follow these steps sequentially for a successful deployment.

## Prerequisites

### Required Tools

| Tool | Minimum Version | Installation |
|------|----------------|--------------|
| **Minikube** | 1.32+ | https://minikube.sigs.k8s.io/docs/start/ |
| **Docker** | 24.0+ | https://docs.docker.com/get-docker/ |
| **kubectl** | 1.28+ | https://kubernetes.io/docs/tasks/tools/ |
| **Helm** | 3.12+ | https://helm.sh/docs/intro/install/ |

### Optional AI Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| **Gordon** | AI-assisted Dockerfile generation | Docker Desktop 4.53+ Beta |
| **kubectl-ai** | Natural language Kubernetes operations | https://github.com/sozercan/kubectl-ai |
| **kagent** | Cluster health analysis | https://github.com/kubeshop/kagent |

### System Requirements

- **CPU**: 4 cores minimum (8 cores recommended)
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Disk**: 20GB free space
- **OS**: Windows 10/11, macOS 10.15+, or Linux

### Required Credentials

- **Neon Database URL**: PostgreSQL connection string from Phase III
- **Better Auth Secret**: JWT signing secret from Phase III
- **Cohere API Key**: API key for AI chatbot functionality

## Step 1: Verify Prerequisites

```bash
# Check tool versions
minikube version
# Expected: minikube version: v1.32.0 or higher

docker --version
# Expected: Docker version 24.0.0 or higher

kubectl version --client
# Expected: Client Version: v1.28.0 or higher

helm version
# Expected: version.BuildInfo{Version:"v3.12.0" or higher}

# Check system resources
docker info | grep -E "CPUs|Total Memory"
# Expected: CPUs: 4+, Total Memory: 8GB+
```

## Step 2: Start Minikube Cluster

```bash
# Start Minikube with recommended resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Expected output:
# 😄  minikube v1.32.0 on Darwin 13.0
# ✨  Using the docker driver based on user configuration
# 👍  Starting control plane node minikube in cluster minikube
# 🚜  Pulling base image ...
# 🔥  Creating docker container (CPUs=4, Memory=8192MB) ...
# 🐳  Preparing Kubernetes v1.28.0 on Docker 24.0.0 ...
# 🔎  Verifying Kubernetes components...
# 🌟  Enabled addons: storage-provisioner, default-storageclass
# 🏄  Done! kubectl is now configured to use "minikube" cluster

# Verify cluster is running
kubectl cluster-info
# Expected: Kubernetes control plane is running at https://...

kubectl get nodes
# Expected: minikube   Ready    control-plane   1m   v1.28.0
```

## Step 3: Enable Required Addons

```bash
# Enable ingress controller
minikube addons enable ingress

# Expected output:
# 💡  ingress is an addon maintained by Kubernetes
# 🔎  Verifying ingress addon...
# 🌟  The 'ingress' addon is enabled

# Enable metrics server (for kubectl top)
minikube addons enable metrics-server

# Expected output:
# 💡  metrics-server is an addon maintained by Kubernetes
# 🔎  Verifying metrics-server addon...
# 🌟  The 'metrics-server' addon is enabled

# Verify addons are running
kubectl get pods -n ingress-nginx
# Expected: All pods in Running state

kubectl get pods -n kube-system | grep metrics-server
# Expected: metrics-server pod in Running state
```

## Step 4: Configure Host Mapping

### On Linux/macOS:

```bash
# Add entry to /etc/hosts
echo "127.0.0.1 todo.local" | sudo tee -a /etc/hosts

# Verify entry
cat /etc/hosts | grep todo.local
# Expected: 127.0.0.1 todo.local
```

### On Windows (PowerShell as Administrator):

```powershell
# Add entry to hosts file
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "127.0.0.1 todo.local"

# Verify entry
Get-Content C:\Windows\System32\drivers\etc\hosts | Select-String "todo.local"
# Expected: 127.0.0.1 todo.local
```

## Step 5: Build Container Images

### Option A: Using Gordon (AI-Assisted)

```bash
# Build frontend with Gordon
cd frontend
docker ai "Create production Dockerfile for Next.js 16 with standalone output"
docker build -t todo-frontend:latest .

# Build backend with Gordon
cd ../backend
docker ai "Create production Dockerfile for FastAPI with uvicorn"
docker build -t todo-backend:latest .
```

### Option B: Using Pre-Generated Dockerfiles

```bash
# Build frontend
cd frontend
docker build -f ../infra/docker/frontend/Dockerfile -t todo-frontend:latest .

# Build backend
cd ../backend
docker build -f ../infra/docker/backend/Dockerfile -t todo-backend:latest .
```

### Verify Images

```bash
# Check images were created
docker images | grep todo

# Expected output:
# todo-frontend   latest   abc123   2 minutes ago   150MB
# todo-backend    latest   def456   1 minute ago    300MB
```

## Step 6: Load Images into Minikube

```bash
# Load frontend image
minikube image load todo-frontend:latest

# Expected output:
# Loading image todo-frontend:latest into minikube...

# Load backend image
minikube image load todo-backend:latest

# Expected output:
# Loading image todo-backend:latest into minikube...

# Verify images are available in Minikube
minikube image ls | grep todo

# Expected:
# docker.io/library/todo-frontend:latest
# docker.io/library/todo-backend:latest
```

## Step 7: Prepare Secrets

```bash
# Set environment variables with your credentials
export BETTER_AUTH_SECRET="your-jwt-secret-from-phase-iii"
export COHERE_API_KEY="your-cohere-api-key"
export DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"

# Verify variables are set
echo $BETTER_AUTH_SECRET
echo $COHERE_API_KEY
echo $DATABASE_URL
```

## Step 8: Deploy with Helm

```bash
# Navigate to project root
cd /path/to/phase04

# Install Helm chart
helm install todo-app ./infra/helm/todo-app \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.cohereApiKey="$COHERE_API_KEY" \
  --set secrets.databaseUrl="$DATABASE_URL"

# Expected output:
# NAME: todo-app
# LAST DEPLOYED: [timestamp]
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
# NOTES:
# Thank you for installing todo-app!
# ...
```

## Step 9: Verify Deployment

```bash
# Check all resources
kubectl get all

# Expected output:
# NAME                            READY   STATUS    RESTARTS   AGE
# pod/todo-app-frontend-xxx       1/1     Running   0          1m
# pod/todo-app-backend-xxx        1/1     Running   0          1m
#
# NAME                         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
# service/todo-app-frontend    ClusterIP   10.96.1.1       <none>        3000/TCP   1m
# service/todo-app-backend     ClusterIP   10.96.1.2       <none>        8000/TCP   1m
#
# NAME                                READY   UP-TO-DATE   AVAILABLE   AGE
# deployment.apps/todo-app-frontend   1/1     1            1           1m
# deployment.apps/todo-app-backend    1/1     1            1           1m

# Check ingress
kubectl get ingress

# Expected output:
# NAME        CLASS   HOSTS        ADDRESS        PORTS   AGE
# todo-app    nginx   todo.local   192.168.49.2   80      1m

# Wait for pods to be ready (if not already)
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=todo-app --timeout=120s

# Expected output:
# pod/todo-app-frontend-xxx condition met
# pod/todo-app-backend-xxx condition met
```

## Step 10: Access Application

```bash
# Test ingress connectivity
curl http://todo.local

# Expected: HTML response from Next.js frontend

# Test backend API
curl http://todo.local/api/health

# Expected: {"status":"healthy","timestamp":"..."}

# Open in browser
open http://todo.local
# Or on Linux: xdg-open http://todo.local
# Or on Windows: start http://todo.local
```

## Step 11: Verify Functionality

### Test Authentication

1. Navigate to http://todo.local
2. Click "Sign Up" or "Sign In"
3. Create account or log in with existing credentials
4. Verify successful authentication

### Test Task Management

1. Create a new task
2. View task list
3. Update task status
4. Delete a task
5. Verify all operations work correctly

### Test AI Chatbot

1. Navigate to chat interface
2. Send message: "Add task buy milk"
3. Verify task is created
4. Send message: "Show my tasks"
5. Verify tasks are listed
6. Send message: "What's my email?"
7. Verify profile information is returned

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Common issues:
# - ImagePullBackOff: Image not loaded into Minikube
#   Solution: minikube image load <image>:latest
# - CrashLoopBackOff: Application error
#   Solution: Check logs for error details
# - Pending: Insufficient resources
#   Solution: Increase Minikube resources or reduce pod requests
```

### Ingress Not Working

```bash
# Check ingress controller is running
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl describe ingress todo-app

# Verify host mapping
cat /etc/hosts | grep todo.local

# Test with minikube tunnel (alternative)
minikube tunnel
# Then access via http://todo.local
```

### Database Connection Errors

```bash
# Check backend logs
kubectl logs -l app.kubernetes.io/component=backend

# Verify secret is set correctly
kubectl get secret todo-app-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Test database connectivity from pod
kubectl exec -it <backend-pod> -- python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

### Application Not Responding

```bash
# Check all pods are ready
kubectl get pods

# Check service endpoints
kubectl get endpoints

# Check ingress backend
kubectl describe ingress todo-app

# Restart pods if needed
kubectl rollout restart deployment todo-app-frontend
kubectl rollout restart deployment todo-app-backend
```

## AI Tool Demonstrations

### Using kubectl-ai

```bash
# Scale backend
kubectl-ai "Scale backend deployment to 3 replicas"

# Check resource usage
kubectl-ai "Show resource usage for all pods"

# Debug issues
kubectl-ai "Why is the backend pod restarting?"
```

### Using kagent

```bash
# Cluster health check
kagent "Check cluster health"

# Resource optimization
kagent "Analyze resource usage and suggest optimizations"

# Log analysis
kagent "Analyze backend logs for errors"
```

## Cleanup

### Uninstall Application

```bash
# Uninstall Helm release
helm uninstall todo-app

# Verify resources are deleted
kubectl get all
# Expected: No todo-app resources
```

### Stop Minikube

```bash
# Stop cluster (preserves state)
minikube stop

# Delete cluster (removes all data)
minikube delete
```

### Remove Host Mapping

```bash
# Linux/macOS
sudo sed -i '/todo.local/d' /etc/hosts

# Windows (PowerShell as Administrator)
$hosts = Get-Content C:\Windows\System32\drivers\etc\hosts
$hosts | Where-Object { $_ -notmatch 'todo.local' } | Set-Content C:\Windows\System32\drivers\etc\hosts
```

## Next Steps

### Explore Advanced Features

- Scale deployments with kubectl-ai
- Monitor with kagent
- Test pod failure recovery
- Experiment with resource limits
- Try rolling updates

### Production Considerations

- Use external secret management (Sealed Secrets, External Secrets Operator)
- Implement network policies
- Add monitoring (Prometheus, Grafana)
- Configure autoscaling (HPA)
- Set up CI/CD pipeline
- Use production-grade ingress with TLS

## Quick Reference

### Essential Commands

```bash
# Check cluster status
kubectl cluster-info
kubectl get nodes

# View all resources
kubectl get all

# Check pod logs
kubectl logs <pod-name>
kubectl logs -f <pod-name>  # Follow logs

# Describe resource
kubectl describe pod <pod-name>
kubectl describe ingress todo-app

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/sh

# Port forward (alternative to ingress)
kubectl port-forward svc/todo-app-frontend 3000:3000
kubectl port-forward svc/todo-app-backend 8000:8000

# Check resource usage
kubectl top nodes
kubectl top pods

# Helm operations
helm list
helm status todo-app
helm get values todo-app
helm upgrade todo-app ./infra/helm/todo-app
helm rollback todo-app
helm uninstall todo-app
```

### Useful Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgi='kubectl get ingress'
alias kl='kubectl logs'
alias kd='kubectl describe'
alias ke='kubectl exec -it'
```

## Support

### Documentation

- Architecture: `specs/001-k8s-deployment/architecture.md`
- Helm Chart: `specs/001-k8s-deployment/helm-chart-design.md`
- AI Workflows: `specs/001-k8s-deployment/ai-devops-workflows.md`
- Troubleshooting: `docs/deployment/TROUBLESHOOTING.md`

### Common Issues

- **Minikube won't start**: Check Docker is running, try `minikube delete` then `minikube start`
- **Images not found**: Ensure images are loaded with `minikube image load`
- **Ingress not accessible**: Verify ingress addon is enabled and host mapping is correct
- **Pods crashing**: Check logs with `kubectl logs` and verify secrets are set correctly

### Getting Help

- Check Minikube docs: https://minikube.sigs.k8s.io/docs/
- Check Kubernetes docs: https://kubernetes.io/docs/
- Check Helm docs: https://helm.sh/docs/
- Review project README and documentation

## Success Checklist

- [ ] Minikube cluster running
- [ ] Ingress addon enabled
- [ ] Host mapping configured (todo.local)
- [ ] Container images built and loaded
- [ ] Helm chart deployed successfully
- [ ] All pods in Running state (1/1 Ready)
- [ ] Services have endpoints
- [ ] Ingress accessible at http://todo.local
- [ ] Frontend loads in browser
- [ ] Authentication works (sign up/sign in)
- [ ] Task CRUD operations work
- [ ] AI chatbot responds to queries
- [ ] No errors in pod logs

**Congratulations!** Your Todo AI Chatbot is now running on Kubernetes! 🎉
