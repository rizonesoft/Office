---
id: publish-with-compare-and-swap
applies: scripts/lib/office_com.py, scripts/capture-ui.py
topics: tooling
roles: main
source: docs/reviews/02-interface/audit-d02-t01-s3.md#round-2/finding-1
fix: 9abe704
added: 2026-11-12
status: active
---
Publishing a file that something else may write at the same moment: publish with a compare and swap on exactly what was read, or under a lock both writers take, keep the earlier copy until the new one is proved in place, and on rollback remove only what this run wrote. A check followed by a replace, however close together, loses the save that lands between them.
