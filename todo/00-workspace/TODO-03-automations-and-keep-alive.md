---
schema_version: 1
id: automations-and-keep-alive
domain: 00-workspace
status: active
title: "TODO-03 -- Automations and Campaign Keep-Alive"
---

# TODO-03 -- Automations and Campaign Keep-Alive

> **Goal:** Office runs its scheduled jobs from `.conclave/automations/`, as Isotone does: a task list, a runner that logs every run, an email alert on failure, and a Task Scheduler installer. Long `process-plan` and `process-phase` runs are protected by a run guard, a Stop hook that keeps the owning session working while a run is open, the in-session heartbeat, and a keep-alive task that resumes the exact session headless when its process has died. Every piece has a self-test or unit test, and the operator can see what the keep-alive would do with one command.

> **Current state:** Measured 2026-10-20. `.conclave/` holds only `reviewers.toml`; there is no `.claude/settings.json`, no hook, no guard, and no scheduled task. The phase 2 run (`docs/phase-runs/2026-10-20-phase-2.md`) has an in-session `CronCreate` heartbeat whose prompt reads the run file, but nothing survives the session ending. The source to port is Isotone (`R:\GitHub\Isotone`), itself adapted from Rizonetech: `.conclave/automations/{run.py,alert.py,install.ps1,tasks.json,README.md}` (337 lines), `scripts/campaign_guard.py` (1,515 lines with a built-in `--self-test`), `scripts/campaign_keepalive.py` (656 lines with `--self-test`), `.claude/hooks/campaign-stop.ps1` (273 lines), and `scripts/tests/test_automations.py`. Three Isotone assumptions do not hold here: `todo-graph.py query ready` prints JSON, not an `N runnable now` line; the writer model comes from `.conclave/panel.toml`, which this repository does not have; and Isotone's other tasks (.NET SDK, NuGet, panel probe) do not apply. **Renamed 2026-10-20 (owner):** the repository Office-2028 became Office (GitHub `rizonesoft/Office`, local `R:\GitHub\Office`); the Task Scheduler folder is now `\Office\` and the task names `office-*`. Review records under `docs/reviews/` and the phase run files keep the names they verified. **Revised 2026-10-21 (operator):** Office adopted the Conclave-SDK todo and reviewer kits as shipped. The run guard is now the kit's `scripts/campaign_guard.py` with its Python Stop hook (`campaign_guard.py stop-hook` in `.claude/settings.json`) and the in-session heartbeat, tested by `scripts/tests/test_campaign_guard.py`; the keep-alive (§3: `scripts/campaign_keepalive.py`, `.conclave/keepalive.toml`, the SessionStart observer and the `office-claude-keepalive` task), `.claude/hooks/campaign-stop.ps1`, the guard's `--self-test` and CI repair ledger, and the Codex and Antigravity `acquire --runner` guard steps were retired. The sections below record what was built and verified on 2026-10-20.

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
| 7 | §7 | Run guard robustness fixes | §2 | [ ] |
| 8 | §8 | Agent tier verifier YAML strictness | -- | [ ] |
| 9 | §9 | Dependency PR merges at boundaries | §1 | [ ] |

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

Three defects the owner reported on 2026-10-21, found by independent review in a sibling repository and present in Office's guard (`scripts/campaign_guard.py`), each verified here: `fingerprint` calls `os.stat` (following symlinks) on every untracked path and `open()` on any of the first 500, so a FIFO or device in the working tree blocks the Stop hook and a symlink to a directory raises; `acquire` defaults `--phase` to `0`, so a re-point of the owner's own guard (the heartbeat repair at a section boundary) silently resets the run to phase 0; `end` records the pending cancellation, then deletes the guard, so an end interrupted between the two leaves a guard `whoami` still reports as OWNER, and the heartbeat resumes a run that was stopped.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write a failing test for each defect in `scripts/tests/test_campaign_guard.py`. Done when: each fails on the current guard.
2. Fix each at its owning function. Done when: the tests pass and the full guard suite stays green.

- [ ] Make `fingerprint` in `scripts/campaign_guard.py` read each untracked path with `os.lstat`, hash only regular files, record a symlink by its target text and any other entry by its type, and make no filesystem call for a path past both bounds. Done when: a test with a FIFO (POSIX) or a stub `os.lstat` reporting a character device, and a symlink to a directory, returns a fingerprint without opening either. Cheaper substitute: catching the exception after the hook has already blocked.
- [ ] Make `--phase` optional in `scripts/campaign_guard.py` `acquire`: a fresh guard requires it, and a re-point of the owner's own guard without it keeps the guard's phase. Done when: a test re-pointing with a new `--cron-id` and no `--phase` keeps phase 2, and a fresh `acquire` without `--phase` is refused. Cheaper substitute: documenting that every re-point must repeat `--phase`.
- [ ] Mark the guard ended before deleting it in `scripts/campaign_guard.py` `_end_locked`: write `ended` (reason and time) into the guard atomically with the pending cancellation, and make `whoami`, `stop-hook` and `acquire` treat an ended guard as over and finish its deletion. Done when: a test that stops `end` after the pending record is written sees `whoami` print `NO GUARD`, the Stop hook let the turn end, and a later `acquire` start a fresh run. Cheaper substitute: retrying the delete in a loop.
- [ ] Record each defect, its test and the fix in `docs/reviews/00-workspace/D00-T03-s7.md` with the failing-before and passing-after outputs. Done when: three entries quote both results. Cheaper substitute: one summary line.
- [ ] Commit: `guard: fix device and symlink stalls, phase resets on re-point, and interrupted ends`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_campaign_guard.py"` passes, and its three new tests fail when the previous `scripts/campaign_guard.py` is restored.

## 8. Agent Tier Verifier YAML Strictness

`scripts/verify-agent-tiers.mjs` reads agent frontmatter as a closed subset of YAML, but the owner reported on 2026-10-21 that it accepts a line Claude Code cannot load, so an agent passes the check and then fails to load. The file is Office's own (the Conclave SDK link was cut on 2026-10-21), so the fix lands here. The usual case is a plain scalar YAML refuses, such as a value containing `: ` or ` #`, or opening with an indicator character.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Find every frontmatter line the verifier accepts and a YAML 1.2 loader refuses. Done when: the cases are listed with the loader's error.
2. Refuse those lines in the verifier with fixtures. Done when: each case fails the verifier and every agent in `.claude/agents/` still passes.

- [ ] List the frontmatter lines `scripts/verify-agent-tiers.mjs` accepts but a YAML 1.2 loader refuses (a plain scalar containing `: ` or ` #`, opening with an indicator character such as `@`, `` ` ``, `%`, `[`, `{`, `|`, `>`, `!`, `&`, `*`, or holding a tab), checked against a real loader. Done when: `docs/reviews/00-workspace/D00-T03-s8.md` lists each case with the loader's error. Cheaper substitute: guessing the cases without a loader.
- [ ] Refuse each listed case in `scripts/verify-agent-tiers.mjs` with a message naming the line and the rule. Done when: a fixture agent for each case fails the verifier. Cheaper substitute: refusing only the reported case.
- [ ] Add the fixtures and a test runner for them in `scripts/tests/test_verify_agent_tiers.py`, invoking `node scripts/verify-agent-tiers.mjs` on fixture directories. Done when: the suite passes, and fails when the new refusals are removed. Cheaper substitute: checking the repository's own agents only.
- [ ] Commit: `tooling: refuse agent frontmatter Claude Code cannot load`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_verify_agent_tiers.py"` passes and `node scripts/verify-agent-tiers.mjs` reports every agent in `.claude/agents/` valid.

## 9. Dependency PR Merges at Boundaries

Owner request 2026-10-21 (replacing "nothing merges by itself" for dependency pull requests): merge green dependency pull requests inside the campaign loop at section boundaries, the one moment the clone matches GitHub, with a scheduled fallback when no campaign runs. Office has no pull request source yet, so this adds Dependabot for GitHub Actions only; NuGet pins stay with the local proposal tasks, because the WinUI 3 pin follows `winui3/release` builds, which Dependabot cannot express. Local proposal branches (`winui/*`, `dotnet/*`, `pins/*`) still wait for the owner's merge.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `scripts/merge_prs.py` with its safety checks and tests. Done when: it merges an eligible fixture pull request and refuses every unsafe state.
2. Wire it into `process-plan` and the automations. Done when: the skill runs it after each stamp push and the task is installed.

- [ ] Add `.github/dependabot.yml` for the `github-actions` ecosystem, weekly, labelled `dependencies`. Done when: the file validates and GitHub lists the Dependabot configuration. Cheaper substitute: bumping action majors by hand.
- [ ] Write `scripts/merge_prs.py` refusing to run unless the working tree is clean, `HEAD` equals `origin/main` after a fetch, and no open section carries a `Started:` line. Done when: a test of each state exits non-zero naming it. Cheaper substitute: merging from a dirty or unpushed clone.
- [ ] Select eligible pull requests in `scripts/merge_prs.py`: author `dependabot[bot]` or `github-actions[bot]`, a `dependencies` or `pins` label, every check green, mergeable and clean, and no change to `global.json` (the .NET SDK pin moves only through its own proposal). Done when: a test over fixture `gh pr list` JSON selects exactly the eligible ones. Cheaper substitute: merging every Dependabot pull request.
- [ ] Merge one pull request at a time in `scripts/merge_prs.py` with `gh pr merge --rebase --match-head-commit <sha>`, then `git pull --ff-only`, then `python scripts/todo-graph.py validate`, stopping at the first failure and leaving that pull request open. Done when: a test with a failing merge or validate leaves the later pull requests unmerged and exits 1. Cheaper substitute: merging all and validating once at the end.
- [ ] Refuse to run while a campaign is open in `scripts/merge_prs.py` unless `--session` names the guard's own session (`build/claude-campaign-guard.json`). Done when: a test with a guard owned by another session exits non-zero, and one with `--session <owner>` runs. Cheaper substitute: checking for a lock file of another tool.
- [ ] Write `scripts/tests/test_merge_prs.py` covering the safety states, eligibility, the merge sequence and the campaign check with fake `git` and `gh`. Done when: the suite passes and fails when any one safety check is removed. Cheaper substitute: a dry run against the live repository only.
- [ ] Add the run after each stamp push to `process-plan` in `.claude/skills/`, `.agents/skills/` and `.codex/skills/`, before the next row is claimed, with a failure recorded in the run file and the campaign continuing. Done when: all three mirrors name `python scripts/merge_prs.py --session <id>` at the section boundary. Cheaper substitute: merging only when the operator asks.
- [ ] Add an `office-pr-merge` task to `.conclave/automations/tasks.json`, with its README row and line, and install it. Done when: `test_automations.py` passes and `Get-ScheduledTask -TaskPath '\Office\'` lists it. Cheaper substitute: no fallback when no campaign runs.
- [ ] Update `.conclave/automations/README.md` and `AGENTS.md` with the merge rule: green dependency pull requests merge by themselves at section boundaries or on the schedule; local proposal branches still wait for the owner. Done when: both state it and no line says dependency pull requests wait for a manual merge. Cheaper substitute: the rule only in the script's docstring.
- [ ] Commit: `automations: merge green dependency pull requests at section boundaries`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_merge_prs.py"` passes, and `python scripts/merge_prs.py --session <this session>` at a section boundary exits 0 reporting the pull requests it merged or that none were eligible.

## Verification

- `python -m unittest discover -s scripts/tests` passes on a fresh clone.
- `Get-ScheduledTask -TaskPath '\Office\'` lists every task in `tasks.json`, and `README.md` matches it.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
