---
name: process-plan
description: Run the Office implementation plan with Codex as writer and the repository's independent reviewer.
---

# Process plan in Codex

Read `AGENTS.md` and `docs/codex-campaign.md`, then execute the repository's canonical `.claude/skills/process-plan/SKILL.md` workflow. Its plan audit, section build, review, stamp, closeout and park rules remain authoritative. Read the other local workflow skills it references as procedure documents. The following Codex runtime rules replace only the Claude-specific session and timer instructions.

Use this thread's `CODEX_THREAD_ID` for every campaign guard operation, never an inherited Claude session id. In PowerShell use `$env:CODEX_THREAD_ID`. The `.codex/hooks.json` Stop hook calls this project's `scripts/codex-campaign-hook.py` and shares its existing campaign guard with every other writer.

Codex has no Claude timer. Mint a generation and acquire the guard with `--cron-id none`, using the run file, phase and scope required by the canonical workflow. Refuse another live writer. Do not create or renew CronCreate jobs, call CronList or CronDelete, or end a turn expecting a timer to wake it. Wait for reviews and CI inside the session, then continue. End the guard with the native session id on closeout, park, escalation or operator stop. Clear any pending cancellation for the `none` job through `cancel-confirmed`; never delete guard files directly.

Use `--writer codex` and the exact running model id on independent reviews. Keep the existing review schedule and all delivery checks. Never review your own work. Set the requested campaign objective as the session goal when the goal tool is available. The operator's stop ends the run regardless of remaining work.
