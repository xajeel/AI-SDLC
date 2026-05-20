---
name: qa
description: >
  **QA & TESTING SKILL** — Fully automated quality assurance for an implemented feature, division, or any completed work. USE THIS SKILL whenever the user says things like "QA this", "test this feature", "verify the implementation", "run QA on division 3", "check if this is working", "do a QA pass", "make sure this feature works", "validate the implementation", "run tests", "does this match the plan", "QA the auth feature", or "test everything". Trigger this skill after a feature or division has been implemented and the user wants it verified. The agent reads CONTEXT.md, the task plan, changelogs, explores the codebase, identifies what was supposed to be built, checks what was actually built, runs existing tests, writes missing tests, performs regression testing on previously completed features, produces a structured QA report with manual testing steps for non-technical testers, and gives a clear pass/fail verdict. Always use this skill — do NOT just run pytest manually without the full QA workflow.
argument-hint: "Name the feature or division to QA (e.g., 'QA division 2', 'QA the auth feature', 'QA the whole project')"
---

# QA Skill

Automated QA agent that verifies a completed feature, division, or task against its plan, acceptance criteria, and expected behaviour. Performs regression testing on all previously completed features. Produces a structured report with a pass/fail verdict, manual testing steps for non-technical testers, and a remediation list for anything that fails.

## What This Skill Does

1. **Reads project context** — CONTEXT.md, changelogs, code-craft rules
2. **Finds the plan** — reads the task plan and implementation plan automatically
3. **Understands what was supposed to be built** — extracts scope, acceptance criteria, and expected behaviour
4. **Explores what was actually built** — maps the real codebase against the plan
5. **Asks clarifying questions if needed** — MCQ format, same as other skills
6. **Runs existing tests** — executes whatever test suite exists
7. **Writes missing tests** — generates and runs tests for anything untested
8. **Does behavioural checks** — verifies endpoints, logic, DB state, error handling
9. **Runs regression tests** — verifies all previously completed features still work
10. **Produces a QA report** — saved to `.sdlc/qa/` with full pass/fail breakdown
11. **Writes manual testing steps** — step-by-step guide with mock data for non-technical testers

---

## Workflow

```
Read CONTEXT.md + Changelogs
          ↓
Read Task Plan + Implementation Plan
          ↓
     Gap Analysis
          ↓
  (if gaps) MCQ Questions → wait for "done"
          ↓
   Explore Actual Codebase
          ↓
  Cross-check Plan vs Reality
          ↓
    Run Existing Test Suite
          ↓
  Write & Run Missing Tests
          ↓
 Behavioural / Integration Checks
          ↓
    Regression Testing (previous features)
          ↓
  Write Manual Testing Steps
          ↓
  Write QA Report → .sdlc/qa/<name>_qa_report.md
          ↓
  Ask user: Commit, Review, or Fix?
```

---

## Phase 0 — Read Project Context

### 0.1 Read CONTEXT.md

```bash
cat .sdlc/CONTEXT.md 2>/dev/null
```

**If it exists and has content:** Load the project context: tech stack, architecture, repo structure, current state. Proceed to Phase 0.2.

**If it does NOT exist or is empty — STOP and run context-init first:**

> ⚠️ CONTEXT.md is needed for proper QA (understanding the project, running the right tests, regression testing). Do NOT skip this.

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
- Ask the user 3-5 critical questions (tech stack, project type, test runner)
- Create a minimal `.sdlc/CONTEXT.md` with the answers
- Proceed with QA using the available information

### 0.2 Read Changelogs

```bash
cat .sdlc/changelogs/changelog.md 2>/dev/null
```

If it exists, extract the list of all previously completed features. You will regression-test each of these.

### 0.3 Read Code-Craft Rules

```bash
cat .sdlc/rules/code-craft.md 2>/dev/null
```

If it exists, load coding rules. Use these to verify code quality in the review portion.

---

## Phase 1 — Find & Read the Plan

### 1.1 Locate Planning Files

Check these locations in order:

```
.sdlc/planning/project_divisions.md       ← project-level division plan
.sdlc/planning/<task_name>.md             ← feature task breakdown
.sdlc/implementation/<task_name>/         ← implementation detail files
```

To find the right task files, list `.sdlc/planning/` and identify files matching the feature or division the user named. If the user said "QA division 2", find the division 2 entry in `project_divisions.md` to get its name, then find the matching planning files.

### 1.2 Extract What Was Planned

From the planning files, extract and record:

- **Feature / Division / Task name**
- **Goal** — the one-sentence goal
- **Scope** — what is included
- **Out of Scope** — what is explicitly excluded
- **Acceptance Criteria** — the full checklist (these are the primary QA targets)
- **Files Affected** — the file list from the implementation plan
- **Tech stack** — language, framework, DB, package manager
- **Repos affected** — which repos should have changes
- **Phase breakdown** — what each phase was supposed to deliver
- **DB schema** — tables, columns, constraints (if DB is involved)
- **API endpoints** — routes, methods, request/response shapes (if API is involved)

If no planning files exist at all, proceed with gap analysis (Phase 2) to collect this information from the user.

---

## Phase 2 — Gap Analysis & Clarification Questions

After reading the plan (or if no plan exists), check for anything that would block QA:

**Check for gaps:**
- Is it clear which feature/division to QA?
- Is the tech stack known (to run the right test commands)?
- Is the test runner known (pytest, jest, vitest, cargo test, go test, etc.)?
- Are there environment requirements? (DB running, env vars set, server running?)
- Are there external dependencies that need to be mocked or live? (APIs, queues, storage)
- Is there a specific area of concern the user wants focused on?
- Should QA cover only the happy path, or also edge cases and error handling?
- Is this a full QA pass or a targeted check on one specific behaviour?

**If gaps exist:**

Create `.sdlc/planning/questions/` if not present, then write:
`.sdlc/planning/questions/qa_time_questions.md`

Use this exact MCQ format:

```markdown
# QA — Clarification Questions

Please answer the questions below by writing your choice in the `Answer:` field.
For option D (Other), write: `D: your specific answer`
When done, reply in the chat with **done** or **answered**.

---

## Q1: <Short title>

**Question:** <Full question?>

- A: <Option A>
- B: <Option B (Recommended)>
- C: <Option C>
- D: Other

**Answer:** <Write your answer here>

---
```

Tell the user:
```
Before I start QA, I need a few quick answers.

📋 Written to: `.sdlc/planning/questions/qa_time_questions.md`

Fill in the Answer fields, save, then reply **done** or **answered**.
```

Wait. Do not proceed until confirmed. Then read the file and extract answers.

**If no gaps exist:** skip this phase entirely.

---

## Phase 3 — Explore the Actual Codebase

Map what was *actually* built against what was *planned*.

### 3.1 Read Project Structure

```bash
find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.go" -o -name "*.rs" -o -name "*.java" -o -name "*.rb" -o -name "*.php" \) \
  | grep -v node_modules | grep -v .venv | grep -v __pycache__ | grep -v target | grep -v .git | grep -v dist
```

Build a mental map: what modules, routes, models, services, and tests actually exist.

For multi-repo projects, scan each affected repo separately.

### 3.2 Cross-Check Files Affected

For every file listed in the implementation plan's "Files Affected" table:

| Check | Pass / Fail |
|-------|-------------|
| File exists at the expected path | ✅ / ❌ |
| File is non-empty / non-stub | ✅ / ❌ |
| Key functions/classes/routes are present | ✅ / ❌ |
| Signatures match what the plan specified | ✅ / ❌ |

Read each file and compare its actual content against what the implementation plan said it should contain.

### 3.3 Check DB Schema (if applicable)

- Do the expected tables exist? (check migration files or introspect DB if accessible)
- Do columns match the planned schema (names, types, constraints)?
- Are FK relationships correct?
- Did migrations run? Check `alembic_version` or equivalent.

### 3.4 Check API Endpoints (if applicable)

- Are all planned routes registered?
- Do route paths match the plan?
- Are request/response models correct?
- Check router registration in the main app file.

### 3.5 Produce a Reality vs Plan Summary

Before running tests, write a brief summary:

```
## Reality vs Plan

### Files: 8/10 present
- ✅ src/routes/item.py
- ✅ src/services/item.py
- ❌ src/schema/item_response.py (missing)
- ✅ src/models/item.py
- ...

### DB Schema: 3/4 columns correct
- ❌ 'owner_id' column missing FK constraint

### Endpoints: 4/5 registered
- ❌ DELETE /v1/items/{id} not found in router
```

---

## Phase 4 — Run Existing Tests

### 4.1 Find the Test Suite

Look for tests in standard locations:
```
tests/
src/tests/
__tests__/
*.test.ts / *.spec.ts
*_test.go
*_test.rs
test/
spec/
```

### 4.2 Run Tests

Use the project's package manager and test runner. Common patterns:

**Python / uv:**
```bash
uv run pytest tests/ -v --tb=short 2>&1
```

**Python / pip:**
```bash
python -m pytest tests/ -v --tb=short 2>&1
```

**Node / npm:**
```bash
npm test 2>&1
```

**Node / yarn:**
```bash
yarn test 2>&1
```

**Rust:**
```bash
cargo test 2>&1
```

**Go:**
```bash
go test ./... -v 2>&1
```

Capture the full output. Record:
- Total tests run
- Passed / failed / skipped
- Any error tracebacks or failure messages

### 4.3 Run Only Feature-Specific Tests

If the test suite is large, also run tests scoped to this feature:

```bash
uv run pytest tests/<feature>/ -v --tb=long 2>&1
# or
uv run pytest -k "<feature_name>" -v --tb=long 2>&1
```

---

## Phase 5 — Write Missing Tests

For every acceptance criterion that has no existing test coverage, write a test.

### 5.1 Identify Uncovered Criteria

Map each acceptance criterion to existing tests. Any criterion with no test gets one written.

### 5.2 Test Writing Rules

- **One test file per feature area** — save to `tests/<feature>/test_<feature>_qa.py` (or language equivalent)
- **Test the happy path first** — does the core behaviour work?
- **Test edge cases** — empty inputs, boundary values, large payloads
- **Test error handling** — what happens with bad input, missing auth, not-found IDs
- **Test DB state** — after write operations, verify the DB actually changed
- **Test response shape** — correct status codes, response body fields, types
- **Follow code-craft.md rules** — use the project's testing conventions

### 5.3 Run the New Tests

Run the QA-generated tests and record results.

---

## Phase 6 — Behavioural Checks

Beyond unit tests, verify the feature behaves correctly end-to-end.

### 6.1 Check Business Logic

Read the service / business logic layer and verify:
- Does it do what the plan described?
- Are guard clauses present for invalid states?
- Is error handling correct (right exception types, right messages)?
- Are there any obvious logic bugs?

### 6.2 Check Auth & Permissions (if applicable)

- Protected routes require authentication
- Role checks are enforced correctly
- Users cannot access other users' data

### 6.3 Check Data Integrity

- Required fields are validated before DB writes
- FK constraints would catch orphaned records
- No raw string SQL (injection risk)

### 6.4 Check Response Contracts

Read the schema/DTO layer and verify:
- Response models match what the plan specified
- No sensitive fields accidentally exposed (passwords, tokens, internal IDs)
- Pagination, filtering, sorting work if planned

### 6.5 Check Against Each Acceptance Criterion

Go through every acceptance criterion from the task file one by one. For each:

```
Criterion: "Returns 401 for unauthenticated requests"
Check: Read auth middleware / route decorator
Result: ✅ Auth dependency applied to all routes
Evidence: src/routes/item.py line 14
```

---

## Phase 7 — Regression Testing

### 7.1 Read Previously Completed Features

Read `.sdlc/changelogs/changelog.md` to get the list of all previously completed features/divisions/phases.

### 7.2 For Each Previous Feature

1. Find its test suite (either the original tests or QA-generated tests)
2. Run the tests
3. If no tests exist, do a quick smoke check:
   - Key endpoints still respond correctly
   - Key functions still return expected results
   - No import errors or module loading failures

### 7.3 Record Regression Results

```
## Regression Results

| Previous Feature | Test Suite | Result | Notes |
|-----------------|------------|--------|-------|
| Feature: Project Setup | 5/5 pass | ✅ OK | — |
| Feature: User Auth | 12/12 pass | ✅ OK | — |
| Feature: Item CRUD | 8/10 pass | ⚠️ 2 failures | test_delete broken by new migration |
```

If any regression is found, flag it as a **🔴 Critical** issue in the QA report.

---

## Phase 8 — Write Manual Testing Steps

Create step-by-step manual testing instructions that a **non-technical person** can follow to verify the feature works. Use concrete mock data and expected results.

### 8.1 Generate Manual Test Cases

For each key behaviour of the feature, write a test case:

```markdown
## Manual Testing Guide

> These steps can be followed by anyone (developer, QA tester, product manager, client)
> to verify the feature works correctly. No coding knowledge needed.

### Prerequisites
- The application is running locally at <URL> (e.g., http://localhost:8000)
- The database has been seeded / migrated
- <Any other setup needed>

---

### Test 1: <Action Name> (Happy Path)

**What we're testing:** <plain English description>

**Steps:**
1. Open your browser / Postman / API testing tool
2. Navigate to <URL or endpoint>
3. Enter the following test data:
   ```json
   {
     "email": "testuser@example.com",
     "password": "SecurePass123!",
     "name": "Test User"
   }
   ```
4. Click Submit / Send

**✅ Expected Result:**
- Status: 200 OK (or "Success" message on screen)
- Response contains: user ID, email, name
- A confirmation email is sent (check inbox or logs)

**❌ If Something Goes Wrong:**
- If you see a 500 error: check the server logs
- If you see a 422 error: the test data format is wrong
- If you see a 401 error: authentication is not configured

---

### Test 2: <Error Case Name>

**What we're testing:** <what should happen when input is wrong>

**Steps:**
1. <step 1>
2. Enter invalid data:
   ```json
   {
     "email": "not-an-email",
     "password": ""
   }
   ```
3. Click Submit / Send

**✅ Expected Result:**
- Status: 422 Validation Error
- Error message explains what fields are wrong

---

### Test 3: <Another Important Scenario>

... (repeat for all key scenarios)

---

### Quick Checklist

After running all tests above, verify:
- [ ] Test 1 passed — <description>
- [ ] Test 2 passed — <description>
- [ ] Test 3 passed — <description>
- [ ] No errors in the server logs during testing
```

### 8.2 Mock Data Rules

- Use realistic but clearly fake data (test@example.com, John Doe, 555-0100)
- Include all required fields
- Show the exact JSON or form data to enter
- Include both valid and invalid test data
- For each test, show the expected result AND what to do if it fails

---

## Phase 9 — Write QA Report

Save to `.sdlc/qa/<feature_or_task_name>_qa_report.md`.

Create `.sdlc/qa/` if it does not exist.

### Report Format

```markdown
# QA Report — <Feature / Division / Task Name>

**Date:** <date>
**Feature:** <feature name or division number and name>
**Plan Files:**
- `.sdlc/planning/<task_name>.md`
- `.sdlc/implementation/<task_name>/`
**Context:** `.sdlc/CONTEXT.md`

---

## Overall Verdict

> # ✅ PASS  (or  ❌ FAIL  or  ⚠️ PASS WITH WARNINGS)

**Summary:** <2-3 sentences on overall state of the implementation>

---

## Acceptance Criteria Results

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | <criterion text> | ✅ Pass | `src/routes/item.py:45` |
| 2 | <criterion text> | ❌ Fail | Missing DELETE endpoint |
| 3 | <criterion text> | ⚠️ Partial | Works but no error handling |

**Score: X / Y criteria passing**

---

## Test Suite Results

### Existing Tests
```
Ran: 24 tests
Passed: 22
Failed: 2
Skipped: 0
```

**Failing tests:**
- `tests/item/test_item.py::test_delete_item` — `404 Not Found: no route`
- `tests/item/test_item.py::test_owner_filter` — `AssertionError: expected 2, got 5`

### QA-Generated Tests
```
Ran: 8 tests
Passed: 6
Failed: 2
```

---

## Reality vs Plan

### Files
| File | Planned | Actual | Status |
|------|---------|--------|--------|
| `src/routes/item.py` | CREATE | ✅ Exists | OK |
| `src/services/item.py` | CREATE | ✅ Exists | OK |
| `src/schema/item_response.py` | CREATE | ❌ Missing | FAIL |

### DB Schema
| Column | Planned | Actual | Status |
|--------|---------|--------|--------|
| `id` | UUID PK | ✅ UUID PK | OK |
| `owner_id` | UUID FK→users | ❌ UUID, no FK | FAIL |

### Endpoints
| Endpoint | Planned | Actual | Status |
|----------|---------|--------|--------|
| `POST /v1/items/` | ✅ | ✅ Registered | OK |
| `DELETE /v1/items/{id}` | ✅ | ❌ Not registered | FAIL |

---

## Regression Results

| Previous Feature | Test Suite | Result | Notes |
|-----------------|------------|--------|-------|
| Feature: Setup | 5/5 pass | ✅ OK | — |
| Feature: Auth | 12/12 pass | ✅ OK | — |

---

## Issues Found

### 🔴 Critical (blocks acceptance)

#### Issue 1 — <Title>
- **Criterion:** "<related acceptance criterion>"
- **Location:** `<file>:<line>`
- **Detail:** <what's wrong>
- **Fix:** <how to fix it>

### 🟡 Warnings (should fix, does not block all criteria)

#### Warning 1 — <Title>
- **Location:** `<file>:<line>`
- **Detail:** <what's wrong>
- **Fix:** <how to fix it>

### 🟢 What's Working Well

- <positive finding 1>
- <positive finding 2>

---

## Manual Testing Guide

> Steps for a non-technical person to verify this feature with mock data.

### Prerequisites
- <what needs to be running>

### Test 1: <Happy Path>
1. <step>
2. Enter: `<mock data>`
3. <step>
**✅ Expected:** <result>
**❌ If wrong:** <troubleshooting>

### Test 2: <Error Case>
1. <step>
2. Enter: `<invalid mock data>`
**✅ Expected:** <error result>

### Quick Checklist
- [ ] Test 1 passed
- [ ] Test 2 passed
- [ ] No server errors

---

## Remediation Checklist

Copy this into your task tracker or implementation file:

- [ ] <Fix 1>
- [ ] <Fix 2>
- [ ] <Fix 3>

**After fixing:** re-run tests and re-run this QA skill.

---

## QA Coverage Summary

| Area | Coverage |
|------|----------|
| Acceptance criteria | X / Y |
| Planned files present | X / Y |
| DB schema correct | X / Y |
| Endpoints registered | X / Y |
| Test suite passing | X / Y |
| Auth enforced | ✅ / ❌ |
| Error handling | ✅ / ❌ |
| Regression (previous features) | X / Y pass |
| Manual testing steps | ✅ Included |

---

*Generated by QA Skill — `.sdlc/qa/<name>_qa_report.md`*
```

---

## Verdict Rules

| Condition | Verdict |
|-----------|---------|
| All acceptance criteria pass, all tests pass, no regressions | ✅ **PASS** |
| All acceptance criteria pass, minor test gaps or warnings | ⚠️ **PASS WITH WARNINGS** |
| Any acceptance criterion fails | ❌ **FAIL** |
| Core functionality broken | ❌ **FAIL** |
| Auth not enforced when planned | ❌ **FAIL** (always critical) |
| Regression found in previous feature | ❌ **FAIL** (always critical) |
| Missing files with minor impact | ⚠️ **PASS WITH WARNINGS** |

---

## Notify User on Completion

```
✅ QA complete for **<Feature / Task Name>**

**Verdict: <PASS / FAIL / PASS WITH WARNINGS>**

📄 Full report: `.sdlc/qa/<name>_qa_report.md`

**Quick summary:**
- Acceptance criteria: X/Y passing
- Tests: X passed, Y failed
- Regression: X/Y previous features still working
- Critical issues: N
- Warnings: N
- Manual testing steps: included in report

<If FAIL>: Fix the N critical issues listed in the Remediation Checklist, then re-run QA.
<If PASS>:
  Would you like to:
  A) **Commit** this feature (I'll use the code-commit skill)
  B) **Review** the code first (I'll use the code-review skill)
  C) **Move on** to the next feature/division
```

---

## Output Structure

```
.sdlc/
├── CONTEXT.md                             ← read for project context
├── planning/
│   ├── questions/
│   │   └── qa_time_questions.md           ← only if gaps found
│   ├── <task_name>.md
│   └── project_divisions.md
├── qa/
│   └── <feature_name>_qa_report.md        ← main output
└── changelogs/
    └── changelog.md                       ← read for regression scope

tests/
└── <feature>/
    └── test_<feature>_qa.py               ← QA-generated tests (committed to repo)
```

---

## Edge Cases

| Situation | Handling |
|-----------|----------|
| No planning files found | Ask user to provide the scope, acceptance criteria, and tech stack via MCQ |
| No tests exist at all | Write a full test suite, run it, report results |
| Tests exist but don't run (missing deps, env issues) | Document the error, note it as a warning, proceed with behavioural checks |
| User says "just check X" | Scope QA to that specific area only, still produce a report |
| Feature is across multiple repos | QA each repo's changes, run tests in each repo |
| DB not accessible | Skip DB state checks, note as limitation in report |
| No `.sdlc/` folder | Fall back to asking user for scope; still write report to `.sdlc/qa/` |
| No changelogs (first feature) | Skip regression testing, note "first feature — no regressions to check" |
| No CONTEXT.md | Proceed without it, note as suggestion in report |
| User wants QA on the whole project | Run against all divisions/features, produce one combined report |