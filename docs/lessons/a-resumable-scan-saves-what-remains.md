---
id: a-resumable-scan-saves-what-remains
applies: scripts/ci-status.py
topics: tooling, ci
roles: main
source: docs/reviews/00-workspace/D00-T03-s23.md#round-2/finding-1
fix: d58f895
added: 2026-11-12
status: active
---
A scan that can be interrupted and resumed over a list that changes underneath it (CI runs being added, rerun and deleted) must save, durably and before acting on it, the boundary it read against and what remains to be read. Resume from that record, treat a count or page that changed as a reason to read again and never as progress, and never report clean while any part is unread.
