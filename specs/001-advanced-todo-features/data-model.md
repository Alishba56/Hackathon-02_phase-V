# Data Model: Advanced Todo Features

**Feature**: Advanced Todo Features
**Branch**: 001-advanced-todo-features
**Date**: 2026-02-09

## Overview

This document defines the extended data model for the Task entity to support intermediate and advanced productivity features including priorities, tags, search, filtering, sorting, due dates, reminders, and recurring tasks.

## Entities

### Task (Extended)

**Description**: Represents a user's todo item with enhanced organizational and time-management capabilities.

**Table Name**: `tasks`

**Fields**:

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | - | Unique task identifier |
| user_id | INTEGER | NOT NULL, FOREIGN KEY → users(id) | - | Owner of the task (enforces user isolation) |
| title | VARCHAR(255) | NOT NULL | - | Task title/summary |
| description | TEXT | NULLABLE | NULL | Detailed task description |
| status | VARCHAR(20) | NOT NULL, CHECK IN ('pending', 'completed') | 'pending' | Task completion status |
| **priority** | **VARCHAR(20)** | **NOT NULL, CHECK IN ('low', 'medium', 'high', 'urgent')** | **'medium'** | **Task priority level** |
| **tags** | **JSONB** | **NOT NULL** | **'[]'::jsonb** | **Array of tag strings for categorization** |
| **due_date** | **TIMESTAMP WITH TIME ZONE** | **NULLABLE** | **NULL** | **When the task should be completed** |
| **remind_at** | **TIMESTAMP WITH TIME ZONE** | **NULLABLE** | **NULL** | **When to trigger reminder notification** |
| **recurrence_rule** | **JSONB** | **NULLABLE** | **NULL** | **Recurrence pattern definition** |
| **reminded** | **BOOLEAN** | **NOT NULL** | **FALSE** | **Internal flag: has reminder been triggered** |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | CURRENT_TIMESTAMP | Task creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | CURRENT_TIMESTAMP | Last update timestamp |

**New fields are in bold**

### Indexes

**Existing Indexes**:
- `idx_tasks_user_id` ON tasks(user_id) - For user isolation queries
- `idx_tasks_status` ON tasks(status) - For status filtering

**New Indexes**:
- `idx_tasks_due_date` ON tasks(due_date) - For due date filtering and sorting
- `idx_tasks_priority` ON tasks(priority) - For priority filtering and sorting
- `idx_tasks_tags_gin` ON tasks(tags) USING GIN - For efficient tag filtering with JSONB containment

### Relationships

- **tasks.user_id** → **users.id** (Many-to-One)
  - Each task belongs to exactly one user
  - User can have many tasks
  - ON DELETE CASCADE (when user deleted, their tasks are deleted)

## Field Details

### Priority

**Type**: String enum
**Values**: "low", "medium", "high", "urgent"
**Default**: "medium"

**Rationale**: String enum provides readable values in database and API, simplifies UI mapping, and enables straightforward SQL filtering.

**Validation**:
- Must be one of the four allowed values
- Case-sensitive (lowercase only)

**UI Mapping**:
- low → Gray badge
- medium → Yellow badge
- high → Orange badge
- urgent → Red badge

---

### Tags

**Type**: JSONB array of strings
**Default**: `[]` (empty array)

**Format**: `["tag1", "tag2", "tag3"]`

**Rationale**: JSONB provides efficient storage and querying with PostgreSQL's native JSON operators. GIN index enables fast containment queries.

**Validation**:
- Array of strings only
- Maximum 10 tags per task
- Each tag maximum 50 characters
- No duplicate tags within same task
- Tags are case-sensitive

**Query Examples**:
```sql
-- Find tasks with specific tag
WHERE tags @> '["work"]'::jsonb

-- Find tasks with any of multiple tags
WHERE tags ?| array['work', 'urgent']

-- Find tasks with all of multiple tags
WHERE tags @> '["work", "urgent"]'::jsonb
```

---

### Due Date

**Type**: TIMESTAMP WITH TIME ZONE
**Nullable**: Yes
**Default**: NULL

**Rationale**: Timestamp with timezone ensures correct handling across different user timezones. Stored in UTC, displayed in user's local timezone.

**Validation**:
- Must be valid ISO 8601 datetime
- Can be in past (for overdue tasks)
- If recurrence_rule is set, due_date must be set

**Display Logic**:
- Show relative time for near dates ("Tomorrow", "In 2 hours")
- Show absolute date for far dates ("Feb 15, 2026")
- Highlight overdue tasks (due_date < current_time and status = 'pending')

---

### Remind At

**Type**: TIMESTAMP WITH TIME ZONE
**Nullable**: Yes
**Default**: NULL

**Rationale**: Separate reminder time allows flexibility (e.g., remind 30 minutes before due date).

**Validation**:
- Must be valid ISO 8601 datetime
- Should be before due_date if both are set (warning, not hard error)
- Can be in past (will trigger immediately on next task list load)

**Behavior**:
- When remind_at <= current_time and reminded = false:
  - Log reminder message to console
  - Set reminded = true to prevent duplicate reminders
- Placeholder for future notification system (email, push, etc.)

---

### Recurrence Rule

**Type**: JSONB object
**Nullable**: Yes
**Default**: NULL

**Format**:
```json
{
  "frequency": "daily" | "weekly" | "monthly" | "custom",
  "interval": 1,
  "end_date": null | "2026-12-31T23:59:59Z"
}
```

**Fields**:
- `frequency`: Recurrence pattern type
  - "daily": Repeats every N days
  - "weekly": Repeats every N weeks
  - "monthly": Repeats every N months
  - "custom": Custom interval (future extension)
- `interval`: Number of frequency units (e.g., interval=2 with frequency="weekly" = every 2 weeks)
- `end_date`: Optional end date for recurrence (null = no end)

**Validation**:
- If recurrence_rule is set, due_date must be set
- frequency must be one of allowed values
- interval must be positive integer (1-365)
- end_date must be after due_date if set

**Behavior**:
- When task with recurrence_rule is marked completed:
  - Calculate next_due_date based on frequency and interval
  - Create new task with same title, description, priority, tags, recurrence_rule
  - New task has status='pending', new due_date, reminded=false
  - Original task remains completed

**Next Due Date Calculation**:
- daily: due_date + (interval * 1 day)
- weekly: due_date + (interval * 7 days)
- monthly: due_date + (interval * 1 month) - same day of month

---

### Reminded

**Type**: BOOLEAN
**Default**: FALSE

**Rationale**: Internal flag to track whether reminder has been triggered, preventing duplicate reminder logs.

**Behavior**:
- Set to TRUE when reminder is logged
- Reset to FALSE if remind_at is updated
- Not exposed in API responses (internal field only)

## State Transitions

### Task Completion with Recurrence

```
[Recurring Task: status=pending, recurrence_rule={...}]
           |
           | User marks complete
           v
[Original Task: status=completed]
           |
           | System creates next occurrence
           v
[New Task: status=pending, due_date=calculated_next_date]
```

**Rules**:
- Original task is marked completed (not deleted)
- New task inherits: title, description, priority, tags, recurrence_rule
- New task gets: new due_date (calculated), status='pending', reminded=false
- New task does NOT inherit: remind_at (would need recalculation)

### Reminder Trigger

```
[Task: remind_at <= now, reminded=false]
           |
           | System checks on task list load
           v
[Log reminder message to console]
           |
           v
[Task: reminded=true]
```

**Rules**:
- Reminder only triggers once (reminded flag prevents duplicates)
- Reminder triggers on next GET /api/tasks request after remind_at time
- If remind_at is updated, reminded flag resets to false

## Migration Strategy

### Database Migration Script

```sql
-- Add new columns to tasks table
ALTER TABLE tasks
  ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium'
    CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
  ADD COLUMN tags JSONB NOT NULL DEFAULT '[]'::jsonb,
  ADD COLUMN due_date TIMESTAMP WITH TIME ZONE,
  ADD COLUMN remind_at TIMESTAMP WITH TIME ZONE,
  ADD COLUMN recurrence_rule JSONB,
  ADD COLUMN reminded BOOLEAN NOT NULL DEFAULT FALSE;

-- Create indexes for performance
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_tags_gin ON tasks USING GIN(tags);

-- Add check constraint for recurrence validation
ALTER TABLE tasks
  ADD CONSTRAINT chk_recurrence_requires_due_date
  CHECK (recurrence_rule IS NULL OR due_date IS NOT NULL);
```

### Backward Compatibility

**Existing Tasks**:
- All existing tasks will have default values:
  - priority = 'medium'
  - tags = []
  - due_date = NULL
  - remind_at = NULL
  - recurrence_rule = NULL
  - reminded = FALSE

**Existing API Calls**:
- POST /api/tasks without new fields → uses defaults
- PUT /api/tasks without new fields → preserves existing values
- GET /api/tasks without query params → returns all tasks (no filtering)

**No Breaking Changes**: All existing functionality continues to work without modification.

## Validation Rules Summary

1. **Priority**: Must be one of: low, medium, high, urgent
2. **Tags**: Array of strings, max 10 items, each max 50 chars, no duplicates
3. **Due Date**: Valid timestamp, can be past or future
4. **Remind At**: Valid timestamp, should be before due_date (warning only)
5. **Recurrence Rule**: If set, due_date must be set; frequency must be valid; interval must be positive
6. **Reminded**: Boolean, internal field only
7. **User Isolation**: All queries must filter by user_id from JWT token

## Performance Considerations

**Indexes**:
- GIN index on tags enables O(log n) tag containment queries
- B-tree indexes on due_date and priority enable efficient sorting and range queries

**Query Optimization**:
- Use JSONB operators (@>, ?|, ?&) for tag filtering instead of JSON functions
- Combine filters in single WHERE clause for index usage
- Limit result sets with pagination if needed (future enhancement)

**Expected Performance**:
- Tag filtering: <100ms for 1000 tasks
- Due date range queries: <50ms for 1000 tasks
- Combined filters: <200ms for 1000 tasks
- Search (ILIKE): <500ms for 1000 tasks (can add trigram index if needed)

## Security Considerations

**User Isolation**:
- All queries MUST include `WHERE user_id = <authenticated_user_id>`
- JWT token validation required on all endpoints
- No cross-user data access permitted

**Input Validation**:
- Sanitize tag strings to prevent XSS
- Validate timestamp formats to prevent injection
- Limit tag count and length to prevent abuse

**Data Privacy**:
- Task data is private to owning user
- No sharing or collaboration features in this phase
- All timestamps stored in UTC, no timezone leakage
