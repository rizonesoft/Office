# CODEX.md

Follow [AGENTS.md](./AGENTS.md). This file holds only what is specific to OpenAI Codex (`codex`).

- Skills live in `.codex/skills/<name>/` (with `agents/openai.yaml` metadata) and are mirrored as real files in `.agents/skills/<name>/` and `.claude/skills/<name>/`. Change all three together.
- Use `.codex/skills/local-tool-safety` before local tool, Windows/WSL, connector, mail, cloud, SQL, or outbound work.
- Rules live in `.codex/rules/`.
