# UI check — QA check D

Runs only when the feature changes UI. Mechanical: run each check, record pass, FAIL, or SKIPPED.
- A failure needs proof — a screenshot path, `file:line`, or command output — and becomes `### [ ] F<n> — fix(ui): <what>` in spec.md. No proof → a note, not a failure.
- A check the environment cannot run → SKIPPED with the reason. SKIPPED never counts as a pass.
- Load `.sdlc/DESIGN.md` and the walkthrough's `## Design`. Live checks start the app with PROJECT.md `run:` and stop it afterwards.

1. **Screenshots** — browser or screenshot tool present → each changed screen at 375, 768, and 1440 px to `.sdlc/specs/<feature>/shots/after-<screen>-<w>.png`. Fail: sideways scroll, clipped or overlapping content, layout unlike the wireframe. `before-*` shots exist → name each thing that got worse.
2. **Keyboard only** — Tab through each changed screen: every control reachable, order matches the visual order, Enter / Space / Escape work, no focus trap. No browser → grep the diff for click handlers on non-interactive elements (`<div onClick`, `<span @click`); each hit fails.
3. **Focus visible** — every interactive element shows a focus ring (one shot per control type). `outline: none` or `outline-none` with no `:focus-visible` replacement fails.
4. **Contrast** — body text ≥ 4.5:1; large text and control edges ≥ 3:1. Measure in the browser, or compute from the DESIGN.md hex pairs.
5. **States** — each changed component has the states its Design section lists (empty, loading, error, disabled, hover, focus): trigger each, or cite the `file:line` that renders it. A missing state fails.
6. **Motion and touch** — under `prefers-reduced-motion: reduce`, non-essential animation stops. At 375 px every tap target is ≥ 44 × 44 px.
7. **DESIGN.md lint** — Node present → `npx @google/design.md lint .sdlc/DESIGN.md`. Any error fails; warnings are notes.
8. **Off-token values** — scan the added lines of the diff (`git diff -U0 <base>`, plus new files from `git status --short`):
   `grep -oE '#[0-9a-fA-F]{3,8}\b|[0-9]*\.?[0-9]+(px|rem|em)\b'`
   Each style value not found in `.sdlc/DESIGN.md` fails. Exempt: `0`, `1px` borders, percentages. Tailwind arbitrary values (`p-[13px]`) count; default palette classes (`text-gray-500`) fail when DESIGN.md defines its own colors.
9. **Copy** — buttons name what happens; errors say what to do next; empty states say what to do first; no lorem, placeholder, or TODO text; nouns match the walkthrough.

QA log line: `UI: <passed>/<run> · SKIPPED: <check (reason)> | none · Shots: <folder> | none`
