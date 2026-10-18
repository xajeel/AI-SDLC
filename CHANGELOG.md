# Changelog

All notable changes to `ai-sdlc-kit`. Versions are published to PyPI and npm with the same number.

## 0.3.0 — 2026-10-18

The code factory: hand the kit one ticket, ten features, or a whole PRD.

### Added
- `/factory` — runs the pipeline for one feature, a list, `--roadmap`, or a PRD. Plans everything, has a reviewer critique each plan, stops once for your approval, then builds unattended. `--auto` removes the stop; `--ship` opens one PR per feature. Independent features build in parallel git worktrees and merge into an integration branch; blocked features are parked while the rest continue; runs resume from `.sdlc/RUN.md`.
- Cross-model review — a reviewer on a different model (default Opus 4.8, against Opus 5.5 planning and Sonnet 5.5 building) critiques every plan and every diff.
- `/qa` runs four checks in parallel: the gate, an adversarial review, a blast-radius check of callers outside the spec, and a UI check. A finding blocks only with proof. Tester-owned tests are hash-checked.
- `/design` — designs UI before code (new, redesign, or change) and keeps `.sdlc/DESIGN.md` in the open design.md format.
- STE writing rules for walkthroughs (simplified technical English, after ASD-STE100) and `ai-sdlc ste-check <file>`.
- Bug Ledger MCP as bug memory: stages check it before they work in an area, and every record needs your yes. `.sdlc/BUGS.md` is the fallback and the queue for unattended runs.
- Optional code graph (codebase-memory-mcp) for caller search and blast radius, with a grep fallback.
- Evidence tags (`[read]`, `[ran]`, `[doc]`, `[assumed]`) and a five-question self-check in every stage.
- `/test` reviews the spec before writing tests and keeps a risk-ranked budget of about 15 tests per feature (hard cap 25).
- The CLI installs five stage subagents with fixed models, the Bug Ledger MCP config, and — for Claude Code — two guard hooks: tester-owned tests are protected during `/build`, and pushes to protected branches and force-pushes are blocked.
- CLI flags `--no-bugledger` and `--no-hooks`; `ai-sdlc list` shows agents and hooks.

### Changed
- `/automate` is replaced by `/factory`. `ai-sdlc install --force` removes the old skill folder.
- `.sdlc/PROJECT.md` gains `Models:`, `Parallel:`, `Ledger project:`, `Code graph:`, `test-fast:`, and `install:`. Run `/sdlc-init` on a 0.2.x project to upgrade it in place.
- `.sdlc/BUGS.md` uses the Bug Ledger record fields; `/sdlc-init` converts old entries.
- `/plan` reads until every claim is proven instead of stopping at a fixed number of files.

### Removed
- `/automate`.

## 0.2.0 — 2026-08-10
- New `/plan` (diagnose and teach a ticket in plain language, no code) and `/test` (an independent tester writes the tests from the spec before build).
- Specs split into a human `walkthrough.md` and a machine `spec.md` under `.sdlc/specs/<feature>/`.
- Every stage runs as its own fresh agent with configurable model tiers.
- `/automate` adopts an agreed plan and runs with zero stops.
- Git-workflow rules and `AGENTS.md` stubs from `/sdlc-init`; `/ship --pr` opens a self-explanatory pull request.

## 0.1.8 — 2026-07-20
- PyPI and npm realigned on one version number.

## 0.1.7 — 2026-07-20
- New `/mentor` skill: a long-term, file-tracked teacher for any topic, with a codebase mode.

## 0.1.6 — 2026-07-19
- Same kit on npm (`npm install -g ai-sdlc-kit`, zero-dependency Node CLI); releases publish to PyPI and npm together.

## 0.1.5 — 2026-07-19
- `/automate` hands-free flow, stage skipping (`--skip-qa`, `--skip-ship`), a plain-English bug log (`.sdlc/BUGS.md`), and a mental-model section in specs.

## 0.1.4 — 2026-07-12
- Code-craft rulebook `.sdlc/CRAFT.md`: pinned stack versions and idioms, folder structure, env-based config, and a security baseline.

## 0.1.3 — 2026-07-12
- Getting-started guide for new projects, existing codebases, and single features.

## 0.1.2 — 2026-07-12
- Automated PyPI releases via GitHub Actions trusted publishing.

## 0.1.1 — 2026-07-12
- Cleaner README and package presentation.

## 0.1.0 — 2026-07-12
- Initial release: 6 core skills plus architecture-diagram, pip-installable CLI.
