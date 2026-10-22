# Office automations

Every scheduled job for Office lives here: the task list in `tasks.json`, the runner, the failure alert, and the Task Scheduler installer. Ported from Isotone's automations (operator request, 2026-10-20), which were adapted from Rizonetech's; Office runs on Windows, so the tasks are Windows Task Scheduler tasks under `\Office\`.

## What runs

| Task | When (local time) | Runs |
| --- | --- | --- |
| `office-visual-studio` | Monday 07:25 | `scripts/check-visual-studio.py notify` |
| `office-python-pin` | Monday 07:30 | `scripts/check-python-pin.py notify` |
| `office-pr-merge` | Daily 07:43 | `scripts/merge_prs.py --skip-unsafe` |

What each one emails you about, and when it fails (which sends the failure alert instead):

- `office-visual-studio`: emails once per release when this machine's Visual Studio 2026 (the MSVC toolset the C++ build uses) is behind its latest servicing release. Fails when none is installed, or vswhere or the release channel cannot be read.
- `office-python-pin`: emails once when this machine's Python is behind the newest stable CPython (minor or patch). Fails when python.org cannot be read.
- `office-pr-merge`: never emails on success; merges green Dependabot and pins pull requests (labelled `dependencies` or `pins`, every check green, cleanly mergeable) one at a time by rebase, then pulls and validates. It skips quietly (exit 0, the reason in its log) while a campaign run is open (the campaign merges at its own section boundaries) or while the checkout is dirty, off `main`, behind or ahead of `origin/main`, or mid-section. Each pull request is read again and judged again just before its merge, under the run guard's lock. Fails when a merge, pull or validate fails (exit 1), leaving the rest open (a pull request already merged when its pull or validate failed is reported as merged), or when git or gh cannot be run or read (exit 3).

Every task starts when available: a run missed while this PC was off fires at the next chance. A start while the task still runs is ignored, the execution limit is five minutes past the task's timeout, and daily and weekly tasks carry a five-minute random delay. Tasks run only while the operator is logged on, so no password is stored. Everything in this folder is Office's own, for the fixed-time daily trigger and the per-run alert record. Office takes nothing from the Conclave SDK (operator, 2026-10-21): the `office-conclave-kits` drift check and `.conclave/kits.json` were removed that day.

## How you hear about it

Every email goes to `rizonetech@gmail.com` from "Office automations" (`website@rizonetech.com`, through SMTP2GO), and there are exactly three kinds:

- **"Office: ... is ready to merge"**: a pin moved on a branch. A pin task changes a pin only on a new branch from main, after its checks pass, and the email names the branch and the `git merge` command. Nothing changes on main or in your checkout until you merge, and nothing is pushed. No task proposes pins today; the C++ toolchain pins (D00 T03 §11) will.
- **"Office: ... is available", "install ..." or "has drifted"**: something on this PC is behind (Visual Studio, Python). The task succeeds and sends this once per new version or state.
- **"Office automation failed: <task> on <host>"**: a check could not run or found a broken pin. It repeats on every failing run until fixed, with the log tail.

Each new version or state is emailed once, so no new email means nothing new, not that every pin is current: a proposal you have not merged stays on its branch without another email, and a machine finding you have not acted on is not sent again. `python scripts/check-<name>.py check` (exit 1 while main is behind or this PC needs an update) and `git branch --list "pins/*"` show what is still open. Each finished proposal and announcement is a git ref (`refs/office-pin/<key>`, `refs/office-notice/<key>`); `git for-each-ref refs/office-pin refs/office-notice` lists them, and deleting one makes its task propose or announce again. A proposal branch without its ref is an unfinished attempt (an email that failed, a run cut short), which the next run discards and redoes. The shared code is `scripts/lib/pin_proposal.py` and `scripts/lib/pin_sources.py`, ported from RectoPDF on 2026-10-21.

## Campaign runs

There is no keep-alive task. Retired 2026-10-21 (operator: "we do not need the keep-alive in automations, just heartbeat with stop hook"): a `process-plan` run is held by the run guard alone, the Stop hook (`scripts/campaign_guard.py stop-hook`, wired in `.claude/settings.json`) and the in-session `CronCreate` heartbeat. Both die with their session; a session that died is resumed by the operator, and the new session takes the guard with `acquire --handover`. The `process-plan` skill holds the rules.

## Retired pins

Retired 2026-10-22 (owner): the suite moved from WinUI 3 in C# on .NET 11 to native C++ with its own GUI toolkit (D03 T01 §2), so the WinUI 3 pin (`office-winui-pin`), the .NET 11 SDK pin (`office-dotnet-pin`, `office-dotnet-local`), the NuGet pins (`office-nuget-pins`) and the NuGet advisory check (`office-vulnerable-packages`) were removed with their scripts, `Directory.Packages.props` and `global.json` (D00 T03 §10). The latest-stable rule they followed carries over to the C++ toolchain pins in D00 T03 §11.

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

Read back on Venom-PC on 2026-10-21: no task was registered under `\Office\` (the folder was absent). The same day `install.ps1` registered all eight tasks in `tasks.json`, with the first runs read back as `office-winui-pin` 2026-10-21 06:26:59 and `office-dotnet-pin` 06:37:05 (daily), and the weekly tasks from 2026-10-26 07:00:47. The `office-claude-keepalive` task named above was retired the same day (see Campaign runs), and `office-conclave-kits` was removed later that day, leaving seven.

The installer reads `tasks.json` and registers every task it lists; a task under `\Office\` that the file no longer lists is removed.

## Adding an automation

1. Add an entry to `tasks.json`: an `office-` name, a description, the command (a script in this repository, `python` first), a trigger (`{"daily_at": "HH:MM"}`, `{"weekly": "<Day>", "at": "HH:MM"}` or `{"at_logon_delay_minutes": N, "every_minutes": N}`), and `timeout_minutes`.
2. Add its row to the table above and its line to the list under it; `scripts/tests/test_automations.py` fails until the table and the file agree.
3. A check that moves a repository pin proposes it through `pin_proposal.propose` (a branch from main, checks, an email); a check of something on this PC announces it through `pin_proposal.notice` (one email per new version or state). Neither changes main or the checkout. Add its tests to `scripts/tests/test_pin_automations.py`.
4. Run the tests, then the installer.
