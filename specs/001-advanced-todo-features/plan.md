# Implementation Plan: Advanced Todo Features

**Branch**: `001-advanced-todo-features` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-advanced-todo-features/spec.md`

**Note**: This plan focuses exclusively on frontend and backend enhancements to the monolith application. No infrastructure, Dapr, Kafka, microservices, or Kubernetes changes are included.

## Summary

Extend the existing Todo AI Chatbot with intermediate and advanced productivity features to make it competitive with professional tools like Todoist and Notion. Add priority levels (low/medium/high/urgent), multi-tag organization, full-text search, advanced filtering and sorting, due dates with reminders, and recurring task automation. All features implemented within the existing Next.js frontend and FastAPI backend monolith, maintaining 100% backward compatibility with Phase I-IV functionality.

**Primary Requirement**: Complete intermediate features (priorities, tags, search, filter, sort) and advanced features (recurring tasks, due dates, reminders) exclusively in the monolith application.

**Technical Approach**: Extend database schema with new Task fields, enhance REST API with query parameters, update Cohere agent tools for natural language support, and build rich UI components with Tailwind CSS. Implement basic synchronous recurring/reminder logic without external schedulers or event systems.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Next.js 16+ (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Neon Serverless PostgreSQL, Cohere API (command-r-plus), Tailwind CSS, Better Auth (JWT), date-fns (date formatting)
**Storage**: PostgreSQL with JSONB support for tags and recurrence rules, UTC timestamps for dates
**Testing**: Manual validation against success criteria, end-to-end workflow testing via UI and chatbot
**Target Platform**: Web browser (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend + backend monorepo)
**Performance Goals**: Search <5s (100+ tasks), filter <2s, sort <1s, recurring task creation <1s, UI updates instant
**Constraints**: No new external libraries beyond existing stack, no infrastructure changes, no event-driven architecture, maintain backward compatibility
**Scale/Scope**: Support up to 1000 tasks per user with acceptable performance, typical user has 50-200 tasks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Status: ✅ PASS

**Principle I - Fully Spec-Driven Development**: ✅ PASS
- Feature specification created and validated before implementation
- All requirements traceable to spec.md

**Principle II - Zero Manual Coding**: ✅ PASS
- All implementation will be generated via Claude Code using spec references

**Principle IV - Complete User Isolation**: ✅ PASS
- All new features maintain user_id filtering on API endpoints
- JWT authentication required for all operations

**Principle V - Strict Technology Stack Adherence**: ✅ PASS
- Uses only specified stack: Next.js, FastAPI, SQLModel, Neon PostgreSQL, Cohere, Tailwind
- No new external libraries beyond date-fns (already in use)

**Principle VI - Monorepo Structure Compliance**: ✅ PASS
- Maintains frontend/ and backend/ separation
- Specs organized under /specs/001-advanced-todo-features/

**Principle VII - Cohere-First LLM**: ✅ PASS
- Extends existing Cohere agent tools with new parameters
- No OpenAI dependencies

**Principle VIII - Stateless Chat Architecture**: ✅ PASS
- No changes to stateless architecture
- Conversation history remains database-driven

**Principle XII - Zero Breaking Changes**: ✅ PASS (CRITICAL)
- All Phase I-IV features remain operational
- New fields have defaults (priority="medium", tags=[], due_date=None)
- Additive API changes only (new optional fields, new query params)

**Principle XIX - Backward Compatibility Preservation**: ✅ PASS
- Explicitly required by FR-019
- Existing task CRUD, auth, and chatbot functionality unaffected

### Exclusions Verified

**NOT implementing** (per user requirements):
- ❌ Dapr sidecars or components
- ❌ Kafka/Redpanda event publishing
- ❌ Microservices (Notification, Recurring, Audit, WebSocket)
- ❌ Kubernetes/Minikube deployment changes
- ❌ CI/CD pipelines
- ❌ Infrastructure monitoring/logging

**Scope**: Monolith enhancements only (frontend + backend)

## Project Structure

### Documentation (this feature)

```text
specs/001-advanced-todo-features/
├── spec.md                    # Feature specification (completed)
├── plan.md                    # This file (/sp.plan command output)
├── research.md                # Phase 0 output (design decisions)
├── data-model.md              # Phase 1 output (extended Task entity)
├── quickstart.md              # Phase 1 output (usage guide)
├── contracts/                 # Phase 1 output (API specs)
│   ├── task-api-extended.yaml # Extended task endpoints
│   └── query-params.yaml      # Search/filter/sort parameters
├── checklists/
│   └── requirements.md        # Validation checklist (completed)
└── tasks.md                   # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── models.py                  # SQLModel Task class (extend with new fields)
├── schemas.py                 # Pydantic request/response models (extend)
├── main.py                    # FastAPI app (extend endpoints)
├── db.py                      # Database connection (no changes)
├── auth.py                    # JWT authentication (no changes)
├── chat_agent.py              # Cohere agent runner (extend tools)
├── mcp_schemas.py             # MCP tool definitions (extend)
├── chat_schemas.py            # Chat request/response (no changes)
├── cohere_client.py           # Cohere API client (no changes)
├── recurring_helper.py        # NEW: Recurring task logic
└── reminder_helper.py         # NEW: Reminder check logic

frontend/
├── src/
│   ├── app/
│   │   ├── tasks/
│   │   │   └── page.tsx       # Task list page (enhance with filters/search/sort)
│   │   └── chat/
│   │       └── page.tsx       # Chat page (no changes)
│   ├── components/
│   │   ├── TaskForm.tsx       # Task form (add priority, tags, dates, recurrence)
│   │   ├── TaskCard.tsx       # Task card (add badges, chips, due date display)
│   │   ├── TaskList.tsx       # Task list (add search/filter/sort controls)
│   │   ├── PrioritySelect.tsx # NEW: Priority dropdown
│   │   ├── TagsInput.tsx      # NEW: Tag chips input
│   │   ├── DateTimePicker.tsx # NEW: Due date/reminder picker
│   │   ├── RecurrenceSelect.tsx # NEW: Recurrence pattern selector
│   │   ├── SearchBar.tsx      # NEW: Search input
│   │   ├── FilterControls.tsx # NEW: Filter dropdowns
│   │   └── SortDropdown.tsx   # NEW: Sort selector
│   ├── lib/
│   │   ├── api.ts             # API client (extend with new params)
│   │   └── types.ts           # TypeScript types (extend Task interface)
│   └── styles/
│       └── globals.css        # Tailwind styles (add priority colors)
└── package.json               # Dependencies (no new packages)
```

**Structure Decision**: Web application structure with frontend/ and backend/ directories. This matches the existing monorepo layout and supports the full-stack nature of the feature. Backend handles data persistence, business logic, and AI agent integration. Frontend provides rich UI components for task management with search, filtering, and sorting capabilities.

## Complexity Tracking

> **No violations** - All constitution checks passed. This feature is additive only and maintains full backward compatibility.

## Phase 0: Research & Design Decisions

### Decision 1: Priority Storage Format

**Decision**: Use string enum with values: "low", "medium", "high", "urgent"

**Rationale**:
- Easier UI display (no mapping from numbers to labels)
- Simpler filtering in SQL (WHERE priority = 'urgent')
- More readable in database and API responses
- Allows for easy color mapping in frontend

**Alternatives Considered**:
- Numeric scale (1-5): Rejected because requires mapping layer and less intuitive
- Separate priority table: Rejected as over-engineering for 4 fixed values

**Implementation**: SQLModel field with default="medium", frontend dropdown with 4 options

---

### Decision 2: Tags Storage Format

**Decision**: Store as JSONB array in PostgreSQL: `tags JSONB DEFAULT '[]'::jsonb`

**Rationale**:
- PostgreSQL JSONB supports efficient array operations
- GIN index enables fast tag filtering: `WHERE tags @> '["work"]'::jsonb`
- No need for separate tags table and junction table
- Simpler schema and queries
- Supports arbitrary tag names without schema changes

**Alternatives Considered**:
- Separate tags table with many-to-many relationship: Rejected as over-engineering, adds query complexity
- Plain TEXT array: Considered but JSONB more flexible for future extensions

**Implementation**: SQLModel field `tags: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSONB))`, create GIN index for performance

---

### Decision 3: Recurrence Rule Format

**Decision**: Store as simple JSON object: `{"frequency": "daily"|"weekly"|"monthly"|"custom", "interval": 1, "end_date": null}`

**Rationale**:
- No external rrule library needed (keeps dependencies minimal)
- Sufficient for common use cases (daily, weekly, monthly)
- Easy to parse and calculate next occurrence
- Extensible for future enhancements

**Alternatives Considered**:
- Full RRULE string (RFC 5545): Rejected as over-engineering, requires external library
- Separate recurrence table: Rejected as unnecessary complexity

**Implementation**: SQLModel field `recurrence_rule: Optional[dict] = Field(default=None, sa_column=Column(JSONB))`, backend helper function to calculate next due date

---

### Decision 4: Reminder Trigger Mechanism

**Decision**: Simple timestamp check on GET /tasks endpoint, log to console when remind_at <= now

**Rationale**:
- Placeholder for future notification system
- No background scheduler needed (keeps architecture simple)
- Sufficient for Phase V monolith scope
- Easy to replace with real notification system later

**Alternatives Considered**:
- Background scheduler (APScheduler): Rejected as adds complexity and not needed for placeholder
- Dapr Jobs API: Explicitly excluded from this phase

**Implementation**: In list_tasks function, check each task's remind_at, if <= now and not yet reminded, log message and mark as reminded

---

### Decision 5: Search Implementation

**Decision**: PostgreSQL ILIKE on title and description: `WHERE title ILIKE '%keyword%' OR description ILIKE '%keyword%'`

**Rationale**:
- Simple and sufficient for typical task lists (50-200 tasks)
- No additional setup required
- Case-insensitive search
- Can add trigram index (pg_trgm) if performance becomes issue

**Alternatives Considered**:
- Full-text search with tsvector: Rejected as over-engineering for current scale
- Elasticsearch: Rejected as external dependency and infrastructure

**Implementation**: Add search query parameter to GET /tasks, apply ILIKE filter in SQLModel query

---

### Decision 6: Due Date and Reminder UI

**Decision**: Use HTML5 datetime-local input with date-fns for formatting and timezone handling

**Rationale**:
- Native browser support (no external date picker library)
- Consistent UX across browsers
- date-fns already in project for formatting
- Handles timezone conversion (store UTC, display local)

**Alternatives Considered**:
- External date picker library (react-datepicker): Rejected to avoid new dependencies
- Separate date and time inputs: Rejected as less user-friendly

**Implementation**: `<input type="datetime-local">` in TaskForm, date-fns for display formatting in TaskCard

---

### Decision 7: Filter and Sort UI Layout

**Decision**: Horizontal layout with dropdowns and search bar above task list (mobile-friendly)

**Rationale**:
- Clean, uncluttered interface
- Mobile-responsive (dropdowns collapse well)
- Consistent with modern task management apps
- Easy to clear filters

**Alternatives Considered**:
- Advanced sidebar: Rejected as takes up screen space and less mobile-friendly
- Modal/popup filters: Rejected as adds extra clicks

**Implementation**: FilterControls component with inline dropdowns, SearchBar component, SortDropdown component, all in TaskList header

---

## Phase 1: Data Model & API Contracts

### Extended Task Entity

**Core Entity**: Task (extends existing)

**New Fields**:
- `priority`: String enum (low, medium, high, urgent), default "medium"
- `tags`: JSONB array of strings, default []
- `due_date`: Timestamp with timezone, nullable
- `remind_at`: Timestamp with timezone, nullable
- `recurrence_rule`: JSONB object, nullable
- `reminded`: Boolean, default false (internal flag for reminder tracking)

**Existing Fields** (preserved):
- `id`: Integer, primary key
- `user_id`: Integer, foreign key to users table
- `title`: String, required
- `description`: String, nullable
- `status`: String enum (pending, completed), default "pending"
- `created_at`: Timestamp
- `updated_at`: Timestamp

**Indexes**:
- Existing: `user_id`, `status`
- New: `due_date`, `priority`, GIN index on `tags`

**Validation Rules**:
- Priority must be one of: low, medium, high, urgent
- Tags array max 10 items, each tag max 50 characters
- If recurrence_rule present, due_date must be set
- remind_at must be before due_date if both set
- Timestamps stored in UTC, displayed in user's local timezone

**State Transitions**:
- When task with recurrence_rule is marked completed → create new task with next due_date
- When remind_at <= current_time and not reminded → log reminder and set reminded=true

### API Contracts

**Extended Endpoints**:

1. **POST /api/tasks** - Create task with new fields
2. **PUT /api/tasks/{task_id}** - Update task with new fields
3. **GET /api/tasks** - List tasks with search/filter/sort
4. **PATCH /api/tasks/{task_id}/complete** - Complete task (triggers recurring logic)

**New Query Parameters** (GET /api/tasks):
- `search`: String (searches title and description)
- `priority`: String (filters by priority level)
- `tags`: Comma-separated strings (filters by tags, AND logic)
- `status`: String (pending, completed)
- `due_after`: ISO datetime (tasks due after this date)
- `due_before`: ISO datetime (tasks due before this date)
- `sort_by`: String (due_date, priority, created_at, updated_at, title)
- `sort_order`: String (asc, desc), default asc

**Request/Response Schema Changes**:
- TaskCreate: Add optional priority, tags, due_date, remind_at, recurrence_rule
- TaskUpdate: Add optional priority, tags, due_date, remind_at, recurrence_rule
- TaskRead: Include all new fields in response

**Cohere Agent Tool Updates**:
- `add_task`: Add parameters for priority, tags, due_date, remind_at, recurrence_rule
- `update_task`: Add parameters for priority, tags, due_date, remind_at, recurrence_rule
- `list_tasks`: Add parameters for search, priority, tags, status, due_after, due_before, sort_by

### Quickstart Guide

**Using Priority Levels**:
- UI: Select priority from dropdown when creating/editing task
- Chat: "Add urgent task: prepare presentation"

**Using Tags**:
- UI: Type tag names in tag input, press Enter to add
- Chat: "Add task: review code with tags work and urgent"

**Searching Tasks**:
- UI: Type keywords in search bar above task list
- Chat: "Show tasks about meeting"

**Filtering Tasks**:
- UI: Use filter dropdowns (priority, tags, status, date range)
- Chat: "Show high priority tasks tagged work"

**Sorting Tasks**:
- UI: Select sort option from dropdown (due date, priority, created date, title)
- Chat: "Show tasks sorted by due date"

**Setting Due Dates and Reminders**:
- UI: Use datetime pickers in task form
- Chat: "Add task: meeting tomorrow at 3pm, remind 30 min before"

**Creating Recurring Tasks**:
- UI: Select recurrence pattern in task form (daily, weekly, monthly)
- Chat: "Add task: team standup, repeat every Monday at 9am"

## Phase 2: Implementation Phases

### Phase 2.1: Database & Backend Schema

**Tasks**:
1. Extend Task model in models.py with new fields
2. Create database migration script (add columns, indexes)
3. Update Pydantic schemas (TaskCreate, TaskUpdate, TaskRead)
4. Test schema changes with sample data

**Acceptance**:
- Task model includes all new fields with correct types and defaults
- Database migration runs successfully on Neon PostgreSQL
- Pydantic schemas validate new fields correctly

---

### Phase 2.2: API Extensions

**Tasks**:
1. Extend POST /api/tasks to accept new fields
2. Extend PUT /api/tasks/{task_id} to accept new fields
3. Extend GET /api/tasks with query parameters
4. Implement search logic (ILIKE on title/description)
5. Implement filter logic (priority, tags, status, date range)
6. Implement sort logic (multiple sort fields)
7. Update API documentation

**Acceptance**:
- API accepts and persists all new task fields
- Search returns correct results for keywords
- Filters work individually and in combination
- Sort orders tasks correctly by selected field
- API responses include all new fields

---

### Phase 2.3: Recurring & Reminder Logic

**Tasks**:
1. Create recurring_helper.py with calculate_next_due_date function
2. Create reminder_helper.py with check_reminders function
3. Hook recurring logic into PATCH /api/tasks/{task_id}/complete
4. Hook reminder check into GET /api/tasks
5. Test recurring task creation (daily, weekly, monthly)
6. Test reminder logging

**Acceptance**:
- Completing recurring task creates next occurrence with correct due date
- Next occurrence inherits title, description, priority, tags, recurrence_rule
- Reminder logs to console when remind_at time reached
- Reminder only logs once per task (reminded flag prevents duplicates)

---

### Phase 2.4: Cohere Agent Update

**Tasks**:
1. Update mcp_schemas.py with new tool parameters
2. Update chat_agent.py to handle new intents
3. Test natural language commands for all new features
4. Verify chatbot accuracy (target 90%)

**Acceptance**:
- Chatbot creates tasks with priority, tags, due dates, reminders, recurrence
- Chatbot filters and searches tasks correctly
- Chatbot updates task properties via natural language
- Chatbot handles edge cases gracefully

---

### Phase 2.5: Frontend UI Components

**Tasks**:
1. Create PrioritySelect component (dropdown with 4 options)
2. Create TagsInput component (chip input with add/remove)
3. Create DateTimePicker component (datetime-local input)
4. Create RecurrenceSelect component (dropdown with patterns)
5. Create SearchBar component (text input with icon)
6. Create FilterControls component (priority, tags, date range dropdowns)
7. Create SortDropdown component (sort field and order)
8. Update TaskForm with new input components
9. Update TaskCard with priority badge, tag chips, due date display
10. Update TaskList with search/filter/sort controls
11. Add priority color classes to Tailwind config
12. Test UI responsiveness and accessibility

**Acceptance**:
- All new components render correctly
- TaskForm includes all new fields with proper validation
- TaskCard displays priority badge (color-coded), tag chips, due date with icon
- TaskList has search bar, filter controls, sort dropdown
- UI updates instantly when search/filter/sort changes
- Mobile-responsive layout works on small screens

---

### Phase 2.6: Integration & Polish

**Tasks**:
1. Update api.ts with new request parameters
2. Update types.ts with extended Task interface
3. Test end-to-end workflows (UI + API + chatbot)
4. Fix any regressions in Phase I-IV features
5. Verify backward compatibility
6. Polish UI consistency (colors, spacing, typography)
7. Test performance with large task lists (500+ tasks)
8. Handle edge cases (empty states, validation errors)

**Acceptance**:
- All Phase I-IV features work without regression
- End-to-end workflow completes in <2 minutes
- Search performs in <5s with 100+ tasks
- Filters apply in <2s
- Sort updates in <1s
- Recurring task creation in <1s
- UI is visually consistent and polished

---

### Phase 2.7: Final Validation

**Tasks**:
1. Run through all success criteria (SC-001 to SC-012)
2. Test all user stories (P1 to P5)
3. Verify all functional requirements (FR-001 to FR-020)
4. Test all edge cases from spec
5. Prepare demo flow for hackathon judges
6. Document any known limitations

**Acceptance**:
- All 12 success criteria met
- All 5 user stories fully functional
- All 20 functional requirements implemented
- All edge cases handled gracefully
- Demo flow works flawlessly
- Ready for hackathon presentation

---

## Testing Strategy

### Manual Validation Checklist

**Priority Management**:
- [ ] Create task with each priority level (low, medium, high, urgent)
- [ ] Verify color-coded badges display correctly
- [ ] Update task priority via UI
- [ ] Create task with priority via chatbot
- [ ] Filter tasks by priority

**Tag Management**:
- [ ] Add multiple tags to task via UI
- [ ] Remove tag from task
- [ ] Create task with tags via chatbot
- [ ] Filter tasks by single tag
- [ ] Filter tasks by multiple tags
- [ ] Verify duplicate tags prevented

**Search**:
- [ ] Search by title keyword
- [ ] Search by description keyword
- [ ] Search with no results
- [ ] Search with filters active

**Filtering**:
- [ ] Filter by status (pending, completed)
- [ ] Filter by priority
- [ ] Filter by tags
- [ ] Filter by due date range
- [ ] Combine multiple filters
- [ ] Clear all filters

**Sorting**:
- [ ] Sort by due date (asc, desc)
- [ ] Sort by priority (asc, desc)
- [ ] Sort by created date (asc, desc)
- [ ] Sort by title (asc, desc)

**Due Dates & Reminders**:
- [ ] Set due date on task
- [ ] Set reminder time on task
- [ ] Verify due date displays with icon
- [ ] Verify overdue tasks highlighted
- [ ] Set remind_at in past, verify log fires
- [ ] Filter by due date range

**Recurring Tasks**:
- [ ] Create daily recurring task
- [ ] Create weekly recurring task
- [ ] Create monthly recurring task
- [ ] Complete recurring task, verify next occurrence created
- [ ] Verify next occurrence has correct due date
- [ ] Verify next occurrence inherits properties
- [ ] Remove recurrence rule, verify no new occurrence

**Chatbot Integration**:
- [ ] "Add urgent task: meeting with tags work"
- [ ] "Add task: groceries due tomorrow remind 1 hour before repeat daily"
- [ ] "Show high priority tasks tagged urgent"
- [ ] "Make task 3 repeat every Monday"
- [ ] "Search for meeting tasks"

**Backward Compatibility**:
- [ ] Create basic task (no new fields)
- [ ] Update basic task
- [ ] Complete basic task
- [ ] Delete basic task
- [ ] Use chatbot for basic operations
- [ ] Verify auth still works

**Performance**:
- [ ] Create 100+ tasks, test search speed
- [ ] Apply filters with 500+ tasks
- [ ] Change sort order with large list
- [ ] Verify UI remains responsive

**Edge Cases**:
- [ ] Create recurring task without due date (should require or default)
- [ ] Set remind_at after due_date (should validate)
- [ ] Add 20+ tags to task (should limit or handle gracefully)
- [ ] Very long tag names (should truncate)
- [ ] Complete recurring task multiple times quickly
- [ ] Past due dates and reminders

---

## Risk Analysis

**Risk 1: Performance degradation with large task lists**
- Mitigation: Add database indexes on due_date, priority, tags (GIN)
- Mitigation: Implement pagination if needed (not in initial scope)
- Likelihood: Low (typical user has <200 tasks)

**Risk 2: Timezone handling complexity**
- Mitigation: Store all timestamps in UTC, convert to local timezone in frontend
- Mitigation: Use date-fns for consistent timezone handling
- Likelihood: Medium (common source of bugs)

**Risk 3: Recurring task logic bugs**
- Mitigation: Thorough testing of all recurrence patterns
- Mitigation: Simple JSON format reduces complexity
- Likelihood: Medium (date arithmetic is error-prone)

**Risk 4: Chatbot accuracy below 90% target**
- Mitigation: Comprehensive tool schema definitions
- Mitigation: Test with diverse natural language inputs
- Likelihood: Low (Cohere tool-calling is robust)

**Risk 5: Backward compatibility breaks**
- Mitigation: All new fields have defaults
- Mitigation: Additive API changes only
- Mitigation: Comprehensive regression testing
- Likelihood: Very Low (design prioritizes compatibility)

---

## Dependencies & Blockers

**External Dependencies**:
- Neon PostgreSQL database (existing, no changes needed)
- Cohere API (existing, no changes needed)
- date-fns library (existing in frontend)

**Internal Dependencies**:
- Phase I-IV codebase must be stable
- Database migration must complete successfully
- No blockers identified

**Assumptions**:
- Neon PostgreSQL supports JSONB and GIN indexes (verified)
- Cohere API supports extended tool schemas (verified)
- Frontend can handle datetime-local input (standard HTML5)

---

## Success Metrics

**Functional Completeness**:
- All 5 user stories (P1-P5) fully implemented
- All 20 functional requirements (FR-001 to FR-020) met
- All 8 edge cases handled

**Performance Targets**:
- Search: <5 seconds with 100+ tasks
- Filter: <2 seconds with any combination
- Sort: <1 second for any field
- Recurring task creation: <1 second
- UI updates: Instant (<100ms perceived)

**Quality Targets**:
- Chatbot accuracy: 90%+ for new features
- Backward compatibility: 100% (zero regressions)
- User satisfaction: 95% can use without training

**Hackathon Goal**:
- Judges confirm: "Feels like serious competitor to Todoist/Notion"

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Run `/sp.tasks`** to generate detailed task breakdown
3. **Begin Phase 2.1** (Database & Backend Schema)
4. **Iterate through phases** 2.1 to 2.7 sequentially
5. **Validate against success criteria** after each phase
6. **Prepare demo** for hackathon judges

**Estimated Effort**: 3-5 days for full implementation (all phases)

**Ready for**: `/sp.tasks` command to generate actionable task list
