# Implementation Plan: Oracle OKE Dapr Infrastructure Integration

**Branch**: `001-oke-dapr-infrastructure` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-oke-dapr-infrastructure/spec.md`

## Summary

Deploy the existing Phase IV Todo AI Chatbot application to Oracle Cloud Infrastructure Kubernetes Engine (OKE) with Dapr runtime for cloud-native service abstraction, event-driven architecture using Kafka/Redpanda, automated CI/CD pipeline via GitHub Actions, and comprehensive monitoring. This phase transforms the local Minikube deployment into a production-grade, event-driven microservices architecture running on Oracle's always-free tier cloud infrastructure.

**Primary Requirement**: Production-ready Kubernetes deployment on Oracle OKE with Dapr sidecars, event publishing via Kafka, automated CI/CD, and observable infrastructure.

**Technical Approach**: Upgrade existing Helm charts with Dapr annotations, create Dapr component YAMLs for Pub/Sub (Kafka), State (PostgreSQL), Scheduler (Jobs), and Secrets (Kubernetes), modify backend to publish events via Dapr HTTP API, provision Oracle OKE cluster, configure GitHub Actions workflow for automated deployment, and implement monitoring via kubectl logs and Dapr dashboard.

## Technical Context

**Language/Version**: Python 3.11 (backend), Node.js 20 (frontend), Bash/PowerShell (scripts)
**Primary Dependencies**: Dapr 1.12+, Helm 3.x, kubectl 1.28+, Oracle Cloud CLI, GitHub Actions, Kafka (Redpanda Cloud free tier or Strimzi)
**Storage**: Neon Serverless PostgreSQL (existing), Kafka topics (task-events, task-updates, reminders)
**Testing**: pytest (backend), kubectl-ai/kagent (cluster analysis), manual event flow verification
**Target Platform**: Oracle OKE (Kubernetes 1.28+, always-free tier: 4 OCPU, 24GB RAM)
**Project Type**: Web application with infrastructure layer (frontend + backend + Dapr sidecars + event consumers)
**Performance Goals**: Event publishing <50ms latency, application response <2s, Dapr sidecar <128MB memory
**Constraints**: Oracle OKE always-free tier limits (4 OCPU, 24GB RAM), Redpanda Cloud free tier, GitHub Actions free tier, no paid services
**Scale/Scope**: Single-region deployment, 2-3 replicas per service, 3 Kafka topics, 4 Dapr components, 1 CI/CD pipeline

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Phase V Principles Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| XXV. Event-Driven Architecture Mandate | ✅ PASS | Task operations will publish events to Kafka via Dapr Pub/Sub |
| XXVI. Dapr Abstraction Layer Enforcement | ✅ PASS | All infrastructure access (Pub/Sub, State, Secrets, Scheduler) via Dapr APIs only |
| XXVII. Microservices Decomposition | ⚠️ PARTIAL | Chat API as producer; consumer services (Notification, Recurring, Audit) are optional for Phase V |
| XXVIII. Advanced Features Implementation | ✅ PASS | Features already implemented in Phase I-IV; this phase adds infrastructure only |
| XXIX. Kafka/Redpanda Event Backbone | ✅ PASS | Using Redpanda Cloud free tier (preferred) or Strimzi in-cluster |
| XXX. Production Kubernetes Deployment | ✅ PASS | Deploying to Oracle OKE always-free tier |
| XXXI. CI/CD Automation with GitHub Actions | ✅ PASS | Full pipeline: test → build → push → deploy |
| XXXII. Dapr Scheduler and Jobs API | ✅ PASS | Dapr Jobs component for reminders (already implemented in Phase IV) |
| XXXIII. Multi-Environment Configuration | ✅ PASS | Helm values files for local (Minikube) and production (OKE) |
| XXXIV. Comprehensive Monitoring | ✅ PASS | kubectl logs, Dapr dashboard, kubectl-ai/kagent analysis |
| XXXV. Zero Vendor Lock-In Through Dapr | ✅ PASS | Dapr components swappable via YAML configuration only |
| XXXVI. Backward Compatibility Preservation | ✅ PASS | Phase IV functionality remains unchanged; infrastructure is additive |

### ✅ Phase IV Constraints Compliance

| Constraint | Status | Notes |
|-----------|--------|-------|
| Production Kubernetes Target | ✅ PASS | Oracle OKE always-free tier (4 OCPU, 24GB RAM) |
| Event Streaming Platform | ✅ PASS | Redpanda Cloud serverless free tier (preferred) |
| Dapr-Only Infrastructure Access | ✅ PASS | No direct Kafka/PostgreSQL client libraries in application code |
| Microservices Code Isolation | ✅ PASS | Existing code unchanged; event publishing added to backend |
| CI/CD Platform Lock | ✅ PASS | GitHub Actions only |
| Free Tier Compliance | ✅ PASS | All services within free tier limits |
| Database Continuity | ✅ PASS | Neon Serverless PostgreSQL remains external |
| Helm Chart Evolution | ✅ PASS | Upgrading existing Phase IV charts with Dapr annotations |
| Secrets Management | ✅ PASS | Kubernetes Secrets + Dapr Secrets component |
| Monitoring Scope | ✅ PASS | kubectl-ai/kagent, Dapr dashboard, pod logs |

### Gate Evaluation

**Result**: ✅ **PASS** - All Phase V principles and constraints satisfied. No violations requiring justification.

**Notes**:
- Microservices decomposition (Principle XXVII) is partially implemented: Chat API publishes events, but dedicated consumer services (Notification, Recurring, Audit) are optional for this phase. The architecture supports adding them later without code changes.
- All infrastructure changes are additive and non-breaking to existing Phase IV functionality.

## Project Structure

### Documentation (this feature)

```text
specs/001-oke-dapr-infrastructure/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output: Dapr components, OKE setup, Kafka options
├── architecture.md      # Phase 1 output: Final architecture diagram with Dapr + Kafka
├── dapr-components.md   # Phase 1 output: Dapr component specifications
├── cicd-pipeline.md     # Phase 1 output: GitHub Actions workflow design
├── monitoring.md        # Phase 1 output: Observability strategy
├── quickstart.md        # Phase 1 output: One-command deployment guide
└── checklists/
    └── requirements.md  # Acceptance criteria checklist (existing)
```

### Source Code (repository root)

```text
# Infrastructure layer (Dapr + OKE + CI/CD)
infra/
├── dapr-components/
│   ├── kafka-pubsub.yaml           # Dapr Pub/Sub component for Kafka/Redpanda
│   ├── state-postgresql.yaml       # Dapr State Store component for Neon PostgreSQL
│   ├── scheduler-jobs.yaml         # Dapr Scheduler/Jobs component
│   └── secretstores-kubernetes.yaml # Dapr Secrets component for K8s Secrets
├── helm/
│   └── todo-app/
│       ├── Chart.yaml              # Updated version: 0.1.0 → 0.2.0
│       ├── values.yaml             # Updated with Dapr annotations
│       ├── values-oke.yaml         # OKE-specific values (NEW)
│       └── templates/
│           ├── deployment-frontend.yaml  # Updated with Dapr sidecar annotations
│           ├── deployment-backend.yaml   # Updated with Dapr sidecar annotations
│           ├── dapr-components.yaml      # Dapr components deployment (NEW)
│           └── secrets.yaml              # Updated with Kafka credentials
├── oke/
│   ├── cluster-setup.sh            # OKE cluster provisioning script (NEW)
│   ├── dapr-init.sh                # Dapr installation on OKE (NEW)
│   └── README.md                   # OKE setup instructions (NEW)
└── scripts/
    ├── deploy-oke.sh               # OKE deployment script (NEW)
    └── verify-deployment.sh        # Deployment verification script (NEW)

# CI/CD pipeline
.github/
└── workflows/
    └── deploy-oke.yml              # GitHub Actions workflow (NEW)

# Backend modifications (event publishing)
backend/
└── src/
    ├── services/
    │   └── dapr_client.py          # Dapr HTTP client wrapper (NEW)
    └── api/
        └── tasks.py                # Updated with event publishing logic

# Documentation
docs/
├── oke-deployment.md               # OKE deployment guide (NEW)
├── dapr-integration.md             # Dapr integration guide (NEW)
└── demo-script.md                  # Judge demo script (NEW)
```

**Structure Decision**: Infrastructure-focused extension of existing Phase IV monorepo. New directories for Dapr components (`infra/dapr-components/`), OKE setup (`infra/oke/`), and CI/CD pipeline (`.github/workflows/`). Existing Helm charts upgraded in place. Backend modified minimally to add Dapr event publishing. Frontend unchanged.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All Phase V principles and constraints are satisfied.

## Phase 0: Research & Decision Documentation

**Objective**: Resolve all technical unknowns and document architectural decisions for Dapr components, Kafka backend, OKE setup, and CI/CD pipeline.

### Research Tasks

1. **Dapr Component Configuration**
   - Research Dapr Pub/Sub component YAML structure for Kafka
   - Research Dapr State Store component for PostgreSQL (connection string format, table schema)
   - Research Dapr Scheduler/Jobs API component configuration
   - Research Dapr Secrets component for Kubernetes Secrets
   - Document component scopes and metadata requirements

2. **Kafka Backend Selection**
   - Compare Redpanda Cloud serverless (free tier) vs Strimzi self-hosted in OKE
   - Evaluate setup complexity, management overhead, free tier limits
   - Document connection details (bootstrap URLs, authentication, topic creation)
   - **Decision**: Redpanda Cloud (zero management, free, Kafka-compatible, no Zookeeper)

3. **Oracle OKE Cluster Setup**
   - Research OKE always-free tier provisioning (OCI CLI commands or console steps)
   - Document cluster configuration (node pools, networking, security groups)
   - Research kubectl access setup (`oci ce cluster create-kubeconfig`)
   - Document Dapr installation on OKE (`dapr init -k`)

4. **GitHub Actions Workflow Design**
   - Research GitHub Actions for Kubernetes deployment
   - Document OCI authentication methods (service principal, kubeconfig secret)
   - Research Helm upgrade in GitHub Actions
   - Document image registry options (ghcr.io vs Docker Hub vs Oracle Container Registry)
   - **Decision**: ghcr.io (integrated with GitHub Actions, private option)

5. **Secrets Management Strategy**
   - Research Kubernetes Secrets creation and management
   - Document Dapr Secrets API usage in application code
   - Research secret rotation procedures
   - Document environment-specific secret handling (local vs OKE)

6. **Monitoring and Logging**
   - Research Dapr dashboard deployment and access
   - Document kubectl-ai/kagent commands for cluster analysis
   - Research structured logging best practices for Dapr sidecars
   - Document log aggregation strategies (kubectl logs vs optional Loki)

### Output Artifact

**File**: `specs/001-oke-dapr-infrastructure/research.md`

**Structure**:
```markdown
# Research: Oracle OKE Dapr Infrastructure Integration

## Decision 1: Kafka Backend - Redpanda Cloud Serverless
- **Chosen**: Redpanda Cloud serverless free tier
- **Rationale**: Zero management, free, Kafka-compatible, no Zookeeper, fast setup
- **Alternatives Considered**: Strimzi self-hosted (requires cluster resources, management overhead)
- **Implementation**: Sign up → create serverless cluster → get bootstrap URL + credentials

## Decision 2: Dapr Jobs vs Cron Bindings for Reminders
- **Chosen**: Dapr Jobs API
- **Rationale**: Exact timing, no polling, better for hackathon demo
- **Alternatives Considered**: Cron bindings (less precise, polling-based)

## Decision 3: Secret Storage - Dapr Secretstores
- **Chosen**: Dapr secretstores.kubernetes component
- **Rationale**: Portable, unified API, future-proof
- **Alternatives Considered**: Kubernetes Secrets only (less portable)

## Decision 4: Helm Upgrade Strategy
- **Chosen**: Patch existing Phase IV chart
- **Rationale**: Incremental evolution, version continuity
- **Alternatives Considered**: Create new chart (breaks continuity)

## Decision 5: GitHub Actions Runner
- **Chosen**: ubuntu-latest
- **Rationale**: Free, sufficient for deployment tasks
- **Alternatives Considered**: Self-hosted (unnecessary complexity)

## Decision 6: Container Registry
- **Chosen**: GitHub Container Registry (ghcr.io)
- **Rationale**: Integrated with GitHub Actions, private option, free
- **Alternatives Considered**: Docker Hub (rate limits), Oracle Container Registry (additional setup)

## Dapr Component Specifications
[Detailed YAML structures and metadata requirements]

## OKE Cluster Setup
[Step-by-step provisioning commands and configuration]

## GitHub Actions Workflow
[Pipeline stages, authentication, deployment steps]
```

## Phase 1: Design & Contracts

**Objective**: Create detailed architecture diagrams, Dapr component specifications, CI/CD pipeline design, and monitoring strategy.

### Design Tasks

1. **Architecture Diagram**
   - Create final architecture diagram showing:
     - Existing monolith pods (frontend, backend) with Dapr sidecars
     - Dapr components (Pub/Sub, State, Scheduler, Secrets)
     - Kafka/Redpanda topics (task-events, task-updates, reminders)
     - Event flow: Chat API → Dapr Pub/Sub → Kafka → future consumers
     - External dependencies (Neon PostgreSQL, Redpanda Cloud)
   - Document component interactions and data flow

2. **Dapr Component Specifications**
   - Create detailed YAML specifications for each Dapr component:
     - `kafka-pubsub.yaml`: Pub/Sub component with Redpanda connection details
     - `state-postgresql.yaml`: State Store component with Neon connection string
     - `scheduler-jobs.yaml`: Scheduler component for reminders
     - `secretstores-kubernetes.yaml`: Secrets component for K8s Secrets
   - Document component metadata, scopes, and configuration options

3. **CI/CD Pipeline Design**
   - Design GitHub Actions workflow with stages:
     - Test: Run pytest for backend, lint checks
     - Build: Build Docker images with commit SHA tags
     - Push: Push images to ghcr.io
     - Deploy: Helm upgrade on OKE cluster
   - Document authentication strategy (OCI credentials, kubeconfig)
   - Document rollback procedures

4. **Monitoring Strategy**
   - Design observability approach:
     - kubectl logs for application and Dapr sidecar logs
     - Dapr dashboard for component health and metrics
     - kubectl-ai/kagent commands for cluster analysis
   - Document log structure and correlation IDs
   - Document troubleshooting procedures

5. **Helm Chart Upgrade Design**
   - Design Helm chart modifications:
     - Add Dapr sidecar annotations to deployments
     - Add Dapr component template
     - Update values.yaml with Dapr configuration
     - Create values-oke.yaml for OKE-specific settings
   - Document version bump strategy (0.1.0 → 0.2.0)

### Output Artifacts

**File 1**: `specs/001-oke-dapr-infrastructure/architecture.md`
- Final architecture diagram (Mermaid or ASCII)
- Component interaction descriptions
- Event flow documentation

**File 2**: `specs/001-oke-dapr-infrastructure/dapr-components.md`
- Detailed Dapr component YAML specifications
- Metadata and configuration explanations
- Scoping and security considerations

**File 3**: `specs/001-oke-dapr-infrastructure/cicd-pipeline.md`
- GitHub Actions workflow design
- Pipeline stages and dependencies
- Authentication and secrets management
- Rollback procedures

**File 4**: `specs/001-oke-dapr-infrastructure/monitoring.md`
- Observability strategy
- kubectl-ai/kagent command reference
- Log structure and correlation
- Troubleshooting guide

**File 5**: `specs/001-oke-dapr-infrastructure/quickstart.md`
- One-command deployment instructions
- Prerequisites checklist
- Verification steps
- Common issues and solutions

## Phase 2: Implementation Phases

**Note**: Phase 2 (tasks.md) is generated by `/sp.tasks` command, NOT by `/sp.plan`. This section outlines the implementation sequence for reference.

### Implementation Sequence

#### Phase 2.1: Dapr Components & Configuration
- Create Dapr component YAML files in `infra/dapr-components/`
- Configure Kafka Pub/Sub component with Redpanda Cloud credentials
- Configure State Store component with Neon PostgreSQL connection
- Configure Scheduler/Jobs component for reminders
- Configure Secrets component for Kubernetes Secrets
- Validate component YAMLs with Dapr CLI

#### Phase 2.2: Helm Chart Upgrade
- Update `Chart.yaml` version (0.1.0 → 0.2.0)
- Add Dapr sidecar annotations to `deployment-frontend.yaml`
- Add Dapr sidecar annotations to `deployment-backend.yaml`
- Create `templates/dapr-components.yaml` for component deployment
- Update `values.yaml` with Dapr configuration
- Create `values-oke.yaml` for OKE-specific settings
- Update `secrets.yaml` with Kafka credentials

#### Phase 2.3: Oracle OKE Cluster Setup
- Provision OKE cluster using OCI CLI or console (4 OCPU, 24GB RAM)
- Configure kubectl access (`oci ce cluster create-kubeconfig`)
- Install Dapr runtime on OKE (`dapr init -k`)
- Verify Dapr installation (`dapr status -k`)
- Create Kubernetes Secrets for application credentials
- Apply Dapr components to OKE cluster

#### Phase 2.4: Backend Event Publishing Integration
- Create `backend/src/services/dapr_client.py` (Dapr HTTP client wrapper)
- Update `backend/src/api/tasks.py` with event publishing logic
- Add Dapr Pub/Sub calls for task operations (create, update, delete)
- Test event publishing locally with Dapr sidecar
- Verify events appear in Kafka topics (Redpanda dashboard)

#### Phase 2.5: GitHub Actions CI/CD Pipeline
- Create `.github/workflows/deploy-oke.yml`
- Configure workflow triggers (push to main)
- Add test stage (pytest, lint)
- Add build stage (Docker images with commit SHA tags)
- Add push stage (ghcr.io authentication and push)
- Add deploy stage (Helm upgrade on OKE)
- Configure GitHub Secrets (OCI credentials, kubeconfig, registry token)
- Test pipeline with sample commit

#### Phase 2.6: Monitoring & Logging Setup
- Deploy Dapr dashboard to OKE cluster
- Configure kubectl-ai/kagent for cluster analysis
- Document kubectl logs commands for application and Dapr sidecars
- Create monitoring documentation with example commands
- Test log aggregation and correlation IDs

#### Phase 2.7: Final Deployment & Verification
- Deploy full application to OKE using Helm
- Verify all pods running with Dapr sidecars (1/1 Ready)
- Test application accessibility via OKE load balancer
- Perform end-to-end test: create task → verify event in Kafka
- Verify Dapr components healthy (Dapr dashboard)
- Run kubectl-ai/kagent cluster health analysis
- Verify CI/CD pipeline with test commit
- Validate all Phase IV features still working (no regressions)
- Create demo script for judges

### Testing Strategy

**Validation Against Success Criteria**:

1. **Dapr Sidecar Health**: `kubectl get pods` → all sidecars running, no CrashLoop
2. **Pub/Sub Test**: Create task via UI/chat → verify Dapr publishes to Kafka topic → see message in Redpanda dashboard/logs
3. **State Test**: Save/fetch conversation state via Dapr HTTP → confirm persistence
4. **Secrets Test**: Fetch COHERE_API_KEY via Dapr secrets API → agent uses it
5. **Jobs Test**: Schedule dummy job → verify callback endpoint hit
6. **Oracle OKE Access**: `kubectl get nodes` → cluster healthy
7. **CI/CD Pipeline**: Push to main → GitHub Actions runs → images pushed → helm upgrade succeeds on OKE
8. **End-to-End**: Login → chat → task operation → event published → visible in Kafka + logs
9. **kubectl-ai/kagent Demo**: "analyze cluster health", "scale frontend to 3 replicas", "why pod pending?"
10. **No Regressions**: All intermediate/advanced Todo features still work perfectly

## Dependencies and Prerequisites

### External Dependencies
- Oracle Cloud Infrastructure account with OKE access (always-free tier)
- Redpanda Cloud account (free tier) or Strimzi installation
- GitHub repository with Actions enabled
- Container registry access (ghcr.io)
- Neon PostgreSQL database (existing from Phase IV)

### Tool Dependencies
- Dapr CLI 1.12+ (`dapr --version`)
- Helm 3.x (`helm version`)
- kubectl 1.28+ (`kubectl version`)
- Oracle Cloud CLI (`oci --version`)
- Docker or Podman for local testing
- kubectl-ai or kagent for cluster analysis (optional but recommended)

### Knowledge Dependencies
- Kubernetes concepts (pods, deployments, services, secrets)
- Dapr architecture (sidecars, components, building blocks)
- Kafka/Redpanda basics (topics, producers, consumers)
- GitHub Actions workflow syntax
- Helm chart structure and templating

## Risk Analysis

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Oracle OKE always-free tier resource limits | HIGH | Monitor resource usage, optimize pod resource requests/limits |
| Redpanda Cloud free tier limits | MEDIUM | Monitor topic throughput, implement rate limiting if needed |
| Dapr sidecar overhead | MEDIUM | Profile memory/CPU usage, adjust resource allocations |
| GitHub Actions build minutes exhaustion | LOW | Optimize workflow, cache dependencies, use matrix builds sparingly |
| Network latency between OKE and Redpanda Cloud | MEDIUM | Choose Redpanda region close to OKE region, implement retry logic |
| Helm upgrade failures mid-deployment | HIGH | Implement rollback strategy, use `--atomic` flag, test in staging |
| Secrets exposure in logs or configs | HIGH | Use Dapr Secrets API exclusively, audit logs for sensitive data |

### Operational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| OKE cluster provisioning delays | MEDIUM | Provision cluster early, document manual steps as fallback |
| Dapr component misconfiguration | HIGH | Validate YAMLs with Dapr CLI, test locally before OKE deployment |
| CI/CD pipeline authentication failures | HIGH | Test OCI credentials and kubeconfig in isolation, document troubleshooting |
| Event publishing failures | MEDIUM | Implement Dapr retry policies, monitor Pub/Sub metrics |
| Monitoring blind spots | LOW | Document all log sources, test kubectl-ai/kagent commands |

## Success Metrics

### Functional Metrics
- ✅ Application accessible on OKE with <2s response time
- ✅ All Dapr components report healthy status
- ✅ Task operations trigger events in Kafka within 1s
- ✅ CI/CD pipeline completes in <10 minutes
- ✅ Zero regressions in Phase IV features

### Technical Metrics
- ✅ Dapr sidecar memory <128MB per pod
- ✅ Event publishing latency <50ms
- ✅ Application startup time <30s with Dapr sidecar
- ✅ OKE resource usage within free tier limits (4 OCPU, 24GB RAM)

### Observability Metrics
- ✅ Application logs accessible via kubectl logs
- ✅ Dapr dashboard displays real-time metrics
- ✅ Event flow traceable through logs with correlation IDs
- ✅ kubectl-ai/kagent provides actionable cluster insights

### Demo Metrics (Judge Evaluation)
- ✅ Decoupled architecture visible through event flow
- ✅ Zero direct Kafka/database client libraries in code
- ✅ Secrets accessed only via Dapr API
- ✅ One-command deployment works reliably
- ✅ Monitoring demonstrates production-grade observability

## Next Steps

After completing this plan:

1. **Execute Phase 0 (Research)**: Run research tasks and create `research.md` with all decisions documented
2. **Execute Phase 1 (Design)**: Create architecture diagrams, Dapr component specs, CI/CD pipeline design, monitoring strategy, and quickstart guide
3. **Generate Tasks**: Run `/sp.tasks` command to generate detailed implementation tasks in `tasks.md`
4. **Begin Implementation**: Execute tasks in dependency order, starting with Dapr components, then Helm upgrades, then OKE setup, then CI/CD pipeline
5. **Continuous Validation**: Test each phase against success criteria before proceeding to next phase
6. **Create PHRs**: Document all implementation steps in Prompt History Records under `history/prompts/001-oke-dapr-infrastructure/`
7. **Prepare Demo**: Create judge demo script showing event flow, Dapr components, CI/CD pipeline, and monitoring

---

**Plan Status**: ✅ Complete - Ready for Phase 0 (Research)
**Next Command**: `/sp.tasks` (after Phase 0 and Phase 1 artifacts are created)
**Estimated Artifacts**: 5 design documents (research.md, architecture.md, dapr-components.md, cicd-pipeline.md, monitoring.md, quickstart.md)
