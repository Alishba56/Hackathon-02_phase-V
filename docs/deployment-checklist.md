# Oracle OKE Deployment Checklist

**Purpose**: Step-by-step checklist for deploying Todo AI Chatbot to Oracle OKE with Dapr runtime

**Last Updated**: 2026-02-09

---

## Pre-Deployment Checklist

### 1. Prerequisites Verification

- [ ] Oracle Cloud Infrastructure (OCI) account created
- [ ] OCI CLI installed and configured (`oci --version`)
- [ ] kubectl installed (`kubectl version --client`)
- [ ] Helm 3.13+ installed (`helm version`)
- [ ] Dapr CLI installed (`dapr version`)
- [ ] Docker installed (`docker --version`)
- [ ] Git repository cloned locally

### 2. Cloud Services Setup

- [ ] Redpanda Cloud account created
- [ ] Redpanda serverless cluster provisioned
- [ ] Kafka topics created:
  - [ ] `task-events` (3 partitions)
  - [ ] `task-updates` (3 partitions)
  - [ ] `reminders` (3 partitions)
- [ ] Redpanda SASL credentials generated
- [ ] Redpanda bootstrap URL saved
- [ ] Neon PostgreSQL database created
- [ ] Database connection string saved

### 3. Credentials Collection

- [ ] `COHERE_API_KEY` - Cohere API key
- [ ] `BETTER_AUTH_SECRET` - Authentication secret (generate with `openssl rand -hex 32`)
- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `KAFKA_USERNAME` - Redpanda SASL username
- [ ] `KAFKA_PASSWORD` - Redpanda SASL password
- [ ] `KAFKA_BOOTSTRAP_URL` - Redpanda bootstrap server URL

---

## Phase 1: OKE Cluster Provisioning

### 1. Create OKE Cluster

- [ ] Review `infra/oke/README.md` for detailed instructions
- [ ] Update `infra/oke/cluster-setup.sh` with your OCI compartment ID
- [ ] Run cluster provisioning script:
  ```bash
  cd infra/oke
  chmod +x cluster-setup.sh
  ./cluster-setup.sh
  ```
- [ ] Wait for cluster creation (~10-15 minutes)
- [ ] Verify cluster is running in OCI Console

### 2. Configure kubectl Access

- [ ] Generate kubeconfig:
  ```bash
  oci ce cluster create-kubeconfig \
    --cluster-id <cluster-ocid> \
    --file ~/.kube/config \
    --region <region> \
    --token-version 2.0.0
  ```
- [ ] Test cluster access:
  ```bash
  kubectl cluster-info
  kubectl get nodes
  ```
- [ ] Verify nodes are Ready

### 3. Install Dapr Runtime

- [ ] Run Dapr initialization script:
  ```bash
  cd infra/oke
  chmod +x dapr-init.sh
  ./dapr-init.sh
  ```
- [ ] Verify Dapr installation:
  ```bash
  dapr status -k
  kubectl get pods -n dapr-system
  ```
- [ ] Confirm all Dapr pods are Running (operator, sidecar-injector, sentry, placement)

---

## Phase 2: Configuration

### 1. Update Dapr Component Configuration

- [ ] Edit `infra/dapr-components/kafka-pubsub.yaml`
- [ ] Update `brokers` value with Redpanda bootstrap URL
- [ ] Verify SASL credentials reference correct secret name

### 2. Update Helm Values

- [ ] Edit `infra/helm/todo-app/values-oke.yaml`
- [ ] Update `frontend.image.repository` with your registry
- [ ] Update `backend.image.repository` with your registry
- [ ] Update `dapr.kafka.brokers` with Redpanda bootstrap URL
- [ ] Update `ingress.host` if using custom domain

### 3. Create Kubernetes Secrets

- [ ] Create application secrets:
  ```bash
  kubectl create secret generic app-secrets \
    --from-literal=cohere-api-key=$COHERE_API_KEY \
    --from-literal=better-auth-secret=$BETTER_AUTH_SECRET \
    --from-literal=database-url=$DATABASE_URL
  ```
- [ ] Create Kafka secrets:
  ```bash
  kubectl create secret generic kafka-secrets \
    --from-literal=username=$KAFKA_USERNAME \
    --from-literal=password=$KAFKA_PASSWORD
  ```
- [ ] Verify secrets created:
  ```bash
  kubectl get secrets
  ```

---

## Phase 3: Build and Push Docker Images

### 1. Build Docker Images

- [ ] Build frontend image:
  ```bash
  docker build -t <registry>/todo-frontend:latest ./frontend
  ```
- [ ] Build backend image:
  ```bash
  docker build -t <registry>/todo-backend:latest ./backend
  ```
- [ ] Test images locally (optional):
  ```bash
  docker run -p 3000:3000 <registry>/todo-frontend:latest
  docker run -p 8000:8000 <registry>/todo-backend:latest
  ```

### 2. Push Images to Registry

- [ ] Login to container registry:
  ```bash
  docker login ghcr.io
  ```
- [ ] Push frontend image:
  ```bash
  docker push <registry>/todo-frontend:latest
  ```
- [ ] Push backend image:
  ```bash
  docker push <registry>/todo-backend:latest
  ```
- [ ] Verify images in registry

---

## Phase 4: Deploy Application

### 1. Apply Dapr Components

- [ ] Apply all Dapr components:
  ```bash
  kubectl apply -f infra/dapr-components/
  ```
- [ ] Verify components created:
  ```bash
  kubectl get components
  ```
- [ ] Expected components: kafka-pubsub, statestore, scheduler, kubernetes-secrets

### 2. Deploy with Helm

- [ ] Run deployment script:
  ```bash
  chmod +x infra/scripts/deploy-oke.sh
  ./infra/scripts/deploy-oke.sh
  ```
  OR manually:
  ```bash
  helm upgrade --install todo-app ./infra/helm/todo-app \
    --values ./infra/helm/todo-app/values-oke.yaml \
    --wait \
    --timeout 5m
  ```
- [ ] Wait for deployment to complete

### 3. Verify Deployment

- [ ] Run verification script:
  ```bash
  chmod +x infra/scripts/verify-deployment.sh
  ./infra/scripts/verify-deployment.sh
  ```
- [ ] Check pod status (should show 2/2 Ready):
  ```bash
  kubectl get pods
  ```
- [ ] Check Dapr sidecars:
  ```bash
  kubectl logs <backend-pod> -c daprd
  ```

---

## Phase 5: Networking and Access

### 1. Install NGINX Ingress Controller

- [ ] Install NGINX Ingress:
  ```bash
  helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
  helm repo update
  helm install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx \
    --create-namespace
  ```
- [ ] Wait for load balancer IP assignment (~2-5 minutes)

### 2. Get Application URL

- [ ] Get ingress IP:
  ```bash
  kubectl get ingress todo-app-ingress
  ```
- [ ] Wait for EXTERNAL-IP to be assigned:
  ```bash
  kubectl get ingress todo-app-ingress -w
  ```
- [ ] Save the external IP address

### 3. Test Application Access

- [ ] Test frontend:
  ```bash
  curl http://<EXTERNAL-IP>/
  ```
- [ ] Test backend health:
  ```bash
  curl http://<EXTERNAL-IP>/api/health
  ```
- [ ] Open browser and navigate to `http://<EXTERNAL-IP>/`
- [ ] Verify frontend loads successfully
- [ ] Test user registration and login

---

## Phase 6: Event Publishing Verification

### 1. Test Task Creation

- [ ] Create a test task via UI or API
- [ ] Check backend logs for event publishing:
  ```bash
  kubectl logs -l app=backend -c backend | grep "Task created"
  ```
- [ ] Check Dapr sidecar logs:
  ```bash
  kubectl logs -l app=backend -c daprd | grep publish
  ```

### 2. Verify Events in Kafka

- [ ] Login to Redpanda Cloud dashboard
- [ ] Navigate to Topics → task-events
- [ ] Verify event message appears
- [ ] Check event payload contains correct data

### 3. Test All Event Types

- [ ] Create task → verify `task.created` event
- [ ] Update task → verify `task.updated` event
- [ ] Complete task → verify `task.completed` event
- [ ] Delete task → verify `task.deleted` event

---

## Phase 7: CI/CD Pipeline Setup

### 1. Prepare GitHub Repository

- [ ] Push code to GitHub repository
- [ ] Ensure `.github/workflows/deploy-oke.yml` is committed

### 2. Configure GitHub Secrets

- [ ] Generate base64-encoded kubeconfig:
  ```bash
  cat ~/.kube/config | base64 -w 0
  ```
- [ ] Add secrets to GitHub repository (Settings → Secrets and variables → Actions):
  - [ ] `KUBECONFIG` - Base64-encoded kubeconfig
  - [ ] `COHERE_API_KEY` - Cohere API key
  - [ ] `BETTER_AUTH_SECRET` - Authentication secret
  - [ ] `DATABASE_URL` - PostgreSQL connection string
  - [ ] `KAFKA_USERNAME` - Redpanda username
  - [ ] `KAFKA_PASSWORD` - Redpanda password

### 3. Test CI/CD Pipeline

- [ ] Make a small code change
- [ ] Commit and push to main branch
- [ ] Monitor GitHub Actions workflow execution
- [ ] Verify all stages pass (test, build, push, deploy, verify)
- [ ] Verify application updated with new changes

---

## Phase 8: Monitoring Setup

### 1. Deploy Dapr Dashboard

- [ ] Port-forward Dapr dashboard:
  ```bash
  kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080
  ```
- [ ] Access dashboard at `http://localhost:8080`
- [ ] Verify all components show as healthy
- [ ] Check sidecar metrics

### 2. Verify Logging

- [ ] Check frontend logs:
  ```bash
  kubectl logs -l app=frontend -c frontend --tail=50
  ```
- [ ] Check backend logs:
  ```bash
  kubectl logs -l app=backend -c backend --tail=50
  ```
- [ ] Check Dapr sidecar logs:
  ```bash
  kubectl logs -l app=backend -c daprd --tail=50
  ```
- [ ] Verify structured JSON logs with trace_id, user_id, correlation_id

### 3. Test Metrics

- [ ] Port-forward to backend pod:
  ```bash
  kubectl port-forward <backend-pod> 9090:9090
  ```
- [ ] Check Dapr metrics:
  ```bash
  curl http://localhost:9090/metrics | grep dapr
  ```
- [ ] Verify metrics include:
  - `dapr_pubsub_ingress_count`
  - `dapr_http_server_request_count`
  - `dapr_component_loaded`

---

## Phase 9: Final Verification

### 1. End-to-End Testing

- [ ] User registration flow
- [ ] User login flow
- [ ] Create task via chat interface
- [ ] Update task
- [ ] Complete task
- [ ] Delete task
- [ ] Verify all events published to Kafka
- [ ] Check logs for trace context propagation

### 2. Performance Testing

- [ ] Test API response times (<100ms p95)
- [ ] Test concurrent user access
- [ ] Monitor resource usage:
  ```bash
  kubectl top pods
  kubectl top nodes
  ```

### 3. Disaster Recovery Testing

- [ ] Test pod restart:
  ```bash
  kubectl delete pod <backend-pod>
  ```
- [ ] Verify pod recreates with Dapr sidecar (2/2 Ready)
- [ ] Verify application still accessible
- [ ] Test Helm rollback:
  ```bash
  helm rollback todo-app
  ```

---

## Phase 10: Documentation and Handoff

### 1. Document Deployment

- [ ] Save external IP address
- [ ] Document any custom configurations
- [ ] Update README.md with deployment URL
- [ ] Create runbook for common operations

### 2. Share Access

- [ ] Share application URL with stakeholders
- [ ] Provide demo credentials (if applicable)
- [ ] Share Redpanda dashboard access
- [ ] Share OCI Console access (if needed)

### 3. Monitoring and Alerts

- [ ] Set up monitoring dashboards (optional)
- [ ] Configure alerting rules (optional)
- [ ] Document on-call procedures (optional)

---

## Troubleshooting Checklist

### If Pods Not Starting

- [ ] Check pod events: `kubectl describe pod <pod-name>`
- [ ] Check image pull errors
- [ ] Verify secrets exist
- [ ] Check resource limits

### If Dapr Sidecar Not Injecting

- [ ] Verify Dapr operator running: `kubectl get pods -n dapr-system`
- [ ] Check deployment annotations: `kubectl get deployment <name> -o yaml | grep dapr.io`
- [ ] Check Dapr operator logs: `kubectl logs -l app=dapr-operator -n dapr-system`

### If Events Not Publishing

- [ ] Check Dapr Pub/Sub logs: `kubectl logs <pod> -c daprd | grep pubsub`
- [ ] Verify Kafka connectivity
- [ ] Check Kafka credentials in secret
- [ ] Verify Dapr component loaded: `kubectl get components`

### If Application Not Accessible

- [ ] Check ingress status: `kubectl get ingress`
- [ ] Verify load balancer IP assigned
- [ ] Check ingress controller logs: `kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx`
- [ ] Test service directly: `kubectl port-forward svc/todo-app-backend 8000:8000`

---

## Post-Deployment Checklist

### Daily Operations

- [ ] Monitor application logs
- [ ] Check Dapr dashboard for component health
- [ ] Review Kafka topic lag in Redpanda dashboard
- [ ] Monitor resource usage

### Weekly Maintenance

- [ ] Review and rotate logs
- [ ] Check for security updates
- [ ] Review cost usage in OCI Console
- [ ] Backup database (if applicable)

### Monthly Review

- [ ] Review and optimize resource allocation
- [ ] Update dependencies
- [ ] Review and update documentation
- [ ] Conduct disaster recovery drill

---

## Rollback Procedure

### If Deployment Fails

1. [ ] Check deployment status: `kubectl get pods`
2. [ ] Review error logs: `kubectl logs <pod-name>`
3. [ ] Rollback Helm release:
   ```bash
   helm rollback todo-app
   ```
4. [ ] Verify rollback successful:
   ```bash
   kubectl get pods
   curl http://<EXTERNAL-IP>/api/health
   ```

### If Need to Rollback to Specific Version

1. [ ] List release history:
   ```bash
   helm history todo-app
   ```
2. [ ] Rollback to specific revision:
   ```bash
   helm rollback todo-app <revision-number>
   ```
3. [ ] Verify application functionality

---

## Success Criteria

### Deployment Success

- ✅ All pods running (2/2 Ready)
- ✅ All Dapr components loaded
- ✅ Application accessible via external IP
- ✅ Health endpoints responding (200 OK)
- ✅ Events publishing to Kafka
- ✅ Logs showing structured JSON format
- ✅ CI/CD pipeline operational

### Performance Success

- ✅ API response time <100ms (p95)
- ✅ Event publishing <50ms
- ✅ Zero downtime deployments
- ✅ Automatic rollback on failure

### Operational Success

- ✅ Monitoring dashboards accessible
- ✅ Logs searchable and traceable
- ✅ Alerts configured (if applicable)
- ✅ Documentation complete

---

## Support and Resources

### Documentation

- **OKE Deployment Guide**: `docs/oke-deployment.md`
- **Dapr Integration Guide**: `docs/dapr-integration.md`
- **Demo Script**: `docs/demo-script.md`
- **Main README**: `README.md`

### External Resources

- **Oracle OKE Docs**: https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm
- **Dapr Docs**: https://docs.dapr.io/
- **Helm Docs**: https://helm.sh/docs/
- **Redpanda Docs**: https://docs.redpanda.com/

### Support Channels

- **GitHub Issues**: Report bugs and feature requests
- **OCI Support**: For OKE cluster issues
- **Dapr Community**: For Dapr-related questions

---

**Checklist Status**: Ready for Use
**Last Updated**: 2026-02-09
**Version**: 1.0
