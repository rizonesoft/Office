---
name: process-phase
description: Attended runner in Codex that takes one phase of todo/implementation-plan.md to 100 percent. Repair the phase, gap-check it, then ship section after section via process-todo-section plus review-todo-section, parking only when every leftover row is blocked here. Use when the user says process, run, or finish a phase.
---

# Process Phase

One phase, start to 100%, or parked when the rest of it cannot run here. You do not stop in between.

Exactly three endings: zero open rows and a written closeout; every leftover row blocked or waiting in this context, so the phase is parked and `process-plan` moves to the next ready phase; or the operator's own pause. A parked phase is neither complete nor a stall.

The whole plan is `process-plan`, not this skill. When the session entered through `process-plan`, return to it after closeout or park; a session pinned to one phase ends here.

Attended means interruptible, not stoppable: answer a mid-run message briefly and continue the loop in the same turn. The one exception outranks everything: if the user tells you to stop or pause, obey immediately, record it in the run file, and wait.

Completion never buys completion with a bypass: no `--no-verify`, no amend of a candidate under review, no force-push. A red gate is work, not a skip.

## Step 0: open the run

Check that no other writer holds the tree (`git status`; ask about unfamiliar uncommitted work). Writes are serial: this run is the only writer. Open the run file `docs/phase-runs/<YYYY-MM-DD>-phase-<N>.md` (create `docs/phase-runs/` if absent) and append every finding the moment it is made: the file survives session death where chat scrollback does not.

Run guard: if this run entered through `process-plan`, the plan holds the guard; confirm `whoami --session <its session id>` prints OWNER. If pinned to this phase, take the guard before this step's first write with `acquire --runner codex --cron-id none` exactly as this agent's `process-plan` Run guard section states, and end it through `end` however the run ends.

```markdown
# Phase run: <heading>

## Phase repairs              (Step 1: what was wrong with the plan, what was corrected, where)
## Shipped-row verification   (Step 1b: each spine [x] row, stamp and re-run checkpoint result)
## Gap audit                  (Step 2: gaps found, where each was filed; the park record lands here)
## Sections                   (Step 3: one entry per section: ref, outcome, review verdict)
## Critical events            (every stop, pause, resume, session death)
## Lessons                    (what was learned this run, worth keeping)
```

Read the most recent prior run file for this phase, if one exists: anything unresolved there is this run's first input.

## Step 1: repair the phase before running it

1. `python scripts/todo-graph.py validate`: fix every refusal now.
2. `python scripts/todo-graph.py plan --check`: if stale, `plan --sync`.
3. For every open row in the phase: `python scripts/todo-graph.py resolve '<ref>'`. Record the exit code. Exit 4 with unmet dependencies outside this phase, or a waiting Need this session cannot satisfy (`owner-decision`, `third-party`, `operator`, or a host that is not reachable), is a leftover, not a stall: leave the row, ship every exit-0 row, and park when only leftovers remain. Exit 1 or 2 means the plan cites a section that does not exist: repair the reference against the TODO files; a broken reference blocks a park.
4. Read each open section's TODO file top to bottom for phase-level staleness only (per-section validation happens again inside `process-todo-section`): work already shipped elsewhere, sections made moot by a later decision, Current state blocks contradicted by the tree. Correct with dated `**Corrected YYYY-MM-DD:**` notes.

### Step 1b: shipped rows are verified, not trusted

`[x]` rows are claims. Re-check the shipped rows an open row in this phase depends on (the spine): `resolve` exits 3, the receipt matches its stamp, and the section's Test checkpoint still passes when re-run. A checkpoint that no longer passes means the section regressed: treat it as this phase's work through `review-todo-section` in audit stance before building on it.

## Step 2: gap-audit the phase for 100% completeness

Read the phase as a user would use it, end to end, against its governing documents (the milestone "Done when" in the foundation plan, the SPEC sections the phase implements). Ask what is missing for a 100% complete phase: screens, dialogs, controls, settings consumers, refusal/error paths, undo/reverse paths, persistence read-backs, or handoffs between domains nobody specified. Split any coarse umbrella sections into small, single-responsibility sections and expand any summary checkboxes into concrete five-part micro-steps. File each gap with `add-todo` (evidence, owner, dependency) and sync the plan. Never cap planning or silently drop scope. A gap found is a gap filed the same turn.

## Step 3: ship the phase, one row at a time

In the generated plan's table order, for each open row: `process-todo-section`, then `review-todo-section`. Record each outcome in the run file. Commit the section work, then its stamp commit. Skip rows whose `resolve` is not exit 0 here, and re-check them after each stamp: the graph moves as rows flip. When every remaining open row is a leftover, the phase parks: write a column-0 `PARKED <UTC stamp> run=<run id> <one-line reason>` line in the run file (the run id the guard's `acquire` printed) followed by the park record (each leftover, what blocks it, where the blocker lives), commit the run file, and return to `process-plan`; a run pinned to this phase ends instead, through `end --reason park` as the guard requires.

## Step 4: closeout

When the phase table is all `[x]`: `process-todo-file` on any file the phase exhausted, re-run the full test suite once, confirm `query stats` and the regenerated plan show the phase complete, write the closeout under a `## Closeout run=<run id>` heading in the run file (the run id the guard's `acquire` printed) (what shipped, what was repaired, what was learned), commit, and report. A phase is complete when its table says so and the closeout is written: not before. Under `process-plan`, return to it, which re-points the guard; a run pinned to this phase ends through `end --reason closeout` as the guard requires.

## Guardrails

- Do not invent a side loop that ships rows outside `process-todo-section` plus `review-todo-section`.
- Do not tick `implementation-plan.md` by hand. It is generated; sync it.
- Do not claim a phase complete while its table has `[ ]` rows, and do not call a parked phase complete or a stall.
- Do not end the turn on the audit. Ship, park, or close out.
