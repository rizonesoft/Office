---
name: add-todo
description: Front door for new work in Codex. Search the todo/ tree for an existing home first, then route to an existing section, a new section, or a whole new file via create-todo. Use whenever work needs capturing.
---

# Add TODO

New work enters through here. The failure this skill exists to prevent is the near-duplicate TODO in a second domain, which is worse than no entry: two owners, neither complete.

## Workflow

### 1. Search before filing

Search the tree for a home the work already has:

```powershell
Select-String -Path todo\*\TODO-*.md -Pattern "<keywords>" | Select-Object -First 30
python scripts/todo-graph.py query deferred
```

Read the candidates. A home exists when a section's scope already covers the work, even if its checklist does not name it yet. Check `todo/findings.md` too: a finding with `file:line` that matches is scheduled by writing a section and striking the finding with its new `DNN TNN §N`.

### 2. Route to one of four outcomes

| Outcome | When | Do this |
| ------- | ---- | ------- |
| Already covered | A section owns it | Point at the section. File nothing. |
| Fits a section | Open section covers it | Add a micro-step or extend body (never edit `[x]`). |
| Needs a section | New work inside a file | Add `## N.` in order, update table, sync plan. |
| Needs a file | Subject no file owns | Delegate to `create-todo`. |

### 3. New sections are born complete and granular

A new section carries everything the format requires from birth (`todo/README.md`): a short noun-phrase heading (`## N. <Title>`) and matching `Deliverable` cell of at most 88 characters so raw Markdown tables never wrap, context paragraph, `**Phase:**`, `**Needs:**`, `**Surface:**`, a numbered `**Build order:**` whose every step has an observable `Done when:`, a granular micro-step checklist (typically 4 to 15 concrete micro-steps, max 30, never a 1-bullet summary stub) ending in `Commit:`, and a runnable `**Test checkpoint:**` in backticks. Every non-Commit micro-step follows the five-part rule: one action, a named path or symbol in backticks, `Done when:` observable end state in the same bullet, `Cheaper substitute:` on UI and write items, and a source citation when copying behavior. Split multi-subsystem or multi-dialog work into separate small, single-responsibility sections rather than bundling them into one umbrella section. A surface section also carries Fidelity (naming the `design/SPEC.md` section and screenshot), Job, Treatment and Chrome, and accounts for 100% of controls on the surface (working or deferred to a resolving section). A section in a `frozen: true` file carries a `**Freeze check:**`. A section filed as a one-line stub is a plan defect, not a head start.

Plan the full lifecycle so the development plan stays 100% complete: include refusal/error/recovery paths, undo/reverse paths, settings consumers, and atomic write plus read-back steps. Never cap operator-requested planning and never silently drop scope.

Give it a dependency edge, not a wish. If it must wait on another section, say so in `Depends On`; if it truly stands alone, `--`. A prerequisite may not sit in a later phase than its consumer.

### 4. Wire and verify

- Point at related sections with `-> XREF:` in Inputs and point back from each target file. One-sided XREFs refuse validation.
- A deferral that hands work to this section names it as owner (`-> XREF: DNN TNN §N`), so closure is detectable.
- Then prove the tree still holds:

```powershell
python scripts/todo-graph.py validate
python scripts/todo-graph.py plan --sync
python scripts/todo-graph.py plan --check
```

### 5. Commit and report

Commit as `todo: file <what> in <ref>`. Report the section address (`DNN TNN §N`), why that home won over the alternatives searched, and what `query stats` now says.

## Guardrails

- Do not file work into a `[x]` section. New granularity on shipped work is a new section.
- Do not write coarse umbrella sections or summary checkboxes; decompose into small single-responsibility sections and five-part micro-steps.
- Do not write a cross-TODO reference without a section. `D03 T01` alone is not a dependency.
- Do not leave the plan unsynced. The generated plan is the only plan.
- Do not file the same real-world thing twice. Search first.
