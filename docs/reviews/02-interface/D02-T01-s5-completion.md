# Completion review: D02 T01 §5

## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-09T11:03:26Z
- Effort: medium
- Type: adversarial
- Lines: 15
- Digest: 5f2a0fe5d5ab5365

SECTION: D02 T01 §5
PURPOSE: completion
CONTRACT: sha256:66ae2a1eda1185c57c6afff628969eec7751cdae60be9b58ed8af81d6eb4982b

1. **P2 | extend: the checkpoint accepts an empty ribbon structure.** [The checkpoint](D:/GitHub/Office/todo/02-interface/TODO-01-parity-inventory.md:214) requires schema validation and tab counts, without checking their contents. An in-memory counterexample containing 11 `tab` and 10 `contextualTab` records, zero groups and zero controls passed the actual checker, including `--require-behaviour`. Geometry and sizes are also optional, and [behaviour checking](D:/GitHub/Office/scripts/check-inventory.py:582) excludes `menuItem` records. Require section-specific validation of the named tab identities, group/control hierarchy, measured geometry, sizes, expanded entries and behaviour, with deletion tests proving omissions fail. §18 owns baseline comparison, but does not replace these acceptance checks.

2. **P2 | extend: nested ribbon commands have no capture owner.** [The one-level limit](D:/GitHub/Office/todo/02-interface/TODO-01-parity-inventory.md:206) stops before ordinary paths such as Home → Text Effects → Outline → Weight or More Colors. [The baseline](D:/GitHub/Office/design/inventory/word/baseline.json:49) explicitly records these nested controls. The current expander processes only original `control` records, never recursively expanding emitted `menuItem` records ([capture-ui.py:1972](D:/GitHub/Office/scripts/capture-ui.py:1972)). §6 owns dialogs and right-click menus, not these ribbon submenu paths; §18 can report missing identifiers but does not capture their placement or behaviour. Capture nested command-bearing menus recursively, preserving ancestry and order, and verify a nested path.

3. **P2 | extend: equal labels are insufficient evidence for command identity.** [The linking requirement](D:/GitHub/Office/todo/02-interface/TODO-01-parity-inventory.md:210) requires assigning an `idMso` whenever labels match, without defining ambiguous matches. The catalogue already contains three unmatched “Chart” rows ([commands.json:184](D:/GitHub/Office/design/inventory/word/commands.json:184)), and [the importer documents](D:/GitHub/Office/scripts/word-commands.py:13) that repeated names can represent different commands that its source cannot distinguish. Assigning every such row the captured Chart control’s identifier would claim equivalence without evidence; multiple distinct controls sharing a label create the same problem. Require verified disambiguation, retain unresolved candidates in the review list, and test duplicate command names and equal control labels with different identifiers.

4. **P2 | extend: current-build groups excluded by the baseline have no reconciliation step.** [The capture step](D:/GitHub/Office/todo/02-interface/TODO-01-parity-inventory.md:203) assumes the generated ribbon contains the built-in surface. However, [the walker](D:/GitHub/Office/scripts/capture-ui.py:228) diverts a group without recognised baseline identifiers into `ctx.unverified`, outside `ribbon.json`. A legitimate group introduced after the 2024 baseline can therefore disappear while all eleven tabs and their older groups remain. §18 compares baseline identifiers, so it cannot identify this newer group’s omission. Require reviewing the unverified capture output, incorporating confirmed built-in records with `baselineMissing`, and recording exclusions with reasons. Verify that a confirmed newer group cannot remain outside the delivered inventory.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

### Dispositions

1. `extend`: Extended `D02 T01 §5` checklist and test checkpoint to require `validate_word_ribbon(records)` (wired into `scripts/capture-ui.py` and `scripts/check-inventory.py` when checking `design/inventory/word/ribbon.json`) verifying all 11 built-in `tab` identities and all 10 `contextualTab` identities by `idMso`, non-empty `group` and `control` hierarchies under every tab, measured `bounds` and `captureProfile: "fhd-100"` on every record, `size` on every `control`, required expanded `menuItem` chains (including `Borders` and nested submenus) and gallery items with expand control names in `behaviour`, and non-blank `behaviour` on every `contextualTab`, `control` and `menuItem` record, backed by deletion/mutation unit tests in `scripts/tests/test_capture_ui.py`.
2. `extend`: Extended `D02 T01 §5` checklist item 4 to recursively expand nested command-bearing submenus (`menuItem` records with expand-collapse patterns, such as `Home -> Text Effects and Typography -> Outline -> Weight`) in `scripts/capture-ui.py` while preserving parent ancestry and item order, and verify a multi-level nested submenu path in `validate_word_ribbon(records)` and unit tests.
3. `extend`: Extended `D02 T01 §5` checklist item 8 so `scripts/word-commands.py` links a `ListCommands` command without a compact-name `idMso` to a captured ribbon control by `label` only when the command name is unique in `ListCommands` and every captured ribbon control/menuItem with that `label` resolves unambiguously to a single `idMso` (with no `idMso`-less control sharing the label), retaining duplicate command names (such as the three `Chart` rows) and ambiguous control labels in `build/word-commands-unmatched.txt` with unit tests in `scripts/tests/test_word_commands.py`.
4. `extend`: Extended `D02 T01 §5` checklist item 1 and test checkpoint to reconcile `build/capture-ui/word-unverified.json`: promote any confirmed built-in Word group or control on the 11 built-in or 10 contextual tabs that lacks a 2024 baseline identifier into `design/inventory/word/ribbon.json` with `baselineMissing: true`, exclude third-party add-in tabs/groups (such as `Acrobat`) with their exclusion reason recorded in `design/inventory/REFERENCE.md`, and verify in `validate_word_ribbon(records)` and unit tests that confirmed newer built-in groups cannot remain outside `ribbon.json` while add-in tabs are rejected.
