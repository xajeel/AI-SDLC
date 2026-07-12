---
name: sdlc-init
description: "Set up AI-SDLC for a project — creates .sdlc/PROJECT.md (stack, layout, commands, conventions) and .sdlc/STATE.md (feature log). Run once per project, before any other SDLC skill. USE WHEN: 'set up sdlc', 'init project context', or any SDLC skill finds no .sdlc/ folder."
argument-hint: "Optionally: a PRD/description, a doc path, or 'analyze the codebase'"
---

# sdlc-init

Creates the two files every other SDLC skill reads. Both are loaded on every skill run, so every line must earn its place — facts only, no prose.

## Output contract

| File | Contains | Budget |
|---|---|---|
| `.sdlc/PROJECT.md` | Stack, layout, commands, conventions, boundaries | ≤ 80 lines |
| `.sdlc/STATE.md` | Feature status table + cross-feature notes | grows ~1 line per feature |

## Procedure

**1. Existing setup check.** If `.sdlc/PROJECT.md` exists and is non-empty: show a 3-line summary, ask — update, replace, or cancel. Wait for the answer.

**2. Gather facts — use the first source that applies:**
- **PRD or description provided** → read it. Extract: purpose, users, features, stack, constraints.
- **Codebase exists** → detect, don't interrogate:
  - Read manifests (`package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml` / …), `docker-compose.yml`, `.env.example`, README.
  - Read the entry point, 2–3 representative source files (one per layer), and 1 test file.
  - Do NOT scan the whole codebase — ~10 file reads maximum.
- **Neither (greenfield, no PRD)** → question mode; step 3 collects everything.

**3. Close remaining gaps with MCQs.** Only ask what steps 1–2 didn't answer and PROJECT.md needs: language + version, framework, DB, package manager, test runner, repo layout, auth approach, deploy target.
- Format: options A–D, one marked `(Recommended)` where a best practice exists. Blank answer = recommended.
- ≤ 3 questions → ask directly in chat.
- \> 3 questions → write `.sdlc/questions.md` (same A–D format, each with an `Answer:` line), tell the user to fill it and reply **done**. Wait, read the answers, then delete the file.
- Hard cap: 7 questions.

**4. Write `.sdlc/PROJECT.md`** from the template below.
- Conventions: max 12 bullets, each mechanically checkable ("type hints on all functions" — not "write clean code").
- Commands must be real: run the test command once to confirm it works (skip on greenfield).
- No placeholders left in the final file.

**5. Write `.sdlc/STATE.md`** from the template below (empty table).

**6. Report in ≤ 6 lines:** files created, detected stack, and the next step — `/roadmap` for a whole project, `/spec <feature>` for one feature.

## PROJECT.md template

```markdown
# <project name>
<one line: what it is and who uses it>

## Stack
- <language + version, package manager>
- <framework> | <database + ORM> | <frontend or "none">
- <anything else an implementer must know: queue, cache, auth method>

## Layout
- <dir>/ → <responsibility + the one rule that matters, e.g. "routes/ → HTTP only, delegate to services">
- <dir>/ → <…>
- <test location + naming, e.g. "tests/<area>/test_*.py">
> Repos: <single | list each path + purpose if multi-repo>

## Commands
- test: <exact command>
- lint: <exact command>
- run: <exact command>
- migrate: <exact command or "n/a">

## Conventions
- <max 12 checkable bullets>

## Boundaries
- Never edit: <e.g. migrations/versions/*, generated files>
- Never commit: .env*, secrets, build artifacts
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
- Multiple languages in the workspace → list all in Stack, ask which is primary (1 MCQ).
- Monorepo / multi-repo → one PROJECT.md at the workspace root; Layout lists each repo path + purpose.
- User says "skip questions" → use recommended defaults, mark them `(assumed)` in PROJECT.md.
