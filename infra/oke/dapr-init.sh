#!/bin/bash
# Dapr Initialization Script for OKE
# Purpose: Install Dapr runtime on Oracle Kubernetes Engine cluster

set -e

echo "🎯 Dapr Initialization Script for OKE"
echo "======================================"

# Check prerequisites
if ! command -v kubectl &> /dev/null; then
    echo "❌ Error: kubectl not installed"
    echo "   Install from: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

if ! command -v dapr &> /dev/null; then
    echo "❌ Error: Dapr CLI not installed"
    echo "   Install from: https://docs.dapr.io/getting-started/install-dapr-cli/"
    exit 1
fi

# Verify cluster access
echo "🔍 Verifying cluster access..."
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Error: Cannot access Kubernetes cluster"
    echo "   Run: oci ce cluster create-kubeconfig --cluster-id <cluster-id> --file ~/.kube/config"
    exit 1
fi

echo "✓ Cluster access verified"
echo ""

# Check Dapr CLI version
DAPR_VERSION=$(dapr version --client-only 2>/dev/null | grep "CLI version" | awk '{print $3}')
echo "📦 Dapr CLI version: $DAPR_VERSION"
echo ""

# Initialize Dapr on Kubernetes
echo "🚀 Installing Dapr runtime on Kubernetes..."
dapr init -k --wait

echo ""
echo "✅ Dapr installation complete!"
echo ""

# Verify Dapr installation
echo "🔍 Verifying Dapr installation..."
dapr status -k

echo ""
echo "📊 Checking Dapr system pods..."
kubectl get pods -n dapr-system

echo ""
echo "======================================"
echo "✅ Dapr Initialization Complete!"
echo "======================================"
echo ""
echo "Dapr Components Installed:"
echo "  • dapr-operator"
echo "  • dapr-sidecar-injector"
echo "  • dapr-sentry (mTLS)"
echo "  • dapr-placement"
echo ""
echo "Next Steps:"
echo "  1. Apply Dapr components: kubectl apply -f infra/dapr-components/"
echo "  2. Deploy application: helm upgrade --install todo-app ./infra/helm/todo-app"
echo "  3. Verify deployment: kubectl get pods"
echo ""
