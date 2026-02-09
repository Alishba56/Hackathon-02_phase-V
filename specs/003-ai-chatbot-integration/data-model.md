# Data Model

**Feature**: AI Todo Chatbot Integration
**Date**: 2026-02-07
**Status**: Complete

## Overview

This document defines all data entities, their relationships, validation rules, and state transitions for the AI Todo Chatbot Integration feature. The data model extends the existing Phase II schema with two new tables: `conversations` and `messages`.

## Entity Definitions

### Conversation

Represents a chat session between a user and the AI chatbot.

**Table Name**: `conversations`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique conversation identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY → users(id) ON DELETE CASCADE | Owner of the conversation |
| title | VARCHAR(255) | NULLABLE | Auto-generated from first message |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Conversation creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last message timestamp |

**Indexes**:
- `idx_conversations_user_id` on `user_id` (for fast user conversation lookup)

**Relationships**:
- **User → Conversation**: One-to-Many (one user has many conversations)
- **Conversation → Message**: One-to-Many (one conversation has many messages)

**Validation Rules**:
- `user_id` must reference an existing user
- `title` max length: 255 characters
- `title` can be NULL (will be auto-generated on first message)
- `updated_at` must be >= `created_at`

**Business Rules**:
- Title is auto-generated from first user message (first 50 chars, truncated at word boundary)
- Conversations are soft-deleted when user is deleted (CASCADE)
- Empty conversations (no messages) are allowed temporarily
- `updated_at` is updated whenever a new message is added

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)
```

---

### Message

Represents a single message in a conversation (either from user or assistant).

**Table Name**: `messages`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique message identifier |
| conversation_id | UUID | NOT NULL, FOREIGN KEY → conversations(id) ON DELETE CASCADE | Parent conversation |
| role | VARCHAR(20) | NOT NULL, CHECK (role IN ('user', 'assistant')) | Message sender role |
| content | TEXT | NOT NULL | Message text content |
| tool_calls | JSONB | NULLABLE | Tool calls made by assistant (if any) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Message creation timestamp |

**Indexes**:
- `idx_messages_conversation_id` on `conversation_id` (for fast conversation history retrieval)
- `idx_messages_created_at` on `created_at` (for chronological ordering)

**Relationships**:
- **Conversation → Message**: One-to-Many (one conversation has many messages)

**Validation Rules**:
- `conversation_id` must reference an existing conversation
- `role` must be either 'user' or 'assistant'
- `content` cannot be empty (min length: 1 character)
- `content` max length: 10,000 characters (enforced at API level)
- `tool_calls` must be valid JSON if present

**Business Rules**:
- Messages are immutable once created (no updates)
- Messages are deleted when parent conversation is deleted (CASCADE)
- `tool_calls` is only populated for assistant messages that triggered tools
- Messages are ordered chronologically by `created_at`

**tool_calls JSON Structure**:
```json
[
  {
    "name": "add_task",
    "parameters": {
      "title": "Buy groceries",
      "description": "Milk, eggs, bread"
    },
    "result": {
      "success": true,
      "data": {
        "id": "uuid",
        "title": "Buy groceries"
      }
    }
  }
]
```

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False, max_length=10000)
    tool_calls: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

---

### Task (Existing - Phase II)

**No changes to Task entity**. Included here for reference and relationship documentation.

**Table Name**: `tasks`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique task identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY → users(id) | Task owner |
| title | VARCHAR(255) | NOT NULL | Task title |
| description | TEXT | NULLABLE | Task description |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Relationships**:
- **User → Task**: One-to-Many (one user has many tasks)

**Note**: Tasks are managed through MCP tools in the chatbot, but the underlying data structure remains unchanged from Phase II.

---

### User (Existing - Phase II)

**Extended with new relationship**. Core structure managed by Better Auth.

**Table Name**: `users`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | VARCHAR(255) | NOT NULL, UNIQUE | User email address |
| name | VARCHAR(255) | NOT NULL | User display name |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |

**Relationships**:
- **User → Task**: One-to-Many (existing Phase II)
- **User → Conversation**: One-to-Many (NEW - Phase III)

**Note**: User management remains unchanged. Better Auth handles authentication and JWT issuance.

---

## Entity Relationships Diagram

```
┌─────────────────┐
│     User        │
│  (Phase II)     │
│─────────────────│
│ id (PK)         │
│ email           │
│ name            │
│ password_hash   │
│ created_at      │
└────────┬────────┘
         │
         │ 1:N (existing)
         │
         ├──────────────────────────┐
         │                          │
         │                          │
    ┌────▼────────┐         ┌──────▼──────────┐
    │    Task     │         │  Conversation   │
    │ (Phase II)  │         │  (Phase III)    │
    │─────────────│         │─────────────────│
    │ id (PK)     │         │ id (PK)         │
    │ user_id (FK)│         │ user_id (FK)    │
    │ title       │         │ title           │
    │ description │         │ created_at      │
    │ completed   │         │ updated_at      │
    │ created_at  │         └────────┬────────┘
    │ updated_at  │                  │
    └─────────────┘                  │ 1:N
                                     │
                              ┌──────▼──────────┐
                              │    Message      │
                              │  (Phase III)    │
                              │─────────────────│
                              │ id (PK)         │
                              │ conversation_id │
                              │ role            │
                              │ content         │
                              │ tool_calls      │
                              │ created_at      │
                              └─────────────────┘
```

---

## State Transitions

### Conversation Lifecycle

```
[Created] ──(first message)──> [Active] ──(user deletes)──> [Deleted]
    │                              │
    │                              │
    └──(no messages after 24h)────┘
           (optional cleanup)
```

**States**:
1. **Created**: Conversation exists but has no messages yet
2. **Active**: Conversation has at least one message
3. **Deleted**: Conversation and all messages removed (CASCADE)

**Transitions**:
- Created → Active: When first message is added
- Active → Deleted: When user deletes conversation (future feature)
- Created → Deleted: Cleanup job removes empty conversations (optional)

---

### Message Lifecycle

```
[Created] ──(immutable)──> [Persisted]
```

**States**:
1. **Created**: Message is created and saved to database
2. **Persisted**: Message remains unchanged (immutable)

**Note**: Messages are immutable. No updates or state transitions after creation.

---

## Validation Rules Summary

### Conversation Validation

**Creation**:
- ✅ `user_id` must be valid UUID and reference existing user
- ✅ `title` is optional (auto-generated if not provided)
- ✅ `title` max length: 255 characters
- ✅ `created_at` and `updated_at` set to current timestamp

**Updates**:
- ✅ Only `updated_at` can be modified (when new message added)
- ✅ `title` can be updated (future feature)
- ❌ `user_id` cannot be changed
- ❌ `created_at` cannot be changed

**Deletion**:
- ✅ Cascade deletes all associated messages
- ✅ Only owner can delete conversation

---

### Message Validation

**Creation**:
- ✅ `conversation_id` must be valid UUID and reference existing conversation
- ✅ `role` must be 'user' or 'assistant'
- ✅ `content` min length: 1 character
- ✅ `content` max length: 10,000 characters
- ✅ `tool_calls` must be valid JSON if provided
- ✅ `created_at` set to current timestamp

**Updates**:
- ❌ Messages are immutable (no updates allowed)

**Deletion**:
- ✅ Deleted when parent conversation is deleted (CASCADE)
- ❌ Individual message deletion not supported

---

## Database Migrations

### Migration Script (Alembic)

**File**: `alembic/versions/xxx_add_chat_tables.py`

```python
"""Add chat tables for AI chatbot integration

Revision ID: xxx
Revises: yyy
Create Date: 2026-02-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers
revision = 'xxx'
down_revision = 'yyy'  # Previous migration
branch_labels = None
depends_on = None

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('NOW()'))
    )

    # Create index on user_id
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_id', UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('tool_calls', JSONB, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('NOW()'))
    )

    # Add check constraint for role
    op.create_check_constraint(
        'check_message_role',
        'messages',
        "role IN ('user', 'assistant')"
    )

    # Create indexes
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'])

def downgrade():
    # Drop tables in reverse order (messages first due to foreign key)
    op.drop_table('messages')
    op.drop_table('conversations')
```

**Run Migration**:
```bash
# Generate migration (if using autogenerate)
alembic revision --autogenerate -m "Add chat tables"

# Apply migration
alembic upgrade head

# Verify tables created
psql $NEON_DB_URL -c "\dt"
```

---

## Query Patterns

### Common Queries

**Get user's conversations**:
```python
conversations = session.exec(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.updated_at.desc())
).all()
```

**Get conversation with messages**:
```python
conversation = session.exec(
    select(Conversation)
    .where(Conversation.id == conversation_id)
    .where(Conversation.user_id == user_id)  # Security: verify ownership
).first()

messages = session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.asc())
).all()
```

**Get last 20 messages for Cohere**:
```python
messages = session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.desc())
    .limit(20)
).all()

# Reverse to chronological order
messages = list(reversed(messages))
```

**Create conversation and first message**:
```python
# Create conversation
conversation = Conversation(user_id=user_id)
session.add(conversation)
session.commit()
session.refresh(conversation)

# Create first message
message = Message(
    conversation_id=conversation.id,
    role=MessageRole.USER,
    content=user_message
)
session.add(message)

# Generate and update title
conversation.title = generate_title(user_message)
conversation.updated_at = datetime.utcnow()
session.commit()
```

**Add message to existing conversation**:
```python
message = Message(
    conversation_id=conversation_id,
    role=role,
    content=content,
    tool_calls=tool_calls  # Optional
)
session.add(message)

# Update conversation timestamp
conversation.updated_at = datetime.utcnow()
session.commit()
```

---

## Performance Considerations

### Indexing Strategy
- ✅ Index on `conversations.user_id` for fast user conversation lookup
- ✅ Index on `messages.conversation_id` for fast history retrieval
- ✅ Index on `messages.created_at` for chronological ordering
- ✅ Primary keys (UUID) automatically indexed

### Query Optimization
- Limit message queries to last 20 for Cohere API
- Use pagination for conversation list (future feature)
- Avoid N+1 queries with eager loading (if needed)
- Use connection pooling (SQLModel default)

### Storage Estimates
- Average message size: ~200 bytes (text content)
- Average conversation: 20 messages = 4 KB
- 1000 users × 10 conversations × 20 messages = 40 MB
- JSONB tool_calls: ~500 bytes per assistant message with tools
- Total storage for MVP: <100 MB

---

## Security Considerations

### Data Isolation
- All queries MUST filter by authenticated `user_id`
- Conversation ownership verified before access
- Messages only accessible through parent conversation
- No cross-user data leakage

### Data Encryption
- Passwords hashed (Better Auth handles this)
- Database encrypted at rest (Neon default)
- JWT tokens signed with secret key
- HTTPS for all API communication

### Data Retention
- Conversations persist indefinitely (user can delete)
- No automatic cleanup (future feature: archive old conversations)
- Deleted conversations cascade to messages
- Soft delete option for future implementation

---

## Conclusion

The data model extends Phase II with minimal changes, adding only two new tables for chat functionality. All entities follow consistent patterns with proper relationships, validation, and security measures.

**Status**: ✅ Data Model Complete
**Next Step**: Create API contracts (OpenAPI spec + MCP tool definitions)
