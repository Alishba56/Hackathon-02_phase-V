#!/bin/bash

# Minikube Teardown Script for Todo AI Chatbot
# This script safely stops and deletes the Minikube cluster

set -e  # Exit on error

echo "=========================================="
echo "Todo AI Chatbot - Minikube Teardown"
echo "=========================================="
echo ""

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ Error: Minikube is not installed"
    exit 1
fi

# Check if Minikube cluster exists
if ! minikube status &> /dev/null; then
    echo "ℹ️  No Minikube cluster found"
    exit 0
fi

echo "⚠️  This will delete the Minikube cluster and all deployed applications."
echo ""
read -p "Are you sure you want to continue? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "❌ Teardown cancelled"
    exit 0
fi

echo "🛑 Stopping Minikube cluster..."
minikube stop

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Failed to stop Minikube cluster gracefully"
fi

echo ""
echo "🗑️  Deleting Minikube cluster..."
minikube delete

if [ $? -ne 0 ]; then
    echo "❌ Failed to delete Minikube cluster"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Minikube Teardown Complete!"
echo "=========================================="
echo ""
echo "📋 Cleanup Notes:"
echo ""
echo "1. Host file entry (optional cleanup):"
echo "   Remove this line from /etc/hosts:"
echo "   127.0.0.1 todo.local"
echo ""
echo "   Command: sudo sed -i '/todo.local/d' /etc/hosts"
echo ""
echo "2. Docker images (optional cleanup):"
echo "   Remove local images if no longer needed:"
echo "   docker rmi todo-frontend:latest todo-backend:latest"
echo ""
echo "3. To recreate the cluster:"
echo "   ./infra/k8s/minikube/setup.sh"
echo ""
