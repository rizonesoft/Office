---
id: malformed-input-is-refused-not-crashed-on
applies: scripts/*.py
topics: tooling, tests
roles: main
source: docs/reviews/02-interface/audit-d02-t01-s1.md#round-2/finding-2
fix: 8a3ac26
added: 2026-11-12
status: active
---
Malformed or hostile input gets the tool's documented refusal, a line naming the input and its refusal exit code, never a traceback and never an unhandled exception's exit 1. Check the shape of parsed data before using it (a row may be a number, a manifest may be null), and catch the I/O and API errors of every external call, including the ones made while reporting another error.
