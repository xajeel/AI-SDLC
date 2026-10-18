---
name: sdlc-init
description: "Set up AI-SDLC for a project — creates .sdlc/PROJECT.md (what it is, commands, git workflow, the model for each role, Bug Ledger and code-graph settings), .sdlc/CRAFT.md (the code rulebook: pinned stack + idioms, structure, style, config, security), .sdlc/STATE.md (feature log), and rule stubs (AGENTS.md) so ANY coding tool follows the same rules. Run once per project, before any other SDLC skill; run again to upgrade a 0.2.x setup. USE WHEN: 'set up sdlc', 'init project context', or any SDLC skill finds no .sdlc/ folder."
argument-hint: "Optionally: a PRD/description, a doc path, 'analyze the codebase', or --skip-<stage> / --unskip-<stage>"
---

# sdlc-init

Creates the files every other SDLC skill reads. PROJECT.md and CRAFT.md are loaded on every skill run, so every line must earn its place — facts and rules only, no prose.

CRAFT.md is the code rulebook: it is what makes ten build sessions — or ten different models — produce code that looks like one engineer wrote it. /plan and /spec design within its rules, /test and /build write by them, /qa checks the diff against them.

## Output contract

| File | Contains | Budget |
|---|---|---|
| `.sdlc/PROJECT.md` | What the project is, real commands, git workflow, models per role, ledger + graph settings | ≤ 40 lines |
| `.sdlc/CRAFT.md` | Pinned stack + idiom rules, structure, style, config & secrets, security, boundaries | ≤ 80 lines |
| `.sdlc/STATE.md` | Feature status table + cross-feature notes | grows ~1 line per feature |
| `AGENTS.md` (repo root) | ≤ 9-line pointer so any coding tool obeys the same rules | append-only |

## Procedure

**0. Stage toggle?** If the argument is only skip/unskip flags (`--skip-ship`, `--unskip-qa`, or plain words like "skip ship") AND `.sdlc/PROJECT.md` already exists, this is a toggle, not a re-init: update the `Skip stages:` line, confirm in one line, stop. Skippable: `test`, `qa`, `ship` — `plan`, `spec`, and `build` are the irreducible core; refuse anything else with one line. (Skipping `test` is discouraged — say so in the confirmation — it removes the independent-tester bias guard.) On a fresh init the same flags pre-set the line. Skipped stages are bypassed by stage handoffs and /factory; invoking a skipped skill directly still runs it.

**1. Existing setup check.** If `.sdlc/PROJECT.md` or `.sdlc/CRAFT.md` exists and is non-empty: show a 3-line summary, ask — update, replace, or cancel. Wait for the answer. PROJECT.md without a `Models:` line is a 0.2.x setup → offer **upgrade**: run only steps 5–6, add the new lines (`test-fast:`, `install:`, `Models:`, `Parallel:`, `Ledger project:`, `Code graph:`), rewrite the `Agents:` line to the new template (it gains `review=review`), add the new `.gitignore` lines, convert BUGS.md (see Edge cases), keep everything else.

**2. Gather facts — use the first source that applies:**
- **PRD or description provided** → read it. Extract: purpose, users, features, stack, constraints.
- **Codebase exists** → detect, don't interrogate:
  - Read manifests AND lockfiles (`pyproject.toml` + `uv.lock`/`poetry.lock`/`requirements*.txt`, `package.json` + its lockfile, `go.mod`, `Cargo.toml`, …), `docker-compose.yml`, `.env.example`, README.
  - Read the entry point, 2–3 representative source files (one per layer), and 1 test file.
  - Do NOT scan the whole codebase — about 12 file reads detect the facts. Init records facts; it does not plan, so it needs no more.
- **Neither (greenfield, no PRD)** → question mode; steps 3–5 collect everything.

**3. Rules source — one MCQ, always asked.** "How should the code-craft rules be set?"
- A) Derive them from the codebase and show me `(Recommended when code exists)`
- B) Ask me questions and build them from my answers `(Recommended for a new project)`
- C) Propose best-practice rules yourself; I'll review before anything is written
- D) I'll provide my own rules — pasted here or a file path
Blank answer → the recommended option for the situation.

**4. Git workflow — one MCQ, always asked.** On an existing repo, look first (`git log --oneline -15`, branch names) and pre-select what the history shows. "How does this project manage branches and commits?"
- A) Feature branches off the default branch, PRs, Conventional Commits `(Recommended / default)`
- B) GitFlow — develop + feature/release/hotfix branches
- C) Trunk-based — short-lived branches, squash-merge to main
- D) My own — describe it (branch pattern, commit format, merge target)
Blank answer → A, marked `(assumed)`. The answer becomes PROJECT.md's `## Git workflow` section — /build branches by it, /ship commits and opens PRs by it, always.

**5. Models — one MCQ, always asked.** Three roles: **strong** (plan, spec, test, qa), **mid** (build), **review** (the reviewer that tries to break plans and diffs). The review model must differ from strong and mid — a model does not catch its own blind spots. "Which models run each role?"
- A) This tool's defaults `(Recommended)` — on Claude Code: strong=`opus` (Opus 5.5) · mid=`sonnet` (Sonnet 5.5) · review=`claude-opus-4-8`; on another tool, its best model · a faster model · a third model
- B) One model for strong and mid, a different one for review
- C) My own — name each
- D) This tool cannot pick a model per subagent → `review=same` (weaker guard: fresh context only)
Also set `Parallel:` — how many features /factory may build at once (default 2; each one costs tokens).
The agent files carry the defaults (Claude Code: planner, tester, qa = `opus` · builder = `sonnet` · reviewer = `claude-opus-4-8`). A chosen model that differs → edit the `model:` line of `.claude/agents/sdlc-<role>.md` (or `.cursor/agents/sdlc-<role>.md`). The skills spawn these agents by name. Agent files missing → tell the user to run `ai-sdlc install`.

**6. Bug memory and code graph — check, never install without a yes.**
- **Bug Ledger** tools available (`list_areas` answers) → set `Ledger project:` to the repo's root folder name in lowercase (confirm it in the approval gate; worktrees must never change it). Show the existing areas. `.sdlc/BUGS.md` has `## Pending` entries → offer to sync them now (show each, record on yes). Offer once: "Install the Bug Ledger guardrails — Semgrep rules in `.bugledger/` plus one new CI file?" → on yes, call `get_guardrails` and follow its instructions.
- **Not available** → still set `Ledger project:`, and tell the user in one line: `Connect Bug Ledger: claude mcp add bugledger -- uvx bugledger-mcp@0.1.2 (or run: ai-sdlc install)`. Until then bugs go to `.sdlc/BUGS.md`.
- **Code graph** — codebase-memory-mcp tools available → `Code graph: codebase-memory-mcp`. Not available → offer once: "Optional: codebase-memory-mcp gives agents a call graph for faster caller search and a better QA blast-radius check. It is a local MIT binary. Install it? (`npm install -g codebase-memory-mcp`, then `codebase-memory-mcp install`)". Run the commands only on an explicit yes; otherwise `Code graph: none`.

**7. Build the draft rules.**
- **From code (A):** versions come from lockfiles/manifests — exact, never guessed. Structure comes from the real tree. Style rules only from patterns actually observed. Config rules from how the code reads settings today.
- **From answers (B):** MCQs for what steps 1–2 didn't answer: language + version, framework, DB, package manager, test runner, layout, auth approach, deploy target. Options A–D, one `(Recommended)`; blank = recommended. ≤ 3 questions → chat; > 3 → `.sdlc/questions.md` with `Answer:` lines, wait for **done**, read, delete. Hard cap: 7 questions.
- **From the user (D):** take their rules verbatim; MCQ only the gaps.
- **Best practice (C):** the boring industry-standard option for the project type.
- **Version pinning — greenfield, all paths:** pin the newest stable you can confirm — registry check (`pip index versions <pkg>`, `npm view <pkg> version`) or web search when tools allow; otherwise pin the newest you know, marked `(verify)` — the first build task must then confirm and correct CRAFT.md.
- **Idiom rules — all paths:** for every framework/ORM with a breaking major, one line naming the modern API and forbidding the legacy one — e.g. "SQLAlchemy 2.x — `DeclarativeBase`, `Mapped[]`, `mapped_column()`; 1.x style forbidden." This stops a model writing last-generation code against a current library.
- **Simplicity rules — all paths, non-negotiable:** the Style section always includes the four readability bullets pre-filled in the template below. They exist so any developer can trace the code — never drop them.
- **`test-fast:`** — a faster subset command when the runner has one (`pytest --testmon`, `vitest related`, `jest --onlyChanged`, a per-package test), else `same as test`.

**8. Approval gate — never skip.** Show the draft in ≤ 18 lines: pinned stack, folder tree, git workflow, models per role, Ledger project, code graph, and the 5 rules that matter most. Ask: approve, or edit what? Apply edits and re-show until approved. Only then write files.

**9. Write the three .sdlc files** from the templates below.
- Style: max 12 bullets, each mechanically checkable.
- Commands must be real: run the test command once to confirm (skip on greenfield).
- No placeholders left in the final files.
- Add to `.gitignore` (create or append, never duplicate a line): `.sdlc/.stage`, `.sdlc/questions.md`, `.sdlc/RUN.md`, `.sdlc/specs/*/shots/`.

**10. Rule stubs — make every coding tool obey the same rulebook.** Write this block to `AGENTS.md` at the repo root (create it, or append if the file exists — never overwrite existing content):

```markdown
## AI-SDLC rules
Before writing any code in this repo:
1. Read `.sdlc/CRAFT.md` and follow every rule — structure, style, config, security.
2. Read `.sdlc/PROJECT.md` — use its commands and its Git workflow for branches/commits.
3. Feature work lives in `.sdlc/specs/<feature>/` — spec.md is the task authority.
4. Before you fix a bug, search bug memory: Bug Ledger `search_bugs`, or `.sdlc/BUGS.md`.
Keep code boring and readable: minimal comments, no long docstrings, no clever one-liners.
```

If `CLAUDE.md` or `.cursor/rules/` already exist, append/add the same pointer there so Claude Code, Cursor, Codex, Windsurf — any tool — lands on the same rules.

**11. Report in ≤ 7 lines:** files created, pinned stack, git workflow, models per role, Bug Ledger connected or not, code graph, skipped stages (if any), and the next step — `/roadmap` for a whole project, `/plan <ticket>` to diagnose a bug or design a feature, `/design` for UI work, or `/factory <feature>` to run the whole pipeline.

## PROJECT.md template

```markdown
# <project name>
<one line: what it is and who uses it>

## Stack
<one line — full pinned versions live in CRAFT.md>

## Commands
- test: <exact command>
- test-fast: <faster subset command | same as test>
- install: <exact dependency install command — /factory runs it in every worktree>
- lint: <exact command>
- run: <exact command>
- migrate: <exact command or "n/a">

## Git workflow
- Branches: <pattern, e.g. "feat/<feature>, fix/<feature> off main">
- Commits: <format, e.g. "Conventional Commits">
- Merge: <target + method, e.g. "PR to main, squash">

> Repos: <single | list each path + purpose if multi-repo>
> Skip stages: none   <!-- test, qa, ship — handoffs and /factory bypass these -->
> Agents: plan=strong · spec=strong · test=strong · build=mid · qa=strong · review=review
> Models: strong=<model> · mid=<model> · review=<model>
>   <!-- review must differ from strong and mid; "review=same" only when the tool cannot pick a model per subagent.
>        Every stage runs as its own FRESH agent — that separation is the bias guard. -->
> Parallel: 2          <!-- max features /factory builds at once -->
> Ledger project: <slug>   <!-- Bug Ledger `project`; never the folder name of a worktree -->
> Code graph: none | codebase-memory-mcp
```

## CRAFT.md template

```markdown
# Code Craft — <project>
Source: <derived from codebase | agreed with user> · <YYYY-MM-DD>

## Stack — pinned
- <language + version> · <package manager>
- <framework + version> — <modern idiom rule>
- <DB + ORM + version> — <idiom rule: modern API named, legacy API forbidden>
- <test runner + version>
> New dependency → latest stable, exact version recorded here in the same task.

## Structure
- <dir>/ → <one-line responsibility, e.g. "models/ → SQLAlchemy models only">
- <dir>/ → <…>
- <test location + naming, e.g. "tests/<area>/test_*.py">
- One concern per file: models, schemas, routes, services never share a file.
- New files go in the directory matching their concern — never at repo root.

## Style
- Comments only for what the code cannot say — no narration, no restating the line below.
- Docstrings one line, public API only. No essay docstrings.
- Boring beats clever: no dense one-liners, no unneeded abstractions, no premature patterns.
- Functions do one job and are short enough to read whole; a mid-level dev can trace any file top to bottom.
- <up to 8 more project-specific bullets, each mechanically checkable>

## Config & secrets
- All config read from environment variables in ONE settings module: <path>
- Every new key → `.env.example` with a placeholder, in the same task that introduces it
- Never hardcode secrets, URLs, ports, or keys in source

## Security baseline
- Passwords hashed with <bcrypt cost 12 | argon2id> — never logged, never returned
- DB access only through the ORM — never build SQL strings from input
- Every request body validated at the boundary (<validation tool>)
- Every non-public route checks auth before touching data
- Error responses never leak stack traces, queries, or internals

## Boundaries
- Never edit: <e.g. migrations/versions/*, generated files, lockfiles by hand>
- Never commit: .env, secrets, build artifacts — .env.example (placeholders only) IS committed
```

## STATE.md template

```markdown
# State

| Feature | Spec | Status | Shipped |
|---|---|---|---|

## Notes
<!-- cross-feature facts an implementer must know; one line each -->
```

## Edge cases

- Existing code contradicts best practice → the codebase wins: record what IS, mark the divergence `(legacy)` in Style. Rules the code doesn't follow just teach /build to drift.
- Multiple languages in the workspace → list all in Stack, ask which is primary (1 MCQ).
- Monorepo / multi-repo → one PROJECT.md + CRAFT.md at the workspace root; Structure lists each repo path + purpose.
- User says "skip questions" → recommended defaults, marked `(assumed)` in CRAFT.md — but the step-8 approval gate still runs.
- **Old BUGS.md** (0.2.x `## B<n> — …` entries with What went wrong / Why / How to avoid) → convert each `fixed` entry to a `## Pending` entry in the record_bug fields (symptom ← What went wrong, root_cause ← Why, feature_area ← ask once per entry or reuse a ledger area, fix_ref ← none, note ← "legacy"). Move `open` entries under `## Legacy open` — an open bug is not a ledger record. Then offer the sync.
