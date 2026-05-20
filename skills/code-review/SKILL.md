---
name: code-review
description: "**WORKFLOW SKILL** — Structured code review against project architecture, coding standards, and task requirements. USE FOR: reviewing changed files, verifying task completion against a plan, checking coding standards compliance from code-craft.md, catching bugs and regressions, identifying bad patterns. DO NOT USE FOR: implementing new features, planning tasks, or debugging runtime errors. READS: .sdlc/CONTEXT.md for project context, .sdlc/rules/code-craft.md for coding standards, .sdlc/planning/ for task plans. PRODUCES: a structured review report with PASS/FAIL verdicts per category, inline file-level comments, and a final approval decision."
argument-hint: "Provide the feature or task to review (e.g., 'review the auth feature', 'review changes for division 3', 'review all changes on this branch')"
---

# Code Review Skill

Performs a thorough, structured code review against the project's own architecture and coding standards (from `code-craft.md`). Fully generic — works with any language, framework, or project structure. Produces a final verdict and actionable comments.

---

## When to Use

- Reviewing changed files before committing
- Verifying a feature implementation against its plan
- Enforcing architecture and coding standards
- Catching bugs, regressions, or missing test coverage
- After QA passes and before code-commit (optional step)

---

## Phase 0 — Read Project Context

### 0.1 Read CONTEXT.md

```bash
cat .sdlc/CONTEXT.md 2>/dev/null
```

**If it exists and has content:** Extract project name, tech stack, architecture, layer structure, repo structure. This tells you what conventions to expect. Proceed to Phase 0.2.

**If it does NOT exist or is empty — STOP and run context-init first:**

> ⚠️ CONTEXT.md is needed for proper code review (understanding architecture, layer rules, project conventions). Do NOT skip this.

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
- Infer conventions from the codebase by reading 5-10 representative files
- Note in the review output that no CONTEXT.md was found and standards were inferred

### 0.2 Read Code-Craft Rules

```bash
cat .sdlc/rules/code-craft.md 2>/dev/null
```

**If it exists:** This is your primary source for all coding standards. Every rule in this file becomes a checklist item for the review.

**If it does not exist:** Infer conventions from the codebase by reading 5-10 representative files. Note in the review output that no `code-craft.md` was found and standards were inferred.

### 0.3 Read Changelogs

```bash
cat .sdlc/changelogs/changelog.md 2>/dev/null
```

If it exists, understand what's been previously built to check for regressions.

---

## Inputs (Collect Before Starting)

| Input | Required | How to Obtain |
|---|---|---|
| **Task description / plan** | Yes | Read from `.sdlc/planning/`, or user provides |
| **Changed files** | Yes | `git diff`, `git status`, or user specifies |
| **Code standards** | Yes | Read from `.sdlc/rules/code-craft.md` |

If a plan or task doc is not provided, ask the user: *"What was this change supposed to implement or fix?"*

---

## Step-by-Step Review Procedure

### Step 1 — Understand the Task

Read the planning file or task description. Extract:

- **What should be built/fixed?** — describe in one sentence
- **Acceptance criteria** — what does "done" look like?
- **Scope** — which layers/repos are expected to change?
- **What must NOT be touched** — existing behavior that must remain intact

If the user referenced a division, read it from `project_divisions.md`.

State your understanding back in the review output before proceeding.

---

### Step 2 — Gather Changed Files

Collect every changed file. Use the following strategy:

1. If the user provided a file list → use it directly
2. Otherwise, detect changed files:
   ```bash
   git diff --name-only HEAD~1..HEAD 2>/dev/null || git diff --name-only 2>/dev/null || git status --short
   ```
3. Read each changed file in full — never review a file you haven't read

For each changed file, note:
- What layer/module it belongs to (based on `code-craft.md` layer structure)
- What it does vs what it did before

For multi-repo projects, check changes in each repo:
```bash
# For each repo path from CONTEXT.md
git -C <repo_path> diff --name-only
```

---

### Step 3 — Architecture & Layer Compliance

Read the layer/architecture rules from `.sdlc/rules/code-craft.md` (section "File & Folder Structure" or similar).

For each changed file, verify it follows those rules:

**Dynamically build the checklist from code-craft.md. Example:**

If `code-craft.md` says:
```
## File & Folder Structure
- Routes: Accept request, delegate to service, return response. No business logic.
- Services: All business logic. No direct DB queries.
- Repositories: CRUD operations only. No business logic.
- Models: Data definitions only.
```

Then check:
| Layer | Changed File | Allowed | Violation? |
|---|---|---|---|
| Routes | `routes/item.py` | Delegate to service, return response | ✅ OK |
| Services | `services/item.py` | Business logic, call repos | ❌ Direct DB query on line 42 |

**If no layer rules exist in code-craft.md:** infer from the project structure and note your assumptions.

Flag any file that violates layer boundaries as a **LAYER VIOLATION**.

---

### Step 4 — Coding Standards Checklist

Build the checklist dynamically from `.sdlc/rules/code-craft.md`. For every rule in that file, check each changed file.

**Common checks (verify these if mentioned in code-craft.md):**

#### Type Hints / Types
- [ ] Function parameters have type annotations (if required by code-craft)
- [ ] Return types are annotated (if required by code-craft)
- [ ] No `Any` types without justification

#### Formatting
- [ ] Spacing and indentation follow project conventions
- [ ] Import ordering follows project conventions
- [ ] No unused imports

#### Naming
- [ ] Variable/function/file naming follows project conventions
- [ ] Class naming follows project conventions
- [ ] Constants follow project conventions

#### Hard Rules (from code-craft.md)
Go through every "Hard Rule" or "Never Do" listed in `code-craft.md` and check for violations.

Common patterns to check (only if mentioned in code-craft.md):
- No `print()` statements (should use logger)
- No hardcoded secrets or tokens (should use config)
- No inline exceptions (should use custom exception classes)
- No magic literals (should use constants/enums)
- No bare `except:` or silent `except: pass`
- No `console.log` in production code
- Docstrings/comments required on public functions

#### Guard Clauses
- [ ] Early returns/raises used — no deep nesting
- [ ] Functions not overly long (check code-craft for max line count)

---

### Step 5 — Functional Correctness

Verify the implementation actually does what the task requires:

1. **Does the change address every acceptance criterion** from the plan?
2. **Are all new API endpoints correct?** — right HTTP method, right path, right response model
3. **Are DB operations correct?** — right queries, right joins, proper async handling
4. **Is error handling complete?** — all error cases handled where needed
5. **Is data validated properly?** — input validation enforces required constraints
6. **Are foreign keys, indexes, and cascade rules correct** in new DB models?
7. **Is authentication/authorization applied?** — protected routes use proper dependencies
8. **Are permissions respected?** — queries scoped correctly

Flag any missing or incorrect logic as a **FUNCTIONAL ISSUE**.

---

### Step 6 — Regression & Breakage Check

Check that the changes do not break existing behavior:

1. **Modified shared utilities** — did changes to common files affect other consumers?
2. **Import changes** — were any module paths renamed or moved without updating all importers?
3. **DB schema changes** — is there a corresponding migration? Does it cover all changes?
4. **Route/endpoint changes** — do any existing consumers depend on old paths?
5. **Dependency changes** — were new packages added? Are they necessary and safe?
6. **Cross-repo impact** — for multi-repo projects, do changes in one repo break contracts with another?

Flag anything that could cause a runtime crash or regression as a **REGRESSION RISK**.

---

### Step 7 — Test Coverage Check

For every new or modified feature:

- [ ] Is there a corresponding test file?
- [ ] Does it cover the happy path?
- [ ] Does it cover validation errors?
- [ ] Does it cover authentication/authorization errors?
- [ ] Does it cover not-found / edge cases?
- [ ] Are external services mocked (no real API calls in tests)?

Flag any untested path as a **MISSING TEST COVERAGE** note.

---

### Step 8 — Code Quality Scan

Do a final pass for general quality issues:

- [ ] No dead code (commented-out blocks, unused variables/imports)
- [ ] No TODO/FIXME comments left in production code paths
- [ ] No overly complex functions — flag any function over the project's max line count
- [ ] No duplicated logic that should be extracted
- [ ] No inconsistent naming vs the rest of the codebase
- [ ] No placeholder code left in real logic
- [ ] Files are in the right directory (following code-craft.md structure)

---

## Review Output Format

Produce a structured review report in this format:

```markdown
# Code Review: <Feature / Task Name>

## Summary
<One-paragraph description of what this change does, based on your understanding.>

**Plan:** `.sdlc/planning/<task_name>.md`
**Rules:** `.sdlc/rules/code-craft.md`
**Context:** `.sdlc/CONTEXT.md`

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
| `routes/item.py` | Route | ✅ OK | — |
| `services/item.py` | Service | ❌ VIOLATION | Direct DB query on line 42 |

---

## Coding Standards (from code-craft.md)
| Rule | Verdict | Details |
|---|---|---|
| <rule from code-craft> | ✅ PASS | All compliant |
| <rule from code-craft> | ❌ FAIL | Violation in `file.py:58` |
| <rule from code-craft> | ⚠️ PARTIAL | Missing in `service.py` |

---

## Functional Issues
<List each issue as a numbered block:>

### Issue 1 — <Short title>
- **File**: `services/item.py`, line 42
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
| Happy path | ✅ Yes | `test_create_item_success` |
| Invalid input | ❌ No | Missing test |
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

| Level | Meaning | Blocks Approval? |
|---|---|---|
| 🔴 Critical | Bug, security issue, data corruption risk, regression | YES |
| 🟡 Warning | Standards violation, missing tests, code smell | YES |
| 🔵 Suggestion | Minor improvement, style, readability | NO |

---

## Edge Cases

| Situation | Handling |
|-----------|----------|
| No code-craft.md found | Infer conventions from codebase, note in report |
| No CONTEXT.md found | Ask user about project structure, note in report |
| No planning file found | Ask user what the change was supposed to do |
| Very few files changed (1-2) | Still do full review, just shorter |
| Massive PR (50+ files) | Group by module, review layer-by-layer, flag if too large |
| Multi-repo changes | Review each repo separately, check cross-repo contracts |
| No tests exist at all | Flag as 🟡 Warning, suggest test creation |
| User says "just check standards" | Scope review to coding standards only |
