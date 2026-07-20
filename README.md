<p align="center">
  <img src="https://raw.githubusercontent.com/xajeel/AI-SDLC/main/assets/ai-sdlc-kit.png" alt="ai-sdlc-kit" width="320">
</p>

<h1 align="center">ai-sdlc-kit</h1>
<p align="center">Spec-driven SDLC skills that make AI coding agents work like real engineers.</p>

<p align="center">
  <a href="https://pypi.org/project/ai-sdlc-kit/"><img src="https://img.shields.io/pypi/v/ai-sdlc-kit.svg" alt="PyPI version"></a>
  <a href="https://www.npmjs.com/package/ai-sdlc-kit"><img src="https://img.shields.io/npm/v/ai-sdlc-kit.svg" alt="npm version"></a>
  <a href="https://github.com/xajeel/AI-SDLC/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
</p>

---

## What is it?

`ai-sdlc-kit` installs a set of skills for Claude Code, Cursor, Windsurf, and Gemini CLI that take an agent through a real engineering workflow instead of one-shot code generation:

**understand → decide → plan in verifiable steps → build with checks after every step → gate → ship**

| Skill | Does |
|---|---|
| `sdlc-init` | One-time setup: project facts + the code-craft rulebook (`.sdlc/CRAFT.md`) |
| `roadmap` | Splits a PRD into ordered, shippable features |
| `spec` | Plans one feature: decisions, tasks with contracts + verify commands |
| `build` | Executes the spec task-by-task, verifying after every step |
| `qa` | Re-runs verifies + acceptance checks; failures become fix-tasks |
| `ship` | Branch guard, staged commit built from the spec — never pushes |
| `automate` | Hands-free spec → build → qa for one feature; decisions auto-picked and logged |
| `architecture-diagram` | Renders a self-contained HTML/SVG architecture diagram |
| `mentor` | Teaches you a topic — or a whole codebase — one tracked lesson at a time |

## Install

```bash
# Python
pip install ai-sdlc-kit        # or: uv tool install ai-sdlc-kit

# Node
npm install -g ai-sdlc-kit     # or one-off: npx ai-sdlc-kit install --agent claude
```

Both give you the same `ai-sdlc` command and the same skills — pick whichever ecosystem you already have.

## Use

```bash
ai-sdlc install --agent claude   # or cursor / windsurf / gemini / all
```

This copies the skills into your agent's skills directory. They then appear as slash commands: `/sdlc-init`, `/roadmap`, `/spec`, `/build`, `/qa`, `/ship`, `/automate`, `/mentor`.

| Flag | Effect |
|---|---|
| `--agent all` | install for every supported agent at once |
| `--target PATH` | install into a specific project directory (default: `.`) |
| `--global` | install into your home directory instead of a project |
| `--force` | overwrite existing skill folders |

```bash
ai-sdlc list         # see bundled skills
ai-sdlc --version    # print the installed version
```

> **Monorepo, or no Python project at the root?** Not a problem — `ai-sdlc install` only copies skill files into `.claude/skills/` (or your agent's folder); it never reads `pyproject.toml` or anything else at the target. Install the CLI once with `pipx install ai-sdlc-kit` or `uv tool install ai-sdlc-kit` so it works from any directory, then run it at your repo root — or run it from anywhere with `--target /path/to/root`.

## Getting started

Every project starts with `/sdlc-init` — run it once, in your agent, inside your project folder. It writes `.sdlc/PROJECT.md` (project facts + commands), `.sdlc/CRAFT.md` (the code rulebook: pinned stack versions with modern-idiom rules, folder structure, coding style, config & security rules — every build follows it), and `.sdlc/STATE.md` (feature tracker). It works two ways:

- **New project** — `/sdlc-init <path-to-your-PRD-or-description>`. It reads the doc and asks a few multiple-choice questions to fill any gaps (framework, DB, test runner, etc.).
- **Existing codebase** — `/sdlc-init` with no argument. It detects your stack and rules from lockfiles, manifests, and a handful of source files instead of asking you to describe it.

Either way you choose how the rules are set — provide your own, answer questions, or let the agent propose best practices — and it always shows you the stack and rules for approval before writing anything.

From there, pick the path that matches what you're doing:

| Situation | Commands |
|---|---|
| Building a whole project from a PRD | `/sdlc-init <PRD>` → `/roadmap <PRD>` → then `/spec <feature>` → `/build <feature>` → `/qa <feature>` → `/ship <feature>` for each feature in order |
| Adding one feature to an existing codebase | `/sdlc-init` (skip if already run) → `/spec <feature description>` → `/build <feature>` → `/qa <feature>` → `/ship <feature>` |
| Something else — bugfix, refactor, exploration | Skills are for planned feature work; for anything smaller just talk to your agent directly |
| Learning a codebase or a technology | `/mentor` — see [Learning a codebase](#learning-a-codebase) below |

`/roadmap` only makes sense for a whole project — it turns a PRD into an ordered feature list. For a single feature, skip straight to `/spec`.

The `/build → /qa → /build` loop is self-healing: QA never edits code, it appends fix-tasks to the spec, and `/build` executes them like any other task. `/ship` commits once QA passes — it never pushes.

Three workflow controls on top of that:

- **Skip a stage** — `/sdlc-init --skip-ship` (or `--skip-qa`) drops a stage from the flow; toggle any time mid-project with `--unskip-<stage>`. Handoffs and `/automate` bypass skipped stages; invoking one directly still runs it.
- **Hands-free mode** — `/automate <feature>` runs spec → build → qa back-to-back with zero questions: every design choice takes the recommended production-standard option and is recorded in the spec marked `(auto)`, so you can audit each one afterwards. It stops only for real blockers (a verify failing after 3 attempts, an unfixable regression). Add `--ship` to include the commit stage.
- **Bug memory** — `/qa` keeps `.sdlc/BUGS.md`, a plain-English log anyone can read: what went wrong, why it happened, how to avoid it. `/spec` and `/build` read it on every run so the same bug never ships twice.

## Learning a codebase

The other skills build software; `/mentor` teaches it. Point it at a topic ("teach me Kafka") or at the repo you're sitting in ("teach me this codebase") and it builds a curriculum, then teaches **one lesson per session** — never dumping the whole course at once — quizzing you at the end of each and only advancing once you pass.

For a codebase it reads the repo first, then runs a short course of one or two modules:

- **Map & Run** — what the project does, a guided tour of the directories, getting it running locally, and one core flow traced end-to-end through the real files.
- **Work On It** — the subsystems that change most often (picked from `git log`), the repo's conventions, and how a change actually ships here: branch, tests, CI, PR.

Every lesson cites real `file:line` locations and the exercises happen inside the repo — run it, trace it, write a failing test. The final project is a real change with tests passing, so you finish able to contribute rather than just able to describe the code.

State lives in `curriculum/<topic>/` (tracker, lessons, quizzes, projects), so progress survives across days and machines. Say `next` to continue, `quiz me` for a cumulative check, or `status` to see where you are.

## Changelog

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

Related prior art: [github/spec-kit](https://github.com/github/spec-kit).
