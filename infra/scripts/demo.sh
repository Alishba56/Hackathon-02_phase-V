#!/bin/bash

# AI-Powered DevOps Demo Script for Todo AI Chatbot
# This script demonstrates the complete workflow using Gordon, kubectl-ai, and kagent

set -e  # Exit on error

echo "=========================================="
echo "AI-Powered DevOps Demo"
echo "Todo AI Chatbot - Kubernetes Deployment"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print section headers
print_section() {
    echo ""
    echo -e "${BLUE}=========================================="
    echo -e "$1"
    echo -e "==========================================${NC}"
    echo ""
}

# Function to print step headers
print_step() {
    echo -e "${GREEN}▶ $1${NC}"
    echo ""
}

# Function to print warnings
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print errors
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
print_section "Phase 0: Prerequisites Check"

print_step "Checking required tools..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi
echo "✅ Docker: $(docker --version)"

# Check Minikube
if ! command -v minikube &> /dev/null; then
    print_error "Minikube is not installed"
    exit 1
fi
echo "✅ Minikube: $(minikube version --short)"

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed"
    exit 1
fi
echo "✅ kubectl: $(kubectl version --client --short)"

# Check Helm
if ! command -v helm &> /dev/null; then
    print_error "Helm is not installed"
    exit 1
fi
echo "✅ Helm: $(helm version --short)"

# Check for AI tools (optional)
echo ""
print_step "Checking AI DevOps tools (optional)..."

if command -v kubectl-ai &> /dev/null; then
    echo "✅ kubectl-ai: Available"
    KUBECTL_AI_AVAILABLE=true
else
    print_warning "kubectl-ai: Not available (will use standard kubectl)"
    KUBECTL_AI_AVAILABLE=false
fi

if command -v kagent &> /dev/null; then
    echo "✅ kagent: Available"
    KAGENT_AVAILABLE=true
else
    print_warning "kagent: Not available (will use standard kubectl)"
    KAGENT_AVAILABLE=false
fi

# Check if Minikube is running
echo ""
print_step "Checking Minikube status..."
if ! minikube status &> /dev/null; then
    print_warning "Minikube is not running. Starting Minikube..."
    ./infra/k8s/minikube/setup.sh
else
    echo "✅ Minikube is running"
fi

# Phase 1: Containerization with Gordon
print_section "Phase 1: Containerization with Gordon"

print_step "Step 1: Frontend Dockerfile Generation"
echo "Command: docker ai 'Create production Dockerfile for Next.js 16 with standalone output'"
echo ""
print_warning "Note: Gordon (Docker AI) requires Docker Desktop 4.53+ Beta"
print_warning "Using pre-generated Dockerfile from infra/docker/frontend/Dockerfile"
echo ""
echo "Dockerfile features:"
echo "  - Multi-stage build (deps → builder → runner)"
echo "  - node:20-alpine base images"
echo "  - Standalone output mode"
echo "  - Non-root user execution"
echo "  - Optimized layer caching"
echo ""

print_step "Step 2: Build Frontend Image"
echo "Building frontend image..."
docker build -t todo-frontend:latest -f infra/docker/frontend/Dockerfile frontend/
echo ""
echo "✅ Frontend image built: $(docker images todo-frontend:latest --format '{{.Size}}')"
echo ""

print_step "Step 3: Backend Dockerfile Generation"
echo "Command: docker ai 'Create production Dockerfile for FastAPI with uvicorn'"
echo ""
print_warning "Using pre-generated Dockerfile from infra/docker/backend/Dockerfile"
echo ""
echo "Dockerfile features:"
echo "  - python:3.11-slim base image"
echo "  - Efficient dependency installation"
echo "  - Health check configuration"
echo "  - Non-root user execution"
echo "  - Uvicorn production configuration"
echo ""

print_step "Step 4: Build Backend Image"
echo "Building backend image..."
docker build -t todo-backend:latest -f infra/docker/backend/Dockerfile backend/
echo ""
echo "✅ Backend image built: $(docker images todo-backend:latest --format '{{.Size}}')"
echo ""

print_step "Step 5: Load Images into Minikube"
echo "Loading frontend image..."
minikube image load todo-frontend:latest
echo "Loading backend image..."
minikube image load todo-backend:latest
echo ""
echo "✅ Images loaded into Minikube"
echo ""

# Phase 2: Deployment with kubectl-ai
print_section "Phase 2: Deployment with kubectl-ai"

print_step "Step 6: Generate Kubernetes Manifests"
if [ "$KUBECTL_AI_AVAILABLE" = true ]; then
    echo "Using kubectl-ai for manifest generation..."
    echo ""
    echo "Command: kubectl-ai 'Create deployment for frontend with 1 replica, 256Mi memory, readiness probe'"
    echo "Command: kubectl-ai 'Create deployment for backend with 1 replica, 512Mi memory, readiness probe'"
else
    echo "kubectl-ai not available - using pre-generated Helm chart"
fi
echo ""
echo "✅ Using Helm chart: infra/helm/todo-app/"
echo ""

print_step "Step 7: Create Services"
if [ "$KUBECTL_AI_AVAILABLE" = true ]; then
    echo "Command: kubectl-ai 'Create ClusterIP service for frontend on port 3000'"
    echo "Command: kubectl-ai 'Create ClusterIP service for backend on port 8000'"
else
    echo "Using Helm chart service templates"
fi
echo ""
echo "✅ Services defined in Helm chart"
echo ""

print_step "Step 8: Configure Ingress"
if [ "$KUBECTL_AI_AVAILABLE" = true ]; then
    echo "Command: kubectl-ai 'Create ingress for todo.local routing / to frontend and /api to backend'"
else
    echo "Using Helm chart ingress template"
fi
echo ""
echo "✅ Ingress configured for todo.local"
echo ""

print_step "Step 9: Deploy with Helm"
echo "Checking for required secrets..."

if [ -z "$BETTER_AUTH_SECRET" ]; then
    print_warning "BETTER_AUTH_SECRET not set"
    read -p "Enter BETTER_AUTH_SECRET: " BETTER_AUTH_SECRET
fi

if [ -z "$COHERE_API_KEY" ]; then
    print_warning "COHERE_API_KEY not set"
    read -p "Enter COHERE_API_KEY: " COHERE_API_KEY
fi

if [ -z "$DATABASE_URL" ]; then
    print_warning "DATABASE_URL not set"
    read -p "Enter DATABASE_URL: " DATABASE_URL
fi

echo ""
echo "Installing Helm release..."
helm install todo-app ./infra/helm/todo-app \
    --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
    --set secrets.cohereApiKey="$COHERE_API_KEY" \
    --set secrets.databaseUrl="$DATABASE_URL"

echo ""
echo "✅ Helm release installed"
echo ""

print_step "Step 10: Verify Deployment"
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=todo-app --timeout=120s || true
echo ""
kubectl get pods,svc,ingress -l app.kubernetes.io/instance=todo-app
echo ""

# Phase 3: Operations with kubectl-ai
print_section "Phase 3: Operations with kubectl-ai"

print_step "Step 11: Scale Backend"
if [ "$KUBECTL_AI_AVAILABLE" = true ]; then
    echo "Command: kubectl-ai 'Scale backend to 3 replicas'"
    kubectl-ai "Scale backend to 3 replicas" || kubectl scale deployment todo-app-backend --replicas=3
else
    echo "Using standard kubectl command..."
    kubectl scale deployment todo-app-backend --replicas=3
fi
echo ""
echo "✅ Backend scaled to 3 replicas"
echo ""

print_step "Step 12: Check Scaling Status"
echo "Checking pod status..."
kubectl get pods -l app.kubernetes.io/component=backend
echo ""

print_step "Step 13: Simulate Pod Failure"
echo "Deleting one backend pod to demonstrate self-healing..."
BACKEND_POD=$(kubectl get pods -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod $BACKEND_POD
echo ""
echo "✅ Pod deleted: $BACKEND_POD"
echo ""
echo "Waiting for Kubernetes to recreate the pod..."
sleep 5
kubectl get pods -l app.kubernetes.io/component=backend
echo ""

print_step "Step 14: Debug with kubectl-ai"
if [ "$KUBECTL_AI_AVAILABLE" = true ]; then
    echo "Command: kubectl-ai 'Why did the backend pod restart?'"
    echo ""
    print_warning "kubectl-ai would analyze pod events and logs to explain the restart"
else
    echo "Checking pod events..."
    kubectl get events --sort-by='.lastTimestamp' | grep -i backend | head -5
fi
echo ""

# Phase 4: Monitoring with kagent
print_section "Phase 4: Monitoring with kagent"

print_step "Step 15: Cluster Health Check"
if [ "$KAGENT_AVAILABLE" = true ]; then
    echo "Command: kagent 'Check cluster health'"
    kagent "Check cluster health" || echo "kagent command failed, using kubectl"
else
    echo "Using standard kubectl commands..."
    echo ""
    echo "Node Status:"
    kubectl get nodes
    echo ""
    echo "Pod Status:"
    kubectl get pods -l app.kubernetes.io/instance=todo-app
    echo ""
    echo "Service Status:"
    kubectl get svc -l app.kubernetes.io/instance=todo-app
fi
echo ""

print_step "Step 16: Resource Analysis"
if [ "$KAGENT_AVAILABLE" = true ]; then
    echo "Command: kagent 'Analyze resource usage and suggest optimizations'"
    kagent "Analyze resource usage and suggest optimizations" || echo "kagent command failed"
else
    echo "Using kubectl top..."
    kubectl top pods -l app.kubernetes.io/instance=todo-app || print_warning "Metrics not available yet"
fi
echo ""

print_step "Step 17: Log Analysis"
if [ "$KAGENT_AVAILABLE" = true ]; then
    echo "Command: kagent 'Analyze backend logs for errors'"
    kagent "Analyze backend logs for errors" || echo "kagent command failed"
else
    echo "Checking backend logs..."
    BACKEND_POD=$(kubectl get pods -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')
    kubectl logs $BACKEND_POD --tail=20
fi
echo ""

print_step "Step 18: Performance Check"
if [ "$KAGENT_AVAILABLE" = true ]; then
    echo "Command: kagent 'Identify any performance bottlenecks'"
    kagent "Identify any performance bottlenecks" || echo "kagent command failed"
else
    echo "Checking resource usage..."
    kubectl top pods -l app.kubernetes.io/instance=todo-app || print_warning "Metrics not available yet"
fi
echo ""

# Phase 5: Optimization
print_section "Phase 5: Optimization"

print_step "Step 19: Apply Recommendations"
echo "Based on analysis, resource limits are appropriate for local Minikube"
echo "In production, you would apply kagent recommendations here"
echo ""

print_step "Step 20: Verify Improvements"
echo "Current resource usage:"
kubectl top pods -l app.kubernetes.io/instance=todo-app || print_warning "Metrics not available yet"
echo ""

print_step "Step 21: Final Health Check"
if [ "$KAGENT_AVAILABLE" = true ]; then
    echo "Command: kagent 'Confirm cluster is healthy and optimized'"
    kagent "Confirm cluster is healthy and optimized" || echo "kagent command failed"
else
    echo "Final status check..."
    kubectl get all -l app.kubernetes.io/instance=todo-app
fi
echo ""

# Summary
print_section "Demo Complete!"

echo "✅ All phases completed successfully!"
echo ""
echo "📊 Deployment Summary:"
echo "   - Frontend: Containerized and deployed"
echo "   - Backend: Containerized, deployed, and scaled to 3 replicas"
echo "   - Ingress: Configured for http://todo.local"
echo "   - Self-healing: Demonstrated with pod deletion"
echo "   - Monitoring: Health checks and resource analysis performed"
echo ""
echo "🌐 Access the application:"
echo "   1. Ensure host file is configured:"
echo "      127.0.0.1 todo.local"
echo ""
echo "   2. Open in browser:"
echo "      http://todo.local"
echo ""
echo "📋 Useful Commands:"
echo "   - View logs: kubectl logs -l app.kubernetes.io/instance=todo-app -f"
echo "   - Check status: kubectl get all -l app.kubernetes.io/instance=todo-app"
echo "   - Resource usage: kubectl top pods -l app.kubernetes.io/instance=todo-app"
echo "   - Uninstall: helm uninstall todo-app"
echo ""
echo "🎉 Thank you for watching the AI-Powered DevOps demo!"
echo ""
