# Agent Skills and Rules Structure

Claude Code (Opus 5.5) is this repository's only writer (owner decision 2026-10-23), so skills and agent rules live in one place, `.claude/`. GPT-6.1 Sol reviews through the Codex CLI (`scripts/review-dispatch.py`), reading the prompt it is given rather than any skill. The Antigravity and Codex skill mirrors, their rules and the `GEMINI.md` and `CODEX.md` entry files were removed that day; git history keeps them.

## Skill Location

Skills live under:

```text
.claude/skills/<skill-name>/
  SKILL.md
  references/
  scripts/
  assets/
```

- `SKILL.md` is required.
- `references/` is standard Agent Skills structure for longer documentation.
- `scripts/` is for executable helpers.
- `assets/` is for templates or resources.
- Skills are real files, never symlinks.

## Naming and placement

- Name a skill for its capability, not with a project namespace prefix. Project-specific routing context belongs in the description and instructions, where it is read on demand, rather than in the name, which is paid for in the always-on catalog by every session.

## Rules

Use the word "rules" carefully:

- Durable project behavior belongs in `AGENTS.md`.
- Claude Code wiring belongs in `CLAUDE.md` and `.claude/rules/`.
- Markdown checklists or rule references belong in a skill `references/` folder or in `docs/`.

## Adding a New Skill

1. Create `.claude/skills/<skill-name>/SKILL.md` as a real file (never a symlink).
2. Keep the `name` field equal to `<skill-name>`, using lowercase letters, numbers, and hyphens only.
3. Name the skill for the capability, not the project namespace (`authoring-skills`, `local-tool-safety`, `process-todo-section`).
4. Keep `description` specific enough for automatic selection.
5. Put long checklists in `references/`.
6. Update `AGENTS.md` if the skill changes project behavior.
7. Validate the skill file, its references and its frontmatter.

## Current Skills

| Skill | Path |
| ----- | ---- |
| `local-tool-safety` | `.claude/skills/local-tool-safety/` |
| `authoring-skills` | `.claude/skills/authoring-skills/` |
