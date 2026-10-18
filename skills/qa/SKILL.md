---
name: qa
description: "Independent QA for a built feature — four checks in parallel: (A) the mechanical gate (verifies, tester suite, acceptance, regression, diff scan, guardrails), (B) an adversarial review by a DIFFERENT model that tries to break the diff, (C) a blast-radius check of callers the spec never listed, and (D) a UI check for UI changes. A finding blocks only with proof. Failures become fix-tasks /build executes; confirmed fixes become Bug Ledger records. USE WHEN: 'qa X', 'test the feature', 'verify the implementation', after /build finishes."
argument-hint: "The feature to QA (must have a spec in .sdlc/specs/)"
---

# qa

Verifies a feature against its spec AND against what the spec missed. Runs on the strong model in a FRESH context that never saw the implementation reasoning — QA judges the code, not the story behind it. Invoked by you → it runs in this conversation; start a fresh session. Invoked by /factory → it runs as the subagent `sdlc-qa`, cannot ask you anything, and returns bug drafts in its report instead of recording them. QA reports; /build fixes.

## Setup

**1. Load** `.sdlc/PROJECT.md` + `.sdlc/CRAFT.md` + `.sdlc/specs/<feature>/spec.md` + `walkthrough.md`. (Legacy layout: a single `.sdlc/specs/<feature>.md` → treat it as spec.md.) Spec name unclear → list `.sdlc/specs/` and ask.

**2. Collect the diff — committed AND uncommitted.** /build does not commit, so a commit range alone shows nothing. Base = the merge target in PROJECT.md's Git workflow.
- `git diff <base>` — every change to tracked files since the base: commits, staged, and unstaged.
- `git ls-files --others --exclude-standard` — new untracked files; include each in full with `git diff --no-index /dev/null <file>`.
Checks B, C, and D get this full patch (or these two commands) — never only file names. List the changed symbols: functions, routes, schemas, components.

**3. Start checks B, C, D as parallel background subagents, then run check A yourself.** Each subagent gets only the files named below and returns findings, never file dumps.

## A — Gate (you)

- **Task verifies.** Re-run the Verify command of every `[x]` task. Record pass/fail per task.
- **Tester suite.** Run every test file in the spec's `Tests` section. All green required — these ARE the feature's contract. Recompute each test file's sha256 and compare it with the hash /test recorded: a mismatch without a `fixed after challenge` line means build edited a tester test — CRITICAL.
- **Acceptance checks.** Run each command; compare actual vs expected. A check that needs a live app → start it with PROJECT.md's `run:` command and stop it afterwards.
- **Regression.** Run the full `test:` suite. Any failure outside this feature's own tests — especially in areas under `Touches → Risk` — is a regression: always CRITICAL, always blocks PASS.
- **Coverage gap.** An Acceptance check no test covers → ask /test in coverage mode (agent `sdlc-tester`) for ONE minimal test. QA never writes tests.
- **Guardrails.** `.bugledger/` exists and `semgrep` is installed → `semgrep --config .bugledger/ --error <changed files>`. ERROR findings block.
- **Diff scan:**
  - Every changed file appears in some task's `Files:` list or the Tests section — unlisted changes get flagged.
  - Each changed file respects CRAFT.md Structure, Style bullets, and Boundaries — walk them mechanically.
  - No hardcoded config/secrets — literal keys, passwords, tokens, URLs, ports that belong in the settings module + `.env.example`.
  - No legacy-version APIs forbidden by CRAFT.md's Stack idiom lines.
  - **PR-readiness:** no debug prints or leftover logging, no commented-out code, no dead code, no TODO/FIXME, no narration comments or bloated docstrings.
  - Complexity: a function a mid-level developer couldn't trace is a note; concerns mixed in one file block.

## B — Adversarial review (agent `sdlc-reviewer`)

Model: the agent file carries PROJECT.md's review model (/sdlc-init sets it in `.claude/agents/sdlc-reviewer.md`) — do not pass a model on the spawn. It must differ from the model that built the code. The tool cannot pick a model per subagent → use a fresh agent on the same model and log `review: same model (weaker guard)`.
Give it: spec.md, walkthrough.md, the diff. Brief: "Try to break this change. Look for wrong logic, unhandled input, crash paths, race conditions, security holes, and behavior the spec promised but the code does not deliver. Return ≤ 10 findings, most severe first, each with proof."

## C — Blast radius (agent `sdlc-reviewer`, second instance)

Give it: the changed symbols, spec `Touches`, the diff. Brief: "Find every caller of each changed symbol that is NOT in Touches → Edits. Use `detect_changes` and `trace_path` when the code graph is enabled, else grep. Read each caller. For each one, decide if the change breaks it (signature, return shape, null, error type, timing) and prove it by running that caller's tests or a probe command. Return ≤ 10 findings with proof."

## D — UI check (only when the diff changes UI)

Follow `../design/ui-check.md` (the design skill's checklist). No browser or screenshot tool → each visual check is SKIPPED with the reason — never counted as a pass.

## Verdict

**The proof rule.** A finding from B, C, or D blocks only with proof: a failing test, a command and its output, or `path:line` plus a concrete input that triggers it. Without proof it is a note. Merge duplicate findings.

- **PASS** — every gate check green, no proven finding, no unlisted changes, no secret/structure/security/idiom violation, PR-ready. Notes alone don't block.
- **FAIL** — anything else. For each failure append a fix-task to the spec's Tasks section, so `/build <feature>` can execute it:

```markdown
### [ ] F1 — fix: <what>
Bug: <symptom — what goes wrong> · cause: <root cause, the mechanism>
Files: …
Do: …
Verify: `<command that failed>` → <expected>
```

## Bug memory — confirmed fixes only

Record a bug when its fix is confirmed: an `F<n>` task from an earlier QA run that now passes, or — on PASS — a walkthrough with `Type: bug` (symptom from "What happens now", cause from "Why"). Never record a failure that is still open, a red tester test before build, feature work, or a guess. Write symptom and root_cause in STE (plan skill's `ste.md`).
- **Running as a subagent** (/factory) → never record: put each draft in your report; the caller queues it.
- **User present AND Bug Ledger tools available** → show the draft (symptom, root_cause, feature_area = spec Area, project = PROJECT.md Ledger project, severity if justified, the fix diff as `diff_hunk`), wait for an explicit yes, then `record_bug(..., source="confirm")`. Add the returned id to the QA log `Ledger:` line.
- **User present but ledger not connected** → append the draft to `.sdlc/BUGS.md` (create it if missing). Then tell the user once: `Connect Bug Ledger: claude mcp add bugledger -- uvx bugledger-mcp@0.1.2 (or run: ai-sdlc install)`. The fields match `record_bug` (the title and `note` are for humans only), so a later sync is mechanical:

```markdown
# Bugs
## Pending   <!-- waiting for a user yes, then moved to Bug Ledger -->
### P<n> — <title> · <feature> · <YYYY-MM-DD>
- symptom: <what was observed before the fix>
- root_cause: <why it happened — the mechanism, ≥ 20 characters>
- feature_area: <spec Area>
- project: <PROJECT.md Ledger project>
- severity: low | medium | high   <!-- omit if not justified -->
- fix_ref: <commit hash | none>   <!-- passed to record_bug only when it is a hash -->
- note: <e.g. "fix is the spec F<n> diff" — not sent to the ledger>
```
- **Sync:** user present, ledger connected, and `## Pending` has entries → show each, ask yes per entry (or "all"), record it, delete it from BUGS.md.
- A bug a Bug Ledger guardrail now covers → `resolve_bug(id, project)`.

## QA log — append to spec.md (≤ 20 lines per run)

```markdown
### QA <date> — PASS | FAIL
Task verifies: 6/6 · Tester suite: 14/14 · Acceptance: 3/3 · Suite: 42 passed, 0 failed · Regressions: 0
Unlisted changes: none · Craft scan: clean · Guardrails: clean | SKIPPED · PR-ready: yes
Review (<model>): 4 findings, 1 proven · Blast radius: 7 callers checked, 0 broken
UI: <passed>/<run> · SKIPPED: <check (reason)> | none · Shots: <folder> | none   <!-- or "UI: n/a" -->
Failures: <one line per F-task, or "none">
Notes: <unproven findings and nits, or "none">
Ledger: <rec_… ids | pending P<n> | none>
Try it:
1. <command or click-path with concrete sample data>
2. <expected result>
```

The **Try it** block is 2–5 steps any human can follow to see the feature working: concrete sample data, exact expected outcome.

**Report in ≤ 8 lines:** verdict, the counts lines, failures if any, next step — `/build <feature>` to execute fixes, or `/ship <feature>` on PASS. If ship is on `Skip stages:`, do ship's bookkeeping here (spec Status → `done`, STATE.md row → `done`, ROADMAP status if listed) and report the feature complete.

## Rules

- Never PASS with a failing acceptance check, a red tester test, a regression, or a proven finding. No "pass with warnings" for those.
- Never fix code and never write tests — failures become F-tasks for /build, coverage gaps go to /test. QA writes only `.sdlc/` files.
- Never edit a tester-owned test — a wrong test goes through /test's challenge mode.
- Scope is this feature's diff, its callers, and the test suite — do not re-review the whole codebase.
- Environment blocks a check (no DB, no network, no browser)? Record it as SKIPPED with the reason — never silently count it as passing.
- Invoked directly while qa is on the skip list → run anyway (a direct call outranks the list) and note it in the report.
