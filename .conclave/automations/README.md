# Office automations

Every scheduled job for Office lives here: the task list in `tasks.json`, the runner, the failure alert, and the Task Scheduler installer. Ported from Isotone's automations (operator request, 2026-10-20), which were adapted from Rizonetech's; Office runs on Windows, so the tasks are Windows Task Scheduler tasks under `\Office\`.

## What runs

| Task | When (local time) | Runs |
| --- | --- | --- |
| `office-winui-pin` | Daily 06:23 | `scripts/check-winui-pin.py update` |
| `office-vulnerable-packages` | Monday 07:15 | `scripts/check-vulnerable-packages.py` |
| `office-dotnet-ga` | Monday 07:30 | `scripts/check-sdk-ga.py` |

Each fails, and so alerts, when:

- `office-winui-pin`: a newer stable WinUI 3 release cannot be proposed (a check fails, which leaves no branch), or the releases or NuGet cannot be read. A proposal is emailed and is a success.
- `office-vulnerable-packages`: a NuGet package in the solution, direct or transitive, has a published advisory, or the restore or the report fails. No solution yet (until D03 T01 §12 creates it) is a success.
- `office-dotnet-ga`: the .NET 11 GA SDK is out while `global.json` still pins a release candidate, so D03 T01 §2 is ready. A newer release candidate is printed, not failed.

Every task starts when available: a run missed while this PC was off fires at the next chance. A start while the task still runs is ignored, the execution limit is five minutes past the task's timeout, and weekly tasks carry a five-minute random delay. Tasks run only while the operator is logged on, so no password is stored.

## Campaign runs

There is no keep-alive task. Retired 2026-10-21 (operator, adopting the Conclave-SDK todo kit: "we do not need the keep-alive in automations, just heartbeat with stop hook"): a `process-plan` run is held by the todo kit's run guard alone, the Stop hook (`scripts/campaign_guard.py stop-hook`, wired in `.claude/settings.json`) and the in-session `CronCreate` heartbeat. Both die with their session; a session that died is resumed by the operator, and the new session takes the guard with `acquire --handover`. The `process-plan` skill holds the rules.

## The WinUI 3 pin

Owner rule (2026-10-20): the repository always pins the latest stable WinUI 3 release, the newest `winui3/release/<version>` GitHub release of the microsoft-ui-xaml repository that is neither a prerelease nor experimental. The pin is the `Microsoft.WindowsAppSDK` version in `Directory.Packages.props`.

Each morning `scripts/check-winui-pin.py update` compares the two. When a newer stable release exists and NuGet publishes it, the script adds a temporary git worktree on a new branch `winui/<version>` from main, rewrites only the pin there, runs the checks (the file parses, NuGet has the version, and, once a solution exists, `dotnet build` passes), commits, removes the worktree and emails `rizonetech@gmail.com` the branch to merge (`git merge winui/<version>`). It never touches the operator's checkout or main, and never pushes. A branch that already exists means the release was proposed before, so nothing is redone or re-sent. It fails (and alerts) when a check fails, which leaves no branch, or when the releases or NuGet cannot be read.

`python scripts/check-winui-pin.py check` exits 1 while a newer stable release is pending, and `update --dry-run` says what the task would do.

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
pwsh .conclave/automations/install.ps1 -Uninstall   # remove every \Office\ task
Get-ScheduledTask -TaskPath '\Office\' | Get-ScheduledTaskInfo | Format-Table TaskName, NextRunTime, LastRunTime, LastTaskResult
python .conclave/automations/run.py <name>                    # run one task in this console
python .conclave/automations/alert.py <name> --dry-run        # preview the alert for its last run
python -m unittest discover -s scripts/tests -p "test_automations.py"
```

Installed and verified on the operator's PC (Venom-PC) on 2026-10-20: `office-claude-keepalive` is registered under `\Office\` with a logon trigger (3 minute delay) and an hourly time trigger, next run 2026-10-20 04:16:56 South Africa Standard Time (UTC+2), last result 267011 (not yet run); `campaign_keepalive.py status` answered `idle: no open campaign run` before the phase 2 run was put under the guard; the alert dry run rendered the task, exit and log tail; and one real alert (the throwaway task `office-alert-test`, exiting 1 in a scratch workspace, sent through the runner with the operator's go-ahead) arrived in `rizonetech@gmail.com` from `website@rizonetech.com`: subject "Office automation failed: office-alert-test on Venom-PC", received 2026-10-20 01:17:45 UTC, `internetMessageId` `<E1xIyU5-FnQW0hPmZ73-1DpI@message-id.smtpcorp.com>`. That send predates the runner recording sends in `last.json`; `test_automations.py` (`AlertRecord`) proves every later send records its email id (or that none was given) in a per-run `<log>.alert.json` and in `last.json` while it still describes that run, and an unsent one its error.

Read back on Venom-PC on 2026-10-21: no task is registered under `\Office\` (the folder is absent), so none of the tasks above runs until `install.ps1` is run again. The `office-claude-keepalive` task named above was retired the same day (see Campaign runs).

The installer reads `tasks.json` and registers every task it lists; a task under `\Office\` that the file no longer lists is removed.

## Adding an automation

1. Add an entry to `tasks.json`: an `office-` name, a description, the command (a script in this repository, `python` first), a trigger (`{"weekly": "<Day>", "at": "HH:MM"}` or `{"at_logon_delay_minutes": N, "every_minutes": N}`), and `timeout_minutes`.
2. Add its row to the table above; `scripts/tests/test_automations.py` fails until the table and the file agree.
3. Run the tests, then the installer.
