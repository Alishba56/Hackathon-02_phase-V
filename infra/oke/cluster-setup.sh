#!/bin/bash
# OKE Cluster Provisioning Script
# Purpose: Provision Oracle Cloud Infrastructure Kubernetes Engine (OKE) cluster
# Target: Always-free tier (4 OCPU, 24GB RAM)

set -e

echo "🚀 Oracle OKE Cluster Provisioning Script"
echo "=========================================="

# Configuration
COMPARTMENT_ID="${OCI_COMPARTMENT_ID:-}"
REGION="${OCI_REGION:-us-ashburn-1}"
CLUSTER_NAME="todo-app-cluster"
VCN_NAME="todo-app-vcn"
SUBNET_NAME="todo-app-subnet"
NODE_POOL_NAME="todo-app-nodes"
NODE_SHAPE="VM.Standard.E2.1.Micro"
NODE_COUNT=2
K8S_VERSION="v1.28.2"

# Check prerequisites
if [ -z "$COMPARTMENT_ID" ]; then
    echo "❌ Error: OCI_COMPARTMENT_ID environment variable not set"
    echo "   Set it with: export OCI_COMPARTMENT_ID=ocid1.compartment.oc1..xxx"
    exit 1
fi

if ! command -v oci &> /dev/null; then
    echo "❌ Error: OCI CLI not installed"
    echo "   Install from: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm"
    exit 1
fi

echo "✓ Prerequisites check passed"
echo ""

# Step 1: Create VCN
echo "📡 Step 1: Creating VCN..."
VCN_ID=$(oci network vcn create \
    --compartment-id "$COMPARTMENT_ID" \
    --display-name "$VCN_NAME" \
    --cidr-block 10.0.0.0/16 \
    --region "$REGION" \
    --query 'data.id' \
    --raw-output 2>/dev/null || \
    oci network vcn list \
        --compartment-id "$COMPARTMENT_ID" \
        --query "data[?\"display-name\"=='$VCN_NAME'].id | [0]" \
        --raw-output)

echo "✓ VCN created/found: $VCN_ID"

# Step 2: Create Internet Gateway
echo "🌐 Step 2: Creating Internet Gateway..."
IGW_ID=$(oci network internet-gateway create \
    --compartment-id "$COMPARTMENT_ID" \
    --vcn-id "$VCN_ID" \
    --is-enabled true \
    --display-name "${VCN_NAME}-igw" \
    --query 'data.id' \
    --raw-output 2>/dev/null || \
    oci network internet-gateway list \
        --compartment-id "$COMPARTMENT_ID" \
        --vcn-id "$VCN_ID" \
        --query "data[0].id" \
        --raw-output)

echo "✓ Internet Gateway created/found: $IGW_ID"

# Step 3: Create Route Table
echo "🛣️  Step 3: Creating Route Table..."
RT_ID=$(oci network route-table create \
    --compartment-id "$COMPARTMENT_ID" \
    --vcn-id "$VCN_ID" \
    --display-name "${VCN_NAME}-rt" \
    --route-rules "[{\"destination\":\"0.0.0.0/0\",\"networkEntityId\":\"$IGW_ID\"}]" \
    --query 'data.id' \
    --raw-output 2>/dev/null || \
    oci network route-table list \
        --compartment-id "$COMPARTMENT_ID" \
        --vcn-id "$VCN_ID" \
        --query "data[0].id" \
        --raw-output)

echo "✓ Route Table created/found: $RT_ID"

# Step 4: Create Security List
echo "🔒 Step 4: Creating Security List..."
SL_ID=$(oci network security-list create \
    --compartment-id "$COMPARTMENT_ID" \
    --vcn-id "$VCN_ID" \
    --display-name "${VCN_NAME}-sl" \
    --egress-security-rules '[{"destination":"0.0.0.0/0","protocol":"all","isStateless":false}]' \
    --ingress-security-rules '[{"source":"0.0.0.0/0","protocol":"6","tcpOptions":{"destinationPortRange":{"min":80,"max":80}}},{"source":"0.0.0.0/0","protocol":"6","tcpOptions":{"destinationPortRange":{"min":443,"max":443}}}]' \
    --query 'data.id' \
    --raw-output 2>/dev/null || \
    oci network security-list list \
        --compartment-id "$COMPARTMENT_ID" \
        --vcn-id "$VCN_ID" \
        --query "data[0].id" \
        --raw-output)

echo "✓ Security List created/found: $SL_ID"

# Step 5: Create Subnet
echo "🌐 Step 5: Creating Subnet..."
SUBNET_ID=$(oci network subnet create \
    --compartment-id "$COMPARTMENT_ID" \
    --vcn-id "$VCN_ID" \
    --display-name "$SUBNET_NAME" \
    --cidr-block 10.0.1.0/24 \
    --route-table-id "$RT_ID" \
    --security-list-ids "[\"$SL_ID\"]" \
    --region "$REGION" \
    --query 'data.id' \
    --raw-output 2>/dev/null || \
    oci network subnet list \
        --compartment-id "$COMPARTMENT_ID" \
        --vcn-id "$VCN_ID" \
        --query "data[?\"display-name\"=='$SUBNET_NAME'].id | [0]" \
        --raw-output)

echo "✓ Subnet created/found: $SUBNET_ID"

# Step 6: Create OKE Cluster
echo "☸️  Step 6: Creating OKE Cluster (this takes ~10 minutes)..."
CLUSTER_ID=$(oci ce cluster create \
    --compartment-id "$COMPARTMENT_ID" \
    --name "$CLUSTER_NAME" \
    --kubernetes-version "$K8S_VERSION" \
    --vcn-id "$VCN_ID" \
    --region "$REGION" \
    --wait-for-state SUCCEEDED \
    --query 'data.resources[0].identifier' \
    --raw-output 2>/dev/null || \
    oci ce cluster list \
        --compartment-id "$COMPARTMENT_ID" \
        --query "data[?name=='$CLUSTER_NAME'].id | [0]" \
        --raw-output)

echo "✓ OKE Cluster created/found: $CLUSTER_ID"

# Step 7: Create Node Pool
echo "🖥️  Step 7: Creating Node Pool (this takes ~5 minutes)..."
NODE_POOL_ID=$(oci ce node-pool create \
    --cluster-id "$CLUSTER_ID" \
    --compartment-id "$COMPARTMENT_ID" \
    --name "$NODE_POOL_NAME" \
    --node-shape "$NODE_SHAPE" \
    --size "$NODE_COUNT" \
    --kubernetes-version "$K8S_VERSION" \
    --subnet-ids "[\"$SUBNET_ID\"]" \
    --wait-for-state SUCCEEDED \
    --query 'data.id' \
    --raw-output 2>/dev/null || \
    oci ce node-pool list \
        --compartment-id "$COMPARTMENT_ID" \
        --cluster-id "$CLUSTER_ID" \
        --query "data[0].id" \
        --raw-output)

echo "✓ Node Pool created/found: $NODE_POOL_ID"

# Step 8: Generate kubeconfig
echo "📝 Step 8: Generating kubeconfig..."
mkdir -p ~/.kube
oci ce cluster create-kubeconfig \
    --cluster-id "$CLUSTER_ID" \
    --file ~/.kube/config \
    --region "$REGION" \
    --token-version 2.0.0 \
    --kube-endpoint PUBLIC_ENDPOINT

echo "✓ Kubeconfig generated at ~/.kube/config"

# Step 9: Verify cluster access
echo "✅ Step 9: Verifying cluster access..."
kubectl cluster-info
kubectl get nodes

echo ""
echo "=========================================="
echo "✅ OKE Cluster Provisioning Complete!"
echo "=========================================="
echo ""
echo "Cluster Details:"
echo "  Name: $CLUSTER_NAME"
echo "  ID: $CLUSTER_ID"
echo "  Region: $REGION"
echo "  Nodes: $NODE_COUNT x $NODE_SHAPE"
echo "  Kubernetes Version: $K8S_VERSION"
echo ""
echo "Next Steps:"
echo "  1. Run: kubectl get nodes"
echo "  2. Run: ./infra/oke/dapr-init.sh"
echo "  3. Continue with Dapr component setup"
echo ""
