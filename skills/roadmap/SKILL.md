---
name: roadmap
description: "Break a whole project (PRD or description) into an ordered list of shippable features — creates .sdlc/ROADMAP.md. Optional: for greenfield projects or large multi-feature efforts. USE WHEN: 'divide this project', 'break down this PRD', 'create a development plan'. NOT for a single feature or bug — use /plan directly."
argument-hint: "The PRD, project description, or doc path to break down"
---

# roadmap

Turns a PRD into an ordered feature list where each feature fits one `/plan → /spec → /test → /build → /qa` cycle. It decides WHAT to build and in what order — never HOW (no file lists, no schemas; that is /plan and /spec's job).

## Procedure

**1.** Read `.sdlc/PROJECT.md`. Missing → run the sdlc-init skill first (follow its SKILL.md), then return here.

**2.** Read the PRD/description fully. Extract: purpose, features, constraints, non-functional needs (auth, scale, deploy).

**3. Gaps → MCQ.** Ask only what changes the breakdown: rough scale, auth needs, deploy target, what is out of scope for v1. Max 5 questions; options A–D with one `(Recommended)`. ≤ 3 → ask in chat; > 3 → write `.sdlc/questions.md`, wait for **done**, read answers, delete the file. Under /factory: take each `(Recommended)` option and write it under `## Assumed` in ROADMAP.md marked `(auto)` — the user sees it at the factory's review stop.

**4. Divide.** Rules:
- Each feature = one meaningful capability, shippable and testable on its own. Target size: one focused /build session.
- Order by dependency: skeleton → data layer → auth → core features → integrations → polish. Auth before anything protected; schema before anything that uses it.
- On greenfield, feature 1 is always the project skeleton (installs, runs, lints, health check).
- Max 10 lines per feature block. If a feature needs more, it is two features.
- `Needs` lists only real dependencies — a feature that does not use another's code or data does not need it. Fewer false edges let /factory build more features in parallel.
- Multi-repo platform → name the repo in each feature's `Touches`.

**5. Write `.sdlc/ROADMAP.md`:**

```markdown
# Roadmap — <project>

| # | Feature | Needs | Status |
|---|---------|-------|--------|
| 1 | skeleton | — | todo |
| 2 | user-auth | 1 | todo |

## 1. skeleton
Goal: <one line>
Area: <slug>     <!-- the product area it lives in, e.g. auth; reuse Bug Ledger list_areas slugs -->
Scope: <3–6 bullets>
Touches: <directories or modules it will change — /factory runs features that share these one after another>
Done when: <2–3 verifiable criteria — "returns 401 unauthenticated", not "works">

## 2. user-auth
…

## Out of v1
- <anything deliberately dropped, one line each>

## Assumed                 <!-- /factory only: questions answered with the recommended option -->
```

**6. Report in ≤ 6 lines:** feature count, phase summary, and the next command: `/plan <feature-1>` to design it together — or `/factory --roadmap` to plan every feature, review them once, and build them unattended.

## Rules
- Cover the ENTIRE PRD scope — anything skipped goes under "Out of v1", never silently dropped.
- Feature names are kebab-case; they become spec folder names (`.sdlc/specs/<feature>/`).
- The Status column is owned by /ship — it flips `todo → done` as features ship. Don't pre-fill anything else.
- "Done when" criteria flow into the spec's Acceptance checks — write them so a command can prove them.
