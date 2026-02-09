# Task Management Skill

A skill for managing tasks through the API endpoints.

## Commands

### create-task

Create a new task.

**Usage:** `/create-task <title> [description]`

**Parameters:**
- `title` (required): The task title
- `description` (optional): The task description

**API Endpoint:** `POST /api/tasks`

**Example:**
```
/create-task "Implement login feature" "Add JWT authentication to the login endpoint"
```

---

### list-tasks

List all tasks with optional filtering and sorting.

**Usage:** `/list-tasks [status] [sort]`

**Parameters:**
- `status` (optional): Filter by status (e.g., "pending", "completed")
- `sort` (optional): Sort order (e.g., "created_at", "title")

**API Endpoint:** `GET /api/tasks`

**Example:**
```
/list-tasks pending created_at
/list-tasks
```

---

### get-task

Get details of a specific task by ID.

**Usage:** `/get-task <id>`

**Parameters:**
- `id` (required): The task ID

**API Endpoint:** `GET /api/tasks/{id}`

**Example:**
```
/get-task 42
```

---

### update-task

Update an existing task.

**Usage:** `/update-task <id> <updates>`

**Parameters:**
- `id` (required): The task ID
- `updates` (required): JSON object with fields to update

**API Endpoint:** `PUT /api/tasks/{id}`

**Example:**
```
/update-task 42 {"title": "Updated title", "description": "New description"}
```

---

### delete-task

Delete a task by ID.

**Usage:** `/delete-task <id>`

**Parameters:**
- `id` (required): The task ID

**API Endpoint:** `DELETE /api/tasks/{id}`

**Example:**
```
/delete-task 42
```

---

### toggle-complete

Toggle the completion status of a task.

**Usage:** `/toggle-complete <id>`

**Parameters:**
- `id` (required): The task ID

**API Endpoint:** `PATCH /api/tasks/{id}/complete`

**Example:**
```
/toggle-complete 42
```

## MCP Tools

The following MCP tools provide programmatic access to task management functionality:

### add_task

**Purpose:** Create a new task

**Parameters:**
- `user_id` (string, required): The user identifier
- `title` (string, required): The task title
- `description` (string, optional): The task description

**Returns:**
```json
{
  "task_id": 123,
  "status": "created",
  "title": "Task title"
}
```

**Database Operation:** Inserts a new record into the tasks table with the provided user_id

---

### list_tasks

**Purpose:** Retrieve a user's tasks with optional filtering

**Parameters:**
- `user_id` (string, required): The user identifier
- `status` (string, optional): Filter by status - accepts "all", "pending", or "completed"

**Returns:**
```json
[
  {
    "id": 123,
    "title": "Task title",
    "description": "Task description",
    "completed": false,
    "created_at": "2026-02-08T10:00:00Z",
    "updated_at": "2026-02-08T10:00:00Z"
  }
]
```

---

### complete_task

**Purpose:** Mark a task as complete

**Parameters:**
- `user_id` (string, required): The user identifier
- `task_id` (integer, required): The task identifier

**Returns:**
```json
{
  "task_id": 123,
  "status": "completed",
  "title": "Task title"
}
```

**Database Operation:** Updates the task record setting `completed=true` and `updated_at=now()`

---

### delete_task

**Purpose:** Delete a task

**Parameters:**
- `user_id` (string, required): The user identifier
- `task_id` (integer, required): The task identifier

**Returns:**
```json
{
  "task_id": 123,
  "status": "deleted",
  "title": "Task title"
}
```

**Security:** Verifies task ownership before deletion

---

### update_task

**Purpose:** Update task properties

**Parameters:**
- `user_id` (string, required): The user identifier
- `task_id` (integer, required): The task identifier
- `title` (string, optional): New task title
- `description` (string, optional): New task description

**Returns:**
```json
{
  "task_id": 123,
  "status": "updated",
  "title": "Updated task title"
}
```

**Behavior:** Only updates fields that are provided in the request

---

## Implementation Notes

When invoked, these commands should:
1. Parse the provided arguments
2. Make the appropriate HTTP request to the API endpoint
3. Handle responses and errors appropriately
4. Display results to the user in a clear format

## Error Handling

- Validate required parameters before making API calls
- Handle HTTP errors (4xx, 5xx) gracefully
- Provide clear error messages to users
- Handle network failures and timeouts
- Verify task ownership for update/delete operations
