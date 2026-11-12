---
id: a-deadline-covers-every-blocking-call
applies: scripts/ci-status.py, scripts/capture-ui.py, scripts/lib/process_tree.py
topics: tooling, ci
roles: main
source: docs/reviews/00-workspace/D00-T03-s15.md#round-1/finding-3
fix: b49cc86
added: 2026-11-12
status: active
---
A deadline holds only if it starts before the first blocking call and every later call is given what remains of it, never a fresh allowance: a wait made of several calls overran, and an initialisation that blocked before the timer started hung for good. Compute one end time, pass the remainder to each call, and test a call that blocks at each stage.
