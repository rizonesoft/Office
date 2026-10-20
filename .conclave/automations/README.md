# Office-2028 automations

Every scheduled job for Office-2028 lives here: the task list in `tasks.json`, the runner, the failure alert, and the Task Scheduler installer. Ported from Isotone's automations (operator request, 2026-10-20), which were adapted from Rizonetech's; Office-2028 runs on Windows, so the tasks are Windows Task Scheduler tasks under `\Office-2028\`.

## What runs

| Task | When (local time) | Runs | Fails when |
| --- | --- | --- | --- |

Every task starts when available: a run missed while this PC was off fires at the next chance. A start while the task still runs is ignored, the execution limit is five minutes past the task's timeout, and weekly tasks carry a five-minute random delay. Tasks run only while the operator is logged on, so no password is stored.

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
```

The installer reads `tasks.json` and registers every task it lists; a task under `\Office-2028\` that the file no longer lists is removed.

## Adding an automation

1. Add an entry to `tasks.json`: an `office-2028-` name, a description, the command (a script in this repository, `python` first), a trigger (`{"weekly": "<Day>", "at": "HH:MM"}` or `{"at_logon_delay_minutes": N, "every_minutes": N}`), and `timeout_minutes`.
2. Add its row to the table above; `scripts/tests/test_automations.py` fails until the table and the file agree.
3. Run the tests, then the installer.
