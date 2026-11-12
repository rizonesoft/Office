---
id: evidence-is-observed-never-manufactured
applies: scripts/capture-ui.py, scripts/check-inventory.py, design/inventory/**/*.json
topics: tooling, ui
roles: main
source: docs/reviews/02-interface/D02-T01-s4.md#round-1/finding-1
fix: 6014285
added: 2026-11-12
status: active
---
A record that claims to be measured (a live capture, a build's provenance) holds only what that run observed, checked against a source outside itself. A constant published as a measurement, a rule generated instead of observed, and a value compared with the record under check are all fabricated evidence. Mark what was not observed as such, and make the checker compare with the reference.
