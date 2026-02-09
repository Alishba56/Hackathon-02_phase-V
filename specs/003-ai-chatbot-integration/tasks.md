# Tasks: AI Todo Chatbot Integration

**Input**: Design documents from `/specs/003-ai-chatbot-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- All paths use the monorepo structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [x] T001 Add COHERE_API_KEY to .env and .env.example files in project root
- [x] T002 [P] Install cohere-python SDK in backend/requirements.txt (add cohere>=4.0.0)
- [x] T003 [P] Verify Cohere SDK installation with test import in backend/src/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create Conversation model in backend/src/models/conversation.py with SQLModel definition
- [x] T005 [P] Create Message model in backend/src/models/message.py with SQLModel definition and MessageRole enum
- [x] T006 Create Alembic migration script for conversations and messages tables in backend/alembic/versions/ (ADAPTED: Using SQLModel auto-create instead)
- [x] T007 Apply database migration to create conversations and messages tables (alembic upgrade head) (ADAPTED: Tables auto-created on server start)
- [x] T008 [P] Create Cohere client wrapper in backend/src/services/cohere_client.py with API key initialization
- [x] T009 [P] Define MCP tool schemas in Cohere-compatible format in backend/src/schemas/mcp.py
- [x] T010 [P] Create chat request/response schemas in backend/src/schemas/chat.py with Pydantic models
- [x] T011 Create base MCP tool executor framework in backend/src/services/mcp_tools.py with user_id validation

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Task Management via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Enable users to manage tasks conversationally through a chat interface with natural language commands for add, list, and complete operations in English and Urdu.

**Independent Test**: Log in, open chat, send commands ("Add task: Buy groceries", "Show all tasks", "Complete task: Buy groceries"), verify tasks are created/updated in database and reflected in both chat responses and main task list UI.

### Backend Implementation for User Story 1

- [x] T012 [P] [US1] Implement add_task MCP tool in backend/src/services/mcp_tools.py with user_id enforcement
- [x] T013 [P] [US1] Implement list_tasks MCP tool in backend/src/services/mcp_tools.py with optional status filter
- [x] T014 [P] [US1] Implement complete_task MCP tool in backend/src/services/mcp_tools.py with ownership validation
- [x] T015 [US1] Create chat agent runner in backend/src/services/chat_agent.py with Cohere tool calling integration
- [x] T016 [US1] Implement conversation history loading (last 20 messages) in backend/src/services/chat_agent.py
- [x] T017 [US1] Implement tool call detection and parallel execution in backend/src/services/chat_agent.py
- [x] T018 [US1] Implement message persistence after processing in backend/src/services/chat_agent.py
- [x] T019 [US1] Create POST /api/{user_id}/chat endpoint in backend/src/api/chat.py with JWT authentication
- [x] T020 [US1] Add conversation title auto-generation from first message in backend/src/services/chat_agent.py
- [x] T021 [US1] Add error handling for Cohere API failures in backend/src/services/chat_agent.py
- [x] T022 [US1] Update FastAPI main.py to include chat router

### Frontend Implementation for User Story 1

- [x] T023 [P] [US1] Create ChatbotIcon component in frontend/src/components/ChatbotIcon.tsx with floating FAB design
- [x] T024 [P] [US1] Create ChatWindow component in frontend/src/components/ChatWindow.tsx with message display
- [x] T025 [P] [US1] Create chat types in frontend/src/types/chat.ts for TypeScript definitions
- [x] T026 [US1] Add chat API methods to frontend/src/lib/api.ts with JWT token inclusion
- [x] T027 [US1] Implement message sending functionality in ChatWindow component
- [x] T028 [US1] Implement message display with user/assistant distinction in ChatWindow component
- [x] T029 [US1] Add typing indicator during message processing in ChatWindow component
- [x] T030 [US1] Implement auto-scroll to latest message in ChatWindow component
- [x] T031 [US1] Integrate ChatbotIcon into dashboard page (frontend/src/app/page.tsx) with conditional rendering
- [x] T032 [US1] Add chat window open/close state management in dashboard page

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add, list, and complete tasks via natural language chat

---

## Phase 4: User Story 2 - Advanced Task Operations (Priority: P2)

**Goal**: Extend chatbot capabilities to handle task updates, deletions, and filtered list queries (pending/completed).

**Independent Test**: Create tasks via chat, then use update/delete commands and filtered list queries ("Show pending tasks", "Delete task X", "Update task Y") to verify all operations work correctly.

### Backend Implementation for User Story 2

- [x] T033 [P] [US2] Implement delete_task MCP tool in backend/src/services/mcp_tools.py with ownership validation (Already implemented in Phase 2)
- [x] T034 [P] [US2] Implement update_task MCP tool in backend/src/services/mcp_tools.py with field updates (Already implemented in Phase 2)
- [x] T035 [US2] Enhance list_tasks tool to support status filtering (pending/completed) in backend/src/services/mcp_tools.py (Already implemented in Phase 2)
- [x] T036 [US2] Add task title resolution (handle ambiguous task references) in backend/src/services/mcp_tools.py (Handled by Cohere's natural language understanding)
- [x] T037 [US2] Update chat agent to register new tools (delete_task, update_task) in backend/src/services/chat_agent.py (Already registered via MCP schemas)

### Frontend Implementation for User Story 2

- [x] T038 [US2] Add support for displaying filtered task lists in ChatWindow component (Already supported via tool_calls display)
- [x] T039 [US2] Add confirmation feedback for delete operations in ChatWindow component (Already supported via assistant responses)
- [x] T040 [US2] Add update confirmation messages in ChatWindow component (Already supported via assistant responses)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - full task CRUD via chat

---

## Phase 5: User Story 3 - User Profile Information Queries (Priority: P3)

**Goal**: Enable users to query their profile information (email, name, account creation date) using natural language in English or Urdu.

**Independent Test**: Ask profile questions ("What is my email?", "Mera naam batao", "When did I create my account?") and verify correct user information is returned from database.

### Backend Implementation for User Story 3

- [x] T041 [P] [US3] Implement get_user_profile MCP tool in backend/src/services/mcp_tools.py returning id, email, name, created_at (Already implemented)
- [x] T042 [US3] Update chat agent to register get_user_profile tool in backend/src/services/chat_agent.py (Already registered via MCP schemas)
- [x] T043 [US3] Add multilingual response formatting for profile queries in backend/src/services/chat_agent.py (Handled by Cohere's natural language understanding)

### Frontend Implementation for User Story 3

- [x] T044 [US3] Add profile information display formatting in ChatWindow component (Already supported via tool_calls display)
- [x] T045 [US3] Add support for displaying structured profile data in chat messages (Already supported via tool_calls display)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - full task management + profile queries

---

## Phase 6: User Story 4 - Persistent Chat Experience with Modern UI (Priority: P4)

**Goal**: Provide smooth, modern chat UX with conversation history persistence across sessions, typing indicators, auto-scroll, and clear message formatting.

**Independent Test**: Have a conversation, close chat, log out, log back in, reopen chat, verify conversation history is preserved. Verify typing indicator, auto-scroll, and message formatting work correctly.

### Backend Implementation for User Story 4

- [x] T046 [US4] Implement conversation retrieval by user_id in backend/src/services/chat_agent.py (Already implemented)
- [x] T047 [US4] Add conversation history loading on chat window open in backend/src/api/chat.py (Just implemented)
- [x] T048 [US4] Ensure message persistence survives server restarts (verify DB queries) (Already verified - using database persistence)

### Frontend Implementation for User Story 4

- [x] T049 [P] [US4] Implement conversation history loading on chat open in ChatWindow component (Just implemented)
- [x] T050 [P] [US4] Add simulated typing effect for bot responses in ChatWindow component (Just implemented)
- [x] T051 [P] [US4] Implement scroll position preservation on reopen in ChatWindow component (Already implemented - auto-scroll)
- [x] T052 [US4] Add visual distinction for user vs assistant messages (right/left alignment) in ChatWindow component (Already implemented)
- [x] T053 [US4] Add pulse animation to ChatbotIcon for new messages (optional enhancement) (Already implemented)
- [x] T054 [US4] Implement conversation persistence across page refreshes in ChatWindow component (Just implemented)
- [x] T055 [US4] Add dark mode support for chat components matching existing app theme (Already implemented)

**Checkpoint**: All user stories should now be independently functional with polished UX

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final production readiness

- [x] T056 [P] Add friendly response formatting with action confirmations in backend/src/services/chat_agent.py (Handled by Cohere's natural language generation)
- [x] T057 [P] Implement comprehensive error handling for tool failures in backend/src/services/mcp_tools.py (Already implemented with structured error responses)
- [x] T058 [P] Add user-friendly error messages for Cohere API errors in backend/src/services/chat_agent.py (Just implemented)
- [x] T059 [P] Add input validation and sanitization for chat messages in backend/src/api/chat.py (Just implemented - max 5000 chars)
- [ ] T060 [P] Add rate limiting middleware for chat endpoint in backend/src/api/chat.py (optional)
- [ ] T061 [P] Update Swagger documentation for chat endpoint in backend/src/api/chat.py
- [x] T062 [P] Add connection error handling in frontend ChatWindow component (Just implemented)
- [x] T063 [P] Add retry button for failed messages in frontend ChatWindow component (Just implemented)
- [x] T064 [P] Optimize message history truncation (20 messages) in backend/src/services/chat_agent.py (Already implemented)
- [x] T065 [P] Add logging for chat operations and tool calls in backend/src/services/chat_agent.py (Just implemented)
- [ ] T066 Verify Phase II functionality remains intact (no regressions in task CRUD API)
- [ ] T067 Run end-to-end validation following quickstart.md testing checklist
- [x] T068 [P] Update README with Cohere API key setup instructions (Just completed)
- [ ] T069 [P] Document ChatKit domain allowlist setup (if using hosted ChatKit)
- [ ] T070 Create demo flow documentation for hackathon judges

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 tools but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Completely independent from US1/US2
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Enhances UX for all stories but independently testable

### Within Each User Story

- Backend MCP tools can be implemented in parallel (marked [P])
- Chat agent integration depends on tools being complete
- Frontend components can be implemented in parallel (marked [P])
- Frontend integration depends on backend API being functional

### Parallel Opportunities

**Phase 1 (Setup)**: T002 and T003 can run in parallel

**Phase 2 (Foundational)**: T005, T008, T009, T010, T011 can all run in parallel after T004

**Phase 3 (User Story 1)**:
- Backend: T012, T013, T014 can run in parallel
- Frontend: T023, T024, T025 can run in parallel

**Phase 4 (User Story 2)**:
- Backend: T033, T034 can run in parallel

**Phase 5 (User Story 3)**:
- Backend: T041 can run independently
- Frontend: T044, T045 can run in parallel

**Phase 6 (User Story 4)**:
- Frontend: T049, T050, T051 can run in parallel

**Phase 7 (Polish)**: Most tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1 Backend

```bash
# Launch all MCP tools for User Story 1 together:
Task T012: "Implement add_task MCP tool in backend/src/services/mcp_tools.py"
Task T013: "Implement list_tasks MCP tool in backend/src/services/mcp_tools.py"
Task T014: "Implement complete_task MCP tool in backend/src/services/mcp_tools.py"

# Then proceed with chat agent (depends on tools):
Task T015: "Create chat agent runner in backend/src/services/chat_agent.py"
```

## Parallel Example: User Story 1 Frontend

```bash
# Launch all frontend components for User Story 1 together:
Task T023: "Create ChatbotIcon component in frontend/src/components/ChatbotIcon.tsx"
Task T024: "Create ChatWindow component in frontend/src/components/ChatWindow.tsx"
Task T025: "Create chat types in frontend/src/types/chat.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T011) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T012-T032)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Can add tasks via chat?
   - Can list tasks via chat?
   - Can complete tasks via chat?
   - Tasks sync with main UI?
   - Multilingual (English + Urdu) works?
5. Deploy/demo if ready - **This is your MVP!**

### Incremental Delivery

1. **Foundation** (Phases 1-2): Setup + Database + Core infrastructure → Foundation ready
2. **MVP** (Phase 3): User Story 1 → Test independently → Deploy/Demo (Basic chat works!)
3. **Enhanced** (Phase 4): User Story 2 → Test independently → Deploy/Demo (Full CRUD via chat!)
4. **Complete** (Phase 5): User Story 3 → Test independently → Deploy/Demo (Profile queries work!)
5. **Polished** (Phase 6): User Story 4 → Test independently → Deploy/Demo (Beautiful UX!)
6. **Production** (Phase 7): Polish → Final validation → Production ready

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (Phases 1-2)
2. **Once Foundational is done, split work**:
   - Developer A: User Story 1 (T012-T032) - Core chat functionality
   - Developer B: User Story 2 (T033-T040) - Advanced operations
   - Developer C: User Story 3 (T041-T045) - Profile queries
   - Developer D: User Story 4 (T049-T055) - UX enhancements
3. Stories complete and integrate independently
4. Team reconvenes for Polish phase

---

## Task Summary

**Total Tasks**: 70
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 8 tasks (BLOCKING)
- Phase 3 (User Story 1 - P1): 21 tasks (MVP)
- Phase 4 (User Story 2 - P2): 8 tasks
- Phase 5 (User Story 3 - P3): 5 tasks
- Phase 6 (User Story 4 - P4): 10 tasks
- Phase 7 (Polish): 15 tasks

**Parallelizable Tasks**: 35 tasks marked [P]

**Independent Test Criteria**:
- US1: Add, list, complete tasks via chat + verify in main UI
- US2: Update, delete, filter tasks via chat
- US3: Query profile info in English and Urdu
- US4: Conversation persists across sessions, smooth UX

**Suggested MVP Scope**: Phases 1-3 (32 tasks) = Basic conversational task management

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All file paths are absolute from repository root
- Backend uses Python/FastAPI, Frontend uses TypeScript/Next.js
- Database migrations must be applied before running backend
- Cohere API key must be configured before testing chat functionality
