<p align="center">
  <img src="https://raw.githubusercontent.com/xajeel/AI-SDLC/main/assets/ai-sdlc-kit.png" alt="ai-sdlc-kit" width="320">
</p>

<h1 align="center">ai-sdlc-kit</h1>
<p align="center">A code factory for AI coding agents — spec-driven, test-first, independently reviewed — that leaves the developer understanding every change.</p>

<p align="center">
  <a href="https://pypi.org/project/ai-sdlc-kit/"><img src="https://img.shields.io/pypi/v/ai-sdlc-kit.svg" alt="PyPI version"></a>
  <a href="https://www.npmjs.com/package/ai-sdlc-kit"><img src="https://img.shields.io/npm/v/ai-sdlc-kit.svg" alt="npm version"></a>
  <a href="https://github.com/xajeel/AI-SDLC/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
</p>

---

## What is it?

`ai-sdlc-kit` installs skills, subagents, guard hooks, and a bug-memory server for Claude Code, Cursor, Windsurf, and Gemini CLI that turn one coding agent into a small engineering team with separated roles:

**diagnose & teach → spec in verifiable tasks → review by another model → write the tests first → build to the tests → independent QA → ship**

Hand it one ticket, ten features, or a whole PRD. `/factory` plans everything, has a different model review each plan, stops **once** for your approval, then builds the rest unattended — in parallel where features don't collide.

Three ideas drive the design:

1. **The developer must understand everything.** `/plan` walks you through the problem in plain, simplified technical English — *"When the user does X, `a()` runs. It must return Y, but it returns Z. Line 42 causes it."* — plus the solution options and why one wins. Every feature keeps a human-readable `walkthrough.md` next to its machine-readable `spec.md`. You finish able to trace the code and defend the decisions.
2. **No agent grades its own homework.** Each stage runs as its own fresh agent. The tester writes tests from the spec before the code exists, and the builder can't touch them. A reviewer on a **different model** tries to break every plan and every diff. QA never sees the builder's reasoning.
3. **Evidence, not confidence.** Every claim about the code carries a tag — `[read path:line]`, `[ran cmd → result]`, `[doc source version]`, or `[assumed]` — and nothing ships on an `[assumed]`. A QA finding blocks only with proof: a failing test, a command's output, or a line plus the input that breaks it.

| Skill | Role | Does |
|---|---|---|
| `sdlc-init` | — | One-time setup: project facts, git workflow, the model for each role, the code-craft rulebook, Bug Ledger and code-graph settings, rule stubs for every coding tool |
| `roadmap` | Planner | Splits a PRD into ordered, shippable features with dependencies |
| `plan` | Planner (strong) | Diagnoses a ticket from the real code, teaches you the flow in STE, proposes production-grade solutions — never writes code |
| `design` | Planner (strong) | Designs UI before code: new screens, redesigns, or targeted changes — tokens, wireframes, and `.sdlc/DESIGN.md` |
| `spec` | Planner (strong) | Turns the agreed plan into ≤ 8 tasks with contracts, dependencies, and verify commands |
| `test` | Tester (strong) | Reviews the spec, then writes a focused, risk-ranked test suite (about 15 tests) BEFORE implementation |
| `build` | Developer (mid) | Implements task-by-task with a self-review per task until the tester's tests go green — it may never edit them |
| `qa` | QA (strong) + reviewer | Four parallel checks: the gate, an adversarial review by another model, a blast-radius check of callers, and a UI check |
| `ship` | — | Branch guard, staged commit per your git workflow, links the fix to its bug records; `--pr` opens a self-explanatory pull request |
| `factory` | Orchestrator | The whole pipeline for one feature, many, or a whole project — review once, or `--auto` for zero stops |
| `architecture-diagram` | — | Renders a self-contained HTML/SVG architecture diagram |
| `mentor` | — | Teaches you a topic — or a whole codebase — one tracked lesson at a time |

## Install

```bash
# Python
pip install ai-sdlc-kit        # or: uv tool install ai-sdlc-kit

# Node
npm install -g ai-sdlc-kit     # or one-off: npx ai-sdlc-kit install --agent claude
```

Both give you the same `ai-sdlc` command and the same kit.

## Use

```bash
ai-sdlc install --agent claude   # or cursor / windsurf / gemini / all
```

This copies the skills into your agent's skills directory, the subagents into `.claude/agents/` (or `.cursor/agents/`), adds the Bug Ledger MCP server to your agent's MCP config, and — for Claude Code — installs the two guard hooks into `.claude/hooks/ai-sdlc/` and `.claude/settings.json`. Config files are merged, never overwritten. The skills then appear as slash commands: `/sdlc-init`, `/roadmap`, `/plan`, `/design`, `/spec`, `/test`, `/build`, `/qa`, `/ship`, `/factory`, `/mentor`.

| Flag | Effect |
|---|---|
| `--agent all` | install for every supported agent at once |
| `--target PATH` | install into a specific project directory (default: `.`) |
| `--global` | install into your home directory instead of a project |
| `--force` | overwrite existing skill and agent files |
| `--no-bugledger` | don't add the Bug Ledger MCP server |
| `--no-hooks` | don't install the guard hooks (Claude Code) |

```bash
ai-sdlc list                  # see bundled skills, agents, and hooks
ai-sdlc ste-check <file>      # check a walkthrough against the STE writing rules
ai-sdlc --version             # print the installed version
```

Bug Ledger runs through [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (`uvx bugledger-mcp`). Upgrading from 0.2.x? `ai-sdlc install --force` replaces the old `/automate` skill with `/factory`, and `/sdlc-init` upgrades your `.sdlc/` files in place.

> **Monorepo, or no Python project at the root?** Not a problem — `ai-sdlc install` only copies files into `.claude/` (or your agent's folder) and merges its config files; it never reads `pyproject.toml` or anything else at the target. Install the CLI once with `pipx install ai-sdlc-kit` or `uv tool install ai-sdlc-kit`, then run it at your repo root — or from anywhere with `--target /path/to/root`.

## Getting started

Every project starts with `/sdlc-init` — run it once, in your agent, inside your project folder. It writes:

- `.sdlc/PROJECT.md` — project facts, real commands, **your git workflow**, the **model for each role** (strong for thinking, mid for building, and a *different* review model), how many features may build in parallel, and the Bug Ledger and code-graph settings
- `.sdlc/CRAFT.md` — the code rulebook: pinned stack versions with modern-idiom rules, folder structure, style (including the always-on simplicity rules: minimal comments, no essay docstrings, boring beats clever), config and security rules
- `.sdlc/STATE.md` — the feature tracker
- `AGENTS.md` at the repo root — a short pointer so **any** coding tool (Claude Code, Cursor, Codex, Windsurf…) lands on the same rules before writing code

It works two ways: give it a PRD (`/sdlc-init <path>`) for a new project, or run it bare on an existing codebase and it detects your stack from lockfiles and a handful of source files. Either way it shows you the rules for approval before writing anything.

On Claude Code the default models are Opus 5.5 (strong), Sonnet 5.5 (mid), and Opus 4.8 (review) — the reviewer differs from both the planner and the builder.

## The pipeline

Every feature or bug lives in `.sdlc/specs/<name>/` as exactly two files:

- **`walkthrough.md`** — for humans: a glossary, the problem, the traced flow, the chosen solution, and every decision with its "why" — written in an STE style (simplified technical English, after ASD-STE100) and checked by `ste-check`.
- **`spec.md`** — for machines: tasks, file whitelists, dependencies, contracts, verify commands. No prose.

The stages, each in its own fresh agent:

1. **`/plan <ticket>`** — the conversation. It reads the real code until every claim is proven, and explains what the ticket means, what actually happens (with `file:line` traces), why, and the production-grade ways to fix or build it. UI work goes through `/design`. You push back and refine; when you agree, it writes `walkthrough.md`. It never writes code.
2. **`/spec <feature>`** — turns the agreed direction into ≤ 8 small, independently verifiable tasks, and lists every caller of every symbol it will change.
3. **`/test <feature>`** — a separate tester first reviews the spec for gaps, then writes a short test plan where each test names the bug it catches: the bug reproduction, the acceptance checks, one happy path per contract, and only the edge cases that can crash, corrupt, or leak. About 15 tests, never 100.
4. **`/build <feature>`** — implements task-by-task, self-reviews each task's diff, and stops at red → green. It may never edit the tester's tests; if one looks wrong it files a challenge and `/test` adjudicates against the spec.
5. **`/qa <feature>`** — four checks in parallel: **(A)** the gate re-runs every verify, the suite, the acceptance checks, and a PR-readiness scan; **(B)** a reviewer on another model tries to break the diff; **(C)** a blast-radius check reads and tests the callers the spec never listed; **(D)** a UI check (screens at three widths, keyboard, focus, contrast, states, off-token values). Proven failures become fix-tasks `/build` executes.
6. **`/ship <feature>`** — commits per your git workflow and links the fix commit to its bug records; `/ship <feature> --pr` pushes and opens a PR whose description (why / what changed / how to test) stands alone for any outside reviewer.

Pick the path that matches what you're doing:

| Situation | Commands |
|---|---|
| A bug ticket | `/plan <ticket>` → agree on the fix → `/factory <name>` (or step through `/spec` → `/test` → `/build` → `/qa`) |
| One feature | `/plan <feature>` → agree on the design → `/factory <name>` |
| Several features | `/factory f1 f2 f3` — plans all, you review once, it builds the rest |
| A whole project from a PRD | `/sdlc-init <PRD>` → `/factory <PRD>` — roadmap, plans, one review, then everything else |
| "Just do it, don't ask me" | `/factory <ticket> --auto` — a reviewer model replaces your review; every call is logged `(auto)` |
| UI work | `/design new <brief>`, `/design redesign <page>`, or `/design change <what>` |
| Learning a codebase or a technology | `/mentor` — see [Learning a codebase](#learning-a-codebase) below |

## The factory

`/factory` runs any scope — one feature, a list, `--roadmap`, or a PRD — through the same stage graph:

1. **Plan everything** in parallel: plan → spec → a reviewer on a different model critiques each plan, and the planner fixes every proven finding.
2. **One stop:** you review the batch — three lines per feature, its open questions with a recommended answer, and the reviewer's notes. Approve all, or edit. With `--auto` there is no stop.
3. **Build everything unattended:** test → build → qa per feature. Independent features run in parallel git worktrees (`Parallel:` in PROJECT.md); features whose files or callers overlap run one after another. Each QA-passed feature merges into an integration branch `factory/<date>`, and the full suite must stay green there.

A feature that gets stuck is **parked** — its reason and resume command go to `.sdlc/RUN.md` — and the rest keep going. `--ship` opens one PR per feature; PRs are never merged for you. The factory advances a feature only on evidence it checks itself — files, exit codes, the QA log — never on an agent's word.

Overnight: run it in a dedicated clone or container, e.g. `claude -p "/factory --roadmap" --permission-mode auto --max-budget-usd 50`. Interrupted? Run the same command again — it adopts every artifact and continues.

Other controls:

- **Skip a stage** — `/sdlc-init --skip-ship` (or `--skip-qa`, `--skip-test`) drops a stage from handoffs and `/factory`; toggle any time with `--unskip-<stage>`. Invoking a skipped skill directly still runs it.
- **Bug memory** — fixed bugs are stored in [Bug Ledger](https://github.com/xajeel/bugledger-mcp), a local MCP server. `/plan`, `/spec`, `/test`, and `/build` check it before they work in an area; `/build` searches it when a test fails. Every record needs your yes. During unattended runs, or when the ledger isn't connected, bugs wait in `.sdlc/BUGS.md` and move to the ledger once you approve them.
- **Code graph (optional)** — with [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) installed, agents find callers through a call graph and QA maps the diff to its blast radius. Without it, everything falls back to search. Graph results are leads; agents still read the code.
- **Guard hooks (Claude Code)** — while `/build` runs, edits to tester-owned tests are blocked, and pushes to protected branches or force-pushes are blocked always. They need `python3` on your PATH; skip them with `--no-hooks`.

## Learning a codebase

The other skills build software; `/mentor` teaches it. Point it at a topic ("teach me Kafka") or at the repo you're sitting in ("teach me this codebase") and it builds a curriculum, then teaches **one lesson per session** — never dumping the whole course at once — quizzing you at the end of each and only advancing once you pass.

For a codebase it reads the repo first, then runs a short course of one or two modules:

- **Map & Run** — what the project does, a guided tour of the directories, getting it running locally, and one core flow traced end-to-end through the real files.
- **Work On It** — the subsystems that change most often (picked from `git log`), the repo's conventions, and how a change actually ships here: branch, tests, CI, PR.

Every lesson cites real `file:line` locations and the exercises happen inside the repo — run it, trace it, write a failing test. The final project is a real change with tests passing, so you finish able to contribute rather than just able to describe the code.

State lives in `curriculum/<topic>/` (tracker, lessons, quizzes, projects), so progress survives across days and machines. Say `next` to continue, `quiz me` for a cumulative check, or `status` to see where you are.

## Changelog

- [x] `0.3.0` — the code factory: `/automate` becomes `/factory` (one feature, many, or a whole PRD; review once or `--auto`; parallel worktrees, integration branch, park-and-continue); a reviewer on a different model critiques every plan and diff; `/qa` runs four parallel checks with a proof rule; `/test` reviews the spec first and writes a risk-ranked suite of about 15 tests; evidence tags and a five-question self-check in every stage; walkthroughs in STE with `ai-sdlc ste-check`; new `/design` skill with `.sdlc/DESIGN.md`; Bug Ledger MCP as bug memory with `.sdlc/BUGS.md` as fallback; optional code graph; stage subagents with fixed models and guard hooks installed by the CLI
- [x] `0.2.0` — pipeline redesign: new `/plan` (diagnose & teach a ticket in plain language, no code) and `/test` (independent tester writes the tests from the spec before build) skills; specs split into human `walkthrough.md` + machine `spec.md` under `.sdlc/specs/<feature>/`; every stage runs as its own fresh agent with configurable model tiers; `/automate` adopts an agreed plan and runs with zero stops; git-workflow rules and `AGENTS.md` stubs from `/sdlc-init`; `/ship --pr` opens a self-explanatory pull request
- [x] `0.1.8` — PyPI and npm realigned on one version number, so `pip` and `npm` always ship the same kit
- [x] `0.1.7` — new `/mentor` skill: a long-term, file-tracked teacher for any topic, with a codebase mode that onboards you to a repo well enough to contribute to it
- [x] `0.1.6` — same kit on npm: `npm install -g ai-sdlc-kit` (zero-dependency Node CLI); releases now publish to PyPI and npm together
- [x] `0.1.5` — `/automate` hands-free flow, stage skipping (`--skip-qa` / `--skip-ship`), plain-English bug log (`.sdlc/BUGS.md`) that feeds future specs, and specs now open with a mental-model section (what / why / how) presented in chat
- [x] `0.1.4` — code-craft rulebook: `.sdlc/CRAFT.md` pins stack versions + modern idioms, enforces folder structure (one concern per file), env-based config with `.env.example`, and a security baseline across `/spec`, `/build`, `/qa`
- [x] `0.1.3` — added a Getting started section: how to actually invoke the skills for a new project, an existing codebase, or a single feature
- [x] `0.1.2` — automated PyPI releases via GitHub Actions trusted publishing
- [x] `0.1.1` — cleaner README, professional package presentation
- [x] `0.1.0` — initial release: 6 core skills + architecture-diagram, pip-installable CLI

---

The STE writing rules are an unofficial paraphrase in the style of ASD-STE100; this project is not affiliated with or endorsed by ASD. ASD-STE100 is a trademark of ASD.

Related prior art: [github/spec-kit](https://github.com/github/spec-kit).
