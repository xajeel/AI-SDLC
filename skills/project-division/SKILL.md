---
name: project-division
description: >
  **PROJECT DIVISION SKILL** — Breaks a full project into implementable development divisions. USE THIS SKILL when a user provides a project PRD, project brief, or project description and wants it divided into tasks. Trigger when the user says "divide this project", "break down this PRD", "split into tasks", "plan this project", "create a development plan", "divide into features", "break this into stories", or shares a full project description. DO NOT USE when the user already knows what feature to build — they should use the planning skill directly. This skill is for WHOLE PROJECT breakdown, not individual feature planning. Reads `.sdlc/CONTEXT.md` if it exists for project context. Handles multi-repo projects (backend + frontend in separate repos). Produces a clean feature-by-feature division that any developer or AI agent can implement.
argument-hint: "Provide the PRD or project description to divide (e.g., 'divide this project', 'break down this PRD into tasks')"
---

# Project Division Skill

A professional SDLC planning skill that takes a project PRD or description, identifies information gaps, collects answers via structured MCQ files, then produces a clean feature-by-feature project division that any developer or AI agent can implement.

> **When NOT to use this skill:** If you already know what feature or task you need to build, skip this and go directly to the **planning** skill. This skill is for dividing a _whole project_ into chunks — not for planning a single feature.

---

## Workflow Overview

```
Check for .sdlc/CONTEXT.md (read if exists)
        ↓
Input (PRD or Description)
        ↓
  Gap Analysis
        ↓
  Write MCQ Questions → .sdlc/planning/questions/division_time_questions.md
        ↓
  Tell user to answer & confirm with "done"/"answered"
        ↓
  Read answers from file
        ↓
  Generate Project Division → .sdlc/planning/project_divisions.md
```

---

## Phase 0: Read Existing Context

### 0.1 Check for CONTEXT.md

Before anything else, check if project context has been initialized:

```bash
cat .sdlc/CONTEXT.md 2>/dev/null
```

**If it exists and has content:** Read it fully. Extract project name, tech stack, architecture, repo structure, and current state. Use this information to skip questions the context already answers. Proceed to Phase 0.2.

**If it does NOT exist or is empty — STOP and run context-init first:**

> ⚠️ CONTEXT.md is the foundation that ALL skills depend on (planning, QA, code-review, code-commit). Do NOT skip this.

1. Tell the user:
   ```
   📋 No project context found (`.sdlc/CONTEXT.md` is missing).
   
   I need to set up the project context first — this is a one-time setup that
   all SDLC skills depend on. Let me run through the context-init workflow.
   ```
2. **Find and read the context-init skill file.** It will be in the same skills directory as this skill (e.g., `context-init/SKILL.md`).
3. **Follow the context-init skill workflow completely** — this will create `.sdlc/CONTEXT.md` and `.sdlc/rules/code-craft.md`.
4. **After CONTEXT.md is created**, return here and continue from Phase 0.2.

If for any reason you cannot find or read the context-init skill file, do a minimal fallback:
- Ask the user 3-5 critical questions (tech stack, project type, repo structure)
- Create a minimal `.sdlc/CONTEXT.md` with the answers
- Tell the user to run the full context-init skill later for a more complete setup

### 0.2 Check for Code-Craft Rules

```bash
cat .sdlc/rules/code-craft.md 2>/dev/null
```

If it exists, note the coding conventions. These won't affect division directly but inform how granular to make tasks.

---

## Phase 1: Ingest & Gap Analysis

### 1.1 Accept Input

Accept either:
- A pasted PRD / project description in the chat
- An uploaded `.md`, `.txt`, `.pdf`, or `.docx` file (read it first)
- A reference to CONTEXT.md ("use the context file")

Parse and extract what is known:
- Project goal / purpose
- Target users / audience
- Core features mentioned
- Tech stack (language, framework, DB, infra, etc.)
- Constraints (deadlines, team size, budget hints)
- Non-functional requirements (auth, performance, security, scale)
- Integration needs (APIs, third-party services)
- Deployment target (cloud, on-prem, mobile, web, CLI, etc.)

**If CONTEXT.md was read:** Cross-reference — don't ask about things already covered in the context file.

### 1.2 Identify Gaps

Think like a senior engineer preparing to hand work to a team. Ask yourself:

**Tech Stack Gaps**
- Language / runtime specified? Version?
- Package manager specified? (pip/uv/poetry for Python; npm/yarn/pnpm for JS; cargo for Rust; etc.)
- Framework specified? (FastAPI, Django, Express, Next.js, etc.)
- Database type? (SQL vs NoSQL) Which one?
- ORM / query layer?
- Frontend framework (if applicable)?
- State management approach?
- CSS / styling approach?

**Architecture Gaps**
- Monolith vs microservices vs serverless?
- REST vs GraphQL vs gRPC?
- Sync vs async processing?
- Queue/broker needed? (RabbitMQ, Redis, Kafka)
- Caching layer needed?

**Auth & Security Gaps**
- Authentication method? (JWT, sessions, OAuth, API keys, passkeys)
- Authorization model? (RBAC, ABAC, simple roles)
- Multi-tenancy?

**Deployment & Infrastructure Gaps**
- Deployment target? (AWS, GCP, Azure, VPS, local, Docker, k8s)
- CI/CD needed? Which platform?
- Environment strategy? (dev/staging/prod)
- Container strategy?

**Data & Storage Gaps**
- File storage? (local, S3, GCS)
- Media/upload handling?
- Data migration / seeding strategy?

**Testing Gaps**
- Testing approach? (unit, integration, e2e)
- Testing framework preference?
- Coverage requirements?

**Repository Gaps**
- Single repo or multiple repos?
- If multi-repo: which repos, what goes where?

**Team / Process Gaps**
- Solo dev or team?
- AI-assisted implementation or human devs?
- Preferred granularity of tasks? (hours, days)

**Frontend Gaps**
- Frontend Info is present or not
- Any UI design Info or requirements
- Frontend layout

> ⚠️ Do NOT ask about things already clearly stated in the PRD or CONTEXT.md. Only ask about genuine gaps.

---

## Phase 2: Write MCQ Questions File

### 2.1 Create Directory Structure

```bash
mkdir -p .sdlc/planning/questions
```

Create (or overwrite) the file:
```
.sdlc/planning/questions/division_time_questions.md
```

### 2.2 File Format

Use EXACTLY this format for every question. No deviations.

```markdown
# Project Division — Clarification Questions

Please answer the questions below by writing your choice in the `Answer:` field.
For option D (Other), write: `D: your specific answer`
When done, reply in the chat with **done** or **answered**.

---

## Q1: <Short question title>

**Question:** <Full question text?>

- A: <Option A>
- B: <Option B (Recommended)>  ← mark recommended if applicable
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

### 2.3 Question Writing Rules

- **Always provide 3-4 meaningful options** — not just "yes/no" unless binary choice is truly the only option
- **Mark one option as (Recommended)** when there is a clear best practice
- **Order options** from most common/simple → most complex → Other
- **Be specific** — instead of "Which database?" write "Which database system will you use for primary data storage?"
- **Group related questions** — all Python tooling questions together, all auth questions together, etc.
- **Minimum 5 questions, maximum 20** — only what's truly needed
- Include a brief one-line **context comment** before options if the question needs it

### 2.4 Question Categories & Examples

**Package Manager Example:**
```markdown
## Q1: Python Package Manager

**Question:** Which Python package manager should be used for this project?

- A: pip (standard, widely supported)
- B: uv (Recommended — fast, modern, Rust-based)
- C: poetry (great for packaging and publishing)
- D: Other

**Answer:** <Write your answer here>
```

**Database Example:**
```markdown
## Q2: Primary Database

**Question:** Which database will serve as the primary data store?

- A: PostgreSQL (Recommended — robust, feature-rich SQL)
- B: MySQL / MariaDB
- C: SQLite (good for local/single-user apps)
- D: Other (e.g., MongoDB, DynamoDB)

**Answer:** <Write your answer here>
```

**Repository Structure Example:**
```markdown
## Q5: Repository Structure

**Question:** How is the codebase organized?

- A: Single repository — everything in one repo (Recommended for smaller projects)
- B: Multi-repo — separate repos for backend, frontend, etc.
- C: Monorepo with workspaces (e.g., Nx, Turborepo, pnpm workspaces)
- D: Other

**Answer:** <Write your answer here>
```

---

## Phase 3: Notify User

After writing the questions file, tell the user:

```
I've analyzed your project and identified [N] clarification questions that will help me divide it properly.

📋 I've written them to:
`.sdlc/planning/questions/division_time_questions.md`

Please open that file, fill in the **Answer:** fields for each question, save it, then come back here and reply with **done** or **answered** — and I'll generate your full project division plan.
```

Then **stop and wait**. Do not proceed until the user confirms.

---

## Phase 4: Read Answers & Generate Division

### 4.1 Triggered By

When user says: `done`, `answered`, `finished`, `I've answered`, or similar confirmation.

### 4.2 Read the Answers File

Read `.sdlc/planning/questions/division_time_questions.md` and extract every `Answer:` field. Map each answer back to its question context. Handle:
- Single letter answers: `A` → pick that option's text
- `D: custom text` → use the custom text
- Blank or `<Write your answer here>` → treat as "no preference, use recommended"

### 4.3 Synthesize Full Project Context

Combine:
- CONTEXT.md (if it exists)
- Original PRD / project description
- All extracted answers
- Your own professional engineering judgment for anything still unclear

---

## Phase 5: Generate Project Divisions

### 5.1 Division Philosophy

Divide the project the way a **Staff Engineer** would divide it for a team of developers or AI agents:

- **Feature-complete chunks** — each division implements one meaningful feature end-to-end
- **Independently testable** — each chunk can be verified without other chunks being done
- **Logically ordered** — chunks build on each other in the right sequence (infra before features, auth before protected routes, etc.)
- **Right-sized** — not too big ("build the whole backend"), not too small ("add one button"); aim for 1–3 days of focused work per division
- **Clear boundaries** — each chunk has a single clear responsibility
- **Complete Description** — Complete description of the chunk including the info about overall project and how & where this chunk fits in the project. Also explain the flow.
- **Multi-repo aware** — if the project has multiple repos, tag each division with which repo(s) it affects

Each chunk should be self-explanatory and a developer should be able to understand all the requirements of the chunk (division). It should be an explanatory portion.

### 5.2 Division Structure

Group divisions into **phases**. Typical phase flow:

```
Phase 0 — Project Setup & Infrastructure
Phase 1 — Data Layer & Core Models
Phase 2 — Authentication & Authorization
Phase 3 — Core Features (one division per major feature)
Phase 4 — Supporting Features & Integrations
Phase 5 — Frontend / UI (if applicable)
Phase 6 — Testing, Polish & Deployment
```

Adjust phases based on the actual project. Not every project needs all phases.

### 5.3 Output File Format

Write to `.sdlc/planning/project_divisions.md` using this format:

```markdown
# Project Division Plan
**Project:** <Project Name>
**Generated:** <Date>
**Total Divisions:** <N>
**Context File:** `.sdlc/CONTEXT.md`

---

## Overview

<2-3 sentence summary of the project and the division strategy chosen>

### Tech Stack
- **Language:** ...
- **Framework:** ...
- **Database:** ...
- **Package Manager:** ...
- **Auth:** ...
- **Deployment:** ...
- *(add/remove rows as needed)*

### Repository Structure
| Repo | Path | Purpose |
|------|------|---------|
| <e.g., backend> | <./backend> | <API server> |
| <e.g., frontend> | <./frontend> | <Web UI> |

---

## Division Map

> Read top-to-bottom. Each division depends on all prior divisions being complete.

| # | Division | Phase | Repo(s) | Key Deliverable | Testable Via |
|---|----------|-------|---------|-----------------|--------------|
| 1 | Project Setup | Setup | all | Runnable skeleton | App starts, health check passes |
| 2 | Database Schema | Data Layer | backend | All models defined | Migrations run, tables exist |
| ... | | | | | |

---

## Divisions

---

### Division 1 — Project Setup & Skeleton

**Phase:** Setup
**Repo(s):** all
**Goal:** Create a working, runnable project skeleton with all tooling configured.
**Description:** <two to 3 lines project summary> <Chunk explanation and flow>

**Scope:**
- Initialize project with chosen package manager
- Set up directory structure following [framework] conventions
- Configure linting, formatting (e.g., ruff, eslint, prettier)
- Environment variable management (.env, config loader)
- Basic health-check / ping endpoint or entry point
- README with setup instructions
- Git initialization + .gitignore

**Out of Scope:** No business logic, no DB, no auth

**Acceptance Criteria:**
- [ ] Project installs cleanly from scratch with one command
- [ ] Linter passes with zero errors
- [ ] Health check returns 200 OK (or app starts without error)
- [ ] README documents how to run locally

**Dependencies:** None

---

### Division 2 — <Name>

**Phase:** <Phase Name>
**Repo(s):** <which repos are affected — e.g., backend, frontend, or all>
**Goal:** <One-sentence goal>
**Description:** <two to 3 lines project summary> <Chunk explanation and flow>

**Scope:**
- <bullet 1>
- <bullet 2>
- ...

**Out of Scope:** <what explicitly is NOT included>

**Acceptance Criteria:**
- [ ] <Verifiable criterion 1>
- [ ] <Verifiable criterion 2>
- [ ] <Verifiable criterion 3>

**Dependencies:** Division <N>

---

*(repeat for all divisions)*

---

## Implementation Order

```
Division 1 → Division 2 → Division 3
                       ↓
                  Division 4 → Division 5
```
*(draw the actual dependency graph for the project)*

---

## Notes for Implementers

- <Any important architectural decision or gotcha>
- <Any division that could be done in parallel with another>
- <Any external dependency that needs to be set up first (API keys, cloud accounts, etc.)>
- For each division, use the **planning** skill to create a detailed implementation plan before coding
- After implementing each division, use the **qa-tester** skill to verify and run regression tests
- Use the **code-commit** skill to commit — always on a feature branch, never on main/staging
```

### 5.4 Division Writing Rules

- **Every division must have acceptance criteria** — without them, no one knows when it's done
- **"Out of Scope" is mandatory** — prevents scope creep per division
- **Dependencies must be explicit** — "Division 3" not "the auth stuff"
- **Goal is one sentence** — if you can't say it in one sentence, split the division
- **Acceptance criteria must be verifiable** — "works correctly" is not a criterion; "returns 401 for unauthenticated requests" is
- **Order matters** — write them in the order they should be implemented
- **Repo(s) must be specified** — for multi-repo projects, every division must say which repos it touches
- **Mention test cases** — each division should note what tests to write

---

## Phase 6: Notify Completion

After writing the file, tell the user:

```
✅ Project division complete!

I've broken your project into [N] divisions across [M] phases, saved to:
`.sdlc/planning/project_divisions.md`

Here's a quick summary:

**Phase 0 — Setup:** Division 1 (Project skeleton)
**Phase 1 — Data Layer:** Divisions 2–3 (Models, migrations)
...

Each division is independently testable and includes clear acceptance criteria.

🚀 Next steps:
  - Pick a division and use the **planning** skill to plan it in detail
  - Or jump straight to implementing Division 1

Ready to start? Pick Division 1 and let's go! 🚀
```

---

## Edge Cases

| Situation | Handling |
|-----------|----------|
| PRD is very detailed, no gaps | Ask only 2–3 truly essential questions (e.g., deployment target) |
| PRD is just one sentence | Ask more questions (up to 20), extract everything needed |
| User says "skip questions, just divide" | Use your best-practice defaults, note assumptions at top of divisions file |
| User answers "D: Other" with something unusual | Incorporate their choice faithfully |
| User wants a specific number of divisions | Honor it, adjust granularity accordingly |
| Project is very small (< 1 week) | Fewer divisions (3–6), still follow format |
| Project is large (> 3 months) | More divisions (15–25+), consider suggesting sub-phases |
| CONTEXT.md exists | Read it first, skip questions it already answers |
| Multi-repo project | Tag every division with affected repo(s) |

---

## Quality Checklist (self-check before saving)

Before writing the final `project_divisions.md`, verify:

- [ ] Divisions cover the ENTIRE project scope — nothing is missing
- [ ] Division 1 is always "Project Setup"
- [ ] Auth always comes before any protected feature
- [ ] DB/schema division always comes before any feature that uses data
- [ ] Every division has at least 3 acceptance criteria
- [ ] Every division has an explicit "Out of Scope" section
- [ ] Every division has "Repo(s)" specified (even for single-repo projects)
- [ ] The implementation order makes logical sense
- [ ] No division is so large it would take > 3–4 days
- [ ] No division is so small it's trivial (< 2 hours)
- [ ] Parallel opportunities are noted in the Notes section
- [ ] Mention to write each chunk/division test cases
- [ ] CONTEXT.md was checked and referenced (if it exists)
