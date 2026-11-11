---
name: process-todo-section
description: Process exactly one TODO section end to end. Resolve it, validate and fact-check the plan against the repository, correct every drifted claim, build it, run the gates, hand to review, and commit. Use whenever asked to process, implement, ship, continue, or finish a TODO section.
---

# Process TODO Section

The section is the contract, and a contract is checked before it is signed.

Processing a section is two jobs, in order. First establish that the plan is sound: internally consistent, still true of the code and of its governing documents, buildable as written, and verifiable when built. Then implement it. Do not improvise around the plan, and do not implement a plan you have found to be wrong. Correct it in the file, visibly, then build the corrected version.

## Use this skill when

- The user names a section in any form: a `DNN TNN §N` reference, a path plus section, or a row pasted straight out of `todo/implementation-plan.md`. Step 0 turns all of them into the same thing.
- A runner picks the next ready row from the plan.
- Do not use it to audit shipped work: that is `review-todo-section` in audit stance.

## Step 0: resolve the argument before anything else

Never hand-translate a reference into a filename. Ask the graph:

```powershell
python scripts/todo-graph.py resolve "$ARGUMENTS"
```

It prints the path, title, phase, needs, dependencies (met and unmet) and the section body. Its exit code is the instruction:

| Exit | Meaning | Do this |
| :-: | --- | --- |
| 0 | Open, dependencies met, no waiting Need | Proceed to step 1. |
| 1 | No such section | Stop; report the reference as unresolvable. |
| 2 | No section reference in the input | Stop and ask which section. |
| 3 | The section is already `[x]` | Hand to `review-todo-section` in audit stance. |
| 4 | Waiting on deps, file status, or person Need | Stop at the gate and name what it waits on. |

Use the printed `skill_arg` (`DNN TNN §N`) as the canonical form for the rest of the run, including the commit message and the review call.

If the section carries `windows-host`, `arm64-host`, `display-session`, `office`, `libreoffice` or `attended` in Needs, confirm that environment is actually reachable before writing `Started:`. If it is not, stop and say what the section waits on: starting an environment-bound section without the environment burns a session producing nothing committable.

Before the first edit in a session, read `todo/README.md` (the format every TODO edit must keep). Before any write, stop here if another writer holds the tree. Check `git status` for unfamiliar uncommitted work you do not understand, and ask before building over it.

Write `Started:` now. If the section body carries no `> **Started:**` line, add one directly under its heading with the current UTC instant. Do not overwrite an existing one on resume.

## Execution discipline

- **Validate before building.** Step 2 is a gate, not a formality.
- **Follow the corrected contract.** The checklist items define the scope. Adjacent wrongness gets filed with `add-todo` (or in `todo/findings.md` with `file:line` when it is genuinely out of scope), not fixed in passing inside this section's work. The standing rule to fix what you find applies at the owning layer with its own owner; it does not widen this section.
- **Commits follow logical steps.** A section may be committed in one or more commits as steps complete; review fix-loop commits append to the candidate range, never amend. Plan corrections ride with the section commits or land as their own `todo:` commit first when substantial.
- **Never mark `[x]` without evidence.** The Implementation Order row flips only through `stamp`, after review. This skill never flips a row itself.
- **User data first.** Every file write follows the foundation plan's saving rule: temporary file in the destination folder, then atomic replace (`ReplaceFileW`, `MoveFileExW`, or `os.replace`). Read back what was written. Destructive paths are confirmed. The checkpoint exercises a failure path, not only the happy path.
- **The layer rules hold.** Respect the module boundaries and thread-safety contract in `AGENTS.md` and the foundation plan. A fix that violates the module table is wrong even when it works.
- **Fidelity is the bar on surfaces.** Build against `design/SPEC.md` and its screenshot, using tokens from `design/tokens/` only. No raw hex value on a control.

## Delegation

The main loop is the lead (`AGENTS.md`, Subagents): it decides, builds the section and every review fix itself (owner, 2026-11-11: the main session is the writer, so the owner can follow the development), runs the gates and the review loop, triages and quotes. The readers read and run; no agent writes (owner, 2026-11-11). Hand a step over when its result can be checked, start independent readers in one message so they run side by side, and keep working on what does not depend on them. One command's worth of work is never delegated.

- **Step 4, the build:** the main loop builds the section itself, as the Workflow's step 4 says, an architecture decision record under `docs/specs/` included. No agent writes (owner, 2026-11-11: the Opus `section-writer` and the Fable `principal-implementer` were removed), so there is no work packet to hand over and none to accept or reject. A build that is hard is the main loop's to split along its Build order steps, never to delegate.

- **Step 2, facts about the tree:** `code-explorer` locates the paths, symbols, counts and XREFs the section names (through the `LSP` tool where a language server is loaded) and `git-runner` reads the history of the touched paths and of the section's deferrals. Brief them with the section ref and the exact names to find.
- **Step 2, facts about the world:** on a decision, specification or interoperability section, `source-researcher` answers numbered questions of fact from primary sources, each with its URL and quotation.
- **Step 4, gates while iterating:** `test-runner` runs the affected test files, and the full suite (`python scripts/run-tests.py`) when the change is wide, writing each full log to scratch and returning its path.
- **Steps 4 and 6, a gate that fails for no evident reason:** `debug-evidence` collects the timeline, the state and a safe reproduction before any theory is formed.
- **Never delegated:** the seven answers of step 2 and every plan correction, the plan review's remedies, any write under `todo/` or `docs/reviews/`, every commit, anything that drives Office or the desktop (one desktop, one driver), the Test checkpoint of step 6, and the report.

What keeps the quality the main loop would have delivered alone:

- Evidence quoted in a commit body, a findings file or a `--check` comes from a command the main loop ran itself, or from the full log an agent wrote, opened and read by the main loop. An agent's summary is never quoted as evidence.
- A correction, a tick or a deletion never rests on an agent's word alone: the main loop opens every `file:line` and URL it relies on, and repeats the search itself before it treats "not found" as absence.
- A brief is self-contained (section ref, exact paths or commands, the scratch folder, the size of reply wanted) and, to a reader, asks for observations, never for a verdict or a fix.
- A reader that fails, times out or returns nothing useful is not retried in a loop and never parks a section: the main loop does that step itself.
- An agent whose reply the main loop's own check proves wrong (a wrong fact, a wrong result, a claim it did not verify) is removed from the fleet as `AGENTS.md` (Subagents) says, in its own commit, before the section carries on.

## Workflow

### 1. Read the whole contract

Read the entire TODO file, not just the section: Goal, Current state, Inputs and Adjacency carry context the section assumes. Read the sections this one depends on: their `Verified:` stamps and receipts tell you what actually shipped versus what was planned. Read the governing excerpts named in Inputs (foundation plan sections, SPEC sections).

### 2. Validate the plan before building it

Seven questions, each answered against the repository and the governing documents rather than from memory:

| Check | What you are asking | The failure it catches |
| ----- | ------------------- | ---------------------- |
| Legitimacy | Does the plan, SPEC, or spec demand this? | Unwanted work invented by the plan |
| Currency | Do named files, classes, and APIs match? | Section pinned to a moved path |
| Consistency | Do items agree with Current state and deps? | Contradictory items in one file |
| Correctness | Do stated behaviors match the source/SPEC? | Stale behavior ported into code |
| Sufficiency | Can this build without inventing decisions? | Section becomes a design session |
| Verifiability | Can the checkpoint run and fail on fixtures? | Unfalsifiable checkpoint passes |
| Accuracy | Are paths, counts, refs, and deferrals true? | Authority citing moved facts |

Ground each answer: `python scripts/todo-graph.py validate`, searches over `src/` and `tests/` for the named symbols, `git log --oneline -5 -- <touched paths>`. Check deferrals in both directions with `python scripts/todo-graph.py query deferred`: deferrals this section owns are part of its scope; deferrals this section wrote get re-read against today's tree (owner shipped means close it as `Resolved:`, changing only the marker so the deferring section's contract digest, and its receipt, still hold; description drifted means correct it; work quietly done elsewhere means verify it, close the deferral, and tick the owner's item).

Anything unclear becomes a question answered from the source. Where the source is silent, take the industry-standard option, record that it is a default with the cost of changing it, and carry on.

### 3. Correct the section when validation fails

Fix findings in the TODO file, before implementation, so plan and build never disagree in the record. Stale facts are corrected in place and marked `**Corrected YYYY-MM-DD:**` with what they said before. Contradictions resolve toward the source and the later decision. Overlong `Deliverable` cells or `## N. <Title>` headings (`> 88` characters) are shortened to a concise noun phrase so raw Markdown table rows do not wrap. Unbuildable or coarse 1-bullet summary items are decomposed into concrete five-part micro-steps (one action, named path/symbol in backticks, `Done when:` in the same bullet, `Cheaper substitute:` on UI and write items, and source citation). Items already 100% implemented in the codebase are ticked with the XREF, `file:line`, or commit SHA that shipped them; half-implemented items stay `[ ]` and are rewritten to name the exact missing pieces. Genuinely wrong work is struck with a stated reason, never silently dropped. An unfalsifiable checkpoint is rewritten so it can fail. A **frozen** behavior that looks wrong is not changed in code or plan: record the question for the operator and continue around it. If the whole section is wrong, stop and report instead of implementing.

Correct the plan, never the goalpost: narrowing a section so the code you were about to write happens to satisfy it is fitting the contract to the implementation. Report every plan correction alongside the implementation. If step 2 finds nothing, say so in one line and move on.

### 3a. Plan review by the pinned reviewer (one pass, before any code)

One pass by the pinned reviewer asks whether building the corrected section as written gives the user a whole feature: every entry point, surface, state, error path, undo path and persistence read-back the feature implies, not only the piece the section names. `stamp` refuses the section without it.

Once the section is corrected, commit it (with `plan --sync`) so the reviewer reads the exact contract you will build; that commit holds the `Started:` line, and the plan review's candidate must be that commit or an earlier one. Check the pin (`python scripts/review_pin.py --check` prints `ok`) and make sure it is committed: the section runs under the pin committed at this review's candidate, and a later pin change does not move it. Fill the prompt into a scratch file from `docs/plan-review-prompt.md` with `review-prompt.py` (the section through `--ref`, which also finds its TODO file), then run it:

```powershell
python scripts/review-prompt.py --kind plan --candidate <full SHA of that commit> --ref "D<NN> T<NN> §<N>" [--fidelity <design source>] --governing <the spec or plan> --out <scratch-plan-prompt.md>
python scripts/review-dispatch.py --kind plan --candidate <full SHA of that commit> --writer claude --prompt <scratch-plan-prompt.md> --record docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md
```

`--fidelity` names the design source of a `Surface: yes` section and is left out otherwise. The reviewer reads the repository at the candidate, so the SPEC and inventory excerpts the section cites need no copying in.

The dispatcher sets the effort and the `plan` lens from the pin's `[schedule] plan` step and appends a `## Plan review` section to the section's own findings file, the one its round and completion review will also be recorded in; a findings file takes one returned plan review. The reply must carry its `LENS plan: clean` or `LENS plan: findings` line and a `HIGHEST:` line and end `PLAN: complete` or `PLAN: gaps` then its `OVERALL:` line, or it is recorded as no review.

On `PLAN: gaps`, give each gap one remedy. Fix every `P1` and `P2` gap in the section the same way as step 3 (corrected in place, dated), when the piece belongs to the section's single responsibility; otherwise, and for a `P3` you do not take, file a new section through `add-todo`, with an XREF back. Under the plan review in the findings file, add one line per gap: `- Planned: <gap> in <commit>` or `- Filed: DNN TNN §N (<gap>)`. There is no second plan review: the completion review after the build is what checks the result. Commit the findings file with the section and any filed sections, then build.

Failure and recovery, so an unattended campaign neither stops nor loops:

- No review (exit 1: the reviewer is missing, failed, timed out or blocked, or the reply lacks a required line): run the pass once more. A second failure parks the section with the reason in the run file, the campaign takes its next ready row, and this section is retried once at the next phase start; a failure there parks it for the owner.
- Exit 2 (an argument or the pin was refused, the pass is out of order, or `--record` refused the file): nothing was appended. Fix what the message names. A findings file the dispatcher cannot read names its first unreadable line: a writer's own note must not sit under a heading that starts `## Round`, `## Plan review`, `## Completion review` or `## Reconciliation review`.
- A session that dies resumes from the findings file: a returned plan review is never dispatched again.
- A section reopened by `unstamp` starts a fresh cycle: `unstamp` kept its old findings file under a revoked name, so write a new `Started:` line, commit, and run a new plan review into the section's findings file as above.

### 4. Build the corrected contract

Work the Build order and micro-step checklist top to bottom. Tick each micro-step item as its `Done when:` becomes true, in the file, as you go; never tick a partially finished item (`partial-flip-shipped` is fatal). If every micro-step in the section was already 100% implemented in the codebase, do not churn working code just to manufacture a diff: verify every `Done when:` and `Cheaper substitute:`, write any missing falsifiable test, run the checkpoint in Step 6, commit the ticked checklist and verification evidence in Step 7, and hand to `review-todo-section`. Write the failing test first where the section names one. Build the cheaper substitute's failure into the checkpoint so the wrong thing cannot pass. UI sections consume the shared controls and slots named in `**Chrome:**` (one shell window, named slots, the own GUI toolkit's controls); a second toolbar, panel or dialog shape is a defect.

Run gates while iterating, bounded to the touched area: the build for the touched projects, the affected test cases, and CLI runs over the named corpus files. Warnings are errors at the configured level.

### 5. Surface and feature completeness

Before the checkpoint, account for 100% of every control, menu item, dialog and state on the Fidelity screenshot and SPEC section: each is working (proven on the rendered surface with real data and read-back) or deferred to a named, resolving section (`python scripts/todo-graph.py resolve '<ref>'` must not exit 1 or 2). A control disabled with a reason that names no section is missing, not deferred. Confirm the refusal/error/recovery path and undo/reverse path required by the section hold. `review-todo-section` refuses the stamp for an unaccounted control, so decide here.

### 6. Run the Test checkpoint, for real

Execute the checkpoint command and read the output. Quote the result in the commit body. If the checkpoint cannot run (no host, no fixture, no corpus file), the section is not done: record what ran, what did not and why, and stop without a stamp. Then run the section's other owed gates: affected tests green, build warnings clean, `python scripts/todo-graph.py validate` clean, and the `**Freeze check:**` in frozen files.

### 7. Commit, then hand to review

Commit the section work (in one or more commits as steps complete), recording the checkpoint evidence in the final implementation commit body:

```text
<area>: <what now works> (<DNN TNN §N>)

<checkpoint output, quoted>
<plan corrections, if any>
```

Then invoke `review-todo-section` on the same ref. Review writes the stamp (through `stamp`, which flips the row and syncs the plan). Commit the stamp and the regenerated plan as the stamp commit (`todo: stamp <ref>`).

### 8. Report

Tell the user plainly: what was built, what the checkpoint proved (quoted), what plan corrections were made, what was filed rather than fixed, and where the stamp stands. End with the `Layer:` line the standing rules require.

## Guardrails

- Do not implement a section you judged wrong. Correct it or stop.
- Do not widen the section. File adjacent work.
- Do not flip the Implementation Order row or hand-write `Verified:` lines. `stamp` owns both.
- Do not claim a checkpoint passed without running it: quote the output.
- Do not build a UI surface the SPEC does not describe. The SPEC change ships first.
- Do not end with the plan unsynced.
