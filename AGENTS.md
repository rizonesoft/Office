# AGENTS.md

This repository builds **Rizonesoft Office**, an open-source (GPL-3.0-or-later) Windows office suite in planning and design, whose six apps are to match their Microsoft counterparts feature by feature: Write (Word), Grid (Excel), Stage (PowerPoint), Flow (Visio), Plan (Project) and Mail (Outlook). The names and identifiers are recorded in `docs/brand/NAMES.md`; the plan is `todo/`; brand and icon sources are `scripts/lib/` and `design/`, with generated outputs in `assets/`. The verification commands are `python scripts/todo-graph.py validate`, `python scripts/build-icons.py --check` and `python scripts/run-tests.py` (the test files of `scripts/tests` side by side; `python -m unittest discover -s scripts/tests` runs the same tests serially), all run in CI (`.github/workflows/ci.yml`). Claude Code (the latest Fable as the orchestrator, started by alias in `scripts/start-campaign.ps1`, with the Claude workers it delegates to) is the only writer and the one Codex reviewer `.conclave/reviewers.toml` routes to the only reviewer (owner decisions 2026-10-23; the pin, not this file, names it); the repository takes nothing from the Conclave SDK.

## Product bar

We are building a better product than Microsoft's, not a clone (owner, 2026-10-23). Parity is the floor; every feature is optimised and improved, beats Office's measured times on the same PC, and never takes a shortcut where the harder, better version is possible. The rules a plan, a build and a review check are in [docs/product-principles.md](./docs/product-principles.md).

## Autonomy

Act as the owner would, and better (owner, 2026-11-10; [docs/product-principles.md](./docs/product-principles.md)): decide what can be worked out and record it, improve the plan, skills, agents, runners, tools and methods as part of the product, repair the run's own failures at their owning layer with a test, and never plan less because something is hard or no competitor does it. Ask only for what the owner alone holds: a credential, a legal signature, money, or something that cannot be undone.

## Working rules

- Verify files, routes, schemas, tools, and commands before relying on them. A path someone mentions is a hypothesis until it is on disk.
- Inspect existing patterns, imports, the package manager, the framework, and the test commands before editing. Do not infer architecture or tool schemas from memory when the repository can answer.
- Resolve a tool by capability before path. Prefer explicit config, then discovery, then a setup-required state. Store discovered paths only in ignored local config and never hardcode user-specific absolute paths.
- Build tools are repo scoped and portable (owner, 2026-11-10): CMake, Ninja, sccache, vcpkg and the LLVM tools are fetched at pinned versions and hashes into an ignored folder inside the clone by the bootstrap the build foundation creates (D03 T01 §17), and used from there, never from a machine install or `PATH`. Visual Studio's MSVC toolset and the Windows SDK cannot be carried and stay host prerequisites. Other tools (Python, Git, `gh`, the agent CLIs) are user-level installs; add repo-scoped wrappers where they encode project-specific behavior or reproducible commands.
- Real data only. Demo or seed data stays behind an explicit demo mode and is labeled as such.
- Develop straight on `main` (owner, 2026-11-10): no feature branches and no pull requests for our own work; commit to `main` and push. The only branches are the ones tooling makes (`pins/*` proposals, Dependabot, short-lived CI proof branches).
- Run the relevant typecheck, lint, and tests after a change.
- Fix at the owning layer: a setting in its setting, behaviour in the code that produces it, data in the data. No output filters that hide a problem. Code changes end the report with a `Layer:` line.
- Markdown prose is never hard-wrapped: one line per paragraph and per list item. Every Markdown table row stays `<= 100` characters so raw `.md` files never wrap.
- Never use em dashes or en dashes anywhere: prose, code, comments, commit messages and generated files.
- Temporary files and full logs go to scratch, never the repository: the folder the `OFFICE_SCRATCH` environment variable names (on the owner's PC `R:\scratch`, which WSL sees as `/mnt/r/scratch`), or the session scratchpad when one is given. Code never writes a machine's path: a tool finds the repository from its own location, scratch through `OFFICE_SCRATCH` (falling back to the system temporary folder), and a program through `PATH`, `vswhere` or an environment variable; `scripts/tests/test_no_hardcoded_paths.py` fails on a drive, home or mount path in a tool. A `R:\scratch\...` path in a TODO section means that scratch folder, and the code built from it resolves it.

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

- The main loop is the orchestrator (owner, 2026-11-10): it decides, plans, writes each work packet, reads every diff and judges; it spends its own tokens on thinking, not on typing or on reading what a script can check. Work goes to the cheapest tier that can do it at the main loop's own quality bar, which never drops:
  1. A script, for anything with one right answer (validate, sync, stamp, scaffolding, path checks, generated blocks). Mechanical work done twice by a model becomes a script.
  2. Haiku, for read-only lookups a script or the main loop verifies (the Haiku rule below).
  3. Sonnet: the readers below, and `implementer` for a change whose design is settled and whose failing test or proving command is given.
  4. Opus: `senior-implementer`, for code that takes real thought with the approach given, or a packet `implementer` reported blocked. The main loop sets the `effort` of each call. Low is the preferred effort on Opus and Fable (owner, 2026-11-10: encouraged, not forced): start from low and choose medium only where the packet gives a reason, such as correctness that is subtle or several files that must stay consistent.
  - Effort ceilings (owner, 2026-11-10): a Sonnet or Haiku agent never runs above `high`, an Opus or Fable agent never above `medium`, whether the effort comes from the definition's `effort:` field or from the call. A packet that an Opus worker cannot finish at medium goes one tier up; it is never retried at a higher effort.
  5. Fable at low effort: `principal-implementer`, rarely, for a packet `senior-implementer` reported blocked or code the main loop judges Opus will not finish, with every decision already made in the packet. It is cheaper than the main loop doing that work, because it starts from a small fresh context and its exploration never enters the main loop's.
  6. The main loop itself: architecture and plan decisions, ambiguous debugging, the triage of review findings, anything outward or irreversible, any packet that needs a decision, and any packet `principal-implementer` reported blocked.
- Escalation is one tier up, on evidence, never in a loop: a proving command that still fails after the worker's second attempt, a `BLOCKED:` reply, a diff that leaves the packet's paths, or the same review finding returning. The next tier gets the evidence (the failing output, the diff), not the earlier worker's explanation.
- A work packet names the paths that may change, the done-when, the proving command (with the test that must fail first, where there is one), what is out of scope and the scratch folder. One worker writes in the tree at a time, into a clean tree (the main loop commits its own pending edits first); readers may run beside it.
- What keeps the quality: the main loop reads the whole change of every worker before committing it (`git status --porcelain --untracked-files=all`, then `git diff HEAD`, which shows staged changes too, and every new file in full), commits only the packet's paths, and on a change outside those paths sets the whole tree aside with a named `git stash push --include-untracked` and sends the packet one tier up. It never restores or deletes to reject a packet, because a changed path may be the owner's own edit, and it never drops a stash. It also runs the proving command and the gates itself, has `mutation-tester` prove a worker's new tests can fail, and commits. Workers never stage, commit, push, stamp, review or touch `todo/`. The independent review is unchanged.
- Claude subagents pin an explicit `model:`: Sonnet by default, and Opus (with a `model_rationale:`) only where the work needs it.
- An agent reads and runs unless it is a declared worker. Every Claude subagent declares an explicit `tools:` list, never `*`; Edit, Write, MultiEdit and NotebookEdit are allowed only with `write_scope: packet` in the frontmatter, and never on Haiku. No agent declares `memory:`, because Claude Code then enables Write and Edit whatever the `tools:` list says.
- Haiku is only for near-mechanical work, at least 90% mechanical (read-only lookups, inventories, structural checks), whose output a script or the main loop verifies. Pin `claude-haiku-5-5` or later, declare `mechanical_share:` (90 to 100), point `haiku_replay:` at a record of a known-answer replay that showed no loss against Sonnet, and give it no edit tools. Never use Haiku for review, audit, research, security, debugging, diagnosis, planning or design.
- An agent that gets its job wrong is removed, not kept and watched (owner, 2026-11-10: quality matters more than delegation). When the main loop's own check shows an agent returned a wrong fact, a wrong result or a claim it did not verify, delete its definition from `.claude/agents/`, its entry in the fleet list below and its lines in the Delegation sections of the skills, in one commit that says what it got wrong, and do that work in the main loop from then on. An agent that only failed to run (a timeout, an empty reply) is not removed for that.
- Run `node scripts/verify-agent-tiers.mjs` after adding, changing or removing an agent definition; it enforces these rules.
- The fleet is `.claude/agents/`: `code-explorer` (locate and map code), `git-runner` (history and diffs), `test-runner` (suites and gates, full log to scratch), `mutation-tester` (prove a test can fail), `debug-evidence` (facts about a failure), `source-researcher` (primary-source facts with URLs), and the three workers `implementer` (Sonnet), `senior-implementer` (Opus) and `principal-implementer` (Fable at low effort). Which step hands what to whom, and what the main loop still checks itself, is the Delegation section of `process-todo-section` and of `review-todo-section`.

## Code intelligence

- Claude Code loads two language servers through the plugins enabled in `.claude/settings.json`: `pyright-lsp` for the Python tooling (configured by `pyrightconfig.json`, on which `pyright` reports 0 errors today) and `clangd-lsp` for C++. Use the `LSP` tool for definitions, references and call hierarchies before text search, and read the diagnostics it reports after an edit.
- Each needs its server on `PATH`, installed per user and never into the repository: `uv tool install "pyright[nodejs]"` gives `pyright-langserver`, and `clangd` is, until the tool bootstrap exists (D03 T01 §17), the one in Visual Studio's LLVM component (`VC\Tools\Llvm\x64\bin` under the installation `vswhere` reports); from then on it is the bootstrapped one. A clone installs the plugins once with `claude plugin install pyright-lsp@claude-plugins-official --scope project` and the same for `clangd-lsp`.

## TODO workflow

Plan and build through the TODO system: [docs/todo-workflow.md](./docs/todo-workflow.md).

- Every clone runs `git config core.hooksPath scripts/hooks`: its pre-commit hook refuses a TODO change committed without `python scripts/todo-graph.py plan --sync`.
- Before a section is built, one completion review (`docs/completion-review-prompt.md`) checks that building it as written gives a whole feature; each gap extends the section or is filed as a new one, and `stamp` refuses a section without that record (`process-todo-section`).
- Review rounds go through `scripts/review-dispatch.py` to the one reviewer `.conclave/reviewers.toml` pins, up to 33 rounds (22 before 2026-10-23); from round 9 on, a round whose findings are all `P3` or advisory ends the loop and its findings are filed (`review-todo-section`).
- Tests: `python scripts/run-tests.py`, or one file with `python -m unittest discover -s scripts/tests -p "test_<name>.py"` (agent tooling, TODO graph, run guard, automations and project scripts).
