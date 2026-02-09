# Kubernetes Deployment Troubleshooting Guide

**Feature**: Cloud-Native Todo AI Chatbot Kubernetes Deployment
**Purpose**: Comprehensive troubleshooting procedures for Kubernetes deployment issues

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Pod Health Monitoring](#pod-health-monitoring)
3. [Log Access and Analysis](#log-access-and-analysis)
4. [Resource Monitoring](#resource-monitoring)
5. [Event Monitoring](#event-monitoring)
6. [Common Issues and Solutions](#common-issues-and-solutions)
7. [kubectl-ai Debugging Integration](#kubectl-ai-debugging-integration)
8. [Advanced Debugging Techniques](#advanced-debugging-techniques)

---

## Quick Diagnostics

### Initial Health Check

Run these commands first to get an overview of the deployment status:

```bash
# Check all resources
kubectl get all -l app.kubernetes.io/instance=todo-app

# Check pod status
kubectl get pods -l app.kubernetes.io/instance=todo-app

# Check recent events
kubectl get events --sort-by='.lastTimestamp' | head -20

# Check ingress status
kubectl get ingress -l app.kubernetes.io/instance=todo-app
```

### Quick Status Summary

```bash
# One-liner to check if everything is running
kubectl get pods -l app.kubernetes.io/instance=todo-app -o wide

# Expected output:
# NAME                               READY   STATUS    RESTARTS   AGE
# todo-app-backend-xxx               1/1     Running   0          5m
# todo-app-frontend-xxx              1/1     Running   0          5m
```

---

## Pod Health Monitoring

### Check Pod Status

```bash
# List all pods with detailed status
kubectl get pods -l app.kubernetes.io/instance=todo-app -o wide

# Check specific pod details
kubectl describe pod <pod-name>

# Watch pod status in real-time
kubectl get pods -l app.kubernetes.io/instance=todo-app --watch
```

### Pod Status Meanings

| Status | Meaning | Action |
|--------|---------|--------|
| `Running` | Pod is healthy and running | ✅ No action needed |
| `Pending` | Pod is waiting to be scheduled | Check node resources, events |
| `ContainerCreating` | Container is being created | Wait or check image pull status |
| `CrashLoopBackOff` | Container keeps crashing | Check logs, environment variables |
| `ImagePullBackOff` | Cannot pull container image | Check image name, Minikube image cache |
| `Error` | Container exited with error | Check logs for error details |
| `Completed` | Container finished successfully | Normal for jobs, unusual for deployments |
| `Terminating` | Pod is being deleted | Wait for graceful shutdown |

### Check Readiness and Liveness Probes

```bash
# Check probe configuration
kubectl describe pod <pod-name> | grep -A 10 "Liveness\|Readiness"

# Check probe results
kubectl describe pod <pod-name> | grep -A 5 "Conditions"

# Expected output for healthy pod:
# Conditions:
#   Type              Status
#   Initialized       True
#   Ready             True
#   ContainersReady   True
#   PodScheduled      True
```

### Check Pod Restarts

```bash
# Check restart count
kubectl get pods -l app.kubernetes.io/instance=todo-app

# If RESTARTS > 0, investigate:
kubectl describe pod <pod-name> | grep -A 20 "Events"
kubectl logs <pod-name> --previous  # Logs from previous container
```

### Pod Health Checklist

- [ ] All pods show `Running` status
- [ ] All pods show `1/1` in READY column
- [ ] Restart count is 0 or minimal (< 3)
- [ ] Readiness probe is passing
- [ ] Liveness probe is passing
- [ ] No recent error events

---

## Log Access and Analysis

### Basic Log Access

```bash
# View logs from frontend pod
kubectl logs -l app.kubernetes.io/component=frontend

# View logs from backend pod
kubectl logs -l app.kubernetes.io/component=backend

# View logs from specific pod
kubectl logs <pod-name>

# Follow logs in real-time
kubectl logs -l app.kubernetes.io/component=backend -f

# View logs from previous container (after crash)
kubectl logs <pod-name> --previous
```

### Advanced Log Filtering

```bash
# Last 50 lines
kubectl logs <pod-name> --tail=50

# Logs since specific time
kubectl logs <pod-name> --since=1h
kubectl logs <pod-name> --since=30m

# Logs with timestamps
kubectl logs <pod-name> --timestamps

# Logs from all pods with label
kubectl logs -l app.kubernetes.io/instance=todo-app --all-containers=true
```

### Log Analysis Patterns

**Frontend Logs (Next.js)**:
```bash
# Check for startup messages
kubectl logs -l app.kubernetes.io/component=frontend | grep -i "ready\|listening\|started"

# Check for errors
kubectl logs -l app.kubernetes.io/component=frontend | grep -i "error\|exception\|failed"

# Check for API connection issues
kubectl logs -l app.kubernetes.io/component=frontend | grep -i "api\|fetch\|connection"
```

**Backend Logs (FastAPI)**:
```bash
# Check for startup messages
kubectl logs -l app.kubernetes.io/component=backend | grep -i "uvicorn\|started\|application startup"

# Check for database connection
kubectl logs -l app.kubernetes.io/component=backend | grep -i "database\|postgres\|connection"

# Check for API errors
kubectl logs -l app.kubernetes.io/component=backend | grep -i "error\|exception\|traceback"

# Check for Cohere API issues
kubectl logs -l app.kubernetes.io/component=backend | grep -i "cohere\|api key"
```

### Structured Log Analysis

```bash
# Export logs to file for analysis
kubectl logs <pod-name> > pod-logs.txt

# Search for specific patterns
kubectl logs <pod-name> | grep -E "ERROR|WARN|CRITICAL"

# Count error occurrences
kubectl logs <pod-name> | grep -c "ERROR"

# Extract unique error messages
kubectl logs <pod-name> | grep "ERROR" | sort | uniq
```

### Log Checklist

- [ ] Logs are accessible for all pods
- [ ] No critical errors in logs
- [ ] Application startup messages present
- [ ] Database connection successful (backend)
- [ ] No authentication errors
- [ ] No API rate limit errors

---

## Resource Monitoring

### Check Resource Usage

```bash
# View resource usage for all pods
kubectl top pods -l app.kubernetes.io/instance=todo-app

# View node resource usage
kubectl top nodes

# Expected output:
# NAME                        CPU(cores)   MEMORY(bytes)
# todo-app-backend-xxx        50m          400Mi
# todo-app-frontend-xxx       20m          150Mi
```

### Check Resource Limits and Requests

```bash
# View configured resources
kubectl describe pod <pod-name> | grep -A 10 "Limits\|Requests"

# Expected configuration:
# Frontend:
#   Requests: cpu: 200m, memory: 256Mi
#   Limits:   cpu: 500m, memory: 512Mi
# Backend:
#   Requests: cpu: 300m, memory: 512Mi
#   Limits:   cpu: 1000m, memory: 1Gi
```

### Resource Monitoring Commands

```bash
# Continuous monitoring (updates every 2 seconds)
watch -n 2 kubectl top pods -l app.kubernetes.io/instance=todo-app

# Check if pods are being throttled
kubectl describe pod <pod-name> | grep -i "throttl"

# Check for OOMKilled events
kubectl get events | grep -i "oomkilled"

# Check node capacity
kubectl describe node minikube | grep -A 10 "Allocated resources"
```

### Resource Health Indicators

**Healthy Resource Usage**:
- CPU usage < 80% of limit
- Memory usage < 80% of limit
- No CPU throttling events
- No OOMKilled events
- Node has available capacity

**Warning Signs**:
- CPU usage consistently > 80% of limit
- Memory usage > 90% of limit
- Frequent CPU throttling
- OOMKilled events in pod history
- Node resources exhausted

### Resource Checklist

- [ ] CPU usage within configured limits
- [ ] Memory usage within configured limits
- [ ] No pods being throttled
- [ ] No OOMKilled events
- [ ] Node has sufficient capacity
- [ ] Resource requests match actual usage patterns

---

## Event Monitoring

### View Cluster Events

```bash
# View all recent events
kubectl get events --sort-by='.lastTimestamp'

# View events for specific namespace
kubectl get events --sort-by='.lastTimestamp' -n default

# View events for specific pod
kubectl describe pod <pod-name> | grep -A 20 "Events"

# Watch events in real-time
kubectl get events --watch
```

### Filter Events by Type

```bash
# Warning events only
kubectl get events --field-selector type=Warning

# Normal events only
kubectl get events --field-selector type=Normal

# Events in last hour
kubectl get events --sort-by='.lastTimestamp' | head -20

# Events for specific resource
kubectl get events --field-selector involvedObject.name=<pod-name>
```

### Common Event Types

**Normal Events** (informational):
- `Scheduled`: Pod assigned to node
- `Pulling`: Pulling container image
- `Pulled`: Successfully pulled image
- `Created`: Container created
- `Started`: Container started
- `Killing`: Container being terminated

**Warning Events** (require attention):
- `Failed`: Container failed to start
- `BackOff`: Container in crash loop
- `FailedScheduling`: Cannot schedule pod
- `FailedMount`: Cannot mount volume
- `Unhealthy`: Probe failed
- `ImagePullBackOff`: Cannot pull image

### Event Analysis Workflow

1. **Check for warnings**:
   ```bash
   kubectl get events --field-selector type=Warning
   ```

2. **Identify affected resources**:
   ```bash
   kubectl get events --field-selector type=Warning -o json | jq '.items[].involvedObject.name'
   ```

3. **Get detailed event information**:
   ```bash
   kubectl describe pod <affected-pod-name>
   ```

4. **Correlate with logs**:
   ```bash
   kubectl logs <affected-pod-name>
   ```

### Event Monitoring Checklist

- [ ] No warning events in last 10 minutes
- [ ] All pods successfully scheduled
- [ ] All images pulled successfully
- [ ] No probe failures
- [ ] No mount failures
- [ ] No scheduling conflicts

---

## Common Issues and Solutions

### Issue 1: Pod Startup Failures

**Symptoms**:
- Pod stuck in `Pending` or `ContainerCreating` state
- Pod shows `CrashLoopBackOff` status
- Pod shows `Error` status

**Diagnosis**:
```bash
# Check pod status and events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check previous container logs if crashed
kubectl logs <pod-name> --previous
```

**Common Causes and Solutions**:

1. **Missing Environment Variables**:
   ```bash
   # Check if secrets are created
   kubectl get secrets -l app.kubernetes.io/instance=todo-app

   # Verify secret values (base64 encoded)
   kubectl get secret todo-app-secrets -o yaml

   # Solution: Ensure secrets are set during Helm install
   helm upgrade todo-app ./infra/helm/todo-app \
     --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
     --set secrets.cohereApiKey="$COHERE_API_KEY" \
     --set secrets.databaseUrl="$DATABASE_URL"
   ```

2. **Database Connection Failure**:
   ```bash
   # Check backend logs for connection errors
   kubectl logs -l app.kubernetes.io/component=backend | grep -i "database\|connection"

   # Solution: Verify DATABASE_URL is correct and accessible
   # Test connection from within pod:
   kubectl exec -it <backend-pod> -- python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
   ```

3. **Invalid Cohere API Key**:
   ```bash
   # Check backend logs for API errors
   kubectl logs -l app.kubernetes.io/component=backend | grep -i "cohere\|api"

   # Solution: Verify COHERE_API_KEY is valid
   # Update secret:
   kubectl delete secret todo-app-secrets
   helm upgrade todo-app ./infra/helm/todo-app \
     --set secrets.cohereApiKey="$NEW_COHERE_API_KEY"
   ```

4. **Application Code Error**:
   ```bash
   # Check logs for Python/JavaScript errors
   kubectl logs <pod-name> | grep -i "error\|exception\|traceback"

   # Solution: Fix code issue, rebuild image, reload into Minikube
   docker build -t todo-backend:latest -f infra/docker/backend/Dockerfile backend/
   minikube image load todo-backend:latest
   kubectl rollout restart deployment todo-app-backend
   ```

### Issue 2: Ingress Not Accessible

**Symptoms**:
- Cannot access http://todo.local
- Browser shows "This site can't be reached"
- 404 or 502 errors

**Diagnosis**:
```bash
# Check ingress status
kubectl get ingress -l app.kubernetes.io/instance=todo-app

# Check ingress details
kubectl describe ingress todo-app-ingress

# Check if ingress controller is running
kubectl get pods -n ingress-nginx

# Check service endpoints
kubectl get endpoints -l app.kubernetes.io/instance=todo-app
```

**Common Causes and Solutions**:

1. **Ingress Addon Not Enabled**:
   ```bash
   # Check if ingress addon is enabled
   minikube addons list | grep ingress

   # Solution: Enable ingress addon
   minikube addons enable ingress

   # Wait for ingress controller to be ready
   kubectl wait --namespace ingress-nginx \
     --for=condition=ready pod \
     --selector=app.kubernetes.io/component=controller \
     --timeout=120s
   ```

2. **Host File Not Configured**:
   ```bash
   # Check if todo.local resolves to 127.0.0.1
   ping todo.local

   # Solution: Add to /etc/hosts (Linux/macOS) or C:\Windows\System32\drivers\etc\hosts (Windows)
   echo "127.0.0.1 todo.local" | sudo tee -a /etc/hosts
   ```

3. **Minikube Tunnel Not Running**:
   ```bash
   # Check if tunnel is needed
   minikube ip

   # Solution: Start Minikube tunnel (requires separate terminal)
   minikube tunnel
   ```

4. **Service Not Ready**:
   ```bash
   # Check if services have endpoints
   kubectl get endpoints

   # Solution: Wait for pods to be ready
   kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=todo-app --timeout=120s
   ```

5. **Ingress Path Configuration**:
   ```bash
   # Check ingress rules
   kubectl get ingress todo-app-ingress -o yaml

   # Solution: Verify paths are correct
   # Frontend: path: /
   # Backend: path: /api
   ```

### Issue 3: Database Connectivity Issues

**Symptoms**:
- Backend pod crashes on startup
- Logs show database connection errors
- API returns 500 errors

**Diagnosis**:
```bash
# Check backend logs
kubectl logs -l app.kubernetes.io/component=backend | grep -i "database\|postgres"

# Check DATABASE_URL secret
kubectl get secret todo-app-secrets -o jsonpath='{.data.databaseUrl}' | base64 -d

# Test connection from pod
kubectl exec -it <backend-pod> -- curl -v telnet://<db-host>:<db-port>
```

**Common Causes and Solutions**:

1. **Invalid DATABASE_URL**:
   ```bash
   # Solution: Verify format
   # postgresql://username:password@host:port/database

   # Update secret
   helm upgrade todo-app ./infra/helm/todo-app \
     --set secrets.databaseUrl="postgresql://user:pass@host:5432/dbname"
   ```

2. **Database Not Accessible from Cluster**:
   ```bash
   # Solution: Ensure database allows connections from Minikube IP
   minikube ip

   # Update database firewall rules to allow Minikube IP
   ```

3. **Connection Pool Exhausted**:
   ```bash
   # Check logs for pool errors
   kubectl logs -l app.kubernetes.io/component=backend | grep -i "pool"

   # Solution: Increase connection pool size or scale down replicas
   kubectl scale deployment todo-app-backend --replicas=1
   ```

### Issue 4: Resource Constraints

**Symptoms**:
- Pods stuck in `Pending` state
- OOMKilled events
- CPU throttling
- Slow performance

**Diagnosis**:
```bash
# Check pod status
kubectl describe pod <pod-name> | grep -i "insufficient\|oomkilled\|throttl"

# Check node resources
kubectl describe node minikube | grep -A 10 "Allocated resources"

# Check resource usage
kubectl top pods -l app.kubernetes.io/instance=todo-app
kubectl top nodes
```

**Common Causes and Solutions**:

1. **Insufficient Node Resources**:
   ```bash
   # Check Minikube configuration
   minikube config view

   # Solution: Increase Minikube resources
   minikube stop
   minikube delete
   minikube start --cpus=4 --memory=8192
   ```

2. **Memory Limit Too Low (OOMKilled)**:
   ```bash
   # Check memory usage
   kubectl top pod <pod-name>

   # Solution: Increase memory limit in values.yaml
   # backend.resources.limits.memory: "1.5Gi"

   helm upgrade todo-app ./infra/helm/todo-app \
     --set backend.resources.limits.memory=1.5Gi
   ```

3. **CPU Throttling**:
   ```bash
   # Check CPU usage
   kubectl top pod <pod-name>

   # Solution: Increase CPU limit in values.yaml
   # backend.resources.limits.cpu: "1500m"

   helm upgrade todo-app ./infra/helm/todo-app \
     --set backend.resources.limits.cpu=1500m
   ```

4. **Too Many Replicas**:
   ```bash
   # Check replica count
   kubectl get deployments -l app.kubernetes.io/instance=todo-app

   # Solution: Scale down
   kubectl scale deployment todo-app-backend --replicas=1
   kubectl scale deployment todo-app-frontend --replicas=1
   ```

### Issue 5: Image Pull Errors

**Symptoms**:
- Pod stuck in `ImagePullBackOff` or `ErrImagePull`
- Events show "Failed to pull image"

**Diagnosis**:
```bash
# Check pod events
kubectl describe pod <pod-name> | grep -A 10 "Events"

# Check image name
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[0].image}'

# Check images in Minikube
minikube image ls | grep todo
```

**Common Causes and Solutions**:

1. **Image Not Loaded into Minikube**:
   ```bash
   # Solution: Load images into Minikube
   ./infra/scripts/load-images.sh

   # Or manually:
   minikube image load todo-frontend:latest
   minikube image load todo-backend:latest
   ```

2. **Wrong Image Name**:
   ```bash
   # Check configured image name
   kubectl get deployment todo-app-backend -o jsonpath='{.spec.template.spec.containers[0].image}'

   # Solution: Verify image name matches built image
   docker images | grep todo

   # Update Helm values if needed
   helm upgrade todo-app ./infra/helm/todo-app \
     --set backend.image.repository=todo-backend \
     --set backend.image.tag=latest
   ```

3. **ImagePullPolicy Issue**:
   ```bash
   # Check pull policy
   kubectl get pod <pod-name> -o jsonpath='{.spec.containers[0].imagePullPolicy}'

   # Solution: Ensure imagePullPolicy is "IfNotPresent" or "Never" for local images
   # Update values.yaml:
   # backend.image.pullPolicy: IfNotPresent
   ```

---

## kubectl-ai Debugging Integration

### Using kubectl-ai for Troubleshooting

If kubectl-ai is installed, you can use natural language commands for debugging:

```bash
# Check if kubectl-ai is available
kubectl-ai version
```

### Common kubectl-ai Debugging Commands

**Pod Failures**:
```bash
# Diagnose why pod is failing
kubectl-ai "Why is the backend pod in CrashLoopBackOff state?"

# Expected AI analysis:
# - Checks pod status and events
# - Analyzes recent logs
# - Identifies root cause (e.g., missing env var, connection failure)
# - Provides specific remediation steps
```

**Log Analysis**:
```bash
# Analyze logs for errors
kubectl-ai "Analyze backend logs for errors in the last hour"

# Find specific error patterns
kubectl-ai "Show me all database connection errors from backend pods"

# Summarize log patterns
kubectl-ai "Summarize the most common errors in backend logs"
```

**Resource Issues**:
```bash
# Diagnose resource problems
kubectl-ai "Why is the backend pod being OOMKilled?"

# Get optimization suggestions
kubectl-ai "Analyze resource usage and suggest optimal limits"

# Check for throttling
kubectl-ai "Are any pods being CPU throttled?"
```

**Networking Issues**:
```bash
# Diagnose connectivity problems
kubectl-ai "Why can't frontend connect to backend service?"

# Check ingress configuration
kubectl-ai "Is the ingress configured correctly for todo.local?"

# Verify service endpoints
kubectl-ai "Check if all services have healthy endpoints"
```

**Performance Analysis**:
```bash
# Identify bottlenecks
kubectl-ai "What is causing slow response times?"

# Analyze pod performance
kubectl-ai "Which pods are using the most resources?"

# Get scaling recommendations
kubectl-ai "Should I scale up the backend deployment?"
```

### kubectl-ai Workflow Examples

**Workflow 1: Diagnose Pod Startup Failure**

```bash
# Step 1: Identify the issue
kubectl-ai "Why is the backend pod not starting?"

# Step 2: Get detailed analysis
kubectl-ai "Show me the last 50 lines of backend logs"

# Step 3: Get remediation steps
kubectl-ai "How do I fix the database connection error?"

# Step 4: Verify fix
kubectl-ai "Is the backend pod now healthy?"
```

**Workflow 2: Debug Performance Issues**

```bash
# Step 1: Identify slow components
kubectl-ai "Which pods have high CPU or memory usage?"

# Step 2: Analyze resource patterns
kubectl-ai "Show me resource usage trends for backend pods"

# Step 3: Get optimization recommendations
kubectl-ai "What resource limits should I set for optimal performance?"

# Step 4: Verify improvements
kubectl-ai "Compare current resource usage to previous baseline"
```

**Workflow 3: Troubleshoot Networking**

```bash
# Step 1: Check connectivity
kubectl-ai "Can frontend pods reach backend service?"

# Step 2: Verify DNS resolution
kubectl-ai "Is the backend service DNS resolving correctly?"

# Step 3: Check ingress routing
kubectl-ai "Verify ingress routes traffic correctly to frontend and backend"

# Step 4: Test end-to-end
kubectl-ai "Is the application accessible from outside the cluster?"
```

### kubectl-ai Fallback Procedures

If kubectl-ai is not available, use standard kubectl commands:

```bash
# Instead of: kubectl-ai "Why is the pod failing?"
# Use:
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl get events --field-selector involvedObject.name=<pod-name>

# Instead of: kubectl-ai "Analyze logs for errors"
# Use:
kubectl logs <pod-name> | grep -i "error\|exception\|failed"

# Instead of: kubectl-ai "Check resource usage"
# Use:
kubectl top pods
kubectl describe pod <pod-name> | grep -A 10 "Limits\|Requests"
```

---

## Advanced Debugging Techniques

### Interactive Pod Debugging

```bash
# Execute shell in running pod
kubectl exec -it <pod-name> -- /bin/sh

# Run commands inside pod
kubectl exec <pod-name> -- env  # Check environment variables
kubectl exec <pod-name> -- ps aux  # Check running processes
kubectl exec <pod-name> -- netstat -tlnp  # Check listening ports

# Test connectivity from inside pod
kubectl exec <pod-name> -- curl http://backend:8000/api/health
kubectl exec <pod-name> -- nslookup backend
```

### Debug with Ephemeral Containers

```bash
# Add debug container to running pod (Kubernetes 1.23+)
kubectl debug <pod-name> -it --image=busybox --target=<container-name>

# Use debug container for network troubleshooting
kubectl debug <pod-name> -it --image=nicolaka/netshoot
```

### Port Forwarding for Local Testing

```bash
# Forward backend port to localhost
kubectl port-forward svc/todo-app-backend 8000:8000

# Test backend API locally
curl http://localhost:8000/api/health

# Forward frontend port
kubectl port-forward svc/todo-app-frontend 3000:3000

# Access frontend at http://localhost:3000
```

### Deployment Rollback

```bash
# Check rollout history
kubectl rollout history deployment todo-app-backend

# Rollback to previous version
kubectl rollout undo deployment todo-app-backend

# Rollback to specific revision
kubectl rollout undo deployment todo-app-backend --to-revision=2

# Check rollout status
kubectl rollout status deployment todo-app-backend
```

### Resource Cleanup and Reset

```bash
# Delete and reinstall Helm release
helm uninstall todo-app
helm install todo-app ./infra/helm/todo-app \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.cohereApiKey="$COHERE_API_KEY" \
  --set secrets.databaseUrl="$DATABASE_URL"

# Force delete stuck pod
kubectl delete pod <pod-name> --grace-period=0 --force

# Restart deployment
kubectl rollout restart deployment todo-app-backend
kubectl rollout restart deployment todo-app-frontend
```

### Debugging Checklist

- [ ] Checked pod status and events
- [ ] Reviewed pod logs for errors
- [ ] Verified environment variables and secrets
- [ ] Checked resource usage and limits
- [ ] Verified network connectivity
- [ ] Tested service endpoints
- [ ] Checked ingress configuration
- [ ] Reviewed recent cluster events
- [ ] Attempted interactive debugging if needed
- [ ] Documented issue and resolution

---

## Getting Help

### Useful Resources

- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Minikube Documentation**: https://minikube.sigs.k8s.io/docs/
- **Helm Documentation**: https://helm.sh/docs/
- **kubectl Cheat Sheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/

### Support Channels

- Check project documentation in `docs/deployment/`
- Review AI tools guide: `docs/deployment/AI_TOOLS_GUIDE.md`
- Review quickstart guide: `specs/001-k8s-deployment/quickstart.md`

### Diagnostic Data Collection

When reporting issues, collect this information:

```bash
# Collect all diagnostic data
kubectl get all -l app.kubernetes.io/instance=todo-app -o yaml > deployment-state.yaml
kubectl describe pods -l app.kubernetes.io/instance=todo-app > pod-details.txt
kubectl logs -l app.kubernetes.io/instance=todo-app --all-containers=true > all-logs.txt
kubectl get events --sort-by='.lastTimestamp' > events.txt
kubectl top pods -l app.kubernetes.io/instance=todo-app > resource-usage.txt
minikube version > minikube-version.txt
kubectl version > kubectl-version.txt
helm list > helm-releases.txt
```

---

## Summary

This troubleshooting guide covers:

✅ Quick diagnostic procedures
✅ Pod health monitoring
✅ Log access and analysis
✅ Resource monitoring
✅ Event monitoring
✅ Common issues and solutions
✅ kubectl-ai debugging integration
✅ Advanced debugging techniques

For AI-powered troubleshooting workflows, see `docs/deployment/AI_TOOLS_GUIDE.md`.

For deployment procedures, see `specs/001-k8s-deployment/quickstart.md`.
