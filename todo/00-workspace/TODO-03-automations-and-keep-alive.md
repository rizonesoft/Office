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
| 16 | §16 | Completion evidence adoption boundary | §14 | [ ] |
| 17 | §17 | CI push reconciliation | §15 | [ ] |
| 18 | §18 | CI recovery budget | §15 | [ ] |
| 19 | §19 | CI gate checks | §15, §17, §18 | [ ] |

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

- [ ] Record `completion_rules: 2` in every receipt `stamp` writes from §14 on, and accept a receipt without the field as `completion_rules: 1` (the D00 T03 §13 rules) in `receipt_data_ok` in `scripts/lib/todo_graph.py`, never applying the version 2 checks to it. Done when: `python scripts/todo-graph.py validate` passes with the stored D00 T03 §12 and §13 receipts unchanged, and a receipt claiming `completion_rules: 2` whose record lacks a `CONTRACT:` line is refused. Cheaper substitute: adding a digest to an old review by hand.
- [ ] Refuse in `stamp` any completion evidence that fails the version 2 rules, a re-stamp after `unstamp` included, whatever rules the section's earlier receipt met. Done when: a test unstamps a section stamped under version 1 and refuses its re-stamp with the old digest-free record, then accepts it after a fresh round with the `CONTRACT:` line. Cheaper substitute: letting a reopened section re-stamp on evidence from before the hardening.
- [ ] State the boundary in the stamps paragraph of `todo/README.md` and in `.claude/skills/review-todo-section/SKILL.md`. Done when: both name `completion_rules`, the two versions and the re-stamp rule. Cheaper substitute: a rule only the code knows.
- [ ] Commit: `automations: keep stored receipts under their own completion rules and harden every new stamp`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_todo_graph.py"` passes and `python scripts/todo-graph.py validate` exits 0 with every stored receipt unchanged.

## 17. CI Push Reconciliation

Filed 2026-10-23 from round 1 of D00 T03 §15's completion review (`docs/reviews/00-workspace/D00-T03-s15-completion.md`, finding 3): §15 records `ci-pending` only after a stamp push, so a dependency merge, a closeout push, another campaign push, or a session that dies between a push and its record leaves a commit on `main` whose CI nobody checks. This section makes the pending set come from the pushed history, not from notes. **Groomed 2026-10-23:** finding 1 of round 2 of §15's completion review: GitHub runs a push workflow only for the push's tip, so the unit is the push head, not every commit; commits under a green head are covered by it.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Derive the unchecked pushes from git and the run files. Done when: a command lists every commit on `origin/main` since the last `ci-green` that has no `ci-green` record.
2. Run the reconciliation at campaign start, phase start and every resume. Done when: both skills name it.

- [ ] Add `--pending <run file>` to `scripts/ci-status.py`: list the push heads on `origin/main` after the newest head recorded `ci-green` in that run file or any earlier run file in `docs/phase-runs/` (a push head is a commit recorded `ci-pending`, or the `headSha` of a `ci.yml` push run on `main`, or `origin/main` itself), and report the status of each, oldest first; a commit that is not a push head is covered by the first push head after it and is never checked on its own. Done when: fixtures with a merge commit, a closeout push and an unrecorded stamp push each list the unchecked head, two implementation commits pushed with their stamp list only the stamp, and a history whose head is recorded green lists nothing. Cheaper substitute: trusting the run file's own `ci-pending` notes, or checking every commit and parking on runs GitHub never creates.
- [ ] Record `ci-pending <sha> <UTC>` for every campaign push, not only stamp pushes: dependency merges by `scripts/merge_prs.py`, closeout and park commits, and repair commits, in `.claude/skills/process-plan/SKILL.md`. Done when: the skill names each push kind. Cheaper substitute: watching only the stamp commits.
- [ ] Run `python scripts/ci-status.py --pending <run file>` at campaign start, at every phase start and on every manual or heartbeat resume, before any row is claimed, and act on each listed commit with §15's exit rules, in `.claude/skills/process-plan/SKILL.md` and `.claude/skills/process-phase/SKILL.md`. Done when: both skills name the command and the three moments. Cheaper substitute: losing a red commit when a session dies between its push and its record.
- [ ] Commit: `automations: reconcile unchecked pushes with CI on start and resume`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_ci_status.py"` passes and `python scripts/ci-status.py --pending docs/phase-runs/2026-10-23-phase-0.md` lists the pushed commits without a `ci-green` record on this PC.

## 18. CI Recovery Budget

Filed 2026-10-23 from round 1 of D00 T03 §15's completion review (finding 6): §15 bounds the repair at three commits that leave the same job red, which misses an infrastructure outage, an unreadable log, a rerun that fails, and repairs that turn a different job red each time. This section gives the whole recovery one budget that survives a resume.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Persist the budget per red commit. Done when: the run file records each attempt.
2. Escalate when it is spent, whatever the cause. Done when: the skill names every way the budget is consumed.

- [ ] Record each recovery attempt for a red commit in the run file as `ci-attempt <sha> <n> <kind>` (`repair`, `rerun`, `wait`, `unreadable`), in `.claude/skills/process-plan/SKILL.md`, read back on resume so a resumed session continues the count. Done when: the skill names the record and that resume reads it. Cheaper substitute: a budget that starts again with every session.
- [ ] Spend at most four attempts on one red `main` (any mix of repair commits, the single flake rerun, a bounded wait, an unreadable result), counting a repair that turns another job red against the same budget; when it is spent, file the failure through `add-todo`, email the owner through `.conclave/automations/alert.py`, and park with `ci-red` even when no useful code change exists. Done when: the skill names the budget, what consumes it, the filing, the email and the park. Cheaper substitute: three repair commits per job, which an outage or alternating jobs never reaches.
- [ ] Define the single flake rerun: one `gh run rerun <id> --failed` per red commit, counted against the budget; a pass records `ci-flaky <sha> <job>` and files the flake through `add-todo`; a fail continues the repair. Done when: the skill names the one rerun and both outcomes. Cheaper substitute: re-running until green.
- [ ] Commit: `automations: one recovery budget per red main, kept across resumes`

**Test checkpoint:** `python scripts/check-design-doc.py .claude/skills/process-plan/SKILL.md` exits 0 and `Select-String -Path .claude/skills/process-plan/SKILL.md -Pattern 'ci-attempt'` finds the record.

## 19. CI Gate Checks

Filed 2026-10-23 from round 1 of D00 T03 §15's completion review (finding 8): the CI gate lives mostly in skill prose, which a test of `scripts/ci-status.py` alone cannot hold to its word. This section adds checks that fail when the skills and the guard stop enforcing it.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Teach the run guard the CI parks. Done when: the Stop hook and `whoami` treat a `ci-red` or `ci-unknown` park like `host-not-ready`.
2. Lint the skills for the gate. Done when: a test fails when a required step is removed.

- [ ] Make `scripts/campaign_guard.py` treat a column-0 `PARKED ... run=<run id> ci-red:`, `ci-unknown:` or `host-not-ready:` line as campaign-ending in either scope (the Stop hook lets the turn end, and a resumed run must start fresh), with tests in `scripts/tests/test_campaign_guard.py`. Done when: tests prove each reason ends the run and a phase park without one still chains. Cheaper substitute: relying on the heartbeat prompt's wording alone.
- [ ] Add `scripts/tests/test_skill_ci_gate.py`, which reads `.claude/skills/process-plan/SKILL.md` and `.claude/skills/process-phase/SKILL.md` and fails unless each names the boundary check, the four exit actions, the three hard gates, the resume check, the pending reconciliation and the recovery budget. Done when: the test passes, and removing any one of those lines from a copy makes it fail. Cheaper substitute: reading the skills by eye.
- [ ] Commit: `automations: hold the campaign to its CI gate with guard and skill checks`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_skill_ci_gate.py"` and `python -m unittest discover -s scripts/tests -p "test_campaign_guard.py"` pass.

## Verification

- `python -m unittest discover -s scripts/tests` passes on a fresh clone.
- `Get-ScheduledTask -TaskPath '\Office\'` lists every task in `tasks.json`, and `README.md` matches it.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
