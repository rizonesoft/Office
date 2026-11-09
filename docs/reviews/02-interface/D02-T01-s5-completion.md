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

## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-09T11:09:08Z
- Effort: medium
- Type: adversarial
- Lines: 11
- Digest: af8222316d015060

SECTION: D02 T01 §5
PURPOSE: completion
CONTRACT: sha256:06cacec0203f9d59116186b4fa7fdd811511c1c5df1a028575d948f1db28d6a8

1. **P2 | extend: document-dependent ribbon menus lack capture setup.** The [fixture requirement](D:/GitHub/Office/todo/02-interface/TODO-01-parity-inventory.md:204) enables contextual tabs, but does not establish the states needed to expand every built-in menu. For example, capturing Mailings on a blank document without a recipient source leaves merge-dependent commands unavailable. The [expander](D:/GitHub/Office/scripts/capture-ui.py:1983) attempts expansion without preparing that state; an empty result merely produces a note. Consequently, “capture every menu” can either fail or omit commands despite retaining all required tab hierarchies. Extend the section with capture prerequisites for state-dependent menus, scratch data where necessary, and explicit reconciliation of menus that cannot be expanded. Verify a merge-ready capture and require unresolved expansion failures to prevent completion. §6 owns Mail Merge Recipients’ dialog inventory, not preparation of this ribbon capture; §18’s baseline report does not perform that preparation.

2. **P2 | extend: the completeness contract does not protect KeyTips.** The [validator requirement](D:/GitHub/Office/todo/02-interface/TODO-01-parity-inventory.md:208) enumerates geometry, sizes, hierarchies and behaviour but omits KeyTips, although they are an explicit deliverable. [Capture currently omits the field when access-key extraction returns nothing](D:/GitHub/Office/scripts/capture-ui.py:150), and the schema makes it optional. Removing every `keytip` therefore violates none of the proposed validator requirements, leaving downstream keyboard navigation without its reference sequences. Require reconciliation against observed KeyTips, distinguish controls with no KeyTip from failed reads, and add deletion tests for known tab and control KeyTips. §17 owns keyboard shortcuts, while D02 T02 §4 consumes the inventory to specify KeyTip sequences; neither supplies this missing capture acceptance check.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

### Dispositions

1. `extend`: Extended `D02 T01 §5` checklist items 2, 4 and 6 so `scripts/capture-ui.py` prepares document and session state before expanding state-dependent ribbon menus (including creating a scratch mail-merge recipient CSV `R:\scratch\fixtures\word-recipients.csv` and attaching it via `MailMerge.OpenDataSource` when capturing `Mailings` so merge-dependent menus such as `Insert Merge Field`, `Rules`, `Finish & Merge` and `Start Mail Merge` expand, and seeding selection/clipboard/citation/comment/revision/table state where needed), reconciles any expandable controls that genuinely expose no child items in Word inside `design/inventory/REFERENCE.md`, and requires `validate_word_ribbon(records)` to verify merge-dependent `Mailings` menu expansions (`Insert Merge Field`, `Rules`, `Finish & Merge`) and fail on any unreconciled empty expandable menu/splitButton/gallery or expansion failure note (`capture-ui: expand failed to open a popup`).
2. `extend`: Extended `D02 T01 §5` checklist item 6 and test checkpoint so `scripts/capture-ui.py` and `validate_word_ribbon(records)` enforce KeyTip completeness across all 11 built-in `tab` records, all 10 `contextualTab` records, and every top-level `control` record: distinguishing controls that genuinely expose no UIA `CurrentAccessKey` in Word (reconciled explicitly in `design/inventory/REFERENCE.md` and `validate_word_ribbon`'s allowlist) from failed/missing KeyTip reads, verifying known tab and control KeyTips (`Home` `H`, `Insert` `N`, `Table Design` `JT`, `Bold` `1`), and adding deletion unit tests in `scripts/tests/test_capture_ui.py` proving that removing tab or control `keytip` values fails validation.

## Round 3: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-09T11:15:19Z
- Effort: medium
- Type: adversarial
- Lines: 11
- Digest: 71fddf5ee9528885

SECTION: D02 T01 §5
PURPOSE: completion
CONTRACT: sha256:55bbb8be8e450db51d6efa24ca1f0e8399da74e5a9ed374c5ecab3d4c5ebfb63

1. **P2 | extend: Preserve command availability and selection states.** [TODO-01-parity-inventory.md:206](D:/GitHub/Office/todo/02-interface/TODO-01-parity-inventory.md:206) prepares state to open menus, but does not require recording the conditions that enable commands or determine checked and mixed states. The validator specified at line 208 accepts an inventory without that information; the current record builder also omits it ([capture-ui.py:141](D:/GitHub/Office/scripts/capture-ui.py:141)). For example, captures of Bold with plain, bold and mixed-format selections can produce indistinguishable records, leaving the consumer without the observed state rules. D02 T02 §4 owns the shared command-state model and visual states, but does not own measuring these per-command conditions. Extend this section to record relevant state conditions and observed results, in structured fields or explicit behaviour descriptions, with representative state-change checks.

2. **P2 | extend: Include expanded-menu KeyTips in completeness validation.** [TODO-01-parity-inventory.md:208](D:/GitHub/Office/todo/02-interface/TODO-01-parity-inventory.md:208) explicitly limits KeyTip checks to tabs and top-level controls. Removing every `keytip` from the recursively captured `menuItem` records would satisfy that contract, leaving keyboard routes through nested menus undocumented. D02 T01 §17 owns shortcut chords, while D02 T02 §4 consumes inventory sequences for Alt navigation; neither owns recovering these missing menu KeyTips. Require capture and validation of exposed KeyTips throughout expanded menus, reconcile genuine absences, and add a deletion test for a nested menu item's KeyTip.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

### Dispositions

1. `extend`: Extended `D02 T01 §5` checklist item 6 and test checkpoint so every `control` and `menuItem` `behaviour` sentence records its observed enablement precondition and (for `toggleButton`, `checkBox`, `radioButton`, `gallery` and stateful `menuItem` records) its checked/selected/mixed selection-state rules observed across representative document states (for example plain, bold and mixed-format selections for `Bold`, table/object selection for contextual commands, and attached recipient source for `Mailings` merge commands), and `validate_word_ribbon(records)` verifies representative enablement and toggle/checked/mixed state descriptions with mutation unit tests in `scripts/tests/test_capture_ui.py`.
2. `extend`: Extended `D02 T01 §5` checklist item 6 and test checkpoint so `scripts/capture-ui.py` and `validate_word_ribbon(records)` also enforce `keytip` capture and validation across expanded `menuItem` and nested submenu records (reconciling `menuItem` records such as `galleryItem` or unkeyed entries that genuinely expose no UIA `CurrentAccessKey` in Word inside `design/inventory/REFERENCE.md`), with deletion unit tests in `scripts/tests/test_capture_ui.py` covering nested `menuItem` `keytip` values alongside tab and top-level control `keytip` values.

## Round 4: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-09T11:20:10Z
- Effort: medium
- Type: adversarial
- Lines: 9
- Digest: 9162aa3fee0115e2

SECTION: D02 T01 §5
PURPOSE: completion
CONTRACT: sha256:0731bb8afe173380badd93019ba33771f8fc1b833e88e83ad3c66f3854596c15

1. **P2 | extend: Additional built-in ribbon contexts have no capture owner.** The fixed list at [TODO-01-parity-inventory.md:205](/D:/GitHub/Office/todo/02-interface/TODO-01-parity-inventory.md:205) omits baseline tabs including [Graphics Format](/D:/GitHub/Office/design/inventory/word/baseline.json:3954), [3D Model Format](/D:/GitHub/Office/design/inventory/word/baseline.json:4082), [Outlining](/D:/GitHub/Office/design/inventory/word/baseline.json:1054) and [Background Removal](/D:/GitHub/Office/design/inventory/word/baseline.json:1126). Selecting an SVG or entering background-removal mode is outside the prescribed fixture triggers, so building exactly this plan can omit those command surfaces while satisfying `11 10`. Their availability in the reference build is neither established nor reconciled. §6 owns dialogs and panes; §18 detects missing baseline identifiers but does not capture these tabs. Extend §5 to reconcile all baseline ribbon tabs against their triggering states, capture each available tab with its descendants, and record evidence for unavailable or superseded tabs. Make validation require that reconciled set, with deletion tests for additional contexts.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

### Dispositions

1. `extend`: Extended `D02 T01 §5` intro, checklist items 2, 3, 6 and 9, and the test checkpoint to reconcile all 20 `coreTab` and 23 `contextualTab` tab rows in `design/inventory/word/baseline.json` (while `placement == "backstage"` tabs belong to `D02 T01 §6`): extending `R:\scratch\fixtures\word-contextual.docx` and `scripts/capture-ui.py` to trigger and capture every additional built-in mode and object ribbon tab available in Word `16.0.20527.20150` (`TabGraphicsToolsFormat` via an SVG graphic, `Tab3DModelToolsFormat` via a 3D model, `TabOutlining` via Outline view, `TabBackgroundRemoval` via picture background-removal mode, `TabLearningTools` via Immersive Reader, and any other triggerable baseline tab) with its groups, controls and `behaviour`, recording documented evidence in `design/inventory/REFERENCE.md` for every superseded legacy `.doc` or unavailable/cloud-only baseline tab (`TabChartToolsDesign`, `TabChartToolsLayout`, `TabChartToolsFormat`, `TabDrawingToolsFormatClassic`, `TabPictureToolsFormatClassic`, `TabTextBoxToolsFormat`, `TabWordArtToolsFormat`, `TabDiagramToolsFormatClassic`, `TabOrganizationChartToolsFormat`, `TabInkToolsPens`, `TabAddIns`, `TabSyntex`, `TabConflicts`, `TabBroadcastPresentation`, `TabBlogPost`, `TabBlogInsert`, `TabPrintPreview`), and requiring `validate_word_ribbon(records)` to verify that the union of captured tab/contextualTab `idMso`s and the reconciled unavailable/superseded baseline set equals the full baseline `coreTab` + `contextualTab` set, with deletion unit tests in `scripts/tests/test_capture_ui.py` covering the additional contexts.

## Round 5: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-09T11:26:14Z
- Effort: medium
- Type: adversarial
- Lines: 13
- Digest: 4c9dba86e258ef11

SECTION: D02 T01 §5
PURPOSE: completion
CONTRACT: sha256:9fb185c226279f5c3610021bc57f32283ff855bed2372d1ea17db4d35bd0bdc5

No completion gaps found after challenging tab coverage, state-dependent expansion, nested KeyTips, provenance reconciliation and ambiguous command linking against the supplied contract.

Adjacent responsibilities have named owners: D02 T01 §6 covers non-ribbon surfaces, §17 shortcuts, and §18 baseline coverage; D02 T02 §4 covers ribbon resizing and §13 accessibility. Product performance measurement belongs to D03 T01 §29.

This approves the plan’s completeness, not an implementation or completed capture.

COMPLETE: yes
HIGHEST: none
OVERALL: approve
