#!/bin/bash
# OKE Deployment Script
# Purpose: Automated deployment of Todo AI Chatbot to Oracle OKE

set -e

echo "🚀 Todo AI Chatbot - OKE Deployment Script"
echo "==========================================="

# Configuration
NAMESPACE="${NAMESPACE:-default}"
HELM_RELEASE="todo-app"
HELM_CHART="./infra/helm/todo-app"
VALUES_FILE="./infra/helm/todo-app/values-oke.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ Error: kubectl not installed${NC}"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ Error: Helm not installed${NC}"
    exit 1
fi

if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}❌ Error: Cannot access Kubernetes cluster${NC}"
    echo "   Run: oci ce cluster create-kubeconfig --cluster-id <cluster-id> --file ~/.kube/config"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"
echo ""

# Check if secrets exist
echo "🔐 Checking Kubernetes secrets..."

if ! kubectl get secret app-secrets -n $NAMESPACE &> /dev/null; then
    echo -e "${YELLOW}⚠️  Warning: app-secrets not found${NC}"
    echo "   Create with: kubectl create secret generic app-secrets \\"
    echo "     --from-literal=cohere-api-key=\$COHERE_API_KEY \\"
    echo "     --from-literal=better-auth-secret=\$BETTER_AUTH_SECRET \\"
    echo "     --from-literal=database-url=\$DATABASE_URL"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if ! kubectl get secret kafka-secrets -n $NAMESPACE &> /dev/null; then
    echo -e "${YELLOW}⚠️  Warning: kafka-secrets not found${NC}"
    echo "   Create with: kubectl create secret generic kafka-secrets \\"
    echo "     --from-literal=username=\$KAFKA_USERNAME \\"
    echo "     --from-literal=password=\$KAFKA_PASSWORD"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✓ Secrets check complete${NC}"
echo ""

# Apply Dapr components
echo "📦 Applying Dapr components..."

if [ -d "./infra/dapr-components" ]; then
    kubectl apply -f ./infra/dapr-components/ -n $NAMESPACE
    echo -e "${GREEN}✓ Dapr components applied${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Dapr components directory not found${NC}"
fi

echo ""

# Deploy with Helm
echo "☸️  Deploying application with Helm..."

helm upgrade --install $HELM_RELEASE $HELM_CHART \
    --values $VALUES_FILE \
    --namespace $NAMESPACE \
    --wait \
    --timeout 5m \
    --atomic

echo -e "${GREEN}✓ Helm deployment complete${NC}"
echo ""

# Verify deployment
echo "🔍 Verifying deployment..."

kubectl rollout status deployment/todo-app-frontend -n $NAMESPACE --timeout=3m
kubectl rollout status deployment/todo-app-backend -n $NAMESPACE --timeout=3m

echo -e "${GREEN}✓ Deployment verification complete${NC}"
echo ""

# Display status
echo "📊 Deployment Status:"
echo "===================="
kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=todo-app
echo ""
kubectl get svc -n $NAMESPACE -l app.kubernetes.io/name=todo-app
echo ""
kubectl get ingress -n $NAMESPACE
echo ""
kubectl get components -n $NAMESPACE
echo ""

# Get application URL
INGRESS_IP=$(kubectl get ingress todo-app-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")

echo "==========================================="
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "==========================================="
echo ""
echo "Application URL: http://${INGRESS_IP}"
echo ""
echo "Next Steps:"
echo "  1. Wait for ingress IP if pending: kubectl get ingress -n $NAMESPACE -w"
echo "  2. Access application: http://${INGRESS_IP}"
echo "  3. Check logs: kubectl logs -l app=backend -c backend -n $NAMESPACE"
echo "  4. Check Dapr logs: kubectl logs -l app=backend -c daprd -n $NAMESPACE"
echo "  5. View Dapr dashboard: dapr dashboard -k"
echo ""
