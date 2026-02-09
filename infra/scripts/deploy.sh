#!/bin/bash

# Helm Deployment Script for Todo AI Chatbot
# This script deploys the application to Minikube using Helm

set -e  # Exit on error

echo "=========================================="
echo "Todo AI Chatbot - Helm Deployment"
echo "=========================================="
echo ""

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ Error: Helm is not installed"
    echo "Please install Helm: https://helm.sh/docs/intro/install/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ Error: kubectl is not installed"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo "❌ Error: Minikube is not running"
    echo "Please start Minikube: ./infra/k8s/minikube/setup.sh"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Check for required environment variables
if [ -z "$BETTER_AUTH_SECRET" ]; then
    echo "⚠️  Warning: BETTER_AUTH_SECRET not set"
    read -p "Enter BETTER_AUTH_SECRET: " BETTER_AUTH_SECRET
fi

if [ -z "$COHERE_API_KEY" ]; then
    echo "⚠️  Warning: COHERE_API_KEY not set"
    read -p "Enter COHERE_API_KEY: " COHERE_API_KEY
fi

if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  Warning: DATABASE_URL not set"
    read -p "Enter DATABASE_URL: " DATABASE_URL
fi

echo ""
echo "✅ Secrets configured"
echo ""

# Lint Helm chart
echo "🔍 Linting Helm chart..."
helm lint ./infra/helm/todo-app

if [ $? -ne 0 ]; then
    echo "❌ Helm chart has errors"
    exit 1
fi

echo "✅ Helm chart is valid"
echo ""

# Check if release already exists
if helm list | grep -q "todo-app"; then
    echo "⚠️  Release 'todo-app' already exists"
    read -p "Do you want to upgrade the existing release? (yes/no): " -r
    echo ""

    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "🔄 Upgrading existing release..."
        helm upgrade todo-app ./infra/helm/todo-app \
            --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
            --set secrets.cohereApiKey="$COHERE_API_KEY" \
            --set secrets.databaseUrl="$DATABASE_URL"

        if [ $? -ne 0 ]; then
            echo "❌ Failed to upgrade release"
            exit 1
        fi

        echo "✅ Release upgraded successfully"
    else
        echo "❌ Deployment cancelled"
        exit 0
    fi
else
    # Install new release
    echo "🚀 Installing Helm release..."
    echo "   Release name: todo-app"
    echo "   Chart: ./infra/helm/todo-app"
    echo ""

    helm install todo-app ./infra/helm/todo-app \
        --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
        --set secrets.cohereApiKey="$COHERE_API_KEY" \
        --set secrets.databaseUrl="$DATABASE_URL"

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install release"
        exit 1
    fi

    echo ""
    echo "✅ Release installed successfully"
fi

echo ""
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/instance=todo-app \
    --timeout=120s 2>/dev/null || echo "⚠️  Pods may still be starting"

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "📊 Deployment Status:"
kubectl get pods,svc,ingress -l app.kubernetes.io/instance=todo-app

echo ""
echo "📋 Access Information:"
echo ""
echo "1. Ensure host file is configured:"
echo "   127.0.0.1 todo.local"
echo ""
echo "2. Access the application:"
echo "   http://todo.local"
echo ""
echo "3. Check logs:"
echo "   kubectl logs -l app.kubernetes.io/instance=todo-app -f"
echo ""
echo "4. Check resource usage:"
echo "   kubectl top pods -l app.kubernetes.io/instance=todo-app"
echo ""
echo "🛑 To uninstall: helm uninstall todo-app"
echo ""
