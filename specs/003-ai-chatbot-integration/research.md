# Research & Technical Decisions

**Feature**: AI Todo Chatbot Integration
**Date**: 2026-02-07
**Status**: Complete

## Overview

This document captures all research findings and architectural decisions made during the planning phase for the AI Todo Chatbot Integration feature. All decisions are final and will guide implementation.

## Key Architectural Decisions

### 1. Cohere Model Selection

**Decision**: Use `command-r-plus` model

**Rationale**:
- Superior tool-calling accuracy and reasoning capabilities compared to command-r
- Better multilingual support for English + Urdu natural language understanding
- More reliable for complex task management commands with multiple parameters
- Hackathon demo requires best-in-class performance to impress judges
- Cost difference is acceptable for demo/MVP phase

**Alternatives Considered**:
- **command-r**: Faster (lower latency) and cheaper per token
  - **Rejected because**: Accuracy and reliability are more critical than speed for hackathon demo
  - Tool-calling accuracy is lower, which could lead to failed commands
  - Multilingual support is less robust

**Implementation Impact**:
- API calls will use `model="command-r-plus"` parameter
- Expected response time: 1-2 seconds per request
- Token costs: ~$0.003 per 1K input tokens, ~$0.015 per 1K output tokens

**References**:
- Cohere documentation: https://docs.cohere.com/docs/command-r-plus
- Tool calling guide: https://docs.cohere.com/docs/tool-use

---

### 2. Tool Calling Implementation

**Decision**: Use Cohere native tool calling API

**Rationale**:
- Built-in support for parallel tool execution (can call multiple tools in one request)
- More reliable than forcing JSON mode with custom parsing
- Structured outputs with automatic validation
- Official SDK support with type safety
- Reduces custom code and potential bugs

**Alternatives Considered**:
- **Force JSON mode with custom parsing**: Manually parse tool calls from text response
  - **Rejected because**: Lower reliability, more error-prone, requires custom validation logic
  - No parallel tool execution support
  - More maintenance burden

**Implementation Impact**:
- Tools defined as list of dictionaries with Cohere-compatible JSON schema
- Use `client.chat(tools=tools_list)` parameter
- Handle `response.tool_calls` array for execution
- Pass `tool_results` back to Cohere for final response generation

**Code Pattern**:
```python
tools = [
    {
        "name": "add_task",
        "description": "Add a new task for the user",
        "parameter_definitions": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string", "required": False}
        }
    }
]

response = client.chat(
    message=user_message,
    model="command-r-plus",
    tools=tools,
    chat_history=history
)

if response.tool_calls:
    # Execute tools and collect results
    tool_results = execute_tools(response.tool_calls)
    # Get final response
    final_response = client.chat(
        message=user_message,
        model="command-r-plus",
        tools=tools,
        tool_results=tool_results,
        chat_history=history
    )
```

---

### 3. Chat UI Technology

**Decision**: Hybrid approach - OpenAI ChatKit with custom Tailwind fallback

**Rationale**:
- **Primary**: OpenAI ChatKit provides production-ready chat UI with minimal setup
  - Professional appearance, battle-tested components
  - Handles message rendering, input, scrolling automatically
  - Can be configured with domain allowlist for hosted mode
- **Fallback**: Custom React + Tailwind component ensures project completion
  - Full control over styling and behavior
  - Matches existing Phase II design system
  - No external dependencies or setup issues

**Implementation Plan**:
1. Attempt ChatKit integration first
2. Configure domain allowlist for production deployment
3. If setup issues arise (API keys, domain verification, etc.), switch to custom component
4. Document both approaches in quickstart.md

**Alternatives Considered**:
- **Pure custom implementation**: Build everything from scratch
  - **Rejected because**: More development time, reinventing the wheel
  - ChatKit provides better UX out of the box
- **Pure ChatKit**: Rely entirely on hosted solution
  - **Rejected because**: Risk of setup issues blocking progress during hackathon

**Implementation Impact**:
- Frontend will have conditional rendering: ChatKit if available, custom if not
- Custom component will use existing Tailwind classes for consistency
- Both approaches will call the same backend API endpoint

---

### 4. Floating Icon Design

**Decision**: Modern circular FAB (Floating Action Button) with pulse animation

**Rationale**:
- Familiar pattern used by WhatsApp, Telegram, Intercom, and other chat applications
- Non-intrusive: doesn't block main UI content
- Always accessible: fixed position in bottom-right corner
- Pulse animation provides visual feedback for new messages (future enhancement)

**Styling Specifications**:
- Position: `fixed bottom-6 right-6`
- Size: 60px diameter (w-15 h-15 in Tailwind)
- Z-index: 1000 (above all other content)
- Background: Primary brand color with gradient
- Icon: Chat bubble or message icon (from Heroicons or Lucide)
- Shadow: `shadow-lg` for depth
- Hover effect: Scale up slightly (scale-110)
- Pulse animation: Subtle ring animation when new messages arrive

**Alternatives Considered**:
- **Chat bubble icon in header**: Less accessible, requires scrolling
  - **Rejected because**: Not always visible, less modern UX
- **Sidebar toggle**: Takes up more space
  - **Rejected because**: More intrusive, conflicts with main UI

**Implementation Impact**:
- Single component: `ChatbotIcon.tsx`
- Conditional rendering: Only show when user is authenticated
- Click handler: Opens ChatWindow modal

---

### 5. Message History Management

**Decision**: Truncate to last 20 messages per conversation

**Rationale**:
- Prevents token limit issues with Cohere API (command-r-plus has 128K context but costs scale)
- Maintains sufficient context for task management conversations
- Reduces API costs significantly (fewer tokens per request)
- Improves response time (less data to process)
- 20 messages = ~10 user turns, enough for most task management sessions

**Alternatives Considered**:
- **Unlimited history**: Send all messages to Cohere
  - **Rejected because**: Token costs grow unbounded, potential API limits
  - Slower response times for long conversations
- **10 messages**: More aggressive truncation
  - **Rejected because**: May lose important context for complex multi-step operations
- **Sliding window with summarization**: Summarize old messages
  - **Rejected because**: Adds complexity, requires additional API calls

**Implementation Impact**:
- Load all messages from database (for UI display)
- Send only last 20 messages to Cohere API
- Format: `[{role: "user", content: "..."}, {role: "assistant", content: "..."}]`
- Oldest messages still visible in UI, just not sent to LLM

**Code Pattern**:
```python
# Load all messages for UI
all_messages = db.query(Message).filter(
    Message.conversation_id == conversation_id
).order_by(Message.created_at.asc()).all()

# Send only last 20 to Cohere
recent_messages = all_messages[-20:] if len(all_messages) > 20 else all_messages
chat_history = [
    {"role": msg.role, "message": msg.content}
    for msg in recent_messages
]
```

---

### 6. Tool Execution Strategy

**Decision**: Parallel execution when Cohere returns multiple tool calls

**Rationale**:
- Cohere supports parallel tool calling natively
- Faster response for multi-step operations (e.g., "Add 3 tasks")
- Better user experience (single response instead of multiple turns)
- Each tool validates user_id independently, so parallel execution is safe

**Safety Considerations**:
- Each tool function validates user_id before execution
- Database transactions ensure atomicity
- Tool failures are isolated (one failure doesn't block others)
- All results collected and returned together

**Alternatives Considered**:
- **Sequential execution**: Execute tools one at a time
  - **Rejected because**: Slower, no benefit for independent operations
  - Cohere already determines which tools can run in parallel

**Implementation Impact**:
- Use `asyncio.gather()` or `concurrent.futures` for parallel execution
- Collect all tool results before sending back to Cohere
- Handle partial failures gracefully (some tools succeed, some fail)

**Code Pattern**:
```python
async def execute_tools_parallel(tool_calls, user_id):
    tasks = [
        execute_single_tool(call, user_id)
        for call in tool_calls
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [
        {"call": call, "result": result}
        for call, result in zip(tool_calls, results)
    ]
```

---

### 7. Response Streaming

**Decision**: Simulate typing effect in frontend (no real streaming)

**Rationale**:
- Cohere basic setup doesn't require streaming for good UX
- Simulated typing provides visual feedback and feels responsive
- Simpler implementation for hackathon timeline
- Real streaming adds complexity (SSE or WebSockets)

**Implementation**:
- Backend returns complete response in single HTTP response
- Frontend displays response character-by-character with 20ms delay
- Typing indicator shows while backend is processing
- User can skip animation by clicking

**Alternatives Considered**:
- **Real streaming with SSE**: Server-Sent Events for token-by-token streaming
  - **Rejected because**: Adds complexity, requires different endpoint design
  - Cohere streaming API requires different SDK usage
- **No animation**: Display response immediately
  - **Rejected because**: Less engaging UX, feels abrupt

**Implementation Impact**:
- Frontend component handles animation
- Backend remains simple (single response)
- No changes to API contract

---

### 8. Conversation Naming

**Decision**: Auto-generate title from first user message

**Rationale**:
- Reduces user friction (no manual naming required)
- Provides meaningful conversation identification in history
- Can be updated later if user wants custom name
- Common pattern in chat applications (ChatGPT, Claude, etc.)

**Algorithm**:
1. Extract first 50 characters of first user message
2. Truncate at last word boundary (don't cut words)
3. Add ellipsis if truncated
4. Store in `conversations.title` field

**Alternatives Considered**:
- **Manual naming**: Prompt user to name conversation
  - **Rejected because**: Adds friction, interrupts flow
- **Generic names**: "Conversation 1", "Conversation 2"
  - **Rejected because**: Not meaningful, hard to find specific conversations
- **AI-generated summary**: Use Cohere to generate title
  - **Rejected because**: Extra API call, adds latency

**Implementation Impact**:
- Title generated on first message
- Stored in database for future reference
- Displayed in conversation list (future feature)

**Code Pattern**:
```python
def generate_conversation_title(first_message: str) -> str:
    max_length = 50
    if len(first_message) <= max_length:
        return first_message

    truncated = first_message[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]

    return truncated + "..."
```

---

## Technology Research

### Cohere Python SDK

**Package**: `cohere-python`
**Version**: Latest stable (4.x+)
**Installation**: `pip install cohere`
**Documentation**: https://docs.cohere.com/docs/python-sdk

**Key Classes and Methods**:
- `cohere.Client(api_key: str)`: Initialize client
- `client.chat()`: Main chat method with tool calling support
- `client.chat_stream()`: Streaming variant (not used in Phase III)

**Authentication**:
- API key from environment variable: `COHERE_API_KEY`
- Pass to client constructor: `Client(api_key=os.getenv("COHERE_API_KEY"))`

**Error Handling**:
- `cohere.CohereAPIError`: Base exception for API errors
- `cohere.CohereConnectionError`: Network/connection issues
- Rate limit errors: Check `response.meta` for rate limit info

**Best Practices**:
- Reuse client instance (connection pooling)
- Set reasonable timeout (default 60s)
- Handle rate limits with exponential backoff
- Log API errors for debugging

---

### Model Context Protocol (MCP)

**Protocol Version**: 1.0
**Purpose**: Standardized interface for AI agent-tool communication

**Key Principles**:
1. **Strict Schemas**: All tools have well-defined input/output schemas
2. **Type Safety**: Use Pydantic models for validation
3. **Error Handling**: Structured error responses
4. **Context Propagation**: User context (user_id) passed to all tools

**Tool Definition Format**:
```python
{
    "name": "tool_name",
    "description": "What the tool does",
    "parameter_definitions": {
        "param1": {
            "type": "string",
            "description": "Parameter description",
            "required": True
        }
    }
}
```

**Tool Response Format**:
```python
{
    "success": bool,
    "data": dict | list | None,
    "error": str | None
}
```

**Implementation Requirements**:
- All tools must validate user_id
- All tools must return structured responses
- All tools must handle errors gracefully
- All tools must be idempotent where possible

---

### Database Schema Design

**ORM**: SQLModel (combines SQLAlchemy + Pydantic)
**Database**: Neon Serverless PostgreSQL

**New Tables**:

**conversations**:
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

**messages**:
```sql
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
```

**Relationships**:
- User → Conversations: One-to-Many
- Conversation → Messages: One-to-Many
- User → Tasks: One-to-Many (existing Phase II)

**Migration Strategy**:
- Use Alembic for database migrations
- Create migration script: `alembic revision --autogenerate -m "Add chat tables"`
- Apply migration: `alembic upgrade head`

---

### JWT Authentication Pattern

**Library**: python-jose (existing Phase II dependency)
**Token Format**: Bearer token in Authorization header

**Existing Flow** (Phase II):
1. User logs in via Better Auth
2. JWT issued with claims: `{user_id: UUID, email: str, exp: timestamp}`
3. Frontend stores token in localStorage
4. Backend validates with `get_current_user` dependency

**Extension for Chat**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security)
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401)
        return await get_user_by_id(user_id)
    except JWTError:
        raise HTTPException(status_code=401)
```

**Usage in Chat Endpoint**:
```python
@router.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    # Verify user_id matches authenticated user
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403)

    # Process chat request
    ...
```

---

## Performance Considerations

### Target Metrics
- **Response Time**: <3 seconds for 95% of requests
- **Concurrent Sessions**: Support 50+ simultaneous users
- **Database Queries**: <100ms for conversation history retrieval
- **API Calls**: Cohere typically responds in 1-2 seconds

### Optimization Strategies

**Database**:
- Index on `conversations.user_id` for fast user lookup
- Index on `messages.conversation_id` for history retrieval
- Index on `messages.created_at` for chronological ordering
- Limit queries to last 20 messages: `LIMIT 20`
- Use connection pooling (SQLModel default)

**API**:
- Reuse Cohere client instance (avoid reconnection overhead)
- Set reasonable timeout (30 seconds)
- Implement retry logic with exponential backoff
- Cache user profile data (low change frequency)

**Frontend**:
- Debounce message sending (prevent double-submit)
- Optimistic UI updates (show message immediately)
- Lazy load conversation history (pagination)
- Use React.memo for message components

---

## Security Research

### Input Validation
- **Message Length**: Max 5000 characters
- **Sanitization**: Escape HTML, prevent XSS
- **SQL Injection**: Use parameterized queries (SQLModel handles this)
- **Conversation ID**: Validate UUID format, check ownership

### Authentication
- **JWT Validation**: Verify signature, check expiration
- **User Isolation**: All queries filter by authenticated user_id
- **Token Storage**: Frontend uses httpOnly cookies or secure localStorage
- **CORS**: Configure allowed origins for API

### Rate Limiting
- **Per-User Limits**: 10 requests per minute (optional for MVP)
- **Global Limits**: 100 requests per minute (optional for MVP)
- **Implementation**: Use FastAPI middleware or API gateway
- **Response**: 429 status with Retry-After header

### Data Privacy
- **Logging**: Never log tokens, passwords, or sensitive data
- **Conversation History**: User-isolated, encrypted at rest (Neon default)
- **API Keys**: Environment variables only, never in code
- **Compliance**: GDPR-ready (user can delete conversations)

---

## Error Handling Strategy

### Tool Execution Errors
| Error Type | User Message | HTTP Status | Logging |
|------------|--------------|-------------|---------|
| Task not found | "Task not found. Please check the task ID." | 200 (in response) | Info |
| Invalid input | "Invalid input: [specific field issue]" | 200 (in response) | Warning |
| Database error | "Unable to complete request. Please try again." | 500 | Error |
| Ownership violation | "You don't have permission to access this task." | 403 | Warning |

### Cohere API Errors
| Error Type | User Message | HTTP Status | Logging |
|------------|--------------|-------------|---------|
| Rate limit | "Service is busy, please try again in a moment." | 429 | Warning |
| Timeout | "Request timed out, please try again." | 504 | Error |
| Invalid API key | "Service unavailable." | 500 | Critical |
| Model error | "Unable to process request." | 500 | Error |

### Authentication Errors
| Error Type | User Message | HTTP Status | Logging |
|------------|--------------|-------------|---------|
| Missing JWT | "Authentication required." | 401 | Info |
| Invalid JWT | "Invalid authentication token." | 401 | Warning |
| Expired JWT | "Session expired, please log in again." | 401 | Info |

### Frontend Error Handling
- Display error messages in chat window (not alerts)
- Provide retry button for transient errors
- Show connection status indicator
- Graceful degradation if chat service unavailable
- Log errors to console for debugging

---

## Conclusion

All research and architectural decisions are complete. The implementation can proceed with confidence based on these findings. Key decisions prioritize:

1. **Reliability**: Native tool calling, structured responses, comprehensive error handling
2. **Performance**: Message truncation, parallel execution, database indexing
3. **Security**: JWT authentication, user isolation, input validation
4. **User Experience**: Friendly responses, typing simulation, modern UI

**Status**: ✅ Research Complete
**Next Step**: Proceed to Phase 1 (Data Model & Contracts)
