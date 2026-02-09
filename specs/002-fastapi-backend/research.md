# Research & Technical Decisions: Backend API Implementation

**Feature**: Secure Backend API for Todo Application
**Branch**: `002-fastapi-backend`
**Date**: 2026-02-07

## Overview

This document captures the research findings and technical decisions made during the planning phase for the FastAPI backend implementation. All decisions are based on best practices, framework recommendations, and the specific requirements of the hackathon project.

## 1. FastAPI Authentication Middleware Patterns

### Research Question
How should JWT authentication be implemented in FastAPI to ensure security, reusability, and maintainability?

### Findings

**FastAPI Dependency Injection Pattern**:
- FastAPI provides a powerful dependency injection system via `Depends()`
- Dependencies can be reused across multiple routes
- Automatic validation and error handling
- Integrates with OpenAPI documentation

**Best Practice**: Create a reusable `get_current_user` dependency that:
1. Extracts the Authorization header
2. Verifies the JWT token
3. Extracts user information from token claims
4. Returns a User object or raises HTTPException

### Decision
Use FastAPI's `Depends()` with a custom `get_current_user` dependency function.

### Rationale
- **Reusability**: Single implementation used across all protected routes
- **Declarative**: Route signatures clearly show authentication requirement
- **Type Safety**: FastAPI validates the dependency return type
- **Documentation**: Automatic OpenAPI security scheme generation
- **Testing**: Easy to mock for unit tests

### Implementation Pattern
```python
from fastapi import Depends, HTTPException, Header
from typing import Optional

async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")

        # Fetch or create user object
        return User(id=user_id)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Alternatives Considered
- **Middleware approach**: Global middleware for all routes
  - Rejected: Less flexible, harder to exclude specific routes
- **Manual extraction**: Extract token in each route handler
  - Rejected: Code duplication, error-prone

## 2. SQLModel Session Management

### Research Question
What is the best pattern for managing database sessions in FastAPI with SQLModel?

### Findings

**SQLModel/SQLAlchemy Session Patterns**:
1. **Global session**: Single session for entire application
2. **Per-request session**: New session for each request
3. **Session pool**: Reuse sessions from a pool

**FastAPI Recommendation**: Per-request session via dependency injection

### Decision
Use per-request session management with FastAPI dependency injection.

### Rationale
- **Thread Safety**: Each request gets its own session
- **Automatic Cleanup**: Session closed automatically after request
- **Connection Pooling**: Engine handles connection reuse
- **Transaction Management**: Clear transaction boundaries per request
- **Best Practice**: Recommended by FastAPI and SQLModel documentation

### Implementation Pattern
```python
from sqlmodel import Session, create_engine

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

# Usage in routes
@app.get("/api/tasks")
async def list_tasks(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    statement = select(Task).where(Task.user_id == current_user.id)
    tasks = session.exec(statement).all()
    return tasks
```

### Alternatives Considered
- **Global session**: `session = Session(engine)`
  - Rejected: Not thread-safe, connection leaks
- **Manual session management**: Create/close in each route
  - Rejected: Boilerplate code, easy to forget cleanup

## 3. JWT Verification Library

### Research Question
Which Python library should be used for JWT token verification?

### Findings

**Available Libraries**:
1. **PyJWT**: Lightweight, focused on JWT operations
2. **python-jose**: Includes JWT and JWS support
3. **authlib**: Comprehensive OAuth and JWT library

**PyJWT Features**:
- Simple API: `jwt.decode(token, secret, algorithms=["HS256"])`
- Well-maintained, widely used
- Handles expiration, signature verification
- Minimal dependencies

### Decision
Use PyJWT for JWT token verification.

### Rationale
- **Simplicity**: Only need JWT verification, not full OAuth
- **Lightweight**: Minimal dependencies, fast installation
- **Proven**: Used by millions of projects
- **Sufficient**: Meets all requirements for token verification
- **Documentation**: Excellent documentation and examples

### Implementation Pattern
```python
import jwt
from datetime import datetime

def verify_jwt_token(token: str, secret: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Alternatives Considered
- **authlib**: Full OAuth library
  - Rejected: Overkill for simple JWT verification
- **python-jose**: JWT + JWS support
  - Rejected: Extra features not needed

## 4. Neon PostgreSQL Connection

### Research Question
How should the application connect to Neon Serverless PostgreSQL with proper SSL and connection pooling?

### Findings

**Neon Connection Requirements**:
- SSL mode: `sslmode=require`
- Channel binding: `channel_binding=require`
- Connection pooling: Built into Neon's pooler endpoint
- Driver: psycopg2 or asyncpg

**SQLModel/SQLAlchemy Engine Configuration**:
- Connection string format: `postgresql://user:pass@host/db?params`
- Pool size configuration via engine parameters
- SSL parameters in connection string

### Decision
Use SQLModel's `create_engine` with Neon connection string including SSL parameters.

### Rationale
- **Security**: SSL encryption for all database traffic
- **Performance**: Neon's pooler handles connection reuse
- **Simplicity**: Connection string includes all parameters
- **Compatibility**: Works with SQLModel/SQLAlchemy

### Implementation Pattern
```python
from sqlmodel import create_engine

NEON_DB_URL = "postgresql://user:pass@host/db?sslmode=require&channel_binding=require"

engine = create_engine(
    NEON_DB_URL,
    echo=True,  # Log SQL queries (disable in production)
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,  # Connection pool size
    max_overflow=10  # Additional connections when pool full
)
```

### Alternatives Considered
- **asyncpg**: Async PostgreSQL driver
  - Rejected: Adds complexity, not needed for hackathon scope
- **Manual connection management**: Create connections per query
  - Rejected: Poor performance, connection overhead

## 5. CORS Configuration

### Research Question
How should CORS be configured to allow frontend access while maintaining security?

### Findings

**CORS Requirements**:
- Allow specific origin (frontend URL)
- Support credentials (cookies, authorization headers)
- Allow all HTTP methods for API
- Allow all headers for flexibility

**FastAPI CORS Middleware**:
- Built-in `CORSMiddleware`
- Configurable origins, methods, headers
- Supports credentials flag

### Decision
Configure CORS middleware with specific frontend origin and credentials support.

### Rationale
- **Security**: Only allows requests from known frontend
- **Credentials**: Supports Authorization header and cookies
- **Flexibility**: Allows all methods and headers for API
- **Development**: Easy to configure for different environments

### Implementation Pattern
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
```

### Alternatives Considered
- **Wildcard origin**: `allow_origins=["*"]`
  - Rejected: Security risk, doesn't work with credentials
- **No CORS**: Serve frontend and backend from same origin
  - Rejected: Requires reverse proxy, adds complexity

## 6. Environment Variable Loading

### Research Question
What is the best approach for loading environment variables in FastAPI?

### Findings

**Available Options**:
1. **python-dotenv**: Simple .env file loader
2. **pydantic-settings**: Type-safe settings with validation
3. **os.environ**: Direct environment variable access

**python-dotenv Features**:
- Loads .env file at startup
- Simple API: `load_dotenv()`
- No additional configuration needed
- Works with os.getenv()

### Decision
Use python-dotenv for environment variable loading.

### Rationale
- **Simplicity**: Single function call to load .env
- **Compatibility**: Works with provided .env example
- **No Overhead**: Minimal complexity for hackathon scope
- **Standard**: Widely used pattern in Python projects

### Implementation Pattern
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
NEON_DB_URL = os.getenv("NEON_DB_URL")
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")
```

### Alternatives Considered
- **pydantic-settings**: Type-safe settings class
  - Rejected: Overkill for simple key-value pairs
- **Direct os.environ**: No .env file support
  - Rejected: Requires manual environment setup

## 7. Error Handling Patterns

### Research Question
How should errors be handled consistently across all API endpoints?

### Findings

**FastAPI Error Handling**:
- `HTTPException`: Standard exception for HTTP errors
- Status codes: 400, 401, 403, 404, 500
- Detail message: User-friendly error description
- Exception handlers: Global error handling

**Best Practices**:
- Use appropriate status codes
- Provide clear error messages
- Don't expose sensitive information
- Log errors for debugging

### Decision
Use HTTPException with appropriate status codes and clear detail messages.

### Rationale
- **Consistency**: Same error format across all endpoints
- **Standards**: HTTP status codes follow REST conventions
- **User-Friendly**: Clear messages help developers debug
- **Security**: No stack traces or sensitive data in responses

### Implementation Pattern
```python
from fastapi import HTTPException

# 400 Bad Request - Validation error
if not task.title:
    raise HTTPException(status_code=400, detail="Task title is required")

# 401 Unauthorized - Authentication error
if not token:
    raise HTTPException(status_code=401, detail="Missing authentication token")

# 403 Forbidden - Authorization error
if task.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized to access this task")

# 404 Not Found - Resource not found
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

### Alternatives Considered
- **Custom exception classes**: Create domain-specific exceptions
  - Rejected: Adds complexity, HTTPException sufficient
- **Global exception handler**: Catch all exceptions
  - Rejected: Less explicit, harder to debug

## 8. Request/Response Validation

### Research Question
How should request and response data be validated in FastAPI?

### Findings

**Pydantic Models**:
- Automatic validation of request bodies
- Type checking and conversion
- Custom validators for complex rules
- Separate models for create, update, response

**FastAPI Integration**:
- Request body: Pydantic model as parameter
- Response model: `response_model` parameter
- Automatic OpenAPI documentation

### Decision
Use separate Pydantic models for TaskCreate, TaskUpdate, and TaskResponse.

### Rationale
- **Validation**: Different fields required for create vs update
- **Documentation**: Clear API contracts in OpenAPI
- **Security**: Response model controls what data is exposed
- **Type Safety**: Compile-time type checking

### Implementation Pattern
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
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

    class Config:
        from_attributes = True  # Allow ORM models
```

### Alternatives Considered
- **Single model**: Use one model for all operations
  - Rejected: Less clear validation, security concerns
- **Manual validation**: Validate in route handlers
  - Rejected: Code duplication, error-prone

## Summary of Key Decisions

| Decision Area | Choice | Primary Rationale |
|---------------|--------|-------------------|
| Authentication | FastAPI Depends with get_current_user | Reusability, type safety, documentation |
| Session Management | Per-request via dependency | Thread safety, automatic cleanup |
| JWT Library | PyJWT | Lightweight, sufficient features |
| Database Connection | SQLModel engine with Neon URL | SSL support, connection pooling |
| CORS | Specific origin with credentials | Security, frontend compatibility |
| Environment Variables | python-dotenv | Simplicity, standard pattern |
| Error Handling | HTTPException with status codes | Consistency, REST standards |
| Validation | Separate Pydantic models | Clear contracts, security |

## Implementation Readiness

All technical decisions have been made and documented. The implementation can proceed with confidence that:

1. ✅ Authentication pattern is secure and maintainable
2. ✅ Database access is efficient and thread-safe
3. ✅ JWT verification is robust and standards-compliant
4. ✅ CORS configuration allows frontend integration
5. ✅ Error handling provides clear feedback
6. ✅ Validation ensures data integrity

## Next Steps

1. Create data-model.md with database schema
2. Generate API contracts in contracts/rest-api.yaml
3. Write quickstart.md for setup instructions
4. Proceed to implementation with `/sp.tasks`
