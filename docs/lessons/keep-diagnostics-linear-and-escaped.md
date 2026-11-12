---
id: keep-diagnostics-linear-and-escaped
applies: scripts/check-*.py
topics: tooling, security
roles: main
source: docs/reviews/02-interface/audit-d02-t01-s1.md#round-12/finding-1
fix: 80bb2f9
added: 2026-11-12
status: active
---
Diagnostics are part of a checker's attack surface. Build them in one pass (gather locations once per file, never rebuild a set or rescan a list for every record), bound how much one bad file may report, and print any text taken from the input escaped, so a hostile value cannot write to the terminal. Add a fixture of a few thousand bad records with a time bound.
