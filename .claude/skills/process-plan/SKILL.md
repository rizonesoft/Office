---
name: process-plan
description: Front door for todo/implementation-plan.md. Audit the plan, then run process-phase on the first phase with a ready row, then the next ready phase after each closeout or park. Use when the user says process the plan. The argument --audit is audit only. A named phase is one phase and does not chain.
---

# Process the Implementation Plan

The only front door for `todo/implementation-plan.md` when the user did not name a single phase. The file is a generated projection of the 100% complete development plan (small, single-responsibility sections and granular five-part micro-steps): processing it is not "pick a row and improvise", and it is not "tick the boxes" (boxes flip only through `stamp`).

This skill does not ship a section and does not write a stamp. It audits, then chains `process-phase` runs until the plan is 100% complete or every leftover row is blocked here. Writes stay serial: the run this skill starts is the only writer on the tree.

## The loop

One continuous loop. You do not stop between sections or phases:

1. Audit (below), start the run guard (below), then start `process-phase` on the first phase with a ready row, in this same turn.
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
| Another writer holds the tree | Stop and say so; never run two writers on one tree. |
| Argument is `--audit` | Run the audit below, then stop. Do not start a run. |
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
python -m unittest discover -s tests/scripts
```

The two test runs are the kits' own tests, which kits install under `scripts/tests`, and the project's own script tests under `tests/scripts`; run both, skip only a folder the repository does not have, and add any further suite the project's `AGENTS.md` names. A project's tests are never dropped for the kits' or the other way round.

Fix every validator refusal before talking about shipping. If `plan --check` is stale, run `plan --sync` and re-check. The deep phase repair belongs to `process-phase` step 1; this audit is the commands above plus five recorded lines in the first phase's run file (`docs/phase-runs/<date>-phase-<N>.md`), not as the turn's last words:

1. Graph: valid section count, or the refusal.
2. Plan currency: the `--check` result.
3. Ready rows: count and first ref per phase.
4. Blocked rows: count and what blocks them (unmet dependencies, waiting Needs, unreachable hosts).
5. The phase being started, and why it is first.

Ready means runnable now in this context: `query ready` already excludes rows waiting on dependencies, inactive files and people Needs; rows needing a host this session cannot reach (`arm64-host`, `display-session`, `office`, `attended`) are leftovers here even when listed, and `process-phase` re-checks each row with `resolve` rather than trusting a previous list.

If no phase has a ready row, report the leftovers with their blockers and stop. That is a genuine halt.

### Run guard

A run without a guard dies silently when the session stalls, so starting the first phase also starts the run guard, always. It has two parts, and they cover different failures. There is no keep-alive outside the session: nothing relaunches a session that died.

- **Stop hook** (`python3 ... scripts/campaign_guard.py stop-hook`, wired in `.claude/settings.json`): while the run is open it blocks this session's end of turn and names the next ready row. It lets the turn end when the guard file is gone, the run file has a `## Closeout run=<run id>` heading or a column-0 `PARKED <UTC> run=<run id>` line, or `query ready` has nothing runnable. It blocks only the session named in the guard, never a subagent or a second session, and it fails open on a bad payload or an error, recording the error for the heartbeat. Its stall breaker lets the turn end after 3 blocks with no change to HEAD, the working-tree diff, the untracked files, or the run file without its `- bookkeeping:` lines, and counts a trip in `build/claude-campaign-state.json`. A heartbeat or retry note is written as a `- bookkeeping: ...` line, so it never passes for progress. `python forge.py doctor . todo` reports the hook as `setup_required` when `.claude/settings.json` does not run it.
- **Heartbeat** (`CronCreate`): it fires only when this session is idle and runs inside it with full context, so it is a real resume. It covers what the hook cannot hold: a tripped breaker, an API error, a turn that crashed out.

Commands here are written `python`; on Linux and WSL run them with `python3`. The heartbeat prompt says `<python>`: fill in the interpreter of the machine the session runs on.

Start it in this order:

1. Reconcile: `CronList`, then `python scripts/campaign_guard.py reconcile --session $CLAUDE_CODE_SESSION_ID --jobs <ids of every job whose prompt starts "Claude run-guard heartbeat", comma-separated>`, and do what it prints: `CronDelete` an orphan or stale job, and start nothing when another session owns the guard.
2. Mint a generation with `python scripts/campaign_guard.py mint-generation`, then `CronCreate` with cron `3-59/5 * * * *`, recurring, and the canonical prompt below with `<N>`, `<run file>`, `<generation>` and `<python>` filled in.
3. Acquire: `python scripts/campaign_guard.py acquire --session $CLAUDE_CODE_SESSION_ID --phase <N> --run-file <run file> --cron-id <job id> --generation <generation> --scope plan`. It writes `build/claude-campaign-guard.json` exclusively and prints the run's id, which every end marker of this run carries. A refused `acquire` means another session owns the run: `CronDelete` the job step 2 created, start nothing, and report the owner. The owning session re-points its own guard with the same command (a new phase or job); taking another session's live guard needs the operator's `--handover <reason>`.
4. Record the session id, job id, generation and run id in the run file's Critical events.

At every section boundary (after each stamp): `CronList`, then `python scripts/campaign_guard.py health --session $CLAUDE_CODE_SESSION_ID --jobs <live heartbeat job ids>` and `python scripts/campaign_guard.py expiry --session $CLAUDE_CODE_SESSION_ID`. A missing job, or one within 12 hours of its 7-day expiry, is replaced (steps 2 and 3 with a fresh generation) and the repair recorded.

The heartbeat dies with this session. A run resumed in a new session takes the guard with `acquire --handover <reason>` and a new job and generation; the old session's heartbeat then reads `NOT THE OWNER` and deletes itself.

Every way a run ends (closeout of the last phase, park with nothing left, plan done, operator stop, escalation, a stall) goes through `python scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason <closeout|park|plan-done|operator-stop|escalation|stall>`, never a direct delete. It checks that path's marker, deletes the guard and state files, and names the heartbeat job: `CronDelete` it, confirm it is gone with `CronList`, then run `python scripts/campaign_guard.py cancel-confirmed --cron-id <job>`. An escalation to the operator writes a column-0 `PARKED <UTC> run=<run id> escalation: <cause>` line and ends the run first, so the hook lets the report turn end. An operator stop said in words runs `end --reason operator-stop` and deletes the job before confirming; resume recreates both before any other step.

Canonical prompt:

```text
Claude run-guard heartbeat for Phase <N> (run file <run file>, generation <generation>). This session went idle while a campaign run may still be open. Check, then act, in this turn.

1. Run `<python> scripts/campaign_guard.py whoami --session $CLAUDE_CODE_SESSION_ID --generation <generation>`. OWNER run=<run id> scope=<plan|phase> means this job is the run's; the scope says what to resume (steps 5 and 7). If it prints NOT THE OWNER or NOT THE CURRENT JOB, CronDelete this job, change nothing else, and reply with that line. If it prints MALFORMED GUARD, run step 2, report the malformed guard to the operator, and stop.
2. Run `<python> scripts/campaign_guard.py hook-error --session $CLAUDE_CODE_SESSION_ID`. If it prints a line, the Stop hook failed open: append that line to <run file>'s Critical events, then run the same command with `--ack "<that line>"`.
3. Run `<python> scripts/campaign_guard.py pending-cancel`. For each job it names: CronDelete it, confirm with CronList, then `<python> scripts/campaign_guard.py cancel-confirmed --cron-id <job>`.
4. If step 1 printed NO GUARD, the run is over: run `<python> scripts/campaign_guard.py reset-state --expect-no-guard yes`, CronDelete this job, and reply RUN FINISHED.
5. If <run file> has a "## Closeout run=<run id>" heading or a column-0 "PARKED" line carrying "run=<run id>" and step 1 printed scope=phase, the one phase asked for is over: run `<python> scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason closeout` (or `--reason park` for a PARKED line), CronDelete this job, confirm, run cancel-confirmed for it, and reply RUN FINISHED. With scope=plan, if `<python> scripts/todo-graph.py query ready` lists nothing, run `<python> scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason plan-done`, CronDelete this job, confirm, run cancel-confirmed for it, and reply RUN FINISHED. If rows are still ready, the phase ended but the plan did not: resume under step 7.
6. If build/claude-campaign-state.json has trips of 2 or more, the run stalled twice with no change: append a Critical events line naming what blocks it, run `<python> scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason stall`, CronDelete this job, confirm, run cancel-confirmed, and report the stall to the operator.
7. Otherwise append `- bookkeeping: heartbeat resumed <UTC>` to the run file's Critical events and resume: under process-plan for scope=plan, or under process-phase for Phase <N> only for scope=phase. Re-run `<python> scripts/todo-graph.py query ready`, pick up the open section in the run file where it stopped, and keep shipping. Stop only at closeout, park, or an operator stop.
```

## 2. After a phase closeout or park

`process-phase` ends in exactly one of three ways: the phase table is all `[x]` with a written closeout; every leftover is blocked here and it parked (a `PARKED` line and park record in its run file); or the operator paused it. A parked phase is not complete and not a stall. Do not call it either.

Re-run `python scripts/todo-graph.py query ready`. If another phase has a ready row, re-point the guard to it before anything else (`CronDelete` the old job, `CronCreate` a new one for the new phase and run file, and `acquire` with the new phase, run file, job and a fresh generation), then start `process-phase` on it in the same turn, same session, same rules. If none does, end the run through `end` (plan-done, or park with the leftovers) and delete its job. If none does, report which: plan done, or the leftovers and their blockers, with the run files named.

## Deny

- Do not invent a side loop that ships rows outside `process-todo-section` plus `review-todo-section`.
- Do not start a second run, and do not resume a paused run unless the operator said resume.
- Do not start a run without its guard file and heartbeat job, and do not end, stop or pause a run without deleting both through `end`.
- Do not tick `implementation-plan.md` by hand, and do not edit it at all: it is generated.
- Do not claim a phase complete while its table has `[ ]` rows.
- Do not treat a named phase as the whole plan. Chaining is this skill's job, and only this skill's.
- Do not end the turn on the audit table.
