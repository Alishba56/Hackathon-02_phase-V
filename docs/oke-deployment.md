# Oracle OKE Deployment Guide

**Purpose**: Complete guide for deploying the Todo AI Chatbot application to Oracle Cloud Infrastructure Kubernetes Engine (OKE) with Dapr runtime and event-driven architecture.

## Prerequisites

Before deploying to OKE, ensure you have:

- ✅ Oracle Cloud Infrastructure (OCI) account
- ✅ OKE cluster provisioned (see `infra/oke/README.md`)
- ✅ Dapr installed on OKE cluster
- ✅ Redpanda Cloud serverless cluster created
- ✅ Kubernetes Secrets configured
- ✅ Docker images built and pushed to registry

## Quick Deployment

### One-Command Deployment

```bash
# Set environment variables
export NAMESPACE=default

# Run deployment script
chmod +x infra/scripts/deploy-oke.sh
./infra/scripts/deploy-oke.sh
```

The script will:
1. Check prerequisites (kubectl, helm, cluster access)
2. Verify Kubernetes secrets exist
3. Apply Dapr components
4. Deploy application with Helm
5. Verify deployment status
6. Display application URL

**Duration**: ~5 minutes

## Manual Deployment Steps

### Step 1: Create Kubernetes Secrets

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

# Verify secrets
kubectl get secrets
```

### Step 2: Update Dapr Component Configuration

Edit `infra/dapr-components/kafka-pubsub.yaml` and update the Redpanda bootstrap URL:

```yaml
metadata:
  - name: brokers
    value: "YOUR_REDPANDA_BOOTSTRAP_URL:9092"  # Update this
```

### Step 3: Apply Dapr Components

```bash
# Apply all Dapr components
kubectl apply -f infra/dapr-components/

# Verify components
kubectl get components

# Expected output:
# NAME                  AGE
# kafka-pubsub          10s
# kubernetes-secrets    10s
# scheduler             10s
# statestore            10s
```

### Step 4: Update Helm Values

Edit `infra/helm/todo-app/values-oke.yaml`:

```yaml
frontend:
  image:
    repository: ghcr.io/YOUR_GITHUB_USERNAME/todo-frontend
    tag: latest

backend:
  image:
    repository: ghcr.io/YOUR_GITHUB_USERNAME/todo-backend
    tag: latest

ingress:
  host: todo-app.example.com  # Update with your domain

dapr:
  kafka:
    brokers: "YOUR_REDPANDA_BOOTSTRAP_URL:9092"  # Update this
```

### Step 5: Deploy with Helm

```bash
# Install/upgrade Helm release
helm upgrade --install todo-app ./infra/helm/todo-app \
  --values ./infra/helm/todo-app/values-oke.yaml \
  --wait \
  --timeout 5m

# Verify deployment
kubectl get pods
kubectl get services
kubectl get ingress
```

### Step 6: Verify Deployment

```bash
# Run verification script
chmod +x infra/scripts/verify-deployment.sh
./infra/scripts/verify-deployment.sh
```

The script checks:
- Cluster connectivity
- Dapr installation
- Application pods (2/2 Ready with sidecars)
- Dapr components
- Kubernetes secrets
- Services and ingress
- Application health endpoints

## Accessing the Application

### Get Application URL

```bash
# Get ingress IP
kubectl get ingress todo-app-ingress

# Wait for EXTERNAL-IP to be assigned
kubectl get ingress todo-app-ingress -w
```

### Access Application

```
Frontend: http://<EXTERNAL-IP>/
Backend API: http://<EXTERNAL-IP>/api/
Health Check: http://<EXTERNAL-IP>/api/health
```

### Configure DNS (Optional)

```bash
# Get load balancer IP
INGRESS_IP=$(kubectl get ingress todo-app-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Add DNS A record
# todo-app.example.com -> $INGRESS_IP
```

## Monitoring and Logs

### View Application Logs

```bash
# Frontend logs
kubectl logs -l app=frontend -c frontend --tail=100 -f

# Backend logs
kubectl logs -l app=backend -c backend --tail=100 -f

# Dapr sidecar logs
kubectl logs -l app=backend -c daprd --tail=100 -f
```

### View Dapr Dashboard

```bash
# Port-forward Dapr dashboard
kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080

# Access at http://localhost:8080
```

### Check Pod Status

```bash
# Get all pods
kubectl get pods

# Describe pod
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

## Testing Event Publishing

### Create a Task

```bash
# Port-forward to backend
kubectl port-forward svc/todo-app-backend 8000:8000

# Create task (requires JWT token)
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{
    "title": "Test task",
    "description": "Testing event publishing"
  }'
```

### Verify Event Published

```bash
# Check Dapr logs for event publishing
kubectl logs -l app=backend -c daprd | grep publish

# Expected output:
# Publishing event to topic 'task-events'
# Event published successfully
```

### Check Redpanda Dashboard

1. Login to Redpanda Cloud dashboard
2. Navigate to Topics → task-events
3. View messages to see published events

## Updating the Application

### Update via CI/CD (Recommended)

```bash
# Push changes to main branch
git add .
git commit -m "Update application"
git push origin main

# GitHub Actions will automatically:
# 1. Run tests
# 2. Build Docker images
# 3. Push to registry
# 4. Deploy to OKE
```

### Manual Update

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

## Rollback

### Automatic Rollback

Helm's `--atomic` flag automatically rolls back on failure:

```bash
helm upgrade todo-app ./infra/helm/todo-app --atomic
```

### Manual Rollback

```bash
# List release history
helm history todo-app

# Rollback to previous version
helm rollback todo-app

# Rollback to specific revision
helm rollback todo-app <revision-number>
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -c <container-name>
```

### Dapr Sidecar Issues

```bash
# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd

# Check Dapr operator logs
kubectl logs -l app=dapr-operator -n dapr-system

# Restart pod
kubectl delete pod <pod-name>
```

### Events Not Publishing

```bash
# Check Dapr Pub/Sub logs
kubectl logs -l app=backend -c daprd | grep pubsub

# Verify Kafka connectivity
kubectl exec -it <backend-pod> -c daprd -- curl http://localhost:3500/v1.0/healthz

# Check Kafka credentials
kubectl get secret kafka-secrets -o yaml
```

### Ingress Not Working

```bash
# Check ingress status
kubectl describe ingress todo-app-ingress

# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

## Cleanup

### Delete Application

```bash
# Uninstall Helm release
helm uninstall todo-app

# Delete secrets
kubectl delete secret app-secrets kafka-secrets

# Delete Dapr components
kubectl delete -f infra/dapr-components/
```

### Delete OKE Cluster

See `infra/oke/README.md` for cluster deletion instructions.

## Support

- **OKE Documentation**: https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm
- **Dapr Documentation**: https://docs.dapr.io/
- **Helm Documentation**: https://helm.sh/docs/

---

**Deployment Guide Status**: Complete
**Last Updated**: 2026-02-09
