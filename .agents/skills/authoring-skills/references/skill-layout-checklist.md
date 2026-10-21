# Skill Layout Checklist

Use this checklist whenever adding or changing a skill across Antigravity (gy), Claude Code (claude), and OpenAI Codex (codex).

## Antigravity Skill (.agents/skills/)

- [ ] Skill lives in .agents/skills/<skill-name>/ as a real directory, not a symlink.
- [ ] SKILL.md exists with 
ame and description frontmatter matching <skill-name>.
- [ ] Long docs live in 
eferences/, executable helpers in scripts/, assets in ssets/.
- [ ] No gents/openai.yaml exists under .agents/skills/<skill-name>/.

## Claude Skill (.claude/skills/)

- [ ] Skill lives in .claude/skills/<skill-name>/ as a real directory, not a symlink.
- [ ] SKILL.md exists with 
ame and description frontmatter matching <skill-name>.
- [ ] Long docs live in 
eferences/, executable helpers in scripts/, assets in ssets/.
- [ ] No gents/openai.yaml exists under .claude/skills/<skill-name>/.

## Codex Skill (.codex/skills/)

- [ ] .codex/skills/<skill-name>/SKILL.md is a real file, not a symlink.
- [ ] .codex/skills/<skill-name>/references is a real directory when references exist, not a symlink.
- [ ] .codex/skills/<skill-name>/agents/openai.yaml is a real OpenAI/Codex metadata file when needed.
- [ ] Codex wording is adapted for Codex when needed.

## Rules

- [ ] Repo-wide durable instructions are in AGENTS.md.
- [ ] Agent-specific entry files (GEMINI.md, CLAUDE.md, CODEX.md) and rules (.agents/rules/, .claude/rules/, .codex/rules/) stay isolated per tool.
- [ ] Markdown reference checklists live in docs/ or skill 
eferences/.
