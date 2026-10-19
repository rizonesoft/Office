---
name: authoring-skills
description: Use when creating, moving, reviewing, or documenting project skills, skill references, Antigravity (.agents/skills), Claude (.claude/skills), or Codex (.codex/skills) skill folders, reusable skill-kit templates, or Codex command-policy rules.
---

# Authoring Skills

Follow `docs/agent-skills-and-rules-structure.md` before creating or moving skills or rules.

## Required Pattern

1. Put Antigravity-facing skill content under `.agents/skills/<skill-name>/`, Claude-facing skill content under `.claude/skills/<skill-name>/`, and Codex-facing skill content under `.codex/skills/<skill-name>/`.
2. Put required instructions in `SKILL.md`.
3. Name skills for the capability, not the project namespace. Prefer gerunds or clear noun phrases such as `authoring-skills` or `local-tool-safety`; keep project-specific scope in the description and instructions.
4. Put long checklists, conventions, and detailed docs in `references/`.
5. Put helper scripts in `scripts/` and templates/resources in `assets/`.
6. Do not put OpenAI/Codex-specific `agents/openai.yaml` inside `.agents/skills` or `.claude/skills`.
7. Keep `.agents/skills/<skill-name>/`, `.claude/skills/<skill-name>/`, and `.codex/skills/<skill-name>/` as real files and directories, never symlinks.
8. Keep `agents/openai.yaml` as a real file in `.codex/skills/<skill-name>/agents/openai.yaml` when needed.
9. Update `kits/base/templates/` (and `skills/{agy,claude,codex}/` in `Conclave-SDK`) when new projects should inherit the skill.
10. Use `.codex/rules/*.rules` for Codex Starlark command execution policies and `.agents/rules/`, `.claude/rules/`, `.codex/rules/` for agent-scoped rules.

## Validation

- Confirm `SKILL.md` exists in each target tool's skill folder (`.agents/skills`, `.claude/skills`, `.codex/skills`).
- Confirm the skill `name` frontmatter matches its directory.
- Confirm no symlinks exist between `.agents/skills`, `.claude/skills`, and `.codex/skills`.
- Confirm no provider-specific `agents/openai.yaml` leaked into `.agents/skills` or `.claude/skills`.
- Confirm the reusable kit template is updated when the behavior should apply to future projects.
- Update `AGENTS.md` or `docs` when adding behavior that future agents must follow.
