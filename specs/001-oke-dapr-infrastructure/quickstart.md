# Quickstart: Deploy to Oracle OKE

**Date**: 2026-02-09
**Feature**: Oracle OKE Dapr Infrastructure Integration
**Branch**: `001-oke-dapr-infrastructure`

## Overview

This guide provides step-by-step instructions for deploying the Phase V Todo AI Chatbot to Oracle Cloud Infrastructure Kubernetes Engine (OKE) with Dapr runtime, event-driven architecture, and automated CI/CD.

## Prerequisites

### Required Accounts
- ✅ Oracle Cloud Infrastructure (OCI) account with OKE access
- ✅ GitHub account with repository access
- ✅ Redpanda Cloud account (free tier) OR Strimzi setup
- ✅ Neon PostgreSQL database (existing from Phase IV)

### Required Tools
- ✅ `oci` CLI (Oracle Cloud CLI) - [Install](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm)
- ✅ `kubectl` v1.28+ - [Install](https://kubernetes.io/docs/tasks/tools/)
- ✅ `helm` v3.x - [Install](https://helm.sh/docs/intro/install/)
- ✅ `dapr` CLI v1.12+ - [Install](https://docs.dapr.io/getting-started/install-dapr-cli/)
- ✅ `docker` or `podman` - [Install](https://docs.docker.com/get-docker/)
- ✅ `git` - [Install](https://git-scm.com/downloads)

### Verify Tool Installation

```bash
# Verify all tools are installed
oci --version          # Oracle Cloud CLI
kubectl version        # Kubernetes CLI
helm version           # Helm package manager
dapr --version         # Dapr CLI
docker --version       # Docker
git --version          # Git
```

## One-Command Deployment (After Setup)

Once prerequisites are configured, deploy with:

```bash
# Deploy to OKE
./infra/scripts/deploy-oke.sh

# Verify deployment
kubectl get pods
kubectl get components
```

## Detailed Setup Instructions

### Step 1: Provision Oracle OKE Cluster

#### Option A: OCI Console (Recommended for First-Time)

1. **Login to OCI Console**: https://cloud.oracle.com/
2. **Navigate to OKE**: Developer Services → Kubernetes Clusters (OKE)
3. **Create Cluster**:
   - Click "Create Cluster"
   - Select "Quick Create" workflow
   - Configure:
     - **Name**: `todo-app-cluster`
     - **Kubernetes Version**: 1.28 or later
     - **Node Pool Shape**: `VM.Standard.E2.1.Micro` (always-free)
     - **Number of Nodes**: 2
     - **Node Pool Subnet**: Public subnet
   - Click "Create Cluster"
   - Wait ~10 minutes for provisioning

4. **Access Cluster**:
   - Click on cluster name
   - Click "Access Cluster"
   - Follow instructions to set up kubeconfig

#### Option B: OCI CLI (Recommended for Automation)

```bash
# Set variables
export COMPARTMENT_ID="ocid1.compartment.oc1..xxx"
export REGION="us-ashburn-1"

# Create VCN (if not exists)
oci network vcn create \
  --compartment-id $COMPARTMENT_ID \
  --display-name todo-app-vcn \
  --cidr-block 10.0.0.0/16 \
  --region $REGION

# Get VCN OCID
export VCN_ID=$(oci network vcn list \
  --compartment-id $COMPARTMENT_ID \
  --query "data[?\"display-name\"=='todo-app-vcn'].id | [0]" \
  --raw-output)

# Create subnet
oci network subnet create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --display-name todo-app-subnet \
  --cidr-block 10.0.1.0/24 \
  --region $REGION

# Get subnet OCID
export SUBNET_ID=$(oci network subnet list \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --query "data[?\"display-name\"=='todo-app-subnet'].id | [0]" \
  --raw-output)

# Create OKE cluster (this takes ~10 minutes)
oci ce cluster create \
  --compartment-id $COMPARTMENT_ID \
  --name todo-app-cluster \
  --kubernetes-version v1.28.2 \
  --vcn-id $VCN_ID \
  --region $REGION

# Get cluster OCID
export CLUSTER_ID=$(oci ce cluster list \
  --compartment-id $COMPARTMENT_ID \
  --query "data[?name=='todo-app-cluster'].id | [0]" \
  --raw-output)

# Create node pool
oci ce node-pool create \
  --cluster-id $CLUSTER_ID \
  --compartment-id $COMPARTMENT_ID \
  --name todo-app-nodes \
  --node-shape VM.Standard.E2.1.Micro \
  --size 2 \
  --kubernetes-version v1.28.2 \
  --subnet-ids "[\"$SUBNET_ID\"]" \
  --region $REGION
```

#### Configure kubectl Access

```bash
# Generate kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id $CLUSTER_ID \
  --file $HOME/.kube/config \
  --region $REGION \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT

# Verify access
kubectl cluster-info
kubectl get nodes

# Expected output:
# NAME                                STATUS   ROLES    AGE   VERSION
# oke-node-pool-1-xxx                 Ready    <none>   5m    v1.28.2
# oke-node-pool-2-xxx                 Ready    <none>   5m    v1.28.2
```

### Step 2: Install Dapr on OKE

```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr installation
dapr status -k

# Expected output:
# NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
# dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   30s
# dapr-sentry            dapr-system  True     Running  1         1.12.0   30s
# dapr-operator          dapr-system  True     Running  1         1.12.0   30s
# dapr-placement         dapr-system  True     Running  1         1.12.0   30s

# Verify Dapr components
kubectl get pods -n dapr-system
```

### Step 3: Set Up Redpanda Cloud (Kafka)

#### Sign Up and Create Cluster

1. **Sign up**: https://redpanda.com/try-redpanda
2. **Create serverless cluster**:
   - Click "Create Cluster"
   - Select "Serverless"
   - Choose region close to OKE region (e.g., `us-east-1`)
   - Name: `todo-app-kafka`
3. **Create topics**:
   - Navigate to Topics
   - Create: `task-events` (3 partitions)
   - Create: `task-updates` (3 partitions)
   - Create: `reminders` (3 partitions)
4. **Generate credentials**:
   - Navigate to Security → SASL
   - Create new user: `todo-app-user`
   - Save username and password
5. **Get bootstrap URL**:
   - Navigate to Overview
   - Copy bootstrap server URL (e.g., `seed-abc123.cloud.redpanda.com:9092`)

#### Save Credentials

```bash
# Save for later use
export KAFKA_BOOTSTRAP_URL="seed-abc123.cloud.redpanda.com:9092"
export KAFKA_USERNAME="todo-app-user"
export KAFKA_PASSWORD="<your-password>"
```

### Step 4: Create Kubernetes Secrets

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

### Step 5: Update Dapr Components with Kafka URL

Edit `infra/dapr-components/kafka-pubsub.yaml`:

```yaml
metadata:
  - name: brokers
    value: "seed-abc123.cloud.redpanda.com:9092"  # Update with your URL
```

### Step 6: Deploy Dapr Components

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

# Check component details
kubectl describe component kafka-pubsub
```

### Step 7: Build and Push Docker Images

#### Option A: Local Build and Push

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

# Build frontend
cd frontend
docker build -t ghcr.io/$GITHUB_USERNAME/todo-frontend:latest .
docker push ghcr.io/$GITHUB_USERNAME/todo-frontend:latest

# Build backend
cd ../backend
docker build -t ghcr.io/$GITHUB_USERNAME/todo-backend:latest .
docker push ghcr.io/$GITHUB_USERNAME/todo-backend:latest
```

#### Option B: Use GitHub Actions (Recommended)

```bash
# Push code to trigger CI/CD
git add .
git commit -m "Deploy to OKE"
git push origin main

# GitHub Actions will automatically:
# 1. Run tests
# 2. Build images
# 3. Push to ghcr.io
# 4. Deploy to OKE
```

### Step 8: Update Helm Values for OKE

Create `infra/helm/todo-app/values-oke.yaml`:

```yaml
# OKE-specific values
global:
  environment: production
  imagePullPolicy: IfNotPresent

frontend:
  image:
    repository: ghcr.io/<your-username>/todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  replicas: 1

backend:
  image:
    repository: ghcr.io/<your-username>/todo-backend
    tag: latest
    pullPolicy: IfNotPresent
  replicas: 1

ingress:
  enabled: true
  className: nginx
  host: todo-app.example.com  # Update with your domain
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod  # Optional: TLS

# Dapr configuration
dapr:
  enabled: true
  appId: todo-app
  logLevel: info
```

### Step 9: Deploy Application with Helm

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

# Expected output:
# NAME                        READY   STATUS    RESTARTS   AGE
# frontend-abc123-xyz         2/2     Running   0          1m
# backend-def456-uvw          2/2     Running   0          1m
```

### Step 10: Configure Ingress (Optional)

#### Install NGINX Ingress Controller

```bash
# Install NGINX ingress controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --set controller.service.type=LoadBalancer

# Get external IP
kubectl get svc ingress-nginx-controller

# Wait for EXTERNAL-IP to be assigned (may take 2-3 minutes)
```

#### Configure DNS

```bash
# Get load balancer IP
export INGRESS_IP=$(kubectl get svc ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Configure DNS: todo-app.example.com -> $INGRESS_IP"
```

### Step 11: Verify Deployment

```bash
# Check all pods are running
kubectl get pods

# Check Dapr sidecars
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[*].name}{"\n"}{end}'

# Check Dapr components
kubectl get components

# Test application
curl http://$INGRESS_IP/
curl http://$INGRESS_IP/api/health

# Check logs
kubectl logs -l app=backend -c backend --tail=50
kubectl logs -l app=backend -c daprd --tail=50
```

### Step 12: Test Event Publishing

```bash
# Port-forward to backend
kubectl port-forward svc/backend 8000:8000

# Create a task (triggers event publishing)
curl -X POST http://localhost:8000/api/user-123/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{
    "title": "Test task",
    "description": "Testing event publishing"
  }'

# Check Dapr logs for event publishing
kubectl logs -l app=backend -c daprd | grep publish

# Check Redpanda dashboard for events
# Navigate to Redpanda Cloud → Topics → task-events
```

## GitHub Actions CI/CD Setup

### Step 1: Configure GitHub Secrets

Navigate to GitHub repository → Settings → Secrets and variables → Actions:

```bash
# Generate base64-encoded kubeconfig
cat $HOME/.kube/config | base64 -w 0 > kubeconfig.base64

# Add secrets via GitHub UI or gh CLI:
gh secret set KUBECONFIG < kubeconfig.base64
gh secret set COHERE_API_KEY --body "$COHERE_API_KEY"
gh secret set BETTER_AUTH_SECRET --body "$BETTER_AUTH_SECRET"
gh secret set DATABASE_URL --body "$DATABASE_URL"
gh secret set KAFKA_USERNAME --body "$KAFKA_USERNAME"
gh secret set KAFKA_PASSWORD --body "$KAFKA_PASSWORD"
```

### Step 2: Enable GitHub Actions

1. Navigate to repository → Actions tab
2. Enable workflows if disabled
3. Verify `.github/workflows/deploy-oke.yml` exists

### Step 3: Trigger Deployment

```bash
# Push to main branch
git add .
git commit -m "Enable CI/CD deployment"
git push origin main

# Monitor workflow
gh run watch

# Or view in GitHub UI: Actions tab
```

## Monitoring and Observability

### Access Dapr Dashboard

```bash
# Port-forward Dapr dashboard
kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080

# Access at http://localhost:8080
```

### View Logs

```bash
# Application logs
kubectl logs -l app=backend -c backend --tail=100 -f

# Dapr sidecar logs
kubectl logs -l app=backend -c daprd --tail=100 -f

# All logs for a pod
kubectl logs backend-abc123-xyz --all-containers=true
```

### Use kubectl-ai/kagent

```bash
# Analyze cluster health
kagent analyze cluster

# Debug pod issues
kagent debug pod backend-abc123-xyz

# Optimize resources
kubectl-ai optimize deployment backend
```

## Troubleshooting

### Issue: Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -c <container-name>
```

### Issue: Dapr Component Not Ready

```bash
# Check component status
kubectl get components
kubectl describe component kafka-pubsub

# Check Dapr operator logs
kubectl logs -l app=dapr-operator -n dapr-system
```

### Issue: Cannot Access Application

```bash
# Check ingress
kubectl get ingress
kubectl describe ingress todo-app-ingress

# Check services
kubectl get svc

# Check load balancer
kubectl get svc ingress-nginx-controller
```

### Issue: Events Not Publishing

```bash
# Check Dapr Pub/Sub logs
kubectl logs -l app=backend -c daprd | grep pubsub

# Test Kafka connectivity
kubectl exec -it backend-abc123-xyz -c daprd -- \
  curl http://localhost:3500/v1.0/healthz

# Verify Kafka credentials
kubectl get secret kafka-secrets -o yaml
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

### Delete Dapr

```bash
# Uninstall Dapr from cluster
dapr uninstall -k
```

### Delete OKE Cluster

```bash
# Via OCI CLI
oci ce cluster delete --cluster-id $CLUSTER_ID --force

# Or via OCI Console:
# Navigate to OKE → Clusters → Select cluster → Delete
```

## Next Steps

After successful deployment:

1. ✅ **Test all features**: Login, create tasks, chat with AI, verify events
2. ✅ **Monitor performance**: Check Dapr dashboard, logs, metrics
3. ✅ **Set up alerts**: Configure monitoring and alerting
4. ✅ **Document for judges**: Create demo script showing event flow
5. ✅ **Optimize resources**: Adjust pod limits based on usage

## Support

- **Dapr Documentation**: https://docs.dapr.io/
- **OKE Documentation**: https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm
- **Redpanda Documentation**: https://docs.redpanda.com/
- **Helm Documentation**: https://helm.sh/docs/

---

**Quickstart Guide Status**: ✅ Complete - Ready for Deployment
**Estimated Setup Time**: 30-45 minutes (first time), 5 minutes (subsequent deployments)
