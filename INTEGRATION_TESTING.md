# Integration Testing Guide

**Purpose**: Step-by-step guide to test the full-stack Todo application
**Date**: 2026-02-07

## Prerequisites

- Backend running on http://localhost:8001
- Frontend running on http://localhost:3000
- Neon PostgreSQL database accessible
- Better Auth configured with matching secrets

---

## Test Suite 1: Backend API Testing

### Setup
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Test 1.1: Health Check
```bash
curl http://localhost:8001/health
```
**Expected**: `{"status":"healthy"}`

### Test 1.2: API Documentation
- Navigate to http://localhost:8001/docs
- **Expected**: Swagger UI loads with all 6 endpoints visible

### Test 1.3: Authentication - No Token
```bash
curl -X GET http://localhost:8001/api/tasks
```
**Expected**: 401 Unauthorized with error message

### Test 1.4: Authentication - Invalid Token
```bash
curl -X GET http://localhost:8001/api/tasks \
  -H "Authorization: Bearer invalid_token_here"
```
**Expected**: 401 Unauthorized with "Invalid token" message

### Test 1.5: Create Task (with valid token)
```bash
# First, generate a test token (see backend/generate_test_token.py)
export TOKEN="your_jwt_token_here"

curl -X POST http://localhost:8001/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "This is a test task",
    "priority": "high"
  }'
```
**Expected**: 201 Created with task JSON including id

### Test 1.6: List Tasks
```bash
curl -X GET http://localhost:8001/api/tasks \
  -H "Authorization: Bearer $TOKEN"
```
**Expected**: 200 OK with array of tasks

### Test 1.7: Get Specific Task
```bash
# Use task_id from previous response
curl -X GET http://localhost:8001/api/tasks/{task_id} \
  -H "Authorization: Bearer $TOKEN"
```
**Expected**: 200 OK with task details

### Test 1.8: Update Task
```bash
curl -X PUT http://localhost:8001/api/tasks/{task_id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Task Title",
    "completed": true
  }'
```
**Expected**: 200 OK with updated task

### Test 1.9: Toggle Completion
```bash
curl -X PATCH http://localhost:8001/api/tasks/{task_id}/complete \
  -H "Authorization: Bearer $TOKEN"
```
**Expected**: 200 OK with toggled completion status

### Test 1.10: Delete Task
```bash
curl -X DELETE http://localhost:8001/api/tasks/{task_id} \
  -H "Authorization: Bearer $TOKEN"
```
**Expected**: 204 No Content

### Test 1.11: Filtering - Pending Tasks
```bash
curl -X GET "http://localhost:8001/api/tasks?status=pending" \
  -H "Authorization: Bearer $TOKEN"
```
**Expected**: 200 OK with only incomplete tasks

### Test 1.12: Filtering - Completed Tasks
```bash
curl -X GET "http://localhost:8001/api/tasks?status=completed" \
  -H "Authorization: Bearer $TOKEN"
```
**Expected**: 200 OK with only completed tasks

### Test 1.13: Sorting - By Title
```bash
curl -X GET "http://localhost:8001/api/tasks?sort=title" \
  -H "Authorization: Bearer $TOKEN"
```
**Expected**: 200 OK with tasks sorted alphabetically

### Test 1.14: Combined Filter and Sort
```bash
curl -X GET "http://localhost:8001/api/tasks?status=pending&sort=created" \
  -H "Authorization: Bearer $TOKEN"
```
**Expected**: 200 OK with pending tasks sorted by creation date

### Test 1.15: User Isolation
```bash
# Create a second user token with different user_id
export TOKEN2="second_user_token_here"

# Try to access first user's task with second user's token
curl -X GET http://localhost:8001/api/tasks/{first_user_task_id} \
  -H "Authorization: Bearer $TOKEN2"
```
**Expected**: 403 Forbidden

---

## Test Suite 2: Frontend UI Testing

### Setup
```bash
npm run dev
# Navigate to http://localhost:3000
```

### Test 2.1: Landing Page
- Navigate to http://localhost:3000
- **Expected**: Landing page loads with navigation to login/signup

### Test 2.2: Login Page
- Navigate to http://localhost:3000/login
- **Expected**: Login form displays with email and password fields

### Test 2.3: Form Validation - Empty Fields
- Click "Sign in" without entering credentials
- **Expected**: Error messages appear for required fields

### Test 2.4: Form Validation - Invalid Email
- Enter "invalid-email" in email field
- Enter "password123" in password field
- Click "Sign in"
- **Expected**: "Please enter a valid email address" error

### Test 2.5: Form Validation - Short Password
- Enter "test@example.com" in email field
- Enter "123" in password field
- Click "Sign in"
- **Expected**: "Password must be at least 6 characters" error

### Test 2.6: Loading State
- Enter valid credentials
- Click "Sign in"
- **Expected**: Button shows spinner and "Signing in..." text

### Test 2.7: Signup Page
- Navigate to http://localhost:3000/signup
- **Expected**: Signup form with name, email, password, confirm password

### Test 2.8: Signup Validation - Password Mismatch
- Enter "John Doe" in name
- Enter "test@example.com" in email
- Enter "Password123" in password
- Enter "Password456" in confirm password
- Click "Create account"
- **Expected**: "Passwords do not match" error

### Test 2.9: Signup Validation - Weak Password
- Enter "password" in password field
- **Expected**: Error about password requirements (uppercase, lowercase, number)

### Test 2.10: Dashboard Access (Authenticated)
- Complete login flow
- **Expected**: Redirect to /dashboard with task list

### Test 2.11: Theme Toggle
- Click theme toggle button in header
- **Expected**: UI switches between light and dark mode smoothly

### Test 2.12: Responsive Design - Mobile
- Resize browser to mobile width (< 768px)
- **Expected**:
  - Mobile navigation appears
  - FAB (Floating Action Button) visible
  - Layout adapts to mobile view

### Test 2.13: Responsive Design - Desktop
- Resize browser to desktop width (> 1024px)
- **Expected**:
  - Sidebar visible
  - Desktop navigation
  - Add Task button in header

### Test 2.14: Empty State
- View dashboard with no tasks
- **Expected**: Empty state component with "No tasks yet" message

### Test 2.15: Create Task
- Click "Add Task" button
- Enter task details
- Click "Create"
- **Expected**:
  - Task appears in list immediately (optimistic update)
  - Success feedback

### Test 2.16: Task Completion Animation
- Click checkbox on a task
- **Expected**:
  - Smooth strike-through animation
  - Task marked as completed
  - Optimistic update (immediate UI response)

### Test 2.17: Edit Task
- Click edit button on a task
- Modify task details
- Save changes
- **Expected**: Task updates with new information

### Test 2.18: Delete Task
- Click delete button on a task
- Confirm deletion
- **Expected**: Task removed from list with animation

### Test 2.19: Keyboard Navigation
- Use Tab key to navigate through form fields
- **Expected**:
  - Focus indicators visible
  - Logical tab order
  - All interactive elements accessible

### Test 2.20: Focus States
- Tab through interactive elements
- **Expected**: Clear focus rings on all focusable elements

---

## Test Suite 3: Full-Stack Integration

### Test 3.1: Complete User Flow
1. Start backend and frontend
2. Navigate to signup page
3. Create new account
4. Verify redirect to dashboard
5. Create 3 tasks with different priorities
6. Mark one task as complete
7. Edit one task
8. Delete one task
9. Filter by pending tasks
10. Sort by title
11. Toggle theme
12. Sign out
13. Sign in again
14. Verify tasks persist

**Expected**: All operations succeed without errors

### Test 3.2: CORS Verification
- Open browser DevTools Network tab
- Perform any API operation from frontend
- **Expected**:
  - No CORS errors in console
  - Requests include credentials
  - Responses have proper CORS headers

### Test 3.3: Error Handling
- Stop backend server
- Try to create a task from frontend
- **Expected**: User-friendly error message displayed

### Test 3.4: Token Expiry
- Use an expired JWT token
- Try to access protected route
- **Expected**: 401 error, redirect to login

---

## Test Suite 4: Performance Testing

### Test 4.1: Backend Response Time
```bash
# Install Apache Bench if not available
# Test GET /api/tasks endpoint
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/tasks
```
**Expected**: Average response time < 200ms

### Test 4.2: Concurrent Requests
```bash
# Test with 100 concurrent requests
ab -n 100 -c 100 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/tasks
```
**Expected**:
- No failed requests
- No connection errors
- Response time < 500ms

### Test 4.3: Frontend Load Time
- Open browser DevTools Performance tab
- Navigate to dashboard
- **Expected**:
  - First Contentful Paint < 1s
  - Time to Interactive < 2s
  - Total load time < 2s

### Test 4.4: Bundle Size
```bash
npm run build
```
**Expected**:
- Check .next/static for bundle sizes
- Main bundle < 200KB gzipped

---

## Test Suite 5: Accessibility Testing

### Test 5.1: Keyboard Navigation
- Use only keyboard (no mouse)
- Navigate through entire application
- **Expected**: All features accessible via keyboard

### Test 5.2: Screen Reader (NVDA/JAWS/VoiceOver)
- Enable screen reader
- Navigate through application
- **Expected**:
  - All content announced properly
  - Form labels read correctly
  - Button purposes clear

### Test 5.3: Color Contrast
- Use browser extension (e.g., axe DevTools)
- Check all pages
- **Expected**: WCAG AA compliance (4.5:1 for normal text)

### Test 5.4: Focus Indicators
- Tab through all interactive elements
- **Expected**: Visible focus indicators on all elements

### Test 5.5: ARIA Labels
- Inspect elements in DevTools
- **Expected**: Proper ARIA labels on all interactive elements

---

## Test Suite 6: Security Testing

### Test 6.1: SQL Injection
```bash
# Try SQL injection in task title
curl -X POST http://localhost:8001/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test'; DROP TABLE tasks; --"
  }'
```
**Expected**: Task created with literal string, no SQL execution

### Test 6.2: XSS Prevention
- Create task with title: `<script>alert('XSS')</script>`
- View task in frontend
- **Expected**: Script not executed, displayed as text

### Test 6.3: JWT Tampering
- Modify JWT token payload
- Try to access API
- **Expected**: 401 Unauthorized

### Test 6.4: Sensitive Data Exposure
- Check all error messages
- **Expected**: No sensitive data (database details, stack traces) exposed

---

## Test Results Template

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| 1.1 | Health Check | ⬜ | |
| 1.2 | API Documentation | ⬜ | |
| 1.3 | Auth - No Token | ⬜ | |
| ... | ... | ⬜ | |

**Legend**: ✅ Pass | ❌ Fail | ⬜ Not Tested | ⚠️ Warning

---

## Troubleshooting

### Backend Not Starting
- Check virtual environment is activated
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check .env file exists with correct values
- Verify database connection string

### Frontend Not Starting
- Check Node.js version (14+)
- Run `npm install` to install dependencies
- Check for port conflicts
- Verify .env.local file exists

### CORS Errors
- Verify BETTER_AUTH_URL in backend .env matches frontend URL
- Check CORS middleware configuration in main.py
- Ensure credentials are included in requests

### Authentication Failures
- Verify BETTER_AUTH_SECRET matches in both backend and frontend
- Check JWT token format (Bearer prefix)
- Verify token hasn't expired
- Check user exists in database

---

## Automated Testing Script

```bash
#!/bin/bash
# run-integration-tests.sh

echo "Starting Integration Tests..."

# Start backend
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
sleep 3

# Start frontend
cd ..
npm run dev &
FRONTEND_PID=$!
sleep 5

# Run tests
echo "Running backend tests..."
# Add test commands here

echo "Running frontend tests..."
# Add test commands here

# Cleanup
kill $BACKEND_PID
kill $FRONTEND_PID

echo "Tests complete!"
```

---

## Success Criteria

All tests must pass for production readiness:
- ✅ All backend endpoints respond correctly
- ✅ Authentication works properly
- ✅ User data isolation enforced
- ✅ Frontend loads without errors
- ✅ All user flows complete successfully
- ✅ Performance metrics met
- ✅ Accessibility standards met
- ✅ Security vulnerabilities addressed
