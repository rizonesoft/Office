---
id: windows-paths-compare-without-case
applies: scripts/check-*.py
topics: tooling, windows
roles: main
source: docs/reviews/02-interface/audit-d02-t01-s1.md#round-22/finding-2
fix: 6e0db0f
added: 2026-11-12
status: active
---
Windows opens a file whatever the case of its name, so a rule keyed on an exact file or folder name is skipped by a name in another case. Compare names case-insensitively wherever the name selects what a check applies to, and add a fixture whose name differs only in case.
