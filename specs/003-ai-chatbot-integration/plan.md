# Implementation Plan: AI Todo Chatbot Integration

**Branch**: `003-ai-chatbot-integration` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-ai-chatbot-integration/spec.md`

## Summary

Integrate a Cohere-powered AI chatbot into the existing Next.js + FastAPI Todo application that enables natural language task management in English and Urdu. The chatbot will use Cohere's command-r-plus model with native tool calling to execute task CRUD operations and user profile queries through MCP-compatible tools. Implementation follows a stateless architecture with database-persisted conversation history, JWT authentication, and strict user ownership enforcement. The frontend will feature a floating chat icon that opens a modern chat interface (hybrid approach: OpenAI ChatKit with custom fallback), while maintaining 100% backward compatibility with Phase II functionality.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/JavaScript (frontend with Next.js 16+)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, cohere-python SDK, Pydantic, python-jose (JWT)
- Frontend: Next.js 16+ (App Router), React 18+, Tailwind CSS, Better Auth client
**Storage**: Neon Serverless PostgreSQL (existing + new tables: conversations, messages)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web application (desktop browsers, responsive design)
**Project Type**: Web (monorepo with frontend/ and backend/ separation)
**Performance Goals**:
- Chat response time <3 seconds for 95% of requests
- Support 50+ concurrent chat sessions
- Database queries <100ms for conversation history retrieval
**Constraints**:
- Stateless backend (no in-memory session state)
- Single-turn HTTP requests (no WebSockets/streaming)
- Text-only chat (no voice, images, file uploads)
- Maximum 20 messages per conversation sent to Cohere (token management)
**Scale/Scope**:
- Multi-user application with user isolation
- 6 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task, get_user_profile)
- 2 new database tables (conversations, messages)
- 1 new protected API endpoint (POST /api/{user_id}/chat)
- 2 new frontend components (ChatbotIcon, ChatWindow)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Core Principles Compliance

- **I. Fully Spec-Driven Development**: ✅ All implementation will follow spec.md with PHR traceability
- **II. Zero Manual Coding**: ✅ All code generated via Claude Code with @specs references
- **III. Modular Architecture**: ✅ Chat Agent as separate module with defined MCP tool interfaces
- **IV. User Isolation**: ✅ JWT authentication + user_id enforcement on all chat operations
- **V. Technology Stack**: ✅ Using specified stack (Next.js, FastAPI, SQLModel, Neon, Cohere, Tailwind)
- **VI. Monorepo Structure**: ✅ Following existing frontend/backend separation
- **VII. Cohere-First**: ✅ Exclusive use of Cohere API (command-r-plus model)
- **VIII. Stateless Architecture**: ✅ Database-persisted conversations, no in-memory state
- **IX. MCP Tool Compliance**: ✅ All 6 tools follow MCP standards with strict schemas
- **X. Security-First**: ✅ JWT on chat endpoint, user_id validation on all tool calls
- **XI. Multilingual**: ✅ English + Urdu natural language understanding
- **XII. Zero Breaking Changes**: ✅ Additive feature only, Phase II remains untouched
- **XIII. Database-Driven Context**: ✅ Load history from DB on every request
- **XIV. Friendly Behavior**: ✅ Action confirmations, graceful errors, helpful responses
- **XV. Production-Ready**: ✅ Pydantic validation, error handling, Swagger docs, env config
- **XVI. PHR Traceability**: ✅ All decisions documented in history/prompts/

### ✅ Phase II Constraints Compliance

- **Technology Stack Lock**: ✅ No deviations from Next.js, FastAPI, SQLModel, Neon, Better Auth, Tailwind
- **Database Access Policy**: ✅ No direct DB access from frontend, stateless JWT auth
- **Data Security**: ✅ Task ownership enforcement extended to conversations/messages
- **Schema Compliance**: ✅ Extending existing schema with new tables, preserving Phase II tables

### ✅ Phase III Constraints Compliance

- **LLM Provider Lock**: ✅ Cohere API only (command-r-plus model)
- **Minimal Dependencies**: ✅ Only adding cohere-python SDK
- **Environment Config**: ✅ COHERE_API_KEY added to .env
- **Stateless Server**: ✅ All state in database, horizontally scalable
- **Authentication Scope**: ✅ Reusing get_current_user, chat endpoint protected
- **Communication Protocol**: ✅ Single-turn HTTP, no WebSockets
- **Feature Scope**: ✅ Text-based task management + profile queries only
- **Integration Timeline**: ✅ Backend first, then frontend, no Phase II disruption

### Gate Status: ✅ PASSED

All constitutional requirements are met. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-chatbot-integration/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoint
│   └── mcp-tools.json   # MCP tool definitions
├── checklists/
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── user.py              # Existing (Phase II)
│   │   ├── task.py              # Existing (Phase II)
│   │   ├── conversation.py      # NEW: Conversation model
│   │   └── message.py           # NEW: Message model
│   ├── services/
│   │   ├── auth.py              # Existing (Phase II)
│   │   ├── task_service.py      # Existing (Phase II)
│   │   ├── cohere_client.py     # NEW: Cohere API client wrapper
│   │   ├── chat_agent.py        # NEW: Main chat agent with tool calling
│   │   └── mcp_tools.py         # NEW: MCP tool implementations
│   ├── api/
│   │   ├── auth.py              # Existing (Phase II)
│   │   ├── tasks.py             # Existing (Phase II)
│   │   └── chat.py              # NEW: Chat endpoint
│   ├── schemas/
│   │   ├── task.py              # Existing (Phase II)
│   │   ├── chat.py              # NEW: Chat request/response schemas
│   │   └── mcp.py               # NEW: MCP tool schemas
│   └── main.py                  # Existing (update with new routes)
└── tests/
    ├── test_tasks.py            # Existing (Phase II)
    ├── test_chat_agent.py       # NEW: Chat agent unit tests
    ├── test_mcp_tools.py        # NEW: MCP tools unit tests
    └── test_chat_api.py         # NEW: Chat endpoint integration tests

frontend/
├── src/
│   ├── components/
│   │   ├── TaskList.tsx         # Existing (Phase II)
│   │   ├── TaskForm.tsx         # Existing (Phase II)
│   │   ├── ChatbotIcon.tsx      # NEW: Floating chat icon (FAB)
│   │   └── ChatWindow.tsx       # NEW: Chat modal/window
│   ├── app/
│   │   ├── page.tsx             # Existing (Phase II dashboard)
│   │   ├── login/               # Existing (Phase II)
│   │   └── chat/                # NEW: Optional dedicated chat page
│   ├── lib/
│   │   ├── api.ts               # Existing (update with chat methods)
│   │   └── auth.ts              # Existing (Phase II)
│   └── types/
│       ├── task.ts              # Existing (Phase II)
│       └── chat.ts              # NEW: Chat types
└── tests/
    └── chat.test.tsx            # NEW: Chat component tests

.env (root)
├── COHERE_API_KEY               # NEW: Cohere API key
├── BETTER_AUTH_SECRET           # Existing (Phase II)
├── NEON_DB_URL                  # Existing (Phase II)
└── NEXT_PUBLIC_API_URL          # Existing (Phase II)
```

**Structure Decision**: Using existing monorepo web application structure (Option 2 from template) with frontend/ and backend/ separation. All Phase III additions are integrated into existing directories following the established pattern. New files are clearly marked as "NEW" while existing Phase II files remain untouched except for minimal integration points (main.py routes, api.ts methods).

## Complexity Tracking

> **No violations - this section is empty per template instructions**

## Phase 0: Research & Decisions

### Key Architectural Decisions

#### 1. Cohere Model Selection
**Decision**: Use `command-r-plus` model
**Rationale**:
- Superior tool-calling accuracy and reasoning capabilities
- Better multilingual support (English + Urdu)
- More reliable for complex task management commands
- Hackathon demo requires best-in-class performance
**Alternatives Considered**:
- `command-r`: Faster and cheaper but less accurate for tool calling
- Rejected because accuracy is more important than speed for demo

#### 2. Tool Calling Implementation
**Decision**: Use Cohere native tool calling API
**Rationale**:
- Built-in support for parallel tool execution
- More reliable than forcing JSON mode
- Structured outputs with validation
- Official SDK support
**Alternatives Considered**:
- Force JSON mode with custom parsing: Rejected due to lower reliability

#### 3. Chat UI Technology
**Decision**: Hybrid approach - OpenAI ChatKit with custom fallback
**Rationale**:
- ChatKit provides production-ready chat UI
- Custom fallback ensures project completion if ChatKit setup fails
- Tailwind-based custom component matches existing design
**Implementation Plan**:
1. Attempt ChatKit integration with domain allowlist configuration
2. If setup issues arise, use custom React + Tailwind modal
3. Document both approaches in quickstart.md
**Alternatives Considered**:
- Pure custom implementation: More work but guaranteed compatibility
- Pure ChatKit: Risk of setup issues blocking progress

#### 4. Floating Icon Design
**Decision**: Modern circular FAB (Floating Action Button) with pulse animation
**Rationale**:
- Familiar pattern (WhatsApp, Telegram, Intercom)
- Non-intrusive, always accessible
- Pulse animation on new messages provides visual feedback
**Styling**: Bottom-right corner, 60px diameter, z-index 1000, Tailwind CSS

#### 5. Message History Management
**Decision**: Truncate to last 20 messages per conversation
**Rationale**:
- Prevents token limit issues with Cohere API
- Maintains sufficient context for task management
- Reduces API costs
- Improves response time
**Implementation**: Load all messages from DB, send only last 20 to Cohere

#### 6. Tool Execution Strategy
**Decision**: Parallel execution when Cohere returns multiple tool calls
**Rationale**:
- Cohere supports parallel tool calling
- Faster response for multi-step operations
- Better user experience
**Safety**: Each tool validates user_id independently

#### 7. Response Streaming
**Decision**: Simulate typing effect in frontend (no real streaming)
**Rationale**:
- Cohere basic setup doesn't require streaming
- Simulated typing provides good UX
- Simpler implementation for hackathon timeline
**Implementation**: Frontend displays response character-by-character with delay

#### 8. Conversation Naming
**Decision**: Auto-generate title from first user message
**Rationale**:
- Reduces user friction (no manual naming)
- Provides meaningful conversation identification
- Can be updated later if needed
**Implementation**: Extract first 50 characters of first user message, truncate at word boundary

### Technology Research

#### Cohere API Integration
**SDK**: `cohere-python` (official Python SDK)
**Installation**: `pip install cohere`
**Authentication**: API key via environment variable
**Key Methods**:
- `cohere.Client(api_key=...)`
- `client.chat(message=..., model=..., tools=..., chat_history=...)`
- Tool results passed back via `tool_results` parameter

**Tool Definition Format** (Cohere-compatible JSON schema):
```json
{
  "name": "add_task",
  "description": "Add a new task for the user",
  "parameter_definitions": {
    "title": {
      "description": "Task title",
      "type": "string",
      "required": true
    },
    "description": {
      "description": "Task description",
      "type": "string",
      "required": false
    }
  }
}
```

#### MCP Tool Standards
**Protocol**: Model Context Protocol (MCP)
**Key Principles**:
- Strict input/output schemas
- Type safety with Pydantic models
- Error handling with structured responses
- User context propagation (user_id)

**Tool Response Format**:
```python
{
  "success": bool,
  "data": dict | list | None,
  "error": str | None
}
```

#### Database Schema Extensions
**New Tables**:

**conversations**:
- `id`: UUID (primary key)
- `user_id`: UUID (foreign key to users.id)
- `title`: VARCHAR(255) (nullable, auto-generated)
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

**messages**:
- `id`: UUID (primary key)
- `conversation_id`: UUID (foreign key to conversations.id)
- `role`: ENUM('user', 'assistant')
- `content`: TEXT
- `tool_calls`: JSONB (nullable, stores tool call metadata)
- `created_at`: TIMESTAMP

**Indexes**:
- `conversations.user_id` (for user isolation queries)
- `messages.conversation_id` (for history retrieval)
- `messages.created_at` (for chronological ordering)

#### JWT Authentication Flow
**Existing Pattern** (Phase II):
1. User logs in via Better Auth
2. JWT token issued with user_id claim
3. Frontend stores token in localStorage/cookie
4. Backend validates token with `get_current_user` dependency

**Extension for Chat**:
1. Frontend includes JWT in Authorization header: `Bearer <token>`
2. Chat endpoint uses `get_current_user` dependency
3. Extracted user_id passed to all MCP tools
4. Tools validate ownership before operations

### Error Handling Strategy

#### Tool Execution Errors
- **Task not found**: Return friendly message "Task not found. Please check the task ID."
- **Invalid input**: Return validation error with specific field issues
- **Database error**: Return generic error, log details server-side
- **Ownership violation**: Return 403 with "You don't have permission to access this task"

#### Cohere API Errors
- **Rate limit**: Return "Service is busy, please try again in a moment"
- **API timeout**: Return "Request timed out, please try again"
- **Invalid API key**: Log error, return generic "Service unavailable"
- **Model error**: Log error, return "Unable to process request"

#### Authentication Errors
- **Missing JWT**: Return 401 "Authentication required"
- **Invalid JWT**: Return 401 "Invalid authentication token"
- **Expired JWT**: Return 401 "Session expired, please log in again"

#### Frontend Error Handling
- Display error messages in chat window
- Provide retry button for transient errors
- Show connection status indicator
- Graceful degradation if chat service unavailable

### Performance Optimization

#### Database Query Optimization
- Index on `conversations.user_id` for fast user conversation lookup
- Index on `messages.conversation_id` for fast history retrieval
- Limit query to last 20 messages with `ORDER BY created_at DESC LIMIT 20`
- Use connection pooling (SQLModel default)

#### API Response Time
- Target: <3 seconds for 95% of requests
- Cohere API typically responds in 1-2 seconds
- Database queries <100ms
- Tool execution <500ms
- Total budget: 3 seconds

#### Caching Strategy
- No caching for chat responses (always fresh)
- Consider caching user profile data (low change frequency)
- Cache Cohere client instance (reuse connection)

### Security Considerations

#### Input Validation
- Sanitize all user inputs before passing to Cohere
- Validate message length (max 5000 characters)
- Prevent SQL injection via SQLModel parameterized queries
- Validate conversation_id belongs to authenticated user

#### Output Sanitization
- Escape HTML in chat responses
- Prevent XSS attacks in frontend rendering
- Validate tool call results before returning to user

#### Rate Limiting
- Consider per-user rate limits (e.g., 10 requests/minute)
- Implement at API gateway or middleware level
- Return 429 "Too many requests" with retry-after header

#### Data Privacy
- Never log sensitive user data (passwords, tokens)
- Log only conversation_id and user_id for debugging
- Comply with data retention policies
- Ensure conversation history is user-isolated

## Phase 1: Design & Contracts

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions, relationships, and validation rules.

**Summary**:
- **Conversation**: User-owned chat sessions with auto-generated titles
- **Message**: Individual messages in conversations (user/assistant roles)
- **Task**: Existing Phase II entity (no changes)
- **User**: Existing Phase II entity (no changes)

**Key Relationships**:
- User 1:N Conversations (one user has many conversations)
- Conversation 1:N Messages (one conversation has many messages)
- User 1:N Tasks (existing Phase II relationship)

### API Contracts

See [contracts/](./contracts/) for complete OpenAPI specifications and MCP tool definitions.

**New Endpoint**:
- `POST /api/{user_id}/chat`: Main chat endpoint (see contracts/chat-api.yaml)

**MCP Tools** (see contracts/mcp-tools.json):
1. `add_task`: Create new task
2. `list_tasks`: List tasks with optional filters
3. `complete_task`: Mark task as complete
4. `delete_task`: Delete task
5. `update_task`: Update task fields
6. `get_user_profile`: Retrieve user information

### Implementation Phases

#### Phase 1.1: Foundation (Backend)
**Duration**: First implementation sprint
**Deliverables**:
1. Add `COHERE_API_KEY` to `.env` and `.env.example`
2. Install `cohere-python` SDK: `pip install cohere`
3. Create database models: `conversation.py`, `message.py`
4. Run database migrations to create new tables
5. Create Cohere client wrapper: `cohere_client.py`

**Acceptance Criteria**:
- Environment variable configured
- Database tables created with proper indexes
- Cohere client can authenticate and make test calls

#### Phase 1.2: MCP Tools Implementation (Backend)
**Duration**: Second implementation sprint
**Deliverables**:
1. Create `mcp_tools.py` with all 6 tool functions
2. Define tool schemas in Cohere-compatible format
3. Implement user_id validation in each tool
4. Add comprehensive error handling
5. Write unit tests for each tool

**Acceptance Criteria**:
- All 6 tools implemented and tested
- User ownership enforced on all operations
- Tools return structured responses (success/data/error)
- 90%+ test coverage

#### Phase 1.3: Chat Agent & Endpoint (Backend)
**Duration**: Third implementation sprint
**Deliverables**:
1. Create `chat_agent.py` with Cohere runner logic
2. Implement conversation history loading (last 20 messages)
3. Implement tool call detection and execution
4. Implement message persistence after processing
5. Create `chat.py` API endpoint with JWT protection
6. Add Swagger documentation for chat endpoint
7. Write integration tests for end-to-end flow

**Acceptance Criteria**:
- Chat endpoint accepts requests and returns responses
- Tool calls are detected and executed correctly
- Conversation history persists across requests
- JWT authentication enforced
- Integration tests pass

#### Phase 1.4: Frontend Chat UI (Frontend)
**Duration**: Fourth implementation sprint
**Deliverables**:
1. Create `ChatbotIcon.tsx` (floating FAB)
2. Create `ChatWindow.tsx` (chat modal/window)
3. Update `api.ts` with chat methods
4. Add chat types in `types/chat.ts`
5. Implement message sending and display
6. Add typing indicator and auto-scroll
7. Integrate with existing dashboard page

**Acceptance Criteria**:
- Floating icon appears when user is logged in
- Chat window opens/closes smoothly
- Messages display correctly (user right, assistant left)
- Typing indicator shows during processing
- Auto-scroll to latest message works
- JWT token included in API requests

#### Phase 1.5: Polish & Optimization (Full Stack)
**Duration**: Fifth implementation sprint
**Deliverables**:
1. Implement friendly response formatting
2. Add error handling in UI (connection lost, invalid response)
3. Ensure dark mode consistency
4. Optimize message history truncation (20 messages)
5. Add simulated typing effect in frontend
6. Implement conversation title auto-generation
7. Add pulse animation to chat icon for new messages

**Acceptance Criteria**:
- Responses include action confirmations and emojis
- Error messages are user-friendly
- Dark mode works correctly
- Performance meets targets (<3s response time)
- UX feels polished and professional

#### Phase 1.6: Integration & Testing (Full Stack)
**Duration**: Sixth implementation sprint
**Deliverables**:
1. End-to-end testing: chat controls tasks → main UI reflects changes
2. Security testing: JWT validation, user isolation
3. Multilingual testing: English + Urdu commands
4. Edge case testing: empty messages, long inputs, task not found
5. Performance testing: concurrent sessions, response times
6. Verify no regressions in Phase II functionality
7. Document ChatKit domain allowlist setup (if used)
8. Create demo flow for judges

**Acceptance Criteria**:
- All success criteria from spec.md met
- No Phase II regressions
- Security tests pass (no cross-user access)
- Multilingual support works
- Performance targets met
- Demo flow documented and rehearsed

### Testing Strategy

#### Unit Tests (Backend)
- Test each MCP tool independently
- Mock database calls
- Test user_id validation
- Test error handling
- Target: 90%+ coverage

#### Integration Tests (Backend)
- Test chat endpoint end-to-end
- Test tool call execution flow
- Test conversation persistence
- Test JWT authentication
- Use test database

#### Component Tests (Frontend)
- Test ChatbotIcon rendering and click behavior
- Test ChatWindow message display
- Test message sending
- Test error state handling
- Use React Testing Library

#### End-to-End Tests
- Test full user flow: login → open chat → manage tasks
- Test conversation persistence across sessions
- Test task synchronization between chat and main UI
- Test multilingual commands
- Use Playwright or Cypress

#### Security Tests
- Test JWT validation (missing, invalid, expired tokens)
- Test user isolation (attempt to access other user's data)
- Test input sanitization (SQL injection, XSS attempts)
- Test rate limiting (if implemented)

#### Performance Tests
- Test response time under normal load
- Test concurrent session handling (50+ users)
- Test database query performance
- Test Cohere API timeout handling

### Quickstart Guide

See [quickstart.md](./quickstart.md) for complete setup and development instructions.

**Quick Summary**:
1. Add `COHERE_API_KEY` to `.env`
2. Run database migrations: `alembic upgrade head`
3. Start backend: `uvicorn main:app --reload`
4. Start frontend: `npm run dev`
5. Open chat: Click floating icon in bottom-right corner
6. Test commands: "Add task buy milk", "Show all tasks", "Mera email kya hai?"

## Next Steps

After completing this planning phase:

1. **Review this plan** with stakeholders/team
2. **Run `/sp.tasks`** to generate actionable task breakdown
3. **Begin Phase 1.1** (Foundation) implementation
4. **Create PHR** documenting this planning session
5. **Update agent context** with new technologies (Cohere, MCP)

## Architectural Decision Records (ADRs)

The following architectural decisions should be documented as ADRs:

1. **ADR-001: Cohere Model Selection (command-r-plus)**
   - Context: Need to choose between command-r and command-r-plus
   - Decision: Use command-r-plus for better tool-calling accuracy
   - Consequences: Higher API costs but better demo performance

2. **ADR-002: Stateless Chat Architecture**
   - Context: Need to decide between stateful (in-memory) vs stateless (DB-backed) chat
   - Decision: Stateless with database-persisted conversations
   - Consequences: Horizontally scalable, survives restarts, slightly higher latency

3. **ADR-003: Message History Truncation (20 messages)**
   - Context: Need to balance context richness vs token limits
   - Decision: Send last 20 messages to Cohere
   - Consequences: Prevents token blowup, maintains sufficient context for task management

4. **ADR-004: Hybrid Chat UI Approach (ChatKit + Custom Fallback)**
   - Context: Need reliable chat UI within hackathon timeline
   - Decision: Try ChatKit first, fallback to custom Tailwind component
   - Consequences: Best of both worlds, guaranteed completion

## Success Metrics

### Functional Metrics
- ✅ All 6 MCP tools working correctly
- ✅ Natural language commands understood (English + Urdu)
- ✅ Conversation history persists across sessions
- ✅ Task synchronization between chat and main UI
- ✅ User profile queries return correct data

### Technical Metrics
- ✅ Response time <3 seconds (95th percentile)
- ✅ Support 50+ concurrent sessions
- ✅ Database queries <100ms
- ✅ Zero cross-user data leakage
- ✅ 90%+ test coverage

### User Experience Metrics
- ✅ Friendly action confirmations
- ✅ Graceful error handling
- ✅ Smooth UI interactions (typing indicator, auto-scroll)
- ✅ Dark mode consistency
- ✅ Judges rate as "impressive" and "seamless"

### Integration Metrics
- ✅ Zero Phase II regressions
- ✅ Backward compatibility maintained
- ✅ Existing APIs unchanged
- ✅ Existing UI components unaffected

---

**Plan Status**: ✅ Complete - Ready for Phase 0 Research
**Next Command**: `/sp.tasks` to generate task breakdown
**Estimated Implementation Time**: 6 sprints (Foundation → Integration & Testing)
