# STE writing rules

These rules apply to all text for humans in this kit: walkthrough.md, bug records, and the "Why" part of a PR description. They are an unofficial paraphrase in the style of ASD-STE100 (Issue 9). ASD does not endorse this kit, and the kit has no link to ASD. ASD-STE100 is a trademark of ASD.

Check a file: `python3 <plan skill dir>/scripts/ste_check.py <file>` (or `ai-sdlc ste-check <file>`). Fix every ERROR. Read every WARN and fix it, unless the word is a technical noun.

## Text types
- **Procedural** text tells the reader what to do. Use the imperative. 20 words per sentence maximum.
- **Descriptive** text tells the reader what is true or why. 25 words per sentence maximum.

## Words
1. Use simple, common words. A word has one sense in the whole file.
2. Give one thing one name. Do not change to a synonym later. Put project terms in the glossary.
3. You can use technical nouns: code names, file paths, commands, error text, and domain words. Put code in backticks. A code span counts as one word.
4. Do not use a technical noun as a verb.
5. Swap these words: `may` or `might` → can, `should` → must, `ensure` → make sure that, `utilize` → use, `perform` → do, `begin` → start.
6. Do not use a verb with a particle, such as `set up`, `find out`, or `carry out`. Use one verb: install, learn, do.
7. Do not use contractions, slang, or Latin abbreviations such as `e.g.`, `i.e.`, and `etc.`
8. Noun clusters: 3 words maximum. Break longer ones with "of", "for", or "in".

## Verbs
9. Use the imperative, the simple present, the simple past, or the simple future.
10. Do not use verb forms that end in `-ing`. Do not use the perfect tenses.
11. Use the active voice. Use the passive only when you do not know the actor.
12. Show an action with a verb, not with a noun ("check the token", not "do a check of the token").

## Sentences and paragraphs
13. One topic per sentence. Keep "the", "a", and "that". Do not delete words to make a sentence short.
14. A paragraph has one topic. Put the topic sentence first. 6 sentences maximum.
15. Connect sentences with "then", "but", or "because". Use a list for complex steps.
16. Do not use semicolons.

## Procedures
17. One instruction per sentence, unless the two actions occur at the same time.
18. Put the condition first: "If the test fails, read the log."
19. A note gives information. A note never gives an instruction.

## Risk
20. Put the risk label first: `WARNING:` for harm to people or data loss, `CAUTION:` for damage to code or systems. Then give the command, then the risk.

## Example
Bad: `We should probably be ensuring the token is getting validated before it's used; otherwise auth may break.`
Good: "The code must check the token before it uses the token. If the token is not valid, `login()` returns 401."
