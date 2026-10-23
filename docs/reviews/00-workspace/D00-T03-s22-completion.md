# Completion review: D00 T03 §22

## Round 1: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T14:02:16Z
- Effort: medium
- Lines: 15
- Digest: 5dae8713507c58b3

SECTION: D00 T03 §22
PURPOSE: completion
CONTRACT: sha256:6b4b2f667d69dd084c4a2ca9f003c70627dfbdfd5ead38a6aa219d7bbf04da3d

1. **P1 | extend: Wire continuation into the unattended campaign.** Saving progress does not make the caller continue. §17 and the current `process-plan` procedure retry exit 2 once, then park, so work requiring three or more tries still stops. Define an explicit incomplete-but-progressing result and teach campaign start, phase start and resume to continue it before claiming any row. Preserve §15's refusal rules for actual failures and §18's repair budget. Add a campaign gate fixture requiring at least three tries, and include `test_skill_ci_gate.py` in the checkpoint.

2. **P2 | extend: Define checkpoint validity when inputs change.** The state records runs and a page number without binding them to the repository, fetched head, baseline or outcome records. A push, dependency merge or repair between tries can make that checkpoint stale. GitHub exposes numbered pages, so the plan also needs to handle changes to the run list between requests. Define checkpoint identity, refresh and invalidation rules that discover new heads without repeatedly discarding useful progress. Test a new push and a new workflow run between tries, with no omitted heads or premature green result. [GitHub pagination parameters](https://docs.github.com/en/rest/actions/workflow-runs#list-workflow-runs-for-a-workflow).

3. **P2 | extend: Preserve results through final reporting and durable acknowledgement.** “Each head already settled” does not specify which results are reusable, whether pending or unknown heads are checked again, or how earlier results reach the final output and aggregate exit code. The campaign needs those results to write `ci-green` and `ci-superseded` records under §17 and §20. Define stored outcomes and supporting run identity, rechecks for unresolved heads, complete final reporting, and checkpoint deletion only when losing it cannot force the same oversized reconciliation to restart. Test an early red result followed by interruption, a pending head becoming green, and interruption before campaign records are written.

4. **P2 | extend: Define a proven stopping boundary.** “A page's runs are all older than the baseline commit” leaves the comparison undefined. Commit dates do not establish push-run order: commits can be pushed later, and unrelated branch runs share the unfiltered history. A timestamp comparison could therefore stop before discovering an unchecked main push head. Specify a boundary that proves no required head remains, or continue to the endpoint's end when that proof is unavailable. Preserve §17's first-run baseline semantics and §20's empty-history and no-green cases. Add fixtures for delayed pushes, nonmonotonic commit dates and pages containing only other branches or events.

COMPLETE: no
HIGHEST: P1
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended
3. extended
4. extended
