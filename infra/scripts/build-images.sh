#!/bin/bash

# Docker Image Build Script for Todo AI Chatbot
# This script builds both frontend and backend Docker images

set -e  # Exit on error

echo "=========================================="
echo "Todo AI Chatbot - Build Docker Images"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Error: Docker daemon is not running"
    echo "Please start Docker Desktop or Docker daemon"
    exit 1
fi

echo "✅ Docker is available"
echo ""

# Build frontend image
echo "🔨 Building frontend image..."
echo "   Image: todo-frontend:latest"
echo "   Context: frontend/"
echo "   Dockerfile: infra/docker/frontend/Dockerfile"
echo ""

docker build \
    -t todo-frontend:latest \
    -f infra/docker/frontend/Dockerfile \
    frontend/

if [ $? -ne 0 ]; then
    echo "❌ Failed to build frontend image"
    exit 1
fi

echo ""
echo "✅ Frontend image built successfully"
echo ""

# Build backend image
echo "🔨 Building backend image..."
echo "   Image: todo-backend:latest"
echo "   Context: backend/"
echo "   Dockerfile: infra/docker/backend/Dockerfile"
echo ""

docker build \
    -t todo-backend:latest \
    -f infra/docker/backend/Dockerfile \
    backend/

if [ $? -ne 0 ]; then
    echo "❌ Failed to build backend image"
    exit 1
fi

echo ""
echo "✅ Backend image built successfully"
echo ""

# Display image information
echo "=========================================="
echo "✅ Build Complete!"
echo "=========================================="
echo ""
echo "📦 Built Images:"
docker images | grep -E "REPOSITORY|todo-frontend|todo-backend"

echo ""
echo "📊 Image Sizes:"
echo "   Frontend: $(docker images todo-frontend:latest --format '{{.Size}}')"
echo "   Backend: $(docker images todo-backend:latest --format '{{.Size}}')"

echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Test images locally (optional):"
echo "   docker run -p 3000:3000 todo-frontend:latest"
echo "   docker run -p 8000:8000 -e DATABASE_URL=... todo-backend:latest"
echo ""
echo "2. Load images into Minikube:"
echo "   ./infra/scripts/load-images.sh"
echo ""
echo "3. Deploy with Helm:"
echo "   ./infra/scripts/deploy.sh"
echo ""
