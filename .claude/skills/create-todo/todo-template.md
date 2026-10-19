---
schema_version: 1
id: CHANGEME-unique-kebab-id
domain: CHANGEME-NN-domain
status: draft
title: "TODO-NN -- CHANGEME Title"
---

# TODO-NN -- CHANGEME Title

> **Goal:** CHANGEME: one paragraph. What is true when this file is finished, in plain terms.

> **Current state:** Measured YYYY-MM-DD. CHANGEME: what exists right now, before this TODO runs. Name real files, real behaviour and real gaps.

## Inputs

- CHANGEME: the governing plan or SPEC sections, and existing files with what each section consumes.
- -> XREF: CHANGEME DNN TNN §N -- the related work and what flows each way (reciprocate in the target file)

## Outcome

- CHANGEME: an observable end state, not an activity.
- CHANGEME: a second end state, with its readback.

**Adjacency:** CHANGEME: `all=not-applicable (reason covering the whole scope)`, or all nine keys exactly once separated by semicolons: `key=applicable`, `key=applicable @ DNN TNN §N`, `key=not-applicable (reason)`.

**Adjacency rationale:** CHANGEME: the substantive decisions behind the line above, in prose.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | CHANGEME deliverable | -- | [ ] |
| 2 | §2 | CHANGEME deliverable | §1 | [ ] |

## 1. CHANGEME Single-Responsibility Section Title

CHANGEME: one paragraph of context: why this section exists, the single coherent capability it delivers, and what it must not break. Split multi-subsystem work into separate small sections in this file.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. CHANGEME: edit `backtick/path` from named source evidence. Done when: a command, readback or rendered surface proves it.
2. CHANGEME: wire the refusal, cancellation, or recovery path in `backtick/path`. Done when: bad input or abort fails cleanly without corrupting state.

- [ ] CHANGEME micro-step 1 in `backtick/path` (one action, source citation). Done when: CHANGEME observable end state. Cheaper substitute: CHANGEME the shortcut or wrong layer that must fail.
- [ ] CHANGEME micro-step 2 in `backtick/path` (refusal/error/read-back path). Done when: CHANGEME observable end state. Cheaper substitute: CHANGEME silent swallow or in-memory-only stub.
- [ ] CHANGEME micro-step 3 in `tests/backtick/path` (falsifiable test covering happy + refusal path). Done when: CHANGEME test command passes and fails if production logic is reverted.
- [ ] Commit: `scope: concrete outcome`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0; replace with the feature's own falsifiable check before making this file active.

## 2. CHANGEME Second Single-Responsibility Section Title

CHANGEME: one paragraph of context. Surface sections set `**Surface:** yes` and add Fidelity, Job, Treatment and Chrome lines, accounting for 100% of controls on the SPEC surface (working or deferred to a resolving `-> XREF: DNN TNN §N`); sections in a `frozen: true` file add a `**Freeze check:**` line naming the fixtures that must not move.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. CHANGEME step in `backtick/path`. Done when: CHANGEME observable end state.
2. CHANGEME verification step in `tests/backtick/path`. Done when: CHANGEME observable end state.

- [ ] CHANGEME micro-step 1 in `backtick/path`. Done when: CHANGEME observable end state. Cheaper substitute: CHANGEME the wrong thing.
- [ ] CHANGEME micro-step 2 in `tests/backtick/path`. Done when: CHANGEME observable end state.
- [ ] Commit: `scope: concrete outcome`

**Test checkpoint:** CHANGEME: the falsifiable proof, as a runnable command in backticks with its expected result.

## Verification

- CHANGEME: the connected outcome, end to end, with its evidence.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
