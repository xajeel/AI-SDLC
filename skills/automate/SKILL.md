---
name: automate
description: "Hands-free cycle for ONE feature: runs /spec → /build → /qa back-to-back with zero questions — every design choice takes the recommended production-standard option and is recorded in the spec marked (auto). Honors PROJECT.md's Skip stages line. Stops only for real blockers. USE WHEN: 'automate <feature>', 'run the whole flow for X', 'build X end to end without asking me'."
argument-hint: "The feature to run end-to-end (e.g. 'user-auth', 'roadmap feature 2', 'payments --ship')"
---

# automate

Runs the full cycle for one feature without waiting for the user between stages. Each stage follows its own SKILL.md to the letter — automate changes only WHO answers: every question a stage would normally ask is answered here, by rule, and logged so the user can audit every choice afterwards.

## Setup

1. Read `.sdlc/PROJECT.md`, `.sdlc/CRAFT.md`, `.sdlc/STATE.md`, and `.sdlc/BUGS.md` if present. PROJECT.md or CRAFT.md missing → stop: run /sdlc-init first (init is never automated — its approval gate needs a human).
2. Resolve the feature: from the argument, or by name/number from a `todo` roadmap entry. Already `done` in STATE.md → stop and say so. A spec already exists → resume from its state (Status `building` → start at build; `qa` → start at qa).
3. Read PROJECT.md's `Skip stages:` line — skipped stages are bypassed.
4. Announce in ≤ 2 lines what will run — e.g. `automate user-auth → spec → build → qa (ship skipped) — decisions auto-picked and logged` — then go. Do not wait for a reply.

## Decision policy — replaces every question

- A stage wants to ask an MCQ → take its `(Recommended)` option; if none is marked, take the boring production standard for this stack — the choice a senior engineer would defend without a meeting.
- Record EVERY auto-made choice in the spec's Decisions section in the normal format, marked `(auto)`.
- /build hits a stop-and-ask (unlisted file needed, spec conflicts with CRAFT.md) → make the smallest spec amendment that resolves it in CRAFT.md's favor, mark it `(auto-amended)` in the spec, log one line in chat, continue.
- Never auto-answer: anything destructive, anything touching credentials, payments, or data deletion, or a change to CRAFT.md itself. Those stop the run.

## Stages — in order, each per its own SKILL.md

1. **spec** — full procedure. Step-5 MCQs go through the decision policy. Still present the plan in chat (mental model + decisions + tasks) — but continue without waiting.
2. **build** — full task loop with every verify gate and checkpoint. The 3-attempt limit and the regression rule stay hard stops.
3. **qa** — full run; failures become F-tasks and BUGS.md entries as normal. On FAIL → run **build** on the F-tasks, then **qa** again. Max 3 QA rounds total; still failing → stop and report.
4. **ship** — NOT run by default; automation ends before the commit. Run it only when ship is not skipped AND the user asked for it (`--ship` or "including ship") — then ship's confirm step is auto-approved, but its own guards (branch guard, staging by name, never push) still apply in full.

## Hard stops — automation never bulldozes these

- A verify or the suite still fails after 3 fix attempts → stop, report exactly like /build would.
- A regression it cannot fix → stop.
- A spec-vs-CRAFT.md conflict no spec amendment can fix → stop and ask.
- On any stop, report: the stage, what completed, what is blocking, and the exact command to resume — the stages are resumable (/build continues from the first unchecked task).

## Final report — ≤ 15 lines

- The spec's Mental model in 3 lines: what was built, why, how it works
- Stages run and results: tasks done, QA verdict, suite counts
- Every `(auto)` and `(auto-amended)` decision, one line each — the audit trail
- Next step: `/ship <feature>` — or "feature complete" if ship was skipped or already run
