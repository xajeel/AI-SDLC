---
name: build
description: "Implement a spec task-by-task with a verify gate after every task and a full-suite checkpoint every 2 tasks. USE WHEN: 'build X', 'implement the spec', 'continue building X', or after /spec produced .sdlc/specs/<feature>.md. Executes the spec exactly — it does not redesign. Resumable: always continues from the first unchecked task."
argument-hint: "The feature to build (must have a spec in .sdlc/specs/)"
---

# build

Executes `.sdlc/specs/<feature>.md`. The spec is the authority: `Files` lists are a whitelist, `Do` bullets are the instructions, `Verify` commands are the gate. Progress lives in the spec's checkboxes, so a fresh session resumes exactly where the last one stopped.

## Setup

1. Read `.sdlc/PROJECT.md` (commands), `.sdlc/CRAFT.md` (the code rulebook: pinned stack + idiom rules, structure, style, config & secrets, security, boundaries), and the spec. Spec missing → tell the user to run /spec first. CRAFT.md missing → run sdlc-init first. Do not improvise a plan.
2. If spec Status is `draft`, set it to `building`.
3. `git branch --show-current` — on main/master/develop/staging/release/* → create and switch to `feat/<feature>` before touching anything.

## Task loop — repeat until no `[ ]` tasks remain

1. **Pick** the first `[ ]` task, top to bottom.
2. **Read only** the files in its `Files:` and `Pattern:` lines — not the whole codebase.
3. **Implement** exactly what the Do bullets say:
   - Mirror the Pattern file's style: naming, error handling, imports, structure.
   - Obey every CRAFT.md rule: structure (one concern per file, files in their directory), style bullets, config & secrets, security baseline, boundaries.
   - Write code for the PINNED versions — check CRAFT.md's idiom line before using any framework/ORM API (e.g. SQLAlchemy 2.x `Mapped[]` style when 2.x is pinned — never 1.x `Column` style).
   - Touch ONLY the listed files. If another file needs changing → STOP, report which file and why, propose the spec edit, wait for approval.
   - Spec conflicts with CRAFT.md (wrong directory, hardcoded value, legacy API) → STOP, report the conflict, propose the spec fix, wait. Never pick one silently.
   - No new dependencies unless the task names them. No drive-by refactors. No TODO/FIXME placeholders.
4. **Verify.** Run the task's Verify command.
   - Pass → continue.
   - Fail → fix and rerun, up to 3 attempts. Still failing → mark the task `[!]` in the spec, STOP, report the exact failing output.
5. **Mark done.** Flip `[ ]` to `[x]` in the spec. Tell the user one line: `T3 done — <name> (verify: pass)`.
6. **Checkpoint** — after every 2 completed tasks and after the final task: run the full `test:` command from PROJECT.md.
   - A previously-passing test now failing is a regression → fix it NOW, before the next task. Not fixed in 3 attempts → STOP and report.

## Finish

When every task is `[x]` and the final checkpoint is green:
1. Set spec Status: `qa`.
2. Report in ≤ 6 lines: tasks completed, files created/edited, suite result, then: "Run `/qa <feature>`."

## Hard rules
- Never mark a task `[x]` without its Verify passing. No exceptions, no "fix later".
- Never hardcode a secret or config value — read it from the environment via the settings module and add the key to `.env.example` in the same task.
- Never use a legacy-version API when CRAFT.md pins a newer major — the idiom lines under Stack are law.
- Never weaken a failing test to make it pass — fix the code. If the test itself is wrong, say so and ask.
- Stop conditions are stops, not suggestions: unlisted file needed · 3 failed verify attempts · unfixable regression · missing spec.
- Fix-tasks appended by /qa (`F1`, `F2`, …) are ordinary tasks — the same loop executes them.
