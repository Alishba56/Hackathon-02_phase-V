# Authentication Skill

A skill for managing user authentication through JWT-based API endpoints.

## Commands

### signup

Register a new user account.

**Usage:** `/signup <email> <password> <name>`

**Parameters:**
- `email` (required): User's email address
- `password` (required): User's password
- `name` (required): User's full name

**API Endpoint:** `POST /api/auth/signup`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Example:**
```
/signup user@example.com myPassword123 "John Doe"
```

---

### login

Authenticate an existing user and receive a JWT token.

**Usage:** `/login <email> <password>`

**Parameters:**
- `email` (required): User's email address
- `password` (required): User's password

**API Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Example:**
```
/login user@example.com myPassword123
```

---

### get-current-user

Get the currently authenticated user's information from JWT token.

**Usage:** `/get-current-user`

**Parameters:** None (uses JWT from Authorization header)

**API Endpoint:** `GET /api/auth/me`

**Headers Required:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-02-08T10:30:00Z"
}
```

**Example:**
```
/get-current-user
```

---

### protect-route

Middleware function to verify JWT and inject user_id into request context.

**Usage:** Applied automatically to protected routes

**Functionality:**
- Extracts JWT token from Authorization header
- Verifies token signature and expiration
- Decodes user_id from token payload
- Injects user_id into request context for downstream handlers
- Returns 401 Unauthorized if token is missing or invalid

**Implementation Pattern:**
```javascript
// Middleware usage
app.get('/api/protected-resource', protectRoute, (req, res) => {
  const userId = req.user.id; // Injected by middleware
  // Handle protected resource
});
```

**Error Responses:**
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Token expired or malformed

---

## Implementation Notes

### JWT Token Management

**Token Storage:**
- Store JWT token in localStorage or secure cookie after login/signup
- Include token in Authorization header for protected requests: `Authorization: Bearer <token>`

**Token Format:**
```
Header: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Payload:**
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "iat": 1675849200,
  "exp": 1675935600
}
```

### Security Considerations

1. **Password Requirements:**
   - Minimum 8 characters
   - Should include mix of letters, numbers, and special characters
   - Passwords are hashed with bcrypt before storage

2. **Token Expiration:**
   - Tokens typically expire after 24 hours
   - Implement token refresh mechanism for long-lived sessions

3. **HTTPS Only:**
   - Always use HTTPS in production to protect tokens in transit
   - Never log or expose tokens in error messages

4. **Error Handling:**
   - Don't reveal whether email exists during login failures
   - Use generic "Invalid credentials" message for security

### Common Workflows

**Registration Flow:**
```
1. User submits signup form
2. POST /api/auth/signup
3. Receive JWT token
4. Store token in localStorage
5. Redirect to dashboard
```

**Login Flow:**
```
1. User submits login form
2. POST /api/auth/login
3. Receive JWT token
4. Store token in localStorage
5. Redirect to dashboard
```

**Protected Request Flow:**
```
1. Retrieve token from localStorage
2. Add Authorization header to request
3. Make API call to protected endpoint
4. Server validates token via protect_route middleware
5. Request proceeds with user_id in context
```

**Logout Flow:**
```
1. Remove token from localStorage
2. Redirect to login page
3. (Optional) Call logout endpoint to invalidate token server-side
```

## Error Handling

### Signup Errors
- `400 Bad Request` - Invalid email format or missing fields
- `409 Conflict` - Email already registered
- `422 Unprocessable Entity` - Password doesn't meet requirements

### Login Errors
- `400 Bad Request` - Missing email or password
- `401 Unauthorized` - Invalid credentials
- `429 Too Many Requests` - Rate limit exceeded

### Protected Route Errors
- `401 Unauthorized` - Missing, invalid, or expired token
- `403 Forbidden` - Valid token but insufficient permissions

## Example Usage

```bash
# Signup
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123","name":"John Doe"}'

# Login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'

# Get current user (with token)
curl -X GET http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Access protected resource
curl -X GET http://localhost:3000/api/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Integration with Task Management

Protected task endpoints should use the `protect_route` middleware:

```javascript
// All task operations require authentication
app.post('/api/tasks', protectRoute, createTask);
app.get('/api/tasks', protectRoute, listTasks);
app.get('/api/tasks/:id', protectRoute, getTask);
app.put('/api/tasks/:id', protectRoute, updateTask);
app.delete('/api/tasks/:id', protectRoute, deleteTask);
app.patch('/api/tasks/:id/complete', protectRoute, toggleComplete);
```

This ensures that:
- Only authenticated users can manage tasks
- Tasks are associated with the authenticated user
- User context is available in all handlers via `req.user.id`

---

## MCP Tools

The following MCP tools provide programmatic access to user profile functionality:

### get_user_profile

**Purpose:** Retrieve the current user's basic profile information

**Parameters:**
- `user_id` (string, required): The user identifier

**Returns:**
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "createdAt": "2026-02-08T10:30:00Z"
}
```

**Database Operation:** Fetches user record from the users table (managed by Better Auth)

**Security:** Only returns profile data for the matching user_id. This ensures users can only access their own profile information and prevents unauthorized access to other users' data.

**Usage Notes:**
- The user_id must match the authenticated user's ID
- Returns ISO 8601 formatted timestamp for createdAt
- All fields are guaranteed to be present in the response
- This tool integrates with Better Auth's user management system
