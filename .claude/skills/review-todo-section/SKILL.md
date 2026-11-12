---
name: review-todo-section
description: Quality-gate a just-implemented TODO section with self-review, independent review lenses and a bounded fix loop, then write the Verified stamp through the stamp command. Also runs in audit stance on shipped sections. Use after process-todo-section or when asked whether a section is really done.
---

# Review TODO Section

The gate between "code exists" and "the row says `[x]`". Nothing else may flip that row, and the flip happens only through `python scripts/todo-graph.py stamp`, which refuses a section with unticked items, an open prerequisite, a waiting Need, or no review evidence.

Review is mandatory and independent: the implementing session self-reviews, and every external pass comes from the one reviewer `.conclave/reviewers.toml` routes the writer to (a different model family from the writer, no fallback), run through `scripts/review-dispatch.py --writer claude`: Claude Code is this repository's only writer. The pin's `[schedule]` owns each pass's reasoning effort and lenses, so the writer never picks them. Every pass is recorded in a findings file; the stamp's receipt names the passes. A verdict with no record is an opinion.

## Use this skill when

- A section was just implemented (`process-todo-section` ends by invoking this).
- The user asks "is §N really done?", "re-verify §N", "audit §N": run in audit stance (below).
- Before closing a TODO file with `process-todo-file`.

## Step 0: resolve the argument

Same front door as `process-todo-section`: `python scripts/todo-graph.py resolve "$ARGUMENTS"`. Exit 3 means the row is already `[x]`: that is the signal for audit stance, not an error.

## The review schedule

The pin's schedule is three-pass (owner decision 2026-11-11, with the import of the Conclave SDK reviewer kit): a plan review before the build, one round after it carrying every defect lens, one completion review of the final candidate, and reconciliations only after gaps. `python scripts/review_pin.py --check` loads the pin (it prints `ok` or the refusal), `python scripts/review_pin.py --lenses <plan|round|completion|reconciliation>` prints a pass's lenses with their questions, and `--caps` prints `pass_cap`. A section runs under the pin committed at its plan review's candidate (schedule and route both), so a later pin change never moves a section already planned. Sections stamped before 2026-11-11 keep the receipts they have: those are frozen by digest in `docs/reviews/legacy-receipts.json` and answer to the rules they were written under.

## The three questions

Every review answers these with code and behavior evidence, never assertion:

1. **Does it make sense?** Does the implementation produce the exact outcome the section asked for, without unnecessary scope?
2. **Is it logical?** Do the contracts agree: threading rules, error paths, settings consumers, UI states, failure behavior?
3. **Did it break anything else?** Inspect callers, consumers, tests and adjacent workflows that read what changed.

## Delegation

The reader subagents in `.claude/agents/` gather what the review weighs; no subagent reviews. The main loop triages every finding itself and writes the fixes itself (owner, 2026-11-11: the main session is the writer), each fix at its cause with a test that fails without it, asking what else in the candidate has the same fault, since a reviewer names one instance. The rules of `process-todo-section`'s Delegation section hold here too (the main loop opens what it relies on, quotes only output it ran or read in full, and does the step itself when an agent fails).

- **Step 1:** on a candidate of many commits, `git-runner` lists each commit's files and the later changes to the files the section owns.
- **Step 2:** `code-explorer` maps the callers and consumers of every changed symbol (through the `LSP` tool where a language server is loaded), which is the blast radius question 3 is answered against. `mutation-tester` measures "a test that passes without exercising the behavior": the main loop names the mutations (one per new check, refusal and boundary the section added), and a mutation that survives is a finding to fix before the round, not a note.
- **Step 4:** `test-runner` re-runs the owed suites and gates in the background, each log in scratch, while the main loop runs the section's Test checkpoint itself.
- **Never delegated:** the three questions, the triage of a reviewer's findings, the reading of every fix before it is committed, the stamp, and every review pass itself. The independent reviewer is the one `.conclave/reviewers.toml` pins and nobody else: a subagent's opinion of the candidate is not a review pass, is not recorded as one and never stands in for one when the dispatcher cannot run.

## Workflow

### 1. Fix the candidate

Name the candidate: the implementation commit, or the commit range (`<BASE_SHA>..<TIP_SHA>`) when the section landed across multiple logical step commits or when fix-loop commits append (commits are never amended once review starts). Record the full SHA(s) in the findings file at `docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md`. For an audit, the candidate is the section's own stamped commit plus every later change to the files it owns, up to today's tip (`<STAMPED_SHA>..HEAD -- <owned paths>`): a regression lives in those later changes. Read the actual diff (`git show` or `git diff <BASE_SHA>..<TIP_SHA>`), not memory of writing it. Map each ticked micro-step checklist item (its `Done when:` and `Cheaper substitute:`) to the code and test that satisfy it; an item with no corresponding change or a partially met `Done when:` (`partial-flip-shipped`) is not done (untick it) or was already true (note where). On a stamped section (audit stance) edit nothing in the section by hand: record the item in the findings file, and when it is a regression, run `unstamp` first; the item is unticked in the reopened section afterwards.

### 2. Self-review

Work the three questions across the diff and its blast radius. Fix what you find, then re-ask them. Look specifically for the failure modes this codebase invites:

- The failure modes the project's `AGENTS.md`, foundation plan and SPEC call out for the area you touched: list them in the findings file and check each one.
- An error path that throws, aborts or swallows instead of returning the project's typed error, or a failure reported as success.
- Work on the wrong thread, mutable state shared across threads, or unbounded recursion or allocation on hostile input.
- A file write that is not temp-then-replace, or an original modified in place.
- A hard-coded colour, size or string where design tokens or settings own it, or a control without an accessible name.
- A setting nothing reads, a command nothing reaches, or a link or automation that acts without asking.
- A test that passes without exercising the behavior.

### 3. Review passes

The passes run in this order for the section's findings file (`docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md`). Each pass is on a commit descending from the one before, the dispatcher refuses a pass out of order before a reviewer runs, and it refuses a second pass while one is running. Commit the pin before the section's plan review: the section runs under the pin committed at that review's candidate.

1. **Plan review**, before the build (`process-todo-section` step 3a): `--kind plan --candidate <commit holding the section>`.
2. **The round**, after the build, its gates and its commit. Fill the prompt into a scratch file from `docs/review-round-prompt.md` with `review-prompt.py` (the candidate, the section through `--ref`, what the change is for and the governing documents), then run it with the candidate (required), adding `--surface` on a `Surface: yes` section so the `design` lens joins:

```bash
python3 scripts/review-prompt.py --kind round --candidate <full tip SHA> --ref "D<NN> T<NN> §<N>" --purpose "<one or two sentences>" --governing <the spec or plan> --out <scratch-round-prompt.md>
python3 scripts/review-dispatch.py --kind round --candidate <full tip SHA> --writer claude [--surface] --prompt <scratch-round-prompt.md> --record docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md
```

   The dispatcher appends a `## Round 1` section and the pin's lenses (the lens table below is the vocabulary). Verify every finding against the code, fix what is real in new commits appended to the candidate, record why anything else is not real under a `## Writer note:` heading, and re-run the gates (step 5). There is no second round: the dispatcher refuses one.
   **Triage the round's findings before the completion review.** Once the round's findings are fixed and the gates are green again, and before the completion review is dispatched, give every finding of the plan review and of the round that was confirmed and fixed one line in the record's triage file, `docs/lessons/triage/<path>.md` for `docs/reviews/<path>.md`: `<pass> finding K: <disposition> [reason]` (the pass written `plan` or `round N`), the disposition being `lesson:<id>` (the kind can recur and no check stops it), `enforced:<path>` (a check or test in the repository now stops it) or `one-off` with a reason (`docs/lessons/README.md`). Write the lesson file for each new `lesson:<id>`. A lesson this section's own work made enforceable (it added the check or the test) is retired in the same commit: `status: retired` with `retired_by` naming it. Run `python scripts/lessons.py check` until it exits 0 and commit the lines and the lessons, so they are in the candidate the completion review reads. A completion review's gaps, and the new findings of a reconciliation, are triaged the same way (`completion finding K`, `reconciliation N finding K`) once they are fixed and before the next reconciliation is dispatched; the gaps of the last pass before the stamp are left to that record's next visit, since a line written after the stamped candidate is in no reviewed commit. On a resumed section run `python scripts/lessons.py candidates --untriaged --p3 <the record>` (`--p3` because a fixed `P3` finding is triaged too) and write only what it prints: a finding never gets a second line. All four kinds of pass are covered: the plan review, the round, the completion review and each reconciliation (D00 T05 §9).
3. **The completion review** of the final candidate: prompt from `docs/completion-review-prompt.md`, filled by `review-prompt.py` (the candidate SHA, the section and its TODO file's Goal and Outcome through `--ref`, the design source named in Fidelity as `--fidelity` (leave it out on `Surface: no`), what the feature is for and, as `--governing`, the section's spec or plan; `docs/product-principles.md` is what its second part is judged against):

```bash
python3 scripts/review-prompt.py --kind completion --candidate <full tip SHA> --ref "D<NN> T<NN> §<N>" [--fidelity <design source>] --purpose "<one or two sentences>" --governing <the spec or plan> --out <scratch-completion-prompt.md>
python3 scripts/review-dispatch.py --kind completion --candidate <full tip SHA> --writer claude --prompt <scratch-completion-prompt.md> --record docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md
```

   It judges the built feature as a user meets it and against the strongest competitor or alternative: part 1 lists every control, state, error path and read-back the feature needs, each `present`, `missing-in-scope` or `missing-out-of-scope`, and part 2 lists where it falls short of beating the alternative, each `in-scope` or `out-of-scope`. It ends `COMPLETION: complete` or `COMPLETION: gaps`. A findings file takes one returned completion review.
4. **Reconciliation after gaps.** On `COMPLETION: gaps` the stamp is blocked and the failed review stays on record. Implement every in-scope gap in new commits without changing what the section promises (its checklist text: the stamp compares it between the failed completion and each reconciliation), add one line per gap under the review (`- Implemented: <gap> in <commit>`), re-run the gates, then run a reconciliation on the new tip with a prompt filled from `docs/reconciliation-review-prompt.md` (put the gate output in a file for `--gates`; after a reconciliation that returned gaps add `--last <the SHA that reconciliation reviewed>`, otherwise `--last` defaults to `--failed`):

```bash
python3 scripts/review-prompt.py --kind reconciliation --candidate <full new tip SHA> --ref "D<NN> T<NN> §<N>" --failed <the failed completion's SHA> --findings docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md --gates <scratch-gates.txt> --governing <the spec or plan> --out <scratch-reconciliation-prompt.md>
python3 scripts/review-dispatch.py --kind reconciliation --candidate <full new tip SHA> --writer claude --prompt <scratch-reconciliation-prompt.md> --record docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md
```

   It ends `RECONCILIATION: complete` or `RECONCILIATION: gaps`. After gaps, repair and run another. File each out-of-scope gap through `add-todo` as a new section and add a `- Filed: DNN TNN §N (<gap>)` line under the review that raised it. Under a last pass that ended complete write no `- Filed:` line: the stamp reads those lines under the last returned pass and takes them only with the `filed` verdict.

Every reply must carry one line `LENS <name>: clean` or `LENS <name>: findings` for each lens the dispatcher scheduled (it appends them to your prompt) and a `HIGHEST: P1|P2|P3|none` line before the final verdict lines. A `[[schedule.conditional]]` entry in the pin adds its lenses when the section changed a file under its paths, and a plan review takes those files from `--paths <file> ...`. Headings that start `## Round`, `## Completion review`, `## Plan review` or `## Reconciliation review` are reserved for what `--record` writes: a writer's own note uses another heading (for example `## Writer note: ...`), or the file stops being readable and the next review is refused with the offending line named.

**A pass that will not converge (owner, 2026-11-11: no writer agent).** When a reconciliation returns a finding that an earlier repair was reported to have closed, or two in a row return blocking gaps, stop patching. Name in the findings file, under `## Re-think`, the cause the passes share; check every open finding against the section's purpose and record one about a case the repository does not have and the section does not promise as out of scope, not owed; and rebuild the unit that keeps failing so the whole class of finding cannot occur.

**How a section ends, case by case.** Do not stop to ask the operator in any of them.

- **The section cannot be stamped until something outside the run happens** (an owner decision filed as its own section, an event on a known date): park it. In the commit that records why (the `## Re-think` or the filed section), add `> **Parked:** <UTC instant> until <DNN TNN §N or UTC instant>: <what is waited for>` directly under its `Started:` line (`todo/README.md`, Started and Parked; D00 T03 §59). The section then leaves `query ready` and stops holding the dependency merge, and it returns to `query ready` by itself when the named section is stamped or the instant has passed. Never park a section to get past a finding that can be repaired now.

- **A reply recorded as incomplete** (exit 1: a missing `LENS` line, a missing `HIGHEST:` line, missing final verdict lines, or a complete verdict that declares a blocking severity; also any outage) is no review and did not count toward the cap. Its text is kept under a `none` section. Run the same command again; a session-only pass is not a substitute.
- **The last pass ended gaps and its worst finding is below the pin's `blocking` levels** (`P1` and `P2`). It takes no further pass and the dispatcher refuses a reconciliation. File each finding as a new section through `add-todo`, add a `- Filed: DNN TNN §N (<what>)` line for each under that last review in the findings file, and stamp with `--completion '<findings file>:filed'`.
- **A blocking gap** (a severity the pin's `blocking` lists) needs a reconciliation that ends `RECONCILIATION: complete`, stamped with `:reconciled`. Repair in new commits, re-run the gates and run the next reconciliation until one is complete.
- **The dispatcher refuses a reconciliation** because the section has spent the pin's `pass_cap` returned passes (plan, round, completion and every reconciliation count; the pin sets 33), or because `no_progress_cap` reconciliations in a row made no progress. The section stays unstamped: there is no cap-outcome verdict under three-pass, so never stamp at the cap with gaps open. Record it in the findings file under a heading of your own (for example `## Cap reached`, never one that starts with a reserved heading above: passes spent, every open gap) and in the run file, and carry on with the phase's other ready rows. `python scripts/review_pin.py --caps` prints the caps.

The lens vocabulary:

| Lens | Asks |
| ---- | ---- |
| `plan` | Will the section as written produce a 100% complete feature? (plan review only) |
| `plan-delivery` | Does the build deliver every planned item, with nothing quietly narrowed? |
| `adversarial` | How does this fail on hostile input, races, aborts, automation or links? |
| `consistency` | Does it match the module rules, naming, shared components and settings? |
| `integration` | Do callers and consumers still hold, with every contract kept? |
| `source-defect` | Is the upstream spec or SPEC read accurately with deviations noted? |
| `quality` | Is the code clear, tested where it can fail, and free of dead or duplicated logic? |
| `design` | Does the rendered UI match the design source and its tokens? |
| `optimization` | Is there avoidable work, allocation, latency or step count on a hot path? |
| `record` | Does evidence match what ran, with owned deferrals and earned flip? |

Architecture check: on sections touching an architectural boundary the governing plan names (process or thread contracts, data ownership, module seams), one findings-file paragraph answers whether the change keeps the governing plan's architecture intact, naming any decision it effectively revises. A revision is recorded as a plan correction, never smuggled in as code.

### 4. Re-run the gates

After the round's fixes, and after each repair before a reconciliation, re-run the section's Test checkpoint and its owed gates (affected test suites, build warnings clean, `validate`, the Freeze check in frozen files, ASan where the section names it). Quote the outputs in the findings file. A fix verified by reasoning is not verified. A red gate reopens the candidate: fix, re-run to green, and re-run the affected lens, because earlier verdicts rested on the broken candidate.

### 5. Surface, feature, and frozen checks

Surface and feature completeness: 100% of every control, menu item, dialog and state on the Fidelity counterpart is working (proven on the rendered surface with real data and read-back in this review) or deferred to a named, resolving section, and every required refusal/error/undo path is exercised. Refuse the stamp for an unaccounted control or a `Cheaper substitute` shortcut. Frozen files: every `**Freeze check:**` ran and passed with the result quoted; a frozen behavior that moved without a recorded operator approval means no stamp and a question for the operator.

### 6. Stamp

Tick nothing by hand. Confirm every checklist item except `Commit:` is `[x]`, then stamp, with the last returned pass having reviewed the stamped commit:

```powershell
python scripts/todo-graph.py stamp 'DNN TNN §N' --sha <full tip SHA> --plan 'docs/reviews/<domain>/D<NN>-T<NN>-s<N>.md' --completion 'docs/reviews/<domain>/D<NN>-T<NN>-s<N>.md:<complete|reconciled|filed>' --review '<N>:docs/reviews/<domain>/D<NN>-T<NN>-s<N>.md:<clean|fixed>' --check '<checkpoint command> -> <quoted result>'
```

The verdicts: `--completion` is `complete` (the completion found no gap), `reconciled` (it returned gaps and the last reconciliation ended complete) or `filed` (the last pass ended gaps whose worst finding is below the pin's `blocking` levels and every gap is on a `- Filed:` line). `completed` is not accepted. There is exactly one `--review`, for the one round that returned a review, under the number the dispatcher gave it: `1` when the first attempt returned, and the number in the `round` field of its summary (the `## Round N` heading that names a reviewer in the findings file) when an earlier attempt was an outage or an incomplete reply. Its verdict is `clean` when it approved, `fixed` when it found something that was then fixed. There is no `--cap-outcome`, no `stopped-` verdict and no severity stop. The receipt records `passes_spent` and `pass_cap`.

One `--plan` (required, naming the section's own findings file; `stamp` refuses without it, with any other file, with a findings file that holds no `## Plan review` returned by another model family and ending `PLAN: complete` or `PLAN: gaps` then its `OVERALL:` line, or with a plan review whose candidate is not the commit that recorded the section's `Started:` line or an earlier one), one `--completion` (required; `stamp` refuses without it, with an unknown verdict, with a findings file that holds no returned `## Completion review`, with a verdict the review's `COMPLETION:` line does not support, or with a `filed` verdict whose `- Filed:` refs are missing or do not resolve), the one `--review`, one `--check` per gate actually run. `stamp` also replays the section's pin (its `[schedule]` at the plan review's candidate) through the dispatcher's own scheduler and refuses any pass whose effort or lenses differ from what the schedule gave it, naming the pass, the expected and the recorded values; it also checks the chain itself: plan, one round, completion, then reconciliations, each on a later candidate than the pass before, the last on the stamped commit, within `pass_cap`. The receipt records the plan review (`plan`: findings file, candidate, reviewer, model, effort, lenses), the pin's schedule (`schedule`), the completion review (`completion`: findings file, verdict, candidate, reviewer, model, filed sections), `rounds_spent` (every round the dispatcher recorded in the findings file, outage rounds included), `round_cap`, `passes_spent` and `pass_cap`; `python scripts/todo-graph.py query rounds` lists them across stamped sections so the cap can be tuned. `stamp` writes the receipt `docs/reviews/<ref>.json`, ticks the `Commit:` item and the Implementation Order row, appends the `Verified:` and `Review:` lines, marks the file `done` when its last section stamps, and the CLI syncs the plan. Commit the stamp, receipt, findings file and regenerated plan together as `todo: stamp <ref>`. Add any `Deferred:` lines (each with its `-> XREF:` owner) and `Started:` to `Duration:` notes to the section before stamping, since a stamped section's checklist is never rewritten; a later change is a new section that names the old one.

### 7. Audit stance

On an already-`[x]` section: run steps 1, 2, 4 and 5 and the round of step 3 (and a completion review if wanted) against the section's own candidate and receipt (a receipt stamped before 2026-11-11 names a pre-build `-completion.md` record instead and stays valid as frozen), changing nothing in the section itself until `unstamp` has reopened it. Record the audit's rounds in a findings file of their own, `docs/reviews/<NN-domain>/audit-d<NN>-t<NN>-s<N>.md` (`--record` that path), never in the section's stamped findings file: its receipt names that file's last round, so a round appended there makes the receipt refuse validation and blocks `unstamp`. Confirm the stamp's evidence still holds (re-run the checkpoint) or find the regression. The only permitted row change is `[x]` back to `[ ]`, and only through `python scripts/todo-graph.py unstamp '<ref>' --reason '<what regressed; repair -> XREF: <ref>>'`, which removes the stamp lines, unticks the `Commit:` item and the row, reopens the file, keeps the receipt as `docs/reviews/<ref>.revoked-<date>.json` and the section's findings file as `D<NN>-T<NN>-s<N>.revoked-<date>.md` (the reopened section takes a fresh plan review, round and completion review) and adds an `Unstamped:` note stamped to the second (a hand edit leaves the graph refusing a checkbox/stamp mismatch). File the repair with `add-todo` first so the reason can name it, and say plainly that downstream sections stamped on this one are suspect until it re-stamps: they keep their stamps (the graph accepts a stamped section whose prerequisite carries an `Unstamped:` note) and `unstamp` prints them. A re-confirmed row keeps its stamp; say so in one line. The audit file is not named for a section, so it is a review outside a section: it has no order and no cap. Each `--kind round` call takes the pin's round lenses, `--candidate` is optional, and `--paths <file> ...` with the changed files adds the conditional lenses when the pin has `[[schedule.conditional]]` entries. Stop when a round's summary shows `"blocking": false`.

## Guardrails

- Do not stamp without a findings file holding the section's plan review, its one round, and a completion that was complete, reconciled or filed within the blocking levels.
- Do not run a second round, use a stopped verdict or a `--cap-outcome`, or stamp at `pass_cap` with gaps open.
- Do not stamp an unaccounted control on a surface section, or a moved frozen behavior.
- Do not hand-write `Verified:` lines, hand-flip rows, or edit a receipt. `stamp` owns the record.
- Do not review the working tree when the candidate is a commit or range. Name the hashes.
- Do not transfer evidence across changed candidates: a new tip re-runs its gates.
