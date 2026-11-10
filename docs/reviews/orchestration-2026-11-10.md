## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-10T18:40:17Z
- Effort: medium
- Type: adversarial
- Lines: 38
- Digest: 98ed225791eed4c6

## adversarial: needs-attention

1. **[P1] Persistent memory bypasses the edit-tool restriction.** `scripts/verify-agent-tiers.mjs:557` checks only `tools`; `scripts/verify-agent-tiers.mjs:604` rejects Haiku only when `write_scope` is present. This frontmatter passes both checks:

   ```yaml
   ---
   name: lookup
   description: List file names
   model: claude-haiku-5-5
   tools: Read, Grep
   memory: project
   mechanical_share: 100
   haiku_replay: AGENTS.md
   ---
   ```

   I reproduced `parseError: null`, `toolProblems: []` and `haikuProblems: []` using the exported functions. `AGENTS.md` supplies an existing file for the replay-path check; substituting a genuine replay record preserves the bypass. With auto memory enabled, Claude automatically adds Write and Edit. The same bypass works for an undeclared Sonnet reader. Preconditions are ordinary agent configuration and enabled memory, not machine compromise. Validate implicit tool grants from `memory` as well as explicit grants. [Claude subagent memory documentation](https://code.claude.com/docs/en/sub-agents#enable-persistent-memory)

## consistency: needs-attention

2. **[P3] The phase workflow still carries the old writing rule.** `.claude/skills/process-phase/SKILL.md:37` says subagents read and run, the main loop writes, and every correction and repair belongs to the main loop. Loading this skill during the normal campaign contradicts the newly introduced worker routing.

3. **[P3] Failure routing contradicts the new escalation rule.** `.claude/skills/process-todo-section/SKILL.md:71` tells the main loop to take over whenever an agent fails. Line 58 instead escalates a worker’s second failed attempt one tier. A Sonnet worker returning unsuccessful evidence therefore triggers conflicting instructions: invoke the senior implementer or bypass it. Restrict the old fallback rule to readers or reconcile it explicitly.

## integration: needs-attention

Finding 1 is a verifier/runtime contract mismatch: the verifier approves a reader definition whose effective runtime tools include editing.

## source-defect: approve

No additional finding against scope decisions 27 and 28.

## record: advisory

The repository verifier and four launcher tests passed. I exercised permission checks in memory without modifying files. The filesystem-writing verifier test suite and live campaign launch were not run; runtime memory behavior is supported by the upstream documentation, not a live agent invocation.

HIGHEST: P1
OVERALL: needs-attention

## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-10T18:44:26Z
- Effort: medium
- Type: adversarial
- Lines: 28
- Digest: 142fccd041e4c13f

## adversarial: approve

No bypass found in the exercised cases: undeclared editing, wildcard grants, missing tools, persistent memory, Haiku workers, duplicate fields and quoted keys.

## consistency: needs-attention

1. **[P3] Worker briefs still prohibit requesting a fix.** `.claude/skills/process-todo-section/SKILL.md:70` requires a brief to ask for observations, “never for a verdict or a fix.” During an ordinary implementation handoff, this contradicts line 58’s instruction to give workers implementation packets. Restrict the observations-only rule to readers.

## integration: needs-attention

2. **[P2] The worker acceptance procedure uses the working-tree diff as the worker’s diff.** `.claude/skills/process-todo-section/SKILL.md:58` instructs the orchestrator to read the whole `git diff` and discard a diff containing paths outside the packet. That command excludes untracked files and includes pre-existing tracked edits.

   Two normal scenarios break this procedure:
   - A worker creates a new source file or test. Its contents never appear in the prescribed review command, defeating the requirement to review every worker change.
   - The orchestrator ticks a completed checklist item as line 129 requires, then delegates the next source-only packet. The pending `todo/` edit appears outside that packet, so the procedure rejects valid work and directs discarding changes the worker did not make.

   Record the pre-packet state, review new files explicitly, and distinguish worker changes from existing edits before rejecting or reverting anything.

## source-defect: approve

No additional finding against scope decisions 27 and 28.

## record: advisory

The repository verifier and all four launcher tests passed. Permission probes ran in memory. The filesystem-writing verifier suite and a live campaign launch were not run under this read-only review. No files were modified.

HIGHEST: P2
OVERALL: needs-attention
