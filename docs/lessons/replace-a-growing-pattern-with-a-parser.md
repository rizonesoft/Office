---
id: replace-a-growing-pattern-with-a-parser
applies: design/inventory/schema.json, scripts/check-*.py
topics: tooling, review
roles: main
source: docs/reviews/02-interface/audit-d02-t01-s1.md#round-2/finding-1
fix: 8a3ac26
added: 2026-11-12
status: active
---
One regular expression that needs an exception every round is the wrong tool: the inventory's address rule took 33 rounds, each fix opening a new bypass or a new false refusal. When two rounds running find both in the same pattern, stop patching it. Split the text into tokens and state the rule over tokens, or replace the rule with a closed list of what is allowed, and keep the pattern for the simple, bounded part only.
