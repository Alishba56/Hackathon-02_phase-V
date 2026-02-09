---
id: 2
title: Phase III AI Chatbot Constitution
stage: constitution
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: phase-iii-ai-chatbot
branch: main
user: alish
command: /sp.constitution
labels: ["constitution", "phase-iii", "ai-chatbot", "cohere", "mcp-tools"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - None (constitution document)
---

## Prompt

/sp.constitution

Project: Phase III – AI Todo Chatbot Integration into Existing Full-Stack Todo Application

Core principles:

1. **Cohere-First Architecture**: Use Cohere API exclusively for LLM operations (command-r-plus or command-r model), adapt OpenAI Agents SDK patterns to Cohere's tool-calling API

2. **Stateless & Scalable**: Zero in-memory session state - all conversation history persisted in database (conversations + messages tables), server restarts don't lose context

3. **MCP Tool Standard**: All agent-tool interactions follow Model Context Protocol - expose task operations (add, list, complete, delete, update) and user profile as MCP-compatible tools

4. **Security-First**: JWT authentication on all chat endpoints, user_id extracted from token and enforced on all operations, strict task/conversation ownership isolation

5. **Natural Language Control**: Agent understands multilingual intents (English + Urdu), handles task management commands naturally ("Add task buy milk", "Show pending tasks", "Mera profile batao")

6. **Zero Breaking Changes**: Phase II functionality (task CRUD API, auth, frontend) remains fully operational, chatbot is additive feature only

7. **Database-Driven Context**: Conversation history loaded from DB on every request, messages stored after processing, enables context continuity across sessions

8. **Friendly & Contextual**: Agent provides action confirmations, graceful error handling, helpful responses with tool call visibility

9. **Spec-Driven Implementation**: All code generated via Claude Code with @specs references, full traceability through PHR (Prompt History Records)

10. **Production-Ready**: Pydantic validation, comprehensive error handling, Swagger docs, environment-based configuration, docker-compose deployment

## Response snapshot

Successfully created Phase III constitution (v1.1.0) with comprehensive principles for AI chatbot integration.

**Version Change**: 1.0.0 → 1.1.0 (MINOR bump)

**Rationale**: Added 10 new principles (VII-XVI) for Phase III AI chatbot integration while preserving all Phase II principles (I-VI). This is a material expansion of governance scope without breaking existing principles.

**Key Additions**:
- Principles VII-XVI covering Cohere integration, MCP tools, stateless architecture, security, multilingual support
- Phase III Constraints section (LLM provider lock, minimal dependencies, environment config, etc.)
- Phase III Standards section (chat endpoint spec, MCP tools spec, conversation storage, agent behavior)
- Phase III Success Criteria section (functional, technical, integration, quality requirements, deliverables)

**Preserved from Phase II**:
- All original principles I-VI unchanged
- Phase II constraints maintained
- Development workflow preserved
- Governance structure intact

**File Updated**: `.specify/memory/constitution.md`

**Sync Impact**:
- ✅ constitution.md - updated
- ⚠ plan-template.md - may need review for AI/MCP tool planning sections
- ⚠ spec-template.md - may need review for agent/chatbot specification sections
- ⚠ tasks-template.md - may need review for AI integration task categories

## Outcome

- ✅ Impact: Phase III constitution established with 16 comprehensive principles, clear constraints, standards, and success criteria. Provides complete governance framework for Cohere-powered AI chatbot integration.
- 🧪 Tests: N/A (constitution document)
- 📁 Files: 1 file updated (.specify/memory/constitution.md)
- 🔁 Next prompts: /sp.specify (create Phase III feature specification), /sp.plan (design architecture), /sp.tasks (break down implementation)
- 🧠 Reflection: Constitution successfully balances Phase II preservation with Phase III innovation. Clear separation of concerns between phases. MCP tool standard and Cohere-first approach well-defined. Security and stateless architecture principles ensure production readiness.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution creation successful
- Graders run and results (PASS/FAIL): Manual review - PASS (all placeholders filled, version incremented correctly, principles clear and testable)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed with /sp.specify to create detailed feature specification for AI chatbot, referencing constitution principles
