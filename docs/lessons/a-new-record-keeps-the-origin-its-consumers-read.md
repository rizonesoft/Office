---
id: a-new-record-keeps-the-origin-its-consumers-read
applies: scripts/capture-ui.py, scripts/lib/*.py
topics: tooling, review
roles: main
source: docs/reviews/02-interface/D02-T01-s35.md#round-1/finding-2
fix: 5f05618
added: 2026-11-15
status: active
---
A new kind of record that measures from its own corner breaks every tool that reads the old ones: the menus capture put a mini toolbar's controls from the toolbar's corner and the toolbar from the menu's, and scripts/check-layout.py, which takes a child's place in its parent as the difference of their bounds, reported every control as moved. Before a capture writes a field other tools read, find its consumers and run one of them over the new records in a test: one origin for a parent and all that stands under it.
