# Quickstart Guide: AI Todo Chatbot Integration

**Feature**: AI Todo Chatbot Integration
**Date**: 2026-02-07
**Audience**: Developers setting up and running the feature

## Overview

This guide provides step-by-step instructions for setting up, running, and testing the AI Todo Chatbot Integration feature. Follow these instructions to get the chatbot working in your local development environment.

## Prerequisites

Before starting, ensure you have:

- ✅ Phase II Todo application fully functional (frontend + backend)
- ✅ Node.js 18+ and npm installed
- ✅ Python 3.11+ and pip installed
- ✅ Neon PostgreSQL database accessible
- ✅ Cohere API account and API key
- ✅ Git repository cloned locally

## Setup Steps

### 1. Environment Configuration

**Add Cohere API Key to `.env`**:

```bash
# Navigate to project root
cd /path/to/phase03

# Edit .env file (or create if it doesn't exist)
nano .env
```

**Add the following line**:
```env
# Existing Phase II variables
BETTER_AUTH_SECRET=your-secret-key-here
NEON_DB_URL=postgresql://user:pass@host/db
NEXT_PUBLIC_API_URL=http://localhost:8000

# NEW: Phase III Cohere API key
COHERE_API_KEY=your-cohere-api-key-here
```

**Get Cohere API Key**:
1. Visit https://dashboard.cohere.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Copy your API key
5. Paste into `.env` file

**Verify environment variables**:
```bash
# Check that all required variables are set
grep -E "COHERE_API_KEY|BETTER_AUTH_SECRET|NEON_DB_URL" .env
```

---

### 2. Install Dependencies

**Backend (Python)**:

```bash
# Navigate to backend directory
cd backend

# Install Cohere SDK
pip install cohere

# Or update requirements.txt and install all
echo "cohere>=4.0.0" >> requirements.txt
pip install -r requirements.txt

# Verify installation
python -c "import cohere; print('Cohere SDK installed:', cohere.__version__)"
```

**Frontend (Node.js)**:

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies (if not already installed)
npm install

# No new dependencies needed for Phase III
# (using existing React, Tailwind, etc.)
```

---

### 3. Database Migration

**Create and apply migration for new tables**:

```bash
# Navigate to backend directory
cd backend

# Generate migration (if using Alembic)
alembic revision --autogenerate -m "Add chat tables for AI chatbot"

# Review the generated migration file
# File location: alembic/versions/xxx_add_chat_tables.py

# Apply migration
alembic upgrade head

# Verify tables created
psql $NEON_DB_URL -c "\dt" | grep -E "conversations|messages"
```

**Expected output**:
```
 public | conversations | table | your_user
 public | messages      | table | your_user
```

**Manual migration (if Alembic not configured)**:

```sql
-- Connect to database
psql $NEON_DB_URL

-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Verify tables
\dt
```

---

### 4. Start Development Servers

**Terminal 1 - Backend (FastAPI)**:

```bash
# Navigate to backend directory
cd backend

# Start FastAPI server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
```

**Terminal 2 - Frontend (Next.js)**:

```bash
# Navigate to frontend directory
cd frontend

# Start Next.js development server
npm run dev

# Expected output:
# ▲ Next.js 16.x.x
# - Local:        http://localhost:3000
# - Ready in 2.5s
```

**Verify servers are running**:
- Backend: http://localhost:8000/docs (Swagger UI)
- Frontend: http://localhost:3000 (Application)

---

### 5. Test the Chatbot

**Step 1: Create an account or log in**

1. Open http://localhost:3000
2. Sign up with email and password (if new user)
3. Or log in with existing credentials
4. Verify you're redirected to the dashboard

**Step 2: Open the chat interface**

1. Look for the floating chat icon in the bottom-right corner
2. Click the icon to open the chat window
3. Verify the chat window opens with a welcome message

**Step 3: Test basic commands**

**Add a task**:
```
You: Add task: Buy groceries
Bot: ✓ Task 'Buy groceries' add kar diya gaya!
```

**List tasks**:
```
You: Show me all my tasks
Bot: Aap ki tasks:
     1. Buy groceries (pending)
```

**Complete a task**:
```
You: Mark 'Buy groceries' as done
Bot: ✓ Task 'Buy groceries' completed!
```

**Delete a task**:
```
You: Delete task: Buy groceries
Bot: ✓ Task 'Buy groceries' deleted successfully.
```

**Update a task**:
```
You: Change task 'Buy groceries' to 'Buy groceries and milk'
Bot: ✓ Task updated to 'Buy groceries and milk'
```

**Step 4: Test user profile queries**

**English**:
```
You: What is my email?
Bot: Your email is user@example.com
```

**Urdu**:
```
You: Mera email kya hai?
Bot: Aap ka email hai user@example.com
```

```
You: Mera naam batao
Bot: Aap ka naam hai [Your Name]
```

**Step 5: Test conversation persistence**

1. Send a few messages in the chat
2. Close the chat window
3. Reopen the chat window
4. Verify all previous messages are still visible
5. Continue the conversation
6. Restart the backend server (Ctrl+C, then restart)
7. Refresh the frontend page
8. Open the chat again
9. Verify conversation history is still intact

---

## Troubleshooting

### Issue: "Cohere API key not found"

**Symptoms**: Backend logs show error about missing API key

**Solution**:
```bash
# Verify .env file has COHERE_API_KEY
cat .env | grep COHERE_API_KEY

# If missing, add it:
echo "COHERE_API_KEY=your-key-here" >> .env

# Restart backend server
```

---

### Issue: "Tables 'conversations' or 'messages' do not exist"

**Symptoms**: Database errors when trying to use chat

**Solution**:
```bash
# Check if tables exist
psql $NEON_DB_URL -c "\dt" | grep -E "conversations|messages"

# If not found, run migration again
cd backend
alembic upgrade head

# Or create tables manually (see step 3)
```

---

### Issue: "Chat icon not visible"

**Symptoms**: Floating chat icon doesn't appear on dashboard

**Solution**:
1. Verify you're logged in (check for JWT token in browser dev tools)
2. Check browser console for JavaScript errors
3. Verify ChatbotIcon component is imported in dashboard page
4. Clear browser cache and hard refresh (Ctrl+Shift+R)

---

### Issue: "401 Unauthorized" when sending messages

**Symptoms**: Chat requests fail with 401 error

**Solution**:
```bash
# Check JWT token in browser dev tools
# Application > Local Storage > JWT token

# Verify token is being sent in Authorization header
# Network tab > Chat request > Headers > Authorization: Bearer <token>

# If token is missing or invalid, log out and log in again
```

---

### Issue: "Tool calls not working"

**Symptoms**: Chatbot responds but doesn't execute task operations

**Solution**:
1. Check backend logs for tool execution errors
2. Verify MCP tools are properly registered with Cohere client
3. Test individual tools directly via Swagger UI (/docs)
4. Check database permissions for task operations

---

### Issue: "Slow response times"

**Symptoms**: Chat takes >5 seconds to respond

**Solution**:
1. Check Cohere API status: https://status.cohere.com/
2. Verify database connection is fast (test with simple query)
3. Check if message history is too long (should be limited to 20)
4. Monitor backend logs for slow queries
5. Consider upgrading Cohere plan for higher rate limits

---

## Testing Checklist

Use this checklist to verify all functionality is working:

### Basic Functionality
- [ ] Chat icon appears when logged in
- [ ] Chat icon hidden when logged out
- [ ] Chat window opens/closes smoothly
- [ ] Messages display correctly (user right, bot left)
- [ ] Typing indicator shows during processing
- [ ] Auto-scroll to latest message works

### Task Operations
- [ ] Add task: "Add task: Buy milk"
- [ ] List all tasks: "Show me all my tasks"
- [ ] List pending tasks: "Show pending tasks"
- [ ] List completed tasks: "Show completed tasks"
- [ ] Complete task: "Mark task X as done"
- [ ] Delete task: "Delete task X"
- [ ] Update task: "Change task X to Y"

### User Profile
- [ ] Get email: "What is my email?"
- [ ] Get name: "Who am I?"
- [ ] Get profile: "Show my profile"
- [ ] Urdu query: "Mera email kya hai?"

### Multilingual Support
- [ ] English commands work
- [ ] Urdu commands work
- [ ] Mixed language conversation works
- [ ] Responses match query language

### Persistence
- [ ] Conversation history persists after closing chat
- [ ] Conversation history persists after page refresh
- [ ] Conversation history persists after backend restart
- [ ] New conversation created if none exists

### Security
- [ ] Cannot access chat without login
- [ ] Cannot access other users' tasks
- [ ] Cannot access other users' conversations
- [ ] JWT validation works correctly

### Integration
- [ ] Tasks created via chat appear in main task list
- [ ] Tasks completed via chat update in main task list
- [ ] Tasks deleted via chat removed from main task list
- [ ] Phase II functionality still works (no regressions)

### Error Handling
- [ ] Empty message rejected with friendly error
- [ ] Invalid task ID shows "Task not found"
- [ ] Network error shows retry option
- [ ] Expired JWT prompts re-login

---

## Development Workflow

### Making Changes

**Backend changes**:
1. Edit files in `backend/src/`
2. FastAPI auto-reloads (if using `--reload` flag)
3. Test changes via Swagger UI or chat interface
4. Check logs for errors

**Frontend changes**:
1. Edit files in `frontend/src/`
2. Next.js auto-reloads (hot module replacement)
3. Test changes in browser
4. Check browser console for errors

**Database changes**:
1. Create new Alembic migration
2. Review generated SQL
3. Apply migration: `alembic upgrade head`
4. Verify changes: `psql $NEON_DB_URL -c "\dt"`

### Running Tests

**Backend tests**:
```bash
cd backend
pytest tests/ -v

# Run specific test file
pytest tests/test_chat_agent.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

**Frontend tests**:
```bash
cd frontend
npm test

# Run specific test
npm test -- ChatWindow.test.tsx

# Run with coverage
npm test -- --coverage
```

---

## API Documentation

### Swagger UI

Access interactive API documentation at:
- http://localhost:8000/docs

### Chat Endpoint

**POST /api/{user_id}/chat**

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "conversation_id": "optional-uuid",
  "message": "Add task: Buy groceries"
}
```

**Response**:
```json
{
  "conversation_id": "uuid",
  "response": "✓ Task 'Buy groceries' add kar diya gaya!",
  "tool_calls": [
    {
      "name": "add_task",
      "parameters": {"title": "Buy groceries"},
      "result": {
        "success": true,
        "data": {"id": "uuid", "title": "Buy groceries"}
      }
    }
  ]
}
```

---

## Production Deployment

### Environment Variables

Ensure all production environment variables are set:

```env
# Production values
COHERE_API_KEY=prod-key-here
BETTER_AUTH_SECRET=strong-secret-key
NEON_DB_URL=postgresql://prod-connection-string
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Optional: ChatKit domain allowlist
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key
```

### Database Migration

```bash
# Run migrations on production database
alembic upgrade head

# Verify tables created
psql $NEON_DB_URL -c "\dt"
```

### Build and Deploy

**Backend**:
```bash
cd backend
pip install -r requirements.txt
gunicorn main:app --workers 4 --bind 0.0.0.0:8000
```

**Frontend**:
```bash
cd frontend
npm run build
npm start
```

### Health Checks

- Backend: http://your-domain.com/health
- Frontend: http://your-domain.com/
- Database: Check connection with `psql $NEON_DB_URL -c "SELECT 1"`

---

## Additional Resources

### Documentation
- [Cohere API Docs](https://docs.cohere.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)

### Support
- GitHub Issues: [Your repo URL]
- Team Chat: [Your team chat link]
- Email: [Support email]

---

## Next Steps

After completing this quickstart:

1. ✅ Verify all tests pass
2. ✅ Review code for Phase III implementation
3. ✅ Test edge cases and error scenarios
4. ✅ Prepare demo for hackathon judges
5. ✅ Document any issues or improvements

**Ready for production?** Follow the deployment checklist above.

**Need help?** Check the troubleshooting section or contact the team.

---

**Last Updated**: 2026-02-07
**Version**: 1.0.0
**Status**: ✅ Complete
