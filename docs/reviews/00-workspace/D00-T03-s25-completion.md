# Completion review: D00 T03 §25

## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-10T16:17:22Z
- Effort: medium
- Type: adversarial
- Lines: 9
- Digest: 4daa21ea2eb72474

SECTION: D00 T03 §25
PURPOSE: completion
CONTRACT: sha256:3a215d4d6a4f534a44e79786ec9911b974881a4effb0ec24f5cffe83d4ef7e11

1. **P3 | extend:** Concurrent first-time recording is not covered. At [TODO-03-automations-and-keep-alive.md:738](/D:/Office/todo/00-workspace/TODO-03-automations-and-keep-alive.md:738), skipping an existing baseline is claimed to prevent races and preserve the first proof. However, the launcher and heartbeat can both read “no baseline” before either publishes. Both then perform the replacement required at line 737, overwriting the first timestamp; an interleaved read-back can also report a recording failure despite a valid baseline. The sequential second-run test cannot detect this. Define concurrent publication so the first published same-boot baseline survives, and add an interleaving test where both readers initially see no baseline. This affects evidence and diagnostics, rather than the validity of the boot proof.

COMPLETE: no
HIGHEST: P3
OVERALL: needs-attention

## Outcome (round 1)

1. extended

## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-10T16:20:36Z
- Effort: medium
- Type: adversarial
- Lines: 9
- Digest: 6050bc632f80f46a

SECTION: D00 T03 §25
PURPOSE: completion
CONTRACT: sha256:219f4eb209fc8f48420ed9af3791469c302df1a39a0b8bc48d4d80835d9b056c

1. **P3, extend:** The required write documentation contradicts the persistence design. [Line 740](D:/Office/todo/00-workspace/TODO-03-automations-and-keep-alive.md:740) requires saying nothing except `build/host-lock-baseline.json` is written, but lines 737 and 739 require a temporary file and `build/host-lock-baseline.lock`. An ordinary first successful check therefore violates the documented claim; the existing test explicitly expects both persistent files (`scripts/tests/test_check_campaign_host.py:499`). Amend the documentation requirement to name the baseline, lock file and transient atomic-write files.

COMPLETE: no
HIGHEST: P3
OVERALL: needs-attention

## Outcome (round 2)

1. filed -> D00 T03 §26
