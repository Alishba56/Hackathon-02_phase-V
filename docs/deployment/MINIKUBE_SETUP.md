# Minikube Setup Guide

**Feature**: Cloud-Native Todo AI Chatbot Kubernetes Deployment
**Purpose**: Step-by-step guide for setting up Minikube for local Kubernetes development

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Prerequisites Installation](#prerequisites-installation)
4. [Minikube Installation](#minikube-installation)
5. [Minikube Configuration](#minikube-configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)

---

## Overview

Minikube is a tool that runs a single-node Kubernetes cluster locally. It's perfect for:
- Local development and testing
- Learning Kubernetes
- CI/CD pipelines
- Prototyping applications

This guide will help you set up Minikube for deploying the Todo AI Chatbot.

---

## System Requirements

### Minimum Requirements

- **CPU**: 4 cores (2 cores minimum, 4+ recommended)
- **Memory**: 8GB RAM (4GB minimum, 8GB+ recommended)
- **Disk Space**: 20GB free space
- **Virtualization**: Must be enabled in BIOS/UEFI

### Supported Operating Systems

- **Linux**: Ubuntu 20.04+, Debian 10+, Fedora 35+, CentOS 8+
- **macOS**: 10.13+ (High Sierra or later)
- **Windows**: Windows 10/11 (with WSL2 or Hyper-V)

### Check Virtualization Support

**Linux**:
```bash
# Check if virtualization is enabled
grep -E --color 'vmx|svm' /proc/cpuinfo

# If output is empty, virtualization is not enabled
# Enable it in BIOS/UEFI settings
```

**macOS**:
```bash
# Virtualization is enabled by default on macOS
sysctl -a | grep machdep.cpu.features | grep VMX
```

**Windows**:
```powershell
# Check if Hyper-V is enabled
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All

# Or check virtualization in Task Manager:
# Performance tab → CPU → Virtualization: Enabled
```

---

## Prerequisites Installation

### 1. Install Docker

Minikube can use Docker as a driver (recommended for most users).

**Linux (Ubuntu/Debian)**:
```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
```

**macOS**:
```bash
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Or use Homebrew
brew install --cask docker

# Start Docker Desktop from Applications
# Verify installation
docker --version
```

**Windows**:
```powershell
# Download Docker Desktop for Windows
# https://www.docker.com/products/docker-desktop

# Install and restart computer
# Verify installation
docker --version
```

### 2. Install kubectl

kubectl is the Kubernetes command-line tool.

**Linux**:
```bash
# Download latest release
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Make executable
chmod +x kubectl

# Move to PATH
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client
```

**macOS**:
```bash
# Using Homebrew
brew install kubectl

# Or download binary
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client
```

**Windows**:
```powershell
# Using Chocolatey
choco install kubernetes-cli

# Or download binary
curl.exe -LO "https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe"

# Add to PATH and verify
kubectl version --client
```

### 3. Install Helm

Helm is the Kubernetes package manager.

**Linux**:
```bash
# Download installation script
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installation
helm version
```

**macOS**:
```bash
# Using Homebrew
brew install helm

# Verify installation
helm version
```

**Windows**:
```powershell
# Using Chocolatey
choco install kubernetes-helm

# Or using Scoop
scoop install helm

# Verify installation
helm version
```

---

## Minikube Installation

### Linux

```bash
# Download Minikube binary
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Install Minikube
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify installation
minikube version
```

### macOS

```bash
# Using Homebrew
brew install minikube

# Or download binary
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
sudo install minikube-darwin-amd64 /usr/local/bin/minikube

# Verify installation
minikube version
```

### Windows

```powershell
# Using Chocolatey
choco install minikube

# Or using Windows Package Manager
winget install Kubernetes.minikube

# Or download installer
# https://storage.googleapis.com/minikube/releases/latest/minikube-installer.exe

# Verify installation
minikube version
```

---

## Minikube Configuration

### Automated Setup (Recommended)

Use the provided setup scripts for quick configuration:

**Linux/macOS**:
```bash
# Navigate to project root
cd /path/to/phase04

# Run setup script
./infra/k8s/minikube/setup.sh
```

**Windows PowerShell**:
```powershell
# Navigate to project root
cd C:\path\to\phase04

# Run setup script
.\infra\k8s\minikube\setup.ps1
```

### Manual Setup

If you prefer manual configuration:

#### Step 1: Start Minikube

```bash
# Start with recommended configuration
minikube start \
  --cpus=4 \
  --memory=8192 \
  --driver=docker \
  --kubernetes-version=stable

# Wait for cluster to start (may take 2-5 minutes)
```

**Driver Options**:
- `docker` (recommended): Uses Docker as container runtime
- `hyperkit` (macOS): Native macOS hypervisor
- `hyperv` (Windows): Windows Hyper-V
- `virtualbox`: VirtualBox (cross-platform)
- `kvm2` (Linux): KVM virtualization

#### Step 2: Enable Required Addons

```bash
# Enable ingress controller
minikube addons enable ingress

# Enable metrics server (for kubectl top)
minikube addons enable metrics-server

# Verify addons
minikube addons list
```

#### Step 3: Configure kubectl Context

```bash
# Set kubectl context to minikube
kubectl config use-context minikube

# Verify context
kubectl config current-context

# Should output: minikube
```

#### Step 4: Configure Host File

Add `todo.local` to your hosts file:

**Linux/macOS**:
```bash
# Add entry to /etc/hosts
echo "127.0.0.1 todo.local" | sudo tee -a /etc/hosts

# Verify
cat /etc/hosts | grep todo.local
```

**Windows**:
```powershell
# Run PowerShell as Administrator
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "127.0.0.1 todo.local"

# Verify
Get-Content C:\Windows\System32\drivers\etc\hosts | Select-String "todo.local"
```

#### Step 5: Start Minikube Tunnel (Required for Ingress)

```bash
# Start tunnel in separate terminal (keep running)
minikube tunnel

# This command requires sudo/admin privileges
# Keep this terminal open while using the application
```

---

## Verification

### Check Minikube Status

```bash
# Check cluster status
minikube status

# Expected output:
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured
```

### Check Kubernetes Cluster

```bash
# Check nodes
kubectl get nodes

# Expected output:
# NAME       STATUS   ROLES           AGE   VERSION
# minikube   Ready    control-plane   5m    v1.28.x

# Check system pods
kubectl get pods -n kube-system

# All pods should be Running
```

### Check Addons

```bash
# List enabled addons
minikube addons list | grep enabled

# Should show:
# ✅ ingress
# ✅ metrics-server
```

### Check Docker Integration

```bash
# Point Docker CLI to Minikube's Docker daemon (optional)
eval $(minikube docker-env)

# List images in Minikube
minikube image ls

# Reset Docker CLI to host
eval $(minikube docker-env -u)
```

### Verification Checklist

- [ ] Minikube status shows "Running"
- [ ] kubectl can connect to cluster
- [ ] Ingress addon is enabled
- [ ] Metrics-server addon is enabled
- [ ] Host file includes todo.local entry
- [ ] Minikube tunnel is running (if needed)

---

## Troubleshooting

### Issue 1: Minikube Won't Start

**Symptoms**:
- `minikube start` fails
- Error: "Exiting due to PROVIDER_DOCKER_NOT_RUNNING"

**Solutions**:

1. **Ensure Docker is running**:
   ```bash
   docker ps
   # If error, start Docker Desktop
   ```

2. **Delete and recreate cluster**:
   ```bash
   minikube delete
   minikube start --cpus=4 --memory=8192 --driver=docker
   ```

3. **Try different driver**:
   ```bash
   minikube start --driver=virtualbox
   # or
   minikube start --driver=hyperkit  # macOS
   ```

### Issue 2: Insufficient Resources

**Symptoms**:
- Pods stuck in Pending state
- Error: "Insufficient cpu/memory"

**Solutions**:

1. **Increase Minikube resources**:
   ```bash
   minikube stop
   minikube delete
   minikube start --cpus=6 --memory=12288
   ```

2. **Check available resources**:
   ```bash
   # Check node capacity
   kubectl describe node minikube | grep -A 10 "Allocated resources"
   ```

### Issue 3: Ingress Not Working

**Symptoms**:
- Cannot access http://todo.local
- 404 or connection refused errors

**Solutions**:

1. **Verify ingress addon**:
   ```bash
   minikube addons enable ingress
   kubectl get pods -n ingress-nginx
   ```

2. **Start Minikube tunnel**:
   ```bash
   minikube tunnel
   # Keep running in separate terminal
   ```

3. **Check host file**:
   ```bash
   cat /etc/hosts | grep todo.local
   # Should show: 127.0.0.1 todo.local
   ```

### Issue 4: Slow Performance

**Symptoms**:
- Slow pod startup
- High CPU usage
- Sluggish kubectl commands

**Solutions**:

1. **Allocate more resources**:
   ```bash
   minikube stop
   minikube start --cpus=6 --memory=12288
   ```

2. **Use faster driver**:
   ```bash
   # macOS: use hyperkit instead of docker
   minikube start --driver=hyperkit
   ```

3. **Disable unnecessary addons**:
   ```bash
   minikube addons list
   minikube addons disable <addon-name>
   ```

### Issue 5: Image Pull Errors

**Symptoms**:
- Pods stuck in ImagePullBackOff
- Error: "Failed to pull image"

**Solutions**:

1. **Load images into Minikube**:
   ```bash
   # Build images first
   docker build -t todo-frontend:latest -f infra/docker/frontend/Dockerfile frontend/
   docker build -t todo-backend:latest -f infra/docker/backend/Dockerfile backend/

   # Load into Minikube
   minikube image load todo-frontend:latest
   minikube image load todo-backend:latest

   # Verify
   minikube image ls | grep todo
   ```

2. **Set imagePullPolicy**:
   ```yaml
   # In Helm values.yaml
   image:
     pullPolicy: IfNotPresent  # or Never for local images
   ```

---

## Advanced Configuration

### Custom Resource Allocation

```bash
# Start with custom resources
minikube start \
  --cpus=6 \
  --memory=12288 \
  --disk-size=40g \
  --driver=docker
```

### Multiple Profiles

```bash
# Create development profile
minikube start -p dev --cpus=2 --memory=4096

# Create production-like profile
minikube start -p prod --cpus=6 --memory=12288

# Switch between profiles
minikube profile dev
minikube profile prod

# List profiles
minikube profile list
```

### Enable Additional Addons

```bash
# Dashboard
minikube addons enable dashboard
minikube dashboard

# Registry
minikube addons enable registry

# Storage provisioner
minikube addons enable storage-provisioner

# List all available addons
minikube addons list
```

### Configure Docker Environment

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Now docker commands use Minikube's Docker
docker ps

# Build images directly in Minikube
docker build -t myapp:latest .

# Reset to host Docker
eval $(minikube docker-env -u)
```

### Persistent Configuration

```bash
# Set default configuration
minikube config set cpus 4
minikube config set memory 8192
minikube config set driver docker

# View configuration
minikube config view

# These settings apply to future minikube start commands
```

### SSH into Minikube

```bash
# SSH into Minikube node
minikube ssh

# Run commands inside node
docker ps
exit
```

### Access Services

```bash
# Get service URL
minikube service todo-app-frontend --url

# Open service in browser
minikube service todo-app-frontend

# List all service URLs
minikube service list
```

---

## Cleanup

### Stop Minikube

```bash
# Stop cluster (preserves state)
minikube stop
```

### Delete Cluster

```bash
# Delete cluster (removes all data)
minikube delete

# Delete specific profile
minikube delete -p dev
```

### Complete Cleanup

```bash
# Delete all profiles and data
minikube delete --all --purge

# Remove Minikube configuration
rm -rf ~/.minikube
```

---

## Next Steps

After setting up Minikube:

1. **Build Docker Images**:
   ```bash
   ./infra/scripts/build-images.sh
   ```

2. **Load Images into Minikube**:
   ```bash
   ./infra/scripts/load-images.sh
   ```

3. **Deploy Application**:
   ```bash
   ./infra/scripts/deploy.sh
   ```

4. **Access Application**:
   - Open browser: http://todo.local

For detailed deployment instructions, see:
- `specs/001-k8s-deployment/quickstart.md`
- `infra/README.md`

For troubleshooting, see:
- `docs/deployment/TROUBLESHOOTING.md`

---

## Additional Resources

- **Minikube Documentation**: https://minikube.sigs.k8s.io/docs/
- **Minikube GitHub**: https://github.com/kubernetes/minikube
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **kubectl Cheat Sheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/

---

## Summary

This guide covered:

✅ System requirements and prerequisites
✅ Installing Docker, kubectl, Helm, and Minikube
✅ Configuring Minikube for the Todo AI Chatbot
✅ Verification procedures
✅ Common troubleshooting scenarios
✅ Advanced configuration options

Your Minikube cluster is now ready for deploying the Todo AI Chatbot!
