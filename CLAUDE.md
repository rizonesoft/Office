# CLAUDE.md

Follow [AGENTS.md](./AGENTS.md). This file holds only what is specific to Claude Code (`claude`), the repository's only writer (owner decision 2026-10-23).

- Skills live in `.claude/skills/<name>/`, the only copy.
- Use `.claude/skills/local-tool-safety` before local tool, Windows/WSL, connector, mail, cloud, SQL, or outbound work.
- The main loop orchestrates and routes work to the cheapest tier that holds its quality bar (AGENTS.md, Subagents): scripts, then Haiku for verified lookups, Sonnet, Opus at an effort the main loop sets, a Fable worker in a fresh context, then itself. Workers write only from a work packet; the main loop reads every diff, runs the gates and commits.
- Reviews go through `scripts/review-dispatch.py --writer claude` to the one reviewer `.conclave/reviewers.toml` routes to (`--check-pin` names it; the owner's 2026-11-10 decision is that it is the same one reviewer whether `claude`, `agy` or `muse` wrote the work, and that it never changes). No other file names the reviewer in use.
