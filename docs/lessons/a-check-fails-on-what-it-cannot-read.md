---
id: a-check-fails-on-what-it-cannot-read
applies: scripts/check-*.py, scripts/capture-ui.py, scripts/ci-status.py, scripts/lib/*.py
topics: tooling, tests
roles: main
source: docs/reviews/02-interface/audit-d02-t01-s1.md#round-17/finding-2
fix: c1de42d
added: 2026-11-12
status: active
---
A check that cannot read or parse its input must fail and name it, never treat it as absent, off, zero or passing: an unreadable folder, a missing key, empty or malformed output of a tool it ran, a timeout, a truncated history. Write the unreadable and the malformed case as tests beside the passing one, and make a missing answer a distinct result from a negative one.
