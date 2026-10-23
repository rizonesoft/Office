# Completion review: D00 T03 §23

## Round 1: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T18:39:54Z
- Effort: medium
- Lines: 11
- Digest: a252d4b7e397992a

SECTION: D00 T03 §23
PURPOSE: completion
CONTRACT: sha256:cf145a26dda43f0879fee1c9d2d2aa5ac82fcc3f8b050e72b4b6c9f8df4838bf

1. **P2 | extend:** Deletion-safe discovery is missing from `Pages.newest`, which §22 uses on resumed tries. With more than one page of new runs, deleting an already-read run during that refresh can skip a new push head. A completed forward scan has no remaining boundaries to check, and the held deleted run can mask the omission in the count comparison. Extend boundary recovery to newest-page refreshes, including their stopping condition. Require a fixture with a completed checkpoint, multiple pages of new runs and a deletion during refresh that still discovers every remaining head.

2. **P2 | extend:** Reading only page N again cannot recover shifts larger than one page. For example, read original positions 1 through 200, delete positions 1 through 150, then read page 3: it returns original positions 351 through 450. Rereading page 2 recovers 251 through 350 but leaves 201 through 250 unseen. Bulk workflow-run cleanup is within this feature's deletion scenario. Extend recovery to rewind far enough to re-establish continuity, with bounded calls and persisted recovery progress. Require a fixture deleting more than 100 already-read runs and proving every remaining run is discovered.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended

## Round 2: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T18:43:06Z
- Effort: medium
- Lines: 9
- Digest: c8c2b4cfe078ab7d

SECTION: D00 T03 §23
PURPOSE: completion
CONTRACT: sha256:6ac5c2b4c9fd452ec318542b66ba4c602b266328a12f54d432282ad679fc77e4

1. **P2 | extend:** Persist unfinished newest-page refreshes, including when interrupted before a boundary check detects deletion. For example, a completed checkpoint gains 300 new runs; a refresh reads the first 200, then the first 100 are deleted and the deadline expires before page 3. On resume, page 1 contains the already-held second hundred and passes the unchanged-page stop condition. The deleted hundred still held masks the unread hundred in `total_count`, so those remaining heads are never discovered. Saving only the recovery rewind position does not cover this state because recovery never started. Extend the checkpoint to retain an unfinished refresh cursor and its boundary anchor, and prevent an unchanged first page from cancelling that outstanding scan. Require a fixture reproducing this interruption and deletion, proving subsequent tries discover every remaining head.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 2)

1. filed -> D00 T03 §24
