---
id: python-text-tests-are-not-the-schemas
applies: scripts/check-*.py, design/inventory/schema.json
topics: tooling
roles: main
source: docs/reviews/02-interface/audit-d02-t01-s1.md#round-3/finding-2
fix: 7d37649
added: 2026-11-12
status: active
---
Python's strip, isspace, isdigit and the classes \s, \d and \w accept Unicode characters that a JSON Schema pattern, or a rule meant for ASCII, does not, so a script and a schema that should agree drift apart on blank text and digits. Name the characters in an explicit class on both sides, and add fixtures with a non-ASCII digit, a non-breaking space and an invisible character.
