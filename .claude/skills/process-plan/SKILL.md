---
name: process-plan
description: Front door for todo/implementation-plan.md. Audit the plan, then run process-phase on the first phase with a ready row, then the next ready phase after each closeout or park. Use when the user says process the plan. The argument --audit is audit only. A named phase is one phase and does not chain.
---

# Process the Implementation Plan

The only front door for `todo/implementation-plan.md` when the user did not name a single phase. The file is a generated projection of the 100% complete development plan (small, single-responsibility sections and granular five-part micro-steps): processing it is not "pick a row and improvise", and it is not "tick the boxes" (boxes flip only through `stamp`).

This skill does not ship a section and does not write a stamp. It audits, then chains `process-phase` runs until the plan is 100% complete or every leftover row is blocked here. Writes stay serial: the run this skill starts is the only writer on the tree.

## The loop

One continuous loop. You do not stop between sections or phases:

1. Audit (below), start the run guard (below), run the host readiness check (below), then start `process-phase` on the first phase with a ready row, in this same turn.
2. After that phase's closeout or park (a `host-not-ready`, `ci-red` or `ci-unknown` park excepted: it ends the run, see Host readiness and CI watch), re-run `python scripts/todo-graph.py query ready` and start the next phase with a ready row this session can run: `query ready` does not know which hosts are reachable, so a row whose Needs name an unreachable host (`arm64-host`, `display-session`, `office`, `attended`) is a leftover here even when listed. At each phase start, first retry once every row the run file records as `completion-parked` (its completion review returned no review, `process-todo-section` step 3a); a row that fails again is parked for the owner with its reason, and the plan moves on.
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

The two test runs are the agent tooling tests under `scripts/tests` (review dispatch, automations) and the project's script tests under `tests/scripts`; run both, skip only a folder the repository does not have, and add any further suite the project's `AGENTS.md` names. Neither is dropped in favour of the other.

Read `todo/README.md` (the format every TODO edit keeps) before the first edit, then fix every validator refusal before talking about shipping. If `plan --check` is stale, run `plan --sync` and re-check. The deep phase repair belongs to `process-phase` step 1; this audit is the commands above plus five recorded lines in the first phase's run file (`docs/phase-runs/<date>-phase-<N>.md`), not as the turn's last words:

1. Graph: valid section count, or the refusal.
2. Plan currency: the `--check` result.
3. Ready rows: count and first ref per phase.
4. Blocked rows: count and what blocks them (unmet dependencies, waiting Needs, unreachable hosts).
5. The phase being started, and why it is first.

Ready means runnable now in this context: `query ready` already excludes rows waiting on dependencies, inactive files and people Needs; rows needing a host this session cannot reach (`arm64-host`, `display-session`, `office`, `attended`) are leftovers here even when listed, and `process-phase` re-checks each row with `resolve` rather than trusting a previous list.

If no phase has a ready row, report the leftovers with their blockers and stop. That is a genuine halt.

### Host readiness

An unattended campaign that meets a locked screen, a sleeping PC, a missing Office app or a missing compiler parks with the fixes recorded instead of failing mid-section (D00 T03 §12). Once the guard is up, and again at every phase start (`process-phase` Step 0), run:

```powershell
python scripts/check-campaign-host.py --notify
```

It runs at four entry points: campaign start, every phase start reached by chaining, a phase started on its own, and every resume (by hand or by the heartbeat), always before any row is claimed. Exit 0: carry on. Exit 1 (a check failed) or 2 (a check could not run): the script has printed one line per check with the fix for each failure and emailed them through `.conclave/automations/alert.py` (or printed `email not sent: <reason>`, which is recorded too). This park stops the whole campaign, not one phase: copy every non-`ok` line and its fix (and any `email not sent` line) into the run file's Critical events, write a column-0 `PARKED <UTC> run=<run id> host-not-ready: <failing checks>` line and the park record (the fixes), commit the run file, run `python scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason park`, `CronDelete` the heartbeat it names, confirm with `CronList`, and run `cancel-confirmed`. Never chain to another phase after a host-not-ready park, even one with ready rows: no row in any phase is claimed until a resumed run's check exits 0. The owner applies the fixes and resumes the campaign by hand.

A resume after a host-not-ready park is a fresh run, never a continuation of the parked one. If the guard file still exists (the park was interrupted before `end`), finish that park first: `end --session <the session_id in build/claude-campaign-guard.json> --reason park` (the `PARKED` marker is already there), delete its heartbeat, and confirm. Then start a new run under a new run id: `CronCreate` a new heartbeat with a fresh generation and `acquire` without `--handover` (the guard is gone), with a new run file for the phase (`docs/phase-runs/<today>-phase-<N>.md`, or `-2`, `-3` on the same day), so no earlier `host-not-ready` marker carrying the old run id can end the new run. Never `acquire --handover` onto a run parked for host readiness.

### CI watch

The campaign pushes to `main`, so it also reads what GitHub Actions made of each push and never builds on a red one (D00 T03 §15). After every stamp push, note its SHA; nothing is written to the run file yet, so the tree stays clean for the dependency merge (a session that dies before the records below is covered by D00 T03 §17's reconciliation from the pushed history). At the next section boundary, before the next row is claimed, run `python scripts/ci-status.py <sha>` and act on its exit:

- 0 (green): run the dependency merge below first, while the tree is still clean and `HEAD` pushed. If it merged anything, `main` has a new head on GitHub, which the local `HEAD` may not have (`merged-then-failed`: the pull after the merge failed): run `git fetch origin main` and `git pull --ff-only origin main` so the clone matches the merged head (if it still cannot, park with `ci-unknown: cannot align with origin/main`, since no repair can start from a stale checkout), then `python scripts/ci-status.py HEAD --wait --timeout 1800` and act on it by these same rules (repair, wait, retry or park), all before any row is claimed. Then append `ci-pending <sha> <UTC>` and `ci-green <sha>` for each push checked, and the merge's outcome, to the run file; they ride with the next section's commit, so no bookkeeping push exists to go unchecked.
- 1 (red): repair it before the next row, as below.
- 3 (pending): run `python scripts/ci-status.py <sha> --wait --timeout 1800` and act on that result.
- 2 (unknown: `gh` cannot be read, or no push run 10 minutes after the commit): retry once after five minutes; still 2, park the campaign with `ci-unknown` as the reason, since green cannot be established.

Repair a red run before the next row: run `python scripts/ci-status.py <sha> --log <scratch>\ci-<sha>.log`, read the failing jobs and steps it prints and the log, reproduce the failure locally where the job can run here, fix it at the owning layer in a `ci: <what was fixed> (repair for <sha>, run <id>)` commit, re-run the local gates, push, note the repair commit's SHA, and `--wait` for green; on green continue as the green step says (merge first, then write the records), so the tree is clean for the merge. A failure that passes on one `gh run rerun <id> --failed --repo github.com/<owner>/<name>` (the repository in the run URL `ci-status.py` printed, which is `origin`'s, so `GH_REPO` cannot redirect it) is recorded as `ci-flaky <sha> <job>` and filed through `add-todo` as a flake to fix, never ignored.

Bound the repair: after three repair commits that leave the same job red, file the failure through `add-todo` (run link, job, step, what was tried), email the owner through `.conclave/automations/alert.py` (record `email not sent: <reason>` if it fails; the park goes ahead), and park with `ci-red` as the reason.

A `ci-red` or `ci-unknown` park ends the whole campaign, as a `host-not-ready` park does: write a column-0 `PARKED <UTC> run=<run id> ci-red: <job>` (or `ci-unknown: <reason>`) line and the park record, commit it and push it (so the resume below checks a pushed `HEAD`; a push that fails is recorded in the park record, and the resume pushes first), run `python scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason park`, `CronDelete` the heartbeat, confirm with `CronList`, and run `cancel-confirmed`. Never chain to another phase after it. An owner resume is a fresh run (as for `host-not-ready`) that pushes any unpushed commit, then runs the reconciliation below (`--pending`, then the fast-forward to `origin/main`) before any row, waiting on a pending newest head, and parks again unless every listed head ends green or superseded.

Every campaign push gets a `ci-pending <sha> <UTC>` record when the boundary's records are written: stamp pushes, dependency merges by `scripts/merge_prs.py`, closeout and park commits, and repair commits. A red push head whose later push head is green is recorded `ci-superseded <sha> by <later sha>`, with no repair (the later green run includes its changes); a red head that is still the newest is repaired as above.

Reconcile from the pushed history (D00 T03 §17) at campaign start, at every phase start and on every manual or heartbeat resume, before any row is claimed, as the one CI step there (no separate check of a possibly stale local `HEAD`): first align the clone (push any unpushed commit, then `git pull --ff-only origin main`), then reconcile; `--pending` exits 2 unless `HEAD` is exactly the `origin/main` it just fetched, so the run files it reads and the head it checks are the history the next row builds on. If it reports the clone ahead or behind (another push landed meanwhile), align and reconcile once more, then park with `ci-unknown: cannot align with origin/main`: `python scripts/ci-status.py --pending <run file>` fetches `origin/main`, lists every push head after the baseline with no `ci-green` or `ci-superseded` record of its own, and checks each. Act on its exit as on a single commit's: 0, record `ci-green` for each listed head; 1, settle each listed head newest first: when the newest listed head is still pending, first wait for it (`python scripts/ci-status.py <sha> --wait --timeout 1800`) and settle with its result; a red head with a later green head (listed or recorded) is recorded `ci-superseded <sha> by <later sha>` and never repaired; only when the newest head itself is red, first align the clone with the fetched head (`git pull --ff-only origin main`; if local changes or a diverged branch prevent it, park with `ci-unknown: cannot align with origin/main`, since no repair can start from a stale checkout), then repair it, and once it is green record the earlier red heads superseded; 3, wait; 2 (incomplete discovery: a failed fetch or `gh`, an unreadable run file, a cut-off run history), retry once after five minutes, then park with `ci-unknown`.

Green is a hard gate in three places: a phase closeout (`process-phase` Step 4), a draft release, and the campaign's end (`plan-done`) each run `python scripts/ci-status.py HEAD --wait --timeout 3600` and proceed only on exit 0. `process-phase` runs this same procedure, by reference, for a phase started on its own.

### Run guard

A run without a guard dies silently when the session stalls, so starting the first phase also starts the run guard, always. It has two parts, and they cover different failures. There is no keep-alive outside the session: nothing relaunches a session that died.

- **Stop hook** (`python3 ... scripts/campaign_guard.py stop-hook`, wired in `.claude/settings.json`): while the run is open it blocks this session's end of turn and names the next ready row. It lets the turn end when the guard file is gone, the run file has a `## Closeout run=<run id>` heading or a column-0 `PARKED <UTC> run=<run id>` line, or `query ready` has nothing runnable. It blocks only the session named in the guard, never a subagent or a second session, and it fails open on a bad payload or an error, recording the error for the heartbeat. Its stall breaker lets the turn end after 3 blocks with no change to HEAD, the working-tree diff, the untracked files, or the run file without its `- bookkeeping:` lines, and counts a trip in `build/claude-campaign-state.json`. A heartbeat or retry note is written as a `- bookkeeping: ...` line, so it never passes for progress.
- **Heartbeat** (`CronCreate`): it fires only when this session is idle and runs inside it with full context, so it is a real resume. It covers what the hook cannot hold: a tripped breaker, an API error, a turn that crashed out.

Commands here are written `python`; on Linux and WSL run them with `python3`. The session id is written `$CLAUDE_CODE_SESSION_ID`, the bash spelling; in PowerShell it is `$env:CLAUDE_CODE_SESSION_ID` (a bare `$CLAUDE_CODE_SESSION_ID` there is an empty variable and the guard refuses the arguments). The heartbeat prompt says `<python>`: fill in the interpreter of the machine the session runs on.

Start it in this order:

1. Reconcile: `CronList`, then `python scripts/campaign_guard.py reconcile --session $CLAUDE_CODE_SESSION_ID --jobs <ids of every job whose prompt starts "Claude run-guard heartbeat", comma-separated>`, and do what it prints: `CronDelete` an orphan or stale job, and start nothing when another session owns the guard.
2. Mint a generation with `python scripts/campaign_guard.py mint-generation`, then `CronCreate` with cron `3-59/5 * * * *`, recurring, and the canonical prompt below with `<N>`, `<run file>`, `<generation>` and `<python>` filled in.
3. Acquire: `python scripts/campaign_guard.py acquire --session $CLAUDE_CODE_SESSION_ID --phase <N> --run-file <run file> --cron-id <job id> --generation <generation> --scope plan`. It writes `build/claude-campaign-guard.json` exclusively and prints the run's id, which every end marker of this run carries. A refused `acquire` means another session owns the run: `CronDelete` the job step 2 created, start nothing, and report the owner. The owning session re-points its own guard with the same command (a new phase or job); taking another session's live guard needs the operator's `--handover <reason>`.
4. Record the session id, job id, generation and run id in the run file's Critical events.

At every section boundary (after each stamp): `CronList`, then `python scripts/campaign_guard.py health --session $CLAUDE_CODE_SESSION_ID --jobs <live heartbeat job ids>` and `python scripts/campaign_guard.py expiry --session $CLAUDE_CODE_SESSION_ID`. A missing job, or one within 12 hours of its 7-day expiry, is replaced (steps 2 and 3 with a fresh generation) and the repair recorded. Nothing is written to the run file at a boundary until the CI watch and the dependency merge below are done: the heartbeat repair, the `ci-pending` and `ci-green` lines and the merge outcome are all appended afterwards, together, so `merge_prs.py` always finds a clean tree.

Then run the CI watch above for the stamp push; only on green, and before anything is written to the run file (the stamp commit pushed and the tree clean, the one moment the clone matches GitHub), merge green dependency pull requests before claiming the next row: `python scripts/merge_prs.py --session $CLAUDE_CODE_SESSION_ID`. It merges only Dependabot or pins pull requests that are labelled, green, cleanly mergeable and leave the C++ toolchain pin files alone, one at a time by rebase, and refuses (exit 2) a dirty tree, an unpushed `HEAD` or a section in progress. Then gate any merged head as the CI watch's green step says, record the `ci-pending` and `ci-green` lines and what it merged, or its failure, in the run file's Critical events, and carry on: a pull request it could not merge stays open for the owner, and a merge never ends the run.

The heartbeat dies with this session. A run resumed in a new session takes the guard with `acquire --handover <reason>` and a new job and generation; the old session's heartbeat then reads `NOT THE OWNER` and deletes itself.

Every way a run ends (closeout of the last phase, park with nothing left, plan done, operator stop, escalation, a stall) goes through `python scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason <closeout|park|plan-done|operator-stop|escalation|stall>`, never a direct delete. It checks that path's marker, deletes the guard and state files, and names the heartbeat job: `CronDelete` it, confirm it is gone with `CronList`, then run `python scripts/campaign_guard.py cancel-confirmed --cron-id <job>`. An escalation to the operator writes a column-0 `PARKED <UTC> run=<run id> escalation: <cause>` line and ends the run first, so the hook lets the report turn end. An operator stop said in words runs `end --reason operator-stop` and deletes the job before confirming; resume recreates both before any other step.

Canonical prompt:

```text
Claude run-guard heartbeat for Phase <N> (run file <run file>, generation <generation>). This session went idle while a campaign run may still be open. Check, then act, in this turn.

1. Run `<python> scripts/campaign_guard.py whoami --session $CLAUDE_CODE_SESSION_ID --generation <generation>`. OWNER run=<run id> scope=<plan|phase> means this job is the run's; the scope says what to resume (steps 5 and 7). If it prints NOT THE OWNER or NOT THE CURRENT JOB, CronDelete this job, change nothing else, and reply with that line. If it prints MALFORMED GUARD, run step 2, report the malformed guard to the operator, and stop.
2. Run `<python> scripts/campaign_guard.py hook-error --session $CLAUDE_CODE_SESSION_ID`. If it prints a line, the Stop hook failed open: append that line to <run file>'s Critical events, then run the same command with `--ack "<that line>"`.
3. Run `<python> scripts/campaign_guard.py pending-cancel`. For each job it names: CronDelete it, confirm with CronList, then `<python> scripts/campaign_guard.py cancel-confirmed --cron-id <job>`.
4. If step 1 printed NO GUARD, the run is over: run `<python> scripts/campaign_guard.py reset-state --expect-no-guard yes`, CronDelete this job, and reply RUN FINISHED.
5. If <run file> has a column-0 "PARKED" line carrying "run=<run id>" and "host-not-ready", "ci-red" or "ci-unknown", whatever the scope, the campaign is over until the owner resumes it by hand: run `<python> scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason park`, CronDelete this job, confirm, run cancel-confirmed for it, and reply RUN FINISHED, even when rows are ready and the host check would now pass. Otherwise, if <run file> has a "## Closeout run=<run id>" heading or a column-0 "PARKED" line carrying "run=<run id>" and step 1 printed scope=phase, the one phase asked for is over; for a closeout, first finish it as `process-phase` Step 4 says (commit any uncommitted closeout content with its run file, push every unpushed commit), then run `<python> scripts/ci-status.py --pending <run file>` and `<python> scripts/ci-status.py HEAD --wait --timeout 3600`, and unless both exit 0 resume under step 7, whose CI watch repairs or parks, instead of ending: run `<python> scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason closeout` (or `--reason park` for a PARKED line), CronDelete this job, confirm, run cancel-confirmed for it, and reply RUN FINISHED. With scope=plan, if `<python> scripts/todo-graph.py query stats` shows every row verified, first commit any uncommitted closeout content and push every unpushed commit, then run `<python> scripts/ci-status.py --pending <run file>` and `<python> scripts/ci-status.py HEAD --wait --timeout 3600`: unless both exit 0, do not end the run; resume under step 7, where the skill's CI watch repairs or parks. On exit 0, run `<python> scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason plan-done`, CronDelete this job, confirm, run cancel-confirmed for it, and reply RUN FINISHED. If `query ready` lists nothing, or only rows whose Needs name a host this session cannot reach, while rows stay open, write a column-0 `PARKED <UTC> run=<run id> <reason>` line and park record in <run file>, commit, then end with `--reason park` the same way. If rows are still ready, the phase ended but the plan did not: resume under step 7.
6. If build/claude-campaign-state.json has trips of 2 or more, the run stalled twice with no change: append a Critical events line naming what blocks it, run `<python> scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID --reason stall`, CronDelete this job, confirm, run cancel-confirmed, and report the stall to the operator.
7. Otherwise resume, writing `- bookkeeping: heartbeat resumed <UTC>` to the run file's Critical events only after the checks below and any dependency merge, so the tree is clean for the merge: under process-plan for scope=plan, or under process-phase for Phase <N> only for scope=phase. Run `<python> scripts/check-campaign-host.py --notify` first: a non-zero exit parks the campaign as the skill's Host readiness step says. Then run `<python> scripts/ci-status.py --pending <run file>` (it checks `origin/main` and every unchecked push head before it) and act on it as the skill's CI watch step says before claiming any row. Re-run `<python> scripts/todo-graph.py query ready`, pick up the open section in the run file where it stopped, and keep shipping. Stop only at closeout, park, or an operator stop.
```

## 2. After a phase closeout or park

`process-phase` ends in exactly one of three ways: the phase table is all `[x]` with a written closeout; every leftover is blocked here and it parked (a `PARKED` line and park record in its run file); or the operator paused it. A parked phase is not complete and not a stall. Do not call it either.

Re-run `python scripts/todo-graph.py query ready`. If another phase has a ready row this session can run (Needs within reach, as in the loop above), re-point the guard to it before anything else (`CronDelete` the old job, `CronCreate` a new one for the new phase and run file, and `acquire` with the new phase, run file, job and a fresh generation), then start `process-phase` on it in the same turn, same session, same rules. If none does, end the run through `end` and delete its job: `plan-done` only when every row is stamped (`query stats` shows `verified` equal to `total`; `end` refuses `plan-done` otherwise) and, after the last closeout commit is pushed, `python scripts/ci-status.py HEAD --wait --timeout 3600` exits 0 (anything else goes to the CI watch, which repairs or parks); otherwise (rows remain open, blocked or needing a host this session cannot reach) first write a column-0 `PARKED <UTC> run=<run id> <one-line reason>` line and the park record (each leftover and what blocks it) in the current run file, commit it, then `end --reason park`, which refuses without that marker. Then report which: plan done, or the leftovers and their blockers, with the run files named.

## Deny

- Do not invent a side loop that ships rows outside `process-todo-section` plus `review-todo-section`.
- Do not start a second run, and do not resume a paused run unless the operator said resume.
- Do not start a run without its guard file and heartbeat job, and do not end, stop or pause a run without deleting both through `end`.
- Do not tick `implementation-plan.md` by hand, and do not edit it at all: it is generated.
- Do not claim a phase complete while its table has `[ ]` rows.
- Do not treat a named phase as the whole plan. Chaining is this skill's job, and only this skill's.
- Do not end the turn on the audit table.
