---
name: factory
description: "The code factory: runs the whole pipeline — plan → spec → review → test → build → qa (→ ship) — for one feature, a list of features, the whole roadmap, or a whole project from a PRD. Without --auto it plans everything, has a different model review each plan, stops ONCE for your review, then builds unattended. With --auto it never stops. Independent features run in parallel worktrees; blocked features are parked while the rest continue. USE WHEN: 'factory <x>', 'build these features', 'build the whole roadmap overnight', 'fix this ticket end to end', 'build X without asking me'."
argument-hint: "<feature | ticket> | f1 f2 … | --roadmap | <PRD path>   [--auto] [--ship]"
---

# factory

Runs the pipeline for any scope. Each stage follows its own SKILL.md to the letter — the factory decides only WHO runs each stage (a fresh subagent on the right model), WHO answers questions (you once, or the decision policy), and WHAT runs in parallel. A single feature is a queue of one: same rules, same graph. The factory itself runs in your session: it is the only part that talks to you.

## The stage graph

The factory moves a feature to the next stage only on evidence it checks ITSELF — the file exists, the command's exit code, the QA log line. A subagent saying "done" is not evidence.

| Stage | Agent (model) | Writes | Pass — checked by the factory | On fail |
|---|---|---|---|---|
| plan | `sdlc-planner` (strong) | walkthrough.md | file exists · `ste_check.py` exit 0 · no `[assumed]` the code depends on | redo once with the reason |
| spec | `sdlc-planner` (strong) | spec.md | spec quality bar · every task has a Verify | redo once |
| review | `sdlc-reviewer` (review) | findings → factory writes `Reviewed:` | no proven finding left | planner revises · max 2 rounds → park |
| your review | you (skipped with `--auto`) | answers, edits | you approve → factory writes `Agreed:` | re-run plan/spec/review for changed features |
| test | `sdlc-tester` (strong) | tests + Tests section | new tests red · existing `test:` exit 0 | redo once → park |
| build | `sdlc-builder` (mid) | code, checkboxes | all tasks `[x]` · `test:` exit 0 | build's own 3 attempts → park |
| qa | `sdlc-qa` (strong) + 2 `sdlc-reviewer` | QA log, F-tasks | latest QA log line is PASS | build F-tasks → qa again · max 3 rounds → park |
| ship | this session | commit, PR | commit exists | park |

**One writer per file:** walkthrough.md → plan/spec (the factory writes only its `Agreed:` and `Reviewed:` header lines) · spec tasks → spec, or test as `(auto-amended)` · task checkboxes → build · `## Tests` → test · QA log and F-tasks → qa · STATE.md, ROADMAP status, BUGS.md → ship in a one-feature run, the factory on the integration branch in a multi-feature run · `.sdlc/RUN.md` → factory.

**Models.** Spawn `sdlc-<role>` — the CLI installs these agents in `.claude/agents/` (or `.cursor/agents/`). The agent file carries the role's model — /sdlc-init edits its `model:` line when PROJECT.md `Models:` differs from the defaults — so do not pass a model on the spawn. Agents not installed → a general subagent with the model alias closest to PROJECT.md's choice, logged in RUN.md. The reviewer must differ from the model that wrote what it reviews; the tool cannot pick a model per subagent → same model in a fresh context, logged `same model (weaker guard)`. No subagents at all → run stages one by one, each started clean: drop prior reasoning, re-read only that stage's files.

## Approval states — the walkthrough.md header

- `Agreed: <YYYY-MM-DD>` — you approved it (in /plan, or at the factory's stop). Build it as-is.
- `Agreed: auto <YYYY-MM-DD>` — only the reviewer approved it, in an `--auto` run. A later run without `--auto` treats it as pending.
- `Agreed: pending` — nobody approved it. It goes through review and the stop, whatever other artifacts exist.
- `Reviewed: <model> <YYYY-MM-DD> · <n> proven findings fixed` — written after the review stage. Missing → the review has not run.

## Setup

1. Read `.sdlc/PROJECT.md`, `.sdlc/CRAFT.md`, `.sdlc/STATE.md`. PROJECT.md or CRAFT.md missing → stop: run /sdlc-init first (init is never automated — its approval gate needs a human). `.sdlc/RUN.md` lists unfinished features → **resume**: reuse its scope, mode, integration branch, and per-feature stage and worktree; skip to the phase it records.
2. **Resolve the scope:**
   - one feature or ticket → a queue of one
   - `f1 f2 …` → those features · `--roadmap` → every `todo` row of `.sdlc/ROADMAP.md`
   - a PRD path → run /roadmap first (its questions take the `(Recommended)` option, marked `(auto)` under `## Assumed` — you see the roadmap at the stop), then every feature on it
   Already `done` in STATE.md → drop it and say so.
3. **Adopt what exists — never redo an approved stage.** Per feature: a walkthrough approved for this mode (see Approval states) starts at its first missing artifact — no spec → spec · no `## Tests` → test · unchecked tasks → build · no QA PASS → qa. Anything not approved for this mode enters Phase 1 at its first missing artifact, then review and the stop.
4. **Preflight:** no uncommitted changes outside `.sdlc/` · the full `test:` suite passes on the base branch · Bug Ledger tools available — if not, say once that bugs wait in `.sdlc/BUGS.md` and how to connect the ledger, then continue. Read `Skip stages:` and `Parallel:` (default 2).
5. **Write `.sdlc/RUN.md` now** — scope, mode, base branch, integration branch name, and one row per feature (stage, branch, worktree, status). Update it at every stage change. It is the resume point.
6. Announce in ≤ 3 lines: scope, mode (`review once` or `--auto`), what runs in parallel. Do not wait for a reply.

## Phase 1 — Plan everything (parallel)

For every feature not yet approved, in roadmap order, up to `Parallel:` at a time: **plan** → **spec** → **review**. The reviewer gets walkthrough.md + spec.md and the brief: "Find what is wrong, missing, or unsafe in this plan. Proof is a `path:line` that contradicts it, a ticket requirement it drops, or a task a builder could read two ways. ≤ 10 findings." Proven findings go back to the planner; notes go to walkthrough.md Open risks. Then write the `Reviewed:` line.

## Phase 2 — The one stop (skipped with `--auto`)

Show the batch in one message: per feature — 3 lines (problem, solution, main risk), task count, its Open questions with the recommended option, and reviewer notes; link every walkthrough.md. Wait for your answer: "approve all", or edits and answers per feature. Changed features re-run plan/spec/review. Then set `Agreed: <date>`, say "running unattended now", and never stop again.
With `--auto`: the reviewer's critique replaces your review. Open questions take the recommended option, marked `(auto)`. Set `Agreed: auto <date>`.

## Phase 3 — Build everything (unattended)

1. **Order:** a feature waits for every feature it `Needs` (ROADMAP) and for any running feature whose impact set overlaps its own. Impact set = the spec's `Files:` + `Touches → Callers` (+ `detect_changes` output when the code graph is enabled). The rest run in parallel, up to `Parallel:`.
2. **Isolation.** One feature → the current checkout on its feature branch. Several → create the integration branch `factory/<YYYY-MM-DD>` from the base (record its name in RUN.md; a resume reuses it). Commit the approved plans on it FIRST — every `.sdlc/specs/<feature>/`, `.sdlc/ROADMAP.md`, `.sdlc/BUGS.md` — as `chore(factory): approved plans`. Then give each feature a git worktree on its own feature branch (PROJECT.md Git workflow) cut from the integration branch. In each worktree run PROJECT.md's `install:` command and copy the git-ignored files the app needs (for example `.env`).
3. **Run** test → build → qa per the stage graph, each stage a fresh subagent. QA returns bug drafts in its report → queue them in `.sdlc/BUGS.md` `## Pending` in the qa skill's format (on the integration branch in a multi-feature run). Never record them in Bug Ledger without your yes.
4. **Integrate** (several features). On QA PASS: commit on the feature branch (ship's message and staging rules, never STATE.md, ROADMAP.md, or BUGS.md), then merge it into the integration branch and run the full `test:` there.
   - Merge conflict, or `test:` red → abort or revert that merge and park the feature with the exact output.
   - Green → on the integration branch update STATE.md, the ROADMAP status, and BUGS.md, then commit `chore(factory): integrate <feature>`.
   Dependents start only after their dependencies are integrated. Remove each worktree when its feature is integrated or parked.
5. **Ship.** With `--ship`: run /ship `--pr` for each integrated feature from its branch, in dependency order. A feature built on another feature from this run starts its PR description with `Depends on #<n>` — its diff shows that feature's commits until the first PR merges. Without `--ship`: one feature stops before the commit — next step `/ship <feature>`; several features stay as local commits on their branches and on the integration branch.

**Park, don't stop.** A feature that hits a park condition gets status `blocked` in STATE.md and RUN.md (stage, exact failing output, resume command), and its dependents are skipped as `blocked: needs <x>`. Everything else continues. The whole run stops only when the integration branch is red and no single merge explains it, or when something hits the never-auto-answer list.

## Decision policy — replaces every question after the stop

- A stage would ask an MCQ → its `(Recommended)` option; none marked → the boring production standard for this stack — the choice a senior engineer would defend without a meeting. Record it in walkthrough.md marked `(auto)`.
- /build files a test challenge → /test's challenge mode in a fresh subagent; its verdict is final. The spec itself is ambiguous → smallest `(auto-amended)` fix in CRAFT.md's favor.
- A stage says "stop and ask the user" for a reason not listed here → park the feature with that question in RUN.md.
- Never auto-answer: anything destructive, anything touching credentials, payments, or data deletion, or a change to CRAFT.md. That feature parks.

## Final report

Bring `.sdlc/RUN.md` to its final state and show ≤ 15 lines of it in chat:

```markdown
# Factory run <YYYY-MM-DD> · scope: <…> · mode: review once | auto
Base: <branch> · Integration: factory/<YYYY-MM-DD> | none
| Feature | Stage | Status | Branch / PR | Worktree | QA rounds | Note |
|---|---|---|---|---|---|---|
## Decisions made without you      <!-- every (auto) and (auto-amended), one line each -->
## Reviewer notes not fixed
## Pending bug records             <!-- P<n> entries in .sdlc/BUGS.md waiting for your yes -->
## Resume                          <!-- exact command per blocked feature -->
```

You are present and the Bug Ledger tools exist → offer the pending bug records now: show each, record it on your yes (`record_bug`), delete it from BUGS.md.

## Running overnight

Start it in a dedicated clone or container, not in the checkout you work in. For a headless run: `claude -p "/factory --roadmap" --permission-mode auto --max-budget-usd <limit>` — never `bypassPermissions` on your own machine. In a container, mount `BUGLEDGER_HOME` so the ledger survives. Interrupted → run the same command again: the factory reads RUN.md and continues where it stopped.

## Hard rules

- Every stage runs in a fresh subagent — the factory never lets the context that wrote something judge it.
- Never push to or merge into a protected branch. Never force-push. PRs are opened, never merged.
- Never move a feature forward on a subagent's word — check the file, the exit code, or the QA log line.
- Build inside one feature is sequential. Parallelism is across features, explorers, and QA checks only.
