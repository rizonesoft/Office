# Operating mode measurement, 2026-11-10

Which model should lead the campaign, and should it work alone or route work to cheaper models? Measured, not argued (owner, 2026-11-10; scope record decisions 28, 30, 35 and 36).

## Method

Three open sections were each built three ways from commit `402351a37ee1`: by the latest Opus alone, by the latest Fable alone, and by Fable routing work packets to Sonnet and Opus workers (the design of decision 27). That is nine headless Claude Code sessions, each in its own local clone with no remote, under a folder name that does not reveal the arm, with a limit of 40 US dollars and 75 minutes. The session measured ran no gate that counts and no review: the harness then ran `python scripts/todo-graph.py validate`, `python scripts/todo-graph.py plan --check` and `python scripts/run-tests.py` in each clone, and the pinned reviewer reviewed each result blind through `scripts/review-dispatch.py` with one fixed prompt naming only the commit range and the section. Cost is what Claude Code reported per session, subagents included, at list prices. The sections: D00 T03 §32 (small), D00 T03 §29 (medium) and D02 T01 §30 (a new tool written from nothing).

The harness was a scratch script; D00 T03 §36 makes it a command of the repository.

## Measurements

First pass: the build, before any review fix.

| Run | Section | Arm | Cost | Seconds | Gates | Review findings |
| --- | ------- | --- | ---- | ------- | ----- | --------------- |
| run-1 | D00 T03 §32 | Fable alone | $2.05 | 321 | pass | none |
| run-2 | D00 T03 §32 | Opus alone | $1.04 | 303 | pass | none |
| run-3 | D00 T03 §32 | Routed | $2.52 | 826 | pass | none |
| run-4 | D00 T03 §29 | Opus alone | $1.18 | 394 | pass | 1 P1, 0 P2, 0 P3 |
| run-5 | D00 T03 §29 | Routed | $2.31 | 558 | pass | 0 P1, 1 P2, 1 P3 |
| run-6 | D00 T03 §29 | Fable alone | $2.70 | 856 | pass | none |
| run-7 | D02 T01 §30 | Routed | $4.68 | 682 | pass | 1 P1, 0 P2, 2 P3 |
| run-8 | D02 T01 §30 | Fable alone | $3.94 | 499 | pass | 0 P1, 0 P2, 1 P3 |
| run-9 | D02 T01 §30 | Opus alone | $1.59 | 375 | pass | 2 P1, 1 P2, 1 P3 |

In the routed arm (Fable routing packets), the cost per model was:

| Run | Cost per model |
| --- | -------------- |
| run-3 | fable $2.26, sonnet $0.26 |
| run-5 | fable $2.05, sonnet $0.26 |
| run-7 | fable $2.97, sonnet $0.60, opus $1.11 |

| Arm | Total cost, three sections |
| --- | -------------------------- |
| Opus alone | $3.82 |
| Fable alone | $8.69 |
| Routed (Fable routing packets) | $9.51 |

The serious findings were read and are real defects: an empty file with a byte order mark passing an emptiness check (both the Opus and the packet-routing build of §29), and a layout check that could approve the wrong part of the interface (both the Opus and the packet-routing build of D02 T01 §30).

## Findings

- Routing packets cost the most and was not the cleanest. Fable spent 2.26, 2.05 and 2.97 dollars coordinating the three sections; on the smallest that was more than building the section alone (2.05), and on the other two less (2.70 and 3.94), but the workers' cost on top made the routed run dearer than Fable alone on the first and third.
- Opus alone cost about half of Fable alone or less on every section (51, 44 and 40 percent), and 44 percent in total.
- Opus's first-pass quality fell as the work got harder: no finding on the small section, one `P1` on the medium one, two `P1` and a `P2` on the new tool. Fable alone had one `P3` in three sections.
- What the first pass does not show is the cost to reach an approved review, which the last section of this record measures.

## Decision

Owner, 2026-11-10 (scope record decision 35): one long session on the latest Opus leads and hands each section's build and each round of review fixes to an Opus writer agent in a fresh context; Sonnet agents only read; Haiku is retired; Fable is on call, taking a section over after review round 8 with a `P1` or `P2` still open or when a finding reported fixed returns, and building the architecture decision records.

Limits of this measurement: three sections, all Python tooling of this repository, one run per arm and section, and the chosen shape (an Opus lead above an Opus writer) was not itself one of the three arms. D00 T03 §37 measures again, to the approved review and with that shape as an arm, every 300 stamped sections and whenever a lead alias resolves to a new model.

## Cost to an approved review

Each result whose first review had a `P1` or `P2` was fixed by its own arm in its own clone, gated by the harness and reviewed blind again, until a review had no `P1` or `P2` (a `P3` alone counts as approved, as the stamp's severity stop does).

| Run | Section | Arm | Build | Fix rounds | Total | Reviews | End |
| --- | ------- | --- | ----- | ---------- | ----- | ------- | --- |
| run-1 | D00 T03 §32 | Fable alone | $2.05 | none | $2.05 | 1 | approved |
| run-2 | D00 T03 §32 | Opus alone | $1.04 | none | $1.04 | 1 | approved |
| run-3 | D00 T03 §32 | Routed | $2.52 | none | $2.52 | 1 | approved |
| run-4 | D00 T03 §29 | Opus alone | $1.18 | $0.80 | $1.98 | 2 | approved |
| run-5 | D00 T03 §29 | Routed | $2.31 | $1.94 | $4.25 | 2 | approved |
| run-6 | D00 T03 §29 | Fable alone | $2.70 | none | $2.70 | 1 | approved |
| run-7 | D02 T01 §30 | Routed | $4.68 | $3.90, $3.83, $3.78 | $16.20 | 4 | stopped, P2 open |
| run-8 | D02 T01 §30 | Fable alone | $3.94 | none | $3.94 | 1 | approved |
| run-9 | D02 T01 §30 | Opus alone | $1.59 | $1.34, $0.80 | $3.74 | 3 | approved |

| Arm | Cost to approval, three sections | Reviews |
| --- | -------------------------------- | ------- |
| Opus alone | $6.76 | 6 |
| Fable alone | $8.69 | 3 |
| Routed (Fable routing packets) | $22.97, one section not approved | 7 |

- Opus alone reached approval on all three sections for 78 percent of what Fable alone cost, with twice as many reviews (6 against 3).
- The gap closes with difficulty. On the new tool Opus needed two fix rounds and ended at 3.74 dollars against Fable's 3.94 with none: 5 percent apart, and Opus took three reviews to Fable's one. On work harder than this, Fable alone would likely be the cheaper way to an approved review; this measurement has no section that hard, so that is an inference and not a result.
- Routing packets was stopped by hand on the new tool after three fix rounds at about 3.80 dollars each with a `P2` still open (run-7), once it was clear the arm had lost; its total is therefore a lower bound.
- The reviewer's time is not in these costs. Each review is a Codex run of several minutes, so Opus's extra reviews cost wall-clock time that the dollar figures do not show.

The verdict under the rule of decision 36 (lowest cost to an approved review among the arms that got there): Opus alone. It supports the owner's choice of an Opus lead and writer, and the takeover rule: the harder the section, the more the stronger model is worth, which is where Fable is called.

The raw results are `docs/experiments/operating-mode-2026-11-10.json`. The nine clones were deleted after this record was written.
