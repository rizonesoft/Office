---
id: a-restore-lives-in-the-process-that-outlives-the-work
applies: scripts/capture-ui.py, scripts/lib/*.py
topics: tooling, review
roles: main
source: docs/reviews/02-interface/D02-T01-s32.md#round-1/finding-1
fix: ed3f8df
added: 2026-11-13
status: active
---
Cleanup that must happen cannot live only in a process someone else may kill: the pane capture put Word's panes back from its worker, which is ended on Ctrl+C or a time limit, and Word then kept the changed state. Keep the snapshot and the restore in the process that outlives the work and owns the resource, run it on that process's every exit path before the resource is released, and attempt every cleanup step even after one fails.
