---
name: spec
description: "Plan one feature into a single executable spec — .sdlc/specs/<feature>.md with decisions (why), integration map, and small verifiable tasks (instructions + contracts, NOT code). USE WHEN: 'plan X', 'spec the auth feature', 'plan roadmap feature 3', before building anything non-trivial. Produces the file /build executes."
argument-hint: "The feature to spec (e.g. 'user auth', 'roadmap feature 3', 'payment webhooks')"
---

# spec

Produces ONE file containing everything about a feature — what, why, and how — as tasks small enough that a weak model can implement each one without judgment calls. Tasks carry contracts and instructions, never full code. The developer reads the Decisions section and can explain the design to anyone.

## Procedure

**1. Load context — these files and nothing else:**
- `.sdlc/PROJECT.md` — missing → run the sdlc-init skill first, then return here.
- `.sdlc/CRAFT.md` — the code rulebook (pinned stack + idioms, structure, style, config, security). Missing → run sdlc-init first. Every task you write must be implementable without breaking it.
- `.sdlc/STATE.md` — what already shipped; never re-plan existing work.
- `.sdlc/BUGS.md` — if it exists: plain-English bugs from past QA runs. No task may reintroduce one; where a recorded bug touches this feature's area, add a Do bullet or Verify that guards against it.
- `.sdlc/ROADMAP.md` — only if the user referenced a roadmap feature; pull its goal, scope, done-when.

**2. Understand — build the mental model.** Restate the feature in ≤ 2 sentences: what the user gets, what changes in the system. This becomes `Goal`. Then draft the **Mental model** section — three labelled parts, plain English:
- **What we are building** — 2–3 sentences: the thing itself, concretely.
- **Why** — 1–2 sentences: the problem it solves; what stays broken without it.
- **How it will work** — 3–5 sentences tracing the journey from the user's action to the result, naming each moving part and where it lives. Add a ≤ 8-line ASCII flow when the path has 3+ hops.
The test: after reading it the developer can explain the feature to anyone — what will exist, why, and how the pieces connect — before any code is written. Define technical terms in brackets at first use.

**3. Research the unknowns (no code yet).** List the components the feature needs (e.g. "JWT refresh flow", "webhook signature verification", "cursor pagination"). For each one not already solved in this codebase:
- Find the standard production approach — official docs / web search if tools are available, otherwise known best practice.
- Research against the versions CRAFT.md pins — the pinned major's API, not whatever version is most common in old tutorials.
- Write a **Decision** in the template's format, ≤ 5 lines, in plain English:
  1. what the component IS — one simple line, assume the reader has never heard of it
  2. what we chose
  3. why, in everyday words
  4. what we rejected and why not
- Define every technical term in brackets at first use — e.g. "JWT (a signed pass the server can verify without a database lookup)".
- Audience rule: **Mental model** and **Decisions** are written for the developer and anyone they must explain the feature to — a boss, a client, a teammate — NOT for the model. If a sentence needs a CS degree, rewrite it.

**4. Integration scan.** Read ONLY the existing files this feature touches or extends. Record in `Touches`:
- files to be edited, and what changes in each
- pattern files — existing code the new code must mirror (the style-drift guard)
- existing behavior this could break (shared utils, routes, schema) → these become QA regression targets

**5. Gaps → MCQ.** Only unknowns that change the design. Max 5; options A–D with one `(Recommended)`. ≤ 3 → ask in chat; > 3 → write `.sdlc/questions.md`, wait for **done**, read answers, delete the file.

**6. Write `.sdlc/specs/<feature>.md`** (kebab-case filename) from the template below. Task rules — /build depends on these:
- **≤ 8 tasks.** Need more → split the feature; tell the user.
- Order by dependency. Each task independently verifiable.
- Each task ≤ 20 lines with exactly these fields:
  - `Files:` explicit CREATE / EDIT list — /build treats this as a whitelist
  - `Pattern:` existing file to mirror (omit if none)
  - `Do:` 3–7 imperative bullets — exact names, signatures, routes, data shapes, edge cases
  - `Verify:` one runnable command + expected outcome
- Code appears ONLY as: function/route signatures, request/response/schema shapes, and ≤ 5-line pseudocode for genuinely tricky logic. NEVER full file bodies.
- Every Do bullet must be decidable without judgment: "hash with bcrypt, cost 12" — not "hash securely".
- `Files:` must follow CRAFT.md Structure — one concern per file. `CREATE src/auth.py` holding models + schemas + routes is an invalid task: split into `models/user.py`, `schemas/auth.py`, `routers/auth.py`, … per the Structure section.
- A task that introduces a config value (secret key, DB URL, token TTL, port) gets a Do bullet: read it via the settings module and add the key to `.env.example`. Never plan a hardcoded value.
- A task that adds a dependency names the exact package + version, consistent with CRAFT.md's pins.
- If tests aren't built into each task, the last task is the feature's tests.

**7. Present the plan in chat — never just the file path.** Show, in this order:
- the **Mental model** section, verbatim
- each Decision as one line: `**<Component>** — chose <X> because <Y>`
- the task list, one line per task: `T1 — <name>`
Then: "Review the spec — edit anything — then run `/build <feature>`." The reader must come away knowing what is being built, why, and how it will work — without opening the file.

## Spec template

```markdown
# <feature>
Status: draft            <!-- draft → building → qa → done · owned by build/qa/ship -->
Goal: <one line>
Done when:
- <verifiable criterion>
- <verifiable criterion>

## Mental model — read this first
**What we are building:** <2–3 sentences — the thing itself, concretely>
**Why:** <1–2 sentences — the problem this solves; what stays broken without it>
**How it will work:** <3–5 sentences — the journey from the user's action to the
result, naming each moving part and where it lives. Optional ≤ 8-line ASCII flow.>

## Decisions
<!-- One block per choice · ≤ 5 lines each · plain English · define jargon in
     brackets at first use. A non-programmer must be able to read these. -->
- **<Component>** — <what this thing is, one simple line>.
  Chose: <choice>. Why: <reason in everyday words>.
  Rejected: <alternative> — <why not>.

## Touches
- Edits: <existing files + what changes in each>
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
…

## Acceptance checks
- [ ] `<command>` → <expected observable result>
- [ ] `<command>` → <expected>

## QA log
<!-- appended by /qa -->
```

## Quality bar — check before saving
- [ ] A model with ONLY this spec + PROJECT.md + CRAFT.md could implement every task
- [ ] Every task has a runnable Verify; every "Done when" maps to an Acceptance check
- [ ] No full code bodies; no vague bullets ("handle errors properly")
- [ ] Every `Files:` list lands each concern in its CRAFT.md directory — no multi-concern files
- [ ] No config value is hardcoded anywhere in the plan — settings module + `.env.example` only
- [ ] Touches lists every existing file that will change
- [ ] No task reintroduces a bug recorded in `.sdlc/BUGS.md`
- [ ] **Mental model** + **Decisions** pass the explain-it-to-anyone test: a reader with no
      coding background can say what is being built, why, and how it will work —
      every technical term is defined at first use
