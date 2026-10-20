---
name: process-plan
description: Front door for todo/implementation-plan.md. Audit the plan, then run process-phase on the first phase with a ready row, then the next ready phase after each closeout or park. Use when the user says process the plan. The argument --audit is audit only. A named phase is one phase and does not chain.
---

# Process the Implementation Plan

The only front door for `todo/implementation-plan.md` when the user did not name a single phase. The file is a generated projection of the 100% complete development plan (small, single-responsibility sections and granular five-part micro-steps): processing it is not "pick a row and improvise", and it is not "tick the boxes" (boxes flip only through `stamp`).

This skill does not ship a section and does not write a stamp. It audits, then chains `process-phase` runs until the plan is 100% complete or every leftover row is blocked here. Writes stay serial: the run this skill starts is the only writer on the tree.

## The loop

One continuous loop. You do not stop between sections or phases:

1. Start the run guard on the first phase with a ready row (Run guard, below: the guard comes before the first write), audit (below), then start `process-phase` on that phase, in this same turn.
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

A run without a guard dies silently when the session stalls, so every run starts the run guard, always, before its first write (ported from Isotone, operator request 2026-10-20). The audit writes (repairs, `plan --sync`, run-file lines), so the guard comes first: pick the first phase with a ready row from the read-only Route queries, start the guard on that phase's run file, then audit. The guard has three parts, and they cover different failures.

- **Stop hook** (`.claude/hooks/campaign-stop.ps1`, wired in `.claude/settings.json`): while the run is open, it blocks this session's end of turn and names the next ready row. It lets the turn end when the guard file is gone, the run file has a `## Closeout run=<run id>` heading or a column-0 `PARKED <UTC> run=<run id>` line, or `query ready` prints an empty list `[]`. It blocks only the session named in the guard file, never subagents, a second session, or another runner, and it fails open on a bad payload or a thrown error. `python scripts/campaign_guard.py --self-test` drives it against a throwaway workspace, run by `scripts/tests/test_campaign_guard.py`. A thrown error is recorded for the heartbeat: in the state file when this session provably owns the run, otherwise in `build/claude-campaign-hook-errors/`.
- **Stall breaker** (inside the hook): after 3 blocks in a row with no change to HEAD, the working-tree diff, the untracked files, or the run file without its `- bookkeeping:` lines, the hook lets the turn end and counts a trip in `build/claude-campaign-state.json`. Real progress resets the count. Bookkeeping is not progress: a heartbeat or retry note is written as a `- bookkeeping: ...` line and leaves the fingerprint unchanged, while any other Critical events line counts.
- **Heartbeat** (`CronCreate`): it fires only when this session is idle, and it runs inside this session with full context, so it is a real resume, not a detached reminder. It covers the turns the hook cannot hold: a tripped breaker, an API error, a crash out of the turn.

Start it in this order:

1. Reconcile first: `CronList`, then `python scripts/campaign_guard.py reconcile --session $CLAUDE_CODE_SESSION_ID --jobs <every job id whose prompt contains Claude run-guard heartbeat for Office-2028, comma-separated>`, and do what it prints: `CronDelete` an orphan or stale job, and start nothing when another session or runner owns the guard. A crash between creating a job and acquiring a guard is repaired here, before a second one is made.
2. Mint a generation: `python scripts/campaign_guard.py mint-generation`. `CronCreate` with cron `3-59/5 * * * *`, recurring true, and the canonical prompt below with `<N>`, `<run file>`, `<generation>` and `<scope>` filled in. The scope is `plan` when `process-plan` chains phases, and `phase <N> only` when the operator named one phase: the heartbeat never widens what the operator asked for.
3. Acquire the guard: `python scripts/campaign_guard.py acquire --session $CLAUDE_CODE_SESSION_ID --phase <N> --run-file <run file> --cron-id <job id> --generation <generation>` writes `build/claude-campaign-guard.json` (gitignored) with the runner, session, phase, run file, job, generation and `run_id`, the identity every terminal marker of this run carries. It refuses a guard another session or another runner (a Codex or Antigravity run, which takes the same guard with `--runner`) holds, so two writers never share the tree; the owning session re-points its own guard with the same command, and taking over another session's live guard needs the operator's `--handover <reason>`. A refused `acquire` means another session owns the run (or another runner does): `CronDelete` the job step 2 just created, start nothing, and report the owner.
4. Observe this session for the keep-alive: `python scripts/campaign_keepalive.py observe --session $CLAUDE_CODE_SESSION_ID` records its Claude process (the SessionStart hook does this too; this covers a session that started before the hook existed). A keep-alive cannot prove an unobserved owner gone, so it never resumes one.
5. Record the session id, the job id, the generation, the scope, and the guard's run id in the run file's Critical events.

At every section boundary (after each stamp), check the heartbeat: `CronList`, then `python scripts/campaign_guard.py health --session $CLAUDE_CODE_SESSION_ID --jobs <live heartbeat job ids>` and `python scripts/campaign_guard.py expiry --session $CLAUDE_CODE_SESSION_ID`. A missing job, or one within 12 hours of its 7-day expiry, is replaced (steps 2 and 3 with a fresh generation and the same scope) and the repair recorded in the run file.

The run file's end markers are exact and carry the run's id: a closeout is a line `## Closeout run=<run id>` followed by the closeout text, and a park is a column-0 line `PARKED <UTC stamp> run=<run id> <one-line reason>` followed by the park record. Markers are case-sensitive. The hook, `end`, and the heartbeat honour only markers carrying this run's id, so a reused run file's old markers never end a new run.

The heartbeat is session-only: it dies with this session, and a recurring job expires after 7 days, which the section-boundary `expiry` check replaces before it lapses. A run resumed in a new session takes the guard with `acquire --handover <reason>` and a new job and generation; the old session's heartbeat then reads `NOT THE OWNER` from `whoami` and deletes itself. The `office-2028-claude-keepalive` task (`.conclave/automations/README.md`) covers the session dying: three minutes after logon and then hourly, it resumes this exact session headless with `claude -p --resume` when every observed process of the session is provably gone and no other Office-2028 session is open, and the resume prompt brings it back through these steps. While the operator has any Office-2028 session open, or another runner holds the guard, it waits.

Every way a run ends (closeout, park, plan done, operator stop, escalation, an operator wait, a stall the heartbeat stops) deletes the guard, the state and the job, always through the locked, session-checked `end` and never by deleting files directly: `python scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason <closeout|park|plan-done|operator-stop|escalation|stall>` checks that path's marker, deletes the guard file and the state file, leaves `build/claude-campaign-pending-cancel.json` naming the heartbeat job, and names it; the runner `CronDelete`s it, confirms it gone with `CronList`, and only then runs `python scripts/campaign_guard.py cancel-confirmed --cron-id <job>`, so a failed delete stays recoverable.

Escalation ends the run before its report: a report to the operator (a cause the tree cannot fix) first writes a column-0 `PARKED <UTC> run=<run id> escalation: <cause>` line, then runs `end --reason escalation` and deletes the job, so the Stop hook lets the report turn end and no heartbeat resumes against it. Resume recreates the guard and the job before any other step.

Operator waits are parks of the whole run: work that needs the operator's go-ahead first (for example a live capture that drives an Office app; a standing go-ahead counts only when the operator gave it in words and the run file records it as a `- go-ahead:` line naming that work) records `- waiting: <what> <UTC>` under Critical events and a column-0 `PARKED <UTC> run=<run id> waiting: <what>` line, runs `end --reason park` and deletes the job before the question turn, so the hook lets that turn end and no heartbeat or keep-alive resumes past it. The answer is recorded as `- go-ahead: <what> <UTC>` under Critical events, and resume recreates the guard and the job before any other step. Unattended, a run never waits: it takes the documented default or skips the row as a leftover.

Operator stop: pressing Esc interrupts without the hook firing. A stop or pause said in words deletes the guard file, the state file, and the job (`end --reason operator-stop`, then `CronDelete`), before confirming. Resume recreates all three before any other step.

Canonical prompt:

```text
Claude run-guard heartbeat for Office-2028 Phase <N> (run file <run file>, generation <generation>, scope <scope>). This session went idle while a campaign run may still be open. Check, then act, in this turn.

1. Run `python scripts/campaign_guard.py whoami --session $CLAUDE_CODE_SESSION_ID --generation <generation>`. It prints OWNER with the run's id (`OWNER run=<run id>`) when this job is the run's. If it prints NOT THE OWNER or NOT THE CURRENT JOB, this job is not the run's: CronDelete this job, read and change nothing else, and reply with that line. If it prints MALFORMED GUARD, run step 2, report the malformed guard to the operator, and stop.
2. Run `python scripts/campaign_guard.py hook-error --session $CLAUDE_CODE_SESSION_ID`. If it prints a line, the Stop hook failed open: append that line to <run file>'s Critical events, then run the same command with `--ack "<that line>"` to clear it.
3. Run `python scripts/campaign_guard.py pending-cancel`. If it names a job, CronDelete that job, confirm it gone with CronList, and run `python scripts/campaign_guard.py cancel-confirmed --cron-id <that job>`.
4. If step 1 printed NO GUARD, the run is over: run `python scripts/campaign_guard.py reset-state --expect-no-guard yes`, CronDelete this job (find it with CronList by this prompt's first sentence), and reply RUN FINISHED.
5. If the newest "- waiting: <what>" line under <run file>'s Critical events has no later "- go-ahead:" line naming the same <what>, or <run file> has a column-0 line starting "PARKED" that carries "run=<run id>" (the id step 1 printed) and whose reason starts "escalation:" or "waiting:", the run stopped for the operator. For a waiting line without its PARKED line, first append `PARKED <UTC> run=<run id> waiting: <what>`. Never resume past it: run `python scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason escalation` for an escalation or `--reason park` for a wait, CronDelete this job, confirm it gone with CronList, then run `cancel-confirmed` for it, and reply with that waiting or PARKED line.
6. If <run file> has a line "## Closeout run=<run id>" or any other column-0 "PARKED" line carrying "run=<run id>": with scope `phase <N> only`, the run is over: run `end` with `--reason closeout` or `--reason park` to match, CronDelete this job, confirm it gone with CronList, run `cancel-confirmed` for it, and reply RUN FINISHED. With scope `plan`, run `python scripts/todo-graph.py query ready`. If it prints an empty list `[]`, the plan run is over: run `python scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason plan-done`, CronDelete this job, confirm it gone with CronList, then run `cancel-confirmed` for it, and reply RUN FINISHED. Otherwise the phase ended but the plan did not: delete nothing and go on to step 7. A phase closeout alone never ends a plan run.
7. If build/claude-campaign-state.json has trips of 2 or more: the run stalled twice with no change to the tree. Do not resume. Append a Critical events line to the run file naming what blocks it, run `python scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason stall`, CronDelete this job, confirm it gone with CronList, then run `cancel-confirmed` for it, and report the stall to the operator.
8. Otherwise append `- bookkeeping: heartbeat resumed <UTC>` to the run file's Critical events and resume within the scope: scope `plan` resumes under process-plan (re-run `python scripts/todo-graph.py query ready`, pick up the open section in the run file exactly where it stopped, and after a phase closeout or park re-point the guard to the next ready phase), and scope `phase <N> only` resumes under process-phase for Phase <N> and nothing else. Keep shipping: finish the section, stamp it, then the next section. A commit is not a stop. Stop only at closeout, park, or an operator stop.
```

## 2. After a phase closeout or park

`process-phase` ends in exactly one of three ways: the phase table is all `[x]` with a written closeout; every leftover is blocked here and it parked (a `PARKED` line and park record in its run file); or the operator paused it. A parked phase is not complete and not a stall. Do not call it either. A park whose reason starts `escalation:` or `waiting:` stopped the whole run for the operator and already ended the guard: report it and stop, never chain past it.

Re-run `python scripts/todo-graph.py query ready`. If another phase has a row this session can run (not a leftover of a phase this run already parked), start `process-phase` on it in the same turn, same session, same rules. If none does, the run halts, and a halt always ends the guard before the report: an empty ready list is `end --reason plan-done`; leftovers only ends with the reason that matches the guard's own run file, the last phase's: `end --reason closeout` when that phase closed out (its `## Closeout run=<run id>` heading) and `end --reason park` when it parked. Then report which: plan done, or the leftovers and their blockers, with the run files named.

When another phase has a row to run, re-point the guard to the new phase's run file before anything else, in this order so a crash never leaves the guard without a live job: mint a generation and `CronCreate` a new job from the canonical prompt with the new phase, run file and scope `plan`; re-point the guard with `python scripts/campaign_guard.py acquire` (same session, new `--phase`, `--run-file`, `--cron-id` and `--generation`); then `CronDelete` the old job and confirm it gone with `CronList`; record the new ids and the printed run id in the new run file. Each `end` of the halt above is followed by `CronDelete`, `CronList` and `cancel-confirmed` as the Run guard section states.

## Deny

- Do not invent a side loop that ships rows outside `process-todo-section` plus `review-todo-section`.
- Do not start a second run, and do not resume a paused run unless the operator said resume.
- Do not start a run without its guard file and heartbeat job, and do not end, stop, or pause a run without ending the guard through `campaign_guard.py end` and deleting the job.
- Do not tick `implementation-plan.md` by hand, and do not edit it at all: it is generated.
- Do not claim a phase complete while its table has `[ ]` rows.
- Do not treat a named phase as the whole plan. Chaining is this skill's job, and only this skill's.
- Do not end the turn on the audit table.
