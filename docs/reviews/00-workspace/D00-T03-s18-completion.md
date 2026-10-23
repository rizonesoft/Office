# Completion review: D00 T03 §18

## Round 1: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T12:28:29Z
- Effort: medium
- Lines: 15
- Digest: a04432e54b2b6ce2

SECTION: D00 T03 §18
PURPOSE: completion
CONTRACT: sha256:81d1537402e38dfec91ed88b4de4636fa5ad524c4a103257b5debe37d07a9c39

1. **[P2] Recovery identity across repair heads is undefined.** The section requires repairs that turn another job red to share one budget, but records attempts against `<sha>` without defining whether it is the original red head or the latest repair head. Each repair produces another SHA, so counting by the current head can restart the budget indefinitely. **Remedy: extend** with a stable recovery identifier, explicit association of repair heads with that recovery, and a reset rule that requires established green. Preserve the separate one-rerun allowance for each head while charging every rerun to the shared budget.

2. **[P2] Resume persistence lacks an ordering and interrupted-attempt rule.** Recording an attempt after its action permits a session death between a rerun or push and its record to erase the expenditure. Recording it immediately also conflicts with the existing instruction to defer run-file writes until CI and dependency merging finish. Furthermore, owner resumes create a new run file, while this section only requires reading “the run file.” **Remedy: extend** to durably reserve each numbered attempt before its action, define how an interrupted reservation is recovered without repeating a rerun or resetting the count, read the applicable prior run files, and reconcile those writes with the clean-tree requirements.

3. **[P2] Pending and unreadable results have no complete budget transition rules.** Naming `wait` and `unreadable` as consumers does not specify what happens when a bounded wait returns 3 again, status or log retrieval fails during recovery, or a rerun command cannot execute. The inherited unknown path still parks with `ci-unknown` after one retry, without the budget-exhaustion filing and notification. The section also does not distinguish a successful fourth attempt from an exhausted unsuccessful recovery. **Remedy: extend** with explicit transitions for each result, charging rules for compound operations, precedence over §15’s existing retry rules, and escalation after the fourth unsuccessful attempt. Retain `ci-unknown` for discovery failures outside an established red recovery.

4. **[P2] No checkpoint proves that the budget remains bounded.** `check-design-doc.py` checks document structure and formatting; searching for `ci-attempt` proves only that the token exists. §19 owns guard behavior and skill-presence checks, but does not explicitly require checks of shared counting, interrupted attempts, cross-file resume, or exhaustion transitions. All three gaps above could survive those checkpoints. **Remedy: extend** with falsifiable recovery scenarios covering alternating failing jobs across repair SHAs, mixed attempt kinds, interrupted and fresh-run resumes, a second rerun refusal, repeated pending or unreadable results, fourth-attempt success, and exhaustion that files, attempts notification, and parks even if notification fails. Explicitly assign these checks to §19 if it remains their verification owner.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended
3. extended
4. extended

## Round 2: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T12:30:15Z
- Effort: medium
- Lines: 9
- Digest: 9b824df5ae729ee7

SECTION: D00 T03 §18
PURPOSE: completion
CONTRACT: sha256:0703af846a63180f7298f0dd5cdea90eb4d4e1f1f6762b329478e92268e73d01

1. **[P2] Resume does not explicitly reconcile an open recovery with an already-green head.** A session can die after a repair or rerun succeeds but before `close` runs. On resume, §17 can establish green and continue through the watch's green path, while §18 only requires wiring the red path and closing on an attempt's green result. The persisted recovery can therefore remain open, causing a later independent failure to inherit its spent budget. **Remedy: extend** the start/resume procedure to inspect the open recovery and close it when reconciliation establishes a governing green head equal to or descending from its first head, before dependency merging or further work. Test interrupted success, including success on attempt four, followed by resume and a new red recovery with a fresh budget. §17 owns push reconciliation and §19 owns general gate checks; neither explicitly owns this recovery-state reconciliation.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 2)

1. filed -> D00 T03 §21
