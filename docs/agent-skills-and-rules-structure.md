# Agent Skills and Rules Structure

This repo keeps skill content honest by separating tool-specific skill files from shared operating intent across Google Antigravity (`agy`), Claude Code (`claude`), and OpenAI Codex (`codex`).

## Tool-Specific Skill Locations

Antigravity-facing skills live under:

```text
.agents/skills/<skill-name>/
  SKILL.md
  references/
  scripts/
  assets/
```

Claude-facing skills live under:

```text
.claude/skills/<skill-name>/
  SKILL.md
  references/
  scripts/
  assets/
```

Codex-facing skills live under:

```text
.codex/skills/<skill-name>/
  SKILL.md
  references/
  agents/openai.yaml
```

- `SKILL.md` is required in every tool folder.
- `references/` is standard Agent Skills structure for longer documentation.
- `scripts/` is for executable helpers.
- `assets/` is for templates or resources.
- `agents/openai.yaml` is OpenAI/Codex-specific metadata. It belongs only in `.codex/skills/<skill-name>/`, never in `.agents/skills` or `.claude/skills`.
- Do not use symlinks between `.agents`, `.claude`, and `.codex`. The files may start as aligned copies, but each model/tool is free to diverge in wording, metadata, and operational detail.

## Naming and placement

- Name a skill for its capability, not with a project namespace prefix. Project-specific routing context belongs in the description and instructions, where it is read on demand, rather than in the name, which is paid for in the always-on catalog by every session.
- Antigravity skills live under `.agents/skills/`, Claude skills under `.claude/skills/`, Codex skills under `.codex/skills/` as real files rather than symlinks, and Codex-specific `agents/openai.yaml` metadata only in `.codex/skills/`.

## Rules

Use the word "rules" carefully:

- Durable project behavior belongs in `AGENTS.md`.
- Agent-specific entry files (`GEMINI.md`, `CLAUDE.md`, `CODEX.md`) and rules (`.agents/rules/`, `.claude/rules/`, `.codex/rules/`) hold tool-specific wiring.
- Markdown checklists or rule references belong in a skill `references/` folder or in `docs/`.
- Codex command execution policy files belong in `.codex/rules/*.rules` when using the Codex Starlark `.rules` format.

## Adding a New Skill

1. Create `.agents/skills/<skill-name>/SKILL.md`, `.claude/skills/<skill-name>/SKILL.md`, and `.codex/skills/<skill-name>/SKILL.md` as real files (never symlinks).
2. Keep the `name` field equal to `<skill-name>`, using lowercase letters, numbers, and hyphens only.
3. Name the skill for the capability, not the project namespace (`authoring-skills`, `local-tool-safety`, `process-todo-section`).
4. Keep `description` specific enough for automatic selection.
5. Put long checklists in `references/`.
6. Put OpenAI/Codex metadata in `.codex/skills/<skill-name>/agents/openai.yaml`.
7. Update `AGENTS.md` if the skill changes project behavior.
8. Validate all skill files, references, and metadata.

## Current Shared Skills

| Skill | Agent paths (`<agent>` in `.agents`, `.claude`, `.codex`) |
| ----- | --------------------------------------------------------- |
| `local-tool-safety` | `<agent>/skills/local-tool-safety/` |
| `authoring-skills` | `<agent>/skills/authoring-skills/` |
