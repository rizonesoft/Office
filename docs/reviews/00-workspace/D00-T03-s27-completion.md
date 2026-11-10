# Completion review: D00 T03 §27

## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-10T16:46:32Z
- Effort: medium
- Type: adversarial
- Lines: 17
- Digest: 9215788cd0e8e088

SECTION: D00 T03 §27
PURPOSE: completion
CONTRACT: sha256:fddec948f97bf239fd1d6b08447840d9678387139ca4842ee0c0f6f2746e5cf2

1. **P2: Reversed ranges are not refused.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:798` equates reversing arguments with an empty diff. Git produces a nonempty reverse patch: read-only checks of `HEAD~1 HEAD` and `HEAD HEAD~1` both returned changes, with additions and deletions swapped. The planned check therefore accepts precisely the wrong-direction review the feature promises to prevent. **Remedy: extend** with commit ancestry validation, rejecting reversed and divergent ranges, and tests using distinct commits with different trees.

2. **P2: Path filtering can silently turn a whole-range review into a partial review.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:799` permits replacing an oversized diff with selected paths, but requires neither disclosure of omitted files nor ownership of their subsequent review. A range changing implementation and tests can produce a prompt containing only tests while still naming the entire commit range. The reviewer cannot reconstruct the omitted changes using Git. **Remedy: extend** with explicit scope and omitted-path information in the prompt, plus skill instructions requiring coverage of every remaining changed path before treating the candidate as reviewed. Test a range containing both included and excluded files.

3. **P2: The filtered diff has no enforced size limit.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:799` says to write the filtered diff whenever `--path` is supplied. Selecting one large file, or the repository root, can still exceed 400,000 bytes and defeat the bound. The specified passing filtered test does not exercise this state. **Remedy: extend** with a second size check on the actual selected diff, refusing an oversized result without replacing the output. Test both below-limit and above-limit filtered results.

4. **P2: Required completion context becomes optional without a completeness rule.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:796` supplies the section and Implementation Order table but makes other context optional. For a section citing SPEC chapters and inventory records, omitting `--context` leaves no specified source for the excerpts required by `docs/completion-review-prompt.md:18`, or the neighbouring-section context at line 19. Replacing the existing skill instruction at `.claude/skills/process-todo-section/SKILL.md:106` removes its explicit requirement to inline those excerpts. **Remedy: extend** with automatic context assembly or required supplied context when those sources apply, and an explicit not-applicable case for tooling sections. Test a section with real citations and refusal when its required context is absent.

5. **P2: Template additions can leave unresolved instructions without triggering refusal.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:798` detects a missing expected placeholder, but not an additional unknown placeholder. Adding a new required field while retaining existing fields passes that rule; the round acceptance test at line 797 only checks SHAs, diff and section. **Remedy: extend** with validation of the complete template placeholder set for both commands before substitution. Reject unknown placeholders and test additions as well as removals, while preserving legitimate angle-bracket text inside inserted sections and diffs.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended
3. extended
4. extended
5. extended

## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-10T16:48:44Z
- Effort: medium
- Type: adversarial
- Lines: 15
- Digest: 0c2b7bfacc1d4ed3

SECTION: D00 T03 §27
PURPOSE: completion
CONTRACT: sha256:d53a4ee98b937c5c0ce9532f27c256f32aebe0edf62cc5fbf31dfda77c0c354d

1. **P2: Empty diffs still pass.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:799` requires distinct commits and forward ancestry, but neither guarantees changes: a commit followed by its revert yields identical endpoint trees. A mistyped `--path` also produces an empty selected diff. Both can produce a successful prompt containing nothing to review. **Remedy: extend** with explicit refusal of empty whole-range and selected diffs, exit 2 without replacing the output, and tests for both scenarios.

2. **P2: Split prompts have no defined integration with recorded rounds.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:804` treats multiple dispatches as parts of one round, but `scripts/review-dispatch.py:465` records each dispatch as a separate round. Existing stopping rules count those records, and `scripts/lib/todo_graph.py:364` requires the last recorded review to be clean or stopped. Consequently, nine parts of the first candidate can reach the low-severity stopping threshold intended for repeated reviews. The plan also leaves aggregation of conflicting part verdicts undefined. **Remedy: extend** with an explicit mapping between parts, records and stopping rules, requiring every part to cover the same resolved candidate and preserving every unresolved finding. Test a failing first part followed by a clean final part, an unavailable part, and enough parts to cross the stopping threshold.

3. **P2: A single oversized file has no completion path.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:801` refuses any selected diff over 400,000 bytes and directs the caller to `--path`. If one changed file alone exceeds that limit, every selection containing it is refused, so the coverage requirement at line 804 can never finish. **Remedy: extend** with a bounded, lossless way to partition an individual file’s patch, retaining file identity and coverage, or another explicitly owned review route. Test one file exceeding the limit and prove all its changes reach review.

4. **P2: Required context can still be empty.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:797` checks whether `--context` was supplied, but does not require its file to contain any text. An empty or whitespace-only scratch file therefore satisfies the prescribed checks for a surface section while supplying none of its required excerpts. **Remedy: extend** with refusal of empty context and tests proving that rejection preserves the existing output. Keep the caller’s responsibility to supply the cited excerpts explicit.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 2)

1. filed -> D00 T03 §29
2. filed -> D00 T03 §30
3. filed -> D00 T03 §30
4. filed -> D00 T03 §29
