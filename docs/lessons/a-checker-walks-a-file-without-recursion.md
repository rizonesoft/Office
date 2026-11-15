---
id: a-checker-walks-a-file-without-recursion
applies: scripts/lib/*.py, scripts/check-inventory.py
topics: tooling, review
roles: main
source: docs/reviews/02-interface/D02-T01-s35.md#round-1/finding-1
fix: 5f05618
added: 2026-11-15
status: active
---
A checker that follows a file's own parent chain by calling itself once per level crashes on the file it exists to refuse: 1,100 records hung one under another ended the menus checker with RecursionError before its one-level rule was reached. A file is never trusted to be shallow. Collect what stands under a record with an explicit stack, let the rule that limits the depth do the refusing, and test with a chain deeper than Python's stack.
