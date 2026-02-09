# CI/CD Pipeline Design

**Date**: 2026-02-09
**Feature**: Oracle OKE Dapr Infrastructure Integration
**Branch**: `001-oke-dapr-infrastructure`

## Overview

This document describes the GitHub Actions CI/CD pipeline for automated testing, building, and deployment of the Todo AI Chatbot application to Oracle OKE.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Repository                            │
│                  (Push to main branch)                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  GitHub Actions Workflow                         │
│                  (.github/workflows/deploy-oke.yml)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Stage 1: Test                                           │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │ • Checkout code                                         │    │
│  │ • Set up Python 3.11                                    │    │
│  │ • Install backend dependencies                          │    │
│  │ • Run pytest (unit + integration tests)                │    │
│  │ • Run linting (flake8, black)                          │    │
│  │ Duration: ~2 minutes                                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                         │                                        │
│                         │ (on success)                           │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Stage 2: Build                                          │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │ • Set up Docker Buildx                                  │    │
│  │ • Build frontend image (multi-stage)                   │    │
│  │ • Build backend image (multi-stage)                    │    │
│  │ • Tag images with commit SHA                           │    │
│  │ Duration: ~3 minutes                                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                         │                                        │
│                         │ (on success)                           │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Stage 3: Push                                           │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │ • Login to GitHub Container Registry (ghcr.io)         │    │
│  │ • Push frontend image                                   │    │
│  │ • Push backend image                                    │    │
│  │ • Tag as 'latest' for main branch                      │    │
│  │ Duration: ~1 minute                                     │    │
│  └────────────────────────────────────────────────────────┘    │
│                         │                                        │
│                         │ (on success)                           │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Stage 4: Deploy                                         │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │ • Configure kubectl with OKE kubeconfig                │    │
│  │ • Verify cluster connectivity                          │    │
│  │ • Helm upgrade --install todo-app                      │    │
│  │ • Wait for rollout completion                          │    │
│  │ • Run smoke tests                                       │    │
│  │ Duration: ~2 minutes                                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Stage 5: Verify                                         │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │ • Check pod status (all Running)                       │    │
│  │ • Verify Dapr sidecars healthy                         │    │
│  │ • Test application endpoints                           │    │
│  │ • Notify on success/failure                            │    │
│  │ Duration: ~1 minute                                     │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Oracle OKE Cluster                            │
│              (Application deployed and running)                  │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow File

### File Location
`.github/workflows/deploy-oke.yml`

### Full Workflow Specification

```yaml
name: Deploy to Oracle OKE

on:
  push:
    branches:
      - main
      - 001-oke-dapr-infrastructure
  pull_request:
    branches:
      - main
  workflow_dispatch:  # Allow manual trigger

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: ${{ github.repository_owner }}

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install backend dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run linting
        run: |
          cd backend
          pip install flake8 black
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          black --check .

      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --tb=short
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          COHERE_API_KEY: ${{ secrets.COHERE_API_KEY }}
          BETTER_AUTH_SECRET: ${{ secrets.BETTER_AUTH_SECRET }}

  build:
    name: Build Docker Images
    runs-on: ubuntu-latest
    needs: test

    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Generate image metadata
        id: meta
        run: |
          SHORT_SHA=$(echo ${{ github.sha }} | cut -c1-7)
          echo "tags=sha-${SHORT_SHA}" >> $GITHUB_OUTPUT
          echo "date=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" >> $GITHUB_OUTPUT

      - name: Build frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          file: ./frontend/Dockerfile
          push: false
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/todo-frontend:${{ steps.meta.outputs.tags }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/todo-frontend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
          outputs: type=docker,dest=/tmp/frontend-image.tar

      - name: Build backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          file: ./backend/Dockerfile
          push: false
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/todo-backend:${{ steps.meta.outputs.tags }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/todo-backend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
          outputs: type=docker,dest=/tmp/backend-image.tar

      - name: Upload frontend image artifact
        uses: actions/upload-artifact@v4
        with:
          name: frontend-image
          path: /tmp/frontend-image.tar
          retention-days: 1

      - name: Upload backend image artifact
        uses: actions/upload-artifact@v4
        with:
          name: backend-image
          path: /tmp/backend-image.tar
          retention-days: 1

  push:
    name: Push Images to Registry
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - name: Download frontend image
        uses: actions/download-artifact@v4
        with:
          name: frontend-image
          path: /tmp

      - name: Download backend image
        uses: actions/download-artifact@v4
        with:
          name: backend-image
          path: /tmp

      - name: Load Docker images
        run: |
          docker load --input /tmp/frontend-image.tar
          docker load --input /tmp/backend-image.tar

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Push images
        run: |
          docker push --all-tags ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/todo-frontend
          docker push --all-tags ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/todo-backend

  deploy:
    name: Deploy to OKE
    runs-on: ubuntu-latest
    needs: [build, push]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'v1.28.0'

      - name: Set up Helm
        uses: azure/setup-helm@v3
        with:
          version: 'v3.13.0'

      - name: Configure kubectl
        run: |
          mkdir -p $HOME/.kube
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > $HOME/.kube/config
          chmod 600 $HOME/.kube/config

      - name: Verify cluster connectivity
        run: |
          kubectl cluster-info
          kubectl get nodes

      - name: Create/Update Kubernetes Secrets
        run: |
          kubectl create secret generic app-secrets \
            --from-literal=cohere-api-key=${{ secrets.COHERE_API_KEY }} \
            --from-literal=better-auth-secret=${{ secrets.BETTER_AUTH_SECRET }} \
            --from-literal=database-url=${{ secrets.DATABASE_URL }} \
            --dry-run=client -o yaml | kubectl apply -f -

          kubectl create secret generic kafka-secrets \
            --from-literal=username=${{ secrets.KAFKA_USERNAME }} \
            --from-literal=password=${{ secrets.KAFKA_PASSWORD }} \
            --dry-run=client -o yaml | kubectl apply -f -

      - name: Deploy with Helm
        run: |
          SHORT_SHA=$(echo ${{ github.sha }} | cut -c1-7)

          helm upgrade --install todo-app ./infra/helm/todo-app \
            --values ./infra/helm/todo-app/values-oke.yaml \
            --set frontend.image.repository=${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/todo-frontend \
            --set frontend.image.tag=sha-${SHORT_SHA} \
            --set backend.image.repository=${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/todo-backend \
            --set backend.image.tag=sha-${SHORT_SHA} \
            --wait \
            --timeout 5m \
            --atomic

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/frontend --timeout=3m
          kubectl rollout status deployment/backend --timeout=3m

      - name: Check pod status
        run: |
          kubectl get pods -l app=frontend
          kubectl get pods -l app=backend
          kubectl get components

      - name: Run smoke tests
        run: |
          # Wait for ingress to be ready
          sleep 30

          # Get ingress URL
          INGRESS_URL=$(kubectl get ingress todo-app-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

          # Test frontend
          curl -f http://${INGRESS_URL}/ || exit 1

          # Test backend health
          curl -f http://${INGRESS_URL}/api/health || exit 1

          echo "✅ Smoke tests passed!"

  notify:
    name: Notify Deployment Status
    runs-on: ubuntu-latest
    needs: [deploy]
    if: always()

    steps:
      - name: Notify success
        if: needs.deploy.result == 'success'
        run: |
          echo "✅ Deployment to OKE successful!"
          echo "Commit: ${{ github.sha }}"
          echo "Branch: ${{ github.ref }}"

      - name: Notify failure
        if: needs.deploy.result == 'failure'
        run: |
          echo "❌ Deployment to OKE failed!"
          echo "Commit: ${{ github.sha }}"
          echo "Branch: ${{ github.ref }}"
          exit 1
```

## GitHub Secrets Configuration

### Required Secrets

Configure the following secrets in GitHub repository settings (Settings → Secrets and variables → Actions):

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `KUBECONFIG` | Base64-encoded kubeconfig for OKE | `apiVersion: v1...` (base64) |
| `COHERE_API_KEY` | Cohere API key | `co_abc123...` |
| `BETTER_AUTH_SECRET` | JWT secret for Better Auth | `random-secret-string` |
| `DATABASE_URL` | Neon PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `KAFKA_USERNAME` | Redpanda SASL username | `redpanda-user` |
| `KAFKA_PASSWORD` | Redpanda SASL password | `redpanda-pass` |

### Creating Secrets

```bash
# Generate kubeconfig for OKE
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file kubeconfig.yaml \
  --region <region> \
  --token-version 2.0.0

# Base64 encode kubeconfig
cat kubeconfig.yaml | base64 -w 0 > kubeconfig.base64

# Add to GitHub Secrets (via UI or gh CLI)
gh secret set KUBECONFIG < kubeconfig.base64
gh secret set COHERE_API_KEY --body "$COHERE_API_KEY"
gh secret set BETTER_AUTH_SECRET --body "$BETTER_AUTH_SECRET"
gh secret set DATABASE_URL --body "$DATABASE_URL"
gh secret set KAFKA_USERNAME --body "$KAFKA_USERNAME"
gh secret set KAFKA_PASSWORD --body "$KAFKA_PASSWORD"
```

## Pipeline Stages Detailed

### Stage 1: Test (Duration: ~2 minutes)

**Purpose**: Validate code quality and functionality before building images.

**Steps**:
1. Checkout code from repository
2. Set up Python 3.11 with pip caching
3. Install backend dependencies
4. Run linting (flake8, black)
5. Run pytest with coverage

**Success Criteria**:
- All tests pass
- No linting errors
- Code coverage > 80% (optional)

**Failure Handling**:
- Pipeline stops immediately
- No images built or deployed
- Developer notified via GitHub UI

### Stage 2: Build (Duration: ~3 minutes)

**Purpose**: Build Docker images for frontend and backend with multi-stage optimization.

**Steps**:
1. Set up Docker Buildx for advanced features
2. Generate image metadata (tags, labels)
3. Build frontend image with layer caching
4. Build backend image with layer caching
5. Save images as artifacts for next stage

**Image Tagging Strategy**:
- `sha-<commit-sha>`: Unique tag for this commit
- `latest`: Latest successful build on main branch

**Optimization**:
- GitHub Actions cache for Docker layers
- Multi-stage builds to minimize image size
- Parallel builds for frontend and backend

### Stage 3: Push (Duration: ~1 minute)

**Purpose**: Push built images to GitHub Container Registry.

**Steps**:
1. Download image artifacts from build stage
2. Load images into Docker
3. Login to ghcr.io with GITHUB_TOKEN
4. Push images with all tags

**Registry Configuration**:
- Registry: `ghcr.io`
- Repository: `ghcr.io/<username>/todo-frontend`, `ghcr.io/<username>/todo-backend`
- Visibility: Private (can be made public)

### Stage 4: Deploy (Duration: ~2 minutes)

**Purpose**: Deploy application to Oracle OKE using Helm.

**Steps**:
1. Configure kubectl with OKE kubeconfig
2. Verify cluster connectivity
3. Create/update Kubernetes Secrets
4. Run Helm upgrade with new image tags
5. Wait for rollout completion (--atomic flag)

**Helm Configuration**:
- Release name: `todo-app`
- Namespace: `default`
- Values file: `values-oke.yaml`
- Timeout: 5 minutes
- Atomic: Rollback on failure

### Stage 5: Verify (Duration: ~1 minute)

**Purpose**: Validate deployment success with smoke tests.

**Steps**:
1. Check pod status (all Running)
2. Verify Dapr sidecars healthy
3. Test frontend endpoint
4. Test backend health endpoint
5. Notify deployment status

**Smoke Tests**:
- Frontend accessible: `curl http://<ingress-ip>/`
- Backend health: `curl http://<ingress-ip>/api/health`
- Pods running: `kubectl get pods`
- Dapr components ready: `kubectl get components`

## Rollback Procedures

### Automatic Rollback

Helm's `--atomic` flag automatically rolls back on deployment failure:
```yaml
helm upgrade --install todo-app ./infra/helm/todo-app --atomic
```

### Manual Rollback

```bash
# List release history
helm history todo-app

# Rollback to previous version
helm rollback todo-app

# Rollback to specific revision
helm rollback todo-app <revision-number>
```

### Rollback via GitHub Actions

Trigger workflow with previous commit SHA:
```bash
# Manually trigger workflow with specific commit
gh workflow run deploy-oke.yml --ref main
```

## Monitoring and Notifications

### Pipeline Monitoring

**GitHub Actions UI**:
- View workflow runs: Repository → Actions tab
- Real-time logs for each step
- Artifacts download (Docker images)

**Status Badges**:
```markdown
![Deploy to OKE](https://github.com/<user>/<repo>/actions/workflows/deploy-oke.yml/badge.svg)
```

### Notifications

**Built-in GitHub Notifications**:
- Email on workflow failure
- GitHub UI notifications
- Mobile app notifications

**Optional: Slack/Discord Integration**:
```yaml
- name: Notify Slack
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Deployment ${{ job.status }}: ${{ github.sha }}"
      }
```

## Performance Optimization

### Build Time Optimization

1. **Docker Layer Caching**:
   ```yaml
   cache-from: type=gha
   cache-to: type=gha,mode=max
   ```

2. **Dependency Caching**:
   ```yaml
   - uses: actions/setup-python@v5
     with:
       cache: 'pip'
   ```

3. **Parallel Jobs**:
   - Test and build can run in parallel (if tests are fast)
   - Frontend and backend builds are independent

### Cost Optimization

**GitHub Actions Free Tier**:
- 2000 minutes/month for private repos
- Unlimited for public repos

**Estimated Usage**:
- Per deployment: ~9 minutes
- Monthly deployments (20): ~180 minutes
- Well within free tier limits

## Security Best Practices

### Secret Management

1. **Never commit secrets to repository**
2. **Use GitHub Secrets for sensitive data**
3. **Rotate secrets regularly**
4. **Use least-privilege access for kubeconfig**

### Image Security

1. **Scan images for vulnerabilities**:
   ```yaml
   - name: Scan image
     uses: aquasecurity/trivy-action@master
     with:
       image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/todo-backend:latest
   ```

2. **Sign images** (optional):
   ```yaml
   - name: Sign image
     uses: sigstore/cosign-installer@main
   ```

### Cluster Access

1. **Use token-based kubeconfig** (auto-refresh)
2. **Limit kubeconfig permissions** (deploy namespace only)
3. **Enable audit logging** in OKE

## Troubleshooting

### Common Issues

**Issue 1: Test Stage Fails**
```
Error: pytest failed with exit code 1
```
**Solution**:
- Check test logs in GitHub Actions UI
- Run tests locally: `cd backend && pytest tests/ -v`
- Verify environment variables are set correctly

**Issue 2: Build Stage Fails**
```
Error: failed to solve: failed to compute cache key
```
**Solution**:
- Check Dockerfile syntax
- Verify all COPY paths exist
- Clear GitHub Actions cache

**Issue 3: Push Stage Fails**
```
Error: denied: permission_denied
```
**Solution**:
- Verify GITHUB_TOKEN has write permissions
- Check repository settings → Actions → General → Workflow permissions
- Enable "Read and write permissions"

**Issue 4: Deploy Stage Fails**
```
Error: Kubernetes cluster unreachable
```
**Solution**:
- Verify KUBECONFIG secret is correctly base64-encoded
- Check OKE cluster is running: `oci ce cluster get --cluster-id <id>`
- Verify network connectivity from GitHub Actions to OKE

**Issue 5: Helm Upgrade Fails**
```
Error: timed out waiting for the condition
```
**Solution**:
- Check pod logs: `kubectl logs <pod-name>`
- Verify image pull secrets
- Check resource limits (OKE free tier constraints)
- Increase timeout: `--timeout 10m`

### Debug Mode

Enable debug logging:
```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

---

**CI/CD Pipeline Design Status**: ✅ Complete - Ready for Implementation
**Next Steps**: Create monitoring strategy and quickstart guide
