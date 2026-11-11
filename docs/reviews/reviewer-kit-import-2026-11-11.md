## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-11T19:25:17Z
- Candidate: 5237b1d7470b9271748939c60a2678bbc8b04639
- Effort: medium
- Lenses: adversarial, integration, source-defect, consistency, quality, optimization
- Lines: 24
- Digest: c789a1274178fe2a

### adversarial: approve

### integration: needs-attention

1. **P2, `scripts/review-dispatch.py:991`: Reopened legacy sections cannot enter the new review cycle.** `unstamp()` preserves their findings files, but existing rounds prevent a plan review, while every subsequent pass requires that plan review. Reproduction: reopen the currently stamped `D00 T03 §13`, then follow the documented review workflow using `docs/reviews/00-workspace/D00-T03-s13.md`. Read-only calls to `check_three_pass_order()` confirmed that plan, round, completion and reconciliation all refuse against that preserved file. Using another filename cannot resolve this because `plan_record()` requires the section’s canonical findings path. Add an explicit review-cycle transition that preserves the revoked evidence and permits fresh reviews.

### source-defect: approve

### consistency: needs-attention

2. **P3, `docs/todo-workflow.md:15`: The governing workflow still specifies the retired review order.** It directs callers to run completion review before implementation, whereas the imported dispatcher requires plan, round, then completion. Reproduction: follow that lifecycle for a new section; the completion dispatch refuses because no round exists. Update the lifecycle to match the new schedule.

### quality: approve

### optimization: approve

LENS adversarial: clean
LENS integration: findings
LENS source-defect: clean
LENS consistency: findings
LENS quality: clean
LENS optimization: clean
HIGHEST: P2
OVERALL: needs-attention

## Writer note: dispositions after round 1

Candidate `5c01808..5237b1d`. Both findings verified against the code and fixed in the next commit.

1. P2, a reopened section cannot enter the new review cycle: fixed in `unstamp` (`scripts/lib/todo_graph.py`). It keeps the section's own findings file as `D<NN>-T<NN>-s<N>.revoked-<date>.md` and turns a remaining `Started:` line into a `Duration:` note, so the reopened section takes a fresh plan review, round and completion review. Test: `test_unstamp_reopens_a_regressed_section_and_allows_a_restamp` in `scripts/tests/test_todo_stamp.py`, which restamps through a fresh cycle.
2. P3, `docs/todo-workflow.md` gave the retired order: fixed, the lifecycle line names plan review, build, round, completion review, stamp.

Gates: `python scripts/run-tests.py` -> 1247 tests in 31 files, 2 skipped, OK; `python scripts/todo-graph.py validate` -> `valid: 156 sections`.
