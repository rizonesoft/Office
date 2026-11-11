# Completion review: D00 T03 §35

## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-11T07:09:17Z
- Effort: medium
- Type: adversarial
- Lines: 17
- Digest: ff1c7bc6581aa311

SECTION: D00 T03 §35
PURPOSE: completion
CONTRACT: sha256:a9c3513d6ec058c8e72219af8d3b6593eb08019f826d9d54f86651e94879465f

1. **[P2] Exact owner actions have no reliable source.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1053` specifies the first paragraph as the instructions. Existing paragraphs describe purpose, not the steps or evidence needed to unblock work. For example, `todo/00-workspace/TODO-02-licensing-and-contributions.md:102` describes the contributor agreement, while the required review, approval and removal of Needs appear at lines 115-116. The prescribed test checks inclusion and dependant count, so it passes without actionable instructions. **Remedy: extend** with an explicit owner-action field or equivalent deterministic source, populate it for eligible sections, and test that the digest includes the actions and where to record completion.

2. **[P2] Stopped campaigns are reported as running.** The fallback at `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1055` treats absence of `PARKED` or `STOPPED` as evidence of running. Actual operator stops use Critical events prose: `docs/phase-runs/2026-11-11-phase-0.md:28` records an ended guard and deleted heartbeat without either marker. A digest generated after that stop would claim “Running.” A commit date also cannot establish that a campaign survived a reboot or closed window. **Remedy: extend** with authoritative lifecycle-state handling, including stopped, completed, inactive and unknown states. Test the existing operator-stop format and absence of a live run.

3. **[P2] The specified CI command cannot report CI, and non-green states lack acceptance coverage.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1055` invokes `python scripts/ci-status.py` without arguments; `scripts/ci-status.py:820-821` explicitly rejects that invocation. The checkpoint tests only parked and running states. Even after adding a ref, red, pending and unavailable CI must become digest content rather than accidentally aborting the email through generic subprocess failure handling. **Remedy: extend** to specify the commit/ref being reported and test green, red, pending and unknown results, including unavailable GitHub access.

4. **[P2] Truncation can permanently hide owner actions.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1056` explicitly accepts cutting the report to 120 lines and replacing omitted items with a count. Combined with the fixed priority order at line 1054, a persistent backlog can hide the same lower-ranked waiting items every week. This does not deliver every waiting item with exact steps. **Remedy: extend** with a complete overflow delivery mechanism within the single email, such as a plain-text attachment containing all omitted instructions, and reserve summary space for progress, totals, run state and CI. Test that every waiting item remains accessible when the cap is exceeded.

5. **[P2] Existing immediate emails remain outside the promised weekly digest.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1041` promises no other interruption, but line 1039 explicitly retains the three existing email kinds. `.conclave/automations/run.py:252-258` sends an immediate failure email, and `.claude/skills/process-plan/SKILL.md:82` requires immediate host-failure notification. A failing daily automation therefore still interrupts the owner outside the digest. §1 and §12 own those existing senders, but no named section owns their transition to the new policy. **Remedy: new section** to persist those notices for inclusion in the digest and retire their immediate sends, with tests proving failures remain visible without additional email.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended
3. extended
4. extended
5. filed -> D00 T03 §53

## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-11T07:11:33Z
- Effort: medium
- Type: adversarial
- Lines: 13
- Digest: d0aeb9b405d198f4

SECTION: D00 T03 §35
PURPOSE: completion
CONTRACT: sha256:12f7ca69ad761064782da3a866b01646621395895e2763f44b14184a2dcd1b1c

1. **P2: Guard existence can falsely report a stopped campaign as Running.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1058` explicitly makes file existence sufficient. However, `scripts/campaign_guard.py:153-157` recognises an ended guard whose file remains after interrupted cleanup, and lines 18-25 document that a dead session leaves its guard for handover. An ordinary session crash can therefore produce a weekly claim that work is running when nothing is executing. **Remedy: extend** the section to honour ended guards and distinguish an open guard from verified session activity. Report activity as unknown when it cannot be established. Test ended and abandoned guards, not only absent and present files.

2. **P2: Progress overflow has no preservation path.** The progress requirement at `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1053` promises the sections verified during the week, but line 1060 reserves attachment preservation only for waiting items. A productive week with 130 completed sections exceeds the 120-line body before run state, CI, totals or waiting items are included. Implementing the stated truncation can silently lose the promised progress list; the 300-waiting-item test would still pass. **Remedy: extend** overflow handling to preserve the complete progress list in an attachment too, with explicit body counts. Test progress-only overflow and combined progress/waiting overflow.

3. **P2: A transient send failure loses the weekly digest without a recovery path.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1061-1063` specifies one send and a weekly trigger, but no pending-delivery state or retry. The existing runner records a failed command and returns (`.conclave/automations/run.py:130-144`); the installer provides missed-start catch-up, not failed-send recovery (`.conclave/automations/install.ps1:79-81`). If the network is unavailable on Monday morning, the next scheduled digest is a week later, when the original reporting window has disappeared. §53 owns failure notices, not digest delivery recovery. **Remedy: extend** the section with persisted reporting periods, bounded recovery after definite delivery failures, and an explicit policy for ambiguous send outcomes that avoids blind duplicate sends. Test failure followed by recovery and ensure the original progress remains reportable.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 2)

1. filed -> D00 T07 §1
2. filed -> D00 T07 §2
3. filed -> D00 T07 §3
