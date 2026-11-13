---
id: a-second-check-asks-the-first-never-restates-it
applies: scripts/check-*.py, design/inventory/schema.json
topics: tooling, review
roles: main
source: docs/reviews/02-interface/D02-T01-s27.md#round-1/finding-1
fix: ee2e913
added: 2026-11-13
status: active
---
A check that backs up another rule (a scan for what a pattern cannot count, a script beside a schema) drifts from it when it restates that rule in words of its own: the call scan's own list of what may follow an argument refused texts the pattern accepts. Make the second check ask the first: split the input and hand each part to the rule itself. Then prove agreement over generated inputs both ways: it refuses nothing the rule accepts, and its verdict does not change with the size it exists for.
