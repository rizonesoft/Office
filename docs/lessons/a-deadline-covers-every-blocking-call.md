---
id: a-deadline-covers-every-blocking-call
applies: scripts/ci-status.py, scripts/capture-ui.py, scripts/lib/process_tree.py, scripts/make-word-state-fixtures.py
topics: tooling, ci
roles: main
source: docs/reviews/00-workspace/D00-T03-s15.md#round-1/finding-3
fix: b49cc86
added: 2026-11-12
revised: 2026-11-15
status: active
---
A deadline holds only if it starts before the first blocking call and ends after the last one, with every call given what remains of it: a wait made of several calls overran, an initialisation that blocked before the timer started hung for good, and a watchdog cancelled before the cleanup left a quit that blocks to hold the run. Closing, counting and quitting are blocking calls too. Compute one end time, keep it running until the resource is seen released, and test a call that blocks at each stage, the last one included.
