---
name: planning
description: "**WORKFLOW SKILL** — Feature, task, and project planning with full implementation blueprints. USE FOR: planning a new feature, designing a new module, breaking down a large task into micro-tasks, writing implementation plans before coding, planning a division from project_divisions.md, understanding current codebase state before adding something new. DO NOT USE FOR: actually implementing code, debugging existing issues, reviewing code, or dividing a whole project (use project-division skill for that). PRODUCES: a task breakdown file in .sdlc/planning/ linked to per-phase implementation files in .sdlc/implementation/<feature>/ — all cross-linked so an agent handed either file can navigate to the other automatically."
argument-hint: "Describe what you want to plan (e.g., 'plan the payments feature', 'plan division 3', 'plan lead scoring task', 'plan the auth system')"
---

# Planning Skill

Produces a structured, professional planning output for any feature, task, or project division. Works with or without prior project division — you can plan a standalone feature or a specific division from `project_divisions.md`.

## When to Use

- Starting a new feature from scratch
- Planning a specific division from `project_divisions.md`
- Breaking down a large or ambiguous task before coding begins
- Understanding the current codebase state relative to what needs to be built
- Writing an implementation plan from a PRD or task description
- Ensuring new work fits the existing architecture
- Being assigned a feature or task on an existing project

## Deliverables

For every planning session, produce the following linked files:

| File | Purpose |
|------|---------|
| `.sdlc/planning/<task_name>.md` | Task breakdown — micro-tasks, phases, TODOs — each phase links directly to its implementation file |
| `.sdlc/implementation/<task_name>/<task_name>_phase_<N>_implementation.md` | One file per phase — deep implementation blueprint with code, diagrams, step-by-step guide — back-links to the task file |

### How the Files Link Together

The task file is the **navigator**: it contains high-level phases and TODOs. Each phase header includes a direct markdown link to that phase's dedicated implementation file in `.sdlc/implementation/<task_name>/`.

Each implementation file is the **detail layer** for one phase: it opens with a back-link to the task file and closes with a checklist mirroring the TODOs for that phase.

This means:
- Tell an agent *"implement Phase 2 from `.sdlc/planning/<task_name>.md`"* → it reads the phase, follows the link, gets all the code for that phase
- Tell an agent *"look at the Phase 2 implementation file"* → it sees the back-link and can find the task context

### Folder & Naming Convention

```
.sdlc/
├── CONTEXT.md                                             ← project context (read first)
├── rules/
│   └── code-craft.md                                      ← coding rules (checked before every plan)
├── planning/
│   ├── project_divisions.md                               ← division plan (if project was divided)
│   └── <task_name>.md                                     ← task breakdown file
├── implementation/
│   └── <task_name>/                                       ← one folder per feature / task
│       ├── <task_name>_phase_1_implementation.md
│       ├── <task_name>_phase_2_implementation.md
│       └── ...
├── qa/
│   └── <task_name>_qa_report.md                           ← QA report (written by qa-tester skill)
└── changelogs/
    └── changelog.md                                       ← single file, appended during the final QA phase
```

Naming: `snake_case` matching the task name.

Examples:
- Task file: `.sdlc/planning/lead_scoring.md`
- Implementation folder: `.sdlc/implementation/lead_scoring/`
- Phase files: `lead_scoring_phase_1_implementation.md`, `lead_scoring_phase_2_implementation.md`, …

---

## Step-by-Step Procedure

### Step 0 — Read Project Context & Changelogs

Before anything else, read the project context and history.

#### 0.1 Read CONTEXT.md

```bash
cat .sdlc/CONTEXT.md 2>/dev/null
```

**If it exists and has content:** Read it fully. Load the project name, tech stack, architecture, repo structure, and current state into context. This informs all planning decisions. Proceed to Step 0.2.

**If it does NOT exist or is empty — STOP and run context-init first:**

> ⚠️ CONTEXT.md is the foundation that ALL skills depend on (planning, QA, code-review, code-commit). Do NOT skip this.

1. Tell the user:
   ```
   📋 No project context found (`.sdlc/CONTEXT.md` is missing).
   
   I need to set up the project context first — this is a one-time setup that
   all SDLC skills depend on. Let me run through the context-init workflow.
   ```
2. **Find and read the context-init skill file.** It will be in the same skills directory as this planning skill (e.g., `context-init/SKILL.md`).
3. **Follow the context-init skill workflow completely** — this will create `.sdlc/CONTEXT.md` and `.sdlc/rules/code-craft.md`.
4. **After CONTEXT.md is created**, return here and continue from Step 0.2.

If for any reason you cannot find or read the context-init skill file, do a minimal fallback:
- Ask the user 3-5 critical questions (tech stack, project type, repo structure)
- Create a minimal `.sdlc/CONTEXT.md` with the answers
- Tell the user to run the full context-init skill later for a more complete setup

#### 0.2 Read Changelogs

```bash
cat .sdlc/changelogs/changelog.md 2>/dev/null
```

**If it exists:** Read it to understand what features have already been built. This prevents planning something that already exists and helps you understand the current application state.

#### 0.3 Check for Division Context

If the user referenced a division (e.g., "plan division 3"):

```bash
cat .sdlc/planning/project_divisions.md 2>/dev/null
```

Find the referenced division and extract its goal, scope, acceptance criteria, out of scope, and dependencies. Use this as the basis for planning.

**If no division was referenced:** the user is planning a standalone feature. Proceed normally.

---

### Step 0.5 — Gap Analysis & Clarification Questions

Before planning anything, analyze the request for missing information that would affect the implementation plan. Think like a senior engineer reviewing a ticket before estimation.

**Check for gaps in:**
- Which layer/module is affected (route, service, DB, frontend, etc.)?
- DB changes needed? Which table(s)?
- Auth/permission requirements?
- External integrations or third-party services?
- Error handling expectations?
- Testing requirements (unit, integration, e2e)?
- Specific framework/library constraints?
- Performance or scale considerations?
- Whether this extends existing code or is greenfield?
- Which repo(s) are affected (if multi-repo)?

**If gaps are found:**

1. Create the directory structure:
   ```
   .sdlc/planning/questions/
   ```
2. Write `.sdlc/planning/questions/planning_time_questions.md` using the exact MCQ format below
3. Tell the user to answer and confirm with `done` / `answered`
4. When confirmed, read the file and extract answers before proceeding to Step 1

**If no gaps are found:** skip this step entirely and proceed directly to Step 1.

#### MCQ File Format

```markdown
# Planning — Clarification Questions

Please answer the questions below by writing your choice in the `Answer:` field.
For option D (Other), write: `D: your specific answer`
When done, reply in the chat with **done** or **answered**.

---

## Q1: <Short question title>

**Question:** <Full question text?>

- A: <Option A>
- B: <Option B (Recommended)>
- C: <Option C>
- D: Other

**Answer:** <Write your answer here — e.g., A or D: my custom answer>

---

## Q2: <Short question title>

**Question:** <Full question text?>

- A: <Option A>
- B: <Option B>
- C: <Option C>
- D: Other

**Answer:** <Write your answer here>

---
```

**MCQ question rules:**
- Always provide 3–4 meaningful options — not just yes/no unless the choice is truly binary
- Mark one option `(Recommended)` when there is a clear best practice
- Only ask about genuine unknowns — never ask about things already stated or covered in CONTEXT.md
- Minimum 2 questions, maximum 15 — only what actually affects planning
- Blank / unfilled answers → treat as "use recommended option"

After writing the file, tell the user:
```
I found some gaps before I can plan this properly.

📋 I've written clarification questions to:
`.sdlc/planning/questions/planning_time_questions.md`

Please open that file, fill in the **Answer:** fields, save it, then reply with **done** or **answered** and I'll proceed with the full plan.
```

Then stop and wait. Do not proceed until confirmed.

---

### Step 1 — Code-Craft Rules Check

After gap questions are resolved (or skipped), and **before writing any plan**, check for the coding rules file:

```bash
cat .sdlc/rules/code-craft.md 2>/dev/null
```

There are three possible situations. Handle each exactly as follows:

---

#### Situation A — `code-craft.md` exists and has content

Read it fully. Load all rules into context. You will apply these rules to every code block and file recommendation written in the implementation plan. Proceed to Step 2 without pausing.

---

#### Situation B — No codebase exists (greenfield) AND `code-craft.md` is missing

1. Create the file empty:
   ```bash
   mkdir -p .sdlc/rules
   touch .sdlc/rules/code-craft.md
   ```
2. Tell the user:
   ```
   📋 No codebase was found and no coding rules file exists yet.

   I've created an empty rules file at:
   `.sdlc/rules/code-craft.md`

   Please open it, write your coding standards and conventions (language style,
   naming conventions, error handling rules, testing requirements, formatting
   preferences, etc.), save it, then reply with **done** and I'll proceed with
   the full plan.
   ```
3. Stop and wait. Do not proceed until the user confirms.
4. When confirmed, read the file and load all rules before continuing to Step 2.

---

#### Situation C — Codebase exists BUT `code-craft.md` is missing or empty

1. Read the existing codebase — scan representative files across all layers (routes, models, services, tests, configs, etc.)
2. Infer the coding rules actually being followed: naming conventions, file structure patterns, error handling style, type hint usage, import ordering, test patterns, formatting, etc.
3. Create `.sdlc/rules/code-craft.md` and populate it with the inferred rules in this format:

```markdown
# Code-Craft — Coding Rules & Conventions

> Auto-generated by the planning agent from codebase analysis. Review and edit as needed.

## Language & Runtime
- <e.g., Python 3.11+, strict type hints on all functions>

## Naming Conventions
- <e.g., snake_case for variables/functions, PascalCase for classes>

## File & Folder Structure
- <describe the actual project structure — NOT a prescribed one>

## Error Handling
- <e.g., guard clauses at top of function, no bare except, custom exception classes>

## Type Hints
- <e.g., all function signatures typed, Pydantic models for request/response>

## Imports
- <e.g., stdlib → third-party → local, one blank line between groups>

## Testing
- <e.g., pytest, one test file per module, fixtures in conftest.py>

## Formatting
- <e.g., black + isort, 88 char line limit, two blank lines between top-level defs>

## Other Conventions
- <anything else observed in the codebase>
```

4. Tell the user:
   ```
   🔍 I didn't find a code-craft rules file, so I analyzed your codebase and
   generated one based on the conventions I observed.

   📋 Please review it at:
   `.sdlc/rules/code-craft.md`

   Edit anything that looks wrong or add anything I missed, save it, then reply
   with **done** and I'll proceed with the full plan using these rules.
   ```
5. Stop and wait. Do not proceed until the user confirms.
6. When confirmed, re-read the file and load all rules before continuing to Step 2.

---

### Step 2 — Understand the Problem / Task

Read and restate the user's request in your own words before doing anything else.

- What is being asked to build or change?
- Is this a feature, a bug fix, a refactor, or a new project?
- What is the expected outcome for the end user?
- Are there constraints (performance, security, compatibility)?
- Which repo(s) are affected? (if multi-repo)

If a division was referenced, incorporate its goal, scope, and acceptance criteria.
If CONTEXT.md was read, use the project context to inform understanding.
If changelogs were read, note what's already built and how this fits.
If gap answers were collected, incorporate them fully here.

---

### Step 3 — Understand the Current State of the Codebase

If code already exists in the workspace:

1. **Read the project structure** — map out folders, modules, existing routes/models/services
2. **Identify what is already implemented** — list features, endpoints, DB tables, services that exist
3. **Identify what is partially implemented** — half-built features, stubs, TODOs
4. **Identify what is missing** — gaps between current state and what needs to be built
5. **Read relevant existing files** — any file that the new task will interact with or extend
6. **For multi-repo projects** — scan each affected repo separately

State this as a clear "Current State Summary" before planning.

---

### Step 4 — Create directory structure

```bash
mkdir -p .sdlc/planning
mkdir -p .sdlc/implementation/<task_name>
```

---

### Step 5 — Write the Task Breakdown File

Save to `.sdlc/planning/<task_name>.md`.

> **Linking rule:** Every phase heading must include a markdown link to that phase's dedicated implementation file inside `.sdlc/implementation/<task_name>/`.

```markdown
# <Task Name>

> 📋 Project context: [CONTEXT.md](../CONTEXT.md)
> 📋 Coding rules: [code-craft.md](../rules/code-craft.md)
> 📋 Division source: [project_divisions.md](project_divisions.md) — Division <N>  ← only if from a division

## Problem Statement
<One paragraph describing what needs to be built and why.>

## Current State
<Bullet list of what already exists and what is relevant to this task.>

## Goal
<What the application can do after this task is complete.>

## Out of Scope
<What is explicitly NOT included in this task.>

## Repos Affected
| Repo | Path | Changes |
|------|------|---------|
| <e.g., backend> | <./backend> | <New endpoints, models> |
| <e.g., frontend> | <./frontend> | <New pages, components> |

---

## Phases & Micro-Tasks

> 💡 Each phase title links to its dedicated implementation file (code, diagrams,
> step-by-step guide) inside `.sdlc/implementation/<task_name>/`.

---

### Phase 1 — <Phase Name> → [View Implementation](../implementation/<task_name>/<task_name>_phase_1_implementation.md)

- [ ] Task 1.1 — <specific, actionable item>
- [ ] Task 1.2 — <specific, actionable item>
- [ ] Task 1.3 — <specific, actionable item>
- [ ] Task 1.4 — Update `.sdlc/planning/<task_name>.md` and mark Phase 1 complete ✅

---

### Phase 2 — <Phase Name> → [View Implementation](../implementation/<task_name>/<task_name>_phase_2_implementation.md)

- [ ] Task 2.1 — <specific, actionable item>
- [ ] Task 2.2 — <specific, actionable item>
- [ ] Task 2.3 — Update `.sdlc/planning/<task_name>.md` and mark Phase 2 complete ✅

---

### Phase 3 — <Phase Name> → [View Implementation](../implementation/<task_name>/<task_name>_phase_3_implementation.md)

- [ ] Task 3.1 — <specific, actionable item>
- [ ] Task 3.2 — Update `.sdlc/planning/<task_name>.md` and mark Phase 3 complete ✅

---

### Phase <N+1> — QA, Review & Changelog → [View Implementation](../implementation/<task_name>/<task_name>_phase_<N+1>_implementation.md)

> This is the mandatory final phase for every feature. Run it after all implementation phases are complete.

- [ ] Task <N+1>.1 — Run the **QA skill** against the whole application as built so far — log all findings
- [ ] Task <N+1>.2 — Fix any issues surfaced by QA before marking the feature done
- [ ] Task <N+1>.3 — Append a changelog entry for this feature to `.sdlc/changelogs/changelog.md` (version, date, summary of changes, files affected)
- [ ] Task <N+1>.4 — Run the **code-commit** skill to commit on the feature branch
- [ ] Task <N+1>.5 — Update `.sdlc/planning/<task_name>.md` and mark Phase <N+1> complete ✅

---

## Acceptance Criteria
- [ ] <Measurable condition that proves the task is done>
- [ ] <Another condition>
- [ ] QA skill has been run and all findings resolved
- [ ] Changelog entry appended to `.sdlc/changelogs/changelog.md`
- [ ] Code committed on feature branch (not main/staging)

## Dependencies
- <Any external service, library, or prior task this depends on>
```

**Rules for micro-tasks:**
- Each micro-task should be completable in one focused dev session
- Name them as actions: "Create X", "Add Y to Z", "Update A to support B"
- Order them by dependency (can't write service before the model exists)
- Group into phases: typically Schema → Model → Migration → Service → Route → Tests (or whatever fits the project's structure per `code-craft.md`)
- **The last sub-task of every phase** (including the QA phase) must always be: *"Update `.sdlc/planning/<task_name>.md` and mark Phase N complete ✅"*
- **The final phase of every task** must always be the QA, Review & Changelog phase as shown above
- For multi-repo projects, note which repo each task applies to

---

### Step 6 — Write the Implementation Files (One Per Phase)

For **each phase** (including the QA phase), create a dedicated file:

```
.sdlc/implementation/<task_name>/<task_name>_phase_<N>_implementation.md
```

Each file follows this exact structure:

```markdown
# <Task Name> — Phase <N>: <Phase Name> — Implementation

> 📋 Task breakdown & all phases: [`<task_name>.md`](../../planning/<task_name>.md)
> 📋 Project context: [CONTEXT.md](../../CONTEXT.md)
> 📋 Coding rules: [code-craft.md](../../rules/code-craft.md)

---

## Phase <N> — <Phase Name>

> 🔗 Back to task: [Phase <N> TODOs](../../planning/<task_name>.md#phase-n--<phase-name-slugified>)

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

| Repo | File | Action | Reason |
|------|------|--------|--------|
| <repo> | `src/routes/item.py` | CREATE | New API endpoints for items |
| <repo> | `src/models/item.py` | CREATE | ORM model for items table |
| <repo> | `src/services/item.py` | CREATE | Business logic for item management |
| <repo> | `src/main.py` | EDIT | Register new router |

### ASCII Architecture Diagram

**Data Flow:**
```
Request
  │
  ▼
[Route: POST /v1/items/]
  │  delegates
  ▼
[Service: create_item()]
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
    └── services/item.py
            ├── repositories/item.py
            │       └── models/item.py
            └── utils/exceptions.py
```

### Code for Each File

#### `<repo>/src/models/item.py`
```<language>
# Full implementation code here
# Following rules from .sdlc/rules/code-craft.md
```

#### `<repo>/src/services/item.py`
```<language>
# Full implementation code here
```

### Step-by-Step Implementation Guide

1. Create `<repo>/src/models/item.py` with the model code above
2. Run database migration (if applicable)
3. Create `<repo>/src/services/item.py` with business logic
4. Create `<repo>/src/routes/item.py` and register in main app
5. Write tests in `<repo>/tests/item/test_item.py`
6. Run tests to verify all pass

### Phase <N> — TODO Mirror

> These mirror the TODOs in the task file. Check them off as you implement.

- [ ] Task N.1 — <same text as in task file>
- [ ] Task N.2 — <same text as in task file>
- [ ] Task N.X — Update `.sdlc/planning/<task_name>.md` and mark Phase <N> complete ✅

---
```

#### QA Phase Implementation File

The final phase implementation file (`<task_name>_phase_<N+1>_implementation.md`) has a slightly different structure:

```markdown
# <Task Name> — Phase <N+1>: QA, Review & Changelog — Implementation

> 📋 Task breakdown & all phases: [`<task_name>.md`](../../planning/<task_name>.md)

---

## Phase <N+1> — QA, Review & Changelog

> 🔗 Back to task: [Phase <N+1> TODOs](../../planning/<task_name>.md#phase-n1--qa-review--changelog)

### Summary
Final verification phase. Run the QA skill against the full application, resolve all findings, and record the feature in the changelog.

### QA Scope
- Full application as built through all implementation phases of this feature
- Any integration points with existing features
- Edge cases identified during planning
- Regression testing against all previously completed features

### QA Checklist
- [ ] Trigger the **QA skill** — pass it the full context of what was built in this feature
- [ ] Review all QA findings — categorize as: blocker / warning / nice-to-have
- [ ] Fix all blockers before proceeding
- [ ] Document warnings and nice-to-haves as follow-up tickets if not fixed now
- [ ] Verify the manual testing steps pass (from QA report)

### Changelog Entry

Append the following entry to `.sdlc/changelogs/changelog.md`:

```markdown
# Changelog — <Task Name>

**Date:** <YYYY-MM-DD>
**Version:** <semver or sprint label>
**Author:** <agent or developer name>

## Summary
<One paragraph describing what was built.>

## Changes
- <File or module> — <what changed>
- <File or module> — <what changed>

## QA Results
- Blockers found: <N> — all resolved
- Warnings: <list or "none">

## Related Files
- Task: `.sdlc/planning/<task_name>.md`
- Implementation: `.sdlc/implementation/<task_name>/`
- QA Report: `.sdlc/qa/<task_name>_qa_report.md`
```

### Code Commit

After QA passes and changelog is written:
- Use the **code-commit** skill to commit on the feature branch
- Never commit directly to main, master, staging, or develop

### Phase <N+1> — TODO Mirror

- [ ] Task <N+1>.1 — Run the **QA skill** against the whole application as built so far — log all findings
- [ ] Task <N+1>.2 — Fix any issues surfaced by QA before marking the feature done
- [ ] Task <N+1>.3 — Append a changelog entry for this feature to `.sdlc/changelogs/changelog.md`
- [ ] Task <N+1>.4 — Run the **code-commit** skill to commit on the feature branch
- [ ] Task <N+1>.5 — Update `.sdlc/planning/<task_name>.md` and mark Phase <N+1> complete ✅

---
```

---

### Database Schema Section (if DB is involved)

If the task involves database changes, include a dedicated section inside the relevant phase implementation file:

```markdown
### Database Schema

#### Table: `<table_name>`

| Column | Type | Constraints | Reason |
|--------|------|-------------|--------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid4 | Globally unique, not guessable |
| `name` | VARCHAR(255) | NOT NULL | Core identifier |
| `owner_id` | UUID | FK → users.id, NOT NULL | Ownership |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT now() | Audit trail |

#### Why This Schema
<Explain design decisions — UUID vs int, nullable choices, FK relationships, indexing strategy.>

#### Entity Relationship
```
users
  │
  │ 1:N
  ▼
items ──────── categories
```

#### Model Code
```<language>
# Full model code — following code-craft.md conventions
```

#### Migration Code
```<language>
# Full migration code (upgrade + downgrade)
```
```

---

## Quality Checks Before Finalizing

Before saving the files, verify:

- [ ] CONTEXT.md was checked — project context is loaded
- [ ] Changelogs were checked — previous features are known
- [ ] `code-craft.md` was checked — rules are loaded and applied to all code in implementation files
- [ ] Every phase in the task file has a `→ [View Implementation](...)` link pointing to the correct phase file in `.sdlc/implementation/<task_name>/`
- [ ] Every phase implementation file opens with a `📋` back-link to the task file and a `🔗` back-link to the correct phase anchor
- [ ] Every phase implementation file closes with a `TODO Mirror` checklist matching the task file
- [ ] The last sub-task of **every** phase is "Update task file and mark phase complete ✅"
- [ ] The **final phase** is always the QA, Review & Changelog phase
- [ ] The anchor slugs in all links are correct (lowercase, spaces → `-`, `—` → `--`)
- [ ] Every micro-task is specific and actionable
- [ ] Phases are ordered by dependency — no phase assumes something from a later phase
- [ ] Every file in "Files Affected" has full implementation code
- [ ] The "Repo" column in "Files Affected" is filled in (even for single-repo projects — just use the project name or `.`)
- [ ] ASCII diagrams are present for data flow AND module dependencies in each phase file
- [ ] DB schema section is present if any tables are added or modified
- [ ] The approach section explains WHY, not just WHAT
- [ ] Code follows the rules in `.sdlc/rules/code-craft.md`
- [ ] If from a division, the acceptance criteria from the division are included

---

## Output Format Summary

```
.sdlc/
├── CONTEXT.md                                          ← read before planning
├── rules/
│   └── code-craft.md                                   ← created/verified before planning
├── planning/
│   ├── questions/
│   │   └── planning_time_questions.md                  ← only if gaps were found
│   ├── project_divisions.md                            ← checked if planning a division
│   └── <task_name>.md                                  ← task breakdown, links → impl files
├── implementation/
│   └── <task_name>/                                    ← one folder per feature
│       ├── <task_name>_phase_1_implementation.md
│       ├── <task_name>_phase_2_implementation.md
│       ├── ...
│       └── <task_name>_phase_<N+1>_implementation.md   ← always the QA phase
├── qa/
│   └── <task_name>_qa_report.md                        ← written by QA skill during final phase
└── changelogs/
    └── changelog.md                                    ← entry appended during QA phase
```

---

## How an Agent Should Use These Files

When an agent is handed the **task file** and told "implement Phase 2":
1. Read Phase 2 TODOs in the task file
2. Follow the `→ [View Implementation]` link to `.sdlc/implementation/<task_name>/<task_name>_phase_2_implementation.md`
3. Read the code, diagrams, and step-by-step guide in that file
4. Implement, then check off TODOs in both the task file and the phase implementation file
5. Complete the final sub-task: mark the phase complete in the task file

When an agent is handed the **task file** and told "run the final QA phase":
1. Open the last phase in the task file (the QA phase)
2. Follow its link to the QA implementation file
3. Trigger the QA skill, fix blockers, write the changelog entry
4. Use the code-commit skill to commit on the feature branch
5. Mark the QA phase complete in the task file

When an agent is handed an **implementation file** directly:
1. Read the top-level `📋` back-link to find the task file for full context
2. Use the `🔗` back-link to jump to the correct phase TODOs in the task file
3. Use the TODO Mirror at the end of the file to track progress