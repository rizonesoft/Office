# Office-2028 automations

Every scheduled job for Office-2028 lives here: the task list in `tasks.json`, the runner, the failure alert, and the Task Scheduler installer. Ported from Isotone's automations (operator request, 2026-10-20), which were adapted from Rizonetech's; Office-2028 runs on Windows, so the tasks are Windows Task Scheduler tasks under `\Office-2028\`.

## What runs

| Task | When (local time) | Runs | Fails when |
| --- | --- | --- | --- |
| office-2028-claude-keepalive | Logon, hourly | scripts/campaign_keepalive.py resurrect | Below |

Every task starts when available: a run missed while this PC was off fires at the next chance. A start while the task still runs is ignored, the execution limit is five minutes past the task's timeout, and weekly tasks carry a five-minute random delay. Tasks run only while the operator is logged on, so no password is stored.

## The keep-alive

The run heartbeat (`CronCreate`) runs inside its Claude session, so it dies with it. The keep-alive covers what it cannot: a restart, a crash, or a closed terminal that leaves the guard (`build/claude-campaign-guard.json`) open with nobody working the run. It resumes that exact session headless (`claude -p --resume <session> --model <writer> --permission-mode bypassPermissions`), with the writer model from `.conclave/keepalive.toml`, and supervises it.

It acts only on proof. The SessionStart hook (`campaign_keepalive.py observe`, wired in `.claude/settings.json`) records the Claude process of every Office-2028 session as a pid and creation time under `build/claude-sessions/`. A launch needs the guard's session recorded and that exact process gone, and no other Office-2028 session alive: while the operator has any Office-2028 session open, the keep-alive waits, because one session owns the tree. A guard taken by a Codex or Antigravity run (`acquire --runner`) is held too: only Claude runs are ever resumed. While a resume runs, the supervisor ends its process tree as soon as the guard is ended or handed over, or another Office-2028 session starts. The full rule list is in the `campaign_keepalive.py` docstring, and `python scripts/campaign_keepalive.py status` says what it would do now.

It runs 3 minutes after each logon and then hourly. It fails (and alerts) when a resumed session exits non-zero or runs past 4 hours, three resumes in a row make no progress (reported once), `.conclave/keepalive.toml` names no writer model, or no `claude` is on PATH. No open run, a live owner, or an attended session is a success.

The resumed session's output goes to `build/claude-keepalive/<run id>-<UTC>.log`, and the keep-alive's own state to `build/claude-keepalive.json`.

## When a run fails

Task Scheduler starts `pythonw.exe .conclave/automations/run.py <name>`. The runner writes the run's output to `build/automations/<name>/<UTC>.log` (the newest 20 kept) and its outcome to `build/automations/<name>/last.json`. On a non-zero exit or a timeout it calls `alert.py`, which emails `rizonetech@gmail.com` the task, its exit, and the tail of that run's log.

- It sends through SMTP2GO from `website@rizonetech.com`, the verified sender the Rizonetech automations use (Rizonesoft is a brand of Rizonetech).
- The key is read at send time from the Conclave vault item "Rizonetech SMTP2GO (website mail)" through `conclave-op` in WSL. Nothing is stored here, and there is no `.env`.
- SMTP2GO answers a refused send with HTTP 200 and `succeeded: 0`; the alert treats that as a failure.
- The runner exits with the command's code (124 on a timeout), or 3 when the alert could not be sent, with the reason appended to the run's log, so Task Scheduler's Last Run Result shows every failure.

## Install and inspect

```powershell
pwsh .conclave/automations/install.ps1              # idempotent; re-run after editing tasks.json
pwsh .conclave/automations/install.ps1 -DryRun      # print what would be registered or removed
pwsh .conclave/automations/install.ps1 -Uninstall   # remove every \Office-2028\ task
Get-ScheduledTask -TaskPath '\Office-2028\' | Get-ScheduledTaskInfo | Format-Table TaskName, NextRunTime, LastRunTime, LastTaskResult
python .conclave/automations/run.py <name>                    # run one task in this console
python .conclave/automations/alert.py <name> --dry-run        # preview the alert for its last run
python -m unittest discover -s scripts/tests -p "test_automations.py"
python scripts/campaign_keepalive.py status                    # what the keep-alive would do now
```

Installed and verified on the operator's PC (Venom-PC) on 2026-10-20: `office-2028-claude-keepalive` is registered under `\Office-2028\` with a logon trigger (3 minute delay) and an hourly time trigger, next run 2026-10-20 04:16:56 South Africa Standard Time (UTC+2), last result 267011 (not yet run); `campaign_keepalive.py status` answered `idle: no open campaign run` before the phase 2 run was put under the guard; the alert dry run rendered the task, exit and log tail; and one real alert (the throwaway task `office-2028-alert-test`, exiting 1 in a scratch workspace, sent through the runner with the operator's go-ahead) arrived in `rizonetech@gmail.com` from `website@rizonetech.com`: subject "Office-2028 automation failed: office-2028-alert-test on Venom-PC", received 2026-10-20 01:17:45 UTC, `internetMessageId` `<E1xIyU5-FnQW0hPmZ73-1DpI@message-id.smtpcorp.com>`. That send predates the runner recording sends in `last.json`; `test_automations.py` (`AlertRecord`) proves every later send records its email id (or that none was given) in a per-run `<log>.alert.json` and in `last.json` while it still describes that run, and an unsent one its error.

The installer reads `tasks.json` and registers every task it lists; a task under `\Office-2028\` that the file no longer lists is removed.

## Adding an automation

1. Add an entry to `tasks.json`: an `office-2028-` name, a description, the command (a script in this repository, `python` first), a trigger (`{"weekly": "<Day>", "at": "HH:MM"}` or `{"at_logon_delay_minutes": N, "every_minutes": N}`), and `timeout_minutes`.
2. Add its row to the table above; `scripts/tests/test_automations.py` fails until the table and the file agree.
3. Run the tests, then the installer.
