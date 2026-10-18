---
name: ship
description: "Commit a QA-passed feature safely — branch guard, explicit staging, commit built from the spec per PROJECT.md's Git workflow, STATE.md + roadmap update, fix commit linked to its Bug Ledger records. With --pr: pushes the branch and opens a pull request whose description stands alone for an outside reviewer. Never pushes without --pr, never commits on protected branches, never merges. USE WHEN: 'ship X', 'commit the feature', 'open the PR', after /qa passes."
argument-hint: "The feature to ship (e.g. 'ship user-auth', 'ship user-auth --pr')"
---

# ship

Reads the spec for the message, guards the branch, stages files by name, updates the feature log, commits — and, only with `--pr`, pushes and opens the pull request. Follows PROJECT.md's `## Git workflow` for branch names, commit format, and merge target.

## Procedure

**1. Gate.** Read `.sdlc/specs/<feature>/spec.md` (legacy: a single `.sdlc/specs/<feature>.md` → treat it as spec.md). The latest QA log entry must be PASS. Not PASS, or no QA log → say so and offer `/qa <feature>`. Two exceptions, each noted in the commit body: qa is on PROJECT.md's `Skip stages:` line (`qa: skipped`), or an explicit user override ("ship anyway").

**2. Branch guard** (per repo, if multi-repo). `git branch --show-current`. On main / master / develop / development / staging / integration / release/* or detached HEAD → refuse and offer:
- A) create the branch PROJECT.md's Git workflow prescribes (default `feat/<feature>`) and continue
- B) user switches manually
- C) cancel

**3. Update records first, so they ride in the same commit:**
- Spec `Status:` → `done`
- `.sdlc/STATE.md` → add or update the row: `| <feature> | specs/<feature>/ | done | <YYYY-MM-DD> |`
- `.sdlc/ROADMAP.md` (if the feature is on it) → flip its Status to `done`

**4. Stage.** `git status --short`. Stage by name — never `git add .` or `-A`:
- every file from the spec's task `Files:` lists and the `Tests` section
- the spec folder itself, STATE.md, ROADMAP.md, BUGS.md if touched
- never `.env` or any secret-bearing file, `.sdlc/.stage`, build artifacts, dependency dirs — `.env.example` (placeholders only) is fine and expected
- changed files NOT in the spec → list them, ask include / exclude (under /factory: exclude them and log them in RUN.md)

**5. Build the message** in PROJECT.md's commit format (default Conventional Commits):

```
<type>(<feature>): <spec Goal, imperative, ≤ 72 chars>

- <one bullet per task — the behavior, not the file names>

Spec: .sdlc/specs/<feature>/spec.md
```

Type: feat | fix | refactor | test | chore — whichever the spec actually did.

**6. Confirm.** Show branch, staged file list, and the message. Wait for **yes** (or apply requested edits). Then commit — multi-line via `git commit -F .sdlc/commit-msg.txt`, delete the temp file after.

**7. Link the fix to its bug records.** For each id on the QA log's `Ledger:` lines → `update_bug(id, fix_ref=<commit hash>)` when the ledger tools exist, so the ledger stores the real diff. For this feature's entries in `.sdlc/BUGS.md` `## Pending` → set `fix_ref:` to the commit hash (amend the commit only if the user agrees; otherwise it rides in the next commit; under /factory never amend).

**8. PR — only with `--pr` (or the user asking for one).** Push the branch and open the PR against the Git workflow's merge target (`gh pr create` or the host's equivalent). The description must stand alone for an outside reviewer — a human or a model on another platform — who has none of this conversation:
- **Why** — the problem and chosen solution, 3–4 lines from walkthrough.md, in STE (plan skill's `ste.md`)
- **What changed** — one bullet per task
- **How to test** — the QA log's Try it steps, verbatim
Show the PR body and get one confirmation before pushing. Without `--pr`: never push; report the push command as reference only.

**9. Report in ≤ 5 lines:** short hash, branch, file count, bug records linked, and either the PR URL or the push command as reference.

**Under /factory** (only with `--ship`): the confirm steps are auto-approved, but every guard still applies — branch guard, staging by name, never a protected branch, never a force push. The PR is opened, never merged. In a multi-feature run the factory already committed the feature and owns STATE.md, ROADMAP.md, and BUGS.md: skip steps 3–7 and go to step 8 from the existing commit. A feature built on another feature from the same run starts its PR description with `Depends on #<n>`.

## Rules

- Never push without `--pr` + confirmation (or `/factory --ship`). Never commit on a protected branch. Never stage secrets. Never merge a PR.
- Merge-conflict markers anywhere → refuse; user resolves first.
- Multi-repo: run guard → stage → commit per repo that has changes; each repo gets its own message.
- Clean working tree → show status, exit cleanly — unless the feature's commit already exists on this branch and `--pr` was given: then go to step 8.
- Branch named `trunk` or `mainline` → treat as protected, ask before proceeding.
