# Completion review: D00 T03 §26

## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-10T16:34:37Z
- Effort: medium
- Type: adversarial
- Lines: 13
- Digest: 156ce768e8c08f12

SECTION: D00 T03 §26
PURPOSE: completion
CONTRACT: sha256:cae9672ad565b5e3b7f10c63687f720fab2918a4ee9571e56ab2b3ed2f962aa2

1. **P2: The exhaustive file list omits normal probe and notification writes.** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:768` requires “nothing else is written”, but `scripts/check-campaign-host.py:364-367` creates temporary `campaign-host-*/out` and `err` files during probes, and lines 394-396 create `campaign-notice-*/notice.json` for notifications. Building the section exactly as written leaves the documentation false during ordinary use. **Remedy: extend** the inventory and its test to cover these scratch files, their locations and cleanup lifetimes. §12 owns their implementation, but this section must document them.

2. **P2: The promised temporary-file lifetime excludes real failure states.** The same checklist at `todo/00-workspace/TODO-03-automations-and-keep-alive.md:768` requires “exists only during one write, removed on success and on failure”. However, `scripts/check-campaign-host.py:295-302` cannot clean up after process termination between creation and replacement, and explicitly suppresses cleanup errors. A terminated check or failed deletion can therefore leave the temporary file behind, precisely the state this documentation should explain. **Remedy: extend** the wording to distinguish normal cleanup from interrupted writes and failed cleanup, with a test pinning that qualification. §25 owns the write mechanism; it does not establish unconditional removal.

3. **P3: The prescribed test does not pin the promised names and lifetimes.** At `todo/00-workspace/TODO-03-automations-and-keep-alive.md:769`, substring checks permit removing the standalone baseline entry because its name remains inside the temporary-file name. They also permit replacing the temporary filename with merely `.tmp`, or deleting every lifetime explanation. The fresh-root directory assertion would still pass. **Remedy: extend** the assertions to require each complete documented entry and its lifetime, and verify that removing each entry or lifetime independently fails.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended
3. extended
