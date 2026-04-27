---
name: planning
description: "**WORKFLOW SKILL** — Feature, task, and project planning with full implementation blueprints. USE FOR: planning a new feature, designing a new module, breaking down a large task into micro-tasks, writing implementation plans before coding, planning an entire application from PRD, understanding current codebase state before adding something new. DO NOT USE FOR: actually implementing code (use backend-dev skill), debugging existing issues, or reviewing code. PRODUCES: structured .md files in .project_docs/ with task breakdown, implementation plan, file-level code outlines, ASCII diagrams, and DB schema decisions."
argument-hint: "Describe what you want to plan (e.g., 'plan the payments feature', 'plan the full app from PRD', 'plan lead scoring task')"
---

# Planning Skill

Produces a structured, professional planning output for any feature, task, or full project. All output is saved to `.project_docs/`.

## When to Use

- Starting a new feature from scratch
- Breaking down a large or ambiguous task before coding begins
- Understanding the current codebase state relative to what needs to be built
- Writing an implementation plan from a PRD
- Ensuring new work fits the existing architecture

## Deliverables

For every planning session, produce two files in `.project_docs/`:

| File | Purpose |
|------|---------|
| `<task_name>.md` | Task breakdown — micro-tasks, phases, acceptance criteria |
| `<task_name>_implementation_plan.md` | Deep implementation blueprint per phase |

---

## Step-by-Step Procedure

### Step 1 — Understand the Problem / Task

Read and restate the user's request in your own words before doing anything else.

- What is being asked to build or change?
- Is this a feature, a bug fix, a refactor, or a new project?
- What is the expected outcome for the end user?
- Are there constraints (performance, security, compatibility)?

If a PRD document is attached or exists in `.project_docs/`, read it fully at this step.

---

### Step 2 — Understand the Current State of the Codebase

If code already exists in the workspace:

1. **Read the project structure** — map out folders, modules, existing routes/models/interactors
2. **Identify what is already implemented** — list features, endpoints, DB tables, services that exist
3. **Identify what is partially implemented** — half-built features, stubs, TODOs
4. **Identify what is missing** — gaps between current state and what needs to be built
5. **Read relevant existing files** — any file that the new task will interact with or extend

State this as a clear "Current State Summary" before planning.

---

### Step 3 — Create `.project_docs/` if it doesn't exist

Check whether `.project_docs/` exists at the workspace root. If not, create it.

---

### Step 4 — Break the Task into Micro-Tasks

Save to `.project_docs/<task_name>.md`.

Structure:

```markdown
# <Task Name>

## Problem Statement
<One paragraph describing what needs to be built and why.>

## Current State
<Bullet list of what already exists and what is relevant to this task.>

## Goal
<What the application can do after this task is complete.>

## Out of Scope
<What is explicitly NOT included in this task.>

## Phases & Micro-Tasks

### Phase 1 — <Phase Name>
- [ ] Task 1.1 — <specific, actionable item>
- [ ] Task 1.2 — <specific, actionable item>

### Phase 2 — <Phase Name>
- [ ] Task 2.1 — ...

## Acceptance Criteria
- [ ] <Measurable condition that proves the task is done>
- [ ] <Another condition>

## Dependencies
- <Any external service, library, or prior task this depends on>
```

Rules for micro-tasks:
- Each micro-task should be completable in one focused dev session
- Name them as actions: "Create X", "Add Y to Z", "Update A to support B"
- Order them by dependency (can't write interactor before the model exists)
- Group into phases: typically Schema → Model → Migration → Interactor → Route → Tests

---

### Step 5 — Write the Implementation Plan

Save to `.project_docs/<task_name>_implementation_plan.md`.

For **each phase**, include all of the following sections:

```markdown
# <Task Name> — Implementation Plan

---

## Phase <N>: <Phase Name>

### Summary
<2-3 sentence description of what this phase accomplishes.>

### What Already Exists
<Bullet list of existing code/files/tables that are relevant and will be reused or extended.>

### What Will Change
<Bullet list of what will be added, modified, or removed in this phase.>

### Approach
<Describe the implementation approach in plain English — how will this be built?>

### Why This Approach
<Justify the choice: why is this the professional, standard, scalable way to implement it? What alternatives were considered and why rejected?>

### Fit & Scalability
<Explain how this fits into the current application architecture and how it can scale for future features.>

### Files Affected

| File | Action | Reason |
|------|--------|--------|
| `backend/database/models/item.py` | CREATE | New ORM model for items table |
| `backend/database/migrations/item.py` | CREATE | CRUD operations for items |
| `backend/interactors/item.py` | CREATE | Business logic for item management |
| `backend/routes/item.py` | CREATE | API endpoints for item CRUD |
| `backend/schema/item.py` | CREATE | Request/response Pydantic models |
| `backend/main.py` | EDIT | Register new router |

### ASCII Architecture Diagram

<Draw a diagram showing how this phase's components connect. Examples below.>

**Data Flow:**
```
Request
  │
  ▼
[Route: POST /v1/items/]
  │  delegates
  ▼
[Interactor: create_item()]
  │  calls
  ▼
[Repository: item_repo.create_item()]
  │  writes
  ▼
[DB: items table]
  │  returns
  ▼
[ItemResponse]
  │
  ▼
Response
```

**Module Dependency:**
```
routes/item.py
    └── interactors/item.py
            ├── database/migrations/item.py
            │       └── database/models/item.py
            └── utils/custom_exceptions.py
```

### Code for Each File

For each file in the "Files Affected" table, include the full implementation code:

#### `backend/schema/item.py`
```python
# Full implementation code here
```

#### `backend/database/models/item.py`
```python
# Full implementation code here
```

#### `backend/database/migrations/item.py`
```python
# Full implementation code here
```

#### `backend/interactors/item.py`
```python
# Full implementation code here
```

#### `backend/routes/item.py`
```python
# Full implementation code here
```

### Step-by-Step Implementation Guide

Numbered instructions for the developer to follow — in order:

1. Create `backend/schema/item.py` with the Pydantic models above
2. Create `backend/database/models/item.py` and register in `__init__.py`
3. Run `uv run alembic revision --autogenerate -m "add_items_table"` and review the generated file
4. Run `uv run alembic upgrade head` to apply migration
5. Create `backend/database/migrations/item.py` with CRUD functions
6. Create `backend/interactors/item.py` with business logic
7. Create `backend/routes/item.py` and register in `main.py`
8. Write tests in `backend/tests/item/test_item.py`
9. Run `uv run pytest tests/item/` to verify all pass
```

---

### Database Schema Section (if DB is involved)

If the task involves database changes, include a dedicated section:

```markdown
### Database Schema

#### Table: `<table_name>`

| Column | Type | Constraints | Reason |
|--------|------|-------------|--------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid4 | Globally unique, not guessable |
| `name` | VARCHAR(255) | NOT NULL | Core identifier for the item |
| `owner_id` | UUID | FK → users.id, NOT NULL | Multi-tenant ownership |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT now() | Audit trail |

#### Why This Schema
<Explain the design decisions — why UUID vs int ID, why certain nullable/non-null choices, why specific FK relationships, indexing strategy.>

#### Entity Relationship

```
users
  │
  │ 1:N
  ▼
items ──────── sub_accounts
  │                  │
  │ N:1              │ 1:N
  ▼                  ▼
item_tags       account_items
```

#### SQLAlchemy Model Code
```python
# Full model code
```

#### Alembic Migration Code
```python
# Full migration code (upgrade + downgrade)
```
```

---

## Quality Checks Before Finalizing

Before saving the files, verify:

- [ ] Every micro-task is specific and actionable (not vague like "implement feature")
- [ ] Phases are ordered by dependency — no phase assumes something from a later phase
- [ ] Every file in the "Files Affected" table has full implementation code
- [ ] ASCII diagrams are drawn for data flow AND module dependencies
- [ ] DB schema section is present if any tables are added or modified
- [ ] Implementation guide is in numbered order matching the phase dependency
- [ ] The approach section explains WHY, not just WHAT
- [ ] Scalability and fit sections address future extensibility
- [ ] Code follows project rules (type hints, two blank lines, guard clauses, no raw exceptions, etc.)

---

## Output Format Summary

```
.project_docs/
├── <task_name>.md                        # Task breakdown + micro-tasks
└── <task_name>_implementation_plan.md    # Full implementation blueprint
```

Naming convention: use `snake_case` for file names matching the task name.

Examples:
- `lead_scoring.md` + `lead_scoring_implementation_plan.md`
- `payments_integration.md` + `payments_integration_implementation_plan.md`
- `full_app_mvp.md` + `full_app_mvp_implementation_plan.md`
