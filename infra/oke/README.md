# Oracle OKE Setup Guide

**Purpose**: Instructions for provisioning and configuring Oracle Cloud Infrastructure Kubernetes Engine (OKE) cluster for the Todo AI Chatbot application.

**Target**: Always-free tier (4 OCPU, 24GB RAM)

## Prerequisites

### Required Accounts
- ✅ Oracle Cloud Infrastructure (OCI) account
- ✅ OCI Compartment with appropriate permissions
- ✅ OCI CLI configured with credentials

### Required Tools
- ✅ `oci` CLI v3.0+ - [Install Guide](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm)
- ✅ `kubectl` v1.28+ - [Install Guide](https://kubernetes.io/docs/tasks/tools/)
- ✅ `dapr` CLI v1.12+ - [Install Guide](https://docs.dapr.io/getting-started/install-dapr-cli/)
- ✅ `helm` v3.x - [Install Guide](https://helm.sh/docs/intro/install/)

### Verify Installation

```bash
oci --version          # Oracle Cloud CLI
kubectl version        # Kubernetes CLI
dapr --version         # Dapr CLI
helm version           # Helm package manager
```

## Step 1: Configure OCI CLI

```bash
# Configure OCI CLI (interactive)
oci setup config

# Or use existing config
export OCI_COMPARTMENT_ID="ocid1.compartment.oc1..xxx"
export OCI_REGION="us-ashburn-1"
```

## Step 2: Provision OKE Cluster

### Option A: Automated Script (Recommended)

```bash
# Set environment variables
export OCI_COMPARTMENT_ID="ocid1.compartment.oc1..xxx"
export OCI_REGION="us-ashburn-1"

# Run provisioning script
chmod +x infra/oke/cluster-setup.sh
./infra/oke/cluster-setup.sh
```

The script will:
1. Create VCN (Virtual Cloud Network)
2. Create Internet Gateway
3. Create Route Table
4. Create Security List (allow HTTP/HTTPS)
5. Create Subnet
6. Create OKE Cluster (Kubernetes v1.28.2)
7. Create Node Pool (2 nodes, VM.Standard.E2.1.Micro)
8. Generate kubeconfig at `~/.kube/config`
9. Verify cluster access

**Duration**: ~15 minutes

### Option B: OCI Console (Manual)

1. Navigate to: **Developer Services → Kubernetes Clusters (OKE)**
2. Click **"Create Cluster"**
3. Select **"Quick Create"** workflow
4. Configure:
   - **Name**: `todo-app-cluster`
   - **Kubernetes Version**: 1.28 or later
   - **Node Pool Shape**: `VM.Standard.E2.1.Micro` (always-free)
   - **Number of Nodes**: 2
   - **Node Pool Subnet**: Public subnet
5. Click **"Create Cluster"**
6. Wait ~10 minutes for provisioning

## Step 3: Configure kubectl Access

```bash
# Generate kubeconfig (if not done by script)
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file ~/.kube/config \
  --region <region> \
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

## Step 4: Install Dapr Runtime

```bash
# Run Dapr initialization script
chmod +x infra/oke/dapr-init.sh
./infra/oke/dapr-init.sh
```

The script will:
1. Verify prerequisites (kubectl, dapr CLI)
2. Check cluster access
3. Install Dapr runtime on Kubernetes
4. Verify Dapr installation
5. Display Dapr system pods

**Duration**: ~2 minutes

### Verify Dapr Installation

```bash
# Check Dapr status
dapr status -k

# Expected output:
# NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
# dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   1m
# dapr-sentry            dapr-system  True     Running  1         1.12.0   1m
# dapr-operator          dapr-system  True     Running  1         1.12.0   1m
# dapr-placement         dapr-system  True     Running  1         1.12.0   1m

# Check Dapr pods
kubectl get pods -n dapr-system
```

## Step 5: Install NGINX Ingress Controller

```bash
# Add Helm repository
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install NGINX Ingress Controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --set controller.service.type=LoadBalancer \
  --wait

# Get external IP (may take 2-3 minutes)
kubectl get svc ingress-nginx-controller

# Wait for EXTERNAL-IP to be assigned
watch kubectl get svc ingress-nginx-controller
```

## Resource Allocation

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

## Troubleshooting

### Issue: Cluster Creation Fails

```bash
# Check OCI service limits
oci limits resource-availability get \
  --compartment-id $OCI_COMPARTMENT_ID \
  --service-name compute \
  --limit-name vm-standard-e2-1-micro-count

# Verify compartment permissions
oci iam compartment get --compartment-id $OCI_COMPARTMENT_ID
```

### Issue: kubectl Cannot Connect

```bash
# Regenerate kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-id> \
  --file ~/.kube/config \
  --region <region> \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT

# Verify kubeconfig
kubectl config view
kubectl config current-context
```

### Issue: Dapr Installation Fails

```bash
# Check Dapr CLI version
dapr version

# Uninstall and reinstall
dapr uninstall -k
dapr init -k --wait

# Check Dapr logs
kubectl logs -l app=dapr-operator -n dapr-system
```

### Issue: Nodes Not Ready

```bash
# Check node status
kubectl describe nodes

# Check node pool status
oci ce node-pool get --node-pool-id <node-pool-id>

# Check events
kubectl get events --all-namespaces --sort-by='.lastTimestamp'
```

## Cleanup

### Delete Application

```bash
# Uninstall Helm release
helm uninstall todo-app

# Delete Dapr components
kubectl delete -f infra/dapr-components/

# Uninstall Dapr
dapr uninstall -k
```

### Delete OKE Cluster

```bash
# Via OCI CLI
oci ce cluster delete --cluster-id <cluster-id> --force

# Or via OCI Console:
# Navigate to OKE → Clusters → Select cluster → Delete
```

## Next Steps

After OKE cluster is provisioned and Dapr is installed:

1. ✅ **Set up Redpanda Cloud**: Sign up and create serverless cluster
2. ✅ **Create Kubernetes Secrets**: Application and Kafka credentials
3. ✅ **Apply Dapr Components**: kubectl apply -f infra/dapr-components/
4. ✅ **Deploy Application**: helm upgrade --install todo-app ./infra/helm/todo-app
5. ✅ **Verify Deployment**: kubectl get pods, kubectl get components

## Support

- **OKE Documentation**: https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm
- **Dapr Documentation**: https://docs.dapr.io/
- **Kubernetes Documentation**: https://kubernetes.io/docs/

---

**Setup Status**: Ready for cluster provisioning
**Estimated Time**: 20-30 minutes (first time)
