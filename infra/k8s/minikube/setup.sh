#!/bin/bash

# Minikube Setup Script for Todo AI Chatbot Kubernetes Deployment
# This script initializes a local Minikube cluster with required addons

set -e  # Exit on error

echo "=========================================="
echo "Todo AI Chatbot - Minikube Setup"
echo "=========================================="
echo ""

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ Error: Minikube is not installed"
    echo "Please install Minikube: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ Error: kubectl is not installed"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Start Minikube with recommended configuration
echo "🚀 Starting Minikube cluster..."
echo "   Configuration: 4 CPUs, 8GB RAM, Docker driver"
echo ""

minikube start \
    --cpus=4 \
    --memory=8192 \
    --driver=docker \
    --kubernetes-version=v1.28.0

if [ $? -ne 0 ]; then
    echo "❌ Failed to start Minikube cluster"
    exit 1
fi

echo ""
echo "✅ Minikube cluster started successfully"
echo ""

# Enable ingress addon
echo "🔧 Enabling ingress addon..."
minikube addons enable ingress

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Failed to enable ingress addon"
else
    echo "✅ Ingress addon enabled"
fi

echo ""

# Enable metrics-server addon
echo "🔧 Enabling metrics-server addon..."
minikube addons enable metrics-server

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Failed to enable metrics-server addon"
else
    echo "✅ Metrics-server addon enabled"
fi

echo ""

# Wait for ingress controller to be ready
echo "⏳ Waiting for ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/component=controller \
    --timeout=120s 2>/dev/null || echo "⚠️  Ingress controller may still be starting"

echo ""

# Verify cluster is ready
echo "🔍 Verifying cluster status..."
kubectl cluster-info

echo ""
kubectl get nodes

echo ""
echo "=========================================="
echo "✅ Minikube Setup Complete!"
echo "=========================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Configure host file mapping:"
echo "   Add this line to /etc/hosts (requires sudo):"
echo "   127.0.0.1 todo.local"
echo ""
echo "   Command: echo '127.0.0.1 todo.local' | sudo tee -a /etc/hosts"
echo ""
echo "2. Build and load Docker images:"
echo "   ./infra/scripts/build-images.sh"
echo "   ./infra/scripts/load-images.sh"
echo ""
echo "3. Deploy application with Helm:"
echo "   ./infra/scripts/deploy.sh"
echo ""
echo "📊 Cluster Information:"
echo "   Dashboard: minikube dashboard"
echo "   IP: $(minikube ip)"
echo "   Status: minikube status"
echo ""
echo "🛑 To stop the cluster: minikube stop"
echo "🗑️  To delete the cluster: ./infra/k8s/minikube/teardown.sh"
echo ""
