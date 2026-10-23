# Skill Layout Checklist

Use this checklist whenever adding or changing a skill. Claude Code is the only writer (owner decision 2026-10-23), so a skill has one home.

## Skill (`.claude/skills/`)

- [ ] Skill lives in `.claude/skills/<skill-name>/` as a real directory, not a symlink.
- [ ] `SKILL.md` exists with `name` and `description` frontmatter, `name` matching `<skill-name>`.
- [ ] Long docs live in `references/`, executable helpers in `scripts/`, assets in `assets/`.

## Rules

- [ ] Repo-wide durable instructions are in `AGENTS.md`.
- [ ] Claude Code wiring is in `CLAUDE.md` and `.claude/rules/`.
- [ ] Markdown reference checklists live in `docs/` or a skill's `references/`.
