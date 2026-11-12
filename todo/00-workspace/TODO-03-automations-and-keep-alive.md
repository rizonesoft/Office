---
schema_version: 1
id: automations-and-keep-alive
domain: 00-workspace
status: active
title: "TODO-03 -- Automations and Campaign Keep-Alive"
---

# TODO-03 -- Automations and Campaign Keep-Alive

> **Goal:** Office runs its scheduled jobs from `.conclave/automations/`, as Isotone does: a task list, a runner that logs every run, an email alert on failure, and a Task Scheduler installer. Long `process-plan` and `process-phase` runs are protected by a run guard, a Stop hook that keeps the owning session working while a run is open, the in-session heartbeat, and a keep-alive task that resumes the exact session headless when its process has died. Every piece has a self-test or unit test, and the operator can see what the keep-alive would do with one command.

> **Current state:** Measured 2026-10-20. `.conclave/` holds only `reviewers.toml`; there is no `.claude/settings.json`, no hook, no guard, and no scheduled task. The phase 2 run (`docs/phase-runs/2026-10-20-phase-2.md`) has an in-session `CronCreate` heartbeat whose prompt reads the run file, but nothing survives the session ending. The source to port is Isotone (`R:\GitHub\Isotone`), itself adapted from Rizonetech: `.conclave/automations/{run.py,alert.py,install.ps1,tasks.json,README.md}` (337 lines), `scripts/campaign_guard.py` (1,515 lines with a built-in `--self-test`), `scripts/campaign_keepalive.py` (656 lines with `--self-test`), `.claude/hooks/campaign-stop.ps1` (273 lines), and `scripts/tests/test_automations.py`. Three Isotone assumptions do not hold here: `todo-graph.py query ready` prints JSON, not an `N runnable now` line; the writer model comes from `.conclave/panel.toml`, which this repository does not have; and Isotone's other tasks (.NET SDK, NuGet, panel probe) do not apply. **Renamed 2026-10-20 (owner):** the repository Office-2028 became Office (GitHub `rizonesoft/Office`, local `R:\GitHub\Office`); the Task Scheduler folder is now `\Office\` and the task names `office-*`. Review records under `docs/reviews/` and the phase run files keep the names they verified. **Revised 2026-10-21 (operator):** Office adopted the Conclave-SDK todo and reviewer kits as shipped. The run guard is now the kit's `scripts/campaign_guard.py` with its Python Stop hook (`campaign_guard.py stop-hook` in `.claude/settings.json`) and the in-session heartbeat, tested by `scripts/tests/test_campaign_guard.py`; the keep-alive (§3: `scripts/campaign_keepalive.py`, `.conclave/keepalive.toml`, the SessionStart observer and the `office-claude-keepalive` task), `.claude/hooks/campaign-stop.ps1`, the guard's `--self-test` and CI repair ledger, and the Codex and Antigravity `acquire --runner` guard steps were retired. The sections below record what was built and verified on 2026-10-20. **Revised 2026-10-22 (owner):** the move to native C++ (D03 T01 §2) retires the WinUI 3, .NET SDK and NuGet pin tasks (§10) and replaces them with C++ toolchain pins (§11).

## Inputs

- Isotone's `.conclave/automations/README.md`: the behaviour to reproduce, including the keep-alive's launch rules, supervision and stall breaker.
- Isotone's `process-plan` and `process-phase` skills: the guard, Stop hook and heartbeat steps the runners follow.
- Alert transport: SMTP2GO from `website@rizonetech.com` to `rizonetech@gmail.com`, key read at send time from the Conclave vault item "Rizonetech SMTP2GO (website mail)" through `conclave-op` in WSL (Rizonesoft is a brand of Rizonetech). AGENTS.md: ask the operator once before sending mail.
- The open phase 2 run (`docs/phase-runs/2026-10-20-phase-2.md`), which §6 moves under the guard.
- -> XREF: T04 §1 -- `tools.lock.json`, the lock file of the portable build tools, joins the pins §11 keeps at the latest stable release
- -> XREF: D03 T01 §17 -- the authoring sections whose `Author` items §31 lists in the plan as files still to author
- -> XREF: T07 §1 -- the owner digest follow-ups for §35 (a live run told from an abandoned guard, a long progress list, a failed send), in their own file because this one holds 55 sections

## Outcome

- `pwsh .conclave/automations/install.ps1` registers every task in `tasks.json` under `\Office\`, and `python scripts/tests/test_automations.py` passes, failing when README and `tasks.json` disagree.
- `python -m unittest discover -s scripts/tests -p "test_campaign_guard.py"` drives the guard and its Stop hook against fixture workspaces that use this repository's JSON `query ready` output.
- While a run is open, the Stop hook blocks the owning session's end of turn and names the next ready row, and the in-session heartbeat resumes an idle run; a session that died is resumed by the operator (revised 2026-10-21: the keep-alive task is retired).

**Adjacency:** all=not-applicable (developer automation for this repository; no product records, settings or user documents)

**Adjacency rationale:** These are build-machine jobs and session supervision for the people and agents building the suite. They hold no user data, so none of the nine product keys applies.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Automation runner, alert and installer | -- | [x] |
| 2 | §2 | Run guard and Stop hook | -- | [x] |
| 3 | §3 | Keep-alive task and session observer | §1, §2 | [x] |
| 4 | §4 | Run skills create and check the guard | §2, §3 | [x] |
| 5 | §5 | Install the tasks and verify on this PC | §1, §3 | [x] |
| 6 | §6 | Adopt the guard for the open phase 2 run | §4, §5 | [x] |
| 7 | §7 | Run guard robustness fixes | §2 | [x] |
| 8 | §8 | Agent tier verifier YAML strictness | -- | [x] |
| 9 | §9 | Dependency PR merges at boundaries | §1 | [x] |
| 10 | §10 | Retire the .NET and WinUI 3 pins | §9 | [x] |
| 11 | §11 | C++ toolchain pins | §10, D03 T01 §17 | [ ] |
| 12 | §12 | Campaign host readiness check | §10 | [x] |
| 13 | §13 | Single writer, cap 33, completion review | §10 | [x] |
| 14 | §14 | Completion evidence hardening | §13 | [x] |
| 15 | §15 | CI watch and red-run repair | §13 | [x] |
| 16 | §16 | Completion evidence adoption boundary | §14 | [x] |
| 17 | §17 | CI push reconciliation | §15 | [x] |
| 18 | §18 | CI recovery budget | §15 | [x] |
| 19 | §19 | CI gate checks | §15, §17, §18 | [x] |
| 20 | §20 | CI reconciliation at scale | §17 | [x] |
| 21 | §21 | CI recovery closed on resume | §17, §18 | [x] |
| 22 | §22 | CI reconciliation past limits | §20 | [x] |
| 23 | §23 | CI reconciliation after deleted runs | §22 | [x] |
| 24 | §24 | Resumable newest-page refresh | §23 | [x] |
| 25 | §25 | Host lock baseline across policy writes | §12 | [x] |
| 26 | §26 | Host check names every file it writes | §25 | [x] |
| 27 | §27 | Review prompt builder | -- | [x] |
| 28 | §28 | Host check scratch leftover rule | §26 | [x] |
| 29 | §29 | Review prompt empty-input refusals | §27 | [x] |
| 30 | §31 | Plan lists files still to author | -- | [x] |
| 31 | §32 | Validate checks plan row width | -- | [x] |
| 32 | §33 | Plan groups a phase by domain | §31, §32 | [x] |
| 33 | §35 | Weekly owner digest | §1 | [x] |
| 34 | §36 | Operating mode measurement command | -- | [x] |
| 35 | §37 | Operating mode rule and launcher | §36 | [x] |
| 36 | §38 | Parallel streams design record | §37 | [ ] |
| 37 | §39 | Parallel streams sections authored | §38 | [ ] |
| 38 | §50 | Withdrawn sections | -- | [x] |
| 39 | §53 | Automation notices go in the weekly digest | §35 | [ ] |
| 40 | §54 | One process-tree containment for every tool | §36 | [x] |
| 41 | §55 | Scheduled tasks run in the shared process tree | §54 | [x] |
| 42 | §56 | Digest delivery when no evidence remains | -- | [ ] |
| 43 | §57 | Completion reviews leave the Commit item to the stamp | -- | [x] |
| 44 | §58 | The plan lists sections, never TODO files | -- | [x] |
| 45 | §59 | A parked section is neither ready nor in progress | -- | [ ] |

## 1. Automation Runner, Alert and Installer

> **Started:** 2026-10-20T00:24:39Z

The shared plumbing every scheduled job uses: the task list, a runner that logs each run and alerts on failure, the alert sender, and the installer that keeps Task Scheduler in step with the list. Ported from Isotone with names and paths changed and Isotone's own tasks left out.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Port `run.py`, `alert.py`, `install.ps1` and `README.md` into `.conclave/automations/` with Office names. Done when: `python .conclave/automations/alert.py --help` runs and `python .conclave/automations/run.py <unknown task>` exits 2 naming it. **Corrected 2026-10-20:** said `run.py --help`; the ported runner takes only a task name.
2. Port `scripts/tests/test_automations.py`. Done when: it passes against an Office `tasks.json`.

- [x] Copy `run.py` from Isotone to `.conclave/automations/run.py`, changing the log root to `build/automations/<name>/` under this repository and every Isotone name to Office. Done when: `python .conclave/automations/run.py <fixture task>` writes a log and `last.json` under `build/automations/`. Cheaper substitute: invoking scripts straight from Task Scheduler with no log or outcome file.
- [x] Copy `alert.py` to `.conclave/automations/alert.py` with the subject prefix `Office` and the same SMTP2GO sender, recipient and vault item. Done when: `python .conclave/automations/alert.py <task> --dry-run` prints the message without sending and without reading the key. Cheaper substitute: an API key in a file or environment variable.
- [x] Copy `install.ps1` to `.conclave/automations/install.ps1` registering under `\Office\` and removing tasks the list no longer names. Done when: `install.ps1 -DryRun` lists the tasks it would register and remove, changing nothing. Cheaper substitute: tasks created by hand in Task Scheduler.
- [x] Write `.conclave/automations/tasks.json` with schema version 1, folder `\Office\`, and no Isotone task. Done when: it parses and the test in this section reads it. Cheaper substitute: copying Isotone's tasks, which call scripts this repository does not have.
- [x] Write `.conclave/automations/README.md` from Isotone's, describing only Office tasks. Done when: `python scripts/check-design-doc.py .conclave/automations/README.md --require "What runs" --require "When a run fails"` exits 0. Cheaper substitute: linking to Isotone's README.
- [x] Port `scripts/tests/test_automations.py` with Office names. Done when: `python -m unittest discover -s scripts/tests -p "test_automations.py"` passes and fails when a README table row and `tasks.json` disagree.
- [x] Commit: `automations: add runner, failure alert and installer`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_automations.py"` passes, and `python .conclave/automations/alert.py --help` exits 0.

> **Verified:** 2026-10-20 | §1 | 9311a2ee357b54860fbbd8e8738c3c354781c777
> **Review:** `docs/reviews/d00-t03-s1.json`

## 2. Run Guard and Stop Hook

> **Started:** 2026-10-20T00:40:34Z

The guard file `build/claude-campaign-guard.json` names the session that owns an open run, its phase, run file and heartbeat job. The Stop hook reads it and blocks that session's end of turn while the run is open, with a stall breaker. Ported from Isotone, with the ready count read from this repository's JSON `query ready` output.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Port `scripts/campaign_guard.py` and adapt its ready count. Done when: `python scripts/campaign_guard.py --self-test` passes.
2. Port `.claude/hooks/campaign-stop.ps1` and wire it in `.claude/settings.json`. Done when: the guard's self-test drives the hook and passes.

- [x] Copy `campaign_guard.py` from Isotone to `scripts/campaign_guard.py`, renaming every Isotone mention to Office. Done when: `rg -n -i isotone scripts/campaign_guard.py` returns nothing. Cheaper substitute: a hand-written guard without the lock, generations and pending-cancel record.
- [x] Replace `_ready_count` in `scripts/campaign_guard.py` with a reader of the JSON list `todo-graph.py query ready` prints, counting its entries. Done when: a fixture `todo-graph.py` printing a two-entry list reads as 2, and invalid output reads as unknown. Cheaper substitute: keeping the `N runnable now` regex, which never matches here, so plan-done could never be proven.
- [x] Update the self-test's fixture `todo-graph.py` writer to print a JSON list of the controlled length. Done when: `python scripts/campaign_guard.py --self-test` passes every case except the 13 `skill-*` cases. **Corrected 2026-10-20:** the self-test also reads the real `process-plan` skill for the guard steps, which land in §4; those cases pass there. Cheaper substitute: skipping the self-test cases that need a ready count.
- [x] Copy `campaign-stop.ps1` to `.claude/hooks/campaign-stop.ps1`, reading the next ready ref from the JSON list. Done when: the self-test's hook cases pass. Cheaper substitute: a Stop hook that always blocks, which traps every session.
- [x] Create `.claude/settings.json` with the Stop hook entry, using the same `CLAUDE_PROJECT_DIR` launch line as Isotone. Done when: the file parses and names `campaign-stop.ps1`. Cheaper substitute: wiring the hook in user-level settings, which would fire in every repository.
- [x] Add `scripts/tests/test_campaign_guard.py` that runs `python scripts/campaign_guard.py --self-test` and fails on any failed case other than the `skill-*` cases until §4 (`SKILL_TEXT_CASES_PENDING`). Done when: `python -m unittest discover -s scripts/tests` includes it and it fails when a non-skill case fails.
- [x] Commit: `automations: add campaign run guard and Stop hook`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_campaign_guard.py"` passes, with `python scripts/campaign_guard.py --self-test` failing only its 13 `skill-*` cases (**Corrected 2026-10-20:** said the self-test exits 0; that is §4's checkpoint).

> **Verified:** 2026-10-20 | §2 | b10277a6db91c37d4f78db3d7b32c8c4567d2905
> **Review:** `docs/reviews/d00-t03-s2.json`

## 3. Keep-Alive Task and Session Observer

> **Started:** 2026-10-20T01:08:32Z

When the owning session's process is gone and no other Office session is open, the keep-alive resumes that exact session headless and supervises it. The SessionStart hook records each session's process so death can be proven, never guessed. **Retired 2026-10-21 (operator):** the keep-alive, its observer and its task were removed when Office adopted the Conclave-SDK todo kit's run guard; see Current state.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Port `scripts/campaign_keepalive.py` with the writer model read from `.conclave/keepalive.toml`. Done when: `python scripts/campaign_keepalive.py --self-test` passes.
2. Wire the SessionStart hook and the task. Done when: `.claude/settings.json` names `campaign_keepalive.py observe` and `tasks.json` lists `office-claude-keepalive`.

- [x] Copy `campaign_keepalive.py` to `scripts/campaign_keepalive.py`, renaming Isotone to Office in the prompt, messages and task name. Done when: `rg -n -i isotone scripts/campaign_keepalive.py` returns nothing. Cheaper substitute: a resume script that relaunches whenever no window is open, without proving the owner gone.
- [x] Write `.conclave/keepalive.toml` with `[writer] model = "claude-opus-5-5"` and change `writer_model()` to read it. Done when: the self-test's fixture reads the model from `keepalive.toml`, and a missing file makes `resurrect` refuse with a setup message before counting a resume (**Corrected 2026-10-20:** said `status`; only a launch reads the model). Cheaper substitute: hard-coding the model in the script.
- [x] Add the SessionStart hook to `.claude/settings.json` running `campaign_keepalive.py observe`. Done when: starting a new Claude session writes `build/claude-sessions/<session>.json`. Cheaper substitute: observing only when a run starts, which cannot prove an older session gone.
- [x] Add `office-claude-keepalive` to `.conclave/automations/tasks.json` (3 minutes after logon, then hourly, timeout 245 minutes) and its row to the README table. Done when: `test_automations.py` passes with the new task. Cheaper substitute: a task the README does not describe.
- [x] Add `scripts/tests/test_campaign_keepalive.py` running `--self-test`. Done when: it fails when the self-test fails.
- [x] Commit: `automations: add campaign keep-alive and session observer`

**Test checkpoint:** `python scripts/campaign_keepalive.py --self-test` exits 0, and `python -m unittest discover -s scripts/tests -p "test_campaign_keepalive.py"` passes.

> **Verified:** 2026-10-20 | §3 | 081daed7eb99383e0f4175fef13c2315ba624e57
> **Review:** `docs/reviews/d00-t03-s3.json`

## 4. Run Skills Create and Check the Guard

> **Started:** 2026-10-20T01:32:06Z

`process-plan` and `process-phase` gain the run-guard steps from Isotone: reconcile and create the heartbeat with its canonical prompt, acquire the guard, observe the session, check heartbeat health and expiry at each section boundary, and end the run through `campaign_guard.py end`. Skills live in three mirrored directories and change together (AGENTS.md).

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Port the guard sections of Isotone's `process-plan` and `process-phase` into `.claude/skills/`, then mirror them. Done when: the three copies of each skill are identical apart from agent-specific tool names.

- [x] Add the run-guard section (reconcile, mint a generation, `CronCreate` with the canonical heartbeat prompt, `acquire`, `observe`) to `.claude/skills/process-plan/SKILL.md`, adapted to Office names. Done when: the canonical prompt names `Office` and `campaign_guard.py`. Cheaper substitute: a heartbeat with no guard, which cannot tell its owner from a stale job.
- [x] Add the section-boundary heartbeat check and the guard-aware stop and park rules to `.claude/skills/process-phase/SKILL.md`. Done when: the skill names `health`, `expiry` and `end --reason`. Cheaper substitute: deleting the guard file by hand at a stop.
- [x] Set `SKILL_TEXT_CASES_PENDING = False` in `scripts/tests/test_campaign_guard.py` so the guard self-test must exit 0. Done when: the test fails if any `skill-*` case fails. Cheaper substitute: leaving the staging flag on.
- [x] Mirror both skills to `.agents/skills/` and `.codex/skills/` as real files. Done when: the Claude copies carry the full guard text and the `.agents` and `.codex` copies carry the agent-specific rule that a guard means a Claude session owns the tree (the guard, Stop hook and heartbeat are Claude Code features). **Corrected 2026-10-20:** said the copies differ only in agent-specific wording; the guard itself is Claude-only. Cheaper substitute: symlinks, which AGENTS.md forbids.
- [x] Add the operator rule from the phase 2 run (a go-ahead before every live Office capture, recorded as `- waiting:` and `- go-ahead:` lines that the heartbeat honours) to the canonical prompt. Done when: the prompt names both line forms, and a go-ahead answers only the wait it names. **Corrected 2026-10-20:** the operator's own standing go-ahead ("run captures unattended", recorded in the phase 2 run file) is honoured when recorded as a `- go-ahead:` line naming that work; a wait is a park of the whole run (`PARKED ... waiting:`) so the Stop hook and the keep-alive never resume past it. Cheaper substitute: relying on memory of the rule across sessions.
- [x] Commit: `skills: run plan and phase under the campaign guard`

**Test checkpoint:** `python scripts/campaign_guard.py --self-test` exits 0 after the skill change, and `rg -c "campaign_guard.py" .claude/skills/process-plan/SKILL.md .agents/skills/process-plan/SKILL.md .codex/skills/process-plan/SKILL.md` prints a non-zero count for each file.

> **Verified:** 2026-10-20 | §4 | c919592d7309639e9d373eb7633d17994c2c4f60
> **Review:** `docs/reviews/d00-t03-s4.json`

## 5. Install the Tasks and Verify on This PC

> **Started:** 2026-10-20T01:18:15Z

Registers the tasks in Task Scheduler on the operator's Windows host and proves each piece live: the task exists with the right triggers, the keep-alive's `status` answers, and the alert renders. A real alert email is sent once, only with the operator's go-ahead.

**Phase:** 0
**Needs:** windows-host, attended
**Surface:** no

**Build order:**

1. Run `pwsh .conclave/automations/install.ps1`. Done when: `Get-ScheduledTask -TaskPath '\Office\'` lists every task in `tasks.json`.
2. Verify each task and the alert. Done when: the findings below are recorded in `.conclave/automations/README.md` under `## Install and inspect`.

- [x] Run `pwsh .conclave/automations/install.ps1` and read back `Get-ScheduledTask -TaskPath '\Office\' | Get-ScheduledTaskInfo`. Done when: `office-claude-keepalive` shows its next run time. Cheaper substitute: assuming the installer worked.
- [x] Run `python scripts/campaign_keepalive.py status` with no run open. Done when: it prints `idle: no open campaign run`. **Corrected 2026-10-20:** also asked for `hold` with a run open; no run is under the guard until §6, whose checkpoint already proves `hold`. Cheaper substitute: reading the code instead of running it.
- [x] Run `python .conclave/automations/alert.py office-claude-keepalive --dry-run`. Done when: the rendered alert names the task, its exit and the log tail. Cheaper substitute: none; the dry run sends nothing.
- [x] With the operator's go-ahead, send one real alert by running `python .conclave/automations/run.py` on a fixture task that exits 1. Done when: the email is in the operator's inbox (checked through the Gmail connector) and the runner records each send in `last.json`, proven by `AlertRecord` in `test_automations.py`. **Corrected 2026-10-20:** said the operator confirms arrival (the operator was offline; the inbox check is direct evidence); the live send predates the `last.json` alert record, which this section added to `run.py`. Cheaper substitute: declaring the alert path working from the dry run alone.
- [x] Commit: `automations: record install and live verification`

**Test checkpoint:** `Get-ScheduledTask -TaskPath '\Office\' | Select-Object -ExpandProperty TaskName` lists `office-claude-keepalive`, and `python scripts/campaign_keepalive.py status` exits 0.

> **Verified:** 2026-10-20 | §5 | e602dc70fb77384f825e7bb029218428e1c880e4
> **Review:** `docs/reviews/d00-t03-s5.json`

## 6. Adopt the Guard for the Open Phase 2 Run

> **Started:** 2026-10-20T02:06:37Z

The phase 2 run was opened before the guard existed. This section moves it under the guard: acquire with this session, replace the interim heartbeat with the canonical one, and record the ids in the run file.

**Phase:** 0
**Needs:** attended
**Surface:** no

**Build order:**

1. Acquire the guard for `docs/phase-runs/2026-10-20-phase-2.md`. Done when: `build/claude-campaign-guard.json` names this session, phase 2 and the run file.
2. Replace the interim heartbeat. Done when: `CronList` shows only the canonical job and the guard names its id.

- [x] Run `python scripts/campaign_guard.py acquire` with this session id, phase 2, the run file and a fresh generation. Done when: `python scripts/campaign_guard.py whoami --session <id>` prints that this session owns the run. Cheaper substitute: writing the guard file by hand.
- [x] Reconcile, then `CronDelete` the interim heartbeat as `reconcile` directs and `CronCreate` the canonical one from `process-plan`, then acquire the guard with its id. **Corrected 2026-10-20:** said delete, create, then re-point; the guard did not exist yet, so `reconcile` names the interim job an orphan and the guard is created with the new job's id. Done when: `python scripts/campaign_guard.py health --session <id> --jobs <id>` reports healthy. Cheaper substitute: keeping the interim prompt, which the guard cannot verify.
- [x] Record the guard's run id and the heartbeat job id under Critical events in the run file. Done when: both ids appear with a UTC time. Cheaper substitute: ids only in chat.
- [x] Commit: `todo: put the phase 2 run under the campaign guard`

**Test checkpoint:** `python scripts/campaign_guard.py whoami --session <this session id>` prints the owner line, and `python scripts/campaign_keepalive.py status` prints `hold`.

> **Verified:** 2026-10-20 | §6 | 4bac442d4ea5ecbbeefe4a5687777c2ce739c845
> **Review:** `docs/reviews/d00-t03-s6.json`

## 7. Run Guard Robustness Fixes

> **Started:** 2026-10-21T21:05:00Z

Three defects the owner reported on 2026-10-21, found by independent review in a sibling repository and present in Office's guard (`scripts/campaign_guard.py`), each verified here: `fingerprint` calls `os.stat` (following symlinks) on every untracked path and `open()` on any of the first 500, so a FIFO or device in the working tree blocks the Stop hook and a symlink to a directory raises; `acquire` defaults `--phase` to `0`, so a re-point of the owner's own guard (the heartbeat repair at a section boundary) silently resets the run to phase 0; `end` records the pending cancellation, then deletes the guard, so an end interrupted between the two leaves a guard `whoami` still reports as OWNER, and the heartbeat resumes a run that was stopped.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write a failing test for each defect in `scripts/tests/test_campaign_guard.py`. Done when: each fails on the current guard.
2. Fix each at its owning function. Done when: the tests pass and the full guard suite stays green.

- [x] Make `fingerprint` in `scripts/campaign_guard.py` read each untracked path with `os.lstat`, hash only regular files, record a symlink by its target text and any other entry by its type, and make no filesystem call for a path past both bounds. Done when: a test with a FIFO (POSIX) or a stub `os.lstat` reporting a character device, and a symlink to a directory, returns a fingerprint without opening either. Cheaper substitute: catching the exception after the hook has already blocked.
- [x] Make `--phase` optional in `scripts/campaign_guard.py` `acquire`: a fresh guard requires it, and a re-point of the owner's own guard without it keeps the guard's phase. Done when: a test re-pointing with a new `--cron-id` and no `--phase` keeps phase 2, and a fresh `acquire` without `--phase` is refused. Cheaper substitute: documenting that every re-point must repeat `--phase`.
- [x] Mark the guard ended before deleting it in `scripts/campaign_guard.py` `_end_locked`: write `ended` (reason and time) into the guard atomically with the pending cancellation, and make `whoami`, `stop-hook` and `acquire` treat an ended guard as over and finish its deletion. Done when: a test that stops `end` after the pending record is written sees `whoami` print `NO GUARD`, the Stop hook let the turn end, and a later `acquire` start a fresh run. Cheaper substitute: retrying the delete in a loop.
- [x] Record each defect, its test and the fix in `docs/reviews/00-workspace/D00-T03-s7.md` with the failing-before and passing-after outputs. Done when: three entries quote both results. Cheaper substitute: one summary line.
- [x] Commit: `guard: fix device and symlink stalls, phase resets on re-point, and interrupted ends`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_campaign_guard.py"` passes, and its three new tests fail when the previous `scripts/campaign_guard.py` is restored.

> **Verified:** 2026-10-21 | §7 | 2d237eefa1258b8655dc3b0fb6f8249825f5e5d9
> **Review:** `docs/reviews/d00-t03-s7.json`

## 8. Agent Tier Verifier YAML Strictness

> **Started:** 2026-10-21T22:05:00Z

`scripts/verify-agent-tiers.mjs` reads agent frontmatter as a closed subset of YAML, but the owner reported on 2026-10-21 that it accepts a line Claude Code cannot load, so an agent passes the check and then fails to load. The file is Office's own (the Conclave SDK link was cut on 2026-10-21), so the fix lands here. The usual case is a plain scalar YAML refuses, such as a value containing `: ` or ` #`, or opening with an indicator character.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Find every frontmatter line the verifier accepts and a YAML 1.2 loader refuses. Done when: the cases are listed with the loader's error.
2. Refuse those lines in the verifier with fixtures. Done when: each case fails the verifier and every agent in `.claude/agents/` still passes.

- [x] List the frontmatter lines `scripts/verify-agent-tiers.mjs` accepts but a YAML 1.2 loader refuses (a plain scalar containing `: ` or ` #`, opening with an indicator character such as `@`, `` ` ``, `%`, `[`, `{`, `|`, `>`, `!`, `&`, `*`, or holding a tab), checked against a real loader. Done when: `docs/reviews/00-workspace/D00-T03-s8.md` lists each case with the loader's error. Cheaper substitute: guessing the cases without a loader.
- [x] Refuse each listed case in `scripts/verify-agent-tiers.mjs` with a message naming the line and the rule. Done when: a fixture agent for each case fails the verifier. Cheaper substitute: refusing only the reported case.
- [x] Add the fixtures and a test runner for them in `scripts/tests/test_verify_agent_tiers.py`, invoking `node scripts/verify-agent-tiers.mjs` on fixture directories. Done when: the suite passes, and fails when the new refusals are removed. Cheaper substitute: checking the repository's own agents only.
- [x] Commit: `tooling: refuse agent frontmatter Claude Code cannot load`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_verify_agent_tiers.py"` passes and `node scripts/verify-agent-tiers.mjs` reports every agent in `.claude/agents/` valid.

> **Verified:** 2026-10-22 | §8 | c6f40d6ca6c7e56635cedd257a4c41896a5c708f
> **Review:** `docs/reviews/d00-t03-s8.json`

## 9. Dependency PR Merges at Boundaries

> **Started:** 2026-10-22T00:35:00Z

Owner request 2026-10-21 (replacing "nothing merges by itself" for dependency pull requests): merge green dependency pull requests inside the campaign loop at section boundaries, the one moment the clone matches GitHub, with a scheduled fallback when no campaign runs. Office has no pull request source yet, so this adds Dependabot for GitHub Actions only; NuGet pins stay with the local proposal tasks, because the WinUI 3 pin follows `winui3/release` builds, which Dependabot cannot express. Local proposal branches (`winui/*`, `dotnet/*`, `pins/*`) still wait for the owner's merge.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `scripts/merge_prs.py` with its safety checks and tests. Done when: it merges an eligible fixture pull request and refuses every unsafe state.
2. Wire it into `process-plan` and the automations. Done when: the skill runs it after each stamp push and the task is installed.

- [x] Add `.github/dependabot.yml` for the `github-actions` ecosystem, weekly, labelled `dependencies`. Done when: the file validates and GitHub lists the Dependabot configuration. Cheaper substitute: bumping action majors by hand.
- [x] Write `scripts/merge_prs.py` refusing to run unless the working tree is clean, `HEAD` equals `origin/main` after a fetch, and no open section carries a `Started:` line. Done when: a test of each state exits non-zero naming it. Cheaper substitute: merging from a dirty or unpushed clone.
- [x] Select eligible pull requests in `scripts/merge_prs.py`: author `dependabot[bot]` or `github-actions[bot]`, a `dependencies` or `pins` label, every check green, mergeable and clean, and no change to `global.json` (the .NET SDK pin moves only through its own proposal). Done when: a test over fixture `gh pr list` JSON selects exactly the eligible ones. Cheaper substitute: merging every Dependabot pull request.
- [x] Merge one pull request at a time in `scripts/merge_prs.py` with `gh pr merge --rebase --match-head-commit <sha>`, then `git pull --ff-only`, then `python scripts/todo-graph.py validate`, stopping at the first failure and leaving the rest open; each merge re-reads the pull request and the clone under the run guard's lock first. **Corrected 2026-10-22:** said it leaves "that pull request" open, which a failure after the merge cannot do, and judged each pull request only from the listing. Done when: a test with a failing merge or validate leaves the later pull requests unmerged and exits 1. Cheaper substitute: merging all and validating once at the end.
- [x] Refuse to run while a campaign is open in `scripts/merge_prs.py` unless `--session` names the guard's own session (`build/claude-campaign-guard.json`). Done when: a test with a guard owned by another session exits non-zero (zero with `--skip-unsafe`, the scheduled task's flag, so an unsafe moment never alerts), and one with `--session <owner>` runs. **Corrected 2026-10-22:** added `--skip-unsafe`; without it the scheduled task would email a failure every morning of a campaign. Cheaper substitute: checking for a lock file of another tool.
- [x] Write `scripts/tests/test_merge_prs.py` covering the safety states, eligibility, the merge sequence and the campaign check with fake `git` and `gh`. Done when: the suite passes and fails when any one safety check is removed. Cheaper substitute: a dry run against the live repository only.
- [x] Add the run after each stamp push to `process-plan` in `.claude/skills/`, `.agents/skills/` and `.codex/skills/`, before the next row is claimed, with a failure recorded in the run file and the campaign continuing. Done when: all three mirrors name `python scripts/merge_prs.py` at the section boundary, with `--session <id>` where the agent holds the run guard (Claude). **Corrected 2026-10-22:** required `--session` in every mirror; the Antigravity and Codex mirrors hold no run guard, so they call it without one and it defers to an open Claude campaign. Cheaper substitute: merging only when the operator asks.
- [x] Add an `office-pr-merge` task to `.conclave/automations/tasks.json`, with its README row and line, and install it. Done when: `test_automations.py` passes and `Get-ScheduledTask -TaskPath '\Office\'` lists it. Cheaper substitute: no fallback when no campaign runs.
- [x] Update `.conclave/automations/README.md` and `AGENTS.md` with the merge rule: green dependency pull requests merge by themselves at section boundaries or on the schedule; local proposal branches still wait for the owner. Done when: both state it and no line says dependency pull requests wait for a manual merge. Cheaper substitute: the rule only in the script's docstring.
- [x] Commit: `automations: merge green dependency pull requests at section boundaries`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_merge_prs.py"` passes, `python scripts/merge_prs.py --session <this session>` refuses while this section is in progress, naming it, and the first run after its stamp exits 0 reporting what it merged or that nothing was eligible (recorded in the run file). **Corrected 2026-10-22:** asked for an exit 0 "at a section boundary" before the stamp, which the in-progress rule this section adds makes impossible; the boundary run moves to just after the stamp.

> **Verified:** 2026-10-22 | §9 | a89d8abf44813692c3b08c6955c20957f025c96d
> **Review:** `docs/reviews/d00-t03-s9.json`

## 10. Retire the .NET and WinUI 3 Pins

Owner decision 2026-10-22 (D03 T01 §2): the suite moves from WinUI 3 in C# on .NET 11 to native C++ with its own GUI toolkit, so the WinUI 3, .NET SDK and NuGet pin tooling built on 2026-10-20 and 2026-10-21 guards pins that no longer exist, and its daily tasks keep proposing releases nobody will merge. This section removes that tooling and the .NET assumptions in the shared scripts; the C++ toolchain pins that replace it are §11.

**Phase:** 0
**Needs:** windows-host, attended
**Surface:** no

**Build order:**

1. Remove the retired tasks, scripts, tests and pin files, and the .NET assumptions in the scripts that stay. Done when: `python -m unittest discover -s scripts/tests` passes without them.
2. Unregister the retired tasks on this PC and clear the retired proposal branches. Done when: `Get-ScheduledTask -TaskPath '\Office\'` lists exactly the tasks in `tasks.json`.

- [x] Remove `office-winui-pin`, `office-dotnet-pin`, `office-nuget-pins`, `office-vulnerable-packages` and `office-dotnet-local` from `.conclave/automations/tasks.json`, with their rows, lines and the WinUI 3 and .NET 11 pin sections in `.conclave/automations/README.md`. Done when: `python -m unittest discover -s scripts/tests -p "test_automations.py"` passes, `tasks.json` names no retired task, and the README names them only in its dated `## Retired pins` record and read-back history. Cheaper substitute: disabling the tasks, which the next install re-enables. **Corrected 2026-10-23:** said neither file names a retired task, which the README's dated records must.
- [x] Delete `scripts/check-winui-pin.py`, `scripts/check-dotnet-pin.py`, `scripts/check-nuget-pins.py`, `scripts/check-vulnerable-packages.py`, `scripts/lib/package_versions.py`, their tests, `Directory.Packages.props` and `global.json`, first moving the `pin_proposal.propose` tests that lived in `scripts/tests/test_check_winui_pin.py` to a neutral `Proposal` fixture in `scripts/tests/test_pin_automations.py`. Done when: the files are gone and `python -m unittest discover -s scripts/tests` passes. **Corrected 2026-10-22:** did not say the WinUI 3 test file held the only tests of the shared `propose`, which §11 reuses. Cheaper substitute: leaving the scripts in place unscheduled, where a later session runs them and pins .NET again.
- [x] Remove the `dotnet build` step from `scripts/lib/pin_proposal.py` and its tests. Done when: no `dotnet` call remains and `python -m unittest discover -s scripts/tests -p "test_pin_automations.py"` passes. Cheaper substitute: a step that finds no solution and passes without building anything.
- [x] Point the pin-file refusal in `scripts/merge_prs.py` (`PIN_FILES`) at the C++ toolchain pin files (`vcpkg.json`, `vcpkg-configuration.json`, `CMakePresets.json`) in place of `global.json`, keeping its page-by-page file read and rename handling and matching names in any case, with its tests. Done when: `python -m unittest discover -s scripts/tests -p "test_merge_prs.py"` passes, a late, renamed or differently cased pin file is refused, and the script no longer names `global.json`. Cheaper substitute: deleting the refusal, which leaves the file paging dead and the C++ pins unguarded until §11. **Corrected 2026-10-22:** removed the refusal and left the C++ pin files to §11.
- [x] Replace `.cs` and `.xaml` in `scripts/check-spdx.py` with the C++ sources (`.cpp`, `.cppm`, `.ixx`, `.h`, `.hpp`, `.rc`, `.hlsl`, `.manifest`) and the CMake files (`CMakeLists.txt`, `.cmake`), and update the header instructions in `CONTRIBUTING.md` to match. Done when: a fixture of each new kind (and `CMakeLists.txt` in any case) fails without its header and passes with it in `scripts/tests/test_check_spdx.py`. Cheaper substitute: adding the C++ kinds when the first file lands, by which point unheaded files exist. **Corrected 2026-10-22:** listed `.cpp`, `.h`, `.hpp`, `.ixx` and `.rc` only; module units, shaders and app manifests are sources too.
- [x] Rewrite the reason in `scripts/check-visual-studio.py` from .NET 11 to the C++ toolchain: the newest stable Visual Studio 2026 carries the MSVC toolset the C++ standard pin needs. Done when: no docstring or message names .NET and its tests pass. Cheaper substitute: keeping a reason that no longer holds.
- [x] Update the merge rule in `AGENTS.md` and the `process-plan` mirrors in `.claude/skills/`, `.agents/skills/` and `.codex/skills/` (drop the `winui/*` and `dotnet/*` branches and the `global.json` exclusion), and the comment in `.github/dependabot.yml`. Done when: `git grep -n -i -E "winui|dotnet|nuget|Directory\.Packages|global\.json" -- AGENTS.md CONTRIBUTING.md scripts .github .claude .agents .codex .conclave/automations/tasks.json ".conclave/automations/*.py" ".conclave/automations/*.ps1"` prints nothing. Cheaper substitute: instructions that point at deleted files. The automations README names the retired tasks only in its dated `## Retired pins` record and its read-back history. **Corrected 2026-10-23:** the grep covered all of `.conclave/`, whose README keeps those records.
- [x] Run `pwsh .conclave/automations/install.ps1` on this PC, which unregisters every `\Office\` task `tasks.json` no longer lists. Done when: `Get-ScheduledTask -TaskPath '\Office\'` lists exactly the tasks in `tasks.json`. Cheaper substitute: leaving the retired tasks to fail every morning once their scripts are gone.
- [x] List the local `winui/*` and `dotnet/*` proposal branches and the `refs/office-pin/winui-*` and `refs/office-pin/dotnet-*` markers, and delete them (owner instruction 2026-10-22: "clean out all the C# and WinUI3 stuff"). Done when: `git branch --list "winui/*" "dotnet/*"` and `git for-each-ref refs/office-pin/` print no WinUI 3 or .NET entry. Cheaper substitute: leaving proposals that look ready to merge.
- [x] Commit: `automations: retire the .NET and WinUI 3 pins`

**Test checkpoint:** `python -m unittest discover -s scripts/tests` passes, `python scripts/check-spdx.py` exits 0 and `git grep -n -i -E "winui|dotnet|nuget|Directory\.Packages|global\.json" -- AGENTS.md CONTRIBUTING.md scripts .github .claude .agents .codex .conclave/automations/tasks.json ".conclave/automations/*.py" ".conclave/automations/*.ps1"` prints nothing. **Corrected 2026-10-23:** the grep covered all of `.conclave/`, including the README's dated records.

> **Verified:** 2026-10-23 | §10 | f8cc83c6ec870fdd1fe92bcb25408299e8f3c9b3
> **Review:** `docs/reviews/d00-t03-s10.json`

## 11. C++ Toolchain Pins

The owner's pin rule (2026-10-20 for WinUI 3, 2026-10-21 for .NET and NuGet) carries over to the native C++ stack decided on 2026-10-22 (D03 T01 §2): every toolchain pin is the newest stable release, proposed on a branch by a daily task and merged by the owner. The pins are the C++ standard flag (C++23 through `/std:c++23preview` today, moving to a stable C++23 flag and then to C++26 as MSVC ships them), the MSVC toolset (through Visual Studio, already watched by `office-visual-studio`), the Windows SDK, CMake and the vcpkg baseline, held in the files the foundation plan's Toolchain section names (D03 T01 §12). **Groomed 2026-10-23:** those files (`CMakePresets.json`, `vcpkg.json`, `vcpkg-configuration.json`) are created by the first section of `todo/04-platform/TODO-01-build-foundation.md`, which D03 T01 §17 authors and adds to this section's `Depends On`, so the section moved from Phase 3 to Phase 4.

**Phase:** 4
**Needs:** none
**Surface:** no

**Build order:**

1. Add one latest-stable check per pin, each with a fixture test and a daily task. Done when: every pin the Toolchain section names has a check that fails on an older fixture.

- [ ] Add `scripts/check-cpp-standard.py`, which compiles a probe with the newest installed stable MSVC and exits 1 when it accepts a stable flag newer than the pinned one (`/std:c++23` while `/std:c++23preview` is pinned, then `/std:c++26`), with an `office-cpp-standard` task that emails the operator once per new flag. Done when: a fake compiler accepting `/std:c++26` fails, the installed toolset passes, and `test_automations.py` passes. Cheaper substitute: watching the MSVC release notes by hand.
- [ ] Add `scripts/check-vcpkg-baseline.py`, which compares the `builtin-baseline` in `vcpkg.json` with the newest vcpkg release tag and proposes a newer one on a `pins/vcpkg-<tag>` branch through `scripts/lib/pin_proposal.py`, building the CMake preset in the proposal worktree, with an `office-vcpkg-baseline` task. Done when: a fixture on an older baseline proposes a branch, the current baseline passes, and `test_automations.py` passes. Cheaper substitute: bumping the baseline by hand when a port is missing.
- [ ] Add latest-stable checks for the Windows SDK and CMake versions the Toolchain section pins, in a new script or in `scripts/check-visual-studio.py`. Done when: an older pinned fixture fails and the current pin passes for each. Cheaper substitute: building with whatever SDK and CMake the machine has.
- [ ] Refuse in `scripts/merge_prs.py` any pull request that changes a toolchain pin file (`vcpkg.json`, `CMakePresets.json` or the files the Toolchain section names), since those move only through their own proposals. Done when: a test with such a pull request, including a rename away from the file, refuses it. Cheaper substitute: letting Dependabot move a pin past the proposal checks. Already shipped: `scripts/merge_prs.py` `PIN_FILES` (D00 T03 §10); add any further pin file the Toolchain section names.
- [ ] Commit: `automations: add the C++ toolchain pins`

**Test checkpoint:** `python -m unittest discover -s scripts/tests` passes and `python scripts/check-cpp-standard.py` exits 0 on this host.

## 12. Campaign Host Readiness Check

> **Started:** 2026-10-23T05:47:00Z

Owner decision 2026-10-22 (`docs/specs/2026-10-23-campaign-scope-design.md`, decisions 1, 2 and 15): the campaign runs unattended on this PC for days to months, resumed by hand when it stops. A run that meets a locked screen, a sleeping PC, a missing Office app or a missing compiler should park with a reason the owner reads on return, not fail mid-section. This section adds one read-only check the campaign runs before it starts and at every phase start.

**Phase:** 0
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Write `scripts/check-campaign-host.py` with one check per requirement and a test per check. Done when: each check has a passing and a failing fixture.
2. Wire it into `process-plan` and `process-phase`. Done when: both skills run it and park on a failure. **Corrected 2026-10-23:** said all three skill mirrors; `.claude/skills/` is the only copy since D00 T03 §13.

- [x] Check the interactive session in `scripts/check-campaign-host.py`: a console session is active and unlocked (`WTSQuerySessionInformationW` with `WTSSessionInfoEx`). Done when: a fake locked session fails naming "screen locked" and an unlocked one passes, and a console showing another user's session (Fast User Switching) fails. Cheaper substitute: assuming the screen is unlocked because the session exists. **Corrected 2026-10-23 (review round 14):** did not require the console session to be the campaign's own (`ProcessIdToSessionId`).
- [x] Check the power settings: sleep and hibernate after `0` (never) on AC for the active scheme (`PowerGetActiveScheme` and `PowerReadACValueIndex` for `STANDBYIDLE` and `HIBERNATEIDLE` in `SUB_SLEEP`), and no screen lock timeout (no secure screen saver as the live session runs it, read through `SystemParametersInfoW` `SPI_GETSCREENSAVEACTIVE`, `SPI_GETSCREENSAVESECURE` and `SPI_GETSCREENSAVETIMEOUT`, with `SCRNSAVE.EXE` from `HKCU\Control Panel\Desktop`, and no `InactivityTimeoutSecs` machine policy), each screen saver value read from `HKCU\Software\Policies\Microsoft\Windows\Control Panel\Desktop` first when the policy sets it. **Corrected 2026-10-23 (review round 11):** read `ScreenSaveActive` and `ScreenSaverIsSecure` from the stored profile, which a temporary setting in the live session can differ from. **Corrected 2026-10-23 (review rounds 15 and 16):** a saver program that does not exist never runs (a forced one that does not exist is ignored, so the user's own saver is checked), and since the inactivity limit is read when Windows starts, a change to its policy key (or a deleted ancestor key) after the last start fails asking for a restart; whether a write stamp falls after the start is decided by replaying the clock since boot (this boot's Kernel-General 12 start event, then every Kernel-General 1 clock step after it by record number), never by comparing one boot instant. Done when: a fixture with a 30 minute sleep timeout fails naming the `powercfg` command that fixes it, fixtures with a secure screen saver and with the inactivity policy each fail naming their fix, and a fixture where the policy requires a secure screen saver while the user's own setting is off fails naming the policy. **Groomed 2026-10-23:** completion finding 1. Cheaper substitute: telling the owner in prose only. **Corrected 2026-10-23:** read `powercfg /query` text, whose labels are localised, and left "screen lock timeout" undefined.
- [x] Check the Office reference build for Phase 2: Word, Excel, PowerPoint, Outlook (classic), Visio and Project executables are present under the Click-to-Run root, and report the build number. Done when: a fixture missing `VISIO.EXE` fails naming it, and the check runs while any unstamped section carries the `office` Need (Phase 2 captures, the D03 T01 §3 page counts, Phase 6 interoperability and the VBA object-model capture) and is skipped once none does; the script reads the sections through `scripts/lib/todo_graph.py` `graph()` from the TODO files themselves, never `build/todo-cache.json`, and checks Office when the tree cannot be read; fixtures prove a missing cache, a stale cache (one that says no section needs Office) and the moment the last Phase 2 capture stamps while D03 T01 §3 is still open each still check Office. Cheaper substitute: checking Word only, or only during Phase 2. **Corrected 2026-10-23:** skipped the check once Phase 2 closed. **Corrected 2026-10-23:** ran `todo-graph.py build` and read the derived cache, which a stale or missing cache could still mislead; the source is the TODO files.
- [x] Check the C++ toolchain through `vswhere.exe -include packages` on the newest stable Visual Studio 2026 (**Corrected 2026-10-23:** said `-requires`, which answers only all or nothing and cannot name the missing component): the desktop C++ workload, the x64 and Arm64 MSVC tools, CMake, vcpkg, the LLVM clang tools and a Windows 11 SDK. Done when: a fixture without `Microsoft.VisualStudio.Component.VC.Llvm.Clang` fails and prints the one elevated install command. Cheaper substitute: discovering a missing tool when a build fails.
- [x] Check the services the campaign calls: `gh auth status` succeeds, the pinned reviewer's CLI from `.conclave/reviewers.toml` is on PATH and signed in (`codex login status`, run non-interactively with no prompt on standard input, printing nothing it reads), and at least 50 GB is free on the repository drive. Done when: each failing fixture exits 1 naming what to fix, including a signed-out reviewer and a reviewer CLI that cannot start. Cheaper substitute: a run that stalls at its first review round. **Groomed 2026-10-23:** completion finding 2.
- [x] Print one line per check and exit 0 only when every required check passes, 1 with the list of fixes, 2 when a check cannot run; a check that cannot run (an API error, unreadable output, a probe past its deadline, a crash) is reported as `ERROR` while every other check still runs and prints, exit 2 outranks exit 1, and every subprocess probe (`vswhere`, `gh`, the reviewer CLI) has a 120 second deadline. Done when: `python scripts/check-campaign-host.py` on this PC prints every line and its exit code matches, and fixtures prove a timed-out probe, an API error and a crashing check each exit 2 with the other checks reported, and a failure beside an error exits 2. Cheaper substitute: a single pass or fail with no fix named, or a probe that hangs the campaign before its park. **Groomed 2026-10-23:** completion finding 3.
- [x] Survive a failed email under `--notify`: when `pin_proposal.notify` raises (no vault key, a refused send, no network), the script prints `email not sent: <reason>` on standard output so the run file records it, and keeps its exit code. Done when: tests cover a sent email, a refused one (exit code unchanged, the line printed) and no email when ready. Cheaper substitute: a readiness failure lost because its email failed. **Groomed 2026-10-23:** completion finding 4.
- [x] Write `scripts/tests/test_check_campaign_host.py` with fake readers for every check. Done when: the suite passes and fails when any one check is made to always pass. Cheaper substitute: running the script on this PC only.
- [x] Run the check at campaign start and at every phase start in `process-plan` and `process-phase` (in `.claude/skills/`, the only copy since D00 T03 §13; **Corrected 2026-10-23:** named the `.agents/` and `.codex/` mirrors too); a failure records the fixes in the run file, emails them through `.conclave/automations/alert.py` (the script's `--notify` flag, through `scripts/lib/pin_proposal.py` `notify`, which sends with `alert.send`), and parks the campaign. Done when: both skills name the command and the park rule. Cheaper substitute: a check the owner must remember to run.
- [x] Make a host failure stop the whole campaign, not one phase: in `.claude/skills/process-plan/SKILL.md` and `.claude/skills/process-phase/SKILL.md`, exit 1 or 2 at campaign start, at a phase start reached by chaining, at a phase started on its own, and on a manual or heartbeat resume writes the column-0 `PARKED <UTC> run=<run id> host-not-ready: ...` line, runs `campaign_guard.py end --reason park`, deletes the heartbeat and confirms it with `CronList`, and claims no further row in any phase until a resumed run's check exits 0; `process-plan` never chains past a host-not-ready park. Done when: both skills name the four entry points, the guard end, the heartbeat cancellation and the no-chain rule. Cheaper substitute: a park that `process-plan` reads as one phase parking and chains past. **Groomed 2026-10-23:** completion finding 5.
- [x] Commit: `automations: add the campaign host readiness check`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_check_campaign_host.py"` passes and `python scripts/check-campaign-host.py` exits 0 on this PC once the LLVM clang tools are installed.

> **Verified:** 2026-10-23 | §12 | 77c39bc9c4a1ef2a164f9e79fe5fa482e8a705ee
> **Review:** `docs/reviews/d00-t03-s12.json`

## 13. Single Writer, Cap 33, Completion Review

Owner decisions 2026-10-23: Opus 5.5 (Claude Code) is the only writer from now on, so the Antigravity and Codex writer set-ups (their skill mirrors, entry files, rules and reviewer routes) are removed, leaving one route: Claude's work is reviewed by GPT-6.1 Sol through the Codex CLI. The build is complex enough that the review loop's cap rises from 22 to 33 rounds. And every section gets one completion review before it is built: the pinned reviewer reads the section against `design/SPEC.md`, the inventory and its neighbouring sections and says whether building it as written yields a whole feature (every menu item, button, dialog, state, error path and undo path the feature implies, not only the one named). A gap is closed by extending the section, when the missing piece belongs to its single responsibility, or by filing a new section through `add-todo` with an XREF; the build starts only after that. `stamp` refuses a section whose completion record is missing, belongs to another section, or leaves a gap without a disposition. **Groomed 2026-10-23:** extended with the five gaps of this section's own completion review (`docs/reviews/00-workspace/D00-T03-s13-completion.md`): resolved gaps as a stamp condition, evidence bound to the section, failure and recovery states, the review skills' writer routing, and adoption for sections already under review.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Reduce the repository to one writer and one route. Done when: `Test-Path .agents, .codex, CODEX.md, GEMINI.md` returns `False` four times and `python scripts/review-dispatch.py --check-pin` passes.
2. Raise the cap and add the completion review to the tooling and skills. Done when: `stamp` refuses each invalid completion record the tests name.

- [x] Reduce `.conclave/reviewers.toml` to the `sol` reviewer and the single route `claude = ["sol"]`, dropping the `sonnet` reviewer and the `codex` and `gemini` routes, with the owner decision in its comments. Done when: `python scripts/review-dispatch.py --check-pin` exits 0 and the file names no other reviewer or route. Cheaper substitute: leaving dead routes that a later session might use.
- [x] Restrict `scripts/review-dispatch.py` to the one writer and the one reviewer CLI the pin can use: `WRITERS = ("claude",)`, the Codex CLI only (the Antigravity and Claude Code reviewer command lines, which no route can now reach, removed), the docstring and `--writer` help, with `scripts/tests/test_review_dispatch.py` updated. Done when: `--writer codex` is refused by the argument parser, a pin naming an `agy` or `claude` reviewer is refused, and the dispatcher tests pass. Cheaper substitute: keeping code paths no route serves.
- [x] Delete `.agents/`, `.codex/`, `CODEX.md` and `GEMINI.md`. Done when: `Test-Path .agents, .codex, CODEX.md, GEMINI.md` returns `False` for each. Cheaper substitute: leaving mirrors nobody maintains, which drift from `.claude/skills/`.
- [x] Rewrite the single-writer rules in `AGENTS.md`, `CLAUDE.md`, `docs/agent-skills-and-rules-structure.md`, `docs/todo-workflow.md` and `.claude/skills/authoring-skills/` (its `SKILL.md` and `references/skill-layout-checklist.md`): skills live only in `.claude/skills/`, Claude Code writes, Sol reviews. Done when: `git grep -n -i -E "\.agents/|\.codex/|CODEX\.md|GEMINI\.md|antigravity|\bastra\b|gemini|sonnet 5\.5|claude\|codex" -- AGENTS.md CLAUDE.md ":(glob)docs/*.md" .claude .conclave scripts/review-dispatch.py` prints only the retirement notes. Cheaper substitute: instructions that still tell a session to change three mirrors. **Corrected 2026-10-23:** the search matched `docs/reviews/` history, the subagents' Sonnet model and "astral"; it now reads only top-level `docs/*.md`, the Sonnet 5.5 reviewer and the whole word Astra.
- [x] Replace the writer routing in `.claude/skills/independent-review/SKILL.md` (its three-writer table and Astra) and `.claude/skills/review-todo-section/SKILL.md` (its `--writer <claude|codex|gemini>` command) with the one route, Claude reviewed by Sol. Done when: both name only `--writer claude` and Sol, and the grep above passes. Cheaper substitute: skills that advertise routes the dispatcher now refuses. **Groomed 2026-10-23:** completion finding 4.
- [x] Correct the open TODO sections that name the removed mirrors (D00 T03 §12 and D03 T01 §13) with dated notes. Done when: neither names `.agents/skills/` or `.codex/skills/`. Cheaper substitute: leaving checklist items no session can finish.
- [x] Raise `REVIEW_ROUND_CAP` to 33 in `scripts/lib/todo_graph.py`, add `stopped-at-33` to `VERDICTS` and 22 to `EARLIER_CAPS`, with tests in `scripts/tests/test_todo_graph.py`. Done when: a receipt over 33 returned reviews is refused, a `stopped-at-33` receipt with its cap outcome passes, and every existing receipt still validates. Cheaper substitute: changing the number in the skills only.
- [x] Update the cap in `.claude/skills/review-todo-section/SKILL.md`, `.claude/skills/independent-review/SKILL.md`, `AGENTS.md` and `todo/README.md`. Done when: `git grep -n -E "22 rounds|stopped-at-22" -- AGENTS.md todo/README.md .claude` names only the earlier-cap history. Cheaper substitute: a cap the tooling and the skills disagree on.
- [x] Finish `docs/completion-review-prompt.md`: the reply opens with `SECTION: <ref>` and `PURPOSE: completion`, lists numbered gaps with a remedy each, and ends with `COMPLETE: yes` or `COMPLETE: no`, then `HIGHEST:` and `OVERALL:` (approve only with `COMPLETE: yes`). Done when: `python scripts/check-design-doc.py docs/completion-review-prompt.md` exits 0 and the prompt names all five reply lines. Cheaper substitute: reusing the code review prompt, which judges what was built, not what was left out. **Groomed 2026-10-23:** completion finding 2.
- [x] Add the completion step to `.claude/skills/process-todo-section/SKILL.md` before the build: dispatch the prompt with `--record docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>-completion.md` (its first line `# Completion review: <ref>`), then extend the section or file a new section through `add-todo` for each gap, and write `## Outcome (round N)` in that file, N the round it answers, with one line per gap, `N. extended` or `N. filed -> DNN TNN §N`. Done when: the skill names the command, the heading, both remedies and the outcome format. Cheaper substitute: a completion check the executor may skip.
- [x] Define the completion failure and recovery states in `.claude/skills/process-todo-section/SKILL.md`, `.claude/skills/process-phase/SKILL.md` and `.claude/skills/process-plan/SKILL.md`: a dispatch that returns no review (exit 1, or a reply without the `SECTION`, `PURPOSE` and `COMPLETE` lines) parks the section with the reason in the run file and the campaign takes its next ready row, retrying that section once at the next phase start; after an `extended` outcome the section is re-dispatched once, and gaps that re-review still reports are filed as new sections, never dispatched a third time; a completion file that already holds the outcome of its last round is reused after a session dies, so no pass is spent twice. Done when: the three skills name each state and its transition. Cheaper substitute: a campaign that stops, or loops, on a reviewer outage. **Groomed 2026-10-23:** completion finding 3.
- [x] Make `stamp` in `scripts/lib/todo_graph.py` require `--completion <path>` and record it in the receipt as `completion`: the path is `docs/reviews/<domain>/D<NN>-T<NN>-s<N>-completion.md` for this section, the file opens `# Completion review: <ref>`, its rounds are ones the dispatcher wrote with the pinned reviewer, the last returned round's reply opens `SECTION: <ref>` and `PURPOSE: completion` (earlier rounds are history) and pairs `COMPLETE: yes` with `OVERALL: approve` (or `COMPLETE: no` with `needs-attention`), and either the last returned round says `COMPLETE: yes` or that round's `## Outcome (round N)` gives every numbered gap a disposition, each `filed ->` reference resolving to a real section. Done when: tests refuse a missing flag, a missing file, another section's file, a code review file, a contradictory verdict, an unresolved gap, a `filed ->` to no section and an outage-only file, and accept a valid one. Cheaper substitute: accepting any readable review file. **Groomed 2026-10-23:** completion findings 1 and 2.
- [x] Require fresh completion evidence after a reopen: for a section carrying an `Unstamped:` note, `stamp` refuses a completion round run before that note's date. Done when: a test unstamps, fails to re-stamp with the old completion file, and re-stamps after a new round. Cheaper substitute: reusing the evidence the regression slipped past. **Groomed 2026-10-23:** completion finding 5.
- [x] Require `completion` on every receipt with `round_cap` 33 in receipt validation, and leave receipts with earlier caps as they are. Done when: a cap-33 receipt without it fails `python scripts/todo-graph.py validate`, and every receipt in `docs/reviews/` still validates. Cheaper substitute: requiring it only at stamp time, so an edited receipt could drop it.
- [x] Record the adoption rule in `todo/README.md` and the review skills: a section whose review loop began before this section stamps (D02 T01 §23 in the paused run `docs/phase-runs/2026-10-22-phase-2.md` is one) continues under the 33-round cap, and before its stamp runs one completion review of its contract, whose gaps are filed as new sections because its code already exists; a section reopened by `unstamp` gets a fresh completion review. Done when: both documents state the rule and the paused run file names it for D02 T01 §23. Cheaper substitute: leaving in-flight sections unable to stamp under the new rules. **Groomed 2026-10-23:** completion finding 5.
- [x] Show `--completion` in the stamp example of `.claude/skills/review-todo-section/SKILL.md` and in the stamps paragraph of `todo/README.md`. Done when: both name the flag and the completion file path. Cheaper substitute: a flag only the code knows.
- [x] Commit: `automations: one writer, a 33-round cap and a completion review before building`

**Test checkpoint:** `python -m unittest discover -s scripts/tests` passes, `python scripts/todo-graph.py validate` exits 0, `python scripts/review-dispatch.py --check-pin` exits 0, `Test-Path .agents, .codex, CODEX.md, GEMINI.md` returns `False` four times, and `git grep -n -i -E "\.agents/|\.codex/|CODEX\.md|GEMINI\.md|antigravity|\bastra\b|gemini|sonnet 5\.5|claude\|codex" -- AGENTS.md CLAUDE.md ":(glob)docs/*.md" .claude .conclave scripts/review-dispatch.py` prints only the retirement notes.

> **Verified:** 2026-10-23 | §13 | c663f93d19b3d944939fe4a0724e3893819e28a2
> **Review:** `docs/reviews/d00-t03-s13.json`

## 14. Completion Evidence Hardening

> **Started:** 2026-10-23T09:36:00Z

Filed 2026-10-23 from round 2 of D00 T03 §13's completion review (`docs/reviews/00-workspace/D00-T03-s13-completion.md`): after the one permitted re-check the reviewer still found four gaps, and §13's own rule files such gaps as a new section rather than reviewing a third time. §13 makes `stamp` require a completion record for the section; this section makes that record prove it reviewed the contract that was built, that no required re-check is pending, that a dispatcher refusal cannot leave a silent hole, and that evidence is fresh after a reopen to the second, not the day.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Extend the completion record format and `stamp`'s checks in `scripts/lib/todo_graph.py`. Done when: each refusal below has a test that fails without it.
2. Teach the skills the new record steps. Done when: `.claude/skills/process-todo-section/SKILL.md` names each.

- [x] Add `python scripts/todo-graph.py contract-digest '<ref>'`, printing `sha256:<hex>` of the section's text with every checkbox written unticked and the `Verified:`, `Review:`, `Started:` and `Duration:` lines removed. Done when: the command exists, ticking an item or turning `Started:` into `Duration:` leaves the digest unchanged, and editing an item's wording or adding a `Deferred:` line changes it. **Corrected 2026-10-23 (review round 1):** kept `Duration:`, which review-todo-section adds before the stamp. Cheaper substitute: trusting that an approved section was never edited.
- [x] Bind each completion round to the contract it was given: `docs/completion-review-prompt.md` carries `Contract: sha256:<digest>` (printed by `contract-digest` from the same text the prompt inlines) and asks the reviewer to open its reply with `SECTION: <ref>`, `PURPOSE: completion` and `CONTRACT: sha256:<digest>` copied from the prompt, so the digest is inside the dispatcher's recorded reply, not written after it. Done when: the prompt names the line and `python scripts/check-design-doc.py docs/completion-review-prompt.md` exits 0. Cheaper substitute: a digest written into the record after the review, which can bind approval to text the reviewer never saw. **Groomed 2026-10-23:** completion finding 1 (replaces an outcome-block digest).
- [x] Refuse in `stamp` (`completion_ok` in `scripts/lib/todo_graph.py`) a section whose current contract digest differs from the `CONTRACT:` line of the last returned completion round, or whose last returned round has no such line when it ran at or after `CONTRACT_REQUIRED_FROM` (a UTC instant constant in `scripts/lib/todo_graph.py`: when `docs/completion-review-prompt.md` first carried the line; earlier rounds, this section's own included, are judged by the D00 T03 §13 rules, and D00 T03 §16 records which rules each receipt met). Done when: tests refuse an edit made after dispatch (the reply carries the old digest), a section extended after its approving round, and a reply without the line run after `CONTRACT_REQUIRED_FROM`, pass one re-reviewed after the extension, and pass a digest-free round run before it. Cheaper substitute: binding the evidence to the section reference only. **Corrected 2026-10-23:** did not say when the line becomes required, which would have refused every record written before the prompt carried it, this section's own included.
- [x] Refuse a pending re-check in `stamp`: when the `## Outcome (round N)` of the last returned completion round gives any gap `extended`, the re-check has not returned yet, whatever outage rounds were recorded after it, and the stamp is refused; a later returned round (the single re-check, or its one retry after an outage at the next phase start) satisfies it, with its own gaps `filed ->`. In `.claude/skills/process-todo-section/SKILL.md` the "never a third time" limit counts returned passes, not attempts, so a retry after an outage is allowed. Done when: tests refuse a session that died after recording `extended`, refuse one whose re-check returned an outage, pass one whose re-check returned after an outage round, and pass one whose re-check gaps were all filed; the skill states the counting rule. Cheaper substitute: one outcome block for the whole file, or counting outage attempts as passes. **Groomed 2026-10-23:** completion finding 2.
- [x] Keep the completion record recoverable in `.claude/skills/process-todo-section/SKILL.md`: commit the record with its `# Completion review: <ref>` line before the first dispatch, and commit it again after every returned round and its outcome, before anything else is built; a dispatch that exits 2 leaves the record untouched (nothing to restore), and a record `read_rounds` cannot read is restored from its last commit, which then holds every returned round; either parks the section with the reason in the run file and retries once at the next phase start. Done when: the skill names both commits, exit 2, the read-back check, the restore and the single retry, and a test in `scripts/tests/test_review_dispatch.py` proves an exit 2 on `--record` leaves the record byte for byte unchanged. Cheaper substitute: building on a review that was never recorded, or restoring over uncommitted returned rounds. **Groomed 2026-10-23:** completion finding 3.
- [x] Record reopening to the second: `python scripts/todo-graph.py unstamp` writes `> **Unstamped:** <UTC instant>: <reason>` (an ISO 8601 time ending in `Z`), and `stamp` refuses a completion round whose `Run:` time is not after the latest reopening; a date-only note from before this section counts as the end of its day. Done when: tests cover a review before and after a same-day reopen, two reopenings, and a legacy date-only note. Cheaper substitute: comparing dates.
- [x] Commit: `automations: bind completion evidence to the reviewed contract and its round`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_todo_graph.py"` and `python -m unittest discover -s scripts/tests -p "test_review_dispatch.py"` pass, and `python scripts/todo-graph.py validate` exits 0.

> **Verified:** 2026-10-23 | §14 | aa432a1c4cb8f1fc304d0219774fa8ee2665e550
> **Review:** `docs/reviews/d00-t03-s14.json`

## 15. CI Watch and Red-Run Repair

> **Started:** 2026-10-23T10:12:00Z

Filed 2026-10-23 from the owner's question whether the campaign keeps an eye on CI and fixes red runs. It does not: `process-plan` runs every gate locally and pushes after each stamp, but nothing reads the GitHub Actions result afterwards (the old guard's CI repair ledger was retired on 2026-10-21, and the Phase 2 run's CI repairs were found by hand). Once C++ lands, the Arm64 build and tests run only in CI, so a red run would go unseen. This section makes CI part of the loop: the previous push is checked at every section boundary, a red run is repaired before the next row is claimed, a phase closeout, a draft release and the end of the campaign wait for green, and a failure that will not yield parks the campaign, since a red `main` is shared infrastructure.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `scripts/ci-status.py` with its tests. Done when: each state has a fixture over a fake `gh`.
2. Wire it into `process-plan` and `process-phase`. Done when: both skills name the boundary check, the hard gates, the repair rule and the bound.

- [x] Write `scripts/ci-status.py`, which resolves its argument (`HEAD` or a ref) to a full SHA with `git rev-parse --verify <ref>^{commit}`, selects the governing run (the `ci.yml` run with event `push` on branch `main` for that `headSha`, the newest by `createdAt` when there are several, its latest attempt as `gh run view` reports it; pull request and manual runs never count), and exits 0 when it concluded `success`, 1 for every other conclusion (`failure`, `cancelled`, `timed_out`, `startup_failure`, `action_required`, `skipped`, `neutral`, `stale`), naming the conclusion and printing the failing jobs and steps from `gh run view <id> --json jobs`, 3 while it is queued or in progress, and 2 when `gh` cannot be read or no push run exists 10 minutes after the commit's committer date (before that, 3). `gh` and `git` are found through `find_cli`. Done when: fixtures for each state exit with their code, including competing push and pull request runs, a rerun attempt that turned green, a cancelled run and a run created late. Cheaper substitute: reading the newest run on `main`, which may belong to another commit. **Groomed 2026-10-23:** completion findings 4 and 7.
- [x] Add `--wait --timeout <seconds>` to `scripts/ci-status.py`, polling every 30 seconds until the run ends, and `--log <path>` writing `gh run view <id> --log-failed` to scratch, bounded to the last 400 lines; every `gh` and `git` call has a deadline of 60 seconds or the wait's remaining time, whichever is shorter, and a call past it counts as unreadable. Done when: a fixture that turns green after two polls exits 0, one that never ends exits 3 at the timeout, a hung `gh` exits 2 within its deadline, a log that cannot be read is reported without failing the status, and the log lands outside the repository. Cheaper substitute: an unbounded wait, or a full log pasted into the run file. **Groomed 2026-10-23:** completion finding 7.
- [x] Record each push in the run file in `.claude/skills/process-plan/SKILL.md`: after a stamp push, append `ci-pending <sha> <UTC>`; at the next section boundary, before the next row is claimed, run `python scripts/ci-status.py <sha>` and act on its exit: 0 records `ci-green <sha>`; 1 starts the repair below; 3 waits with `--wait --timeout 1800` and acts on the result; 2 is retried once after five minutes and, still 2, parks the campaign with `ci-unknown` as the reason, since green cannot be established. Done when: the skill names both records and the action for each of the four exits. Cheaper substitute: checking CI only at phase ends, when several red commits have stacked, or claiming the next row while CI is pending or unreadable. **Groomed 2026-10-23:** completion finding 1.
- [x] Repair a red run before the next row in `.claude/skills/process-plan/SKILL.md`: read the failing jobs and the log from `--log`, reproduce locally where the job can run here, fix at the owning layer in a `ci: <what was fixed> (repair for <sha>, run <id>)` commit, re-run the local gates, push, and `--wait` for green. A failure that passes on one `gh run rerun <id> --failed` is recorded as `ci-flaky <sha> <job>` and filed through `add-todo` as a flake to fix, never ignored. Done when: the skill names each step, the commit format and the flake rule. Cheaper substitute: re-running until green.
- [x] Bound the repair in `.claude/skills/process-plan/SKILL.md`: after three repair commits that leave the same job red, the campaign files the failure through `add-todo` (run link, job, step, what was tried), emails the owner through `.conclave/automations/alert.py`, and parks with `ci-red` as the reason. Done when: the skill names the bound, the filing, the email and the park. Cheaper substitute: an endless repair loop, or pushing more work onto a red `main`.
- [x] Make green a hard gate in `.claude/skills/process-phase/SKILL.md` and `.claude/skills/process-plan/SKILL.md`: a phase closeout, a draft release and the campaign's end each run `python scripts/ci-status.py HEAD --wait --timeout 3600` and proceed only on exit 0. Done when: both skills name the three gates. Cheaper substitute: closing a phase on local gates alone.
- [x] Run the same boundary check in `.claude/skills/process-phase/SKILL.md` for a phase started on its own: after each stamp push and before claiming the next row, and on every manual or heartbeat resume before any row, by reference to the one procedure in `process-plan` so the two never diverge. Done when: `process-phase` names the boundary check, the resume check and the reference. Cheaper substitute: a standalone phase that ships several sections before looking at CI. **Groomed 2026-10-23:** completion finding 2.
- [x] Make a `ci-red` or `ci-unknown` park end the whole campaign as a `host-not-ready` park does: in `.claude/skills/process-plan/SKILL.md` it writes the column-0 `PARKED <UTC> run=<run id> ci-red: <job>` (or `ci-unknown:`) line, ends the guard with `--reason park`, deletes and confirms the heartbeat, is never chained past, and the heartbeat prompt's step 5 treats it as terminal in either scope; an owner resume runs `python scripts/ci-status.py HEAD --wait --timeout 3600` before any row and parks again unless it exits 0; a failed email is recorded and never stops the park. Done when: the skill and its heartbeat prompt name both reasons, the no-chain rule and the resume check. Cheaper substitute: a park that the chaining or the heartbeat restarts on a red `main`. **Groomed 2026-10-23:** completion finding 5.
- [x] Add a CI line to the readiness check (D00 T03 §12) wiring: `scripts/check-campaign-host.py` confirms `gh run list --workflow ci.yml --limit 1` can be read. Done when: the readiness item names it and a fixture without `gh` access fails. Cheaper substitute: discovering at the first boundary that CI cannot be read.
- [x] Write `scripts/tests/test_ci_status.py` with a fake `gh` for every state, the wait, the timeout and the log bound. Done when: the suite passes and fails when any state's exit code is changed. Cheaper substitute: running the script against the live repository only.
- [x] Commit: `automations: watch CI at section boundaries and repair red runs`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_ci_status.py"` passes, `python scripts/ci-status.py HEAD` prints the latest pushed commit's run state on this PC, and `python scripts/todo-graph.py validate` exits 0.

-> XREF: §17 (pending pushes reconciled on start and resume), §18 (CI recovery budget), §19 (campaign CI gate integration checks)

> **Verified:** 2026-10-23 | §15 | 70dbb6de58cb5a87656a921f3870e1a2a513a777
> **Review:** `docs/reviews/d00-t03-s15.json`

## 16. Completion Evidence Adoption Boundary

> **Started:** 2026-10-23T11:21:00Z

Filed 2026-10-23 from round 2 of D00 T03 §14's completion review (`docs/reviews/00-workspace/D00-T03-s14-completion.md`): §14 hardens what a completion record must prove (a `CONTRACT:` digest in the reply, no pending re-check, reopening to the second), but completion records written before it, such as D00 T03 §12's and §13's, carry no digest. Rewriting old reviews to add one would forge evidence. This section states and tests the boundary: stored receipts keep validating under the rules they were stamped with, and every stamp from §14 on, re-stamps after a reopen included, meets the hardened rules.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Record the boundary in each receipt and in `todo/README.md`. Done when: new receipts name the completion rules they met.
2. Test both sides of the boundary. Done when: the tests below pass and fail when the boundary is removed.

- [x] Record `completion_rules: 2` in every receipt `stamp` writes, and classify a stored receipt without the field in `receipt_data_ok` in `scripts/lib/todo_graph.py` by its completion record: version 2 when the last returned round ran at or after `CONTRACT_REQUIRED_FROM` (D00 T03 §15's receipt), version 1 otherwise (§12, §13 and §14's, §14 being the section that introduced the rules); a version 2 receipt is validated with the `CONTRACT:` check (the echo is present and matches the stamped section's contract digest), a version 1 receipt never. Done when: `python scripts/todo-graph.py validate` passes with all four stored receipts unchanged, a test proves a version 2 receipt (written or classified) fails validation once its section's wording changes while a version 1 receipt does not, and a receipt claiming `completion_rules: 2` whose record lacks a `CONTRACT:` line is refused. Cheaper substitute: adding a digest to an old review by hand, or treating every receipt without the field as version 1. **Groomed 2026-10-23:** completion finding 1.
- [x] Refuse in `stamp` any completion evidence that fails the version 2 rules, whatever its round's run date (the `CONTRACT_REQUIRED_FROM` exemption no longer applies to a new stamp), a re-stamp after `unstamp` included, whatever rules the section's earlier receipt met. Done when: a first-stamp test with genuine digest-free evidence run before `CONTRACT_REQUIRED_FROM` is refused with nothing written, then a fresh matching review is accepted and the receipt reads `completion_rules: 2`; and a test unstamps a section stamped under version 1 and refuses its re-stamp with the old record, then accepts it after a fresh round with the `CONTRACT:` line. Cheaper substitute: letting a new or reopened section stamp on evidence from before the hardening. **Groomed 2026-10-23:** completion finding 2.
- [x] State the boundary in the stamps paragraph of `todo/README.md` and in `.claude/skills/review-todo-section/SKILL.md`. Done when: both name `completion_rules`, the two versions and the re-stamp rule. Cheaper substitute: a rule only the code knows.
- [x] Commit: `automations: keep stored receipts under their own completion rules and harden every new stamp`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_todo_graph.py"` passes and `python scripts/todo-graph.py validate` exits 0 with every stored receipt unchanged.

> **Verified:** 2026-10-23 | §16 | e2b8c3ddd3d6ab23afbb0900614595ce81c72b54
> **Review:** `docs/reviews/d00-t03-s16.json`

## 17. CI Push Reconciliation

> **Started:** 2026-10-23T11:45:00Z

Filed 2026-10-23 from round 1 of D00 T03 §15's completion review (`docs/reviews/00-workspace/D00-T03-s15-completion.md`, finding 3): §15 records `ci-pending` only after a stamp push, so a dependency merge, a closeout push, another campaign push, or a session that dies between a push and its record leaves a commit on `main` whose CI nobody checks. This section makes the pending set come from the pushed history, not from notes. **Groomed 2026-10-23:** finding 1 of round 2 of §15's completion review: GitHub runs a push workflow only for the push's tip, so the unit is the push head, not every commit; commits under a green head are covered by it.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Derive the unchecked pushes from git and the run files. Done when: a command lists every commit on `origin/main` since the last `ci-green` that has no `ci-green` record.
2. Run the reconciliation at campaign start, phase start and every resume. Done when: both skills name it.

- [x] Add `--pending <run file>` to `scripts/ci-status.py`: list the push heads on `origin/main` (a push head is a commit recorded `ci-pending`, or the `headSha` of a `ci.yml` push run on `main`, or `origin/main` itself) that have no recorded outcome (`ci-green`, or `ci-superseded <sha> by <sha>`) in that run file or any earlier run file in `docs/phase-runs/`, after the baseline, and report the status of each, oldest first; a commit that is not a push head is covered by the first push head after it and is never checked on its own; a later green head never covers an earlier push head that has no outcome of its own. Done when: fixtures with a merge commit, a closeout push and an unrecorded stamp push each list the unchecked head, two implementation commits pushed with their stamp list only the stamp, an unchecked head A followed by a recorded-green head B lists A, and a history whose every head has an outcome lists nothing. Cheaper substitute: trusting the run file's own `ci-pending` notes, starting after the newest green record, or checking every commit and parking on runs GitHub never creates. **Groomed 2026-10-23:** completion finding 4.
- [x] Fetch before enumerating: `--pending` runs `git fetch origin main` (bounded like every call, 60 seconds) and reads the fetched `origin/main`, never a stale tracking ref; a fetch that fails exits 2. Done when: a fixture where the remote advanced past the local tracking ref lists the new head, and a failed fetch exits 2. Cheaper substitute: reconciling against the clone's last fetch, which a failed pull after a merge leaves behind. **Groomed 2026-10-23:** completion finding 1.
- [x] Define the first-run baseline: when no run file holds an outcome, the baseline is the newest push head on `origin/main` whose governing push run is green (history before it is covered by that run), found among the `ci.yml` push runs on `main`; with no green push run at all, every push head in that run history is listed. Done when: fixtures with no run file, with an empty one, and with run files holding no outcome each pick that baseline, and one with no green run lists every head. Cheaper substitute: an undefined start that lists nothing or the whole history. **Groomed 2026-10-23:** completion finding 2.
- [x] Treat incomplete discovery as unknown, never as an empty list: `--pending` exits 2 when the fetch fails, a run file cannot be read, `gh run list` fails, or it returns as many runs as its limit (500, so history may be cut off), and exits 0 with no heads listed only after a complete enumeration; the CI watch acts on exit 2 with §15's retry-then-park rule before any row is claimed. Done when: fixtures for an unreadable run file, a failed `gh`, a full page of runs and a genuinely empty result each exit as stated. Cheaper substitute: an empty or partial list that lets work continue. **Groomed 2026-10-23:** completion finding 3.
- [x] Record a red push head whose later push head is green as `ci-superseded <sha> by <later sha>` in `.claude/skills/process-plan/SKILL.md` (no repair: the later green run includes its changes), and repair a red head that is still the newest under §15's rules. Done when: the skill names the record and when it applies. Cheaper substitute: repairing a failure `main` no longer has, or dropping it silently.
- [x] Record `ci-pending <sha> <UTC>` for every campaign push, not only stamp pushes: dependency merges by `scripts/merge_prs.py`, closeout and park commits, and repair commits, in `.claude/skills/process-plan/SKILL.md`. Done when: the skill names each push kind. Cheaper substitute: watching only the stamp commits.
- [x] Run `python scripts/ci-status.py --pending <run file>` at campaign start, at every phase start and on every manual or heartbeat resume, before any row is claimed, and act on each listed commit with §15's exit rules, in `.claude/skills/process-plan/SKILL.md` and `.claude/skills/process-phase/SKILL.md`. Done when: both skills name the command and the three moments. Cheaper substitute: losing a red commit when a session dies between its push and its record.
- [x] Commit: `automations: reconcile unchecked pushes with CI on start and resume`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_ci_status.py"` passes and `python scripts/ci-status.py --pending docs/phase-runs/2026-10-23-phase-0.md` lists the pushed commits without a `ci-green` record on this PC.

> **Verified:** 2026-10-23 | §17 | 29c5792e03628303041a3410a531c69745afb992
> **Review:** `docs/reviews/d00-t03-s17.json`

## 18. CI Recovery Budget

> **Started:** 2026-10-23T12:28:00Z

Filed 2026-10-23 from round 1 of D00 T03 §15's completion review (finding 6): §15 bounds the repair at three commits that leave the same job red, which misses an infrastructure outage, an unreadable log, a rerun that fails, and repairs that turn a different job red each time. This section gives the whole recovery one budget that survives a resume.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `scripts/ci-recovery.py`, which holds the budget in `build/ci-recovery.json`. Done when: its tests cover every transition below.
2. Drive the CI watch's red path through it. Done when: `.claude/skills/process-plan/SKILL.md` names each command. **Groomed 2026-10-23:** the budget moved from run-file prose into a tool with tests (completion findings 1 to 4).

- [x] Add `scripts/ci-recovery.py` with one recovery per red `main`, identified by the first red head's SHA: `open <sha>` starts it (or returns the open one), every repair head pushed during it is attached with `attach <head>`, and only `close <green head>`, for a green head that descends from the recovery's first head, ends it and resets the budget. Done when: tests prove a repair that turns another job red stays in the same recovery, and the budget resets only on a descendant green. Cheaper substitute: counting per current head, which a new repair SHA resets. **Groomed 2026-10-23:** completion finding 1.
- [x] Persist the recovery in `build/ci-recovery.json` (gitignored, atomic temp-then-replace writes), so it survives a session's death, a resume and a new run file without dirtying the tree; `reserve <kind>` records attempt `n` (`repair`, `rerun`, `wait`, `unreadable`) before the action runs, and a reserved attempt with no recorded result after a resume counts as spent and is never repeated (a reserved rerun is not rerun). Done when: tests kill the session between a reservation and its result, resume with a fresh run file, and show the count kept and the rerun not repeated. Cheaper substitute: a run-file note written after the action, which a death between action and note erases. **Groomed 2026-10-23:** completion finding 2.
- [x] Spend at most four attempts per recovery, any mix of kinds: a repair push, the single flake rerun (one per head, refused a second time), a bounded wait that returns pending again, and a status or log read that is unreadable during the recovery (inside an open recovery these consume the budget instead of §15's one-retry `ci-unknown` park, which still applies to discovery outside one); a green result at any attempt closes the recovery; `reserve` refuses a fifth attempt with exit 1 and prints `exhausted`. Done when: tests cover each kind, a fourth-attempt success, a second rerun refused, repeated pending and unreadable results, and the refusal of a fifth. Cheaper substitute: three repair commits per job, which an outage or alternating jobs never reaches. **Groomed 2026-10-23:** completion finding 3.
- [x] On `exhausted`, in `.claude/skills/process-plan/SKILL.md`: file the failure through `add-todo` (run link, jobs, steps, every attempt from `python scripts/ci-recovery.py show`), email the owner through `.conclave/automations/alert.py` (record `email not sent` if it fails; the park goes ahead), and park with `ci-red`, even when no useful code change exists. Done when: the skill names `open`, `attach`, `reserve`, `close`, `show`, the exhaustion steps and the park. Cheaper substitute: a budget the skill describes but nothing enforces.
- [x] Define the single flake rerun: one `gh run rerun <id> --failed --repo github.com/<owner>/<name>` per head, reserved as `rerun` before it runs; a pass closes the recovery, records `ci-flaky <sha> <job>` and files the flake through `add-todo`; a fail continues the recovery. Done when: the skill names the one rerun and both outcomes, and `reserve rerun` refuses a second rerun for the same head in a test. Cheaper substitute: re-running until green.
- [x] Commit: `automations: one recovery budget per red main, kept across resumes`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_ci_recovery.py"` passes, covering alternating failing jobs across repair heads, mixed attempt kinds, an interrupted reservation and a fresh-run resume, a refused second rerun, repeated pending and unreadable results, a fourth-attempt success and exhaustion.

> **Verified:** 2026-10-23 | §18 | ec0927a6fba6fc0f8f49e3d7d93711a960278b13
> **Review:** `docs/reviews/d00-t03-s18.json`

## 19. CI Gate Checks

> **Started:** 2026-10-23T12:56:00Z

Filed 2026-10-23 from round 1 of D00 T03 §15's completion review (finding 8): the CI gate lives mostly in skill prose, which a test of `scripts/ci-status.py` alone cannot hold to its word. This section adds checks that fail when the skills and the guard stop enforcing it.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Teach the run guard the CI parks. Done when: the Stop hook and `whoami` treat a `ci-red` or `ci-unknown` park like `host-not-ready`.
2. Lint the skills for the gate. Done when: a test fails when a required step is removed.

- [x] Make `scripts/campaign_guard.py` treat a column-0 `PARKED ... run=<run id> ci-red:`, `ci-unknown:` or `host-not-ready:` line as campaign-ending in either scope (the Stop hook lets the turn end, and a resumed run must start fresh), with tests in `scripts/tests/test_campaign_guard.py`. Done when: tests prove each reason ends the run and a phase park without one still chains. Cheaper substitute: relying on the heartbeat prompt's wording alone.
- [x] Add `scripts/tests/test_skill_ci_gate.py`, which reads `.claude/skills/process-plan/SKILL.md` and `.claude/skills/process-phase/SKILL.md` and fails unless each names the boundary check, the four exit actions, the three hard gates, the resume check, the pending reconciliation and the recovery budget (`process-phase` by its explicit reference to `process-plan`'s one procedure, which the test also checks). Done when: the test passes, and removing any one of those lines from a copy makes it fail. Cheaper substitute: reading the skills by eye.
- [x] Check the terminal-park procedure in the same test: the heartbeat prompt's step 5 ends the run for a `host-not-ready`, `ci-red` or `ci-unknown` park carrying the current run id in either scope, and `process-plan` names the no-chain rule, the guard's `end --reason park`, the heartbeat's deletion and confirmation, and a fresh-run resume. Done when: copies of the skill with each obligation removed or weakened (a reason dropped, the run-id match dropped, chaining allowed, the guard end or the heartbeat deletion removed, the fresh run replaced by a handover) each fail the test. Cheaper substitute: checking that the park reasons are named somewhere. **Groomed 2026-10-23:** completion finding 1.
- [x] Commit: `automations: hold the campaign to its CI gate with guard and skill checks`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_skill_ci_gate.py"` and `python -m unittest discover -s scripts/tests -p "test_campaign_guard.py"` pass.

> **Verified:** 2026-10-23 | §19 | 315f3475c7f48857515ea106a6068010680dd511
> **Review:** `docs/reviews/d00-t03-s19.json`

## 20. CI Reconciliation at Scale

> **Started:** 2026-10-23T13:25:00Z

Filed 2026-10-23 from round 2 of D00 T03 §17's completion review (`docs/reviews/00-workspace/D00-T03-s17-completion.md`): §17 lists unchecked push heads oldest first and treats a full 500-run page as unknown. Two cases remain: an older red head followed by a later head that is pending, unknown or red (supersession needs a later green head, and repair covers only the newest red head), and a workflow history past 500 runs, where retrying the same capped query parks the campaign for good even when every recent push is green.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Settle the newest head first. Done when: earlier red heads are resolved only after it.
2. Page the history down to a proven boundary. Done when: more than 500 runs reconcile.

- [x] Reconcile from the newest head back in `.claude/skills/process-plan/SKILL.md`: establish the newest listed head's outcome first (wait while pending, repair while red, park on unknown under §15's rules), and only once it is green record each earlier red head as `ci-superseded <sha> by <newest sha>`. Done when: the skill names the order, and fixtures in `scripts/tests/test_ci_status.py` for red A then pending B and red A then red B show `--pending` reporting both heads with their states so the order can be followed. Cheaper substitute: oldest-first processing that meets a red head with no rule.
- [x] Hold the new order in `scripts/tests/test_skill_ci_gate.py`: obligations for newest-first settlement and for superseding earlier red heads only once the newest is green, each with a weakening fixture that fails, and the reconciliation paragraph's pin updated on purpose for the new text. Done when: the suite passes, and copies that settle oldest first, or supersede before the newest is green, fail. Cheaper substitute: a skill edit the gate test rejects, or a pin updated without new obligations. **Groomed 2026-10-23:** completion finding 3.
- [x] Enumerate every `ci.yml` push run on `main` in `scripts/ci-status.py --pending` by paging the REST API (`gh api --paginate repos/<owner>/<name>/actions/workflows/ci.yml/runs?branch=main&event=push&per_page=100`), so no page cap applies; the enumeration is complete when the API has no further page and the runs collected match its `total_count`, whether or not any run predates the baseline (the baseline may be the workflow's first run, the history may be empty, and with no green run every head is listed, as §17 defines); exit 2 only when a page cannot be read or the count does not match. Done when: fixtures with more than 500 runs find every unchecked head, an earliest-run baseline, an empty workflow history and several pages with no green run each reconcile as defined, and a short page set (fewer runs than `total_count`) exits 2. Cheaper substitute: one capped page that parks a long campaign for good. **Groomed 2026-10-23:** completion finding 2 (was: page `gh run list` until a run older than the baseline, which a first-run baseline never reaches).
- [x] Remove the git history ceiling: `--pending` reads the whole first-parent history of `origin/main` (no `--max-count`), so a baseline any number of commits back is reached, and `HISTORY_LIMIT` and its cut-off refusals go. Done when: a fixture with more than 5,000 first-parent commits and an unchecked head beyond the former limit reconciles and lists it. Cheaper substitute: a window that parks for good once the baseline falls outside it. **Groomed 2026-10-23:** completion finding 1.
- [x] Commit: `automations: reconcile CI from the newest head and across any history length`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_ci_status.py"` and `python -m unittest discover -s scripts/tests -p "test_skill_ci_gate.py"` pass.

> **Verified:** 2026-10-23 | §20 | cc9247770f900e087207e86eb96b5de24aa50d88
> **Review:** `docs/reviews/d00-t03-s20.json`

## 21. CI Recovery Closed on Resume

> **Started:** 2026-10-23T13:50:00Z

Filed 2026-10-23 from round 2 of D00 T03 §18's completion review (`docs/reviews/00-workspace/D00-T03-s18-completion.md`): a session can die after a repair or rerun turns `main` green but before `scripts/ci-recovery.py close` runs. On resume, §17's reconciliation establishes green and the campaign carries on, while the recovery stays open, so a later, unrelated red `main` would inherit its spent budget.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Teach the recovery tool to settle against reconciled history. Done when: an open recovery closes on a green descendant found at resume.
2. Run it at every start and resume. Done when: both skills name it before any merge or row.

- [x] Add `settle <green head>` to `scripts/ci-recovery.py`: when a recovery is open and the given head is green and is its first head or descends from it, close it (resetting the budget), else leave it open and say why. Done when: tests cover an interrupted success (including success on attempt four), a resume that settles it, and a new red recovery afterwards starting with a fresh budget of four. Cheaper substitute: a recovery left open that charges the next, unrelated failure.
- [x] Run `python scripts/ci-recovery.py settle <origin/main sha>` whenever reconciliation establishes the fetched newest head as green, at campaign start, phase start and every resume, before the dependency merge or any row, in `.claude/skills/process-plan/SKILL.md` and `.claude/skills/process-phase/SKILL.md`: when `--pending` exits 0, when it exits 1 but the newest head is green and the earlier red heads are superseded, and when a pending newest head turns green after the wait. Done when: both skills name the command, the three paths and its place before the merge. Cheaper substitute: relying on `close` running in the same session as the green result, or settling only on an all-green exit. **Groomed 2026-10-23:** completion finding 1.
- [x] Hold the settlement in `scripts/tests/test_skill_ci_gate.py`: obligations for `settle` on each of the three paths in `process-plan` and by reference in `process-phase`, placed before the dependency merge and before any row, each with a weakening fixture (settlement removed, or moved after the merge or the row) that fails, and the affected paragraph pins updated on purpose with every existing obligation kept. Done when: the suite passes and each weakened copy fails. Cheaper substitute: a recovery tool whose campaign wiring no test holds. **Groomed 2026-10-23:** completion finding 2.
- [x] Commit: `automations: settle an open CI recovery against green found at resume`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_ci_recovery.py"` and `python -m unittest discover -s scripts/tests -p "test_skill_ci_gate.py"` pass.

> **Verified:** 2026-10-23 | §21 | 1f31f669af94c23e7d3ad41fa432d6ca368a2d18
> **Review:** `docs/reviews/d00-t03-s21.json`

## 22. CI Reconciliation Past Limits

> **Started:** 2026-10-23T14:05:00Z

Filed 2026-10-23 from round 2 of D00 T03 §20's completion review (`docs/reviews/00-workspace/D00-T03-s20-completion.md`): §20 pages the workflow-runs endpoint filtered by `branch` and `event`, which GitHub caps at 1,000 results however it is paged ([List workflow runs for a workflow](https://docs.github.com/en/rest/actions/workflow-runs#list-workflow-runs-for-a-workflow)); §20's `total_count` check turns the cap into an honest exit 2, but past 1,000 push runs that exit repeats forever. And `--pending` gives discovery one 60-second call and the whole reconciliation 600 seconds, so a long history or a large unchecked backlog can run out of time on every try without making progress.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Page the unfiltered endpoint to its end, keeping progress in a checkpoint bound to its inputs. Done when: more than 1,000 matching runs are found over several tries.
2. Teach the campaign to continue a progressing reconciliation. Done when: both skills and the gate test hold it. **Groomed 2026-10-23:** completion findings 1 to 4.

- [x] Page the unfiltered `repos/<owner>/<name>/actions/workflows/ci.yml/runs?per_page=100` endpoint in `scripts/ci-status.py --pending` and keep runs with event `push` on branch `main` locally, reading to the endpoint's last page (no stop on dates: commit dates do not prove push order, and other branches share the pages), every request a bounded call of its own. Done when: a fixture that reproduces the server's 1,000-result cap on filtered queries finds every one of more than 1,000 matching runs through the unfiltered pages; fixtures with a delayed push, non-monotonic commit dates and pages holding only other branches or events still find every unchecked head; §17's first-run baseline and §20's empty-history and no-green cases hold; and a page that cannot be read exits 2. Cheaper substitute: the filtered query, which stops at 1,000, or a date cut-off that misses a late push. **Groomed 2026-10-23:** completion finding 4.
- [x] Keep reconciliation progress in `build/ci-reconcile.json` (gitignored, written temp-then-replace), bound to its inputs: the repository, the fetched `origin/main` head, the baseline and a digest of the outcome and pending records. On a later try with the same inputs it continues where it stopped; when the head or the records changed (a push, a merge, a repair, a new record), it keeps the runs already read (they do not change, except reruns, below) and refreshes from the first page until it meets a run it already holds, so new runs and heads are found without discarding the rest. Done when: fixtures with a new push and a new workflow run between tries find every head, omit none and report no early green, and a try with unchanged inputs reads no page twice. Cheaper substitute: a checkpoint reused after the history moved, or thrown away on every change. **Groomed 2026-10-23:** completion finding 2.
- [x] Store each settled head's result in the checkpoint with its run id, attempt and conclusion: a completed run's result (green or red) is reused while its run id and attempt are unchanged, a pending or unknown head is checked again on every try, and the final report prints every listed head's result, stored or new, with the aggregate exit computed over all of them. The checkpoint is deleted only by `python scripts/ci-status.py --pending <run file> --ack`, which the campaign runs after it has written the `ci-green` and `ci-superseded` records, so an interruption before the records keeps the finished work. Done when: fixtures cover an early red result followed by an interruption (reported and counted at the end), a pending head turning green on a later try, a rerun that changes a stored result, and an interruption before the records (the next try reports without re-reading). Cheaper substitute: settled heads that drop out of the final report or the exit code. **Groomed 2026-10-23:** completion finding 3.
- [x] Add a progressing result: `--pending` exits 4 when it saved progress (more pages read or more heads settled than the try before) but did not finish within its time, and 2 when a try makes no progress; in `.claude/skills/process-plan/SKILL.md` and `.claude/skills/process-phase/SKILL.md`, at campaign start, phase start and every resume, exit 4 is run again at once, before any row, without spending §15's one retry or §18's recovery budget, which still govern exit 2 and red heads. Done when: both skills name exit 4 and its handling, `scripts/tests/test_skill_ci_gate.py` holds it with a weakening that fails (pins updated on purpose), and a simulated-clock fixture where paging takes longer than one call's 60 seconds and settling the heads longer than one try's 600 seconds completes over at least three tries, each call still bounded. Cheaper substitute: restarting the whole reconciliation each try, or parking after the second. **Groomed 2026-10-23:** completion finding 1.
- [x] Commit: `automations: reconcile CI past the API's search cap and across tries`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_ci_status.py"` and `python -m unittest discover -s scripts/tests -p "test_skill_ci_gate.py"` pass.

> **Verified:** 2026-10-23 | §22 | e7ee628ea490a63dec6b9a174a080ec1ed79a9f1
> **Review:** `docs/reviews/d00-t03-s22.json`

## 23. CI Reconciliation After Deleted Runs

> **Started:** 2026-10-23T18:45:00Z

Filed 2026-10-23 from round 13 of D00 T03 §22's review (`docs/reviews/00-workspace/D00-T03-s22.md`): `scripts/ci-status.py` `Pages.forward` proves the scan complete only by comparing the runs it holds with the API's `total_count`. When a run already read is deleted while the pages are read, every older run moves up one place, the run that crosses a page boundary is never read, and the count still matches because the deleted run stays held, so an unrecorded push head on `main` can be left out of the report. A deleted run also breaks confirmation: `read_run` gets a 404 for a held run a stored result rests on, and every try then exits 2. The precondition is rare (someone deletes a workflow run during a reconciliation, or between its tries), but the results are a head reported as covered without being checked, or a reconciliation that never finishes.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Detect a shift across each page boundary the reader walks, in the forward scan and in the newest-page refresh, and read again what it skipped, however many pages the shift spans. Done when: fixtures that delete already-read runs mid-scan, one run or more than a page of them, still find every run. **Groomed 2026-10-23:** completion findings 1 and 2.
2. Treat a run the API reports gone as gone. Done when: a fixture whose settled head's run is deleted between tries finishes with that head settled again.

- [x] After reading forward page N+1 in `scripts/ci-status.py` `Pages.forward`, read the single run at page N's last position (`per_page=1&page=<100 N>`) and, when it is not the run held there, recover (next item) before going on; keep the id of the last run of the last page read in the checkpoint (`build/ci-reconcile.json`, checked by `well_formed`), so a boundary that spans two tries is checked too. Done when: a fixture with 300 runs that deletes a run already read, between pages and between tries, finds every remaining run, and a fixture without deletions reads one boundary run per page and no page twice. Cheaper substitute: the count comparison alone, which a deletion matches.
- [x] Recover from a shifted boundary in `scripts/ci-status.py` `Pages` by stepping back: read the previous page again, then the one before it, until a re-read page's first run is a run already held whose successor on the page before is also held (continuity re-established), so a shift of any size is recovered with calls bounded by the pages it spans; save the rewind position in the checkpoint so a recovery cut short by the deadline resumes, and count each recovery page as progress. Done when: a fixture deleting 150 already-read runs (more than a page) before the next page is read finds every remaining run, and a fixture cutting the recovery short finishes it on the next try. Cheaper substitute: re-reading only page N, which a shift of more than one page defeats. **Groomed 2026-10-23:** completion finding 2.
- [x] Apply the same boundary check and recovery to `scripts/ci-status.py` `Pages.newest`, the refresh every resumed try runs: each page after the first is checked against the one before it, and its stop condition (a page with nothing new or changed) counts only once that page's boundary checks out. Done when: a fixture with a completed checkpoint, more than one page of new runs and a deletion of an already-read run during the refresh finds every remaining head. Cheaper substitute: a refresh whose unchanged page hides a skipped new run. **Groomed 2026-10-23:** completion finding 1.
- [x] Remove a held run from the checkpoint in `scripts/ci-status.py` when `read_run` gets HTTP 404 for it, and settle again every listed head whose stored result rested on it (`look_up`, which reads the head's governing run as it is now); any other failure stays unknown. Done when: a fixture deleting a settled head's only run between tries reports that head as GitHub now does (pending or unknown with no run, or its older run's result) instead of exiting 2 on every try, and a fixture with a 502 still exits 2. Cheaper substitute: exiting 2 forever on a run that no longer exists.
- [x] Keep the listing right without the removed run in `scripts/ci-status.py` `unchecked_heads`: a head whose only run was removed is listed only through its records or as `origin/main`, as for any commit without a run, and a head with an older run is decided by that run. Done when: fixtures for both cases list the head as described.
- [x] Commit: `automations: reconcile CI through deleted runs`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_ci_status.py"` passes.

> **Verified:** 2026-11-08 | §23 | ae496065b9af82d2167fa80b76815cf274116c42
> **Review:** `docs/reviews/d00-t03-s23.json`

## 24. Resumable Newest-Page Refresh

> **Started:** 2026-11-08T10:25:00Z

Filed 2026-10-23 from round 2 of D00 T03 §23's completion review (`docs/reviews/00-workspace/D00-T03-s23-completion.md`): `scripts/ci-status.py` `Pages.newest`, the refresh every resumed try runs, keeps no state between tries. When a refresh that has read some pages of new runs is cut short by the deadline, and runs already read are deleted before the next try, that try's first page can hold only runs already held and stop the refresh as unchanged, while the deleted runs still held make the count match `total_count`; the new runs on the unread pages are never found. §23's boundary checks and rewind do not cover it, because no boundary was ever checked.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Keep an unfinished refresh in the checkpoint and finish it before the refresh may stop as unchanged. Done when: a fixture interrupting a refresh and deleting read runs before the next try still finds every new head.

- [x] Save an unfinished refresh in `build/ci-reconcile.json` from `scripts/ci-status.py` `Pages.newest`: the next page to read and the id of the last run of the last page read (its boundary anchor), written as each page is read and cleared when the refresh ends, and checked by `well_formed`. Done when: after a refresh cut short at page 3, the checkpoint names page 3 and page 2's last run, and after a finished refresh it names none.
- [x] Resume a saved refresh in `scripts/ci-status.py` `Pages.newest` before anything else in the next try: check the anchor's boundary as §23 does (recovering a shift by stepping back), then read on from the saved page; a first page with nothing new does not end the refresh while one is saved. Done when: a fixture with a completed checkpoint that gains 300 new runs, reads 200 of them, deletes the first 100 and runs out of time before page 3 finds every remaining head over the following tries. Cheaper substitute: restarting the refresh at page 1, whose unchanged first page ends it early.
- [x] Count each saved refresh page as progress in `scripts/ci-status.py`, so a refresh longer than one try exits 4, not 2. Done when: a fixture whose refresh needs more than one try's reads returns 4 until it finishes.
- [x] Commit: `automations: resume an unfinished CI refresh`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_ci_status.py"` passes.

> **Verified:** 2026-11-08 | §24 | 337058c6a8b385d1cc3927863d72e4028bcace22
> **Review:** `docs/reviews/d00-t03-s24.json`

## 25. Host Lock Baseline Across Policy Writes

> **Started:** 2026-11-10T16:14:00Z

Filed 2026-11-10 from a readiness failure on this PC: `python scripts/check-campaign-host.py` failed `screen lock` with "the machine lock policy changed since Windows started, so the inactivity limit in force is unknown", although `InactivityTimeoutSecs` was absent and the same boot had passed the check on 2026-11-08 (`docs/phase-runs/2026-10-22-phase-2.md`, the 19:26Z and 19:37Z resumes). `check_screen_lock` (§12) fails whenever anything has written the key `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System` since Windows started. That key also holds the User Account Control values and others that Windows and installers write (25 values on this PC, last written 2026-11-10, two days after Windows started), so a campaign meant to run for weeks parks with `host-not-ready` at its next phase start or heartbeat resume, and stays parked until the owner restarts Windows, for a write that never touched the limit. The remedy keeps §12's caution (a limit read when Windows starts may stay in force after its value is removed) and adds the evidence that settles it: a record, made while the key was still unwritten since this boot, that no limit was stored at this boot.

**Source:** Microsoft Learn, "Interactive logon: Machine inactivity limit" (<https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/interactive-logon-machine-inactivity-limit>, applies to Windows 10 and 11, `ms.date` 2018-09-18, updated 2026-04-27, opened 2026-11-10), under "Restart requirement": "Restart is required for changes to this policy to become effective when they're saved locally or distributed through Group Policy." And under "Possible values": "If **Machine will be locked after** is set to zero (0) or has no value (blank), the policy setting is disabled and a user sign-in session is never locked after any inactivity." The reading that holds is therefore: every change, a new limit and a removed one alike, takes effect at the next start. The steps below are safe under that reading and under the other one. Next start: a boot that began with no limit has none in force until Windows restarts, whatever is written to the key afterwards, and the baseline proves the boot began with none. At once: the limit in force is the stored one, and the accepting branch requires that none is stored now. Microsoft's documentation does not name the registry value; `InactivityTimeoutSecs` under `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System` is the value §12 already reads and the one found set on real PCs.

**Phase:** 0
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Record when a changed limit takes effect, from Microsoft's own documentation. Done when: this section carries a `**Source:**` line with the URL and the quotation.
2. Keep a per-boot baseline in `build/host-lock-baseline.json` and write it on every pass that proves the limit absent. Done when: a passing check on an unwritten key leaves a baseline naming this boot.
3. Accept a written key when the baseline is this boot's and no limit is stored now. Done when: the four baseline cases and the limit-present case are tested, and the check passes on this host.

- [x] Add a `**Source:**` line under this section's context stating what Microsoft's documentation of the "Interactive logon: Machine inactivity limit" policy says about when a changed `InactivityTimeoutSecs` takes effect, with its URL, the page's date and the quotation, gathered through `source-researcher` and opened by the main loop. Done when: the line names which reading holds (effective at once, or at the next start) and the steps below are safe under both. Cheaper substitute: asserting the restart rule from memory, as §12 did.
- [x] Add `Host.boot_id()` to `scripts/check-campaign-host.py`, returning the record number and time of this boot's start event (the Kernel-General 12 event `boot_clock` already reads) and raising `Unreadable` when the log no longer holds it. Done when: `scripts/tests/test_check_campaign_host.py` shows two reads of one fixture log agree and a log with a later start event gives a different id.
- [x] Add `Host.lock_baseline()` and `Host.record_lock_baseline()` to `scripts/check-campaign-host.py`, reading and writing `build/host-lock-baseline.json` (`schema_version`, `boot`, `recorded`), the write through a temporary file in `build/` then `os.replace`, read back afterwards. Done when: a test writes a baseline and reads it back equal, and a torn file, a foreign `schema_version` or a missing field reads as no baseline. Cheaper substitute: writing in place, or treating an unreadable file as a baseline.
- [x] Write the baseline in `check_screen_lock` on every run where `InactivityTimeoutSecs` is absent and `changed_since_boot(SYSTEM_POLICY)` is false. Done when: a fake host in that state leaves a baseline for its boot, and a host with the limit stored or the key written leaves none. **Corrected 2026-11-10:** two cases the item left open, decided before the build. (a) A run that finds this boot's baseline already recorded keeps it and does not write again, so `recorded` stays the first proof of this boot and two checks running side by side (the launcher and a heartbeat) do not race on the file; a test shows the second run leaves the file byte for byte. (b) A baseline that cannot be written (`OSError` from the temporary file or `os.replace`, or a read-back that differs) never fails the check, because the host is ready and a false park is the defect this section removes: the result stays `ok` and its detail ends "; the lock baseline could not be recorded: <reason>", so the next run tries again; a test shows it.
- [x] Make `Host.record_lock_baseline()` decide and publish under an exclusive lock on `build/host-lock-baseline.lock` (`msvcrt.locking` on Windows, `fcntl.flock` elsewhere; the operating system releases it when the process ends, so a crashed check leaves no stale lock), in this order: take the lock, waiting at most `LOCK_SECONDS` (5); read the baseline again; if it now names this boot, keep it and write nothing; otherwise write the temporary file, replace, and read back; release the lock. A lock not obtained in time raises `OSError`, which the check reports as "could not be recorded" and never as a failure. Done when: a test in which two recorders both saw no baseline and then record one after the other leaves the first one's `recorded` in the file and raises nothing, and a test holding the lock from a second handle shows `OSError` after the wait. Cheaper substitute: checking for a baseline before writing without a lock, which lets the second of two side-by-side checks overwrite the first proof or fail its read-back. **Groomed 2026-11-10:** completion finding 1 (round 1): the launcher and a heartbeat can both read "no baseline" before either publishes.
- [x] Correct the module docstring of `scripts/check-campaign-host.py`, which says "Every check only reads": name the one write, `build/host-lock-baseline.json`. Done when: the docstring names the file and says nothing else is written. **Added 2026-11-10** during plan validation: the statement would be false once the baseline exists.
- [x] Accept in `check_screen_lock` a key written since boot when `InactivityTimeoutSecs` is absent now and the baseline's `boot` is this boot's id, reporting `ok` with "no inactivity limit at this boot (recorded <UTC>) and none stored now". Done when: tests show a same-boot baseline passes, and no baseline, another boot's baseline and an unreadable baseline each fail with the restart fix as before. Cheaper substitute: dropping the written-since-boot check, which passes a limit removed after boot that may still be in force.
- [x] Keep the limit-stored branch of `check_screen_lock` unchanged whatever the baseline says. Done when: a test with a same-boot baseline and `InactivityTimeoutSecs` set still fails with the remove-and-restart fix.
- [x] State the baseline rule in the docstring of `check_screen_lock` and in the Host readiness paragraph of `.claude/skills/process-plan/SKILL.md` (one sentence: a policy-key write no longer parks a boot that has already passed). Done when: both name `build/host-lock-baseline.json`, and `python -m unittest discover -s scripts/tests -p "test_skill_ci_gate.py"` still passes.
- [x] Commit: `automations: keep a per-boot lock baseline for the host check`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_check_campaign_host.py"` passes, `python scripts/check-campaign-host.py` prints `ok    screen lock` on this host, and `build/host-lock-baseline.json` names this boot.

> **Verified:** 2026-11-10 | §25 | 88f88a9751d44cecc895d6d39f46136ad6df5855
> **Review:** `docs/reviews/d00-t03-s25.json`

## 26. Host Check Names Every File It Writes

> **Started:** 2026-11-10T16:34:00Z

Filed 2026-11-10 from §25's completion review (round 2, finding 1, `docs/reviews/00-workspace/D00-T03-s25-completion.md`): §25 makes the module docstring of `scripts/check-campaign-host.py` say that `build/host-lock-baseline.json` is the one file written and nothing else, but the same section also creates `build/host-lock-baseline.lock` (kept, never deleted) and, for the length of one write, a temporary file `host-lock-baseline.json.<random>.tmp` beside the baseline. A reader who trusts the docstring would treat the lock file as stray and delete it, or suspect a leak. This section makes the statement true and pins it. -> XREF: §25

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. State every write in the module docstring. Done when: `scripts/check-campaign-host.py` carries a "Files written" block with one line per file, each with where it is and how long it lives.
2. Pin the block with a test. Done when: removing or rewording any one line of the block fails `scripts/tests/test_check_campaign_host.py`.

- [x] Replace the "One file is written" sentence in the module docstring of `scripts/check-campaign-host.py` with a block headed "Files written (nothing else is):" that has exactly these five lines, in this order, each starting with the path: (1) `build/host-lock-baseline.json`: kept; the proof that this boot began with no inactivity limit. (2) `build/host-lock-baseline.lock`: kept, empty, never deleted; it serialises checks that run side by side. (3) `build/host-lock-baseline.json.<random>.tmp`: lives for one write of the baseline; removed when the write succeeds or fails; a check killed in the middle of the write, or a removal the system refuses, can leave one behind, and it is safe to delete while no check runs. (4) `<system temp>/campaign-host-<random>/` (`out`, `err`, `work/`): one probe's captured output and working folder; removed when the probe ends; a removal the system refuses (a descendant still holding a file) can leave the folder, safe to delete. (5) `<system temp>/campaign-notice-<random>/notice.json`: only with `--notify` after a failed check; the email's text handed to the sender; removed when the send ends. Done when: the docstring holds the block and the old sentence is gone. Cheaper substitute: deleting the "nothing else" claim, which leaves the lock file unexplained. **Groomed 2026-11-10:** completion findings 1 and 2 (round 1): the probe and notice scratch files of §12 are written in ordinary use, and a killed check or a refused removal can leave a temporary file, so the block covers both.
- [x] Add `test_the_docstring_lists_every_file_the_check_writes` to the `LockBaseline` class in `scripts/tests/test_check_campaign_host.py`: it holds the five expected lines word for word, takes the lines of the module docstring from the "Files written (nothing else is):" heading to the next blank line, and asserts they are equal to the heading followed by those five lines. Done when: the test passes, and deleting any one line, or changing one word of any lifetime, fails it. **Groomed 2026-11-10:** completion finding 3 (round 1): substring checks let an entry or a lifetime be removed unnoticed.
- [x] Add `test_a_recording_run_leaves_only_the_baseline_and_the_lock` to the same class: after one recording run on a fresh root the names in `build/` are exactly `host-lock-baseline.json` and `host-lock-baseline.lock`. Done when: the test passes and fails when `record_lock_baseline` no longer removes its temporary file after a successful write.
- [x] Add `test_a_probe_removes_its_scratch_folder` to the `Probe` class in the same file: it points `tempfile.tempdir` at a fresh folder, runs one real `Host().run` of `python -c "print(1)"`, and asserts the folder holds no `campaign-host-*` entry afterwards. Done when: the test passes and fails when `Host.run` keeps its scratch folder.
- [x] Commit: `automations: name every file the host check writes`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_check_campaign_host.py"` passes, and `python -c "import pathlib; t = pathlib.Path('scripts/check-campaign-host.py').read_text(encoding='utf-8').split('import argparse')[0]; print(all(n in t for n in ('Files written (nothing else is):', 'build/host-lock-baseline.lock', '.tmp', 'campaign-host-', 'campaign-notice-')), 'One file is written' in t)"` prints `True False`.

> **Verified:** 2026-11-10 | §26 | 85b53866520c9375ac99213be9fcf5b14affa670
> **Review:** `docs/reviews/d00-t03-s26.json`

## 27. Review Prompt Builder

> **Started:** 2026-11-10T16:45:00Z

Filed 2026-11-10 from the campaign run of that day (`docs/phase-runs/2026-11-10-phase-0.md`, Gap audit): every section needs two prompts, the completion review's (`docs/completion-review-prompt.md`, §13) and each code review round's (`docs/review-round-prompt.md`), and both are filled in by hand in a scratch file: the section text copied in, the `contract-digest` line pasted, the commit range written out, the diff inlined because the reviewer's sandbox cannot run git. The steps are mechanical and each has already gone wrong once (an argument order that gave an empty diff, `docs/phase-runs/2026-10-23-phase-0.md`, the 2026-10-23T20:10Z entry). The owner's instruction of 2026-11-10 is that the mechanics must be followed perfectly by a weaker executor, so the filling becomes one command per prompt that refuses what a hand would get wrong.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Build the completion prompt from a section reference. Done when: `python scripts/review-prompt.py completion '<ref>' ...` writes a prompt whose Contract line equals `contract-digest`'s output for that section.
2. Build a round prompt from a section reference and a commit range. Done when: `python scripts/review-prompt.py round '<ref>' <base> <tip> ...` writes a prompt holding both full SHAs, the section contract, the scope and the diff.
3. Point the skills at the two commands. Done when: `process-todo-section` step 3a and `review-todo-section` step 3 name them in place of the hand-filled scratch file.

- [x] Add `scripts/review-prompt.py` with the subcommand `completion <ref> --purpose <text> (--context <file> | --no-context <reason>) --out <path>`: it reads the template below the `---` line of `docs/completion-review-prompt.md`, fills the reference and title, the section text from its heading to its Test checkpoint, the `Contract:` line from `todo_graph.contract_digest`, the purpose, the file's Implementation Order table, and either the context file's text or the line "No further context: <reason>", and writes `--out` through a temporary file then `os.replace`. Done when: a test on a fixture tree shows the written prompt contains the section text and the same digest `contract-digest` prints. Cheaper substitute: leaving a placeholder unfilled, which the reviewer reads as an instruction.
- [x] Require the context a section's citations call for, in the `completion` subcommand: exactly one of `--context` and `--no-context` must be given (exit 2 with neither or both), and `--no-context` is refused (exit 2, naming what the section cites) when the section says `**Surface:** yes`, carries an `> **Implements:**` line or names `design/SPEC.md`, because such a section's excerpts must be inlined (`docs/completion-review-prompt.md`, "Context to read"). Done when: tests show a tooling section passes with `--no-context`, a section citing `design/SPEC.md` is refused with `--no-context` and passes with `--context`, and neither option is exit 2. **Groomed 2026-11-10:** completion finding 4 (round 1): an optional context let a surface section go to review without its SPEC excerpts.
- [x] Add the subcommand `round <ref> <base> <tip> --purpose <text> --governing <text> [--note <file>] [--path <path> ...] --out <path>` to `scripts/review-prompt.py`: it resolves both commits to full SHAs, inlines `git diff <base>..<tip>` (of the `--path` arguments when given) and the section as `resolve` prints it, and fills `docs/review-round-prompt.md` below its `---` line. Done when: a test on a fixture repository shows both 40-character SHAs, the diff and the section in the prompt. Cheaper substitute: naming the range without the diff, which a reviewer whose sandbox cannot run git cannot read.
- [x] Refuse a range that does not run forward, in the `round` subcommand: `<base>` must be an ancestor of `<tip>` (`git merge-base --is-ancestor`) and a different commit; a reversed range, a divergent one and `<base>` equal to `<tip>` each exit 2 with a reason that says which. Done when: tests on a fixture repository with three commits of different trees and a side branch show the forward range passing and the reversed, divergent and equal ranges refused. Cheaper substitute: refusing only an empty diff, which a reversed range does not give (its patch is the same changes with additions and deletions swapped). **Groomed 2026-11-10:** completion finding 1 (round 1).
- [x] State the scope in every round prompt, in a `## Scope` block the `round` subcommand writes above the diff: the changed paths of the whole range (`git diff --name-only <base>..<tip>`), split into "Included in this prompt" and "Not in this prompt (review them in another round part)", with the sentence "This prompt covers only the included paths." when any path is omitted; and print the same two lists as JSON on standard output (`{"base", "tip", "included", "omitted", "out"}`). Done when: a test on a range changing a script and its test with `--path` naming only the test shows the script under "Not in this prompt", in the JSON `omitted` list, and absent from the diff. Cheaper substitute: filtering the diff silently, which lets a partial review pass for a whole one. **Groomed 2026-11-10:** completion finding 2 (round 1).
- [x] Keep the inlined diff bounded in the `round` subcommand: the diff actually inlined (whole, or of the `--path` arguments) is measured, and one over `MAX_DIFF_BYTES` (400,000) is refused with exit 2, naming its size, the limit and the `--path` option, and `--out` is not written. Done when: tests with a small limit show the whole diff refused, a `--path` selection under the limit written, and a `--path` selection still over the limit refused. Cheaper substitute: truncating the diff, which hides the code under review. **Groomed 2026-11-10:** completion finding 3 (round 1): the filtered diff had no second check.
- [x] Check the whole template before any substitution, in both subcommands: `PLACEHOLDERS` in `scripts/review-prompt.py` lists, per template, every backticked span that contains `<` (the ones the command fills and the ones that stay as the reviewer's reply format), and a template whose spans are not exactly that list (one added, one removed, one reworded) is refused with exit 2 naming the first difference. Only the template is scanned, never the inserted section or diff, so angle brackets in them are kept as they are. Done when: tests show the two real templates accepted, a template with an added placeholder and one with a removed placeholder each refused, and a section body containing `<x>` written through unchanged. **Groomed 2026-11-10:** completion finding 5 (round 1): checking only for missing placeholders let a new template field reach the reviewer unfilled.
- [x] Refuse, with exit 2 and a one-line reason on standard error, in both subcommands: a reference `todo_graph.extract_ref` does not resolve; a commit git does not know; and a `--out` path inside the repository (prompts are scratch files). Done when: one test per refusal shows exit 2, the reason, and that `--out` was not written.
- [x] Replace the hand-filling instructions in `.claude/skills/process-todo-section/SKILL.md` (step 3a.2) and `.claude/skills/review-todo-section/SKILL.md` (step 3) with the exact command for each prompt, its arguments in order, what each exit code means (0 written, 2 refused with the reason on standard error), the rule that `--no-context` is only for sections with no SPEC or inventory citation, and the rule for a split round: when the JSON `omitted` list is not empty, build and dispatch one more part with `--path` for the omitted paths, until every changed path has been in one part, and only then is the round complete. Done when: both skills name `scripts/review-prompt.py`, the split rule is in `review-todo-section`, and `python -m unittest discover -s scripts/tests -p "test_skill_ci_gate.py"` still passes. **Groomed 2026-11-10:** completion findings 2 and 4 (round 1).
- [x] Add `scripts/tests/test_review_prompt.py` covering the items above, with fixture trees and repositories under a temporary folder and no reviewer run. Done when: `python -m unittest discover -s scripts/tests -p "test_review_prompt.py"` passes and `python scripts/check-spdx.py` accepts the two new files.
- [x] Commit: `review: build the completion and round prompts with one command each`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_review_prompt.py"` passes, and `python scripts/review-prompt.py round 'D00 T03 §27' HEAD HEAD --purpose x --governing y --out <scratch>\p.md` exits 2 with a reason saying the base and the tip are the same commit.

> **Verified:** 2026-11-10 | §27 | da8f9f18455e3ab2f0745239691599898ac7bccd
> **Review:** `docs/reviews/d00-t03-s27.json`

## 28. Host Check Scratch Leftover Rule

> **Started:** 2026-11-10T17:08:00Z

Filed 2026-11-10 from §26's completion review (round 2, finding 1, `docs/reviews/00-workspace/D00-T03-s26-completion.md`): the "Files written" block §26 puts in the module docstring of `scripts/check-campaign-host.py` says the notice file is "removed when the send ends" and explains a leftover only for the baseline's temporary file and, in part, for the probe folder. All three temporary entries share the same two exceptions: a check that is killed before its cleanup runs, and a removal the system refuses (`ignore_cleanup_errors=True` in `Host.run` and `Host.notify`, the suppressed `OSError` in `Host.record_lock_baseline`). Stating the exceptions entry by entry is how one was missed, so this section states the rule once, for every temporary entry, and keeps the per-entry lines to the normal lifetime. -> XREF: §26

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. State the leftover rule once in the block. Done when: the block's last line covers every temporary entry and no entry repeats it.
2. Pin the new block. Done when: the word-for-word test of §26 expects the new text and passes.

- [x] Shorten entries 3, 4 and 5 of the "Files written (nothing else is):" block in the module docstring of `scripts/check-campaign-host.py` to their normal lifetime: (3) `build/host-lock-baseline.json.<random>.tmp`: temporary; lives for one write of the baseline. (4) `<system temp>/campaign-host-<random>/` (`out`, `err`, `work/`): temporary; one probe's captured output and working folder, removed when the probe ends. (5) `<system temp>/campaign-notice-<random>/notice.json`: temporary; only with `--notify` after a failed check; the email's text handed to the sender, removed when the send ends. Done when: none of the three lines mentions a leftover. Cheaper substitute: adding a leftover clause to the one entry the review named, which leaves the next entry added without one.
- [x] Add a sixth and last line to the block: "- Leftovers: every entry marked temporary is removed in normal use; a check that is killed, or a removal the system refuses, can leave one behind, and a leftover is safe to delete once the check and its child processes have stopped." Done when: the line is the block's last, directly above the blank line that ends the block.
- [x] Update `WRITTEN` in the `LockBaseline` class of `scripts/tests/test_check_campaign_host.py` to the new six lines after the heading, word for word, and add to `test_the_docstring_lists_every_file_the_check_writes` the assertion that every entry line containing `<random>` contains "temporary;" and that the last line starts "- Leftovers:". Done when: the test passes, and fails when "temporary;" is removed from one entry or the Leftovers line is deleted.
- [x] Commit: `automations: state the leftover rule for the host check's scratch files once`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_check_campaign_host.py"` passes, and `python -c "import pathlib; t = pathlib.Path('scripts/check-campaign-host.py').read_text(encoding='utf-8').split('import argparse')[0]; print(t.count('temporary;'), t.count('- Leftovers:'))"` prints `3 1`.

> **Verified:** 2026-11-10 | §28 | 295a4a337b37e3933f37e2d9335b98160f4490d8
> **Review:** `docs/reviews/d00-t03-s28.json`

## 29. Review Prompt Empty-Input Refusals

> **Started:** 2026-11-10T22:21:45Z

Filed 2026-11-10 from §27's completion review (round 2, findings 1 and 4, `docs/reviews/00-workspace/D00-T03-s27-completion.md`): §27 refuses a range whose base and tip are one commit or run backwards, but a forward range can still hold nothing to review (a commit followed by its revert leaves identical trees, and a mistyped `--path` selects no file), and a `--context` file can exist and be empty, which hands a surface section to the reviewer with none of its excerpts. An input that is present and empty is refused like one that is missing. -> XREF: §27

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Refuse a round with nothing to review. Done when: a commit-then-revert range and a `--path` that selects no changed file each exit 2.
2. Refuse empty text inputs. Done when: an empty or whitespace-only `--context`, `--note`, `--purpose`, `--governing` or `--no-context` exits 2.

- [x] Refuse in the `round` subcommand of `scripts/review-prompt.py` a range that changes no path (`git diff --name-only <base>..<tip>` prints nothing), with exit 2 and a reason that says the range changes no file. Done when: a test on a fixture repository with a commit and its revert shows exit 2 and the reason. Cheaper substitute: relying on the ancestry check, which a commit and its revert pass.
- [x] Refuse in the `round` subcommand a `--path` selection that matches no changed path, with exit 2 and a reason that lists the changed paths. Done when: a test with a mistyped path shows exit 2 and the real paths in the reason.
- [x] Refuse in both subcommands an empty or whitespace-only value: the files `--context` and `--note`, and the texts `--purpose`, `--governing` and `--no-context`, each with exit 2 and a reason naming the option. Done when: one test per option shows exit 2 and the option's name in the reason. Cheaper substitute: checking only that the option was given, which an empty scratch file satisfies.
- [x] Keep an existing `--out` file byte for byte on every refusal above. Done when: each test above first writes `--out` with known bytes and reads the same bytes back after the refusal.
- [x] State in `.claude/skills/process-todo-section/SKILL.md` step 3a.2 that the context file must hold the excerpts the section cites, copied in by the main loop, and that the command only checks it is not empty. Done when: the sentence is there and `python -m unittest discover -s scripts/tests -p "test_skill_ci_gate.py"` still passes.
- [x] Commit: `review: refuse empty ranges and empty inputs in the prompt builder`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_review_prompt.py"` passes, with the tests named above among them.

> **Verified:** 2026-11-11 | §29 | b6fe3a1d06839c751a4f902673ef2088b52b6bd0
> **Review:** `docs/reviews/d00-t03-s29.json`

## 31. Plan Lists Files Still to Author

> **Started:** 2026-11-10T23:40:00Z

**Corrected 2026-11-11:** the tree now holds 161 sections (it said 132) and 84 `Author` items naming 84 distinct paths, none on disk (it said 83); the authoring sections are D03 T01 §17 to §27 and also D00 T03 §39, whose one `Author` item names `todo/00-workspace/TODO-06-parallel-streams.md`. The checklist below is unchanged: it already reads every section, not only D03 T01.

Filed 2026-11-10 (owner: "the todo plan file is not complete"). `todo/implementation-plan.md` lists only sections that exist. The whole product (the shared platform, the engines, the six apps, interoperability, VBA and release) is written into the tree later by the authoring sections D03 T01 §17 to §27, whose checklist items each begin with `Author` and a backticked `todo/<domain>/TODO-NN-<name>.md` path: 83 files on 2026-11-10, none of which the plan shows. A reader sees 132 sections and cannot tell that most of the road is not in the file yet, or which row will put it there. This section makes the plan say so: every TODO file an `Author` item names that is not on disk is listed with the section that authors it, and the progress line counts them. The block is derived from the sections, like the rest of the plan, and empties itself as the files are authored.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Collect the files still to author in `scripts/lib/todo_graph.py`. Done when: a fixture section with two `Author` items, one file on disk, yields the other.
2. Render them in the plan. Done when: `plan --sync` writes the block and `plan --check` fails when it is stale.
3. Refuse a ticked `Author` item whose file is missing. Done when: `validate` exits 2 naming the item's section and path.

- [x] Add `to_author(root)` to `scripts/lib/todo_graph.py`: for every section, read the checklist items that match `Author` followed by a backticked path of the form `todo/<domain>/TODO-NN-<name>.md`, and return each path that is not a file, with the reference of the section that names it, in plan order. Done when: tests in `scripts/tests/test_todo_graph.py` show a missing path returned with its `DNN TNN §N`, a path that exists left out, and an `Author` item naming a path of another form ignored.
- [x] Refuse in `validate` a path named by the `Author` items of two different sections, naming both. Done when: a fixture with the same path in two sections exits 2 with both references. Cheaper substitute: listing it twice, which leaves two sections to write one file.
- [x] Refuse in `validate` a ticked `Author` item whose path is not a file, naming the section and the path. Done when: a fixture with `- [x] Author` and no file exits 2, and the same fixture with the file present validates.
- [x] Render a `### Still to author` block in `projection()` after the last phase table and before the progress line: one sentence saying these TODO files do not exist yet and that their sections and checklist items are not in the totals, then a table with the columns `File`, `Authored by` and `Status` (the authoring section's box), one row per file. Done when: a test on a fixture tree shows the block with one row per missing file, and no block at all when nothing is missing. Cheaper substitute: a hand-written list in `todo/README.md`, which drifts from the sections.
- [x] Hold the block's table to `MAX_TABLE_ROW` like the phase tables, naming the path that is too long in the refusal. Done when: a fixture path that makes a row longer than the limit is refused by `plan --sync` with that path in the message.
- [x] Add the count to the progress line: after the verified and ready counts, `N TODO files still to author (not counted here)` when N is above zero, and nothing when it is zero. Done when: a test shows the phrase with the fixture's count and its absence on a tree with no missing file.
- [x] Add `to_author` (the count) to the JSON `query stats` prints. Done when: `python scripts/todo-graph.py query stats` on this repository shows `"to_author": 83`, or the number the tree holds on the day this runs, equal to the block's row count.
- [x] Document the block in `todo/README.md` under "The Implementation Order table is the dependency graph": what an `Author` item is, that the plan lists its file until the file exists, and the two refusals. Done when: the README names the block, the item form and both refusals.
- [x] Run `python scripts/todo-graph.py plan --sync` and commit the regenerated `todo/implementation-plan.md`. Done when: the plan holds the block and `python scripts/todo-graph.py plan --check` exits 0.
- [x] Commit: `todo: list the files still to author in the plan`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_todo_graph.py"` passes with the tests named above among them, and `python scripts/todo-graph.py plan --check` exits 0 with a `### Still to author` block in `todo/implementation-plan.md`.

> **Verified:** 2026-11-11 | §31 | 8a201b673a65c70aae2d731ec673d6b199dc207f
> **Review:** `docs/reviews/d00-t03-s31.json`

## 32. Validate Checks Plan Row Width

> **Started:** 2026-11-10T23:50:00Z

**Corrected 2026-11-11:** since D00 T03 §31 (stamped at 2a7d326) the plan has a second table, `### Still to author`, whose row width `plan --sync` also measures alone (the refusal "still-to-author table wraps raw md"); the measurement this section moves into `validate` covers both tables, and the new fourth item says so. The finding's `file:line` reads `scripts/lib/todo_graph.py:523` from before §31 moved the code.

Filed 2026-11-10 from `todo/findings.md` (the entry of 2026-11-10). `validate` accepts a section title that `plan --sync` then refuses with "plan table for phase N wraps raw md", because a plan row's width depends on the widest title and the widest Needs cell of the whole phase, which only the plan renderer measures (`projection()` in `scripts/lib/todo_graph.py`). A commit can therefore pass `validate` and leave the plan unsyncable, which stops an unattended run at its next sync. `validate` runs the same measurement.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Move the row-width measurement into one function both commands call. Done when: `validate` and `plan --sync` refuse the same fixture with the same message.

- [x] Extract the phase table's width check from `projection()` in `scripts/lib/todo_graph.py` into a function that takes a phase's rows and raises the existing refusal. Done when: `projection()` calls it and the existing plan tests still pass.
- [x] Call that function for every phase from `validate`. Done when: a test in `scripts/tests/test_todo_graph.py` with a title of legal length (at most 88 characters) that makes its phase's plan row longer than `MAX_TABLE_ROW` shows `validate` exiting 2 with the message that names the section. Cheaper substitute: lowering the title limit for every section, which refuses titles that fit.
- [x] Assert in the same test that `plan --sync` refuses the fixture with the same message. Done when: both messages are compared for equality.
- [x] Run the `### Still to author` table's width check (D00 T03 §31) from `validate` through the same kind of shared function. Done when: a test in `scripts/tests/test_todo_graph.py` with an `Author` path that makes that table's row longer than `MAX_TABLE_ROW` shows `validate` and `plan --sync` refusing it with the same message, which names the path.
- [x] Strike the finding in `todo/findings.md` as shipped by this section. Done when: the entry ends with this section's reference and the word shipped.
- [x] Commit: `todo: validate refuses a title the plan cannot render`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_todo_graph.py"` passes with the new test among them, and `python scripts/todo-graph.py validate` exits 0 on this repository.

> **Verified:** 2026-11-11 | §32 | 3060e0dd0eb5a79288bbf0e42c84c468016285df
> **Review:** `docs/reviews/d00-t03-s32.json`

## 33. Plan Groups a Phase by Domain

> **Started:** 2026-11-12T00:30:00Z

> **Started:** 2026-11-11T22:10:50Z

Filed 2026-11-10 (owner: "a Word phase with the entire Word dev in it"). The plan renders one table per phase, in dependency order. Phase 5 (Applications) will hold all six apps, several thousand sections once D03 T01 §19 to §24 author them, so Write's rows would be interleaved with Grid's and Mail's and nobody could read "all of Word" in one place or see how far it is. This section renders a phase that spans more than one domain as one block per domain (`06-write`, `07-grid` and so on), each with its own heading, counts and progress, so the whole of Write is one contiguous part of the plan. Phases stay as they are: the phase list is closed (`todo/README.md`) and run order still comes from the dependency graph, so this changes how the plan reads, not what runs when.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Group a phase's rows by domain in `projection()` in `scripts/lib/todo_graph.py`. Done when: a fixture phase with two domains renders two headed tables and a single-domain phase renders as today.
2. Name the domains. Done when: each heading shows the domain's name from `todo/plan.json`.

- [x] Add an optional `domains` object to `todo/plan.json`, read by `plan_config()` in `scripts/lib/todo_graph.py`, mapping a domain folder (`06-write`) to its display name (`Write (Word)`); refuse a key that is not a folder under `todo/` and an empty name. Done when: tests in `scripts/tests/test_todo_graph.py` show both refusals and a tree without the key rendering folder names. Cheaper substitute: names typed into the renderer, which a new domain would not get.
- [x] Render, for a phase whose rows come from more than one domain, one `#### <domain name>` heading per domain in domain-number order, each followed by a line with its section count, checklist item count and verified count, and its own table with the rows in plan order. Done when: a fixture phase with two domains shows two headings, each table holding only its domain's rows, and the counts of the two adding up to the phase line. Cheaper substitute: sorting the one table by reference, which still gives no per-app progress. **Corrected 2026-11-12:** the plan review (gap 2) asked for exact proof: a test asserts every row kept once, the domain order, the plan order inside each domain, and each domain's section, checklist and verified counts on a phase with verified and open rows.
- [x] Keep a phase whose rows all come from one domain exactly as it renders today. Done when: a test compares the fixture's single-domain phase byte for byte with the output before this change.
- [x] Apply the row-width check of §32 to each domain table on its own. Done when: a fixture with one over-wide title is refused naming that section, and the shared function is the one §32 extracted. **Corrected 2026-11-12:** the plan review (gap 1) found the item silent on `validate`: `_plan_tables_ok()` builds the same grouped tables `projection()` renders, so a fixture whose two domain tables each fit but whose combined table would not is accepted by both `validate` and `plan --sync`, and an over-wide domain table gets the same refusal from both.
- [x] Group the `### Still to author` block of §31 the same way, one `#### <domain name>` heading per domain with its files under it, each table refused on its own width. Done when: a fixture with missing files in two domains shows both headings in the block, each file under its destination domain with its file, authoring reference and status cells as before, and a test shows a one-domain block without a heading and a domain not on disk under its folder name. **Corrected 2026-11-12:** a block whose files all sit in one domain renders as today, the same rule as a phase; a domain not yet on disk (a file still to author creates it) shows its folder name until `todo/plan.json` names it.
- [x] Add the names of the domains that exist today to `todo/plan.json` (`00-workspace` to `03-architecture`), and state in the authoring contract paragraph of D03 T01 §17 that each authoring section adds its domain's name to `todo/plan.json`. Done when: `python scripts/todo-graph.py plan --sync` renders the names and the §17 paragraph names the file and the key.
- [x] Document the grouping and the `domains` key in `todo/README.md` beside the `todo/plan.json` description. Done when: the README names the key, the heading form and the single-domain rule.
- [x] Run `python scripts/todo-graph.py plan --sync` and commit the regenerated `todo/implementation-plan.md`. Done when: `python scripts/todo-graph.py plan --check` exits 0.
- [x] Commit: `todo: group each phase of the plan by domain`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_todo_graph.py"` passes with the tests named above among them, and `python scripts/todo-graph.py plan --check` exits 0.

> **Verified:** 2026-11-12 | §33 | 0eba903ac6915a0591905e72ee06d9b54040b5d0
> **Review:** `docs/reviews/d00-t03-s33.json`

## 35. Weekly Owner Digest

> **Started:** 2026-11-11T07:10:00Z

**Corrected 2026-11-11:** since D00 T03 §50 a section can be withdrawn; a withdrawn section is waiting on nobody and is left out of the waiting part and its dependant counts, and the totals come from `query stats`, which already leaves withdrawn sections out of `total` and reports them under `withdrawn` (the digest shows that count too). README's "exactly three kinds" of email becomes four with this digest.

Owner decision 2026-11-10 (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 32): the run never waits on the owner and never interrupts the owner. It works around every item only the owner can do, and once a week one email says what was built and what is waiting, with the exact steps for each waiting item. The owner's choice of this digest is the standing permission to send it (`AGENTS.md`, Safety, asks once before mail); it covers this one weekly email and nothing else. The digest is built by a script from the tree, so it costs no model tokens and says the same thing whoever runs it.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `scripts/owner-digest.py`. Done when: `--dry-run` prints the digest from this repository.
2. Send it weekly through the automations. Done when: the task is in `tasks.json` and the README, and a dry run of the task prints the email.

- [x] Write the progress part of `scripts/owner-digest.py`: from `python scripts/todo-graph.py query stats` and the stamp dates in the receipts under `docs/reviews/`, the sections verified in the last seven days (reference and title), the totals verified, ready and blocked, and the number of TODO files still to author (§31). Done when: a test in `scripts/tests/test_owner_digest.py` over a fixture tree with two receipts inside the week and one outside lists the two.
- [x] Add an `**Owner action:**` field to the TODO format in `scripts/lib/todo_graph.py`: the exact steps the owner takes and where the answer is recorded, required by `validate` on every open, non-withdrawn section whose Needs include `operator`, `owner-decision`, `third-party` or `store-account`, and refused elsewhere. Done when: tests in `scripts/tests/test_todo_graph.py` show both refusals, and `todo/README.md` (What every section declares) names the field. **Groomed 2026-11-11:** completion finding 1 (a section's first paragraph says why, not what to do).
- [x] Write the owner action of each of the six sections that need one today (D00 T02 §3 and §4, D01 T01 §4, §7 and §8, D01 T03 §5), each from the section's own checklist and Needs. Done when: `python scripts/todo-graph.py validate` exits 0.
- [x] Write the waiting part: every open, non-withdrawn section whose Needs include `operator`, `owner-decision`, `third-party` or `store-account`, with its reference, its title, its Needs, its `**Owner action:**` text, and how many open sections depend on it directly or through others. Done when: a fixture with one such section and two dependants lists it with its owner action and the count 2. Cheaper substitute: the list of references alone, which sends the owner into the TODO files to learn what to do.
- [x] Order the waiting part by the number of dependants, largest first, and say `Nothing is waiting on you.` when it is empty. Done when: tests show the order and the empty form.
- [x] Add the state of the run, from the run guard and the newest run file together: `Running` (with the run id and the phase) while `build/claude-campaign-guard.json` exists; otherwise, from the newest file under `docs/phase-runs/`, `Completed` for a `## Closeout run=` heading, `Parked` with the reason of a column-0 `PARKED` line, `Stopped by the operator` for an operator stop recorded in its Critical events, and `Not running` with the date of the last commit when it shows none of these; `Unknown` with the reason when the files cannot be read. Done when: tests cover each state, the operator stop as `docs/phase-runs/2026-11-11-phase-0.md` records it included. **Groomed 2026-11-11:** completion finding 2.
- [x] Add the state of CI for `origin/main`'s head, from `python scripts/ci-status.py <that sha>`, reported as green, red (with the failing jobs it names), pending or unknown (with the reason, when `gh` or the fetch cannot be read), never an error that stops the email. Done when: tests with a replaced runner cover all four. **Groomed 2026-11-11:** completion finding 3 (the command needs a commit).
- [x] Keep the email body to plain text of at most 120 lines, with no line over 100 characters, and no secret or path outside the repository, keeping the run state, CI, totals and the first waiting items in the body and putting the whole waiting list, every item with its owner action, in a plain-text attachment whenever the body cannot hold it, with a last body line that names the attachment and how many items it adds. Done when: a test with 300 fixture waiting sections shows the cut body and an attachment holding all 300. **Groomed 2026-11-11:** completion finding 4.
- [x] Send the digest through the transport of `.conclave/automations/alert.py` (the same sender and recipient), with the attachment when there is one, and `--dry-run` printing it and sending nothing. Done when: a test with a replaced opener shows one request with the digest as its body (and the attachment when the list overflows), and `--dry-run` makes none.
- [x] Add the task `office-owner-digest` to `.conclave/automations/tasks.json` (weekly, Monday 07:00, timeout 5 minutes) and to `.conclave/automations/README.md`. Done when: `python scripts/tests/test_automations.py` passes, which fails when the README and `tasks.json` disagree.
- [x] Register the task on this PC with `pwsh .conclave/automations/install.ps1`. Done when: `Get-ScheduledTask -TaskPath '\Office\'` lists `office-owner-digest`.
- [x] Commit: `automations: send the owner one weekly digest`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_owner_digest.py"` passes, and `python scripts/owner-digest.py --dry-run` prints a digest for this repository and exits 0.

> **Verified:** 2026-11-11 | §35 | b1f45263b1f9f448811af0487ec4c7a23b30e922
> **Review:** `docs/reviews/d00-t03-s35.json`

## 36. Operating Mode Measurement Command

> **Started:** 2026-11-11T20:49:27Z

Owner decision 2026-11-10 (decision 30): which model leads, and whether it works alone or orchestrates workers, is decided by measurement and never by opinion or by asking. The first measurement ran from a scratch script on 2026-11-10 (three sections, each built by Fable alone, by Opus alone and by Fable orchestrating, in separate local clones from one commit, each result gated and reviewed blind); its record is `docs/reviews/operating-mode-2026-11-10.md`. This section makes that a command in the repository, so it can be run again without anyone rewriting it.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `scripts/measure-modes.py`. Done when: a run against a fake `claude` builds every arm in its own clone and writes the results file.
2. Bound it. Done when: a run that hangs or floods its output is stopped with its whole process tree.

- [x] Write the arm table in `scripts/measure-modes.py`: each arm has a name, the model alias, whether subagents are allowed and the instruction added to the task; the arms are `opus-alone` and `fable-alone`; the packet-routing arm measured on 2026-11-10 (`orchestrated`) lost on cost and quality and is not kept. Done when: a test in `scripts/tests/test_measure_modes.py` reads the two arms and refuses a duplicate name. **Corrected 2026-11-11:** this named a third arm, `opus-writer` (an Opus lead handing the build to the Opus `section-writer`); the owner removed that agent and made the main session the writer (decision 40), so every arm works alone.
- [x] Take the sections as `run --section "<ref>"` (repeated, at least one) and resolve each with `scripts/todo-graph.py resolve` run inside a clone at `--base`, so the task text is the section as that commit has it, never the working checkout's; a reference that does not resolve to an open, ready section (exit other than 0) is refused with exit 2 and its reason before any session starts, and `--help` shows a complete invocation. Done when: tests show the refusal for an unknown and a stamped section, and every arm of a section receiving byte-identical task text taken from the base commit. **Corrected 2026-11-11:** added after the plan review (gap 5): the section input was never defined.
- [x] Clone the repository once per arm and section into the folder `--work` names (under the scratch folder by default), at the commit `--base` names, with no remote, under folder names that do not reveal the arm. Done when: a test on a fixture repository shows the clones, no `origin` in any, and a name mapping only in the results file. Cheaper substitute: git worktrees of the working repository, which a session could push from or damage.
- [x] Start each arm as a headless session with the task text on standard input, JSON output, a per-run spending limit (`--budget`, default 40) and a per-run time limit (`--minutes`, default 75), at most `--parallel` (default 3) at a time. Done when: a test with a fake `claude` on `PATH` records each invocation's arguments and standard input, and a test whose fake records its start and end shows no more than `--parallel` sessions overlapping. **Corrected 2026-11-11:** the plan review (gap 6) found the limit of three unproven; it is now a flag with a behavioural test.
- [x] Write `scripts/lib/process_tree.py`, one contained start for any child: on Windows the child starts suspended inside a kill-on-close job object and is resumed once it is in the job, elsewhere it leads its own process group; `end()` stops every member and reports how many were still running. Done when: `scripts/tests/test_process_tree.py` shows a child and its grandchild both gone after `end()`, and the count of strays. **Corrected 2026-11-11:** added; the repository holds three private copies of this containment (`scripts/check-campaign-host.py` `Containment`, `scripts/review-dispatch.py` `run`, `scripts/run-tests.py`), and a fourth is not written: the measurement uses the shared one, and moving the three onto it is filed as §54.
- [x] Stop the whole process tree of a run that passes its time limit or whose output files pass 50 MB, and stop anything still running from a clone when its run ends. Done when: a test with a fake `claude` that starts a child and sleeps shows neither process alive after the limit, and a test whose fake floods its output shows it stopped at the size limit with its child gone. Cheaper substitute: `subprocess.run(timeout=...)`, which kills one process and leaves its children (the 2026-11-08 incident in the global rules). **Corrected 2026-11-11:** the flood test added after the plan review (gap 6).
- [x] Bind each result to a commit before it is judged: after every session the harness records the clone's `HEAD` as the candidate, and a clone with uncommitted or untracked changes counts as a failed `clean-tree` gate (the harness never commits for the arm), so the gates and the review always read the same tree. Done when: a test whose fake leaves an untracked file shows `clean-tree` failed and the candidate recorded. **Corrected 2026-11-11:** added after the plan review (gap 1): nothing bound the gated tree to the reviewed range.
- [x] Run the gates in each clone from the harness, never from the measured session: `python scripts/todo-graph.py validate`, `python scripts/todo-graph.py plan --check` and `python scripts/run-tests.py`, each log kept and each stopped with its process tree after `--gate-minutes` (default 45). Done when: a test shows the three results per run in the results file, and a hung gate recorded as stopped. **Corrected 2026-11-11:** the gate time limit added after the plan review (gap 6).
- [x] Review each result blind through `scripts/review-dispatch.py` with one fixed prompt that names only the range and the section, and record the highest severity and the counts per severity; a pass is a review only when the dispatcher exits 0 with a reviewer and a `HIGHEST:` line, and anything else (exit 1, exit 2, unreadable output, a reply without the line) is recorded as `unreviewed` with its reason, tried once more, and never counted as approval. Done when: a test with a fake reviewer shows the parsed verdict, the prompt contains no arm name, and empty, malformed, failed and incomplete replies each end `unreviewed`. **Corrected 2026-11-11:** the no-review handling added after the plan review (gap 2).
- [x] Run the fix rounds: while a result is not approved (its newest review has a `P1` or `P2`, or a gate failed, `clean-tree` included), start the same arm in the same clone with the review file, the failed gates' log tails and the instruction to verify and fix, run the gates, and review the whole candidate blind again, up to `--fix-rounds` (default 6), recording each round's cost, gates and review; a result is approved only when every gate passes and the review on that same candidate has no `P1` or `P2`. Done when: a test with a fake `claude` and a fake reviewer that approves on the second round shows two fix rounds recorded and a third not started, and a test with a clean review and a failing gate shows a fix round started. **Corrected 2026-11-11:** gate failures feed the loop after the plan review (gap 3).
- [x] Add `clean`, which removes only the clones the results file lists as this measurement's (each under the work folder), once the record is written, and refuses with exit 2 while a run holds the work folder's lock (`run` holds it for its whole life, across separate invocations). Done when: a test shows the listed clones gone, an unlisted folder beside them and the results file and logs kept, and the refusal while the lock is held. Cheaper substitute: leaving the clones in scratch, which is how gigabytes of stale copies pile up. **Corrected 2026-11-11:** the owned-clone inventory and the lock added after the plan review (gap 7).
- [x] Write `results.json` after every stage through a temporary file and `os.replace`, with the measurement's identity (base commit, sections, arm table, budget, limits, fix-round limit), and resume from it stage by stage: a session that recorded an exit is never run again, a stage that started and recorded nothing is run again from the clone's last recorded candidate, and a second `run` whose identity differs is refused with exit 2. Done when: tests interrupt after a build, after the gates and inside a fix round, show the next call running only what is left, and show the mismatch refused. **Corrected 2026-11-11:** resume by stage and the identity check added after the plan review (gap 4).
- [x] Record per run the cost, the wall time, the tokens per model (subagents included), the commit count and the diff size. Done when: a test over a fixture reply shows each field.
- [x] Commit: `campaign: measure the ways of working with one command`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_measure_modes.py"` passes with a fake `claude` and a fake reviewer, and no test starts a real session.

> **Verified:** 2026-11-11 | §36 | 4c3968040e003b0dedf2d19cd442892b9d4728a5
> **Review:** `docs/reviews/d00-t03-s36.json`

## 37. Operating Mode Rule and Launcher

> **Started:** 2026-11-12T01:55:00Z

The measurement only decides something if a rule reads it. This section writes the rule, stores its verdict in one file, makes the launcher start whatever that file says, and has the campaign measure again when the facts may have changed. After it, nobody chooses the lead model: the rule does (decision 30).

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write the rule as `python scripts/measure-modes.py decide`. Done when: fixture results give the expected arm.
2. Store the verdict and make the launcher read it. Done when: `scripts/start-campaign.ps1 -DryRun` shows the model and mode from the file.
3. Measure again at the right moments. Done when: `process-plan` names them.

- [x] Write `decide` on the cost to reach an approved review (owner, 2026-11-10: the review always runs, so a first-pass finding is a cost and not a disqualification): an arm's cost for a section is its build plus every fix round until a review returns no `P1` or `P2`; an arm is eligible when every one of its sections got there within the fix-round limit with all three gates passing (**Corrected 2026-11-12**, plan review gap 3: a run counts as there only when its record ends `approved`, which §36 gives only to a reviewed candidate with every gate passing, `clean-tree` included; `unreviewed` and `fix-rounds-exhausted` runs are not, and tests show a run whose three named gates pass with a dirty tree, and one with no review, each making its arm ineligible); among eligible arms the lowest total cost wins, a tie going to the fewer review rounds and then the shorter wall time. Done when: tests in `scripts/tests/test_measure_modes.py` cover an arm that is cheap to build and dear to fix losing to one that is the reverse, an arm that never reaches approval being ineligible, and each tie. Cheaper substitute: judging the first pass alone, which on 2026-11-10 would have disqualified the arm that was cheapest to finish.
- [x] Refuse to decide on fewer than three sections per arm or when no arm is eligible, with exit 2 and the reason, leaving the stored verdict as it was. Done when: tests show both refusals and the unchanged file. **Corrected 2026-11-12:** the plan review (gap 2) found totals comparable only when every arm ran the same sections under the same conditions: `decide` takes one results file (`--results <file>`, not repeatable), which by construction gives every arm the same base, limits and fix-round cap, and it also refuses (exit 2, verdict unchanged) a file in which the arms do not hold the same set of distinct sections, or a run whose cost or review evidence is missing; tests show each refusal.
- [x] Write the verdict to `.conclave/operating-mode.json` through a temporary file and `os.replace`: the arm, its model alias, the date, the base commit, the per-arm totals and the path of the record. Done when: a test reads it back. **Corrected 2026-11-11:** this also stored whether the arm orchestrates; every arm works alone since decision 40, so the field is not written. **Corrected 2026-11-12:** the verdict also records the full model name the winning arm's sessions reported (`claude-opus-5-5`, from each reply's `modelUsage`), since the re-measure trigger in `process-plan` compares it with what the lead alias resolves to and an alias alone cannot show a change.
- [x] Write the record `docs/reviews/operating-mode-<date>.md` with one table row per run and the verdict with the branch of the rule that produced it. Done when: `python scripts/check-design-doc.py` on it exits 0. **Corrected 2026-11-12:** the checker alone accepts an empty document (plan review gap 6), so tests also compare the generated record with its input: one row per run with its arm, section, cost and end, each arm's total, the stored verdict's arm, and the branch named (lowest cost, a tie on reviews, a tie on wall time), on fixtures that include a tie and an ineligible arm.
- [x] Read `.conclave/operating-mode.json` in `scripts/start-campaign.ps1` for the lead model, falling back to the value in the script when the file is missing or unreadable, and print the model at start. Done when: tests in `scripts/tests/test_start_campaign.py` show each arm's model reaching the command line and the fallback. **Corrected 2026-11-11:** this also chose the goal's sentence on working alone or orchestrating; the owner fixed working alone (decision 40), so the goal has one wording.
- [x] State in `AGENTS.md` (Subagents) that `.conclave/operating-mode.json` names the lead model, and that the lead does the writing itself whichever model it is, with the readers and the on-call Fable worker. Done when: the section names the file. **Corrected 2026-11-12:** the plan review (gap 5) found this restoring the on-call Fable worker that the owner removed on 2026-11-11; the statement is that the lead writes everything, the hard fixes and the architecture decision records included, with only the Sonnet readers beside it, and the opening sentence of AGENTS.md (Subagents), which names the latest Opus, says the lead is the model the stored verdict names. **Corrected 2026-11-11:** this said the routing ladder applies when the stored mode orchestrates; the owner fixed working alone (decision 40), so no arm orchestrates.
- [x] Add to `.claude/skills/process-plan/SKILL.md`, at a section boundary: measure again with `python scripts/measure-modes.py` on three ready sections when 300 sections were stamped since the stored verdict's base, or when the model a lead alias resolves to differs from the one the verdict recorded; apply the verdict and carry on; the launcher picks it up at its next start. Done when: the skill names both triggers and a test in `scripts/tests/test_skill_ci_gate.py` fails when the mention is removed. **Corrected 2026-11-12:** the plan review (gaps 1 and 4) found prose alone unproven and the lifecycle missing. The triggers are a command, `python scripts/measure-modes.py due --model <the lead session's own model id>`: exit 0 printing the reason when `query stats` shows 300 or more verified sections more than the verdict recorded at its decision, or when the given model differs from the verdict's; exit 1 when neither holds; exit 2 when the verdict or the count cannot be read. Tests cover 299 and 300, the same and a different model, and an unreadable verdict. The skill runs it at a section boundary, and when it exits 0 runs one cycle: `run` on three ready sections into a fresh work folder named for the day (`measure-modes-<date>`, resumed by the same command if interrupted), `decide --results` on that folder's `results.json`, then `clean`; with fewer than three ready sections it records the skip and checks again at the next boundary, and a refused `decide` keeps the stored verdict. A test runs two cycles on fixtures, the second replacing the verdict, and a third whose `decide` is refused leaving the second's verdict in place.
- [x] Record the first verdict from the results of 2026-11-10 with `decide`. Done when: `.conclave/operating-mode.json` exists and the launcher's dry run shows its mode. **Corrected 2026-11-12:** those results (`docs/experiments/operating-mode-2026-11-10.json`) predate §36's `results.json` (a run's build and `fix_rounds` in place of `stages`, gate exits as numbers in fix rounds), so `decide --results <file>` reads both layouts through one converter, tested on a copy of each; the 2026-11-10 measurement's `orchestrated` arm is judged like any other and is ineligible (its third section never reached approval).
- [x] Commit: `campaign: let the measurement choose the lead model`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_measure_modes.py"` and `-p "test_start_campaign.py"` pass, and `pwsh scripts/start-campaign.ps1 -DryRun` prints the stored mode.

> **Verified:** 2026-11-12 | §37 | 39b0cec0c266b41c60b71a0778e9d35142abb12f
> **Review:** `docs/reviews/d00-t03-s37.json`

## 38. Parallel Streams Design Record

Owner decision 2026-11-10 (decision 33): once work is independent enough, the system may run several streams at once, each in its own clone, with one integrator landing them on `main` in order with the full gates. This reverses "one tree, one writer" for that case only; it does not bring back branches: development stays straight on `main` (owner, 2026-11-10), and a stream is a clone, not a branch. One section at a time is the limit on calendar time: at thousands of sections a single stream sets the finish date. It is also the change most able to damage the repository, so it is designed and measured before any of it is built.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Measure what a single stream achieves and what parallel streams could. Done when: the record's Measurements section holds both.
2. Write `docs/specs/<date>-parallel-streams-design.md`. Done when: the checker passes with the headings below.

- [ ] Measure the single stream from the receipts under `docs/reviews/`: sections stamped per day and the median hours per section, over the last 30 days of running. Done when: both numbers are under `## Measurements` with the command that produced them.
- [ ] Define when two sections are independent, as a rule a script can check: neither depends on the other in the graph, their named paths do not overlap, and neither changes a file under `todo/` that the other reads (the plan, the indexes). Done when: `## Decision` states the rule and names the script that will check it. Cheaper substitute: independence judged per case, which is how two streams end up editing one file.
- [ ] Decide what is never parallel: the shared platform before its interfaces are stamped, anything that drives Office or the desktop (one desktop, one driver), the plan sync and the stamp, and the integrator itself. Done when: `## Decision` lists them with the reason for each.
- [ ] Design the stream: its own clone under the scratch folder (never a worktree or a branch of this repository: owner, 2026-11-10, development stays straight on `main`), its own run file and run guard, its own scratch folder, commits on that clone's own `main` which only the integrator reads, no remote and no push. Done when: `## Decision` describes each and what stops a stream from pushing.
- [ ] Design the cleanup (owner, 2026-11-10: whatever is made for a job is cleaned up afterwards, or reused when the work recurs): a stream's clone is reused for that stream's next section, brought up to `main` first, and deleted when the stream ends; a command lists every clone the system made with the job it belongs to, and also fails when `git branch -a` or `git worktree list` shows anything but `main` and the tool branches `AGENTS.md` names, or when a clone has no live job; the integrator runs it after every landing and the run's closeout runs it last. Done when: `## Decision` names the command, when it runs, and what it does with a leftover whose job died (remove it after confirming its commits are on `main` or kept in a named ref, never before).
- [ ] Design the integrator: one at a time, in dependency order, it takes a stream's finished section, replays its commits onto this repository's `main` (a replay of commits, not a merge of a branch), runs the full gates and the section's Test checkpoint on the result, and only then stamps and pushes; a section that fails after replay goes back to its stream with the evidence. Done when: `## Decision` describes the order, the gates and the return path. Cheaper substitute: merging stream branches as they finish, which lands work that was never tested together.
- [ ] Set the number of streams from measurement, not preference: the usage limits of the sign-in, the memory and processor a stream's gates take on this PC (`bosun` already queues heavy jobs), and the reviewer's capacity. Done when: `## Measurements` holds each and `## Decision` states a starting number and the rule that raises or lowers it.
- [ ] State the failure paths: a stream that dies, two streams that turn out to conflict, an integrator that fails mid-replay, and a disk that fills. Done when: `## Consequences` names what the system does in each without losing committed work.
- [ ] Commit: `arch: record the parallel streams design`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-parallel-streams-design.md --require Measurements --require Decision --require Consequences` exits 0.

## 39. Parallel Streams Sections Authored

The design record of §38 becomes work. This section authors the TODO file that builds parallel streams, so the build is planned from a reviewed design and each piece is small.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Author `todo/00-workspace/TODO-06-parallel-streams.md` with `create-todo` from the design record. Done when: `python scripts/todo-graph.py validate` passes.

- [ ] Author `todo/00-workspace/TODO-06-parallel-streams.md`: one section each for the independence check, the stream clone and its guard, the integrator, the stream count rule, each failure path of the record's Consequences, and a first parallel run of two streams on two independent sections whose result is compared with the same two sections run one after the other. Done when: the file validates and every Decision and Consequences item of the record is owned by a section. Cheaper substitute: one section for the whole subsystem.
- [ ] Give the last section of that file the rule that parallel work starts: only after its two-stream run landed both sections on `main` with every gate green and no rework. Done when: the section's Done when states it.
- [ ] Confirm the "Develop straight on `main`" bullet of `AGENTS.md` (Working rules) still describes what was built: streams are separate clones with only their own `main`, replayed onto `main` by the integrator, with no branch or worktree in this repository. Done when: the bullet names the design record, and `git branch -a` and `git worktree list` show nothing new after the two-stream trial.
- [ ] Run `python scripts/todo-graph.py plan --sync`. Done when: `python scripts/todo-graph.py plan --check` exits 0.
- [ ] Commit: `todo: author the parallel streams file`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0 and `Test-Path todo/00-workspace/TODO-06-parallel-streams.md` returns `True`.

## 50. Withdrawn Sections

> **Started:** 2026-11-11T06:55:00Z

Filed 2026-11-11 (owner, in session: agents are read-only; the Fable `principal-implementer` and the Opus `section-writer` are removed). D00 T03 §34 built `scripts/packet.py` to accept or reject a writer agent's change, and §46 to §49 extend it; with no writer agent the command has no consumer, so the five sections can never be worth finishing. The plan has no way to retire one section: a file can be `superseded`, a section can only be stamped, and an open section counts against `query stats` forever, so the campaign could never end with `verified` equal to `total`. This section adds a withdrawal, recorded in the section with its reason and decider, then withdraws §34, §46 to §49 and the three TODO-05 sections built on its packets, and removes the code they leave behind.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Teach the graph a withdrawn section. Done when: `validate` accepts a withdrawn section, `query stats` leaves it out of `total`, and the plan shows it as withdrawn.
2. Withdraw the five sections and remove `scripts/packet.py`. Done when: `query stats` no longer counts them and no file names `scripts/packet.py` except history records.

- [x] Read a `> **Withdrawn:** <UTC instant>: <who decided>: <reason>` line in a section body and a `[-]` box in its Implementation Order row in `scripts/lib/todo_graph.py`, and refuse either without the other, a withdrawn section that also carries a stamp, and a line without a decider and a reason. Done when: tests in `scripts/tests/test_todo_graph.py` show each refusal and an accepted withdrawal.
- [x] Refuse an open, non-withdrawn section that depends on a withdrawn one, naming both. Done when: a fixture where an open section depends on a withdrawn one exits 2 with both references, and the same fixture with the dependant withdrawn too validates.
- [x] Leave a withdrawn section out of `query ready`, `query blocked`, `resolve` exit 0 (it exits 3 as settled, with `withdrawn: true`) and the `total` of `query stats`, and add `"withdrawn": N` to `query stats`. Done when: tests show each.
- [x] Render a withdrawn row in the plan with `[-]` in Status and leave it out of the progress line's count, adding `, N withdrawn` to it when N is above zero. Done when: a test on a fixture tree shows both and `plan --check` fails when the plan is stale.
- [x] Count a withdrawn section as finished for a file's `done` status in the validator. Done when: a fixture file whose sections are all stamped or withdrawn validates with `status: done` and refuses `status: active`.
- [x] Count a withdrawn sibling as finished where `stamp` decides that a file is done, in `scripts/lib/todo_graph.py`. Done when: a test stamps the last open section of a fixture file whose other section is withdrawn, the file reads `status: done` and the graph validates afterwards. **Groomed 2026-11-11:** completion finding 2.
- [x] Give `plan_status` in `scripts/todo-graph.py` a `withdrawn` status, so `query plan` reports a withdrawn section as `withdrawn` and never `blocked`. Done when: a test shows it for a withdrawal in an active file and in a done file. **Groomed 2026-11-11:** completion finding 3.
- [x] Document the withdrawal in `todo/README.md` (what it is for, the line, the `[-]` box, who may decide one: the owner, or the lead for a section whose consumer an owner decision removed) and in `.claude/skills/add-todo/SKILL.md` (a withdrawal goes through this, never by deleting a section). Done when: both name the line, the box and the dependant refusal.
- [x] Withdraw D00 T03 §34, §46, §47, §48 and §49, and D00 T05 §5, §6 and §7 (lessons attached to work packets, the packet ledger and the agent score from it, which have no packets to work on once no agent writes), with the owner's 2026-11-11 decision as the reason. Done when: `python scripts/todo-graph.py query stats` shows `"withdrawn": 8`, `resolve` on each exits 3, and `validate` passes with no open section left depending on any of them. **Groomed 2026-11-11:** completion finding 1 (it named five; D00 T05 §5 and §6 depend on §34 and §7 on §6).
- [x] Remove `scripts/packet.py` and `scripts/tests/test_packet.py`, and the `build/packet.json` mention in any document that still describes the command as live. Done when: a search of the repository outside `docs/reviews/`, `docs/phase-runs/` and the withdrawn sections finds no `packet.py`, and `python scripts/run-tests.py` passes.
- [x] Commit: `todo: withdraw a section whose purpose is gone`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_todo_graph.py"` passes with the withdrawal tests among them, `python scripts/todo-graph.py validate` exits 0, and `python scripts/todo-graph.py query stats` shows `"withdrawn": 8`.

> **Verified:** 2026-11-11 | §50 | 920df9794ce485cc82564fad705151f94b935249
> **Review:** `docs/reviews/d00-t03-s50.json`

## 53. Automation Notices Go in the Weekly Digest

> **Started:** 2026-11-12T03:10:00Z

Filed 2026-11-11 from the completion review of §35 (`docs/reviews/00-workspace/D00-T03-s35-completion.md`, round 1, finding 5, P2). Decision 32 of `docs/specs/2026-10-23-campaign-scope-design.md` promises one weekly email and no other interruption, but three senders still email at once: `run.py` when a scheduled task fails (`.conclave/automations/run.py`, through `alert.py`), the host readiness check when a campaign parks (`scripts/check-campaign-host.py --notify`, `process-plan`'s Host readiness step), and the version notices of `check-visual-studio.py` and `check-python-pin.py`. This section records each notice for the digest instead, keeps one immediate email only where waiting a week would lose work, and says which in the README.

**Corrected 2026-11-12** after the plan review (gaps 1 to 7). Gap 1: decision 32 of `docs/specs/2026-10-23-campaign-scope-design.md` permits "one email" a week "and there is no other interruption", and it is later than the alert emails the skills still send, so no sender keeps an immediate email: the two exceptions this section once kept (a task's third failure in a row, a host check that parks a running campaign) are dropped, and with them gaps 5 and 6, which only concerned them. The campaign's own park emails (`process-plan`'s Host readiness and CI watch) become notices too; the digest already reports the run's state. Reversing it costs one condition per sender. Gaps 2, 3, 4 and 7 are planned below.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Record notices for the digest. Done when: every sender writes its notice to one place the digest reads.
2. Send none at once. Done when: the README names each sender and says each waits for the digest.

- [x] Add `record_notice(sender, subject, body)` to `.conclave/automations/alert.py`: one JSON object per line in `build/automations/notices.jsonl` with a stable `id` (a UUID), the UTC time, the sender, the subject, the body and `reported: null`, rewritten whole through a temporary file and `os.replace` under an interprocess lock (`build/automations/notices.lock`, msvcrt or flock, bounded wait), and read back. Done when: tests in `scripts/tests/test_automations.py` show a notice read back in a fresh process, and two writers in separate processes at once both keep their notice. Cheaper substitute: appending without a lock, which lets two writers replace each other's file.
- [x] Refuse, never empty, a queue that cannot be read or written: an unreadable or malformed `notices.jsonl` raises `Refused` naming the file and line and is left as it was, and a failed write leaves the previous file whole. Done when: tests show a malformed file kept byte for byte with the refusal, and a write that fails (a read-only target) leaving the queue as it was.
- [x] Add `pending_notices()` and `mark_reported(ids)` to `alert.py`: the first returns the notices not yet reported; the second sets `reported` on exactly the given ids under the lock, so a notice recorded after the batch was read stays pending. Done when: a test records a notice between reading a batch and marking it, and that notice is still pending afterwards.
- [x] Make `run.py` record a failed or timed-out task's notice (the subject and body `message()` builds today) instead of emailing it; a notice that cannot be recorded is written to the run's log and the run exits 3, as an unsent alert does now. Done when: tests show a failure recorded and no request made, and the exit-3 path. Cheaper substitute: keeping the email and also recording, which is the interruption decision 32 removes.
- [x] Make `check-campaign-host.py --notify` record its notice instead of emailing it. Done when: tests show the notice recorded with every failing check and its fix, and no request made.
- [x] Make the version notices of `check-visual-studio.py` and `check-python-pin.py` record their notices (through `pin_proposal.notice`'s `mail`) and never email; `notice` writes its `refs/office-notice/<key>` mark only after the notice is recorded. Done when: tests show each recorded with no request made, and a recording that fails leaving no mark, so the next run tries again.
- [x] Change `process-plan`'s Host readiness and CI watch steps from emailing the owner through `alert.py` to recording a notice (`python .conclave/automations/alert.py --notice <subject> <body file>`), and add that command to `alert.py`. Done when: the skill names the notice for both parks and `scripts/tests/test_skill_ci_gate.py` pins the new wording.
- [x] Add the pending notices to `scripts/owner-digest.py` as their own part, after the waiting list: one wrapped, path-cleared line per notice (time, sender, subject) within the 120-line body, with every notice's full text in an attached `notices.txt`; the batch is captured when the email is composed and marked reported only after the send succeeds, never by `--dry-run` or a refused send. Done when: tests show the part and the attachment holding every notice of a batch of long notices, the summary and waiting list intact, the batch pending after a dry run and after a refused send, reported after a send, a notice recorded during the send still pending, and an unreadable queue shown as a line in the digest with nothing marked. Cheaper substitute: marking everything read when the digest starts, which loses what arrives or fails meanwhile.
- [x] Say in `.conclave/automations/README.md` (How you hear about it) that every notice waits for the Monday digest, naming each sender (`run.py`, the host check, the two version checks, the campaign's parks), with decision 32 as the reason. Done when: the README names every sender.
- [ ] Commit: `automations: notices wait for the weekly digest`- [ ] Commit: `automations: notices wait for the weekly digest`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_automations.py"` and `-p "test_owner_digest.py"` pass, and `python scripts/owner-digest.py --dry-run` shows the notices part.

## 54. One Process-Tree Containment for Every Tool

> **Started:** 2026-11-12T02:05:00Z

Filed 2026-11-11 while building §36. The repository starts children in a contained process tree in three private copies: `scripts/check-campaign-host.py` (`Containment`, a job object with a memory limit, ended by waiting until the job's member count reads 0), `scripts/review-dispatch.py` (`run`, a kill-on-close job, closed without waiting) and `scripts/run-tests.py` (a job object per test file, `taskkill /T /F` on timeout). §36 wrote the shared `scripts/lib/process_tree.py` and its tests found that the member count can read 0 a moment before the last member's process object is signalled: in 4 of 6 repeats a grandchild was still alive when the count said the tree was gone. `Tree.end()` waits on each member's own handle instead. The three copies keep the race (the host check and `run-tests.py` measure output and exit once the count reads 0) and three ways to get the same thing wrong. This section moves all three onto the shared helper.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Give the helper what the three need. Done when: `process_tree.Tree` takes a memory limit and a piped standard input, with tests.
2. Move each tool onto it. Done when: none of the three defines a job object or calls `taskkill`.

- [x] Add a piped standard input to `scripts/lib/process_tree.py` (`Tree.start(..., stdin_text=)`, fed from a thread so a child that never reads cannot block the caller), which `review-dispatch.py` needs. Done when: a test in `scripts/tests/test_process_tree.py` feeds a child that exits without reading and returns within the time limit.
- [x] Prove the memory limit of `process_tree.Tree(memory_bytes=)` on Windows. Done when: a test shows a child that allocates past the limit failing while the caller is unaffected (the host check's existing test, `test_check_campaign_host.py`, moved to the helper's file). **Corrected 2026-11-12:** the plan review (gap 2) found that moving the test loses the proof that the host check supplies its limit: the helper's file gets its own over-limit and under-limit tests, and the host check's test stays where it is, driving the migrated host check with a reduced `PROBE_MEMORY_BYTES` and showing an allocation past it fail while a bounded one below it succeeds.
- [x] Replace `Containment` in `scripts/check-campaign-host.py` with `process_tree.Tree(memory_bytes=PROBE_MEMORY_BYTES)`. Done when: `test_check_campaign_host.py` passes and the file defines no ctypes job structure. Cheaper substitute: keeping `Containment` as a wrapper around the helper, which keeps a second place for the end logic.
- [x] Replace the job helpers and `kill_tree` in `scripts/review-dispatch.py` with the helper, keeping its output-size watch and its outcomes (`timed out`, `returned more than ... bytes`, `could not start`). Done when: `test_review_dispatch.py` passes and the file calls no `CreateJobObjectW`. **Corrected 2026-11-12:** the dispatcher names the failed start step in its outcome (`could not start: assign to job: ...`) and its tests force each step to fail; the helper's `TreeError` therefore carries the step (`create job`, `configure job`, `start`, `assign to job`, `resume`), and those tests force the helper's steps, so every outcome string the dispatcher records today is kept.
- [x] Replace the job object and `taskkill /T /F` in `scripts/run-tests.py` with the helper. Done when: `test_run_tests.py` passes, including its timeout test, and the file calls no `taskkill`.
- [x] Add `scripts/tests/test_one_containment.py`, which fails when any file under `scripts/` other than `scripts/lib/process_tree.py` calls `CreateJobObjectW` or runs `taskkill`. Done when: it fails on today's tree before the three moves and passes after them. **Corrected 2026-11-12:** the plan review (gap 1) found `taskkill` also in `scripts/start-campaign.ps1` and in three test files, which this section does not move. The check covers the Python tools that contain a child they start, `scripts/*.py` and `scripts/lib/*.py`; it names as outside its scope, with the reason in its docstring, the launcher's `-Stop` (it ends another, already running launcher's tree by its recorded process id, which no job of this process holds) and the test files' teardown of processes a test started through the tool under test.
- [x] Commit: `tools: one process-tree containment for every tool`

**Test checkpoint:** `python scripts/run-tests.py -p "test_process_tree.py"`, `-p "test_check_campaign_host.py"`, `-p "test_review_dispatch.py"`, `-p "test_run_tests.py"` and `-p "test_one_containment.py"` pass.

> **Verified:** 2026-11-12 | §54 | bf906a62988234db1cb8e53578b5e01d9146eff7
> **Review:** `docs/reviews/d00-t03-s54.json`

## 55. Scheduled Tasks Run in the Shared Process Tree

> **Started:** 2026-11-12T02:10:00Z

Filed 2026-11-12 after §54 was stamped. `.conclave/automations/run.py`, which runs every scheduled task, holds a fourth private containment outside the `scripts/` folders §54's check covers: `_kill_tree` runs `taskkill /T /F` only when a task passes its time limit, so a task that ends by itself leaves whatever it started running (a `gh` or `git` child, a test that started a fake), and `taskkill /T` walks parent links, which a process whose parent already exited no longer has. This section runs each task in `scripts/lib/process_tree.py`'s tree and widens the check.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Run each task in the shared tree. Done when: a task's leftover child is gone when its run ends, whether it timed out or not.
2. Widen the check. Done when: `test_one_containment.py` covers `.conclave/automations/`.

- [x] Replace the `popen` and `killer` start and stop in `execute()` of `.conclave/automations/run.py` with `process_tree.run` (output and errors into the run's log, `timeout_minutes` as the limit), keeping its outcomes: exit 124 and `timed_out` on the limit, exit 126 with the reason in the log when the task cannot start, `cleanup_failed` when the tree will not end. Done when: tests in `scripts/tests/test_automations.py` show each outcome. Cheaper substitute: keeping `taskkill /T` on timeout, which leaves the leftovers of a task that ended by itself. **Corrected 2026-11-12** after the plan review (gap 1, P2): `process_tree.run` raised `TreeError` without its outcome when the tree would not end, so the helper's `TreeError` now carries the partial outcome (exit, stop reason, seconds), and `run.py` records a tree it cannot end as exit 125 with `cleanup_failed` when the task itself exited 0 (its own non-zero code otherwise), or exit 124, `timed_out` and `cleanup_failed` after a timeout, each with a diagnostic line in the run's log and a failure notice; tests drive both cases through `main()` and check the returned code, `last.json`, the log and the notice.
- [x] Load the helper by path from `scripts/lib/process_tree.py` under the repository root `run.py` is given, as `review-dispatch.py` does. **Corrected 2026-11-12:** loaded from the repository `run.py` itself lives in (beside it, as the dispatcher does), not from the `root` a test passes, so a fixture root needs no copy; a copy of the automations folder alone (the installer's checks) still validates and only a task run needs the helper. Done when: a test runs `run.py` from a copy of the automations folder against a fixture root holding the helper.
- [x] Prove a task's leftover child ends with its run. Done when: a test whose task starts a sleeping child and exits 0 shows the child gone when `execute()` returns, and the same for a task that passes its limit.
- [x] Extend `scripts/tests/test_one_containment.py` to the Python files under `.conclave/automations/`. Done when: it fails on `run.py` before the move and passes after it.
- [x] Commit: `automations: run each scheduled task in the shared process tree`

**Test checkpoint:** `python scripts/run-tests.py -p "test_automations.py"` and `-p "test_one_containment.py"` pass.

> **Verified:** 2026-11-12 | §55 | bf1e57bfa5a923a80d119a23779694691061ffc2
> **Review:** `docs/reviews/d00-t03-s55.json`

## 56. Digest Delivery When No Evidence Remains

Filed 2026-11-12 from the review of §53 (`docs/reviews/00-workspace/D00-T03-s53.md`, reconciliations 6 to 9). The weekly digest claims its notices before sending, records SMTP2GO's acceptance in a second store, and settles every claim daily against SMTP2GO's activity log. One state stays undecidable: SMTP2GO accepted the digest, every write to the notice queue failed until the PC went off, and the PC stayed off past SMTP2GO's activity history (five days on its free plan). Nothing can then say whether the owner received it, and the two failures trade against each other: (a) count the acceptance as delivery, as §53 does now and as its contract reads ("marked reported only after the send succeeds"), so a bounce SMTP2GO no longer shows goes unseen; or (b) deliver those notices again in full, labelled "may already have reached you", so a delivered digest can repeat once. The reviewer holds §53 to both, which no design can meet; the owner chooses, and §53 is reconciled to that choice.

**Phase:** 0
**Needs:** owner-decision
**Owner action:** Reply in a campaign session "digest: acceptance" (a: a possible unseen bounce) or "digest: repeat" (b: a possible labelled repeat) for the one state where SMTP2GO no longer holds a digest's record; the session records it here and removes this Need.
**Surface:** no

**Build order:**

1. Record the choice. Done when: this section names it with the date.
2. Apply it. Done when: `settle_claims` in `.conclave/automations/alert.py` follows it and §53's reconciliation runs.

- [ ] Record the owner's choice in this section, with the date. Done when: the choice is written here and the `owner-decision` Need is removed.
- [ ] Apply the choice in `settle_claims` of `.conclave/automations/alert.py`: (a) keeps the acceptance record counting as delivery once the log can no longer decide; (b) marks such a claim unconfirmed, so the next digest carries it in full, labelled. Done when: `scripts/tests/test_automations.py` (`test_settling_by_what_the_log_says`) holds the chosen row and `test_owner_digest.py` shows the chosen digest.
- [ ] Run §53's next reconciliation with the choice in its findings file. Done when: the reconciliation is recorded in `docs/reviews/00-workspace/D00-T03-s53.md`.
- [ ] Commit: `automations: the digest follows the owner's choice where no evidence remains`

**Test checkpoint:** `python scripts/run-tests.py -p "test_automations.py"` and `-p "test_owner_digest.py"` pass with the chosen behaviour.
## 57. Completion Reviews Leave the Commit Item to the Stamp

> **Started:** 2026-11-12T08:40:10Z

Filed 2026-11-12 from the review of D00 T05 §1 (`docs/reviews/00-workspace/D00-T05-s1.md`, the completion review's gap 2 and the reconciliation's open P3): the reviewer reported the section's unticked `- [ ] Commit:` item as missing work, but `stamp` ticks that item itself when it writes the `Verified:` line (`scripts/lib/todo_graph.py`, the `Commit:` substitution), so the item is unticked by design until then. A reviewer who is not told this files a gap no writer should close by hand, and the gap then needs a reconciliation or a filed section of its own.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Say it in the prompts. Done when: the completion and reconciliation prompts state the rule.
2. Prove a prompt carries it. Done when: a test reads it in a filled prompt.

- [x] State in `docs/completion-review-prompt.md` and in `docs/reconciliation-review-prompt.md` (the template `scripts/review-prompt.py` fills for a reconciliation; **Corrected 2026-11-12:** the first wording said the script itself) that the section's `- [ ] Commit:` item is ticked by `stamp` when it writes the `Verified:` line, so an unticked Commit item whose commit exists is never a gap. Done when: both prompts hold the sentence.
- [x] Test that a filled completion prompt and a filled reconciliation prompt carry it. Done when: a test in `scripts/tests/test_review_prompt.py` fails with the sentence removed from either.
- [x] Commit: `review: the stamp ticks the Commit item, so a review never asks for it`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_review_prompt.py"` passes with the new test among them.

> **Verified:** 2026-11-12 | §57 | c7154cf8dbfc681c5979925b59ee4c61358662a2
> **Review:** `docs/reviews/d00-t03-s57.json`
## 58. The Plan Lists Sections, Never TODO Files

> **Started:** 2026-11-12T11:18:38Z

Owner, 2026-11-12, in session: the plan file must not reference TODO files; it lists individual sections, in order. Since D00 T03 §31 the generated plan has ended with a `### Still to author` block of file tables (85 rows today), printed straight after Phase 99 under a heading of the same level, so it read as part of that phase. The files in it are not written yet, so their sections do not exist to list; what does exist is the section that writes each one. This section replaces the file tables with one table of those authoring sections, in plan order, each with the number of TODO files it still has to write, under a heading that says these are in no phase yet.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Render the block as sections. Done when: the generated plan holds no TODO file path.
2. Drop the check that guarded the file table. Done when: a long file name no longer refuses validation on the plan's account.

- [x] Replace the `### Still to author` block in `projection` of `scripts/lib/todo_graph.py` with `### Not in the plan yet: sections still to be written`: one sentence saying the sections of N TODO files are not written yet, are in no phase and no total, and join the phase tables as each file is written; then one table of the authoring sections in plan order with the columns Status, Reference, Deliverable and Files to write (a count). Done when: a test shows the heading, one row per authoring section with its count, no `todo/` path anywhere in the block, and the block after the last phase table.
- [x] Keep the Progress line's count of files still to author and `query stats`'s `to_author`, which name no file. Done when: the existing singular and plural tests still pass.
- [x] Remove `author_table` and its call in `_plan_tables_ok`: the plan no longer renders a file name, so a long one cannot break a plan table; the new table's Deliverable is a section title, which the phase tables already bound. Done when: the test for a too-wide file row is replaced by one showing such a name validates and the plan still renders.
- [x] Regenerate `todo/implementation-plan.md`. Done when: `python scripts/todo-graph.py plan --check` passes and the file holds no line starting `| `todo/`.
- [x] Hold the new table to the 120-character row limit with one function that `validate` (`_plan_tables_ok`) and `projection` both call, refusing a row that passes it and naming the section; a long file name is not a reason any more. Done when: a test with a title that fits its phase row but not the new table's row is refused by both, and a tree with a very long file name validates. **Corrected 2026-11-12:** added after the plan review (gap 1, P2); the removal item above keeps only the file-name half.
- [x] Move every test that pins the old block to the new one: `test_query_stats_counts_the_files_still_to_author`, the domain-grouping tests and the empty-block test, with assertions that the table's counts sum to `len(to_author())`, rows are in plan order, a count drops as a file appears, a section whose files all exist leaves the table, and no block at all is rendered when nothing is missing (neither heading). Done when: those tests pass and fail on the old renderer. **Corrected 2026-11-12:** added after the plan review (gap 2, P2).
- [x] Bring the documents in line: `todo/README.md` (the plan shows the authoring sections with a count, and which rows are refused), and a dated amendment to decision 26 of `docs/specs/2026-10-23-campaign-scope-design.md`, which required listing each TODO file. Done when: neither document promises a file table. **Corrected 2026-11-12:** added after the plan review (gap 3, P3).
- [x] Commit: `todo: the plan lists the sections still to be written, never TODO files`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_todo_graph.py"` passes with the new block's tests among them, and `python scripts/todo-graph.py plan --check` passes.

> **Verified:** 2026-11-12 | §58 | 737719c64d9f7b0b12f2c653b97521a20e950694
> **Review:** `docs/reviews/d00-t03-s58.json`
## 59. A Parked Section Is Neither Ready Nor In Progress

> **Started:** 2026-11-12T20:42:27Z

Filed 2026-11-12 from the campaign's own run (`docs/phase-runs/2026-11-12-phase-0.md` and the run before it). Two open sections stand at a committed candidate and wait on something outside the run: §53 on the owner decision §56, and D00 T07 §4 on the weekly digest's first scheduled run on Monday 2026-11-16. Each still carries its `Started:` line, so the tree calls both in progress and ready, and three things go wrong. `scripts/merge_prs.py` refuses at every section boundary (`a section is in progress`), so no dependency pull request can merge until the owner answers. `python scripts/todo-graph.py query ready` lists both, so the Stop hook names a section nobody can work on as the next row. And a campaign with nothing else left cannot see from the graph that it should park. The only record that they are parked is prose in a run file. This section gives a parked section one line in its own TODO section that the graph and the merge both read.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Give a parked section its line and make the graph read it. Done when: `python scripts/todo-graph.py query ready` no longer lists a parked section and `resolve` exits 4 for it, saying what it waits on.
2. Let the dependency merge pass a parked section. Done when: `python scripts/merge_prs.py` refuses for a section in progress and not for a parked one.
3. Park the two sections that are parked. Done when: the merge no longer names them and the Stop hook's next row is a section that can be worked on.

- [ ] Document the `> **Parked:** <UTC instant>: <reason>` line in `todo/README.md`, beside `Started:`: written directly under the `Started:` line of an open section whose work stopped at a committed candidate and waits on something outside the run (an owner decision filed as its own section, a dated event), with the reason naming what it waits on; removed in the commit that resumes the work; never on a section with uncommitted work. Done when: the README names the line, where it sits, who writes and removes it, and what it changes (`query ready`, `resolve`, the merge). Cheaper substitute: a note in the run file, which no tool reads.
- [ ] Parse the line in `scripts/lib/todo_graph.py` into a `parked` field of `Section` (the reason, or empty) and refuse, in `validate`, a `Parked:` line on a section with no `Started:` line, on a stamped section, with no UTC instant, with an empty reason, or given twice. Done when: tests in `scripts/tests/test_todo_graph.py` show each refusal with the section named, and an accepted line read back with its reason.
- [ ] Make `disposition` in `scripts/lib/todo_graph.py` return 4 for a parked section, so `query ready` leaves it out, `query blocked` lists it, and `resolve` exits 4 and prints `parked: <reason>` beside what else it waits on. Done when: tests show a section ready before the line and waiting after it, the reason in `resolve`'s output, and the section ready again once the line is removed. Cheaper substitute: filtering the ready list in the Stop hook alone, which leaves `resolve` and the plan's counts calling it ready.
- [ ] Count a parked section as waiting, not ready, in `query stats` and in the generated plan's progress line (`todo/implementation-plan.md`). Done when: a test shows the ready count one lower with a section parked, and `python scripts/todo-graph.py plan --check` passes on this repository after the sync.
- [ ] Leave parked sections out of `in_progress_sections` in `scripts/merge_prs.py`, keeping every other refusal (a dirty tree, an unpushed `HEAD`, a started section that is not parked). Done when: tests in `scripts/tests/test_merge_prs.py` show a tree whose only started section is parked passing the local safety check, a tree with a started section that is not parked still refused with its reference, and a tree with one of each refused naming only the one in progress. Cheaper substitute: dropping the in-progress refusal, which lets a merge land under a section being built.
- [ ] Say where the line is written and removed in `.claude/skills/review-todo-section/SKILL.md` (a section that stays unstamped because it waits on an owner decision, a dated event or the cap), `.claude/skills/process-todo-section/SKILL.md` (a plan-parked section; on resume, remove the line in the first commit) and `.claude/skills/process-phase/SKILL.md` (Step 1.3: for each parked section of the phase, check whether what it waits on has happened, and resume it if so). Done when: each skill names the line and the moment, and `python -m unittest discover -s scripts/tests -p "test_skill*.py"` passes where such tests exist. Cheaper substitute: leaving it to the lead's memory of the run file.
- [ ] Park §53 (waits on the owner decision §56) and D00 T07 §4 (waits on the scheduled run of Monday 2026-11-16, 07:05 local time) with the line, and make §53 depend on §56 in its Implementation Order row, since that is what it waits on. Done when: `python scripts/todo-graph.py query ready` lists neither, `python scripts/merge_prs.py --session <this session>` no longer names either, and `python scripts/campaign_guard.py stop-hook`'s next row, read from `query ready`, is a section that can be worked on.
- [ ] Commit: `todo: a parked section is neither ready nor in progress`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_todo_graph.py"` and `python -m unittest discover -s scripts/tests -p "test_merge_prs.py"` pass with the tests named above among them, and `python scripts/todo-graph.py query ready` lists neither §53 nor D00 T07 §4.
## Verification
- `python -m unittest discover -s scripts/tests` passes on a fresh clone.
- `Get-ScheduledTask -TaskPath '\Office\'` lists every task in `tasks.json`, and `README.md` matches it.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
