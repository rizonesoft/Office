---
name: authoring-skills
description: Use when creating, moving, reviewing, or documenting project skills, skill references, or agent rules in .claude/skills and .claude/rules.
---

# Authoring Skills

Follow `docs/agent-skills-and-rules-structure.md` before creating or moving skills or rules. Claude Code is the only writer (owner decision 2026-10-23), so every skill lives once, in `.claude/skills/`.

## Required Pattern

1. Put skill content under `.claude/skills/<skill-name>/`.
2. Put required instructions in `SKILL.md`.
3. Name skills for the capability, not the project namespace. Prefer gerunds or clear noun phrases such as `authoring-skills` or `local-tool-safety`; keep project-specific scope in the description and instructions.
4. Put long checklists, conventions, and detailed docs in `references/`.
5. Put helper scripts in `scripts/` and templates/resources in `assets/`.
6. Keep `.claude/skills/<skill-name>/` as real files and directories, never symlinks.
7. Put agent-scoped rules in `.claude/rules/`.

## Validation

- Confirm `SKILL.md` exists in `.claude/skills/<skill-name>/`.
- Confirm the skill `name` frontmatter matches its directory.
- Confirm no symlinks exist under `.claude/skills/`.
- Update `AGENTS.md` or `docs` when adding behavior that future agents must follow.
