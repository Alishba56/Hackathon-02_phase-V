# Data Model: Backend API Database Schema

**Feature**: Secure Backend API for Todo Application
**Branch**: `002-fastapi-backend`
**Date**: 2026-02-07

## Overview

This document defines the database schema for the Todo application backend. The schema consists of two main tables: `users` (managed by Better Auth) and `tasks` (managed by the backend API). The design prioritizes data isolation, query performance, and referential integrity.

## Entity Relationship Diagram

```text
┌─────────────────────────────────────┐
│            users                     │
│  (Managed by Better Auth)           │
├─────────────────────────────────────┤
│ id          VARCHAR(255) PK         │
│ email       VARCHAR(255) UNIQUE     │
│ name        VARCHAR(255)            │
│ created_at  TIMESTAMP               │
│ updated_at  TIMESTAMP               │
└──────────────┬──────────────────────┘
               │
               │ 1:N relationship
               │
               ▼
┌─────────────────────────────────────┐
│            tasks                     │
├─────────────────────────────────────┤
│ id          VARCHAR(255) PK         │
│ user_id     VARCHAR(255) FK ────────┼──> users.id
│ title       VARCHAR(200) NOT NULL   │
│ description TEXT                    │
│ completed   BOOLEAN DEFAULT FALSE   │
│ priority    VARCHAR(20)             │
│ due_date    TIMESTAMP               │
│ created_at  TIMESTAMP DEFAULT NOW() │
│ updated_at  TIMESTAMP DEFAULT NOW() │
├─────────────────────────────────────┤
│ INDEXES:                            │
│ - idx_tasks_user_id (user_id)      │
│ - idx_tasks_completed (completed)  │
│ - idx_tasks_user_completed         │
│   (user_id, completed)              │
└─────────────────────────────────────┘
```

## Entity Definitions

### User Entity

**Purpose**: Represents an authenticated user in the system. Managed by Better Auth on the frontend.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | VARCHAR(255) | PRIMARY KEY | Unique user identifier (UUID from Better Auth) |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address |
| name | VARCHAR(255) | NOT NULL | User's display name |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Notes**:
- This table is primarily managed by Better Auth
- Backend only reads from this table for user verification
- Backend does not create or modify user records
- User ID is extracted from JWT token for all operations

**Relationships**:
- One user has many tasks (1:N)

### Task Entity

**Purpose**: Represents a todo item owned by a specific user.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | VARCHAR(255) | PRIMARY KEY | Unique task identifier (UUID) |
| user_id | VARCHAR(255) | FOREIGN KEY → users.id, NOT NULL, INDEXED | Owner of the task |
| title | VARCHAR(200) | NOT NULL | Task title (required) |
| description | TEXT | NULL | Optional detailed description |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEXED | Completion status |
| priority | VARCHAR(20) | NULL, CHECK IN ('low', 'medium', 'high') | Task priority level |
| due_date | TIMESTAMP | NULL | Optional due date |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification timestamp |

**Validation Rules**:
- `title`: Must not be empty, max 200 characters
- `description`: Max 1000 characters (enforced at application level)
- `priority`: Must be one of: 'low', 'medium', 'high' (if provided)
- `completed`: Boolean, defaults to false
- `user_id`: Must reference existing user

**Relationships**:
- Each task belongs to exactly one user (N:1)

**Business Rules**:
1. **User Isolation**: All queries MUST filter by user_id from authenticated token
2. **Ownership**: Users can only access/modify their own tasks
3. **Soft Delete**: Tasks are permanently deleted (no soft delete for MVP)
4. **Timestamps**: Automatically updated on creation and modification

## Indexes

### Primary Indexes

1. **users.id** (Primary Key)
   - Automatically indexed
   - Used for user lookups and foreign key references

2. **tasks.id** (Primary Key)
   - Automatically indexed
   - Used for direct task retrieval

### Performance Indexes

3. **idx_tasks_user_id** (tasks.user_id)
   - **Purpose**: Optimize queries filtering by user
   - **Usage**: All task list queries, user isolation enforcement
   - **Query Pattern**: `WHERE user_id = ?`
   - **Impact**: Critical for performance, used in every query

4. **idx_tasks_completed** (tasks.completed)
   - **Purpose**: Optimize filtering by completion status
   - **Usage**: Status filter queries (pending/completed)
   - **Query Pattern**: `WHERE completed = ?`
   - **Impact**: Improves filter performance

5. **idx_tasks_user_completed** (tasks.user_id, tasks.completed)
   - **Purpose**: Composite index for combined user and status filtering
   - **Usage**: Most common query pattern (user's pending/completed tasks)
   - **Query Pattern**: `WHERE user_id = ? AND completed = ?`
   - **Impact**: Optimal performance for filtered lists

### Index Strategy

**Rationale for Index Selection**:
- `user_id` index: Every query filters by user (security requirement)
- `completed` index: Common filter for pending/completed tasks
- Composite index: Covers most frequent query pattern
- No index on `created_at`: Sorting can use index scan if needed
- No index on `title`: Full-text search not required for MVP

**Query Performance Expectations**:
- Single task retrieval: <10ms (primary key lookup)
- User's task list: <50ms (indexed user_id scan)
- Filtered task list: <50ms (composite index scan)
- Task creation: <20ms (single insert with index updates)

## SQLModel Implementation

### User Model

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Task Model

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from enum import Enum

class PriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_tasks_user_id", "user_id"),
        Index("idx_tasks_completed", "completed"),
        Index("idx_tasks_user_completed", "user_id", "completed"),
    )

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship (optional, for ORM convenience)
    # user: Optional[User] = Relationship(back_populates="tasks")
```

## Database Migrations

### Initial Schema Creation

**Approach**: Use SQLModel's `create_all()` on application startup

```python
from sqlmodel import SQLModel, create_engine

engine = create_engine(DATABASE_URL)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
```

**SQL Equivalent** (for reference):

```sql
-- Users table (managed by Better Auth)
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high')),
    due_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```

## Query Patterns

### Common Queries

1. **List all tasks for a user**:
```python
statement = select(Task).where(Task.user_id == user_id)
tasks = session.exec(statement).all()
```

2. **List pending tasks for a user**:
```python
statement = select(Task).where(
    Task.user_id == user_id,
    Task.completed == False
)
tasks = session.exec(statement).all()
```

3. **Get specific task with ownership check**:
```python
statement = select(Task).where(
    Task.id == task_id,
    Task.user_id == user_id
)
task = session.exec(statement).first()
```

4. **Create task**:
```python
task = Task(
    user_id=user_id,
    title=title,
    description=description,
    priority=priority
)
session.add(task)
session.commit()
session.refresh(task)
```

5. **Update task with ownership check**:
```python
statement = select(Task).where(
    Task.id == task_id,
    Task.user_id == user_id
)
task = session.exec(statement).first()
if task:
    task.title = new_title
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
```

6. **Delete task with ownership check**:
```python
statement = select(Task).where(
    Task.id == task_id,
    Task.user_id == user_id
)
task = session.exec(statement).first()
if task:
    session.delete(task)
    session.commit()
```

## Data Integrity

### Referential Integrity

- **Foreign Key**: `tasks.user_id` → `users.id`
- **On Delete**: CASCADE (if user deleted, all their tasks deleted)
- **Enforcement**: Database-level constraint

### Application-Level Validation

- Title not empty (Pydantic validation)
- Description max length (Pydantic validation)
- Priority enum values (Pydantic validation)
- User ownership (Query filtering)

### Concurrency Handling

- **Optimistic Locking**: Use `updated_at` timestamp
- **Database Transactions**: SQLModel session handles transactions
- **Connection Pooling**: Engine manages connection reuse

## Security Considerations

### User Data Isolation

**Critical Requirement**: Every query MUST filter by authenticated user_id

**Implementation**:
```python
# CORRECT: Always filter by user_id
statement = select(Task).where(Task.user_id == current_user.id)

# WRONG: Never query without user_id filter
statement = select(Task)  # ❌ Exposes all users' data
```

**Enforcement**:
- All route handlers receive `current_user` from JWT
- All queries include `user_id` filter
- Ownership checks before update/delete operations

### SQL Injection Prevention

- **Parameterized Queries**: SQLModel uses parameterized queries
- **No String Concatenation**: Never build SQL strings manually
- **ORM Protection**: SQLModel/SQLAlchemy handles escaping

### Data Validation

- **Input Validation**: Pydantic models validate all inputs
- **Type Safety**: SQLModel enforces column types
- **Constraints**: Database constraints as last line of defense

## Performance Optimization

### Query Optimization

1. **Use Indexes**: All queries leverage user_id and completed indexes
2. **Limit Results**: Add pagination for large result sets (future enhancement)
3. **Select Specific Columns**: Use `select(Task.id, Task.title)` when full object not needed
4. **Avoid N+1 Queries**: Use joins or eager loading if fetching related data

### Connection Pooling

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,          # Base pool size
    max_overflow=10,      # Additional connections
    pool_pre_ping=True,   # Verify connections
    pool_recycle=3600     # Recycle connections after 1 hour
)
```

### Monitoring

- Log slow queries (>100ms)
- Monitor connection pool usage
- Track query execution times
- Alert on connection pool exhaustion

## Future Enhancements

### Potential Schema Extensions

1. **Task Categories/Tags**: Many-to-many relationship
2. **Task Attachments**: Separate table with file references
3. **Task Comments**: One-to-many relationship
4. **Task History**: Audit log table
5. **Shared Tasks**: Many-to-many user-task relationship

### Performance Improvements

1. **Pagination**: Add limit/offset support
2. **Full-Text Search**: Add GIN index on title/description
3. **Caching**: Redis cache for frequently accessed tasks
4. **Read Replicas**: Separate read/write database connections

## Summary

The data model provides:
- ✅ Clear entity definitions with proper types and constraints
- ✅ Efficient indexes for common query patterns
- ✅ Strong referential integrity with foreign keys
- ✅ User data isolation through consistent filtering
- ✅ Performance optimization through strategic indexing
- ✅ Security through parameterized queries and validation
- ✅ Scalability through connection pooling and query optimization

The schema is production-ready for the hackathon MVP and can be extended for future enhancements.
