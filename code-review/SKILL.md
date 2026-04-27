---
name: code-review
description: "**WORKFLOW SKILL** — Structured PR code review against project architecture, coding standards, and task requirements. USE FOR: reviewing a pull request or set of changed files, verifying task completion against a PRD, checking coding standards compliance, catching bugs and regressions, identifying print statements and bad patterns. DO NOT USE FOR: implementing new features, planning tasks, or debugging runtime errors. REQUIRES: a task description or PRD; optionally a code standards doc. PRODUCES: a structured review report with PASS/FAIL verdicts per category, inline file-level comments, and a final approval decision."
argument-hint: "Provide the PR description or task to review (e.g., 'review the lead CSV upload PR', 'review changes in routes/lead.py against the PRD')"
---

# Code Review Skill

Performs a thorough, structured PR review against project architecture, coding standards, and functional requirements. Produces a final verdict and actionable inline comments.

---

## When to Use

- Reviewing a GitHub PR or a set of changed files before merging
- Verifying a feature implementation against a PRD or task spec
- Enforcing architecture and coding standards across the team
- Catching bugs, regressions, or missing test coverage before they reach main

---

## Inputs (Collect Before Starting)

| Input | Required | How to Obtain |
|---|---|---|
| **Task description / PRD** | Yes | User provides, or read from `.project_docs/` |
| **Changed files / PR diff** | Yes | User pastes diff, or use `get_changed_files` / `git diff` |
| **Code standards doc** | Optional | User provides, or derive from existing codebase |

If a PRD or task doc is not provided, ask the user: *"What was this PR supposed to implement or fix?"*

---

## Step-by-Step Review Procedure

### Step 1 — Understand the Task

Read the PRD, task description, or ticket. Extract:

- **What should be built/fixed?** — describe in one sentence
- **Acceptance criteria** — what does "done" look like?
- **Scope** — which layers are expected to change? (routes, interactors, models, migrations, schemas, tests, frontend)
- **What must NOT be touched** — existing behavior that must remain intact

State your understanding back in the review output before proceeding.

---

### Step 2 — Gather PR Changes

Collect every changed file. Use the following strategy:

1. If the user provided a diff or file list → use it directly
2. Otherwise, run `git diff main...HEAD --name-only` to list changed files
3. Read each changed file in full — never review a file you haven't read

For each changed file, note:
- What layer it belongs to (route / interactor / migration / model / schema / service / test / frontend / config)
- What it does vs what it did before

---

### Step 3 — Architecture & Layer Compliance

Check every changed file against the project's layer rules:

#### Backend Layer Rules

| Layer | Allowed | Forbidden |
|---|---|---|
| `routes/*.py` | Accept request, call interactor, return response | Business logic, direct DB calls, raise HTTPException inline |
| `interactors/*.py` | Business logic, call repositories + services | Direct DB queries, import `routes` |
| `database/migrations/*.py` | CRUD DB operations only | Business logic, calling services |
| `database/models/*.py` | SQLAlchemy model definition | Business logic |
| `schema/*.py` | Pydantic request/response models | Logic or DB calls |
| `services/` | External integrations (email, Retell, Twilio, JWT) | DB access |
| `utils/` | Exceptions, enums, constants, logging | Business logic |
| `config/setting.py` | Env vars and secrets only | Logic |

Flag any file that violates these boundaries as a **LAYER VIOLATION**.

#### Frontend Layer Rules

- API calls only via `services/` — never inline `fetch`/`axios` in components
- Types defined in `types/` — no inline type declarations for reused shapes
- No business logic in components — UI only
- No hardcoded API URLs — use config
- No `console.log` in committed code

---

### Step 4 — Coding Standards Checklist

Run through every changed Python file and check:

#### Type Hints
- [ ] Every function parameter has a type annotation
- [ ] Every function has a return type annotation
- [ ] No `Any` types without justification

#### Formatting
- [ ] Two blank lines between top-level functions/classes
- [ ] Imports in 3 groups: stdlib → third-party → local (one blank line between)
- [ ] No unused imports

#### Naming
- [ ] `snake_case` for variables, functions, files
- [ ] `PascalCase` for classes and enum members
- [ ] `UPPER_SNAKE_CASE` for constants

#### Hard Rules (ZERO tolerance)
- [ ] **No `print()` statements** — must use `logger` from `utils/logger.py`
- [ ] **No hardcoded secrets or tokens** — must use `config/setting.py`
- [ ] **No `os.environ[...]`** outside `config/` — use `settings.VAR_NAME`
- [ ] **No `raise HTTPException(...)` inline** — use custom exceptions from `utils/custom_exceptions.py`
- [ ] **No magic literals** — use `utils/constants.py` or `utils/enums.py`
- [ ] **No bare `except:`** or silent `except Exception: pass`
- [ ] Every public function and class has a **docstring**
- [ ] **No `console.log`** in frontend code

#### Guard Clauses
- [ ] Early returns/raises used — no deep nesting
- [ ] Not more than ~30 lines per function; if longer, should be extracted

---

### Step 5 — Functional Correctness

Verify the implementation actually does what the task requires:

1. **Does the PR address every acceptance criterion** from Step 1?
2. **Are all new API endpoints correct?** — right HTTP method, right path, right response model
3. **Are DB operations correct?** — right queries, right joins, correct use of `await`
4. **Is error handling complete?** — 404s, 422s, 401s, 403s all handled where needed
5. **Is data validated properly?** — Pydantic schemas enforce required constraints
6. **Are foreign keys, indexes, and cascade rules correct** in new DB models?
7. **Is authentication/authorization applied?** — protected routes use proper dependencies
8. **Is multi-tenancy respected?** — queries scoped to correct `sub_account_id` / `org_id`

Flag any missing or incorrect logic as a **FUNCTIONAL ISSUE**.

---

### Step 6 — Regression & Breakage Check

Check that the PR does not break existing behavior:

1. **Modified shared utilities** — did changes to `utils/`, `config/`, `database/session.py`, or `main.py` affect other consumers?
2. **Import changes** — were any module paths renamed or moved without updating all importers?
3. **DB schema changes** — is there a corresponding Alembic migration? Does it cover all changes?
4. **Route prefix/method changes** — do any existing frontend calls or external integrations depend on old paths?
5. **Dependency changes** — were new packages added to `pyproject.toml`? Are they necessary and safe?
6. **Frontend API calls** — do they match the current backend routes and response shapes?

Flag anything that could cause a runtime crash or regression as a **REGRESSION RISK**.

---

### Step 7 — Test Coverage Check

For every new or modified backend feature:

- [ ] Is there a test file in `backend/tests/<module>/`?
- [ ] Does it cover the happy path?
- [ ] Does it cover validation errors (422)?
- [ ] Does it cover authentication errors (401/403)?
- [ ] Does it cover not-found cases (404)?
- [ ] Are external services mocked (no real email/API calls)?
- [ ] Does the fixture use `TRUNCATE ... CASCADE` (not DROP/RECREATE)?

Flag any untested path as a **MISSING TEST COVERAGE** note.

---

### Step 8 — Code Quality Scan

Do a final pass for general quality issues:

- [ ] No dead code (commented-out blocks, unused variables/imports)
- [ ] No TODO/FIXME comments left in production code paths
- [ ] No overly complex functions — flag any function over ~30 lines
- [ ] No duplicated logic that should be extracted
- [ ] No inconsistent naming vs the rest of the codebase
- [ ] No `pass` placeholders left in real logic
- [ ] Files are in the right place (no model in routes, no logic in schema, etc.)

---

## Review Output Format

Produce a structured review report in this format:

```markdown
# PR Review: <PR Title / Task Name>

## Summary
<One-paragraph description of what this PR does, based on your understanding.>

---

## Task Completion
| Requirement | Status | Notes |
|---|---|---|
| <Acceptance criterion 1> | ✅ PASS / ❌ FAIL / ⚠️ PARTIAL | <explanation> |
| <Acceptance criterion 2> | ✅ PASS / ❌ FAIL / ⚠️ PARTIAL | <explanation> |

---

## Architecture & Layer Review
| File | Layer | Verdict | Issue |
|---|---|---|---|
| `routes/lead.py` | Route | ✅ OK | — |
| `interactors/lead.py` | Interactor | ❌ VIOLATION | Direct DB query on line 42 |

---

## Coding Standards
| Check | Verdict | Details |
|---|---|---|
| Type hints | ✅ PASS | All params annotated |
| No `print()` | ❌ FAIL | `print(lead)` found in interactors/lead.py:58 |
| No inline HTTPException | ✅ PASS | — |
| Docstrings | ⚠️ PARTIAL | Missing on `process_csv()` |
| Import order | ✅ PASS | — |

---

## Functional Issues
<List each issue as a numbered block:>

### Issue 1 — <Short title>
- **File**: `interactors/lead.py`, line 42
- **Severity**: 🔴 Critical / 🟡 Warning / 🔵 Suggestion
- **Problem**: <What is wrong>
- **Fix**: <What to do instead>

---

## Regression Risks
<List any regression risks, or state "None identified.">

---

## Test Coverage
| Scenario | Covered | Notes |
|---|---|---|
| Happy path | ✅ Yes | `test_upload_csv_success` |
| Invalid file type | ❌ No | Missing test |
| Unauthorized access | ✅ Yes | — |

---

## Final Verdict

| Category | Result |
|---|---|
| Task Completion | ✅ / ❌ / ⚠️ |
| Architecture | ✅ / ❌ / ⚠️ |
| Coding Standards | ✅ / ❌ / ⚠️ |
| Functional Correctness | ✅ / ❌ / ⚠️ |
| No Regressions | ✅ / ❌ / ⚠️ |
| Test Coverage | ✅ / ❌ / ⚠️ |

### Decision: ✅ APPROVED / ❌ CHANGES REQUIRED / ⚠️ APPROVED WITH NOTES

<One-paragraph final summary. If CHANGES REQUIRED, list the blocking issues by number.>
```

---

## Severity Definitions

| Level | Meaning | Blocks Merge? |
|---|---|---|
| 🔴 Critical | Bug, security issue, data corruption risk, regression | YES |
| 🟡 Warning | Standards violation, missing tests, code smell | YES (in this project) |
| 🔵 Suggestion | Minor improvement, style, readability | NO |

---

## Project-Specific Context

This project is **Eraviya Sales Buddy** — an AI-powered voice/SMS/email agent management platform.

### Architecture
```
Routes → Interactors → Repositories (database/migrations/) + Services
```

### Multi-Tenancy Model
```
Organization → SubAccount(s) → Users / Agents / Leads
```
All data **must be scoped to `sub_account_id`** unless it is organization-level data.

### Key Files to Know
- `config/setting.py` — all env vars and secrets
- `utils/enums.py` — all enum types
- `utils/constants.py` — named constants
- `utils/custom_exceptions.py` — all custom HTTP exceptions
- `utils/logger.py` — logger instance (use this, never `print`)
- `utils/dependencies.py` — FastAPI dependencies (auth, DB, permissions)
- `utils/permissions.py` — permission helpers

### Stack
- **Backend**: FastAPI (async), SQLAlchemy async + asyncpg, PostgreSQL 15, Alembic, Pydantic v2, pytest
- **Frontend**: React 18 + TypeScript + Vite + Tailwind v4 + React Router v7
- **Package manager**: `uv` (backend), `npm` (frontend)

---

## Quick Red Flags (Auto-Fail)

If any of these are found, the PR is an immediate **❌ CHANGES REQUIRED**:

- `print(` anywhere in backend code
- `raise HTTPException(` inline in any file (must use custom exceptions)
- `os.environ[` outside `config/setting.py`
- Hardcoded secrets, tokens, or passwords
- Missing Alembic migration for a DB model change
- `console.log(` in frontend production code
- New DB query inside a route handler (must go through interactor + repository)
- Multi-tenancy data leak (query without `sub_account_id` filter when required)
- Bare `except:` catching all exceptions silently
