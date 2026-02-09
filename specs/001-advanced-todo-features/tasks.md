# Tasks: Advanced Todo Features

**Input**: Design documents from `/specs/001-advanced-todo-features/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/

**Tests**: Tests are NOT requested in this feature specification. Focus on implementation and manual validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend/src/`
- Backend: Python files in `backend/`
- Frontend: TypeScript/React files in `frontend/src/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and verification of existing structure

- [ ] T001 Verify existing project structure (backend/ and frontend/ directories present)
- [ ] T002 Verify backend dependencies (FastAPI, SQLModel, Cohere SDK installed)
- [ ] T003 Verify frontend dependencies (Next.js, Tailwind CSS, date-fns installed)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database and schema changes that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Extend Task model in backend/models.py with new fields (priority, tags, due_date, remind_at, recurrence_rule, reminded)
- [ ] T005 Create database migration script backend/add_advanced_fields_migration.py to add new columns and indexes
- [ ] T006 Run migration script to update Neon PostgreSQL database schema
- [ ] T007 Update TaskCreate schema in backend/schemas.py to accept new optional fields
- [ ] T008 Update TaskUpdate schema in backend/schemas.py to accept new optional fields
- [ ] T009 Update TaskRead schema in backend/schemas.py to include new fields in responses
- [ ] T010 Extend Task TypeScript interface in frontend/src/lib/types.ts with new fields

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Priority Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to assign priority levels (low/medium/high/urgent) to tasks and view color-coded priority badges

**Independent Test**: Create tasks with different priorities via UI and chatbot, verify color-coded badges display correctly, filter by priority

### Backend Implementation for User Story 1

- [ ] T011 [P] [US1] Update POST /api/tasks endpoint in backend/main.py to accept and validate priority field
- [ ] T012 [P] [US1] Update PUT /api/tasks/{task_id} endpoint in backend/main.py to accept and validate priority field
- [ ] T013 [P] [US1] Update GET /api/tasks endpoint in backend/main.py to support priority query parameter for filtering
- [ ] T014 [US1] Update add_task tool in backend/mcp_schemas.py to include priority parameter
- [ ] T015 [US1] Update update_task tool in backend/mcp_schemas.py to include priority parameter
- [ ] T016 [US1] Update list_tasks tool in backend/mcp_schemas.py to include priority filter parameter
- [ ] T017 [US1] Update chat agent in backend/chat_agent.py to handle priority-related natural language commands

### Frontend Implementation for User Story 1

- [ ] T018 [P] [US1] Create PrioritySelect component in frontend/src/components/PrioritySelect.tsx with dropdown for 4 priority levels
- [ ] T019 [P] [US1] Add priority color classes to frontend/src/styles/globals.css (gray/yellow/orange/red for low/medium/high/urgent)
- [ ] T020 [US1] Update TaskForm component in frontend/src/components/TaskForm.tsx to include PrioritySelect
- [ ] T021 [US1] Update TaskCard component in frontend/src/components/TaskCard.tsx to display priority badge with color
- [ ] T022 [US1] Update api.ts in frontend/src/lib/api.ts to include priority in create/update task requests
- [ ] T023 [US1] Test priority management end-to-end (UI creation, display, chatbot commands, filtering)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Task Tagging and Organization (Priority: P2)

**Goal**: Enable users to add multiple tags to tasks and filter by tags

**Independent Test**: Add tags to tasks via UI chips input, view tags on task cards, filter by single/multiple tags, use chatbot to create tagged tasks

### Backend Implementation for User Story 2

- [ ] T024 [P] [US2] Update POST /api/tasks endpoint in backend/main.py to accept and validate tags array
- [ ] T025 [P] [US2] Update PUT /api/tasks/{task_id} endpoint in backend/main.py to accept and validate tags array
- [ ] T026 [P] [US2] Update GET /api/tasks endpoint in backend/main.py to support tags query parameter for filtering (comma-separated, AND logic)
- [ ] T027 [US2] Update add_task tool in backend/mcp_schemas.py to include tags parameter
- [ ] T028 [US2] Update update_task tool in backend/mcp_schemas.py to include tags parameter
- [ ] T029 [US2] Update list_tasks tool in backend/mcp_schemas.py to include tags filter parameter
- [ ] T030 [US2] Update chat agent in backend/chat_agent.py to handle tag-related natural language commands

### Frontend Implementation for User Story 2

- [ ] T031 [P] [US2] Create TagsInput component in frontend/src/components/TagsInput.tsx with chip input (add/remove tags)
- [ ] T032 [US2] Update TaskForm component in frontend/src/components/TaskForm.tsx to include TagsInput
- [ ] T033 [US2] Update TaskCard component in frontend/src/components/TaskCard.tsx to display tag chips with remove button
- [ ] T034 [US2] Update api.ts in frontend/src/lib/api.ts to include tags in create/update task requests
- [ ] T035 [US2] Test tag management end-to-end (UI add/remove, display, chatbot commands, filtering)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Search, Filter, and Sort (Priority: P3)

**Goal**: Enable users to search tasks by keywords, filter by multiple criteria, and sort by various fields

**Independent Test**: Search for tasks by title/description, apply multiple filters (status/priority/tags/date range), change sort order, verify results update correctly

**Dependencies**: Requires US1 (priority filtering) and US2 (tag filtering) to be complete

### Backend Implementation for User Story 3

- [ ] T036 [P] [US3] Implement search logic in backend/main.py GET /api/tasks endpoint using ILIKE on title and description
- [ ] T037 [P] [US3] Implement filter logic in backend/main.py GET /api/tasks endpoint for status, priority, tags, due_date range
- [ ] T038 [P] [US3] Implement sort logic in backend/main.py GET /api/tasks endpoint for due_date, priority, created_at, updated_at, title
- [ ] T039 [US3] Update list_tasks tool in backend/mcp_schemas.py to include search, filter, and sort parameters
- [ ] T040 [US3] Update chat agent in backend/chat_agent.py to handle search/filter/sort natural language commands

### Frontend Implementation for User Story 3

- [ ] T041 [P] [US3] Create SearchBar component in frontend/src/components/SearchBar.tsx with text input and search icon
- [ ] T042 [P] [US3] Create FilterControls component in frontend/src/components/FilterControls.tsx with dropdowns for status, priority, tags, date range
- [ ] T043 [P] [US3] Create SortDropdown component in frontend/src/components/SortDropdown.tsx with sort field and order selectors
- [ ] T044 [US3] Update TaskList component in frontend/src/app/tasks/page.tsx to include SearchBar, FilterControls, and SortDropdown
- [ ] T045 [US3] Update api.ts in frontend/src/lib/api.ts to include search, filter, and sort query parameters
- [ ] T046 [US3] Implement client-side state management for search/filter/sort in TaskList component
- [ ] T047 [US3] Test search/filter/sort end-to-end (UI controls, chatbot commands, combined filters, clear filters)

**Checkpoint**: All user stories 1, 2, and 3 should now be independently functional

---

## Phase 6: User Story 4 - Due Dates and Reminders (Priority: P4)

**Goal**: Enable users to set due dates and reminder times for tasks, view due dates on task cards, and trigger reminders

**Independent Test**: Create tasks with due dates and reminders via UI datetime pickers, view due dates with calendar icons, verify overdue highlighting, observe reminder logs when remind_at time reached

### Backend Implementation for User Story 4

- [ ] T048 [P] [US4] Update POST /api/tasks endpoint in backend/main.py to accept and validate due_date and remind_at timestamps
- [ ] T049 [P] [US4] Update PUT /api/tasks/{task_id} endpoint in backend/main.py to accept and validate due_date and remind_at timestamps
- [ ] T050 [P] [US4] Update GET /api/tasks endpoint in backend/main.py to support due_after and due_before query parameters
- [ ] T051 [P] [US4] Create reminder_helper.py in backend/ with check_reminders function to log reminders when remind_at <= now
- [ ] T052 [US4] Integrate check_reminders into GET /api/tasks endpoint in backend/main.py
- [ ] T053 [US4] Update add_task tool in backend/mcp_schemas.py to include due_date and remind_at parameters
- [ ] T054 [US4] Update update_task tool in backend/mcp_schemas.py to include due_date and remind_at parameters
- [ ] T055 [US4] Update list_tasks tool in backend/mcp_schemas.py to include due_after and due_before filter parameters
- [ ] T056 [US4] Update chat agent in backend/chat_agent.py to parse natural language dates/times (e.g., "tomorrow at 3pm", "in 2 hours")

### Frontend Implementation for User Story 4

- [ ] T057 [P] [US4] Create DateTimePicker component in frontend/src/components/DateTimePicker.tsx using HTML5 datetime-local input
- [ ] T058 [US4] Update TaskForm component in frontend/src/components/TaskForm.tsx to include DateTimePicker for due_date and remind_at
- [ ] T059 [US4] Update TaskCard component in frontend/src/components/TaskCard.tsx to display due date with calendar icon and overdue highlighting
- [ ] T060 [US4] Update FilterControls component in frontend/src/components/FilterControls.tsx to include due date range pickers
- [ ] T061 [US4] Update api.ts in frontend/src/lib/api.ts to include due_date, remind_at, due_after, due_before parameters
- [ ] T062 [US4] Implement date formatting utilities using date-fns in frontend/src/lib/utils.ts (relative time, timezone conversion)
- [ ] T063 [US4] Test due dates and reminders end-to-end (UI pickers, display, overdue highlighting, reminder logs, chatbot commands)

**Checkpoint**: User Stories 1, 2, 3, and 4 should all work independently

---

## Phase 7: User Story 5 - Recurring Tasks (Priority: P5)

**Goal**: Enable users to create recurring tasks that automatically spawn next occurrence when completed

**Independent Test**: Create recurring task with daily/weekly/monthly pattern, complete the task, verify next occurrence is auto-created with correct due date and inherited properties

**Dependencies**: Requires US4 (due dates) to be complete, as recurring tasks need due_date field

### Backend Implementation for User Story 5

- [ ] T064 [P] [US5] Update POST /api/tasks endpoint in backend/main.py to accept and validate recurrence_rule JSONB object
- [ ] T065 [P] [US5] Update PUT /api/tasks/{task_id} endpoint in backend/main.py to accept and validate recurrence_rule JSONB object
- [ ] T066 [P] [US5] Create recurring_helper.py in backend/ with calculate_next_due_date function for daily/weekly/monthly patterns
- [ ] T067 [US5] Update PATCH /api/tasks/{task_id}/complete endpoint in backend/main.py to check for recurrence_rule and create next occurrence
- [ ] T068 [US5] Implement next occurrence creation logic: inherit title, description, priority, tags, recurrence_rule; calculate new due_date
- [ ] T069 [US5] Update add_task tool in backend/mcp_schemas.py to include recurrence_rule parameter
- [ ] T070 [US5] Update update_task tool in backend/mcp_schemas.py to include recurrence_rule parameter
- [ ] T071 [US5] Update chat agent in backend/chat_agent.py to parse recurrence patterns (e.g., "repeat every day", "every Monday")

### Frontend Implementation for User Story 5

- [ ] T072 [P] [US5] Create RecurrenceSelect component in frontend/src/components/RecurrenceSelect.tsx with dropdown for daily/weekly/monthly/none
- [ ] T073 [US5] Update TaskForm component in frontend/src/components/TaskForm.tsx to include RecurrenceSelect
- [ ] T074 [US5] Update TaskCard component in frontend/src/components/TaskCard.tsx to display recurring icon/indicator
- [ ] T075 [US5] Update api.ts in frontend/src/lib/api.ts to include recurrence_rule in create/update task requests
- [ ] T076 [US5] Update complete task API call in frontend to handle response with next_occurrence data
- [ ] T077 [US5] Test recurring tasks end-to-end (UI creation, completion, next occurrence verification, chatbot commands)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final quality assurance

- [ ] T078 [P] Verify backward compatibility: test existing Phase I-IV features (basic CRUD, auth, chatbot) still work
- [ ] T079 [P] Add validation error messages for all new fields in backend/main.py
- [ ] T080 [P] Add client-side validation for all new form fields in frontend components
- [ ] T081 [P] Polish UI consistency: verify Tailwind classes, spacing, typography across all new components
- [ ] T082 [P] Test mobile responsiveness for all new UI components (SearchBar, FilterControls, etc.)
- [ ] T083 [P] Add loading states for search/filter/sort operations in TaskList component
- [ ] T084 [P] Add empty states for filtered/searched task lists with helpful messages
- [ ] T085 Handle edge case: recurring task without due_date (add validation or default behavior)
- [ ] T086 Handle edge case: remind_at after due_date (add warning message)
- [ ] T087 Handle edge case: duplicate tags (prevent in TagsInput component)
- [ ] T088 Handle edge case: very long tag names (truncate in UI, validate max length in backend)
- [ ] T089 Handle edge case: completing recurring task multiple times quickly (add debounce or lock)
- [ ] T090 Test performance with 100+ tasks: verify search <5s, filter <2s, sort <1s
- [ ] T091 Test performance with 500+ tasks: verify UI remains responsive
- [ ] T092 Verify timezone handling: timestamps stored in UTC, displayed in local timezone
- [ ] T093 Update API documentation (Swagger) with all new endpoints and parameters
- [ ] T094 Code cleanup: remove any console.logs, commented code, unused imports

---

## Phase 9: Final Review

**Purpose**: Comprehensive validation against all success criteria and user stories

- [ ] T095 Run through all 12 success criteria from spec.md (SC-001 to SC-012)
- [ ] T096 Test all 5 user stories end-to-end (P1 to P5) with acceptance scenarios
- [ ] T097 Verify all 20 functional requirements (FR-001 to FR-020) are implemented
- [ ] T098 Test all 8 edge cases from spec.md
- [ ] T099 Prepare demo flow: create advanced task via chat → filter → search → complete recurring → see next task
- [ ] T100 Document any known limitations or future enhancements in README
- [ ] T101 Create demo script for hackathon judges showing all features
- [ ] T102 Final smoke test: complete end-to-end workflow in <2 minutes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Priority): Can start after Foundational - No dependencies on other stories
  - US2 (Tags): Can start after Foundational - No dependencies on other stories (parallel with US1)
  - US3 (Search/Filter/Sort): Depends on US1 and US2 completion (needs priority and tag filtering)
  - US4 (Due Dates/Reminders): Can start after Foundational - No dependencies on other stories (parallel with US1/US2)
  - US5 (Recurring): Depends on US4 completion (recurring tasks need due dates)
- **Polish (Phase 8)**: Depends on all desired user stories being complete
- **Final Review (Phase 9)**: Depends on Polish completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories - Can run parallel with US1
- **User Story 3 (P3)**: Depends on US1 and US2 completion (needs priority and tag filtering to work)
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - No dependencies on other stories - Can run parallel with US1/US2
- **User Story 5 (P5)**: Depends on US4 completion (recurring tasks require due_date field)

### Within Each User Story

- Backend tasks before frontend tasks (API must exist before UI can call it)
- Models/schemas before endpoints (data structures before operations)
- MCP tools after endpoints (tools wrap API functionality)
- Chat agent updates after MCP tools (agent uses tools)
- UI components can be built in parallel (marked with [P])
- Integration/testing after all components complete

### Parallel Opportunities

- **Setup tasks**: T001, T002, T003 can run in parallel
- **Foundational tasks**: T004-T010 should run sequentially (database changes are sensitive)
- **After Foundational completes**:
  - US1 and US2 can start in parallel (independent features)
  - US4 can start in parallel with US1/US2 (independent feature)
- **Within US1**: T011, T012, T013 (backend endpoints) can run in parallel; T018, T019 (UI components) can run in parallel
- **Within US2**: T024, T025, T026 (backend endpoints) can run in parallel; T031 (UI component) independent
- **Within US3**: T036, T037, T038 (backend logic) can run in parallel; T041, T042, T043 (UI components) can run in parallel
- **Within US4**: T048, T049, T050, T051 (backend) can run in parallel; T057 (UI component) independent
- **Within US5**: T064, T065, T066 (backend) can run in parallel; T072 (UI component) independent
- **Polish tasks**: Most T078-T094 can run in parallel (different concerns)

---

## Parallel Example: User Story 1

```bash
# After Foundational phase completes, launch US1 backend tasks in parallel:
Task T011: "Update POST /api/tasks endpoint to accept priority"
Task T012: "Update PUT /api/tasks/{task_id} endpoint to accept priority"
Task T013: "Update GET /api/tasks endpoint to support priority filtering"

# Then launch US1 frontend tasks in parallel:
Task T018: "Create PrioritySelect component"
Task T019: "Add priority color classes to globals.css"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T010) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T011-T023)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready - you now have priority management working!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Priority) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (Tags) → Test independently → Deploy/Demo
4. Add User Story 3 (Search/Filter/Sort) → Test independently → Deploy/Demo
5. Add User Story 4 (Due Dates/Reminders) → Test independently → Deploy/Demo
6. Add User Story 5 (Recurring) → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T010)
2. Once Foundational is done:
   - Developer A: User Story 1 (T011-T023)
   - Developer B: User Story 2 (T024-T035)
   - Developer C: User Story 4 (T048-T063)
3. After US1 and US2 complete:
   - Developer A or B: User Story 3 (T036-T047)
4. After US4 completes:
   - Developer C: User Story 5 (T064-T077)
5. All developers: Polish & Final Review (T078-T102)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Foundational phase is CRITICAL - all user stories depend on it
- US3 depends on US1 and US2 (needs priority and tag filtering)
- US5 depends on US4 (recurring tasks need due dates)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests are NOT included (not requested in spec)
- Focus on implementation and manual validation against success criteria
