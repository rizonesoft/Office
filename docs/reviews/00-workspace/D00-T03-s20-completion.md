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

## Round 2: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T13:26:06Z
- Effort: medium
- Lines: 11
- Digest: 7928f29edf5afc37

SECTION: D00 T03 §20
PURPOSE: completion
CONTRACT: sha256:1f8ebe76bdb80d1375e9c1b6725d62bc366dff33990810e5fc7cff1493eac923

1. **P2, extend: the prescribed API query still has a history ceiling.** GitHub limits workflow-run searches using `branch` or `event` to 1,000 results, even with pagination. The specified command therefore replaces the 500-run ceiling with a 1,000-run ceiling. Count validation can detect truncation, but retrying the same query still parks permanently. [GitHub documents this limit](https://docs.github.com/en/rest/actions/workflow-runs#list-workflow-runs-for-a-workflow). Require an enumeration strategy that avoids the filtered-search ceiling, such as paging the unfiltered workflow endpoint and selecting branch/event locally. Add a fixture exceeding 1,000 matching runs that reproduces the server cap and proves complete discovery.

2. **P2, extend: growing history can still exhaust fixed deadlines without making progress.** The existing `push_runs` call receives at most 60 seconds for the entire paginated subprocess, while `--pending` shares a 600-second deadline across discovery and every head’s status lookup. A sufficiently long history or unchecked backlog can repeatedly exhaust these limits, and neither retry preserves progress. Removing count ceilings alone therefore does not deliver reconciliation across any history length. Require bounded individual requests plus resumable progress, or another strategy that completes large reconciliations without repeatedly restarting the same work. Add simulated-clock fixtures where pagination exceeds 60 seconds and head settlement exceeds 600 seconds, proving eventual completion while individual calls remain bounded. §15 owns retry and park behavior, but does not own progress across these scale limits.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 2)

1. filed -> D00 T03 §22
2. filed -> D00 T03 §22
