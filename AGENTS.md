# AGENTS.md

This repository follows the Conclave-SDK 3-agent conventions. Adapt this file to the project: name what the project is, where the code lives, and which commands verify it.

## Working rules

- Verify files, routes, schemas, tools, and commands before relying on them. A path someone mentions is a hypothesis until it is on disk.
- Inspect existing patterns, imports, the package manager, the framework, and the test commands before editing. Do not infer architecture or tool schemas from memory when the repository can answer.
- Resolve a tool by capability before path. Prefer explicit config, then discovery, then a setup-required state. Store discovered paths only in ignored local config and never hardcode user-specific absolute paths.
- Prefer global or user-level tool installs. Add repo-scoped wrappers only when they encode project-specific behavior or reproducible commands.
- Real data only. Demo or seed data stays behind an explicit demo mode and is labeled as such.
- Run the relevant typecheck, lint, and tests after a change.
- Fix at the owning layer: a setting in its setting, behaviour in the code that produces it, data in the data. No output filters that hide a problem. Code changes end the report with a `Layer:` line.
- Markdown prose is never hard-wrapped: one line per paragraph and per list item. Every Markdown table row stays `<= 100` characters so raw `.md` files never wrap.
- Never use em dashes or en dashes anywhere: prose, code, comments, commit messages and generated files.
- Temporary files and full logs go to scratch, never the repository: `R:\scratch` on Windows, `/mnt/r/scratch` on WSL (the same folder), or the session scratchpad when one is given.

## Safety

- Local reversible work in the repository needs no confirmation.
- Ask the operator once before anything that sends, deletes, or changes something outside the repository: mail, production systems, cloud changes, SQL writes, dropping data, credentials.
- When a command needs sudo, give the operator the exact command to run with `! sudo ...`. Never store the sudo password.
- Never print, log, or commit a secret value.

## Skills

- Antigravity skills live in `.agents/skills/<name>/`, Claude skills in `.claude/skills/<name>/`, and Codex skills in `.codex/skills/<name>/`, all as real files, never symlinks. Change all three together.
- Follow [Agent Skills and Rules Structure](./docs/agent-skills-and-rules-structure.md) before adding or moving skills.
- Name a skill for its capability, not with a project prefix.
- Each agent reads and runs only its own directory (`.agents/` for Antigravity, `.claude/` for Claude Code, `.codex/` for Codex) and never edits another agent's skills unless asked.

## Subagents

- Delegate mechanical subtasks to subagents. Claude subagents pin an explicit `model:`: Sonnet by default, and Opus (with a `model_rationale:`) only where judgment quality needs it.
- Subagents read and run; they never write. Every Claude subagent declares an explicit `tools:` list without Edit, Write, MultiEdit, NotebookEdit or `*`. The main loop makes every change and verifies what subagents return.
- Haiku is only for near-mechanical work, at least 90% mechanical (read-only lookups, inventories, structural checks), whose output a script or the main loop verifies. Pin `claude-haiku-5-5` or later, declare `mechanical_share:` (90 to 100), point `haiku_replay:` at a record of a known-answer replay that showed no loss against Sonnet, and give it no edit tools. Never use Haiku for review, audit, research, security, debugging, diagnosis, planning or design.
- Run `node scripts/verify-agent-tiers.mjs` after adding or changing an agent definition; it enforces these rules.

## TODO workflow

Plan and build through the TODO system: [docs/todo-workflow.md](./docs/todo-workflow.md).
