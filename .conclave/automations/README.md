# Office automations

Every scheduled job for Office lives here: the task list in `tasks.json`, the runner, the failure alert, and the Task Scheduler installer. Ported from Isotone's automations (operator request, 2026-10-20), which were adapted from Rizonetech's; Office runs on Windows, so the tasks are Windows Task Scheduler tasks under `\Office\`.

## What runs

| Task | When (local time) | Runs |
| --- | --- | --- |
| `office-winui-pin` | Daily 06:23 | `scripts/check-winui-pin.py update` |
| `office-dotnet-pin` | Daily 06:33 | `scripts/check-dotnet-pin.py update` |
| `office-nuget-pins` | Monday 07:00 | `scripts/check-nuget-pins.py update` |
| `office-vulnerable-packages` | Monday 07:15 | `scripts/check-vulnerable-packages.py` |
| `office-dotnet-local` | Monday 07:20 | `scripts/check-dotnet-pin.py local` |
| `office-visual-studio` | Monday 07:25 | `scripts/check-visual-studio.py notify` |
| `office-python-pin` | Monday 07:30 | `scripts/check-python-pin.py notify` |
| `office-conclave-kits` | Monday 07:35 | `scripts/check-conclave-kits.py notify` |

What each one emails you about, and when it fails (which sends the failure alert instead):

- `office-winui-pin`: emails when a newer stable WinUI 3 release is on branch `winui/<version>`, ready to merge. Fails when a proposal's checks fail, the pin on main is not an exact stable version on NuGet, or the releases or NuGet cannot be read.
- `office-dotnet-pin`: emails when a newer .NET 11 SDK is on branch `dotnet/<version>`, ready to merge. Fails when a proposal's checks fail, the pin on main is not a .NET 11 SDK the release feed lists, `global.json` does not disable roll-forward, or the feed cannot be read.
- `office-nuget-pins`: emails when the other NuGet pins at their latest stable releases are on branch `pins/nuget-<key>`. Fails when a proposal's checks fail, a pin is not an exact stable version on nuget.org, or nuget.org cannot be read. With no other pin yet, it checks nothing and succeeds.
- `office-vulnerable-packages`: never emails; fails when a NuGet package in the solution, direct or transitive, has a published advisory, or the restore or the report fails. No solution yet (until D03 T01 §12 creates it) is a success.
- `office-dotnet-local`: emails once when this machine lacks the .NET SDK that `global.json` pins. Fails when `global.json` cannot be read or `dotnet` is not on PATH.
- `office-visual-studio`: emails once per release when this machine's Visual Studio 2026 is behind its latest servicing release. Fails when none is installed, or vswhere or the release channel cannot be read.
- `office-python-pin`: emails once when this machine's Python is behind the newest stable CPython (minor or patch). Fails when python.org cannot be read.
- `office-conclave-kits`: emails once per state when Office's base, todo or reviewer kit files drift from the Conclave SDK's committed kits, or its doctor reports a gap. Fails when no SDK checkout is configured (`CONCLAVE_SDK_ROOT`) or found beside this repository (`Conclave-SDK`), the doctor gives no report, or an allow-list entry has no reason.

Every task starts when available: a run missed while this PC was off fires at the next chance. A start while the task still runs is ignored, the execution limit is five minutes past the task's timeout, and daily and weekly tasks carry a five-minute random delay. Tasks run only while the operator is logged on, so no password is stored. Office keeps its own runner, alert and installer rather than the Conclave SDK automations kit's (operator, 2026-10-21), for the fixed-time daily trigger and the per-run alert record.

## How you hear about it

Every email goes to `rizonetech@gmail.com` from "Office automations" (`website@rizonetech.com`, through SMTP2GO), and there are exactly three kinds:

- **"Office: ... is ready to merge"**: a pin moved on a branch. The WinUI 3, .NET and NuGet tasks change pins only on a new branch from main, after its checks pass, and the email names the branch and the `git merge` command. Nothing changes on main or in your checkout until you merge, and nothing is pushed.
- **"Office: ... is available", "install ..." or "has drifted"**: something on this PC is behind (Visual Studio, Python, the pinned .NET SDK) or the Conclave kits drifted. The task succeeds and sends this once per new version or state.
- **"Office automation failed: <task> on <host>"**: a check could not run or found a broken pin. It repeats on every failing run until fixed, with the log tail.

Each new version or state is emailed once, so no new email means nothing new, not that every pin is current: a proposal you have not merged stays on its branch without another email, and a machine finding you have not acted on is not sent again. `python scripts/check-<name>.py check` (exit 1 while main is behind or this PC needs an update) and `git branch --list winui/* dotnet/* pins/*` show what is still open. Each finished proposal and announcement is a git ref (`refs/office-pin/<key>`, `refs/office-notice/<key>`); `git for-each-ref refs/office-pin refs/office-notice` lists them, and deleting one makes its task propose or announce again. A proposal branch without its ref is an unfinished attempt (an email that failed, a run cut short), which the next run discards and redoes. The shared code is `scripts/lib/pin_proposal.py`, `scripts/lib/pin_sources.py` and `scripts/lib/package_versions.py`, ported from RectoPDF on 2026-10-21.

## Campaign runs

There is no keep-alive task. Retired 2026-10-21 (operator, adopting the Conclave-SDK todo kit: "we do not need the keep-alive in automations, just heartbeat with stop hook"): a `process-plan` run is held by the todo kit's run guard alone, the Stop hook (`scripts/campaign_guard.py stop-hook`, wired in `.claude/settings.json`) and the in-session `CronCreate` heartbeat. Both die with their session; a session that died is resumed by the operator, and the new session takes the guard with `acquire --handover`. The `process-plan` skill holds the rules.

## The WinUI 3 pin

Owner rule (2026-10-20): the repository always pins the latest stable WinUI 3 release, the newest `winui3/release/<version>` GitHub release of the microsoft-ui-xaml repository that is neither a prerelease, a draft nor experimental, and NuGet must publish it. The pin is the `Microsoft.WindowsAppSDK` version in `Directory.Packages.props`.

Each morning `scripts/check-winui-pin.py update` compares the newest stable release with the pin on main (never the checkout). When a newer one exists, it adds a temporary git worktree on a new branch `winui/<version>` from main, rewrites only the pin there, runs the checks (the file parses, NuGet has the version, and once a solution exists every solution builds with `dotnet build`), commits, removes the worktree and emails the branch to merge. A finished release (its `refs/office-pin/winui-<version>`) is never proposed again, even after you delete its branch.

`python scripts/check-winui-pin.py check` exits 1 while a newer stable release is pending, and `update --dry-run` says what the task would do.

## The .NET 11 pin

Owner rule (2026-10-21): the repository always pins the newest .NET 11 SDK, at any stage: the release candidate now, the release once it ships, then each later patch or feature band. The pin is `sdk.version` in `global.json`, with roll-forward disabled so every build uses exactly that SDK. The target is `latest-sdk` in the .NET 11 release metadata (`https://builds.dotnet.microsoft.com/dotnet/release-metadata/11.0/releases.json`, the feed `dotnet-install` reads).

Each morning `scripts/check-dotnet-pin.py update` proposes a newer SDK on `dotnet/<version>` the same way as the WinUI 3 pin. Once a solution exists, the proposal is built only when this PC has that SDK installed, so the failure alert asks you to install it first. Weekly, `check-dotnet-pin.py local` emails you once when this PC lacks the SDK the checkout pins. This replaces `check-sdk-ga.py`, which only reported the release; moving the pin to the release is now a proposal like any other.

`python scripts/check-dotnet-pin.py check` exits 1 while a newer SDK is pending, and `update --dry-run` says what the task would do.

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
python -m unittest discover -s scripts/tests -p "test_pin_automations.py"
git for-each-ref refs/office-pin refs/office-notice           # finished proposals and sent notices
```

Installed and verified on the operator's PC (Venom-PC) on 2026-10-20: `office-claude-keepalive` is registered under `\Office\` with a logon trigger (3 minute delay) and an hourly time trigger, next run 2026-10-20 04:16:56 South Africa Standard Time (UTC+2), last result 267011 (not yet run); `campaign_keepalive.py status` answered `idle: no open campaign run` before the phase 2 run was put under the guard; the alert dry run rendered the task, exit and log tail; and one real alert (the throwaway task `office-alert-test`, exiting 1 in a scratch workspace, sent through the runner with the operator's go-ahead) arrived in `rizonetech@gmail.com` from `website@rizonetech.com`: subject "Office automation failed: office-alert-test on Venom-PC", received 2026-10-20 01:17:45 UTC, `internetMessageId` `<E1xIyU5-FnQW0hPmZ73-1DpI@message-id.smtpcorp.com>`. That send predates the runner recording sends in `last.json`; `test_automations.py` (`AlertRecord`) proves every later send records its email id (or that none was given) in a per-run `<log>.alert.json` and in `last.json` while it still describes that run, and an unsent one its error.

Read back on Venom-PC on 2026-10-21: no task was registered under `\Office\` (the folder was absent). The same day `install.ps1` registered all eight tasks in `tasks.json`, with the first runs read back as `office-winui-pin` 2026-10-21 06:26:59 and `office-dotnet-pin` 06:37:05 (daily), and the weekly tasks from 2026-10-26 07:00:47. The `office-claude-keepalive` task named above was retired the same day (see Campaign runs).

The installer reads `tasks.json` and registers every task it lists; a task under `\Office\` that the file no longer lists is removed.

## Adding an automation

1. Add an entry to `tasks.json`: an `office-` name, a description, the command (a script in this repository, `python` first), a trigger (`{"daily_at": "HH:MM"}`, `{"weekly": "<Day>", "at": "HH:MM"}` or `{"at_logon_delay_minutes": N, "every_minutes": N}`), and `timeout_minutes`.
2. Add its row to the table above and its line to the list under it; `scripts/tests/test_automations.py` fails until the table and the file agree.
3. A check that moves a repository pin proposes it through `pin_proposal.propose` (a branch from main, checks, an email); a check of something on this PC announces it through `pin_proposal.notice` (one email per new version or state). Neither changes main or the checkout. Add its tests to `scripts/tests/test_pin_automations.py`.
4. Run the tests, then the installer.
