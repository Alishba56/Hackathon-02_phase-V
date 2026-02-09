# Backend API - Todo Application

**FastAPI Backend with JWT Authentication and PostgreSQL**

This is the backend API for the Todo Application, built with FastAPI, SQLModel, and Neon PostgreSQL. It provides secure RESTful endpoints for task management with JWT authentication and user data isolation.

## Features

### Phase II - Task Management
- ✅ 6 RESTful API endpoints for task CRUD operations
- ✅ JWT authentication verification (Better Auth integration)
- ✅ User data isolation (users can only access their own tasks)
- ✅ Task filtering by status (all/pending/completed)
- ✅ Task sorting by created date, title, or due date
- ✅ Comprehensive error handling with clear messages
- ✅ PostgreSQL database with connection pooling
- ✅ Automatic API documentation (Swagger UI & ReDoc)
- ✅ CORS enabled for frontend integration

### Phase III - AI Chatbot Integration (NEW)
- ✅ Natural language task management via AI chatbot
- ✅ Cohere command-r-plus model integration
- ✅ 6 MCP tools (add, list, complete, delete, update tasks, get user profile)
- ✅ Conversation history persistence
- ✅ Multilingual support (English + Urdu)
- ✅ Tool calling with parallel execution
- ✅ User profile queries
- ✅ Friendly error handling and logging

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **ORM**: SQLModel 0.0.14
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: PyJWT 2.8.0 (Better Auth integration)
- **Server**: Uvicorn 0.24.0

## Prerequisites

- Python 3.11 or higher
- Neon PostgreSQL database (connection string required)
- Better Auth secret (shared with frontend)

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Authentication (must match frontend)
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3001

# Database
NEON_DB_URL=postgresql://user:password@host/database?sslmode=require

# AI Chatbot (Phase III - NEW)
COHERE_API_KEY=your-cohere-api-key-here

# Server
PORT=8000
HOST=0.0.0.0
```

**Important**:
- The `BETTER_AUTH_SECRET` must match the secret used in the frontend for JWT verification to work.
- Get your `COHERE_API_KEY` from https://dashboard.cohere.com/ (free tier available)

### 3. Run the Server

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The server will start at `http://localhost:8000`

### 4. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

All endpoints require JWT authentication via `Authorization: Bearer <token>` header (except `/health`).

### Task Management (Phase II)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List all tasks for authenticated user |
| POST | `/api/tasks` | Create a new task |
| GET | `/api/tasks/{task_id}` | Get a specific task |
| PUT | `/api/tasks/{task_id}` | Update a task |
| DELETE | `/api/tasks/{task_id}` | Delete a task |
| PATCH | `/api/tasks/{task_id}/complete` | Toggle task completion |

### AI Chatbot (Phase III - NEW)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/{user_id}/chat` | Send message to AI chatbot for natural language task management |
| GET | `/api/{user_id}/conversations/{conversation_id}/messages` | Retrieve conversation history |

**Chat Endpoint Features:**
- Natural language task operations (add, list, complete, delete, update)
- User profile queries (email, name, account creation date)
- Multilingual support (English + Urdu)
- Conversation history persistence
- Tool calling with structured responses

### Query Parameters

**GET /api/tasks** supports:
- `status`: Filter by status (`all`, `pending`, `completed`)
- `sort`: Sort by field (`created`, `title`, `due_date`)

Example: `GET /api/tasks?status=pending&sort=due_date`

## Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── models.py            # SQLModel database models (User, Task, Conversation, Message)
├── schemas.py           # Pydantic request/response schemas
├── chat_schemas.py      # Chat-specific schemas (Phase III)
├── db.py                # Database connection and session management
├── auth.py              # JWT authentication middleware
├── routes/
│   ├── tasks.py         # Task CRUD endpoints (Phase II)
│   └── chat.py          # Chat endpoints (Phase III)
├── cohere_client.py     # Cohere API client wrapper (Phase III)
├── chat_agent.py        # Chat agent with tool calling (Phase III)
├── mcp_tools.py         # MCP tool implementations (Phase III)
├── mcp_schemas.py       # MCP tool schemas (Phase III)
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
├── .gitignore          # Git ignore rules
└── venv/               # Virtual environment (not in git)
```

## Database Schema

### Users Table (Phase II)
- `id` (string, primary key)
- `email` (string, unique, indexed)
- `name` (string)
- `password_hash` (string)
- `created_at` (datetime)
- `updated_at` (datetime)

### Tasks Table (Phase II)
- `id` (string, primary key)
- `user_id` (string, foreign key to users.id, indexed)
- `title` (string, max 200 chars)
- `description` (string, optional, max 1000 chars)
- `completed` (boolean, indexed)
- `priority` (enum: low/medium/high, optional)
- `due_date` (datetime, optional)
- `created_at` (datetime)
- `updated_at` (datetime)

**Indexes**: `user_id`, `completed`, composite `(user_id, completed)`

### Conversations Table (Phase III - NEW)
- `id` (string, primary key)
- `user_id` (string, foreign key to users.id, indexed)
- `title` (string, optional, max 255 chars, auto-generated)
- `created_at` (datetime)
- `updated_at` (datetime)

**Indexes**: `user_id`

### Messages Table (Phase III - NEW)
- `id` (string, primary key)
- `conversation_id` (string, foreign key to conversations.id, indexed)
- `role` (enum: user/assistant)
- `content` (text, max 10000 chars)
- `tool_calls` (json, optional, stores tool execution metadata)
- `created_at` (datetime, indexed)

**Indexes**: `conversation_id`, `created_at`

## Authentication

The backend verifies JWT tokens issued by Better Auth on the frontend:

1. Frontend authenticates users via Better Auth
2. Frontend receives JWT token
3. Frontend sends token in `Authorization: Bearer <token>` header
4. Backend verifies token using shared `BETTER_AUTH_SECRET`
5. Backend extracts `user_id` from token payload
6. All queries filter by `user_id` for data isolation

## Security Features

- ✅ JWT token verification on all protected endpoints
- ✅ User data isolation (queries filtered by user_id)
- ✅ Ownership checks on all task operations
- ✅ Input validation with Pydantic models
- ✅ SQL injection protection (parameterized queries)
- ✅ CORS configured for specific origin only
- ✅ No sensitive data in error messages

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `204 No Content`: Successful deletion
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User doesn't own the resource
- `404 Not Found`: Resource doesn't exist

All errors include a `detail` field with a clear message.

## Testing

### Manual Testing with curl

```bash
# Health check (no auth required)
curl http://localhost:8000/health

# List tasks (requires JWT)
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Create task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "priority": "high"}'

# Update task
curl -X PUT http://localhost:8000/api/tasks/{task_id} \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Task", "completed": true}'

# Delete task
curl -X DELETE http://localhost:8000/api/tasks/{task_id} \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Testing with Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter: `Bearer YOUR_JWT_TOKEN`
4. Test endpoints interactively

## Frontend Integration

The backend is designed to work seamlessly with the Next.js frontend:

1. Frontend uses Better Auth for user authentication
2. Frontend stores JWT token after login
3. Frontend makes API calls to `http://localhost:8000/api/*`
4. Frontend includes JWT in `Authorization` header
5. Backend verifies token and processes requests

**CORS Configuration**: The backend allows requests from `http://localhost:3001` (frontend URL) with credentials.

## Performance

- Connection pooling: 10 base connections, 20 max overflow
- Indexed queries for user_id and completed status
- Per-request database sessions (thread-safe)
- Typical response time: <50ms for single operations
- Supports 100+ concurrent requests

## Troubleshooting

### "Module not found" errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### "Connection refused" to database
- Verify `NEON_DB_URL` in `.env` is correct
- Check internet connection
- Verify Neon database is active

### "401 Unauthorized" on all requests
- Verify `BETTER_AUTH_SECRET` matches frontend
- Check JWT token format: `Bearer <token>`
- Verify token hasn't expired

### "CORS Error" from frontend
- Verify `BETTER_AUTH_URL` in `.env` matches frontend URL
- Restart backend after CORS changes

## Development

### Enable SQL Query Logging

Edit `backend/db.py`:
```python
engine = create_engine(DATABASE_URL, echo=True)  # Shows all SQL queries
```

### Add New Endpoints

1. Create route handler in `backend/routes/`
2. Import and register router in `main.py`
3. Use `get_current_user` dependency for authentication
4. Filter queries by `user_id` for data isolation

## Production Deployment

Before deploying:

- [ ] Change `BETTER_AUTH_SECRET` to strong random value
- [ ] Use production database URL
- [ ] Enable HTTPS/TLS
- [ ] Set `echo=False` in database engine
- [ ] Configure proper CORS origins
- [ ] Add rate limiting
- [ ] Set up monitoring and logging
- [ ] Review error messages (no sensitive data)

## Support

For detailed setup instructions, see: `specs/002-fastapi-backend/quickstart.md`

For API contracts, see: `specs/002-fastapi-backend/contracts/rest-api.yaml`

For implementation plan, see: `specs/002-fastapi-backend/plan.md`

## License

Part of the Todo Application Hackathon Phase 2 project.
