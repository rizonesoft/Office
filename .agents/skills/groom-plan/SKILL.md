---
name: groom-plan
description: Harden the todo tree in Antigravity for a weaker executor with a sequence check, drift sweep, gap scan and complete-feature pass, without ticking boxes or starting a run. Use before a long run, or when the plan feels stale.
---

# Groom Plan

Hardening the tree so a weaker executor can run it. Grooming adds prerequisites and fills gaps; it never ticks a box, never stamps, and never starts a campaign.

## Workflow

### 1. Sequence check

For every dependency edge (section `Depends On` and file `depends_on`), confirm the prerequisite sits no later than its consumer: phase first, then row order in the generated plan. The validator already refuses a prerequisite in a later phase and any cycle; grooming catches the legal-but-hostile orders. Where an edge points later in practice:

- Prefer adding or splitting the prerequisite as a small new section ahead of the consumer, with a dated note.
- Never renumber a section or reuse a number: addresses are permanent.
- Record each fix with `**Corrected YYYY-MM-DD:**` or `**Groomed YYYY-MM-DD:**`, saying what it said before.

Run `python scripts/todo-graph.py validate` after every structural edit.

### 2. Drift sweep and brownfield reconciliation

Walk every open section's concrete claims against today's repository and governing documents: files, classes, paths, counts, versions, engine and SDK details, and `design/SPEC.md` section numbers. Correct drift in place with dated notes, without building anything. Pay special attention to:

- "Nothing exists yet" claims that are no longer true: update `> **Current state:**` with measured paths and behavior.
- Micro-steps already 100% implemented in the codebase: verify their `Done when:` and `Cheaper substitute:` against `file:line` and tests, then tick them with the commit SHA or `file:line` that shipped them.
- Half-implemented items in the codebase (for example, UI exists with hardcoded hex colors, or write path exists without atomic replace or refusal tests): keep `[ ]` and rewrite the micro-steps to target the exact remaining gaps rather than re-planning what already works.
- Counts and versions quoted confidently (these age fastest).
- Deferrals whose descriptions drifted while their owners stayed open (`python scripts/todo-graph.py query deferred`).
- XREFs whose targets shipped or moved.
- Current state blocks older than the last shipped section in their domain.

### 3. Gap scan and 100% complete plan audit

Read the plan as the user will use the finished product, domain by domain, against `design/SPEC.md` (every screen, dialog and state) and the foundation plan's milestone "Done when" column. Running `process-plan` to completion must produce a 100% complete, shippable product with zero unowned surfaces, controls, settings, refusal/error paths, undo/reverse paths, or persistence read-backs. Compare the union of (`existing working codebase` + `open TODO sections`) against the spec: anything already 100% working in baseline code belongs in `Current state:`, and every remaining gap gets filed via `add-todo` (evidence, owner, dependency) and synced into the plan. Never cap operator-requested planning and never silently drop scope.

Check the Adjacency declarations while here (`python scripts/todo-graph.py query adjacency`): an `applicable` with no owning section, or a `not-applicable` whose reason no longer holds, becomes work or a corrected declaration.

### 4. Complete-feature and micro-step granularity pass

For every user-facing surface in the plan, confirm the feature is whole against its SPEC screenshot: every control, menu item, dialog and state is working in a named section or deferred to a named, resolving section. For every engine surface, confirm the reverse and the failure path: cancel, abort, wrong password, damaged file, partial write. File what is missing; do not redesign what exists.

Audit section and checklist granularity across every open file (and upgrade legacy or incomplete TODO files to the current schema):
- Split coarse umbrella sections (bundling multiple subsystems, dialogs, or workflows into one section) into small, single-responsibility sections with explicit `Depends On` edges.
- Shorten any `Deliverable` cell, `## N. <Title>` heading, or index `Scope` cell over 88 characters to a concise noun phrase (`<= 88` chars) so raw Markdown table rows stay under 140 characters (with description cells <= 88 characters) and never wrap in raw `.md` view; move parenthetical symbol lists and file paths into the section body and checklist.
- Expand any 1-bullet or 2-bullet summary checklist into concrete buildable micro-steps (typically 4 to 15 micro-steps per section, max 30, ending with `Commit:`). Every non-Commit item must follow the five-part rule: one action, named path/symbol in backticks, `Done when:` observable end state in the same bullet, `Cheaper substitute:` on UI and write items, and source citation.
- Never rewrite a `[x]` section's checklist; if a shipped `[x]` section was coarse or incomplete, leave it intact and add a new open `## N.` section in numerical order for the missing pieces.

### 5. Report and commit

Write the groom record: what was sequenced, what drifted and was corrected, what coarse sections or summary checklists were decomposed into micro-steps, what gaps were filed and where they landed, and what `query stats` now says. Commit as `todo: groom <scope> (<date>)` after a final `validate`, `plan --sync` and `plan --check`.

## Guardrails

- Do not tick a box or write a stamp. Grooming never ships.
- Do not start a run. Grooming prepares one.
- Do not leave coarse umbrella sections, summary checkboxes, or unowned SPEC controls in the plan.
- Do not redesign sections. Harden them.
- Do not rewrite a `[x]` section's checklist. That is the contract its stamp covers.
- Do not leave the tree unvalidated.
