---
id: not-recorded-is-not-not-read
applies: scripts/capture-ui.py, scripts/lib/*.py
topics: tooling, review
roles: main
source: docs/reviews/02-interface/D02-T01-s31.md#round-1/finding-1
fix: 79cb26f
added: 2026-11-13
status: active
---
Leaving data out of the output does not meet a rule that it is never read: the Options capture fetched every element's name, an add-in's folder and the entries of grids among them, and filtered afterwards. When a tool must not read something, decide from structure before fetching: walk to what you need step by step instead of searching, fetch a field lazily, and test with a fake that counts reads and requires none.
