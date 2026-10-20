---
schema_version: 1
id: parity-inventory
domain: 02-interface
status: active
title: "TODO-01 -- Microsoft 365 Parity Inventory"
---

# TODO-01 -- Microsoft 365 Parity Inventory

> **Goal:** "Feature by feature, in the same place" becomes measurable. A machine-readable inventory in `design/inventory/` lists every visible element of the six reference Microsoft 365 apps (tabs, groups, commands in order, control type and size, contextual tabs, Backstage pages, panes, status bar items, views, dialogs reachable from the ribbon, and keyboard shortcuts) with its position captured through UI Automation at a fixed window size. Every later interface and application section cites inventory ids, and the coverage report shows how much of the inventory the suite implements.

> **Current state:** Measured 2026-10-20. No inventory, schema or capture tool exists. The operator's Windows 11 Pro host has Microsoft 365 Apps build 16.0.20430.20182, Current Channel, x64, licensed as O365BusinessRetail, ProjectProRetail and VisioProRetail, with Word, Excel, PowerPoint, Visio, Project and Outlook all installed; the operator also uses Word interactively, so captures must never touch windows they did not open. No UI Automation Python package is installed yet. Microsoft publishes every control identifier per app in its MIT-licensed Office Fluent UI control identifier lists (last updated 2024-03-18), used as the completeness baseline (§19). **Rule, 2026-10-20 (owner):** the inventory holds facts only (control names, positions, types, ids, shortcuts) with behaviour in our own words; no Microsoft text (ScreenTip descriptions, help prose) and no Microsoft links anywhere in the repository (§21). The owner decided on 2026-10-20 to inventory both the Classic and the Simplified Ribbon from the start, and to use classic Outlook as the Mail reference (§2).

## Inputs

- A licensed Microsoft 365 Apps install on the operator's Windows host (Word, Excel, PowerPoint, Outlook) plus Visio Plan 2 and Project Plan 3 or Project Professional: the capture source.
- The reference apps themselves: each behaviour sentence is written in our own words from using the control. Microsoft's help pages may be read to learn a feature, but none of their text or links is stored (**Corrected 2026-10-20:** said they were the cited source per element).
- Windows UI Automation (UIA) tree: names, control types, automation ids and bounding rectangles of ribbon elements. ScreenTip descriptions are Microsoft prose and are not recorded (**Corrected 2026-10-20**).
- Office Fluent UI control identifier lists (`<app>controls.xlsx`, Microsoft 365 Current Channel, MIT): every tab, group and control with its `idMso` and type, including controls not shown by default. The completeness baseline that the live capture is checked against.
- Word's built-in `ListCommands` command (through COM, `Application.ListCommands(True)`): every Word command with its keyboard assignment, including commands with no ribbon button.
- Legal boundary: the inventory records names, positions and behaviour as text and numbers only. It never commits Microsoft icons, screenshots or artwork; screenshots stay in `R:\scratch`.
- -> XREF: D02 T02 §3 -- the shell layout spec is measured from the shell chrome inventory in §4
- -> XREF: D03 T01 §13 -- application TODO domains are authored from this inventory, one section per inventory group

## Outcome

- `design/inventory/schema.json` defines an element record; `python scripts/check-inventory.py` validates every inventory file against it and refuses duplicates, orphans and missing sources.
- `design/inventory/<app>/` holds `ribbon.json`, `backstage.json`, `panes.json`, `statusbar.json`, `dialogs.json` and `shortcuts.json` for each of `word`, `excel`, `powerpoint`, `visio`, `project` and `outlook`, plus `design/inventory/shell/chrome.json`.
- `python scripts/inventory-report.py` prints element counts per app and kind, and writes `design/inventory/COVERAGE.md`.

**Adjacency:** all=not-applicable (a reference catalogue of Microsoft's surfaces; it creates no user records, settings or permissions in the product)

**Adjacency rationale:** The inventory is a measuring stick for later work. Every list, document, settings, reporting, notifications, permissions, audit, exchange and reverse surface it records is owned by the application section that implements the inventoried element.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Inventory schema and checker | D00 T01 §1 | [x] |
| 2 | §2 | Reference build and capture configuration | -- | [ ] |
| 3 | §3 | UI Automation capture tool | §1, §2, §21 | [ ] |
| 4 | §4 | Shared shell chrome inventory | §3 | [ ] |
| 5 | §5 | Word ribbon and contextual tabs inventory | §3, §19 | [ ] |
| 6 | §6 | Word Backstage, panes, status bar and dialogs inventory | §5 | [ ] |
| 7 | §7 | Excel ribbon and contextual tabs inventory | §3, §19 | [ ] |
| 8 | §8 | Excel Backstage, formula bar, panes and dialogs inventory | §7 | [ ] |
| 9 | §9 | PowerPoint ribbon and contextual tabs inventory | §3, §19 | [ ] |
| 10 | §10 | PowerPoint Backstage, views, panes and dialogs inventory | §9 | [ ] |
| 11 | §11 | Visio ribbon and contextual tabs inventory | §3, §19 | [ ] |
| 12 | §12 | Visio Backstage, shapes pane and dialogs inventory | §11 | [ ] |
| 13 | §13 | Project ribbon and contextual tabs inventory | §3, §19 | [ ] |
| 14 | §14 | Project views, Backstage, panes and dialogs inventory | §13 | [ ] |
| 15 | §15 | Outlook module and item window ribbons inventory | §3, §19 | [ ] |
| 16 | §16 | Outlook modules, panes, views and dialogs inventory | §15 | [ ] |
| 17 | §17 | Keyboard shortcut inventory for six apps | §1, §20 | [ ] |
| 18 | §18 | Inventory coverage report | §4, §6, §8, §10, §12, §14, §16, §17, §19 | [ ] |
| 19 | §19 | Microsoft control identifier baseline import | §1, §21 | [x] |
| 20 | §20 | Word command catalogue from ListCommands | §1, §2, §21 | [ ] |
| 21 | §21 | Microsoft-free inventory model | §1 | [x] |

## 1. Inventory Schema and Checker

> **Started:** 2026-10-20T00:00:18Z

Every inventoried element is one JSON record with a stable dotted id (`word.home.font.bold`), so specs, TODO sections and tests can cite it. The checker keeps the inventory consistent as hundreds of records are added.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Write `design/inventory/schema.json` (JSON Schema draft 2020-12). Done when: it defines every field listed in the micro-steps.
2. Write `scripts/check-inventory.py` and its tests. Done when: the tests pass and fail when a rule is disabled.

- [x] Define the element record in `design/inventory/schema.json`: `id`, `app`, `kind` (tab, contextualTab, group, control, backstagePage, pane, statusItem, view, region, dialog, dialogTab, setting, contextMenu, menuItem, miniToolbar, shortcut, command), `label`, `parent`, `order`; files are JSON arrays of records. **Corrected 2026-10-20:** the kind list lacked the records §6 to §16 and §20 write (context menus, menu items, mini toolbar, view regions, dialog tabs, Options settings, Word commands). Done when: the schema validates a hand-written example record. Cheaper substitute: free-text Markdown tables that no script can read.
- [x] Add control fields to `design/inventory/schema.json`: `controlType` (button, splitButton, dropdown, gallery, galleryItem, comboBox, checkBox, radioButton, toggleButton, spinner, dialogLauncher, menu, dynamicMenu, colorPicker, editBox, label, separator, box, buttonGroup, listBox, slider), **Corrected 2026-10-20:** added the types Microsoft's control lists (§19) and dialogs use; `size` (large, medium, small), `keytip`, `shortcut`. Done when: a split button example validates and an unknown `controlType` fails. Cheaper substitute: a single `type` string with no enumeration.
- [x] Add position fields to `design/inventory/schema.json`: `bounds` (`x`, `y`, `width`, `height` in pixels at 100 percent scaling, relative to the window client area) and `captureProfile`. Done when: a record without `captureProfile` but with `bounds` fails. Cheaper substitute: positions described in words.
- [x] Add behaviour fields to `design/inventory/schema.json`: `behaviour` (one sentence), `screentip` (captured title and description), `idMso` (Microsoft control identifier where one exists), `source` (URL), `capturedFrom` (build string from §2). Done when: a control record without `source` fails, and with `--require-behaviour` a control without `behaviour` or with a non-web `source` fails. **Corrected 2026-10-20:** a raw capture cites itself (`uia:<build>`), so requiring a web source on every control would fail §3's own checkpoint; §5 to §16 run the checker with `--require-behaviour` once behaviour is written. Cheaper substitute: behaviour from memory with no citation.
- [x] Write `scripts/check-inventory.py` validating every `design/inventory/**/*.json` file against the schema with a standard library validator for the subset used. Done when: `python scripts/check-inventory.py` exits 0 on the example and 1 on each refusal fixture. Cheaper substitute: adding a third-party dependency for one script.
- [x] Add duplicate-id and orphan-parent checks to `scripts/check-inventory.py`. Done when: a record whose `parent` names no record fails with `orphan`, and checking one file resolves parents found anywhere under `design/inventory/`. Cheaper substitute: checking ids within one file only.
- [x] Write `scripts/tests/test_check_inventory.py` covering each rule. Done when: `python -m unittest discover -s scripts/tests -p "test_check_inventory.py"` passes and fails when any rule is disabled.
- [x] Commit: `inventory: add element schema and checker`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_check_inventory.py"` reports at least 6 tests and `OK`.

> **Verified:** 2026-10-20 | §1 | 602f9dd43adfd329c5b03acf2eeb8e0528a0ec6c
> **Review:** `docs/reviews/d02-t01-s1.json`

## 2. Reference Build and Capture Configuration

> **Started:** 2026-10-20T02:46:15Z

Positions only mean something against one fixed configuration. This section records the exact reference: product versions, update channel, display settings and the two owner choices that change the layout (Classic versus Simplified Ribbon; classic Outlook versus the new Outlook for Windows). Decision, 2026-10-20 (owner): both the Classic and the Simplified Ribbon are inventoried and built from the start, with Office's switch between them; the Outlook reference is classic Outlook; Visio and Project are installed on the operator's host.

**Phase:** 2
**Needs:** office, windows-host
**Surface:** no

**Build order:**

1. Confirm the decision line in this section matches `## Layout choices`. Done when: both name the same choices.
2. Write `design/inventory/REFERENCE.md`. Done when: the design-doc checker passes with the required headings.

- [x] Record the version and build of each app from File, Account, About into `design/inventory/REFERENCE.md` under `## Builds`. **Corrected 2026-10-20:** read from the Click-to-Run configuration and each program's file version, the values the Account page reports, so no live app is opened for it; the Account page's month-coded feature version is not stored outside the UI and is not needed to pin the build. Done when: six rows carry version, build and channel. Cheaper substitute: "latest Microsoft 365".
- [x] Record the capture profile in `design/inventory/REFERENCE.md` under `## Capture profile`: display 1920x1080 at 100 percent scaling, window maximised, Office theme `White`, language `en-US`, ribbon always shown. Done when: the profile has an id that `captureProfile` fields reference. Cheaper substitute: capturing at whatever resolution the host uses.
- [x] Record the 2026-10-20 layout choices (Classic and Simplified Ribbon both, classic Outlook) in `design/inventory/REFERENCE.md` under `## Layout choices`, with the steps that switch each reference app between the two ribbons. **Corrected 2026-10-20:** Word build 20430 offers no switch (its Ribbon Display Options were read live, without changing a setting), the baseline lists no toggle for Excel, PowerPoint, Visio or Project, and classic Outlook is not started unattended because starting it sends the Outbox; each app's ribbon section (§5, §7, §9, §11, §13, §15) records whether its build offers the switch and the steps, and this section records what was observed. Done when: both choices carry the owner's date and the switch steps. Cheaper substitute: capturing one ribbon layout and inferring the other.
- [x] Record which apps are unlicensed on the host and how they will be licensed (trial or subscription) in `design/inventory/REFERENCE.md` under `## Licensing`. Done when: Visio and Project each show `installed` or a dated plan. Cheaper substitute: inventorying Visio and Project from web screenshots.
- [ ] Commit: `inventory: record reference build and capture profile`

**Test checkpoint:** `python scripts/check-design-doc.py design/inventory/REFERENCE.md --require Builds --require "Capture profile" --require "Layout choices" --require Licensing` exits 0.

## 3. UI Automation Capture Tool

Hand-transcribing thousands of controls is slow and error-prone. A capture tool walks the UIA tree of a running app window and writes draft inventory records with names, control types, automation ids and bounding rectangles; a person then adds behaviour and sources.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Write `scripts/capture-ui.py` using `uiautomation` or `pywinauto` (UIA backend), installed per AGENTS.md tool rules. Done when: it dumps the Home tab of Word to JSON records that pass `scripts/check-inventory.py`.
2. Add tab switching and contextual tab triggering. Done when: one run captures every built-in tab of the open app.

- [ ] Add `--launch` in `scripts/capture-ui.py` that starts the reference app in a new window on a blank document from `R:\scratch\fixtures\` and records that window's handle, and refuse to act on any window the tool did not open. Done when: with the operator's own Word document open, a capture run leaves that document's window, selection and contents untouched. Cheaper substitute: attaching to the first Word window found, which can type into the operator's work.
- [ ] Add window discovery to `scripts/capture-ui.py` by process name (`WINWORD.EXE`, `EXCEL.EXE`, `POWERPNT.EXE`, `VISIO.EXE`, `WINPROJ.EXE`, `OUTLOOK.EXE` or `olk.exe`). Done when: `--app word` finds the Word window or exits 2 naming the missing process. Cheaper substitute: a hardcoded window title.
- [ ] Add a UIA walker in `scripts/capture-ui.py` that emits tab, group and control records with `label`, `controlType`, `order` and `bounds` relative to the client area. Done when: the Word Home tab output passes `python scripts/check-inventory.py`. Cheaper substitute: capturing screen coordinates that change with window position.
- [ ] Map UIA control types and ribbon patterns to schema `controlType` values in `scripts/capture-ui.py` (`SplitButton`, `MenuItem`, gallery `List`). Done when: Paste is captured as `splitButton` and Styles as `gallery`. Cheaper substitute: recording every control as `button`.
- [ ] Add `--tab <name>` and `--all-tabs` in `scripts/capture-ui.py` that select tabs through the UIA `SelectionItem` pattern. Done when: `--all-tabs` captures every tab listed in the app's ribbon. Cheaper substitute: simulating mouse clicks at fixed coordinates.
- [ ] Record only each control's name (its label, a functional fact) in `scripts/capture-ui.py`, and drop the UIA `HelpText` and `FullDescription` properties, which carry Microsoft's ScreenTip prose. Done when: a capture of Word Home holds no ScreenTip description and `python scripts/check-inventory.py` passes on it. Cheaper substitute: capturing the descriptions and filtering them out later. **Corrected 2026-10-20:** recorded ScreenTip titles and descriptions.
- [ ] Add `--expand` in `scripts/capture-ui.py` that opens every drop-down, split-button menu and gallery on a tab, records its items in order, and closes it with Escape. Done when: the Word Home Paste menu and Styles gallery items are captured without a click left open. Cheaper substitute: top-level controls only.
- [ ] Add `--keytips` in `scripts/capture-ui.py` that presses Alt and records KeyTip labels per control. Done when: Word Home Bold records keytip `1`. Cheaper substitute: typing KeyTips from memory.
- [ ] Add a merge mode in `scripts/capture-ui.py` that updates `bounds` and `order` in an existing file without overwriting hand-written `behaviour` and `source`. Done when: re-running on an annotated file keeps the annotations. Cheaper substitute: regenerating files and losing annotations.
- [ ] Add `--layout classic|simplified` in `scripts/capture-ui.py`, writing `ribbon.json` or `ribbon-simplified.json`. Done when: the same tab captured in both layouts produces two files that pass the checker. Cheaper substitute: deriving the Simplified layout from the Classic capture.
- [ ] Write files atomically (temporary file then replace) in `scripts/capture-ui.py`. Done when: killing the process mid-write leaves the previous file intact. Cheaper substitute: writing in place.
- [ ] Commit: `inventory: add UI Automation capture tool`

**Test checkpoint:** `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` exits 0 and `python scripts/check-inventory.py R:\scratch\word-home.json` exits 0.

## 4. Shared Shell Chrome Inventory

The shell is shared by every app: title bar (AutoSave toggle, Quick Access Toolbar, document name and save state, search box, account, minimise, maximise, close), the ribbon tab row (File, tabs, Comments, Editing mode, Share), ribbon display options, the KeyTips layer, the Backstage frame, and the common parts of the status bar.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Capture the title bar and tab row from Word, Excel and PowerPoint with `scripts/capture-ui.py`. Done when: `design/inventory/shell/chrome.json` passes the checker.
2. Annotate behaviour and sources. Done when: every record has `behaviour` and `source`.

- [ ] Capture the title bar elements of Word into `design/inventory/shell/chrome.json` with ids under `shell.titlebar.*`. Done when: AutoSave, Quick Access Toolbar, document name, search, account and caption buttons each have a record with `bounds`. Cheaper substitute: one record for the whole title bar.
- [ ] Capture the Quick Access Toolbar default commands and its customise menu into `shell.qat.*`. Done when: each menu entry has an `order`. Cheaper substitute: recording only the visible buttons.
- [ ] Capture the ribbon tab row right-side controls (Comments, Editing or Viewing mode, Share) into `shell.tabrow.*`. Done when: each has `bounds` and `behaviour`. Cheaper substitute: recording them inside each app's ribbon file.
- [ ] Capture the ribbon display options menu (Full-screen mode, Show tabs only, Always show Ribbon, Show Quick Access Toolbar) into `shell.ribbonDisplay.*`. Done when: four records exist with behaviour. Cheaper substitute: describing collapse modes in prose only.
- [ ] Capture the search box drop-down (recent actions, suggested actions, Help, Files) into `shell.search.*`. Done when: each result category has a record. Cheaper substitute: treating search as a plain text box.
- [ ] Record differences between apps in the shell (for example Outlook's title bar and Project's lack of AutoSave) with `app`-scoped overrides in `design/inventory/shell/chrome.json`. Done when: each app with a difference has an override record. Cheaper substitute: assuming the shell is identical in every app.
- [ ] Commit: `inventory: capture shared shell chrome`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/shell/chrome.json` exits 0 and `python -c "import json; print(len(json.load(open('design/inventory/shell/chrome.json'))))"` prints at least 40.

## 5. Word Ribbon and Contextual Tabs Inventory

Every built-in Word tab (File, Home, Insert, Draw, Design, Layout, References, Mailings, Review, View, Help) and every contextual tab (Table Design, Table Layout, Picture Format, Shape Format, Header and Footer, Equation, Chart Design, Chart Format, SmartArt Design, Format) with groups, controls in order, sizes and KeyTips.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Run `python scripts/capture-ui.py --app word --all-tabs --keytips` into `design/inventory/word/ribbon.json`. Done when: every built-in tab is present.
2. Trigger each contextual tab with a fixture document and capture it. Done when: every contextual tab named above is present.

- [ ] Capture all built-in Word tabs into `design/inventory/word/ribbon.json`. Done when: the eleven tabs named in this section each have a `tab` record with groups. Cheaper substitute: capturing Home only and extrapolating.
- [ ] Create `R:\scratch\fixtures\word-contextual.docx` containing a table, picture, shape, header, equation, chart and SmartArt for triggering contextual tabs. Done when: selecting each object shows its contextual tab. Cheaper substitute: committing the fixture, which may embed Microsoft template content.
- [ ] Capture each contextual tab into `design/inventory/word/ribbon.json` as `contextualTab` records with the trigger object in `behaviour`. Done when: all ten contextual tabs named in this section exist. Cheaper substitute: listing contextual tab names without groups.
- [ ] Capture every drop-down and split-button menu one level deep (for example Paste options, Line and Paragraph Spacing, Borders) as child `control` records. Done when: the Borders menu lists every border command in order. Cheaper substitute: recording the top-level button only.
- [ ] Capture galleries (Styles, Themes, Text Effects, Shape Styles) with their default first items and the gallery's expand behaviour. Done when: each gallery record names its expand control. Cheaper substitute: treating galleries as buttons.
- [ ] Write a `behaviour` sentence in our own words for every Word ribbon control, from using it in the reference build. Done when: `python scripts/check-inventory.py --require-behaviour design/inventory/word/ribbon.json` exits 0. **Corrected 2026-10-20:** said "from Microsoft Support pages". Cheaper substitute: copying the control label into `behaviour`.
- [ ] Capture every Word tab in the Simplified Ribbon into `design/inventory/word/ribbon-simplified.json` with `--layout simplified`, including each overflow menu. Done when: every Classic tab has a Simplified counterpart and the checker passes. Cheaper substitute: assuming the Simplified Ribbon is the Classic one with smaller buttons. **Corrected 2026-10-20 (D02 T01 §2):** the reference build may not offer a Simplified Ribbon (Word build 16.0.20430.20182's Ribbon Display Options has no Classic or Simplified switch, and the 2024 baseline lists `SingleLineRibbonToggle` only for Word and Outlook, outside the ribbon). First record in `design/inventory/REFERENCE.md` `## Layout choices` whether this build offers it and the exact steps that switch it; capture only if it does, otherwise record the absence there, which the owner question in the phase 2 run file covers.
- [ ] Commit: `inventory: capture Word ribbon and contextual tabs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/word/ribbon.json` exits 0 and the file holds at least 11 `tab` and 10 `contextualTab` records.

## 6. Word Backstage, Panes, Status Bar and Dialogs Inventory

Word beyond the ribbon: Backstage pages (Home, New, Open, Info, Save, Save As, Print, Share, Export, Transform, Close, Account, Feedback, Options), task panes (Navigation, Styles, Clipboard, Reviewing, Editor, Format Shape, Selection), status bar items, views, and every dialog reachable from a ribbon dialog launcher or Backstage.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Capture Backstage pages into `design/inventory/word/backstage.json`. Done when: every page named above has a record with its sections.
2. Capture panes, status bar and dialogs into their files. Done when: all four files pass the checker.

- [ ] Capture each Backstage page and its sections into `design/inventory/word/backstage.json`. Done when: the fourteen pages named in this section exist with child records. Cheaper substitute: page names only.
- [ ] Capture the Word Options dialog categories and every setting label in order into `design/inventory/word/backstage.json` under `word.options.*`. Done when: each category lists its settings with control type. Cheaper substitute: category names only.
- [ ] Capture task panes into `design/inventory/word/panes.json` with docking side, default width and the command that opens each. Done when: the seven panes named in this section exist. Cheaper substitute: panes without their opening command.
- [ ] Capture the status bar items and the Customize Status Bar menu into `design/inventory/word/statusbar.json`. Done when: every menu item has `order` and default on or off state. Cheaper substitute: only the items visible by default.
- [ ] Capture each dialog reachable from a Word dialog launcher or Backstage into `design/inventory/word/dialogs.json` with tabs and control labels. Done when: Font, Paragraph, Page Setup, Find and Replace, Insert Table, Symbol, Index, Table of Contents, Bookmark and Mail Merge Recipients exist at minimum. Cheaper substitute: dialog titles without controls.
- [ ] Capture the Word right-click context menus (text, table, picture, shape, header and footer, hyperlink, spelling error, tracked change, comment) and the mini toolbar into `design/inventory/word/menus.json`, one record per menu item in order. Done when: each context named here has its menu captured with submenus one level deep. Cheaper substitute: the text context menu only.
- [ ] Commit: `inventory: capture Word Backstage, panes, status bar and dialogs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/word` exits 0 and `design/inventory/word/dialogs.json` holds at least 10 `dialog` records.

## 7. Excel Ribbon and Contextual Tabs Inventory

Every built-in Excel tab (File, Home, Insert, Draw, Page Layout, Formulas, Data, Review, View, Automate, Help) and contextual tab (Table Design, PivotTable Analyze, PivotTable Design, Chart Design, Format, Picture Format, Shape Format, Sparkline, Header and Footer, Query, Timeline, Slicer).

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Run `python scripts/capture-ui.py --app excel --all-tabs --keytips` into `design/inventory/excel/ribbon.json`. Done when: every built-in tab is present.
2. Trigger and capture each contextual tab with a fixture workbook. Done when: every contextual tab named above is present.

- [ ] Capture all built-in Excel tabs into `design/inventory/excel/ribbon.json`. Done when: the eleven tabs each have a `tab` record with groups. Cheaper substitute: capturing Home and Formulas only.
- [ ] Create `R:\scratch\fixtures\excel-contextual.xlsx` with a table, PivotTable, chart, picture, shape, sparkline, query, timeline and slicer. Done when: each object shows its contextual tab when selected. Cheaper substitute: committing the fixture.
- [ ] Capture each contextual tab into `design/inventory/excel/ribbon.json` as `contextualTab` records. Done when: the twelve contextual tabs named in this section exist. Cheaper substitute: names without groups.
- [ ] Capture the Formulas tab function library menus (Financial, Logical, Text, Date and Time, Lookup and Reference, Math and Trig, More Functions) with every function in order. Done when: each category lists its functions. Cheaper substitute: category names only, which hides the function surface.
- [ ] Capture drop-down menus one level deep (Conditional Formatting, Format, Sort and Filter, Insert, Delete) as child `control` records. Done when: Conditional Formatting lists its rule families in order. Cheaper substitute: top-level buttons only.
- [ ] Write a `behaviour` sentence in our own words for every Excel ribbon control, from using it in the reference build. Done when: `python scripts/check-inventory.py --require-behaviour design/inventory/excel/ribbon.json` exits 0. Cheaper substitute: labels copied into `behaviour`.
- [ ] Capture every Excel tab in the Simplified Ribbon into `design/inventory/excel/ribbon-simplified.json` with `--layout simplified`, including each overflow menu. Done when: every Classic tab has a Simplified counterpart and the checker passes. Cheaper substitute: assuming the Simplified Ribbon is the Classic one with smaller buttons. **Corrected 2026-10-20 (D02 T01 §2):** the reference build may not offer a Simplified Ribbon (Word build 16.0.20430.20182's Ribbon Display Options has no Classic or Simplified switch, and the 2024 baseline lists `SingleLineRibbonToggle` only for Word and Outlook, outside the ribbon). First record in `design/inventory/REFERENCE.md` `## Layout choices` whether this build offers it and the exact steps that switch it; capture only if it does, otherwise record the absence there, which the owner question in the phase 2 run file covers.
- [ ] Commit: `inventory: capture Excel ribbon and contextual tabs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/excel/ribbon.json` exits 0 and the file holds at least 11 `tab` and 12 `contextualTab` records.

## 8. Excel Backstage, Formula Bar, Panes and Dialogs Inventory

Excel beyond the ribbon: Name Box and formula bar, sheet tabs and their context menu, Backstage pages, Excel Options, task panes (Format Cells pane forms, PivotTable Fields, Queries and Connections, Selection, Clipboard), status bar aggregates and their customise menu, and dialogs (Format Cells, Insert Function, Function Arguments, Name Manager, Data Validation, Conditional Formatting Rules Manager, Sort, Paste Special, Go To Special, Goal Seek, Scenario Manager).

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Capture the formula bar, Name Box and sheet tab strip into `design/inventory/excel/panes.json`. Done when: each element has `bounds`.
2. Capture Backstage, status bar and dialogs. Done when: all Excel files pass the checker.

- [ ] Capture the Name Box, formula bar (Cancel, Enter, Insert Function, expand) and sheet tab strip with its context menu into `design/inventory/excel/panes.json`. Done when: each control has `bounds` and `behaviour`. Cheaper substitute: treating the formula bar as one text box.
- [ ] Capture Backstage pages and Excel Options categories with every setting into `design/inventory/excel/backstage.json`. Done when: each Options category lists its settings. Cheaper substitute: category names only.
- [ ] Capture task panes into `design/inventory/excel/panes.json` with the command that opens each. Done when: the five panes named in this section exist. Cheaper substitute: panes without their opening command.
- [ ] Capture the status bar aggregates and Customize Status Bar menu into `design/inventory/excel/statusbar.json`. Done when: Average, Count, Numerical Count, Minimum, Maximum and Sum each record default state. Cheaper substitute: Sum only.
- [ ] Capture each dialog named in this section into `design/inventory/excel/dialogs.json` with tabs and controls. Done when: the eleven dialogs exist. Cheaper substitute: titles without controls.
- [ ] Capture the Excel right-click context menus (cell, row header, column header, sheet tab, table, PivotTable, chart, picture, shape) and the mini toolbar into `design/inventory/excel/menus.json`, one record per menu item in order. Done when: each context named here has its menu captured with submenus one level deep. Cheaper substitute: the text context menu only.
- [ ] Commit: `inventory: capture Excel Backstage, formula bar, panes and dialogs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/excel` exits 0 and `design/inventory/excel/dialogs.json` holds at least 11 `dialog` records.

## 9. PowerPoint Ribbon and Contextual Tabs Inventory

Every built-in PowerPoint tab (File, Home, Insert, Draw, Design, Transitions, Animations, Slide Show, Record, Review, View, Help) and contextual tab (Shape Format, Picture Format, Table Design, Table Layout, Chart Design, Chart Format, SmartArt Design, Video Format, Playback, Audio Format, Equation).

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Run `python scripts/capture-ui.py --app powerpoint --all-tabs --keytips` into `design/inventory/powerpoint/ribbon.json`. Done when: every built-in tab is present.
2. Trigger and capture each contextual tab. Done when: every contextual tab named above is present.

- [ ] Capture all built-in PowerPoint tabs into `design/inventory/powerpoint/ribbon.json`. Done when: the twelve tabs each have groups. Cheaper substitute: Home and Insert only.
- [ ] Create `R:\scratch\fixtures\powerpoint-contextual.pptx` with a shape, picture, table, chart, SmartArt, video, audio and equation. Done when: each object shows its contextual tab. Cheaper substitute: committing the fixture.
- [ ] Capture each contextual tab as `contextualTab` records. Done when: the eleven contextual tabs named in this section exist. Cheaper substitute: names without groups.
- [ ] Capture the Transitions and Animations galleries with every effect in order and its Effect Options menu. Done when: each effect lists its options. Cheaper substitute: gallery records without effects.
- [ ] Write a `behaviour` sentence in our own words for every PowerPoint ribbon control, from using it in the reference build. Done when: `python scripts/check-inventory.py --require-behaviour design/inventory/powerpoint/ribbon.json` exits 0. Cheaper substitute: labels copied into `behaviour`.
- [ ] Capture every PowerPoint tab in the Simplified Ribbon into `design/inventory/powerpoint/ribbon-simplified.json` with `--layout simplified`, including each overflow menu. Done when: every Classic tab has a Simplified counterpart and the checker passes. Cheaper substitute: assuming the Simplified Ribbon is the Classic one with smaller buttons. **Corrected 2026-10-20 (D02 T01 §2):** the reference build may not offer a Simplified Ribbon (Word build 16.0.20430.20182's Ribbon Display Options has no Classic or Simplified switch, and the 2024 baseline lists `SingleLineRibbonToggle` only for Word and Outlook, outside the ribbon). First record in `design/inventory/REFERENCE.md` `## Layout choices` whether this build offers it and the exact steps that switch it; capture only if it does, otherwise record the absence there, which the owner question in the phase 2 run file covers.
- [ ] Commit: `inventory: capture PowerPoint ribbon and contextual tabs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/powerpoint/ribbon.json` exits 0 and the file holds at least 12 `tab` and 11 `contextualTab` records.

## 10. PowerPoint Backstage, Views, Panes and Dialogs Inventory

PowerPoint beyond the ribbon: views (Normal, Outline, Slide Sorter, Notes Page, Reading, Slide Master, Handout Master, Notes Master, Slide Show, Presenter View), the thumbnail pane, notes pane, status bar, Backstage and Options, task panes (Animation Pane, Selection, Format Shape, Design Ideas), and dialogs.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Capture each view's layout regions into `design/inventory/powerpoint/panes.json`. Done when: the ten views named above each have a `view` record with regions and `bounds`.
2. Capture Backstage, status bar and dialogs. Done when: all PowerPoint files pass the checker.

- [ ] Capture each view named in this section as a `view` record with its regions in `design/inventory/powerpoint/panes.json`. Done when: Presenter View records current slide, next slide, notes, timer and tool bar regions. Cheaper substitute: Normal view only.
- [ ] Capture task panes with their opening commands in `design/inventory/powerpoint/panes.json`. Done when: the four panes named in this section exist. Cheaper substitute: panes without commands.
- [ ] Capture Backstage pages and PowerPoint Options into `design/inventory/powerpoint/backstage.json`. Done when: each Options category lists its settings. Cheaper substitute: category names only.
- [ ] Capture the status bar and its customise menu into `design/inventory/powerpoint/statusbar.json`. Done when: Notes, Comments, view buttons and zoom slider have records. Cheaper substitute: zoom only.
- [ ] Capture dialogs (Font, Paragraph, Header and Footer, Slide Size, Set Up Slide Show, Insert Hyperlink, Format Background pane forms) into `design/inventory/powerpoint/dialogs.json`. Done when: each has tabs and controls. Cheaper substitute: titles only.
- [ ] Capture the PowerPoint right-click context menus (slide canvas, slide thumbnail, text box, placeholder, table, picture, shape, chart, notes) and the mini toolbar into `design/inventory/powerpoint/menus.json`, one record per menu item in order. Done when: each context named here has its menu captured with submenus one level deep. Cheaper substitute: the text context menu only.
- [ ] Commit: `inventory: capture PowerPoint views, Backstage, panes and dialogs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/powerpoint` exits 0 and `design/inventory/powerpoint/panes.json` holds at least 10 `view` records.

## 11. Visio Ribbon and Contextual Tabs Inventory

Every built-in Visio tab (File, Home, Insert, Draw, Design, Data, Process, Review, View, Help, plus Developer when enabled) and contextual tabs (Shape Format, Picture Format, Container Format, Table Design and Layout where present, Data Graphic, Callout).

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Run `python scripts/capture-ui.py --app visio --all-tabs --keytips` into `design/inventory/visio/ribbon.json`. Done when: every built-in tab is present.
2. Trigger and capture each contextual tab with a fixture drawing. Done when: every contextual tab present in the reference build is captured.

- [ ] Capture all built-in Visio tabs into `design/inventory/visio/ribbon.json`. Done when: every tab named in this section that the reference build shows has groups. Cheaper substitute: Home only.
- [ ] Create `R:\scratch\fixtures\visio-contextual.vsdx` with a container, picture, callout, data graphic and connector. Done when: each object shows its contextual tab. Cheaper substitute: committing the fixture.
- [ ] Capture each contextual tab as `contextualTab` records with triggers. Done when: every contextual tab observed has groups. Cheaper substitute: names only.
- [ ] Capture the Home tab Tools group (Pointer, Connector, Text, drawing tools) and the Design tab Themes, Variants and Layouts galleries. Done when: each tool and gallery item has a record. Cheaper substitute: top-level buttons only.
- [ ] Write a `behaviour` sentence in our own words for every Visio ribbon control, from using it in the reference build. Done when: `python scripts/check-inventory.py --require-behaviour design/inventory/visio/ribbon.json` exits 0. Cheaper substitute: labels copied into `behaviour`.
- [ ] Record in `design/inventory/REFERENCE.md` whether the reference Visio build offers the Simplified Ribbon; if it does, capture it into `design/inventory/visio/ribbon-simplified.json` with `--layout simplified`. Done when: the reference file states the finding and any capture passes the checker. Cheaper substitute: assuming Visio has the same ribbon modes as Word.
- [ ] Commit: `inventory: capture Visio ribbon and contextual tabs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/visio/ribbon.json` exits 0 and the file holds at least 9 `tab` records.

## 12. Visio Backstage, Shapes Pane and Dialogs Inventory

Visio beyond the ribbon: the Shapes pane (stencil list, More Shapes menu, Quick Shapes, search), drawing page tabs, rulers, grid, Pan and Zoom, Size and Position, Shape Data, Format Shape panes, the template gallery on New, Backstage and Options, status bar, and dialogs (Page Setup, Shape Data, Define Shape Data, Layers, Data Selector).

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Capture the Shapes pane and drawing canvas chrome into `design/inventory/visio/panes.json`. Done when: every element has `bounds`.
2. Capture Backstage, template gallery, status bar and dialogs. Done when: all Visio files pass the checker.

- [ ] Capture the Shapes pane structure (More Shapes, Quick Shapes, stencil headers, search box) into `design/inventory/visio/panes.json`. Done when: each part has `bounds` and `behaviour`. Cheaper substitute: one record for the whole pane.
- [ ] Capture the More Shapes category tree and the stencil names it lists into `design/inventory/visio/panes.json`. Done when: every category lists its stencils. Cheaper substitute: the top-level categories only.
- [ ] Capture the New page template categories and template names into `design/inventory/visio/backstage.json`. Done when: every template category lists its templates. Cheaper substitute: the first category only.
- [ ] Capture Visio Options, status bar and the dialogs named in this section into their files. Done when: each dialog lists tabs and controls. Cheaper substitute: titles only.
- [ ] Capture the Visio right-click context menus (drawing page, shape, connector, container, page tab, stencil, shape in the Shapes pane) and the mini toolbar into `design/inventory/visio/menus.json`, one record per menu item in order. Done when: each context named here has its menu captured with submenus one level deep. Cheaper substitute: the text context menu only.
- [ ] Commit: `inventory: capture Visio panes, Backstage and dialogs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/visio` exits 0 and `design/inventory/visio/dialogs.json` holds at least 5 `dialog` records.

## 13. Project Ribbon and Contextual Tabs Inventory

Every built-in Project tab (File, Task, Resource, Report, Project, View, Help, plus Developer when enabled) and contextual Format tabs (Gantt Chart Tools, Timeline Tools, Task Usage Tools, Resource Sheet Tools, Report Design and Report Table and Chart tabs).

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Run `python scripts/capture-ui.py --app project --all-tabs --keytips` into `design/inventory/project/ribbon.json`. Done when: every built-in tab is present.
2. Switch views to trigger each Format tab variant and capture it. Done when: every Format variant is present.

- [ ] Capture all built-in Project tabs into `design/inventory/project/ribbon.json`. Done when: the seven tabs each have groups. Cheaper substitute: Task only.
- [ ] Capture the Format contextual tab once per active view (Gantt, Timeline, Task Usage, Resource Sheet, Network Diagram, Calendar) as distinct `contextualTab` records. Done when: each variant records its triggering view. Cheaper substitute: one Format tab record.
- [ ] Capture the Report tab report gallery and the Report Design contextual tabs with a fixture report open. Done when: every built-in report name has a record. Cheaper substitute: report categories only.
- [ ] Write a `behaviour` sentence in our own words for every Project ribbon control, from using it in the reference build. Done when: `python scripts/check-inventory.py --require-behaviour design/inventory/project/ribbon.json` exits 0. Cheaper substitute: labels copied into `behaviour`.
- [ ] Record in `design/inventory/REFERENCE.md` whether the reference Project build offers the Simplified Ribbon; if it does, capture it into `design/inventory/project/ribbon-simplified.json` with `--layout simplified`. Done when: the reference file states the finding and any capture passes the checker. Cheaper substitute: assuming Project has the same ribbon modes as Word.
- [ ] Commit: `inventory: capture Project ribbon and contextual tabs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/project/ribbon.json` exits 0 and the file holds at least 7 `tab` records.

## 14. Project Views, Backstage, Panes and Dialogs Inventory

Project beyond the ribbon: built-in views (Gantt Chart, Tracking Gantt, Task Usage, Team Planner, Network Diagram, Calendar, Resource Sheet, Resource Usage, Resource Graph, Timeline, Task Sheet, Task Form, Resource Form), the view bar and split view, default tables and their columns, Backstage and Project Options, status bar, and dialogs (Task Information, Resource Information, Project Information, Change Working Time, Assign Resources, Level Resources, Baseline).

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Capture each view's layout and default table columns into `design/inventory/project/panes.json`. Done when: every view named above has a `view` record.
2. Capture Backstage, status bar and dialogs. Done when: all Project files pass the checker.

- [ ] Capture each view named in this section with its default table and column list in order into `design/inventory/project/panes.json`. Done when: Gantt Chart lists Task Mode, Task Name, Duration, Start, Finish, Predecessors and Resource Names in captured order. Cheaper substitute: view names only.
- [ ] Capture the Gantt chart timescale tiers, bar styles defaults and the split view behaviour into `design/inventory/project/panes.json`. Done when: the default timescale tiers and units are recorded. Cheaper substitute: a picture description.
- [ ] Capture Backstage pages and Project Options with every setting into `design/inventory/project/backstage.json`. Done when: Schedule and Calculation categories list every setting. Cheaper substitute: category names only.
- [ ] Capture the status bar (new task mode, view shortcuts, zoom) into `design/inventory/project/statusbar.json`. Done when: each item has `bounds`. Cheaper substitute: zoom only.
- [ ] Capture the dialogs named in this section with every tab and control into `design/inventory/project/dialogs.json`. Done when: Task Information lists General, Predecessors, Resources, Advanced, Notes and Custom Fields tabs. Cheaper substitute: titles only.
- [ ] Capture the Project right-click context menus (task row, resource row, column header, Gantt bar, timeline, timescale) and the mini toolbar into `design/inventory/project/menus.json`, one record per menu item in order. Done when: each context named here has its menu captured with submenus one level deep. Cheaper substitute: the text context menu only.
- [ ] Commit: `inventory: capture Project views, Backstage, panes and dialogs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/project` exits 0 and `design/inventory/project/panes.json` holds at least 13 `view` records.

## 15. Outlook Module and Item Window Ribbons Inventory

Outlook has a ribbon per module (Mail, Calendar, People, Tasks) and per item window (new message, read message, appointment, meeting, contact, task). The capture follows the Outlook client chosen in §2.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Capture each module's ribbon into `design/inventory/outlook/ribbon.json` with module-scoped ids. Done when: every module has its tabs.
2. Open each item window type and capture its ribbon. Done when: every item window named in the micro-steps is present.

- [ ] Capture the Mail module tabs (Home, Send and Receive, View, Help, plus Folder where shown) into `design/inventory/outlook/ribbon.json` under `outlook.mail.*`. Done when: each tab has groups. Cheaper substitute: the Home tab only.
- [ ] Capture the Calendar, People and Tasks module tabs under `outlook.calendar.*`, `outlook.people.*` and `outlook.tasks.*`. Done when: each module has its tabs. Cheaper substitute: assuming modules share the Mail ribbon.
- [ ] Capture the new message window tabs (Message, Insert, Options, Draw, Format Text, Review, Help) under `outlook.compose.*`. Done when: each tab has groups. Cheaper substitute: the Message tab only.
- [ ] Capture the read message, appointment, meeting request, contact and task window ribbons under their own id prefixes. Done when: five item window types each have tabs. Cheaper substitute: one generic item window.
- [ ] Write a `behaviour` sentence in our own words for every Outlook ribbon control, from using it in the reference build. Done when: `python scripts/check-inventory.py --require-behaviour design/inventory/outlook/ribbon.json` exits 0. Cheaper substitute: labels copied into `behaviour`.
- [ ] Capture every Outlook tab in the Simplified Ribbon into `design/inventory/outlook/ribbon-simplified.json` with `--layout simplified`, including each overflow menu. Done when: every Classic tab has a Simplified counterpart and the checker passes. Cheaper substitute: assuming the Simplified Ribbon is the Classic one with smaller buttons. **Corrected 2026-10-20 (D02 T01 §2):** the reference build may not offer a Simplified Ribbon (Word build 16.0.20430.20182's Ribbon Display Options has no Classic or Simplified switch, and the 2024 baseline lists `SingleLineRibbonToggle` only for Word and Outlook, outside the ribbon). First record in `design/inventory/REFERENCE.md` `## Layout choices` whether this build offers it and the exact steps that switch it; capture only if it does, otherwise record the absence there, which the owner question in the phase 2 run file covers.
- [ ] Commit: `inventory: capture Outlook module and item window ribbons`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/outlook/ribbon.json` exits 0 and the file has records under `outlook.mail`, `outlook.calendar`, `outlook.people`, `outlook.tasks` and `outlook.compose`.

## 16. Outlook Modules, Panes, Views and Dialogs Inventory

Outlook's layout beyond the ribbon: navigation bar, folder pane, message list with its columns and conversation grouping, reading pane positions, To-Do Bar, calendar views (Day, Work Week, Week, Month, Schedule), People views, search scopes, Backstage (Info with Account Settings, Rules, Automatic Replies), Outlook Options, and dialogs (Account Settings, Rules and Alerts, Signatures and Stationery, Categories, Address Book).

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Capture each module's layout regions into `design/inventory/outlook/panes.json`. Done when: every module has a `view` record with regions.
2. Capture Backstage, Options and dialogs. Done when: all Outlook files pass the checker.

- [ ] Capture the navigation bar, folder pane and default folders into `design/inventory/outlook/panes.json`. Done when: each element has `bounds` and default order. Cheaper substitute: folder names only.
- [ ] Capture the message list columns, sort and group options, and reading pane positions (Right, Bottom, Off). Done when: each option has a record. Cheaper substitute: the default layout only.
- [ ] Capture the calendar views and their regions (date navigator, calendar list, time grid) as `view` records. Done when: the five calendar views named in this section exist. Cheaper substitute: Month view only.
- [ ] Capture Backstage pages and Outlook Options categories into `design/inventory/outlook/backstage.json`. Done when: each Options category lists its settings. Cheaper substitute: category names only.
- [ ] Capture the dialogs named in this section into `design/inventory/outlook/dialogs.json`. Done when: Rules and Alerts lists its rule wizard steps. Cheaper substitute: titles only.
- [ ] Capture the Outlook right-click context menus (message in the list, folder, calendar item, calendar grid, contact, task, attachment) and the mini toolbar into `design/inventory/outlook/menus.json`, one record per menu item in order. Done when: each context named here has its menu captured with submenus one level deep. Cheaper substitute: the text context menu only.
- [ ] Commit: `inventory: capture Outlook modules, panes, views and dialogs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/outlook` exits 0 and `design/inventory/outlook/panes.json` holds at least 5 calendar `view` records.

## 17. Keyboard Shortcut Inventory for Six Apps

Muscle memory is part of parity. Each app's published shortcut list becomes `shortcut` records linked to the command they invoke.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Record each app's default shortcuts as key chords with our own short action names into `design/inventory/<app>/shortcuts.json`; Microsoft's published shortcut lists may be read as a checklist, but none of their text or links is stored (**Corrected 2026-10-20:** said "transcribe"). Done when: six files pass the checker.

- [ ] Transcribe Word shortcuts into `design/inventory/word/shortcuts.json` with `shortcut`, `behaviour`, `source` and the target command id where one exists. Done when: every table on the source page is covered. Cheaper substitute: the twenty most common shortcuts.
- [ ] Transcribe Excel shortcuts into `design/inventory/excel/shortcuts.json`. Done when: every table on the source page is covered. Cheaper substitute: the twenty most common shortcuts.
- [ ] Transcribe PowerPoint shortcuts into `design/inventory/powerpoint/shortcuts.json`, including slide show shortcuts. Done when: every table on the source page is covered. Cheaper substitute: editing shortcuts only.
- [ ] Transcribe Visio shortcuts into `design/inventory/visio/shortcuts.json`. Done when: every table on the source page is covered. Cheaper substitute: the twenty most common shortcuts.
- [ ] Transcribe Project shortcuts into `design/inventory/project/shortcuts.json`. Done when: every table on the source page is covered. Cheaper substitute: the twenty most common shortcuts.
- [ ] Transcribe Outlook shortcuts into `design/inventory/outlook/shortcuts.json` for the Outlook client chosen in §2. Done when: every table on the source page is covered. Cheaper substitute: mixing classic and new Outlook shortcuts.
- [ ] Add a conflict check to `scripts/check-inventory.py` refusing two `shortcut` records with the same key chord and scope in one app. Done when: a duplicate chord fixture fails. Cheaper substitute: detecting duplicates by eye.
- [ ] Commit: `inventory: add keyboard shortcut inventory`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory` exits 0 and each of the six `shortcuts.json` files holds at least 50 records.

## 18. Inventory Coverage Report

The report turns the inventory into the parity scoreboard: counts per app and kind now, and implemented versus total once application sections start citing ids.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Write `scripts/inventory-report.py`. Done when: it prints counts per app and kind and writes `design/inventory/COVERAGE.md`.

- [ ] Add a baseline comparison to `scripts/inventory-report.py` listing every `idMso` in `design/inventory/<app>/baseline.json` (§19) that is visible in the reference build but missing from the captured inventory. Done when: removing one captured Word control makes the report name its `idMso`. Cheaper substitute: trusting the capture to be complete.
- [ ] Count records per app and `kind` in `scripts/inventory-report.py`. Done when: `python scripts/inventory-report.py` prints a table with one row per app. Cheaper substitute: a file count.
- [ ] Add an implemented count in `scripts/inventory-report.py` by scanning `todo/**/*.md` for `[x]` sections that cite inventory ids. Done when: a fixture TODO citing `word.home.font.bold` in a stamped section counts it as implemented. Cheaper substitute: a hand-maintained percentage.
- [ ] Add `--app`, `--kind` and `--cited-in <file>` filters to `scripts/inventory-report.py`, where `--cited-in` reports the percentage of matching record ids that appear in the file, and `--control-types` reports which `controlType` values the file names. Done when: a fixture spec citing half the Word tabs reports 50 percent for `--app word --kind tab`. Cheaper substitute: a citation count with no denominator.
- [ ] Write `design/inventory/COVERAGE.md` atomically with rows at most 100 characters. Done when: `python scripts/check-design-doc.py design/inventory/COVERAGE.md` exits 0. Cheaper substitute: printing to the console only.
- [ ] Write `scripts/tests/test_inventory_report.py`. Done when: the suite passes and fails when the implemented scan is disabled.
- [ ] Commit: `inventory: add coverage report`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_inventory_report.py"` passes and `python scripts/inventory-report.py` exits 0.

## 19. Microsoft Control Identifier Baseline Import

> **Started:** 2026-10-20T02:31:07Z

Microsoft publishes, per app, every ribbon tab, group and control with its `idMso` identifier, type and parent, including contextual tabs, hidden commands and every Outlook item window. Importing these lists gives a complete checklist, so the live capture can be proven complete rather than assumed complete. The lists date from 2024-03-18; anything newer in build 16.0.20430.20182 is found by the live capture and recorded as `baselineMissing`.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Download the Current Channel lists into `R:\scratch\office-ui-ids\` and convert them with `scripts/import-office-ids.py`. Done when: `design/inventory/<app>/baseline.json` exists for all six apps.
2. Record the source commit and licence. Done when: `design/inventory/REFERENCE.md` names the upstream commit SHA and MIT licence.

- [x] Download `wordcontrols.xlsx`, `excelcontrols.xlsx`, `powerpointcontrols.xlsx`, `visiocontrols.xlsx`, `projectcontrols.xlsx` and every `outlook*controls.xlsx` from the Current Channel folder at a pinned commit into `R:\scratch\office-ui-ids\<sha>\`. Done when: the files and the commit SHA are recorded. Cheaper substitute: reading the lists from the live website each run, which drifts.
- [x] Write `scripts/import-office-ids.py` reading each workbook with `openpyxl` (read-only) and emitting `design/inventory/<app>/baseline.json` with `idMso`, `controlType`, `tab`, `group` and order. **Corrected 2026-10-20:** a baseline row has no visible label, so it cannot be an inventory record (which requires `label`); the file is its own format, `{source, columns, rows}` with one row per workbook row (a row's position is its order) plus `placement`, `tabSet`, parents and `policyId`, checked against `design/inventory/baseline.schema.json` by `scripts/check-inventory.py`. Rows the workbooks list without an identifier are kept with a null `idMso`, and the workbooks' "None (...)" wording becomes our own `placement` enum rather than copied text. Done when: Word's baseline lists the Home tab's Clipboard, Font, Paragraph, Styles and Editing groups in order. Cheaper substitute: copying a few rows by hand.
- [x] Merge the Outlook item-window workbooks into `design/inventory/outlook/baseline.json` keyed by window type (explorer, mail compose, mail read, appointment, contact, task and the rest). Done when: every Outlook workbook contributes records under its window type. Cheaper substitute: the explorer workbook only, which misses every item window.
- [x] Write the upstream commit SHA, licence and import date to `design/inventory/REFERENCE.md` under `## Baseline` and add the MIT notice to `THIRD-PARTY-NOTICES.md` as a data source. Done when: both files name the SHA. Cheaper substitute: an unpinned link.
- [x] Write `scripts/tests/test_import_office_ids.py` with a small fixture workbook. Done when: the suite passes and fails when the group order is not preserved.
- [x] Commit: `inventory: import Microsoft control identifier baseline`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_import_office_ids.py"` passes and `python scripts/check-inventory.py design/inventory` exits 0 with six `baseline.json` files present.

> **Verified:** 2026-10-20 | §19 | 8193634e3a193aefd853262271a5a2fb2a35893b
> **Review:** `docs/reviews/d02-t01-s19.json`

## 20. Word Command Catalogue from ListCommands

Word can list every command it has, with the keyboard shortcut assigned to each, through its built-in `ListCommands` command. Run through COM, this captures commands that have no ribbon button and the complete default shortcut map, which the support pages only partly document.

**Phase:** 2
**Needs:** office, windows-host
**Surface:** no

**Build order:**

1. Run `scripts/word-commands.py` against a Word instance it starts itself. Done when: `design/inventory/word/commands.json` holds every listed command.
2. Link commands to ribbon records and shortcuts. Done when: shortcut records in `design/inventory/word/shortcuts.json` reference command records.

- [ ] Write `scripts/word-commands.py` that starts its own hidden Word instance through COM (`win32com.client.DispatchEx("Word.Application")`), calls `ListCommands(True)` on a new document, reads the resulting table, and quits that instance without saving. Done when: the script never attaches to the operator's running Word and leaves no `WINWORD.EXE` it started behind. Cheaper substitute: `GetActiveObject`, which drives the operator's own Word.
- [ ] Write each row to `design/inventory/word/commands.json` as a `command` record with name, modifiers, key and the menu path Word reports. Done when: the record count equals the table's row count. Cheaper substitute: keeping only commands that have a shortcut.
- [ ] Link each command to its ribbon control by `idMso` or label where they match, in `scripts/word-commands.py`. Done when: unmatched commands are listed in the run output for review. Cheaper substitute: silent best-effort matching.
- [ ] Commit: `inventory: capture Word command catalogue`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/word/commands.json` exits 0 and the file holds at least 1,000 `command` records.

## 21. Microsoft-Free Inventory Model

> **Started:** 2026-10-20T02:16:35Z

The owner ruled on 2026-10-20 that the repository holds no Microsoft text and no Microsoft links: the inventory keeps facts only (control names, positions, types, ids, shortcuts), and every behaviour sentence is written in our own words. Section 1 (stamped) shipped a `screentip` field for captured ScreenTip prose, web URLs as behaviour sources, and a `--require-behaviour` gate that demanded a web source. This section replaces those three; §1's checklist stays as its stamped record.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Change `design/inventory/schema.json` so records cannot hold ScreenTip prose or URLs. Done when: the schema refuses both.
2. Change `scripts/check-inventory.py` to refuse links in any field and to gate behaviour without a source rule. Done when: the tests in the checklist pass and fail on the old behaviour.

- [x] Remove the `screentip` property from `design/inventory/schema.json`. Done when: a record carrying `screentip` fails with `unknown field screentip`. Cheaper substitute: keeping the field and promising not to fill it.
- [x] Restrict `source` in `design/inventory/schema.json` to capture provenance: `uia:<build>`, `baseline:<commit>` or `listcommands:<build>`. Done when: an `https://` source fails the pattern and `uia:16.0.20430.20182` passes. Cheaper substitute: a description that discourages links while the pattern still allows them.
- [x] Add `links()` in `scripts/check-inventory.py` refusing any string value in a record that contains `http://`, `https://` or `www.`. Done when: a behaviour sentence containing a URL fails with `link`. Cheaper substitute: checking only the `source` field.
- [x] Change `--require-behaviour` in `scripts/check-inventory.py` to require a non-blank behaviour sentence on every control, with no web-source rule. Done when: a control with a behaviour sentence and a `uia:` source passes, and one without behaviour fails. Cheaper substitute: leaving the web-source rule, which would force the links this rule forbids.
- [x] Update `scripts/tests/test_check_inventory.py`: fixtures use `uia:` sources only, add cases for a `screentip` field, an `https` source, a URL inside `behaviour`, and the new behaviour gate. Done when: the suite passes and each new case fails when its rule is disabled.
- [x] Commit: `inventory: keep Microsoft text and links out of the inventory model`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_check_inventory.py"` passes, and `rg -n -i "https?://|microsoft\.com|screentip" design/inventory scripts/check-inventory.py scripts/tests/test_check_inventory.py` finds nothing except the refusal fixtures in `scripts/tests/test_check_inventory.py` and the schema's `$schema` line. **Corrected 2026-10-20:** said nothing except the `links()` pattern; the checklist's own refusal cases must hold a `screentip` field and `https` values, and `$schema` is the JSON Schema standard's required dialect identifier, not a reference link (the `$id` became a `urn:`). The `links()` pattern `https?://` does not match its own search.

> **Verified:** 2026-10-20 | §21 | 8f59a68e156be1f9157226c05293ce7d46f5586a
> **Review:** `docs/reviews/d02-t01-s21.json`

## Verification

- `python scripts/check-inventory.py design/inventory` exits 0 over every file.
- `design/inventory/COVERAGE.md` lists all six apps and the shell with non-zero counts per kind.
- `git ls-files design/inventory | Select-String -Pattern "\.(png|jpg|ico)$"` finds nothing.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
