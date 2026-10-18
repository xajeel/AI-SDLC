<p align="center">
  <img src="https://raw.githubusercontent.com/xajeel/AI-SDLC/main/assets/ai-sdlc-kit.png" alt="ai-sdlc-kit" width="320">
</p>

<h1 align="center">ai-sdlc-kit</h1>
<p align="center">A spec-driven, test-first code factory for AI coding agents.</p>

<p align="center">
  <a href="https://pypi.org/project/ai-sdlc-kit/"><img src="https://img.shields.io/pypi/v/ai-sdlc-kit.svg" alt="PyPI version"></a>
  <a href="https://www.npmjs.com/package/ai-sdlc-kit"><img src="https://img.shields.io/npm/v/ai-sdlc-kit.svg" alt="npm version"></a>
  <a href="https://github.com/xajeel/AI-SDLC/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
</p>

---

`ai-sdlc-kit` gives your coding agent an engineering team's workflow. It plans with you, writes the tests before the code, builds to those tests, and has a **different model** try to break the result — for one ticket or a whole PRD. Works with Claude Code, Cursor, Windsurf, and Gemini CLI.

## Install

```bash
pip install ai-sdlc-kit          # or: uv tool install ai-sdlc-kit
npm install -g ai-sdlc-kit       # or: npx ai-sdlc-kit install

ai-sdlc install --agent claude   # cursor | windsurf | gemini | all
```

`install` adds the skills, five stage subagents, the [Bug Ledger](https://github.com/xajeel/bugledger-mcp) MCP config, and — for Claude Code — two guard hooks. Existing config files are merged, never overwritten.

## Quick start

```text
/sdlc-init              once per project: stack, code rules, git workflow, models
/plan <ticket>          understand the problem and agree on a fix — no code yet
/factory <feature>      spec → review → tests → build → QA, unattended after one review
```

## Commands

| Command | What it does |
|---|---|
| `/sdlc-init` | Sets up `.sdlc/`: project facts, the code rulebook, git workflow, a model per role |
| `/roadmap <PRD>` | Splits a PRD into ordered, shippable features |
| `/plan <ticket>` | Traces the bug or feature through the real code and explains it — never writes code |
| `/design new\|redesign\|change` | Designs UI before code; keeps `.sdlc/DESIGN.md` |
| `/spec <feature>` | Turns the agreed plan into ≤ 8 tasks with contracts and verify commands |
| `/test <feature>` | Reviews the spec, then writes a focused test suite before the code exists |
| `/build <feature>` | Implements task by task until the tests pass — never edits them |
| `/qa <feature>` | Gate, adversarial review, blast-radius check, and UI check, in parallel |
| `/ship <feature> [--pr]` | Commits per your git workflow; `--pr` opens the pull request |
| `/factory …` | Runs the whole pipeline for any scope (below) |
| `/mentor` | Teaches you a topic or a codebase, one tracked lesson at a time |
| `/architecture-diagram` | Renders an HTML/SVG architecture diagram |

## The factory

```text
/factory <feature>          one feature or ticket
/factory f1 f2 f3           several features
/factory --roadmap          every open roadmap feature
/factory <PRD path>         a whole project: roadmap first, then every feature
   --auto                   no stops — a reviewer model replaces your review
   --ship                   open one PR per feature (never merged for you)
```

It plans every feature, has the reviewer critique each plan, and stops **once** for your approval. Then it builds unattended: independent features run in parallel git worktrees, each passing feature merges into an integration branch, and a stuck feature is parked while the rest continue. Progress and resume commands live in `.sdlc/RUN.md`.

## How it works

- **Separate roles.** Every stage runs in a fresh agent. The tester writes tests before the code; the builder can't edit them.
- **A second opinion.** A reviewer on a different model attacks every plan and every diff. Claude Code defaults: Opus 5.5 plans, Sonnet 5.5 builds, Opus 4.8 reviews.
- **Evidence, not confidence.** Claims about the code carry `[read path:line]` or `[ran cmd]`; nothing ships on `[assumed]`. A QA finding blocks only with proof.
- **Focused tests.** About 15 per feature, each naming the bug it catches.
- **Readable plans.** Each feature keeps a human `walkthrough.md`, in simplified technical English, next to a machine `spec.md`.
- **Bug memory.** Fixed bugs go to Bug Ledger after your yes, and every stage checks it before working in that area.

## CLI

```bash
ai-sdlc install [--agent NAME] [--target PATH] [--global] [--force] [--no-bugledger] [--no-hooks]
ai-sdlc list                      # bundled skills, agents, and hooks
ai-sdlc ste-check FILE...         # check a walkthrough against the writing rules
ai-sdlc --version
```

## Requirements

- Python 3.9+ or Node 18+ for the CLI, and git
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) for Bug Ledger
- `python3` on your PATH for the guard hooks
- Optional: [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) for faster caller search

## Upgrading from 0.2.x

```bash
ai-sdlc install --agent claude --force   # replaces /automate with /factory
```

Then run `/sdlc-init` in each project — it upgrades `.sdlc/` in place.

## Links

- [Changelog](https://github.com/xajeel/AI-SDLC/blob/main/CHANGELOG.md)
- [License (MIT)](https://github.com/xajeel/AI-SDLC/blob/main/LICENSE)

The writing rules are an unofficial paraphrase in the style of ASD-STE100; this project is not affiliated with or endorsed by ASD. ASD-STE100 is a trademark of ASD.
