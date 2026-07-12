---
name: qa
description: "Mechanical QA gate for a built feature — re-runs every task Verify, runs Acceptance checks, full-suite regression, and a convention diff scan, then appends a verdict to the spec. Failures become fix-tasks /build can execute. USE WHEN: 'qa X', 'test the feature', 'verify the implementation', after /build finishes."
argument-hint: "The feature to QA (must have a spec in .sdlc/specs/)"
---

# qa

Verifies a feature against its own spec. Mechanical by design: the spec already defines every check — QA executes them, it does not wander the codebase. QA reports; /build fixes.

## Procedure

**1. Load** `.sdlc/PROJECT.md` + the spec. Spec name unclear → list `.sdlc/specs/` and ask.

**2. Task verifies.** Re-run the Verify command of every `[x]` task. Record pass/fail per task.

**3. Acceptance checks.** Run each command under Acceptance checks; compare actual vs expected. If a check needs a live app, start it with PROJECT.md's `run:` command and stop it afterwards.

**4. Regression.** Run the full `test:` suite. Any failure outside this feature's own tests — especially in areas named under `Touches → Risk` — is a regression: always CRITICAL, always blocks PASS.

**5. Coverage gap.** Any acceptance check not covered by a test in the suite → write ONE minimal test for it (following the project's test pattern), run it, keep it.

**6. Diff scan.** `git diff --name-only` (plus `git status --short` for untracked). Exactly two checks:
- Every changed file appears in some task's `Files:` list — unlisted changes get flagged.
- Each changed file respects PROJECT.md Conventions and Boundaries — walk the bullets mechanically.

**7. Verdict.**
- **PASS** — all task verifies, acceptance checks, and the suite are green; no unlisted changes. Convention nits alone don't block — list them as notes.
- **FAIL** — anything else. For each failure, append a fix-task to the spec's Tasks section — `### [ ] F1 — fix: <what>` with Files / Do / Verify filled in — so `/build <feature>` can execute the fixes directly.

**8. Append to the spec's QA log** (≤ 20 lines per run):

```markdown
### QA <date> — PASS | FAIL
Task verifies: 6/6 · Acceptance: 3/3 · Suite: 42 passed, 0 failed · Regressions: 0
Unlisted changes: none
Failures: <one line per F-task, or "none">
Notes: <convention nits, or "none">
Try it:
1. <command or click-path with concrete sample data>
2. <expected result>
```

The **Try it** block is 2–5 steps any human — technical or not — can follow to see the feature working: concrete sample data, exact expected outcome.

**9. Report in ≤ 8 lines:** verdict, the counts line, failures if any, next step — `/build <feature>` to execute fixes, or `/ship <feature>` on PASS.

## Rules
- Never PASS with a failing acceptance check or a regression. There is no "pass with warnings" for those.
- Never fix code here — failures become F-tasks for /build. (Sole exception: the minimal coverage test in step 5.)
- Scope is this feature's diff plus the test suite — do not re-review the whole codebase.
- Environment blocks a check (no DB, no network)? Record it as SKIPPED with the reason — never silently count it as passing.
