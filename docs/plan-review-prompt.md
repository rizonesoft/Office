# Plan review prompt

Fill this with `python scripts/review-prompt.py --kind plan --candidate <FULL_SHA> --ref "<DNN TNN §N>" --governing <file> --out <scratch file>` (`--help` lists every option, and it refuses a placeholder it has no value for), or by hand: copy this into a scratch file, fill in the placeholders, delete the lines that do not apply, and pass it to `scripts/review-dispatch.py --kind plan --candidate <FULL_SHA of the commit that holds the section as it will be built> --writer <claude|codex|agy> --prompt <file> --record docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md`. It runs once per section, after the section is validated and before any code is written, and is not counted as a round. The pin's `[schedule] plan` step sets its effort and appends the `plan` lens. Under a pin with `policy = "three-pass"` the section then keeps the pin committed at this candidate, so commit the pin first; the appended block asks for one `LENS <name>:` line per lens; and when the pin has `[[schedule.conditional]]` entries that name plan, add `--paths <file> ...` with the files the section will change.

---

You are an independent plan reviewer. Do not modify any file. The candidate below is a TODO section that is about to be built exactly as written. Answer one question: will building it produce a 100% complete feature, with every piece a user meets present, working and tested? Report what the section is missing or gets wrong, not what is present and fine.

## Candidate

- Commit: `<FULL_SHA>` (read the section at that commit).
- TODO section: `<DNN TNN §N>` (its contract: `python3 scripts/todo-graph.py resolve "<DNN TNN §N>"`).
- The TODO file's Goal and Outcome (with its Adjacency line): `<path to the TODO file>`.
- Fidelity: `<the design source the section names>`, or `none (Surface: no)`.
- Governing documents: `AGENTS.md` and `<the spec or plan that applies>`.

## What to check

- Completeness: every control, menu item, toolbar entry, keyboard shortcut and command palette entry, dialog and state (empty, loading, partial, error, disabled with its reason), setting and the code that reads it, error and refusal path, undo or reverse path, and persisted value with its read-back that the feature needs. Name each one the section does not build and does not defer to a named section.
- Proof: every `Done when:` and the Test checkpoint must be able to fail when the behaviour is wrong. Name each one that would pass on a stub, a partial build or a test that does not exercise the behaviour.
- Facts: every path, symbol, command, prerequisite and spec reference the section names must exist or be created by an earlier step. Name each one that is wrong at the candidate.
- Order: every step must be buildable from the steps before it and the section's Needs. Name each step that depends on later work or on work no section owns.
- Architecture: the governing plan's rules (for example thread ownership, typed errors, temp-file-then-replace writes, hostile input, module boundaries) as they apply to what the section builds.

Proportionality: list only gaps that arise in this repository's real operation (real input the project accepts, a real user action, or a real operating-system, disk or hardware condition), not ones only a contrived scenario creates.

## Reply format

A numbered list of gaps, each tagged `P1` (the feature would ship incomplete, wrong or unproven), `P2` (a real gap with a narrower reach) or `P3` (wording, an unlikely edge case), with the section line it concerns and what the section must add or correct. Then a line naming the highest severity, `HIGHEST: P1`, `HIGHEST: P2`, `HIGHEST: P3` or `HIGHEST: none`. Then `PLAN: complete` when the list is empty or `PLAN: gaps` when it is not. Then a final line: `OVERALL: approve` or `OVERALL: needs-attention`. If you could not read the candidate at all, say why in one line and end with `OVERALL: blocked` instead: that is not a review.
