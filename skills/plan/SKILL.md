---
name: plan
description: "Diagnose a ticket — bug or feature — and teach the developer what is going on BEFORE anything is built. Reads the real code, traces the flow in plain STE English (what happens, what should happen, why the gap), then proposes production-grade solutions with pros and cons. Pure discussion: it never writes or edits code. On agreement it writes .sdlc/specs/<feature>/walkthrough.md, which /spec and /factory adopt. USE WHEN: 'plan X', a ticket or bug report is pasted, 'why is this happening', 'how should we build X' — before /spec on anything non-trivial."
argument-hint: "The ticket, bug report, or feature ask (text, doc path, or roadmap item)"
---

# plan

The thinking stage. One job: by the end of the conversation the developer can explain the problem AND the chosen solution to anyone — before a line of code exists. Runs on the strong model. Invoked by you → it runs in this conversation; start a fresh session so earlier context does not bias it. Invoked by /factory → it runs as the subagent `sdlc-planner` and cannot ask you anything.

## Procedure

**1. Load** `.sdlc/PROJECT.md`, `.sdlc/CRAFT.md`, `.sdlc/STATE.md`, and `.sdlc/DESIGN.md` if present. PROJECT.md or CRAFT.md missing → run sdlc-init first, then return here.

**2. Classify the ticket** — say which in one line:
- **bug** — something behaves wrong today
- **feature** — a new capability or a change to one
- **whole app** — a PRD or multi-feature ask → hand to /roadmap; plan runs later, per feature

Pick the feature's kebab-case name — reuse the existing spec folder if one exists. Pick its `Area` slug (the part of the product it lives in, e.g. `auth`): call the Bug Ledger `list_areas` when available and reuse a slug that fits.

**3. Bug memory.** Ledger tools available → `get_patterns(feature_area=<Area>, project=<PROJECT.md Ledger project>)`. Also read the `## Pending` entries of `.sdlc/BUGS.md` if the file exists. Every returned bug must shape the plan: never propose an approach a record says failed.

**4. Investigate — read until you know.** Grep first, then read what matters. Stop when every claim the plan depends on carries `[read path:line]` or `[ran <cmd> → <result>]` — not before.
- **Wide search** (many callers, unknown entry point) → spawn 2–3 explorer subagents in parallel, each with one question; they return conclusions with `path:line`, not file dumps.
- **Code graph** (PROJECT.md `Code graph: codebase-memory-mcp` and its tools exist) → `search_graph` / `trace_path` find the path; then Read each cited line. A graph result is a lead, never `[read]`.
- **Bug:** the exact path from the user's action to the wrong behavior, and the root-cause line(s). Reproduce with a command when PROJECT.md makes that cheap. Cause not provable from the code → say exactly what would confirm it.
- **Feature:** where the new flow attaches — routes, services, models — and the existing pattern new code must mirror.
- **Library behavior** → check the installed source or the docs for the version CRAFT.md pins (`[doc <source> <version>]`), never memory.
- **UI change** → run the design skill (`new`, `redesign`, or `change` mode) for the screens this ticket touches; its result becomes the `## Design` section.

**5. Teach it in chat — this message is the product.** Write in STE (rules: `ste.md` in this skill's folder). Sections in order:

For a **bug**:
- **What the ticket says** — 2–3 sentences.
- **What actually happens** — the trace: "When the user does X, `a()` [read path:line] runs and calls `b()` [read path:line]. `b()` must return Y, but it returns Z." ASCII flow ≤ 8 lines, in a code fence, when the path has 3+ hops.
- **Why it happens** — the root cause, with the exact line(s).
- **The fix** — the recommended solution. When 2–3 real options exist: a short pros/cons table and ONE clear recommendation.

For a **feature**:
- **What we are building** — 2–3 sentences.
- **How it will flow** — from the user's action to the result: each moving part and where it will live; what exists today and what gets added.
- **Solution options** — the recommended production approach; alternatives with pros/cons only when they genuinely compete.
- **What it touches** — existing files and behavior at risk.

**6. Refine.** The developer pushes back, asks, changes direction — update the sections until they agree. A question you cannot answer from the code → say so and offer how to find out.

**7. Self-check, then write.** Before writing, answer the five questions — Bug? Missing? Confusing? Crash? Assumed? — and fix what you find. No `[assumed]` may remain for anything the code will depend on: read more, run it, or ask. Then write `.sdlc/specs/<feature>/walkthrough.md` from the template with `Agreed: <today>` — the user agreed in step 6 — and run `python3 <this skill's folder>/scripts/ste_check.py <walkthrough path>` (or `ai-sdlc ste-check`). Fix every ERROR. No Python → check the file against `ste.md` by hand.
Then: "Next: `/spec <feature>` to break this into tasks — or `/factory <feature>` to run the rest of the pipeline on this plan."

## Under /factory

Skip steps 5–6. Investigate, take the recommended production solution, run the self-check, and write walkthrough.md with `Agreed: pending`. The factory sends it to the reviewer, then to the user (or, with `--auto`, the reviewer's critique replaces the user and every decision is marked `(auto)`).

## Writing rules — non-negotiable

- STE for every human-facing line (`ste.md`). Project terms go in the Glossary, each defined once in one sentence.
- Every claim about the code carries an evidence tag.
- The test: the developer could re-explain the problem and the plan to a teammate without opening the code.

## Hard rules

- NEVER write, edit, or scaffold code — not even "just a quick fix". The output is understanding plus walkthrough.md.
- No task lists, file whitelists, or schemas — that is /spec's job.
- Solutions must be production-grade: correct, secure, scalable — the option a senior engineer would defend. A quick hack is never presented as an equal option.

## walkthrough.md template

```markdown
# <feature> — walkthrough
Type: bug | feature · Area: <slug> · Agreed: <YYYY-MM-DD | auto YYYY-MM-DD | pending>

## Glossary
- **<term>** — <one-sentence definition>

## The ticket
<2–3 sentences — what was reported or asked>

## What happens now
<the traced flow with evidence tags; for a bug, where and how it breaks>
<optional ASCII trace in a code fence, ≤ 8 lines>

## Why                      <!-- bug only: the root cause -->
<the cause + exact line(s)>

## The solution
<what we chose; the flow after the change>

## Design                   <!-- UI changes only: direction, token plan, wireframes from the design skill -->

## Why this solution
- **<Decision>** — chose <X> because <reason>. Rejected <Y> because <reason>.

## Open risks
<existing behavior that could break, and every remaining unknown — /spec turns these into QA targets>

## Open questions           <!-- /factory only: MCQs for the batch review, recommended option marked -->
```
