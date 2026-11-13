---
id: a-restarted-task-must-be-safe-to-run-again
applies: .conclave/automations/**, scripts/owner-digest.py, scripts/lib/digest_state.py
topics: process, tests
roles: main
source: docs/reviews/00-workspace/D00-T03-s53.md#reconciliation-11/finding-2
fix: e846afb
added: 2026-11-13
status: active
---
A restart-on-failure setting reruns a command that exited non-zero after doing part of its work. The weekly digest sent its email, failed to mark the notices, exited 1, and the scheduler's retry would have sent a second email. Before giving a task a restart policy, read what each of its non-zero exits leaves done, and make the command know a rerun from a new run by its own record (here: a digest for today already exists), with a test that runs it again after each such exit.
