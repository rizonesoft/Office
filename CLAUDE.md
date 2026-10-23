# CLAUDE.md

Follow [AGENTS.md](./AGENTS.md). This file holds only what is specific to Claude Code (`claude`), the repository's only writer (owner decision 2026-10-23).

- Skills live in `.claude/skills/<name>/`, the only copy.
- Use `.claude/skills/local-tool-safety` before local tool, Windows/WSL, connector, mail, cloud, SQL, or outbound work.
- Subagents: Sonnet by default, Opus only where judgment quality needs it, Haiku only for near-mechanical work under the AGENTS.md rule. The main loop reviews what they return.
- Reviews go to GPT-6.1 Sol through `scripts/review-dispatch.py --writer claude`, the one route `.conclave/reviewers.toml` pins.
