---
name: git-commit
description: >
  **GIT COMMIT SKILL** — Stages and commits code changes to feature branches using the task/division plan as the commit message source. USE THIS SKILL whenever the user says things like "commit this", "commit the code", "make a commit", "commit my changes", "git commit", "save my progress", "commit what I've done", "commit division 2", "commit the feature", or "commit and move on". NEVER commits on main, master, staging, develop, or integration branches — always checks branch first and refuses if on a protected branch. Reads CONTEXT.md for multi-repo awareness. Reads the task breakdown file from .sdlc/planning/ automatically to write a meaningful, structured commit message. Supports multi-repo projects — commits to each affected repo separately. Does NOT push — commit only.
argument-hint: "Name the feature or division being committed (e.g., 'commit division 2', 'commit auth feature', 'commit my changes')"
---

# Git Commit Skill

Stages and commits completed work to feature branches. Reads CONTEXT.md for multi-repo awareness and planning files for meaningful commit messages. Refuses to commit on protected branches. Supports committing across multiple repos. Never pushes.

---

## Workflow

```
Read CONTEXT.md (check for multi-repo)
        ↓
For each repo (or single repo):
        ↓
  Check current branch
        ↓
    ❌ protected branch → STOP (offer to create feature branch)
        ↓
    ✅ feature branch → continue
        ↓
  Read task file from .sdlc/planning/
        ↓
  Check git status (what changed)
        ↓
  Confirm with user what to stage
        ↓
  Stage files (git add)
        ↓
  Build commit message from plan
        ↓
  git commit
        ↓
  Update changelog
        ↓
  Show commit summary
```

---

## Phase 0 — Read Project Context

### 0.1 Check for Multi-Repo

```bash
cat .sdlc/CONTEXT.md 2>/dev/null
```

**If it exists and has content:** Read the "Repository Structure" section. Extract:
- How many repos exist
- Their paths (e.g., `./backend`, `./frontend`)
- Their purposes

Proceed to Phase 0.2.

**If it does NOT exist or is empty — STOP and run context-init first:**

> ⚠️ CONTEXT.md is needed for proper commits (multi-repo awareness, understanding what was built, changelog context). Do NOT skip this.

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
- Assume single repo (current directory)
- Proceed with commit workflow
- Note in the commit summary that no CONTEXT.md was found

**If multi-repo:** Run the commit workflow for each repo that has changes.
**If single repo or no CONTEXT.md:** Run the workflow once for the current directory.

### 0.2 Determine Affected Repos

```bash
# For multi-repo: check which repos have changes
git -C ./backend status --short 2>/dev/null
git -C ./frontend status --short 2>/dev/null
# etc.
```

Or for single repo:
```bash
git status --short
```

Only proceed with repos that have uncommitted changes.

---

## Phase 1 — Branch Safety Check (Per Repo)

**This is the first thing to do for each repo. Do not skip it under any circumstance.**

```bash
git branch --show-current
# or for multi-repo:
git -C <repo_path> branch --show-current
```

### Protected Branch List

| Branch Pattern | Action |
|---------------|--------|
| `main` | ❌ **STOP** |
| `master` | ❌ **STOP** |
| `staging` | ❌ **STOP** |
| `develop` | ❌ **STOP** |
| `development` | ❌ **STOP** |
| `integration` | ❌ **STOP** |
| `release/*` | ❌ **STOP** |
| `HEAD` (detached) | ❌ **STOP** |
| anything else | ✅ Continue |

### If on a Protected Branch — STOP and Offer Help

Tell the user:

```
🚫 Commit refused — you're on the `<branch>` branch in <repo_name>.

Committing directly to protected branches (`main`, `master`, `staging`, `develop`, `integration`, `release/*`) is not allowed.

Would you like me to create a feature branch?

Suggested branch name: feature/<feature-or-division-name>

A) Yes, create `feature/<name>` and switch to it
B) I'll switch manually — tell me the command
C) Cancel the commit

Reply with A, B, or C.
```

If user picks A:
```bash
git checkout -b feature/<name>
# or for multi-repo:
git -C <repo_path> checkout -b feature/<name>
```

Then continue with the commit workflow.

If user picks B:
```
Run this command to create and switch to a feature branch:

  git checkout -b feature/<your-feature-name>

Then re-run the commit.
```

If user picks C: abort cleanly.

### If on a Feature Branch — Continue

Note the branch name. You'll reference it in the commit message and summary.

---

## Phase 2 — Find the Task File

Look for the planning file that corresponds to what was just implemented.

### 2.1 Check for explicit name

If the user named a division or feature (e.g., "commit division 2", "commit the auth feature"):
- Check `project_divisions.md` for the division name
- Find the matching `<task_name>.md` in `.sdlc/planning/`

### 2.2 Infer from branch name

If the user just said "commit this" with no name, infer from the branch name:

```bash
git branch --show-current
```

Strip common prefixes (`feature/`, `feat/`, `fix/`, `chore/`, `bugfix/`, `hotfix/`) and match the remainder against files in `.sdlc/planning/`.

For example: branch `feature/user-auth` → look for `user_auth.md` or `auth.md` in `.sdlc/planning/`.

### 2.3 List planning files if still unclear

```bash
ls .sdlc/planning/*.md 2>/dev/null | grep -v questions
```

If multiple task files exist and it's still ambiguous, ask the user:

```
Which task file should I base the commit message on?

Files found:
- user_auth.md
- payments.md
- lead_scoring.md

Reply with the file name or a number.
```

Wait for response. Then read the chosen file.

### 2.4 If no planning files exist

Proceed without a task file. Use git diff to infer what changed and write a best-effort commit message. Note in the summary that no planning file was found.

---

## Phase 3 — Read Git Status (Per Repo)

```bash
git status --short
git diff --stat HEAD
```

For multi-repo:
```bash
git -C <repo_path> status --short
git -C <repo_path> diff --stat HEAD
```

Categorize the changes:

| Symbol | Meaning |
|--------|---------|
| `M` | Modified existing file |
| `A` | New file staged |
| `??` | Untracked new file |
| `D` | Deleted file |
| `R` | Renamed file |

List all changed files grouped by category. This is what you'll show the user before staging.

---

## Phase 4 — Read the Task File

Read `.sdlc/planning/<task_name>.md` and extract:

- **Feature/Division name** → used as commit title
- **Goal** → used as commit body summary
- **Phase being committed** → if only one phase was implemented, note which
- **Completed TODOs** → cross-reference with changed files to see which tasks are done
- **Acceptance criteria** → note which are now met
- **Repos affected** → verify changes match expected repos

Also check if implementation files exist:
```
.sdlc/implementation/<task_name>/
```
If they do, note the phase names and match them to the changed files.

---

## Phase 5 — Confirm What to Stage (Per Repo)

Show the user a clear summary before touching anything:

```
📋 Ready to commit on branch: `feature/user-auth`

<For multi-repo: show per-repo breakdown>

**Repo: backend** (./backend)
**Task:** User Authentication (from user_auth.md)
**Goal:** JWT-based login and registration for API users

**Changed files to be staged:**
  ✅ src/routes/auth.py          (new)
  ✅ src/services/auth.py        (new)
  ✅ src/schema/auth.py          (new)
  ✅ src/models/user.py          (modified)
  ✅ tests/auth/test_auth.py     (new)
  ⚠️  .env.example                (modified — contains no secrets)

**Will NOT stage:**
  ⛔ .env                         (ignored — secrets file)
  ⛔ __pycache__/                  (ignored)

**Repo: frontend** (./frontend)
  ✅ src/pages/Login.tsx          (new)
  ✅ src/services/auth.ts         (new)

**Proposed commit message:**
─────────────────────────────────────
feat(auth): implement JWT authentication

- Add login and registration endpoints (POST /v1/auth/login, /v1/auth/register)
- Add JWT token generation and validation
- Add User model with hashed password storage
- Add Pydantic schemas for auth request/response
- Add Login page component in frontend
- Add test coverage for login, registration, and token validation

Branch: feature/user-auth
Plan: .sdlc/planning/user_auth.md
─────────────────────────────────────

Reply **yes** to commit, or tell me what to change.
```

Wait for confirmation. If the user says:
- `yes` / `ok` / `go` / `do it` → proceed to staging
- requests changes to the message → update and show again
- wants to exclude a file → note it and exclude from `git add`
- `no` / `cancel` → abort cleanly

---

## Phase 6 — Stage Files (Per Repo)

Stage all confirmed files:

```bash
git add <file1> <file2> ...
# or for multi-repo:
git -C <repo_path> add <file1> <file2> ...
```

**Never use `git add .` or `git add -A`** — always be explicit about what is staged. Build the file list from the confirmed changed files, excluding:

- `.env`, `.env.local`, `.env.*` (secret files)
- `*.pyc`, `__pycache__/` (build artifacts)
- `node_modules/` (dependencies)
- `.venv/`, `venv/` (virtual environments)
- `dist/`, `build/` (build output)
- Any file the user explicitly excluded

After staging, verify:

```bash
git status --short
```

Confirm staged files match what was confirmed with the user.

---

## Phase 7 — Build the Commit Message

### Format

Follow the **Conventional Commits** standard:

```
<type>(<scope>): <short title — max 72 chars>

<body — what was done, one bullet per logical change>

Branch: <branch-name>
Plan: .sdlc/planning/<task_name>.md
```

### Type selection

| Situation | Type |
|-----------|------|
| New feature or division | `feat` |
| Bug fix | `fix` |
| Refactor (no behaviour change) | `refactor` |
| Tests only | `test` |
| Infrastructure / config / tooling | `chore` |
| DB migration | `feat` or `chore` depending on context |
| Documentation | `docs` |

### Scope selection

Use the feature or module name: `auth`, `items`, `payments`, `db`, `routes`, etc.

### Title rules

- Max 72 characters
- Imperative mood: "implement", "add", "update", "remove" — NOT "implemented", "added"
- No trailing period
- Specific: "implement JWT login endpoint" not "add auth stuff"

### Body rules

- One bullet per logical change (not per file)
- Start each bullet with a verb: "Add", "Update", "Remove", "Fix", "Migrate"
- Reference the acceptance criteria or TODOs from the task file where relevant
- Do NOT list every file — describe the behaviour, not the file names
- For multi-repo commits, note which repo each change is in if helpful

### Examples of good commit messages

```
feat(auth): implement JWT login and registration

- Add POST /v1/auth/login — returns access + refresh tokens
- Add POST /v1/auth/register — validates email uniqueness, hashes password
- Add JWT bearer dependency for use on protected routes
- Add User model with bcrypt password hashing
- Add Login page component in frontend
- Add full test coverage for happy path and error cases

Branch: feature/user-auth
Plan: .sdlc/planning/user_auth.md
```

```
feat(items): add item CRUD with owner-scoped access

- Add items table with UUID PK, owner_id FK → users
- Add POST /v1/items/, GET /v1/items/, DELETE /v1/items/{id}
- Scope all queries to authenticated user — no cross-user data access
- Add request/response schemas
- Add 12 tests covering CRUD, auth enforcement, and 404 handling

Branch: feature/items-crud
Plan: .sdlc/planning/items_crud.md
```

---

## Phase 8 — Commit (Per Repo)

For single repo:
```bash
git commit -m "<title>" -m "<body>"
```

For multi-line bodies, write to a temp file inside the project:
```bash
git commit -F .sdlc/scratch/commit_msg.txt
```

For multi-repo, commit in each repo that has staged files:
```bash
git -C <repo_path> commit -m "<title>" -m "<body>"
```

Capture the output:
```bash
git log --oneline -1
```

Clean up any temp commit message files after committing.

---

## Phase 9 — Update Changelog

After a successful commit, check if a changelog entry should be appended:

```bash
cat .sdlc/changelogs/changelog.md 2>/dev/null
```

If the QA skill already wrote a changelog entry (during the QA phase), this step is already done.

If no changelog entry exists for this feature:

```bash
mkdir -p .sdlc/changelogs
```

Append an entry to `.sdlc/changelogs/changelog.md`:

```markdown
---

## <Feature Name>

**Date:** <YYYY-MM-DD>
**Branch:** <branch-name>
**Commit:** <short hash>

### Summary
<One sentence describing what was built.>

### Changes
- <Logical change 1>
- <Logical change 2>

### Repos
- <repo1>: <what changed>
- <repo2>: <what changed>
```

---

## Phase 10 — Show Commit Summary

Tell the user:

```
✅ Committed successfully!

<For single repo:>
**Commit:** abc1234
**Branch:** feature/user-auth
**Message:** feat(auth): implement JWT login and registration
**Files committed:** 5

<For multi-repo:>
**Commits:**
  📦 backend (./backend): abc1234 — feat(auth): implement JWT auth
     Files: 5
  📦 frontend (./frontend): def5678 — feat(auth): add login page
     Files: 2

**Changelog:** Updated `.sdlc/changelogs/changelog.md`

To push when ready:
  git push origin feature/user-auth
  <For multi-repo:>
  git -C ./backend push origin feature/user-auth
  git -C ./frontend push origin feature/user-auth

Or open a pull request when the full feature/division is complete.
```

Do NOT push. Do NOT suggest opening a PR automatically. Just show the push command as a reference.

---

## Safety Rules (never violate these)

| Rule | Reason |
|------|--------|
| Never commit on `main`, `master`, `staging`, `develop`, `integration`, or `release/*` | Protects protected branches |
| Never use `git add .` blindly | Prevents accidental staging of secrets or build artifacts |
| Never push | This skill is commit-only by design |
| Never commit `.env` files | Secrets must never enter git history |
| Always show the proposed commit message before committing | User must approve |
| Always verify branch before any git operation | First check, every time |
| For multi-repo: check branch in EVERY repo | Each repo could be on a different branch |
| Use `.sdlc/scratch/` for temp files, not `/tmp` | Keep everything in the project |

---

## Edge Cases

| Situation | Handling |
|-----------|----------|
| Nothing to commit (clean working tree) | Tell user, show `git status`, exit cleanly |
| Git not initialized | Tell user to run `git init` first |
| Merge conflict markers present | Refuse commit, tell user to resolve conflicts first |
| Staged files already exist (user pre-staged) | Respect what's staged, show it, confirm before committing |
| No planning file found | Write best-effort commit message from `git diff --stat`, note it |
| User is on a branch named `mainline` or `trunk` | Treat as protected — ask user to confirm it's a feature branch before proceeding |
| Partial implementation (only some phases done) | Note in commit body which phase/tasks are included |
| `.gitignore` missing | Warn user before staging, suggest creating one |
| Multi-repo: repos on different branches | Show warning, ask user to align branches or confirm per-repo |
| Multi-repo: only one repo has changes | Only commit in that repo, note which repos had no changes |

---

## Output

No files written to disk except changelog updates and temp commit message files (cleaned up after).

```
.sdlc/changelogs/changelog.md     ← appended with new entry
.sdlc/planning/<task_name>.md     ← read only, not modified
git log                           ← one new commit added per repo
```