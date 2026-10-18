---
name: spec
description: "Turn an agreed plan into an executable spec — .sdlc/specs/<feature>/spec.md: machine-facing tasks with contracts, dependencies, and verify commands, nothing else. Adopts the walkthrough from /plan (creates one itself if none exists); every human explanation and decision lives in walkthrough.md, never in the spec. USE WHEN: 'spec X', after /plan agreement, 'plan roadmap feature 3' when you want tasks directly. Produces the file /test and /build execute."
argument-hint: "The feature to spec (e.g. 'user-auth', 'roadmap feature 3')"
---

# spec

Produces the machine-facing plan: tasks small enough that a mid-tier model implements each one without judgment calls. Human understanding lives in `walkthrough.md` (from /plan); `spec.md` is contracts and instructions only — no prose, no decisions, no teaching. Runs on the strong model. Invoked by you → it runs in this conversation; start a fresh session so earlier context does not bias it. Invoked by /factory → it runs as the subagent `sdlc-planner` and cannot ask you anything.

## Procedure

**1. Load — these files and nothing else:**
- `.sdlc/PROJECT.md`, `.sdlc/CRAFT.md` — missing → run sdlc-init first, then return.
- `.sdlc/STATE.md` — what already shipped; never re-plan existing work.
- `.sdlc/DESIGN.md` — only if the feature changes UI.
- `.sdlc/ROADMAP.md` — only if the user referenced a roadmap feature.
- **Bug memory** — Ledger tools available → `get_patterns(feature_area=<Area>, project=<Ledger project>)`; plus `## Pending` in `.sdlc/BUGS.md` if it exists. No task may reintroduce a recorded bug; where one touches this feature, add a guarding Do bullet or Verify.

**2. Adopt or create the walkthrough.**
- `.sdlc/specs/<feature>/walkthrough.md` exists (from /plan) → it IS the agreed direction: design within it. Never re-litigate its decisions; if research below contradicts one, raise that in one line before proceeding.
- Missing → run the plan skill's steps 2–4 yourself, take the recommended production solution, write walkthrough.md from plan's template with `Agreed: pending` — the user's go-ahead on this spec sets the date. Decisions and every "why" go THERE — never into spec.md.

**3. Research the unknowns (no code yet).** For each component the solution needs that this codebase hasn't solved: find the standard production approach for the versions CRAFT.md pins — official docs or the installed package source, tagged `[doc <source> <version>]`. Record each choice as a Decision line in walkthrough.md, in STE (plan skill's `ste.md`).

**4. Integration scan.** Read the existing files this feature touches or extends. For every function, route, or schema a task will change, find its callers: code graph `trace_path` (inbound) when PROJECT.md enables it, otherwise grep — then Read each caller you list. Record in `Touches`: files to be edited and what changes, pattern files new code must mirror, and existing behavior this could break (→ QA regression targets). Fold in walkthrough.md's Open risks. A symbol with 5+ callers gets a Verify that runs those callers' tests.

**5. Gaps → MCQ.** Only unknowns that change the design. Max 5; options A–D with one `(Recommended)`. ≤ 3 → ask in chat; > 3 → write `.sdlc/questions.md`, wait for **done**, read answers, delete the file.
Under /factory: never wait. Without `--auto`, add each MCQ to walkthrough.md `## Open questions` with the recommended option marked — the batch review answers it. With `--auto`, take `(Recommended)` and log it in walkthrough.md marked `(auto)`.

**6. Write `.sdlc/specs/<feature>/spec.md`** from the template. Task rules — /test and /build depend on these:
- **≤ 8 tasks.** Need more → split the feature; tell the user. Under /factory: write nothing, report "needs a split" — the factory parks it.
- Order by dependency. `Needs:` names the tasks that must finish first (omit when none). Each task independently verifiable.
- Each task ≤ 20 lines with these fields:
  - `Files:` explicit CREATE / EDIT list — /build treats this as a whitelist
  - `Needs:` earlier task ids (optional)
  - `Pattern:` existing file to mirror (omit if none)
  - `Do:` 3–7 imperative bullets — exact names, signatures, routes, data shapes, edge cases
  - `Verify:` one runnable command + expected outcome
- Code appears ONLY as: function/route signatures, request/response/schema shapes, and ≤ 5-line pseudocode for genuinely tricky logic. NEVER full file bodies.
- Every Do bullet must be decidable without judgment: "hash with bcrypt, cost 12" — not "hash securely".
- Every error path a task creates is named in a Do bullet: what input triggers it and what the code returns — no unhandled crash paths.
- `Files:` must follow CRAFT.md Structure — one concern per file, each file in its concern's directory.
- A task that introduces a config value gets a Do bullet: read it via the settings module and add the key to `.env.example`. Never plan a hardcoded value.
- A task that adds a dependency names the exact package + version, consistent with CRAFT.md's pins.
- UI tasks name the DESIGN.md tokens and components they use — no new colors or sizes.
- Do NOT write test tasks — /test owns the test suite. Name every public contract (signature, route, shape) precisely enough that /test can write tests from the spec alone.

**7. Self-check, then present.** Run the Quality bar below and the five questions — Bug? Missing? Confusing? Crash? Assumed? Fix what you find. Run `ste_check.py` on walkthrough.md if you added Decision lines. Then present in chat, briefly — /plan already taught the problem:
- each new Decision as one line: `**<Component>** — chose <X> because <Y>`
- the task list, one line per task: `T1 — <name>`
- then: "Review the spec, then `/test <feature>` writes the tests and `/build <feature>` implements — or `/factory <feature>` runs the rest hands-free."

## Spec template

```markdown
# <feature>
Status: draft            <!-- draft → building → qa → done · owned by build/qa/ship -->
Area: <slug>             <!-- Bug Ledger feature_area, same as walkthrough.md -->
Goal: <one line>
Done when:
- <verifiable criterion>
- <verifiable criterion>

## Touches
- Edits: <existing files + what changes in each>
- Callers: <callers of changed symbols outside Edits — read, not edited>
- Mirrors: <pattern file(s) new code must match>
- Risk: <existing behavior that could break — QA checks these>

## Tasks

### [ ] T1 — <name>
Files: CREATE src/…, EDIT src/…
Pattern: src/…
Do:
- <exact imperative instruction>
- <signature / shape where needed>
Verify: `<command>` → <expected>

### [ ] T2 — <name>
Files: …
Needs: T1
…

## Acceptance checks
- [ ] `<command>` → <expected observable result>

## Tests
<!-- written by /test — read-only for /build -->

## QA log
<!-- appended by /qa -->
```

## Quality bar — check before saving

- [ ] A model with ONLY spec.md + PROJECT.md + CRAFT.md could implement every task
- [ ] /test could write the full suite from spec.md alone — every public contract is named
- [ ] Every task has a runnable Verify; every "Done when" maps to an Acceptance check
- [ ] Every error path has a named input and a named result
- [ ] No full code bodies; no vague bullets ("handle errors properly")
- [ ] spec.md contains ZERO explanation prose — every "why" lives in walkthrough.md
- [ ] Every `Files:` list lands each concern in its CRAFT.md directory — no multi-concern files
- [ ] No config value hardcoded anywhere in the plan — settings module + `.env.example` only
- [ ] Touches lists every existing file that will change and every caller of a changed symbol
- [ ] `Needs:` matches the real order; no task uses something a later task creates
- [ ] No task reintroduces a recorded bug (Bug Ledger or BUGS.md)
- [ ] No `[assumed]` left in walkthrough.md for anything a task depends on
