---
name: process-plan
description: Front door in Codex for todo/implementation-plan.md. Audit the plan, then run process-phase on the first phase with a ready row, then the next ready phase after each closeout or park. Use when the user says process the plan. The argument --audit is audit only. A named phase is one phase and does not chain.
---

# Process the Implementation Plan

The only front door for `todo/implementation-plan.md` when the user did not name a single phase. The file is a generated projection of the 100% complete development plan (small, single-responsibility sections and granular five-part micro-steps): processing it is not "pick a row and improvise", and it is not "tick the boxes" (boxes flip only through `stamp`).

This skill does not ship a section and does not write a stamp. It audits, then chains `process-phase` runs until the plan is 100% complete or every leftover row is blocked here. Writes stay serial: the run this skill starts is the only writer on the tree.

## The loop

One continuous loop. You do not stop between sections or phases:

1. Take the run guard on the first phase with a ready row (Run guard, below: before the first write), audit (below), then start `process-phase` on that phase, in this same turn.
2. After that phase's closeout or park, re-run `python scripts/todo-graph.py query ready` and start the next ready phase.
3. Stop only when no phase has a ready row: every remaining `[ ]` row is blocked or waiting in this context, or the plan is done. That, and an operator stop, are the only halts.

A report to the operator is not a stop. An audit-only reply while a ready phase exists is a process defect: starting the phase is the next action, in the same turn. The self-correcting parts stay in the loop: drifted plan claims are corrected before building (inside `process-todo-section`), every gap and review leftover files through `add-todo`, and red gates are fixed, never bypassed (no `--no-verify`, no amend of a reviewed candidate, no force-push).

## 0. Route

```powershell
git status -sb
python scripts/todo-graph.py validate
python scripts/todo-graph.py query ready
```

| State | Do this |
| ----- | ------- |
| Another writer holds the tree | Stop and say so; never run two writers on one tree. A guard file (`build/claude-campaign-guard.json`) this session does not own is another writer. |
| Argument is `--audit` | Run the audit below read-only, then stop: report each refusal and a stale plan instead of repairing it, and write no run file. Repairs are a run's work, under its guard. |
| Argument is a phase (`0`, `Phase 0`) | Run `process-phase` for that phase only; do not chain. |
| Empty argument, "the plan", or path | Audit below, then chain ready phases. |

## 1. Audit the whole plan

```powershell
python scripts/todo-graph.py validate
python scripts/todo-graph.py plan --check
python scripts/todo-graph.py query ready
python scripts/todo-graph.py query blocked
python scripts/todo-graph.py query stats
python -m unittest discover -s scripts/tests
```

Fix every validator refusal before talking about shipping. If `plan --check` is stale, run `plan --sync` and re-check. The deep phase repair belongs to `process-phase` step 1; this audit is the commands above plus five recorded lines in the first phase's run file (`docs/phase-runs/<date>-phase-<N>.md`), not as the turn's last words:

1. Graph: valid section count, or the refusal.
2. Plan currency: the `--check` result.
3. Ready rows: count and first ref per phase.
4. Blocked rows: count and what blocks them (unmet dependencies, waiting Needs, unreachable hosts).
5. The phase being started, and why it is first.

Ready means runnable now in this context: `query ready` already excludes rows waiting on dependencies, inactive files and people Needs; rows needing a host this session cannot reach (`arm64-host`, `display-session`, `office`, `attended`) are leftovers here even when listed, and `process-phase` re-checks each row with `resolve` rather than trusting a previous list.

If no phase has a ready row, report the leftovers with their blockers and stop. That is a genuine halt.

### Run guard

Every run takes the run guard before its first write (the audit writes), so no two agents ever share the tree. Pick the first phase with a ready row from the read-only Route queries, then run `python scripts/campaign_guard.py acquire --runner codex --session codex-<UTC stamp, digits only>-<the output of python scripts/campaign_guard.py mint-generation> --phase <N> --run-file <run file> --cron-id none` and record the session id and the printed `run_id` in the run file's Critical events. A refused `acquire` means another writer (a Claude session or another runner) owns the tree: start nothing and report the owner. This agent has no Stop hook, heartbeat or keep-alive (Claude Code features; see `.conclave/automations/README.md`), so nothing resumes it. Every end marker carries the run id (`## Closeout run=<run id>`, column-0 `PARKED <UTC> run=<run id> <reason>`), and every way the run ends, an operator stop included, goes through `python scripts/campaign_guard.py end --session <that session id> --reason <closeout|park|plan-done|operator-stop|escalation>`. A question for the operator records `- waiting: <what> <UTC>` under Critical events and parks first with a `waiting: <what>` reason and ends the guard (the answer is recorded as `- go-ahead: <what> <UTC>`), so the tree is free while it waits.

## 2. After a phase closeout or park

`process-phase` ends in exactly one of three ways: the phase table is all `[x]` with a written closeout; every leftover is blocked here and it parked (a `PARKED` line and park record in its run file); or the operator paused it. A parked phase is not complete and not a stall. Do not call it either. A park whose reason starts `escalation:` or `waiting:` stopped the whole run for the operator and already ended the guard: report it and stop, never chain past it.

Re-run `python scripts/todo-graph.py query ready`. If another phase has a row this session can run (not a leftover of a phase this run already parked), start `process-phase` on it in the same turn, same session, same rules. If none does, the run halts, and a halt always ends the guard before the report: an empty ready list is `end --reason plan-done`; leftovers only (the last phase parked, its `PARKED` line in the guard's run file) is `end --reason park`. Then report which: plan done, or the leftovers and their blockers, with the run files named. When another phase does have a row to run, re-point the guard before its first write: `python scripts/campaign_guard.py acquire --runner codex --session <the same session id> --phase <new N> --run-file <new run file> --cron-id none`, and record the printed run id in the new run file; its markers carry that id.

## Deny

- Do not invent a side loop that ships rows outside `process-todo-section` plus `review-todo-section`.
- Do not start a second run, and do not resume a paused run unless the operator said resume.
- Do not tick `implementation-plan.md` by hand, and do not edit it at all: it is generated.
- Do not claim a phase complete while its table has `[ ]` rows.
- Do not treat a named phase as the whole plan. Chaining is this skill's job, and only this skill's.
- Do not end the turn on the audit table.
