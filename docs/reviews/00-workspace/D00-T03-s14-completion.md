# Completion review: D00 T03 §14

## Round 1: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T09:34:56Z
- Effort: medium
- Lines: 12
- Digest: bc3098b708aba839

SECTION: D00 T03 §14
PURPOSE: completion

1. **[P2] Bind the digest to the dispatched input.** The plan places `Contract:` in the outcome, which is written after the review and potentially after section extensions. It never requires capturing the digest before dispatch or checking it against the section inlined into the prompt. If the section changes while the reviewer runs, recording its current digest afterward can bind approval to text the reviewer never saw. Remedy: **extend** with a digest captured from the dispatched contract, preserved for that round, and compared with the current contract before building and stamping. Test an edit between dispatch and outcome recording.

2. **[P2] Make an interrupted re-check recoverable after an outage.** Requiring a returned round N+1 conflicts with the existing next-phase retry: the dispatcher records an outage as round N+1, so the successful retry becomes N+2. The literal requirement would permanently refuse that recovered section, while the skill also prohibits a third dispatch. Remedy: **extend** to distinguish review attempts from returned completion passes, preserve the pending re-check across outages, and allow the single authorised retry to satisfy it. Test extension, recorded outage, next-phase successful retry and successful stamp.

3. **[P2] Define recovery when no committed record exists.** The skill creates the completion record before its first dispatch but commits it only after completion and dispositions. Consequently, a first-session refusal or unreadable record may have no “last commit” to restore. Restoration can also discard valid uncommitted rounds and outcomes, losing the evidence needed to resume without spending a pass twice. Remedy: **extend** with explicit recovery for new and partially completed records, preserving valid returned evidence and pending re-check state. Test refusal before the first record commit and recovery after an uncommitted returned round.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended
3. extended

## Round 2: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T09:36:32Z
- Effort: medium
- Lines: 8
- Digest: 07605dff2b348170

SECTION: D00 T03 §14
PURPOSE: completion

1. **[P2] extend: Own compatibility for existing stamped completion evidence.** `receipt_data_ok` and `graph` already call `completion_ok` when validating stamped sections. The existing §13 receipt uses cap 33, but its completion record has no `CONTRACT:` line. Applying the new refusal unconditionally there would invalidate §13 and block graph-dependent commands, including this section's checkpoint. Specify an explicit adoption boundary: preserve validation of historical receipts while requiring the hardened checks for every new stamp, including re-stamps after reopening. Do not retrofit a digest into an old review. Add regression tests proving the existing §13 receipt still validates and a new stamp using digest-free evidence is refused.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 2)

1. filed -> D00 T03 §16
