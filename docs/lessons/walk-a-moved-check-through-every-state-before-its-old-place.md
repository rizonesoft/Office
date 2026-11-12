---
id: walk-a-moved-check-through-every-state-before-its-old-place
applies: todo/**/*.md
topics: process
roles: main
source: docs/reviews/03-architecture/D03-T01-s30.md#round-1/finding-1
fix: a7ae178
added: 2026-11-12
status: active
---
A check that ran once at a gate assumes the finished state. Moved earlier, it meets every state on the way there: nothing captured, captured and unclaimed, half claimed while the claims are being written. Twice in one section a check moved to an earlier place would have refused the commits that lead to the gate. Before moving a check, list each state the tree passes through between the new place and the old one, say what the check does in each, and name the event that turns it strict; a first sign of progress is rarely that event.
