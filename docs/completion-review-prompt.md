# Completion and excellence review prompt

Fill this with `python scripts/review-prompt.py --kind completion --candidate <FULL_SHA> [--base <BASE_SHA>] [--ref "<DNN TNN §N>"] [--fidelity <source>] --purpose "<text>" --governing <file> --out <scratch file>` (`--help` lists every option, and it refuses a placeholder it has no value for), or by hand: copy this into a scratch file, fill in the placeholders, delete the lines that do not apply, and pass it to `scripts/review-dispatch.py --kind completion --candidate <FULL_SHA> --writer <claude|codex|agy> --prompt <file> --record docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md`. It runs once per section and is not counted as a round. Under a pin with `policy = "three-pass"` it is the last of the three passes: it reviews the final candidate, after the one round's findings are fixed and the gates rerun, and when it ends `COMPLETION: gaps` the gaps are repaired and checked by a reconciliation review (`docs/reconciliation-review-prompt.md`). Under a rotation pin it runs after the section is built and before the regular review rounds (`docs/review-round-prompt.md`).

---

You are an independent product reviewer. Do not modify any file. The candidate below is a feature a TODO section has just built. Answer two questions about it: is it complete for a user, and does it do the job better than the strongest alternative a user could pick instead. Report what is missing or weaker, not what is present and fine.

## Candidate

- Commit or range: `<FULL_SHA>` or `<BASE_SHA>..<TIP_SHA>` (inspect it with `git show` or `git diff`).
- TODO section: `<DNN TNN §N>` (its contract: `python3 scripts/todo-graph.py resolve "<DNN TNN §N>"`).
- The TODO file's Goal and Outcome (with its Adjacency line): `<path to the TODO file>`.
- Fidelity: `<the design source the section names>`, or `none (Surface: no)`.
- What the feature is for: `<one or two sentences: the user, the verb, what consumes the result>`.
- Governing documents: `AGENTS.md` and `<the plan, spec or competitive analysis that applies>`.

## Part 1: completeness

List every piece the feature needs to be complete for a user, then mark each one. Think the feature through end to end, the way a user meets it: an Open file feature also needs its menu item, toolbar button, keyboard shortcut, recent-files entry, drag-and-drop, error dialog and tests. Cover every kind below that applies:

- Controls, menu items and toolbar entries, each with its automation name and tooltip.
- Keyboard shortcuts and command palette entries for every command.
- Dialogs, panels and every state they can show (empty, loading, partial, error, disabled with its reason).
- Settings and the code that reads each one (a setting nothing reads is missing).
- Error and refusal paths: hostile or malformed input, cancellation, a full disk, a locked file, a missing permission.
- The undo or reverse path of every create, change or delete.
- Persistence and its read-back: what is saved, where, written temp-file-then-replace, and read back on the next start.
- Tests that would fail if the piece broke.

Mark each item `present` (name the `file:line` or test that shows it), `missing-in-scope` (the section's contract, its Fidelity surface or its Goal covers it, so the section must build it) or `missing-out-of-scope` (a real need the section's contract does not cover, so it is filed as a new section; say which domain owns it).

Proportionality: list only needs that arise in this repository's real operation: real input the project accepts (a file, request or message from outside is hostile, so a crafted one a user receives is real), a real user action, or a real operating-system, disk or hardware condition. Do not list a need that only a contrived scenario creates (an attacker who already controls the machine, the clock, the repository, the build or the tools, or a precondition no real file, user or system produces).

## Part 2: excellence

The project must do each job better than the alternatives, not only reach parity. For this feature, name how the strongest competitor or alternative does the same job (the governing documents may name them; say which you are comparing with and what you know of its behaviour), then list each concrete way the delivered feature falls short of beating it:

- Speed: time to first result, time on a large or damaged file, work done on the UI thread.
- Steps: clicks, keystrokes and dialogs for the common case, counted against the competitor's.
- Defaults: what the user gets without changing anything.
- Error recovery: what happens on a bad file, a cancel, a crash or a full disk, and whether work survives.
- Accessibility: keyboard paths, screen-reader names and order, contrast, scaling, reduced motion.
- Polish: wording, feedback while it runs, consistency with the rest of the project.

Give each shortfall a measurable target where you can (a time, a step count, a golden image) and mark it `in-scope` (it fits the section's designed surface and behaviour, so the section builds it now) or `out-of-scope` (it needs a new section, or a design change first because it changes the designed surface). Never propose weakening an improvement that is already decided.

## Reply format

Part 1 as a numbered list of every item with its mark and evidence. Part 2 as the competitor named, then a numbered list of shortfalls, each with its target and mark. Then a numbered gap list that repeats every `missing-in-scope`, `missing-out-of-scope`, `in-scope` and `out-of-scope` item in one place, one line each, with its mark and a severity: `P1` (the feature ships incomplete, wrong or unproven in real operation), `P2` (a real gap with a narrower reach) or `P3` (polish, an unlikely edge case). Then a line naming the highest severity in that list: `HIGHEST: P1`, `HIGHEST: P2`, `HIGHEST: P3` or `HIGHEST: none`. Then a final line: `COMPLETION: complete` when the gap list is empty, or `COMPLETION: gaps` when it is not. If you could not read the candidate at all (the commit, the diff or the files), say why in one line and end with `COMPLETION: blocked` instead: that is not a review.
