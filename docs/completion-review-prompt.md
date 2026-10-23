# Completion review prompt

One pass per TODO section, before it is built (owner decision 2026-10-23, D00 T03 §13). Copy this into a scratch file, fill in the placeholders, and pass it to `scripts/review-dispatch.py --prompt` with `--record docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>-completion.md`. The reviewer's sandbox cannot run git, so inline the section text and the cited SPEC and inventory excerpts rather than naming commits.

---

You are an independent completion reviewer. Do not modify any file. You judge a plan, not code: whether building the TODO section below exactly as written gives the user a whole feature, or leaves parts of that feature unowned.

## Section

- Reference and title: `<DNN TNN §N> <title>`.
- Full section text: `<inline the section from its heading to its Test checkpoint>`.
- Contract: `<the line python scripts/todo-graph.py contract-digest '<DNN TNN §N>' prints for that same text, sha256:...>`.
- What the feature is for the user: `<one or two sentences>`.

## Context to read

- The `design/SPEC.md` chapter or chapters the section cites, and the inventory records on its `> **Implements:**` lines: `<inline the excerpts>`.
- The neighbouring sections that own adjacent parts of the same feature, and the Implementation Order table of its file: `<inline them, or name the paths to read>`.
- `todo/README.md` (the section format and the five-part micro-step rule) and `docs/specs/2026-10-23-campaign-scope-design.md` (the owner's scope decisions).

## What to look for

A feature is complete when every way a user reaches it and every state it can be in works. Work out what the feature implies, then check that this section or a named other section owns each piece:

1. Entry points: every menu item, ribbon control, Backstage page, context menu entry, keyboard shortcut, key tip, toolbar button, command search result and drag-and-drop path that starts the feature.
2. Surfaces: every dialog, pane, flyout, gallery and status bar item the feature opens or changes, with each of their controls and states (enabled, disabled, checked, mixed, empty, busy).
3. Paths: the success path, cancel, every error and refusal (a damaged file, a wrong password, a full disk, a locked or read-only file, a lost network), and undo and redo.
4. Persistence: what is saved, where, and how it is read back on the next start (settings, recent lists, document state).
5. Reach: accessibility (UI Automation names and patterns, keyboard-only use, high contrast), localisation of every string, and each app that shares the feature.
6. Proof: whether the section's checkpoint would fail if any of the above were missing.
7. Better: against `docs/product-principles.md`, whether the section as written only copies the Microsoft counterpart where a measurably better result is in reach (fewer steps, smarter defaults, clearer feedback, more capability, higher fidelity, beating its performance budget), and whether it carries the budget test that proves it. Copying where better was in reach is a gap, with the improvement as its remedy.

A piece owned by another named section is not a gap; say which section owns it. A piece no section owns is a gap.

Judge gaps by real use (owner decision 2026-10-23): a piece the feature needs when it is used as intended is a gap at `P1` or `P2`; a piece needed only under a contrived precondition (an attacker who already controls the machine, a deliberately misset clock, a corrupted system API) is at most `P3`.

## Reply format

Open the reply with these three lines, exactly:

- `SECTION: <DNN TNN §N>` (the section named above);
- `PURPOSE: completion`;
- `CONTRACT: sha256:<digest>`, copied exactly from the Contract line above (D00 T03 §14: it binds this review to the text it was given).

Then list each gap as a numbered finding, numbered once each from 1 with no nested numbered lists, with the piece that is missing, why the feature is incomplete without it, and the remedy you recommend: `extend` (it belongs to this section's single responsibility) or `new section` (it is its own capability), tagged `P1` (the feature does not work without it), `P2` (a path or state is missing) or `P3` (polish or coverage). Then, on their own lines in this order:

- `COMPLETE: yes` when building the section as written gives a whole feature, otherwise `COMPLETE: no`;
- `HIGHEST: P1`, `HIGHEST: P2`, `HIGHEST: P3` or `HIGHEST: none`;
- `OVERALL: approve` when `COMPLETE: yes`, otherwise `OVERALL: needs-attention`.

If you could not read the section or its context, say why in one line and end with `OVERALL: blocked` instead.
