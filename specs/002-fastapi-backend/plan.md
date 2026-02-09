# Implementation Plan: Secure Backend API for Todo Application

**Branch**: `002-fastapi-backend` | **Date**: 2026-02-07 | **Spec**: [specs/002-fastapi-backend/spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-fastapi-backend/spec.md`

## Summary

Build a secure, production-grade FastAPI backend that provides RESTful API endpoints for task CRUD operations with JWT-based authentication verification, strict user data isolation, and seamless integration with the existing Next.js frontend. The backend will use SQLModel ORM for database operations with Neon Serverless PostgreSQL, implement comprehensive error handling and validation, support task filtering and sorting, and ensure zero data leakage between users through authentication middleware and query filtering.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.104+, SQLModel 0.0.14+, PyJWT 2.8+, python-dotenv 1.0+, uvicorn 0.24+, psycopg2-binary 2.9+ (PostgreSQL driver)
**Storage**: Neon Serverless PostgreSQL (cloud-hosted PostgreSQL with connection pooling)
**Testing**: Manual API testing with Postman/Thunder Client/curl, integration testing with frontend
**Target Platform**: Linux/Windows server, containerized with Docker
**Project Type**: Web backend API (monorepo structure with backend/ directory)
**Performance Goals**: <200ms response time for typical requests, 100+ concurrent requests, <50ms query execution for filtered lists
**Constraints**: Stateless authentication (JWT only, no sessions), strict user data isolation, CORS enabled for frontend origin, all routes under /api/ prefix
**Scale/Scope**: Multi-user application, 6 RESTful endpoints, 2 database tables (users, tasks), JWT middleware on all protected routes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Compliance Status

- **I. Fully Spec-Driven and Agentic Development**: ✅ All implementation will be generated via Claude Code using references to specs
- **II. Zero Manual Coding Enforcement**: ✅ No hand-written code, all generated through Claude Code
- **III. Modular Architecture Through Agents and Skills**: ✅ Backend follows modular structure (models, routes, middleware, db)
- **IV. Complete User Isolation and Data Ownership**: ✅ JWT authentication on all endpoints, user_id filtering on all queries
- **V. Strict Technology Stack Adherence**: ✅ FastAPI, SQLModel, Neon PostgreSQL, Better Auth JWT - all within specified stack
- **VI. Monorepo Structure Compliance**: ✅ Backend code in backend/ directory as per monorepo specification

### Additional Constraints Compliance

- **Technology Stack Lock**: ✅ Using only FastAPI, SQLModel, Neon PostgreSQL, PyJWT
- **Database Access Policy**: ✅ No direct database access from frontend, all through protected API endpoints
- **Data Security Requirements**: ✅ JWT verification on all routes, task ownership enforcement, shared BETTER_AUTH_SECRET
- **Database Schema Compliance**: ✅ Schema matches specification (users table for Better Auth, tasks table with user_id FK)

**Gate Result**: ✅ PASS - All constitutional requirements met, no violations to justify

## Project Structure

### Documentation (this feature)

```text
specs/002-fastapi-backend/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Technical decisions and best practices
├── data-model.md        # Phase 1: Database schema and entity relationships
├── quickstart.md        # Phase 1: Setup and integration guide
├── contracts/           # Phase 1: API contracts (OpenAPI/REST endpoints)
│   └── rest-api.yaml    # OpenAPI 3.0 specification for all endpoints
└── tasks.md             # Phase 2: Task breakdown (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI application entry point, CORS, startup events
├── models.py            # SQLModel models (Task, User)
├── db.py                # Database engine, session management, dependencies
├── auth.py              # JWT verification middleware, get_current_user dependency
├── routes/              # API route handlers
│   └── tasks.py         # Task CRUD endpoints with user filtering
├── schemas.py           # Pydantic request/response models
├── .env                 # Environment variables (BETTER_AUTH_SECRET, NEON_DB_URL)
├── requirements.txt     # Python dependencies
└── Dockerfile           # Container configuration (optional)

tests/                   # Manual testing scripts and integration tests
└── api_tests.md         # Test scenarios and curl commands
```

**Structure Decision**: Web application structure with backend/ directory. FastAPI follows a flat structure for small projects with clear separation of concerns: models (data), routes (handlers), auth (middleware), db (connection), schemas (validation). This aligns with FastAPI best practices and keeps the codebase maintainable for a hackathon project.

## Complexity Tracking

> No constitutional violations - this section is not needed.

## Architecture Overview

### System Components

```text
┌─────────────────────────────────────────────────────────────┐
│                     Next.js Frontend                         │
│              (Better Auth JWT Token Issuer)                  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP Requests with JWT in Authorization header
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  CORS Middleware (allow frontend origin)             │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     ▼                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  JWT Verification Middleware (auth.py)               │   │
│  │  - Decode token with BETTER_AUTH_SECRET              │   │
│  │  - Extract user_id from 'sub' claim                  │   │
│  │  - Inject current_user into request context          │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     ▼                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Route Handlers (routes/tasks.py)                    │   │
│  │  - GET /api/tasks (list with filters)                │   │
│  │  - POST /api/tasks (create)                          │   │
│  │  - GET /api/tasks/{id} (retrieve)                    │   │
│  │  - PUT /api/tasks/{id} (update)                      │   │
│  │  - DELETE /api/tasks/{id} (delete)                   │   │
│  │  - PATCH /api/tasks/{id}/complete (toggle)           │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     ▼                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SQLModel ORM (models.py)                            │   │
│  │  - Task model with user_id relationship              │   │
│  │  - User model (minimal, Better Auth manages)         │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     ▼                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Database Session (db.py)                            │   │
│  │  - Connection pooling                                │   │
│  │  - Per-request session via dependency                │   │
│  └──────────────────┬───────────────────────────────────┘   │
└────────────────────┼────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          Neon Serverless PostgreSQL                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  users table (managed by Better Auth)                │   │
│  │  - id (primary key)                                  │   │
│  │  - email, name, etc.                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  tasks table                                         │   │
│  │  - id (primary key)                                  │   │
│  │  - user_id (foreign key → users.id) [INDEXED]       │   │
│  │  - title, description, completed [INDEXED]           │   │
│  │  - created_at, updated_at, due_date, priority        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow Example

1. **Frontend**: User clicks "Create Task" → POST /api/tasks with JWT in Authorization header
2. **CORS Middleware**: Validates origin, allows request
3. **JWT Middleware**: Decodes token, extracts user_id="abc123", injects into request
4. **Route Handler**: Receives TaskCreate schema, validates title not empty
5. **Database**: Creates task with user_id="abc123", returns task with id
6. **Response**: Returns 201 Created with task JSON
7. **Frontend**: Displays new task in UI

### Authentication Flow

```text
Frontend (Better Auth)          Backend (FastAPI)
      │                               │
      │  1. User logs in              │
      ├──────────────────────────────>│
      │                               │
      │  2. Better Auth issues JWT    │
      │     with user_id in 'sub'     │
      │<──────────────────────────────┤
      │                               │
      │  3. Store JWT in frontend     │
      │                               │
      │  4. API request with JWT      │
      │     Authorization: Bearer <token>
      ├──────────────────────────────>│
      │                               │
      │                          5. Verify JWT
      │                             with BETTER_AUTH_SECRET
      │                               │
      │                          6. Extract user_id
      │                             from 'sub' claim
      │                               │
      │                          7. Query tasks
      │                             WHERE user_id = <extracted>
      │                               │
      │  8. Return user's tasks only  │
      │<──────────────────────────────┤
```

## Key Technical Decisions

### 1. Dependency Injection for Current User

**Decision**: Use FastAPI `Depends` with reusable `get_current_user` dependency

**Rationale**:
- Clean, declarative syntax: `current_user: User = Depends(get_current_user)`
- Automatic JWT verification on every route that uses the dependency
- Reusable across all protected endpoints
- FastAPI best practice for authentication
- Enables automatic OpenAPI documentation with security schemes

**Alternative Rejected**: Manual token extraction in each route handler
- Reason: Code duplication, error-prone, harder to maintain

**Implementation**:
```python
# auth.py
async def get_current_user(authorization: str = Header(None)) -> User:
    # Verify JWT, extract user_id, return User object
    pass

# routes/tasks.py
@router.get("/api/tasks")
async def list_tasks(current_user: User = Depends(get_current_user)):
    # current_user is automatically injected and verified
    pass
```

### 2. Database Session Management

**Decision**: Per-request Session via dependency injection

**Rationale**:
- FastAPI best practice for SQLModel/SQLAlchemy
- Automatic session lifecycle management (open, commit, close)
- Thread-safe for concurrent requests
- Prevents connection leaks
- Aligns with FastAPI's dependency injection system

**Alternative Rejected**: Global session
- Reason: Not thread-safe, connection leaks, poor for concurrent requests

**Implementation**:
```python
# db.py
def get_session():
    with Session(engine) as session:
        yield session

# routes/tasks.py
@router.get("/api/tasks")
async def list_tasks(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
    return tasks
```

### 3. Environment Variable Loading

**Decision**: python-dotenv for .env file loading

**Rationale**:
- Simple, lightweight, widely used
- Matches provided .env example in requirements
- No additional complexity needed for hackathon scope
- Loads variables at startup before FastAPI initialization

**Alternative Rejected**: pydantic-settings
- Reason: Overkill for simple key-value pairs, adds unnecessary complexity

**Implementation**:
```python
# main.py
from dotenv import load_dotenv
import os

load_dotenv()
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
NEON_DB_URL = os.getenv("NEON_DB_URL")
```

### 4. CORS Configuration

**Decision**: Allow specific frontend origin with credentials support

**Rationale**:
- Secure: Only allows requests from known frontend origin
- Supports credentials (cookies) if Better Auth uses them
- Prevents CORS errors during development and production
- Configurable via environment variable for different environments

**Alternative Rejected**: Wildcard (*) origin
- Reason: Security risk, doesn't work with credentials

**Implementation**:
```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. JWT Library

**Decision**: PyJWT for token verification

**Rationale**:
- Lightweight, focused on JWT operations
- Widely used, well-documented
- Sufficient for verification-only use case
- No unnecessary features

**Alternative Rejected**: authlib
- Reason: Heavier library with OAuth features we don't need

**Implementation**:
```python
# auth.py
import jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 6. Database Table Creation

**Decision**: SQLModel `create_all()` on startup

**Rationale**:
- Simple, automatic schema creation
- Acceptable for hackathon/development
- Neon PostgreSQL handles schema management
- No migration complexity needed for initial version

**Alternative Rejected**: Manual migrations (Alembic)
- Reason: Overkill for hackathon, adds complexity, not required for MVP

**Implementation**:
```python
# main.py
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
```

### 7. API Prefix

**Decision**: All routes under `/api/` prefix

**Rationale**:
- Clean separation from potential frontend routes
- Matches specification requirements
- Industry standard for API versioning path
- Easier to apply middleware to all API routes

**Implementation**:
```python
# main.py
app.include_router(tasks_router, prefix="/api")
```

### 8. Response Models

**Decision**: Separate Pydantic models for TaskCreate, TaskUpdate, TaskResponse

**Rationale**:
- Better validation: Different fields required for create vs update
- Clear API documentation: OpenAPI shows exact request/response shapes
- Security: Response model excludes sensitive fields if needed
- Type safety: Prevents accidental field exposure

**Implementation**:
```python
# schemas.py
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    priority: Optional[str]
    due_date: Optional[datetime]
    user_id: str
```

## Testing Strategy

### Manual API Testing

**Tools**: Postman, Thunder Client, or curl

**Test Scenarios**:
1. **Authentication Tests**:
   - Request without token → 401 Unauthorized
   - Request with invalid token → 401 Unauthorized
   - Request with expired token → 401 Unauthorized
   - Request with valid token → 200 OK

2. **Task CRUD Tests**:
   - Create task with valid data → 201 Created
   - Create task without title → 400 Bad Request
   - List tasks → 200 OK with user's tasks only
   - Get specific task → 200 OK
   - Get non-existent task → 404 Not Found
   - Update task → 200 OK
   - Delete task → 204 No Content

3. **User Isolation Tests**:
   - User A creates task
   - User B attempts to access User A's task → 403 Forbidden
   - User B lists tasks → Only sees their own tasks

4. **Filtering Tests**:
   - GET /api/tasks?status=pending → Only incomplete tasks
   - GET /api/tasks?status=completed → Only completed tasks
   - GET /api/tasks?status=all → All tasks

5. **Sorting Tests**:
   - GET /api/tasks?sort=created → Sorted by creation date
   - GET /api/tasks?sort=title → Sorted alphabetically
   - GET /api/tasks?sort=due_date → Sorted by due date

### Integration Testing

**Scenario**: Full-stack integration test
1. Start backend: `uvicorn main:app --reload`
2. Start frontend: `npm run dev`
3. User flow:
   - Sign up via frontend
   - Log in via frontend
   - Create task via UI
   - Verify task appears in list
   - Toggle task completion
   - Edit task
   - Delete task
4. Verify all operations succeed with proper authentication

### Database Connection Testing

**Test**: Neon PostgreSQL connection
1. Verify connection string format with SSL and channel binding
2. Test connection on startup
3. Verify tables are created automatically
4. Check indexes exist on user_id and completed fields

### Performance Testing

**Test**: Concurrent request handling
1. Use tool like Apache Bench or wrk
2. Send 100 concurrent requests to /api/tasks
3. Verify response times < 200ms
4. Check for errors or connection pool exhaustion

## Phase 0: Research & Technical Decisions

**Status**: All technical decisions documented above

**Key Research Areas**:
1. ✅ FastAPI best practices for authentication middleware
2. ✅ SQLModel session management patterns
3. ✅ JWT verification with PyJWT
4. ✅ Neon PostgreSQL connection string format
5. ✅ CORS configuration for cross-origin requests
6. ✅ Error handling patterns in FastAPI
7. ✅ Request/response validation with Pydantic

**Output**: research.md (to be generated with detailed findings)

## Phase 1: Design & Contracts

**Deliverables**:
1. **data-model.md**: Database schema with Task and User entities, relationships, indexes
2. **contracts/rest-api.yaml**: OpenAPI 3.0 specification for all 6 endpoints
3. **quickstart.md**: Setup instructions, environment variables, running the backend

**Key Design Elements**:
- Task entity with all required fields
- User entity (minimal, Better Auth manages)
- Foreign key relationship: Task.user_id → User.id
- Indexes on user_id and completed for query optimization
- API contracts with request/response schemas
- Error response formats

## Phase 2: Implementation Phases

### Foundation Phase
**Goal**: Set up FastAPI project structure and dependencies

**Tasks**:
1. Create backend/ directory structure
2. Create requirements.txt with all dependencies
3. Create .env file with BETTER_AUTH_SECRET and NEON_DB_URL
4. Create main.py with FastAPI app initialization
5. Configure CORS middleware for frontend origin
6. Add basic health check endpoint

**Validation**: `uvicorn main:app --reload` starts successfully

### Database Layer Phase
**Goal**: Implement SQLModel models and database connection

**Tasks**:
1. Create models.py with Task and User SQLModel classes
2. Create db.py with engine, session, and get_session dependency
3. Add startup event to create tables automatically
4. Add indexes on user_id and completed fields
5. Test database connection with Neon PostgreSQL

**Validation**: Tables created in Neon database, connection successful

### Authentication Middleware Phase
**Goal**: Implement JWT verification and user extraction

**Tasks**:
1. Create auth.py with JWT verification logic
2. Implement get_current_user dependency
3. Handle token errors (missing, invalid, expired)
4. Extract user_id from 'sub' claim
5. Return User object for dependency injection

**Validation**: Requests with valid tokens succeed, invalid tokens return 401

### Task Models & Schemas Phase
**Goal**: Define Pydantic request/response models

**Tasks**:
1. Create schemas.py with TaskCreate, TaskUpdate, TaskResponse
2. Add validation rules (title not empty, etc.)
3. Define optional fields (description, priority, due_date)
4. Configure response model to exclude sensitive fields

**Validation**: Models validate correctly, OpenAPI docs show schemas

### Task CRUD Routes Phase
**Goal**: Implement all 6 task endpoints with user filtering

**Tasks**:
1. Create routes/tasks.py with APIRouter
2. Implement GET /api/tasks (list with filters)
3. Implement POST /api/tasks (create)
4. Implement GET /api/tasks/{id} (retrieve)
5. Implement PUT /api/tasks/{id} (update)
6. Implement DELETE /api/tasks/{id} (delete)
7. Add user_id filtering on all queries
8. Add ownership checks (403 for wrong user)

**Validation**: All endpoints work, user isolation enforced

### Toggle Completion Route Phase
**Goal**: Implement PATCH endpoint for toggling task completion

**Tasks**:
1. Add PATCH /api/tasks/{id}/complete endpoint
2. Implement optimistic toggle logic (flip completed boolean)
3. Add ownership check
4. Return updated task

**Validation**: Toggle works, completion status flips correctly

### Error Handling & Validation Phase
**Goal**: Centralize error handling and validation

**Tasks**:
1. Add HTTPException for all error cases
2. Implement proper status codes (400, 401, 403, 404)
3. Add clear error messages
4. Validate request data with Pydantic
5. Handle database errors gracefully

**Validation**: All error cases return appropriate responses

### Query Parameters Phase
**Goal**: Add filtering and sorting support

**Tasks**:
1. Add status query parameter (all, pending, completed)
2. Add sort query parameter (created, title, due_date)
3. Implement filtering logic in list endpoint
4. Implement sorting logic in list endpoint
5. Test all combinations

**Validation**: Filtering and sorting work correctly

### Integration & Polish Phase
**Goal**: Final integration and testing

**Tasks**:
1. Enable Swagger UI at /docs
2. Test full flow with frontend
3. Verify zero data leakage between users
4. Check all success criteria met
5. Add logging for debugging
6. Document any known issues

**Validation**: Full-stack integration works, all tests pass

### Final Review Phase
**Goal**: Ensure production readiness

**Tasks**:
1. Security audit (JWT verification, SQL injection prevention)
2. Performance testing (concurrent requests, query times)
3. Error handling review (all edge cases covered)
4. Documentation review (README, API docs)
5. Code quality check (no hardcoded secrets, clean structure)

**Validation**: All success criteria met, judges confirm compliance

## Success Criteria Mapping

| Success Criterion | Implementation | Validation Method |
|-------------------|----------------|-------------------|
| SC-001: All 6 endpoints respond correctly | All routes implemented in routes/tasks.py | Manual API testing with Postman |
| SC-002: Auth rejects invalid tokens | JWT middleware in auth.py | Test with invalid/missing/expired tokens |
| SC-003: User data isolation enforced | user_id filtering on all queries | Multi-user test with different accounts |
| SC-004: <200ms response time | Efficient queries with indexes | Performance testing with concurrent requests |
| SC-005: 100+ concurrent requests | Connection pooling in db.py | Load testing with Apache Bench |
| SC-006: <50ms query execution | Indexes on user_id and completed | Database query profiling |
| SC-007: Frontend integration succeeds | CORS and JWT verification | Full-stack integration test |
| SC-008: Clear error messages | HTTPException with detail messages | Test all error scenarios |
| SC-009: Database connection succeeds | Engine initialization in db.py | Startup test with Neon connection |
| SC-010: Filtering returns correct results | Query parameter logic | Test all filter combinations |
| SC-011: Sorting returns correct order | Order by clauses | Test all sort options |
| SC-012: No security vulnerabilities | JWT verification, parameterized queries | Security audit and penetration testing |

## Integration Points with Frontend

### API Base URL
- **Development**: `http://localhost:8000`
- **Environment Variable**: Frontend should use `NEXT_PUBLIC_API_URL`

### Authentication Flow
1. Frontend uses Better Auth to authenticate user
2. Better Auth issues JWT with user_id in 'sub' claim
3. Frontend stores JWT (localStorage or cookie)
4. Frontend includes JWT in Authorization header: `Bearer <token>`
5. Backend verifies JWT and extracts user_id
6. Backend filters all data by user_id

### Request Format
```http
GET /api/tasks HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### Response Format
```json
{
  "id": "uuid-here",
  "title": "Task title",
  "description": "Task description",
  "completed": false,
  "created_at": "2026-02-07T10:00:00Z",
  "updated_at": "2026-02-07T10:00:00Z",
  "priority": "high",
  "due_date": "2026-02-10T00:00:00Z",
  "user_id": "user-uuid"
}
```

### Error Response Format
```json
{
  "detail": "Task not found"
}
```

### Status Codes
- **200 OK**: Successful GET, PUT, PATCH
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Validation error
- **401 Unauthorized**: Missing/invalid/expired token
- **403 Forbidden**: Attempting to access another user's resource
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server error

## Environment Variables

### Required Variables

```bash
# .env file
BETTER_AUTH_SECRET=secret
BETTER_AUTH_URL=http://localhost:3000
NEON_DB_URL=postgresql://neonpg_5xMPfhq9XgaS@ep-bitter-cloud-adk6f8ds-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### Variable Descriptions

- **BETTER_AUTH_SECRET**: Shared secret for JWT verification (must match frontend)
- **BETTER_AUTH_URL**: Frontend URL for CORS configuration
- **NEON_DB_URL**: PostgreSQL connection string with SSL and channel binding

## Risk Mitigation

### Potential Risks

1. **JWT Secret Mismatch**: Frontend and backend use different secrets
   - **Mitigation**: Document shared secret requirement, use same .env value

2. **Database Connection Failures**: Neon connection issues
   - **Mitigation**: Test connection on startup, provide clear error messages

3. **CORS Errors**: Frontend can't access backend
   - **Mitigation**: Configure CORS with correct origin, test cross-origin requests

4. **User Data Leakage**: Queries don't filter by user_id
   - **Mitigation**: Enforce user_id filtering on all queries, test with multiple users

5. **Performance Degradation**: Slow queries under load
   - **Mitigation**: Add indexes, use connection pooling, test with concurrent requests

6. **Token Expiry Handling**: Expired tokens not handled gracefully
   - **Mitigation**: Return 401 with clear message, frontend should refresh token

## Next Steps

1. **Run `/sp.tasks`**: Generate detailed task breakdown from this plan
2. **Implement Phase by Phase**: Follow the implementation phases in order
3. **Test Continuously**: Validate each phase before moving to next
4. **Integrate with Frontend**: Test full-stack integration early and often
5. **Security Audit**: Review authentication and data isolation before demo

## References

- **Specification**: [specs/002-fastapi-backend/spec.md](./spec.md)
- **Constitution**: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **PyJWT Documentation**: https://pyjwt.readthedocs.io/
