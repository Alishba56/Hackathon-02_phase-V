<!--
Sync Impact Report:
- Version change: 1.2.0 → 1.3.0 (MINOR bump - added Phase V event-driven microservices principles)
- Modified principles: None (Phase II, III, and IV principles preserved)
- Added sections:
  * Principles XXV-XXXVI (Phase V Event-Driven Microservices with Dapr)
  * Phase V Constraints section
  * Phase V Standards section
  * Phase V Success Criteria section
  * Phase V Implementation Sequence
- Removed sections: None
- Templates requiring updates:
  ✅ constitution.md - updated
  ⚠ plan-template.md - review for event-driven architecture and Dapr planning sections
  ⚠ spec-template.md - review for microservices and event specification sections
  ⚠ tasks-template.md - review for event-driven and Dapr task categories
- Follow-up TODOs: None
-->

# Phase V – Advanced Cloud-Native Todo AI Chatbot Constitution

## Project Overview

**Project**: Phase V – Advanced Cloud-Native Todo AI Chatbot (Event-Driven Microservices + Dapr + Production Kubernetes)

**Objective**: Evolve the Phase IV cloud-native application into a production-grade, event-driven microservices architecture using Dapr for portability, Kafka/Redpanda for event streaming, and deploy to production Kubernetes clusters (Oracle OKE, Azure AKS, or Google GKE) with full CI/CD automation, advanced features (recurring tasks, reminders, priorities, tags, search), and AI-augmented DevOps.

## Core Principles

### I. Fully Spec-Driven and Agentic Development
All development MUST follow spec-driven methodology where every feature is defined in advance in the /specs folder before implementation begins. All code generation MUST be performed through Claude Code agents using Spec-Kit references, with zero manual coding allowed. Every implementation step MUST be traceable through Prompt History Records (PHRs).

**Rationale**: Ensures complete traceability, reproducibility, and adherence to architectural decisions throughout the development lifecycle.

### II. Zero Manual Coding Enforcement
No hand-written code is permitted - all implementation MUST be generated via Claude Code using references to specifications in the /specs folder. Every line of code MUST be traceable back to a specific requirement in the specs.

**Rationale**: Maintains consistency with the agentic development approach and ensures all code is generated from verified specifications.

### III. Modular Architecture Through Agents and Skills
System architecture MUST utilize modular agent design with defined responsibilities: Main Agent, Task Agent, Auth Agent, UI Agent, and Chat Agent. Each agent MUST have clearly defined skills and interfaces to ensure loose coupling and maintainability.

**Rationale**: Enables independent development, testing, and scaling of different system components.

### IV. Complete User Isolation and Data Ownership
Every API endpoint MUST require valid JWT token authentication and filter data by authenticated user_id. Users MUST only access their own data with strict enforcement of data ownership boundaries to prevent any cross-user data leakage. This applies to tasks, conversations, and messages.

**Rationale**: Ensures data security, privacy compliance, and prevents unauthorized access across user boundaries.

### V. Strict Technology Stack Adherence
Implementation MUST use only the specified technology stack: Next.js 16+ (App Router), FastAPI, SQLModel, Neon Serverless PostgreSQL, Better Auth (JWT), Tailwind CSS, Cohere API (command-r-plus or command-r), and Official MCP SDK. No external libraries beyond the specified stack are permitted without explicit justification.

**Rationale**: Maintains consistency, reduces complexity, and ensures compatibility across all system components.

### VI. Monorepo Structure Compliance
Adherence to the defined monorepo structure with proper separation of frontend/ and backend/ directories. All files and folders MUST be created exactly as per the monorepo specification structure. New Phase III artifacts MUST be organized under /specs/agents/ and /specs/skills/. Phase IV infrastructure artifacts MUST be organized under /specs/infra/.

**Rationale**: Maintains project organization and enables efficient navigation and maintenance.

### VII. Cohere-First LLM Architecture
Use Cohere API exclusively for all LLM operations (command-r-plus or command-r model). Adapt OpenAI Agents SDK patterns to work with Cohere's tool-calling capabilities, structured outputs, and chat completions API. NO OpenAI API calls are permitted.

**Rationale**: Demonstrates platform flexibility and leverages Cohere's enterprise-grade tool-calling capabilities for production-ready agent systems.

### VIII. Stateless and Scalable Chat Architecture
Zero in-memory session state - all conversation history MUST be persisted in database (conversations + messages tables). Server restarts MUST NOT lose conversation context. Every chat request MUST load context from database and store results after processing.

**Rationale**: Enables horizontal scaling, fault tolerance, and ensures conversation continuity across server restarts.

### IX. MCP Tool Standard Compliance
All agent-tool interactions MUST follow Model Context Protocol (MCP) standards. Expose all task operations (add_task, list_tasks, complete_task, delete_task, update_task) and user profile (get_user_profile) as MCP-compatible tools with strict schemas.

**Rationale**: Provides standardized, type-safe interface for agent-tool communication and enables future extensibility.

### X. Security-First Chat Operations
All chat endpoints MUST be protected by JWT authentication. user_id MUST be extracted from token and enforced on all operations. Strict task and conversation ownership isolation MUST prevent data leakage. All MCP tools MUST validate user_id before execution.

**Rationale**: Maintains security posture consistent with Phase II and prevents unauthorized access to user data through chat interface.

### XI. Natural Language and Multilingual Support
Agent MUST understand natural language intents in English and Urdu. Handle task management commands naturally (e.g., "Add task buy milk", "Show pending tasks", "Mera profile batao", "Mark task 4 complete"). Provide contextual, friendly responses with action confirmations.

**Rationale**: Enhances user experience and demonstrates AI capabilities for diverse user bases.

### XII. Zero Breaking Changes to Phase II
Phase II functionality (task CRUD API, auth, frontend) MUST remain fully operational. Chatbot is an additive feature only. All existing endpoints, authentication flows, and UI components MUST continue to work without modification.

**Rationale**: Ensures backward compatibility and allows incremental adoption of AI features.

### XIII. Database-Driven Conversation Context
Conversation history MUST be loaded from database on every request. User and assistant messages MUST be stored after processing. Context continuity MUST be maintained across sessions and server restarts.

**Rationale**: Enables stateless server architecture while maintaining rich conversational context.

### XIV. Friendly and Contextual Agent Behavior
Agent MUST provide action confirmations, graceful error handling, and helpful responses. Tool call results MUST be visible in responses. Error messages MUST be user-friendly and actionable.

**Rationale**: Ensures positive user experience and builds trust in AI-powered features.

### XV. Production-Ready Implementation Standards
All code MUST use Pydantic models for validation, comprehensive error handling, Swagger documentation, environment-based configuration, and docker-compose deployment support.

**Rationale**: Ensures code quality, maintainability, and production readiness.

### XVI. Complete Traceability Through PHRs
All implementation MUST be traceable through Prompt History Records (PHRs) stored in history/prompts/. Every significant decision MUST be documented. All @specs references MUST be recorded.

**Rationale**: Provides complete audit trail and enables learning from implementation decisions.

### XVII. AI-Powered Infrastructure Automation
All infrastructure operations MUST prioritize AI-powered tools over manual commands. Use Gordon (Docker AI Agent) for containerization, kubectl-ai for Kubernetes resource generation, and kagent for cluster analysis and debugging. Manual kubectl, helm, or docker commands are permitted only as fallback when AI tools are unavailable.

**Rationale**: Demonstrates cutting-edge AI-augmented DevOps workflows and reduces human error in infrastructure management.

### XVIII. Container-First Application Design
Both frontend (Next.js) and backend (FastAPI) MUST be containerized with production-ready Dockerfiles. Images MUST be optimized (multi-stage builds, minimal base images, proper layer caching). All application dependencies MUST be explicitly declared and version-pinned.

**Rationale**: Ensures consistent deployment across environments and enables cloud-native orchestration.

### XIX. Helm-Based Deployment Management
All Kubernetes resources MUST be managed through Helm charts with proper templating, values.yaml configuration, and release versioning. Charts MUST include deployments, services, ingress, secrets, and configmaps. No raw kubectl apply of manifests in production workflow.

**Rationale**: Provides declarative, version-controlled, and repeatable deployment process with easy rollback capabilities.

### XX. Local Kubernetes Development Parity
Minikube deployment MUST mirror production Kubernetes architecture. All services MUST be accessible via Ingress with proper host mapping (e.g., todo.local). Local development MUST use the same Helm charts and configuration patterns as production.

**Rationale**: Ensures "develop locally, deploy anywhere" philosophy and catches deployment issues early.

### XXI. Secrets and Configuration Management
All sensitive data (JWT secrets, API keys, database credentials) MUST be injected via Kubernetes Secrets. Non-sensitive configuration MUST use ConfigMaps. NO hardcoded secrets in container images or Helm charts. Environment-specific values MUST be externalized in values.yaml.

**Rationale**: Maintains security best practices and enables environment-specific configuration without code changes.

### XXII. Observability and Health Monitoring
All pods MUST implement readiness and liveness probes. Application logs MUST be structured and accessible via kubectl logs. Resource requests and limits MUST be defined for all containers. Cluster health MUST be verifiable through kubectl-ai analysis.

**Rationale**: Enables proactive issue detection, proper resource allocation, and production-grade reliability.

### XXIII. Zero-Downtime Deployment Strategy
All deployments MUST use rolling update strategy with proper readiness checks. Database migrations MUST be backward-compatible. Application MUST handle graceful shutdown. No service interruption during updates.

**Rationale**: Ensures high availability and professional deployment practices.

### XXIV. Infrastructure as Code Traceability
All infrastructure changes MUST be traceable to specifications in @specs/infra/. Dockerfiles, Helm charts, and Kubernetes manifests MUST reference their source specs. Infrastructure evolution MUST follow the same spec-driven workflow as application code.

**Rationale**: Maintains consistency with agentic development principles and ensures infrastructure changes are documented and reviewable.

### XXV. Event-Driven Architecture Mandate
System MUST adopt event-driven architecture with clear separation between producers and consumers. All state changes (task creation, updates, completion, deletion) MUST publish events to Kafka/Redpanda topics. Specialized consumer services MUST process events asynchronously. NO direct synchronous calls between services for state propagation.

**Rationale**: Enables loose coupling, independent scaling, fault tolerance, and supports advanced features like notifications, audit trails, and recurring task automation.

### XXVI. Dapr Abstraction Layer Enforcement
ALL infrastructure concerns (Pub/Sub, State Management, Service Invocation, Secrets, Scheduler/Jobs) MUST be accessed exclusively through Dapr APIs. NO direct Kafka client libraries, database drivers, or service mesh configurations in application code. Dapr components MUST be swappable via YAML configuration only.

**Rationale**: Achieves true cloud portability, vendor independence, and simplifies application code by delegating infrastructure complexity to Dapr sidecars.

### XXVII. Microservices Decomposition
System MUST decompose into specialized services: Chat API (producer), Notification Service (consumer), Recurring Task Service (consumer), Audit Service (consumer), WebSocket Service (consumer). Each service MUST have single responsibility, independent deployment, and communicate only via events or Dapr service invocation.

**Rationale**: Enables independent development, scaling, and deployment of features while maintaining system cohesion through event contracts.

### XXVIII. Advanced Features Implementation
System MUST implement production-grade task management features: recurring tasks (cron-like patterns with auto-spawning), exact-time reminders (via Dapr Jobs API), priorities (low/medium/high/urgent), tags (array-based), full-text search, and comprehensive filtering/sorting (by due_date, priority, status, tags).

**Rationale**: Demonstrates enterprise-grade functionality and differentiates from basic CRUD applications in hackathon evaluation.

### XXIX. Kafka/Redpanda Event Backbone
Event streaming MUST use Kafka (Strimzi self-hosted in-cluster) or Redpanda (Cloud serverless free tier). Topics MUST include: task-events, reminders, task-updates. Events MUST follow CloudEvents specification for standardization. Dapr Pub/Sub component MUST abstract the underlying message broker.

**Rationale**: Provides reliable, scalable event streaming with industry-standard tooling while maintaining flexibility through Dapr abstraction.

### XXX. Production Kubernetes Deployment
Application MUST deploy to production-grade Kubernetes clusters: Oracle OKE (always-free tier preferred), Azure AKS, or Google GKE. Deployment MUST use same Helm charts as local Minikube with environment-specific values. NO vendor-specific configurations in application code or base Helm templates.

**Rationale**: Proves production readiness and cloud portability while leveraging free-tier resources for cost-effective demonstration.

### XXXI. CI/CD Automation with GitHub Actions
ALL deployments MUST be automated through GitHub Actions pipelines. Pipeline MUST include: test execution, Docker image building/pushing, Helm chart deployment to staging, and promotion to production. NO manual kubectl apply or helm install in production workflow.

**Rationale**: Ensures repeatable, auditable deployments and demonstrates modern DevOps practices essential for production systems.

### XXXII. Dapr Scheduler and Jobs API for Reminders
Exact-time reminders MUST use Dapr Jobs API (scheduler component) with NO polling mechanisms. Jobs MUST be created when tasks with due dates are added. Job execution MUST trigger reminder events. Recurring tasks MUST use scheduler for next occurrence calculation.

**Rationale**: Provides efficient, scalable reminder system without resource-intensive polling and leverages Dapr's built-in scheduling capabilities.

### XXXIII. Multi-Environment Configuration Management
System MUST support seamless deployment across local (Minikube), staging, and production environments through Helm values files only. Environment-specific configurations (database URLs, Kafka endpoints, replica counts, resource limits) MUST be externalized. NO environment-specific code branches.

**Rationale**: Enables "build once, deploy anywhere" philosophy and reduces configuration drift across environments.

### XXXIV. Comprehensive Monitoring and Observability
System MUST implement structured logging (JSON format), distributed tracing (via Dapr), metrics collection (Prometheus-compatible), and health monitoring. Dapr dashboard MUST be accessible for sidecar monitoring. kubectl-ai/kagent MUST be used for intelligent cluster analysis and optimization.

**Rationale**: Provides visibility into distributed system behavior, enables proactive issue detection, and demonstrates production-grade operational practices.

### XXXV. Zero Vendor Lock-In Through Dapr
System architecture MUST demonstrate vendor independence by supporting component swaps: Kafka ↔ Redis Pub/Sub, PostgreSQL ↔ Redis State Store, Kubernetes Secrets ↔ Azure Key Vault. Swaps MUST require ONLY Dapr component YAML changes with NO code modifications.

**Rationale**: Proves architectural flexibility and Dapr's value proposition for multi-cloud and hybrid deployments.

### XXXVI. Backward Compatibility Preservation
Phase IV functionality (Kubernetes deployment, AI chatbot, task CRUD) MUST remain fully operational. Event-driven features are additive only. Existing APIs MUST continue to work. Migration to microservices MUST be transparent to frontend users.

**Rationale**: Ensures incremental evolution without breaking existing functionality and allows phased rollout of advanced features.

## Phase II Constraints (Preserved)

### Technology Stack Lock
Technology stack is fixed: Next.js 16+ (App Router), FastAPI, SQLModel, Neon Serverless PostgreSQL, Better Auth (JWT), Tailwind CSS. No deviations from this stack are allowed.

### Database Access Policy
No direct database access from frontend - all operations MUST go through protected FastAPI endpoints. No session storage on backend – authentication MUST be stateless using JWT only.

### Data Security Requirements
All CRUD operations MUST enforce task ownership (user can only access their own tasks). Better Auth MUST be configured with JWT plugin and shared BETTER_AUTH_SECRET between frontend and backend.

### Database Schema Compliance
Database schema MUST match specifications exactly (users table managed by Better Auth, tasks table with user_id foreign key). All references in prompts MUST use @specs/path/to/file.md format.

## Phase III Constraints (Preserved)

### LLM Provider Lock
Use Cohere API exclusively (no OpenAI calls). Adapt OpenAI Agents SDK patterns to Cohere's chat/tool-calling API. Model: command-r-plus or command-r with tool calling enabled.

### Minimal External Dependencies
No new external libraries beyond Cohere SDK (cohere-python) and Official MCP SDK. Reuse existing Phase II dependencies wherever possible.

### Environment Configuration
Add COHERE_API_KEY environment variable. Reuse existing BETTER_AUTH_SECRET and NEON_DB_URL. All secrets MUST be environment-based, never hardcoded.

### Stateless Server Architecture
No in-memory session state. All conversation state MUST be in database. Server MUST be horizontally scalable.

### Authentication Scope
Public auth routes (signup/signin) remain unchanged. Chat endpoint MUST be fully protected with JWT. Reuse existing get_current_user dependency.

### Communication Protocol
No real-time (WebSockets) - single-turn stateless HTTP requests only. Each request is independent and loads context from database.

### Feature Scope Boundaries
No advanced features like multi-agent swarms, voice, image generation, or real-time streaming. Keep to text-based task management and user profile queries only.

### Integration Timeline
Integrate without disrupting Phase II task CRUD UI/API. Phased rollout: backend first, then frontend integration.

## Phase IV Constraints

### Deployment Target Lock
Deployment target is local Minikube only. No cloud Kubernetes clusters (EKS, GKE, AKS). Single-node cluster configuration for demo purposes.

### AI Tool Priority
Gordon (Docker AI Agent) MUST be used for containerization when available (Docker Desktop 4.53+ Beta). kubectl-ai and kagent MUST be used for all Kubernetes operations where applicable. Manual commands only as documented fallback.

### Helm Chart Generation
Helm charts MUST be generated by Claude Code or kubectl-ai. No manual helm create or hand-written templates. All chart modifications MUST be traceable to specs.

### Database Strategy
Neon Serverless PostgreSQL can remain as external service OR migrate to local PostgreSQL pod for full local demo. Database connection MUST work in both scenarios through environment configuration.

### No Cloud Resources
No production cloud infrastructure. No cloud load balancers, cloud storage, or managed services beyond Neon DB (which can be replaced with local Postgres).

### Code Preservation
Existing Phase III application code (frontend/, backend/) MUST remain untouched. Only add infrastructure layer (Dockerfiles, Helm charts, K8s configs). No refactoring of application logic.

### Environment Injection
All environment variables MUST be injected via Kubernetes Secrets or ConfigMaps. No .env files in container images. Values MUST be externalized in Helm values.yaml.

### Ingress Requirement
Application MUST be accessible via Ingress controller with proper host-based routing (e.g., http://todo.local). No NodePort or port-forwarding in final demo.

## Phase V Constraints

### Production Kubernetes Target
Deployment target is production-grade Kubernetes: Oracle OKE (always-free tier, 4 OCPU/24GB RAM, preferred), Azure AKS, or Google GKE. Local Minikube MUST remain functional for development. Multi-environment support (local, staging, production) is mandatory.

### Event Streaming Platform
Kafka via Strimzi (self-hosted in-cluster, free) OR Redpanda Cloud (serverless free tier). NO paid Kafka services (Confluent Cloud, AWS MSK). Dapr Pub/Sub component MUST abstract the broker choice.

### Dapr-Only Infrastructure Access
NO direct client libraries for Kafka, PostgreSQL, Redis, or service mesh in application code. ALL infrastructure interactions MUST go through Dapr HTTP/gRPC APIs. Dapr components MUST be defined in /infra/dapr-components/ YAML files only.

### Microservices Code Isolation
New consumer services (Notification, Recurring Task, Audit, WebSocket) MUST be minimal Python/FastAPI services in /services/ directory. Existing Phase IV code (frontend/, backend/) MUST remain unchanged except for Dapr sidecar annotations and event publishing logic.

### CI/CD Platform Lock
GitHub Actions ONLY for CI/CD pipelines. NO ArgoCD, Tekton, Jenkins, or GitLab CI. Pipeline definition MUST be in .github/workflows/ with clear staging and production deployment stages.

### Free Tier Compliance
NO paid services beyond free credits/tiers. Oracle OKE always-free tier (preferred), Redpanda Cloud free tier, Neon DB free tier, GitHub Actions free tier. All infrastructure MUST fit within free resource limits.

### Database Continuity
Neon Serverless PostgreSQL MUST remain as external database (consistent with previous phases). NO migration to in-cluster PostgreSQL unless explicitly required for demo. Dapr State Store can use PostgreSQL or Redis based on performance needs.

### Helm Chart Evolution
Existing Phase IV Helm charts MUST be upgraded (not replaced) with Dapr sidecar annotations, Dapr component definitions, and new microservice deployments. Chart version MUST increment following semantic versioning.

### Secrets Management
All secrets (JWT, Cohere API key, database credentials, Kafka credentials) MUST be injected via Kubernetes Secrets. Dapr Secrets component MUST use kubernetes secret store. NO external secret managers (HashiCorp Vault, Azure Key Vault) in initial implementation.

### Monitoring Scope
Basic monitoring via kubectl-ai/kagent analysis, Dapr dashboard, and pod logs is mandatory. Prometheus/Grafana setup is optional (nice-to-have). NO paid monitoring services (Datadog, New Relic).

## Phase III Standards (Preserved)

### Chat Endpoint Specification
- **Route**: `POST /api/{user_id}/chat`
- **Authentication**: JWT required (user_id from token)
- **Request**: `{conversation_id?: string, message: string}`
- **Response**: `{conversation_id: string, response: string, tool_calls: array}`

### MCP Tools Specification
MUST implement exactly these tools with strict schemas:
- `add_task(user_id, title, description?, priority?, due_date?)`
- `list_tasks(user_id, status?, sort?)`
- `complete_task(user_id, task_id)`
- `delete_task(user_id, task_id)`
- `update_task(user_id, task_id, updates)`
- `get_user_profile(user_id)` → returns {id, email, name, createdAt}

All tools MUST require user_id and enforce ownership.

### Conversation Storage
- **conversations table**: id, user_id, created_at, updated_at
- **messages table**: id, conversation_id, role (user/assistant), content, tool_calls, created_at
- All queries MUST filter by authenticated user_id

### Agent Behavior Requirements
- Understand natural language intents (English + Urdu)
- Parse commands: "Add task X", "Show tasks", "Complete task N", "Delete task N", "Update task N", "My profile"
- Provide confirmations: "✓ Task added: buy milk"
- Handle errors gracefully: "Task not found. Please check the task ID."
- Show tool calls in response for transparency

### Cohere Integration
- API key via COHERE_API_KEY environment variable
- Model: command-r-plus (preferred) or command-r
- Enable tool calling with MCP tool definitions
- Use structured outputs for reliability
- Handle rate limits and API errors gracefully

### Validation and Error Handling
- Pydantic models for all request/response schemas
- Validate user_id from JWT on every request
- Return 401 for auth failures
- Return 404 for task/conversation not found
- Return 400 for invalid input with helpful messages
- Return 403 for ownership violations

### API Documentation
- Update Swagger docs to include /api/{user_id}/chat endpoint
- Document all MCP tools with schemas
- Provide example requests and responses
- Include authentication requirements

### Frontend Integration
- Integrate OpenAI ChatKit (or compatible Cohere-compatible chat UI)
- New page/route in Next.js app
- Call backend /api/{user_id}/chat with JWT in Authorization header
- Display conversation history and tool call results
- Handle loading states and errors

### Domain Allowlist
Prepare for ChatKit hosted mode - document domain allowlist setup in README for production deployment.

## Phase IV Standards

### Dockerfile Standards
- **Frontend Dockerfile**:
  - Multi-stage build (build stage + production stage)
  - Base: node:20-alpine or node:20-slim
  - Build artifacts only in final stage
  - Non-root user execution
  - Health check endpoint exposed
  - Environment variables for API URL configuration

- **Backend Dockerfile**:
  - Multi-stage build (dependencies + runtime)
  - Base: python:3.11-slim or python:3.11-alpine
  - Virtual environment for dependencies
  - Non-root user execution
  - Health check endpoint exposed
  - Uvicorn with proper worker configuration

### Helm Chart Structure
```
todo-app/
├── Chart.yaml (name, version, description)
├── values.yaml (all configurable parameters)
├── templates/
│   ├── deployment-frontend.yaml
│   ├── deployment-backend.yaml
│   ├── service-frontend.yaml
│   ├── service-backend.yaml
│   ├── ingress.yaml
│   ├── secrets.yaml
│   ├── configmap.yaml
│   └── _helpers.tpl
```

### Kubernetes Resource Specifications
- **Deployments**:
  - Replicas: 1 (local), configurable via values.yaml
  - Rolling update strategy: maxSurge=1, maxUnavailable=0
  - Resource requests and limits defined
  - Readiness probe: HTTP GET /health or /api/health
  - Liveness probe: HTTP GET /health or /api/health
  - Environment variables from secrets/configmaps

- **Services**:
  - Type: ClusterIP (internal communication)
  - Proper port mapping (frontend: 3000, backend: 8000)
  - Selector labels matching deployments

- **Ingress**:
  - Host: todo.local (or configurable)
  - Path-based routing: / → frontend, /api → backend
  - Annotations for ingress controller (nginx)

- **Secrets**:
  - BETTER_AUTH_SECRET (base64 encoded)
  - COHERE_API_KEY (base64 encoded)
  - DATABASE_URL (base64 encoded)

- **ConfigMaps**:
  - Non-sensitive configuration
  - API URLs, feature flags, etc.

### Minikube Setup Requirements
- Minikube version: 1.32+
- Driver: docker (preferred) or virtualbox
- Addons enabled: ingress, metrics-server
- Host file entry: `127.0.0.1 todo.local`
- Resource allocation: 4GB RAM, 2 CPUs minimum

### AI Tool Usage Standards
- **Gordon**: Use for generating Dockerfiles with `docker ai` commands
- **kubectl-ai**: Use for generating K8s manifests, analyzing deployments, suggesting optimizations
- **kagent**: Use for cluster health analysis, debugging pod failures, log analysis

### Deployment Workflow
1. Build Docker images (via Gordon or Claude-generated Dockerfiles)
2. Load images into Minikube: `minikube image load <image>`
3. Install Helm chart: `helm install todo-app ./todo-app`
4. Verify deployment: `kubectl get pods,svc,ingress`
5. Access application: http://todo.local

### Observability Standards
- Structured logging (JSON format preferred)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Health endpoints: /health (frontend), /api/health (backend)
- Resource monitoring via kubectl top pods
- Event monitoring via kubectl get events

## Phase V Standards

### Event Schema Standards
- **Event Format**: CloudEvents 1.0 specification
- **Required Fields**: id, source, specversion, type, datacontenttype, data
- **Event Types**:
  - `com.todo.task.created` - Task creation events
  - `com.todo.task.updated` - Task update events
  - `com.todo.task.completed` - Task completion events
  - `com.todo.task.deleted` - Task deletion events
  - `com.todo.reminder.due` - Reminder trigger events
  - `com.todo.task.recurring.spawn` - Recurring task spawn events
- **Data Payload**: JSON with task_id, user_id, timestamp, and event-specific fields
- **Idempotency**: All events MUST include unique event ID for deduplication

### Dapr Component Standards
- **Pub/Sub Component** (pubsub.yaml):
  - Type: pubsub.kafka or pubsub.redis
  - Metadata: brokers, consumerGroup, clientId
  - Scopes: chat-api, notification-service, recurring-service, audit-service

- **State Store Component** (statestore.yaml):
  - Type: state.postgresql or state.redis
  - Metadata: connectionString, tableName
  - Features: transactions, etags, ttl

- **Scheduler Component** (scheduler.yaml):
  - Type: scheduler.kubernetes
  - Metadata: namespace, jobNamespace

- **Secrets Component** (secrets.yaml):
  - Type: secretstores.kubernetes
  - Metadata: vaultName (optional for cloud)

### Kafka Topic Standards
- **Topic Naming**: kebab-case (task-events, reminders, task-updates)
- **Partitions**: 3 (local), 6+ (production) for parallelism
- **Replication Factor**: 1 (local), 3 (production) for durability
- **Retention**: 7 days (configurable via Helm values)
- **Compression**: snappy or lz4 for efficiency
- **Consumer Groups**: One per service (notification-group, recurring-group, audit-group)

### Microservices Architecture Standards
- **Service Structure**:
  ```
  /services/<service-name>/
  ├── app/
  │   ├── main.py (FastAPI app with Dapr subscription)
  │   ├── handlers.py (event handlers)
  │   ├── models.py (Pydantic models)
  │   └── dapr_client.py (Dapr HTTP/gRPC client wrapper)
  ├── Dockerfile
  ├── requirements.txt
  └── README.md
  ```

- **Service Responsibilities**:
  - **Chat API**: Publishes task events via Dapr Pub/Sub
  - **Notification Service**: Consumes reminder events, sends notifications (log/email stub)
  - **Recurring Task Service**: Consumes completion events, spawns next occurrence
  - **Audit Service**: Consumes all task events, logs to audit trail
  - **WebSocket Service**: Consumes task updates, broadcasts to connected clients (optional)

### Advanced Features Implementation Standards
- **Recurring Tasks**:
  - Cron expression support: `0 9 * * 1` (every Monday 9 AM)
  - Interval support: `every 3 days`, `every 2 weeks`
  - Next occurrence calculation on completion
  - Auto-spawn via Recurring Task Service
  - Store pattern in `recurrence_pattern` field (TEXT)

- **Reminders**:
  - Exact datetime in `due_date` field (TIMESTAMP WITH TIMEZONE)
  - Dapr Job created on task creation with due date
  - Job triggers reminder event at exact time
  - Notification Service processes reminder event
  - NO polling mechanisms allowed

- **Priorities**:
  - Enum: low, medium, high, urgent
  - Database field: `priority` (VARCHAR or ENUM)
  - Default: medium
  - Sortable and filterable

- **Tags**:
  - Array field: `tags` (JSONB or TEXT[])
  - Support multiple tags per task
  - Searchable via array contains queries
  - Filter by single or multiple tags

- **Search and Filtering**:
  - Full-text search on title and description (PostgreSQL tsvector)
  - Filter by: status, priority, tags, due_date range, user_id
  - Sort by: created_at, due_date, priority, status
  - Pagination support (limit, offset)

### Helm Chart Upgrade Standards
- **Chart Version**: Increment from Phase IV (e.g., 0.2.0 → 0.3.0)
- **New Templates**:
  - `deployment-notification.yaml`
  - `deployment-recurring.yaml`
  - `deployment-audit.yaml`
  - `deployment-websocket.yaml` (optional)
  - `dapr-components.yaml` (or separate files in templates/dapr/)
  - `kafka-strimzi.yaml` (if self-hosted)

- **Dapr Annotations** (add to all deployments):
  ```yaml
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "<service-name>"
    dapr.io/app-port: "<service-port>"
    dapr.io/log-level: "info"
    dapr.io/enable-metrics: "true"
  ```

- **Values.yaml Additions**:
  - Dapr configuration (enabled, version, components)
  - Kafka configuration (broker URLs, topics, partitions)
  - Microservices configuration (replicas, resources, images)
  - Advanced features flags (recurring, reminders, search)

### CI/CD Pipeline Standards
- **Pipeline Stages**:
  1. **Test**: Run unit tests, integration tests, linting
  2. **Build**: Build Docker images for all services
  3. **Push**: Push images to container registry (GitHub Container Registry)
  4. **Deploy Staging**: Deploy to staging environment with Helm
  5. **Smoke Test**: Run basic health checks on staging
  6. **Deploy Production**: Deploy to production with approval gate

- **GitHub Actions Workflow** (.github/workflows/deploy.yml):
  - Trigger: push to main branch
  - Secrets: KUBECONFIG, REGISTRY_TOKEN, COHERE_API_KEY
  - Artifacts: Helm chart, Docker images
  - Notifications: Slack/Discord webhook on success/failure

- **Image Tagging Strategy**:
  - Development: `latest`
  - Staging: `staging-<git-sha>`
  - Production: `v<semver>` (e.g., v1.0.0)

### Production Kubernetes Standards
- **Cluster Requirements**:
  - Kubernetes version: 1.28+
  - Nodes: 2+ (for HA), 1 acceptable for free tier
  - Storage class: default or gp2/standard
  - Ingress controller: nginx or cloud provider

- **Oracle OKE Specific** (preferred):
  - Shape: VM.Standard.E2.1.Micro (always-free)
  - Nodes: 2 (within free tier limits)
  - Region: Any with free tier availability
  - Network: VCN with public subnet for ingress

- **Resource Allocation**:
  - Frontend: 256Mi RAM, 0.25 CPU (requests), 512Mi RAM, 0.5 CPU (limits)
  - Backend: 512Mi RAM, 0.5 CPU (requests), 1Gi RAM, 1 CPU (limits)
  - Microservices: 256Mi RAM, 0.25 CPU (requests), 512Mi RAM, 0.5 CPU (limits)
  - Kafka (if in-cluster): 1Gi RAM, 1 CPU (requests), 2Gi RAM, 2 CPU (limits)

- **High Availability**:
  - Replicas: 2+ for critical services (frontend, backend)
  - Pod Disruption Budgets: minAvailable=1
  - Anti-affinity rules: spread across nodes (if multi-node)

### Monitoring and Observability Standards
- **Dapr Dashboard**:
  - Accessible via port-forward or ingress
  - Monitor sidecar health, metrics, logs

- **kubectl-ai/kagent Usage**:
  - Cluster health analysis: `kagent analyze cluster`
  - Pod debugging: `kagent debug pod <name>`
  - Resource optimization: `kubectl-ai optimize deployment <name>`
  - Log analysis: `kagent logs <service> --analyze`

- **Structured Logging**:
  - Format: JSON with timestamp, level, service, message, context
  - Fields: user_id, task_id, event_id, trace_id (Dapr)
  - Centralized: kubectl logs aggregation or optional Loki

- **Metrics** (optional Prometheus):
  - Dapr metrics: request latency, error rate, throughput
  - Application metrics: task operations, event processing rate
  - Infrastructure metrics: CPU, memory, disk, network

### Security Standards
- **Network Policies** (optional):
  - Restrict inter-service communication
  - Allow only necessary ingress/egress

- **Pod Security**:
  - Run as non-root user
  - Read-only root filesystem where possible
  - Drop all capabilities except required

- **Secrets Rotation**:
  - Document rotation procedure
  - Support external secret stores (future)

- **TLS/HTTPS**:
  - Ingress with TLS termination (cert-manager optional)
  - Internal service mesh encryption (optional via Dapr mTLS)

## Phase III Success Criteria (Preserved)

### Functional Requirements
1. ✅ Chatbot fully manages tasks via natural language: add, list (with filters), complete, delete, update
2. ✅ User profile queries work: "Mera email kya hai?" returns id, email, name, createdAt
3. ✅ Conversation context preserved across requests via DB persistence
4. ✅ Conversation resumes correctly after server restart
5. ✅ All operations secure: JWT required, user_id enforced, no cross-user access

### Technical Requirements
1. ✅ Agent uses Cohere for reasoning/tool selection
2. ✅ Successful tool calls visible in response (tool_calls array)
3. ✅ Endpoint returns correct format: {conversation_id, response, tool_calls}
4. ✅ Zero regressions in Phase II functionality (task CRUD, auth)
5. ✅ Runs locally with docker-compose (frontend + backend + Neon)

### Integration Requirements
1. ✅ Full integration: Frontend ChatKit UI tab/page calling backend chat endpoint
2. ✅ JWT attachment working correctly
3. ✅ Conversation history displays properly
4. ✅ Tool call results shown to user

### Quality Requirements
1. ✅ Friendly confirmations for all actions
2. ✅ Graceful error handling with helpful messages
3. ✅ Multilingual support (English + Urdu) working
4. ✅ Response times acceptable (<2s for typical requests)

### Deliverables
1. ✅ Updated monorepo: New specs in /specs/agents/ and /specs/skills/
2. ✅ Backend additions: /api/{user_id}/chat endpoint, Cohere agent runner, MCP tools
3. ✅ DB schema extensions: Conversation and Message tables
4. ✅ Frontend: ChatKit integration in Next.js
5. ✅ README updates: Cohere API key setup, domain allowlist, run instructions
6. ✅ Complete traceable history of spec-driven prompts (@specs references)
7. ✅ Working end-to-end: Natural language chat controls entire Todo app + user info

### Demo Validation
Judges confirm: "Seamless Phase III upgrade – agentic, secure, scalable, Cohere-powered, fully spec-driven"

## Phase IV Success Criteria

### Infrastructure Requirements
1. ⬜ Minikube cluster running with all required addons (ingress, metrics-server)
2. ⬜ Frontend and backend containerized with production-ready Dockerfiles
3. ⬜ Helm chart successfully generated and deployed
4. ⬜ All pods in Running state with 1/1 Ready status
5. ⬜ Services properly configured and reachable within cluster
6. ⬜ Ingress configured with todo.local host mapping
7. ⬜ Application accessible via http://todo.local in browser

### Application Functionality in Kubernetes
1. ⬜ User authentication working (signup/signin)
2. ⬜ Task CRUD operations fully functional
3. ⬜ AI Chatbot responding to natural language commands
4. ⬜ All Phase III features working identically in K8s environment
5. ⬜ Database connectivity working (Neon or local Postgres)
6. ⬜ JWT authentication enforced across all protected endpoints
7. ⬜ User isolation maintained in K8s deployment

### AI-Powered DevOps Demonstration
1. ⬜ Gordon used for Dockerfile generation (or Claude-generated with documentation)
2. ⬜ kubectl-ai used for at least 3 operations (deploy, scale, analyze)
3. ⬜ kagent used for cluster health analysis and debugging
4. ⬜ All AI tool interactions documented in PHRs
5. ⬜ Demo script showing intelligent operations (scale, health check, issue resolution)

### Observability and Reliability
1. ⬜ All pods have readiness and liveness probes configured
2. ⬜ Logs accessible via kubectl logs for all pods
3. ⬜ Resource requests and limits defined for all containers
4. ⬜ Health endpoints responding correctly
5. ⬜ No crash loops or restart cycles
6. ⬜ kubectl-ai analysis shows healthy cluster state

### Security and Configuration
1. ⬜ All secrets injected via Kubernetes Secrets (no hardcoded values)
2. ⬜ ConfigMaps used for non-sensitive configuration
3. ⬜ No .env files in container images
4. ⬜ Environment-specific values externalized in values.yaml
5. ⬜ Containers running as non-root users

### Spec-Driven Traceability
1. ⬜ All infrastructure specs created under @specs/infra/
2. ⬜ Architecture spec documenting K8s design decisions
3. ⬜ Helm chart spec with all template requirements
4. ⬜ Deployment pipeline spec with workflow steps
5. ⬜ All infrastructure changes traceable to specs via PHRs
6. ⬜ ADRs created for significant architectural decisions

### Deliverables
1. ⬜ /infra/ folder with Dockerfiles, Helm chart, and setup scripts
2. ⬜ Updated specs: @specs/infra/architecture.md, helm-chart.md, deployment-pipeline.md
3. ⬜ README with one-command deploy instructions
4. ⬜ Demo script showing Gordon + kubectl-ai + kagent usage
5. ⬜ Complete PHR history of infrastructure implementation
6. ⬜ Working end-to-end: Full application running in Kubernetes with AI chatbot

### Demo Validation
Judges confirm: "Production-grade cloud-native deployment – AI-augmented DevOps, Kubernetes-native, fully observable, spec-driven infrastructure"

## Phase V Success Criteria

### Event-Driven Architecture Requirements
1. ⬜ Kafka/Redpanda cluster running (Strimzi in-cluster OR Redpanda Cloud)
2. ⬜ All required topics created: task-events, reminders, task-updates
3. ⬜ Chat API successfully publishes events on task operations
4. ⬜ All consumer services (Notification, Recurring, Audit) receiving and processing events
5. ⬜ Event flow visible: Create task → event published → consumers process → actions triggered
6. ⬜ No direct service-to-service synchronous calls for state propagation
7. ⬜ Event deduplication working (idempotent processing)

### Dapr Integration Requirements
1. ⬜ Dapr installed on all clusters (local Minikube + production)
2. ⬜ All services have Dapr sidecars running (1/1 Ready status)
3. ⬜ Dapr Pub/Sub component configured and working
4. ⬜ Dapr State Store component configured and working
5. ⬜ Dapr Scheduler component configured for reminders
6. ⬜ Dapr Secrets component configured for Kubernetes secrets
7. ⬜ Dapr Service Invocation working between services
8. ⬜ Dapr dashboard accessible and showing healthy sidecars
9. ⬜ Component swap demonstration: Kafka → Redis Pub/Sub with YAML-only change

### Advanced Features Requirements
1. ⬜ Recurring tasks fully implemented with cron/interval patterns
2. ⬜ Next occurrence auto-calculated and spawned on completion
3. ⬜ Exact-time reminders working via Dapr Jobs API (no polling)
4. ⬜ Reminder notifications triggered at correct time
5. ⬜ Priorities (low/medium/high/urgent) implemented and sortable
6. ⬜ Tags array working with multi-tag support
7. ⬜ Full-text search functional on title and description
8. ⬜ Comprehensive filtering: status, priority, tags, due_date range
9. ⬜ Sorting working: created_at, due_date, priority, status
10. ⬜ All advanced features visible and functional in UI

### Microservices Architecture Requirements
1. ⬜ Chat API service running and publishing events
2. ⬜ Notification Service consuming reminder events and logging notifications
3. ⬜ Recurring Task Service consuming completion events and spawning tasks
4. ⬜ Audit Service consuming all events and maintaining audit trail
5. ⬜ WebSocket Service (optional) broadcasting real-time updates
6. ⬜ All services independently deployable and scalable
7. ⬜ Service health endpoints responding correctly
8. ⬜ No direct database access from consumer services (Dapr State Store only)

### Production Kubernetes Deployment Requirements
1. ⬜ Oracle OKE cluster provisioned and accessible (or AKS/GKE)
2. ⬜ Helm chart successfully deployed to production cluster
3. ⬜ All pods in Running state with proper readiness/liveness probes
4. ⬜ Ingress configured with public domain or IP
5. ⬜ Application accessible via HTTPS (TLS certificate configured)
6. ⬜ Multi-environment support: local, staging, production working
7. ⬜ Resource limits and requests properly configured
8. ⬜ Horizontal Pod Autoscaling configured (optional)

### CI/CD Pipeline Requirements
1. ⬜ GitHub Actions workflow created and functional
2. ⬜ Pipeline stages working: test → build → push → deploy staging → deploy production
3. ⬜ Docker images automatically built and pushed to registry
4. ⬜ Helm chart automatically deployed on push to main
5. ⬜ Staging environment deployment successful
6. ⬜ Production deployment with approval gate working
7. ⬜ Pipeline notifications configured (success/failure alerts)
8. ⬜ Rollback capability demonstrated

### Application Functionality Requirements
1. ⬜ All Phase IV features working: authentication, task CRUD, AI chatbot
2. ⬜ Create task with due date → reminder triggered at exact time
3. ⬜ Create recurring task → auto-spawns next occurrence on completion
4. ⬜ Task with priority and tags → searchable and filterable
5. ⬜ Natural language chat commands working with advanced features
6. ⬜ User isolation maintained across all services
7. ⬜ No regressions in existing functionality
8. ⬜ Performance acceptable: <2s response time for typical operations

### Monitoring and Observability Requirements
1. ⬜ Structured JSON logging implemented across all services
2. ⬜ Dapr dashboard accessible and showing metrics
3. ⬜ kubectl-ai/kagent used for cluster analysis and optimization
4. ⬜ Pod logs accessible and searchable via kubectl logs
5. ⬜ Distributed tracing visible via Dapr trace IDs
6. ⬜ Resource monitoring working: kubectl top pods/nodes
7. ⬜ Health checks passing for all services
8. ⬜ Prometheus/Grafana dashboards (optional, nice-to-have)

### Portability and Flexibility Requirements
1. ⬜ Same Helm chart deploys to Minikube and production cluster
2. ⬜ Dapr component swap demonstrated: Kafka ↔ Redis with config-only change
3. ⬜ State store swap demonstrated: PostgreSQL ↔ Redis with config-only change
4. ⬜ No vendor-specific code in application services
5. ⬜ Environment-specific values externalized in Helm values files
6. ⬜ Database remains external (Neon) with no code changes

### Spec-Driven Traceability Requirements
1. ⬜ All Phase V specs created under @specs/infra/phase-v/
2. ⬜ Architecture spec documenting event-driven design and Dapr usage
3. ⬜ Microservices spec with service responsibilities and contracts
4. ⬜ Kafka/Dapr spec with component configurations
5. ⬜ CI/CD spec with pipeline stages and deployment strategy
6. ⬜ All implementation traceable to specs via PHRs
7. ⬜ ADRs created for significant architectural decisions
8. ⬜ Complete PHR history in history/prompts/

### Deliverables
1. ⬜ Updated monorepo with /services/ directory for microservices
2. ⬜ /infra/helm/todo-app/ upgraded with Dapr sidecars and new services
3. ⬜ /infra/dapr-components/ with all Dapr component YAMLs
4. ⬜ .github/workflows/deploy.yml with complete CI/CD pipeline
5. ⬜ Updated specs: @specs/infra/phase-v/architecture.md, dapr.md, kafka.md, cicd.md, monitoring.md
6. ⬜ README with one-command local deploy and cloud deploy instructions
7. ⬜ Demo script showing: event flow, reminders, recurring tasks, component swap
8. ⬜ Complete PHR history of Phase V implementation
9. ⬜ Live demo: browser → chat → create recurring task with reminder → see automation

### Demo Validation
Judges confirm: "This is production-grade event-driven microservices with Dapr portability, AI-assisted DevOps, full advanced Todo functionality, and seamless multi-cloud deployment – absolutely top-tier hackathon work showcasing unmatched depth, scalability, and modern cloud-native mastery"

## Development Workflow

### Feature Implementation Process
All features MUST be implemented exactly as defined in /specs folder. Each feature follows the sequence: Specification → Plan → Tasks → Implementation → Validation. Code structure MUST follow guidelines in root CLAUDE.md, frontend/CLAUDE.md, and backend/CLAUDE.md.

### Phase III Implementation Sequence (Completed)
1. **Specification Phase**: Create specs in /specs/agents/ and /specs/skills/
2. **Planning Phase**: Design DB schema, API contracts, MCP tool definitions
3. **Backend Implementation**: Chat endpoint, Cohere integration, MCP tools, DB models
4. **Frontend Integration**: ChatKit UI, API client, conversation display
5. **Testing Phase**: End-to-end testing, security validation, performance testing
6. **Documentation Phase**: README updates, API docs, deployment guides

### Phase IV Implementation Sequence (Completed)
1. **Infrastructure Specification Phase**: Create specs in /specs/infra/ (architecture, helm-chart, deployment-pipeline)
2. **Containerization Phase**: Generate Dockerfiles using Gordon or Claude Code, build and test images
3. **Helm Chart Generation Phase**: Create Helm chart structure with all templates and values
4. **Minikube Setup Phase**: Initialize cluster, enable addons, configure ingress
5. **Deployment Phase**: Deploy Helm release, verify pods, services, ingress
6. **AI Tool Integration Phase**: Use kubectl-ai and kagent for operations and analysis
7. **Validation Phase**: End-to-end testing in K8s, security verification, observability checks
8. **Documentation Phase**: README updates, demo script, deployment guides

### Phase V Implementation Sequence
1. **Architecture Specification Phase**: Create specs in /specs/infra/phase-v/ (architecture.md, dapr.md, kafka.md, microservices.md, cicd.md, monitoring.md)
2. **Database Schema Evolution Phase**: Add fields for recurring tasks (recurrence_pattern), priorities, tags, due_date with timezone
3. **Event Infrastructure Phase**: Deploy Kafka/Redpanda (Strimzi or Cloud), create topics, configure Dapr Pub/Sub component
4. **Dapr Installation Phase**: Install Dapr on Minikube and production cluster, create all Dapr components (pubsub, state, scheduler, secrets)
5. **Backend Event Publishing Phase**: Update Chat API to publish events via Dapr Pub/Sub on task operations
6. **Microservices Development Phase**: Create consumer services (Notification, Recurring Task, Audit, WebSocket) with Dapr subscriptions
7. **Advanced Features Implementation Phase**: Implement recurring tasks, reminders (Dapr Jobs), priorities, tags, search/filter/sort
8. **Helm Chart Upgrade Phase**: Add Dapr annotations, new service deployments, Dapr components, updated values.yaml
9. **Production Cluster Setup Phase**: Provision Oracle OKE (or AKS/GKE), configure kubectl access, setup ingress
10. **CI/CD Pipeline Phase**: Create GitHub Actions workflow with test, build, push, deploy stages
11. **Multi-Environment Deployment Phase**: Deploy to local (Minikube), staging, and production with environment-specific values
12. **Monitoring and Observability Phase**: Setup Dapr dashboard, configure structured logging, integrate kubectl-ai/kagent
13. **Portability Demonstration Phase**: Demonstrate Dapr component swaps (Kafka↔Redis, PostgreSQL↔Redis) with config-only changes
14. **End-to-End Validation Phase**: Test all advanced features, event flows, reminders, recurring tasks, CI/CD pipeline
15. **Documentation and Demo Phase**: Update README, create demo script, record PHRs, prepare live demonstration

### Frontend Requirements
Responsive, clean UI using Tailwind CSS and Next.js App Router (server components by default). Frontend MUST include authentication pages, task list, create/edit forms, and chat interface with proper user isolation. Frontend MUST be containerized and deployable to Kubernetes.

### API Endpoint Standards
Every API endpoint MUST require valid JWT token and filter data by authenticated user_id. FastAPI middleware MUST correctly verify JWT and extract user_id on every protected route. Chat endpoint MUST follow same security standards. All endpoints MUST work identically in Kubernetes environment.

### Quality Gates
All implementations MUST meet the success criteria: Complete implementation of all 5 basic task CRUD operations + toggle completion + AI chat interface as a multi-user web app running in Kubernetes. Project MUST be deployable with single helm install command after Minikube setup.

## Governance

This constitution governs all development activities for the Phase IV Cloud-Native Todo AI Chatbot project. All code reviews and pull requests MUST verify compliance with these principles. Deviations require explicit constitutional amendments with version bump. All implementation MUST be traceable to specs via Claude Code prompts using @specs references with complete history maintained in Prompt History Records (PHRs) under history/prompts/.

### Amendment Procedure
1. Propose amendment with rationale
2. Document impact on existing principles
3. Update version following semantic versioning
4. Propagate changes to dependent templates
5. Create PHR documenting the amendment

### Versioning Policy
- **MAJOR**: Backward incompatible governance/principle removals or redefinitions
- **MINOR**: New principle/section added or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance Review
All implementations MUST be reviewed against this constitution before merge. Non-compliance MUST be documented and justified or corrected.

---

**Version**: 1.3.0 | **Ratified**: 2026-02-07 | **Last Amended**: 2026-02-09
