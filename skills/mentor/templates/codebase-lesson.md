# Lesson <M.L> — <Title>

<!-- For type: codebase only. Voice: senior engineer onboarding a new
     teammate. Every claim about the code cites path:line. Every snippet is
     copied from the repo — never invented. Length scales with the tracker's
     time-per-session. -->

## Warm-up *(only if the tracker's Review Queue is non-empty)*

<2 quick questions on queued concepts. Grade them in chat before continuing.>

## 1. What & Why

<What this part of the codebase does, why the project needs it, and what
would break if it disappeared. Plain language — assume they know the stack,
not this repo.>

## 2. The Map

<The files and directories this lesson covers, as a small annotated tree —
one line each on what lives there and why it's separate.>

```
src/
  auth/            # <what it owns>
    middleware.ts  # <one-liner>
```

## 3. Code Walk

<Trace ONE real flow through the actual code, step by step, in execution
order. Each step: path:line, the relevant snippet (copied, trimmed), and
what it does in plain language. End with "open X and find Y yourself"
so they navigate, not just read.>

> **Checkpoint:** <1–2 questions — e.g. "which file would you open if
> symptom Z appeared?" Answers at the bottom of this file — say so.>

## 4. How It Connects

<Upstream and downstream: who calls into this, what it calls out to, and
the key interfaces/contracts at those boundaries. A tiny diagram is fine.>

## 5. Conventions & Gotchas

<Patterns this repo uses that the code walk showed (error handling, naming,
test style), plus the traps a new contributor hits here. Cite a real
example of each convention.>

## 6. Exercise

<One hands-on task done IN the repo within the session's time budget —
run it, trace it in a debugger, add a log line, write a failing test,
make a tiny reversible change. Include a "you know it worked when…"
success check and how to undo the change.>

## 7. Quiz

<3–5 questions mixing navigation ("where does X happen"), comprehension
("why is Y done this way here"), and transfer ("a user reports symptom Z —
which file do you open first?"). No answers here — the user replies in chat
and the mentor grades. Also saved to quizzes/<M>-<L>-quiz.md.>

---

<details><summary>Checkpoint answers</summary>

<answers to the checkpoint questions>

</details>
