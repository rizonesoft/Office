# CLAUDE.md

Follow [AGENTS.md](./AGENTS.md). This file holds only what is specific to Claude Code (`claude`), the repository's only writer (owner decision 2026-10-23).

- Skills live in `.claude/skills/<name>/`, the only copy.
- Use `.claude/skills/local-tool-safety` before local tool, Windows/WSL, connector, mail, cloud, SQL, or outbound work.
- The lead is one long Opus session (AGENTS.md, Subagents): it decides, builds every section and every fix round itself (owner, 2026-11-11: the main session is the writer), runs the gates and the review loop and commits. Agents only read (owner, 2026-11-11): the Sonnet readers are the whole fleet, and no writer agent exists, Opus or Fable. A review loop that will not converge is re-thought by the lead itself (AGENTS.md, Subagents). Haiku is retired.
- Reviews go through `scripts/review-dispatch.py --writer claude` to the one reviewer `.conclave/reviewers.toml` routes to (`--check-pin` names it; the owner's 2026-11-10 decision is that it is the same one reviewer whether `claude`, `agy` or `muse` wrote the work, and that it never changes). No other file names the reviewer in use.
