# Reconciliation review prompt

Fill this with `python scripts/review-prompt.py --kind reconciliation --candidate <FULL_SHA> --failed <COMPLETION_SHA> [--last <LAST_SHA>] --findings <file> --gates <file> --governing <file> [--ref "<DNN TNN §N>"] --out <scratch file>` (`--help` lists every option, and it refuses a placeholder it has no value for), or by hand: copy this into a scratch file, fill in the placeholders, delete the lines that do not apply, and pass it to `scripts/review-dispatch.py --kind reconciliation --candidate <FULL_SHA of the repaired candidate> --writer <claude|codex|agy> --prompt <file> --record docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md`. It exists only under a pin with `policy = "three-pass"`. It runs after a completion review ended `COMPLETION: gaps` and its gaps were repaired and the gates rerun, and again after each reconciliation that ended `RECONCILIATION: gaps`, until one ends `RECONCILIATION: complete` or the section has spent the pin's `pass_cap` passes. The dispatcher appends its lenses from the pin, asks for one `LENS <name>:` line per lens and a `HIGHEST:` line, and refuses a pass out of order, past the cap, or after a pass whose worst finding is below the pin's `blocking` levels.

---

You are an independent reviewer. Do not modify any file. A completion review of this TODO section returned gaps, and the writer says they are repaired. Decide whether the repair really closes them. The obligations are the ones that review held the section to: the writer cannot narrow, reclassify or waive them to obtain approval. Only the owner can decide between two of them that conflict, as check 4 says.

## Candidate

- TODO section: `<DNN TNN §N>` (its contract: `python3 scripts/todo-graph.py resolve "<DNN TNN §N>"`).
- Findings file holding the failed completion review, any earlier reconciliations that returned gaps, and the writer's `- Implemented:` and `- Filed:` lines: `<docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md>`.
- The failed completion's candidate: `<COMPLETION_SHA>`.
- The last reviewed candidate (the failed completion's, or the last reconciliation's): `<LAST_SHA>`.
- The repaired candidate: `<FULL_SHA>`. The repair is `<COMPLETION_SHA>..<FULL_SHA>`, read all of it, with `<LAST_SHA>..<FULL_SHA>` the newest part.
- Gate results on the repaired candidate: `<quoted output>`.
- Governing documents: `AGENTS.md` and `<the spec or plan that applies>`.

## What to check

1. Every gap in the failed completion review and in each earlier reconciliation that returned gaps: closed or still open. A gap that review marked in scope (`missing-in-scope` or `in-scope`) is closed by the repair, shown by the `path:line` or test and the writer's `- Implemented:` line, with one exception: an obligation the owner gave up, which check 4 closes and nothing else does. Filing an in-scope gap elsewhere is narrowing the section's promise and leaves it open. A gap that review marked out of scope (`missing-out-of-scope` or `out-of-scope`) is closed when it is filed: a `- Filed: DNN TNN §N (<gap>)` line under the review that raised it, naming a section that exists (`python3 scripts/todo-graph.py resolve "DNN TNN §N"` does not exit 1 or 2) and whose text owns that gap. A filed section that does not resolve, or does not cover the gap, leaves it open.
2. Each repair: does it introduce a regression, a weakened test or a narrowed behaviour?
3. The section's contract: are its promises the same as when the completion review read them? The stamp compares the section's text at both commits and refuses a changed promise.
4. An owner decision between conflicting obligations. Sometimes two obligations the reviews held the section to cannot both be met in the same state, and the product's owner has chosen which one to keep. Such a choice counts only when all of this holds: it is a numbered, dated decision in the governing document named above, which is the owner's record and not the writer's; it identifies the gap, by naming this section, or the section filed to settle the gap (which names this one), or by saying plainly which behaviour is chosen; it was made after the failed completion review; and the writer's `- Decided: <gap> by owner decision <N> of <record>` line under the review that raised the gap points to it. Read the decision in the record itself. The obligation the owner kept is checked like any other. The obligation the owner gave up is `closed by owner decision <N>` when the candidate does exactly what the decision says, shows no more of the given-up behaviour than the decision allows, and a test holds that behaviour; say which test. A writer's note, a re-think, a filed section by itself, a decision that does not identify the gap in one of those ways, or one that predates the completion review, settles nothing: the gap stays open. A decision never closes a gap the repair could have closed without giving anything up.

The section's `- [ ] Commit:` item is ticked by `stamp` when it writes the section's `Verified:` line, so an unticked Commit item whose commit exists is never a gap.

Proportionality: report only what arises in this repository's real operation, not what only a contrived scenario creates.

## Reply format

Cite every repository location as `path:line` in backticks. Number each gap with `closed` or `open` and its evidence, then any new finding from the repair, each tagged `P1` (data loss, a security hole, a crash, a wrong result or a broken contract in real operation), `P2` (a real defect with a narrower reach) or `P3` (cosmetic, style, an unlikely edge case). Then the lines the dispatcher appends a request for: one `LENS <name>: clean` or `LENS <name>: findings` per lens, and `HIGHEST: P1`, `HIGHEST: P2`, `HIGHEST: P3` or `HIGHEST: none`. End with a final line: `RECONCILIATION: complete` only when every gap is closed and the repair introduced no real defect, otherwise `RECONCILIATION: gaps`. If you could not read the candidate or the findings file, say why in one line and end with `OVERALL: blocked` instead: that is not a review.
