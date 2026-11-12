---
id: a-test-stands-in-for-every-program-its-code-calls
applies: scripts/tests/*.py, scripts/tests/fixtures/*
topics: tests, security
roles: main
source: docs/reviews/00-workspace/D00-T07-s4.md#round-1/finding-1
fix: 3031d96
added: 2026-11-12
status: active
---
A test that runs real code against stand-ins must stand in for every program that code can start, native programs included: the installer's tests replaced the Scheduler cmdlets but not wevtutil, and from an elevated window would have changed this PC's logging. When a tool gains a call to an external program, add its stand-in to the fixture in the same change, and assert the calls the stand-in received.
