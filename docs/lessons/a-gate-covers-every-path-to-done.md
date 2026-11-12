---
id: a-gate-covers-every-path-to-done
applies: .claude/skills/*/SKILL.md
topics: process, ci
roles: main
source: docs/reviews/00-workspace/D00-T03-s15.md#round-2/finding-1
fix: ae2d99c
added: 2026-11-12
status: active
---
A gate written into a skill (CI is green before the next row, a closeout is pushed before the run ends) holds only if every path to the end passes through it: the heartbeat, a phase run on its own, a resume, a park. For each gate, list the ways the procedure can finish and write the gate into each, and check the commit the gate approved is the one that ships: after a pull, a merge or a bookkeeping commit it is not.
