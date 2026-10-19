---
name: review-todo-section
description: Quality-gate a just-implemented TODO section in Codex with self-review, independent review lenses and a bounded fix loop, then write the Verified stamp through the stamp command. Also runs in audit stance on shipped sections. Use after process-todo-section or when asked whether a section is really done.
---

# Review TODO Section

The gate between "code exists" and "the row says `[x]`". Nothing else may flip that row, and the flip happens only through `python scripts/todo-graph.py stamp`, which refuses a section with unticked items, an open prerequisite, a waiting Need, or no review evidence.

Review is mandatory and independent: the implementing session self-reviews, and at least one review round comes from a reviewer of a different model, the one pinned in `.conclave/reviewers.toml` (the `reviewer` kit: GPT-6 Astra by default, failing over to Gemini 4 then Sonnet 5.5; Codex-written work goes to Gemini 4 first), run through `scripts/review-dispatch.py`. Every round is recorded in a findings file; the stamp's receipt names the rounds. A verdict with no record is an opinion.

## Use this skill when

- A section was just implemented (`process-todo-section` ends by invoking this).
- The user asks "is §N really done?", "re-verify §N", "audit §N": run in audit stance (below).
- Before closing a TODO file with `process-todo-file`.

## Step 0: resolve the argument

Same front door as `process-todo-section`: `python scripts/todo-graph.py resolve "<section-ref>"`. Exit 3 means the row is already `[x]`: that is the signal for audit stance, not an error.

## The three questions

Every review answers these with code and behavior evidence, never assertion:

1. **Does it make sense?** Does the implementation produce the exact outcome the section asked for, without unnecessary scope?
2. **Is it logical?** Do the contracts agree: threading rules, error paths, settings consumers, UI states, failure behavior?
3. **Did it break anything else?** Inspect callers, consumers, tests and adjacent workflows that read what changed.

## Workflow

### 1. Fix the candidate

Name the candidate: the implementation commit, or the commit range (`<BASE_SHA>..<TIP_SHA>`) when the section landed across multiple logical step commits or when fix-loop commits append (commits are never amended once review starts). Record the full SHA(s) in the findings file at `docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md`. For an audit, the candidate is the section's own stamped commit, not today's tree. Read the actual diff (`git show` or `git diff <BASE_SHA>..<TIP_SHA>`), not memory of writing it. Map each ticked micro-step checklist item (its `Done when:` and `Cheaper substitute:`) to the code and test that satisfy it; an item with no corresponding change or a partially met `Done when:` (`partial-flip-shipped`) is not done (untick it) or was already true (note where).

### 2. Self-review

Work the three questions across the diff and its blast radius. Fix what you find, then re-ask them. Look specifically for the failure modes this codebase invites:

- The failure modes the project's `AGENTS.md`, foundation plan and SPEC call out for the area you touched: list them in the findings file and check each one.
- An error path that throws, aborts or swallows instead of returning the project's typed error, or a failure reported as success.
- Work on the wrong thread, mutable state shared across threads, or unbounded recursion or allocation on hostile input.
- A file write that is not temp-then-replace, or an original modified in place.
- A hard-coded colour, size or string where design tokens or settings own it, or a control without an accessible name.
- A setting nothing reads, a command nothing reaches, or a link or automation that acts without asking.
- A test that passes without exercising the behavior.

### 3. Independent review rounds (the pinned reviewer)

Run the lenses as separate passes over the candidate, at least one round by the pinned independent reviewer. Write the prompt to a scratch file from `docs/review-round-prompt.md` (candidate SHA, section contract, governing documents, lenses), then run it, naming your own agent as the writer (`claude`, `codex` or `gemini`):

```bash
python3 scripts/review-dispatch.py --writer <claude|codex|gemini> --prompt <scratch-review-prompt.md> --record docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md
```

The dispatcher fails over by itself and appends a `## Round N` section naming the reviewer, its model and any reviewer it skipped. Complete that round with the candidate SHA, per-lens verdicts (`approve`, `needs-attention` with numbered findings naming `file:line`, or `advisory`), and the quoted gate outputs (the Live proof). On Windows run `python` instead of `python3`. A repository without `scripts/review-dispatch.py` gets it with `forge.py kit . reviewer`.

| Lens | Asks |
| ---- | ---- |
| `adversarial` | How does this fail on hostile input, races, aborts, automation or links? |
| `consistency` | Does it match the module rules, naming, shared components and settings? |
| `integration` | Do callers and consumers still hold, with every contract kept? |
| `source-defect` | Is the upstream spec or SPEC read accurately with deviations noted? |
| `design` | Does the rendered UI match the design source and its tokens? |
| `record` | Does evidence match what ran, with owned deferrals and earned flip? |

The loop is bounded: at most 3 rounds. Findings are fixed in new commits appended to the candidate, gates re-run, and the affected lenses re-run against the new tip. A unit patched three rounds running is stopped and re-thought instead of patched again. Round verdicts for the receipt: `clean` (no findings), `fixed` (findings found and fixed in a later round), `stopped-at-3` (cap reached; every leftover is filed through `add-todo` with an owner, or the run stops with no stamp when a leftover is safety, data-integrity or stamp-invalidating). When the dispatcher exits 1 (no pinned reviewer could run), record the outage in the findings file with an owner and a due date and stop without a stamp: a session-only pass is not a substitute.

Architecture check: on sections touching an architectural boundary the foundation plan names (process or thread contracts, data ownership, module seams), one findings-file paragraph answers whether the change keeps the foundation plan architecture intact, naming any decision it effectively revises. A revision is recorded as a plan correction, never smuggled in as code.

### 4. Re-run the gates

After the last fix, re-run the section's Test checkpoint and its owed gates (affected test suites, build warnings clean, `validate`, the Freeze check in frozen files, ASan where the section names it). Quote the outputs in the findings file. A fix verified by reasoning is not verified. A red gate reopens the candidate: fix, re-run to green, and re-run the affected lens, because earlier verdicts rested on the broken candidate.

### 5. Surface, feature, and frozen checks

Surface and feature completeness: 100% of every control, menu item, dialog and state on the Fidelity counterpart is working (proven on the rendered surface with real data and read-back in this review) or deferred to a named, resolving section, and every required refusal/error/undo path is exercised. Refuse the stamp for an unaccounted control or a `Cheaper substitute` shortcut. Frozen files: every `**Freeze check:**` ran and passed with the result quoted; a frozen behavior that moved without a recorded operator approval means no stamp and a question for the operator.

### 6. Stamp

Tick nothing by hand. Confirm every checklist item except `Commit:` is `[x]`, then:

```powershell
python scripts/todo-graph.py stamp 'DNN TNN §N' --sha <full candidate tip SHA> --review '1:docs/reviews/<domain>/D<NN>-T<NN>-s<N>.md:clean' --check '<checkpoint command> -> <quoted result>'
```

One `--review` per round, one `--check` per gate actually run. `stamp` writes the receipt `docs/reviews/<ref>.json`, ticks the `Commit:` item and the Implementation Order row, appends the `Verified:` and `Review:` lines, marks the file `done` when its last section stamps, and the CLI syncs the plan. Commit the stamp, receipt, findings file and regenerated plan together as `todo: stamp <ref>`. Add any `Deferred:` lines (each with its `-> XREF:` owner) and `Started:` to `Duration:` notes to the section before stamping, since a stamped section's checklist is never rewritten; a later change is a new section that names the old one.

### 7. Audit stance

On an already-`[x]` section: run steps 1 to 5 against the section's own candidate and receipt. Confirm the stamp's evidence still holds (re-run the checkpoint) or find the regression. The only permitted row change is `[x]` back to `[ ]`, done by removing nothing silently: record the regression in the section as a dated blocking note, file the repair with `add-todo`, and say plainly that downstream sections stamped on this one are suspect until it re-stamps. A re-confirmed row keeps its stamp; say so in one line.

## Guardrails

- Do not stamp without a findings file and at least one independent round.
- Do not stamp an unaccounted control on a surface section, or a moved frozen behavior.
- Do not hand-write `Verified:` lines, hand-flip rows, or edit a receipt. `stamp` owns the record.
- Do not review the working tree when the candidate is a commit. Name the hashes.
- Do not transfer evidence across changed candidates: a new tip re-runs its gates.
