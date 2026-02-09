# Feature Specification: Oracle OKE Dapr Infrastructure Integration

**Feature Branch**: `001-oke-dapr-infrastructure`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Phase V – Remaining Infrastructure & Cloud-Native Integration (Oracle OKE Only)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Application to Oracle OKE with Dapr Sidecars (Priority: P1)

As a DevOps engineer, I need to deploy the existing Todo AI Chatbot application to Oracle Cloud Infrastructure's Kubernetes Engine (OKE) with Dapr sidecars attached to all services, so that the application runs in a production-grade cloud environment with decoupled service communication.

**Why this priority**: This is the foundation for all other infrastructure work. Without the application running on OKE with Dapr, none of the event-driven or CI/CD features can be demonstrated. This delivers immediate value by proving the application can run in a cloud-native environment.

**Independent Test**: Can be fully tested by deploying the Helm chart to OKE, verifying all pods are running with Dapr sidecars, and confirming the application is accessible via the OKE load balancer. Delivers a working cloud deployment that judges can access.

**Acceptance Scenarios**:

1. **Given** the Oracle OKE cluster is provisioned with 4 OCPU and 24GB RAM (always-free tier), **When** the Helm chart is deployed with Dapr sidecar annotations, **Then** all application pods start successfully with both application and Dapr sidecar containers running
2. **Given** Dapr is initialized on the OKE cluster, **When** Dapr components are applied (kafka-pubsub, state.postgresql, scheduler.jobs, secretstores.kubernetes), **Then** all components are in ready state and accessible to application pods
3. **Given** the application is deployed to OKE, **When** a user accesses the application URL, **Then** the frontend loads successfully and can communicate with backend services through Dapr service invocation
4. **Given** secrets are stored in Kubernetes Secrets, **When** the application starts, **Then** Dapr Secrets API provides COHERE_API_KEY, BETTER_AUTH_SECRET, and NEON_DB_URL to the application without exposing them in environment variables

---

### User Story 2 - Event-Driven Architecture with Kafka Pub/Sub (Priority: P2)

As a system architect, I need task operations to publish events to Kafka topics via Dapr Pub/Sub, so that the system demonstrates a decoupled, event-driven architecture where services communicate asynchronously through message brokers.

**Why this priority**: This demonstrates the core architectural pattern that makes the system production-grade and scalable. Event-driven architecture is a key evaluation criterion for judges. It builds on P1 (requires OKE deployment) but can be tested independently by verifying event flow.

**Independent Test**: Can be fully tested by performing a task operation (create/update/delete), verifying the event is published to the Kafka topic via Dapr Pub/Sub, and confirming subscriber services receive and process the event. Delivers observable event-driven behavior.

**Acceptance Scenarios**:

1. **Given** the Chat API is running with Dapr sidecar, **When** a user creates a new task through the chat interface, **Then** a task-created event is published to the "task-events" Kafka topic via Dapr Pub/Sub API
2. **Given** a task-created event is published to Kafka, **When** the event consumer service polls the topic, **Then** the event is received and processed correctly with all task metadata intact
3. **Given** the application is processing task operations, **When** a task is updated or deleted, **Then** corresponding events (task-updated, task-deleted) are published to appropriate Kafka topics ("task-updates")
4. **Given** reminder functionality is active, **When** a reminder is triggered, **Then** a reminder event is published to the "reminders" Kafka topic and can be consumed by notification services
5. **Given** Kafka is unavailable temporarily, **When** the application attempts to publish events, **Then** Dapr handles retries gracefully and events are eventually delivered when Kafka recovers

---

### User Story 3 - Automated CI/CD Pipeline with GitHub Actions (Priority: P3)

As a development team, I need a GitHub Actions pipeline that automatically builds, tests, and deploys the application to OKE on every push, so that changes are continuously integrated and deployed without manual intervention.

**Why this priority**: Automation is essential for production systems but depends on P1 (OKE deployment) being functional. This can be tested independently by triggering the pipeline and verifying successful deployment. It demonstrates DevOps maturity to judges.

**Independent Test**: Can be fully tested by pushing a commit to the repository, observing the GitHub Actions workflow execute all stages (test, build Docker images, push to registry, deploy via Helm), and confirming the updated application is running on OKE. Delivers automated deployment capability.

**Acceptance Scenarios**:

1. **Given** code changes are pushed to the repository, **When** the GitHub Actions workflow is triggered, **Then** all tests run successfully before proceeding to build stage
2. **Given** tests pass, **When** the build stage executes, **Then** Docker images for frontend and backend are built with appropriate tags and pushed to the container registry
3. **Given** Docker images are pushed, **When** the deploy stage executes, **Then** Helm upgrade command deploys the new images to OKE cluster without downtime
4. **Given** deployment completes, **When** the pipeline finishes, **Then** the workflow reports success status and the application is accessible with the new changes
5. **Given** any stage fails (tests, build, or deploy), **When** the pipeline executes, **Then** the workflow stops at the failed stage, reports detailed error information, and does not proceed to subsequent stages

---

### User Story 4 - Monitoring and Observability (Priority: P4)

As an operations engineer, I need visibility into application health, event flow, and Dapr component status through logs and dashboards, so that I can monitor system behavior and troubleshoot issues in production.

**Why this priority**: Monitoring is critical for production but can be added after core functionality (P1-P3) is working. This can be tested independently by accessing logs and dashboards. It provides judges with evidence that the system is observable.

**Independent Test**: Can be fully tested by accessing kubectl logs for application pods, viewing the Dapr dashboard, and using kubectl-ai/kagent to analyze cluster health. Delivers operational visibility without requiring application changes.

**Acceptance Scenarios**:

1. **Given** the application is running on OKE, **When** an operator runs kubectl logs commands, **Then** application logs and Dapr sidecar logs are visible and contain structured information about requests, events, and errors
2. **Given** Dapr dashboard is deployed, **When** an operator accesses the dashboard, **Then** all Dapr components, sidecars, and their health status are visible in the UI
3. **Given** events are flowing through Kafka, **When** an operator checks Dapr Pub/Sub metrics, **Then** publish/subscribe counts, latencies, and error rates are visible
4. **Given** kubectl-ai or kagent is available, **When** an operator queries cluster health, **Then** AI-powered analysis identifies any issues with pods, resources, or configurations
5. **Given** an error occurs in event processing, **When** an operator reviews logs, **Then** the error is traceable from the originating service through Dapr to the message broker with correlation IDs

---

### Edge Cases

- What happens when the Oracle OKE cluster reaches resource limits (4 OCPU, 24GB RAM) and cannot schedule new pods?
- How does the system handle Kafka broker unavailability or network partitions between OKE and Kafka?
- What happens when Dapr sidecar fails to start or crashes while the application container is running?
- How does the CI/CD pipeline handle deployment failures or rollback scenarios?
- What happens when Kubernetes Secrets are not properly configured or Dapr Secrets API cannot access them?
- How does the system behave when multiple events are published rapidly and Kafka topic partitions become unbalanced?
- What happens when Helm upgrade fails mid-deployment and leaves the cluster in an inconsistent state?
- How does monitoring handle log volume when the system is under heavy load?

## Requirements *(mandatory)*

### Functional Requirements

#### Dapr Integration

- **FR-001**: System MUST deploy Dapr runtime to Oracle OKE cluster using `dapr init -k` command
- **FR-002**: All application deployments (frontend, backend, chat API) MUST include Dapr sidecar annotations (`dapr.io/enabled: "true"`, `dapr.io/app-id`, `dapr.io/app-port`)
- **FR-003**: System MUST configure Dapr Pub/Sub component for Kafka with connection details for either Redpanda Cloud (free tier) or self-hosted Strimzi
- **FR-004**: System MUST configure Dapr State component for PostgreSQL pointing to Neon database
- **FR-005**: System MUST configure Dapr Scheduler/Jobs API component for scheduled task execution
- **FR-006**: System MUST configure Dapr Secrets component to read from Kubernetes Secrets
- **FR-007**: Application code MUST publish events using Dapr HTTP API (`POST /v1.0/publish/{pubsubname}/{topic}`) instead of direct Kafka client libraries
- **FR-008**: Application code MUST access secrets using Dapr Secrets API (`GET /v1.0/secrets/{secretstore}/{key}`) instead of direct environment variables

#### Event-Driven Architecture

- **FR-009**: Chat API MUST publish task-created events to "task-events" Kafka topic when a new task is created
- **FR-010**: Chat API MUST publish task-updated events to "task-updates" Kafka topic when a task is modified
- **FR-011**: Chat API MUST publish task-deleted events to "task-events" Kafka topic when a task is removed
- **FR-012**: System MUST publish reminder events to "reminders" Kafka topic when reminders are triggered
- **FR-013**: Event payloads MUST include task metadata (id, title, description, status, timestamps) in JSON format
- **FR-014**: Event consumers MUST subscribe to topics via Dapr Pub/Sub subscriptions (declarative YAML or programmatic)
- **FR-015**: System MUST handle event publishing failures gracefully with Dapr retry policies

#### Oracle OKE Deployment

- **FR-016**: System MUST deploy to Oracle Cloud Infrastructure Kubernetes Engine (OKE) using always-free tier resources (4 OCPU, 24GB RAM)
- **FR-017**: OKE cluster MUST be configured with appropriate node pools, networking, and security groups
- **FR-018**: Helm chart MUST be updated with Dapr sidecar annotations for all deployments
- **FR-019**: Helm chart MUST include Kubernetes Secrets for COHERE_API_KEY, BETTER_AUTH_SECRET, and NEON_DB_URL
- **FR-020**: Helm chart MUST deploy Dapr component YAML files to the cluster
- **FR-021**: Application MUST be accessible via OKE load balancer with public IP or domain name
- **FR-022**: System MUST use Kafka from either Redpanda Cloud serverless (free tier) or self-hosted Strimzi in the same OKE cluster

#### CI/CD Pipeline

- **FR-023**: GitHub Actions workflow MUST trigger on push to main branch or feature branches
- **FR-024**: Pipeline MUST run automated tests before building Docker images
- **FR-025**: Pipeline MUST build Docker images for frontend and backend with commit SHA tags
- **FR-026**: Pipeline MUST push Docker images to container registry (Docker Hub, GitHub Container Registry, or Oracle Container Registry)
- **FR-027**: Pipeline MUST deploy to OKE using `helm upgrade --install` command with new image tags
- **FR-028**: Pipeline MUST authenticate to OKE cluster using Oracle Cloud credentials or kubeconfig
- **FR-029**: Pipeline MUST report deployment status (success/failure) with detailed logs

#### Monitoring and Observability

- **FR-030**: System MUST expose application logs via kubectl logs command for all pods
- **FR-031**: Dapr sidecar logs MUST be accessible separately from application logs
- **FR-032**: System MUST deploy Dapr dashboard for visualizing component health and metrics
- **FR-033**: Logs MUST include structured information (timestamps, log levels, correlation IDs) for traceability
- **FR-034**: System MUST support kubectl-ai or kagent for AI-powered cluster health analysis
- **FR-035**: Event flow MUST be traceable through logs from publisher to Kafka to subscriber

### Key Entities

- **Dapr Component**: Configuration defining how Dapr sidecars interact with external systems (Kafka, PostgreSQL, Kubernetes Secrets). Includes component type, metadata (connection strings, credentials), and scopes (which apps can use it).

- **Event**: Asynchronous message published to Kafka topics representing task operations or system events. Contains event type, timestamp, task metadata, and correlation ID for tracing.

- **Kafka Topic**: Named channel for event distribution. Three primary topics: "task-events" (create/delete), "task-updates" (modifications), "reminders" (scheduled notifications).

- **OKE Cluster**: Oracle Kubernetes Engine cluster running on always-free tier. Contains node pools, networking configuration, and deployed workloads.

- **Helm Release**: Versioned deployment of the application to OKE. Includes all Kubernetes resources (deployments, services, secrets, Dapr components) managed as a single unit.

- **CI/CD Pipeline**: GitHub Actions workflow automating the build-test-deploy cycle. Consists of stages (test, build, push, deploy) with dependencies and failure handling.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Application is fully accessible on Oracle OKE cluster with all services responding to requests within 2 seconds
- **SC-002**: All Dapr components (kafka-pubsub, state.postgresql, scheduler.jobs, secretstores.kubernetes) report healthy status when queried
- **SC-003**: Task operations trigger events that appear in Kafka topics within 1 second of the operation completing
- **SC-004**: Event consumers successfully receive and process 100% of published events with no message loss
- **SC-005**: CI/CD pipeline completes full deployment cycle (test, build, push, deploy) in under 10 minutes
- **SC-006**: Automated deployment succeeds on first attempt for 95% of commits with passing tests
- **SC-007**: Application logs are accessible via kubectl logs and contain sufficient detail to trace request flow through services
- **SC-008**: Dapr dashboard displays real-time metrics for all sidecars and components
- **SC-009**: System operates within Oracle OKE always-free tier limits (4 OCPU, 24GB RAM) without resource exhaustion
- **SC-010**: Judges can verify decoupled architecture by observing event flow from task operation to Kafka topic to consumer logs
- **SC-011**: Zero direct database connections or Kafka client libraries in application code (all communication via Dapr APIs)
- **SC-012**: Secrets are never exposed in logs, environment variables, or configuration files (accessed only via Dapr Secrets API)

## Scope and Boundaries

### In Scope

- Dapr runtime installation and configuration on Oracle OKE
- Dapr component definitions for Kafka Pub/Sub, PostgreSQL State, Scheduler/Jobs, and Kubernetes Secrets
- Updating existing Helm chart with Dapr sidecar annotations
- Modifying Chat API to publish events via Dapr HTTP API
- Oracle OKE cluster provisioning and configuration (always-free tier)
- GitHub Actions CI/CD pipeline for automated deployment
- Basic monitoring via kubectl logs and Dapr dashboard
- Kafka integration using Redpanda Cloud (free tier) or self-hosted Strimzi
- Documentation for one-command deployment to OKE

### Out of Scope

- Implementing new Todo features (priorities, tags, recurring tasks, reminders, search, filter, sort) - already complete in Phase I-IV
- Deployment to Azure AKS, Google GKE, or local Minikube
- Advanced observability stack (Prometheus, Grafana, Jaeger, full distributed tracing)
- Multi-region or multi-cluster deployments
- Auto-scaling based on metrics
- Service mesh (Istio, Linkerd) beyond Dapr
- Advanced Kafka features (schema registry, exactly-once semantics, compaction)
- Disaster recovery and backup strategies
- Performance testing and load testing infrastructure

### Dependencies

- Oracle Cloud Infrastructure account with access to OKE always-free tier
- Existing application codebase from Phase I-IV with complete Todo features
- Existing Helm chart from Phase IV
- Neon PostgreSQL database (already provisioned)
- Kafka broker (Redpanda Cloud free tier or self-hosted Strimzi)
- GitHub repository with Actions enabled
- Container registry (Docker Hub, GitHub Container Registry, or Oracle Container Registry)
- Dapr CLI and runtime (version 1.12+)

### Assumptions

- Oracle OKE always-free tier provides sufficient resources (4 OCPU, 24GB RAM) for the application and Dapr sidecars
- Redpanda Cloud free tier or self-hosted Strimzi provides adequate Kafka throughput for demo purposes
- Network connectivity between OKE and external services (Neon, Redpanda Cloud) is reliable
- GitHub Actions has sufficient build minutes for CI/CD pipeline
- Existing application code can be modified to add Dapr HTTP API calls without major refactoring
- Judges have access to kubectl and can view logs/dashboards for evaluation
- One-command deployment assumes prerequisites (OKE cluster, Dapr init, secrets) are already configured

## Non-Functional Requirements

### Performance

- Event publishing via Dapr Pub/Sub adds no more than 50ms latency compared to direct Kafka client
- Dapr sidecar memory footprint does not exceed 128MB per pod
- Application startup time with Dapr sidecar does not exceed 30 seconds

### Reliability

- System handles temporary Kafka unavailability with automatic retries (exponential backoff, max 5 attempts)
- Dapr sidecar failures do not crash application containers (independent lifecycle)
- CI/CD pipeline includes rollback capability if deployment health checks fail

### Security

- All secrets accessed via Dapr Secrets API, never hardcoded or exposed in logs
- Kubernetes Secrets encrypted at rest in OKE cluster
- Dapr mTLS enabled for service-to-service communication
- Container images scanned for vulnerabilities before deployment

### Scalability

- Architecture supports horizontal scaling of services (multiple replicas with Dapr sidecars)
- Kafka topics support partitioning for parallel event processing
- OKE cluster can scale within always-free tier limits

### Maintainability

- Dapr components defined in version-controlled YAML files
- Helm chart values externalized for environment-specific configuration
- CI/CD pipeline logs provide clear failure diagnostics
- Documentation includes troubleshooting guide for common issues

## Acceptance Criteria Summary

The feature is considered complete when:

1. ✅ Application is deployed to Oracle OKE with all pods running and Dapr sidecars attached
2. ✅ All Dapr components (kafka-pubsub, state.postgresql, scheduler.jobs, secretstores.kubernetes) are configured and healthy
3. ✅ Task operations publish events to Kafka topics via Dapr Pub/Sub API
4. ✅ Event consumers receive and process events from Kafka topics
5. ✅ GitHub Actions CI/CD pipeline successfully deploys application to OKE on push
6. ✅ Application is accessible via OKE load balancer URL
7. ✅ Kubectl logs show application and Dapr sidecar logs with event flow traceability
8. ✅ Dapr dashboard displays component health and metrics
9. ✅ No direct Kafka client libraries or database connection strings in application code
10. ✅ Secrets accessed only via Dapr Secrets API
11. ✅ README includes one-command deployment instructions for OKE
12. ✅ Judges can verify decoupled, event-driven architecture through logs and dashboard

## Notes

- This specification focuses exclusively on infrastructure, event-driven architecture, Dapr integration, Oracle OKE deployment, CI/CD, and monitoring
- All Todo features (intermediate and advanced) are already implemented in Phase I-IV and are not part of this specification
- The target audience is hackathon judges evaluating the production-grade, cloud-native architecture
- Success depends on demonstrating clean separation of concerns, decoupled services, and observable event flow
