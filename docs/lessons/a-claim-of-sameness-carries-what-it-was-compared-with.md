---
id: a-claim-of-sameness-carries-what-it-was-compared-with
applies: scripts/lib/*.py, scripts/capture-ui.py, scripts/check-inventory.py
topics: tooling, review
roles: main
source: docs/reviews/02-interface/D02-T01-s36.md#round-1/finding-2
fix: a10215e
added: 2026-11-15
status: active
---
A record that says only "the same as that one" changes meaning when that one changes: a page of a document state was recorded as unchanged with nothing but the id of the blank page it equalled, so capturing the blank document again would have rewritten what seven states claim without touching them. When a record stands for another by reference, store a digest of what it was compared with, have the checker recompute it, and refuse the dependent record until it is made again. Let each stale one be remade in turn: a rule that needs all fresh at once can never be met.
