---
id: cleanup-touches-only-what-the-tool-owns
applies: scripts/capture-ui.py, scripts/lib/office_com.py
topics: tooling, windows
roles: main
source: docs/reviews/02-interface/D02-T01-s4.md#round-12/finding-1
fix: 69eacbb
added: 2026-11-12
status: active
---
A tool that drives something the operator also uses (an Office application, the clipboard, the working tree) may close, overwrite or restore only what it made itself, shown at the moment it acts and not at an earlier check. Take ownership by an identity the tool created, check it again in the same step that acts, and refuse and report when ownership cannot be shown: an unsaved document or a newer clipboard is never discarded.
