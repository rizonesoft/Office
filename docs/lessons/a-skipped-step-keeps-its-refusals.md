---
id: a-skipped-step-keeps-its-refusals
applies: scripts/lib/*.py, scripts/*.py
topics: tooling, review
roles: main
source: docs/reviews/00-workspace/D00-T03-s62.md#round-1/finding-1
fix: ca48553
added: 2026-11-13
status: active
---
Removing a call because nothing reads its answer also removes what its failure refused: a graph read stopped comparing two commits for a pass no lens watched, and a receipt naming a commit the repository no longer held began to pass. Before skipping work for speed, list what refuses when that work fails, and keep each refusal by a cheaper proof (the object is in a set already read) or keep the call where there is none. Test the skipped path with the input only the old call refused.
