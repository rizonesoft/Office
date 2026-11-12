---
id: a-test-fails-when-the-behaviour-is-removed
applies: scripts/tests/*.py
topics: tests, review
roles: main
source: docs/reviews/00-workspace/D00-T05-s4.md#round-1/finding-2
fix: b460781
added: 2026-11-12
status: active
---
A test that asserts a marker (a heading, a phrase somewhere in a file, an exit code alone) still passes when the behaviour it stands for is moved, emptied or removed. For each test, name the change that would break the promise and still pass, then assert the behaviour itself: where a step sits, what it returns, what it leaves on disk. Before trusting it, remove or move the behaviour and see the test fail.
