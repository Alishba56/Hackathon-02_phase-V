# Implementation Tasks: Secure Backend API for Todo Application

**Feature**: Secure Backend API for Todo Application
**Branch**: `002-fastapi-backend`
**Created**: 2026-02-07
**Status**: Draft

## Task Organization Strategy

This task breakdown follows the spec-driven development approach, organizing work by user stories to enable independent implementation and testing. Each phase builds upon the previous while maintaining the ability to deliver value incrementally.

**Implementation Strategy**: MVP first approach - focus on foundational infrastructure (authentication, database) and User Story 1 (Task CRUD) to establish the core API, then enhance with filtering/sorting in subsequent phases.

## Phase 1: Setup Tasks

Establish foundational project structure and dependencies.

- [x] T001 Create backend/ directory structure per implementation plan
- [x] T002 Create requirements.txt with FastAPI 0.104+, SQLModel 0.0.14+, PyJWT 2.8+, python-dotenv 1.0+, uvicorn 0.24+, psycopg2-binary 2.9+
- [x] T003 Create .env file with BETTER_AUTH_SECRET, BETTER_AUTH_URL, NEON_DB_URL environment variables
- [x] T004 Create backend/.gitignore for Python (venv/, __pycache__/, *.pyc, .env)
- [x] T005 Initialize Python virtual environment and install dependencies from requirements.txt
- [x] T006 Create backend/main.py with FastAPI app initialization and health check endpoint

## Phase 2: Foundational Components (Blocking Prerequisites)

Build core infrastructure that enables all user stories. This phase includes authentication (US2), database setup (US5), and error handling patterns (US4).

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T007 [P] Create backend/models.py with User SQLModel (id, email, name, created_at, updated_at)
- [x] T008 [P] Create backend/models.py with Task SQLModel (id, user_id, title, description, completed, priority, due_date, created_at, updated_at) and indexes
- [x] T009 Create backend/db.py with SQLModel engine using NEON_DB_URL and connection pooling configuration
- [x] T010 Add get_session() dependency function in backend/db.py for per-request database sessions
- [x] T011 Add startup event in backend/main.py to create database tables using SQLModel.metadata.create_all()
- [x] T012 [P] Create backend/schemas.py with TaskCreate Pydantic model (title, description, priority, due_date)
- [x] T013 [P] Create backend/schemas.py with TaskUpdate Pydantic model (title, description, completed, priority, due_date - all optional)
- [x] T014 [P] Create backend/schemas.py with TaskResponse Pydantic model (all Task fields for API responses)
- [x] T015 Create backend/auth.py with verify_jwt_token() function using PyJWT to decode and validate tokens
- [x] T016 Create backend/auth.py with get_current_user() dependency function that extracts JWT from Authorization header and returns user_id
- [x] T017 Add CORS middleware in backend/main.py allowing frontend origin (http://localhost:3001) with credentials
- [x] T018 Create backend/routes/ directory for API route handlers

**Checkpoint**: Foundation ready - authentication, database, and schemas are in place. User story implementation can now begin.

## Phase 3: User Story 1 - Task CRUD Operations (Priority: P1) 🎯 MVP

A user wants to manage their personal tasks through a secure API that allows them to create, read, update, and delete tasks. The system must ensure that users can only access and modify their own tasks.

**Goal**: Implement all 6 RESTful API endpoints for task management with JWT authentication and user data isolation.

**Independent Test**: Make API calls with valid JWT to create a task, retrieve it, update it, mark it complete, and delete it. Verify user isolation by attempting to access another user's task (should return 403).

### Implementation for User Story 1

- [x] T019 [US1] Create backend/routes/tasks.py with APIRouter for task endpoints
- [x] T020 [US1] Implement GET /api/tasks endpoint in backend/routes/tasks.py to list all tasks for authenticated user (filter by user_id)
- [x] T021 [US1] Implement POST /api/tasks endpoint in backend/routes/tasks.py to create new task with user_id from current_user
- [x] T022 [US1] Implement GET /api/tasks/{task_id} endpoint in backend/routes/tasks.py to retrieve specific task with ownership check
- [x] T023 [US1] Implement PUT /api/tasks/{task_id} endpoint in backend/routes/tasks.py to update task with ownership check
- [x] T024 [US1] Implement DELETE /api/tasks/{task_id} endpoint in backend/routes/tasks.py to delete task with ownership check
- [x] T025 [US1] Implement PATCH /api/tasks/{task_id}/complete endpoint in backend/routes/tasks.py to toggle task completion status
- [x] T026 [US1] Add HTTPException error handling for 400 (validation), 401 (unauthorized), 403 (forbidden), 404 (not found) in all endpoints
- [x] T027 [US1] Add user_id filtering to all query operations to enforce data isolation per FR-009
- [x] T028 [US1] Register tasks router in backend/main.py with /api prefix
- [x] T029 [US1] Verify all endpoints require authentication using get_current_user dependency
- [x] T030 [US1] Test task creation, retrieval, update, deletion, and completion toggle with valid JWT token

**Checkpoint**: At this point, User Story 1 (Task CRUD) should be fully functional. All 6 endpoints work with authentication and user isolation enforced. This is the MVP.

## Phase 4: User Story 3 - Task Filtering and Sorting (Priority: P2)

Users want to efficiently find and organize their tasks by filtering them based on completion status and sorting them by different criteria.

**Goal**: Enhance GET /api/tasks endpoint with query parameters for filtering and sorting.

**Independent Test**: Create multiple tasks with different statuses and attributes, then make API requests with various filter and sort parameters to verify correct results are returned in the expected order.

### Implementation for User Story 3

- [x] T031 [US3] Add status query parameter (all/pending/completed) to GET /api/tasks endpoint in backend/routes/tasks.py
- [x] T032 [US3] Implement filtering logic in GET /api/tasks to filter by completed status based on status parameter
- [x] T033 [US3] Add sort query parameter (created/title/due_date) to GET /api/tasks endpoint in backend/routes/tasks.py
- [x] T034 [US3] Implement sorting logic in GET /api/tasks using SQLModel order_by() based on sort parameter
- [x] T035 [US3] Test filtering: GET /api/tasks?status=pending returns only incomplete tasks
- [x] T036 [US3] Test filtering: GET /api/tasks?status=completed returns only completed tasks
- [x] T037 [US3] Test sorting: GET /api/tasks?sort=created returns tasks ordered by creation date
- [x] T038 [US3] Test sorting: GET /api/tasks?sort=title returns tasks in alphabetical order
- [x] T039 [US3] Test combined: GET /api/tasks?status=pending&sort=due_date returns filtered and sorted results

**Checkpoint**: At this point, User Stories 1 AND 3 should both work. Users can perform CRUD operations and filter/sort their task lists.

## Phase 5: Polish & Cross-Cutting Concerns

Address final quality, performance, and integration requirements. User Stories 2 (Authentication), 4 (Error Handling), and 5 (Performance) are implemented throughout the codebase as infrastructure and quality attributes.

### User Story 2 - Secure Authentication Verification (P1)

Authentication is implemented in Phase 2 (Foundational) and used throughout all endpoints. These tasks validate the implementation.

- [x] T040 [US2] Test authentication: Request without token returns 401 Unauthorized
- [x] T041 [US2] Test authentication: Request with invalid token returns 401 Unauthorized
- [x] T042 [US2] Test authentication: Request with expired token returns 401 Unauthorized
- [x] T043 [US2] Test authentication: Request with valid token succeeds and extracts correct user_id
- [x] T044 [US2] Verify JWT verification uses BETTER_AUTH_SECRET from environment variables

### User Story 4 - Robust Error Handling and Validation (P2)

Error handling is implemented throughout all endpoints. These tasks validate the implementation.

- [x] T045 [US4] Test validation: POST /api/tasks without title returns 400 Bad Request with clear error message
- [x] T046 [US4] Test validation: POST /api/tasks with invalid priority returns 400 Bad Request
- [x] T047 [US4] Test error handling: GET /api/tasks/{invalid_id} returns 404 Not Found
- [x] T048 [US4] Test authorization: GET /api/tasks/{other_user_task_id} returns 403 Forbidden
- [x] T049 [US4] Verify all error responses include clear detail messages and appropriate HTTP status codes

### User Story 5 - Database Connection and Performance (P2)

Database setup and performance optimizations are implemented in Phase 2 (Foundational). These tasks validate the implementation.

- [x] T050 [US5] Verify database connection succeeds on startup using NEON_DB_URL with SSL parameters
- [x] T051 [US5] Verify tables (users, tasks) are created automatically on startup
- [x] T052 [US5] Verify indexes exist on tasks.user_id, tasks.completed, and composite (user_id, completed)
- [x] T053 [US5] Test connection pooling: Make 10 concurrent requests and verify no connection errors
- [x] T054 [US5] Verify query performance: GET /api/tasks with 100 tasks completes in <50ms

### Integration and Documentation

- [x] T055 [P] Enable Swagger UI documentation at /docs endpoint in backend/main.py
- [x] T056 [P] Enable ReDoc documentation at /redoc endpoint in backend/main.py
- [ ] T057 Test full-stack integration: Start backend and frontend, perform complete user flow (signup, login, create task, list, update, delete)
- [x] T058 Verify CORS configuration allows frontend requests with credentials
- [x] T059 Create backend/README.md with setup instructions, environment variables, and running the server
- [ ] T060 Verify all success criteria from spec.md are met (6 endpoints, auth verification, user isolation, performance, integration)

### Security and Production Readiness

- [x] T061 Security audit: Verify no SQL injection vulnerabilities (parameterized queries used)
- [x] T062 Security audit: Verify no sensitive data in error messages or logs
- [x] T063 Security audit: Verify JWT secret is loaded from environment, not hardcoded
- [ ] T064 Performance test: Send 100 concurrent requests to /api/tasks and verify <200ms response time
- [x] T065 Verify all queries filter by user_id to prevent data leakage between users
- [ ] T066 Final validation: Run through quickstart.md to ensure all setup steps work correctly

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion - Core MVP functionality
- **User Story 3 (Phase 4)**: Depends on User Story 1 completion - Enhances existing GET endpoint
- **Polish (Phase 5)**: Depends on all user stories being complete - Final validation and testing

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Implemented in Foundational phase as authentication infrastructure
- **User Story 3 (P2)**: Depends on User Story 1 (enhances GET /api/tasks endpoint)
- **User Story 4 (P2)**: Implemented throughout all endpoints as error handling patterns
- **User Story 5 (P2)**: Implemented in Foundational phase as database infrastructure

### Within Each Phase

- **Setup**: Tasks can run sequentially or in small parallel groups
- **Foundational**: Models [P], Schemas [P] can run in parallel; Auth and DB setup are sequential
- **User Story 1**: Endpoints can be implemented in parallel after router setup
- **User Story 3**: Sequential enhancement of existing endpoint
- **Polish**: Validation tasks [P] can run in parallel

### Parallel Opportunities

1. **Foundational Phase**: T007-T008 (models), T012-T014 (schemas) can run in parallel
2. **User Story 1**: T020-T025 (endpoint implementations) can run in parallel after T019 (router setup)
3. **Polish Phase**: T040-T044 (auth tests), T045-T049 (error tests), T050-T054 (performance tests) can run in parallel

## Parallel Example: User Story 1

```bash
# After T019 (router setup), launch all endpoint implementations together:
Task: "Implement GET /api/tasks endpoint in backend/routes/tasks.py"
Task: "Implement POST /api/tasks endpoint in backend/routes/tasks.py"
Task: "Implement GET /api/tasks/{task_id} endpoint in backend/routes/tasks.py"
Task: "Implement PUT /api/tasks/{task_id} endpoint in backend/routes/tasks.py"
Task: "Implement DELETE /api/tasks/{task_id} endpoint in backend/routes/tasks.py"
Task: "Implement PATCH /api/tasks/{task_id}/complete endpoint in backend/routes/tasks.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T018) - CRITICAL blocking phase
3. Complete Phase 3: User Story 1 (T019-T030) - Core CRUD operations
4. **STOP and VALIDATE**: Test all 6 endpoints independently with authentication
5. Deploy/demo if ready - this is a functional task management API

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (authentication, database, schemas)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - full CRUD API!)
3. Add User Story 3 → Test independently → Deploy/Demo (Enhanced with filtering/sorting)
4. Complete Polish → Final validation → Production ready
5. Each phase adds value without breaking previous functionality

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T018)
2. Once Foundational is done:
   - Developer A: Implements GET and POST endpoints (T020-T021)
   - Developer B: Implements GET by ID and PUT endpoints (T022-T023)
   - Developer C: Implements DELETE and PATCH endpoints (T024-T025)
3. Integrate and test together (T026-T030)
4. Continue with User Story 3 and Polish phases

## MVP Scope

**Minimum Viable Product**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (User Story 1)

This delivers:
- ✅ Secure JWT authentication
- ✅ User data isolation
- ✅ All 6 RESTful endpoints (GET, POST, PUT, DELETE, PATCH)
- ✅ Database persistence with Neon PostgreSQL
- ✅ Error handling and validation
- ✅ CORS enabled for frontend integration
- ✅ API documentation at /docs

**Total MVP Tasks**: T001-T030 (30 tasks)

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- User Story 2, 4, and 5 are infrastructure/quality concerns implemented throughout
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate functionality independently
- All endpoints must filter by user_id to enforce data isolation
- Use get_current_user dependency on all protected routes
- Follow FastAPI best practices for dependency injection
