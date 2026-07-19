---
name: roadmap
description: "Break a whole project (PRD or description) into an ordered list of shippable features — creates .sdlc/ROADMAP.md. Optional: for greenfield projects or large multi-feature efforts. USE WHEN: 'divide this project', 'break down this PRD', 'create a development plan'. NOT for a single feature — use /spec directly."
argument-hint: "The PRD, project description, or doc path to break down"
---

# roadmap

Turns a PRD into an ordered feature list where each feature fits one `/spec → /build → /qa → /ship` cycle. It decides WHAT to build and in what order — never HOW (no file lists, no schemas; that is /spec's job).

## Procedure

**1.** Read `.sdlc/PROJECT.md`. Missing → run the sdlc-init skill first (follow its SKILL.md), then return here.

**2.** Read the PRD/description fully. Extract: purpose, features, constraints, non-functional needs (auth, scale, deploy).

**3. Gaps → MCQ.** Ask only what changes the breakdown: rough scale, auth needs, deploy target, what is out of scope for v1. Max 5 questions; options A–D with one `(Recommended)`. ≤ 3 → ask in chat; > 3 → write `.sdlc/questions.md`, wait for **done**, read answers, delete the file.

**4. Divide.** Rules:
- Each feature = one meaningful capability, shippable and testable on its own. Target size: one focused /build session.
- Order by dependency: skeleton → data layer → auth → core features → integrations → polish. Auth before anything protected; schema before anything that uses it.
- On greenfield, feature 1 is always the project skeleton (installs, runs, lints, health check).
- Max 10 lines per feature block. If a feature needs more, it is two features.

**5. Write `.sdlc/ROADMAP.md`:**

```markdown
# Roadmap — <project>

| # | Feature | Needs | Status |
|---|---------|-------|--------|
| 1 | skeleton | — | todo |
| 2 | user-auth | 1 | todo |

## 1. skeleton
Goal: <one line>
Scope: <3–6 bullets>
Done when: <2–3 verifiable criteria — "returns 401 unauthenticated", not "works">

## 2. user-auth
…

## Out of v1
- <anything deliberately dropped, one line each>
```

**6. Report in ≤ 6 lines:** feature count, phase summary, and the next command: `/spec <feature-1>` — or `/automate <feature-1>` to run its whole cycle hands-free.

## Rules
- Cover the ENTIRE PRD scope — anything skipped goes under "Out of v1", never silently dropped.
- Feature names are kebab-case; they become spec filenames (`.sdlc/specs/<feature>.md`).
- The Status column is owned by /ship — it flips `todo → done` as features ship. Don't pre-fill anything else.
- "Done when" criteria flow into the spec's Acceptance checks — write them so a command can prove them.
