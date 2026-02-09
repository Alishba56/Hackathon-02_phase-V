# API Contract: Extended Task Endpoints

**Feature**: Advanced Todo Features
**Version**: 2.0
**Base URL**: `/api`
**Authentication**: JWT Bearer token required for all endpoints

## Overview

This document defines the extended REST API for task management with support for priorities, tags, search, filtering, sorting, due dates, reminders, and recurring tasks.

## Common Types

### Task Object

```json
{
  "id": 1,
  "user_id": 123,
  "title": "Complete project proposal",
  "description": "Draft and review the Q1 project proposal document",
  "status": "pending",
  "priority": "high",
  "tags": ["work", "urgent"],
  "due_date": "2026-02-15T14:00:00Z",
  "remind_at": "2026-02-15T13:30:00Z",
  "recurrence_rule": {
    "frequency": "weekly",
    "interval": 1,
    "end_date": null
  },
  "created_at": "2026-02-09T10:00:00Z",
  "updated_at": "2026-02-09T10:00:00Z"
}
```

### Priority Enum

- `"low"` - Low priority task
- `"medium"` - Medium priority task (default)
- `"high"` - High priority task
- `"urgent"` - Urgent priority task

### Status Enum

- `"pending"` - Task not yet completed
- `"completed"` - Task completed

### Recurrence Rule Object

```json
{
  "frequency": "daily" | "weekly" | "monthly" | "custom",
  "interval": 1,
  "end_date": "2026-12-31T23:59:59Z" | null
}
```

## Endpoints

### 1. Create Task

**POST** `/api/tasks`

Creates a new task with optional advanced features.

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "string (required, max 255 chars)",
  "description": "string (optional)",
  "priority": "low|medium|high|urgent (optional, default: medium)",
  "tags": ["string", "string"] (optional, default: [], max 10 items),
  "due_date": "ISO 8601 datetime (optional)",
  "remind_at": "ISO 8601 datetime (optional)",
  "recurrence_rule": {
    "frequency": "daily|weekly|monthly|custom",
    "interval": 1,
    "end_date": "ISO 8601 datetime or null"
  } (optional)
}
```

**Response**: `201 Created`
```json
{
  "id": 1,
  "user_id": 123,
  "title": "Complete project proposal",
  "description": "Draft and review the Q1 project proposal document",
  "status": "pending",
  "priority": "high",
  "tags": ["work", "urgent"],
  "due_date": "2026-02-15T14:00:00Z",
  "remind_at": "2026-02-15T13:30:00Z",
  "recurrence_rule": {
    "frequency": "weekly",
    "interval": 1,
    "end_date": null
  },
  "created_at": "2026-02-09T10:00:00Z",
  "updated_at": "2026-02-09T10:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request` - Invalid input (missing title, invalid priority, etc.)
- `401 Unauthorized` - Missing or invalid JWT token
- `422 Unprocessable Entity` - Validation error (e.g., recurrence_rule without due_date)

**Examples**:

Basic task:
```json
{
  "title": "Buy groceries"
}
```

Task with all features:
```json
{
  "title": "Team standup meeting",
  "description": "Daily sync with the team",
  "priority": "high",
  "tags": ["work", "meetings"],
  "due_date": "2026-02-10T09:00:00Z",
  "remind_at": "2026-02-10T08:45:00Z",
  "recurrence_rule": {
    "frequency": "daily",
    "interval": 1,
    "end_date": null
  }
}
```

---

### 2. Update Task

**PUT** `/api/tasks/{task_id}`

Updates an existing task. All fields are optional; only provided fields are updated.

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Path Parameters**:
- `task_id` (integer, required) - ID of the task to update

**Request Body**:
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "status": "pending|completed (optional)",
  "priority": "low|medium|high|urgent (optional)",
  "tags": ["string"] (optional)",
  "due_date": "ISO 8601 datetime (optional, null to clear)",
  "remind_at": "ISO 8601 datetime (optional, null to clear)",
  "recurrence_rule": {
    "frequency": "daily|weekly|monthly|custom",
    "interval": 1,
    "end_date": "ISO 8601 datetime or null"
  } (optional, null to clear)
}
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "user_id": 123,
  "title": "Updated title",
  "description": "Updated description",
  "status": "pending",
  "priority": "urgent",
  "tags": ["work", "urgent", "important"],
  "due_date": "2026-02-16T14:00:00Z",
  "remind_at": "2026-02-16T13:30:00Z",
  "recurrence_rule": null,
  "created_at": "2026-02-09T10:00:00Z",
  "updated_at": "2026-02-09T15:30:00Z"
}
```

**Error Responses**:
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - Task belongs to different user
- `404 Not Found` - Task not found
- `422 Unprocessable Entity` - Validation error

---

### 3. List Tasks (Extended)

**GET** `/api/tasks`

Retrieves tasks for the authenticated user with support for search, filtering, and sorting.

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters**:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `search` | string | Search in title and description (case-insensitive) | `?search=meeting` |
| `status` | string | Filter by status (pending, completed) | `?status=pending` |
| `priority` | string | Filter by priority (low, medium, high, urgent) | `?priority=high` |
| `tags` | string | Filter by tags (comma-separated, AND logic) | `?tags=work,urgent` |
| `due_after` | ISO datetime | Filter tasks due after this date | `?due_after=2026-02-10T00:00:00Z` |
| `due_before` | ISO datetime | Filter tasks due before this date | `?due_before=2026-02-20T23:59:59Z` |
| `sort_by` | string | Sort field (due_date, priority, created_at, updated_at, title) | `?sort_by=due_date` |
| `sort_order` | string | Sort order (asc, desc) | `?sort_order=asc` |

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 123,
    "title": "Complete project proposal",
    "description": "Draft and review the Q1 project proposal document",
    "status": "pending",
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_date": "2026-02-15T14:00:00Z",
    "remind_at": "2026-02-15T13:30:00Z",
    "recurrence_rule": null,
    "created_at": "2026-02-09T10:00:00Z",
    "updated_at": "2026-02-09T10:00:00Z"
  },
  {
    "id": 2,
    "user_id": 123,
    "title": "Buy groceries",
    "description": null,
    "status": "pending",
    "priority": "medium",
    "tags": ["personal"],
    "due_date": "2026-02-10T18:00:00Z",
    "remind_at": null,
    "recurrence_rule": {
      "frequency": "weekly",
      "interval": 1,
      "end_date": null
    },
    "created_at": "2026-02-09T11:00:00Z",
    "updated_at": "2026-02-09T11:00:00Z"
  }
]
```

**Error Responses**:
- `400 Bad Request` - Invalid query parameters
- `401 Unauthorized` - Missing or invalid JWT token

**Query Examples**:

Search for tasks:
```
GET /api/tasks?search=meeting
```

Filter by priority and status:
```
GET /api/tasks?priority=high&status=pending
```

Filter by multiple tags:
```
GET /api/tasks?tags=work,urgent
```

Filter by due date range:
```
GET /api/tasks?due_after=2026-02-10T00:00:00Z&due_before=2026-02-20T23:59:59Z
```

Sort by due date:
```
GET /api/tasks?sort_by=due_date&sort_order=asc
```

Combined filters:
```
GET /api/tasks?priority=high&tags=work&status=pending&sort_by=due_date&sort_order=asc
```

---

### 4. Complete Task

**PATCH** `/api/tasks/{task_id}/complete`

Marks a task as completed. If the task has a recurrence rule, automatically creates the next occurrence.

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Path Parameters**:
- `task_id` (integer, required) - ID of the task to complete

**Request Body**: None

**Response**: `200 OK`
```json
{
  "completed_task": {
    "id": 1,
    "user_id": 123,
    "title": "Team standup meeting",
    "description": "Daily sync with the team",
    "status": "completed",
    "priority": "high",
    "tags": ["work", "meetings"],
    "due_date": "2026-02-09T09:00:00Z",
    "remind_at": "2026-02-09T08:45:00Z",
    "recurrence_rule": {
      "frequency": "daily",
      "interval": 1,
      "end_date": null
    },
    "created_at": "2026-02-08T10:00:00Z",
    "updated_at": "2026-02-09T09:15:00Z"
  },
  "next_occurrence": {
    "id": 15,
    "user_id": 123,
    "title": "Team standup meeting",
    "description": "Daily sync with the team",
    "status": "pending",
    "priority": "high",
    "tags": ["work", "meetings"],
    "due_date": "2026-02-10T09:00:00Z",
    "remind_at": null,
    "recurrence_rule": {
      "frequency": "daily",
      "interval": 1,
      "end_date": null
    },
    "created_at": "2026-02-09T09:15:00Z",
    "updated_at": "2026-02-09T09:15:00Z"
  }
}
```

**Note**: If task has no recurrence_rule, `next_occurrence` will be `null`.

**Error Responses**:
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - Task belongs to different user
- `404 Not Found` - Task not found
- `409 Conflict` - Task already completed

---

### 5. Get Task by ID

**GET** `/api/tasks/{task_id}`

Retrieves a single task by ID.

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Path Parameters**:
- `task_id` (integer, required) - ID of the task

**Response**: `200 OK`
```json
{
  "id": 1,
  "user_id": 123,
  "title": "Complete project proposal",
  "description": "Draft and review the Q1 project proposal document",
  "status": "pending",
  "priority": "high",
  "tags": ["work", "urgent"],
  "due_date": "2026-02-15T14:00:00Z",
  "remind_at": "2026-02-15T13:30:00Z",
  "recurrence_rule": null,
  "created_at": "2026-02-09T10:00:00Z",
  "updated_at": "2026-02-09T10:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - Task belongs to different user
- `404 Not Found` - Task not found

---

### 6. Delete Task

**DELETE** `/api/tasks/{task_id}`

Deletes a task permanently.

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Path Parameters**:
- `task_id` (integer, required) - ID of the task to delete

**Response**: `204 No Content`

**Error Responses**:
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - Task belongs to different user
- `404 Not Found` - Task not found

---

## Validation Rules

### Priority
- Must be one of: "low", "medium", "high", "urgent"
- Case-sensitive (lowercase only)

### Tags
- Array of strings
- Maximum 10 tags per task
- Each tag maximum 50 characters
- No duplicate tags within same task
- Empty array allowed

### Due Date
- Must be valid ISO 8601 datetime with timezone
- Can be in past (for overdue tasks)
- If recurrence_rule is set, due_date must be set

### Remind At
- Must be valid ISO 8601 datetime with timezone
- Should be before due_date (warning, not error)
- Can be in past (will trigger immediately)

### Recurrence Rule
- If set, due_date must be set
- frequency must be one of: "daily", "weekly", "monthly", "custom"
- interval must be positive integer (1-365)
- end_date must be after due_date if set

## Error Response Format

All error responses follow this format:

```json
{
  "error": "Error message",
  "detail": "Detailed explanation of the error",
  "field": "field_name (for validation errors)"
}
```

## Authentication

All endpoints require JWT authentication via Bearer token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

The JWT token must contain the `user_id` claim, which is used to enforce user isolation on all operations.

## Rate Limiting

No rate limiting in current implementation. Future consideration for production deployment.

## Backward Compatibility

All new fields are optional in requests. Existing API clients that don't send new fields will continue to work with default values:
- priority: "medium"
- tags: []
- due_date: null
- remind_at: null
- recurrence_rule: null
