#!/bin/bash

# Docker Image Load Script for Minikube
# This script loads Docker images into Minikube's image cache

set -e  # Exit on error

echo "=========================================="
echo "Todo AI Chatbot - Load Images to Minikube"
echo "=========================================="
echo ""

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ Error: Minikube is not installed"
    echo "Please install Minikube: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo "❌ Error: Minikube is not running"
    echo "Please start Minikube: ./infra/k8s/minikube/setup.sh"
    exit 1
fi

echo "✅ Minikube is running"
echo ""

# Check if images exist
echo "🔍 Checking for Docker images..."

if ! docker images todo-frontend:latest --format '{{.Repository}}' | grep -q todo-frontend; then
    echo "❌ Error: Frontend image not found"
    echo "Please build images first: ./infra/scripts/build-images.sh"
    exit 1
fi

if ! docker images todo-backend:latest --format '{{.Repository}}' | grep -q todo-backend; then
    echo "❌ Error: Backend image not found"
    echo "Please build images first: ./infra/scripts/build-images.sh"
    exit 1
fi

echo "✅ Docker images found"
echo ""

# Load frontend image
echo "📦 Loading frontend image into Minikube..."
minikube image load todo-frontend:latest

if [ $? -ne 0 ]; then
    echo "❌ Failed to load frontend image"
    exit 1
fi

echo "✅ Frontend image loaded"
echo ""

# Load backend image
echo "📦 Loading backend image into Minikube..."
minikube image load todo-backend:latest

if [ $? -ne 0 ]; then
    echo "❌ Failed to load backend image"
    exit 1
fi

echo "✅ Backend image loaded"
echo ""

# Verify images in Minikube
echo "🔍 Verifying images in Minikube..."
echo ""
minikube image ls | grep -E "todo-frontend|todo-backend"

echo ""
echo "=========================================="
echo "✅ Images Loaded Successfully!"
echo "=========================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Deploy application with Helm:"
echo "   ./infra/scripts/deploy.sh"
echo ""
echo "2. Or deploy manually:"
echo "   helm install todo-app ./infra/helm/todo-app \\"
echo "     --set secrets.betterAuthSecret=\$BETTER_AUTH_SECRET \\"
echo "     --set secrets.cohereApiKey=\$COHERE_API_KEY \\"
echo "     --set secrets.databaseUrl=\$DATABASE_URL"
echo ""
