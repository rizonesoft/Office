# Completion review: D00 T03 §20

## Round 1: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T13:24:14Z
- Effort: medium
- Lines: 13
- Digest: cf0fec5e3bb367da

SECTION: D00 T03 §20
PURPOSE: completion
CONTRACT: sha256:bc7956ab9eaa8bf6367c565c2266913014217d767be9aa544144e49b51eb6767

1. **P2, extend: Remove the remaining Git history ceiling.** `unchecked_heads()` still reads at most `HISTORY_LIMIT = 5000` commits and chooses the oldest recorded outcome as its baseline. Once that outcome falls outside the window, reconciliation exits 2 indefinitely, even with complete workflow pagination and green recent pushes. Extend this section to traverse Git history to the required baseline without a fixed total limit. Add a fixture exceeding 5,000 commits, with an unchecked head beyond the former limit, that reconciles successfully.

2. **P2, extend: Define successful pagination termination without an older run.** The required boundary is a run created before the baseline commit, but legitimate histories need not contain one: the baseline may be the workflow’s first run. First-run reconciliation can also have no baseline because no push run is green. As written, these states cannot reach the required boundary and must exit 2 permanently. Define how proven exhaustion completes discovery, preserve §17’s first-run baseline selection, and enumerate every head when no green baseline exists. Add fixtures for an earliest-run baseline, empty workflow history, and multiple pages containing no green run.

3. **P2, extend: Verify the changed reconciliation procedure.** The two mixed-state fixtures prove that `--pending` prints both heads, but cannot detect a skill that still resolves older red heads first or supersedes them before the newest head is green. The checkpoint also omits `test_skill_ci_gate.py`, whose existing paragraph pin will reject the required skill edit. Extend those gate checks with newest-first and green-before-supersession obligations, update the pin deliberately, and include that suite in the checkpoint. §19 owns the existing gate checks; this section needs to extend them for its new behavior.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended
3. extended
