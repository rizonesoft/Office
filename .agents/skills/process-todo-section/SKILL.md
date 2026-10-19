---
name: process-todo-section
description: Process exactly one TODO section end to end in Antigravity. Resolve it, validate and fact-check the plan against the repository, correct every drifted claim, build it, run the gates, hand to review, and commit. Use whenever asked to process, implement, ship, continue, or finish a TODO section.
---

# Process TODO Section

The section is the contract, and a contract is checked before it is signed.

Processing a section is two jobs, in order. First establish that the plan is sound: internally consistent, still true of the code and of its governing documents, buildable as written, and verifiable when built. Then implement it. Do not improvise around the plan, and do not implement a plan you have found to be wrong. Correct it in the file, visibly, then build the corrected version.

## Use this skill when

- The user names a section in any form: a `DNN TNN §N` reference, a path plus section, or a row pasted straight out of `todo/implementation-plan.md`. Step 0 turns all of them into the same thing.
- A runner picks the next ready row from the plan.
- Do not use it to audit shipped work: that is `review-todo-section` in audit stance.

## Step 0: resolve the argument before anything else

Never hand-translate a reference into a filename. Pass the section reference or pasted plan row (`<section-ref>`) to the graph:

```powershell
python scripts/todo-graph.py resolve "<section-ref>"
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

Write `Started:` now. If the section body carries no `> **Started:**` line, add one directly under its heading with the current UTC instant. Do not overwrite an existing one on resume.

Stop here if another writer holds the tree. Check `git status` for unfamiliar uncommitted work you do not understand, and ask before building over it.

## Execution discipline

- **Validate before building.** Step 2 is a gate, not a formality.
- **Follow the corrected contract.** The checklist items define the scope. Adjacent wrongness gets filed with `add-todo` (or in `todo/findings.md` with `file:line` when it is genuinely out of scope), not fixed in passing inside this section's work. The standing rule to fix what you find applies at the owning layer with its own owner; it does not widen this section.
- **Commits follow logical steps.** A section may be committed in one or more commits as steps complete; review fix-loop commits append to the candidate range, never amend. Plan corrections ride with the section commits or land as their own `todo:` commit first when substantial.
- **Never mark `[x]` without evidence.** The Implementation Order row flips only through `stamp`, after review. This skill never flips a row itself.
- **User data first.** Every file write follows the saving rule: temporary file in the destination folder, then atomic replace (`ReplaceFileW`, `MoveFileExW`, or `os.replace`). Read back what was written. Destructive paths are confirmed. The checkpoint exercises a failure path, not only the happy path.
- **The layer rules hold.** Respect the module boundaries and thread-safety contract in `AGENTS.md` and the foundation plan (e.g., `src/pdf` owns the native PDF engine, the UI thread never parses or renders PDFs, and a document belongs to its actor thread). A fix that violates the module table is wrong even when it works.
- **Fidelity is the bar on surfaces.** Build against `design/SPEC.md` and its screenshot, using tokens from `design/tokens/` only. No raw hex value on a control.

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

Ground each answer: `python scripts/todo-graph.py validate`, searches over `src/` and `tests/` for the named symbols, `git log --oneline -5 -- <touched paths>`. Check deferrals in both directions with `python scripts/todo-graph.py query deferred`: deferrals this section owns are part of its scope; deferrals this section wrote get re-read against today's tree (owner shipped means close it as `Resolved:`; description drifted means correct it; work quietly done elsewhere means verify it, close the deferral, and tick the owner's item).

Anything unclear becomes a question answered from the source. Where the source is silent, take the industry-standard option, record that it is a default with the cost of changing it, and carry on.

### 3. Correct the section when validation fails

Fix findings in the TODO file, before implementation, so plan and build never disagree in the record. Stale facts are corrected in place and marked `**Corrected YYYY-MM-DD:**` with what they said before. Contradictions resolve toward the source and the later decision. Overlong `Deliverable` cells or `## N. <Title>` headings (`> 88` characters) are shortened to a concise noun phrase so raw Markdown table rows do not wrap. Unbuildable or coarse 1-bullet summary items are decomposed into concrete five-part micro-steps (one action, named path/symbol in backticks, `Done when:` in the same bullet, `Cheaper substitute:` on UI and write items, and source citation). Items already 100% implemented in the codebase are ticked with the XREF, `file:line`, or commit SHA that shipped them; half-implemented items stay `[ ]` and are rewritten to name the exact missing pieces. Genuinely wrong work is struck with a stated reason, never silently dropped. An unfalsifiable checkpoint is rewritten so it can fail. A **frozen** behavior that looks wrong is not changed in code or plan: record the question for the operator and continue around it. If the whole section is wrong, stop and report instead of implementing.

Correct the plan, never the goalpost: narrowing a section so the code you were about to write happens to satisfy it is fitting the contract to the implementation. Report every plan correction alongside the implementation. If step 2 finds nothing, say so in one line and move on.

### 4. Build the corrected contract

Work the Build order and micro-step checklist top to bottom. Tick each micro-step item as its `Done when:` becomes true, in the file, as you go; never tick a partially finished item (`partial-flip-shipped` is fatal). If every micro-step in the section was already 100% implemented in the codebase, do not churn working code just to manufacture a diff: verify every `Done when:` and `Cheaper substitute:`, write any missing falsifiable test, run the checkpoint in Step 6, commit the ticked checklist and verification evidence in Step 7, and hand to `review-todo-section`. Write the failing test first where the section names one. Build the cheaper substitute's failure into the checkpoint so the wrong thing cannot pass. UI sections consume the shared controls and slots named in `**Chrome:**` (one `ShellPage`, named slots, stock WinUI controls); a second toolbar, panel or dialog shape is a defect.

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
