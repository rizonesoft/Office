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
- -> XREF: D03 T01 §13 -- application TODO domains are authored from this inventory, every inventory record owned by exactly one section (1:1), proven by §22
- -> XREF: D03 T01 §14 -- decides each cloud-backed record's disposition, the field §28 adds

## Outcome

- `design/inventory/schema.json` defines an element record; `python scripts/check-inventory.py` validates every inventory file against it and refuses duplicates, orphans and missing sources.
- `design/inventory/<app>/` holds `ribbon.json`, `backstage.json`, `panes.json`, `statusbar.json`, `dialogs.json` and `shortcuts.json` for each of `word`, `excel`, `powerpoint`, `visio`, `project` and `outlook`, plus `design/inventory/shell/chrome.json`.
- `python scripts/inventory-report.py` prints element counts per app and kind, and writes `design/inventory/COVERAGE.md`.
- `python scripts/inventory-report.py --owners --check` names every inventory record no TODO section owns, so each element of the six apps maps 1:1 to the section that implements it.

**Adjacency:** all=not-applicable (a reference catalogue of Microsoft's surfaces; it creates no user records, settings or permissions in the product)

**Adjacency rationale:** The inventory is a measuring stick for later work. Every list, document, settings, reporting, notifications, permissions, audit, exchange and reverse surface it records is owned by the application section that implements the inventoried element.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Inventory schema checker | D00 T01 §1 | [x] |
| 2 | §2 | Reference build setup | -- | [x] |
| 3 | §3 | UIA capture tool | §1, §2, §21 | [x] |
| 4 | §4 | Shell chrome inventory | §3, §23, §24, §26 | [x] |
| 5 | §5 | Word ribbon | §3, §19, §23, §24, §26 | [x] |
| 6 | §6 | Word Backstage pages | §5 | [x] |
| 7 | §7 | Excel ribbon | §3, §19, §23, §24, §26 | [ ] |
| 8 | §8 | Excel panes, dialogs | §7, §17 | [ ] |
| 9 | §9 | PowerPoint ribbon | §3, §19, §23, §24, §26 | [ ] |
| 10 | §10 | PowerPoint panes, dialogs | §9, §17 | [ ] |
| 11 | §11 | Visio ribbon | §3, §19, §23, §24, §26 | [ ] |
| 12 | §12 | Visio panes, dialogs | §11, §17 | [ ] |
| 13 | §13 | Project ribbon | §3, §19, §23, §24, §26 | [ ] |
| 14 | §14 | Project panes, dialogs | §13, §17 | [ ] |
| 15 | §15 | Outlook ribbons | §3, §19, §23, §24, §26 | [ ] |
| 16 | §16 | Outlook panes, dialogs | §15, §17 | [ ] |
| 17 | §17 | Keyboard shortcuts | §1, §20, §23, §26 | [x] |
| 18 | §18 | Inventory coverage report | §4, §5, §19, §25 | [x] |
| 19 | §19 | Control ID baseline | §1, §21 | [x] |
| 20 | §20 | Word command catalogue | §1, §2, §21 | [x] |
| 21 | §21 | Microsoft-free inventory | §1 | [x] |
| 22 | §22 | Inventory ownership check | §18 | [x] |
| 23 | §23 | Audit schema checker | §1 | [x] |
| 24 | §24 | Audit capture tool | §3 | [x] |
| 25 | §25 | Audit control ID baseline | §19 | [x] |
| 26 | §26 | Audit Microsoft-free rule | §21 | [x] |
| 27 | §27 | Checker mutation sweep | §23 | [x] |
| 28 | §28 | Record dispositions | §18, §22, §23 | [x] |
| 29 | §29 | Inventory layout tables | §22 | [x] |
| 30 | §30 | Built-app layout check | §3 | [ ] |
| 31 | §31 | Word Options settings | §6 | [ ] |
| 32 | §32 | Word task panes | §5 | [ ] |
| 33 | §33 | Word status bar | §5 | [ ] |
| 34 | §34 | Word dialogs | §5 | [ ] |
| 35 | §35 | Word context menus and mini toolbar | §5 | [ ] |
| 36 | §36 | Word Backstage document states | §6 | [ ] |
| 37 | §37 | Word Backstage account states | §6 | [ ] |
| 38 | §38 | Sweep gate on checker changes | §27 | [ ] |

## 1. Inventory Schema Checker

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

## 2. Reference Build Setup

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
- [x] Record the 2026-10-20 layout choices (Classic and Simplified Ribbon both, classic Outlook) in `design/inventory/REFERENCE.md` under `## Layout choices`, with the steps that switch each reference app between the two ribbons. **Corrected 2026-10-20:** Word build 20430's Ribbon Display Options menu has no switch (read live, without changing a setting; elsewhere in Word is unverified), the baseline lists no toggle for Excel, PowerPoint, Visio or Project, and classic Outlook is not started unattended because starting it sends the Outbox; each app's ribbon section (§5, §7, §9, §11, §13, §15) records whether its build offers the switch and the steps, and this section records what was observed. Done when (corrected): both choices carry the owner's date, what was observed is recorded, and every app's switch steps are owned by its ribbon section's corrected item. Done when: both choices carry the owner's date and the switch steps. Cheaper substitute: capturing one ribbon layout and inferring the other.
- [x] Record which apps are unlicensed on the host and how they will be licensed (trial or subscription) in `design/inventory/REFERENCE.md` under `## Licensing`. Done when: Visio and Project each show `installed` or a dated plan. Cheaper substitute: inventorying Visio and Project from web screenshots. **Corrected 2026-10-20:** each app shows its installed state and the licence found; Visio has none, so its capture sections §11 and §12 carry `owner-decision` until the owner confirms its licence, rather than holding this section and every capture behind it.
- [x] Commit: `inventory: record reference build and capture profile`

**Test checkpoint:** `python scripts/check-design-doc.py design/inventory/REFERENCE.md --require Builds --require "Capture profile" --require "Layout choices" --require Licensing` exits 0.

> **Verified:** 2026-10-20 | §2 | c549c6014b05224248ea78cbbe47fc3aad04bb8d
> **Review:** `docs/reviews/d02-t01-s2.json`

## 3. UIA Capture Tool

> **Started:** 2026-10-20T04:20:46Z

Hand-transcribing thousands of controls is slow and error-prone. A capture tool walks the UIA tree of a running app window and writes draft inventory records with names, control types, automation ids and bounding rectangles; a person then adds behaviour and sources.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Write `scripts/capture-ui.py` using `uiautomation` or `pywinauto` (UIA backend), installed per AGENTS.md tool rules. Done when: it dumps the Home tab of Word to JSON records that pass `scripts/check-inventory.py`.
2. Add tab switching and contextual tab triggering. Done when: one run captures every built-in tab of the open app. **Corrected 2026-10-20:** contextual tab triggering needs the Word fixture document that §5 creates, so it moves there. -> XREF: D02 T01 §5

- [x] Add `--launch` in `scripts/capture-ui.py` that starts the reference app in a new window on a blank document from `R:\scratch\fixtures\` and records that window's handle, and refuse to act on any window the tool did not open. Done when: with the operator's own Word document open, a capture run leaves that document's window, selection and contents untouched. **Corrected 2026-10-20:** the blank document is created through COM inside the tool's own instance rather than opened from a fixture file: Word and Excel run as a separate instance (`DispatchEx`), an app that allows one instance only is launched only when it is not running, and Outlook is never started unattended (starting it sends the Outbox). Verified live with the operator's Word (pid 70908) open throughout: it was never touched, and the tool's instance exited after every run. Cheaper substitute: attaching to the first Word window found, which can type into the operator's work.
- [x] Add window discovery to `scripts/capture-ui.py` by process name (`WINWORD.EXE`, `EXCEL.EXE`, `POWERPNT.EXE`, `VISIO.EXE`, `WINPROJ.EXE`, `OUTLOOK.EXE` or `olk.exe`). Done when: `--app word` finds the Word window or exits 2 naming the missing process. **Corrected 2026-10-20:** the tool never attaches to a window it did not open, so process names identify a running single-instance app (which it refuses) and the window is the one its own instance reports; an app that cannot be started exits 2 naming its process (`test_a_missing_app_exits_2_naming_its_process`). Cheaper substitute: a hardcoded window title.
- [x] Add a UIA walker in `scripts/capture-ui.py` that emits tab, group and control records with `label`, `controlType`, `order` and `bounds` relative to the client area. Done when: the Word Home tab output passes `python scripts/check-inventory.py`. Cheaper substitute: capturing screen coordinates that change with window position.
- [x] Map UIA control types and ribbon patterns to schema `controlType` values in `scripts/capture-ui.py` (`SplitButton`, `MenuItem`, gallery `List`). Done when: Paste is captured as `splitButton` and Styles as `gallery`. Cheaper substitute: recording every control as `button`.
- [x] Add `--tab <name>` and `--all-tabs` in `scripts/capture-ui.py` that select tabs through the UIA `SelectionItem` pattern. Done when: `--all-tabs` captures every tab listed in the app's ribbon. Cheaper substitute: simulating mouse clicks at fixed coordinates.
- [x] Record only each control's name (its label, a functional fact) in `scripts/capture-ui.py`, and drop the UIA `HelpText` and `FullDescription` properties, which carry Microsoft's ScreenTip prose. Done when: a capture of Word Home holds no ScreenTip description and `python scripts/check-inventory.py` passes on it. Cheaper substitute: capturing the descriptions and filtering them out later. **Corrected 2026-10-20:** recorded ScreenTip titles and descriptions.
- [x] Add `--expand` in `scripts/capture-ui.py` that opens every drop-down, split-button menu and gallery on a tab, records its items in order, and closes it with Escape. Done when: the Word Home Paste menu and Styles gallery items are captured without a click left open. Cheaper substitute: top-level controls only.
- [x] Add `--keytips` in `scripts/capture-ui.py` that presses Alt and records KeyTip labels per control. Done when: Word Home Bold records keytip `1`. **Corrected 2026-10-20:** no key is pressed: UI Automation exposes each control's full KeyTip path as its access key (`Alt, H, 1`), and the tool records the last step. Cheaper substitute: typing KeyTips from memory.
- [x] Add a merge mode in `scripts/capture-ui.py` that updates `bounds` and `order` in an existing file without overwriting hand-written `behaviour` and `source`. Done when: re-running on an annotated file keeps the annotations. Cheaper substitute: regenerating files and losing annotations.
- [x] Add `--layout classic|simplified` in `scripts/capture-ui.py`, writing `ribbon.json` or `ribbon-simplified.json`. Done when: the same tab captured in both layouts produces two files that pass the checker. **Corrected 2026-10-20:** Word build 16.0.20430.20182 has no Classic or Simplified switch, so `--layout simplified` exits 2 naming the missing `SingleLineRibbonToggle`; the switching itself is built where an app offers it. -> XREF: D02 T01 §15 Cheaper substitute: deriving the Simplified layout from the Classic capture.
- [x] Write files atomically (temporary file then replace) in `scripts/capture-ui.py`. Done when: killing the process mid-write leaves the previous file intact. Cheaper substitute: writing in place.
- [x] Commit: `inventory: add UI Automation capture tool`

**Test checkpoint:** `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` exits 0 and `python scripts/check-inventory.py R:\scratch\word-home.json` exits 0.

> **Verified:** 2026-10-20 | §3 | 59a4e067a17b78e10346424b33e1e43db8704b63
> **Review:** `docs/reviews/d02-t01-s3.json`

## 4. Shell Chrome Inventory

> **Duration:** 2026-11-09T02:53:45Z .. 2026-11-09T09:42:10Z (6h 48m 25s)

The shell is shared by every app: title bar (AutoSave toggle, Quick Access Toolbar, document name and save state, search box, account, minimise, maximise, close), the ribbon tab row (File, tabs, Comments, Editing mode, Share), ribbon display options, the KeyTips layer, the Backstage frame, and the common parts of the status bar.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Capture the shared shell chrome and per-app shell differences from Word, Excel, PowerPoint, Visio and Project (plus baseline-backed shell overrides for classic Outlook whose live attended explorer and item-window shell measurements are completed in `D02 T01 §15`) into `design/inventory/shell/chrome.json` with `scripts/capture-ui.py --shell`, and provide `effective_shell(records, app, window=None)` and `validate_shell_chrome(records)` in `scripts/capture-ui.py`. Done when: `design/inventory/shell/chrome.json` passes the checker and `validate_shell_chrome(records)`.
2. Annotate behaviour, bounds and sources. Done when: every record has `behaviour`, `captureProfile: "fhd-100"` and `source` (`uia:<build>` on every shared `shell.*` and live-captured `excel`, `powerpoint`, `visio` and `project` override record, with non-zero `bounds`), and `python scripts/check-inventory.py --require-behaviour design/inventory/shell/chrome.json` exits 0.

- [x] Add `--shell`, `effective_shell(records, app, window=None)` and `validate_shell_chrome(records)` to `scripts/capture-ui.py` (stripping `$defs.noControl` bidi format characters from UIA names, resolving PowerPoint's `PPTFrameClass` and Project's `JWinproj-WhimperMainClass` top-level window handles, normalising system-DPI-scaled client coordinates on the 96-DPI capture monitor, and sanitising personal account or file names out of shell records) and capture the title bar elements of Word into `design/inventory/shell/chrome.json` with ids under `shell.titlebar.*`. Done when: `shell.titlebar.systemMenu` (`uiaId: "MenuBar"`), `shell.titlebar.qat`, `shell.titlebar.autosave` (`idMso: "AutoSaveSwitch"`), `shell.titlebar.documentTitle`, `shell.titlebar.caption`, `shell.titlebar.search` (`uiaId: "TellMeControlAnchor"`), `shell.titlebar.account` (`label: "Account"`, `uiaId: "MeControlWidget"`), `shell.titlebar.minimize`, `shell.titlebar.maximize` and `shell.titlebar.close` each have a record with non-zero `bounds`, `captureProfile: "fhd-100"`, `source: "uia:<build>"` and `behaviour`, covered by unit and refusal tests in `scripts/tests/test_capture_ui.py`. Cheaper substitute: one record for the whole title bar.
- [x] Capture the Quick Access Toolbar default commands (`shell.qat.autosave`, `shell.qat.save` with `idMso: "FileSave"`, `shell.qat.undo` with `idMso: "Undo"` and `shell.qat.undo.dropdown`, `shell.qat.redo` with `idMso: "RedoOrRepeat"`, `shell.qat.customize`) and its customise menu into `shell.qat.*`. Done when: each default button and each of the 16 `Customize Quick Access Toolbar` menu entries (`Automatically Save` through `Hide Quick Access Toolbar`) has an `order`, non-zero `bounds`, `captureProfile: "fhd-100"`, `source: "uia:<build>"` and `behaviour`. Cheaper substitute: recording only the visible buttons.
- [x] Capture the ribbon tab row controls (`shell.tabrow.file` with `uiaId: "FileTabButton"`, `shell.tabrow.tabs`, `shell.tabrow.comments`, `shell.tabrow.editingMode` with its three child mode items `Editing`, `Reviewing` and `Viewing`, and `shell.tabrow.share` with its three child items `Share...`, `Copy Link...` and `Manage Access...`) into `shell.tabrow.*`. Done when: each has `order`, non-zero `bounds`, `captureProfile: "fhd-100"`, `source: "uia:<build>"` and `behaviour`. Cheaper substitute: recording them inside each app's ribbon file.
- [x] Capture the ribbon display options button (`shell.ribbonDisplay.button`) and menu (`Full-screen mode`, `Show tabs only`, `Always show Ribbon`, and `Hide Quick Access Toolbar` when the QAT is shown or `Show Quick Access Toolbar` when hidden, per `design/inventory/REFERENCE.md`) into `shell.ribbonDisplay.*`. Done when: the anchor button and all four menu items exist with `order`, non-zero `bounds`, `captureProfile: "fhd-100"`, `source: "uia:<build>"` and `behaviour`. Cheaper substitute: describing collapse modes in prose only.
- [x] Capture the search box (`shell.search.input` with `uiaId: "TellMeTextBoxAutomationId"`, `shell.search.voice`) and its drop-down flyout (`shell.search.flyout`) and categories (`shell.search.recentActions`, `shell.search.suggestedActions` with its default items, `shell.search.actions`, `shell.search.findInDocument`, `shell.search.people` without personal names, `shell.search.files`, `shell.search.help`) into `shell.search.*`. Done when: the search input, voice button, flyout container and each result category have records with non-zero `bounds`, `captureProfile: "fhd-100"`, `source: "uia:<build>"` and `behaviour`. Cheaper substitute: treating search as a plain text box.
- [x] Capture the shared window frame regions (`shell.region.titlebar`, `shell.region.tabrow`, `shell.region.ribbon`, `shell.region.messageBar`, `shell.region.documentArea`, `shell.region.taskPaneDock`, `shell.region.statusbar`), KeyTips layer (`shell.keytips.layer` and the 11 top-level shell KeyTip badge records), Backstage frame (`shell.backstage.frame`, `shell.backstage.titlebar`, `shell.backstage.navBar` with `uiaId: "OutSpaceNavBar"`, `shell.backstage.navList` with `uiaId: "NavBarMenu"`, `shell.backstage.back` with `uiaId: "FileTabButton"`, `shell.backstage.contentPane` with `uiaId: "BackstageView"`) and shared status bar frame (`shell.statusbar.bar`, `shell.statusbar.leftZone`, `shell.statusbar.rightZone`, `shell.statusbar.displaySettings`, `shell.statusbar.viewSwitcher`, `shell.statusbar.zoomOut`, `shell.statusbar.zoomSlider`, `shell.statusbar.zoomIn`, `shell.statusbar.zoomPercent`, `shell.statusbar.customizeMenu`) into `design/inventory/shell/chrome.json` for `D02 T02 §3`, `§5` and `§6`. Done when: every region and frame record named above has non-zero `bounds`, `captureProfile: "fhd-100"`, `source: "uia:<build>"` and `behaviour`. Cheaper substitute: leaving the regions, KeyTips, Backstage frame or status bar frame out of `chrome.json`, or omitting `bounds`.
- [x] Record differences between apps in the shell as `app`-scoped override records (`<app>.shell.<path>`, or `<app>.<window>.shell.<path>` for classic Outlook's window contexts `explorer` and `compose`, corresponding to shared `shell.<path>`) resolved deterministically by `effective_shell(records, app, window=None)` in `scripts/capture-ui.py` (where an override container `<prefix>.shell.<container>` with child records replaces the shared container's direct children, recursively prunes the entire descendant subtree of any excluded shared child such as `shell.tabrow.editingMode`'s three mode items in Excel or `shell.qat.customize`'s menu items when replaced, prunes shared `menuItem` children when a leaf override changes `controlType` to a non-container control such as `visio.shell.tabrow.share` `button`, keeps `shell.keytips.layer` as a root overlay region whose badges track the active title bar, QAT and tab row controls in each app/window context, remaps `parent` on retained descendants to the active override container id so the resolved graph has zero orphan `parent` references, and for `app="outlook"` selects `outlook.<window>.shell.*` with `window="explorer"` by default or `window="compose"` for item windows): live-measured `excel.shell.*` (tab row without `editingMode` and its three mode items, `Redo` splitButton on QAT), `powerpoint.shell.*` (`SlideShowFromBeginning` QAT button, `Present in Teams` tab-row button, and their KeyTip badges), `visio.shell.*` (title bar and QAT without `AutoSaveSwitch`, direct `Share...` button without child menu items and MDI document `Close` button on the tab row, and QAT KeyTip badges `1..3`), and `project.shell.*` (live-measured from `WINPROJ.EXE` `JWinproj-WhimperMainClass` with `source: "uia:<build>"` and non-zero `bounds`: title bar and QAT without `AutoSaveSwitch`, `Redo` splitButton on QAT, `TellMeControlAnchor` search placed on the tab row, and QAT/search KeyTip badges), plus baseline-backed `outlook.explorer.shell.*` (full explorer title bar and tab row with `SendReceiveAll`, `Undo`, `SingleLineRibbonToggle`, `MinimizeRibbon`, `FindContactCombo` on QAT) and `outlook.compose.shell.*` (full item-window title bar and tab row with `FileSave`, `Undo`, `RedoOrRepeat`, `SingleLineRibbonToggle`, `MinimizeRibbon` on QAT) whose attended live UIA geometry and window-type shell measurements are assigned to `D02 T01 §15`. -> XREF: D02 T01 §15 Done when: `excel`, `powerpoint`, `visio` and `project` each have live UIA override records (`source: "uia:<build>"`, non-zero `bounds`), `outlook` has its `outlook.explorer.shell.*` and `outlook.compose.shell.*` baseline-backed override records (`source: "baseline:<sha>"`), and `effective_shell(records, app, window)` and `validate_shell_chrome(records)` verify every app and Outlook window context (including that Word retains `editingMode` and its three mode items, Excel prunes `editingMode` and all three mode items with zero orphan parents, PowerPoint includes `fromBeginning` and `presentInTeams`, Visio and Project omit `autosave` and retain `shell.keytips.layer`, Visio prunes menu items under `visio.shell.tabrow.share`, Project places `search` on the tab row while retaining its search children, and Outlook's `explorer` and `compose` shells resolve independently with full title bar controls and exclude each other's context-only commands). Cheaper substitute: assuming the shell is identical in every app, leaving orphaned descendant records when a container child is excluded, or merging Outlook's explorer and compose QATs into one context.
- [x] Commit: `inventory: capture shared shell chrome`

**Test checkpoint:** `python scripts/check-inventory.py --require-behaviour design/inventory/shell/chrome.json` exits 0, `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` passes, and `python -c "import importlib.util, json; s=importlib.util.spec_from_file_location('c','scripts/capture-ui.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); d=json.load(open('design/inventory/shell/chrome.json',encoding='utf-8')); m.validate_shell_chrome(d); print(len(d))"` exits 0 and prints at least 110.

> **Verified:** 2026-11-09 | §4 | c465fa97d049c2334fa8adac8e4a4ab2fbd3e791
> **Review:** `docs/reviews/d02-t01-s4.json`

## 5. Word Ribbon

> **Duration:** 2026-11-09T10:58:00Z .. 2026-11-09T19:27:00Z (8h 29m 0s)

Every built-in Word tab (Home, Insert, Draw, Design, Layout, References, Mailings, Review, View, Developer, Help) and every contextual or mode-triggered ribbon tab in `design/inventory/word/baseline.json` (Table Design, Table Layout, Picture Format, Shape Format, Header & Footer, Equation, Chart Design, Format [Chart Tools], SmartArt Design, Format [SmartArt Tools], plus Graphics Format `TabGraphicsToolsFormat`, 3D Model `Tab3DModelToolsFormat`, Outlining `TabOutlining`, Background Removal `TabBackgroundRemoval`, Immersive Reader `TabLearningTools`, and full reconciliation of all 20 `coreTab` and 23 `contextualTab` baseline tab rows) with groups, controls in order, sizes and KeyTips. **Corrected 2026-11-09:** `File` (`FileTabButton`) is the Backstage button on the shell tab row captured in `design/inventory/shell/chrome.json` (`shell.tabrow.file`, D02 T01 §4) and its `placement == "backstage"` pages in `design/inventory/word/backstage.json` (D02 T01 §6), whereas `Developer` (`TabDeveloper`) is the eleventh always-available built-in main ribbon tab (`coreTab` in `design/inventory/word/baseline.json`, enabled alongside `Draw` `TabDrawInk`); in Word build `16.0.20527.20150`, the Header & Footer Tools contextual tab label is `Header & Footer` (`TabHeaderAndFooterToolsDesign`) and the Chart Tools formatting contextual tab label is `Format` (`TabChartToolsFormatNew`, disambiguated from SmartArt Tools' `Format` `TabSmartArtToolsFormat` by its `idMso`).

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Run `python scripts/capture-ui.py --app word --all-tabs --expand` into `design/inventory/word/ribbon.json`. Done when: every built-in tab is present. **Corrected 2026-11-09:** replaced `--keytips` with `--expand`; per D02 T01 §3, KeyTips are read automatically from `CurrentAccessKey` without a flag, while `--expand` captures drop-down menus, split-button menus and galleries.
2. Trigger each contextual and mode-driven ribbon tab with a fixture document and Word's object model/commands, capture every available tab, and reconcile all remaining baseline `coreTab` and `contextualTab` rows in `design/inventory/REFERENCE.md`. Done when: every available contextual/mode tab is captured and every baseline `coreTab` and `contextualTab` `idMso` is accounted for.

- [x] Capture all built-in Word tabs into `design/inventory/word/ribbon.json`, reconciling `build/capture-ui/word-unverified.json` so any confirmed built-in Word group or control on the captured built-in or contextual/mode tabs that lacks a 2024 baseline identifier is included in `design/inventory/word/ribbon.json` with `baselineMissing: true` while third-party add-in tabs and groups (such as `Acrobat`) remain excluded with their exclusion reason recorded in `design/inventory/REFERENCE.md`. Done when: the eleven always-available tabs named in this section (`Home` `TabHome`, `Insert` `TabInsert`, `Draw` `TabDrawInk`, `Design` `TabWordDesign`, `Layout` `TabPageLayoutWord`, `References` `TabReferences`, `Mailings` `TabMailings`, `Review` `TabReviewWord`, `View` `TabView`, `Developer` `TabDeveloper`, `Help` `HelpTab`) each have a `tab` record with non-empty `group` and `control` children, confirmed newer built-in groups carry `baselineMissing: true` inside `ribbon.json`, and add-in tabs are excluded. Cheaper substitute: capturing Home only and extrapolating, or silently dropping newer built-in groups into `word-unverified.json`. **Corrected 2026-11-09:** named the eleven built-in `coreTab` tabs explicitly (`Developer` in place of `File`) and added unverified-group reconciliation.
- [x] Create `R:\scratch\fixtures\word-contextual.docx` containing a table, picture, shape, SVG graphic, 3D model, header, equation, chart and SmartArt for triggering contextual and mode tabs, plus scratch prerequisite fixtures (`R:\scratch\fixtures\word-recipients.csv`, `R:\scratch\fixtures\dot.png`, `R:\scratch\fixtures\icon.svg`, `R:\scratch\fixtures\cube.glb`). Done when: selecting each object or entering each mode (Outline view, Background Removal, Immersive Reader) shows its ribbon tab and attaching `R:\scratch\fixtures\word-recipients.csv` enables `Mailings` merge-dependent menus. Cheaper substitute: committing the fixture, which may embed Microsoft template content, or omitting SVG/3D/mode triggers and leaving those baseline tabs uncaptured.
- [x] Capture each available contextual and mode-triggered ribbon tab in `design/inventory/word/baseline.json` into `design/inventory/word/ribbon.json` as `contextualTab` records with the trigger object or mode in `behaviour`, and reconcile all 20 `coreTab` and 23 `contextualTab` rows in `design/inventory/word/baseline.json` by recording documented evidence in `design/inventory/REFERENCE.md` for every superseded legacy `.doc` or unavailable/cloud-only tab (`TabChartToolsDesign`, `TabChartToolsLayout`, `TabChartToolsFormat`, `TabDrawingToolsFormatClassic`, `TabPictureToolsFormatClassic`, `TabTextBoxToolsFormat`, `TabWordArtToolsFormat`, `TabDiagramToolsFormatClassic`, `TabOrganizationChartToolsFormat`, `TabInkToolsPens`, `TabAddIns`, `TabSyntex`, `TabConflicts`, `TabBroadcastPresentation`, `TabBlogPost`, `TabBlogInsert`, `TabPrintPreview`). Done when: all ten core object contextual tabs (`TabTableToolsDesign`, `TabTableToolsLayout`, `TabPictureToolsFormat`, `TabDrawingToolsFormat`, `TabHeaderAndFooterToolsDesign`, `TabEquationToolsDesign`, `TabChartToolsDesignNew`, `TabChartToolsFormatNew`, `TabSmartArtToolsDesign`, `TabSmartArtToolsFormat`) plus every additional available object/mode tab in Word `16.0.20527.20150` (`TabGraphicsToolsFormat`, `Tab3DModelToolsFormat`, `TabOutlining`, `TabBackgroundRemoval`, `TabLearningTools`, and any other live-triggerable baseline tab) exist with their groups, controls and trigger `behaviour`, and every remaining baseline `coreTab`/`contextualTab` `idMso` is reconciled with evidence in `design/inventory/REFERENCE.md`. Cheaper substitute: listing contextual tab names without groups, or ignoring additional baseline contextual/mode tabs outside the first ten. **Corrected 2026-11-09:** named the baseline `idMso` identifiers and added full reconciliation of all 20 `coreTab` and 23 `contextualTab` rows in `design/inventory/word/baseline.json`.
- [x] Prepare document and session prerequisites for state-dependent ribbon menus (attaching `R:\scratch\fixtures\word-recipients.csv` via `MailMerge.OpenDataSource` before expanding `Mailings` so merge-dependent menus such as `Insert Merge Field`, `Rules`, `Finish & Merge` and `Start Mail Merge` expand, and seeding selection/clipboard/tracked-change/comment/table state where needed), capture every drop-down and split-button menu and its nested command-bearing submenus recursively (for example `Paste` options, `Line and Paragraph Spacing`, `Borders`, `Mailings -> Rules`, `Mailings -> Finish & Merge`, and `Home -> Text Effects and Typography -> Outline -> Weight`) as child `menuItem` records preserving parent ancestry and order, and reconcile in `design/inventory/REFERENCE.md` any expandable control that genuinely exposes no child items in Word. Done when: the `Borders` menu, merge-ready `Mailings` menus (`Insert Merge Field`, `Rules`, `Finish & Merge`) and nested submenus such as `Text Effects and Typography -> Outline` have their child `menuItem` records captured under their parent, and no unreconciled `menu`, `splitButton` or `gallery` has zero child `menuItem` records or a `capture-ui: expand failed to open a popup` note. Cheaper substitute: recording the top-level button or first menu level only, or leaving state-dependent menus unexpanded behind an expansion-failure note. **Corrected 2026-11-09:** replaced one-level `control` wording with state-prepared recursive `menuItem` submenu expansion per D02 T01 §3, D02 T01 §24 and `design/inventory/schema.json`.
- [x] Capture galleries (Styles, Themes, Text Effects, Shape Styles) with their default first items and the gallery's expand behaviour. Done when: each gallery record has child `menuItem` records and names its expand control in `behaviour`. Cheaper substitute: treating galleries as buttons.
- [x] Write a `behaviour` sentence in our own words for every Word ribbon `contextualTab`, `control` and `menuItem` record, from using it in the reference build (including each control's and menu item's enablement precondition and, for `toggleButton`, `checkBox`, `radioButton`, `gallery` and stateful `menuItem` records, the conditions that produce unchecked, checked/selected and mixed states across representative document selections such as plain, formatted and mixed-format text, object selections and attached mail-merge data), and enforce Word ribbon completeness in `validate_word_ribbon(records)` (called by `scripts/capture-ui.py` and `scripts/check-inventory.py` when checking `design/inventory/word/ribbon.json`). Done when: `python scripts/check-inventory.py --require-behaviour design/inventory/word/ribbon.json` exits 0 and `validate_word_ribbon(records)` verifies all 11 always-available `tab` `idMso` identities, all captured `contextualTab` `idMso` identities (including `TabGraphicsToolsFormat`, `Tab3DModelToolsFormat`, `TabOutlining`, `TabBackgroundRemoval`, `TabLearningTools` alongside the 10 object contextual tabs) and complete reconciliation of all 20 `coreTab` + 23 `contextualTab` baseline rows, non-empty `group` and `control` hierarchies, non-zero `bounds` and `captureProfile: "fhd-100"` on every record, `size` on every `control`, `keytip` presence and known reference sequences across all `tab` records, all `contextualTab` records, every top-level `control` and every expanded `menuItem` including nested submenus (distinguishing controls and menu items that genuinely expose no UIA `CurrentAccessKey` in Word, reconciled in `design/inventory/REFERENCE.md`, from missing/failed KeyTip reads), required expanded `menuItem` chains (including `Borders`, merge-ready `Mailings` menus and nested submenus) with zero unreconciled expansion failures, gallery expand-control descriptions, and non-blank `behaviour` with observed enablement and checked/mixed state rules on every `contextualTab`, `control` and `menuItem`, with deletion/mutation unit tests in `scripts/tests/test_capture_ui.py` covering built-in tabs, additional contextual/mode tabs, controls, top-level and nested `menuItem` KeyTips, menus, state rules and behaviour. **Corrected 2026-10-20:** said "from Microsoft Support pages". Cheaper substitute: copying the control label into `behaviour`, omitting KeyTip or state-rule validation on controls and nested `menuItem` records, or checking tab counts without structural validation.
- [x] Capture every Word tab in the Simplified Ribbon into `design/inventory/word/ribbon-simplified.json` with `--layout simplified`, including each overflow menu. Done when: every Classic tab has a Simplified counterpart and the checker passes. Cheaper substitute: assuming the Simplified Ribbon is the Classic one with smaller buttons. **Corrected 2026-10-20 (D02 T01 §2):** the reference build may not offer a Simplified Ribbon (Word build 16.0.20430.20182's Ribbon Display Options has no Classic or Simplified switch, and the 2024 baseline lists `SingleLineRibbonToggle` only for Word and Outlook, outside the ribbon). First record in `design/inventory/REFERENCE.md` `## Layout choices` whether this build offers it and the exact steps that switch it; capture only if it does, otherwise record the absence there, which the owner question in the phase 2 run file covers. Done when (corrected): if the build offers the switch, every Classic tab has a Simplified counterpart and the checker passes; if it does not, `REFERENCE.md` records the absence and where it was looked for.
- [x] Link `design/inventory/word/commands.json` to the captured ribbon controls by label where no `idMso` matched, in `scripts/word-commands.py`, only when the command name occurs once in `ListCommands` and every captured ribbon `control` or `menuItem` with that `label` resolves unambiguously to a single `idMso` (with no `idMso`-less control sharing the label), keeping duplicate command names (such as the three `Chart` rows) and ambiguous control labels in `build/word-commands-unmatched.txt` for review. Done when: every unambiguous single-row command whose label matches a single-`idMso` captured ribbon control carries that `idMso`, ambiguous or duplicate names remain in `build/word-commands-unmatched.txt`, and `scripts/tests/test_word_commands.py` tests unique matches, duplicate command names and conflicting control `idMso`s. Cheaper substitute: leaving commands linked only by identifier, or assigning one control's `idMso` to duplicate or ambiguous command rows without evidence. (Moved from D02 T01 §20.)
- [x] Add contextual and mode tab triggering to `scripts/capture-ui.py`: open `R:\scratch\fixtures\word-contextual.docx` in the tool's own instance and select each object or activate each mode through Word's object model/commands, capturing the tabs that appear as `contextualTab` records. Done when: one run captures every contextual and mode tab the fixture triggers and leaves the fixture unmodified. Cheaper substitute: clicking objects at fixed screen positions. (Moved from D02 T01 §3.)
- [x] Commit: `inventory: capture Word ribbon and contextual tabs`

**Test checkpoint:** `python scripts/check-inventory.py --require-behaviour design/inventory/word/ribbon.json` exits 0, `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` and `python -m unittest discover -s scripts/tests -p "test_word_commands.py"` pass, and `python -c "import importlib.util, json; s=importlib.util.spec_from_file_location('c','scripts/capture-ui.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); d=json.load(open('design/inventory/word/ribbon.json',encoding='utf-8')); m.validate_word_ribbon(d); print(sum(r['kind']=='tab' for r in d), sum(r['kind']=='contextualTab' for r in d))"` exits 0 and prints `11` and at least `15` (all 11 built-in `tab` records and all reconciled live-triggerable `contextualTab` records).

> **Verified:** 2026-11-09 | §5 | 07550e9edf3de4b62d059abda3dc3a941f01ee24
> **Review:** `docs/reviews/d02-t01-s5.json`

## 6. Word Backstage Pages

> **Duration:** started 2026-11-13T01:15:23Z, reopened 2026-11-13T03:11:16Z

> **Started:** 2026-11-13T03:11:16Z

Word beyond the ribbon, part one: the Backstage view behind File, its pages (Home, New, Open, Info, Save, Save As, Print, Share, Export, Transform, Close, Account, Feedback, Options) and the sections each page shows. **Corrected 2026-11-13:** split from §6, which bundled six capture surfaces, each needing its own capture mode in `scripts/capture-ui.py` (the tool knew only the ribbon and the shell); one surface per section.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Add the Backstage capture. Done when: its fake-tree test passes.
2. Capture Word's Backstage. Done when: `design/inventory/word/backstage.json` holds the fourteen pages with their sections and passes the checker. **Corrected 2026-11-13 (fresh plan review, gap 4):** every entry of Words own navigation list is recorded as a page or an action, reconciled with the baseline as the items below say; the fourteen were a count, not the reference.

- [x] Add `--backstage` to `scripts/capture-ui.py` for `--app word`: open File, visit each page in the navigation list in order, and record one `backstagePage` record per page (`order`, label, key tip) with one child record per section, button or list the page shows, then leave Backstage with Escape, written through the tool's existing publish path (temporary file, then replace) and merged with `--merge` like a ribbon capture. Done when: a test in `scripts/tests/test_capture_ui.py` over the file's fake UI Automation tree (`E`, `FakeApp`) produces the pages in order with their children, and leaves the fake in the document view, and a refusal test shows the mode exits non-zero naming the surface when it cannot be opened. Cheaper substitute: a hand-written file, which no capture can check again on a new Office build.
- [x] Tell navigation pages from action entries in `--backstage`: an entry that opens content in the Backstage pane (Home, New, Open, Info, Save As, Print, Share, Export, Transform, Account, Feedback, and Save when it opens Save As for a new document) is a `backstagePage`; an entry that acts (Save on a saved document, Close) or leaves Backstage (Options, which opens the dialog §31 captures) is a `control` (`controlType` `button`) recorded from the navigation list and never invoked. The capture works on a new blank document it opened itself, so no user document can be saved or closed by it. Done when: a fake-tree test shows Close and Options recorded as controls with no invoke or select call made on them, and a page entry visited and left. Cheaper substitute: visiting every entry, which saves or closes the capture's document or strands the traversal in a dialog. **Corrected 2026-11-13 (plan review, gap 1).**
- [x] Expand every nested control on each page one level, with the tool's existing popup capture (`expand_items`, `popup_items`): menus (Info's protection menu), split buttons, location choices (Open, Save As) and Print's settings, recording dropdown items in order and numeric inputs as `spinner` or `editBox`. Done when: a fake-tree test of a page with a menu, a dropdown and a spinner records all three with the menu's items, and a test with the expansion removed fails the validator below. Cheaper substitute: the controls a page shows before anything is opened. **Corrected 2026-11-13 (plan review, gap 2).** **Corrected again 2026-11-13 (fresh plan review, gap 1):** one item per menu proved only that it opened. The capture reads each opened menu until two reads a moment apart agree, records how many items it saw on the control (`itemCount`, a new optional field of `design/inventory/schema.json`), and `validate_word_backstage` refuses a menu-type control whose recorded items differ from that count. Done when, in addition: tests show a menu that is still filling read again until it settles, one that never settles failing the capture, and the committed file with one item removed from a full menu (Margins Custom Margins) refused, naming the control.
- [x] Reconcile the capture with the Backstage rows of `design/inventory/word/baseline.json` in a new `validate_word_backstage` in `scripts/capture-ui.py`, which `scripts/check-inventory.py` runs on `design/inventory/word/backstage.json` as it runs `validate_word_ribbon` on the ribbon: every baseline `tab` row of `placement` `backstage` is a captured page or action, and every baseline group or control with an `idMso` under a captured page is captured or listed in `WORD_BACKSTAGE_ABSENT` with the state it needs (**Corrected 2026-11-13, build:** the rules, the absence list `ABSENT` and `validate` live in `scripts/lib/word_backstage.py`, which `scripts/capture-ui.py` and `scripts/check-inventory.py` both import; tests in `scripts/tests/test_word_backstage.py`) (a read-only, protected, checked-out or upgradable document, a server location, a pending update), each such state documented in `design/inventory/REFERENCE.md`. **Corrected 2026-11-13 (fresh plan review, gap 3):** an absence for a state this capture cannot reach names the section that captures it: `document-state` ids by §36 (Word Backstage document states), `account-state` and `layout-variant` ids by §37 (Word Backstage account states); `not-offered` and `not-exposed` are final, with their reasons. Done when, in addition: REFERENCE.md names the owning section of each reason, and `validate_word_backstage` refuses a reason that has no documented owner or final disposition. Done when: tests show a missing page, a missing group and an absent id whose reason `REFERENCE.md` does not hold each refused with the id named, and the committed capture accepted. Cheaper substitute: a fixed count of pages. **Corrected 2026-11-13 (plan review, gaps 1 and 2):** the fourteen pages were a count, not a reconciliation; the reference's own navigation is the truth, and a justified absence is recorded, never an invented page.
- [x] Write a `behaviour` sentence, in our own words under the Microsoft-free rule (§21), for every page, action and actionable control in `design/inventory/word/backstage.json`, saying what it does and when it is disabled; `validate_word_backstage` refuses an actionable record without one. Done when: a test with one behaviour removed is refused naming the record, and `python scripts/check-inventory.py design/inventory/word` exits 0 on the committed file. Cheaper substitute: raw captured labels with no behaviour. **Corrected 2026-11-13 (plan review, gap 3).**
- [x] Bound every page's readiness: after an entry is selected, wait at most a set time (`wait_for`) for its content pane to hold at least one child that is not a loading indicator, and treat a page still loading or empty as a failure of the capture, never as an empty page; on any failure leave Backstage, close the document and Word the tool opened, publish nothing and leave the previous `design/inventory/word/backstage.json` as it was. Done when: tests show a page that never loads, and a traversal that fails on its third page after two good ones, each exiting non-zero naming the page, with the fake's window closed and a previous output file byte-for-byte unchanged. Cheaper substitute: a fixed sleep. **Corrected 2026-11-13 (plan review, gap 4).** **Corrected again 2026-11-13 (fresh plan review, gap 2):** one loaded child is not a loaded page. A page, and each Share and Export task panel, is ready only when two reads of its content a moment apart are equal and none of it is loading. Done when, in addition: tests show a page that fills in two steps recorded in full, and one that keeps changing failing the capture with the previous file unchanged.
- [x] Capture Word's Backstage on this PC with `python scripts/capture-ui.py --app word --backstage` into `design/inventory/word/backstage.json`. Done when: every entry of Word's own navigation list is recorded as a page or an action, each page with its expanded child records, and `python scripts/check-inventory.py design/inventory/word` exits 0 (which runs the reconciliation and behaviour checks above). Cheaper substitute: page names only. **Corrected 2026-11-13:** was the fourteen pages named in this section.
- [x] Commit: `inventory: capture Word Backstage pages`

**Measured:** 2026-11-13, Word `16.0.20527.20150` (`fhd-100`): `design/inventory/word/backstage.json` holds 282 records (9 pages, the three navigation actions, 63 groups, the rest controls and menu items, 221 with a behaviour sentence); 99 baseline ids are listed absent in five documented reasons. The capture records no list entry, person, date, printer, e-mail address or organisation name; a second capture gave the same 282 ids. **Corrected 2026-11-13 (completion review, gap 3):** 61 groups, 121 controls and 90 menu items, and ten pages once Save on a never-saved document is recorded as the page it shows; the earlier count of groups was wrong. **Corrected again 2026-11-13 (fresh plan review, gap 2):** with every page read until it settles, Home also shows five suggested prompts that load late, so the file holds 287 records (126 controls) and 226 behaviour sentences; three captures gave the same 287 ids. **Corrected again 2026-11-13 (fresh round 1):** with Change File Type's eight formats recorded, 295 records (134 controls) and 234 behaviour sentences.

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` and `-p "test_word_backstage.py"` pass (**Corrected 2026-11-13, fresh plan review gap 1:** the librarys tests added), `python scripts/check-inventory.py design/inventory/word` exits 0, which runs `validate_word_backstage` on `design/inventory/word/backstage.json`. **Corrected 2026-11-13:** was a count of 14 pages.

> **Verified:** 2026-11-13 | §6 | f8537dc1eab7900e5db59b1df78bea6729b287e9
> **Review:** `docs/reviews/d02-t01-s6.json`

## 7. Excel Ribbon

Every built-in Excel tab (File, Home, Insert, Draw, Page Layout, Formulas, Data, Review, View, Automate, Help) and contextual tab (Table Design, PivotTable Analyze, PivotTable Design, Chart Design, Format, Picture Format, Shape Format, Sparkline, Header and Footer, Query, Timeline, Slicer).

**Phase:** 5
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
- [ ] Capture every Excel tab in the Simplified Ribbon into `design/inventory/excel/ribbon-simplified.json` with `--layout simplified`, including each overflow menu. Done when: every Classic tab has a Simplified counterpart and the checker passes. Cheaper substitute: assuming the Simplified Ribbon is the Classic one with smaller buttons. **Corrected 2026-10-20 (D02 T01 §2):** the reference build may not offer a Simplified Ribbon (Word build 16.0.20430.20182's Ribbon Display Options has no Classic or Simplified switch, and the 2024 baseline lists `SingleLineRibbonToggle` only for Word and Outlook, outside the ribbon). First record in `design/inventory/REFERENCE.md` `## Layout choices` whether this build offers it and the exact steps that switch it; capture only if it does, otherwise record the absence there, which the owner question in the phase 2 run file covers. Done when (corrected): if the build offers the switch, every Classic tab has a Simplified counterpart and the checker passes; if it does not, `REFERENCE.md` records the absence and where it was looked for.
- [ ] Make `scripts/capture-ui.py` leave no Excel process behind: on 2026-10-20 a probe's Excel stayed running, hidden, after `Quit` and the release of every COM reference, until it was force-closed. Find what keeps it alive and end it through Excel's own shutdown. Done when: an Excel capture run exits 0 and no `EXCEL.EXE` it started is running afterwards. Cheaper substitute: killing the process after a timeout.
- [ ] Commit: `inventory: capture Excel ribbon and contextual tabs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/excel/ribbon.json` exits 0 and the file holds at least 11 `tab` and 12 `contextualTab` records.

## 8. Excel Panes, Dialogs

Excel beyond the ribbon: Name Box and formula bar, sheet tabs and their context menu, Backstage pages, Excel Options, task panes (Format Cells pane forms, PivotTable Fields, Queries and Connections, Selection, Clipboard), status bar aggregates and their customise menu, and dialogs (Format Cells, Insert Function, Function Arguments, Name Manager, Data Validation, Conditional Formatting Rules Manager, Sort, Paste Special, Go To Special, Goal Seek, Scenario Manager).

**Phase:** 5
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
- [ ] Transcribe Excel shortcuts into `design/inventory/excel/shortcuts.json` with `shortcut`, `behaviour`, `source` and the target command id where one exists. Done when: every table on the source page is covered, the file holds at least 50 records and `python scripts/check-inventory.py design/inventory` exits 0 with §17's conflict check. Cheaper substitute: the twenty most common shortcuts. **Corrected 2026-11-12:** moved here from §17 by D03 T01 §30 (decision 44).
- [ ] Commit: `inventory: capture Excel Backstage, formula bar, panes and dialogs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/excel` exits 0 and `design/inventory/excel/dialogs.json` holds at least 11 `dialog` records.

## 9. PowerPoint Ribbon

Every built-in PowerPoint tab (File, Home, Insert, Draw, Design, Transitions, Animations, Slide Show, Record, Review, View, Help) and contextual tab (Shape Format, Picture Format, Table Design, Table Layout, Chart Design, Chart Format, SmartArt Design, Video Format, Playback, Audio Format, Equation).

**Phase:** 5
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
- [ ] Capture every PowerPoint tab in the Simplified Ribbon into `design/inventory/powerpoint/ribbon-simplified.json` with `--layout simplified`, including each overflow menu. Done when: every Classic tab has a Simplified counterpart and the checker passes. Cheaper substitute: assuming the Simplified Ribbon is the Classic one with smaller buttons. **Corrected 2026-10-20 (D02 T01 §2):** the reference build may not offer a Simplified Ribbon (Word build 16.0.20430.20182's Ribbon Display Options has no Classic or Simplified switch, and the 2024 baseline lists `SingleLineRibbonToggle` only for Word and Outlook, outside the ribbon). First record in `design/inventory/REFERENCE.md` `## Layout choices` whether this build offers it and the exact steps that switch it; capture only if it does, otherwise record the absence there, which the owner question in the phase 2 run file covers. Done when (corrected): if the build offers the switch, every Classic tab has a Simplified counterpart and the checker passes; if it does not, `REFERENCE.md` records the absence and where it was looked for.
- [ ] Commit: `inventory: capture PowerPoint ribbon and contextual tabs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/powerpoint/ribbon.json` exits 0 and the file holds at least 12 `tab` and 11 `contextualTab` records.

## 10. PowerPoint Panes, Dialogs

PowerPoint beyond the ribbon: views (Normal, Outline, Slide Sorter, Notes Page, Reading, Slide Master, Handout Master, Notes Master, Slide Show, Presenter View), the thumbnail pane, notes pane, status bar, Backstage and Options, task panes (Animation Pane, Selection, Format Shape, Design Ideas), and dialogs.

**Phase:** 5
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
- [ ] Transcribe PowerPoint shortcuts into `design/inventory/powerpoint/shortcuts.json`, including slide show shortcuts with `shortcut`, `behaviour`, `source` and the target command id where one exists. Done when: every table on the source page is covered, the file holds at least 50 records and `python scripts/check-inventory.py design/inventory` exits 0 with §17's conflict check. Cheaper substitute: editing shortcuts only. **Corrected 2026-11-12:** moved here from §17 by D03 T01 §30 (decision 44).
- [ ] Commit: `inventory: capture PowerPoint views, Backstage, panes and dialogs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/powerpoint` exits 0 and `design/inventory/powerpoint/panes.json` holds at least 10 `view` records.

## 11. Visio Ribbon

Every built-in Visio tab (File, Home, Insert, Draw, Design, Data, Process, Review, View, Help, plus Developer when enabled) and contextual tabs (Shape Format, Picture Format, Container Format, Table Design and Layout where present, Data Graphic, Callout).

**Answered 2026-10-20:** the owner registered the Visio licence; the subscription store now holds `visioproretail` (D02 T01 §2, `design/inventory/REFERENCE.md` `## Licensing`). The capture refuses if Visio still shows a licence notice.

**Phase:** 5
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

## 12. Visio Panes, Dialogs

Visio beyond the ribbon: the Shapes pane (stencil list, More Shapes menu, Quick Shapes, search), drawing page tabs, rulers, grid, Pan and Zoom, Size and Position, Shape Data, Format Shape panes, the template gallery on New, Backstage and Options, status bar, and dialogs (Page Setup, Shape Data, Define Shape Data, Layers, Data Selector).

**Answered 2026-10-20:** the owner registered the Visio licence; the subscription store now holds `visioproretail` (D02 T01 §2, `design/inventory/REFERENCE.md` `## Licensing`). The capture refuses if Visio still shows a licence notice.

**Phase:** 5
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
- [ ] Transcribe Visio shortcuts into `design/inventory/visio/shortcuts.json` with `shortcut`, `behaviour`, `source` and the target command id where one exists. Done when: every table on the source page is covered, the file holds at least 50 records and `python scripts/check-inventory.py design/inventory` exits 0 with §17's conflict check. Cheaper substitute: the twenty most common shortcuts. **Corrected 2026-11-12:** moved here from §17 by D03 T01 §30 (decision 44).
- [ ] Commit: `inventory: capture Visio panes, Backstage and dialogs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/visio` exits 0 and `design/inventory/visio/dialogs.json` holds at least 5 `dialog` records.

## 13. Project Ribbon

Every built-in Project tab (File, Task, Resource, Report, Project, View, Help, plus Developer when enabled) and contextual Format tabs (Gantt Chart Tools, Timeline Tools, Task Usage Tools, Resource Sheet Tools, Report Design and Report Table and Chart tabs).

**Phase:** 5
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

## 14. Project Panes, Dialogs

Project beyond the ribbon: built-in views (Gantt Chart, Tracking Gantt, Task Usage, Team Planner, Network Diagram, Calendar, Resource Sheet, Resource Usage, Resource Graph, Timeline, Task Sheet, Task Form, Resource Form), the view bar and split view, default tables and their columns, Backstage and Project Options, status bar, and dialogs (Task Information, Resource Information, Project Information, Change Working Time, Assign Resources, Level Resources, Baseline).

**Phase:** 5
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
- [ ] Transcribe Project shortcuts into `design/inventory/project/shortcuts.json` with `shortcut`, `behaviour`, `source` and the target command id where one exists. Done when: every table on the source page is covered, the file holds at least 50 records and `python scripts/check-inventory.py design/inventory` exits 0 with §17's conflict check. Cheaper substitute: the twenty most common shortcuts. **Corrected 2026-11-12:** moved here from §17 by D03 T01 §30 (decision 44).
- [ ] Commit: `inventory: capture Project views, Backstage, panes and dialogs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/project` exits 0 and `design/inventory/project/panes.json` holds at least 13 `view` records.

## 15. Outlook Ribbons

Outlook has a ribbon per module (Mail, Calendar, People, Tasks) and per item window (new message, read message, appointment, meeting, contact, task). The capture follows the Outlook client chosen in §2.

**Phase:** 5
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
- [ ] Capture every Outlook tab in the Simplified Ribbon into `design/inventory/outlook/ribbon-simplified.json` with `--layout simplified`, including each overflow menu. Done when: every Classic tab has a Simplified counterpart and the checker passes. Cheaper substitute: assuming the Simplified Ribbon is the Classic one with smaller buttons. **Corrected 2026-10-20 (D02 T01 §2):** the reference build may not offer a Simplified Ribbon (Word build 16.0.20430.20182's Ribbon Display Options has no Classic or Simplified switch, and the 2024 baseline lists `SingleLineRibbonToggle` only for Word and Outlook, outside the ribbon). First record in `design/inventory/REFERENCE.md` `## Layout choices` whether this build offers it and the exact steps that switch it; capture only if it does, otherwise record the absence there, which the owner question in the phase 2 run file covers. Done when (corrected): if the build offers the switch, every Classic tab has a Simplified counterpart and the checker passes; if it does not, `REFERENCE.md` records the absence and where it was looked for.
- [ ] Add the Simplified Ribbon switch to `scripts/capture-ui.py --layout simplified`, using the steps recorded in `design/inventory/REFERENCE.md` `## Layout choices`, and restore the operator's setting afterwards. Done when: the same Outlook tab captured in both layouts produces two files that pass the checker, and the setting reads as it did before the run. Cheaper substitute: deriving the Simplified layout from the Classic capture. (Moved from D02 T01 §3.)
- [ ] Refresh `outlook.explorer.shell.*` and `outlook.compose.shell.*` in `design/inventory/shell/chrome.json` with live attended UIA measurements (`source: "uia:<build>"`, `captureProfile: "fhd-100"` and non-zero `bounds`) for classic Outlook's explorer shell and item-window shell (title bar, Quick Access Toolbar, tab row and search placement). Done when: every `outlook.explorer.shell.*` and `outlook.compose.shell.*` record in `design/inventory/shell/chrome.json` has `source: "uia:<build>"` and non-zero `bounds`, and `python scripts/check-inventory.py --require-behaviour design/inventory/shell/chrome.json` exits 0. Cheaper substitute: leaving Outlook's shell overrides with baseline-only provenance after attended Outlook capture runs. (From D02 T01 §4 completion review.)
- [ ] Commit: `inventory: capture Outlook module and item window ribbons`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/outlook/ribbon.json` exits 0 and the file has records under `outlook.mail`, `outlook.calendar`, `outlook.people`, `outlook.tasks` and `outlook.compose`.

## 16. Outlook Panes, Dialogs

Outlook's layout beyond the ribbon: navigation bar, folder pane, message list with its columns and conversation grouping, reading pane positions, To-Do Bar, calendar views (Day, Work Week, Week, Month, Schedule), People views, search scopes, Backstage (Info with Account Settings, Rules, Automatic Replies), Outlook Options, and dialogs (Account Settings, Rules and Alerts, Signatures and Stationery, Categories, Address Book).

**Phase:** 5
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
- [ ] Transcribe Outlook shortcuts into `design/inventory/outlook/shortcuts.json` for the Outlook client chosen in §2 with `shortcut`, `behaviour`, `source` and the target command id where one exists. Done when: every table on the source page is covered, the file holds at least 50 records and `python scripts/check-inventory.py design/inventory` exits 0 with §17's conflict check. Cheaper substitute: mixing classic and new Outlook shortcuts. **Corrected 2026-11-12:** moved here from §17 by D03 T01 §30 (decision 44).
- [ ] Commit: `inventory: capture Outlook modules, panes, views and dialogs`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/outlook` exits 0 and `design/inventory/outlook/panes.json` holds at least 5 calendar `view` records.

## 17. Keyboard Shortcuts

Muscle memory is part of parity. Each app's published shortcut list becomes `shortcut` records linked to the command they invoke.

**Phase:** 2
**Needs:** none
**Surface:** no

> **Started:** 2026-11-13T04:05:06Z

**Build order:**

1. Record each app's default shortcuts as key chords with our own short action names into `design/inventory/<app>/shortcuts.json`; Microsoft's published shortcut lists may be read as a checklist, but none of their text or links is stored (**Corrected 2026-10-20:** said "transcribe"). Done when: Word's file passes the checker (**Corrected 2026-11-12**, D03 T01 §30, decision 44: was six files; each later app's shortcuts are recorded with that app's inventory, in §8, §10, §12, §14 and §16, since a shortcut names the command id of an inventory captured then).

- [x] Transcribe Word shortcuts into `design/inventory/word/shortcuts.json` with `shortcut`, `behaviour`, `source` and the target command id where one exists. Done when: every table on the source page is covered. Cheaper substitute: the twenty most common shortcuts. **Corrected 2026-11-13 (fact check at start):** the file already holds 255 `shortcut` records read from Word's own key table (D02 T01 §20, source `listcommands`), each with a target and none with a behaviour. This section keeps them and: reads each of the 28 tables of Microsoft's published Windows list for Word as a checklist; for each row, finds the `listcommands` record of the same chord and scope or adds a `shortcut` record for it (keys Word's table does not list: ribbon, dialog, table, outline, Read Mode and selection keys), with source `published:<date read>` (a new provenance form: the list was read on that date; no text or link of it is stored) and a target where a command record exists; gives every record a `scope` (a new field with a fixed set: `document`, `table`, `outline`, `read-mode`, `ribbon`, `dialog`, `backstage`, `print-preview`, `mail-merge`, `field`, `ime`) and a behaviour sentence in our own words; and documents the provenance and the scopes in `design/inventory/REFERENCE.md`. Done when: a coverage table in the section's findings file maps each of the 28 tables, by our own scope and row count, to the record ids covering it, with no row left unmapped, and the checker requires `scope` and `behaviour` on every shortcut record. **Corrected 2026-11-13 (plan review, gaps 2, 3 and 5):** which command a chord runs is asked of the reference build itself (Word's `FindKey` through its object model, in a document) for every chord two records share and every chord the published list gives; a binding Word runs only in some state keeps that state in a new optional `condition` field, in our own words; shortcuts the published list gives in its prose rather than its tables (closing or moving between task panes, moving between the window's regions) are on the checklist too, with the scopes `task-pane` and `window` added; and the checklist itself is `COVERAGE` in a new `scripts/lib/word_shortcuts.py`: for each of the tables and the prose passages, our own short name, its row count and the ids that cover each row, and the `listcommands` ids besides. The checker refuses a shortcut record `COVERAGE` does not list, an id it lists that the file lacks, a table whose ids are fewer than its rows, a record without `scope` or `behaviour`, and a scope outside the set. Done when, in addition: tests show each of those refusals, and the FindKey answers are in the gates. **Measured 2026-11-13:** 352 records: 252 from Word's key table and 100 from the published list, covering its 28 tables (292 rows) and its prose; `FindKey` in the reference build settled the three chords Word's table gives twice and corrected five of the list's keys. **Corrected 2026-11-13 (build):** the scopes `field` and `mail-merge` are not kept, since those keys work in the document like any other; `task-pane` and `window` are, as the plan review asked. **Corrected again 2026-11-13 (round 1):** a dialog's keys are their own records, so 353 records, 101 of them from the published list.
- [x] Add a conflict check to `scripts/check-inventory.py` refusing two `shortcut` records with the same key chord and scope in one app. Done when: a duplicate chord fixture fails. Cheaper substitute: detecting duplicates by eye. **Corrected 2026-11-13 (fact check at start):** a chord is compared in one canonical form (modifiers in the order Ctrl, Alt, Shift, so `Alt+Ctrl+V` and `Ctrl+Alt+V` are one chord), and the three chords Word's own table gives two records (`Ctrl+0`, `Alt+Ctrl+V`, `Alt+Shift+A`) are resolved by their scope or, where Word itself assigns one chord twice in one scope, kept as one record with the other listed in REFERENCE.md. Done when, in addition: tests show the same chord written in two modifier orders refused, and the same chord in two scopes accepted. **Corrected 2026-11-13 (plan review, gap 4):** a chord is keys pressed together joined by `+`; a sequence is chords pressed one after another joined by `, ` (as the ribbon's KeyTips are); a key that is itself `+` or `,` is written `Plus` or `Comma`; and each alternative binding of one action is its own record with the same target. Done when, in addition: tests show a sequence and the chord of the same keys held apart, `Ctrl+Plus` parsed as one key with a modifier, and two alternatives each checked for conflicts.
- [x] Make `scripts/word-commands.py` keep what this section adds when it regenerates the file: the `scope`, `condition` and `behaviour` of each record it writes again, carried by id, and every `published:` record, kept; a `listcommands` binding that changes its chord or disappears refuses the run, writing nothing and naming each, so it is reconciled by hand. Done when: a test reruns the producer with a fake key table over the committed file and the result is the same file, and one with a moved binding exits 1 and leaves the file unchanged (**Added 2026-11-13, plan review gap 1**). Cheaper substitute: never rerunning the producer.
- [x] Commit: `inventory: add keyboard shortcut inventory`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory` exits 0 and `design/inventory/word/shortcuts.json` holds at least 50 records (**Corrected 2026-11-12**, D03 T01 §30: was each of six files; the other five are checked in §8, §10, §12, §14 and §16). **Corrected 2026-11-13 (fact check at start):** and `python -m unittest discover -s scripts/tests -p "test_check_inventory.py"` passes.

> **Verified:** 2026-11-13 | §17 | 5e98aebc39800de390781a4e89bc9c4592139a32
> **Review:** `docs/reviews/d02-t01-s17.json`

## 18. Inventory Coverage Report

The report turns the inventory into the parity scoreboard: counts per app and kind now, and implemented versus total once application sections start citing ids.

**Phase:** 2
**Needs:** none
**Surface:** no

> **Started:** 2026-11-13T05:05:40Z

**Build order:**

1. Write `scripts/inventory-report.py`. Done when: it prints counts per app and kind and writes `design/inventory/COVERAGE.md`.

- [x] Add a baseline comparison to `scripts/inventory-report.py` listing every `idMso` in `design/inventory/<app>/baseline.json` (§19) that is visible in the reference build but missing from the captured inventory. Done when: removing one captured Word control makes the report name its `idMso`. Cheaper substitute: trusting the capture to be complete. **Corrected 2026-11-13 (fact check at start):** whether a baseline control is visible cannot be read for a ribbon control no capture opened, so the report names a baseline `idMso` as missing when it sits on a surface the app's inventory captured (a tab, contextual tab or Backstage page recorded with that `idMso`, by the baseline row's `tab`), no record of the app's inventory or the shell's holds it, and no documented absence lists it (`ABSENT` in `scripts/lib/word_backstage.py` for Backstage; the absent tab rows of REFERENCE.md's Word ribbon reconciliation for tabs). Baseline rows on a surface not yet captured are counted per placement as `pending surface`, never as missing. `COVERAGE.md` gives the counts; `--missing` prints the names. Done when, in addition: a test shows a documented absence not named and a row on an uncaptured surface counted as pending. **Corrected 2026-11-13 (plan review, gap 1):** a baseline row is matched as one occurrence, not app-wide: it is captured only when a record with its `idMso` sits under the record of its own `tab` (by the parent chain, or the record's own `tab`), so `BlockAuthorsMenu` on Review and on Developer are two occurrences; a row with no `tab` (the Quick Access Toolbar's, the shell's) matches any record of the app or the shell holding its `idMso`. Done when, in addition: removing one occurrence of an `idMso` while another remains names the removed one. **Measured 2026-11-13:** of Word's 5,638 baseline rows, 701 are captured, 1,288 documented absent, 1,344 unmatched on captured tabs and pages, 2,106 on surfaces not yet captured (context menus, commands not on the ribbon) and 199 without an `idMso`; Excel, PowerPoint, Outlook, Visio and Project are `pending inventory`. **Corrected 2026-11-13 (build):** a baseline row with no `idMso` is counted in its own column, since nothing can match it. **Corrected again 2026-11-13 (round 1):** a row on no tab now matches any record of the app or the shell, as gap 1 said, so 1,184 rows are captured and 1,623 pending.
- [x] Count records per app and `kind` in `scripts/inventory-report.py`. Done when: `python scripts/inventory-report.py` prints a table with one row per app. Cheaper substitute: a file count.
- [x] Add an implemented count in `scripts/inventory-report.py` by scanning `todo/**/*.md` for `[x]` sections whose `> **Implements:**` lines name inventory ids (§22). Done when: a fixture stamped section implementing the Word Bold control counts it as implemented. Cheaper substitute: a hand-maintained percentage. **Corrected 2026-11-13 (fact check at start):** no section carries a `> **Implements:**` line yet (§22 introduces it), so the count is proved on fixtures and reads 0 in the committed report; a stamped section is one the TODO graph reads as verified, and the claim reader (blockquote lines opening `> **Implements:**`, each backticked id a claim, an id anywhere else none) lives in a library §22's `--owners` reuses, `scripts/lib/inventory_claims.py`. **Corrected 2026-11-13 (plan review, gap 4):** an implemented record is one a verified section claims, counted once however many claim it. Done when, in addition: fixtures show an unstamped section's claim, a section with every item ticked and no stamp, and an id named outside an `Implements` line each counting nothing, and unstamping the Bold fixture taking Bold out of the count.
- [x] Add `--app`, `--kind` and `--cited-in <file>` filters to `scripts/inventory-report.py`, where `--cited-in` reports the percentage of matching record ids that appear in the file, and `--control-types` reports which `controlType` values the file names. Done when: a fixture spec citing half the Word tabs reports 50 percent for `--app word --kind tab`. Cheaper substitute: a citation count with no denominator. **Corrected 2026-11-13 (plan review, gap 5):** a filtered run only prints and never writes `COVERAGE.md`, which only the unfiltered run writes, whole; an id is cited when it appears in the file as a whole token (bounded by characters an id cannot hold), so `word.home.bold` does not cite `word.home.bold-2`; a filter that matches no record prints `0 of 0` and exits 0; and `--control-types` prints, for the matching records, each `controlType` with how many are cited and how many are not. Done when, in addition: tests show a filtered run leaving the committed report as it was, the empty filter, the whole-token rule and the control types.
- [x] Write `design/inventory/COVERAGE.md` atomically with rows at most 120 characters. Done when: `python scripts/check-design-doc.py design/inventory/COVERAGE.md` exits 0. Cheaper substitute: printing to the console only. **Corrected 2026-11-13 (fact check at start):** the report holds no date, time or other value of the run, so writing it twice gives the same bytes and `--check` compares them. **Corrected 2026-11-13 (plan review, gap 6):** the report is published through the repository's atomic write (temporary file, then replace). Done when, in addition: a test where the write or the replace fails exits non-zero and leaves the previous report, and the written report read back holds the expected counts and regenerates to the same bytes.
- [x] Report an app that has a `baseline.json` and no captured record file as one `pending inventory` row in `scripts/inventory-report.py`, with its baseline count and exit 0, so the report is built and proved on the inventories that exist (the shell's and Word's). Done when: a test over a fixture with one captured app and one baseline-only app prints the captured app's counts and the other app's `pending inventory` row, and exits 0. Cheaper substitute: failing, or printing a row of zeros, for an app nobody has captured yet. **Corrected 2026-11-12:** added by D03 T01 §30 (decision 44 of `docs/specs/2026-10-23-campaign-scope-design.md`): this section depended on every app's inventory (§6, §8, §10, §12, §14, §16) and on §17, none of which the tool reads to be built; it now depends on §4, §5, §19 and §25, and D03 T01 §13 requires a report with no pending app.
- [x] Add `--check` to `scripts/inventory-report.py`: generate the report again and exit 1, naming `design/inventory/COVERAGE.md`, when the committed file differs; and run it from `scripts/hooks/pre-commit` for commits that stage `design/inventory/`, with a test in `scripts/tests/test_pre_commit_hook.py`. Done when: a test shows a stale `COVERAGE.md` exits 1 and a fresh one exits 0, and staging a new inventory record without the regenerated report refuses the commit. Cheaper substitute: a checklist item in each inventory section asking for the report to be run again, which nothing enforces. **Corrected 2026-11-12:** added by D03 T01 §30, so the report is run again as each inventory lands. **Corrected 2026-11-13 (fact check at start):** the hook now leaves at once unless `todo/` is staged; it is restructured so a commit staging `design/inventory/` runs `inventory-report.py --check`, one staging `todo/` runs the plan check, and one staging both runs both, with the existing hook tests still passing. **Corrected 2026-11-13 (plan review, gaps 2 and 3):** the coverage check also runs for a commit staging `todo/`, since a stamp changes the implemented count; and it reads what is committed: `design/inventory/` (with `COVERAGE.md`) and `todo/` may hold no unstaged or untracked change when it runs. Done when, in addition: tests show stamping and unstamping an implementing section without regenerating the report refused, and a regenerated but unstaged `COVERAGE.md` refused.
- [x] Write `scripts/tests/test_inventory_report.py`. Done when: the suite passes and fails when the implemented scan is disabled.
- [x] Commit: `inventory: add coverage report`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_inventory_report.py"` passes and `python scripts/inventory-report.py` exits 0.

> **Verified:** 2026-11-13 | §18 | c7fda83c4773e05f833aca42cb9aafc23018d2bd
> **Review:** `docs/reviews/d02-t01-s18.json`

## 19. Control ID Baseline

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

## 20. Word Command Catalogue

> **Started:** 2026-10-20T02:59:39Z

Word can list every command it has, with the keyboard shortcut assigned to each, through its built-in `ListCommands` command. Run through COM, this captures commands that have no ribbon button and the complete default shortcut map, which the support pages only partly document.

**Phase:** 2
**Needs:** office, windows-host
**Surface:** no

**Build order:**

1. Run `scripts/word-commands.py` against a Word instance it starts itself. Done when: `design/inventory/word/commands.json` holds every listed command.
2. Link commands to ribbon records and shortcuts. Done when: shortcut records in `design/inventory/word/shortcuts.json` reference command records.

- [x] Write `scripts/word-commands.py` that starts its own hidden Word instance through COM (`win32com.client.DispatchEx("Word.Application")`), calls `ListCommands(True)` on a new document, reads the resulting table, and quits that instance without saving. Done when: the script never attaches to the operator's running Word and leaves no `WINWORD.EXE` it started behind. Cheaper substitute: `GetActiveObject`, which drives the operator's own Word.
- [x] Write each row to `design/inventory/word/commands.json` as a `command` record with name, modifiers, key and the menu path Word reports. Done when: the record count equals the table's row count. **Corrected 2026-10-20:** Word build 20430's table has three columns (name, modifiers, key) and no menu column, and a name can repeat for a second shortcut or for a different command, which the table cannot tell apart; so each row is one `command` record (repeats get `-2`, `-3`) and each keyed row also one `shortcut` record in `shortcuts.json`. The schema stores a key chord whole as `shortcut`, so a keyed command record carries `shortcut` (modifiers then key, as Word lists them), and `scripts/word-commands.py` refuses any row whose chord would not split back into that row's modifiers (a run of `Ctrl+`, `Alt+`, `Shift+`) and key, so both values are kept exactly. Cheaper substitute: keeping only commands that have a shortcut.
- [x] Link each command to its ribbon control by `idMso` or label where they match, in `scripts/word-commands.py`. Done when: unmatched commands are listed in the run output for review. **Corrected 2026-10-20:** matched by `idMso` against `design/inventory/word/baseline.json` (no Word ribbon records exist yet); the run prints the counts and writes the unmatched names to `build/word-commands-unmatched.txt`; label matching against captured ribbon controls moves to the Word ribbon capture. -> XREF: D02 T01 §5 Cheaper substitute: silent best-effort matching.
- [x] Commit: `inventory: capture Word command catalogue`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/word/commands.json` exits 0 and the file holds at least 1,000 `command` records.

> **Verified:** 2026-10-20 | §20 | c6ee91afdaad1bd44488a196a51b1b75f028a052
> **Review:** `docs/reviews/d02-t01-s20.json`

## 21. Microsoft-Free Inventory

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

## 22. Inventory Ownership Check

> **Started:** 2026-11-13T14:12:14Z

Parity is 1:1: every element the inventory records for Word, Excel, PowerPoint, Outlook, Visio and Project is built by exactly the TODO section that cites it, so the plan always says what to implement where. A section claims a record only on a `> **Implements:**` line listing the record ids in backticks; an id named anywhere else (an example, a capture step, a test) claims nothing. This section builds the check that proves it at record level (every `control`, `tab`, `contextualTab`, `group`, menu item, `dialog`, `pane`, `view`, Backstage page, Options setting, status bar item, `command` and `shortcut` record), not one section per group. D03 T01 §13 runs it to zero and makes it a standing gate. Owner request 2026-10-21: "We need to match Word, Excel, PowerPoint, Outlook, Visio, Projects feature per feature 1:1."

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Add `--owners` to `scripts/inventory-report.py`, reading `> **Implements:**` lines from `todo/**/TODO-*.md`. Done when: it lists every unowned record id per app and kind.
2. Add `--check` so a non-empty unowned list exits 1. Done when: the fixture tests below pass and fail as described.

- [x] Document the `> **Implements:**` section line in `todo/README.md`: one or more blockquote lines in a section body, each listing backticked inventory record ids the section builds. Done when: the README names the line, its form and that nothing else claims a record. Cheaper substitute: treating every backticked id in a section as a claim.
- [x] Add a claim reader to `scripts/inventory-report.py` that collects the ids on `> **Implements:**` lines in `todo/**/TODO-*.md`, keyed by the section reference (`DNN TNN §N`), and ignores ids named anywhere else. Done when: a fixture section with the Bold control on its `> **Implements:**` line maps that id to its reference, and the same id in a checklist item of another fixture section claims nothing. Cheaper substitute: a plain substring search over the whole tree with no section attribution. **Corrected 2026-11-13 (fact check at start):** the reader exists: D02 T01 §18 shipped `scripts/lib/inventory_claims.py` with `claims` (the ids on a section's `> **Implements:**` lines) and `implemented` (the claims of stamped sections, for coverage). This item adds `owners` beside them: every section's claims, stamped or not, as record id to the references claiming it, since ownership is what the plan says, not what is built. The sections come from `todo_graph.graph()`, as the report already reads them, so the TODO tree has one reader.
- [x] Add `--owners` to `scripts/inventory-report.py` listing, per app and `kind`, every captured record id in `design/inventory/<app>/*.json` that no section cites, with counts owned and total. Done when: removing one claimed id from a fixture `> **Implements:**` line makes the report name that id. Cheaper substitute: checking only `group`, `dialog`, `pane` and `view` ids. **Corrected 2026-11-13 (fact check at start):** the report already has `--app` and `--check` (the staleness of `COVERAGE.md`, D02 T01 §18); with `--owners` they filter and check ownership, and without it they are unchanged. `--owners` prints for each app its state and its owned and total counts, then the counts for each `kind`, then each unowned id. With `--check` the unowned ids are printed only where they are refusals, so a commit hook does not print the 11,478 records Word holds today while Word is pending.
- [x] Report a claimed id the inventory does not hold in `scripts/inventory-report.py --owners`, naming the claiming section. Done when: a fixture `> **Implements:**` line naming an id absent from the fixture inventory is reported with its `DNN TNN §N`. Cheaper substitute: ignoring unknown ids. **Corrected 2026-11-13 (fact check at start):** an unknown or doubly claimed id belongs to the app its first dotted part names (`word.home.font.bold` is Word's), which is how `--app` filters them.
- [x] Report an id claimed on the `> **Implements:**` lines of more than one section in `scripts/inventory-report.py --owners`. Done when: a fixture with two sections claiming one id reports both references. Cheaper substitute: allowing silent co-ownership.
- [x] Add `--check` to `scripts/inventory-report.py --owners`: exit 1 while any record is unowned, any claim is unknown or any id has two owners; exit 0 otherwise. Done when: the three fixtures above exit 1 and a fully cited fixture exits 0. Cheaper substitute: always exiting 0 and relying on someone reading the list. **Corrected 2026-11-13 (round 1, finding 1):** the build ended quietly with exit 0 when the reader of its output closed the pipe (`--owners | head`), and did so under `--check` too, so a failing check piped to a reader that had gone reported success. The verdict is now decided before a line is written: the refusals go to stderr first, and a reader that stopped listening only ends the writing, never changing the exit code; a report that could not be written for another reason exits 1. Tests hold both, one of them with a real closed pipe on the repository's own inventory.
- [x] Add `--app` filtering to `--owners` so one app can be brought to zero at a time. Done when: `--owners --check --app word` ignores unowned Excel ids in a fixture. Cheaper substitute: a whole-tree check only. **Corrected 2026-11-13 (plan review, gap 2):** with `--owners`, an `--app` that is not an app folder of the inventory exits 2 naming the apps it could have been, so a mistyped name cannot pass a check by selecting nothing. Done when, in addition: `--owners --check --all --app wrod` exits 2 naming the apps, and `--owners --check --all --app excel` on a fixture where Excel has a baseline and no captured record exits 1 naming Excel as having no captured record. **Measured 2026-11-13 (build):** the fixture's Excel has a baseline and no captured record, so the test of the filter uses the shell: `--owners --check --app word` passes while the shell has an unowned record and an unknown, doubled claim, and `--app shell` refuses all three.
- [x] Give every app (the shell counts as one) one of three states in `scripts/inventory-report.py --owners`, printed beside its counts: `pending inventory` (no captured record), `pending authoring` (captured records, and the section that authors the app's domain not yet stamped, whether or not some records are already claimed) and `enforced` (that authoring section stamped). The authoring section of each app is read from `design/inventory/authoring.json`, which this item adds (shell D03 T01 §17, word §19, excel §20, powerpoint §21, outlook §22, visio §23, project §24) and `python scripts/check-inventory.py` refuses when an app folder has no entry or an entry names no section; whether it is stamped is read from its Implementation Order row. Done when: a test over a fixture with one app in each state prints the three states, a fixture app with some records claimed and its authoring section open prints `pending authoring`, and the same fixture with that section stamped prints `enforced`. Cheaper substitute: treating every unowned record as a failure, which refuses every commit between an app's capture and its authoring. **Corrected 2026-11-12:** added by D03 T01 §30 after its plan review (gap 1): the shell's and Word's records are captured long before D03 T01 §17 and §19 write the sections that own them. **Corrected again 2026-11-12:** D03 T01 §30's round 1 found that enforcing from the first claim refuses the authoring itself: D03 T01 §17's platform sections claim Word's Help tab records before D03 T01 §19 has written Word's other owners, and §19 commits its files one at a time. The boundary is the stamp of the app's authoring section. **Corrected 2026-11-13 (fact check at start):** `design/inventory/authoring.json` is one JSON object mapping each app folder (`shell`, `word`, `excel`, `powerpoint`, `outlook`, `visio`, `project`) to its section reference. `scripts/check-inventory.py` holds it in a run over the whole inventory: the repository's inventory must have the file, an inventory that has it must name a section for every app folder and no other key, and each reference must be a section the TODO tree holds, which the checker asks `todo_graph.graph()` (a tree that cannot be read is exit 2). The file is left out of the record files the checker validates, as the baseline manifest is. `--owners` exits 2 naming an app folder the file does not name. **Corrected 2026-11-13 (plan review, gap 1):** the file has one reader, `scripts/lib/inventory_authoring.py` (new), which the checker and `--owners` both call, so neither can accept what the other refuses: the file is a JSON object, every app folder of the inventory is a key, no key is anything else, every value is a section reference, and every reference is a section the TODO tree holds. `--owners` exits 2 with the reader's line for each of these (a missing file included), never reading an unresolved section as pending; the checker reports the same lines as problems in a whole-inventory run. Whether a reference is a section is asked of `scripts/lib/todo_graph.py` (`section_exists`, new: the TODO file and its `## N.` heading), not of a whole graph read, which needs the repository's history and so cannot run in the private copy `scripts/mutation-sweep-inventory.py` tests the checker in; that copy takes `todo/` as well, so the checker's tests find the sections there. Done when, in addition: tests show `--owners` exiting 2, and the checker reporting a problem, for a missing file, a file that is not an object, a missing app key, a key that is no app folder, a value that is no section reference and a reference to a section that does not exist.
- [x] Make `--owners --check` strict per app from the stamp of its authoring section: an `enforced` app with an unowned `build` or `equivalent` record exits 1, a pending app does not (its unowned records are counted, not refused), and an unknown or doubly owned claim exits 1 in every state. Done when: tests show a pending-authoring app with every record unowned exits 0 and names the app as pending, the same app with half its records claimed still exits 0, the same app with its authoring section stamped exits 1 naming each record still unowned, and an unknown claim and a double claim each exit 1 while every app is pending. Cheaper substitute: enforcing only at the gate, which lets a section of an authored app drop a claim unnoticed; or enforcing from the first claim, which refuses the commits that author the app. **Corrected 2026-11-12:** added by D03 T01 §30 (gap 1); the boundary corrected after its round 1. **Corrected 2026-11-13 (fact check at start):** no record carries a disposition yet: D02 T01 §28 adds the field and teaches this check to leave `excluded` records out. Until then every record is one to build, which is what `build` is when the field is absent.
- [x] Add `--all` to `--owners --check`: every app it covers (all of them, or the one `--app` names) is held as `enforced` whatever its state, so it exits 1 naming each app with no captured record and each unowned record. Done when: tests show the pending fixtures above exit 1 under `--all`, `--all --app` on a half-claimed fixture app exits 1 naming its unowned records, and a fully claimed fixture exits 0. An authoring section proves its own app with `--all --app <app>` before it is stamped (D03 T01 §17 and §19 to §24), and D03 T01 §13 runs `--all` over everything. Cheaper substitute: reading the pending list by eye at the gate. **Corrected 2026-11-12:** added by D03 T01 §30; D03 T01 §13 runs it, so the proof over all six apps and the shell stays where it was.
- [x] Add `python scripts/inventory-report.py --owners --check` to `scripts/hooks/pre-commit` for commits that stage `todo/` or `design/inventory/`, with a test in `scripts/tests/test_pre_commit_hook.py`. Done when: staging a section of an enforced fixture app with one claim removed refuses the commit, staging a new record of a pending app does not, and staging the first, partial claims of an app whose authoring section is open does not. Cheaper substitute: running the check only at the gate. **Corrected 2026-11-12:** moved here from D03 T01 §13 by D03 T01 §30, so the check holds Write's sections from the day they are written. **Corrected 2026-11-13 (build):** the two pending cases, an unknown claim and a missing authoring file are tested in `scripts/tests/test_pre_commit_hook.py`; the enforced case needs a really stamped authoring section, whose fixture is `stamp_fixture` in `scripts/tests/test_inventory_report.py`, so it is `RealStamp.test_the_hook_holds_an_enforced_apps_records_to_their_owners` there (two records, two claims, the section stamped for real, one claim dropped, the commit refused by the hook naming the record). The hook drops the check's stdout (states and counts) and keeps its stderr (refusals).
- [x] Write the owners tests in `scripts/tests/test_inventory_report.py`: unowned, unknown, doubly owned, filtered, example-only and fully claimed fixtures. Done when: the suite passes and fails when the unowned list is forced empty. Cheaper substitute: one happy-path test. **Measured 2026-11-13 (build):** with `ownership` made to return every unowned list empty, 7 of the 13 tests of the `Owners` class fail (0 errors); unchanged, all 13 pass.
- [x] Commit: `inventory: add record-level ownership check`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_inventory_report.py"` passes, and `python scripts/inventory-report.py --owners` exits 0 and prints owned and total counts per app.

> **Verified:** 2026-11-13 | §22 | 8d7b5cebea57965371008e814ffb3784c536afc6
> **Review:** `docs/reviews/d02-t01-s22.json`

## 23. Audit Schema Checker

> **Started:** 2026-10-22T08:20:41Z

`D02 T01 §1` (Inventory Schema Checker) was stamped under the earlier review process: a three-round cap. Its receipt `docs/reviews/d02-t01-s1.json` records 3 rounds (fixed, fixed, stopped-at-3), and its round 3 findings were fixed after the cap without being reviewed again. This section re-verifies it under the current process (owner request 2026-10-21) because every capture and the record-level ownership check (§22) trust it to refuse a malformed record: the section's own Test checkpoint re-run at the current tip, and fresh independent rounds by the pinned reviewer in `review-todo-section`'s audit stance, at most 22 rounds with the severity cutoff. A confirmed stamp stays; a regression reopens the section through `unstamp` with a filed repair.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Re-run `D02 T01 §1`'s Test checkpoint at the current tip. Done when: its output is quoted in `docs/reviews/02-interface/audit-d02-t01-s1.md`.
2. Audit `D02 T01 §1` with independent rounds through `scripts/review-dispatch.py`. Done when: `docs/reviews/02-interface/audit-d02-t01-s1.md` ends in an approving round or a recorded stop with every finding owned.

- [x] Re-run the Test checkpoint that `python scripts/todo-graph.py resolve "D02 T01 §1"` prints, at the current tip, and quote its result in `docs/reviews/02-interface/audit-d02-t01-s1.md`. Done when: the quoted output shows the checkpoint passing, or the failure is recorded as a regression.
- [x] Run audit rounds on `D02 T01 §1`'s stamped candidate and every later change to the files it owns, recording each with `--record docs/reviews/02-interface/audit-d02-t01-s1.md`, never in the section's own findings file. Done when: a round approves, or the severity cutoff or the 22-round cap stops the loop with its outcome recorded.
- [x] Fix each finding at its owning layer in a new commit with a regression test, or file it through `add-todo` with an owner. Done when: no finding in `docs/reviews/02-interface/audit-d02-t01-s1.md` is open without a fix commit or a filed section.
- [x] On a confirmed regression, file the repair through `add-todo`, then run `python scripts/todo-graph.py unstamp "D02 T01 §1" --reason "<what regressed, and the repair section>"` and list the suspect sections it prints in `docs/reviews/02-interface/audit-d02-t01-s1.md`. Done when: the repair section exists and `resolve "D02 T01 §1"` no longer exits 3, or the audit confirms the stamp.
- [x] Commit: `review: audit D02 T01 §1 under the current review process`

**Test checkpoint:** `python scripts/todo-graph.py resolve "D02 T01 §1"` exits 3 (still verified) or shows the `Unstamped:` note with its repair, and `docs/reviews/02-interface/audit-d02-t01-s1.md` ends in an approving round or a recorded stop with every finding fixed or filed.

> **Verified:** 2026-11-08 | §23 | 315ea601c2f1b5a5d6043dbcf8556ba1b428bb8a
> **Review:** `docs/reviews/d02-t01-s23.json`

## 24. Audit Capture Tool

> **Duration:** 2026-11-08T21:41:15Z .. 2026-11-09T02:44:45Z (5h 3m 30s)

`D02 T01 §3` (UIA Capture Tool) was stamped under the earlier review process: a three-round cap. Its receipt `docs/reviews/d02-t01-s3.json` records 3 rounds (fixed, fixed, stopped-at-3), and its round 3 findings were fixed after the cap without being reviewed again. This section re-verifies it under the current process (owner request 2026-10-21) because a capture defect leaves features out of the inventory with nothing to say they are missing: the section's own Test checkpoint and unit tests (`test_capture_ui.py` and `test_word_commands.py`) re-run at the current tip against the installed Office reference build in `design/inventory/REFERENCE.md`, and fresh independent rounds by the pinned reviewer in `review-todo-section`'s audit stance, at most 33 rounds with the severity cutoff (from round 9 on, a round whose findings are all `P3` or advisory stops the loop with `stopped-low-severity`). A confirmed stamp stays; a regression reopens the section through `unstamp` with a filed repair that must restore and re-stamp `D02 T01 §3` before `D02 T01 §24` closes.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Re-run `D02 T01 §3`'s Test checkpoint and unit tests (`test_capture_ui.py` and `test_word_commands.py`) at the current tip. Done when: their outputs are quoted in `docs/reviews/02-interface/audit-d02-t01-s3.md`.
2. Audit `D02 T01 §3` with independent rounds through `scripts/review-dispatch.py`. Done when: `docs/reviews/02-interface/audit-d02-t01-s3.md` ends in an approving round or a recorded stop under the 33-round cap with every finding owned and `D02 T01 §3` verified.

- [x] Re-run the Test checkpoint that `python scripts/todo-graph.py resolve "D02 T01 §3"` prints (`python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` and `python scripts/check-inventory.py R:\scratch\word-home.json`), `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"`, `python -m unittest discover -s scripts/tests -p "test_word_commands.py"`, and `python scripts/check-inventory.py design/inventory` at the current tip (updating `design/inventory/REFERENCE.md` to record the installed Current Channel build alongside the historical `16.0.20430.20182` build that `design/inventory/word/commands.json` and `shortcuts.json` were captured from), and quote their results in `docs/reviews/02-interface/audit-d02-t01-s3.md`. Done when: the quoted outputs show the live capture, unit suites, and whole-inventory check passing, or any failure is recorded as a regression.
- [x] Run audit rounds on `D02 T01 §3`'s stamped candidate and every later change to the files it owns, recording each with `--record docs/reviews/02-interface/audit-d02-t01-s3.md`, never in the section's own findings file. Done when: a round approves (`clean`), or the severity cutoff (`stopped-low-severity`, after round 8 when all findings are `P3` or advisory) or the 33-round cap (`stopped-at-33`) stops the loop with its outcome recorded and matching the receipt's verdict and `--cap-outcome`.
- [x] Fix each finding at its owning layer in a new commit with a regression test, or file it through `add-todo` with an owner. Done when: no finding in `docs/reviews/02-interface/audit-d02-t01-s3.md` is open without a fix commit or a filed section.
- [x] On a confirmed regression, either fix it directly in this section's commits or file the repair through `add-todo` ordered before `D02 T01 §24`, run `python scripts/todo-graph.py unstamp "D02 T01 §3" --reason "<what regressed, and the repair section>"`, list the suspect sections it prints in `docs/reviews/02-interface/audit-d02-t01-s3.md`, complete and re-stamp `D02 T01 §3` after the repair, and re-run `D02 T01 §3`'s checkpoint before stamping `D02 T01 §24`. Done when: `python scripts/todo-graph.py resolve "D02 T01 §3"` exits 3 (`done: true`) with the audit confirming the stamp (or the re-stamped repair), so `D02 T01 §24`'s dependency on `D02 T01 §3` is satisfied at stamp time.
- [x] Commit: `review: audit D02 T01 §3 under the current review process`

**Test checkpoint:** `python scripts/todo-graph.py resolve "D02 T01 §3"` exits 3 (verified, either confirming the original stamp or re-stamped after any repair), `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` and `python scripts/check-inventory.py R:\scratch\word-home.json` exit 0, and `docs/reviews/02-interface/audit-d02-t01-s3.md` ends in an approving round or a recorded stop under the 33-round cap with every finding fixed or filed.

> **Verified:** 2026-11-09 | §24 | 5967d5edbd6e0cec5121777294eca7d054016d04
> **Review:** `docs/reviews/d02-t01-s24.json`

## 25. Audit Control ID Baseline

> **Started:** 2026-11-08T12:23:00Z

`D02 T01 §19` (Control ID Baseline) was stamped under the earlier review process: a three-round cap. Its receipt `docs/reviews/d02-t01-s19.json` records 3 rounds (fixed, fixed, stopped-at-3), and its round 3 findings were fixed after the cap without being reviewed again. This section re-verifies it under the current process (owner request 2026-10-21) because §18's completeness comparison measures every capture against it: the section's own Test checkpoint and the real-workbook `--check` gate re-run at the current tip, and fresh independent rounds by the pinned reviewer in `review-todo-section`'s audit stance, at most 33 rounds with the severity cutoff (from round 9 on, a round whose findings are all `P3` or advisory stops the loop with `stopped-low-severity`). A confirmed stamp stays; a regression reopens the section through `unstamp` with a filed repair.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Re-run `D02 T01 §19`'s Test checkpoint and `import-office-ids.py <source> --check` against the pinned upstream workbooks at the current tip. Done when: their outputs are quoted in `docs/reviews/02-interface/audit-d02-t01-s19.md`.
2. Audit `D02 T01 §19` with independent rounds through `scripts/review-dispatch.py`. Done when: `docs/reviews/02-interface/audit-d02-t01-s19.md` ends in an approving round or a recorded stop under the 33-round cap with every finding owned.

- [x] Re-run the Test checkpoint that `python scripts/todo-graph.py resolve "D02 T01 §19"` prints and `python scripts/import-office-ids.py R:/scratch/office-ui-ids/b230a0df45036b2d5e8b49ebf368b3f90ada8d63 --check` against all 28 pinned upstream workbooks (verifying git blob provenance and byte-for-byte reconciliation across all six `design/inventory/<app>/baseline.json` files) at the current tip, and quote their results in `docs/reviews/02-interface/audit-d02-t01-s19.md`; if the pinned source workbooks are absent or fail reconciliation, treat baseline fidelity as unconfirmed. Done when: the quoted outputs show both checkpoints passing, or any failure is recorded as a regression.
- [x] Run audit rounds on `D02 T01 §19`'s stamped candidate and every later change to the files it owns, recording each with `--record docs/reviews/02-interface/audit-d02-t01-s19.md`, never in the section's own findings file. Done when: a round approves (`clean`), or the severity cutoff (`stopped-low-severity`, after round 8 when all findings are `P3` or advisory) or the 33-round cap (`stopped-at-33`) stops the loop with its outcome recorded and matching the receipt's verdict and `--cap-outcome`.
- [x] Fix each finding at its owning layer in a new commit with a regression test, or file it through `add-todo` with an owner. Done when: no finding in `docs/reviews/02-interface/audit-d02-t01-s19.md` is open without a fix commit or a filed section.
- [x] On a confirmed regression, file the repair through `add-todo`, then run `python scripts/todo-graph.py unstamp "D02 T01 §19" --reason "<what regressed, and the repair section>"` and list the suspect sections it prints in `docs/reviews/02-interface/audit-d02-t01-s19.md`. Done when: the repair section exists and `resolve "D02 T01 §19"` no longer exits 3, or the audit confirms the stamp.
- [x] Commit: `review: audit D02 T01 §19 under the current review process`

**Test checkpoint:** `python scripts/todo-graph.py resolve "D02 T01 §19"` exits 3 (still verified) or shows the `Unstamped:` note with its repair, `python scripts/import-office-ids.py R:/scratch/office-ui-ids/b230a0df45036b2d5e8b49ebf368b3f90ada8d63 --check` exits 0 (when the stamp is confirmed), and `docs/reviews/02-interface/audit-d02-t01-s19.md` ends in an approving round or a recorded stop under the 33-round cap with every finding fixed or filed.

> **Verified:** 2026-11-08 | §25 | 5af840f2faf3011ad71073823067c90173ea4d21
> **Review:** `docs/reviews/d02-t01-s25.json`

## 26. Audit Microsoft-Free Rule

> **Started:** 2026-11-08T12:49:45Z

`D02 T01 §21` (Microsoft-Free Inventory) was stamped under the earlier review process: a three-round cap. Its receipt `docs/reviews/d02-t01-s21.json` records 3 rounds (fixed, fixed, stopped-at-3), and its round 3 findings were fixed after the cap without being reviewed again. This section re-verifies it under the current process (owner request 2026-10-21) because it is the legal boundary that keeps Microsoft text, links and ScreenTips out of the repository: the section's own Test checkpoint and whole-inventory `check-inventory.py` gate re-run at the current tip, and fresh independent rounds by the pinned reviewer in `review-todo-section`'s audit stance, at most 33 rounds with the severity cutoff (from round 9 on, a round whose findings are all `P3` or advisory stops the loop with `stopped-low-severity`). A confirmed stamp stays; a regression reopens the section through `unstamp` with a filed repair.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Re-run `D02 T01 §21`'s Test checkpoint and `python scripts/check-inventory.py design/inventory` at the current tip. Done when: their outputs are quoted in `docs/reviews/02-interface/audit-d02-t01-s21.md`.
2. Audit `D02 T01 §21` with independent rounds through `scripts/review-dispatch.py`. Done when: `docs/reviews/02-interface/audit-d02-t01-s21.md` ends in an approving round or a recorded stop under the 33-round cap with every finding owned.

- [x] Re-run the Test checkpoint that `python scripts/todo-graph.py resolve "D02 T01 §21"` prints and `python scripts/check-inventory.py design/inventory` at the current tip, and quote their results in `docs/reviews/02-interface/audit-d02-t01-s21.md` (verifying that the `rg` search finds nothing except the refusal fixtures in `scripts/tests/test_check_inventory.py`, the JSON Schema `$schema` dialect lines in `design/inventory/schema.json` and `design/inventory/baseline.schema.json`, and the two upstream Visio `idMso` control identifier tokens `ScreenTip` and `DeleteShapeScreenTip` in `design/inventory/visio/baseline.json` added by `D02 T01 §19`). Done when: the quoted outputs show the checkpoint and whole-inventory check passing, or any failure is recorded as a regression.
- [x] Run audit rounds on `D02 T01 §21`'s stamped candidate and every later change to the files it owns, recording each with `--record docs/reviews/02-interface/audit-d02-t01-s21.md`, never in the section's own findings file. Done when: a round approves (`clean`), or the severity cutoff (`stopped-low-severity`, after round 8 when all findings are `P3` or advisory) or the 33-round cap (`stopped-at-33`) stops the loop with its outcome recorded and matching the receipt's verdict and `--cap-outcome`.
- [x] Fix each finding at its owning layer in a new commit with a regression test, or file it through `add-todo` with an owner. Done when: no finding in `docs/reviews/02-interface/audit-d02-t01-s21.md` is open without a fix commit or a filed section.
- [x] On a confirmed regression, file the repair through `add-todo`, then run `python scripts/todo-graph.py unstamp "D02 T01 §21" --reason "<what regressed, and the repair section>"` and list the suspect sections it prints in `docs/reviews/02-interface/audit-d02-t01-s21.md`. Done when: the repair section exists and `resolve "D02 T01 §21"` no longer exits 3, or the audit confirms the stamp.
- [x] Commit: `review: audit D02 T01 §21 under the current review process`

**Test checkpoint:** `python scripts/todo-graph.py resolve "D02 T01 §21"` exits 3 (still verified) or shows the `Unstamped:` note with its repair, `python scripts/check-inventory.py design/inventory` exits 0 (when the stamp is confirmed), and `docs/reviews/02-interface/audit-d02-t01-s21.md` ends in an approving round or a recorded stop under the 33-round cap with every finding fixed or filed.

> **Verified:** 2026-11-08 | §26 | a4ba192190baec153945bb7d0cabcea04250e63d
> **Review:** `docs/reviews/d02-t01-s26.json`

## 27. Checker Mutation Sweep

`D02 T01 §23` audited the inventory checker to its 22-round cap, and `D02 T01 §26` audited the Microsoft-free rule to its 33-round cap. In `D02 T01 §23`, the record lens found one more untested guard in each of rounds 18 to 22, so the claim that every rule's removal fails a test is proven one rule at a time, and its round 22 fixes (`fe3620f`, hexadecimal address components, the compatibility-character class, case-insensitive baseline names) had no independent round left. In `D02 T01 §26`, round 33 exposed that any finite regular-expression parenthesis depth boundary in `$defs.noHost`'s hyphenated dotted-function exemption leaves a deeper nesting threshold inside `maxLength`, and its round 33 fix (`015ff91`) had no independent round left under the 33-round cap. This section proves the mutation claim systematically, enforces arbitrary-depth parenthesis balance for hyphenated dotted-function calls in `scripts/check-inventory.py` up to `maxLength`, and gives both post-cap fix commits their independent review. Sources: `docs/reviews/02-interface/audit-d02-t01-s1.md` (`## Cap reached`) and `docs/reviews/02-interface/audit-d02-t01-s21.md` (`## Cap reached`).

**Phase:** 2
**Needs:** none
**Surface:** no

> **Started:** 2026-11-13T06:16:32Z

**Build order:**

1. List every rule and enforce arbitrary-depth parenthesis balance on hyphenated dotted-function calls in `scripts/check-inventory.py`. Done when: `docs/reviews/02-interface/inventory-mutation-sweep.md` names each guard in `scripts/check-inventory.py` and each pattern alternative and keyword in `design/inventory/schema.json`, and `scripts/check-inventory.py` rejects unclosed or prose-interrupted hyphenated dotted-function calls at any nesting depth up to `maxLength`.
2. Disable each rule on its own and run the checker tests. Done when: every listed rule has a test that fails without it, or a new test was added that does.
3. Review the result, the `D02 T01 §23` round 22 fixes (`fe3620f`), and the `D02 T01 §26` round 33 fixes (`015ff91`) independently. Done when: a round through `scripts/review-dispatch.py` approves, or the cap stops it with every finding owned.

- [x] Enforce arbitrary-depth parenthesis balance and completed-call boundaries for hyphenated dotted-function exemptions in `scripts/check-inventory.py` across all nesting depths permitted by `maxLength`, with paired positive and negative regressions in `scripts/tests/test_check_inventory.py`. Done when: deep malformed expressions such as `=1-REGISTER.ID(` with 20 or more nested `SUM(` calls (with or without trailing `"help desk"`) are refused while balanced deep calls pass. Cheaper substitute: raising the regular-expression nesting depth in `design/inventory/schema.json` by another fixed constant, which only moves the failure threshold; refused. **Corrected 2026-11-13 (fact check at start):** measured on the committed checker, an unclosed call is refused at every depth, but from 20 nested calls a call left open before a trailing string, or closed one level short before prose, passes. The fix is a scan in `check-inventory.py` that runs wherever a field's schema refers to `noHost`: from each hyphenated dotted call it counts parentheses (Excel strings skipped, `""` a quote inside one) and requires the call to close and each completed inner call or string to be followed by what noHost's own pattern allows there, so it refuses only what the pattern's fixed depth hides. Done when, in addition: over generated shallow texts, the scan refuses nothing the pattern accepts. **Corrected 2026-11-13 (resume, measured before ticking):** the scan as first committed (`4aa7102`) also took a call whose hyphen has a space on either side, which the pattern lets stand unfinished at every depth, so it refused 1,728 of the generated texts the pattern accepts; and it took only a name or number before the hyphen, so after `)` or `]` a deep call still passed. The scan now takes the one form the pattern asks a completed call of (a hyphen glued on both sides, after a name, a number, `)` or `]`), and `test_nesting_depth_never_changes_the_address_verdict` in `scripts/tests/test_check_inventory.py` holds both directions over generated calls: nothing the pattern accepts is refused at depths 1 to 3, and a call nested 20 or 40 times gets the verdict it gets nested once. **Corrected 2026-11-13 (round 1, finding 1):** the scan's own list of what may follow a completed inner call or string refused a parenthesis inside a quoted sheet name (`=1-STDEV.S('Q1 (draft)'!A1)`), which the pattern accepts. The scan no longer restates the pattern: it counts parentheses outside `"..."` and `'...'` and requires the call to close; it measures on the pattern itself the depth the pattern counts (14 groups today); and a call nested that deep or deeper is read one level at a time by the pattern (each level's own text under its own function name, the levels inside it replaced by `1`). Below the counted depth the pattern's verdict stands untouched. The generated test now also holds quoted sheet names, structured references, every kind of character after an inner call, and the depths on both sides of the counted one.
- [x] Write `scripts/mutation-sweep-inventory.py` that enumerates the guards in `scripts/check-inventory.py` (each `if` that appends a problem or raises `Unreadable`) and the alternatives of every `pattern` in `design/inventory/schema.json`, disables each one in memory, runs `scripts/tests/test_check_inventory.py`, and prints the survivors. Done when: it runs with `python -B` and prints one line per rule with the number of failing tests. Cheaper substitute: a hand-picked list of mutations, which is what rounds 18 to 22 kept finding gaps in; refused. **Corrected 2026-11-13 (fact check at start):** a rule is one guard of `check-inventory.py` (an `if` whose body adds a problem or raises `Unreadable`: 65), one keyword of `schema.json` the checker's validator reads (`type`, `const`, `enum`, `minLength`, `maxLength`, `pattern`, `required`, `additionalProperties`, `dependentRequired`, `not`, `allOf`, `items`, `minimum`, `$ref`: 148), or one top-level alternative of a `pattern` (30, noHost's nine among them: each a family the rule refuses). The 4,207 alternation bars inside noHost's groups define those families' exemptions and are not swept one by one: each is a full run of the checker's tests, about ten hours in all, and the sweep's record, `docs/reviews/02-interface/inventory-mutation-sweep.md`, states that limit. Each mutation is applied in memory, in worker processes that import the tests once: the checker's source run again with that guard's condition made false, or the schema the checker loads returned without that keyword or alternative. The workers run in parallel, each in a process tree with a time limit (`scripts/lib/process_tree.py`), and the sweep is queued through `bosun run` as a heavy job. Done when, in addition: a test over a tiny fixture checker shows a guard whose removal fails no test reported as a survivor, and one whose removal fails a test reported with that count. **Corrected 2026-11-13 (plan review, gaps 1 to 3):** the rules also take in every `if` whose body returns a refusal (the validator's type mismatch), each entry of a `properties` map, and each `if` and `then` of a conditional, and a test over the fixture shows each kind enumerated. A mutation is no longer applied in memory: each runs in a private copy of `scripts/` and `design/inventory/` with that one rule removed from the file on disk, in a fresh process, so the tests that read the schema themselves or start the checker as a subprocess see it too, and nothing of one mutation survives into the next. Each run reports its passed, failed and errored tests and how many were discovered; a mutation is killed only when a test fails with every test discovered; one whose tests only error, that discovers fewer tests than the unmutated run, that times out or whose process dies is reported as such and makes the sweep exit 1; and the sweep starts with an unmutated run that must pass in full, or it exits 2 having mutated nothing. Done when, in addition: fixture tests show a killed, a surviving, an erroring, a timed-out and an undiscovered mutation each reported apart, and a failing unmutated run stopping the sweep.
- [x] Record the sweep's output in `docs/reviews/02-interface/inventory-mutation-sweep.md`. Done when: the file quotes the full run and the survivor count. **Measured 2026-11-13 (first run, operator stop after it):** 271 rules, 222 killed, 42 survived and 7 only erroring; the next session resumes at the item below with those 49. **Measured 2026-11-13 (second run):** the record now also quotes the full second run and its survivor count of zero. **Measured 2026-11-13 (third run, commit `ee2e913`, after the round's fix):** 271 rules, 271 killed, no survivor and no other outcome, quoted in full in the record.
- [x] Add a regression test to `scripts/tests/test_check_inventory.py` for every survivor. Done when: a re-run of the sweep reports zero survivors. **Corrected 2026-11-13 (resume):** the removals whose tests only error count too (the sweep exits 1 on them), so each of those seven rules also gets a test that fails by assertion: where the rule stands before a lookup that raises without it, the test runs the checker as a program and reads the line it prints. Two survivors were not missing tests but defects, repaired at their cause: the guard for a string that never closes inside `unfinished_call` could never decide anything (the loop's own end-of-text guard refuses first), so it is removed; and `condition` had no `maxLength` in `design/inventory/schema.json`, against the schema's own statement that every string field has one, so it takes 200 (the longest in the inventory is 57 characters) with its test. **Measured 2026-11-13 (second run, commit `3dea566`):** 270 rules, 270 killed, no survivor and no other outcome; the run is quoted in the record.
- [x] Run independent review rounds on `D02 T01 §23`'s round 22 fix commit (`fe3620f`), `D02 T01 §26`'s round 33 fix commit (`015ff91`), and this section's changes, recording each with `--record docs/reviews/02-interface/D02-T01-s27.md`. Done when: a round approves, or the severity cutoff or the 33-round cap stops the loop with every finding fixed or filed. **Corrected 2026-11-13 (fact check):** `fe3620f` is no longer in the history; its round 22 fixes are `6e0db0f` (with CI's follow-up `b481dd4`), which the round reviews in its place; the three-pass policy gives the section one round, which reviews all three. **Done 2026-11-13:** round 1 (astra, candidate `0d3b6bf`) read `6e0db0f`, `b481dd4`, `015ff91` and this section's changes and returned one finding (P2, the quoted sheet name above), fixed with its tests; the three-pass policy allows no second round, so the completion review reads the fix.
- [x] Commit: `inventory: prove every checker rule with a mutation sweep (D02 T01 §27)`

**Test checkpoint:** `python -B scripts/mutation-sweep-inventory.py` exits 0 and prints `survivors: 0`; `python -m unittest discover -s scripts/tests -p "test_check_inventory.py"` passes.

> **Verified:** 2026-11-13 | §27 | 7ba7c990f82305fbf8b6bf365b535e402de4a0ef
> **Review:** `docs/reviews/d02-t01-s27.json`

## 28. Record Dispositions

> **Started:** 2026-11-13T14:47:19Z

Owner decision 2026-10-22 (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 6): every inventoried control that depends on a Microsoft cloud service (Copilot, Designer, Editor, Translator, cloud dictation, stock images and icons, Loop, Teams meetings, Stocks and Geography data types, Researcher, AppSource add-ins and the like) gets a working equivalent of our own, and one with no possible equivalent is excluded with a reason, never left as a dead control. The inventory therefore needs a field saying which records are built as captured, built as an equivalent, or excluded, and the coverage and ownership checks need to honour it. D03 T01 §14 decides each record's value; this section adds the field and the checks.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Add `disposition` to `design/inventory/schema.json` with its rules. Done when: `python scripts/check-inventory.py` refuses an `excluded` record with no reason.
2. Teach `scripts/inventory-report.py` the three dispositions. Done when: coverage and `--owners` treat each as below, under test.

- [x] Add an optional `disposition` field to the record definition in `design/inventory/schema.json` with the values `build` (the default when absent), `equivalent` and `excluded`. Done when: a fixture record with `"disposition": "unknown"` fails `python scripts/check-inventory.py`. Cheaper substitute: a free-text note field, which no check can read.
- [x] Require `dispositionReason` (one sentence, no web address, under the schema's `noLink` rule) when `disposition` is `equivalent` or `excluded`, naming the cloud service and, for `equivalent`, what replaces it. Done when: fixtures without a reason fail and with one pass in `scripts/tests/test_check_inventory.py`. Cheaper substitute: allowing a bare `excluded`. **Corrected 2026-11-13 (fact check at start):** the reason is text a person reads, so it takes the three rules of such a field (`noLink`, `noControl`, `noHost`), a non-blank pattern and a `maxLength` of 500, inside the checker's `MAX_STRING` of 1000. Two more rules make the pair unambiguous: a reason needs a `disposition` beside it, and a record whose `disposition` is `build` carries none, since there is nothing to give a reason for. Done when, in addition: fixtures with a reason and no disposition, and with `build` and a reason, each fail; the reason joins the written-out lists of string fields the checker's tests hold (type, empty, blank, control character, length); and `python -B scripts/mutation-sweep-inventory.py --only disposition` reports `survivors: 0`. **Measured 2026-11-13 (build):** `python -B scripts/mutation-sweep-inventory.py --only disposition --only "allOf/3" --only "allOf/4" --only "record dependentRequired"` removed the 25 rules the two fields add, one at a time: `rules: 25, killed: 25, other outcomes: 0`, `survivors: 0`.
- [x] Count dispositions in `scripts/inventory-report.py`: coverage reports `build`, `equivalent` and `excluded` separately per app, and an `excluded` record counts as accounted for. Done when: a test over a three-record fixture prints each count. Cheaper substitute: dropping excluded records from the totals, which hides them. **Corrected 2026-11-13 (fact check at start):** the committed `design/inventory/COVERAGE.md` gains a `## Dispositions` table, one row for each app with captured records: `Build`, `Equivalent`, `Excluded`, and `Accounted for` (the build and equivalent records a stamped section implements, plus every excluded record). The `Records` table keeps its two counts. The report is regenerated and committed with the change, since the pre-commit hook refuses a stale copy. **Corrected 2026-11-13 (plan review, gap 2):** printing three counts is not enough to hold the table. Done when, in addition: a test over one fixture app holding a record with no `disposition`, one with `build`, one with `equivalent` and one with `excluded` asserts the whole row of the `Dispositions` table (the record with no field counted as `build`) in each of these states: nothing claimed (accounted for: the excluded record alone); the build and equivalent records claimed by an open section (still the excluded record alone); the same claims in a stamped section (those records and the excluded one; an unclaimed record never); and it shows `--check` reporting the committed report stale after a record's disposition changes and after the claiming section is stamped, and current once regenerated. **Corrected 2026-11-13 (build):** the build's own test found the plain report crashing on a record whose `disposition` the schema does not allow; it exits 2 naming the record, as `--owners` does, and guesses nothing.
- [x] Make `python scripts/inventory-report.py --owners --check` (§22) refuse an `excluded` record that a section claims on an `> **Implements:**` line, and require every `build` or `equivalent` record to be owned. Done when: a test with a claimed excluded record and one with an unowned equivalent record each exit 1 naming the id. Cheaper substitute: letting excluded records be claimed, which reopens dead controls. **Corrected 2026-11-12:** restated by D03 T01 §30: "every `build` or `equivalent` record owned" holds for an app from the stamp of its authoring section (§22's `enforced` state) and for all apps under `--all`; the tests here use fixtures, so the tool is built and proved before the later apps are captured. **Corrected 2026-11-13 (fact check at start):** D02 T01 §22 is stamped: `--owners` counts every record as one to build. Here an `excluded` record leaves the owned and unowned counts and is counted apart on the app's line (`7 of 7 records owned, 1 excluded`), in every state and under `--all`; a claim of an excluded record is refused in every state, as an unknown or double claim is, naming the record and the claiming section; `--app` filters it by the record's app. **Corrected 2026-11-13 (plan review, gap 3):** two refusals do not show that a legitimate exclusion is accepted. Done when, in addition: tests show an enforced app whose only unclaimed record is `excluded` passing `--check` and `--check --all`, with that record outside the owned and total counts and counted as excluded on the app's line; an unowned `equivalent` and an unowned explicit `build` record each refused there naming the id; a claimed excluded record refused while its app is pending authoring, under `--all`, and under `--app` for its own app, and not reported under `--app` for another app; and a pending app with unclaimed excluded records still passing.
- [x] Document the field in `design/inventory/REFERENCE.md` with the owner decision and the rule that only D03 T01 §14 sets it. Done when: `python scripts/check-design-doc.py design/inventory/REFERENCE.md --require Disposition` exits 0. Cheaper substitute: the schema description alone. **Corrected 2026-11-13 (plan review, gap 4):** "only D03 T01 §14 sets it" is no longer what D03 T01 §14 says (corrected 2026-11-12 by D03 T01 §30, decision 44): §14 decides each cloud service once, for the suite, and sets the records of the apps captured when it runs; the authoring section of each later app (D03 T01 §20 to §24) sets that app's records from §14's decisions. The reference states that rule, names the owner decision, and says that nothing else writes the field and that a recapture keeps it. Done when, in addition: a test reads the `## Disposition` section of `design/inventory/REFERENCE.md` and finds decision 6, D03 T01 §14, D03 T01 §20 to §24 and the three values.
- [x] Carry `disposition` and `dispositionReason` across every recapture, as `behaviour` is carried: in `carry_behaviours` of `scripts/lib/word_backstage.py` (which today carries the behaviour alone and drops every other hand-written field of a Backstage record), in `HAND` of `scripts/word-commands.py` (the shortcut records), and held by a test for `merge` in `scripts/capture-ui.py`, which already keeps every field it does not refresh. Done when: tests show a committed record with `disposition` `excluded` and its reason keeping both through a Backstage recapture, a command-list refresh and a ribbon merge, and a freshly captured record gaining neither. Cheaper substitute: setting dispositions again after each recapture, which loses the owner's decisions silently the first time someone forgets. **Added 2026-11-13 (fact check at start):** D03 T01 §14 writes the field by hand on committed records; a recapture that drops it would undo that with no refusal anywhere. **Corrected 2026-11-13 (plan review, gap 1):** the command records are the gap that mattered most: `scripts/word-commands.py` regenerates `commands.json` from Word's command table without reading the committed file, and the cloud commands are there (`word.command.copilotresearcher`, `word.command.start-office-dictation`). The refresh reads the committed `commands.json` and carries both fields to the command record of the same id; a committed command record that carries a disposition and is no longer in the table refuses the refresh, naming it, as a moved binding does, since the owner's decision would vanish with the record. Done when, in addition: a refresh test over a fixture table reads back both `commands.json` and `shortcuts.json` and finds the committed dispositions and reasons on the command and the shortcut record of the same ids, neither field on a record new to the table, and the refusal for a disposition-carrying command that left the table. **Corrected 2026-11-13 (build):** a Backstage record that carries a disposition and that the capture no longer shows is refused too, as the command is: `carry_behaviours` kept its rule that a record the capture did not see is not kept, which would have dropped the decision with the record.
- [x] Commit: `inventory: add record dispositions for cloud features`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_check_inventory.py"` and `python -m unittest discover -s scripts/tests -p "test_inventory_report*.py"` pass, and `python scripts/check-inventory.py` exits 0 on the committed inventory.

> **Verified:** 2026-11-13 | §28 | d0b2c8df23ba9cf53375911054089dae3f86450c
> **Review:** `docs/reviews/d02-t01-s28.json`

## 29. Inventory Layout Tables

> **Started:** 2026-11-13T15:26:01Z

Filed 2026-11-10 (owner: the plan must hold the features "complete with button locations and layouts, 100% complete"). §22 proves that every record has an owning section, but an `> **Implements:**` line is a list of ids: the section that builds the Paragraph group of the Home tab would not say that Bullets is the first control, a small split button 39 by 24 pixels at the group's top left with key tip U. Those facts are in the records (`order`, `controlType`, `size`, `bounds`, `keytip`, `label`), in files of several megabytes. This section makes the tool print them as a layout block a section carries, and checks that every block in the tree still equals the inventory, so a feature section is implementable without opening the inventory and can never drift from it.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Add `--layout <parent id>` to `scripts/inventory-report.py`. Done when: it prints the block for `word.home.paragraph` with its 15 controls in order.
2. Add `--layout-check`. Done when: a stale or missing block in a fixture section exits 1 naming the section and the parent.

- [x] Document the layout block in `todo/README.md` beside the `> **Implements:**` line: a section that claims records carries, for each parent whose children it claims (a group, menu, dialog, pane, Backstage page or status bar), a line `**Layout:**` naming the parent id in backticks and its capture profile, followed by one fenced `text` block generated by the tool and never typed by hand. Done when: the README names the line, the block, the command that prints it and the rule that the tool is its only author. Cheaper substitute: a prose description of the layout, which no check can compare. **Corrected 2026-11-13 (fact check at start):** measured on the inventory: `word.home.paragraph` has its 15 controls, every ribbon record has `bounds` and no two children of one parent share an `order`. A block sits in the section body before `**Build order:**`. Each of its rows starts with a word or a number, never with `-`, `*`, `+`, `>` or a backtick, so the TODO graph reads none of them as a list item or a checklist line and no label can close the fence; an empty cell is blank, never a dash. The README says both.
- [x] Add `--layout <parent id>` to `scripts/inventory-report.py`: print the `**Layout:**` line and a fenced block with one row per child record in `order`, in aligned columns: order, id relative to the parent, label, control type, size, x and y relative to the parent's top left corner, width, height and key tip, with an empty cell where a record has no value. Done when: a test in `scripts/tests/test_inventory_report.py` over a fixture group of three controls prints the three rows in order with relative positions, and the same call twice prints identical bytes. Cheaper substitute: printing absolute screen coordinates, which change with the window's position. **Corrected 2026-11-13 (fact check at start):** the children are every record of the inventory whose `parent` is the id, in whichever file of the app they sit; they are ordered by `order` and then by id, a record with no `order` after those with one. The x and y cells are blank when the parent or the child has no `bounds`. The line reads `**Layout:**`, the parent id in backticks, then the parent's capture profile in backticks, or the words `no capture profile`. `--layout` takes no other mode beside it (exit 2). **Corrected 2026-11-13 (plan review, gap 2):** Done when, in addition: fixtures show a child kept in another file of the app among the rows; a child with no `order` after those with one, and two of those in id order; and blank x and y cells for a child with no `bounds` and for every child of a parent with none. **Measured 2026-11-13 (build):** `python scripts/inventory-report.py --layout word.home.paragraph` prints 15 control rows, the first `0  bullets  Bullets  splitButton  small  8  10  39  24  U`: Bullets at the group's top left, 39 by 24, key tip U, as this section's opening says. The generator, the parser and the comparison are `scripts/lib/inventory_layout.py`. A child whose `bounds` lack a member has a blank position and size, since the schema allows no such record.
- [x] Print the parent's own row first (its label, kind, width, height and key tip) and, for a child that is itself a parent (a split button's menu, a gallery), the id to pass to `--layout` for its own block. Done when: the fixture test shows the parent row and the pointer line for a fixture split button with two menu items. **Measured 2026-11-13 (build):** the parent's row is the second line of the block, under the column names, with `parent` in the order column and `.` as its id; a child that has children gets a `children` line after the rows with the count and the id to pass to `--layout`.
- [x] Refuse an id that is not in the inventory or has no children, with exit 2 and the id. Done when: tests show both refusals.
- [x] Add `--layout-check`: read every `**Layout:**` line and its fenced block in `todo/**/TODO-*.md`, generate the block again and compare byte for byte; exit 1 naming the section (`DNN TNN §N`) and the parent for each block that differs. Done when: changing one width in a fixture section's block exits 1 with that section and parent, and the untouched fixture exits 0. Cheaper substitute: checking only that a block exists. **Corrected 2026-11-13 (fact check at start):** the sections are read from `todo_graph.graph()`, as the ownership check reads them, so the TODO tree keeps one reader. A `**Layout:**` line with no fenced block after it, a block whose fence never closes, a parent the inventory does not hold and two blocks for one parent in one section are each named with their section and exit 1. The verdict is decided before a line is printed, the refusals go to stderr, and at most 50 are printed for one section before the rest are counted (lessons `the-verdict-is-decided-before-it-is-printed` and `keep-diagnostics-linear-and-escaped`). **Corrected 2026-11-13 (plan review, gap 1 and 2):** what is compared, and what `--write` repairs, is the whole generated unit: the `**Layout:**` line with its capture profile, the blank line and the fenced block. Done when, in addition: changing only the capture profile on a fixture section's `**Layout:**` line exits 1 naming the section and the parent; and fixtures of a line with no block after it, a fence that never closes, a parent the inventory does not hold and two blocks for one parent in one section each exit 1 naming the section, with the untouched fixture exiting 0.
- [x] Report in `--layout-check` every section that claims a parent's children on its `> **Implements:**` lines (§22) and carries no block for that parent, with exit 1. Done when: a fixture section claiming two controls of one group with no block is named with the group's id. **Corrected 2026-11-13 (fact check at start):** a claim of an id the inventory does not hold, or of a record with no `parent` (a tab), asks for no block: the ownership check refuses the first, and the second has no parent to lay out. Every other claimed record's parent needs its block in that section, a tab whose groups are claimed included. **Corrected 2026-11-13 (plan review, gap 2):** Done when, in addition: a fixture section that claims a tab's group and carries no block for the tab is named with the tab's id, the same section with the tab's block passes, and a section that claims only a tab, or only an id the inventory does not hold, is asked for no block.
- [x] Say in the `--layout-check` message for a stamped section that the inventory changed after its stamp and that the repair is a new section through `add-todo` with `unstamp`, since a stamped section is never rewritten (`todo/README.md`). Done when: a fixture stamped section with a stale block prints that sentence and exits 1.
- [x] Add `--write <TODO file>` to `--layout-check`, which replaces each stale block in that file's open sections with the generated one through a temporary file and `os.replace`, and touches nothing in a stamped section. Done when: a test shows a stale open block rewritten to the generated bytes, the file otherwise identical, and a stale stamped block left as it was. Cheaper substitute: asking the author to paste the output again by hand. **Corrected 2026-11-13 (fact check at start):** the file is one the TODO graph reads (`todo/<NN-domain>/TODO-NN-<name>.md`); any other path exits 2, and the check that follows the write reports what is still wrong in the tree. **Corrected 2026-11-13 (plan review, gap 3):** a write that fails leaves the TODO file as it was. Done when, in addition: tests that make the temporary file's write fail and that make `os.replace` fail each show exit 1 with a line naming the file and the failure, the file's bytes unchanged, and no temporary file left beside it. **Corrected 2026-11-13 (round 1, finding 1):** the build looked for a block's closing fence anywhere later in the section, so a block whose fence had been left out ran on to the next one, and `--write` replaced everything between: the instructions and the next block. A block is rows and nothing else, so it now ends at the first line that is its closing fence, and a blank line, another `**Layout:**` line or another fence before that makes it a block that was never closed, which is refused and never rewritten. A test builds the reviewer's case in a file and requires every byte unchanged.
- [x] Add `python scripts/inventory-report.py --layout-check` to `scripts/hooks/pre-commit` beside the ownership check, for the same staged paths, with a test in `scripts/tests/test_pre_commit_hook.py`. Done when: staging a section whose layout block was edited by hand refuses the commit, and a tree with no layout block yet passes. Cheaper substitute: running the check only at the gate. **Corrected 2026-11-12:** moved here from D03 T01 §13 by D03 T01 §30, so the check holds every block from the first one written. **Measured 2026-11-13 (build):** the hook test prints the block with the tool, commits it, then edits one cell by hand and is refused; a second test removes the block of a claimed parent's child and is refused too.
- [x] Commit: `inventory: print and check layout blocks`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_inventory_report.py"` passes with the tests named above among them, `python scripts/inventory-report.py --layout word.home.paragraph` prints 15 control rows, and `python scripts/inventory-report.py --layout-check` exits 0.

> **Verified:** 2026-11-13 | §29 | fddd35e4897eaf5a1222d3375556ddcae41d00ae
> **Review:** `docs/reviews/d02-t01-s29.json`

## 30. Built-App Layout Check

> **Started:** 2026-11-13T15:44:33Z

The plan's acceptance bar is that every element works in its app at its inventoried position (`todo/plan.json`). A section can only prove that if a command compares what our app shows with what the inventory records. This section builds that comparison, from the same UI Automation capture the inventory itself came from (§3), so every surface section's Test checkpoint can call it for the parents it implements. It is built and tested here on capture fixtures, before any app exists.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Write `scripts/check-layout.py`. Done when: a fixture capture that matches the inventory exits 0 and one with a moved control exits 1 naming it.

- [x] Write the matcher in `scripts/check-layout.py`: given `--parent <id>` and `--capture <file>` (the JSON `scripts/capture-ui.py` writes for a window), pair each child record with a captured element by `uiaId`, and by label with control type where a record has none. Done when: a test in `scripts/tests/test_check_layout.py` pairs three fixture records with three captured elements given in another order. Cheaper substitute: pairing by position alone, which hides a control that is in the wrong place. **Corrected 2026-11-13 (fact check at start):** the file `scripts/capture-ui.py` writes with `--out` is a JSON array of draft records (`id`, `parent`, `uiaId`, `label`, `kind`, `controlType`, `order`, `bounds`, `captureProfile`), so the capture is read as one. Measured on Word's ribbon: 505 of 8,685 records carry a `uiaId`, and 113 sets of siblings share a label and a control type. The rule therefore is: the capture's counterpart of the parent is found first, by the same pairing; its children are the captured records whose `parent` is that record; a child record with a `uiaId` pairs with the captured child of the same `uiaId`; one without pairs by label and type (`controlType`, or `kind` where it has none) with a captured child that has no `uiaId` either; and where several siblings share that key they pair in `order`, first with first. An input that cannot be read or is not an array of records, a parent the inventory does not hold or that has no children there, and a tolerance that is not a whole number of pixels from 0 up are each exit 2 naming it. Done when, in addition: tests show two same-labelled siblings paired in order, a captured child with a `uiaId` not taken by a record that has none, and each exit 2 case. **Corrected 2026-11-13 (plan review, gap 1):** the parent is found from the top of its branch, not by its own label: the inventory parent's ancestors are paired one level at a time, the topmost with a captured record that has no parent, each next one among the captured children of the pair above it, by the children's rule. Word has several `Shadow`, `Reflection`, `Glow`, `Weight` and `Dashes` parents with one label and type and no `uiaId`, in different branches, and only the branch tells them apart. Where a level still cannot be told apart (siblings sharing its label and type, in different numbers on the two sides) the run is refused with exit 2 naming the level, never guessed. Done when, in addition: a fixture with two parents of one label and type under different branches, the requested branch holding a defect and the other correct, reports the defect; the same fixture asked about the correct branch passes; and a level that cannot be told apart is exit 2 naming it. **Corrected 2026-11-13 (round 1, finding 2):** the build refused a level only when the inventory held several of its label and type, so one group in the inventory and two in the capture was paired with whichever came first, and an added whole group could stand in for the original that had lost a control. A level is told apart only when both sides hold as many of its identity (its `uiaId`, or its label and type where it has none): any other number in the capture, other than none, is exit 2 naming the level and both numbers. **Corrected 2026-11-13 (round 1, finding 1):** a record whose `id` is not text, or whose `parent`, `uiaId`, `label`, `kind`, `controlType` or `captureProfile` is something other than text, and a capture holding one `id` twice, are exit 2 naming the record, on the inventory side too; the build crashed on them.
- [x] Report a record with no captured element as `missing`, and a captured element with no record as `extra`. Done when: a fixture with one control removed exits 1 naming its id as missing, and a fixture with one added control lists it as extra and exits 0, since an improvement may add a control but may never lose one. **Corrected 2026-11-13 (fact check at start):** when the capture has no counterpart of the parent itself, the parent is reported `missing` and nothing under it is compared (exit 1).
- [x] Compare each pair's label, control type and order among its siblings, reporting `renamed`, `retyped` or `reordered` with both values. Done when: one fixture per difference exits 1 with the id and both values. **Corrected 2026-11-13 (fact check at start):** order is compared as the sequence of the paired children, by their `order` in the inventory against their `order` in the capture, so a control the built app adds between two others (an `extra`) does not make its neighbours `reordered`; the smallest set of children whose removal leaves the two sequences equal is the set reported. **Corrected 2026-11-13 (plan review, gap 2):** a rename or a type change of a record with a `uiaId` keeps its pair, and is reported. A record without one is paired by its label and type, so the change removes its pair; the children left unpaired on both sides are then paired a second time, in this order: by label alone, reported `retyped`; then, between the same paired neighbours, where as many records as captured children are left and their types agree in order, pair by pair, reported `renamed`. What is still unpaired is `missing` or `extra`: a control with no `uiaId` whose label and type both changed cannot be told from one removed and one added, and is reported as that. Done when, in addition: tests show `renamed` and `retyped` each for a record with a `uiaId` and for one without, and `missing` with `extra` for one without whose label and type both changed. **Corrected 2026-11-13 (round 1, finding 3):** the build took the pair before a run of unpaired children as its place, so with A, X, B, D against A, Y, D, B it reported X renamed to Y. A place is the pair before and the pair after, the same on both sides; otherwise the children are `missing` and `extra`.
- [x] Compare each pair's position relative to the parent and its width and height, at the record's capture profile, within `--tolerance` pixels (default 2), reporting `moved` or `resized` with both rectangles. Done when: a control shifted 5 pixels exits 1, one shifted 1 pixel exits 0, and a capture at another profile than the record's is refused with exit 2. Cheaper substitute: comparing order only, which passes a ribbon whose controls are the wrong size. **Corrected 2026-11-13 (fact check at start):** a pair whose record or captured element has no `bounds`, or whose parent has none on either side, cannot be measured: it is reported `unmeasured` and exits 1 unless `--no-bounds` is given, since a position nobody could compare is not a position that matches. The capture's profile is each captured record's `captureProfile`. **Corrected 2026-11-13 (plan review, gap 3):** Done when, in addition: a width changed by 5 and a height changed by 5, each alone, exit 1 as `resized` with both rectangles, and by 1 exit 0; a pair with no `bounds` on the record, on the captured element, on the inventory parent and on the captured parent each exit 1 as `unmeasured`; and each of those cases, and the moved and resized ones, exits 0 under `--no-bounds`.
- [x] Add `--no-bounds` for a parent whose layout `design/SPEC.md` modernises (Outlook, Visio and Project; `docs/specs/2026-10-23-campaign-scope-design.md`, decision 5): presence, label, type and order are still compared. Done when: a test with a moved control passes under `--no-bounds` and still fails on a missing one.
- [x] Print one line per finding and a last line with the counts, and exit 0 only when nothing is missing, renamed, retyped, reordered, moved or resized. Done when: the tests above assert the lines and the exit codes. **Corrected 2026-11-13 (fact check at start):** the exit code is decided before a line is printed and the findings go to stderr, the counts to stdout (lesson `the-verdict-is-decided-before-it-is-printed`); text read from either file is printed escaped. **Corrected 2026-11-13 (plan review, gap 3):** the exit is 0 only when nothing is missing, renamed, retyped, reordered, moved, resized or unmeasured; `extra` alone exits 0.
- [x] Document the command in `design/inventory/REFERENCE.md` under a `## Layout check` heading: its inputs, each finding and the tolerance. Done when: `python scripts/check-design-doc.py design/inventory/REFERENCE.md --require "Layout check"` exits 0.
- [ ] Commit: `inventory: compare a built app's layout with the inventory`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_check_layout.py"` passes, with a matching fixture exiting 0 and a moved, a missing and a retyped fixture each exiting 1.

## 31. Word Options Settings

The Word Options dialog, reached from Backstage: every category and every setting in each, in order, with its control type, so the product's own Options dialog can match it. **Corrected 2026-11-13:** split from §6, which bundled six capture surfaces, each needing its own capture mode in `scripts/capture-ui.py` (the tool knew only the ribbon and the shell); one surface per section.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Add the Options capture. Done when: its fake-tree test passes.
2. Capture Word Options. Done when: every category's settings are in `design/inventory/word/backstage.json` under `word.options.*`.

- [ ] Add `--options` to `scripts/capture-ui.py` for `--app word`: open Word Options from Backstage, select each category in order, and record each setting as a `setting` record under `word.options.<category>.*` (`order`, label, control type, enabled state), headings included, then close the dialog with Cancel so no setting changes, written through the tool's existing publish path (temporary file, then replace) and merged with `--merge` like a ribbon capture. Done when: a test in `scripts/tests/test_capture_ui.py` over the file's fake UI Automation tree (`E`, `FakeApp`) produces two categories' settings in order with their control types, and records that the dialog was closed with Cancel, and a refusal test shows the mode exits non-zero naming the surface when it cannot be opened. Cheaper substitute: a hand-written file, which no capture can check again on a new Office build.
- [ ] Capture Word Options on this PC with `python scripts/capture-ui.py --app word --options --merge` into `design/inventory/word/backstage.json`. Done when: each category Word Options lists has its settings with control types, the checker exits 0, and Word's options are unchanged (the capture compares a sample of settings read before and after). Cheaper substitute: category names only.
- [ ] Commit: `inventory: capture Word Options settings`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` passes and `python scripts/check-inventory.py design/inventory/word` exits 0 with at least one `setting` record per Options category.

## 32. Word Task Panes

Word's task panes (Navigation, Styles, Clipboard, Reviewing, Editor, Format Shape, Selection): where each docks, its default width, the command that opens it and the controls at its top level. **Corrected 2026-11-13:** split from §6, which bundled six capture surfaces, each needing its own capture mode in `scripts/capture-ui.py` (the tool knew only the ribbon and the shell); one surface per section.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Add the pane capture. Done when: its fake-tree test passes.
2. Capture Word's panes. Done when: `design/inventory/word/panes.json` holds the seven panes.

- [ ] Add `--panes` to `scripts/capture-ui.py` for `--app word`: open each pane by the ribbon command that opens it (its `idMso` from `design/inventory/word/ribbon.json`), record one `pane` record (docking side, width and height, the opening command) with its top-level controls in order, then close it, written through the tool's existing publish path (temporary file, then replace) and merged with `--merge` like a ribbon capture. Done when: a test in `scripts/tests/test_capture_ui.py` over the file's fake UI Automation tree (`E`, `FakeApp`) produces a pane with its docking side, size, opening command and controls, and a refusal test shows the mode exits non-zero naming the surface when it cannot be opened. Cheaper substitute: a hand-written file, which no capture can check again on a new Office build.
- [ ] Capture Word's panes on this PC with `python scripts/capture-ui.py --app word --panes` into `design/inventory/word/panes.json`. Done when: the seven panes named in this section exist with their opening commands and the checker exits 0. Cheaper substitute: panes without their opening command.
- [ ] Commit: `inventory: capture Word task panes`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` passes, `python scripts/check-inventory.py design/inventory/word` exits 0, and `design/inventory/word/panes.json` holds 7 `pane` records.

## 33. Word Status Bar

Word's status bar and its Customize Status Bar menu: every item, its position, and whether it is shown by default. **Corrected 2026-11-13:** split from §6, which bundled six capture surfaces, each needing its own capture mode in `scripts/capture-ui.py` (the tool knew only the ribbon and the shell); one surface per section.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Add the status bar capture. Done when: its fake-tree test passes.
2. Capture Word's status bar. Done when: `design/inventory/word/statusbar.json` holds every menu item.

- [ ] Add `--statusbar` to `scripts/capture-ui.py` for `--app word`: record each item the status bar shows (`statusItem`, `order`, left or right zone, bounds), then open the Customize Status Bar menu with a right click and record each of its items in order with its checked state as the default, then close the menu with Escape without changing any, written through the tool's existing publish path (temporary file, then replace) and merged with `--merge` like a ribbon capture. Done when: a test in `scripts/tests/test_capture_ui.py` over the file's fake UI Automation tree (`E`, `FakeApp`) produces the bar's items and the menu's items with their default states, and a refusal test shows the mode exits non-zero naming the surface when it cannot be opened. Cheaper substitute: a hand-written file, which no capture can check again on a new Office build.
- [ ] Capture Word's status bar on this PC with `python scripts/capture-ui.py --app word --statusbar` into `design/inventory/word/statusbar.json`. Done when: every menu item has `order` and a default on or off state, and the checker exits 0. Cheaper substitute: only the items visible by default.
- [ ] Commit: `inventory: capture Word status bar`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` passes and `python scripts/check-inventory.py design/inventory/word` exits 0 with `design/inventory/word/statusbar.json` holding the Customize Status Bar menu's items.

## 34. Word Dialogs

Every dialog reachable from a Word ribbon dialog launcher or from Backstage: its tabs and its controls in order, with labels and control types. **Corrected 2026-11-13:** split from §6, which bundled six capture surfaces, each needing its own capture mode in `scripts/capture-ui.py` (the tool knew only the ribbon and the shell); one surface per section.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Add the dialog capture. Done when: its fake-tree test passes.
2. Capture Word's dialogs. Done when: `design/inventory/word/dialogs.json` holds at least the ten named.

- [ ] Add `--dialogs` to `scripts/capture-ui.py` for `--app word`: open each dialog by its launcher (the `dialogLauncher` controls of `design/inventory/word/ribbon.json`) or Backstage entry, record one `dialog` record with a `dialogTab` per tab and its controls in order (label, control type), and close it with Cancel or Escape so nothing in the document changes, written through the tool's existing publish path (temporary file, then replace) and merged with `--merge` like a ribbon capture. Done when: a test in `scripts/tests/test_capture_ui.py` over the file's fake UI Automation tree (`E`, `FakeApp`) produces a dialog with two tabs and their controls, and records the Cancel, and a refusal test shows the mode exits non-zero naming the surface when it cannot be opened. Cheaper substitute: a hand-written file, which no capture can check again on a new Office build.
- [ ] Capture Word's dialogs on this PC with `python scripts/capture-ui.py --app word --dialogs` into `design/inventory/word/dialogs.json`, against a scratch document so a dialog that needs a selection (Insert Table, Bookmark) has one. Done when: Font, Paragraph, Page Setup, Find and Replace, Insert Table, Symbol, Index, Table of Contents, Bookmark and Mail Merge Recipients exist at minimum, with their tabs and controls, and the checker exits 0. Cheaper substitute: dialog titles without controls.
- [ ] Commit: `inventory: capture Word dialogs`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` passes, `python scripts/check-inventory.py design/inventory/word` exits 0, and `design/inventory/word/dialogs.json` holds at least 10 `dialog` records.

## 35. Word Context Menus and Mini Toolbar

Word's right-click menus (text, table, picture, shape, header and footer, hyperlink, spelling error, tracked change, comment) and the mini toolbar: one record per item in order, submenus one level deep. **Corrected 2026-11-13:** split from §6, which bundled six capture surfaces, each needing its own capture mode in `scripts/capture-ui.py` (the tool knew only the ribbon and the shell); one surface per section.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Add the menu capture. Done when: its fake-tree test passes.
2. Capture Word's menus. Done when: `design/inventory/word/menus.json` holds each context named.

- [ ] Add `--menus` to `scripts/capture-ui.py` for `--app word`: in the contextual fixture document (`--fixture`), select each kind of content in turn, open its context menu with Shift+F10, record one `contextMenu` record with its `menuItem` records in order and each submenu one level deep, record the `miniToolbar` the selection shows, and close the menu with Escape, written through the tool's existing publish path (temporary file, then replace) and merged with `--merge` like a ribbon capture. Done when: a test in `scripts/tests/test_capture_ui.py` over the file's fake UI Automation tree (`E`, `FakeApp`) produces a context menu with a submenu and a mini toolbar, and a refusal test shows the mode exits non-zero naming the surface when it cannot be opened. Cheaper substitute: a hand-written file, which no capture can check again on a new Office build.
- [ ] Capture Word's menus on this PC with `python scripts/capture-ui.py --app word --menus` into `design/inventory/word/menus.json`. Done when: each context named in this section has its menu captured with submenus one level deep, the mini toolbar is recorded, and the checker exits 0. Cheaper substitute: the text context menu only.
- [ ] Commit: `inventory: capture Word context menus and mini toolbar`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` passes and `python scripts/check-inventory.py design/inventory/word` exits 0 with `design/inventory/word/menus.json` holding nine `contextMenu` records and a `miniToolbar`.

## 36. Word Backstage Document States

Filed 2026-11-13T03:17:13Z from D02 T01 §6's fresh plan review (gap 3). §6 captures Backstage on a new blank document, so the groups and commands Word shows only for a document in another state are listed absent there with reason `document-state`. This section captures them from fixture documents in each state the reference build can produce on this PC, and gives every remaining `document-state` id a final disposition.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Make the fixtures. Done when: each state's document opens in Word in that state.
2. Capture Backstage from each. Done when: every `document-state` id of `ABSENT` is captured or given a final reason.

- [ ] Generate fixtures under `fixtures/word-states/` in `OFFICE_SCRATCH` with a script, `scripts/make-word-state-fixtures.py`, through Word's own object model: a read-only file, a document recommending read only, one marked as final, a Word 97-2003 `.doc` (compatibility mode), a digitally signed document (a self-signed test certificate it makes and removes), and a file carrying the internet zone mark so it opens in Protected View. Done when: running it twice gives fixtures in the same states, each checked by reopening it. Cheaper substitute: hand-made documents nobody can regenerate.
- [ ] Add `--state <name>` to `scripts/capture-ui.py --backstage`: open that fixture in place of the blank document, capture Info and the pages the state changes, and merge the new records under their pages with the state named on each (`captureState`, a new optional field). Done when: a fake-tree test shows a state-only group recorded with its state, and the blank-document records left as they were.
- [ ] Capture each state on this PC and remove from `ABSENT` each `document-state` id the captures show. Done when: `python scripts/check-inventory.py design/inventory/word` exits 0 and every remaining `document-state` id is moved to a final reason (`not-offered` or `not-exposed`) or to the server-state reason below. Cheaper substitute: leaving them absent.
- [ ] Record the states this PC cannot produce (checked out, cached offline, on a server, with upload errors), which need a document library, as `server-state` in `ABSENT` and in `design/inventory/REFERENCE.md`, with what a capture of them would need. Done when: the reason is documented and the checker exits 0.
- [ ] Commit: `inventory: capture Word Backstage in other document states`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` passes and `python scripts/check-inventory.py design/inventory/word` exits 0 with no `document-state` reason left in `ABSENT`.

## 37. Word Backstage Account States

Filed 2026-11-13T03:17:13Z from D02 T01 §6's fresh plan review (gap 3). The `account-state` and `layout-variant` groups of Backstage show only when no account is signed in, when sign-in is disabled, or for an Office Insider or a selectable update channel. Producing those states means signing the owner's Word out on this PC, or changing its update channel, so the owner does it or allows it.

**Phase:** 2
**Needs:** office, windows-host, display-session, operator
**Owner action:** In a campaign session, say whether the session may sign Word out on this PC for a capture and sign it back in afterwards (you will be asked for your account's password to sign back in), or sign out yourself and tell the session; the session records the answer here and removes `operator`.
**Surface:** no

**Build order:**

1. Capture Backstage signed out. Done when: the signed-out groups are captured.
2. Settle the rest. Done when: no `account-state` or `layout-variant` id is left in `ABSENT` without a final reason.

- [ ] Capture Backstage with `python scripts/capture-ui.py --app word --backstage --state signed-out --merge` after Word is signed out. Done when: the sign-in groups and the signed-out layouts of Open and Save As are recorded with `captureState` `signed-out`, and the checker exits 0.
- [ ] Remove from `ABSENT` each `account-state` and `layout-variant` id the capture shows, and give each remaining one (Office Insider, a selectable update channel) a final reason with what showing it needs. Done when: `python scripts/check-inventory.py design/inventory/word` exits 0 and REFERENCE.md documents each remaining id's reason.
- [ ] Commit: `inventory: capture Word Backstage signed out`

**Test checkpoint:** `python scripts/check-inventory.py design/inventory/word` exits 0 with no `account-state` reason left in `ABSENT`.

## 38. Sweep Gate on Checker Changes

Filed 2026-11-13T10:40:00Z by the lead while D02 T01 §27 was built. §27 proved once that every rule of `scripts/check-inventory.py` and `design/inventory/schema.json` is held by a test (`docs/reviews/02-interface/inventory-mutation-sweep.md`), and nothing runs that proof again: the next change to the checker, its schema or its tests can add a rule no test holds, or drop the test that held one, and nobody would know until someone ran the sweep by hand, which takes about an hour on this PC (270 rules, four workers). This section makes the sweep a standing gate that GitHub runs in shares on every push that changes one of those files, so a red head names the unheld rule within one CI run (owner, 2026-11-12, decision 45: this PC runs what a change touches, GitHub does the heavy lifting).

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Give `scripts/mutation-sweep-inventory.py` shares, a stop at the first failing test and a check of what a push changed. Done when: the shares of a fixture sweep together remove every rule exactly once, a killed removal's run ends at its first failure, and a push that changed none of the swept files runs nothing.
2. Add the `sweep` job to `.github/workflows/ci.yml`. Done when: the job runs four shares with the command below and `scripts/ci-status.py` reads its result with the rest of the run.
3. Prove it on GitHub. Done when: the push that adds the job shows four `sweep` shares that removed rules and passed, and a later push that changes none of the swept files shows them skipped.

- [ ] Add `--shard <i>/<n>` to `scripts/mutation-sweep-inventory.py`: the rules, in the order `--list` prints them, are dealt to `n` shares by position, and every share starts with its own unmutated run. Done when: a test in `scripts/tests/test_mutation_sweep_inventory.py` shows the four shares of the fixture disjoint and together equal to the whole list, and `--shard 0/4`, `--shard 5/4` and `--shard x` each exit 2 with a message naming the form. Cheaper substitute: dealing by a hash of the rule's name, which leaves shares uneven and moves a rule between shares when its line number changes; refused. Source: `scripts/run-tests.py`, `--shard`.
- [ ] Stop a removal's test run at its first failing test in `run_tests` of `scripts/mutation-sweep-inventory.py`, with a result class whose `addFailure` stops the run and whose `addError` does not, and report a run stopped that way as `KILLED` without asking that every discovered test ran. Done when: fixture tests show a killed removal reported `KILLED` with one failing test and fewer tests run than discovered, a removal whose tests only error still `ERRORED` after every test ran, a removal whose first test errors and whose later test fails `KILLED`, and a removal that hides a test file still `UNDISCOVERED`. Cheaper substitute: unittest's own `failfast`, which also stops at the first error and would report a killable removal as `ERRORED`; refused.
- [ ] Add `--if-changed <base> <head>` to `scripts/mutation-sweep-inventory.py`: when `git diff --name-only <base> <head>` names none of `scripts/check-inventory.py`, `design/inventory/schema.json`, `scripts/tests/test_check_inventory.py` and `scripts/mutation-sweep-inventory.py`, it prints `sweep skipped: no swept file changed between <base> and <head>` and exits 0 having removed nothing; when one is named, or when either commit cannot be read (the all-zero base of a first push, a commit missing from a shallow clone, `git` failing), it runs the sweep. Done when: tests over a fixture repository show the skip, a run for a change to each of the four files, and a run for an unreadable base, each with the line it prints. Cheaper substitute: a `paths:` filter on a workflow of its own, whose run `scripts/ci-status.py` does not read and which no test here can exercise; refused.
- [ ] Add the `sweep` job to `.github/workflows/ci.yml`: four shares on `windows-latest` with `fail-fast: false`, `fetch-depth: 0`, the Python and requirements steps of the `tests` job, then `python -B scripts/mutation-sweep-inventory.py --shard ${{ matrix.share }}/4 --if-changed ${{ github.event.before }} ${{ github.sha }}`. Done when: a test in `scripts/tests/test_mutation_sweep_inventory.py` reads the workflow and finds the job, its four shares, the full history checkout and that command, and `scripts/tests/test_ci_status.py` shows a run whose `sweep` share failed read as red with that share named. Cheaper substitute: a workflow file of its own, whose red result would not stop the campaign because `scripts/ci-status.py` reads the `ci.yml` run; refused.
- [ ] Name the gate where a reader looks for it: the list of CI checks in `AGENTS.md` (TODO workflow) and the head of `docs/reviews/02-interface/inventory-mutation-sweep.md`, each saying what starts it and how a red share is reproduced here (`python -B scripts/mutation-sweep-inventory.py --shard N/4`). Done when: both name the `sweep` job and that command.
- [ ] Record the proof on GitHub in this section's findings file `docs/reviews/02-interface/D02-T01-s38.md` under a `## Writer note:` heading: the run of the push that adds the job (four `sweep` shares, each printing `survivors: 0` after removing its rules) and the run of a later push that changes none of the four files (four shares, each printing `sweep skipped`), with both run addresses and the seconds each share took. Done when: both runs are green and quoted there. Cheaper substitute: trusting the workflow test alone, which reads the file and never runs it.
- [ ] Commit: `ci: sweep the inventory checker's rules on every change to it`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_mutation_sweep_inventory.py"` passes, and `python scripts/ci-status.py HEAD` exits 0 for a head whose run holds four `sweep` jobs.

## Verification

- `python scripts/check-inventory.py design/inventory` exits 0 over every file.
- `design/inventory/COVERAGE.md` lists all six apps and the shell with non-zero counts per kind.
- `git ls-files design/inventory | Select-String -Pattern "\.(png|jpg|ico)$"` finds nothing.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
