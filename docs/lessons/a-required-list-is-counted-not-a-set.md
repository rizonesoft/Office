---
id: a-required-list-is-counted-not-a-set
applies: scripts/lib/*.py, scripts/check-inventory.py
topics: tooling, review
roles: main
source: docs/reviews/02-interface/D02-T01-s34.md#round-1/finding-3
fix: d1526a4
added: 2026-11-13
status: active
---
A completeness check that folds what was found into a set loses how many there were: Font's Advanced tab must show two spinners labelled By, and either one satisfied both entries of the required list, so a capture missing one would have published. When a hand-written list holds a capture, compare counts (collections.Counter), not membership, and test by removing one of two equal entries with the totals lowered to match.
