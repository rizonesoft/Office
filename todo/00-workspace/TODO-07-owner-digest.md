---
schema_version: 1
id: owner-digest-follow-ups
domain: 00-workspace
status: active
title: "TODO-07 -- Owner Digest Follow-ups"
---

# TODO-07 -- Owner Digest Follow-ups

> **Goal:** The weekly owner digest of D00 T03 §35 stays truthful and complete when a session dies, a week is busy or a send fails: it never calls an abandoned run running, never drops a progress line, and never loses a week.

> **Current state:** Measured 2026-11-11. D00 T03 §35 (in progress) builds `scripts/owner-digest.py` and the `office-owner-digest` task; its completion review round 2 found three gaps this file owns. TODO-03 holds the 55 sections a file may hold, so they open this file.

## Inputs

- `docs/specs/2026-10-23-campaign-scope-design.md`, decision 32: one weekly email, no other interruption.
- `scripts/campaign_guard.py` (the run guard and its state file), `.conclave/automations/alert.py` (the transport), `.conclave/automations/run.py` and `tasks.json` (the scheduled tasks).
- -> XREF: T03 §35 -- the digest these sections extend; T03's Inputs point back here

## Outcome

- The digest reports a run as running only when its session shows life, keeps every progress line however long the week, and is sent again after a failed send, covering the whole period missed.

**Adjacency:** all=not-applicable (developer tooling for one recipient: the owner's weekly email, with no records, settings or surfaces of its own)

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Digest tells a live run from an abandoned guard | T03 §35 | [x] |
| 2 | §2 | Digest keeps a long progress list | T03 §35 | [x] |
| 3 | §3 | Digest delivery survives a failed send | T03 §35 | [x] |
| 4 | §4 | Scheduled tasks start on a Monday morning | -- | [ ] |

## 1. Digest Tells a Live Run From an Abandoned Guard

> **Started:** 2026-11-12T09:30:39Z

Filed 2026-11-11 from the completion review of T03 §35 (`docs/reviews/00-workspace/D00-T03-s35-completion.md`, round 2, finding 1, P2). T03 §35 reports `Running` while `build/claude-campaign-guard.json` exists, but a session that crashed leaves its guard in place for the launcher's handover (`scripts/campaign_guard.py`), and an `end` interrupted after its marker leaves one too. This section reports a run as running only when the guard's session shows life.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Read the guard as `campaign_guard.py` reads it. Done when: an ended, an abandoned and a live guard each report their own state.

- [x] Ask `python scripts/campaign_guard.py whoami` (or the function behind it) from `scripts/owner-digest.py` instead of testing the guard file's existence, and report `Running` only for an open guard whose state file shows a heartbeat or a hook call in the last hour, (**Corrected 2026-11-12:** the state file records no such time, and the heartbeat fires only while the session is idle and the Stop hook only when a turn ends, so a session busy for an hour would read stalled. `campaign_guard.py` gains `liveness(root, now)`: `health` and the Stop hook write `seen_at` into the state file, and a run's last sign of life is the newer of `seen_at` and the newest commit on `HEAD` since the guard's `job_created_at`; the digest asks that function, and a test shows a busy session whose commits keep it `Running`) `Stalled since <time>` for an open guard without one, and the run file's own state for an ended guard. Done when: tests in `scripts/tests/test_owner_digest.py` cover a live, a stalled and an ended guard.
- [x] Take a run's sign of life from what its own session writes, never from commits (which another session may make): the newer of `seen_at` in the state file and the modification time of the session's transcript, `<config>/projects/*/<session_id>.jsonl` (the config folder is `CLAUDE_CONFIG_DIR` or `~/.claude`), which Claude Code appends on every message and tool call, and no tool call outlasts ten minutes. Done when: tests show a session with an hour-old `seen_at` and a fresh transcript reading `Running`, a recent commit by someone else leaving an abandoned guard `Stalled`, and a missing transcript falling back to `seen_at`. **Corrected 2026-11-12:** replaces the newest-commit signal of the first correction after the plan review (gap 1, P1).
- [x] Write `seen_at` where the heartbeat really arrives and where the hook runs: `whoami` (the heartbeat prompt's call, after its session and generation check passes) and the Stop hook (for the guard's own session only), each keeping the stall breaker's fields as they were. Done when: tests call `whoami` and the hook, read the state back through the digest's run line, show `fingerprint`, `blocks`, `trips` and `stalled` unchanged, and show a call from another session after a handover writing nothing. **Corrected 2026-11-12:** the first correction named `health`, which runs only at section boundaries (plan review gaps 2 and 3, P2).
- [x] Tell a missing state file from a broken one: a missing file (a fresh run, or one `acquire` just reset) means no `seen_at` yet and the transcript decides, while a state file that cannot be read or parsed, like an unreadable guard, gives `Unknown: <reason>`. Done when: tests cover a missing, a corrupt and an unreadable state file and a malformed guard, each with its line. **Corrected 2026-11-12:** added after the plan review (gap 4, P2).
- [x] Report `Unknown` with the reason when the guard or its state cannot be read. Done when: a test with a malformed guard shows it.
- [x] Commit: `automations: the digest tells a live run from an abandoned guard`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_owner_digest.py"` passes with the guard tests among them.

> **Verified:** 2026-11-12 | §1 | 8b5510f80645fd1fb559d5878f4a06dfadd1fe1d
> **Review:** `docs/reviews/d00-t07-s1.json`

## 2. Digest Keeps a Long Progress List

> **Started:** 2026-11-12T10:05:09Z

Filed 2026-11-11 from the completion review of T03 §35 (round 2, finding 2, P2). T03 §35 moves an overflowing waiting list into an attachment, but not the list of sections verified in the week, so a productive week could push the run state, CI and the waiting items out of the 120-line body, or cut the progress list. This section puts the whole progress list in the attachment too and keeps the body's summary first.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Order the body and overflow both lists. Done when: a week of 130 stamps keeps the summary, CI and run state in the body and every stamp in the attachment.

- [x] Order the body of `scripts/owner-digest.py` as run state, CI, totals, waiting items, then progress, each cut list ending with a line that counts what the attachment adds. Done when: a test with 130 fixture stamps in the week shows the body's first lines unchanged and the cut line.
- [x] Put the complete progress list in the attachment beside the waiting list. Done when: tests cover progress-only overflow and progress-and-waiting overflow, with every item in the attachment. **Corrected 2026-11-12:** today the body already starts with the run state, CI and totals, but an overflow attaches the waiting list whether or not it was cut and cuts the progress list with no attachment at all. The progress list goes in its own attachment, `verified-this-week.txt`, and each list is attached only when the body cuts it, so a progress-only overflow leaves the waiting list whole in the body; the waiting list keeps its place before the progress list, since it is what asks for the owner's action.
- [x] Cut each list at whole items and count items, not lines: a wrapped entry is shown whole or not at all, and the count line says exactly how many items the attachment adds. Done when: a test whose cut falls on a wrapped title shows that item either whole or left out, the count equal to the items not shown, and every body line within 100 characters and the body within 120 lines in each overflow test. **Corrected 2026-11-12:** added after the plan review (gap 1, P2).
- [x] Keep the notices part of D00 T03 §53 in its place between the waiting and the progress lists, and give it its room before either list takes any: its summary, an unreadable-queue line and the unconfirmed-delivery warning. Done when: a test with notices, an overflowing waiting list and an overflowing progress list shows every attachment's pointer in the body and all three attachments complete. **Corrected 2026-11-12:** added after the plan review (gap 2, P2).
- [x] Commit: `automations: the digest keeps a long progress list`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_owner_digest.py"` passes with both overflow tests among them.

> **Verified:** 2026-11-12 | §2 | 905da4d3812789278a7435ca1a86ac02026f97db
> **Review:** `docs/reviews/d00-t07-s2.json`

## 3. Digest Delivery Survives a Failed Send

> **Started:** 2026-11-12T10:38:16Z

Filed 2026-11-11 from the completion review of T03 §35 (round 2, finding 3, P2). T03 §35 sends once a week; when the send fails (no network on Monday morning), the runner records the failure and the next digest comes a week later, its seven-day window past what was missed. This section remembers the last digest delivered and retries a failed one.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Report from the last delivered digest and retry a failure. Done when: a failed send is retried and its period is reported whole.

- [x] Record each delivered digest in `build/automations/owner-digest.json` (the period it covered and the provider's message id), written temp-then-replace, and report from the end of the last delivered period rather than a fixed seven days. Done when: a test with a failed week shows the next digest covering both weeks.
- [x] Retry a definite failure (a refused send, a network error before a response) at most four times a day until it is delivered, through a daily task `office-owner-digest-retry` that does nothing when the last digest was delivered. **Corrected 2026-11-12:** a daily trigger runs once a day, so four tries need the scheduler's other form: `office-owner-digest-retry` runs `python scripts/owner-digest.py --retry` at logon (after 5 minutes, so a PC that was off on Monday tries as soon as it is back) and every 360 minutes, and `--retry` itself refuses a fifth attempt in one day (the attempts are counted in `build/automations/owner-digest.json`) and exits 0 doing nothing when no failed digest is pending. Done when: tests show a retry after a refusal and none after a delivery, and `tasks.json` and the README agree.
- [x] Treat an ambiguous outcome (a timeout after the request was sent) as possibly delivered: record it, do not resend that period, and say so in the next digest. **Corrected 2026-11-12:** each digest's subject already carries its own token, and D00 T03 §53 asks SMTP2GO's activity log whether a subject went out (`alert.delivery`), so an ambiguous digest is first settled by that log: sent, it is recorded delivered; not sent, it becomes a definite failure and is retried; only when the log cannot tell (unreadable, or past its history) is it treated as possibly delivered, as this item says. Done when: a test shows no second send after a timeout and the note in the following digest.
- [x] Count only two outcomes as a definite failure: SMTP2GO's own answer refusing the send (an HTTP error status or `succeeded: 0`), and a failure before anything was sent (the name did not resolve, the connection was refused). Every other transport error (a timeout, a reset or a cut connection after the request went out) is unsure, settled by the log as below. Done when: a test whose fake accepts the request and then drops the connection records the attempt unsure and sends nothing more for that period. **Corrected 2026-11-12:** replaces the first wording's network error before a response (plan review gap 1, P1).
- [x] Record every attempt before it is sent: the token, the subject, the period and the time go into `build/automations/owner-digest.json` (temp file, then replace) as an attempt in stage `sending`; a run that cannot write it does not send and exits 1. After the send, a delivery moves the period to `delivered` and clears the attempt; a run that ends between the two (killed, or the write failing) leaves the attempt in `sending`, which the next run settles by the log, never by sending again. Done when: tests show a refused pre-send write sending nothing, and a kill after the send (the post-send write failing) followed by a run that asks the log and records delivered with no second send, for a digest with notices and one without. **Corrected 2026-11-12:** added after the plan review (gap 2, P1).
- [x] Settle an attempt in `sending` or unsure at the start of every run, by `alert.delivery` on its subject from its start time, with the rules of D00 T03 §53's claims: `sent` records it delivered; `not-sent`, or `absent` once older than `alert.YOUNG_MINUTES`, makes it a definite failure to retry; `pending`, `absent` while younger, and an unreadable log keep it to ask again at the next run (weekly or retry); still undecided after `alert.SETTLE_DAYS`, it counts as delivered but unconfirmed, and the next digest says so. Done when: one test per outcome (sent, not-sent, young absent, old absent, pending, unreadable, expired) shows the recorded stage and whether a send follows. **Corrected 2026-11-12:** added after the plan review (gap 3, P1).
- [x] Let one digest run at a time: the weekly run and `--retry` take one lock, `build/automations/owner-digest.lock`, before reading the state, and a run that finds it held exits 0 sending nothing; the state is read again under the lock before any send. Done when: a test starting a weekly run and a retry together shows exactly one send. **Corrected 2026-11-12:** added after the plan review (gap 4, P1).
- [x] Fix the period exactly: with no delivery recorded it starts seven days before the first attempt, and that start is kept through every failed or unsure attempt until one is delivered; after a delivery the next period starts on the delivered period's last day (inclusive, since a receipt holds only its date: a section can show twice, never not at all); an unsure attempt still being settled keeps its period, so the next digest starts after it only once it is settled delivered. **Corrected again 2026-11-12:** holding every new digest back until an unsure one settles would cost the owner the weekly email whenever SMTP2GO's log cannot be read (D00 T03 §53's tests expect the next digest to go out), so the weekly run sends while an attempt is unsettled: the unsettled attempt joins `open` and is settled on its own, the new digest starts on its period's last day (so that period is not sent again), and an open attempt the log later shows not sent sets `missed_from` to its start, which the next digest reaches back to. A missing state file is a first run; a corrupt or unreadable one is refused with exit 2 and sends nothing. Done when: tests across separate runs reading the stored state cover the first run, two failed first attempts, a delivery then the next week, a same-day stamp, an unsure period, and a missing, corrupt and unreadable state file. **Corrected 2026-11-12:** added after the plan review (gap 5, P2).
- [x] Prove the retry limit by behaviour: a fifth attempt on one local day (the PC's date; the weekly run's attempt counts) sends nothing, the count survives a restart (it is in the state file), the next day starts at zero, `--retry` with nothing failed changes nothing and sends nothing, and the `tasks.json` entry is the logon trigger after 5 minutes repeating every 360 minutes. Done when: those tests pass and `run.py`'s task loader accepts the entry. **Corrected 2026-11-12:** added after the plan review (gap 6, P2).
- [x] Commit: `automations: a failed digest is sent again`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_owner_digest.py"` and `-p "test_automations.py"` pass with the delivery tests among them.

> **Verified:** 2026-11-12 | §3 | e1e58c0b50bb2bead7353f82b7d796431f94c007
> **Review:** `docs/reviews/d00-t07-s3.json`

## 4. Scheduled Tasks Start on a Monday Morning

> **Started:** 2026-11-12T14:37:35Z

Filed 2026-11-11 from `todo/findings.md` (the entry of 2026-11-11). The 2026-11-09 runs of `office-visual-studio` and `office-python-pin` ended with Task Scheduler result 0x8007010B (the directory name is invalid) before `run.py` started, while `office-pr-merge`, registered the same way, ran on 2026-11-11. `office-owner-digest` runs in the same Monday hour, so a digest could fail the same way and say nothing. This section finds the cause from the machine's own records and fixes it where it lives.

**Phase:** 0
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Establish the cause. Done when: the Task Scheduler and system event records of 2026-11-09 07:25 to 07:35 name why the working directory was refused.
2. Fix it at its owner. Done when: a run of each task started by Task Scheduler itself succeeds and writes its log.

- [ ] Read the Task Scheduler operational log (enable it with `wevtutil sl Microsoft-Windows-TaskScheduler/Operational /e:true` when it is off) and the System log for the failed launches, and record the cause in `todo/findings.md` beside the entry. Done when: the entry names the cause and its evidence. **Corrected 2026-11-12:** read on 2026-11-12. The Task Scheduler operational log was disabled (`wevtutil gl` reports `enabled: false`), so it holds nothing for 2026-11-09. The System log does: event 26 (Application Popup) at 07:26:05 that morning, `Windows - Out of Virtual Memory: Your system is low on virtual memory`, two minutes before the failed launches at 07:28 and 07:31; the PC had been up since 2026-11-08 11:38 (no boot, wake or volume event in between), and `office-pr-merge` left no log under `build/automations/` on 2026-11-08 or 2026-11-09 either, running again on 2026-11-10. So the launches failed while the machine was out of commit memory, a transient state of the host, not a wrong working directory in the task.
- [ ] Fix the cause in the layer that owns it (`.conclave/automations/install.ps1` when it is the task definition, the task's start conditions when it is the machine's state at that hour), (**Corrected 2026-11-12:** it is the machine's state at that hour, which a task cannot prevent but can outlast: the installer gives every task Task Scheduler's own restart on failure, three more attempts ten minutes apart, so a launch that fails in a bad minute is tried again, and it enables the Task Scheduler operational log so the next failed launch leaves its own record) with a test in `scripts/tests/test_automations.py` where the installer changes. Done when: the test fails before the change, and `Start-ScheduledTask -TaskPath '\Office\' -TaskName office-python-pin` leaves `LastTaskResult` 0 and a new log under `build/automations/office-python-pin/`.
- [ ] Make `run.py` or the installer report a launch that never reached `run.py`, so a task that cannot start is not silent: the digest (D00 T03 §35) names any task whose last result is not 0. Done when: a test shows the digest line for a failing task result.
- [ ] Strike the finding in `todo/findings.md` as shipped by this section. Done when: the entry ends with this section's reference and the word shipped.
- [ ] Record the cause as suspected, not proved: the low-memory event is two minutes before the failures, but no record of the launches themselves exists (the Scheduler log was off), so `todo/findings.md` says what is known, what is inferred, and that the restart setting makes the tasks outlast such a minute without curing what exhausted the memory (the 2026-11-08 flood and unqueued heavy jobs, since bounded and queued through `bosun`). Done when: the entry separates the evidence from the inference. **Corrected 2026-11-12:** added after the plan review (gap 2, P2).
- [ ] Prove the recovery on a real failed launch, with a scratch task and never one of the four real ones: `python scripts/check-task-retry.py` registers `\Office\office-retry-selftest` through the same settings function the installer uses, with a working directory that does not exist (the 0x8007010B of 2026-11-09), starts it once, watches Task Scheduler start it again by itself, creates the directory, and sees the next retry write its marker file; a second pass leaves the directory missing and counts the launches to show they stop at the limit; the task and its folder are removed however the script ends, and its settings are read back from the Scheduler. Done when: its output, with the launch times and results, is in the section's findings file. **Corrected 2026-11-12:** added after the plan review (gap 1, P1); a manual start that succeeds proves nothing about retries.
- [ ] Tell a failed task from one that is running, ready or has never run: Task Scheduler's own success statuses (0x41300 ready, 0x41301 running, 0x41302 disabled, 0x41303 not yet run, 0x41325 queued) and 0 are not failures, anything else is. Done when: tests show the digest's own task, running while it composes, not reported, a never-run task not reported, and 0x8007010B reported with its hexadecimal code and the day. **Corrected 2026-11-12:** added after the plan review (gap 3, P2).
- [ ] Have the digest ask Task Scheduler itself, never the task logs: one bounded PowerShell query for the tasks of the folder `tasks.json` names (`Get-ScheduledTask` and `Get-ScheduledTaskInfo` as JSON), since a task that never starts writes no log; a task `tasks.json` lists and the Scheduler does not hold is reported as not installed; when the query fails or its answer cannot be read, the digest says `Scheduled tasks: unknown (<reason>)` and is still sent. Done when: tests with a fake query show a failed launch with no runner log in the composed digest, the not-installed line, the unknown line with the digest delivered, and a healthy set printing nothing. **Corrected 2026-11-12:** added after the plan review (gap 4, P2).
- [ ] Commit: `automations: scheduled tasks start on a Monday morning`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_automations.py"` passes, and `Get-ScheduledTask -TaskPath '\Office\' | Get-ScheduledTaskInfo` shows `LastTaskResult` 0 for every task after a run started by Task Scheduler.

## Verification
- `python -m unittest discover -s scripts/tests -p "test_owner_digest.py"` passes.
- `python scripts/owner-digest.py --dry-run` prints a digest for this repository and exits 0.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
