# Completion review: D00 T03 §34

## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-11T00:04:13Z
- Effort: medium
- Type: adversarial
- Lines: 15
- Digest: a494ca7e2d27f755

SECTION: D00 T03 §34
PURPOSE: completion
CONTRACT: sha256:2fa04b4316bfdfa594df95b8e710074162fcf9eb65181f1836c2e06c2b575ed4

1. **[P2] Concurrent saves during acceptance or rejection are unowned.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1015` stages live files after displaying and checking them. An owner save between those operations can stage content the main loop never reviewed. At line 1016, a save after the stash captures a file but before its cleanup can also be overwritten; checking that the tree is clean afterward does not prove that save was preserved. **Remedy: extend** with an explicit concurrency contract: stage the exact reviewed snapshot, refuse changes to the candidate before acceptance, and establish a safe exclusion boundary for destructive stash cleanup. Test saves injected between inspection, capture and mutation, asserting content preservation rather than merely a clean final status.

2. **[P2] The detected “HEAD moved” state has no safe rejection outcome.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1014` explicitly detects a worker commit, but line 1016 only stashes uncommitted changes. If the worker commits everything, the empty-tree rule at line 999 closes the packet without a stash while leaving the rejected commit on `main`. The next packet can then begin on that rejected baseline. **Remedy: extend** with a defined HEAD-mismatch recovery path. At minimum, refuse normal rejection completion, retain the original baseline and packet, and report the commits requiring reconciliation. Add committed-only and committed-plus-uncommitted fixtures proving that rejection cannot silently bless the moved baseline.

3. **[P2] Interrupted and partially successful rejection has no resumable record.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1016` requires creating a stash, checking it, printing its name and deleting the packet, but owns no intermediate state. If the process stops after successful stashing and before reporting, the next `reject` sees a clean tree and closes without identifying the saved work. A locked file can instead leave a created stash and incomplete cleanup, with no specified retry behavior. **Remedy: extend** with durable rejection progress and the exact stash object ID, retaining the packet until preservation and cleanup are verified. Test interruption after stash creation, cleanup failure and retry; each must identify the preserved snapshot and avoid claiming completed rejection prematurely.

4. **[P2] The prescribed display can conceal staged content.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1013` calls `git diff HEAD` the complete staged and unstaged change. If a file contains A at HEAD, B in the index and A again in the working tree, that diff is empty although status reports a changed file. The required tests use staged and unstaged edits without requiring this opposing-change case, so they do not prove complete inspection. **Remedy: extend** the display contract to show HEAD-to-index and index-to-working-tree changes separately, alongside untracked contents. Add a fixture with opposing edits to the same file and assert both versions are visible.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended
3. extended
4. extended

## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-11T00:06:25Z
- Effort: medium
- Type: adversarial
- Lines: 15
- Digest: 48cac264be8b234a

SECTION: D00 T03 §34
PURPOSE: completion
CONTRACT: sha256:ba6553a5f2946604bfcf72ca78469651cbadf61964081b6a581db561eee743af

1. **[P1] Rejection still permits irreversible loss of a concurrent save.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1016` prescribes checking captured bytes immediately before overwriting or deleting a path. An editor can save after that check but before the mutation. Rejection then destroys bytes absent from the stash. The specified test can pass by injecting its save before the check, leaving this failure untested. **Remedy: extend** with a preservation protocol that protects the actual mutation, including editor saves that replace files. Where protection cannot be established, retain the path and report it unresolved. Test saves between the final comparison and both replacement and deletion.

2. **[P2] The digest need not identify the content actually displayed for review.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1013` specifies printing diffs and then hashing working-tree bytes, without requiring both to use one captured snapshot. A diff can display version A, an editor save version B, and the digest identify B. The subsequent staging command accepts B although the reviewer only saw A. **Remedy: extend** to capture immutable inputs once and derive both the displayed change and its digest from those inputs. Add a test injecting a save between diff generation and hashing, proving undisplayed bytes cannot be accepted.

3. **[P2] Staging has no transaction or interruption-recovery contract.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1015` describes individual index updates but only tests refusals before mutation. For a two-file packet, staging the first file can succeed and the second update fail because of an index lock or disk error, leaving a partially accepted index. No specified state or recovery procedure distinguishes that result from the original packet. **Remedy: extend** to prepare the complete index change separately and publish it atomically under Git’s index lock, verifying the original index has not changed. Test failure after preparing the first entry, concurrent index modification, and interruption around publication; require either an unchanged index or a recorded, recoverable completed acceptance.

4. **[P2] An interrupted rejection can be accepted as a smaller packet.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1018` introduces rejection progress, but the eligibility rules at lines 1014 and 1015 do not exclude that state. If rejection returns one file and then fails on another, `show` can report the remaining in-scope change with unchanged `HEAD`; `show --stage` can accept it and close the packet, abandoning the rejection journal. **Remedy: extend** with explicit lifecycle rules: once rejection starts, staging must refuse, inspection must identify the incomplete rejection, and retry must resume it. Test `show` and `show --stage` after each specified rejection interruption.

COMPLETE: no
HIGHEST: P1
OVERALL: needs-attention

## Outcome (round 2)

1. filed -> D00 T03 §46
2. filed -> D00 T03 §47
3. filed -> D00 T03 §48
4. filed -> D00 T03 §49
