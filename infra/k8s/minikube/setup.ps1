# Minikube Setup Script for Todo AI Chatbot Kubernetes Deployment (Windows)
# This script initializes a local Minikube cluster with required addons

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Todo AI Chatbot - Minikube Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Minikube is installed
if (-not (Get-Command minikube -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Minikube is not installed" -ForegroundColor Red
    Write-Host "Please install Minikube: https://minikube.sigs.k8s.io/docs/start/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Docker is not installed" -ForegroundColor Red
    Write-Host "Please install Docker Desktop: https://docs.docker.com/get-docker/" -ForegroundColor Yellow
    exit 1
}

# Check if kubectl is installed
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: kubectl is not installed" -ForegroundColor Red
    Write-Host "Please install kubectl: https://kubernetes.io/docs/tasks/tools/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green
Write-Host ""

# Start Minikube with recommended configuration
Write-Host "🚀 Starting Minikube cluster..." -ForegroundColor Cyan
Write-Host "   Configuration: 4 CPUs, 8GB RAM, Docker driver" -ForegroundColor Gray
Write-Host ""

minikube start `
    --cpus=4 `
    --memory=8192 `
    --driver=docker `
    --kubernetes-version=v1.28.0

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start Minikube cluster" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Minikube cluster started successfully" -ForegroundColor Green
Write-Host ""

# Enable ingress addon
Write-Host "🔧 Enabling ingress addon..." -ForegroundColor Cyan
minikube addons enable ingress

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Warning: Failed to enable ingress addon" -ForegroundColor Yellow
} else {
    Write-Host "✅ Ingress addon enabled" -ForegroundColor Green
}

Write-Host ""

# Enable metrics-server addon
Write-Host "🔧 Enabling metrics-server addon..." -ForegroundColor Cyan
minikube addons enable metrics-server

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Warning: Failed to enable metrics-server addon" -ForegroundColor Yellow
} else {
    Write-Host "✅ Metrics-server addon enabled" -ForegroundColor Green
}

Write-Host ""

# Wait for ingress controller to be ready
Write-Host "⏳ Waiting for ingress controller to be ready..." -ForegroundColor Cyan
kubectl wait --namespace ingress-nginx `
    --for=condition=ready pod `
    --selector=app.kubernetes.io/component=controller `
    --timeout=120s 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Ingress controller may still be starting" -ForegroundColor Yellow
}

Write-Host ""

# Verify cluster is ready
Write-Host "🔍 Verifying cluster status..." -ForegroundColor Cyan
kubectl cluster-info

Write-Host ""
kubectl get nodes

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Minikube Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Configure host file mapping (requires Administrator):" -ForegroundColor White
Write-Host "   Add this line to C:\Windows\System32\drivers\etc\hosts:" -ForegroundColor Gray
Write-Host "   127.0.0.1 todo.local" -ForegroundColor Gray
Write-Host ""
Write-Host "   PowerShell command (run as Administrator):" -ForegroundColor White
Write-Host "   Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value '127.0.0.1 todo.local'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Build and load Docker images:" -ForegroundColor White
Write-Host "   .\infra\scripts\build-images.sh" -ForegroundColor Gray
Write-Host "   .\infra\scripts\load-images.sh" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Deploy application with Helm:" -ForegroundColor White
Write-Host "   .\infra\scripts\deploy.sh" -ForegroundColor Gray
Write-Host ""
Write-Host "📊 Cluster Information:" -ForegroundColor Yellow
Write-Host "   Dashboard: minikube dashboard" -ForegroundColor Gray
$minikubeIp = minikube ip
Write-Host "   IP: $minikubeIp" -ForegroundColor Gray
Write-Host "   Status: minikube status" -ForegroundColor Gray
Write-Host ""
Write-Host "🛑 To stop the cluster: minikube stop" -ForegroundColor Yellow
Write-Host "🗑️  To delete the cluster: .\infra\k8s\minikube\teardown.sh" -ForegroundColor Yellow
Write-Host ""
