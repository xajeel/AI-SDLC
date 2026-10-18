---
name: build
description: "Implement a spec task-by-task with a verify gate and a self-review after every task, and a test checkpoint every 2 tasks. The tester's tests are the target: red until built, and never edited by build — a suspect test becomes a challenge for /test, not an edit. USE WHEN: 'build X', 'implement the spec', 'continue building X', after /test has written the tests. Executes the spec exactly — it does not redesign. Resumable: continues from the first unchecked task."
argument-hint: "The feature to build (must have .sdlc/specs/<feature>/spec.md)"
---

# build

Executes `.sdlc/specs/<feature>/spec.md`. The spec is the authority: `Files:` lists are a whitelist, `Do` bullets the instructions, `Verify` commands the gate, and the `Tests` section lists tester-owned files this skill runs but never edits. Runs on the mid model in ONE agent — tasks inside a feature are sequential, never split across parallel agents. Invoked by you → it runs in this conversation; start a fresh session so earlier context does not bias it. Invoked by /factory → it runs as the subagent `sdlc-builder` and cannot ask you anything: where this skill says wait for the user, it stops and reports. Progress lives in the spec's checkboxes — a fresh session resumes at the first unchecked task.

## Setup

1. Read `.sdlc/PROJECT.md`, `.sdlc/CRAFT.md`, the spec, and `.sdlc/DESIGN.md` for UI tasks. (Legacy layout: a single `.sdlc/specs/<feature>.md` file → treat it as spec.md.) Spec missing → run /spec first. Do not improvise a plan.
2. **Bug memory:** `get_patterns(feature_area=<spec Area>, project=<Ledger project>)` when the ledger tools exist, plus `## Pending` in `.sdlc/BUGS.md`. Never reintroduce a recorded bug in the files you are about to touch.
3. Spec has no `Tests` section → say so and recommend `/test <feature>` first; continue only if the user explicitly says to build without it — or PROJECT.md's `Skip stages:` lists `test` (then note it in the report).
4. If spec Status is `draft`, set it to `building`. Write `.sdlc/.stage` = `build <feature>`.
5. Branch per PROJECT.md's `## Git workflow` (no section → default: `feat/<feature>` off the default branch). On a protected branch → create and switch before touching anything. Under /factory the branch and worktree already exist — use them.

## Task loop — repeat until no `[ ]` tasks remain

1. **Pick** the first `[ ]` task whose `Needs:` tasks are all `[x]`.
2. **Read** the files in its `Files:` and `Pattern:` lines first. Read anything else you need to understand a contract, a caller in `Touches`, or a library API — never the whole codebase. **Edit** only the `Files:` list.
3. **Implement** exactly what the Do bullets say:
   - Mirror the Pattern file's style: naming, error handling, imports, structure.
   - Obey every CRAFT.md rule: structure, style, config & secrets, security baseline, boundaries. UI code uses only DESIGN.md tokens and components.
   - Write code for the PINNED versions. Not sure how an API behaves in that version → read the installed package source or its docs before you use it. Never code from memory of another version.
   - Write boring, readable code: comments only where the code can't say it (no narration, no long docstrings), no clever one-liners, no drive-by abstractions. A reviewer on a different model will try to break this diff — write for that reviewer.
   - Touch ONLY the listed files. Another file needs changing → STOP, report which and why, propose the spec edit, wait for approval.
   - Spec conflicts with CRAFT.md → STOP, report, propose the spec fix, wait. Never pick one silently.
   - No new dependencies unless the task names them. No drive-by refactors. No TODO/FIXME placeholders.
4. **Verify.** Run the task's Verify command, then the tester's tests covering this task's contracts — they should flip red → green. Trust exit codes and output, never your expectation.
   - Pass → continue.
   - Fail → first call `search_bugs` with the key words of the error (when the ledger tools exist) — the fix may be on record. Then fix the CODE and rerun, up to 3 attempts. Still failing → mark the task `[!]` in the spec, STOP, report the exact failing output.
   - A tester test looks WRONG (contradicts the spec, impossible assertion) → STOP the task and file a **test challenge**: test file + name, why it's wrong, the spec line it contradicts. /test adjudicates — build never edits, skips, or weakens the test itself.
5. **Self-review the task's diff** before marking it done. Re-read every changed line against the Do bullets and answer: Bug? (logic, null/empty, boundaries) · Missing? (a Do bullet not done) · Confusing? (a line a mid-level dev could misread) · Crash? (each error path the spec names is handled) · Assumed? (an API or behavior you did not check). Fix, rerun Verify.
6. **Mark done.** Flip `[ ]` to `[x]`. One line to the user: `T3 done — <name> (verify: pass)`.
7. **Checkpoint** — after every 2 completed tasks run PROJECT.md's `test-fast:` command (or `test:` when there is none); after the final task run the full `test:` command.
   - Tester tests for NOT-yet-built tasks are expected red — not failures.
   - Anything that passed before and fails now is a regression → fix NOW, before the next task. Not fixed in 3 attempts → STOP and report.
   - Final checkpoint: the ENTIRE suite green, tester tests included. A tester test still red after its task is `[x]` gets the same 3-attempt limit — then stop, or challenge it.

## Finish

When every task is `[x]` and the final checkpoint is fully green:
1. Set spec Status: `qa`. Delete `.sdlc/.stage`.
2. Report in ≤ 6 lines: tasks completed, files created/edited, suite result (tester tests: n red → n green), next step: "Run `/qa <feature>`." — unless PROJECT.md's `Skip stages:` lists qa, then point to `/ship <feature>`; if ship is skipped too, update STATE.md to `done` and report the feature complete.

On any STOP, leave `.sdlc/.stage` in place and report: the task, the exact output, and the command to resume. Under /factory, the factory parks the feature and continues with others.

## Hard rules

- Never mark a task `[x]` without its Verify passing. No exceptions, no "fix later".
- Never edit, delete, or weaken a file in the spec's `Tests` section — not with an edit tool, not with a shell command. Suspect tests become challenges for /test.
- Never hardcode a secret or config value — settings module + `.env.example`, same task.
- Never use a legacy-version API when CRAFT.md pins a newer major.
- Comments and docstrings minimal; code a mid-level developer can trace top to bottom. No spaghetti, no cleverness for its own sake.
- Stop conditions are stops, not suggestions: unlisted file needed · 3 failed attempts · unfixable regression · missing spec · test challenge pending.
- Fix-tasks appended by /qa (`F1`, `F2`, …) are ordinary tasks — the same loop executes them.
