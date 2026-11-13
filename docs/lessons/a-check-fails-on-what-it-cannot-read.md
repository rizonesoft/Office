---
id: a-check-fails-on-what-it-cannot-read
applies: scripts/check-*.py, scripts/capture-ui.py, scripts/ci-status.py, scripts/lib/*.py
topics: tooling, tests
roles: main
source: docs/reviews/02-interface/audit-d02-t01-s1.md#round-17/finding-2
fix: c1de42d
added: 2026-11-12
revised: 2026-11-13
status: active
---
A check that cannot read or parse its input must fail and name it, never treat it as absent, off, zero or passing: an unreadable folder, a missing key, malformed output of a tool it ran, a timeout, a truncated history. This holds for every external call, also the tenth inside a loop: list what a non-zero exit of each can mean, and where absent is a legitimate answer prove it with a second question (git ls-tree for a file a commit removed) instead of assuming it. Write the unreadable case as a test beside the passing one, for each call.
