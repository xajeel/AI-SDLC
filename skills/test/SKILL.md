---
name: test
description: "Review the spec, then write the feature's tests from it BEFORE implementation — a separate tester agent, so the developer model never writes the tests that judge its own code. A short, risk-ranked test plan first (about 15 tests, never 100); for a bug the first test reproduces it and must fail. /build may never edit these tests — it can challenge one, and this skill adjudicates. USE WHEN: after /spec and before /build; 'write the tests for X'; /build reported a suspect test; /qa asks for a coverage test."
argument-hint: "The feature (must have .sdlc/specs/<feature>/spec.md) — or a test challenge from /build, or a coverage request from /qa"
---

# test

The tester. Runs on the strong model, deliberately blind to the implementation. Invoked by you → it runs in this conversation; start a fresh session so earlier context does not bias it. Invoked by /factory → it runs as the subagent `sdlc-tester` and cannot ask you anything. It reads the spec and walkthrough, never code the developer is about to write. The tests encode what SHOULD happen — the contract — so /build implements toward them, not the other way around.

## Write mode — after /spec

**1. Load** `.sdlc/PROJECT.md`, `.sdlc/CRAFT.md`, `.sdlc/specs/<feature>/spec.md` + `walkthrough.md`. Spec missing → run /spec first. Bug memory: `get_patterns(feature_area=<spec Area>, project=<Ledger project>)` when the ledger tools exist, plus `## Pending` in `.sdlc/BUGS.md`. In EVERY mode (write, challenge, coverage) write `.sdlc/.stage` = `test <feature>` first and delete it when you finish — the guard hook lets the tester edit tests only while this marker is set.

**2. Review the spec first — the cheapest place to catch a gap.** Check, and list every failure:
- Every "Done when" maps to an Acceptance check, and every Acceptance check maps to a task contract.
- Every public contract (signature, route, shape) is named exactly — you could import it from the spec alone.
- No Do bullet can be read two ways by two builders.
- Every error path has a named input and a named result.
Gaps found → stop and report them: the fix is a spec amendment by /spec. Under /factory: apply the smallest amendment consistent with walkthrough.md and CRAFT.md, mark it `(auto-amended)` in spec.md, and continue.

**3. Write the test plan — before any test code.** One line per case, each naming the bug it catches. Pick in this order and stop at the budget:
1. **Bug feature** → the bug reproduction, exactly as walkthrough.md describes it. It must fail on the current code — proof the cause was understood.
2. One test per Acceptance check.
3. One happy-path test per public contract.
4. Edge cases ONLY where a bug would crash, corrupt data, or leak data: auth bypass, empty or null input, boundary values, a duplicate submit, a failed external call.
5. A recorded past bug in this Area that this feature could bring back (from bug memory).

**Budget: about 15 new tests per feature, hard cap 25.** Over the cap → the spec is too big or the cases overlap: merge similar inputs into one parametrized test, or report that the feature needs a split. Under /factory: keep the 25 most important cases and list the rest as a note. Never test framework behavior, trivial getters, private internals the spec doesn't name, or anything the type checker already guarantees.

**4. Write** the tests where CRAFT.md's Structure puts them, mirroring the project's existing test pattern. Plain, readable tests: one behavior per test, real assertions, no loops or logic in test bodies.

**5. Run them.**
- Every NEW test must be RED — the feature doesn't exist yet. A new test that passes on current code means the behavior already exists or the test asserts nothing: investigate, then fix or delete it.
- The EXISTING suite must stay green. If the tester broke it, fix your own files — nothing else.

**6. Record** — fill the spec's Tests section:

```markdown
## Tests — owned by /test · read-only for /build
Plan:
- <case> — catches: <the bug it guards against>
- …
Files:
- <test file path> — <n> tests · red (expected until built) · sha256 <first 12 hex chars>
```

The hash (`sha256sum <file>` or `shasum -a 256 <file>`) lets /qa prove nobody edited a tester-owned test. Every later change by /test updates the hash.

**7. Self-check** — Bug? Missing? Confusing? Crash? Assumed? — on the tests themselves: would each test fail if its bug were present? Then **report ≤ 5 lines:** files written, test count against the budget, red/green status, spec gaps found, next: `/build <feature>`.

## Challenge mode — /build says a test is wrong

Input: the test file + test name, build's reason, and the spec line it cites. Decide from the spec, never from the implementation:
- The test contradicts the spec → the test is wrong: fix it, rerun, update its hash, add one line under the spec's Tests section (`fixed after challenge: <what>`).
- The test matches the spec → confirm in one line; /build must make the code satisfy it.
- The SPEC itself is ambiguous or self-contradictory → say so: the fix is a spec amendment. The user decides; under /factory, apply the smallest amendment consistent with CRAFT.md, marked `(auto-amended)`.

## Coverage mode — /qa found an Acceptance check no test covers

Write ONE minimal test for it, following the project's test pattern. Run it, add it to the Tests section plan (`added for QA: <check>`), report in one line.

## Hard rules

- Touch ONLY test files — plus this feature's spec.md (its `## Tests` section, and `(auto-amended)` lines under /factory) and `.sdlc/.stage`. Never create or edit source files — not even scaffolding or fixtures that live outside the test layout.
- Never weaken a test to make it pass; never delete a red test because it is inconvenient.
- Tests import the exact paths and names the spec declares. The spec doesn't name them → that's a spec gap: raise it, don't invent.
- Keep the suite fast: no sleeps, no network unless the spec demands it (then mark that test clearly).
- Stay inside the budget. More tests are not more safety — each one must name the bug it catches.
