# Quickstart Guide: Backend API Setup

**Feature**: Secure Backend API for Todo Application
**Branch**: `002-fastapi-backend`
**Date**: 2026-02-07

## Overview

This guide provides step-by-step instructions to set up, run, and test the FastAPI backend for the Todo application. Follow these instructions to get the backend running locally and integrated with the frontend.

## Prerequisites

### Required Software

- **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
- **pip**: Python package manager (included with Python)
- **Git**: Version control system
- **PostgreSQL Client** (optional): For database inspection

### Required Accounts

- **Neon Account**: For PostgreSQL database (connection string provided)

### Environment Setup

Ensure you have the following ready:
- Neon PostgreSQL connection string
- Better Auth secret (shared with frontend)
- Frontend URL for CORS configuration

## Installation

### 1. Clone Repository

```bash
cd C:\Users\alish\Desktop\phase02
git checkout 002-fastapi-backend
```

### 2. Create Backend Directory

```bash
mkdir backend
cd backend
```

### 3. Create Virtual Environment

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

Create `requirements.txt`:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.14
pyjwt==2.8.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9
```

Install packages:

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Authentication
BETTER_AUTH_SECRET=secret
BETTER_AUTH_URL=http://localhost:3001

# Database
NEON_DB_URL=postgresql://neonpg_5xMPfhq9XgaS@ep-bitter-cloud-adk6f8ds-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Server
PORT=8000
HOST=0.0.0.0
```

**Important**:
- `BETTER_AUTH_SECRET` must match the frontend configuration
- `NEON_DB_URL` should use the provided connection string
- Never commit `.env` file to version control

### 6. Verify Installation

```bash
python -c "import fastapi; import sqlmodel; import jwt; print('All dependencies installed successfully')"
```

## Project Structure

After setup, your backend directory should look like:

```
backend/
├── main.py              # FastAPI application entry point
├── models.py            # SQLModel database models
├── db.py                # Database connection and session
├── auth.py              # JWT authentication middleware
├── schemas.py           # Pydantic request/response models
├── routes/
│   └── tasks.py         # Task CRUD endpoints
├── .env                 # Environment variables (not in git)
├── requirements.txt     # Python dependencies
└── venv/                # Virtual environment (not in git)
```

## Running the Backend

### Development Mode

Start the server with auto-reload:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Production Mode

For production deployment:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify Server is Running

Open browser and navigate to:
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/health

## Testing the API

### Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter JWT token: `Bearer <your-token>`
4. Try out endpoints interactively

### Using curl

#### Health Check (No Auth Required)

```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{"status": "healthy"}
```

#### List Tasks (Auth Required)

```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json"
```

#### Create Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "This is a test task",
    "priority": "high"
  }'
```

#### Get Specific Task

```bash
curl -X GET http://localhost:8000/api/tasks/{task_id} \
  -H "Authorization: Bearer <your-jwt-token>"
```

#### Update Task

```bash
curl -X PUT http://localhost:8000/api/tasks/{task_id} \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Task Title",
    "completed": true
  }'
```

#### Toggle Task Completion

```bash
curl -X PATCH http://localhost:8000/api/tasks/{task_id}/complete \
  -H "Authorization: Bearer <your-jwt-token>"
```

#### Delete Task

```bash
curl -X DELETE http://localhost:8000/api/tasks/{task_id} \
  -H "Authorization: Bearer <your-jwt-token>"
```

### Using Postman

1. **Import OpenAPI Spec**: Import `specs/002-fastapi-backend/contracts/rest-api.yaml`
2. **Set Authorization**: Add Bearer token in Authorization tab
3. **Set Base URL**: http://localhost:8000
4. **Test Endpoints**: Use pre-configured requests

## Frontend Integration

### 1. Update Frontend API Configuration

In your Next.js frontend, update the API base URL:

```typescript
// src/lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### 2. Add Environment Variable

Create/update `.env.local` in frontend:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Test Full-Stack Integration

1. Start backend: `uvicorn main:app --reload`
2. Start frontend: `npm run dev`
3. Navigate to http://localhost:3001
4. Sign up/login via frontend
5. Create, view, update, delete tasks
6. Verify all operations work correctly

### 4. Verify JWT Integration

Check that:
- Frontend sends JWT in Authorization header
- Backend verifies JWT successfully
- User ID is extracted correctly
- Tasks are filtered by user ID

## Database Management

### View Database Schema

Connect to Neon PostgreSQL:

```bash
psql "postgresql://neonpg_5xMPfhq9XgaS@ep-bitter-cloud-adk6f8ds-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

List tables:
```sql
\dt
```

View tasks table:
```sql
SELECT * FROM tasks LIMIT 10;
```

### Reset Database (Development Only)

**Warning**: This will delete all data!

```sql
DROP TABLE tasks CASCADE;
DROP TABLE users CASCADE;
```

Restart the backend to recreate tables automatically.

## Troubleshooting

### Common Issues

#### 1. "Module not found" Error

**Problem**: Python can't find installed packages

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. "Connection refused" to Database

**Problem**: Can't connect to Neon PostgreSQL

**Solution**:
- Verify `NEON_DB_URL` in `.env` is correct
- Check internet connection
- Verify Neon database is active
- Check SSL parameters in connection string

#### 3. "401 Unauthorized" on All Requests

**Problem**: JWT verification failing

**Solution**:
- Verify `BETTER_AUTH_SECRET` matches frontend
- Check JWT token format: `Bearer <token>`
- Verify token hasn't expired
- Check token is being sent in Authorization header

#### 4. "CORS Error" from Frontend

**Problem**: Browser blocks cross-origin requests

**Solution**:
- Verify CORS middleware is configured in `main.py`
- Check `allow_origins` includes frontend URL
- Ensure `allow_credentials=True` is set
- Restart backend after CORS changes

#### 5. "403 Forbidden" on Task Access

**Problem**: User trying to access another user's task

**Solution**:
- This is expected behavior (security feature)
- Verify user is accessing their own tasks
- Check user ID in JWT matches task owner

#### 6. Port Already in Use

**Problem**: Port 8000 is occupied

**Solution**:
```bash
# Use different port
uvicorn main:app --reload --port 8001

# Or kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Debug Mode

Enable detailed logging:

```python
# main.py
import logging

logging.basicConfig(level=logging.DEBUG)
```

View SQL queries:

```python
# db.py
engine = create_engine(DATABASE_URL, echo=True)  # Logs all SQL
```

## Performance Optimization

### Connection Pooling

Adjust pool size based on load:

```python
# db.py
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # Increase for more concurrent requests
    max_overflow=20,     # Additional connections when pool full
    pool_pre_ping=True   # Verify connections before use
)
```

### Query Optimization

Monitor slow queries:

```python
import time

@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    if duration > 0.1:  # Log queries > 100ms
        print(f"Slow request: {request.url} took {duration:.2f}s")
    return response
```

## Security Checklist

Before deploying to production:

- [ ] Change `BETTER_AUTH_SECRET` to strong random value
- [ ] Use environment-specific database URLs
- [ ] Enable HTTPS (TLS/SSL)
- [ ] Set `echo=False` in database engine (disable SQL logging)
- [ ] Configure proper CORS origins (no wildcards)
- [ ] Add rate limiting middleware
- [ ] Enable request logging for audit trail
- [ ] Set up monitoring and alerting
- [ ] Review and test all error messages (no sensitive data exposure)
- [ ] Verify all queries filter by user_id

## Next Steps

1. **Run `/sp.tasks`**: Generate detailed implementation tasks
2. **Implement Backend**: Follow task breakdown phase by phase
3. **Test Continuously**: Validate each endpoint as implemented
4. **Integrate with Frontend**: Test full-stack flow early
5. **Security Review**: Audit authentication and data isolation
6. **Performance Test**: Load test with concurrent requests
7. **Documentation**: Update API docs with any changes

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **PyJWT Documentation**: https://pyjwt.readthedocs.io/
- **Neon Documentation**: https://neon.tech/docs/
- **OpenAPI Specification**: `specs/002-fastapi-backend/contracts/rest-api.yaml`

## Support

For issues or questions:
1. Check this quickstart guide
2. Review implementation plan: `specs/002-fastapi-backend/plan.md`
3. Check API contracts: `specs/002-fastapi-backend/contracts/rest-api.yaml`
4. Review data model: `specs/002-fastapi-backend/data-model.md`

## Summary

You now have:
- ✅ Backend environment configured
- ✅ Dependencies installed
- ✅ Database connection ready
- ✅ Development server running
- ✅ API documentation accessible
- ✅ Testing tools configured
- ✅ Frontend integration guide

The backend is ready for implementation. Run `/sp.tasks` to generate the detailed task breakdown and begin development.
