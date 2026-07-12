---
name: ship
description: "Commit a QA-passed feature safely — branch guard, explicit staging, conventional commit built from the spec, STATE.md + roadmap update. Never pushes, never commits on protected branches. USE WHEN: 'ship X', 'commit the feature', 'commit my changes', after /qa passes."
argument-hint: "The feature to ship (e.g. 'ship user-auth')"
---

# ship

Commit-only. Reads the spec for the message, guards the branch, stages files by name, updates the feature log. Never pushes.

## Procedure

**1. Gate.** Read the spec. The latest QA log entry must be PASS. Not PASS, or no QA log → say so and offer `/qa <feature>`. Proceed anyway only on an explicit user override ("ship anyway") — note the override in the commit body.

**2. Branch guard** (per repo, if multi-repo). `git branch --show-current`. On main / master / develop / development / staging / integration / release/* or detached HEAD → refuse and offer:
- A) create `feat/<feature>` and continue
- B) user switches manually
- C) cancel

**3. Update records first, so they ride in the same commit:**
- Spec `Status:` → `done`
- `.sdlc/STATE.md` → add or update the row: `| <feature> | specs/<feature>.md | done | <YYYY-MM-DD> |`
- `.sdlc/ROADMAP.md` (if the feature is on it) → flip its Status to `done`

**4. Stage.** `git status --short`. Stage by name — never `git add .` or `-A`:
- every file from the spec's task `Files:` lists
- the spec itself, STATE.md, ROADMAP.md if touched
- never `.env` or any secret-bearing file, build artifacts, dependency dirs — `.env.example` (placeholders only) is fine and expected
- changed files NOT in the spec → list them, ask include / exclude

**5. Build the message** (Conventional Commits):

```
<type>(<feature>): <spec Goal, imperative, ≤ 72 chars>

- <one bullet per task — the behavior, not the file names>

Spec: .sdlc/specs/<feature>.md
```

Type: feat | fix | refactor | test | chore — whichever the spec actually did.

**6. Confirm.** Show branch, staged file list, and the message. Wait for **yes** (or apply requested edits). Then commit — multi-line via `git commit -F .sdlc/commit-msg.txt`, delete the temp file after.

**7. Report in ≤ 5 lines:** short hash, branch, file count, and the push command as reference only. Do not push. Do not open a PR.

## Rules
- Never push. Never commit on a protected branch. Never stage secrets.
- Merge-conflict markers anywhere → refuse; user resolves first.
- Multi-repo: run guard → stage → commit per repo that has changes; each repo gets its own message.
- Clean working tree → show status, exit cleanly.
- Branch named `trunk` or `mainline` → treat as protected, ask before proceeding.
