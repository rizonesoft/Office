---
schema_version: 1
id: owner-digest-follow-ups
domain: 00-workspace
status: active
title: "TODO-07 -- Owner Digest Follow-ups"
---

# TODO-07 -- Owner Digest Follow-ups

> **Goal:** The weekly owner digest of D00 T03 §35 stays truthful and complete when a session dies, a week is busy or a send fails: it never calls an abandoned run running, never drops a progress line, and never loses a week.

> **Current state:** Measured 2026-11-11. D00 T03 §35 (in progress) builds `scripts/owner-digest.py` and the `office-owner-digest` task; its completion review round 2 found three gaps this file owns. TODO-03 holds the 55 sections a file may hold, so they open this file.

## Inputs

- `docs/specs/2026-10-23-campaign-scope-design.md`, decision 32: one weekly email, no other interruption.
- `scripts/campaign_guard.py` (the run guard and its state file), `.conclave/automations/alert.py` (the transport), `.conclave/automations/run.py` and `tasks.json` (the scheduled tasks).
- -> XREF: T03 §35 -- the digest these sections extend; T03's Inputs point back here

## Outcome

- The digest reports a run as running only when its session shows life, keeps every progress line however long the week, and is sent again after a failed send, covering the whole period missed.

**Adjacency:** all=not-applicable (developer tooling for one recipient: the owner's weekly email, with no records, settings or surfaces of its own)

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Digest tells a live run from an abandoned guard | T03 §35 | [ ] |
| 2 | §2 | Digest keeps a long progress list | T03 §35 | [ ] |
| 3 | §3 | Digest delivery survives a failed send | T03 §35 | [ ] |

## 1. Digest Tells a Live Run From an Abandoned Guard

Filed 2026-11-11 from the completion review of T03 §35 (`docs/reviews/00-workspace/D00-T03-s35-completion.md`, round 2, finding 1, P2). T03 §35 reports `Running` while `build/claude-campaign-guard.json` exists, but a session that crashed leaves its guard in place for the launcher's handover (`scripts/campaign_guard.py`), and an `end` interrupted after its marker leaves one too. This section reports a run as running only when the guard's session shows life.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Read the guard as `campaign_guard.py` reads it. Done when: an ended, an abandoned and a live guard each report their own state.

- [ ] Ask `python scripts/campaign_guard.py whoami` (or the function behind it) from `scripts/owner-digest.py` instead of testing the guard file's existence, and report `Running` only for an open guard whose state file shows a heartbeat or a hook call in the last hour, `Stalled since <time>` for an open guard without one, and the run file's own state for an ended guard. Done when: tests in `scripts/tests/test_owner_digest.py` cover a live, a stalled and an ended guard.
- [ ] Report `Unknown` with the reason when the guard or its state cannot be read. Done when: a test with a malformed guard shows it.
- [ ] Commit: `automations: the digest tells a live run from an abandoned guard`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_owner_digest.py"` passes with the guard tests among them.

## 2. Digest Keeps a Long Progress List

Filed 2026-11-11 from the completion review of T03 §35 (round 2, finding 2, P2). T03 §35 moves an overflowing waiting list into an attachment, but not the list of sections verified in the week, so a productive week could push the run state, CI and the waiting items out of the 120-line body, or cut the progress list. This section puts the whole progress list in the attachment too and keeps the body's summary first.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Order the body and overflow both lists. Done when: a week of 130 stamps keeps the summary, CI and run state in the body and every stamp in the attachment.

- [ ] Order the body of `scripts/owner-digest.py` as run state, CI, totals, waiting items, then progress, each cut list ending with a line that counts what the attachment adds. Done when: a test with 130 fixture stamps in the week shows the body's first lines unchanged and the cut line.
- [ ] Put the complete progress list in the attachment beside the waiting list. Done when: tests cover progress-only overflow and progress-and-waiting overflow, with every item in the attachment.
- [ ] Commit: `automations: the digest keeps a long progress list`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_owner_digest.py"` passes with both overflow tests among them.

## 3. Digest Delivery Survives a Failed Send

Filed 2026-11-11 from the completion review of T03 §35 (round 2, finding 3, P2). T03 §35 sends once a week; when the send fails (no network on Monday morning), the runner records the failure and the next digest comes a week later, its seven-day window past what was missed. This section remembers the last digest delivered and retries a failed one.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Report from the last delivered digest and retry a failure. Done when: a failed send is retried and its period is reported whole.

- [ ] Record each delivered digest in `build/automations/owner-digest.json` (the period it covered and the provider's message id), written temp-then-replace, and report from the end of the last delivered period rather than a fixed seven days. Done when: a test with a failed week shows the next digest covering both weeks.
- [ ] Retry a definite failure (a refused send, a network error before a response) at most four times a day until it is delivered, through a daily task `office-owner-digest-retry` that does nothing when the last digest was delivered. Done when: tests show a retry after a refusal and none after a delivery, and `tasks.json` and the README agree.
- [ ] Treat an ambiguous outcome (a timeout after the request was sent) as possibly delivered: record it, do not resend that period, and say so in the next digest. Done when: a test shows no second send after a timeout and the note in the following digest.
- [ ] Commit: `automations: a failed digest is sent again`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_owner_digest.py"` and `-p "test_automations.py"` pass with the delivery tests among them.

## Verification

- `python -m unittest discover -s scripts/tests -p "test_owner_digest.py"` passes.
- `python scripts/owner-digest.py --dry-run` prints a digest for this repository and exits 0.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
