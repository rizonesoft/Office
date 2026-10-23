# AGENTS.md

This repository builds **Rizonesoft Office**, an open-source (GPL-3.0-or-later) Windows office suite in planning and design, whose six apps are to match their Microsoft counterparts feature by feature: Write (Word), Grid (Excel), Stage (PowerPoint), Flow (Visio), Plan (Project) and Mail (Outlook). The names and identifiers are recorded in `docs/brand/NAMES.md`; the plan is `todo/`; brand and icon sources are `scripts/lib/` and `design/`, with generated outputs in `assets/`. The verification commands are `python scripts/todo-graph.py validate`, `python scripts/build-icons.py --check` and `python -m unittest discover -s scripts/tests`, all run in CI (`.github/workflows/ci.yml`). Claude Code (Opus 5.5) is the only writer and the one Codex reviewer `.conclave/reviewers.toml` routes to the only reviewer (owner decisions 2026-10-23; the pin, not this file, names it); the repository takes nothing from the Conclave SDK.

## Product bar

We are building a better product than Microsoft's, not a clone (owner, 2026-10-23). Parity is the floor; every feature is optimised and improved, beats Office's measured times on the same PC, and never takes a shortcut where the harder, better version is possible. The rules a plan, a build and a review check are in [docs/product-principles.md](./docs/product-principles.md).

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
- Green dependency pull requests merge by themselves (owner decision 2026-10-21): `scripts/merge_prs.py` merges Dependabot and pins pull requests that are labelled `dependencies` or `pins`, have every check green and leave the C++ toolchain pin files (`vcpkg.json`, `vcpkg-configuration.json`, `CMakePresets.json`) alone, one at a time by rebase, at a campaign section boundary or through the `office-pr-merge` task, and never into a dirty, unpushed or mid-section clone. Local pin proposal branches (`pins/*`) still wait for the owner's merge.

## Skills

- Skills live in `.claude/skills/<name>/` as real files, never symlinks. The Antigravity and Codex mirrors were removed on 2026-10-23, when Claude Code became the only writer.
- Follow [Agent Skills and Rules Structure](./docs/agent-skills-and-rules-structure.md) before adding or moving skills.
- Name a skill for its capability, not with a project prefix.

## Subagents

- Delegate mechanical subtasks to subagents. Claude subagents pin an explicit `model:`: Sonnet by default, and Opus (with a `model_rationale:`) only where judgment quality needs it.
- Subagents read and run; they never write. Every Claude subagent declares an explicit `tools:` list without Edit, Write, MultiEdit, NotebookEdit or `*`. The main loop makes every change and verifies what subagents return.
- Haiku is only for near-mechanical work, at least 90% mechanical (read-only lookups, inventories, structural checks), whose output a script or the main loop verifies. Pin `claude-haiku-5-5` or later, declare `mechanical_share:` (90 to 100), point `haiku_replay:` at a record of a known-answer replay that showed no loss against Sonnet, and give it no edit tools. Never use Haiku for review, audit, research, security, debugging, diagnosis, planning or design.
- Run `node scripts/verify-agent-tiers.mjs` after adding or changing an agent definition; it enforces these rules.

## TODO workflow

Plan and build through the TODO system: [docs/todo-workflow.md](./docs/todo-workflow.md).

- Every clone runs `git config core.hooksPath scripts/hooks`: its pre-commit hook refuses a TODO change committed without `python scripts/todo-graph.py plan --sync`.
- Before a section is built, one completion review (`docs/completion-review-prompt.md`) checks that building it as written gives a whole feature; each gap extends the section or is filed as a new one, and `stamp` refuses a section without that record (`process-todo-section`).
- Review rounds go through `scripts/review-dispatch.py` to the one reviewer `.conclave/reviewers.toml` pins, up to 33 rounds (22 before 2026-10-23); from round 9 on, a round whose findings are all `P3` or advisory ends the loop and its findings are filed (`review-todo-section`).
- Tests: `python -m unittest discover -s scripts/tests` (agent tooling, TODO graph, run guard, automations and project scripts).
