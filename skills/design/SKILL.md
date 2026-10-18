---
name: design
description: "Design the UI before code exists — a new screen, a redesign, or a targeted change. Grounds every choice in the user and the screen's job, plans tokens and ASCII wireframes, audits what exists, and keeps .sdlc/DESIGN.md (open design.md format), the UI counterpart of CRAFT.md. Never writes product code. USE WHEN: 'design X', 'redesign this page', 'the UI looks generic', 'change the look of X', or /plan finds that a ticket changes UI."
argument-hint: "new <brief> | redesign <path or url> | change <what>"
---

# design

Decides how a UI looks, reads, and behaves before /spec turns it into tasks. `.sdlc/DESIGN.md` is to UI what CRAFT.md is to code: /plan reads it, /spec names its tokens, /build never steps outside it, /qa lints it and runs `ui-check.md`. Runs on the strong model (`sdlc-planner`) in a fresh agent. Every claim about existing code carries an evidence tag: `[read path:line]`, `[ran <cmd> → <result>]`, `[doc <source> <version>]`, or `[assumed]`.

## Procedure

**1. Load** `.sdlc/PROJECT.md`, `.sdlc/CRAFT.md`, and — if present — `.sdlc/DESIGN.md` and the feature's `walkthrough.md`. PROJECT.md or CRAFT.md missing → run sdlc-init first.

**2. Pick the mode** — from the argument; under /plan, infer it:
- **new** — no UI exists for this screen yet
- **redesign** — the screen exists and its look or flow is the problem
- **change** — add to or adjust a screen; the visual system stays

**3. Detect the stack — never assume.** Read the package manifest, styling setup, and component folder: framework, styling method (plain CSS, modules, Tailwind, CSS-in-JS), component library or primitives, icon set, existing tokens (CSS variables, theme file, Tailwind config). Tag each fact.
UI exists but DESIGN.md does not → **extract it first**: grep the colors, font families, sizes, spacing, and radii the code actually uses; count them; name the frequent ones as tokens; list the strays under Do's and Don'ts as debt. End `description` with `Source: extracted from code <date>` — it records what is, not what should be.

**4. Ground it** — ≤ 6 lines, before any visual choice:
- **Who** — the user, their device, how often they come, their state of mind.
- **Job** — the screen's one main job and its most important action.
- **Ambition** — must the screen *persuade* (marketing), *operate* (product, dashboard), *be read* (content), or *be experienced* (showcase, game)? This sets density, type contrast, and how much motion is welcome.
- **Feel** — three adjectives the user would sign off on.
- **Product UI only** — the domain's own vocabulary (labels use it) and one signature element that makes the screen unmistakably this product.
- **Build order** — native element → existing component or primitive → custom. Custom needs a reason.

**5. Work the mode.**

*new*
1. **Token plan** — one compact table: 4–6 named colors with hex and role, typeface roles (display, body, mono if needed), type scale, spacing scale, radius scale.
2. **Wireframes** — one ASCII sketch per screen, ≤ 15 lines; a second one for mobile when the layout changes.
3. **Self-review** — read the plan against step 4. A choice that would suit any product equally is generic: change it, or write one line on why it stays. Run the step-7 list. Revise now — a plan is cheap to change; shipped CSS is not.

*redesign*
1. **Audit** — score 0–10 with one evidence line each (screenshot or `[read path:line]`): hierarchy, layout and spacing, typography, color and contrast, components and consistency, states, responsiveness, accessibility, copy. Beside each score, write what a 10 looks like for *this* product.
2. **Refine or replace**, per dimension. Refinement keeps what works and tunes it; redesign throws it out. Keep a dimension scoring ≥ 7 unless the brief says otherwise.
3. **Before shots** — a browser or screenshot tool exists → capture each screen at 375, 768, and 1440 px to `.sdlc/specs/<feature>/shots/before-<screen>-<w>.png`. QA takes the matching after shots.
4. Then run *new* 1–3, starting from the current DESIGN.md.

*change*
1. **Reuse** — find the components and tokens already serving this area and use them. Add a token only when none fits; name it and say why.
2. **Findings need proof** — each problem you raise names the rule it breaks, the evidence on the rendered page (screenshot, or `path:line` when no browser exists), and one exact fix. No proof → drop it.
3. **Wireframe** only the part that changes.

**6. Quality floor** — every design meets it; the Design section says how wherever it is not obvious:
- Works from 375 px up with no sideways scroll.
- Visible focus; the whole flow works by keyboard, in visual order.
- Honors reduced motion; motion never carries meaning alone.
- Contrast ≥ 4.5:1 for body text, ≥ 3:1 for large text and control edges.
- Every state drawn: empty, loading, error, disabled, hover, focus — plus success where an action completes.
- Reading text runs about 45–80 characters per line.
- Touch targets ≥ 44 × 44 px.

**7. Defaults that need a reason.** These patterns make a UI look machine-made. None is banned; each one used needs a sentence on why it serves this brief. The user's brief always wins.
- The stock SaaS page: hero, logo strip, a grid of identical icon cards, CTA band.
- Headline text filled with a gradient; a purple-to-blue gradient as the brand.
- A small all-caps label perched over every heading.
- Cards nested inside cards.
- An arrow glyph on every button.
- Everything centered, long paragraphs included.

**8. Words.** A label says what happens ("Save draft", not "Submit"). An error says what went wrong and what to do next. An empty state says what to do first. Use the domain's nouns, not generic ones.

**9. Agree.**
- **Called by /plan** → return the draft (grounding, token plan, wireframes, ≤ 3 open questions). /plan shows it in its refine loop, then writes step 10 from the agreed version.
- **Standalone** → show the same in chat and refine until the user agrees.
- **Under /factory --auto** → no questions: take the option that best fits the grounding, mark each decision `(auto)`, and put every unknown in Open risks.

**10. Write the outputs.**
- **`.sdlc/DESIGN.md`** — from `DESIGN.template.md` next to this file (design.md format: YAML tokens, then prose sections in fixed order). Add tokens; never rename one silently — a rename of a token in use goes to Open risks with the files that use it. Prose in STE. Node available → `npx @google/design.md lint .sdlc/DESIGN.md`; fix every error, fix or note each warning.
- **`## Design` in `.sdlc/specs/<feature>/walkthrough.md`** — in STE (rules and checker: `../plan/ste.md`): mode, the step-4 grounding, direction (feel + signature element), token names used or added (values live only in DESIGN.md), wireframes, the audit table (redesign), quality-floor notes, and Decision lines in /plan's form. Standalone with no walkthrough → create it from /plan's template with `Agreed: pending` (the user's approval sets the date) and fill The ticket from the brief.

Standalone next step: `/spec <feature>` — or `/factory <feature>` for the full run.

## How the pipeline uses it

- /plan calls /design when a ticket changes UI.
- /spec: Do bullets name DESIGN.md tokens and components (`{colors.primary}`, `button-primary`), never raw values.
- /build: no color, size, font, radius, or shadow outside DESIGN.md. Needs one → stop and raise it; /design adds the token.
- /qa check D runs `skills/design/ui-check.md`.

## Hard rules

- Never write or edit product code. Output: DESIGN.md, the Design section, and before shots.
- Never assume the stack, components, or tokens — read them. No `[assumed]` left in anything code depends on.
- The user's brief overrides every default in this skill.
- Deeper polish wanted → mention, never install: Impeccable (`pbakaus/impeccable`), ui-ux-pro-max (`nextlevelbuilder/ui-ux-pro-max-skill`), or the shadcn skill (`shadcn-ui/ui`).
