# Completion review: D00 T03 §21

## Round 1: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T13:43:56Z
- Effort: medium
- Lines: 11
- Digest: 660942a6a51d9ae6

SECTION: D00 T03 §21
PURPOSE: completion
CONTRACT: sha256:2b04c50956db1babfc38dd6961e2692a51d086fbc4027121284622fd3d3eb5a0

1. **P2, extend: settlement misses reconciliation that returns red with a green newest head.** `--pending` returns 1 when any listed head is red, even when `origin/main` is green. §20 owns superseding those earlier red heads, but does not close the recovery. Requiring settlement only after `--pending` reports green leaves this normal interrupted-repair path open, carrying its spent budget into the next failure. Run `settle` whenever reconciliation establishes the fetched newest head as green, including the supersession branch and a pending head that becomes green after waiting, before any merge or row. Require regression coverage for these paths.

2. **P2, extend: the checkpoint does not protect the campaign wiring.** `test_ci_recovery.py` can pass with settlement absent from either skill or placed after the merge. Meanwhile, the required skill edits affect paragraphs pinned by `test_skill_ci_gate.py`, whose updates are unowned here. Extend the section to add settlement obligations and weakening fixtures for both skills, deliberately update affected pins while preserving existing obligations, and include `test_skill_ci_gate.py` in the checkpoint. Tests must fail when settlement is removed or moved past the merge or row.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended

## Round 2: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T13:45:02Z
- Effort: medium
- Lines: 9
- Digest: e0b6505aa9e11e47

SECTION: D00 T03 §21
PURPOSE: completion
CONTRACT: sha256:2c6e5a2517f5c942f2f05b0be993144d18fefbce34b91b32022a7ee126fa47c6

No gaps found. The revised section covers all three green reconciliation paths before any merge or row, interrupted fourth-attempt success, a fresh recovery budget, and tests that reject weakened campaign wiring. Persistence and refusal behavior remain owned by §18; reconciliation and history limits by §17, §20 and §22.

COMPLETE: yes
HIGHEST: none
OVERALL: approve
