#!/bin/bash
# Deployment Verification Script
# Purpose: Verify OKE deployment health and functionality

set -e

echo "🔍 Todo AI Chatbot - Deployment Verification"
echo "============================================="

# Configuration
NAMESPACE="${NAMESPACE:-default}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# Function to check and report
check() {
    local name=$1
    local command=$2

    echo -n "Checking $name... "

    if eval "$command" &> /dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

echo ""
echo "1. Cluster Connectivity"
echo "----------------------"
check "Cluster access" "kubectl cluster-info"
check "Nodes ready" "kubectl get nodes | grep -q Ready"

echo ""
echo "2. Dapr Installation"
echo "-------------------"
check "Dapr operator" "kubectl get pods -n dapr-system -l app=dapr-operator | grep -q Running"
check "Dapr sidecar injector" "kubectl get pods -n dapr-system -l app=dapr-sidecar-injector | grep -q Running"
check "Dapr sentry" "kubectl get pods -n dapr-system -l app=dapr-sentry | grep -q Running"
check "Dapr placement" "kubectl get pods -n dapr-system -l app=dapr-placement | grep -q Running"

echo ""
echo "3. Application Pods"
echo "------------------"
check "Frontend pod running" "kubectl get pods -n $NAMESPACE -l app=frontend | grep -q '2/2.*Running'"
check "Backend pod running" "kubectl get pods -n $NAMESPACE -l app=backend | grep -q '2/2.*Running'"

echo ""
echo "4. Dapr Components"
echo "-----------------"
check "kafka-pubsub component" "kubectl get component kafka-pubsub -n $NAMESPACE"
check "statestore component" "kubectl get component statestore -n $NAMESPACE"
check "scheduler component" "kubectl get component scheduler -n $NAMESPACE"
check "kubernetes-secrets component" "kubectl get component kubernetes-secrets -n $NAMESPACE"

echo ""
echo "5. Kubernetes Secrets"
echo "--------------------"
check "app-secrets exists" "kubectl get secret app-secrets -n $NAMESPACE"
check "kafka-secrets exists" "kubectl get secret kafka-secrets -n $NAMESPACE"

echo ""
echo "6. Services"
echo "----------"
check "Frontend service" "kubectl get svc -n $NAMESPACE | grep -q frontend"
check "Backend service" "kubectl get svc -n $NAMESPACE | grep -q backend"

echo ""
echo "7. Ingress"
echo "---------"
check "Ingress exists" "kubectl get ingress -n $NAMESPACE | grep -q todo-app"

INGRESS_IP=$(kubectl get ingress todo-app-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")

if [ -n "$INGRESS_IP" ] && [ "$INGRESS_IP" != "null" ]; then
    echo -e "${GREEN}✓ Ingress IP assigned: $INGRESS_IP${NC}"

    echo ""
    echo "8. Application Health"
    echo "--------------------"

    # Test frontend
    if curl -f -s -o /dev/null -w "%{http_code}" http://${INGRESS_IP}/ | grep -q "200"; then
        echo -e "${GREEN}✓ Frontend accessible${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend not yet accessible${NC}"
        ERRORS=$((ERRORS + 1))
    fi

    # Test backend health
    if curl -f -s -o /dev/null -w "%{http_code}" http://${INGRESS_IP}/api/health | grep -q "200"; then
        echo -e "${GREEN}✓ Backend health endpoint responding${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend health endpoint not yet accessible${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠️  Ingress IP not yet assigned (this may take a few minutes)${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "9. Pod Logs Check"
echo "----------------"

# Check for errors in backend logs
BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l app=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -n "$BACKEND_POD" ]; then
    ERROR_COUNT=$(kubectl logs $BACKEND_POD -c backend -n $NAMESPACE --tail=100 2>/dev/null | grep -i error | wc -l || echo "0")

    if [ "$ERROR_COUNT" -eq 0 ]; then
        echo -e "${GREEN}✓ No errors in backend logs${NC}"
    else
        echo -e "${YELLOW}⚠️  Found $ERROR_COUNT error(s) in backend logs${NC}"
        echo "   Run: kubectl logs $BACKEND_POD -c backend -n $NAMESPACE | grep -i error"
    fi
else
    echo -e "${YELLOW}⚠️  Backend pod not found${NC}"
fi

echo ""
echo "============================================="

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Deployment is healthy.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  $ERRORS check(s) failed. Review the output above.${NC}"
    echo ""
    echo "Troubleshooting commands:"
    echo "  kubectl get pods -n $NAMESPACE"
    echo "  kubectl describe pod <pod-name> -n $NAMESPACE"
    echo "  kubectl logs <pod-name> -c backend -n $NAMESPACE"
    echo "  kubectl logs <pod-name> -c daprd -n $NAMESPACE"
    echo "  kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'"
    exit 1
fi
