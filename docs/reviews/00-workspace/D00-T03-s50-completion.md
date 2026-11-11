# Completion review: D00 T03 §50

## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-11T06:26:20Z
- Effort: medium
- Type: adversarial
- Lines: 13
- Digest: 5139fcbc3780a35c

SECTION: D00 T03 §50
PURPOSE: completion
CONTRACT: sha256:3f97d1a2c09978044dffa94d5c570b00f4d772113e86647110483cfd39846ff8

1. **P1: The five withdrawals leave live dependants invalid.** `todo/00-workspace/TODO-05-lessons-and-agent-ledger.md:42` and `:43` explicitly make §5 and §6 depend on T03 §34; §7 depends on §6 at `:44`. Contrary to the supplied context, withdrawing exactly the five named sections makes the proposed dependant refusal reject the repository. Removing command mentions does not resolve these dependencies or their promised functionality. **Remedy: extend** this section to decide and record whether these consumers are withdrawn or redesigned, reconcile their dependencies and checkpoints, and adjust the expected withdrawal count accordingly.

2. **P2: Closing a file containing withdrawals has no working stamp transition.** `scripts/lib/todo_graph.py:1205` marks a file done only when every sibling is stamped. After the proposed validator change, stamping the last open section beside a withdrawn sibling leaves the file active; validation at `:1213` rejects it and rolls back the stamp. The section owns validator acceptance of a manually prepared done file but does not own this normal transition. **Remedy: extend** the stamp writer to count withdrawn siblings as finished, with a regression test that stamps the final open section, verifies done status and reads the graph back successfully.

3. **P2: The JSON plan still reports withdrawn sections as blocked.** `scripts/todo-graph.py:43` implements `plan_status()` independently of Markdown rendering. An active-file withdrawal with the proposed disposition 3 falls through to `"blocked"` at `:49`; `query plan` publishes that status at `:146`. The section’s Markdown and resolve tests would pass while this documented plan entry point misrepresents retired work. **Remedy: extend** the JSON plan contract with a withdrawn status and test it for withdrawals in both active and done files.

COMPLETE: no
HIGHEST: P1
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended
3. extended
