# Tasks: Oracle OKE Dapr Infrastructure Integration

**Input**: Design documents from `/specs/001-oke-dapr-infrastructure/`
**Prerequisites**: plan.md, spec.md, research.md, architecture.md, dapr-components.md, cicd-pipeline.md, monitoring.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Infrastructure**: `infra/dapr-components/`, `infra/helm/todo-app/`, `infra/oke/`, `infra/scripts/`
- **CI/CD**: `.github/workflows/`
- **Backend**: `backend/` (existing structure)
- **Documentation**: `docs/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create infrastructure directories and base configuration files

- [ ] T001 Create infra/dapr-components/ directory for Dapr component YAMLs
- [ ] T002 Create infra/oke/ directory for OKE cluster setup scripts
- [ ] T003 Create infra/scripts/ directory for deployment automation scripts
- [ ] T004 Create .github/workflows/ directory for CI/CD pipeline
- [ ] T005 Create docs/ directory for deployment documentation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Oracle OKE cluster provisioning and Dapr installation - MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create OKE cluster provisioning script in infra/oke/cluster-setup.sh
- [ ] T007 Create Dapr initialization script in infra/oke/dapr-init.sh
- [ ] T008 Create OKE setup documentation in infra/oke/README.md
- [ ] T009 Provision Oracle OKE cluster (4 OCPU, 24GB RAM, always-free tier)
- [ ] T010 Configure kubectl access to OKE cluster (generate kubeconfig)
- [ ] T011 Install Dapr runtime on OKE cluster using dapr init -k
- [ ] T012 Verify Dapr installation with dapr status -k
- [ ] T013 Sign up for Redpanda Cloud and create serverless cluster
- [ ] T014 Create Kafka topics in Redpanda (task-events, task-updates, reminders with 3 partitions each)
- [ ] T015 Generate Redpanda SASL credentials and save bootstrap URL

**Checkpoint**: Foundation ready - OKE cluster running, Dapr installed, Kafka available - user story implementation can now begin

---

## Phase 3: User Story 1 - Deploy Application to Oracle OKE with Dapr Sidecars (Priority: P1) 🎯 MVP

**Goal**: Deploy existing Todo AI Chatbot to OKE with Dapr sidecars, making application accessible via OKE load balancer with all Dapr components operational

**Independent Test**: Deploy Helm chart to OKE, verify all pods running with Dapr sidecars (2/2 Ready), access application via load balancer URL, verify Dapr components in ready state

### Dapr Components Creation

- [ ] T016 [P] [US1] Create Dapr Kafka Pub/Sub component in infra/dapr-components/kafka-pubsub.yaml
- [ ] T017 [P] [US1] Create Dapr PostgreSQL State Store component in infra/dapr-components/state-postgresql.yaml
- [ ] T018 [P] [US1] Create Dapr Scheduler/Jobs component in infra/dapr-components/scheduler-jobs.yaml
- [ ] T019 [P] [US1] Create Dapr Secrets component in infra/dapr-components/secretstores-kubernetes.yaml

### Kubernetes Secrets Setup

- [ ] T020 [US1] Create Kubernetes Secret for application credentials (COHERE_API_KEY, BETTER_AUTH_SECRET, DATABASE_URL)
- [ ] T021 [US1] Create Kubernetes Secret for Kafka credentials (SASL username and password)

### Helm Chart Upgrades

- [ ] T022 [US1] Update infra/helm/todo-app/Chart.yaml version from 0.1.0 to 0.2.0
- [ ] T023 [P] [US1] Add Dapr sidecar annotations to infra/helm/todo-app/templates/deployment-frontend.yaml
- [ ] T024 [P] [US1] Add Dapr sidecar annotations to infra/helm/todo-app/templates/deployment-backend.yaml
- [ ] T025 [US1] Create Dapr components template in infra/helm/todo-app/templates/dapr-components.yaml
- [ ] T026 [US1] Update infra/helm/todo-app/values.yaml with Dapr configuration (app-id, ports, log-level)
- [ ] T027 [US1] Create OKE-specific values file in infra/helm/todo-app/values-oke.yaml
- [ ] T028 [US1] Update infra/helm/todo-app/templates/secrets.yaml to include Kafka credentials

### Deployment and Verification

- [ ] T029 [US1] Apply Dapr components to OKE cluster (kubectl apply -f infra/dapr-components/)
- [ ] T030 [US1] Verify Dapr components are ready (kubectl get components)
- [ ] T031 [US1] Deploy application to OKE using Helm (helm upgrade --install todo-app ./infra/helm/todo-app --values values-oke.yaml)
- [ ] T032 [US1] Verify all pods running with Dapr sidecars (kubectl get pods - expect 2/2 Ready)
- [ ] T033 [US1] Verify Dapr sidecars healthy (kubectl logs <pod> -c daprd)
- [ ] T034 [US1] Install NGINX Ingress Controller on OKE cluster
- [ ] T035 [US1] Get external IP from load balancer (kubectl get svc ingress-nginx-controller)
- [ ] T036 [US1] Test application accessibility via load balancer URL
- [ ] T037 [US1] Verify frontend loads successfully
- [ ] T038 [US1] Verify backend health endpoint responds (curl http://<ip>/api/health)
- [ ] T039 [US1] Test Dapr Secrets API access from application pod

**Checkpoint**: User Story 1 complete - Application running on OKE with Dapr sidecars, accessible via load balancer, all components healthy

---

## Phase 4: User Story 2 - Event-Driven Architecture with Kafka Pub/Sub (Priority: P2)

**Goal**: Implement event publishing for task operations via Dapr Pub/Sub, demonstrating decoupled event-driven architecture with observable event flow to Kafka

**Independent Test**: Create task via chat interface, verify event published to Kafka topic via Dapr logs, check Redpanda dashboard for event message, confirm event contains correct task metadata

### Backend Event Publishing Implementation

- [ ] T040 [US2] Create Dapr HTTP client wrapper in backend/services/dapr_client.py
- [ ] T041 [US2] Add event publishing to task creation in backend/routes/tasks.py (POST endpoint)
- [ ] T042 [US2] Add event publishing to task update in backend/routes/tasks.py (PUT endpoint)
- [ ] T043 [US2] Add event publishing to task deletion in backend/routes/tasks.py (DELETE endpoint)
- [ ] T044 [US2] Add event publishing to task completion in backend/routes/tasks.py (PATCH endpoint)
- [ ] T045 [US2] Implement CloudEvents format for all published events
- [ ] T046 [US2] Add trace context propagation to event headers

### Event Flow Testing and Verification

- [ ] T047 [US2] Rebuild backend Docker image with event publishing code
- [ ] T048 [US2] Push updated backend image to container registry
- [ ] T049 [US2] Deploy updated backend to OKE (helm upgrade with new image tag)
- [ ] T050 [US2] Create test task via chat interface
- [ ] T051 [US2] Verify event published in Dapr sidecar logs (kubectl logs <backend-pod> -c daprd | grep publish)
- [ ] T052 [US2] Verify event appears in Redpanda Cloud dashboard (task-events topic)
- [ ] T053 [US2] Verify event payload contains correct task metadata (task_id, user_id, title, timestamp)
- [ ] T054 [US2] Test event publishing for update operation
- [ ] T055 [US2] Test event publishing for delete operation
- [ ] T056 [US2] Test Dapr retry behavior when Kafka is temporarily unavailable

**Checkpoint**: User Story 2 complete - All task operations publish events to Kafka via Dapr, event flow observable and traceable

---

## Phase 5: User Story 3 - Automated CI/CD Pipeline with GitHub Actions (Priority: P3)

**Goal**: Implement GitHub Actions pipeline for automated testing, building, and deployment to OKE on every push to main branch

**Independent Test**: Push commit to repository, observe GitHub Actions workflow execute all stages, verify images pushed to registry, confirm application deployed to OKE with new changes

### GitHub Actions Workflow Creation

- [ ] T057 [US3] Create GitHub Actions workflow file in .github/workflows/deploy-oke.yml
- [ ] T058 [US3] Implement test stage (pytest, linting) in workflow
- [ ] T059 [US3] Implement build stage (Docker images for frontend and backend) in workflow
- [ ] T060 [US3] Implement push stage (push images to ghcr.io) in workflow
- [ ] T061 [US3] Implement deploy stage (Helm upgrade on OKE) in workflow
- [ ] T062 [US3] Implement verify stage (pod status, smoke tests) in workflow
- [ ] T063 [US3] Add workflow triggers (push to main, pull_request, workflow_dispatch)

### GitHub Secrets Configuration

- [ ] T064 [US3] Generate base64-encoded kubeconfig for OKE cluster
- [ ] T065 [US3] Add KUBECONFIG secret to GitHub repository
- [ ] T066 [US3] Add COHERE_API_KEY secret to GitHub repository
- [ ] T067 [US3] Add BETTER_AUTH_SECRET secret to GitHub repository
- [ ] T068 [US3] Add DATABASE_URL secret to GitHub repository
- [ ] T069 [US3] Add KAFKA_USERNAME secret to GitHub repository
- [ ] T070 [US3] Add KAFKA_PASSWORD secret to GitHub repository

### Pipeline Testing and Verification

- [ ] T071 [US3] Commit and push workflow file to trigger pipeline
- [ ] T072 [US3] Monitor workflow execution in GitHub Actions UI
- [ ] T073 [US3] Verify test stage passes (all tests run successfully)
- [ ] T074 [US3] Verify build stage completes (images built with commit SHA tags)
- [ ] T075 [US3] Verify push stage completes (images pushed to ghcr.io)
- [ ] T076 [US3] Verify deploy stage completes (Helm upgrade successful)
- [ ] T077 [US3] Verify application accessible with new changes
- [ ] T078 [US3] Test pipeline failure handling (introduce failing test, verify pipeline stops)
- [ ] T079 [US3] Test rollback procedure (helm rollback command)

**Checkpoint**: User Story 3 complete - CI/CD pipeline operational, automated deployment on every push, rollback capability verified

---

## Phase 6: User Story 4 - Monitoring and Observability (Priority: P4)

**Goal**: Implement comprehensive monitoring and observability with structured logging, Dapr dashboard access, and AI-powered cluster analysis

**Independent Test**: Access kubectl logs for application pods, view Dapr dashboard showing component health, run kubectl-ai/kagent commands for cluster analysis, trace event flow through logs with correlation IDs

### Structured Logging Implementation

- [ ] T080 [P] [US4] Implement structured JSON logging in backend/services/logger.py
- [ ] T081 [P] [US4] Add trace context to all backend log statements
- [ ] T082 [US4] Update backend routes to use structured logger
- [ ] T083 [US4] Add correlation IDs to event publishing logs
- [ ] T084 [US4] Rebuild and deploy backend with structured logging

### Dapr Dashboard Setup

- [ ] T085 [US4] Deploy Dapr dashboard to OKE cluster (dapr dashboard -k)
- [ ] T086 [US4] Configure port-forward for Dapr dashboard access
- [ ] T087 [US4] Verify Dapr dashboard shows all components and sidecars
- [ ] T088 [US4] Verify Dapr dashboard displays metrics and health status

### Monitoring Documentation and Tools

- [ ] T089 [P] [US4] Create monitoring guide in docs/monitoring.md
- [ ] T090 [P] [US4] Document kubectl logs commands for all pods in docs/monitoring.md
- [ ] T091 [P] [US4] Document kubectl-ai/kagent usage examples in docs/monitoring.md
- [ ] T092 [US4] Create troubleshooting runbook in docs/troubleshooting.md

### Monitoring Verification

- [ ] T093 [US4] Test kubectl logs access for frontend pods
- [ ] T094 [US4] Test kubectl logs access for backend pods
- [ ] T095 [US4] Test kubectl logs access for Dapr sidecars
- [ ] T096 [US4] Verify structured logs contain trace_id, user_id, task_id fields
- [ ] T097 [US4] Test event flow tracing through logs (create task → find event in Dapr logs → find in Kafka)
- [ ] T098 [US4] Run kagent analyze cluster command and verify output
- [ ] T099 [US4] Run kubectl-ai commands for pod debugging
- [ ] T100 [US4] Verify Dapr Pub/Sub metrics visible in dashboard

**Checkpoint**: User Story 4 complete - Comprehensive monitoring operational, logs accessible and structured, Dapr dashboard functional, AI-powered analysis available

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, deployment automation, and final verification

- [ ] T101 [P] Create deployment automation script in infra/scripts/deploy-oke.sh
- [ ] T102 [P] Create deployment verification script in infra/scripts/verify-deployment.sh
- [ ] T103 [P] Create OKE deployment guide in docs/oke-deployment.md
- [ ] T104 [P] Create Dapr integration guide in docs/dapr-integration.md
- [ ] T105 [P] Create demo script for judges in docs/demo-script.md
- [ ] T106 Update main README.md with OKE deployment instructions
- [ ] T107 Test one-command deployment (./infra/scripts/deploy-oke.sh)
- [ ] T108 Verify all Phase IV features still work (no regressions)
- [ ] T109 Run complete end-to-end test (login → chat → create task → verify event → check logs)
- [ ] T110 Create final deployment checklist in docs/deployment-checklist.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion (requires OKE deployment)
- **User Story 3 (Phase 5)**: Depends on User Story 1 completion (requires OKE deployment)
- **User Story 4 (Phase 6)**: Depends on User Story 1 completion (requires OKE deployment)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on User Story 1 (requires OKE deployment with Dapr)
- **User Story 3 (P3)**: Depends on User Story 1 (requires OKE deployment target)
- **User Story 4 (P4)**: Depends on User Story 1 (requires OKE deployment to monitor)

### Within Each User Story

**User Story 1**:
- Dapr components can be created in parallel (T016-T019)
- Secrets must be created before deployment (T020-T021)
- Helm chart updates can be done in parallel (T023-T024)
- Deployment must happen after all Helm updates complete
- Verification happens after deployment

**User Story 2**:
- Backend code changes are sequential
- Rebuild/deploy happens after code complete
- Testing happens after deployment

**User Story 3**:
- Workflow file creation is sequential
- Secrets configuration can be done in parallel
- Testing happens after workflow committed

**User Story 4**:
- Logging implementation can be done in parallel (T080-T081)
- Documentation can be created in parallel (T089-T091)
- Testing happens after deployment

### Parallel Opportunities

- All Setup tasks (T001-T005) can run in parallel
- Dapr component creation (T016-T019) can run in parallel
- Helm deployment updates (T023-T024) can run in parallel
- Structured logging implementation (T080-T081) can run in parallel
- Documentation creation (T089-T091, T101-T105) can run in parallel
- User Stories 2, 3, 4 can be worked on in parallel after User Story 1 completes (if team capacity allows)

---

## Parallel Example: User Story 1

```bash
# Launch all Dapr component creation together:
Task: "Create Dapr Kafka Pub/Sub component in infra/dapr-components/kafka-pubsub.yaml"
Task: "Create Dapr PostgreSQL State Store component in infra/dapr-components/state-postgresql.yaml"
Task: "Create Dapr Scheduler/Jobs component in infra/dapr-components/scheduler-jobs.yaml"
Task: "Create Dapr Secrets component in infra/dapr-components/secretstores-kubernetes.yaml"

# Launch Helm deployment updates together:
Task: "Add Dapr sidecar annotations to infra/helm/todo-app/templates/deployment-frontend.yaml"
Task: "Add Dapr sidecar annotations to infra/helm/todo-app/templates/deployment-backend.yaml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T015) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T016-T039)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready - Application running on OKE with Dapr

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - OKE deployment!)
3. Add User Story 2 → Test independently → Deploy/Demo (Event-driven architecture!)
4. Add User Story 3 → Test independently → Deploy/Demo (CI/CD automation!)
5. Add User Story 4 → Test independently → Deploy/Demo (Full observability!)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (blocking - must complete first)
3. Once User Story 1 is done:
   - Developer A: User Story 2 (event publishing)
   - Developer B: User Story 3 (CI/CD pipeline)
   - Developer C: User Story 4 (monitoring)
4. Stories 2, 3, 4 complete and integrate independently

---

## Task Summary

**Total Tasks**: 110
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 10 tasks
- Phase 3 (User Story 1 - P1): 24 tasks
- Phase 4 (User Story 2 - P2): 17 tasks
- Phase 5 (User Story 3 - P3): 23 tasks
- Phase 6 (User Story 4 - P4): 21 tasks
- Phase 7 (Polish): 10 tasks

**Parallel Opportunities**: 28 tasks marked [P]

**Independent Test Criteria**:
- US1: Application accessible on OKE with Dapr sidecars (2/2 Ready)
- US2: Events published to Kafka topics, visible in Redpanda dashboard
- US3: GitHub Actions pipeline deploys successfully on push
- US4: Logs accessible, Dapr dashboard functional, kagent analysis working

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 39 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- User Story 1 is blocking for all other stories (requires OKE deployment)
- User Stories 2, 3, 4 can proceed in parallel after User Story 1 completes
- All tasks follow strict checklist format: - [ ] [TaskID] [P?] [Story?] Description with file path
