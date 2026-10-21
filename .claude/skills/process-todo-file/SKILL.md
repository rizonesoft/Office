---
name: process-todo-file
description: Close out a TODO file whose sections are all shipped. Sweep for loose ends, run the file-level Verification block, reconcile deferrals, update the indexes, and confirm status done. Use when every Implementation Order row is [x], or when asked to close a whole TODO file.
---

# Process TODO File

The last pass over a finished TODO. Its job is to catch what section-by-section work cannot see: the loose ends between sections, the deferrals nobody picked up, and the gap between "every row is `[x]`" and "this actually works end to end".

Do not use it to force a file closed. If sections remain open, they get implemented or explicitly deferred with owners: not swept.

## Workflow

### 1. Confirm the file is actually exhausted

```powershell
python scripts/todo-graph.py validate
python scripts/todo-graph.py plan --check
```

Every row `[x]`, every `[x]` covered by a `Verified:` stamp with a matching receipt (the validator refuses otherwise), and the frontmatter already reads `status: done` (the last stamp sets it; a mismatch refuses validation). Fix any refusal first.

### 2. Run the file-level Verification block

The `## Verification` section is not decoration. Run every item in it and record the real output. This is the only place the file is checked as a whole, and it is where integration gaps surface. For a code TODO that means the full suite, not the filtered runs individual sections used: the complete test run, the CLI corpus pass where the file names one, and a full build where the file's sections are build-facing. Each item executed, none trimmed.

### 3. Loose-end sweep

Read the whole file with fresh eyes and check:

- **Stubs and TODOs in the code.** Search the touched paths for `TODO`, `FIXME` and not-implemented markers introduced during the work. Each is finished now or gets an owning section through `add-todo`.
- **Partial items.** Any checklist item ticked when only part shipped. In a stamped section that is an unearned stamp: run `review-todo-section` in audit stance, which files the repair and reopens the section through `todo-graph.py unstamp` (its consumers become suspect); a stamped checklist is never rewritten by hand. Work beyond the item's own `Done when:` (new granularity) becomes a new section instead.
- **Orphaned deferrals.** `python scripts/todo-graph.py query deferred`: every `Deferred:` line names a live, still-open owner (a shipped owner already refuses validation, so what remains is confirming the description is still true).
- **Integration reality.** The feature is reachable from where its user looks for it: its menu, page or panel, command entry, keyboard shortcut, CLI verb. A control whose Job is a write and that only displays is not done. A setting nothing reads is not done.
- **Adjacency honesty.** `python scripts/todo-graph.py query adjacency`: every `applicable` key has its owning section shipped or still tracked, and every `not-applicable` reason still holds.

### 4. Reconcile the frozen contract

If the file is `frozen: true`: every `**Freeze check:**` ran and passed with the result in a receipt, no frozen behavior moved (or the operator approval is recorded in the section), and the golden fixtures are committed under `tests/corpus/`, not left in scratch.

### 5. Update the indexes

- Move the file's row in the domain `INDEX.md` from the TODOs table to its Completed table, with the completion date.
- Move its line in `todo/TODO-00-INDEX.md` from Active TODOs to Completed TODOs. The filename must stay verbatim in both files (index coverage is validated).
- Where the work is now better documented elsewhere, link that document from the index line rather than deleting section detail. The shipped TODO is the record of how it was built.
- `python scripts/todo-graph.py plan --sync`, then `validate` and `plan --check` again.

### 6. Commit

```text
<domain>: complete TODO-NN -- <one-line summary of what now works>

<full-suite evidence>
<deferrals carried forward, with their owners>
```

### 7. Report

What now works in the user's terms, what was deferred and who owns it, anything the sweep turned into new work, and any gate that did not run with the reason.

## Guardrails

- Do not close a file with open sections. Implement or explicitly defer with an owner.
- Do not close a file whose deferrals point nowhere.
- Do not claim the Verification block passed without running it: quote the output.
- Do not delete section detail on closure, and do not rewrite stamped checklists.
