---
schema_version: 1
id: automations-and-keep-alive
domain: 00-workspace
status: active
title: "TODO-03 -- Automations and Campaign Keep-Alive"
---

# TODO-03 -- Automations and Campaign Keep-Alive

> **Goal:** Office-2028 runs its scheduled jobs from `.conclave/automations/`, as Isotone does: a task list, a runner that logs every run, an email alert on failure, and a Task Scheduler installer. Long `process-plan` and `process-phase` runs are protected by a run guard, a Stop hook that keeps the owning session working while a run is open, the in-session heartbeat, and a keep-alive task that resumes the exact session headless when its process has died. Every piece has a self-test or unit test, and the operator can see what the keep-alive would do with one command.

> **Current state:** Measured 2026-10-20. `.conclave/` holds only `reviewers.toml`; there is no `.claude/settings.json`, no hook, no guard, and no scheduled task. The phase 2 run (`docs/phase-runs/2026-10-20-phase-2.md`) has an in-session `CronCreate` heartbeat whose prompt reads the run file, but nothing survives the session ending. The source to port is Isotone (`R:\GitHub\Isotone`), itself adapted from Rizonetech: `.conclave/automations/{run.py,alert.py,install.ps1,tasks.json,README.md}` (337 lines), `scripts/campaign_guard.py` (1,515 lines with a built-in `--self-test`), `scripts/campaign_keepalive.py` (656 lines with `--self-test`), `.claude/hooks/campaign-stop.ps1` (273 lines), and `scripts/tests/test_automations.py`. Three Isotone assumptions do not hold here: `todo-graph.py query ready` prints JSON, not an `N runnable now` line; the writer model comes from `.conclave/panel.toml`, which this repository does not have; and Isotone's other tasks (.NET SDK, NuGet, panel probe) do not apply.

## Inputs

- Isotone's `.conclave/automations/README.md`: the behaviour to reproduce, including the keep-alive's launch rules, supervision and stall breaker.
- Isotone's `process-plan` and `process-phase` skills: the guard, Stop hook and heartbeat steps the runners follow.
- Alert transport: SMTP2GO from `website@rizonetech.com` to `rizonetech@gmail.com`, key read at send time from the Conclave vault item "Rizonetech SMTP2GO (website mail)" through `conclave-op` in WSL (Rizonesoft is a brand of Rizonetech). AGENTS.md: ask the operator once before sending mail.
- The open phase 2 run (`docs/phase-runs/2026-10-20-phase-2.md`), which §6 moves under the guard.

## Outcome

- `pwsh .conclave/automations/install.ps1` registers every task in `tasks.json` under `\Office-2028\`, and `python scripts/tests/test_automations.py` passes, failing when README and `tasks.json` disagree.
- `python scripts/campaign_guard.py --self-test` and `python scripts/campaign_keepalive.py --self-test` pass against fixture workspaces that use this repository's JSON `query ready` output.
- While a run is open, the Stop hook blocks the owning session's end of turn and names the next ready row; a stopped session is resumed by the `office-2028-claude-keepalive` task, and `python scripts/campaign_keepalive.py status` says what it would do now.

**Adjacency:** all=not-applicable (developer automation for this repository; no product records, settings or user documents)

**Adjacency rationale:** These are build-machine jobs and session supervision for the people and agents building the suite. They hold no user data, so none of the nine product keys applies.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Automation runner, failure alert and installer | -- | [x] |
| 2 | §2 | Run guard and Stop hook | -- | [x] |
| 3 | §3 | Keep-alive resume task and session observer | §1, §2 | [x] |
| 4 | §4 | Run skills create and check the guard | §2, §3 | [ ] |
| 5 | §5 | Install the tasks and verify on this PC | §1, §3 | [ ] |
| 6 | §6 | Adopt the guard for the open phase 2 run | §4, §5 | [ ] |

## 1. Automation Runner, Failure Alert and Installer

> **Started:** 2026-10-20T00:24:39Z

The shared plumbing every scheduled job uses: the task list, a runner that logs each run and alerts on failure, the alert sender, and the installer that keeps Task Scheduler in step with the list. Ported from Isotone with names and paths changed and Isotone's own tasks left out.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Port `run.py`, `alert.py`, `install.ps1` and `README.md` into `.conclave/automations/` with Office-2028 names. Done when: `python .conclave/automations/alert.py --help` runs and `python .conclave/automations/run.py <unknown task>` exits 2 naming it. **Corrected 2026-10-20:** said `run.py --help`; the ported runner takes only a task name.
2. Port `scripts/tests/test_automations.py`. Done when: it passes against an Office-2028 `tasks.json`.

- [x] Copy `run.py` from Isotone to `.conclave/automations/run.py`, changing the log root to `build/automations/<name>/` under this repository and every Isotone name to Office-2028. Done when: `python .conclave/automations/run.py <fixture task>` writes a log and `last.json` under `build/automations/`. Cheaper substitute: invoking scripts straight from Task Scheduler with no log or outcome file.
- [x] Copy `alert.py` to `.conclave/automations/alert.py` with the subject prefix `Office-2028` and the same SMTP2GO sender, recipient and vault item. Done when: `python .conclave/automations/alert.py <task> --dry-run` prints the message without sending and without reading the key. Cheaper substitute: an API key in a file or environment variable.
- [x] Copy `install.ps1` to `.conclave/automations/install.ps1` registering under `\Office-2028\` and removing tasks the list no longer names. Done when: `install.ps1 -DryRun` lists the tasks it would register and remove, changing nothing. Cheaper substitute: tasks created by hand in Task Scheduler.
- [x] Write `.conclave/automations/tasks.json` with schema version 1, folder `\Office-2028\`, and no Isotone task. Done when: it parses and the test in this section reads it. Cheaper substitute: copying Isotone's tasks, which call scripts this repository does not have.
- [x] Write `.conclave/automations/README.md` from Isotone's, describing only Office-2028 tasks. Done when: `python scripts/check-design-doc.py .conclave/automations/README.md --require "What runs" --require "When a run fails"` exits 0. Cheaper substitute: linking to Isotone's README.
- [x] Port `scripts/tests/test_automations.py` with Office-2028 names. Done when: `python -m unittest discover -s scripts/tests -p "test_automations.py"` passes and fails when a README table row and `tasks.json` disagree.
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

- [x] Copy `campaign_guard.py` from Isotone to `scripts/campaign_guard.py`, renaming every Isotone mention to Office-2028. Done when: `rg -n -i isotone scripts/campaign_guard.py` returns nothing. Cheaper substitute: a hand-written guard without the lock, generations and pending-cancel record.
- [x] Replace `_ready_count` in `scripts/campaign_guard.py` with a reader of the JSON list `todo-graph.py query ready` prints, counting its entries. Done when: a fixture `todo-graph.py` printing a two-entry list reads as 2, and invalid output reads as unknown. Cheaper substitute: keeping the `N runnable now` regex, which never matches here, so plan-done could never be proven.
- [x] Update the self-test's fixture `todo-graph.py` writer to print a JSON list of the controlled length. Done when: `python scripts/campaign_guard.py --self-test` passes every case except the 13 `skill-*` cases. **Corrected 2026-10-20:** the self-test also reads the real `process-plan` skill for the guard steps, which land in §4; those cases pass there. Cheaper substitute: skipping the self-test cases that need a ready count.
- [x] Copy `campaign-stop.ps1` to `.claude/hooks/campaign-stop.ps1`, reading the next ready ref from the JSON list. Done when: the self-test's hook cases pass. Cheaper substitute: a Stop hook that always blocks, which traps every session.
- [x] Create `.claude/settings.json` with the Stop hook entry, using the same `CLAUDE_PROJECT_DIR` launch line as Isotone. Done when: the file parses and names `campaign-stop.ps1`. Cheaper substitute: wiring the hook in user-level settings, which would fire in every repository.
- [x] Add `scripts/tests/test_campaign_guard.py` that runs `python scripts/campaign_guard.py --self-test` and fails on any failed case other than the `skill-*` cases until §4 (`SKILL_TEXT_CASES_PENDING`). Done when: `python -m unittest discover -s scripts/tests` includes it and it fails when a non-skill case fails.
- [x] Commit: `automations: add campaign run guard and Stop hook`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_campaign_guard.py"` passes, with `python scripts/campaign_guard.py --self-test` failing only its 13 `skill-*` cases (**Corrected 2026-10-20:** said the self-test exits 0; that is §4's checkpoint).

> **Verified:** 2026-10-20 | §2 | b10277a6db91c37d4f78db3d7b32c8c4567d2905
> **Review:** `docs/reviews/d00-t03-s2.json`

## 3. Keep-Alive Resume Task and Session Observer

> **Started:** 2026-10-20T01:08:32Z

When the owning session's process is gone and no other Office-2028 session is open, the keep-alive resumes that exact session headless and supervises it. The SessionStart hook records each session's process so death can be proven, never guessed.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Port `scripts/campaign_keepalive.py` with the writer model read from `.conclave/keepalive.toml`. Done when: `python scripts/campaign_keepalive.py --self-test` passes.
2. Wire the SessionStart hook and the task. Done when: `.claude/settings.json` names `campaign_keepalive.py observe` and `tasks.json` lists `office-2028-claude-keepalive`.

- [x] Copy `campaign_keepalive.py` to `scripts/campaign_keepalive.py`, renaming Isotone to Office-2028 in the prompt, messages and task name. Done when: `rg -n -i isotone scripts/campaign_keepalive.py` returns nothing. Cheaper substitute: a resume script that relaunches whenever no window is open, without proving the owner gone.
- [x] Write `.conclave/keepalive.toml` with `[writer] model = "claude-opus-5-5"` and change `writer_model()` to read it. Done when: the self-test's fixture reads the model from `keepalive.toml`, and a missing file makes `resurrect` refuse with a setup message before counting a resume (**Corrected 2026-10-20:** said `status`; only a launch reads the model). Cheaper substitute: hard-coding the model in the script.
- [x] Add the SessionStart hook to `.claude/settings.json` running `campaign_keepalive.py observe`. Done when: starting a new Claude session writes `build/claude-sessions/<session>.json`. Cheaper substitute: observing only when a run starts, which cannot prove an older session gone.
- [x] Add `office-2028-claude-keepalive` to `.conclave/automations/tasks.json` (3 minutes after logon, then hourly, timeout 245 minutes) and its row to the README table. Done when: `test_automations.py` passes with the new task. Cheaper substitute: a task the README does not describe.
- [x] Add `scripts/tests/test_campaign_keepalive.py` running `--self-test`. Done when: it fails when the self-test fails.
- [x] Commit: `automations: add campaign keep-alive and session observer`

**Test checkpoint:** `python scripts/campaign_keepalive.py --self-test` exits 0, and `python -m unittest discover -s scripts/tests -p "test_campaign_keepalive.py"` passes.

> **Verified:** 2026-10-20 | §3 | 081daed7eb99383e0f4175fef13c2315ba624e57
> **Review:** `docs/reviews/d00-t03-s3.json`

## 4. Run Skills Create and Check the Guard

`process-plan` and `process-phase` gain the run-guard steps from Isotone: reconcile and create the heartbeat with its canonical prompt, acquire the guard, observe the session, check heartbeat health and expiry at each section boundary, and end the run through `campaign_guard.py end`. Skills live in three mirrored directories and change together (AGENTS.md).

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Port the guard sections of Isotone's `process-plan` and `process-phase` into `.claude/skills/`, then mirror them. Done when: the three copies of each skill are identical apart from agent-specific tool names.

- [ ] Add the run-guard section (reconcile, mint a generation, `CronCreate` with the canonical heartbeat prompt, `acquire`, `observe`) to `.claude/skills/process-plan/SKILL.md`, adapted to Office-2028 names. Done when: the canonical prompt names `Office-2028` and `campaign_guard.py`. Cheaper substitute: a heartbeat with no guard, which cannot tell its owner from a stale job.
- [ ] Add the section-boundary heartbeat check and the guard-aware stop and park rules to `.claude/skills/process-phase/SKILL.md`. Done when: the skill names `health`, `expiry` and `end --reason`. Cheaper substitute: deleting the guard file by hand at a stop.
- [ ] Set `SKILL_TEXT_CASES_PENDING = False` in `scripts/tests/test_campaign_guard.py` so the guard self-test must exit 0. Done when: the test fails if any `skill-*` case fails. Cheaper substitute: leaving the staging flag on.
- [ ] Mirror both skills to `.agents/skills/` and `.codex/skills/` as real files. Done when: a diff of the three copies shows only agent-specific wording. Cheaper substitute: symlinks, which AGENTS.md forbids.
- [ ] Add the operator rule from the phase 2 run (a go-ahead before every live Office capture, recorded as `- waiting:` and `- go-ahead:` lines that the heartbeat honours) to the canonical prompt. Done when: the prompt names both line forms. Cheaper substitute: relying on memory of the rule across sessions.
- [ ] Commit: `skills: run plan and phase under the campaign guard`

**Test checkpoint:** `python scripts/campaign_guard.py --self-test` exits 0 after the skill change, and `rg -c "campaign_guard.py" .claude/skills/process-plan/SKILL.md .agents/skills/process-plan/SKILL.md .codex/skills/process-plan/SKILL.md` prints a non-zero count for each file.

## 5. Install the Tasks and Verify on This PC

Registers the tasks in Task Scheduler on the operator's Windows host and proves each piece live: the task exists with the right triggers, the keep-alive's `status` answers, and the alert renders. A real alert email is sent once, only with the operator's go-ahead.

**Phase:** 0
**Needs:** windows-host, attended
**Surface:** no

**Build order:**

1. Run `pwsh .conclave/automations/install.ps1`. Done when: `Get-ScheduledTask -TaskPath '\Office-2028\'` lists every task in `tasks.json`.
2. Verify each task and the alert. Done when: the findings below are recorded in `.conclave/automations/README.md` under `## Install and inspect`.

- [ ] Run `pwsh .conclave/automations/install.ps1` and read back `Get-ScheduledTask -TaskPath '\Office-2028\' | Get-ScheduledTaskInfo`. Done when: `office-2028-claude-keepalive` shows its next run time. Cheaper substitute: assuming the installer worked.
- [ ] Run `python scripts/campaign_keepalive.py status` with a run open and with none. Done when: it prints `hold` while this session is alive and `no open run` after the guard ends. Cheaper substitute: reading the code instead of running it.
- [ ] Run `python .conclave/automations/alert.py office-2028-claude-keepalive --dry-run`. Done when: the rendered alert names the task, its exit and the log tail. Cheaper substitute: none; the dry run sends nothing.
- [ ] With the operator's go-ahead, send one real alert by running `python .conclave/automations/run.py` on a fixture task that exits 1. Done when: the operator confirms the email arrived, and the run's `last.json` records the send. Cheaper substitute: declaring the alert path working from the dry run alone.
- [ ] Commit: `automations: record install and live verification`

**Test checkpoint:** `Get-ScheduledTask -TaskPath '\Office-2028\' | Select-Object -ExpandProperty TaskName` lists `office-2028-claude-keepalive`, and `python scripts/campaign_keepalive.py status` exits 0.

## 6. Adopt the Guard for the Open Phase 2 Run

The phase 2 run was opened before the guard existed. This section moves it under the guard: acquire with this session, replace the interim heartbeat with the canonical one, and record the ids in the run file.

**Phase:** 0
**Needs:** attended
**Surface:** no

**Build order:**

1. Acquire the guard for `docs/phase-runs/2026-10-20-phase-2.md`. Done when: `build/claude-campaign-guard.json` names this session, phase 2 and the run file.
2. Replace the interim heartbeat. Done when: `CronList` shows only the canonical job and the guard names its id.

- [ ] Run `python scripts/campaign_guard.py acquire` with this session id, phase 2, the run file and a fresh generation. Done when: `python scripts/campaign_guard.py whoami --session <id>` prints that this session owns the run. Cheaper substitute: writing the guard file by hand.
- [ ] `CronDelete` the interim heartbeat and `CronCreate` the canonical one from `process-plan`, then re-point the guard to its id. Done when: `python scripts/campaign_guard.py health --session <id> --jobs <id>` reports healthy. Cheaper substitute: keeping the interim prompt, which the guard cannot verify.
- [ ] Record the guard's run id and the heartbeat job id under Critical events in the run file. Done when: both ids appear with a UTC time. Cheaper substitute: ids only in chat.
- [ ] Commit: `todo: put the phase 2 run under the campaign guard`

**Test checkpoint:** `python scripts/campaign_guard.py whoami --session <this session id>` prints the owner line, and `python scripts/campaign_keepalive.py status` prints `hold`.

## Verification

- `python scripts/campaign_guard.py --self-test`, `python scripts/campaign_keepalive.py --self-test` and `python -m unittest discover -s scripts/tests` pass on a fresh clone.
- `Get-ScheduledTask -TaskPath '\Office-2028\'` lists every task in `tasks.json`, and `README.md` matches it.
- A killed run session is resumed by the keep-alive within an hour, observed once and recorded in the run file.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
