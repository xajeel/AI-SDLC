---
name: context-init
description: >
  **PROJECT CONTEXT SKILL** — Initializes project context for all other SDLC skills. USE THIS SKILL when starting work on any project for the first time, when a user provides a PRD or project description, when the user says "set up the project", "initialize context", "understand this project", "here's the PRD", "start working on this", "explain this codebase", or when `.sdlc/CONTEXT.md` does not exist yet. This skill creates the `.sdlc/CONTEXT.md` file that ALL other skills (planning, QA, code-review, code-commit) rely on. It supports three modes: parsing an existing PRD/doc, asking the user questions, or analyzing the existing codebase. Also creates `.sdlc/rules/code-craft.md` if a codebase exists. DO NOT USE FOR: actually planning features (use planning skill), dividing a project (use project-division skill), or implementing code.
argument-hint: "Provide a PRD, project description, or say 'analyze the codebase' (e.g., 'here is the PRD for our app', 'set up context for this project', 'understand this codebase')"
---

# Context Init Skill

Creates the foundational project context file (`.sdlc/CONTEXT.md`) that all other SDLC skills depend on. This is always the **first skill** to run on any project.

## What This Skill Does

1. **Determines how to gather context** — PRD provided, ask questions, or analyze codebase
2. **Collects all project information** — tech stack, architecture, repos, conventions
3. **Creates `.sdlc/CONTEXT.md`** — the single source of truth for the project
4. **Creates `.sdlc/rules/code-craft.md`** — coding rules (inferred from codebase or user-provided)
5. **Detects multi-repo setups** — maps all repos in the workspace

---

## When to Use

- First time working on a project
- `.sdlc/CONTEXT.md` does not exist
- User provides a new PRD or project description
- User asks to understand or analyze a codebase
- Project scope has changed significantly and context needs updating

---

## Workflow

```
User invokes context-init
        │
        ▼
  Check if .sdlc/CONTEXT.md already exists
        │
        ├── EXISTS → Ask: "Update existing context or start fresh?"
        │
        └── DOES NOT EXIST → Continue
                │
                ▼
  "How would you like to provide project context?"
        │
        ├── Option A: "I have a PRD / project document"
        │       → Read the document
        │       → Extract project info
        │       → Ask clarifying questions if gaps exist
        │       → Generate CONTEXT.md + code-craft.md
        │
        ├── Option B: "I'll answer questions"
        │       → Write MCQ questions file
        │       → Wait for answers
        │       → Generate CONTEXT.md + code-craft.md
        │
        └── Option C: "Understand from the codebase"
                → Scan full codebase
                → Infer project details, architecture, stack
                → Generate CONTEXT.md + code-craft.md
                → Ask user to review and confirm
```

---

## Phase 0 — Check Existing Context

### 0.1 Check for existing CONTEXT.md

```bash
cat .sdlc/CONTEXT.md 2>/dev/null
```

**If it exists and has content:**

Tell the user:
```
📋 I found an existing project context at `.sdlc/CONTEXT.md`.

Would you like to:
A) Update it with new information (keeps existing, adds/modifies)
B) Start fresh (replaces everything)
C) Cancel — the current context is fine

Reply with A, B, or C.
```

Wait for response. If A → read existing context, then proceed with whatever mode the user wants. If B → proceed fresh. If C → stop.

**If it does not exist:** proceed to Phase 1.

---

## Phase 1 — Determine Context Source

If the user provided a PRD or document in the chat → go to **Phase 2A** (Parse PRD).

If the user said "understand the codebase" or similar → go to **Phase 2C** (Analyze Codebase).

Otherwise, ask:

```
How would you like to provide project context?

A) I have a PRD or project document — paste it or tell me where the file is
B) I'll answer questions — I'll ask you about the project
C) Analyze the codebase — I'll read the existing code and infer the project details

Reply with A, B, or C.
```

Wait for response. Route to the appropriate phase.

---

## Phase 2A — Parse PRD / Project Document

### 2A.1 Read the Document

Accept:
- Pasted text in the chat
- File path (`.md`, `.txt`, `.pdf`, `.docx`)
- URL to a document

Read it fully. Extract everything available:
- Project name and description
- Target users / audience
- Core features
- Tech stack
- Architecture decisions
- Non-functional requirements
- External integrations
- Deployment targets
- Team structure

### 2A.2 Gap Analysis

After reading the PRD, identify what's **missing** that would be needed for planning and implementation. Check for:

- Tech stack gaps (language, framework, DB, package manager)
- Architecture gaps (monolith vs micro, API style)
- Auth strategy
- Deployment target
- Testing approach
- Repository structure (mono vs multi-repo)

**If gaps exist:** write MCQ questions → Phase 2B.2

**If no gaps:** proceed to Phase 3 (Detect Repos).

---

## Phase 2B — Ask Questions

### 2B.1 Write MCQ Questions File

```bash
mkdir -p .sdlc/planning/questions
```

Write `.sdlc/planning/questions/context_init_questions.md` using this exact format:

```markdown
# Project Context — Clarification Questions

Please answer the questions below by writing your choice in the `Answer:` field.
For option D (Other), write: `D: your specific answer`
When done, reply in the chat with **done** or **answered**.

---

## Q1: Project Type

**Question:** What type of application are you building?

- A: Web application (frontend + backend)
- B: REST API / backend service only
- C: CLI tool / script
- D: Other

**Answer:** <Write your answer here>

---

## Q2: Primary Language

**Question:** What is the primary programming language for this project?

- A: Python
- B: JavaScript / TypeScript
- C: Go
- D: Other

**Answer:** <Write your answer here>

---
```

### 2B.2 Question Categories

Include questions about:

**Core Project:**
- Project type (web app, API, CLI, mobile, library)
- Primary language and version
- Framework (if applicable)
- Package manager

**Data Layer:**
- Database type and system
- ORM / query layer
- File storage needs

**Architecture:**
- Monolith vs microservices
- API style (REST, GraphQL, gRPC)
- Sync vs async

**Auth & Security:**
- Authentication method
- Authorization model
- Multi-tenancy needs

**Infrastructure:**
- Deployment target
- CI/CD platform
- Container strategy

**Repository:**
- Single repo or multiple repos
- If multiple: what repos and their purposes

**Testing:**
- Testing framework
- Coverage requirements

**Question rules:**
- Minimum 5, maximum 20 questions
- Only ask about genuine unknowns
- Mark one option `(Recommended)` when there's a clear best practice
- Blank answers → use recommended option

### 2B.3 Notify User

```
I need some information about your project to set up the context properly.

📋 I've written clarification questions to:
`.sdlc/planning/questions/context_init_questions.md`

Please open that file, fill in the **Answer:** fields, save it, then reply with **done** or **answered**.
```

**Stop and wait.** Do not proceed until confirmed.

### 2B.4 Read Answers

When user confirms, read the file and extract all answers. Map each answer back to its question. Handle:
- Single letter: `A` → pick that option's text
- `D: custom text` → use custom text
- Blank → use recommended option

Proceed to Phase 3.

---

## Phase 2C — Analyze Existing Codebase

### 2C.1 Scan Project Structure

```bash
find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.go" -o -name "*.rs" -o -name "*.java" -o -name "*.rb" -o -name "*.php" -o -name "*.cs" \) \
  | grep -v node_modules | grep -v .venv | grep -v __pycache__ | grep -v target | grep -v .git | grep -v dist | grep -v build | head -200
```

Build a mental map of the project.

### 2C.2 Detect Tech Stack

Look for these config files and extract information:

| File | Tells You |
|------|-----------|
| `package.json` | Node.js project, dependencies, scripts |
| `pyproject.toml` | Python project, dependencies, tools |
| `requirements.txt` | Python dependencies |
| `go.mod` | Go project, module name |
| `Cargo.toml` | Rust project |
| `pom.xml` / `build.gradle` | Java/Kotlin project |
| `Gemfile` | Ruby project |
| `composer.json` | PHP project |
| `docker-compose.yml` | Services, databases, infrastructure |
| `.env.example` / `.env.sample` | Environment variables needed |
| `Makefile` | Build/run commands |
| `Dockerfile` | Container setup |
| `alembic.ini` | Database migrations (Python/SQLAlchemy) |
| `prisma/schema.prisma` | Database schema (Node.js/Prisma) |
| `tsconfig.json` | TypeScript configuration |

### 2C.3 Read Key Files

Read the following (if they exist):
- README.md
- Entry point files (main.py, index.ts, main.go, etc.)
- Configuration files
- Database model files (first 3-5)
- Route/controller files (first 3-5)
- Test files (first 2-3)

### 2C.4 Infer Architecture

From the files read, determine:
- Layer structure (routes → services → models, MVC, etc.)
- Naming conventions
- Error handling patterns
- Import ordering
- Testing patterns
- Code style

### 2C.5 Present Findings

Before writing CONTEXT.md, show the user what you found:

```
🔍 Here's what I found in your codebase:

**Project:** <inferred name>
**Type:** <web app / API / CLI / etc.>
**Stack:** <language + framework + DB>
**Architecture:** <layered / MVC / microservices / etc.>
**Repos detected:** <1 or N>

Does this look right? Reply **yes** to proceed, or correct anything that's wrong.
```

Wait for confirmation. Then proceed to Phase 3.

---

## Phase 3 — Detect Repository Structure

### 3.1 Check for Multiple Repos

Look for multiple project roots in the workspace:

```bash
# Check for multiple package files at different levels
find . -maxdepth 3 -name "package.json" -o -name "pyproject.toml" -o -name "go.mod" -o -name "Cargo.toml" -o -name "pom.xml" -o -name "Gemfile" -o -name "composer.json" | grep -v node_modules | grep -v .venv
```

Also check for:
- Multiple `git` directories (submodules or separate repos)
- Common multi-repo patterns: `backend/`, `frontend/`, `services/`, `packages/`
- Monorepo tools: `lerna.json`, `pnpm-workspace.yaml`, `nx.json`, `turbo.json`

### 3.2 Classify Repository Structure

| Pattern | Classification |
|---------|---------------|
| Single `package.json` / `pyproject.toml` at root | **Single repo** |
| `backend/pyproject.toml` + `frontend/package.json` | **Multi-repo** (2 repos) |
| `lerna.json` / `pnpm-workspace.yaml` at root | **Monorepo** (with packages) |
| Multiple service folders with their own configs | **Multi-service** |

Record the repos found:

```
Repos detected:
  1. backend/  → Python (FastAPI)
  2. frontend/ → TypeScript (Next.js)
```

Or:

```
Repos detected:
  1. ./  → Single repo (Python, FastAPI)
```

---

## Phase 4 — Generate `.sdlc/rules/code-craft.md`

### 4.1 If Codebase Exists

Read representative files from the codebase and infer coding rules. Create:

```bash
mkdir -p .sdlc/rules
```

Write `.sdlc/rules/code-craft.md`:

```markdown
# Code-Craft — Coding Rules & Conventions

> Auto-generated by context-init from codebase analysis. Review and edit as needed.

## Language & Runtime
- <e.g., Python 3.11+, strict type hints on all functions>

## Naming Conventions
- <e.g., snake_case for variables/functions, PascalCase for classes>

## File & Folder Structure
- <describe the actual project structure observed>
- <e.g., src/routes/ → src/services/ → src/models/ layering>

## Error Handling
- <e.g., guard clauses at top of function, no bare except, custom exception classes>

## Type Hints / Types
- <e.g., all function signatures typed, Pydantic models for request/response>

## Imports
- <e.g., stdlib → third-party → local, one blank line between groups>

## Testing
- <e.g., pytest, one test file per module, fixtures in conftest.py>

## Formatting
- <e.g., black + isort, 88 char line limit>

## Other Conventions
- <anything else observed>
```

### 4.2 If No Codebase Exists (Greenfield)

Create an empty `code-craft.md` and tell the user:

```
📋 No codebase found — this is a greenfield project.

I've created an empty coding rules file at:
`.sdlc/rules/code-craft.md`

Please open it and write your coding standards (naming, style, patterns, testing rules, etc.).
Save it and reply **done** — these rules will guide all planning and code review.

If you're unsure what to write, just reply **skip** and I'll fill in sensible defaults when we start planning.
```

---

## Phase 5 — Generate `.sdlc/CONTEXT.md`

### 5.1 Create Directory Structure

```bash
mkdir -p .sdlc/changelogs
mkdir -p .sdlc/planning
mkdir -p .sdlc/qa
```

### 5.2 Write CONTEXT.md

Save to `.sdlc/CONTEXT.md` using this exact format:

```markdown
# Project Context

> Generated by context-init skill. This file is read by all SDLC skills.
> Update it when the project scope changes significantly.

---

## Project Name
<project name>

## Description
<2-3 sentence description of what the project does, in plain English>

## Project Type
<web application / REST API / CLI tool / mobile app / library / monorepo / etc.>

## Target Users
<who uses this application>

---

## Tech Stack

| Technology | Role | Version |
|------------|------|---------|
| <e.g., Python> | <Backend language> | <3.11+> |
| <e.g., FastAPI> | <Web framework> | <0.100+> |
| <e.g., PostgreSQL> | <Primary database> | <15> |
| <e.g., React> | <Frontend framework> | <18> |
| <e.g., uv> | <Package manager> | <latest> |

---

## Repository Structure

| Repo | Path | Purpose | Tech |
|------|------|---------|------|
| <e.g., backend> | <./backend> | <API server> | <Python/FastAPI> |
| <e.g., frontend> | <./frontend> | <Web UI> | <TypeScript/React> |

> **Type:** <single-repo / multi-repo / monorepo>

---

## Architecture

<Describe the high-level architecture in 3-5 sentences>

### Layer Structure
<Describe how code is organized — e.g., routes → services → repositories → models>

### Data Flow
```
<ASCII diagram showing how a request flows through the system>
```

---

## Key Features (Current State)

- <Feature 1 — brief description, status: implemented / partial / planned>
- <Feature 2>
- ...

---

## External Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| <e.g., Stripe API> | <Payment processing> | <Yes> |
| <e.g., SendGrid> | <Email delivery> | <No — optional> |

---

## Environment & Infrastructure

- **Deployment:** <e.g., Docker on AWS ECS / Vercel / Railway / local only>
- **CI/CD:** <e.g., GitHub Actions / GitLab CI / none>
- **Environments:** <e.g., dev / staging / production>

---

## Coding Rules

> Full coding rules are in `.sdlc/rules/code-craft.md`

Key conventions summary:
- <e.g., snake_case everywhere, PascalCase for classes>
- <e.g., No print statements, use logger>
- <e.g., All functions must have type hints>

---

## Notes

- <Any important context that doesn't fit above>
- <Known technical debt>
- <Planned major changes>
```

---

## Phase 6 — Notify Completion

Tell the user:

```
✅ Project context initialized!

📄 Files created:
  - `.sdlc/CONTEXT.md` — project context (read by all SDLC skills)
  - `.sdlc/rules/code-craft.md` — coding rules & conventions

📁 Directories created:
  - `.sdlc/planning/` — for task breakdowns and implementation plans
  - `.sdlc/changelogs/` — for feature changelogs
  - `.sdlc/qa/` — for QA reports

📋 Project summary:
  **Name:** <project name>
  **Type:** <project type>
  **Stack:** <tech stack summary>
  **Repos:** <N repo(s) detected>

🚀 Next steps:
  - If you need to divide the whole project into tasks → use the **project-division** skill
  - If you already know what feature to build → use the **planning** skill directly
  - Review `.sdlc/rules/code-craft.md` and edit any coding rules that don't look right
```

---

## Edge Cases

| Situation | Handling |
|-----------|----------|
| CONTEXT.md already exists | Ask: update, replace, or cancel |
| PRD is very short (1-2 sentences) | Ask more questions (up to 20) |
| PRD is very detailed | Extract everything, ask only 2-3 gap questions |
| No codebase and no PRD | Go full question mode |
| User says "skip questions" | Use recommended defaults, note assumptions |
| Multiple languages in workspace | List all, ask which is primary |
| Monorepo with many packages | Map all packages, ask user which are active |
| User wants to update just one section | Read existing, update only that section |

---

## Quality Checks

Before saving CONTEXT.md, verify:

- [ ] Project name and description are filled in
- [ ] Tech stack table has at least language + framework
- [ ] Repository structure is documented (single or multi-repo)
- [ ] Architecture section describes the layer structure
- [ ] `code-craft.md` exists (either generated or empty for greenfield)
- [ ] All `.sdlc/` subdirectories are created
- [ ] No placeholder text like `<write here>` remains in the final file
