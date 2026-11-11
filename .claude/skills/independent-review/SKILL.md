---
name: independent-review
description: Get an independent review of your own work from the reviewer pinned in .conclave/reviewers.toml (a different model family from yours) through scripts/review-dispatch.py, then verify and act on every finding. Use before calling a nontrivial change done, before a commit that ships, or when a TODO section needs its review round.
---

# Independent review

Your own review is not enough for a nontrivial change: a different model reviews it. `.conclave/reviewers.toml` names who reviews whose work and on which schedule, and `scripts/review-dispatch.py` runs each pass.

| Work written by | `--writer` | Reviewer (as installed) | Fallback |
| --- | --- | --- | --- |
| Claude Code | `claude` | GPT-6 Astra (`codex`, scheduled effort) | none |
| Antigravity | `agy` (or `gemini`) | GPT-6 Astra (`codex`, scheduled effort) | none |
| Codex | `codex` | none yet: the pin needs a reviewer of another family and a `codex` route | none |

Name your own agent as the writer. The pin as installed routes `claude` and `agy` to GPT-6 Astra through the Codex CLI in a read-only sandbox; the project owns its pin and may change it in `.conclave/reviewers.toml`. A route names exactly one reviewer, never of the writer's own model family, and the pin refuses an unrouted writer, an unknown CLI, a second reviewer or a same-family reviewer.

The pin's `[schedule]` sets each pass's reasoning effort and lenses, so the writer never picks them, and it has two shapes. Check which one applies first: `python scripts/review_pin.py --check` loads the pin, and `[schedule] policy` says which flow runs. `python scripts/review_pin.py --lenses <kind>` prints a three-pass pin's lenses for a pass and `--caps` prints its `pass_cap` and `no_progress_cap`.

- **Three-pass** (`policy = "three-pass"`, what a new install starts on): a plan review before the build, one round after it, one completion review of the final candidate, and a reconciliation only after a pass that returned gaps.
- **Rotation** (no `policy` key): a plan review, a completion review, then rounds at falling effort and one lens per round until a round has no `P1` or `P2` finding.

Proportionality: only a failure that can happen in real operation with real input is `P1` or `P2`; a contrived scenario (a hand-edited record, a tool used against its contract, an input no real user or tool produces) is `P3` at most.

## Steps

1. Review your own change first and fix what you find.
2. Fill the review prompt into a scratch file, not the repository, from `docs/review-round-prompt.md` with `review-prompt.py`, which names the candidate commit or range and the governing documents (the dispatcher adds the lenses). A review outside a TODO section has no `--ref`, so the prompt drops its TODO line:

   ```bash
   python3 scripts/review-prompt.py --kind round --candidate <full SHA> [--base <first SHA of the range>] --purpose "<one or two sentences>" --governing <the spec or plan> --out <scratch>/review-prompt.md
   ```

   It refuses (exit 2, nothing written) a placeholder it has no value for. Fill the template by hand only if the script is missing.
3. Run the pass naming the agent that wrote the change as the writer, never another: a writer the pin does not route refuses, which is no review. Pass `--surface` when the change ships a user-facing surface (`Surface: yes`), so the `design` lens joins:

   ```bash
   python3 scripts/review-dispatch.py --kind round --candidate <full SHA> --writer claude --prompt <scratch>/review-prompt.md --record docs/reviews/<topic>.md
   ```

   On Windows use `python` instead of `python3`; the command is otherwise the same.
4. For planned work in a TODO section (`review-todo-section` runs it), the passes and their order depend on the schedule:
   - Three-pass: `--kind plan` (prompt from `docs/plan-review-prompt.md`, filled by `review-prompt.py --kind plan --ref "D<NN> T<NN> §<N>"`) before the build, one `--kind round` after it, `--kind completion` (prompt from `docs/completion-review-prompt.md`, filled by `review-prompt.py --kind completion --ref "D<NN> T<NN> §<N>"`) on the final candidate, and `--kind reconciliation` (prompt from `docs/reconciliation-review-prompt.md`, filled by `review-prompt.py --kind reconciliation --ref "D<NN> T<NN> §<N>"`) after gaps. Every one takes `--candidate <40-character commit SHA>`. There is no second round, and a pass out of order is refused.
   - Rotation: `--kind plan` before the build, `--kind completion` after it and before the rounds, then the rounds. A round needs no `--candidate`.
5. Read the review. Every finding carries `P1`, `P2` or `P3` (an untagged one counts as `P1`), and the review ends with a `HIGHEST:` line. Under three-pass it also carries one line `LENS <name>: clean` or `LENS <name>: findings` per scheduled lens; a reply missing one, or its final verdict lines, is recorded as no review (exit 1) and did not count: run the pass again. Verify every finding against the code before acting: fix what is real, and record why anything else is not.
6. Commit fixes as new commits. What happens next depends on the schedule:
   - Rotation: run another round on the new tip, up to 33 rounds (a round that returns no review does not count). The first round with no `P1` or `P2` finding (`HIGHEST: P3` or none) ends the loop, from the round after the pin's `severity_stop_after` (the installed rotation pin sets 0, so from round 1); file its `P3` findings as follow-up work. A unit that needs patching three rounds running gets re-thought, not patched again.
   - Three-pass inside a section: the one round is already spent, so rerun the gates and continue with the completion review and any reconciliations as `review-todo-section` describes, up to the pin's `pass_cap`.
   - Three-pass outside a section (below): the round is repeated as often as you need.

## A review outside a TODO section

A findings file not named for a section (for example `docs/reviews/<topic>.md`, or the audit file `docs/reviews/<NN-domain>/audit-d<NN>-t<NN>-s<N>.md`) has no order and no cap. Under a three-pass pin each `--kind round` call takes the pin's round lenses, and `--candidate` is optional there. When the pin has `[[schedule.conditional]]` entries, pass `--paths <file> ...` with the files you changed so their lenses join (the dispatcher refuses `--paths` under a rotation pin). Fix the real findings in new commits and run another round on the new tip, and stop when a round's summary shows `"blocking": false` (under a pin without `blocking`, when the round ends `OVERALL: approve`).

## Rules

- The dispatcher's JSON output and the section it appends to the findings file are the evidence. A verdict with no record is an opinion.
- Exit 1 means no review: the reviewer was not installed, failed, timed out, returned nothing, replied `OVERALL: blocked`, or under three-pass returned an incomplete reply. No other reviewer runs in its place. That is never an approval: record the outage, say so, and do not ship on it.
- A reviewer that could not reach the work (its sandbox could not read the repository) replies `OVERALL: blocked`. Put the diff in the prompt and run the pass again.
- Reviewers run read-only. Never pass a reviewer a secret, and never ask it to edit files.
- Change reviewers only in `.conclave/reviewers.toml`, never by calling a model directly.
