<p align="center">
  <img src="https://raw.githubusercontent.com/xajeel/AI-SDLC/main/assets/ai-sdlc-kit.png" alt="ai-sdlc-kit" width="320">
</p>

<h1 align="center">ai-sdlc-kit</h1>
<p align="center">Spec-driven SDLC skills that make AI coding agents work like real engineers.</p>

<p align="center">
  <a href="https://pypi.org/project/ai-sdlc-kit/"><img src="https://img.shields.io/pypi/v/ai-sdlc-kit.svg" alt="PyPI version"></a>
  <a href="https://github.com/xajeel/AI-SDLC/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
</p>

---

## What is it?

`ai-sdlc-kit` installs a set of skills for Claude Code, Cursor, Windsurf, and Gemini CLI that take an agent through a real engineering workflow instead of one-shot code generation:

**understand → decide → plan in verifiable steps → build with checks after every step → gate → ship**

| Skill | Does |
|---|---|
| `sdlc-init` | One-time project setup: stack, layout, commands, conventions |
| `roadmap` | Splits a PRD into ordered, shippable features |
| `spec` | Plans one feature: decisions, tasks with contracts + verify commands |
| `build` | Executes the spec task-by-task, verifying after every step |
| `qa` | Re-runs verifies + acceptance checks; failures become fix-tasks |
| `ship` | Branch guard, staged commit built from the spec — never pushes |
| `architecture-diagram` | Renders a self-contained HTML/SVG architecture diagram |

## Install

```bash
pip install ai-sdlc-kit
# or: uv tool install ai-sdlc-kit
```

## Use

```bash
ai-sdlc install --agent claude   # or cursor / windsurf / gemini / all
```

This copies the skills into your agent's skills directory. They then appear as slash commands: `/sdlc-init`, `/roadmap`, `/spec`, `/build`, `/qa`, `/ship`.

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

## Getting started

Every project starts with `/sdlc-init` — run it once, in your agent, inside your project folder. It writes `.sdlc/PROJECT.md` (stack, layout, conventions) and `.sdlc/STATE.md` (feature tracker) that every other skill reads. It works two ways:

- **New project** — `/sdlc-init <path-to-your-PRD-or-description>`. It reads the doc and asks a few multiple-choice questions to fill any gaps (framework, DB, test runner, etc.).
- **Existing codebase** — `/sdlc-init` with no argument. It detects your stack from manifests/config and a handful of source files instead of asking you to describe it.

From there, pick the path that matches what you're doing:

| Situation | Commands |
|---|---|
| Building a whole project from a PRD | `/sdlc-init <PRD>` → `/roadmap <PRD>` → then `/spec <feature>` → `/build <feature>` → `/qa <feature>` → `/ship <feature>` for each feature in order |
| Adding one feature to an existing codebase | `/sdlc-init` (skip if already run) → `/spec <feature description>` → `/build <feature>` → `/qa <feature>` → `/ship <feature>` |
| Something else — bugfix, refactor, exploration | Skills are for planned feature work; for anything smaller just talk to your agent directly |

`/roadmap` only makes sense for a whole project — it turns a PRD into an ordered feature list. For a single feature, skip straight to `/spec`.

The `/build → /qa → /build` loop is self-healing: QA never edits code, it appends fix-tasks to the spec, and `/build` executes them like any other task. `/ship` commits once QA passes — it never pushes.

## Changelog

- [x] `0.1.2` — automated PyPI releases via GitHub Actions trusted publishing
- [x] `0.1.1` — cleaner README, professional package presentation
- [x] `0.1.0` — initial release: 6 core skills + architecture-diagram, pip-installable CLI

---

Related prior art: [github/spec-kit](https://github.com/github/spec-kit).
