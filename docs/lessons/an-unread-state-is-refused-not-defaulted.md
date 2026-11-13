---
id: an-unread-state-is-refused-not-defaulted
applies: scripts/capture-ui.py, scripts/lib/*.py
topics: tooling, review
roles: main
source: docs/reviews/02-interface/D02-T01-s33.md#round-1/finding-1
fix: cd4cfdb
added: 2026-11-13
status: active
---
A comparison that turns 'could not read' into a valid value fabricates data: the status bar capture read a tick as state == 1, so an item with no toggle state was recorded as off, and a second reading agreed. When a tool reads a state, keep the raw answer, name the values that count as read, and refuse anything else before a record is built. Test with a source that answers nothing.
