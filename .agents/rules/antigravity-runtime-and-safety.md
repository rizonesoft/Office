---
trigger: always_on
description: Runtime mapping, output discipline, and safety rules for Antigravity CLI sessions on Rizonesoft Office.
---

# Antigravity Runtime, Output, and Safety Rules

Follow [AGENTS.md](../../AGENTS.md) and these runtime and safety rules in every Antigravity (`agy`) session.

## Antigravity tool and campaign mappings

- **Skills discovery**: Project skills live in `.claude/skills/<name>/SKILL.md` and are exposed to Antigravity through `.agents/skills.json`. Always read a skill's `SKILL.md` before executing its workflow.
- **Session identifier (`$CLAUDE_CODE_SESSION_ID`)**: Where a skill (`process-plan`, `process-phase`) or `scripts/campaign_guard.py` refers to `$CLAUDE_CODE_SESSION_ID` or `<this session id>`, pass the session's `Conversation ID` from `<user_information>` as a literal string (`--session <conversation-id>`). The Stop hook in `.agents/hooks.json` reads `conversationId` from its payload and matches it against the guard's `session_id`.
- **In-session heartbeat (`CronCreate`, `CronList`, `CronDelete`)**: Where `process-plan` or `process-phase` names `CronCreate` (`cron: "3-59/5 * * * *"`, `recurring: true`, `durable: false`), call the `schedule` tool with `CronExpression: "3-59/5 * * * *"`, `IsDaemon: false`, `ExactTiming: false`, and `Prompt` set to the skill's heartbeat prompt with `<this session id>` and `<generation>` filled in. Use the returned task ID as `<cron_id>`. Where a skill names `CronList`, call `manage_task` with `Action: "list"`. Where a skill names `CronDelete`, call `manage_task` with `Action: "kill"` and `TaskId: <cron_id>`.
- **Review dispatch (`scripts/review-dispatch.py`)**: Always pass `--writer claude` to `python scripts/review-dispatch.py`, exactly as written in `process-todo-section`, `review-todo-section`, and `independent-review`. The `claude` route in `.conclave/reviewers.toml` (to the cross-family OpenAI Codex reviewer) is the one this repository's work is reviewed under, and `scripts/lib/todo_graph.py` checks every recorded pass against it when stamping receipts.
- **PowerShell (`pwsh`) command execution**: `run_command` runs in PowerShell (`pwsh`) on Windows, with each command in a fresh session. Use PowerShell syntax or `python` scripts; do not use bash-only redirection (`<`) or bash parameter expansion (`${VAR:-default}`) in `run_command`.
- **Subagent delegation**: Use `invoke_subagent` with `research` (or a read-only subagent defined with `EnableWriteTools: false`) for mechanical read-only exploration. Subagents read and run; they never write. The main loop makes every file change and verifies what subagents return.

## Output and formatting discipline

- Lead with the result, action, or answer. Keep status updates to one or two sentences unless the user asks for detail.
- Link every file and code symbol with `file://` links using forward slashes and a basename label.
- Markdown prose is never hard-wrapped: write one line per paragraph and one line per list item.
- Every Markdown table row must stay `<= 100` characters so raw `.md` files never wrap.
- Never use em dashes or en dashes anywhere: prose, code, comments, commit messages, or generated files. Use commas, colons, parentheses, or full stops instead.
- Every new tracked source file (`.py`, `.mjs`, `.ps1`, `.sh`, C++, CMake, or `scripts/hooks/*`) must declare `# SPDX-License-Identifier: GPL-3.0-or-later` and `# Copyright 2026 Rizonesoft` in its first 10 lines (`python scripts/check-spdx.py`).
- Never name a reviewer model identifier outside `.conclave/reviewers.toml` and `docs/reviews/`.

## Safety and quality bar

- Local reversible work in the repository needs no confirmation; act autonomously to resolve build, test, or tooling issues within the repository.
- Ask once before any irreversible external action (sending external mail, modifying production or cloud resources, or deleting untracked user data outside the repository).
- Never print, log, or commit a secret value.
- Temporary files, review prompts, and logs go to `R:\scratch` (or the session scratch directory), never inside the repository tree.
- Honour the visual design (`docs/brand/NAMES.md`, `docs/brand/icon-language.md`, `docs/brand/icon-distinctness.md`, `design/inventory/REFERENCE.md`) and the product bar (`docs/product-principles.md`).
