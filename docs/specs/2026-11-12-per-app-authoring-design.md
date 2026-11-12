# Per-app authoring order

Recorded 2026-11-12 for D03 T01 §30. The owner said in session that the product's own TODO sections for the shell and for Word should be written once the shell's and Word's inventories are done, and that "it is not necessary to wait for all the inventory to be done". This note finds every way the plan made them wait, says what each link really needs, and sets the new wiring and order. The rule itself is decision 44 of `docs/specs/2026-10-23-campaign-scope-design.md`.

## Context

The product's sections are written by the authoring sections of `todo/03-architecture/TODO-01-tech-stack.md`: §17 writes the platform (the toolkit and the shell), §18 the engines, §19 to §24 the six apps, §25 to §27 interoperability, VBA and release. The inventory of each Microsoft app is captured by two sections of `todo/02-interface/TODO-01-parity-inventory.md` (a ribbon section and a panes and dialogs section), and each app has a surface chapter in `todo/02-interface/TODO-02-interface-spec.md`.

Short names used below: `I§N` is D02 T01 §N (inventory), `S§N` is D02 T02 §N (interface spec), `A§N` is D03 T01 §N (architecture). The inventory sections are I§5 and I§6 (Word), I§7 and I§8 (Excel), I§9 and I§10 (PowerPoint), I§11 and I§12 (Visio), I§13 and I§14 (Project), I§15 and I§16 (Outlook). I§4 is the shell's.

## Paths

Found on 2026-11-12 at commit 8bdb82f by walking the `depends` list that `python scripts/todo-graph.py resolve` prints for each section, from the authoring section back to the first inventory section reached. A§17 had 38 such paths and each of A§19 to A§24 had 80. They are few links repeated, so they are listed by the link every one of them passes through.

Link 1, the coverage report names every app's inventory. I§18 depended on I§6, I§8, I§10, I§12, I§14 and I§16. Every path through a tool section ends here:

```text
A§17 <- I§29 <- I§22 <- I§18 <- I§6, I§8, I§10, I§12, I§14, I§16
A§17 <- A§14 <- I§28 <- I§18 <- (the same six)
A§17 <- A§14 <- I§28 <- I§22 <- I§18 <- (the same six)
A§17 <- A§12 <- A§14 <- I§28 <- (both ways above)
A§19 to A§24 <- A§17 <- (all of the above)
A§19 to A§24 <- A§18 <- A§12 <- A§14 <- I§28 <- (both ways above)
```

Link 2, the mock-up sign-off covers all six apps. S§14 depended on S§7 to S§12, and each chapter on its app's panes and dialogs inventory:

```text
A§19 to A§24 <- S§14 <- S§7 <- I§6
A§19 to A§24 <- S§14 <- S§8 <- I§8
A§19 to A§24 <- S§14 <- S§9 <- I§10
A§19 to A§24 <- S§14 <- S§10 <- I§12
A§19 to A§24 <- S§14 <- S§11 <- I§14
A§19 to A§24 <- S§14 <- S§12 <- I§16
```

Link 3, paths that are right and stay. The toolkit prototype reads the ribbon chapter, which reads Word's ribbon; the Backstage and status bar chapters read Word's panes and dialogs:

```text
A§17 <- A§12 <- A§4, A§8, A§9, A§14, A§15 <- A§2 <- S§4 <- I§5
A§17 <- A§12 <- A§10 <- A§3 <- A§2 <- S§4 <- I§5
A§19 <- S§7 <- S§5, S§6 <- I§6
```

What each link really reads:

| Link | What the later section reads from the earlier one |
| ---- | ------------------------------------------------- |
| I§18 from each app's inventory | Nothing to be built: it counts the records on disk; its tests use fixtures. |
| I§22 from I§18 | The script I§18 writes; its tests use fixtures. |
| I§28 from I§18 and I§22 | The script and the ownership check it extends; its tests use fixtures. |
| I§29 from I§22 | The claim reader; its checkpoint prints Word's Paragraph group (I§5, done). |
| A§14 from I§28 | The disposition field, and the records to set it on: only those captured so far. |
| A§17 from I§29 and I§30 | The layout block and the built-app check its sections carry. |
| A§17 from A§12, A§14 to A§16, A§28 | The decisions a platform section must name files and symbols from. |
| S§14 from S§7 to S§12 | Each app's chapter, to draw that app's mock-up; nothing across apps but the shared shell. |
| A§19 to A§24 from S§14 | The reviewer's sign-off of that one app's mock-up. |
| A§19 to A§24 from A§17, A§18, A§29 | The platform and engine sections to depend on, and the app's budgets. |

So nothing an app's authoring reads comes from another app's inventory. Two sections asked for all six only because they were written as one pass over the suite (I§18's prerequisites and S§14's six mock-ups), and three guarantees were placed where they forced the wait (A§14's dispositions on every app's records, and the two pre-commit hooks in A§13).

## Wiring

The rule (decision 44): an app's sections are authored when that app's inventory, its surface chapter with its signed-off mock-up, and the architecture decisions are done. What must hold for all six apps is proved at the ownership gate, A§13, and held from the first day by tools that treat an app with no inventory yet, or no section yet, as pending.

Tools, each built and proved on the inventories that exist (the shell's and Word's) and on fixtures:

| Section | Depends on, after | What changed in its contract |
| ------- | ----------------- | ---------------------------- |
| I§18 coverage report | I§4, I§5, I§19, I§25 | A baseline-only app is one `pending inventory` row, exit 0. |
| I§18, continued | | `--check` refuses a stale `COVERAGE.md`; the pre-commit hook runs it on inventory commits. |
| I§22 ownership check | I§18 | Three states for an app: pending inventory, pending authoring, enforced. |
| I§22, continued | | Enforced from the stamp of the app's authoring section; `--all` holds every app as enforced. |
| I§22, continued | | Unknown and double claims are refused in every state. |
| I§22, continued | | It installs its own pre-commit hook, moved from A§13. |
| I§28 dispositions | I§18, I§22, I§23 | Unchanged but for the pending rows. |
| I§29 layout tables | I§22 | It installs its own pre-commit hook, moved from A§13. |

"Run again as each inventory lands" is done by the hook, not by a checklist item somewhere: a commit that stages `design/inventory/` with a stale `COVERAGE.md` is refused, so the report can never fall behind the inventory.

Decisions and authoring:

| Section | Depends on, after | What changed in its contract |
| ------- | ----------------- | ---------------------------- |
| A§14 cloud equivalents | A§2, I§28 | Decides each service; sets dispositions on the records that exist. |
| S§7 to S§12 chapters | as before, and S§2 | Each gains its app's mock-up, overlay and sign-off, drawn from S§2. |
| S§14 | S§7 to S§12 | Draws nothing; checks the six mock-ups and sign-offs against each other. |
| A§17 platform | A§12, A§28, I§29, I§30, S§5, S§6, S§13 | Chapters named; A§12 brings A§14 to A§16. |
| A§19 Write | A§17, A§18, A§29, S§7 | S§7 in place of S§14; authored as Phase 4. |
| A§20 to A§24 | A§17, A§18, A§29, own chapter | Own chapter in place of S§14. |
| A§20 to A§24, continued | | Grid S§8, Stage S§9, Flow S§10, Plan S§11, Mail S§12. |
| A§20 to A§24, continued | | Apply A§14 to the app's records; file platform gaps in `todo/04-platform/`. |
| A§13 gate | A§25, A§26, A§27, I§22, S§14 | `--owners --check --all`; no pending app in any check. |

An app is enforced from the stamp of its authoring section, not from its first claim: A§17's platform sections claim Word's Help tab records before A§19 has written Word's other owners, and each authoring section commits its files one at a time, so a first-claim rule would refuse the very commits that author the app. `design/inventory/authoring.json` names each app's authoring section (the shell's is A§17). Until that stamp the hook refuses only an unknown or a doubly owned claim; the authoring section itself runs `--owners --check --all --app <app>` as its last item, so it cannot be stamped with a record unowned.

What the graph cannot show. A prerequisite list says which sections come first, not what an item asks for, and six sections on the path asked, in an item's own words, for something of an inventory captured later. Each is restated around the shell and Word, and the later app's part moves to the section that owns that app:

| Section | Asked for | Now | The later apps' part goes to |
| ------- | --------- | --- | ---------------------------- |
| I§17 shortcuts | All six apps' shortcut files | Word's file and the conflict check | I§8, I§10, I§12, I§14, I§16 |
| S§4 ribbon chapter | The algorithm proved on Excel's Home tab | Proved on Word's Insert tab | S§8 to S§12 |
| S§4, continued | Every app's Simplified Ribbon tabs | Word's tabs | S§8 to S§12 |
| S§5 Backstage chapter | Every app's variants and Options categories | Word's; how an app adds its own | S§8 to S§12 |
| S§6 status bar chapter | Every app's items, Excel's zoom range | The frame, Word's items and range | S§8 to S§12 |
| S§13 accessibility chapter | The F6 cycle order per app | The shell's and Word's | S§8 to S§12 |
| A§6 calculation engine | The function list from Excel's ribbon | The list from the standards | A§20 compares the two |

S§14 confirms that the shared chapters hold all six apps, so the gate still proves the whole. The function list is better for the change: a ribbon gallery shows what Excel chooses to show, while ECMA-376 and [MS-XLSX] define every function a file may hold. The test class holds the part of this a test can read: no open section on the path may name a file under another app's inventory folder.

A§13 takes over, for all six apps and the shell: the ownership check with no pending app, the layout check, a coverage report with no pending app, a disposition on every record of a service A§14 decided, and S§14's check across the mock-ups.

A§20 to A§24 each gain two duties the all-at-once plan did not need. The app's inventory may hold records backed by a cloud service: the section sets their dispositions from A§14's record before it claims anything, and adds their rows to that record. And the app's inventory may hold a control type or a shell region that the platform's sections, written from the shell's and Word's inventories, do not build: the section files each as a new section in `todo/04-platform/` and depends on it, so the platform grows with what each app proves it needs.

## Order

The plan orders rows by phase, then by file path, then by the Order column of the file's table, taking the first row whose prerequisites are placed (`ordered` in `scripts/lib/todo_graph.py`). A row of `todo/03-architecture/` therefore runs ahead of a row of `todo/02-interface/` only when its phase is lower, and no Order column can change that. The order comes from the phase numbers:

| Phase | Rows, after |
| ----- | ----------- |
| 2 | Shell and Word inventory, the tools, the shell, ribbon, Backstage, status bar, Word and accessibility chapters. |
| 3 | The architecture decisions, the foundation plan, the benchmarks, authoring of platform, engines, Write, release. |
| 4 | The platform, the engines and Write are built. |
| 5 | The other five apps: inventory, chapter, authoring, then the gate A§13, then their builds. |
| 6, 7 | Interoperability and VBA; release. Unchanged. |

Moved to Phase 5: I§7 to I§16, S§8 to S§12, S§14, A§20 to A§26 and A§13. Write's domain is authored as Phase 4, and `todo/plan.json` names Phase 4 "Shared platform, engines and Write".

Why Write is built before the other apps are inventoried: the platform, the authoring contract, the layout check and the budget tests are all new, and the first app built on them is where their faults show. Finding them once, on Write, and correcting the contract before it is applied five more times costs less than repairing five authored domains, and the first draft release exists sooner. Within Phase 5 the gate still stands before any of the five later apps is built, as it stood before all six.

What this costs, and what reversing it would cost. The later apps are inventoried against the Office build installed then, which may be newer than the one Word was captured from (`design/inventory/REFERENCE.md` records the build with each capture); the shell inventory is re-checked by each capture's audit. An architecture decision made on Word's and the shell's surface may meet a need only a later app shows (a grid, a drawing canvas, a timeline): the platform gap duty above is how it is met, and a decision it overturns is a new dated record. Reversing the order is a phase number on the moved rows and the prerequisite lists above; reversing it after Write's domain is authored also means changing the phase line of its sections.

## Plan order before and after

Quoted from `todo/implementation-plan.md`, the affected rows in plan order.

Before (commit 8bdb82f):

```text
Phase 2: I§1, I§2, I§21, I§3, I§19, I§20, I§23, I§24, I§25, I§26, I§4, I§5, I§6, I§7, I§8, I§9, I§10, I§11,
         I§12, I§13, I§14, I§15, I§16, I§17, I§18, I§22, I§27, I§28, I§29, I§30, S§1, S§2, S§3, S§4, S§5, S§6,
         S§7, S§8, S§9, S§10, S§11, S§12, S§13, S§14
Phase 3: A§1, A§2, A§3, A§4, A§5, A§6, A§7, A§8, A§9, A§10, A§11, A§14, A§15, A§16, A§12, A§18, A§28, A§17,
         A§27, A§29, A§19, A§20, A§21, A§22, A§23, A§24, A§25, A§26, A§13
```

After:

```text
Phase 2: I§1, I§2, I§21, I§3, I§19, I§20, I§23, I§24, I§25, I§26, I§4, I§5, I§6, I§17, I§18, I§22, I§27, I§28,
         I§29, I§30, S§1, S§2, S§3, S§4, S§5, S§6, S§7, S§13
Phase 3: A§1, A§2, A§3, A§4, A§5, A§6, A§7, A§8, A§9, A§10, A§11, A§14, A§15, A§16, A§12, A§18, A§28, A§17,
         A§27, A§29, A§19
Phase 5: I§7, I§8, I§9, I§10, I§11, I§12, I§13, I§14, I§15, I§16, S§8, S§9, S§10, S§11, S§12, S§14, A§20, A§21,
         A§22, A§23, A§24, A§25, A§26, A§13
```

`python scripts/todo-graph.py query ready` after the change lists, ahead of D02 T01 §7: D02 T01 §6, §17, §18, §27 and §30, D02 T02 §1, and D03 T01 §1, §11 and §29. Before it, D02 T01 §7 stood second among the Phase 2 rows, ahead of all but D02 T01 §6, and D02 T01 §18 was not ready at all.

The standing proof is `PerAppAuthoring` in `scripts/tests/test_todo_graph.py`, which reads this repository's own tree: it fails when the platform or Write reaches another app's inventory, when a later app reaches any but its own and Word's, when an edge an authoring section needs is removed, when a chapter loses the glyph decision, when the gate loses a guarantee, when an open section on the path names a file of another app's inventory, and when a row on the path to the platform or Write falls behind D02 T01 §7 in the plan's order.
