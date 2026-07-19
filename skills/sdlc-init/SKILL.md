---
name: sdlc-init
description: "Set up AI-SDLC for a project — creates .sdlc/PROJECT.md (what it is, commands), .sdlc/CRAFT.md (the code rulebook: pinned stack + idioms, folder structure, style, config & secrets, security), and .sdlc/STATE.md (feature log). Run once per project, before any other SDLC skill. USE WHEN: 'set up sdlc', 'init project context', or any SDLC skill finds no .sdlc/ folder."
argument-hint: "Optionally: a PRD/description, a doc path, 'analyze the codebase', or --skip-<stage> / --unskip-<stage>"
---

# sdlc-init

Creates the three files every other SDLC skill reads. PROJECT.md and CRAFT.md are loaded on every skill run, so every line must earn its place — facts and rules only, no prose.

CRAFT.md is the code rulebook: it is what makes ten build sessions — or ten different models — produce code that looks like one engineer wrote it. /spec plans within its rules, /build writes code by them, /qa checks the diff against them.

## Output contract

| File | Contains | Budget |
|---|---|---|
| `.sdlc/PROJECT.md` | What the project is + real commands | ≤ 30 lines |
| `.sdlc/CRAFT.md` | Pinned stack + idiom rules, folder structure, style, config & secrets, security baseline, boundaries | ≤ 80 lines |
| `.sdlc/STATE.md` | Feature status table + cross-feature notes | grows ~1 line per feature |

## Procedure

**0. Stage toggle?** If the argument is only skip/unskip flags (`--skip-ship`, `--unskip-qa`, or plain words like "skip ship") AND `.sdlc/PROJECT.md` already exists, this is a toggle, not a re-init: update the `Skip stages:` line in PROJECT.md, confirm in one line, stop — nothing else runs. Only `qa` and `ship` can be skipped: `spec` and `build` are the irreducible core, and `/roadmap` is already optional — refuse anything else with one line. On a fresh init, the same flags simply pre-set the line. Skipped stages are bypassed by stage handoffs and by /automate; invoking a skipped skill directly still runs it.

**1. Existing setup check.** If `.sdlc/PROJECT.md` or `.sdlc/CRAFT.md` exists and is non-empty: show a 3-line summary, ask — update, replace, or cancel. Wait for the answer.

**2. Gather facts — use the first source that applies:**
- **PRD or description provided** → read it. Extract: purpose, users, features, stack, constraints.
- **Codebase exists** → detect, don't interrogate:
  - Read manifests AND lockfiles (`pyproject.toml` + `uv.lock`/`poetry.lock`/`requirements*.txt`, `package.json` + its lockfile, `go.mod`, `Cargo.toml`, …), `docker-compose.yml`, `.env.example`, README.
  - Read the entry point, 2–3 representative source files (one per layer), and 1 test file.
  - Do NOT scan the whole codebase — ~12 file reads maximum.
- **Neither (greenfield, no PRD)** → question mode; steps 3–4 collect everything.

**3. Rules source — one MCQ, always asked.** "How should the code-craft rules be set?"
- A) Derive them from the codebase and show me `(Recommended when code exists)`
- B) Ask me questions and build them from my answers `(Recommended for a new project)`
- C) Propose best-practice rules yourself; I'll review before anything is written
- D) I'll provide my own rules — pasted here or a file path
Blank answer → the recommended option for the situation.

**4. Build the draft rules.**
- **From code (A):** versions come from lockfiles/manifests — exact, never guessed. Structure comes from the real tree. Style rules only from patterns actually observed in the source (naming, error handling, imports, typing). Config rules from how the code reads settings today.
- **From answers (B):** MCQs for what steps 1–2 didn't answer: language + version, framework, DB, package manager, test runner, layout, auth approach, deploy target. Options A–D, one `(Recommended)`; blank = recommended. ≤ 3 questions → ask in chat; > 3 → write `.sdlc/questions.md` with `Answer:` lines, wait for **done**, read, delete it. Hard cap: 7 questions.
- **From the user (D):** take their rules verbatim; MCQ only the gaps.
- **Best practice (C):** choose the boring industry-standard option for the project type.
- **Version pinning — greenfield, all paths:** pin the newest stable version you can confirm — check the registry (`pip index versions <pkg>`, `npm view <pkg> version`) or web search when tools allow; otherwise pin the newest you know and mark it `(verify)` — the first build task must then confirm installed versions and correct CRAFT.md.
- **Idiom rules — all paths:** for every framework/ORM with a breaking major version, write a one-line idiom rule naming the modern API and forbidding the legacy one — e.g. "SQLAlchemy 2.x — `DeclarativeBase`, `Mapped[]`, `mapped_column()`; 1.x style (`declarative_base()`, `Column = ...`) forbidden." This is what stops a model from writing last-generation code against a current library.

**5. Approval gate — never skip.** Show the draft in ≤ 15 lines: the pinned stack, the folder tree, and the 5 rules that matter most. Ask: approve, or edit what? Apply edits and re-show until approved. Only then write files.

**6. Write the three files** from the templates below.
- Style: max 12 bullets, each mechanically checkable ("type hints on all functions" — not "write clean code").
- Commands must be real: run the test command once to confirm it works (skip on greenfield).
- No placeholders left in the final files.

**7. Report in ≤ 6 lines:** files created, pinned stack, skipped stages (if any), and the next step — `/roadmap` for a whole project, `/spec <feature>` for one feature, or `/automate <feature>` to run a feature's whole cycle hands-free.

## PROJECT.md template

```markdown
# <project name>
<one line: what it is and who uses it>

## Stack
<one line — full pinned versions live in CRAFT.md>

## Commands
- test: <exact command>
- lint: <exact command>
- run: <exact command>
- migrate: <exact command or "n/a">

> Repos: <single | list each path + purpose if multi-repo>
> Skip stages: none   <!-- qa, ship, or both — handoffs and /automate bypass these; toggle via /sdlc-init --skip-<stage> / --unskip-<stage> -->
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
- <max 12 mechanically checkable bullets>

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
- Existing code contradicts best practice → the codebase wins: record what IS, mark the divergence `(legacy)` in Style. Rules the code doesn't actually follow just teach /build to drift.
- Multiple languages in the workspace → list all in Stack, ask which is primary (1 MCQ).
- Monorepo / multi-repo → one PROJECT.md + CRAFT.md at the workspace root; Structure lists each repo path + purpose.
- User says "skip questions" → recommended defaults, marked `(assumed)` in CRAFT.md — but the step-5 approval gate still runs.
