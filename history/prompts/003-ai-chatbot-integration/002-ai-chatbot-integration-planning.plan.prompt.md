---
id: 002
title: AI Chatbot Integration Planning
stage: plan
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: 003-ai-chatbot-integration
branch: 003-ai-chatbot-integration
user: alish
command: /sp.plan
labels: ["planning", "architecture", "cohere", "mcp-tools", "phase3"]
links:
  spec: specs/003-ai-chatbot-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/003-ai-chatbot-integration/plan.md
 - specs/003-ai-chatbot-integration/research.md
 - specs/003-ai-chatbot-integration/data-model.md
 - specs/003-ai-chatbot-integration/contracts/chat-api.yaml
 - specs/003-ai-chatbot-integration/contracts/mcp-tools.json
 - specs/003-ai-chatbot-integration/quickstart.md
tests:
 - Constitution check passed (all 16 principles compliant)
 - Technical context validated
 - All architectural decisions documented
---

## Prompt

Implementation Plan for Phase III – AI Todo Chatbot (Cohere-Powered Integration)

Create comprehensive planning artifacts including:
- Updated backend architecture showing Cohere + custom agent runner integration
- Database schema extensions (Conversation and Message models)
- MCP-compatible tool definitions in Cohere format
- Custom Cohere Runner implementation approach
- Chat endpoint logic flow with authentication
- Frontend chatbot UI integration plan
- Environment variable and security checklist
- Error and fallback strategy documentation

Key decisions requiring documentation:
- Cohere model choice (command-r-plus vs command-r)
- Tool calling implementation (native vs JSON mode)
- Chat UI technology (ChatKit vs custom)
- Floating icon design and behavior
- Message history management (truncation strategy)
- Tool execution order (parallel vs sequential)
- Response streaming approach
- Conversation naming strategy

Technical implementation organized by phases:
1. Foundation: Environment setup, DB schema, tool definitions
2. Backend: Chat endpoint, Cohere agent runner, MCP tools
3. Frontend: Chatbot UI components, API integration
4. Polish: UX enhancements, error handling, dark mode
5. Integration: End-to-end testing, security validation

## Response snapshot

Created comprehensive implementation plan with complete Phase 0 (Research) and Phase 1 (Design & Contracts) artifacts:

**Planning Artifacts Created:**

1. **plan.md** (170+ lines): Master implementation plan with:
   - Technical context (Python 3.11+, FastAPI, Cohere SDK, Next.js 16+)
   - Constitution check (all 16 principles validated ✅)
   - Project structure (monorepo with frontend/backend separation)
   - 6 implementation phases with clear deliverables
   - Success metrics and testing strategy
   - ADR recommendations for key decisions

2. **research.md** (450+ lines): Complete architectural decisions:
   - 8 key decisions documented with rationale and alternatives
   - Cohere model selection: command-r-plus (better accuracy)
   - Native tool calling (more reliable than JSON mode)
   - Hybrid UI approach (ChatKit with custom fallback)
   - Message truncation: last 20 messages (token management)
   - Parallel tool execution (Cohere supports it)
   - Technology research (Cohere SDK, MCP, JWT, database)
   - Performance considerations and security research
   - Comprehensive error handling strategy

3. **data-model.md** (400+ lines): Complete entity definitions:
   - 2 new tables: conversations, messages
   - 2 existing tables: tasks, users (Phase II)
   - Full SQLModel definitions with relationships
   - Validation rules and business logic
   - State transition diagrams
   - Database migration scripts (Alembic)
   - Query patterns and performance optimization

4. **contracts/chat-api.yaml** (300+ lines): OpenAPI 3.0 specification:
   - POST /api/{user_id}/chat endpoint
   - Complete request/response schemas
   - JWT authentication requirements
   - Error responses (400, 401, 403, 429, 500)
   - Multiple examples for different scenarios
   - Tool call transparency in responses

5. **contracts/mcp-tools.json** (250+ lines): MCP tool definitions:
   - 6 tools: add_task, list_tasks, complete_task, delete_task, update_task, get_user_profile
   - Cohere-compatible parameter definitions
   - Return type schemas with examples
   - Security and error handling documentation
   - Implementation notes for parallel execution

6. **quickstart.md** (500+ lines): Developer setup guide:
   - Prerequisites and environment setup
   - Step-by-step installation instructions
   - Database migration procedures
   - Development server startup
   - Comprehensive testing checklist (40+ items)
   - Troubleshooting guide (6 common issues)
   - Production deployment instructions

**Key Architectural Decisions:**

1. **Cohere command-r-plus**: Better tool-calling accuracy for hackathon demo
2. **Stateless architecture**: Database-persisted conversations, horizontally scalable
3. **Native tool calling**: More reliable than JSON mode, supports parallel execution
4. **20-message history**: Prevents token blowup while maintaining context
5. **Hybrid UI**: ChatKit primary, custom Tailwind fallback for reliability
6. **JWT authentication**: Reuse Phase II auth, strict user isolation

**Constitution Compliance:**
- ✅ All 16 core principles validated
- ✅ Phase II constraints preserved (no breaking changes)
- ✅ Phase III constraints met (Cohere-only, stateless, MCP-compliant)
- ✅ No violations requiring justification

**Technical Stack:**
- Backend: Python 3.11+, FastAPI, SQLModel, cohere-python SDK
- Frontend: Next.js 16+, React 18+, Tailwind CSS
- Database: Neon PostgreSQL (2 new tables)
- LLM: Cohere command-r-plus with native tool calling
- Auth: Better Auth JWT (existing Phase II)

## Outcome

- ✅ Impact: Complete planning phase with 6 comprehensive artifacts totaling 2000+ lines of documentation. All architectural decisions documented with rationale. Ready for task breakdown and implementation.
- 🧪 Tests: Constitution check passed (16/16 principles), technical context validated, all design decisions justified with alternatives considered
- 📁 Files: Created 6 planning artifacts - plan.md, research.md, data-model.md, chat-api.yaml, mcp-tools.json, quickstart.md
- 🔁 Next prompts: `/sp.tasks` to generate actionable task breakdown for implementation
- 🧠 Reflection: Planning phase successfully balances technical depth with practical implementation guidance. All decisions prioritize reliability, security, and user experience. Hybrid UI approach ensures project completion within hackathon timeline.

## Evaluation notes (flywheel)

- Failure modes observed: None. Planning workflow completed successfully with all required artifacts.
- Graders run and results (PASS/FAIL): Constitution Check - PASS (16/16 principles), Technical Context - PASS (all fields specified), Design Completeness - PASS (data model, contracts, quickstart all complete)
- Prompt variant (if applicable): Standard /sp.plan workflow with comprehensive user input
- Next experiment (smallest change to try): Proceed to task generation with /sp.tasks to break down implementation into actionable units
